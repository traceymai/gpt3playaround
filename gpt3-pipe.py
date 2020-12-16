from IPython import get_ipython
get_ipython().system('pip install openai')
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
        
def transform_txt(filename, n): # n is the number of input instances wanted for each sentiment category
    """
    This function reads input sentences and associated sentiments 
    """
    # reading text filename into a Dataframe
    data = pd.read_csv(filename, header = 0, encoding = "utf8", sep = ":->")
    df_used = data.groupby('Sentiment_class_label').head(n).reset_index(drop = True)
    df_used['Sentiment_class_label'] = df_used['Sentiment_class_label'].apply(lambda x: change_labels(x))
    return df_used
    
def add_examples(gpt_instance, df_used, n): # n is the number of Example instances to "train" GPT-3 on
    df_subset = df_used.groupby('Sentiment_class_label').head(n).reset_index(drop = True)
    for row in range(df_subset.shape[0]):
        gpt_instance.add_example(Example(df_subset['Phrase_text'][row], df_subset['Sentiment_class_label'][row]))
    return gpt_instance
    
# A function to write prompt into GPT-3 API:
def write_prompts(df_used, gpt_instance):
    df_used['gpt_output'] = df_used["Phrase_text"].apply(lambda x: gpt_instance.submit_request(x).choices[0].text.replace("output (positive/neutral/negative):", "").strip("\n"))
    df_used['matched'] = np.where(df_used['Sentiment_class_label'] == df_used['gpt_output'], 1, 0)
    # dropping Sentiment_class_label column
    df_used.drop(['Sentiment_class_label'], axis = 1)
    return df_used

def main():
    
    with open('GPT_SECRET_KEY.json') as f:
        data = json.load(f)
    openai.api_key = data["API_KEY"]
    gpt = GPT(engine = "davinci", temperature = 0.5, max_tokens = 100, output_prefix = "output (positive/neutral/negative):")
    df_used = transform_txt("sm_text_sentiment_training.txt", 20)
    gpt = add_examples(gpt, df_used, 3)
    out_df = write_prompts(df_used, gpt)
    out_df.drop("Sentiment_class_label", axis = 1, inplace = True)
    accuracy = ((np.sum(out_df['matched'])) / (out_df.shape[0])) * 100
    out_df.to_csv('outf.txt', header = ['Phrase_text', 'gpt_output', 'matched'], index = None, sep = " ", mode = 'a')

if __name__ == "__main__":
    main()

