#!/usr/bin/env python3
"""
pull_comments.py  —  full comment-tree puller for specific megathreads.

This is the "manual megathread path" (Week 2): you've already used
explore_queries.py to find the big threads; now pull EVERY comment under
each one. Uses Arctic Shift's /comments/search with `link_id` (the thread's
id), paginating past the 100-cap.

Workflow:
    1. explore_queries.py  -> find megathreads, get their IDs from the CSV.
    2. Paste the IDs into MEGATHREADS below (already pre-filled from the
       2026-06-08 exploration run).
    3. python3 pull_comments.py
    4. Output: one CSV per thread + one combined CSV in ../../data/reddit/.

What you get per comment: id, link_id (thread), parent_id (for threading),
subreddit, author, created_utc/date, score, body — plus our tags: hurricane,
source_type. Threading is reconstructable from parent_id:
    parent starts t3_ -> top-level comment (reply to the post)
    parent starts t1_ -> reply to another comment

NOT done here (kept downstream, on purpose):
    - cleaning (drop [deleted]/[removed], <3-word, dedupe)  -> merge step
    - VADER scoring, days_from_landfall                     -> Student B merge
    Raw fidelity now; clean on a copy later so we never lose provenance.

Gotchas (from the verified guide):
    - Python MUST send a User-Agent header or the archive 403s.
    - link_id can be given with or without the t3_ prefix; we send the bare id.
    - 100 results/request hard cap -> we paginate on created_utc, sort=asc.
"""

import csv
import datetime
import os
import sys
import time

import requests

# ===================== CONFIG — paste thread IDs here =====================
# Pre-filled from explore_queries.py run on 2026-06-08. Comment out the ones
# you don't want, add more as you find them. source_type per Week 2 tagging:
#   "community_discussion" = organic Reddit (these). WH threads = "government_response".
MEGATHREADS = [
    # --- Tier 1: TropicalWeather meteorological megathreads (huge, on-topic) ---
    {"id": "1ejftpt", "hurricane": "debby",  "subreddit": "TropicalWeather", "source_type": "community_discussion"},  # 892
    {"id": "1fp6k3k", "hurricane": "helene", "subreddit": "TropicalWeather", "source_type": "community_discussion"},  # 6572
    {"id": "1fzv2ub", "hurricane": "milton", "subreddit": "TropicalWeather", "source_type": "community_discussion"},  # 6968 (Day 5)
    # The Milton Day-4 thread (6754 cmts) is also huge — grab its id from the
    # exploration CSV and add it here:
    # {"id": "______", "hurricane": "milton", "subreddit": "TropicalWeather", "source_type": "community_discussion"},

    # --- Tier 2: Helene inland impact (the real disaster zone) ---
    {"id": "1fqljgq", "hurricane": "helene", "subreddit": "asheville",     "source_type": "community_discussion"},  # 1474 MEGATHREAD
    {"id": "1fqe6ty", "hurricane": "helene", "subreddit": "Georgia",       "source_type": "community_discussion"},  # 875 check-in
    {"id": "1fr17c7", "hurricane": "helene", "subreddit": "NorthCarolina", "source_type": "community_discussion"},  # 346 Chimney Rock

    # --- Tier 3: local sentiment (noisy; pull then filter downstream) ---
    {"id": "1ekqiq0", "hurricane": "debby",  "subreddit": "sarasota", "source_type": "community_discussion"},  # 335 flooding
    {"id": "1fqmcri", "hurricane": "helene", "subreddit": "florida",  "source_type": "community_discussion"},  # 417 "Florida wtf"
    {"id": "1fzyo1b", "hurricane": "milton", "subreddit": "sarasota", "source_type": "community_discussion"},  # 159 hurricane aid
]
# =========================================================================

BASE = "https://arctic-shift.photon-reddit.com/api"
HEADERS = {"User-Agent": "ncf-hurricane-research/0.1 (academic; jose araya)"}
OUT_DIR = os.path.join(sys.path[0], "..", "..", "data", "reddit")

KEEP = ["id", "link_id", "parent_id", "subreddit", "author",
        "created_utc", "created_date", "score", "body",
        "hurricane", "source_type"]


def pull_thread(thread_id):
    """All comments under one post, paginating past the 100-cap. Returns rows."""
    url = f"{BASE}/comments/search"
    cursor = None       # no `after` on the first page (after=0 is a 400)
    rows, seen = [], set()
    while True:
        params = {"link_id": thread_id, "limit": 100, "sort": "asc"}
        if cursor is not None:
            params["after"] = cursor    # subsequent pages: start after last comment
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()["data"]
        if not data:
            break
        new = 0
        for c in data:
            if c["id"] not in seen:
                seen.add(c["id"]); rows.append(c); new += 1
        cursor = data[-1]["created_utc"]    # next page starts after last comment
        if len(data) < 100 or new == 0:     # last page, or all dupes -> done
            break
        time.sleep(1)                       # be polite to the free archive
    return rows


def to_row(c, hurricane, source_type):
    """Flatten one Arctic Shift comment into our raw CSV schema.

    Keeps link_id and parent_id so the thread structure can be rebuilt later:
    a parent starting 't3_' is a top-level reply to the post, 't1_' a reply to
    another comment.
    """
    return {
        "id": c.get("id"),
        "link_id": c.get("link_id"),
        "parent_id": c.get("parent_id"),
        "subreddit": c.get("subreddit"),
        "author": c.get("author"),
        "created_utc": c.get("created_utc"),
        "created_date": datetime.datetime.fromtimestamp(
            c["created_utc"], datetime.UTC).strftime("%Y-%m-%d %H:%M")
            if c.get("created_utc") else "",
        "score": c.get("score"),
        "body": c.get("body"),
        "hurricane": hurricane,
        "source_type": source_type,
    }


def save_csv(rows, path):
    """Write comment rows to a CSV with the fixed KEEP column order."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KEEP, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    """Pull the full comment tree for every thread listed in MEGATHREADS.

    Writes one CSV per thread plus a combined file. Raw only — cleaning,
    scoring and days_from_landfall all happen downstream.
    """
    os.makedirs(OUT_DIR, exist_ok=True)
    combined = []
    print(f"Pulling {len(MEGATHREADS)} thread(s)...\n")
    for t in MEGATHREADS:
        tid, storm, st = t["id"], t["hurricane"], t["source_type"]
        try:
            raw = pull_thread(tid)
        except requests.RequestException as e:
            print(f"  {storm:7s} r/{t['subreddit']:15s} {tid}  ERROR {e}")
            continue
        rows = [to_row(c, storm, st) for c in raw]
        combined.extend(rows)
        # one CSV per thread
        per = os.path.join(OUT_DIR, f"comments_{storm}_{t['subreddit']}_{tid}.csv")
        save_csv(rows, per)
        print(f"  {storm:7s} r/{t['subreddit']:15s} {tid}  {len(rows):5d} comments -> {os.path.basename(per)}")
        time.sleep(1)

    # combined CSV across all threads
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    allpath = os.path.join(OUT_DIR, f"megathread_comments_ALL_{stamp}.csv")
    save_csv(combined, allpath)
    print(f"\nTotal: {len(combined)} comments across {len(MEGATHREADS)} threads")
    print(f"Combined -> {os.path.relpath(allpath)}")
    print("Raw pull (no cleaning/scoring yet — that's the merge step).")


if __name__ == "__main__":
    main()
