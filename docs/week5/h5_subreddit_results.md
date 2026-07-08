# H5 — Subreddit-Tier Differences (Student B)

Tiers (Tania 2026-06-30): **expert**=TropicalWeather/hurricane/HurricaneHelene, **local**=tampa/sarasota/asheville, **statewide**=florida/Georgia/NorthCarolina. Comment-level, per hurricane.

**Data-integrity confirmation for Tania:** the four excluded subs (r/southcarolina, r/Tennessee, r/Virginia, r/pics) appear in **0 rows** of the H5 corpus (`reddit_relevant_comments`); they exist only in the White House files, all tagged `government_response` (558 comments) — i.e. purely WH-reaction data in the H7 lane, nothing organic swept in.

Corpus (community comments): expert n=56,501, local n=25,737, statewide n=38,815.

## Debby
Comments: 8,766. Largest-thread-per-subreddit exclusion removes 2,364 comments across 7 threads.

| method | variant | n expert | n local | n statewide | KW H | p | significant? | pairwise (Bonferroni) |
|---|---|---|---|---|---|---|---|---|
| VADER | full data | 2,379 | 1,182 | 5,205 | 0.1 | 9.68e-01 | no | n/a (KW n.s.) |
| VADER | largest thread excl. | 1,220 | 903 | 4,279 | 13.3 | 1.30e-03 | YES | expert vs local: p=1.0e+00, r=+0.01; expert vs statewide: p=4.9e-03, r=+0.06; local vs statewide: p=4.8e-02, r=+0.05 |
| RoBERTa | full data | 2,379 | 1,182 | 5,205 | 39.9 | 2.19e-09 | YES | expert vs local: p=6.6e-01, r=+0.03; expert vs statewide: p=1.7e-09, r=+0.09; local vs statewide: p=1.2e-02, r=+0.05 |
| RoBERTa | largest thread excl. | 1,220 | 903 | 4,279 | 112.5 | 3.66e-25 | YES | expert vs local: p=1.0e+00, r=-0.02; expert vs statewide: p=1.5e-18, r=+0.17; local vs statewide: p=4.0e-13, r=+0.16 |

Tier means (full data): VADER expert=0.090, local=0.089, statewide=0.084; RoBERTa expert=-0.168, local=-0.173, statewide=-0.226.
- **VADER vs RoBERTa agree on significance:** NO (VADER full n.s., RoBERTa full sig).
- **Excluding the largest thread changes the verdict:** YES — FLAG (VADER n.s.→sig, RoBERTa sig→sig).
  - ⚠ **Flag for Tania before paper** (method disagreement or exclusion-sensitive).

## Helene
Comments: 32,948. Largest-thread-per-subreddit exclusion removes 11,388 comments across 9 threads.

| method | variant | n expert | n local | n statewide | KW H | p | significant? | pairwise (Bonferroni) |
|---|---|---|---|---|---|---|---|---|
| VADER | full data | 13,913 | 8,229 | 10,806 | 1.7 | 4.20e-01 | no | n/a (KW n.s.) |
| VADER | largest thread excl. | 6,299 | 6,532 | 8,729 | 1.3 | 5.31e-01 | no | n/a (KW n.s.) |
| RoBERTa | full data | 13,913 | 8,229 | 10,806 | 35.1 | 2.41e-08 | YES | expert vs local: p=5.4e-01, r=-0.01; expert vs statewide: p=2.6e-06, r=+0.04; local vs statewide: p=5.5e-07, r=+0.04 |
| RoBERTa | largest thread excl. | 6,299 | 6,532 | 8,729 | 42.4 | 6.32e-10 | YES | expert vs local: p=8.1e-03, r=-0.03; expert vs statewide: p=1.7e-03, r=+0.03; local vs statewide: p=5.6e-10, r=+0.06 |

Tier means (full data): VADER expert=0.074, local=0.085, statewide=0.077; RoBERTa expert=-0.199, local=-0.181, statewide=-0.215.
- **VADER vs RoBERTa agree on significance:** NO (VADER full n.s., RoBERTa full sig).
- **Excluding the largest thread changes the verdict:** no (VADER n.s.→n.s., RoBERTa sig→sig).
  - ⚠ **Flag for Tania before paper** (method disagreement or exclusion-sensitive).

## Milton
Comments: 79,339. Largest-thread-per-subreddit exclusion removes 18,328 comments across 7 threads.

| method | variant | n expert | n local | n statewide | KW H | p | significant? | pairwise (Bonferroni) |
|---|---|---|---|---|---|---|---|---|
| VADER | full data | 40,209 | 16,326 | 22,804 | 38.3 | 4.80e-09 | YES | expert vs local: p=5.8e-05, r=+0.02; expert vs statewide: p=5.7e-08, r=+0.03; local vs statewide: p=1.0e+00, r=+0.00 |
| VADER | largest thread excl. | 29,099 | 12,209 | 19,703 | 46.0 | 1.03e-10 | YES | expert vs local: p=9.5e-01, r=-0.01; expert vs statewide: p=5.0e-09, r=+0.03; local vs statewide: p=7.7e-08, r=+0.04 |
| RoBERTa | full data | 40,209 | 16,326 | 22,804 | 904.3 | 4.29e-197 | YES | expert vs local: p=2.4e-114, r=+0.12; expert vs statewide: p=6.5e-148, r=+0.12; local vs statewide: p=1.0e+00, r=+0.00 |
| RoBERTa | largest thread excl. | 29,099 | 12,209 | 19,703 | 590.4 | 6.21e-129 | YES | expert vs local: p=6.2e-10, r=+0.04; expert vs statewide: p=1.6e-129, r=+0.13; local vs statewide: p=8.6e-40, r=+0.09 |

Tier means (full data): VADER expert=0.060, local=0.038, statewide=0.034; RoBERTa expert=-0.206, local=-0.293, statewide=-0.291.
- **VADER vs RoBERTa agree on significance:** YES (VADER full sig, RoBERTa full sig).
- **Excluding the largest thread changes the verdict:** no (VADER sig→sig, RoBERTa sig→sig).

## Figure
- `figures/h5_subreddit_box.png/.pdf` — box plots of VADER compound by tier, per hurricane.
