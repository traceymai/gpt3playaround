from pathlib import Path
from valence.gpt3pipe import line_prepender
parent_dir = Path(__file__).parent
parent_dir.mkdir(parents=True, exist_ok=True)
filepath_valence = parent_dir / "valence_fb_sep.txt"
filepath_arousal = parent_dir / "arousal_fb_sep.txt"
with filepath_valence.open(mode="w+", encoding="utf8") as f1:
    f1.truncate(0)
    f1.close()
with filepath_arousal.open(mode="w+", encoding="utf8") as f2:
    f2.truncate(0)
    f2.close()
with open("dataset_rescaled_final.txt", "r", encoding="utf8") as f:
    header = f.readline()
    lines = f.readline()
    while True:
        if lines == "":
            print(lines)
            break
        line = lines.rsplit(",", 2)
        phrase = line[0]
        valence = line[1]
        arousal = line[2].strip("\r\n")
        with filepath_valence.open(mode="a", encoding="utf8") as f1:
            f1.write(valence + ", " + phrase + "\n")
            f1.close()
        with filepath_arousal.open(mode="a", encoding="utf8") as f2:
            f2.write(arousal + ", " + phrase + "\n")
            f2.close()
        lines = f.readline()
line_prepender(filepath_valence, line="Valence, Phrase")
line_prepender(filepath_arousal, line="Arousal, Phrase")
