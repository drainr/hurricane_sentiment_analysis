# Data

Data is kept in git. Six sources (Facebook / Reddit community / White House ×
posts / comments) stay as **separate files** through the pipeline; the master is
a derived snapshot, rebuilt not hand-edited.

## Canonical row counts

| Source                                 | Posts | Comments    |
| -------------------------------------- | ----- | ----------- |
| Facebook (Phillips)                    | 952   | 59,736      |
| Reddit community                       | 3,413 | 121,053     |
| White House                            | 12    | 2,193       |
| **master** (concatenated + provenance) |       | **187,359** |

The Reddit counts are **post-WH-dedup** (the 973 White House comments and 5 WH
posts that the keyword pull had swept in were removed on 2026-06-26). The
`data/roberta/` and `data/vader/` files reflect this fix as of Angelo's latest push.

## Pipeline stages (folder → what it holds → producing code)

| Folder       | Contents                                                                                                              | Produced by                                                                          |
| ------------ | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `facebook/`  | raw + standardized FB (`facebook_master.csv`, split `facebook_posts/comments.csv`), `student_originals/`              | week1 FB standardizer, `week2/split_facebook.py`                                     |
| `reddit/`    | raw collection per hurricane (`debby/`, `helene/`, `milton/`, `*_ext/`, `whitehouse/`) and `combined/` merged corpora | week1–2 collectors, `week2/merge_reddit_angelo.py`, `build_relevant_angelo_fixed.py` |
| `vader/`     | six source files with VADER scores                                                                                    | `week2/run_vader_*.py`                                                               |
| `roberta/`   | six files with VADER + RoBERTa columns; agreement outputs                                                             | `week3/RoBERTa.ipynb`, `week3/vader_roberta_agreement_metrics.py`                    |
| `processed/` | **canonical** six `*_labeled.csv` (VADER + RoBERTa + topics) — the analysis source of truth                           | `week4/label_topics.py`                                                              |
| `merged/`    | `master_vader_roberta_topics.csv`, `ground_truth_400.csv`, comparison + results tables                                | `week4/build_master.py`, `week5/build_ground_truth.py`, `week5` result scripts       |

## Which file to analyze

Read **`data/processed/*_labeled.csv`** — these are the deduped, fully-scored,
topic-labeled files (Reddit = 121,053 / 3,413). Do **not** analyze from `vader/`
or `roberta/` directly unless you need the pre-topic stage.

`ground_truth_400.csv` reads cleanest with `encoding="latin-1"`
