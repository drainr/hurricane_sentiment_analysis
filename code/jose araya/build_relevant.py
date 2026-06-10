"""
build_relevant.py — adds a relevance layer on top of merge_reddit's output
without touching any existing file. It flags each in-window row as on-topic or
not and as a bot or not, then writes the flagged superset (nothing dropped) plus
reddit_relevant.csv, the cleaned corpus we actually analyze.

Relevance is judged per thread, not per comment: a reply under a hurricane post
counts as on-topic even with no keyword of its own, which a comment-level filter
would wrongly throw away.

Built with help from Claude.
"""

from pathlib import Path
import sys
import pandas as pd

COMB = Path(__file__).resolve().parents[2] / "data" / "reddit" / "combined"

# automod / bot boilerplate — not human sentiment
BOT_AUTHORS = {"AutoModerator"}
BOT_PHRASE = "I am a bot, and this action was performed automatically"


def main() -> int:
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

    # ---- file 2: analysis corpus -------------------------------------------
    rel = out[out["thread_relevant"] & ~out["is_bot"]].copy()
    rel_cols = ["id", "type", "platform", "hurricane", "days_from_landfall",
                "source_type", "subreddit", "keyword_hit", "parent_post_id",
                "text", "text_length"]
    rel[rel_cols].to_csv(COMB / "reddit_relevant.csv", index=False)

    # ---- report ------------------------------------------------------------
    n = len(out)
    print(f"in-window rows (unchanged source):   {n:,}")
    print(f"  bots/automod flagged:              {int(out.is_bot.sum()):,}")
    print(f"  thread-relevant:                   {int(out.thread_relevant.sum()):,} "
          f"({round(100*out.thread_relevant.mean(),1)}%)")
    print(f"reddit_relevant.csv (relevant & ~bot): {len(rel):,}")
    print("\nrelevant corpus by hurricane / type:")
    print(rel.groupby(["hurricane", "type"]).size().to_string())
    print("\nrelevant corpus by subreddit:")
    g = rel.groupby(["hurricane", "subreddit"]).size().rename("rows")
    print(g.sort_values(ascending=False).to_string())
    print(f"\nWrote reddit_clean_flagged.csv + reddit_relevant.csv to {COMB}")
    print("(reddit_clean.csv and raw files untouched)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
