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
- `build_facebook_master.py` (José) — builds `facebook_master.csv` from the six raw
  Facebook workbooks in `data/facebook/raw_xlsx/`. Recovered in the Week 8 pass and
  repointed to repo-relative paths; verified to reproduce the file byte for byte.
- `use_arctic_shift.py` (Angelo) — Reddit collection via the Arctic Shift API (locked method).
- `collect_subreddit.py` (José) — per-subreddit post + comment-tree pull.
- `explore_queries.py` (José) — samples each (subreddit × window) query before
  committing to a full pull; also how the megathreads were spotted.

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
- `run_vader_facebook.py`, `run_vader_facebook_split.py` (José), `run_vader_reddit.py`
  (Angelo), `run_vader_whitehouse.py` — apply the shared VADER scorer per source.
  `run_vader_whitehouse.py` was **added in Week 8**: the file previously named
  `run_vader_wh.py` was a byte-identical copy of `run_vader_facebook.py`, so nothing
  in the repo actually produced the White House VADER outputs. The new script
  reproduces them exactly; the misnamed duplicate was removed.
- `three_way_comparison.py` (Angelo) — Facebook vs Reddit vs WH summary tables.
  Takes `--out` since Week 8; it used to hardcode its output path and filename.
- `pull_comments.py`, `pull_whitehouse.py`, `pull_org_mentions.py` (José) — Arctic
  Shift collectors for megathread comment trees, the White House account, and
  organisation mentions. Recovered in the Week 8 pass.

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
  they agree on **every statistic to ~1e-12** since the 2026-07-09 convention fix
  (both now rank by the continuous `roberta_pos − roberta_neg`, not the discrete label).
  The unit test imports Angelo's `hypothesis_tests.py`.
- `evaluate_methods.py` (José) — VADER/RoBERTa vs the 400-item gold standard (joint work).
- `results_table.py`, `build_ground_truth.py`, `verify_data.py` (José) — results grid, gold-standard build, data-integrity checks.
- `tests/test_hypothesis_analysis.py` (Angelo) — unit tests for the H1 helpers.

## week6_figures/
- `f1_dataset_overview.py` — stacked bars, corpus size by source × hurricane.
- `f3_three_way.py` — mean sentiment by source × hurricane with 95% CIs and H1 stars.
- `f4_sentiment_distribution.py` — 100% stacked negative/neutral/positive shares.
- `f6_agreement_heatmap.py` — VADER × RoBERTa 3×3 confusion heatmap.
- `f7_topic_distribution_by_source_type.py` — topic mix per source.
- `f8_topic_evolution.py` — topic mix over `days_from_landfall`.
- `f9_whitehouse_case_study.py` — the White House panel behind H7.
- `h7_per_hurricane.py` — splits the pooled H7 result per storm (it is ~90% Helene).
- `plot_landfall_trajectories.py` (José) — per-hurricane landfall sentiment trajectories.

F2 and F5 have no dedicated script: they are produced by `week5_hypotheses/h2_temporal.py`
and `h5_subreddit.py` respectively.

## week8_reproducibility/
- `rerun_pipeline.py` — runs every stage in dependency order and writes
  `docs/week8/rerun_log.md`. `--list` shows the stages, `--stages` runs a subset.
- `snapshot_outputs.py` — fingerprints every output (bytes, SHA-256, parsed row
  count) so two runs can be compared. `--compare before.csv after.csv`.

See `docs/week8/rerun_verification.md` for what the Week 8 re-run found.
