"""Week 2 (Student B) task: re-scores facebook_master.csv through our shared
VADER scorer (vader_sentiment.py), then checks the new numbers against the Fall
2024 students' original scores on a 50-row sample and logs where, and why, they
differ. It reads the student files read-only and only writes new outputs.

Built with help from Claude.
"""
from __future__ import annotations
import csv, glob, os, re, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))          # code/jose araya/
REPO = os.path.dirname(os.path.dirname(HERE))              # repo root
sys.path.insert(0, HERE)
from vader_sentiment import analyze_sentiment, label_sentiment  # noqa: E402

MASTER = os.path.join(REPO, "data", "facebook", "facebook_master.csv")
WORK = os.path.join(REPO, "data", "facebook", "student_originals")
OUT_DIR = os.path.join(REPO, "data", "facebook")
DOC_DIR = os.path.join(REPO, "docs")
os.makedirs(OUT_DIR, exist_ok=True)

def norm(t: str) -> str:
    """Normalize text for matching across raw-vs-standardized copies."""
    if not isinstance(t, str):
        return ""
    return re.sub(r"\s+", " ", t).strip().lower()

_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF←-⇿⌀-⏿]")
def has_emoji(t: str) -> bool:
    return bool(_EMOJI.search(t)) if isinstance(t, str) else False

def classify(row):
    """Attribute the most likely cause of a new-vs-original discrepancy."""
    if row["delta"] <= 1e-4:
        return "reproduced (label rule)" if row["label_flip"] else "reproduced"
    if has_emoji(row["text"]):
        return "library: emoji lexicon (std scores emoji; NLTK=0)"
    if not row["exact"]:
        return "text cleaning (whitespace/CR/encoding)"
    if row["orig_compound"] == 0.0:
        return "orig score 0 on sentimental text (student bug?)"
    return "library: word-lexicon/punctuation version drift"

# ---- 1. Score facebook_master.csv through the unified pipeline -------------
df = pd.read_csv(MASTER)
scores = df["text"].apply(lambda t: analyze_sentiment(str(t)))
df["vader_neg"] = scores.apply(lambda d: d["neg"])
df["vader_neu"] = scores.apply(lambda d: d["neu"])
df["vader_pos"] = scores.apply(lambda d: d["pos"])
df["vader_compound"] = scores.apply(lambda d: d["compound"])
df["vader_label"] = df["vader_compound"].apply(label_sentiment)
out_master = os.path.join(OUT_DIR, "facebook_master_vader.csv")
df.to_csv(out_master, index=False)
print(f"[scored] {len(df)} rows -> {out_master}")
print(df["vader_label"].value_counts().to_dict())

# ---- 2. Build original-score lookup from student output CSVs --------------
# In every student output CSV the layout is: text, ...scores..., compound, label
# i.e. compound = row[-2], label = row[-1]. (col ORDER of neg/neu/pos differs,
# but compound/label positions are stable.) Helene has no per-row output.
orig = {}            # norm(text) -> (compound, orig_label, student, raw_text)
collisions = 0
def ingest(pattern, student):
    global collisions
    for path in glob.glob(pattern):
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            r = list(csv.reader(f))
        for row in r[1:]:                      # skip header (post text / labels)
            if len(row) < 3:
                continue
            try:
                comp = float(row[-2])
            except ValueError:
                continue                       # header-ish / non-numeric row
            key = norm(row[0])
            if not key:
                continue
            if key in orig and abs(orig[key][0] - comp) > 1e-9:
                collisions += 1
            orig[key] = (comp, row[-1].strip(), student, row[0])

ingest(os.path.join(WORK, "PaigeMiltonCode/Files/Sentiment/VADER_Milton_*.csv"), "Grimes/Milton")
ingest(os.path.join(WORK, "PaigeMiltonCode/Files/GregDeeOriginal/GD_VADER_PostInfo.csv"), "Grimes/Milton")
ingest(os.path.join(WORK, "HurricaneDebbyCode/writeSentimentAnalysis/*.csv"), "Bowers/Debby")
ingest(os.path.join(WORK, "HurricaneDebbyCode/writeGregDeePosts/*.csv"), "Bowers/Debby")
print(f"[originals] {len(orig)} unique scored texts ({collisions} text collisions w/ differing scores)")

# ---- 3. Match master rows to originals, compute deltas --------------------
df["_key"] = df["text"].apply(norm)
df["_orig"] = df["_key"].map(lambda k: orig.get(k))
matched = df[df["_orig"].notna()].copy()
matched["orig_compound"] = matched["_orig"].apply(lambda x: x[0])
matched["orig_label_raw"] = matched["_orig"].apply(lambda x: x[1])
matched["orig_student"] = matched["_orig"].apply(lambda x: x[2])
matched["orig_raw"] = matched["_orig"].apply(lambda x: x[3])
matched["exact"] = matched["text"].astype(str) == matched["orig_raw"].astype(str)
matched["delta"] = (matched["vader_compound"] - matched["orig_compound"]).abs()

print(f"[matched] {len(matched)} / {len(df)} master rows matched a per-row original")
print("  by student:", matched["orig_student"].value_counts().to_dict())
ex = matched[matched["exact"]]
nx = matched[~matched["exact"]]
print(f"  EXACT raw-text matches: {len(ex)}  -> max |delta| = {ex['delta'].max():.6f}, "
      f"delta>1e-4: {(ex['delta']>1e-4).sum()}  (lexicon-reproduction check)")
print(f"  NORMALIZED-only matches: {len(nx)} -> max |delta| = {nx['delta'].max():.6f}, "
      f"delta>1e-4: {(nx['delta']>1e-4).sum()}  (text-cleaning differences)")
print(f"  overall max |delta compound| = {matched['delta'].max():.6f}; "
      f"rows with delta>1e-4 = {(matched['delta']>1e-4).sum()}")

# Map original labels to our 3-class vocabulary for a fair label comparison
LABMAP = {"POS": "positive", "NEG": "negative", "NEU": "neutral",
          "POSITIVE": "positive", "NEGATIVE": "negative", "NEUTRAL": "neutral"}
matched["orig_label"] = matched["orig_label_raw"].str.upper().map(LABMAP)
matched["label_flip"] = matched["vader_label"] != matched["orig_label"]
print(f"  label flips: {matched['label_flip'].sum()} "
      f"(of {matched['orig_label'].notna().sum()} comparable)")

matched["cause"] = matched.apply(classify, axis=1)
print("\n[discrepancy causes — all matched rows]")
print(matched["cause"].value_counts().to_string())

# ---- 4. 50-row sample (stratified across the matched students) ------------
parts = [g.sample(min(len(g), 25), random_state=42)
         for _, g in matched.groupby("orig_student")]
sample = pd.concat(parts).sample(min(50, sum(len(p) for p in parts)),
                                 random_state=42).sort_values("delta", ascending=False)
cols = ["id", "hurricane", "type", "orig_student", "exact", "text",
        "orig_compound", "vader_compound", "delta",
        "orig_label", "vader_label", "label_flip", "cause"]
sample_out = os.path.join(DOC_DIR, "vader_reproduction_50row.csv")
sample[cols].to_csv(sample_out, index=False)
print(f"[sample] 50-row comparison -> {sample_out}")
print(sample[["orig_student", "exact", "orig_compound", "vader_compound", "delta",
              "orig_label", "vader_label", "label_flip"]].head(50).to_string())

# ---- 5. Top discrepancies for the write-up --------------------------------
print("\n[top 10 |delta| among NORMALIZED-only matches] (cleaning-induced)")
print(nx.nlargest(10, "delta")[["orig_student", "text", "orig_raw",
      "orig_compound", "vader_compound", "delta"]].to_string())
