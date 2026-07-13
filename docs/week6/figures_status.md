# Week 6 — Core Figures Status (Student A / Jose)

Color convention: Facebook = blue, Reddit community = orange, White House = green.

| Fig    | What                                                                                                                | Script                                            | Status                                             |
| ------ | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | -------------------------------------------------- |
| **F1** | Dataset overview — stacked bars, records by source × hurricane (WH = 0 for Debby)                                   | `code/week6_figures/f1_dataset_overview.py`       | Final                                              |
| **F2** | Temporal sentiment curves — mean compound by days_from_landfall, 3 panels, 95% CI, WH on Milton day 0               | `code/week5_hypotheses/h2_temporal.py`            | Built                                              |
| **F3** | Three-way source comparison — grouped bars mean sentiment by source × hurricane, 95% CI, H1 stars (VADER + RoBERTa) | `code/week6_figures/f3_three_way.py`              | Built                                              |
| **F4** | Sentiment distribution — 100% stacked % neg/neu/pos by source × hurricane, comment-level (VADER + RoBERTa)          | `code/week6_figures/f4_sentiment_distribution.py` | Built                                              |
| **F5** | Subreddit comparison — box plots by tier, per hurricane (H5)                                                        | `code/week5_hypotheses/h5_subreddit.py`           | Final (VADER-only; add RoBERTa panel before paper) |
| **F6** | VADER vs RoBERTa agreement — 3×3 confusion heatmap, counts + % (overall 54.7%)                                      | `code/week6_figures/f6_agreement_heatmap.py`      | Built                                              |

All figures render PNG + PDF at 300 dpi to `figures/`. Companion result docs in `docs/week6/`. RoBERTa uses the standardized continuous `pos − neg` score.

## Figure captions

- **Figure 1. Dataset composition.** Number of records (posts + comments) per source and hurricane. Facebook n = 60,688, Reddit community n = 124,466, White House n = 2,205 (total 187,359). The White House Reddit account was only active during Helene and Milton, so it has zero records for Debby.
- **Figure 2. Temporal sentiment trajectory.** Mean sentiment (VADER compound) by day relative to landfall, one panel per hurricane. Facebook and Reddit community appear in all three panels; the White House line appears on Milton only (day 0, the single in-window day with WH activity). Shaded bands are 95% confidence intervals and the dashed vertical line marks landfall (day 0). A RoBERTa version is provided as `h2_temporal_curves_roberta`.
- **Figure 3. Mean sentiment by source and hurricane (comment-level).** Grouped bars show mean sentiment for Facebook, Reddit community, and White House per hurricane, with 95% confidence-interval error bars. Brackets mark the Facebook–Reddit comparison (H1) within each hurricane (\*\*\* p < .001). Shown for VADER (compound) and RoBERTa (pos − neg).
- **Figure 4. Sentiment label distribution by source and hurricane (comment-level).** Each bar shows the percentage of comments labeled negative, neutral, and positive. White House has no Debby data. Shown for VADER and RoBERTa.
- **Figure 5. Sentiment by subreddit tier (H5).** Box plots of VADER compound sentiment for the expert, local, and statewide subreddit tiers, one panel per hurricane. Boxes show the interquartile range, the green triangle the mean; outliers hidden for readability.
- **Figure 6. Agreement between VADER and RoBERTa.** 3×3 confusion matrix of VADER vs RoBERTa sentiment labels across all 187,359 records; each cell shows the count and percentage of the total. Overall label agreement is 54.7%.

## Key findings surfaced by the figures

- **F1:** Milton dominates (111,539 records); WH tiny (2,205) and Helene/Milton only.
- **F3:** Facebook > Reddit sentiment every storm (H1 \*\*\*, both methods); WH most negative (H7). RoBERTa puts Reddit/WH clearly below zero.
- **F4:** Facebook most positive; RoBERTa reclassifies much of VADER's "positive" as neutral/negative.
- **F6:** VADER/RoBERTa agree 54.7% overall; VADER-"positive" agrees only 32% (positivity inflation).
