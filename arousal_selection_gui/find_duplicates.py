import pandas as pd
df = pd.read_csv("outmerged_unmatched.txt", header = None)
df.columns = ["Phrase_text", "Arousal_trained", "Arousal_zeroshot", "Matched"]
df = df.drop_duplicates(subset = "Phrase_text", ignore_index = True)
print(df)