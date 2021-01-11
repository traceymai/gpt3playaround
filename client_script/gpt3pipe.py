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
    df.replace(r"(<3|:\*)", emoPos, regex = True, inplace = True)
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

"""def label_processing(label):
    label = label.lower().strip()
    if """

def change_labels(num):
    if num == 1:
        return "positive"
    elif num == 0:
        return "neutral"
    elif num == -1:
        return "negative"
    elif num == 2:
        return "mixed"

def transform_txt(inputf, trainf): # n is the number of randomly chosen input instances wanted for each sentiment category
    """
    This function reads input sentences and associated sentiments 
    """
    df_used = pd.read_csv(trainf, header = None, encoding = "utf8", sep = ":->", engine = "python")
    df_used.columns = ["Sentiment_class_label", "Phrase_text"]
    #df_used = df_train_all.groupby("Sentiment_class_label").head(num_training_per_cate).reset_index(drop = True)
    df_used["Sentiment_class_label"] = df_used["Sentiment_class_label"].apply(lambda x: change_labels(x))
    df_used = clean_text(df_used)
    all_data = pd.read_csv(filename, header = 0, encoding = "utf8", sep = ",", engine = "python")
    all_data.drop(columns = ["#", "SVM.1", 'Unnamed: 5', 'metatag', 'DIT / Dialog Act', 'Organic Study Pose'], inplace = True)
    all_data.columns = ["SVM_label", "Natural_Validation_Label", "ServRep_Validation_Label", "Phrase_text"]
    #all_data["Sentiment_class_label"] = all_data["Sentiment_class_label"].apply(lambda x: change_labels(x))
    all_data = clean_text(all_data)
    print("df_used")
    print(df_used)
    print("all_data")
    print(all_data)
    return all_data, df_used
        #df_used
#transform_txt("train_test_gpt3.txt", 1)
  
def add_examples(gpt_instance, df_subset): # n is the number of Example instances to "train" GPT-3 on
    for row in range(df_subset.shape[0]):
        gpt_instance.add_example(Example(df_subset['Phrase_text'][row], df_subset['Sentiment_class_label'][row]))
    return gpt_instance
    
# A function to write prompt into GPT-3 API:
def write_prompts(all_data, gpt_instance):
    all_data['gpt_output'] = all_data["Phrase_text"].apply(lambda x: gpt_instance.submit_request(x).choices[0].text.lower().strip())
    all_data_used = all_data[all_data['gpt_output'] != "mixed"].reset_index()
    print("all data not classified as mixed")
    print(all_data_used)
    mixed_df = all_data[all_data['gpt_output'] == "mixed"]
    all_data_used['SVM_matched'] = np.where(all_data_used['SVM_label'] == all_data_used['gpt_output'], 1, 0)
    all_data_used['Natural_matched'] = np.where(all_data_used['Natural_Validation_Label'] == all_data_used['gpt_output'], 1, 0)
    all_data_used["ServRep_matched"] = np.zeros(shape = all_data_used.shape[0], dtype = np.int8)
    for i in range(all_data_used.shape[0]):
        str(all_data_used["ServRep_matched"][i]) = (all_data_used['gpt_output'][i] in all_data_used["ServRep_Validation_Label"][i])
    all_data_used["ServRep_matched"] = all_data_used["ServRep_matched"].astype(int)
    #all_data['ServRep_matched'] = np.where(all_data['gpt_output'] in all_data['ServRep_Validation_Label'], 1, 0)
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
def write_output(engine, temp, max_tokens, all_data, df_used):
    gpt = GPT(engine = engine, temperature = temp, max_tokens = max_tokens, output_prefix = "Sentiment:", append_output_prefix_to_query=True)
    gpt = add_examples(gpt, df_used)
    out_df, mixed_df = write_prompts(all_data, gpt)
    print("Mixed DF")
    print(mixed_df)
    SVM_df = out_df[["Phrase_text", "gpt_output", "SVM_matched"]]
    NV_df = out_df[["Phrase_text", "gpt_output", "Natural_matched"]]
    SV_df = out_df[["Phrase_text", "gpt_output", "ServRep_matched"]]
    #out_df.drop("Sentiment_class_label", axis = 1, inplace = True)
    SVM_accuracy = ((np.sum(SVM_df['SVM_matched'])) / (SVM_df.shape[0])) * 100
    print("SVM Accuracy: {}".format(SVM_accuracy))
    NV_accuracy = ((np.sum(NV_df['Natural_matched'])) / (NV_df.shape[0])) * 100
    print("Natural Validation Accuracy: {}".format(NV_accuracy))
    SV_accuracy = ((np.sum(SV_df['ServRep_matched'])) / (SV_df.shape[0])) * 100
    print("ServRep Accuracy: {}".format(SV_accuracy))
    SVM_df.to_csv('GPTvsSVM_mixed.txt', header = ['PHRASE_TEXT', 'GPT_OUTPUT', 'MATCHED'], index = None, sep = " ", mode = 'a')
    #print("###" * 50)
    #print("Instances GPT-3 categorised as Mixed:")
    #mixed_df.to_csv("outzeroshot.txt", sep = " ", mode = "a")
    line_prepender('GPTvsSVM_mixed.txt', "SVM_ACCURACY: {:.2f}, TEMPERATURE: {}".format(SVM_accuracy, temp))
    NV_df.to_csv('GPTvsNatural_mixed.txt', header = ['PHRASE_TEXT', 'GPT_OUTPUT', 'MATCHED'], index = None, sep = " ", mode = 'a')
    line_prepender('GPTvsNatural_mixed.txt', "NATURAL_ACCURACY: {:.2f}, TEMPERATURE: {}".format(NV_accuracy, temp))
    SV_df.to_csv('GPTvsServRep_mixed.txt', header = ['PHRASE_TEXT', 'GPT_OUTPUT', 'MATCHED'], index = None, sep = " ", mode = 'a')
    line_prepender('GPTvsServRep_mixed.txt', "SERVREP_ACCURACY: {:.2f}, TEMPERATURE: {}".format(SV_accuracy, temp))



def main(filename, trainf, temp = None, max_tokens = 3):
    with open('GPT_SECRET_KEY.json') as f:
        data = json.load(f)
    openai.api_key = data["API_KEY"]
    #all_data = transform_txt(filename = filename, trainf = trainf)
    all_data, df_used = transform_txt(inputf = filename, trainf = trainf)
    # if training data is used (n indicating number of training instances per category of sentiment)
    write_output(engine = "instruct-davinci-beta", temp = temp, max_tokens = max_tokens, all_data = all_data, df_used = df_used)
    #write_output(engine = "instruct-davinci-beta", temp = temp, max_tokens = max_tokens, all_data = all_data, df_used = df_used, num_training_per_cate = num_training_per_cate)

        
if __name__ == "__main__":
    #num_testing_per_cate = int(input("Enter number of randomly chosen testing instances per each sentiment category (an int): "))
    # This is always 10
    #num_training_per_cate = int(input("Enter number of randomly chosen training instances per each sentiment category (an int): "))
    # This is 1, 3, 5, 7
    """try:
        temp = float(input("Enter desired temperature setting (a floating point number from 0.0 to 1.0) (Hit \"Enter\" to set at 0.0): "))
    except SyntaxError:
        pass"""
    temp = 0.0
    max_tokens = 3
    filename = "teahslabels.csv"
    trainf = "train.txt"
    main(filename, trainf, temp, max_tokens)




