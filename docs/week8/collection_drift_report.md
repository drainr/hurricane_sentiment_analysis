# Week 8 — collection drift report

Fresh Arctic Shift re-collection (`data/reddit_rerun/`, from `recollect.py`) vs the frozen corpus (`data/reddit/`) the analysis is built on. **`removed`** = ids in the frozen pull that the archive no longer returns (deleted / edited / moderated away since June); **`added`** = ids new since the original pull.

## Per-file (whole-subreddit + window extensions)

| file                                           | frozen  | rerun   | delta | retained | removed | added |
| ---------------------------------------------- | ------- | ------- | ----- | -------- | ------- | ----- |
| debby/comments_debby_Georgia.csv               | 8,658   | 8,658   | +0    | 8,658    | 0       | 0     |
| debby/comments_debby_NorthCarolina.csv         | 8,143   | 8,143   | +0    | 8,143    | 0       | 0     |
| debby/comments_debby_TropicalWeather.csv       | 2,515   | 2,515   | +0    | 2,515    | 0       | 0     |
| debby/comments_debby_florida.csv               | 15,889  | 15,889  | +0    | 15,889   | 0       | 0     |
| debby/comments_debby_hurricane.csv             | 766     | 766     | +0    | 766      | 0       | 0     |
| debby/comments_debby_sarasota.csv              | 2,943   | 2,943   | +0    | 2,943    | 0       | 0     |
| debby/comments_debby_tampa.csv                 | 4,151   | 4,152   | +1    | 4,151    | 0       | 1     |
| debby/posts_debby_Georgia.csv                  | 257     | 257     | +0    | 257      | 0       | 0     |
| debby/posts_debby_NorthCarolina.csv            | 280     | 280     | +0    | 280      | 0       | 0     |
| debby/posts_debby_TropicalWeather.csv          | 49      | 49      | +0    | 49       | 0       | 0     |
| debby/posts_debby_florida.csv                  | 483     | 483     | +0    | 483      | 0       | 0     |
| debby/posts_debby_hurricane.csv                | 59      | 59      | +0    | 59       | 0       | 0     |
| debby/posts_debby_sarasota.csv                 | 86      | 86      | +0    | 86       | 0       | 0     |
| debby/posts_debby_tampa.csv                    | 225     | 225     | +0    | 225      | 0       | 0     |
| helene/comments_helene_Georgia.csv             | 10,499  | 10,499  | +0    | 10,499   | 0       | 0     |
| helene/comments_helene_HurricaneHelene.csv     | 244     | 244     | +0    | 244      | 0       | 0     |
| helene/comments_helene_NorthCarolina.csv       | 9,736   | 9,736   | +0    | 9,736    | 0       | 0     |
| helene/comments_helene_TropicalWeather.csv     | 11,530  | 11,530  | +0    | 11,530   | 0       | 0     |
| helene/comments_helene_asheville.csv           | 11,910  | 11,910  | +0    | 11,910   | 0       | 0     |
| helene/comments_helene_florida.csv             | 17,731  | 17,730  | -1    | 17,730   | 1       | 0     |
| helene/comments_helene_hurricane.csv           | 5,761   | 5,761   | +0    | 5,761    | 0       | 0     |
| helene/comments_helene_sarasota.csv            | 1,902   | 1,902   | +0    | 1,902    | 0       | 0     |
| helene/comments_helene_tampa.csv               | 7,182   | 7,185   | +3    | 7,182    | 0       | 3     |
| helene/posts_helene_Georgia.csv                | 264     | 264     | +0    | 264      | 0       | 0     |
| helene/posts_helene_HurricaneHelene.csv        | 48      | 48      | +0    | 48       | 0       | 0     |
| helene/posts_helene_NorthCarolina.csv          | 309     | 309     | +0    | 309      | 0       | 0     |
| helene/posts_helene_TropicalWeather.csv        | 90      | 90      | +0    | 90       | 0       | 0     |
| helene/posts_helene_asheville.csv              | 345     | 345     | +0    | 345      | 0       | 0     |
| helene/posts_helene_florida.csv                | 617     | 617     | +0    | 617      | 0       | 0     |
| helene/posts_helene_hurricane.csv              | 361     | 361     | +0    | 361      | 0       | 0     |
| helene/posts_helene_sarasota.csv               | 103     | 103     | +0    | 103      | 0       | 0     |
| helene/posts_helene_tampa.csv                  | 369     | 369     | +0    | 369      | 0       | 0     |
| helene_ext/comments_helene_Georgia.csv         | 1,565   | 1,565   | +0    | 1,565    | 0       | 0     |
| helene_ext/comments_helene_HurricaneHelene.csv | 0       | 0       | +0    | 0        | 0       | 0     |
| helene_ext/comments_helene_NorthCarolina.csv   | 2,876   | 2,876   | +0    | 2,876    | 0       | 0     |
| helene_ext/comments_helene_TropicalWeather.csv | 139     | 139     | +0    | 139      | 0       | 0     |
| helene_ext/comments_helene_asheville.csv       | 1,329   | 1,329   | +0    | 1,329    | 0       | 0     |
| helene_ext/comments_helene_florida.csv         | 2,861   | 2,861   | +0    | 2,861    | 0       | 0     |
| helene_ext/comments_helene_hurricane.csv       | 61      | 61      | +0    | 61       | 0       | 0     |
| helene_ext/comments_helene_sarasota.csv        | 229     | 229     | +0    | 229      | 0       | 0     |
| helene_ext/comments_helene_tampa.csv           | 1,082   | 1,082   | +0    | 1,082    | 0       | 0     |
| helene_ext/posts_helene_Georgia.csv            | 70      | 70      | +0    | 70       | 0       | 0     |
| helene_ext/posts_helene_HurricaneHelene.csv    | 0       | 0       | +0    | 0        | 0       | 0     |
| helene_ext/posts_helene_NorthCarolina.csv      | 134     | 134     | +0    | 134      | 0       | 0     |
| helene_ext/posts_helene_TropicalWeather.csv    | 18      | 18      | +0    | 18       | 0       | 0     |
| helene_ext/posts_helene_asheville.csv          | 73      | 73      | +0    | 73       | 0       | 0     |
| helene_ext/posts_helene_florida.csv            | 130     | 130     | +0    | 130      | 0       | 0     |
| helene_ext/posts_helene_hurricane.csv          | 12      | 12      | +0    | 12       | 0       | 0     |
| helene_ext/posts_helene_sarasota.csv           | 27      | 27      | +0    | 27       | 0       | 0     |
| helene_ext/posts_helene_tampa.csv              | 65      | 65      | +0    | 65       | 0       | 0     |
| milton_ext/comments_milton_florida.csv         | 244     | 244     | +0    | 244      | 0       | 0     |
| milton_ext/comments_milton_georgia.csv         | 157     | 157     | +0    | 157      | 0       | 0     |
| milton_ext/comments_milton_hurricane.csv       | 147     | 147     | +0    | 147      | 0       | 0     |
| milton_ext/comments_milton_northcarolina.csv   | 657     | 657     | +0    | 657      | 0       | 0     |
| milton_ext/comments_milton_sarasota.csv        | 138     | 138     | +0    | 138      | 0       | 0     |
| milton_ext/comments_milton_tampa.csv           | 35      | 35      | +0    | 35       | 0       | 0     |
| milton_ext/comments_milton_tropicalweather.csv | 135     | 135     | +0    | 135      | 0       | 0     |
| milton_ext/posts_milton_florida.csv            | 11      | 11      | +0    | 11       | 0       | 0     |
| milton_ext/posts_milton_georgia.csv            | 13      | 13      | +0    | 13       | 0       | 0     |
| milton_ext/posts_milton_hurricane.csv          | 15      | 15      | +0    | 15       | 0       | 0     |
| milton_ext/posts_milton_northcarolina.csv      | 39      | 39      | +0    | 39       | 0       | 0     |
| milton_ext/posts_milton_sarasota.csv           | 2       | 2       | +0    | 2        | 0       | 0     |
| milton_ext/posts_milton_tampa.csv              | 5       | 5       | +0    | 5        | 0       | 0     |
| milton_ext/posts_milton_tropicalweather.csv    | 6       | 6       | +0    | 6        | 0       | 0     |
| **TOTAL (paired)**                             | 135,780 | 135,783 | +3    | 135,779  | 1       | 4     |

## White House (id-set, filenames differ across the two sides)

| file                | frozen | rerun | delta | retained | removed | added |
| ------------------- | ------ | ----- | ----- | -------- | ------- | ----- |
| whitehouse posts    | 15     | 23    | +8    | 15       | 0       | 8     |
| whitehouse comments | 4,109  | 4,769 | +660  | 4,109    | 0       | 660   |

## Interpretation

**The community Reddit corpus re-collects almost exactly.** Across all four
paired groups (Debby, Helene, both window extensions) — 135,780 frozen rows — a
fresh pull a month later returns **135,783 rows: 1 removed, 4 added, everything
else retained.** That is a **0.004 % change (5 of ~135,780 ids)**, and the deltas
are ordinary Reddit churn, not archive instability: one comment
(`helene/comments_helene_florida`) was deleted/removed since June, and a handful
(`debby/tampa` +1, `helene/tampa` +3) were edited or landed at a page boundary so
the cursor now includes them. Every post file and every extension file is
identical. This is strong positive evidence that the frozen corpus is a faithful,
re-collectable snapshot — the collectors run end-to-end and reproduce the data.

**The White House delta is a method difference, not drift.** WH shows +8 posts /
+660 comments but **0 removed** — the re-pull is a strict _superset_ of the frozen
raw files. `pull_whitehouse.py` collects _every_ `u/WhiteHouse` post in the
Aug 1–Nov 15 season and tags them, so the raw re-pull (23 posts / 4,769 comments)
includes the non-storm posts — Halloween, the FTC "click-to-cancel" rule, aviation
and Biden-briefing image posts, etc. — that the frozen storm-tagged
`helene_posts` / `milton_posts` files (15 posts / 4,109 comments) already
filtered out. The **canonical analysis WH set (12 posts / 2,193 comments)** sits
further downstream still, after the single-hurricane de-duplication (2026-06-18),
event-window restriction, and cleaning. So the WH "growth" reflects the raw
collector's wider scope, not the archive changing under us — the 0 removed
confirms nothing from the frozen pull disappeared.

Milton's _primary_ pull is not in this diff: Its window extension (`milton_ext`) is
included above and reproduces exactly (0 removed, 0 added).

**No downstream file was changed and the frozen corpus remains the analysis
basis** (`master_vader_roberta_topics.csv` still 187,359 rows; per-source
3,413 / 121,053 / 12 / 2,193). The re-collection _validates_ that corpus rather
than replacing it.
