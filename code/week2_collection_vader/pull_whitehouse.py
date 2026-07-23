#!/usr/bin/env python3
"""
pull_whitehouse.py  —  collect the White House's own Reddit posts + their
comment trees during the 2024 hurricanes (the official-communication source).

Why this one is different from the others:
    The White House is the ONLY org that actually POSTS on Reddit (FEMA/NOAA
    don't — those are mentions only, see pull_org_mentions.py). So here we
    collect its account directly, the same way the Fall 2024 plan intended.

    Two source types come out of this, per the Week 2 tagging scheme:
      - the WH posts themselves      -> source_type = "government"
      - the comments people left      -> source_type = "government_response"
    These feed H7 (how official hurricane communication was received).

IMPORTANT handle note (verified):
    - COLLECT with author = "WhiteHouse"  (the handle the Biden WH posted under
      in 2024 — that's what the archive stored).
    - CITE in the paper as u/whitehouse46 (the post-Jan-2025 NARA archive name).
    - Querying author=whitehouse46 returns 0 — archives freeze the name as of
      post date. Do NOT change WH_AUTHOR below.

Method: Arctic Shift /posts/search?author=WhiteHouse for the posts, then
/comments/search?link_id=<post id> (paginated) for each post's full tree.

Output -> ../../data/reddit/:
    whitehouse_posts_<stamp>.csv          (one row per WH post)
    whitehouse_comments_<stamp>.csv       (all comments across those posts)

Raw pull — no cleaning/scoring (that's the downstream merge step).
"""

import csv
import datetime
import os
import sys
import time

import requests

# ============================ CONFIG — EDIT ME ============================
WH_AUTHOR = "WhiteHouse"          # collect handle — do NOT use whitehouse46
SEASON = {"after": "2024-08-01", "before": "2024-11-15"}   # scan whole season

# Tag each post by which storm its TITLE/SELFTEXT names — date can't separate
# them because the WH posted about Helene recovery and Milton response in the
# same mid-Oct window. A post naming both is tagged "helene+milton"; a post
# naming none (FTC, Halloween, etc.) is "other".
STORM_KEYWORDS = {
    "debby":  ["debby"],
    "helene": ["helene"],
    "milton": ["milton"],
}
PER_REQUEST_SLEEP = 1.5
RETRY_BACKOFF = 5
# =========================================================================

BASE = "https://arctic-shift.photon-reddit.com/api"
HEADERS = {"User-Agent": "ncf-hurricane-research/0.1 (academic; jose araya)"}
OUT_DIR = os.path.join(sys.path[0], "..", "..", "data", "reddit")

POST_COLS = ["id", "subreddit", "author", "created_utc", "created_date",
             "num_comments", "score", "title", "selftext",
             "hurricane", "source_type"]
COMMENT_COLS = ["id", "link_id", "parent_id", "subreddit", "author",
                "created_utc", "created_date", "score", "body",
                "hurricane", "source_type"]


def get_json(endpoint, params, tries=5):
    """GET with retries; the free API answers heavy queries with a 422
    'slow down' timeout that's retryable."""
    for attempt in range(tries):
        try:
            r = requests.get(f"{BASE}/{endpoint}", params=params,
                             headers=HEADERS, timeout=45)
            if r.status_code == 422 and "slow down" in r.text.lower():
                raise ValueError("server timeout (slow down)")
            r.raise_for_status()
            data = r.json().get("data")
            if data is None:
                raise ValueError(r.json().get("error", "null data"))
            return data
        except (requests.RequestException, ValueError):
            if attempt == tries - 1:
                raise
            time.sleep(RETRY_BACKOFF * (attempt + 1))


def to_date(ts):
    """Format a Unix timestamp as 'YYYY-MM-DD HH:MM' UTC, or '' if missing."""
    return datetime.datetime.fromtimestamp(
        ts, datetime.UTC).strftime("%Y-%m-%d %H:%M") if ts else ""


def which_hurricane(title, selftext):
    """Tag a post by which storm(s) its text names. Both -> 'helene+milton';
    none -> 'other'. More reliable than date (the storms overlap in time)."""
    text = f"{title or ''} {selftext or ''}".lower()
    hits = [storm for storm, kws in STORM_KEYWORDS.items()
            if any(kw in text for kw in kws)]
    return "+".join(hits) if hits else "other"


def pull_wh_posts():
    """All WhiteHouse posts in the season window, paginated past the 100-cap."""
    cursor, rows = None, []
    while True:
        params = {"author": WH_AUTHOR, "before": SEASON["before"],
                  "limit": 100, "sort": "asc"}
        params["after"] = cursor if cursor is not None else SEASON["after"]
        data = get_json("posts/search", params)
        if not data:
            break
        rows.extend(data)
        cursor = data[-1]["created_utc"]
        if len(data) < 100:
            break
        time.sleep(PER_REQUEST_SLEEP)
    return rows


def pull_comment_tree(post_id):
    """All comments under one WH post, paginated."""
    cursor, rows = None, []
    while True:
        params = {"link_id": post_id, "limit": 100, "sort": "asc"}
        if cursor is not None:
            params["after"] = cursor
        data = get_json("comments/search", params)
        if not data:
            break
        rows.extend(data)
        cursor = data[-1]["created_utc"]
        if len(data) < 100:
            break
        time.sleep(PER_REQUEST_SLEEP)
    return rows


def main():
    """Collect the White House's own posts and every comment beneath them.

    Posts are tagged source_type 'government' and comments 'government_response',
    the split H7 rests on. Collected under the author handle 'WhiteHouse', which
    is what the archive froze at post time; the paper cites u/whitehouse46.
    """
    os.makedirs(OUT_DIR, exist_ok=True)

    posts = pull_wh_posts()
    print(f"WhiteHouse posts found ({SEASON['after']} -> {SEASON['before']}): {len(posts)}\n")

    post_rows, comment_rows = [], []
    for p in posts:
        created = to_date(p.get("created_utc"))
        storm = which_hurricane(p.get("title"), p.get("selftext"))
        post_rows.append({
            "id": p.get("id"), "subreddit": p.get("subreddit"),
            "author": p.get("author"), "created_utc": p.get("created_utc"),
            "created_date": created, "num_comments": p.get("num_comments"),
            "score": p.get("score"), "title": p.get("title"),
            "selftext": p.get("selftext"),
            "hurricane": storm, "source_type": "government",
        })
        # pull this post's comment tree
        try:
            tree = pull_comment_tree(p["id"])
        except Exception as e:
            print(f"  r/{p.get('subreddit'):16s} {p['id']}  COMMENT ERROR {e}")
            tree = []
        for c in tree:
            comment_rows.append({
                "id": c.get("id"), "link_id": c.get("link_id"),
                "parent_id": c.get("parent_id"), "subreddit": c.get("subreddit"),
                "author": c.get("author"), "created_utc": c.get("created_utc"),
                "created_date": to_date(c.get("created_utc")),
                "score": c.get("score"), "body": c.get("body"),
                "hurricane": storm, "source_type": "government_response",
            })
        title = (p.get("title") or "")[:50].replace("\n", " ")
        print(f"  {storm:7s} r/{p.get('subreddit'):16s} {p['id']}  "
              f"{len(tree):4d} comments | {title}")
        time.sleep(PER_REQUEST_SLEEP)

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    posts_path = os.path.join(OUT_DIR, f"whitehouse_posts_{stamp}.csv")
    comments_path = os.path.join(OUT_DIR, f"whitehouse_comments_{stamp}.csv")
    with open(posts_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=POST_COLS, extrasaction="ignore")
        w.writeheader(); w.writerows(post_rows)
    with open(comments_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COMMENT_COLS, extrasaction="ignore")
        w.writeheader(); w.writerows(comment_rows)

    print(f"\n{len(post_rows)} posts -> {os.path.relpath(posts_path)}")
    print(f"{len(comment_rows)} comments -> {os.path.relpath(comments_path)}")
    print("Cite the account as u/whitehouse46 in the paper. Raw pull (clean/score downstream).")


if __name__ == "__main__":
    main()
