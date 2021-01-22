import pandas as pd
import sys
def change_to_strings(sent_score):
    if sent_score.strip() == "1.0":
        return "Positive"
    elif sent_score.strip() == "0.0":
        return "Neutral"
    elif sent_score.strip() == "-1.0":
        return "Negative"
    else:
        raise ValueError("Training sentiment score needs to be 1.0 (Positive), 0.0 (Neutral) or -1.0 (Negative)")
# def get_input_prams():
#     if len(sys.argv) > 1:
#         configPath = sys.argv[1]
#     else:
#         configPath = input("Please enter path to JSON config file: ")
#     with open(configPath, encoding="utf8") as jsonDataFile:
#         _data = json.load(jsonDataFile)
#


with open("sm_text_sentiment_training_new.txt", "r", encoding="utf8") as f:
    allDataList = []
    for i, line in enumerate(f):
        allDataList.append(l)
    allDataList = [x.strip("\r\n") for x in allDataList]
    allDataList = [x.split(",", 1) for x in allDataList]
    labelList = [x[0] for x in allDataList]
    phraseList = [x[1] for x in allDataList]
    f.close()

with open("training_data_fin.txt", "r", encoding="utf8") as f:
    trainDataList = f.readlines()[1:]
    trainDataList = [x.strip("\r\n") for x in trainDataList]
    trainDataList = [x.split(":->",1) for x in trainDataList]
    labelTrainList = [x[0] for x in trainDataList]
    labelTrainList = [change_to_strings(x) for x in labelTrainList]
    phraseTrainList = [x[1].strip() for x in trainDataList]
    f.close()

sentiment_prompt = "This is a tweet sentiment classifier\n"
for ind in range(len(phraseTrainList)):
    sentiment_prompt += "Tweet:" + phraseTrainList[ind] + "\n"
    sentiment_prompt += "Sentiment: ", labelTrainList[ind] + "\n"
    sentiment_prompt += "###\n"
sentiment_prompt += "Tweet text\n"
#for





