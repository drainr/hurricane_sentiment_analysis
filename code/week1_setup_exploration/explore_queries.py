#!/usr/bin/env python3
"""
explore_queries.py  —  Arctic Shift query EXPLORER (not the full collector)

Purpose (Week 2, Reddit collection):
    Before we commit to a full paginated pull, we want to SEE what each
    (subreddit x hurricane window) actually returns, so we can decide if the
    query is worth keeping. This script pulls ONE small sample per query and
    prints: how many posts came back + the top threads by comment volume.

    The "top threads by comments" view doubles as megathread-spotting for the
    manual path (it surfaces pinned/major discussion threads with their URLs).

How to use:
    1. Edit the CONFIG block below — add/remove subreddits per hurricane,
       tweak windows. Try r/HurricaneHelene, r/asheville, etc.
    2. Run:  python3 "explore_queries.py"
    3. Read the printout. Good query? Keep it. Empty/junk? Drop or change it.
    4. A CSV log lands in ../../data/reddit/exploration/ — paste into a sheet.

Notes baked in from our verified Arctic Shift guide:
    - A "query" here = subreddit + date window (that's all Arctic Shift needs).
    - `before` is EXCLUSIVE: to INCLUDE Aug 5 you must write before=2024-08-06.
      The windows below are already padded one day for that reason.
    - Python MUST send a User-Agent header or the archive returns 403.
    - This explorer caps at 100 results/query on purpose (one request, fast,
      no pagination). 100 returned = "there's more here" -> good candidate for
      the full collector. It is NOT a complete pull.
    - Don't trust a post's num_comments as gospel (it's a cached count), but
      it's perfect for RANKING which threads are the big ones.
"""

import csv
import datetime
import sys
import time

import requests

# ============================ CONFIG — EDIT ME ============================
# Date windows. `before` is already padded +1 day so the last day is included.
HURRICANES = {
    "debby":  {"after": "2024-07-31", "before": "2024-08-06"},  # Jul 31 - Aug 5
    "helene": {"after": "2024-09-23", "before": "2024-09-28"},  # Sep 23 - Sep 27
    "milton": {"after": "2024-10-05", "before": "2024-10-10"},  # Oct 5  - Oct 9
}

# Subreddits to test per hurricane. Add/remove freely — this is the knob you
# turn most. Hurricane-specific subs (r/HurricaneHelene etc.) often hold the
# biggest megathreads, so they're worth testing first.
SUBREDDITS = {
    "debby": [
        "TropicalWeather", "tampa", "florida", "sarasota",
    ],
    "helene": [
        "TropicalWeather", "tampa", "florida", "sarasota",
        "HurricaneHelene", "asheville", "NorthCarolina", "Georgia",
    ],
    "milton": [
        "TropicalWeather", "tampa", "florida", "sarasota",
        "HurricaneMilton",
    ],
}

KIND = "posts"   # "posts" (threads) or "comments". Start with posts to scout.
TOP_N = 8        # how many top-by-comments rows to print per query
# =========================================================================

BASE = "https://arctic-shift.photon-reddit.com/api"
HEADERS = {"User-Agent": "ncf-hurricane-research/0.1 (academic; jose araya)"}


def fetch(kind, subreddit, after, before, limit=100):
    """One request, no pagination. Returns the list of result dicts (<=100)."""
    url = f"{BASE}/{kind}/search"
    params = {
        "subreddit": subreddit,
        "after": after,
        "before": before,
        "limit": limit,
        "sort": "desc",  # newest first; ranking is done client-side anyway
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()["data"]


def to_date(unix_ts):
    """Format a Unix timestamp as 'YYYY-MM-DD HH:MM' UTC."""
    return datetime.datetime.fromtimestamp(
        unix_ts, datetime.UTC).strftime("%Y-%m-%d %H:%M")


def explore():
    """Sample each (storm, subreddit) query and print what it returns.

    One uncapped request per query, so 100 results back means 'there is more
    here' rather than a complete pull. Also logs the biggest threads by comment
    count, which is how megathreads were spotted.
    """
    log_rows = []  # for the CSV
    for storm, window in HURRICANES.items():
        subs = SUBREDDITS.get(storm, [])
        print(f"\n{'='*70}\n  {storm.upper()}   "
              f"{window['after']} -> {window['before']} (before is exclusive)"
              f"\n{'='*70}")
        for sub in subs:
            try:
                data = fetch(KIND, sub, window["after"], window["before"])
            except requests.HTTPError as e:
                print(f"\n  r/{sub:18s}  ERROR {e.response.status_code} "
                      f"(sub may not exist / be private)")
                log_rows.append([storm, sub, "ERROR", "", "", "", "", ""])
                continue
            except requests.RequestException as e:
                print(f"\n  r/{sub:18s}  ERROR {e}")
                log_rows.append([storm, sub, "ERROR", "", "", "", "", ""])
                continue

            n = len(data)
            flag = "  <-- hit 100 cap, MORE EXIST (good for full pull)" if n >= 100 else ""
            print(f"\n  r/{sub:18s}  {n:3d} {KIND} returned{flag}")

            if n == 0:
                print("       (nothing — probably drop this query or widen window)")
                log_rows.append([storm, sub, 0, "", "", "", "", ""])
                continue

            # Rank by comment volume to surface megathreads / big discussions.
            ranked = sorted(
                data, key=lambda p: p.get("num_comments", 0) or 0, reverse=True)
            for p in ranked[:TOP_N]:
                nc = p.get("num_comments", 0) or 0
                title = (p.get("title") or p.get("body") or "")[:70].replace("\n", " ")
                permalink = f"https://reddit.com/comments/{p['id']}"
                print(f"       {nc:5d} cmts | {to_date(p['created_utc'])} | {title}")
                log_rows.append([
                    storm, sub, n, p["id"], nc,
                    to_date(p["created_utc"]), title, permalink,
                ])
            time.sleep(1)  # be polite to the free archive

    # Write CSV log you can paste into a spreadsheet.
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = f"{sys.path[0]}/../../data/reddit/exploration"
    import os
    os.makedirs(out_dir, exist_ok=True)
    out = f"{out_dir}/exploration_{KIND}_{stamp}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["hurricane", "subreddit", "posts_in_window",
                    "thread_id", "num_comments", "created_date",
                    "title", "permalink"])
        w.writerows(log_rows)
    print(f"\nSaved CSV -> {out}\n"
          f"Open it / paste into a sheet to compile candidate megathread URLs.")


if __name__ == "__main__":
    explore()
