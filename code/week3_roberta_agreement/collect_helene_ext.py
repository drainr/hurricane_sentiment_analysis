#!/usr/bin/env python3
"""
collect_helene_ext.py — APPEND-ONLY extension pull for Helene.

Advisor (2026-06-18) extended the Helene window back to day -5. Helene currently
starts at day -3 (Sep 23); this adds the two missing days -5 / -4 = Sep 21 + 22.

This is a faithful clone of code/jose araya/collect_subreddit.py (same subreddits,
same keyword tagger, same schema, all-posts soft-tag) with three deliberate
changes so it CANNOT touch existing data:
  1. window = Sep 21 .. Sep 22 only  (after=2024-09-21, before=2024-09-23)
  2. output dir = data/reddit/helene_ext/  (new sibling folder; existing
     data/reddit/helene/ is never opened)
  3. STRICT new-days-only comments: a new post's full tree is pulled, but only
     comments dated Sep 21 or Sep 22 are kept (advisor's call). Posts are kept
     regardless (preserves Helene's full-subreddit baseline).

Reversible: delete data/reddit/helene_ext/ to undo completely.
Built with help from Claude.
"""

import csv
import datetime
import os
import re
import sys
import time

import requests

STORM = "helene"
WINDOW = {"after": "2024-09-21", "before": "2024-09-23"}   # Sep 21 + Sep 22
KEEP_DATES = {"2024-09-21", "2024-09-22"}                   # strict comment filter

SUBREDDITS = [
    "TropicalWeather", "hurricane", "HurricaneHelene", "asheville",
    "sarasota", "tampa", "florida", "Georgia", "NorthCarolina",
]
# identical to collect_subreddit.py — storm name added automatically
KEYWORDS = ["hurricane", "storm", "flood", "power", "weather",
            "outage", "category", "fema", "noaa"]

PER_REQUEST_SLEEP = 1.5
RETRY_BACKOFF = 5

BASE = "https://arctic-shift.photon-reddit.com/api"
HEADERS = {"User-Agent": "ncf-hurricane-research/0.1 (academic; jose araya)"}
OUT_DIR = os.path.join(sys.path[0], "..", "data", "reddit", "helene_ext")

POST_COLS = ["id", "subreddit", "author", "created_utc", "created_date",
             "num_comments", "score", "title", "selftext",
             "hurricane", "source_type", "keyword_hit"]
COMMENT_COLS = ["id", "link_id", "parent_id", "subreddit", "author",
                "created_utc", "created_date", "score", "body",
                "hurricane", "source_type", "keyword_hit"]


def get_json(endpoint, params, tries=5):
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
    return datetime.datetime.fromtimestamp(
        ts, datetime.UTC).strftime("%Y-%m-%d %H:%M") if ts else ""


def make_keyword_matcher(storm):
    terms = KEYWORDS + [storm]
    patterns = [(t, re.compile(rf"\b{re.escape(t)}\b", re.I)) for t in terms]

    def match(text):
        text = text or ""
        return "|".join(t for t, p in patterns if p.search(text))
    return match


def pull_posts(subreddit, after, before):
    cursor, rows = None, []
    while True:
        params = {"subreddit": subreddit, "before": before,
                  "limit": 100, "sort": "asc"}
        params["after"] = cursor if cursor is not None else after
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


def collect_one(storm, subreddit, window):
    match = make_keyword_matcher(storm)
    posts = pull_posts(subreddit, window["after"], window["before"])
    post_rows, comment_rows = [], []
    kept_comments = dropped_comments = 0
    for i, p in enumerate(posts, 1):
        post_rows.append({
            "id": p.get("id"), "subreddit": p.get("subreddit"),
            "author": p.get("author"), "created_utc": p.get("created_utc"),
            "created_date": to_date(p.get("created_utc")),
            "num_comments": p.get("num_comments"), "score": p.get("score"),
            "title": p.get("title"), "selftext": p.get("selftext"),
            "hurricane": storm, "source_type": "community_discussion",
            "keyword_hit": match(f"{p.get('title','')} {p.get('selftext','')}"),
        })
        try:
            tree = pull_comment_tree(p["id"])
        except Exception as e:
            print(f"      post {p['id']} comment ERROR {e}")
            tree = []
        for c in tree:
            cdate = to_date(c.get("created_utc"))
            if cdate[:10] not in KEEP_DATES:      # STRICT: new days only
                dropped_comments += 1
                continue
            kept_comments += 1
            comment_rows.append({
                "id": c.get("id"), "link_id": c.get("link_id"),
                "parent_id": c.get("parent_id"), "subreddit": c.get("subreddit"),
                "author": c.get("author"), "created_utc": c.get("created_utc"),
                "created_date": cdate,
                "score": c.get("score"), "body": c.get("body"),
                "hurricane": storm, "source_type": "community_discussion",
                "keyword_hit": match(c.get("body")),
            })
        if i % 20 == 0:
            print(f"      ...{i}/{len(posts)} posts, {kept_comments} kept comments so far")
        time.sleep(PER_REQUEST_SLEEP)
    print(f"      comments kept (Sep 21-22): {kept_comments}, dropped (later dates): {dropped_comments}")
    return post_rows, comment_rows


def save(rows, cols, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    grand_posts = grand_comments = 0
    print(f"\n{'='*64}\n  HELENE EXT  {WINDOW['after']} -> {WINDOW['before']} (days -5,-4)\n{'='*64}")
    for sub in SUBREDDITS:
        print(f"\n  r/{sub} ...")
        try:
            post_rows, comment_rows = collect_one(STORM, sub, WINDOW)
        except Exception as e:
            print(f"  r/{sub}  FAILED: {e}  (skipping; re-run to retry)")
            continue
        save(post_rows, POST_COLS,
             os.path.join(OUT_DIR, f"posts_{STORM}_{sub}.csv"))
        save(comment_rows, COMMENT_COLS,
             os.path.join(OUT_DIR, f"comments_{STORM}_{sub}.csv"))
        grand_posts += len(post_rows)
        grand_comments += len(comment_rows)
        print(f"  r/{sub}  DONE: {len(post_rows)} posts, {len(comment_rows)} comments -> data/reddit/helene_ext/")
        time.sleep(PER_REQUEST_SLEEP)

    print(f"\n{'='*64}\n  TOTAL: {grand_posts} posts, {grand_comments} comments (Sep 21-22)")
    print("  Saved to data/reddit/helene_ext/ . Existing data/reddit/helene/ untouched.")
    print("  Merge later AFTER extending merge_reddit WINDOW['helene'] to (-5, 1).")


if __name__ == "__main__":
    main()
