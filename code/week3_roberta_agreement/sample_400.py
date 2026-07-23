"""
sample_for_labeling.py
Draws a stratified random sample from the hurricane sentiment CSVs
for manual annotation.

Sample breakdown (400 total):
  - 150 Facebook comments
  - 150 Reddit comments
  - 50  White House thread comments
  - 50  Posts (mixed across sources, proportional per source)

Output columns: id, platform, text, label, gratitude_tag
"""

import pandas as pd
import numpy as np
import os

SEED = 100

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

SOURCES = {
    "facebook_posts":      (os.path.join(DATA_DIR, "facebook", "facebook_posts.csv"),                          "facebook",   "post"),
    "facebook_comments":   (os.path.join(DATA_DIR, "facebook", "facebook_comments.csv"),                       "facebook",   "comment"),
    "reddit_posts":        (os.path.join(DATA_DIR, "reddit", "combined", "reddit_relevant_posts.csv"),         "reddit",     "post"),
    "reddit_comments":     (os.path.join(DATA_DIR, "reddit", "combined", "reddit_relevant_comments.csv"),      "reddit",     "comment"),
    "whitehouse_posts":    (os.path.join(DATA_DIR, "reddit", "whitehouse", "whitehouse_threads_posts.csv"),    "whitehouse", "post"),
    "whitehouse_comments": (os.path.join(DATA_DIR, "reddit", "whitehouse", "whitehouse_threads_comments.csv"), "whitehouse", "comment"),
}

COL_MAP = {
    "id":      ["id", "comment_id", "post_id", "link_id", "name"],
    "text":    ["text", "body", "selftext", "message", "content"],
    "is_post": ["is_post", "post_type", "type"],
}


def find_col(df, aliases):
    """Return the first alias present in the DataFrame's columns, or None."""
    for a in aliases:
        if a in df.columns:
            return a
    return None


def load_and_tag(filepath, platform, post_type):
    """Load one source file and tag every row with its platform and post type.

    Column names differ across sources, so the id and text columns are resolved
    through COL_MAP aliases.
    """
    df = pd.read_csv(filepath, low_memory=False)

    id_col   = find_col(df, COL_MAP["id"])
    text_col = find_col(df, COL_MAP["text"])

    if text_col is None:
        raise ValueError(f"Cannot find a text column in {filepath}. Columns: {df.columns.tolist()}")

    type_col = find_col(df, COL_MAP["is_post"])
    if type_col:
        mask = df[type_col].astype(str).str.lower().isin(["true", "1", "post", "submission"])
        df = df[mask] if post_type == "post" else df[~mask]

    df = df[df[text_col].notna() & (df[text_col].astype(str).str.strip() != "")]

    out = pd.DataFrame()
    out["id"]       = df[id_col].astype(str) if id_col else df.index.astype(str)
    out["platform"] = platform
    out["text"]     = df[text_col].astype(str).str.strip()
    out["_source"]  = f"{platform}_{post_type}"
    out["type"]     = post_type

    return out.reset_index(drop=True)


def proportional_sample(dfs_by_source: dict, total: int) -> pd.DataFrame:
    """
    Sample `total` rows from multiple DataFrames proportionally by their size,
    guaranteeing at least 1 row per non-empty source.
    """
    non_empty = {k: v for k, v in dfs_by_source.items() if len(v) > 0}
    if not non_empty:
        return pd.DataFrame()

    sizes     = {k: len(v) for k, v in non_empty.items()}
    total_avail = sum(sizes.values())
    # Proportional allocation
    alloc = {k: max(1, round(total * s / total_avail)) for k, s in sizes.items()}

    # Trim rounding overshoot
    while sum(alloc.values()) > total:
        largest = max(alloc, key=alloc.get)
        alloc[largest] -= 1

    # Fill rounding undershoot
    while sum(alloc.values()) < total:
        # Give extra to the source with the most remaining headroom
        headroom = {k: sizes[k] - alloc[k] for k in alloc}
        if max(headroom.values()) == 0:
            break
        largest_headroom = max(headroom, key=headroom.get)
        alloc[largest_headroom] += 1

    pieces = []
    for k, df in non_empty.items():
        n = min(alloc[k], len(df))
        pieces.append(df.sample(n=n, random_state=SEED))

    result = pd.concat(pieces, ignore_index=True)
    print(f"    Post allocation: { {k: min(alloc[k], sizes[k]) for k in non_empty} }")
    return result


def simple_sample(df, n, label):
    """Take n rows at random, or everything if fewer than n are available."""
    if len(df) == 0:
        print(f"  ⚠  No rows available for '{label}'.")
        return df.copy()
    if len(df) < n:
        print(f"  ⚠  Only {len(df)} rows available for '{label}'; taking all.")
        return df.copy()
    return df.sample(n=n, random_state=SEED)


def main():
    """Draw the stratified 400-item annotation sample.

    Targets 150 Facebook, 150 Reddit community and 50 White House comments plus
    50 posts, which both annotators then label independently.
    """
    print("Loading source files...")

    facebook_comments = []
    reddit_comments   = []
    wh_comments       = []
    post_sources      = {}   # key → df, for proportional post sampling

    for key, (path, platform, ptype) in SOURCES.items():
        if not os.path.exists(path):
            print(f"  ⚠  File not found, skipping: {path}")
            continue
        print(f"  Loading {key} ({platform}, {ptype})...")
        df = load_and_tag(path, platform, ptype)

        if ptype == "comment":
            if platform == "facebook":
                facebook_comments.append(df)
            elif platform == "reddit":
                reddit_comments.append(df)
            elif platform == "whitehouse":
                wh_comments.append(df)
        else:
            post_sources[key] = df

    # Pool comment strata
    def pool(dfs):
        """Concatenate the per-file frames for one platform and drop duplicate ids."""
        return pd.concat(dfs, ignore_index=True).drop_duplicates(subset="id") if dfs else pd.DataFrame()

    fb_pool  = pool(facebook_comments)
    rd_pool  = pool(reddit_comments)
    wh_pool  = pool(wh_comments)

    # Dedup post sources individually, then proportional sample
    post_sources = {k: v.drop_duplicates(subset="id") for k, v in post_sources.items()}

    print(f"\nPool sizes — FB comments: {len(fb_pool)}, Reddit comments: {len(rd_pool)}, "
          f"WH comments: {len(wh_pool)}, Post sources: { {k: len(v) for k, v in post_sources.items()} }")

    s_fb   = simple_sample(fb_pool,  150, "facebook comments")
    s_rd   = simple_sample(rd_pool,  150, "reddit comments")
    s_wh   = simple_sample(wh_pool,   50, "whitehouse comments")
    s_post = proportional_sample(post_sources, 50)

    sample = pd.concat([s_fb, s_rd, s_wh, s_post], ignore_index=True)
    sample = sample.drop(columns=["_type", "_source"], errors="ignore")

    sample["label"]        = ""
    sample["gratitude_tag"] = ""

    sample = sample.sample(frac=1, random_state=SEED).reset_index(drop=True)
    sample = sample[["id", "platform", "type", "text", "label", "gratitude_tag"]]

    out_path = os.path.join(os.path.dirname(__file__), "manual_label_sample.csv")
    sample.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"\n✅  Sample saved → {out_path}")
    print(f"   Rows: {len(sample)}  |  Columns: {list(sample.columns)}")
    print(f"   Platform breakdown:\n{sample['platform'].value_counts().to_string()}")


if __name__ == "__main__":
    main()