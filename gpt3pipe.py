import subprocess
import sys 
import json
import openai
import pandas as pd
from gpt import GPT
from gpt import Example
import numpy as np

def change_labels(num):
    if num == 1:
        return "positive"
    elif num == 0:
        return "neutral"
    elif num == -1:
        return "negative"

def handle_emojis(df):
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

def clean_data(df):
    copy_df = all_data_df.copy()
    urlMention = " [URL_MENTION] "
    email = " [EMAIL_ADDRESS] "
    userMention = " [USER_MENTION] "

    # Replace URLs with urlMention
    copy_df.replace(r"((www\.[\S]+)|(https?://[\S]+))", urlMention, regex = True, inplace=True)

    # Replace emails with email:
    copy_df.replace(r"([a-z0-9!#$%&'*+/=?^_‘{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_‘{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", email, regex = True, inplace=True)

    # Replace @handle with the userMention
    copy_df.replace(r"(@[\S]+)", userMention, regex = True, inplace=True)

    # Replace #hashtag with hashtag
    copy_df.replace("#(\\S+)", r'\1', regex = True, inplace = True)

    # Remove RT(retweet)
    copy_df.replace(r'\brt\b', "", regex = True, inplace = True)

    # Replace consecutive dots with space
    copy_df.replace(r"(\.{2,})", " ", regex = True, inplace = True)

    # Replace curly apostrophes and quotes with straight ones
    copy_df["Phrase_text"] = copy_df["Phrase_text"].apply(unidecode)

    # Strip space, quotation and apostrophe
    copy_df["Phrase_text"] = copy_df["Phrase_text"].str.replace(r"[\"\']", "")

    # Replace emojis with either EMO_POS or EMO_NEG
    handle_emojis(copy_df)

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
    all_data = clean_data(all_data)
    df_used = all_data.groupby('Sentiment_class_label').apply(lambda x: x.sample(n)).reset_index(drop=True)
    #df_used = data.groupby('Sentiment_class_label', as_index = False).apply(fn)
    return all_data, df_used

def extract_example_df(all_data, n):
    df_subset = all_data.groupby('Sentiment_class_label').apply(lambda x: x.sample(n)).reset_index(drop = True)
    return df_subset
    
def add_examples(gpt_instance, df_subset): # n is the number of Example instances to "train" GPT-3 on
    for row in range(df_subset.shape[0]):
        gpt_instance.add_example(Example(df_subset['Phrase_text'][row], df_subset['Sentiment_class_label'][row]))
    return gpt_instance
    
# A function to write prompt into GPT-3 API:
def write_prompts(df_used, gpt_instance):
    df_used['gpt_output'] = df_used["Phrase_text"].apply(lambda x: gpt_instance.submit_request(x).choices[0].text.replace("output (positive/neutral/negative):", "").strip("\n").strip())
    df_used['matched'] = np.where(df_used['Sentiment_class_label'] == df_used['gpt_output'], 1, 0)
    # dropping Sentiment_class_label column
    #df_used.drop(['Sentiment_class_label'], axis = 1)
    return df_used

# Function to write the accuracy at the beginning of output text file
def line_prepender(filename, line):
    with open(filename, encoding = "utf8", mode='r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)



def main():
    
    with open('GPT_SECRET_KEY.json') as f:
        data = json.load(f)
    openai.api_key = data["API_KEY"]
    temp_list = [0.0, 0.5, 1.0]
    accuracy_list = []
    all_data, df_used = transform_txt("sm_text_sentiment_training.txt", 4)
    real_df_used = df_used.copy()
    df_subset = extract_example_df(all_data, 1)
    for temp in temp_list:
        gpt = GPT(engine = "davinci", temperature = temp, max_tokens = 100, output_prefix = "output (positive/neutral/negative):")
        gpt = add_examples(gpt, df_subset)
        out_df = write_prompts(df_used, gpt)
        out_df.drop("Sentiment_class_label", axis = 1, inplace = True)
        accuracy = ((np.sum(out_df['matched'])) / (out_df.shape[0])) * 100
        accuracy_list.append(round(accuracy))
        out_df.to_csv('outf{}.txt'.format(temp), header = ['Phrase_text', 'gpt_output', 'matched'], index = None, sep = " ", mode = 'a')
        line_prepender('outf{}.txt'.format(temp), "accuracy: {:.2f}".format(accuracy))
        line_prepender('outf{}.txt'.format(temp), str(temp))
        df_used = real_df_used.copy()
        


