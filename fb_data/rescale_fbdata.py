import pandas as pd
import numpy as np

df = pd.read_csv("dataset-fb-valence-arousal-anon.csv", header = 0)
df["Valence_final_bool"] = np.where(abs(df["Valence1"] - df["Valence2"]) >= 2, True, False)
df["Valence_final"] = np.where(df["Valence_final_bool"]==False, )
df["Arousal_final_book"] = np.where(abs(df["Arousal1"] - df["Arousal2"]) >= 2, True, False)
print("end")