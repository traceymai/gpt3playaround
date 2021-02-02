import subprocess
import sys 
import json
import openai
import numpy as np
import pandas as pd
from gpt import GPT
from gpt import Example
from unidecode import unidecode
from string import whitespace

""" def handle_emojis(df):
    emoPos = " [EMO_POS] "
    emoNeg = " [EMO_NEG] "
    # Smile     :), : ), :-), (:, (:, (-:, : ')
    df.replace(r"(:\s?\)|:-\)|\(\s?:|\(-:|:\'\))", emoPos, regex = True, inplace = True)
    # Laugh     :D, : D, : -D, xD, X - Dz, x - D, XD
    df.replace(r"(:\s?-?\s?d|x\s?-\s?dz|x\s?-\s?d)", emoPos, regex = True, inplace = True)
    # Love     <3, < 3, :*
    df.replace(r"(<3|:\*)", emoPos, regex = //  True, inplace = True)
    # Wink    ; -), ;), ; -D, ; D, (; , (-;
    df.replace(r"(;-?\)|;-?D|\(-?;)", emoPos, regex = True, inplace = True)
    # Sad     :-(, : (, :(, ) : , ) - :
    df.replace(r"(:\s?\(|:-\(|\)\s?:|\)-:)", emoNeg, regex = True, inplace = True)
    # Cry     :, (, :'(, :"(
    df.replace(r"(:,\s?\(|:\'\s?\(|:\"\s?\()", emoNeg, regex = True, inplace = True)
 """
#from unidecode import unidecode
#import pandas as pd
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
    #copy_df["Phrase_text"] = copy_df["Phrase_text"].apply(unidecode)
    copy_df["Phrase_text"] = copy_df["Phrase_text"].str.replace(u'[\u201c\u201d]', '"')
    copy_df["Phrase_text"] = copy_df["Phrase_text"].str.replace(u'[\u2019\u2019]', "'")
    # Strip space, quotation and apostrophe
    copy_df["Phrase_text"] = copy_df["Phrase_text"].str.replace(whitespace + '""', r'"')
    copy_df["Phrase_text"] = copy_df["Phrase_text"].str.replace(whitespace + "''", r"'")

    # Replace emojis with either EMO_POS or EMO_NEG
    # handle_emojis(copy_df)

    # Replace consecutive spaces with a single space
    copy_df.replace(r"(\s+)", " ", regex = True, inplace = True)

    # Convert more than 2 letter repetitions to 2 letter: eg: funnnnny -> funny
    copy_df.replace(r'(.)\1{2,}', r'\1\1', regex = True, inplace = True)
    return copy_df
def change_labels(num):
    if num == 1:
        return "positive"
    elif num == 0:
        return "neutral"
    elif num == -1:
        return "negative"
    elif num == 2:
        return "mixed"

def transform_txt(filename, num_training_per_cate): # n is the number of randomly chosen input instances wanted for each sentiment category
    """
    This function reads input sentences and associated sentiments 
    """
    #df_train_all = pd.read_csv(filename, skiprows=1, header = 0, encoding = "utf8", sep = ":->", nrows = 28, engine = "python")
    #df_used = df_train_all.groupby("Sentiment_class_label").head(num_training_per_cate).reset_index(drop = True)
    #df_used["Sentiment_class_label"] = df_used["Sentiment_class_label"].apply(lambda x: change_labels(x))
    #df_used = clean_text(df_used)
    all_data = pd.read_csv(filename, skiprows = 31, header = 0, encoding = "utf8", sep = ":->", nrows = 30, engine = "python")
    all_data["Sentiment_class_label"] = all_data["Sentiment_class_label"].apply(lambda x: change_labels(x))
    all_data = clean_text(all_data)
    """ print("df_used")
    print(df_used)
    print("all_data")
    print(all_data) """
    return all_data 
        #df_used
#transform_txt("train_test_gpt3.txt", 1)
  
def add_examples(gpt_instance, df_subset): # n is the number of Example instances to "train" GPT-3 on
    for row in range(df_subset.shape[0]):
        gpt_instance.add_example(Example(df_subset['Phrase_text'][row], df_subset['Sentiment_class_label'][row]))
    return gpt_instance
    
# A function to write prompt into GPT-3 API:
def write_prompts(all_data, gpt_instance):
    all_data['gpt_output'] = all_data["Phrase_text"].apply(lambda x: gpt_instance.submit_request(x).choices[0].text.lower().strip())
    all_data_used = all_data[all_data['gpt_output'] != "mixed"]
    mixed_df = all_data[all_data['gpt_output'] == "mixed"]
    all_data_used['matched'] = np.where(all_data_used['Sentiment_class_label'] == all_data_used['gpt_output'], 1, 0)
    #df_used['gpt_output'] = df_used['gpt_output'].apply(lambda x: bold_abbrev(x))
    # dropping Sentiment_class_label column
    #df_used.drop(['Sentiment_class_label'], axis = 1)
    return all_data_used, mixed_df

# Function to write the accuracy at the beginning of output text file
def line_prepender(filename, line):
    with open(filename, encoding = "utf8", mode='r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

#def write_output(engine, temp, max_tokens, all_data, df_used, num_training_per_cate):
def write_output(engine, temp, max_tokens, all_data, num_training_per_cate):
    gpt = GPT(engine = engine, temperature = temp, max_tokens = max_tokens, output_prefix = "Sentiment:")
    #gpt = add_examples(gpt, df_used)
    out_df, mixed_df = write_prompts(all_data, gpt)
    #print(out_df)
    out_df.drop("Sentiment_class_label", axis = 1, inplace = True)
    accuracy = ((np.sum(out_df['matched'])) / (out_df.shape[0])) * 100
    print("Accuracy: {}".format(accuracy))
    out_df.to_csv('outzeroshot.txt', header = ['PHRASE_TEXT', 'GPT_OUTPUT', 'MATCHED'], index = None, sep = " ", mode = 'a')
    print("###" * 50)
    print("Instances GPT-3 categorised as Mixed:")
    mixed_df.to_csv("outzeroshot.txt", sep = " ", mode = "a")
    line_prepender('../arousal/output/outzeroshot.txt', "ACCURACY: {:.2f}, TEMPERATURE: {}".format(accuracy, temp))



def main(num_testing_per_cate, num_training_per_cate = 0, temp = None, max_tokens = 6):
    with open('GPT_SECRET_KEY.json') as f:
        data = json.load(f)
    openai.api_key = data["API_KEY"]
    filename = "train_data/train_test_gpt3.txt"
    all_data = transform_txt(filename = filename, num_training_per_cate = num_training_per_cate)
    #all_data, df_used = transform_txt(filename = filename, num_training_per_cate = num_training_per_cate)
    # if training data is used (n indicating number of training instances per category of sentiment)
    write_output(engine = "instruct-davinci-beta", temp = temp, max_tokens = max_tokens, all_data = all_data, num_training_per_cate = num_training_per_cate)
    #write_output(engine = "instruct-davinci-beta", temp = temp, max_tokens = max_tokens, all_data = all_data, df_used = df_used, num_training_per_cate = num_training_per_cate)

        
if __name__ == "__main__":
    num_testing_per_cate = int(input("Enter number of randomly chosen testing instances per each sentiment category (an int): "))
    # This is always 10
    num_training_per_cate = int(input("Enter number of randomly chosen training instances per each sentiment category (an int): "))
    # This is 1, 3, 5, 7
    try:
        temp = float(input("Enter desired temperature setting (a floating point number from 0.0 to 1.0) (Hit \"Enter\" to set at 0.0): "))
    except SyntaxError:
        pass
    max_tokens = 3
    main(num_testing_per_cate, num_training_per_cate, temp, max_tokens)




