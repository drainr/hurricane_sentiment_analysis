#!/usr/bin/env python3
"""
collect_subreddit.py — pulls full Reddit posts and their comment trees for each
(subreddit x hurricane window) off the Arctic Shift archive. It's set up for my
half of the split (Helene + Debby), keeps every row, and just soft-tags each one
with keyword_hit so the cleaning and merge step downstream can filter later.

It's a big pull, so run it in the background or one hurricane at a time.

Built with help from Claude.
"""

import csv
import datetime
import os
import re
import sys
import time

import requests

HURRICANES = {
    "debby":  {"after": "2024-07-31", "before": "2024-08-06"},  # Jul 31 - Aug 5
    "helene": {"after": "2024-09-23", "before": "2024-09-28"},  # Sep 23 - Sep 27
}

SUBREDDITS = {
    "debby": [
        "TropicalWeather", "hurricane", "sarasota", "tampa",
        "florida", "Georgia", "NorthCarolina",
    ],
    "helene": [
        "TropicalWeather", "hurricane", "HurricaneHelene", "asheville",
        "sarasota", "tampa", "florida", "Georgia", "NorthCarolina",
    ],
}

# Keywords to TAG (not filter). The storm's own name is added automatically.
KEYWORDS = ["hurricane", "storm", "flood", "power", "weather",
            "outage", "category", "fema", "noaa"]

PER_REQUEST_SLEEP = 1.5
RETRY_BACKOFF = 5
# =========================================================================

BASE = "https://arctic-shift.photon-reddit.com/api"
HEADERS = {"User-Agent": "ncf-hurricane-research/0.1 (academic; jose araya)"}
OUT_DIR = os.path.join(sys.path[0], "..", "..", "data", "reddit")

POST_COLS = ["id", "subreddit", "author", "created_utc", "created_date",
             "num_comments", "score", "title", "selftext",
             "hurricane", "source_type", "keyword_hit"]
COMMENT_COLS = ["id", "link_id", "parent_id", "subreddit", "author",
                "created_utc", "created_date", "score", "body",
                "hurricane", "source_type", "keyword_hit"]


def get_json(endpoint, params, tries=5):
    """GET with retries; heavy queries answer 422 'slow down' (retryable)."""
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
    """Return a fn(text)->'flood|power' using word boundaries. Adds storm name."""
    terms = KEYWORDS + [storm]                       # e.g. + "helene"
    patterns = [(t, re.compile(rf"\b{re.escape(t)}\b", re.I)) for t in terms]

    def match(text):
        text = text or ""
        return "|".join(t for t, p in patterns if p.search(text))
    return match


def pull_posts(subreddit, after, before):
    """Every post in the window, paginated."""
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
    """Every comment under one post, paginated."""
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
            comment_rows.append({
                "id": c.get("id"), "link_id": c.get("link_id"),
                "parent_id": c.get("parent_id"), "subreddit": c.get("subreddit"),
                "author": c.get("author"), "created_utc": c.get("created_utc"),
                "created_date": to_date(c.get("created_utc")),
                "score": c.get("score"), "body": c.get("body"),
                "hurricane": storm, "source_type": "community_discussion",
                "keyword_hit": match(c.get("body")),
            })
        if i % 20 == 0:
            print(f"      ...{i}/{len(posts)} posts, {len(comment_rows)} comments so far")
        time.sleep(PER_REQUEST_SLEEP)
    return post_rows, comment_rows


def save(rows, cols, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def main():
    grand_posts = grand_comments = 0
    for storm, window in HURRICANES.items():
        out = os.path.join(OUT_DIR, storm)
        os.makedirs(out, exist_ok=True)
        print(f"\n{'='*64}\n  {storm.upper()}  {window['after']} -> {window['before']}\n{'='*64}")
        for sub in SUBREDDITS.get(storm, []):
            print(f"\n  r/{sub} ...")
            try:
                post_rows, comment_rows = collect_one(storm, sub, window)
            except Exception as e:
                print(f"  r/{sub}  FAILED: {e}  (skipping; re-run to retry)")
                continue
            save(post_rows, POST_COLS,
                 os.path.join(out, f"posts_{storm}_{sub}.csv"))
            save(comment_rows, COMMENT_COLS,
                 os.path.join(out, f"comments_{storm}_{sub}.csv"))
            grand_posts += len(post_rows)
            grand_comments += len(comment_rows)
            print(f"  r/{sub}  DONE: {len(post_rows)} posts, {len(comment_rows)} comments -> data/{storm}/")
            time.sleep(PER_REQUEST_SLEEP)

    print(f"\n{'='*64}\n  TOTAL: {grand_posts} posts, {grand_comments} comments")
    print("  Saved per-subreddit in ./data/<hurricane>/ . Merge with teammate later.")
    print("  Raw pull — cleaning/VADER is the downstream merge step.")


if __name__ == "__main__":
    main()
