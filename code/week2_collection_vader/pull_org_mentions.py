#!/usr/bin/env python3
"""
pull_org_mentions.py  —  find comments that MENTION an organization.

Why this exists:
    FEMA, NOAA, NWS, NHC do NOT post on Reddit (only the White House does).
    But people talk ABOUT them constantly during/after a storm — trust, blame,
    "where is FEMA", misinformation, etc. This pulls every community comment
    that mentions an org, tagged with which org(s) it named.

    This is the "mentions" angle for H7 (official communication) — distinct
    from collecting an org's own posts. See the project Open Questions note on
    a NER pass over WH/FEMA/Coast Guard mentions (Alam et al. misinformation).

    NOTE (political sensitivity): Helene FEMA discourse got heavily politicized.
    Report sentiment/topics factually, no editorial commentary (standing rule).

Method:
    Arctic Shift /comments/search with `body=<keyword>` + subreddit + window,
    paginating past the 100-cap. Dedupes by comment id across keywords, so a
    comment naming both FEMA and NOAA is ONE row with org_mentioned="FEMA|NOAA".

How to use:
    1. Edit ORGS / HURRICANES / SUBREDDITS below.
    2. python3 pull_org_mentions.py
    3. Output -> ../../data/reddit/org_mentions_<timestamp>.csv

Gotchas:
    - `body=` is the keyword param (NOT `query` — that 400s).
    - Multi-word terms ("National Weather Service") are token-AND, good enough.
    - User-Agent header required or 403.
    - Windows here are EXTENDED past landfall on purpose: org/relief talk is
      aftermath-heavy, so we don't want to cut it at the storm window.
"""

import csv
import datetime
import os
import sys
import time

import requests

# ============================ CONFIG — EDIT ME ============================
# Canonical org name -> list of search terms / aliases to match in comment text.
ORGS = {
    "FEMA": ["FEMA"],
    "NOAA": ["NOAA"],
}

# Windows EXTENDED past landfall — org/relief discourse peaks in the aftermath.
HURRICANES = {
    "debby":  {"after": "2024-07-31", "before": "2024-08-20"},
    "helene": {"after": "2024-09-23", "before": "2024-10-20"},
    "milton": {"after": "2024-10-05", "before": "2024-10-25"},
}

# Which subreddits to scan per storm (org talk concentrates where the storm hit).
SUBREDDITS = {
    "debby":  ["TropicalWeather", "florida", "sarasota", "tampa"],
    "helene": ["TropicalWeather", "florida", "asheville", "NorthCarolina", "Georgia"],
    "milton": ["TropicalWeather", "florida", "tampa", "sarasota"],
}

PER_REQUEST_SLEEP = 2.0   # body-search is heavy server-side; pause between pages
RETRY_BACKOFF = 5         # seconds * attempt on "slow down"/timeout responses
# =========================================================================

BASE = "https://arctic-shift.photon-reddit.com/api"
HEADERS = {"User-Agent": "ncf-hurricane-research/0.1 (academic; jose araya)"}
OUT_DIR = os.path.join(sys.path[0], "..", "..", "data", "reddit")

KEEP = ["id", "link_id", "parent_id", "subreddit", "author",
        "created_utc", "created_date", "score", "body",
        "hurricane", "org_mentioned", "source_type"]


def get_json(params, tries=5):
    """GET with retries. The free API answers heavy body-searches with a 422
    'Timeout. Maybe slow down a bit' — that's retryable, just wait longer."""
    for attempt in range(tries):
        try:
            r = requests.get(f"{BASE}/comments/search", params=params,
                             headers=HEADERS, timeout=45)
            # 422 here = server-side "slow down" timeout, not a bad request
            if r.status_code == 422 and "slow down" in r.text.lower():
                raise ValueError("server timeout (slow down)")
            r.raise_for_status()
            data = r.json().get("data")
            if data is None:
                raise ValueError(r.json().get("error", "null data"))
            return data
        except (requests.RequestException, ValueError) as e:
            if attempt == tries - 1:
                raise
            time.sleep(RETRY_BACKOFF * (attempt + 1))   # 5s,10s,15s,20s backoff


def search(subreddit, term, after, before):
    """All comments in (subreddit, window) whose body matches `term`. Paginated."""
    cursor, rows = None, []
    while True:
        params = {"subreddit": subreddit, "body": term,
                  "before": before, "limit": 100, "sort": "asc"}
        # first page starts at the window's `after`; later pages at the cursor
        params["after"] = cursor if cursor is not None else after
        data = get_json(params)
        if not data:
            break
        rows.extend(data)
        cursor = data[-1]["created_utc"]
        if len(data) < 100:
            break
        time.sleep(PER_REQUEST_SLEEP)
    return rows


def to_date(ts):
    """Format a Unix timestamp as 'YYYY-MM-DD HH:MM' UTC, or '' if missing."""
    return datetime.datetime.fromtimestamp(
        ts, datetime.UTC).strftime("%Y-%m-%d %H:%M") if ts else ""


def main():
    """Collect comments mentioning FEMA, NOAA, NWS or NHC across the storm windows.

    Deduplicates by comment id, so a comment naming two organisations is one row
    with org_mentioned='FEMA|NOAA' rather than two.
    """
    os.makedirs(OUT_DIR, exist_ok=True)
    # comment id -> row dict; org_mentioned accumulates a set
    merged = {}
    for storm, window in HURRICANES.items():
        for sub in SUBREDDITS.get(storm, []):
            for org, terms in ORGS.items():
                for term in terms:
                    try:
                        hits = search(sub, term, window["after"], window["before"])
                    except Exception as e:
                        print(f"  {storm}/{sub}/{org}('{term}')  ERROR {e}")
                        continue
                    for c in hits:
                        cid = c["id"]
                        if cid not in merged:
                            merged[cid] = {
                                "id": cid,
                                "link_id": c.get("link_id"),
                                "parent_id": c.get("parent_id"),
                                "subreddit": c.get("subreddit"),
                                "author": c.get("author"),
                                "created_utc": c.get("created_utc"),
                                "created_date": to_date(c.get("created_utc")),
                                "score": c.get("score"),
                                "body": c.get("body"),
                                "hurricane": storm,
                                "org_mentioned": set(),
                                "source_type": "community_discussion",
                            }
                        merged[cid]["org_mentioned"].add(org)
                    print(f"  {storm:7s} r/{sub:15s} {org:12s} '{term}': {len(hits)} hits "
                          f"(unique so far: {len(merged)})")
                    time.sleep(PER_REQUEST_SLEEP)

    # finalize: join org set into a stable "FEMA|NOAA" string
    rows = []
    for row in merged.values():
        row["org_mentioned"] = "|".join(sorted(row["org_mentioned"]))
        rows.append(row)

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(OUT_DIR, f"org_mentions_{stamp}.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KEEP, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"\nTotal unique comments mentioning an org: {len(rows)}")
    # quick per-org tally
    from collections import Counter
    tally = Counter()
    for row in rows:
        for o in row["org_mentioned"].split("|"):
            tally[o] += 1
    for o, n in tally.most_common():
        print(f"   {o:12s} {n}")
    print(f"Saved -> {os.path.relpath(out)}  (raw — clean/score downstream)")


if __name__ == "__main__":
    main()
