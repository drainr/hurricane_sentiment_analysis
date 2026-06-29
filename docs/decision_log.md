# Decision Log

Running record of methodological decisions.

## Misinformation handling (2026-06-29)

BERTopic did not produce a misinformation topic in any of the six files. Misinformation is a cross-cutting _stance_ that rides on top of other topics (FEMA aid, politics, weather) rather than a distinct semantic cluster, so it does not separate out at any `min_topic_size`. On Reddit, misinformation content is captured inside the **political / FEMA criticism** category; in the White House comments it is captured inside **misinformation removal** (moderator removal notices). Accordingly, H6 and H7 will **not** use "misinformation" as a standalone topic category — they refer to political and FEMA-critical discourse instead. No rerun was required; this is a documentation/framing decision.

## Reddit cleaning funnel (2026-06-29)

Reconstructed from the raw Layer-1 files (`reddit_posts_all.csv`, `reddit_comments_all.csv`) through the canonical pipeline (`merge_reddit.py` → `build_relevant.py`). Numbers reconcile exactly to the final relevant files and the RoBERTa processing log.

**Pipeline note:** the cleaning threshold is **< 3 words** (`MIN_WORDS = 3` in `merge_reddit.py`), not 5. (The < 5-word exclusion is a separate, BERTopic-only step applied to Facebook comments.) The funnel also includes two steps beyond basic cleaning — an **event-window filter** (each row kept only if its own timestamp falls in its storm's Fall-2024 window) and a **thread-relevance + bot-removal** step — because the "final cleaned count" is the _relevant_ analysis corpus, not merely the de-duplicated set.

### Comments

```
Raw collected (comments):                  222,477
After removing deleted/removed content:    206,734   (-15,743)
After removing <3 word rows:               193,225   (-13,509)
After deduplication (by id):               193,225   (-0, no duplicate comment ids)
After event-window filter:                 179,164   (-14,061)
After thread-relevance + bot removal:      122,026   (relevant 122,410 - 384 bot/automod)
Final cleaned count:                       122,026   # matches RoBERTa log
```

### Posts

```
Raw collected (posts):                       6,908
After removing deleted/removed content:      6,908   (-0)
After removing <3 word rows:                 6,770   (-138)
After deduplication (by id):                 6,770   (-0, no duplicate post ids)
After event-window filter:                   6,504   (-266)
After thread-relevance + bot removal:        3,418
Final cleaned count:                         3,418   # matches RoBERTa log
```

**Storm-relevance keyword filter (used at the thread level).** Relevance is judged per _thread_: a post is on-topic if its text matches any keyword below, and its whole comment tree is then kept. Keywords (word-boundary, case-insensitive), plus each storm's own name (`debby` / `helene` / `milton`):

```
hurricane, storm, flood, power, weather, outage, category, fema, noaa
```

### The ~124,000 figure in `subreddit_selection_and_counts.md`

It refers to **comments**, but is an imprecise round number. The exact counts are **122,026 relevant comments** and **3,418 relevant posts** (combined **125,444**). Recommend replacing "~124,000" with the exact comment count (122,026) to avoid ambiguity.

### Two caveats on these counts

- **122,026 / 3,418 are the relevant-corpus / RoBERTa-log counts.** The _currently analyzed_ labeled files are slightly smaller after the White House de-duplication (2026-06-26 removed 973 WH comments + 5 WH posts that the keyword search had pulled into the Reddit files): **121,053 comments / 3,413 posts**.
- **Raw 222,477 vs the 210,822 in `subreddit_selection_and_counts.md`:** the doc's table counts only the nine purposely-searched subreddits; the +11,655 difference is the Helene/Milton early-day window-extension collections (`helene_ext/`, `milton_ext/`), which the doc table predates.
