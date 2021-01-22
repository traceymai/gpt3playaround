import pandas as pd
with open("sm_text_sentiment_training_new.txt", "r", encoding="utf8") as f:
    allText = f.readlines()
    allText = [x.strip("\r\n") for x in allText]
    f.close()
allText = [x.split(",", 1) for x in allText]
sentiment_array = [x[0] for x in allText]
phrase_text = [x[1] for x in allText]
with open("")
print("FINISH")