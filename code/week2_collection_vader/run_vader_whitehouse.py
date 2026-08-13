"""
run_vader_whitehouse.py — score the split White House files with the shared VADER scorer.

Week 8 reproducibility fix. The file previously named `run_vader_wh.py` was a
byte-identical copy of `run_vader_facebook.py` (committed under the wrong name in
dfa5587), so nothing in the repo actually produced the White House VADER outputs
even though `data/vader/whitehouse_threads_*_vader.csv` existed. This script
closes that gap: it is `run_vader_reddit.py` pointed at the two WH files, using
the same `code/common/vader_sentiment.py` scorer every other source goes through.

Verified in the Week 8 pass to reproduce both canonical outputs byte for byte
(12 posts, 2,193 comments).

Input   data/reddit/whitehouse/whitehouse_threads_{posts,comments}.csv
Output  data/vader/whitehouse_threads_{posts,comments}_vader.csv
"""

from __future__ import annotations
import os, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))         # code/week2_collection_vader/
REPO = os.path.dirname(os.path.dirname(HERE))             # repo root
sys.path.insert(0, os.path.join(REPO, "code", "common"))  # shared VADER scorer (code/common)
from vader_sentiment import analyze_sentiment, label_sentiment  # noqa: E402

IN_DIR  = os.path.join(REPO, "data", "reddit", "whitehouse")
OUT_DIR = os.path.join(REPO, "data", "vader")

# WH posts are source_type="government", comments "government_response"; the two
# stay in separate files so H7 can compare them (see the 2026-06-10 decision).
FILES = ["whitehouse_threads_posts.csv", "whitehouse_threads_comments.csv"]


def score(name: str) -> None:
    """Score one WH file and write it to data/vader/ with a _vader suffix."""
    df = pd.read_csv(os.path.join(IN_DIR, name))

    scores = df["text"].apply(lambda t: analyze_sentiment(str(t)))
    df["vader_neg"]      = scores.apply(lambda d: d["neg"])
    df["vader_neu"]      = scores.apply(lambda d: d["neu"])
    df["vader_pos"]      = scores.apply(lambda d: d["pos"])
    df["vader_compound"] = scores.apply(lambda d: d["compound"])
    df["vader_label"]    = df["vader_compound"].apply(label_sentiment)

    out = os.path.join(OUT_DIR, name.replace(".csv", "_vader.csv"))
    df.to_csv(out, index=False)
    print(f"[scored] {len(df)} rows -> {out}")
    print("        ", df["vader_label"].value_counts().to_dict())


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    for f in FILES:
        score(f)
