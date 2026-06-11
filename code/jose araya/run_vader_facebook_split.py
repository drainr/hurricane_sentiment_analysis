"""
run_vader_facebook_split.py — scores the split Facebook files (facebook_posts.csv
and facebook_comments.csv) through the SAME shared VADER scorer used everywhere
else (vader_sentiment.py). 

No reproduction/comparison step here — that was the one-time validation done in
run_vader_facebook.py. This just applies the already-validated scorer to the two
split corpora so posts and comments can be analyzed separately.

Built with help from Claude.
"""

from pathlib import Path
import sys
import pandas as pd

HERE = Path(__file__).resolve().parent                 # code/jose araya/
sys.path.insert(0, str(HERE))
from vader_sentiment import analyze_sentiment, label_sentiment  # noqa: E402

FB = HERE.parents[1] / "data" / "facebook"
FILES = ["facebook_posts.csv", "facebook_comments.csv"]


def score_file(name: str) -> None:
    src = FB / name
    if not src.exists():
        raise SystemExit(f"missing {src} — run split_facebook.py first")

    df = pd.read_csv(src, dtype=str, keep_default_na=False)

    scores = df["text"].apply(lambda t: analyze_sentiment(str(t)))
    df["vader_neg"] = scores.apply(lambda d: d["neg"])
    df["vader_neu"] = scores.apply(lambda d: d["neu"])
    df["vader_pos"] = scores.apply(lambda d: d["pos"])
    df["vader_compound"] = scores.apply(lambda d: d["compound"])
    df["vader_label"] = df["vader_compound"].apply(label_sentiment)

    out = FB / name.replace(".csv", "_vader.csv")
    df.to_csv(out, index=False)
    print(f"[scored] {name:24s} {len(df):,} rows -> {out.name}")
    print(f"         labels: {df['vader_label'].value_counts().to_dict()}")
    print(f"         mean compound: {df['vader_compound'].astype(float).mean():.4f}")


def main() -> int:
    for name in FILES:
        score_file(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
