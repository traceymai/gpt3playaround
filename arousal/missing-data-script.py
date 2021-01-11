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
        return "high activation"
    elif num == 0:
        return "medium activation"
    elif num == -1:
        return "medium deactivation"
    elif num == -2:
        return "high deactivation"

def map_emotions(gpt_out):
    HA = ['surprised', 'amazement', 'ecstasy', 'excited', 'rage', 'shock', 'terror', 'alert']
    MA = ['tense', 'alarmed', 'frustrated', 'happy', 'delighted', 'nervous', 'fear', 'envy']
    MD = ['disgusted', 'depressed', 'sad', 'content', 'relaxed', 'satisfied', 'serene', 'empathetic']
    HD = ['bored', 'tired', 'calm', 'sleepy', 'sorrow', 'grief']
    if gpt_out in HA:
        return "high activation"
    elif gpt_out in MA:
        return "medium activation"
    elif gpt_out in MD:
        return "medium deactivation"
    elif gpt_out in HD:
        return "high deactivation"
    else:
        return gpt_out
def map_to_neutral(num):
    if num == 1:
        return "high activation"
    elif num == 0 or num == -1:
        return "neutral"
    elif num == -2:
        return "high deactivation"

def map_back(astr):
    if astr == "high activation":
        return float(1)
    elif astr == "medium activation":
        return float(0)
    elif astr == "high deactivation":
        return float(-2)
    elif astr == "medium deactivation":
        return float(-1)
    #elif astr == "low activation":
        #return float(-1)
    else:
        return astr

def transform_txt(inputf, trainingf): # n is the number of randomly chosen input instances wanted for each sentiment category
    """
    This function reads input sentences and associated sentiments 
    """
    #df_train_all = pd.read_csv(filename, skiprows=1, header = 0, encoding = "utf8", sep = ":->", nrows = 28, engine = "python")
    #df_used = df_train_all.groupby("Sentiment_class_label").head(num_training_per_cate).reset_index(drop = True)
    #df_used["Sentiment_class_label"] = df_used["Sentiment_class_label"].apply(lambda x: change_labels(x))
    #df_used = clean_text(df_used)
    all_data = pd.read_csv(inputf, encoding = "utf8", sep = ":->", engine = "python", header = None)
    all_data.columns = ["Sentiment_class_label", "Phrase_text"]
    #all_data["Arousal_class_label"] = all_data["Arousal_class_label"].apply(lambda x: change_labels(x))
    #all_data["Arousal_class_label"] = all_data["Arousal_class_label"].apply(lambda x: map_to_neutral(x))
    all_data = clean_text(all_data)
    df_train = pd.read_csv(trainingf, skiprows = 1, nrows = 18, encoding = "utf8", sep = ":->", engine = "python", header = None)
    df_train.columns = ["Arousal_class_label", "Phrase_text"]
    df_train["Arousal_class_label"] = df_train["Arousal_class_label"].apply(lambda x: change_labels(x))
    #df_train["Arousal_class_label"] = df_train["Arousal_class_label"].apply(lambda x: map_to_neutral(x))
    df_train = clean_text(df_train)
    print("df_trained")
    print(df_train)
    print("all_data")
    print(all_data)
    return all_data, df_train

def add_examples(gpt_instance, df_subset): # n is the number of Example instances to "train" GPT-3 on
    for row in range(df_subset.shape[0]):
        gpt_instance.add_example(Example(df_subset['Phrase_text'][row], df_subset['Arousal_class_label'][row]))
    return gpt_instance
    
# A function to write prompt into GPT-3 API:
def write_prompts(all_data, gpt_instance):
    ##all_data['gpt_output'] = all_data["Phrase_text"].apply(lambda x: gpt_instance.submit_request(x))
    all_data['gpt_output'] = all_data["Phrase_text"].apply(lambda x: gpt_instance.submit_request(x).choices[0].text.lower().strip())
    all_data['gpt_output'] = all_data['gpt_output'].apply(lambda x: map_emotions(x))
    #all_data_used = all_data[all_data['gpt_output'] != "mixed"]
    #mixed_df = all_data[all_data['gpt_output'] == "mixed"]
    #all_data['matched'] = np.where(all_data['Arousal_class_label'] == all_data['gpt_output'], 1, 0)
    #df_used['gpt_output'] = df_used['gpt_output'].apply(lambda x: bold_abbrev(x))
    # dropping Sentiment_class_label column
    #df_used.drop(['Sentiment_class_label'], axis = 1)
    return all_data

# Function to write the accuracy at the beginning of output text file
def line_prepender(filename, line):
    with open(filename, encoding = "utf8", mode='r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

def write_output(engine, temp, max_tokens, all_data, df_used):
    #def write_output(engine, temp, max_tokens, all_data, num_training_per_cate):
    gpt = GPT(engine = engine, temperature = temp, max_tokens = max_tokens, output_prefix = "Sentiment:", logprobs = 3, append_output_prefix_to_query=True)
    gpt = add_examples(gpt, df_used)
    out_df = write_prompts(all_data, gpt)
    out_df = out_df[["Sentiment_class_label", "gpt_output", "Phrase_text"]]
    print(out_df)
    out_df["gpt_output"] = out_df["gpt_output"].apply(lambda x: map_back(x))
    #print(out_df)
    #out_df.drop("Arousal_class_label", axis = 1, inplace = True)
    #accuracy = ((np.sum(out_df['matched'])) / (out_df.shape[0])) * 100
    #print("Accuracy: {}".format(accuracy))
    out_df.to_csv('outmissingdata_descriptive_final1.txt', header = False, index = None, sep = ",", mode = 'a')
    #print("###" * 50)
    #print("Instances GPT-3 categorised as Mixed:")
    #mixed_df.to_csv("outzeroshot.txt", sep = " ", mode = "a")
    line_prepender('outmissingdata_descriptive_final1.txt', "VALENCE,AROUSAL,SENTENCE")

def main(inputf, trainingf, temp = None, max_tokens = 6):
    with open('GPT_SECRET_KEY.json') as f:
        data = json.load(f)
    openai.api_key = data["API_KEY"]
    all_data, df_used = transform_txt(inputf = inputf, trainingf = trainingf)
    write_output(engine = "instruct-davinci-beta", temp = temp, max_tokens = max_tokens, all_data = all_data, df_used = df_used)

if __name__ == "__main__":
    inputf = "missing-data/data-without-gpt-output-descriptive.txt"
    trainingf = "arousal_train.txt"
    try:
        temp = float(input("Enter desired temperature setting (a floating point number from 0.0 to 1.0) (Hit \"Enter\" to set at 0.0): "))
    except SyntaxError:
        pass
    max_tokens = 3
    main(inputf, trainingf, temp, max_tokens)