# Code — organized by week

Scripts are grouped by the project week that produced them. The two interns
worked jointly (no Student A/B split), so where both wrote a version of the same
step, **both are kept**, tagged by author, with the canonical one noted here.

Scripts anchor data paths to the repo root (`parents[2]` / `dirname(dirname(HERE))`),
so they run from any working directory. Shared code lives in `common/` and is
imported by name after adding `code/common` to `sys.path`.

## common/
- `vader_sentiment.py` — the shared VADER scorer (standalone, emoji-aware). Both
  interns had an identical copy; unified here. Imported by the `run_vader_*`
  scripts in week 2.

## week1_setup_exploration/
- `use_arctic_shift.py` (Angelo) — Reddit collection via the Arctic Shift API (locked method).
- `collect_subreddit.py` (José) — per-subreddit post + comment-tree pull.
- **Missing source (recover from Drive):** `explore_queries.py` and the Facebook
  standardizer that builds `facebook_master.csv` were committed only as `.pyc`
  and are not in the repo.

## week2_collection_vader/
- `clean_whitehouse_data.py` (Angelo) — WH post/comment cleaning.
- `merge_reddit_jose.py` / `merge_reddit_angelo.py` — Reddit merge to unified schema.
  **Canonical: `merge_reddit_angelo.py`** (carries the final event windows, incl. the
  2026-06-18 window extension).
- `normalize_milton.py` (José) — aligns the teammate's Milton files to the schema.
- `build_relevant_jose.py` / `build_relevant_angelo_fixed.py` — thread-relevance corpus.
  **Canonical: `build_relevant_angelo_fixed.py`** (includes the White House de-dup fix →
  121,053 comments / 3,413 posts).
- `split_facebook.py` (José), `split_reddit.py` (Angelo) — split into posts/comments.
- `run_vader_facebook.py`, `run_vader_facebook_split.py` (José), `run_vader_reddit.py`,
  `run_vader_wh.py` (Angelo) — apply the shared VADER scorer per source.
- `three_way_comparison.py` (Angelo) — Facebook vs Reddit vs WH summary tables.
- **Missing source (recover from Drive):** `pull_comments.py`, `pull_whitehouse.py`,
  `pull_org_mentions.py` (committed only as `.pyc`).

## week3_roberta_agreement/
- `RoBERTa.ipynb` (José) — RoBERTa scoring on Colab (cardiffnlp/twitter-roberta-base-sentiment-latest).
- `vader_roberta_agreement_metrics.py` (Angelo) — VADER↔RoBERTa agreement, Cohen's κ, confusion matrix.
- `sample_400.py` (Angelo) — stratified 400-item annotation sample.
- `collect_helene_ext.py`, `collect_milton_ext.py` — Reddit window-extension collectors (2026-06-18).

## week4_bertopic/
- `BERTopic.ipynb` (José) — BERTopic per corpus on Colab.
- `label_topics.py`, `plot_topics.py`, `topic_distributions.py` (José) — labeling, figures, chi-square distributions.
- `build_master.py` (José) — assembles `master_vader_roberta_topics.csv` from the six files (derived snapshot; rebuild, don't hand-edit).

## week5_hypotheses/
- `h2_temporal.py`, `h5_subreddit.py` (José) — H2 temporal trajectory, H5 subreddit tiers.
- `hypothesis_tests.py` (Angelo) / `hypothesis_tests_jose.py` (José) — H1/H3/H4/H7.
  Two independent runs that cross-validate. They **agree on H1 VADER, H3, H4, H7**;
  they differ on the H1 **RoBERTa** Mann-Whitney because Angelo ranks by the discrete
  label and José by the continuous `pos − neg` score (open item: standardize on `pos − neg`).
  The unit test imports Angelo's `hypothesis_tests.py`.
- `evaluate_methods.py` (José) — VADER/RoBERTa vs the 400-item gold standard (joint work).
- `results_table.py`, `build_ground_truth.py`, `verify_data.py` (José) — results grid, gold-standard build, data-integrity checks.
- `tests/test_hypothesis_analysis.py` (Angelo) — unit tests for the H1 helpers.

## week6_figures/
- `plot_landfall_trajectories.py` (José) — per-hurricane landfall sentiment trajectories.
  Most other figures are generated inline by the week5 scripts (H2/H5) and week4 `plot_topics.py`.
