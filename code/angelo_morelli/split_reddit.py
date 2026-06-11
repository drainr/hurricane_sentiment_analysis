"""
split_reddit.py — modified ver of split_facebook to split reddit data by type

Outputs (data/reddit/*):
  *_posts.csv     rows where type == "post"
  *_comments.csv  rows where type == "comment"

Built with help from Claude.
"""

from pathlib import Path
import pandas as pd

WH = Path(__file__).resolve().parents[2] / "data" / "reddit" / "combined"
SRC = WH / "reddit_relevant_vader.csv"


def main() -> int:
    if not SRC.exists():
        raise SystemExit(f"no facebook_master.csv at {SRC}")

    df = pd.read_csv(SRC, dtype=str, keep_default_na=False)

    types = set(df["type"].unique())
    unexpected = types - {"post", "comment"}
    if unexpected:
        raise SystemExit(f"unexpected type values (not post/comment): {unexpected}")

    posts = df[df["type"] == "post"]
    comments = df[df["type"] == "comment"]

    # no rows lost or duplicated
    assert len(posts) + len(comments) == len(df), "split does not add back to master"

    posts.to_csv(WH / "reddit_relevant_posts_vader.csv", index=False)
    comments.to_csv(WH / "reddit_relevant_comments_vader.csv", index=False)

    print(f"facebook_posts.csv    {len(posts):,} rows")
    print(f"facebook_comments.csv {len(comments):,} rows")
    print(f"master left intact    {len(df):,} rows ({SRC.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
