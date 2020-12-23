import subprocess
import sys 
import json
import openai
import numpy as np
import pandas as pd
from gpt import GPT
from gpt import Example
from unidecode import unidecode

def change_labels(num):
    if num == 1:
        return "positive"
    elif num == 0:
        return "neutral"
    elif num == -1:
        return "negative"

""" def handle_emojis(df):
    emoPos = " [EMO_POS] "
    emoNeg = " [EMO_NEG] "
    # Smile     :), : ), :-), (:, (:, (-:, : ')
    df.replace(r"(:\s?\)|:-\)|\(\s?:|\(-:|:\'\))", emoPos, regex = True, inplace = True)
    # Laugh     :D, : D, : -D, xD, X - Dz, x - D, XD
    df.replace(r"(:\s?-?\s?d|x\s?-\s?dz|x\s?-\s?d)", emoPos, regex = True, inplace = True)
    # Love     <3, < 3, :*
    df.replace(r"(<3|:\*)", emoPos, regex = True, inplace = True)
    # Wink    ; -), ;), ; -D, ; D, (; , (-;
    df.replace(r"(;-?\)|;-?D|\(-?;)", emoPos, regex = True, inplace = True)
    # Sad     :-(, : (, :(, ) : , ) - :
    df.replace(r"(:\s?\(|:-\(|\)\s?:|\)-:)", emoNeg, regex = True, inplace = True)
    # Cry     :, (, :'(, :"(
    df.replace(r"(:,\s?\(|:\'\s?\(|:\"\s?\()", emoNeg, regex = True, inplace = True)
 """
def clean_text(copy_df):
    urlMention = "URL"
    email = "E_M"
    userMention = "U_M"
    space = " "

    # Replace URLs with urlMention
    copy_df.replace(r"((www\.[\S]+)|(https?://[\S]+))", space + urlMention + space, regex = True, inplace=True)

    # Replace emails with email:
    copy_df.replace(r"([a-z0-9!#$%&'*+/=?^_‘{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_‘{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", space + email + space, regex = True, inplace=True)

    # Replace @handle with the userMention
    copy_df.replace(r"(@[\S]+)", space + userMention + space, regex = True, inplace=True)

    # Replace #hashtag with hashtag
    copy_df.replace("#(\\S+)", r'\1', regex = True, inplace = True)

    # Remove RT(retweet)
    copy_df.replace(r'\brt\b', "", regex = True, inplace = True)

    # Replace consecutive dots with space
    copy_df.replace(r"(\.{2,})", " ", regex = True, inplace = True)

    # Replace curly apostrophes and quotes with straight ones
    copy_df["Phrase_text"] = copy_df["Phrase_text"].apply(unidecode)

    # Strip space, quotation and apostrophe
    copy_df["Phrase_text"] = copy_df["Phrase_text"].str.replace(r' "', '"')
    copy_df["Phrase_text"] = copy_df["Phrase_text"].str.replace(r" '", "'")

    # Replace emojis with either EMO_POS or EMO_NEG
    # handle_emojis(copy_df)

    # Replace consecutive spaces with a single space
    copy_df.replace(r"(\s+)", " ", regex = True, inplace = True)
    return copy_df 
        
def transform_txt(filename, n): # n is the number of randomly chosen input instances wanted for each sentiment category
    """
    This function reads input sentences and associated sentiments 
    """
    # reading text filename into a Dataframe
    all_data = pd.read_csv(filename, header = 0, encoding = "utf8", sep = ":->")
    all_data['Sentiment_class_label'] = all_data['Sentiment_class_label'].apply(lambda x: change_labels(x))
    all_data = clean_text(all_data)
    df_used = all_data.groupby('Sentiment_class_label').apply(lambda x: x.sample(n)).reset_index(drop=True)
    #df_used = data.groupby('Sentiment_class_label', as_index = False).apply(fn)
    return all_data, df_used

def bold_abbrev(sentiment_str):
    if sentiment_str == "positive":
        return "POS"
    elif sentiment_str == "negative":
        return "NEG"
    elif sentiment_str == "neutral":
        return "NEU"
    else:
        return sentiment_str

def extract_example_df(all_data, n):
    df_subset = all_data.groupby('Sentiment_class_label').apply(lambda x: x.sample(n)).reset_index(drop = True)
    return df_subset
    
def add_examples(gpt_instance, df_subset): # n is the number of Example instances to "train" GPT-3 on
    for row in range(df_subset.shape[0]):
        gpt_instance.add_example(Example(df_subset['Phrase_text'][row], df_subset['Sentiment_class_label'][row]))
    return gpt_instance
    
# A function to write prompt into GPT-3 API:
def write_prompts(df_used, gpt_instance):
    df_used['gpt_output'] = df_used["Phrase_text"].apply(lambda x: gpt_instance.submit_request(x).choices[0].text.lower().strip())
    df_used['matched'] = np.where(df_used['Sentiment_class_label'] == df_used['gpt_output'], 1, 0)
    #df_used['gpt_output'] = df_used['gpt_output'].apply(lambda x: bold_abbrev(x))
    # dropping Sentiment_class_label column
    #df_used.drop(['Sentiment_class_label'], axis = 1)
    return df_used
def write_output(engine, temp, max_tokens, num_training_per_cate, df_used, df_subset):
    gpt = GPT(engine = engine, temperature = temp, max_tokens = max_tokens, output_prefix = "Sentiment:")
    if type(df_subset) == pd.core.frame.DataFrame:
        gpt = add_examples(gpt, df_subset)
    out_df = write_prompts(df_used, gpt)
    print(out_df)
    #out_df.drop("Sentiment_class_label", axis = 1, inplace = True)
    accuracy = ((np.sum(out_df['matched'])) / (out_df.shape[0])) * 100
    print("Accuracy: {}".format(accuracy))
    #out_df.to_csv('outf{}.txt'.format(temp), header = ['PHRASE_TEXT', 'GPT_OUTPUT', 'MATCHED'], index = None, sep = " ", mode = 'a')
    #line_prepender('outf{}.txt'.format(temp), "ACCURACY ACHIEVED: {:.2f}".format(accuracy))
    #line_prepender('outf{}.txt'.format(temp), "TEMPERATURE SETTING: {}".format(temp))
# Function to write the accuracy at the beginning of output text file
def line_prepender(filename, line):
    with open(filename, encoding = "utf8", mode='r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)



def main(num_testing_per_cate, num_training_per_cate = 1, temp = None, max_tokens = 6):
    
    with open('GPT_SECRET_KEY.json') as f:
        data = json.load(f)
    openai.api_key = data["API_KEY"]
    temp_list = [0.0, 0.5, 1.0]
    all_data, df_used = transform_txt("sm_text_sentiment_training.txt", num_testing_per_cate)
    real_df_used = df_used.copy()
    # if training data is used (n indicating number of training instances per category of sentiment)
    if num_training_per_cate >= 1:
        df_subset = extract_example_df(all_data, num_training_per_cate)
    else:
        df_subset = None
    if temp == None:
        for temp in temp_list:
            write_output(engine = "instruct-davinci-beta", temp = temp, max_tokens = max_tokens, num_training_per_cate = num_training_per_cate, df_used = df_used, df_subset = df_subset)
            df_used = real_df_used
    elif temp != None:
        write_output(engine = "instruct-davinci-beta", temp = temp, max_tokens = max_tokens, num_training_per_cate = num_training_per_cate, df_used = df_used, df_subset = df_subset)

        
if __name__ == "__main__":
    num_testing_per_cate = int(input("Enter number of randomly chosen testing instances per each sentiment category (an int): "))
    num_training_per_cate = int(input("Enter number of randomly chosen training instances per each sentiment category (an int): "))
    try:
        temp = float(input("Enter desired temperature setting (a floating point number from 0.0 to 1.0) (Hit \"Enter\" to skip): "))
    except SyntaxError:
        pass
    max_tokens = 3
    main(num_testing_per_cate, num_training_per_cate, temp, max_tokens)




