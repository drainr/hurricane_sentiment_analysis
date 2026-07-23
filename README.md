# Hurricane Sentiment Analysis

Cross-platform NLP study of public sentiment during three 2024 Atlantic hurricanes
(Debby, Helene, Milton), comparing Facebook (Denis Phillips), organic Reddit
communities, and White House Reddit posts. VADER + RoBERTa sentiment, BERTopic
topics, seven hypotheses (H1–H7). Target: FLAIRS-40 (2027).

Advisor: Tania Roy. Two interns, 8-week summer project.

## Environment

- **Python 3.12** (developed and verified on 3.12.2)
- `pip install -r requirements.txt`
- RoBERTa model string: **`cardiffnlp/twitter-roberta-base-sentiment-latest`**
- VADER: standalone `vaderSentiment` (emoji-aware), **not** NLTK's copy — the two
  disagree on emoji, and the emoji-aware scores are the project's locked choice.

Two stages need a GPU and run as Colab notebooks: RoBERTa scoring (week 3) and
BERTopic (week 4). Everything else runs locally in about 3 minutes.

## Reproduce every step

Frozen inputs are the raw collected files: the six Facebook workbooks in
`data/facebook/raw_xlsx/` and the Reddit / White House pulls in `data/reddit/`.
Everything below is rebuilt from those.

Run the whole local lane at once:

```bash
python3 code/week8_reproducibility/rerun_pipeline.py
```

or step by step, in this order. Every script anchors its paths to the repo root,
so the working directory does not matter.

| # | Command | In | Out |
|---|---|---|---|
| 1 | `python3 code/week1_setup_exploration/build_facebook_master.py` | 6 xlsx in `data/facebook/raw_xlsx/` | `facebook_master.csv` — **60,688** rows |
| 2 | `python3 code/week2_collection_vader/split_facebook.py` | `facebook_master.csv` | `facebook_posts.csv` **952**, `facebook_comments.csv` **59,736** |
| 3 | `python3 code/week2_collection_vader/run_vader_facebook_split.py` | the two above | `*_vader.csv` |
| 4 | `python3 code/week2_collection_vader/merge_reddit_angelo.py` | `data/reddit/*/` | `reddit_clean.csv` — **185,668** in-window rows |
| 5 | `python3 code/week2_collection_vader/build_relevant_angelo_fixed.py` | `reddit_clean.csv` | `reddit_relevant.csv` — **124,466** |
| 6 | `python3 code/week2_collection_vader/run_vader_reddit.py` | `reddit_relevant.csv` | `reddit_relevant_vader.csv` |
| 7 | `python3 code/week2_collection_vader/split_reddit.py` | the above | posts **3,413**, comments **121,053** |
| 8 | `python3 code/week2_collection_vader/clean_whitehouse_data.py` | `data/reddit/whitehouse/` | `whitehouse_threads_*.csv` — **12** posts, **2,193** comments |
| 9 | `python3 code/week2_collection_vader/run_vader_whitehouse.py` | the two above | `data/vader/whitehouse_threads_*_vader.csv` |
| 10 | `python3 code/week2_collection_vader/three_way_comparison.py --out <path> <3 files>` | the `*_vader.csv` | `data/merged/vader_comparison_table_{posts,comments}.csv` |

**— Colab boundary —** steps 11 and 12 run on GPU. See
[`docs/week8/colab_reproducibility_run.md`](docs/week8/colab_reproducibility_run.md).

| # | Notebook | Out |
|---|---|---|
| 11 | `code/week3_roberta_agreement/RoBERTa.ipynb` | `*_vader_roberta.csv` |
| 12 | `code/week4_bertopic/BERTopic.ipynb` | `*_vader_roberta_topics.csv` + saved models |

Download those back into `data/`, then continue:

| # | Command | Out |
|---|---|---|
| 13 | `python3 code/week4_bertopic/label_topics.py --codebook "docs/week4/Topic Codebook.md" --in_dir data/processed --out_dir data/processed` | `*_labeled.csv` ×6 |
| 14 | `python3 code/week4_bertopic/build_master.py --in_dir data/processed --out data/merged/master_vader_roberta_topics.csv` | master — **187,359** rows, 0 duplicate (id, source) |
| 15 | `python3 code/week4_bertopic/topic_distributions.py` and `plot_topics.py` | topic tables, chi-square, topic figures |
| 16 | `python3 code/week5_hypotheses/verify_data.py` | must print **ALL CHECKS PASSED** |
| 17 | `hypothesis_tests_jose.py`, `hypothesis_tests.py`, `h2_temporal.py`, `h5_subreddit.py`, `evaluate_methods.py`, `results_table.py`, `combine_results_jose.py` | `docs/week5/*`, `data/merged/hypothesis_tests_*` |
| 18 | `f1/f3/f4/f6/f7/f8/f9`, `h7_per_hurricane.py`, `plot_landfall_trajectories.py` in `code/week6_figures/` | `figures/*` (300 dpi PNG + PDF) |
| 19 | `python3 -m pytest code/week5_hypotheses/tests/` | 2 passed |

### Two things deliberately left out of the re-run

- **Collection** (`use_arctic_shift.py`, `collect_subreddit.py`, `pull_*.py`,
  `collect_*_ext.py`). These query the Arctic Shift archive, whose contents have
  changed since June, so a fresh pull cannot match the analysed corpus. They are
  kept runnable and documented; the raw files they produced are the frozen input.
- **`build_ground_truth.py`**. It fills consensus labels only where the two
  annotators agreed, so re-running it erases the 38 sentiment and 4 gratitude
  disagreements that were adjudicated by hand. `ground_truth_400.csv` is a curated
  artifact; the script refuses to overwrite an adjudicated copy.

### Verifying a re-run

```bash
python3 code/week8_reproducibility/snapshot_outputs.py --out before.csv
python3 code/week8_reproducibility/rerun_pipeline.py
python3 code/week8_reproducibility/snapshot_outputs.py --out after.csv
python3 code/week8_reproducibility/snapshot_outputs.py --compare before.csv after.csv
```

Expect `VERIFIED: every hash-compared output is byte-identical`. Figures are
checked on existence and size rather than hash, because matplotlib writes a
creation timestamp into every PNG and PDF. Findings from the Week 8 run are in
[`docs/week8/rerun_verification.md`](docs/week8/rerun_verification.md).

## Canonical counts

Any change to these numbers means something upstream moved.

| file | rows |
|---|---|
| `facebook_posts` | 952 |
| `facebook_comments` | 59,736 |
| `reddit_relevant_posts` | 3,413 |
| `reddit_relevant_comments` | 121,053 |
| `whitehouse_threads_posts` | 12 |
| `whitehouse_threads_comments` | 2,193 |
| `master_vader_roberta_topics` | 187,359 |

## Repository layout

Code is organized **by project week**. Data, docs, and figures stay grouped by
kind and are indexed per week.

```
code/
  common/                    shared library imported across weeks (VADER scorer)
  week1_setup_exploration/   Facebook standardization, Reddit access testing
  week2_collection_vader/    Reddit/WH collection, cleaning, merge, unified VADER
  week3_roberta_agreement/   RoBERTa scoring, VADER↔RoBERTa agreement, 400-item sample
  week4_bertopic/            BERTopic on each corpus, labels, master build
  week5_hypotheses/          H1–H7 tests, method validation, data verification
  week6_figures/             publication figures
  week8_reproducibility/     re-run driver + output fingerprinting
data/                        source CSVs (kept in git) — see data/README.md
docs/                        result write-ups, logs — see docs/README.md
figures/                     exported PNG + PDF (300 dpi)
requirements.txt             pinned dependencies (Python 3.12)
```

See **[code/README.md](code/README.md)** for the file-by-file breakdown of each
week, including which of the two authors' duplicate scripts is canonical.

## Week index

| Week | Focus | Code | Key outputs |
| --- | --- | --- | --- |
| 1 | Setup, data audit, Reddit exploration | `code/week1_setup_exploration/` | Reddit access decision, `facebook_master.csv` |
| 2 | Reddit + WH collection, unified VADER, merge | `code/week2_collection_vader/` | `reddit_relevant*`, `whitehouse_threads*`, `*_vader.csv`, three-way tables |
| 3 | RoBERTa scoring + inter-method agreement | `code/week3_roberta_agreement/` | `*_vader_roberta.csv`, `docs/week4/interannotator_kappa.md`, 400-item sample |
| 4 | BERTopic topic modeling | `code/week4_bertopic/` | topic-labeled files, `docs/week4/Topic Codebook.md`, master file |
| 5 | Hypothesis testing (H1–H7) | `code/week5_hypotheses/` | `docs/week5/hypothesis_tests_results.md`, `method_validation_report.md`, H2/H5 figures |
| 6 | Publication figures + results docs | `code/week6_figures/` | `figures/*`, `docs/week6/*` |
| 7 | Paper drafts | — | methodology, literature review, results narrative |
| 8 | Reproducibility, archive, handoff | `code/week8_reproducibility/` | verified full re-run, this README, pinned `requirements.txt` |

## Conventions

- Colors: Facebook = blue, Reddit community = orange, White House = green.
- `days_from_landfall = 0` on landfall day (Debby Aug 5, Helene Sep 26, Milton Oct 9).
- Event windows: Debby −5..0, Helene −4..+1, Milton −5..0.
- Sources kept as six separate files (facebook / reddit / whitehouse × posts /
  comments); the master file is a derived snapshot — rebuild it, never hand-edit it.
- RoBERTa's score is the **continuous** `roberta_pos − roberta_neg`, never the
  discrete label. The label encoding collapses confidence and changes every
  effect size.
- Reddit cleaning drops rows under **3 words**; BERTopic separately excludes rows
  under **5 words**. These are different thresholds at different stages.
- Effect sizes are the headline, not p-values — at 60k–120k comments everything
  is p < 0.001.
