#!/usr/bin/env python3
"""
collect_milton_ext.py — APPEND-ONLY extension pull for Milton.

Advisor (2026-06-18) extended the Milton window back to day -5. Milton currently
starts at day -4 (Oct 5); this adds the one missing day -5 = Oct 4.

Faithful clone of the teammate's collection method
(code/angelo_morelli/use_arctic_shift.py) WITH the normalize_milton step baked in,
so output is merge-ready and matches the existing posts_milton_* / comments_milton_*
schema exactly. Differences vs the original, all to protect existing data:
  1. window = Oct 4 only  (after=2024-10-04, before=2024-10-05)
  2. output dir = data/reddit/milton_ext/  (new sibling folder; existing
     data/reddit/milton/ is never opened)
  3. STRICT new-day-only comments (advisor's call): comments are pulled in the
     Oct-4 window and kept only if (a) dated Oct 4 and (b) under a matched Oct-4
     post — exactly the teammate's link_id filter, one day earlier.

Method parity with existing Milton: posts are keyword-FILTERED at collection
(substring, like the teammate), so Milton stays on-topic-only with no full-sub
baseline. keyword_hit is then regenerated with the word-boundary matcher
(like normalize_milton) so the column means the same thing across all storms.

Reversible: delete data/reddit/milton_ext/ to undo completely.
Built with help from Claude.
"""

import csv
import datetime
import os
import re
import sys
import time

import requests

STORM = "milton"
AFTER, BEFORE = "2024-10-04", "2024-10-05"     # Oct 4 only
KEEP_DATE = "2024-10-04"                         # strict comment filter

LOCATION_SUBS = ["sarasota", "tampa", "florida", "georgia", "northcarolina"]
HURRICANE_SUBS = ["hurricane", "tropicalweather"]
ALL_SUBS = LOCATION_SUBS + HURRICANE_SUBS

# identical keyword set to use_arctic_shift.py (includes storm name)
KEYWORDS = ["milton", "hurricane", "storm", "flood", "power", "weather",
            "outage", "category", "fema", "noaa"]
# word-boundary matcher for the FINAL keyword_hit (matches normalize_milton)
_PATS = [(t, re.compile(rf"\b{re.escape(t)}\b", re.I)) for t in KEYWORDS]

BASE = "https://arctic-shift.photon-reddit.com/api"
HEADERS = {"User-Agent": "ncf-hurricane-research/0.1 (academic; jose araya)"}
OUT_DIR = os.path.join(sys.path[0], "..", "data", "reddit", "milton_ext")

POST_COLS = ["id", "subreddit", "author", "created_utc", "num_comments",
             "title", "selftext", "score", "hurricane", "keyword_hit",
             "created_date", "source_type"]
COMMENT_COLS = ["id", "link_id", "parent_id", "subreddit", "author",
                "created_utc", "score", "body", "hurricane", "keyword_hit",
                "created_date", "source_type"]


def collect(kind, subreddit, after, before, tries=5):
    """Paginated pull of posts|comments for a subreddit in [after, before)."""
    url = f"{BASE}/{kind}/search"
    cursor, rows, seen = None, [], set()
    while True:
        params = {"limit": "auto", "sort": "asc", "subreddit": subreddit,
                  "before": before}
        params["after"] = cursor if cursor is not None else after
        for attempt in range(tries):
            try:
                r = requests.get(url, params=params, headers=HEADERS, timeout=45)
                if r.status_code in (422, 429):
                    raise ValueError("slow down")
                r.raise_for_status()
                break
            except (requests.RequestException, ValueError):
                if attempt == tries - 1:
                    raise
                time.sleep(5 * (attempt + 1))
        data = r.json().get("data") or []
        if not data:
            break
        for item in data:
            if item["id"] not in seen:
                seen.add(item["id"]); rows.append(item)
        cursor = data[-1]["created_utc"]
        if len(data) < 100:
            break
        time.sleep(1)
    return rows


def to_iso(ts):
    """Format a Unix timestamp as a tz-aware ISO 8601 string, or '' if missing."""
    return datetime.datetime.fromtimestamp(ts, datetime.UTC).isoformat() if ts else ""


def to_date(ts):
    """Format a Unix timestamp as 'YYYY-MM-DD HH:MM' UTC, or '' if missing."""
    return datetime.datetime.fromtimestamp(
        ts, datetime.UTC).strftime("%Y-%m-%d %H:%M") if ts else ""


def kw_hit(text):
    """Return the storm keywords present in this text, joined by '|' ('' if none)."""
    text = text or ""
    return "|".join(t for t, p in _PATS if p.search(text))


def substring_match(post):
    """Teammate's inclusion rule: keep a post if any keyword substring appears."""
    content = ((post.get("title") or "") + " " + (post.get("selftext") or "")).lower()
    return any(kw in content for kw in KEYWORDS)


def save(rows, cols, path):
    """Write rows to a CSV with a fixed column order, ignoring extra keys."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def collect_sub(sub):
    """Pull one subreddit's keyword-matching posts and their full comment trees.

    Mirrors the teammate's original Milton method (keyword-filtered posts, not a
    whole-subreddit pull) so the extra day is collected the same way as the rest
    of Milton.
    """
    posts_all = collect("posts", sub, AFTER, BEFORE)
    posts = []
    for p in posts_all:
        if not substring_match(p):
            continue
        text = f"{p.get('title','')} {p.get('selftext','')}"
        posts.append({
            "id": p.get("id"), "subreddit": p.get("subreddit"),
            "author": p.get("author"), "created_utc": to_iso(p.get("created_utc")),
            "num_comments": p.get("num_comments"), "title": p.get("title"),
            "selftext": p.get("selftext"), "score": p.get("score"),
            "hurricane": STORM, "keyword_hit": kw_hit(text),
            "created_date": to_date(p.get("created_utc")),
            "source_type": "community_discussion",
        })
    post_ids = {f"t3_{p['id']}" for p in posts}
    print(f"    {len(posts)} matched posts (from {len(posts_all)} total)")

    comments_all = collect("comments", sub, AFTER, BEFORE)
    comments = []
    for c in comments_all:
        if c.get("link_id") not in post_ids:          # only under matched posts
            continue
        cdate = to_date(c.get("created_utc"))
        if cdate[:10] != KEEP_DATE:                    # STRICT: Oct 4 only
            continue
        comments.append({
            "id": c.get("id"), "link_id": c.get("link_id"),
            "parent_id": c.get("parent_id"), "subreddit": c.get("subreddit"),
            "author": c.get("author"), "created_utc": to_iso(c.get("created_utc")),
            "score": c.get("score"), "body": c.get("body"),
            "hurricane": STORM, "keyword_hit": kw_hit(c.get("body")),
            "created_date": cdate, "source_type": "community_discussion",
        })
    print(f"    {len(comments)} comments (Oct 4, under matched posts; "
          f"from {len(comments_all)} sub-comments)")
    return posts, comments


def main():
    """Collect Milton's extra day into data/reddit/milton_ext/, append-only."""
    os.makedirs(OUT_DIR, exist_ok=True)
    gp = gc = 0
    print(f"\n{'='*64}\n  MILTON EXT  {AFTER} -> {BEFORE} (day -5)\n{'='*64}")
    for sub in ALL_SUBS:
        print(f"\n  r/{sub} ...")
        try:
            posts, comments = collect_sub(sub)
        except Exception as e:
            print(f"  r/{sub}  FAILED: {e}  (skipping; re-run to retry)")
            continue
        save(posts, POST_COLS, os.path.join(OUT_DIR, f"posts_{STORM}_{sub}.csv"))
        save(comments, COMMENT_COLS, os.path.join(OUT_DIR, f"comments_{STORM}_{sub}.csv"))
        gp += len(posts); gc += len(comments)
        print(f"  r/{sub}  DONE -> data/reddit/milton_ext/")
        time.sleep(1)

    print(f"\n{'='*64}\n  TOTAL: {gp} posts, {gc} comments (Oct 4)")
    print("  Saved to data/reddit/milton_ext/ . Existing data/reddit/milton/ untouched.")
    print("  Merge later AFTER extending merge_reddit WINDOW['milton'] to (-5, 0).")


if __name__ == "__main__":
    main()
