"""
for use with reddit data (modified ver of run_vader_facebook without all the comparison code)
"""

from __future__ import annotations
import os, sys
import pandas as pd
 
HERE = os.path.dirname(os.path.abspath(__file__))   # code/<your folder>/
REPO = os.path.dirname(os.path.dirname(HERE))        # repo root
sys.path.insert(0, HERE)
from vader_sentiment import analyze_sentiment, label_sentiment  # noqa: E402 
 
INPUT  = os.path.join(REPO, "data", "reddit", "combined", "reddit_relevant.csv")
OUTPUT = os.path.join(REPO, "data", "reddit", "combined", "reddit_relevant_vader.csv")
 
# ── Score ─────────────────────────────────────────────────────────────────────
 
df = pd.read_csv(INPUT)
 
scores = df["text"].apply(lambda t: analyze_sentiment(str(t)))
df["vader_neg"]      = scores.apply(lambda d: d["neg"])
df["vader_neu"]      = scores.apply(lambda d: d["neu"])
df["vader_pos"]      = scores.apply(lambda d: d["pos"])
df["vader_compound"] = scores.apply(lambda d: d["compound"])
df["vader_label"]    = df["vader_compound"].apply(label_sentiment)
 
df.to_csv(OUTPUT, index=False)
 
print(f"[scored] {len(df)} rows -> {OUTPUT}")
print(df["vader_label"].value_counts().to_dict())