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
    
    # # Pull from whitehouse46 user
    # print("Pulling from u/whitehouse46...")
    
    # # Pull all posts from whitehouse46 (use wide date range to capture all)
    # all_posts = collect(kind="posts", subreddit="", author="whitehouse", after="2024-08-01", before="2024-11-15")
    # print(f"  {len(all_posts)} total posts")
    
    # # Filter posts by milton keyword
    # milton_posts = []
    # for post in all_posts:
    #     title = (post.get("title") or "").lower()
    #     selftext = (post.get("selftext") or "").lower()
    #     content = title + " " + selftext
    #     if "milton" in content:
    #         post_copy = post.copy()
    #         post_copy["hurricane"] = "milton"
    #         # Find which keyword actually matched
    #         for keyword in keywords:
    #             if keyword.lower() in content:
    #                 post_copy["keyword_hit"] = keyword
    #                 break
    #         milton_posts.append(post_copy)
    
    # save_csv(milton_posts, "../../data/reddit/whitehouse/milton_posts.csv", "posts")
    
    
    # # Filter posts by helene keyword
    # helene_posts = []
    # for post in all_posts:
    #     title = (post.get("title") or "").lower()
    #     selftext = (post.get("selftext") or "").lower()
    #     content = title + " " + selftext
    #     if "helene" in content:
    #         post_copy = post.copy()
    #         post_copy["hurricane"] = "helene"
    #         # Find which keyword actually matched
    #         for keyword in keywords:
    #             if keyword.lower() in content:
    #                 post_copy["keyword_hit"] = keyword
    #                 break
    #         helene_posts.append(post_copy)
    
    # save_csv(helene_posts, "../../data/reddit/whitehouse/helene_posts.csv", "posts")
    
    # # Pull comments for milton posts
    # milton_comments = []
    # for post in milton_posts:
    #     cursor = "2000-01-01"
    #     while True:
    #         params = {"link_id": post["id"], "after": cursor, "before": "2099-12-31",
    #                   "limit": 100, "sort": "asc"}
    #         r = requests.get(f"{BASE}/comments/search", params=params, timeout=30)
    #         r.raise_for_status()
    #         data = r.json().get("data", [])
    #         if not data:
    #             break
    #         for c in data:
    #             comment_copy = c.copy()
    #             comment_copy["hurricane"] = post["hurricane"]
    #             comment_copy["keyword_hit"] = post["keyword_hit"]
    #             milton_comments.append(comment_copy)
    #         cursor = data[-1]["created_utc"]
    #         if len(data) < 100:
    #             break
    #         time.sleep(1)
    
    # print(f"  {len(milton_posts)} milton posts, {len(milton_comments)} milton comments")
    # save_csv(milton_comments, "../../data/reddit/whitehouse/milton_comments.csv", "comments")
    
    # # Pull comments for helene posts
    # helene_comments = []
    # for post in helene_posts:
    #     cursor = "2000-01-01"
    #     while True:
    #         params = {"link_id": post["id"], "after": cursor, "before": "2099-12-31",
    #                   "limit": 100, "sort": "asc"}
    #         r = requests.get(f"{BASE}/comments/search", params=params, timeout=30)
    #         r.raise_for_status()
    #         data = r.json().get("data", [])
    #         if not data:
    #             break
    #         for c in data:
    #             comment_copy = c.copy()
    #             comment_copy["hurricane"] = post["hurricane"]
    #             comment_copy["keyword_hit"] = post["keyword_hit"]
    #             helene_comments.append(comment_copy)
    #         cursor = data[-1]["created_utc"]
    #         if len(data) < 100:
    #             break
    #         time.sleep(1)
    
    # print(f"  {len(helene_posts)} helene posts, {len(helene_comments)} helene comments")
    # save_csv(helene_comments, "../../data/reddit/whitehouse/helene_comments.csv", "comments")