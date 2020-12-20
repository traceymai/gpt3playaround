from gpt import GPT
from gpt import Example
import pandas as pd 
import numpy as np
import openai
import json

def change_labels(num):
    if num == 1:
        return "positive"
    elif num == 0:
        return "neutral"
    elif num == -1:
        return "negative"
def write_prompts_all_text(filename):
    with open('GPT_SECRET_KEY.json') as f:
        data = json.load(f)
    openai.api_key = data["API_KEY"]
    gpt = GPT(engine = "davinci", temperature = 0.0, max_tokens = 100, output_prefix = "output (positive/neutral/negative):")
    all_data = pd.read_csv(filename, header = 0, encoding = "utf8", sep = ":->")
    all_data['Sentiment_class_label'] = all_data['Sentiment_class_label'].apply(lambda x: change_labels(x))
    for row in range(all_data.shape[0]):
        gpt.add_example(Example(all_data['Phrase_text'][row], all_data['Sentiment_class_label'][row]))
    return gpt.get_prime_text()

