import requests, time, csv, datetime, os

BASE = "https://arctic-shift.photon-reddit.com/api"

def collect(kind, subreddit, author, after=None, before=None, query=None):
    """kind: 'posts' or 'comments'. after/before: 'YYYY-MM-DD' (optional).
    Returns list of dicts, paginating past the 100-cap."""
    max_retries = 5
    url = f"{BASE}/{kind}/search"
    cursor = None
    rows, seen = [], set()
    while True:
        params = {"limit": "auto", "sort": "asc"}
        if cursor is not None:
            params["after"] = cursor
        elif after:
            params["after"] = after
        if before:
            params["before"] = before
        if subreddit:
            params["subreddit"] = subreddit
        if author:
            params["author"] = author
        if query:
            params["query"] = query
        # Retry loop with exponential backoff
        for attempt in range(max_retries):
            try:
                r = requests.get(url, params=params, timeout=30)
                if r.status_code == 429:  # Too Many Requests
                    wait_time = 2 ** attempt  # exponential backoff: 1, 2, 4, 8, 16 seconds
                    print(f"  Rate limited. Waiting {wait_time}s before retry (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                    continue
                r.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                print(f"  Request failed: {e}. Waiting {wait_time}s before retry (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
        
        data = r.json()["data"]
        if not data:
            break
        for item in data:
            if item["id"] not in seen:        # belt-and-suspenders dedupe
                seen.add(item["id"]); rows.append(item)
        cursor = data[-1]["created_utc"]      # next page starts after last item
        if len(data) < 100:                   # last (partial) page -> done
            break
        time.sleep(1)                         # be polite to the free archive
    return rows

def save_csv(rows, path, kind):
    # Define fields based on whether we're saving posts or comments
    if kind == "posts":
        keep = ["id","subreddit","author","created_utc","num_comments","title","selftext","score","hurricane","keyword_hit"]
    else:  # comments
        keep = ["id","link_id", "parent_id", "subreddit","author","created_utc","score","body","hurricane","keyword_hit"]
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keep, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            # Convert created_utc timestamp to datetime string in UTC
            row["created_utc"] = datetime.datetime.fromtimestamp(
                row["created_utc"], datetime.timezone.utc).isoformat()
            w.writerow(row)

if __name__ == "__main__":
    # Date range for Milton (Oct 5-9, use Oct 10 as before to capture all of Oct 9)
    after = "2024-10-05"
    before = "2024-10-10"
    
    # Keywords for location-based subreddits
    keywords = ["milton", "hurricane", "storm", "flood", "power", "weather", "outage", "category", "fema", "noaa"]
    
    # Location-based subreddits
    location_subreddits = ["sarasota", "tampa", "florida", "georgia", "northcarolina"]
    
    # Hurricane-based subreddits (no keyword filtering needed)
    hurricane_subreddits = ["hurricane", "tropicalweather"]
    
    # Pull from location subreddits
    for subreddit in location_subreddits:
        print(f"Pulling from r/{subreddit}...")
        # Pull all posts and filter by keywords client-side
        posts_all = collect("posts", subreddit, None, after, before)
        
        # Filter posts that contain any of the keywords in title or selftext
        posts = []
        for post in posts_all:
            title = (post.get("title") or "").lower()
            selftext = (post.get("selftext") or "").lower()
            content = title + " " + selftext
            if any(kw.lower() in content for kw in keywords):
                post_copy = post.copy()
                post_copy["hurricane"] = "milton"
                # Find which keyword actually matched
                for keyword in keywords:
                    if keyword.lower() in content:
                        post_copy["keyword_hit"] = keyword
                        break
                posts.append(post_copy)
        
        print(f"  {len(posts)} posts (from {len(posts_all)} total)")
        save_csv(posts, f"../../data/reddit/milton/{subreddit}_posts.csv", "posts")
        
        # Pull all comments from subreddit, then filter to only those from collected posts
        post_ids = {f"t3_{post['id']}" for post in posts}  # API uses t3_ prefix for post IDs
        comments_all = collect("comments", subreddit, None, after, before)
        comments = []
        for c in comments_all:
            if c.get("link_id") in post_ids:
                comment_copy = c.copy()
                # Find the matching post to get hurricane and keyword_hit
                for post in posts:
                    if c.get("link_id") == f"t3_{post['id']}":
                        comment_copy["hurricane"] = post["hurricane"]
                        comment_copy["keyword_hit"] = post.get("keyword_hit")
                        break
                comments.append(comment_copy)
        print(f"  {len(comments)} comments (from {len(posts)} posts)")
        save_csv(comments, f"../../data/reddit/milton/{subreddit}_comments.csv", "comments")
    
    # Pull from hurricane subreddits
    for subreddit in hurricane_subreddits:
        print(f"Pulling from r/{subreddit}...")
        # Pull posts
        posts_all = collect("posts", subreddit, None, after, before)
        
        # Filter posts that contain any of the keywords in title or selftext
        posts = []
        for post in posts_all:
            title = (post.get("title") or "").lower()
            selftext = (post.get("selftext") or "").lower()
            content = title + " " + selftext
            if any(kw.lower() in content for kw in keywords):
                post_copy = post.copy()
                post_copy["hurricane"] = "milton"
                # Find which keyword actually matched
                for keyword in keywords:
                    if keyword.lower() in content:
                        post_copy["keyword_hit"] = keyword
                        break
                posts.append(post_copy)
        
        print(f"  {len(posts)} posts (from {len(posts_all)} total)")
        save_csv(posts, f"../../data/reddit/milton/{subreddit}_posts.csv", "posts")
        
        # Pull all comments from subreddit, then filter to only those from collected posts
        post_ids = {f"t3_{post['id']}" for post in posts}
        comments_all = collect("comments", subreddit, None, after, before)
        comments = []
        for c in comments_all:
            if c.get("link_id") in post_ids:
                comment_copy = c.copy()
                # Find the matching post to get hurricane and keyword_hit
                for post in posts:
                    if c.get("link_id") == f"t3_{post['id']}":
                        comment_copy["hurricane"] = post["hurricane"]
                        comment_copy["keyword_hit"] = post.get("keyword_hit")
                        break
                comments.append(comment_copy)
        print(f"  {len(comments)} comments (from {len(posts)} posts)")
        save_csv(comments, f"../../data/reddit/milton/{subreddit}_comments.csv", "comments")
    
    # ──────────────────────────────────────────────────────────────────────
    # White House (u/whitehouse46) collection
    #
    # BUG (now fixed): the previous version filtered the SAME wide author-pull
    # twice — once `if "milton" in text` and once `if "helene" in text` — and
    # appended each match to a separate list saved independently. A post that
    # mentioned BOTH storm names (e.g. post 1g236sq, a Milton update that also
    # references Helene) was therefore written under BOTH hurricanes, and so
    # were all 46 of its comments. That double-counted 1 post + 46 comments,
    # inflating Helene's government_response totals for H7.
    #
    # FIX: assign each post id to EXACTLY ONE hurricane and guard with a
    # seen-id set so no post (and no comment) is ever written twice. A post
    # naming only one storm goes to that storm; a post naming both goes to the
    # nearer landfall by its own date (it belongs to the event it's dated to).
    #
    # Flip COLLECT_WHITEHOUSE to True to re-run this pull.
    COLLECT_WHITEHOUSE = False
    if COLLECT_WHITEHOUSE:
        LANDFALL = {"helene": datetime.date(2024, 9, 26),
                    "milton": datetime.date(2024, 10, 9)}

        def assign_hurricane(post):
            """Return exactly one hurricane for this post, or None to skip."""
            content = ((post.get("title") or "") + " " + (post.get("selftext") or "")).lower()
            hits = [h for h in ("helene", "milton") if h in content]
            if not hits:
                return None
            if len(hits) == 1:
                return hits[0]
            d = datetime.datetime.fromtimestamp(
                post["created_utc"], datetime.timezone.utc).date()
            return min(hits, key=lambda h: abs((d - LANDFALL[h]).days))

        print("Pulling from u/whitehouse46...")
        all_posts = collect(kind="posts", subreddit="", author="whitehouse",
                            after="2024-08-01", before="2024-11-15")
        print(f"  {len(all_posts)} total posts")

        # one hurricane per post id; seen-set makes a second save impossible
        seen_post_ids = set()
        posts_by_storm = {"helene": [], "milton": []}
        for post in all_posts:
            if post["id"] in seen_post_ids:
                continue
            storm = assign_hurricane(post)
            if storm is None:
                continue
            seen_post_ids.add(post["id"])
            content = ((post.get("title") or "") + " " + (post.get("selftext") or "")).lower()
            pc = post.copy()
            pc["hurricane"] = storm
            pc["keyword_hit"] = next((k for k in keywords if k.lower() in content), storm)
            posts_by_storm[storm].append(pc)

        for storm, posts in posts_by_storm.items():
            save_csv(posts, f"../../data/reddit/whitehouse/{storm}_posts.csv", "posts")
            comments, seen_comment_ids = [], set()
            for post in posts:                      # each post is in exactly one storm
                cursor = None
                while True:
                    params = {"link_id": post["id"], "limit": 100, "sort": "asc"}
                    if cursor is not None:
                        params["after"] = cursor
                    r = requests.get(f"{BASE}/comments/search", params=params, timeout=30)
                    r.raise_for_status()
                    data = r.json().get("data", [])
                    if not data:
                        break
                    for c in data:
                        if c["id"] in seen_comment_ids:   # never save a comment id twice
                            continue
                        seen_comment_ids.add(c["id"])
                        cc = c.copy()
                        cc["hurricane"] = post["hurricane"]
                        cc["keyword_hit"] = post["keyword_hit"]
                        comments.append(cc)
                    cursor = data[-1]["created_utc"]
                    if len(data) < 100:
                        break
                    time.sleep(1)
            save_csv(comments, f"../../data/reddit/whitehouse/{storm}_comments.csv", "comments")
            print(f"  {storm}: {len(posts)} posts, {len(comments)} comments")