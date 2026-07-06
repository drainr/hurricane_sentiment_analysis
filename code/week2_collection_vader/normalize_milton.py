"""
normalize_milton.py — aligns the teammate's Milton pull to the same shape as the
Debby/Helene files so merge_reddit.py and build_relevant.py run untouched.

For each of his data/reddit/milton/<sub>_posts.csv / <sub>_comments.csv it:
  1. derives created_date (naive UTC "%Y-%m-%d %H:%M") from his tz-aware created_utc
  2. injects source_type = "community_discussion"
  3. regenerates keyword_hit at row level with the SAME matcher collect_subreddit
     uses (his was thread-propagated; this makes the column mean the same thing
     across all three storms)
and writes posts_milton_<sub>.csv / comments_milton_<sub>.csv (the naming the
merge glob expects). His originals are left in place — the glob ignores them.

Built with help from Claude.
"""

from pathlib import Path
import re
import pandas as pd

MILTON = Path(__file__).resolve().parents[2] / "data" / "reddit" / "milton"
STORM = "milton"

# identical to collect_subreddit.py
KEYWORDS = ["hurricane", "storm", "flood", "power", "weather",
            "outage", "category", "fema", "noaa"]
_PATS = [(t, re.compile(rf"\b{re.escape(t)}\b", re.I)) for t in KEYWORDS + [STORM]]


def keyword_hit(text: str) -> str:
    text = text or ""
    return "|".join(t for t, p in _PATS if p.search(text))


def to_created_date(s: pd.Series) -> pd.Series:
    """tz-aware ISO -> naive UTC 'YYYY-MM-DD HH:MM' (matches Debby/Helene)."""
    dt = pd.to_datetime(s, utc=True, errors="coerce").dt.tz_localize(None)
    return dt.dt.strftime("%Y-%m-%d %H:%M")


def normalize(path: Path, kind: str) -> int:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["created_date"] = to_created_date(df["created_utc"])
    df["source_type"] = "community_discussion"
    if kind == "posts":
        text = (df["title"].fillna("") + " " + df["selftext"].fillna(""))
    else:
        text = df["body"].fillna("")
    df["keyword_hit"] = text.map(keyword_hit)

    sub = path.name.replace(f"_{kind}.csv", "")        # florida_posts.csv -> florida
    out = MILTON / f"{kind}_{STORM}_{sub}.csv"
    df.to_csv(out, index=False)
    return len(df)


def main() -> int:
    if not MILTON.exists():
        raise SystemExit(f"no milton dir at {MILTON}")
    tp = tc = 0
    for path in sorted(MILTON.glob("*_posts.csv")):
        if path.name.startswith("posts_"):           # skip our own output on re-run
            continue
        tp += normalize(path, "posts")
    for path in sorted(MILTON.glob("*_comments.csv")):
        if path.name.startswith("comments_"):
            continue
        tc += normalize(path, "comments")
    print(f"normalized -> posts_milton_*.csv ({tp:,} posts), "
          f"comments_milton_*.csv ({tc:,} comments)")
    print("originals left in place (merge glob ignores <sub>_posts.csv naming)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
