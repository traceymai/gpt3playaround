import pandas as pd
import numpy as np
df = pd.read_csv("dataset-fb-valence-arousal-anon.csv", header=0)
df["Valence"] = df[["Valence1", "Valence2"]].apply(lambda x: int(max(x["Valence1"], x["Valence2"])) if (abs(x["Valence1"] - x["Valence2"]) >= 2) else round(np.mean([x["Valence1"], x["Valence2"]]), 2), axis = 1)
df["Arousal"] = df[["Arousal1", "Arousal2"]].apply(lambda x: int(max(x["Arousal1"], x["Arousal2"])) if (abs(x["Arousal1"] - x["Arousal2"]) >= 2) else round(np.mean([x["Arousal1"], x["Arousal2"]]), 2), axis = 1)
df.drop(columns = ["Valence1", "Valence2", "Arousal1", "Arousal2"], inplace=True)
df.to_csv("dataset_rescaled_final.txt", index=False)
print(df)
print("FINISH")