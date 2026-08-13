# Week 8 — pipeline re-run log

Stages run: 32 | failed: 0 | skipped (Colab): 3
Total runtime: 175.2s

| #   | stage                                                        | result | seconds |
| --- | ------------------------------------------------------------ | ------ | ------- |
| 1   | Facebook standardization (6 raw xlsx -> facebook_master.csv) | ok     | 89.7    |
| 2   | Split Facebook into posts / comments                         | ok     | 0.7     |
| 3   | VADER on the split Facebook files                            | ok     | 2.6     |
| 4   | Merge Reddit pulls -> reddit_clean.csv (window filter)       | ok     | 3.2     |
| 5   | Thread relevance + bot removal -> reddit_relevant.csv        | ok     | 2.8     |
| 6   | VADER on the Reddit relevant corpus                          | ok     | 8.9     |
| 7   | Split Reddit into posts / comments                           | ok     | 1.2     |
| 8   | Clean White House threads                                    | ok     | 0.5     |
| 9   | VADER on the White House files                               | ok     | 0.7     |
| 10  | Three-way comparison table (posts)                           | ok     | 0.5     |
| 11  | Three-way comparison table (comments)                        | ok     | 0.9     |
| 12  | Build the master snapshot (guardrail: 187,359 rows)          | ok     | 2.1     |
| 13  | Topic distributions + chi-square                             | ok     | 2.4     |
| 14  | Topic figures                                                | ok     | 2.8     |
| 15  | Data integrity verification (expects ALL CHECKS PASSED)      | ok     | 3.0     |
| 16  | Hypotheses H1/H3/H4/H7 (Jose)                                | ok     | 2.1     |
| 17  | Hypotheses H1/H3/H4/H7 (Angelo, independent cross-check)     | ok     | 21.6    |
| 18  | H2 temporal trajectory                                       | ok     | 3.6     |
| 19  | H5 subreddit tiers                                           | ok     | 2.3     |
| 20  | Method validation vs the 400-item gold standard              | ok     | 2.1     |
| 21  | Results grid                                                 | ok     | 2.5     |
| 22  | Combine all 7 hypotheses into one CSV                        | ok     | 0.4     |
| 23  | F1 dataset overview                                          | ok     | 1.8     |
| 24  | F3 three-way means                                           | ok     | 2.2     |
| 25  | F4 sentiment distribution                                    | ok     | 2.3     |
| 26  | F6 VADER x RoBERTa agreement                                 | ok     | 1.7     |
| 27  | F7 topic distribution by source                              | ok     | 2.0     |
| 28  | F8 topic evolution                                           | ok     | 2.9     |
| 29  | F9 White House case study                                    | ok     | 1.8     |
| 30  | H7 per-hurricane check                                       | ok     | 1.6     |
| 31  | Landfall trajectories                                        | ok     | 1.4     |
| 32  | Unit tests                                                   | ok     | 1.2     |

## Skipped (Colab GPU)

- RoBERTa scoring (Colab GPU notebook) — `code/week3_roberta_agreement/RoBERTa.ipynb`
- BERTopic topic modelling (Colab GPU notebook) — `code/week4_bertopic/BERTopic.ipynb`
- Stamp human topic labels onto the six files — `needs BERTopic *_vader_roberta_topics.csv from Colab/Drive`

## Stage output (tail)

### Facebook standardization (6 raw xlsx -> facebook_master.csv)

```
Reading Phillips/Debby ...
  running total: 16373
Reading Phillips/Helene ...
  running total: 30780
Reading Phillips/Milton ...
  [Milton DP] FIX: post 9 date 2025-10-05 → 2024 (raw typo)
  running total: 60281
Reading Greg Dee (all 3) ...
  running total: 60688

WROTE /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/data/facebook/facebook_master.csv  (60688 rows)
```

### Split Facebook into posts / comments

```
facebook_posts.csv    952 rows
facebook_comments.csv 59,736 rows
master left intact    60,688 rows (facebook_master.csv)
```

### VADER on the split Facebook files

```
[scored] facebook_posts.csv       952 rows -> facebook_posts_vader.csv
         labels: {'negative': 420, 'positive': 332, 'neutral': 200}
         mean compound: 0.0082
[scored] facebook_comments.csv    59,736 rows -> facebook_comments_vader.csv
         labels: {'positive': 27163, 'neutral': 22181, 'negative': 10392}
         mean compound: 0.1703
```

### Merge Reddit pulls -> reddit_clean.csv (window filter)

```
  clean rows out:     185,668

  by hurricane / type:
hurricane  type
debby      comment    31718
           post        1400
helene     comment    65774
           post        2691
milton     comment    81672
           post        2413

Wrote 3 files to /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/data/reddit/combined
```

### Thread relevance + bot removal -> reddit_relevant.csv

```
milton     Georgia             1818
debby      NorthCarolina       1122
           Georgia             1052
helene     NorthCarolina        916
           sarasota             686
debby      sarasota             636
           tampa                594
           hurricane            452
helene     HurricaneHelene      170

Wrote reddit_clean_flagged.csv + reddit_relevant.csv + whitehouse_relevant.csv to /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/data/reddit/combined
(reddit_clean.csv and raw files untouched)
```

### VADER on the Reddit relevant corpus

```
[scored] 124466 rows -> /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/data/reddit/combined/reddit_relevant_vader.csv
{'positive': 51994, 'negative': 39132, 'neutral': 33340}
```

### Split Reddit into posts / comments

```
facebook_posts.csv    3,413 rows
facebook_comments.csv 121,053 rows
master left intact    124,466 rows (reddit_relevant_vader.csv)
```

### Clean White House threads

```

helene_posts.csv (posts)
  r/pics rows removed          : 0
  Total dropped                : 0
  Rows remaining               : 10

milton_posts.csv (posts)
  r/pics rows removed          : 3
  Total dropped                : 3
  Rows remaining               : 2

Done.
```

### VADER on the White House files

```
[scored] 12 rows -> /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/data/vader/whitehouse_threads_posts_vader.csv
         {'positive': 10, 'negative': 1, 'neutral': 1}
[scored] 2193 rows -> /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/data/vader/whitehouse_threads_comments_vader.csv
         {'positive': 930, 'negative': 792, 'neutral': 471}
```

### Three-way comparison table (posts)

```

Saved: /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/data/merged/vader_comparison_table_posts.csv

             data_source hurricane    N  mean_compound  pct_positive  pct_negative  pct_neutral
          facebook_posts     Debby  254         0.0070          32.3          49.2         18.5
          facebook_posts    Helene  322         0.0103          34.8          46.0         19.3
          facebook_posts    Milton  376         0.0073          36.7          39.1         24.2
   reddit_relevant_posts     debby  246         0.1170          43.9          28.0         28.0
   reddit_relevant_posts    helene  883         0.0827          40.7          31.1         28.2
whitehouse_threads_posts    helene   10         0.5855          80.0          10.0         10.0
   reddit_relevant_posts    milton 2284         0.0746          41.2          31.8         27.0
whitehouse_threads_posts    milton    2         0.7731         100.0           0.0          0.0
```

### Three-way comparison table (comments)

```

Saved: /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/data/merged/vader_comparison_table_comments.csv

                data_source hurricane     N  mean_compound  pct_positive  pct_negative  pct_neutral
          facebook_comments     Debby 16199         0.1990          48.9          15.7         35.4
          facebook_comments    Helene 14229         0.1922          47.7          15.5         36.9
          facebook_comments    Milton 29308         0.1439          42.5          19.3         38.2
   reddit_relevant_comments     debby  8766         0.0864          44.4          29.6         26.0
   reddit_relevant_comments    helene 32948         0.0780          42.8          29.6         27.6
whitehouse_threads_comments    helene  1963         0.0196          41.8          36.4         21.8
   reddit_relevant_comments    milton 79339         0.0480          41.1          32.4         26.5
whitehouse_threads_comments    milton   230         0.0624          47.4          33.9         18.7
```

### Build the master snapshot (guardrail: 187,359 rows)

```
per-source row counts:
  facebook_posts                      952 (expected 952) OK
  facebook_comments                 59736 (expected 59736) OK
  reddit_relevant_posts              3413 (expected 3413) OK
  reddit_relevant_comments         121053 (expected 121053) OK
  whitehouse_threads_posts             12 (expected 12) OK
  whitehouse_threads_comments        2193 (expected 2193) OK

total rows: 187359 (expected 187359)
duplicate (id, source): 0

OK -- wrote /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/data/merged/master_vader_roberta_topics.csv
```

### Topic distributions + chi-square

```
gratitude                                 0.0000    0.0866                  0.0
preparedness                              0.0653    0.0159                  0.0
forecast analysis                         0.3003    0.3379                  0.0
evacuation logistics                      0.0537    0.0404                  0.0
political / FEMA criticism                0.2412    0.0000                  1.0
misinformation                            0.0000    0.0000                  0.0
government resources                      0.0019    0.0075                  0.0
personal experience                       0.3025    0.3393                  0.0
emotional response                        0.0352    0.1725                  0.0
  source x topic: chi2=26,713.2, dof=14, p=0.00e+00, V=0.385
  within-Reddit: chi2=5,635.7, dof=6, p=0.00e+00, V=0.303
  hurricane x topic: chi2=4,842.2, dof=14, p=0.00e+00, V=0.164
```

### Topic figures

```
wrote topic_dist_by_source_type
wrote topic_heatmap_by_hurricane
wrote topic_temporal_evolution
wrote wh_topic_breakout
```

### Data integrity verification (expects ALL CHECKS PASSED)

```
- facebook_posts: 31.2% raw label agreement
- facebook_comments: 62.0% raw label agreement
- reddit_relevant_posts: 46.4% raw label agreement
- reddit_relevant_comments: 51.6% raw label agreement
- whitehouse_threads_posts: 41.7% raw label agreement
- whitehouse_threads_comments: 49.3% raw label agreement

## Verdict

**ALL CHECKS PASSED.** Clear to proceed to Week 5 hypothesis testing.

Report written to hurricane_sentiment_analysis/docs/week5/data_verification_week5.md
```

### Hypotheses H1/H3/H4/H7 (Jose)

```
- **WH vs Reddit community**: MWU U=128427604, p=8.56e-03, r=-0.032 (mean WH=0.024, Reddit=0.059); variance SD WH=0.516 vs Reddit=0.468, Levene W=62.7, p=2.40e-15.
- **WH vs FB Phillips**: MWU U=55524380, p=2.04e-35, r=-0.152 (mean WH=0.024, FB=0.170).
- **Within WH, political-keyword vs not** (644 vs 1549): MWU U=466718, p=1.72e-02, r=-0.064 (mean political=-0.022, non=0.043).

### RoBERTa
- **WH vs Reddit community**: MWU U=109785884, p=6.51e-44, r=-0.173 (mean WH=-0.363, Reddit=-0.232); variance SD WH=0.512 vs Reddit=0.506, Levene W=1.1, p=2.97e-01.
- **WH vs FB Phillips**: MWU U=36921021, p=1.04e-264, r=-0.436 (mean WH=-0.363, FB=0.048).
- **Within WH, political-keyword vs not** (644 vs 1549): MWU U=417404, p=1.69e-09, r=-0.163 (mean political=-0.476, non=-0.316).


Wrote hurricane_sentiment_analysis/docs/week5/hypothesis_tests_results.md
Wrote hurricane_sentiment_analysis/data/merged/hypothesis_tests_results_jose.csv  (36 rows)
```

### Hypotheses H1/H3/H4/H7 (Angelo, independent cross-check)

```
Wrote hurricane_sentiment_analysis/data/merged/hypothesis_tests_results_angelo.md
Wrote hurricane_sentiment_analysis/data/merged/hypothesis_tests_results_angelo.csv
```

### H2 temporal trajectory

```
## In-window White House comments (plotted on F2)

- Debby window (-5, 0): 0 in-window (WH activity outside window)
- Helene window (-4, 1): 0 in-window (WH activity outside window)
- Milton window (-5, 0): 140 in-window (day 0: 140)

## Figures
- `figures/h2_temporal_curves.png/.pdf` (VADER) — 3 panels, FB+Reddit all panels, WH on Milton only.
- `figures/h2_temporal_curves_roberta.png/.pdf` (RoBERTa cross-check).
- Note: in-window WH comments exist only for Milton (day 0 only — the 140 government_response comments on landfall day; the other 90 WH Milton comments fall on days 1–7, post-landfall and outside the −5..0 window, so they are correctly clipped from this figure). Helene WH activity is outside the −4..+1 window.

Wrote docs/week5/h2_temporal_results.md and figures/h2_temporal_curves*.{png,pdf}
```

### H5 subreddit tiers

```
| RoBERTa | full data | 40,209 | 16,326 | 22,804 | 904.3 | 4.29e-197 | YES | expert vs local: p=2.4e-114, r=+0.12; expert vs statewide: p=6.5e-148, r=+0.12; local vs statewide: p=1.0e+00, r=+0.00 |
| RoBERTa | largest thread excl. | 29,099 | 12,209 | 19,703 | 590.4 | 6.21e-129 | YES | expert vs local: p=6.2e-10, r=+0.04; expert vs statewide: p=1.6e-129, r=+0.13; local vs statewide: p=8.6e-40, r=+0.09 |

Tier means (full data): VADER expert=0.060, local=0.038, statewide=0.034; RoBERTa expert=-0.206, local=-0.293, statewide=-0.291.
- **VADER vs RoBERTa agree on significance:** YES (VADER full sig, RoBERTa full sig).
- **Excluding the largest thread changes the verdict:** no (VADER sig→sig, RoBERTa sig→sig).

## Figure
- `figures/h5_subreddit_box.png/.pdf` — box plots of VADER compound by tier, per hurricane.

Wrote docs/week5/h5_subreddit_results.md + figures/h5_subreddit_box.*
Wrote data/merged/h5_results_jose.csv (39 rows)
```

### Method validation vs the 400-item gold standard

```
Among Facebook comments each method labels **positive**, the fraction carrying the human gratitude tag:

| method | FB comments labeled positive | of those, gratitude-tagged | inflation rate |
|---|---|---|---|
| VADER | 62 | 15 | 24.2% |
| RoBERTa | 42 | 14 | 33.3% |

For reference, among human-labeled-positive FB comments (35), 40.0% are gratitude-tagged.

Interpretation: a non-trivial share of Facebook 'positive' sentiment is gratitude directed at the communicator (thanking Denis Phillips) rather than positive feeling about the storm — so the Facebook–Reddit positivity gap (H1) is partly a person-directed-thanks artifact. Sample is small (gold-standard FB comments only); report as an estimate, not a population rate.

Wrote /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/docs/week5/method_validation_report.md
```

### Results grid

```
| H2 temporal (interaction) | RoBERTa | OLS interaction | β=+0.00364 | 4.54e-02 | R²=0.0604 |
| H3 intensity gap | RoBERTa | Descriptive (gap order) | gaps D/H/M=0.318/0.286/0.240 | — | Debby not smallest → n.s. |
| H4 cross-storm (Reddit) | RoBERTa | Kruskal-Wallis | H=245.1 | 5.95e-54 | ε²=0.0020 |
| H4 cross-storm (Facebook) | RoBERTa | Kruskal-Wallis | H=644.0 | 1.41e-140 | ε²=0.0107 |
| H5 tiers (debby) | RoBERTa | Kruskal-Wallis | H=39.9 | 2.19e-09 | ε²=0.0043 |
| H5 tiers (helene) | RoBERTa | Kruskal-Wallis | H=35.1 | 2.41e-08 | ε²=0.0010 |
| H5 tiers (milton) | RoBERTa | Kruskal-Wallis | H=904.3 | 4.29e-197 | ε²=0.0114 |
| H7 WH vs Reddit | RoBERTa | MWU (+ Levene) | U=1.1e+08; Levene W=1.1 (p=3.0e-01) | 6.51e-44 | rank-biserial -0.173 |
| H7 WH vs FB | RoBERTa | Mann-Whitney U | U=3.69e+07 | 1.04e-264 | rank-biserial -0.436 |
| H7 WH political vs not | RoBERTa | Mann-Whitney U | U=4.17e+05 | 1.69e-09 | rank-biserial -0.163 |

Wrote /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/docs/week5/statistical_results_table.md
```

### Combine all 7 hypotheses into one CSV

```
Wrote /Users/jaas29/Hurricane Sentiment/hurricane_sentiment_analysis/data/merged/hypothesis_tests_all7_jose.csv  (93 rows across H1-H7)
hypothesis
H1     8
H2    18
H3     6
H4    16
H5    39
H7     6
```

### F1 dataset overview

```
| Reddit community | 9,012 | 33,831 | 81,623 | 124,466 |
| White House | 0 | 1,973 | 232 | 2,205 |
| **total** | 25,465 | 50,355 | 111,539 | **187,359** |

Callout: the White House Reddit account only existed for Helene and Milton (0 records for Debby).

Figure: `figures/f1_dataset_overview.png/.pdf` (300 dpi).

Status: **FINAL**.

Wrote figures/f1_dataset_overview.png/.pdf + docs/week6/f1_dataset_overview_results.md
Grand total: 187,359
```

### F3 three-way means

```
| Facebook | helene | 14,229 | +0.0866 | 0.0088 |  |
| Reddit community | helene | 32,948 | -0.1994 | 0.0055 | *** |
| White House | helene | 1,963 | -0.3744 | 0.0224 |  |
| Facebook | milton | 29,308 | -0.0082 | 0.0062 |  |
| Reddit community | milton | 79,339 | -0.2481 | 0.0035 | *** |
| White House | milton | 230 | -0.2676 | 0.0725 |  |

Figures: `figures/f3_three_way_{vader,roberta}.png/.pdf` (300 dpi).

Status: **built (VADER + RoBERTa).**

Wrote figures/f3_three_way_{vader,roberta}.* + docs/week6/f3_three_way_results.md
```

### F4 sentiment distribution

```
| Facebook | helene | 14,229 | 18.7 | 53.9 | 27.5 |
| Reddit community | helene | 32,948 | 38.6 | 48.0 | 13.4 |
| White House | helene | 1,963 | 54.8 | 35.5 | 9.8 |
| Facebook | milton | 29,308 | 24.4 | 53.2 | 22.4 |
| Reddit community | milton | 79,339 | 41.7 | 47.2 | 11.1 |
| White House | milton | 230 | 47.0 | 36.5 | 16.5 |

Figures: `figures/f4_sentiment_distribution_{vader,roberta}.png/.pdf` (300 dpi).

Status: **built (VADER + RoBERTa).**

Wrote figures/f4_sentiment_distribution_{vader,roberta}.* + docs/week6/f4_sentiment_distribution_results.md
```

### F6 VADER x RoBERTa agreement

```

Per-class agreement (VADER label = RoBERTa label, of VADER rows in that class):

- negative: 68.1% (34,544/50,737)
- neutral: 75.0% (42,154/56,193)
- positive: 32.1% (25,785/80,429)

Figure: `figures/f6_vader_roberta_agreement.png/.pdf` (300 dpi).

Status: **built.**

Wrote figures/f6_vader_roberta_agreement.* + docs/week6/f6_agreement_results.md
```

### F7 topic distribution by source

```
| emotional response | 2,096 | 4,966 | 0 | 7,062 |
| political / FEMA criticism | 14,274 | 0 | 1,972 | 16,246 |
| forecast analysis | 16,476 | 9,014 | 0 | 25,490 |
| personal experience | 17,778 | 9,768 | 0 | 27,546 |

Source totals used for percentages: Reddit community 57,350, Facebook 27,850, White House 2,069.

Figure: `figures/f7_topic_distribution_by_source_type.png/.pdf` (300 dpi).

Status: **built**.

Wrote figures/f7_topic_distribution_by_source_type.png/.pdf + docs/week6/f7_topic_distribution_by_source_type_results.md
```

### F8 topic evolution

```
|---|---:|
| debby | 1,547 |
| helene | 0 |
| milton | 1,273 |

Note: Helene day -5 is empty because upstream Reddit event-window filtering starts Helene at -4 in collection/merge logic.

Figure: `figures/f8_topic_evolution.png/.pdf` (300 dpi).

Status: **built**.

Wrote figures/f8_topic_evolution.png/.pdf + docs/week6/f8_topic_evolution_results.md
```

### F9 White House case study

```
| 2024-10-14 | 22 | -0.0145 | -0.2698 |
| 2024-10-15 | 19 | -0.1103 | -0.4700 |
| 2024-10-16 | 32 | -0.0262 | -0.5551 |
| 2024-10-17 | 5 | -0.1739 | -0.2340 |
| 2024-10-18 | 4 | +0.1021 | -0.7640 |
| 2024-10-19 | 2 | +0.2470 | -0.7792 |

Figure: `figures/f9_whitehouse_case_study.png/.pdf` (300 dpi).

Status: **built**.

Wrote figures/f9_whitehouse_case_study.png/.pdf + docs/week6/f9_whitehouse_case_study_results.md
```

### H7 per-hurricane check

```
wrote docs/week6/h7_pooled_helene_check.md
helene  VADER   n=1963 WHmean=+0.020 FB r=-0.184 p=1.3e-41 | RD r=-0.059 p=1.1e-05
helene  RoBERTa n=1963 WHmean=-0.374 FB r=-0.487 p=5.2e-269 | RD r=-0.220 p=3.2e-60
milton  VADER   n= 230 WHmean=+0.062 FB r=-0.067 p=7.0e-02 | RD r=+0.027 p=4.8e-01
milton  RoBERTa n= 230 WHmean=-0.268 FB r=-0.295 p=1.2e-14 | RD r=-0.059 p=1.2e-01
```

### Landfall trajectories

```
   Milton comments    Facebook   -3         0.1429  4578
   Milton comments    Facebook   -2         0.1244  6060
   Milton comments    Facebook   -1         0.1900  3802
   Milton comments    Facebook    0         0.1469 10262
   Milton comments      Reddit   -5         0.0203  1273
   Milton comments      Reddit   -4         0.0310  5547
   Milton comments      Reddit   -3         0.0557 10720
   Milton comments      Reddit   -2         0.0395 18329
   Milton comments      Reddit   -1         0.0471 22416
   Milton comments      Reddit    0         0.0588 21054
   Milton comments White House    0         0.1070   140
   Milton comments White House    1         0.0555    38
```

### Unit tests

```
..                                                                       [100%]
2 passed in 0.94s
```
