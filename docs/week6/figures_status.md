# Week 6 — Core Figures Status (Student A / José)

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

## Key findings surfaced by the figures

- **F1:** Milton dominates (111,539 records); WH tiny (2,205) and Helene/Milton only.
- **F3:** Facebook > Reddit sentiment every storm (H1 \*\*\*, both methods); WH most negative (H7). RoBERTa puts Reddit/WH clearly below zero.
- **F4:** Facebook most positive; RoBERTa reclassifies much of VADER's "positive" as neutral/negative.
- **F6:** VADER/RoBERTa agree 54.7% overall; VADER-"positive" agrees only 32% (positivity inflation).
