"""
build_relevant.py — adds a relevance layer on top of merge_reddit's output
without touching any existing file. It flags each in-window row as on-topic or
not and as a bot or not, then writes the flagged superset (nothing dropped) plus
reddit_relevant.csv, the cleaned corpus we actually analyze.

Relevance is judged per thread, not per comment: a reply under a hurricane post
counts as on-topic even with no keyword of its own, which a comment-level filter
would wrongly throw away.

White House thread posts/comments (data/reddit/whitehouse/) are a separate
data source and are kept out of reddit_relevant.csv entirely — they get their
own file, whitehouse_relevant.csv. Because the White House threads live inside
subreddits we also scrape generally, the same post/comment id can show up in
both sources; any row in the general corpus whose id also appears in the
whitehouse files is dropped from reddit_relevant.csv, so each id lives in
exactly one of the two output files.

Built with help from Claude.
"""

from pathlib import Path
import sys
import pandas as pd

COMB = Path(__file__).resolve().parents[2] / "data" / "reddit" / "combined"
WH = Path(__file__).resolve().parents[2] / "data" / "reddit" / "whitehouse"

# automod / bot boilerplate — not human sentiment
BOT_AUTHORS = {"AutoModerator"}
BOT_PHRASE = "I am a bot, and this action was performed automatically"

# schema of the final analysis corpus — also the schema the pre-cleaned
# whitehouse_threads_posts.csv / whitehouse_threads_comments.csv already use
REL_COLS = ["id", "type", "platform", "hurricane", "days_from_landfall",
            "source_type", "subreddit", "subreddit_category", "keyword_hit",
            "parent_post_id", "text", "text_length"]


def load_whitehouse() -> pd.DataFrame:
    """Load pre-cleaned White House thread posts + comments, if present.

    These files are already in REL_COLS format, so no relevance/bot logic
    is applied to them — they're just validated and deduped against
    themselves before being written out as their own corpus.
    """
    files = {
        "posts": WH / "whitehouse_threads_posts.csv",
        "comments": WH / "whitehouse_threads_comments.csv",
    }
    frames = []
    for label, f in files.items():
        if not f.exists():
            print(f"note: {f} not found — skipping White House {label}")
            continue
        df = pd.read_csv(f, dtype=str, keep_default_na=False)
        missing = [c for c in REL_COLS if c not in df.columns]
        if missing:
            sys.exit(f"{f} is missing expected columns: {missing}")
        frames.append(df[REL_COLS])

    if not frames:
        return pd.DataFrame(columns=REL_COLS)

    wh = pd.concat(frames, ignore_index=True)

    # ids should already be bare (no t1_/t3_ prefix) and unique, but
    # normalize defensively so id matching against the main corpus is solid
    wh["id"] = wh["id"].str.strip()

    # numeric columns come back as strings from dtype=str read — align with
    # the dtypes reddit_relevant.csv already uses
    for col in ("days_from_landfall", "text_length"):
        wh[col] = pd.to_numeric(wh[col], errors="coerce")

    dupe_in_wh = int(wh["id"].duplicated().sum())
    if dupe_in_wh:
        print(f"  whitehouse posts+comments, duplicate ids within source: {dupe_in_wh:,} (dropped)")
        wh = wh.drop_duplicates(subset="id", keep="first")

    return wh


def main() -> int:
    """Build the thread-relevance corpus from the merged Reddit files.

    Writes reddit_clean_flagged.csv (every in-window row, flagged but nothing
    dropped) and reddit_relevant.csv (thread-relevant, non-bot rows only).
    Relevance is measured at THREAD level: if a post matches a storm keyword,
    its whole comment tree is kept, because replies under a megathread are on
    topic without carrying a keyword of their own. This version also removes
    the White House posts and comments that the keyword pull had swept into the
    Reddit corpus, giving the canonical 3,413 posts / 121,053 comments.
    """
    for f in ("reddit_clean.csv", "reddit_posts_all.csv", "reddit_comments_all.csv"):
        if not (COMB / f).exists():
            sys.exit(f"missing {COMB / f} — run merge_reddit.py first")

    clean = pd.read_csv(COMB / "reddit_clean.csv")
    posts = pd.read_csv(COMB / "reddit_posts_all.csv", dtype=str, keep_default_na=False)
    coms = pd.read_csv(COMB / "reddit_comments_all.csv", dtype=str, keep_default_na=False)

    # storm-relevant post ids (post has any keyword_hit)
    rel_post_ids = set(posts.loc[posts["keyword_hit"].str.len() > 0, "id"])

    # per-id lookups from raw: keyword_hit, author, and parent post id
    kw = pd.concat([posts[["id", "keyword_hit", "author"]],
                    coms[["id", "keyword_hit", "author"]]], ignore_index=True)
    kw = kw.drop_duplicates(subset="id", keep="first").set_index("id")
    parent = coms.assign(
        parent_post_id=coms["link_id"].str.replace("t3_", "", regex=False)
    ).drop_duplicates(subset="id", keep="first").set_index("id")["parent_post_id"]

    out = clean.copy()
    out["id"] = out["id"].astype(str).str.strip()
    out["keyword_hit"] = out["id"].map(kw["keyword_hit"]).fillna("")
    out["author"] = out["id"].map(kw["author"]).fillna("")
    # posts are their own parent; comments use link_id
    out["parent_post_id"] = out["id"].map(parent)
    out.loc[out["type"] == "post", "parent_post_id"] = out.loc[out["type"] == "post", "id"]

    own_kw = out["keyword_hit"].str.len() > 0
    parent_rel = out["parent_post_id"].isin(rel_post_ids)
    out["thread_relevant"] = own_kw | parent_rel

    out["is_bot"] = (out["author"].isin(BOT_AUTHORS)
                     | out["text"].str.contains(BOT_PHRASE, regex=False, na=False))

    # ---- file 1: flagged superset (nothing dropped) ------------------------
    flagged_cols = ["id", "type", "platform", "hurricane", "days_from_landfall",
                    "source_type", "subreddit", "author", "keyword_hit",
                    "parent_post_id", "thread_relevant", "is_bot",
                    "text", "text_length"]
    out[flagged_cols].to_csv(COMB / "reddit_clean_flagged.csv", index=False)

    # ---- load whitehouse corpus (its own separate output) ------------------
    wh = load_whitehouse()
    wh_ids = set(wh["id"])

    # ---- file 2: analysis corpus (whitehouse ids excluded) -----------------
    rel = out[out["thread_relevant"] & ~out["is_bot"]].copy()
    rel = rel[REL_COLS]
    n_rel_before_wh_exclusion = len(rel)

    n_excluded_as_whitehouse = int(rel["id"].isin(wh_ids).sum())
    if n_excluded_as_whitehouse:
        rel = rel[~rel["id"].isin(wh_ids)].reset_index(drop=True)

    rel.to_csv(COMB / "reddit_relevant.csv", index=False)

    # ---- file 3: whitehouse corpus, kept separate ---------------------------
    if len(wh):
        wh.to_csv(COMB / "whitehouse_relevant.csv", index=False)

    # ---- report ------------------------------------------------------------
    n = len(out)
    print(f"in-window rows (unchanged source):   {n:,}")
    print(f"  bots/automod flagged:              {int(out.is_bot.sum()):,}")
    print(f"  thread-relevant:                   {int(out.thread_relevant.sum()):,} "
          f"({round(100*out.thread_relevant.mean(),1)}%)")
    print(f"reddit_relevant.csv before whitehouse exclusion: {n_rel_before_wh_exclusion:,}")
    if len(wh):
        print(f"whitehouse posts+comments loaded:      {len(wh):,}")
        print(f"  also present in general corpus (excluded from reddit_relevant.csv): {n_excluded_as_whitehouse:,}")
    print(f"reddit_relevant.csv (final, general corpus only): {len(rel):,}")
    print(f"whitehouse_relevant.csv (separate whitehouse corpus): {len(wh):,}")
    print("\nrelevant corpus by hurricane / type:")
    print(rel.groupby(["hurricane", "type"]).size().to_string())
    print("\nrelevant corpus by subreddit:")
    g = rel.groupby(["hurricane", "subreddit"]).size().rename("rows")
    print(g.sort_values(ascending=False).to_string())
    print(f"\nWrote reddit_clean_flagged.csv + reddit_relevant.csv + whitehouse_relevant.csv to {COMB}")
    print("(reddit_clean.csv and raw files untouched)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())