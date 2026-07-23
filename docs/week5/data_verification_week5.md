# Week 5 Data Verification Report

Read-only reconciliation of all scored/labeled files against the canonical Decision-Log counts.
Row counts are pandas (true records); `wc -l` is shown alongside to confirm embedded-newline inflation.

## 1-2. Row counts (pandas vs canonical vs wc -l) and pipeline-stage consistency

| source | canonical | processed (pandas) | vader | roberta | wc -l (proc) | status |
|---|---|---|---|---|---|---|
| facebook_posts | 952 | 952 | 952 | 952 | 1827 | OK |
| facebook_comments | 59736 | 59736 | 59736 | 59736 | 62501 | OK |
| reddit_relevant_posts | 3413 | 3413 | 3413 | 3413 | 18447 | OK |
| reddit_relevant_comments | 121053 | 121053 | 121053 | 121053 | 202551 | OK |
| whitehouse_threads_posts | 12 | 12 | 12 | 12 | 146 | OK |
| whitehouse_threads_comments | 2193 | 2193 | 2193 | 2193 | 4344 | OK |
| master | 187359 | 187359 | - | - | 289816 | OK |

## 3. Duplicates and cross-file id collisions

- facebook_posts: dup id=0, dup (id,type)=0
- facebook_comments: dup id=0, dup (id,type)=0
- reddit_relevant_posts: dup id=0, dup (id,type)=0
- reddit_relevant_comments: dup id=0, dup (id,type)=0
- whitehouse_threads_posts: dup id=0, dup (id,type)=0
- whitehouse_threads_comments: dup id=0, dup (id,type)=0
- reddit_relevant_posts: 0 White House ids present (WH-removal holds)
- reddit_relevant_comments: 0 White House ids present (WH-removal holds)
- master: dup ('id', 'provenance')=0

## 4-5. VADER and RoBERTa score sanity

- facebook_posts: roberta truncated rate 3.89% (37 rows)
- facebook_comments: roberta truncated rate 0.01% (7 rows)
- reddit_relevant_posts: roberta truncated rate 2.87% (98 rows)
- reddit_relevant_comments: roberta truncated rate 0.19% (231 rows)
- whitehouse_threads_posts: roberta truncated rate 16.67% (2 rows)
- whitehouse_threads_comments: roberta truncated rate 0.50% (11 rows)

## 6. Key columns (windows, hurricane, subreddit)

- facebook_posts: hurricanes=['debby', 'helene', 'milton'], days range=[-5,1]
- facebook_comments: hurricanes=['debby', 'helene', 'milton'], days range=[-5,1]
- reddit_relevant_posts: hurricanes=['debby', 'helene', 'milton'], days range=[-5,1]
- reddit_relevant_comments: hurricanes=['debby', 'helene', 'milton'], days range=[-5,1]
- whitehouse_threads_posts: hurricanes=['helene', 'milton'], days range=[0,25]
- whitehouse_threads_comments: hurricanes=['helene', 'milton'], days range=[0,181]

## 7. VADER vs RoBERTa raw agreement (tripwire)

- facebook_posts: 31.2% raw label agreement
- facebook_comments: 62.0% raw label agreement
- reddit_relevant_posts: 46.4% raw label agreement
- reddit_relevant_comments: 51.6% raw label agreement
- whitehouse_threads_posts: 41.7% raw label agreement
- whitehouse_threads_comments: 49.3% raw label agreement

## Verdict

**ALL CHECKS PASSED.** Data reconciles to the Decision-Log canonical counts; 0 duplicates / 0 WH-in-Reddit; VADER & RoBERTa scores in range with full coverage. Clear to proceed to Week 5 hypothesis testing.
