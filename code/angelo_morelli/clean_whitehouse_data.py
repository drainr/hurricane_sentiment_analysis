"""
clean_whitehouse_data.py
------------------------
Cleans whitehouse Reddit CSVs and merges everything into whitehouse_threads.csv.

Step 1 — Clean comments only (posts are kept as-is):
  - Remove rows where author == '[deleted]'
  - Remove rows where body == '[removed]'
  - Remove rows where body has fewer than 3 words

Step 2 — Build whitehouse_threads.csv with unified schema:
  id                : original Reddit id
  type              : 'post' or 'comment'
  platform          : 'reddit' (constant)
  days_from_landfall: empty (to be filled later)
  source_type       : 'government' for posts, 'government_response' for comments
  subreddit         : subreddit name
  keyword_hit       : keyword that matched
  parent_post_id    : for posts = own id; for comments = link_id (t3_ prefix stripped)
  text              : posts → title + '\\n' + selftext (if any); comments → body
  text_length       : len(text) in characters

Output files (written to DATA_DIR):
  *_comments_cleaned.csv   — one per hurricane
  whitehouse_threads.csv   — merged unified table
"""

import pandas as pd
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

DATA_DIR = Path("../../data/reddit/whitehouse")

# ── Helpers ───────────────────────────────────────────────────────────────────

def word_count(text: str) -> int:
    return len(text.split())


def clean_comments(path: Path):
    df = pd.read_csv(path)
    original_len = len(df)
    stats = {}

    mask_deleted = df["author"].astype(str).str.strip() == "[deleted]"
    stats["deleted_author"] = int(mask_deleted.sum())
    df = df[~mask_deleted].copy()

    mask_removed = df["body"].astype(str).str.strip() == "[removed]"
    stats["removed_body"] = int(mask_removed.sum())
    df = df[~mask_removed].copy()

    mask_short = df["body"].astype(str).apply(word_count) < 3
    stats["short_body"] = int(mask_short.sum())
    df = df[~mask_short].copy()

    stats["total_dropped"] = original_len - len(df)
    stats["remaining"] = len(df)
    return df, stats


def build_comment_rows(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    out["id"]                 = df["id"]
    out["type"]               = "comment"
    out["platform"]           = "reddit"
    out["hurricane"]          = df["hurricane"]
    out["days_from_landfall"] = ""
    out["source_type"]        = "government_response"
    out["subreddit"]          = df["subreddit"]
    out["keyword_hit"]        = df["keyword_hit"]
    # link_id is like 't3_abc123' — strip the prefix to match post ids
    out["parent_post_id"]     = df["link_id"].astype(str).str.replace(r"^t\d+_", "", regex=True)
    out["text"]               = df["body"].astype(str)
    out["text_length"]        = out["text"].str.len()
    return out


def build_post_rows(df: pd.DataFrame) -> pd.DataFrame:
    # Combine title + selftext; selftext may be NaN for link posts
    selftext = df["selftext"].fillna("").astype(str).str.strip()
    title    = df["title"].fillna("").astype(str).str.strip()
    text     = title.where(selftext == "", title + "\n" + selftext)

    out = pd.DataFrame()
    out["id"]                 = df["id"]
    out["type"]               = "post"
    out["platform"]           = "reddit"
    out["hurricane"]          = df["hurricane"]
    out["days_from_landfall"] = ""
    out["source_type"]        = "government"
    out["subreddit"]          = df["subreddit"]
    out["keyword_hit"]        = df["keyword_hit"]
    out["parent_post_id"]     = df["id"]          # posts are their own parent
    out["text"]               = text
    out["text_length"]        = out["text"].str.len()
    return out


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    comment_files = sorted(DATA_DIR.glob("*_comments.csv"))
    post_files    = sorted(DATA_DIR.glob("*_posts.csv"))

    if not comment_files and not post_files:
        print(f"No CSV files found in {DATA_DIR}. "
              "Make sure you run this script from the repo root.")
        return

    all_stats   = []
    thread_rows = []

    # ── Comments: clean then build unified rows ────────────────────────────────
    for path in comment_files:
        print(f"\nCleaning comments: {path.name}")
        df_clean, stats = clean_comments(path)

        out_path = path.with_name(path.stem + "_cleaned.csv")
        df_clean.to_csv(out_path, index=False)
        print(f"  → Saved: {out_path.name}")

        all_stats.append({"file": path.name, "type": "comments", **stats})
        thread_rows.append(build_comment_rows(df_clean))

    # ── Posts: no cleaning, just build unified rows ───────────────────────────
    for path in post_files:
        print(f"\nLoading posts (no cleaning): {path.name}")
        df = pd.read_csv(path)
        print(f"  → {len(df)} rows kept as-is")
        thread_rows.append(build_post_rows(df))

    # ── Merge and write whitehouse_threads.csv ────────────────────────────────
    threads = pd.concat(thread_rows, ignore_index=True)

    # Sort: posts before comments, then by id for readability
    type_order = {"post": 0, "comment": 1}
    threads["_sort"] = threads["type"].map(type_order)
    threads = threads.sort_values(["_sort", "id"]).drop(columns="_sort").reset_index(drop=True)

    out_path = DATA_DIR / "whitehouse_threads.csv"
    threads.to_csv(out_path, index=False)
    print(f"\n  → Merged file saved: {out_path}")
    print(f"     {len(threads)} total rows  "
          f"({(threads['type']=='post').sum()} posts, "
          f"{(threads['type']=='comment').sum()} comments)")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("CLEANING SUMMARY (comments only — posts untouched)")
    print("=" * 70)

    for s in all_stats:
        print(f"\n{s['file']}")
        print(f"  Deleted author rows removed : {s['deleted_author']}")
        print(f"  [removed] body rows removed : {s['removed_body']}")
        print(f"  Under-3-word body removed   : {s['short_body']}")
        print(f"  Total dropped               : {s['total_dropped']}")
        print(f"  Rows remaining              : {s['remaining']}")

    print("\nDone.")


if __name__ == "__main__":
    main()