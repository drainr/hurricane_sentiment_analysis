"""
merge_reddit.py — combines the per-subreddit Reddit CSVs into a raw layer (posts
and comments kept separate, since their schemas differ) and a cleaned layer,
reddit_clean.csv, where deleted/short/duplicate rows are dropped and everything
is restricted to each storm's event window.

Safe to re-run: it globs whatever hurricane folders exist under data/, so once
Milton's data lands you just drop it in and run this again.

Built with help from Claude.
"""

from pathlib import Path
import sys
import pandas as pd

# --- config -----------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "reddit"
OUT_DIR = DATA_DIR / "combined"

# Landfall day = 0 (project hurricane timeline)
LANDFALL = {
    "debby": pd.Timestamp("2024-08-05"),
    "helene": pd.Timestamp("2024-09-26"),
    "milton": pd.Timestamp("2024-10-09"),
}

MIN_WORDS = 3                       # drop comments/posts shorter than this
DELETED = {"[deleted]", "[removed]", ""}

# Layer 2 only: keep rows whose OWN timestamp falls in the Fall-2024 window
# (inclusive days_from_landfall bounds, matching the Facebook collection
# windows). Reddit comments carry real timestamps, so threads
# accrue replies for months; we restrict to the event window for apples-to-apples
# comparability with the day-bounded Facebook data. Raw Layer-1 files keep ALL rows.
WINDOW = {            # (min_days_from_landfall, max_days_from_landfall)
    "debby":  (-5, 0),    # Jul 31 - Aug 5
    "helene": (-3, 1),    # Sep 23 - Sep 27
    "milton": (-4, 0),    # Oct 5 - Oct 9
}


def _read_many(pattern: str) -> pd.DataFrame:
    """Read+concat every CSV matching data/*/<pattern>. Tags nothing extra —
    provenance (subreddit/hurricane/source_type) already lives in the columns."""
    files = sorted(DATA_DIR.glob(f"*/{pattern}"))
    if not files:
        return pd.DataFrame()
    frames = []
    for f in files:
        df = pd.read_csv(f, dtype=str, keep_default_na=False)
        df["_src_file"] = f.parent.name + "/" + f.name   # audit trail
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    print(f"  {pattern:20s} {len(files):2d} files -> {len(out):,} rows")
    return out


def _days_from_landfall(df: pd.DataFrame) -> pd.Series:
    dt = pd.to_datetime(df["created_date"], errors="coerce").dt.normalize()
    land = df["hurricane"].str.lower().map(LANDFALL)
    return (dt - land).dt.days


def main() -> int:
    if not DATA_DIR.exists():
        sys.exit(f"no data dir at {DATA_DIR}")
    OUT_DIR.mkdir(exist_ok=True)

    # ---- Layer 1: raw combined, posts and comments separate ----------------
    print("Layer 1 (raw combined):")
    posts = _read_many("posts_*.csv")
    comments = _read_many("comments_*.csv")
    if posts.empty and comments.empty:
        sys.exit("found no posts_*.csv or comments_*.csv under data/*/")

    posts.to_csv(OUT_DIR / "reddit_posts_all.csv", index=False)
    comments.to_csv(OUT_DIR / "reddit_comments_all.csv", index=False)

    # ---- Layer 2: unified, cleaned, analysis-ready -------------------------
    print("Layer 2 (reddit_clean.csv):")

    p = posts.copy()
    p["type"] = "post"
    p["text"] = (p["title"].fillna("") + " " + p["selftext"].fillna("")).str.strip()

    c = comments.copy()
    c["type"] = "comment"
    c["text"] = c["body"].fillna("").str.strip()

    cols = ["id", "type", "hurricane", "source_type", "subreddit", "text",
            "created_date"]
    unified = pd.concat([p[cols], c[cols]], ignore_index=True)
    unified["platform"] = "reddit"

    before = len(unified)

    # clean: drop deleted/removed, then short, then dedupe by id
    unified["text"] = unified["text"].str.strip()
    unified = unified[~unified["text"].isin(DELETED)]
    n_del = before - len(unified)

    word_count = unified["text"].str.split().str.len()
    unified = unified[word_count >= MIN_WORDS]
    n_short = before - n_del - len(unified)

    unified = unified.drop_duplicates(subset="id", keep="first")
    n_dup = before - n_del - n_short - len(unified)

    unified["days_from_landfall"] = _days_from_landfall(unified)

    # window filter (Layer 2 only) — keep rows whose own timestamp is in-window
    lo = unified["hurricane"].str.lower().map(lambda h: WINDOW[h][0])
    hi = unified["hurricane"].str.lower().map(lambda h: WINDOW[h][1])
    pre_win = len(unified)
    unified = unified[(unified["days_from_landfall"] >= lo)
                      & (unified["days_from_landfall"] <= hi)]
    n_win = pre_win - len(unified)

    unified["text_length"] = unified["text"].str.len()

    final_cols = ["id", "type", "platform", "hurricane", "days_from_landfall",
                  "source_type", "subreddit", "text", "text_length"]
    unified = unified[final_cols]
    unified.to_csv(OUT_DIR / "reddit_clean.csv", index=False)

    # ---- report ------------------------------------------------------------
    print(f"\n  raw rows in:        {before:,}")
    print(f"  - deleted/removed:  {n_del:,}")
    print(f"  - < {MIN_WORDS} words:       {n_short:,}")
    print(f"  - duplicate ids:    {n_dup:,}")
    print(f"  - outside window:   {n_win:,}")
    print(f"  clean rows out:     {len(unified):,}")
    print("\n  by hurricane / type:")
    print(unified.groupby(["hurricane", "type"]).size().to_string())
    bad = unified["days_from_landfall"].isna().sum()
    if bad:
        print(f"\n  WARNING: {bad:,} rows have NaN days_from_landfall "
              "(unparseable date or hurricane not in LANDFALL map)")
    print(f"\nWrote 3 files to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
