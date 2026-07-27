# Repository Verification and Final File Inventory

**Hurricane Sentiment Analysis — Summer 2026**
Jose Araya, Angelo Morelli

Repository: `drainr/hurricane_sentiment_analysis`

---

## Part 1 — Verification against every deliverable in the plan

Legend: **✅ present** · **📁 elsewhere** (exists, but not in the repository) · **❌ absent**

### Week 1 — Setup, Data Audit, Literature, Reddit Exploration

| Deliverable                                      | Status | Location / note                                                                                                                                                                                                                                 |
| ------------------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `facebook_master.csv` standardized and validated | ✅     | `data/facebook/facebook_master.csv` — 60,688 rows = 952 posts + 59,736 comments                                                                                                                                                                 |
| `facebook_data_audit.md`                         | 📁     | In the shared Google Drive (**Week1 Deliverables/`facebook_data_audit.md`**). **Not in the repo**                                                                                                                                               |
| GitHub repository with folder structure          | ✅     | Reorganized by week in Week 5; structure differs from the plan's original flat layout by agreement                                                                                                                                              |
| All dependencies installed and tested            | ✅     | `requirements.txt`, fully pinned                                                                                                                                                                                                                |
| Reddit Access Decision Document                  | 📁     | In the shared Google Drive (**Week1 Deliverables/"reddit access decision"**, Google Doc)**Not in the repo**                                                                                                                                     |
| Literature review draft (3 pages, 12+ papers)    | 📁     | In the shared Google Drive (**Week1 Deliverables/"final literature review"**, Google Doc; local PDF `final literature review.pdf`). **Not in the repo.** Note: covers **4 papers across 5 themes** (Neppalli, Vayansky, Alam, Hutto & Gilbert). |

### Week 2 — Reddit and White House Collection, Unified VADER

| Deliverable                                                 | Status        | Location / note                                                                                                                                                                                                                     |
| ----------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `reddit_clean.csv` collected and cleaned                    | ✅            | `data/reddit/combined/reddit_clean.csv`                                                                                                                                                                                             |
| `whitehouse_threads.csv`                                    | ✅            | Split into `whitehouse_threads_posts` / `_comments` (12 / 2,193)                                                                                                                                                                    |
| `reddit_collection_log.md` — counts per subreddit/hurricane | ✅ Renamed    | `docs/week1/subreddit_selection_and_counts.md` — subreddit selection, per-storm raw counts, and exact cleaned totals (122,026 comments / 3,418 posts / 125,444 combined). Content complete; only the filename differs from the plan |
| `facebook_master_vader.csv`                                 | ✅            | `data/facebook/facebook_master_vader.csv`                                                                                                                                                                                           |
| `master_vader.csv` merged master with VADER                 | ⚠️ Superseded | Deliberately not built. Advisor directed six separate files                                                                                                                                                                         |
| Three-way first-look comparison table                       | ✅            | `data/merged/vader_comparison_table_posts.csv` and `_comments.csv`                                                                                                                                                                  |

### Week 3 — RoBERTa Scoring and Inter-Method Agreement

| Deliverable                                                            | Status        | Location / note                                                                                                                                                              |
| ---------------------------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `master_vader_roberta.csv`                                             | ⚠️ Superseded | Per-source `*_vader_roberta.csv` files in `data/roberta/`, per the six-file decision                                                                                         |
| Agreement metrics: kappa, per-platform, per-hurricane, per-source_type | ⚠️ Partial    | `code/week3_roberta_agreement/vader_roberta_agreement_metrics.py` exists; `agreement_metrics.txt` is **not committed** — it only lives in the Colab run                      |
| Confusion matrix                                                       | ✅            | `figures/f6_vader_roberta_agreement.{png,pdf}` — 54.7% overall agreement                                                                                                     |
| Disagreement analysis document (50 cases, categorized)                 | 📁            | In the shared Google Drive (**Week3 Deliverables/"Disagreement analysis"**, Google Doc). Raw cases also in `data/roberta/disagreement_examples_100.csv`. **Not in the repo** |
| `roberta_processing_log.md`                                            | ✅            | `docs/week3/roberta_processing_log.md`                                                                                                                                       |
| Annotation protocol document                                           | 📁            | In the shared Google Drive (**Summer2026 root/"Annotation Protocol — Hurricane Sentiment Group"**, Google Doc). **Not in the repo**                                          |

### Week 4 — BERTopic Analysis

| Deliverable                                                                | Status                | Location / note                                                                                                                                                                                      |
| -------------------------------------------------------------------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BERTopic models per corpus, with topic assignments, top-words, sizes       | 📁 Off-repo by design | Five saved models live in the shared Google Drive (**Week4 Deliverables/`models/`**); repo `models/` is gitignored (size). Verified against the Week 4 run log in `docs/week8/rerun_verification.md` |
| Full combined model built from the master                                  | ❌                    | Not run — heavy Colab job; per-corpus models feed the codebook. Recommended to skip unless requested                                                                                                 |
| Six files with topic-assignment column written back                        | ✅                    | `data/processed/*_labeled.csv`                                                                                                                                                                       |
| Shared topic codebook, reconciled labels and categories                    | ✅                    | `docs/week4/Topic Codebook.md` — marked final                                                                                                                                                        |
| `master_vader_roberta_topics.csv` with provenance, passing both guardrails | ✅                    | `data/merged/` — 187,359 rows, 0 duplicate (id, source). **Plan's 186,722 guardrail is stale** (predates the window extensions; delta +637)                                                          |
| Topic distributions by source_type, hurricane, subreddit                   | ✅                    | `data/merged/topic_dist_by_*.csv`                                                                                                                                                                    |
| Chi-square results                                                         | ✅                    | `data/merged/chi_square_results.md`                                                                                                                                                                  |
| 4–6 topic figures                                                          | ✅                    | `figures/f7_topic_distribution_by_source_type`, `f8_topic_evolution`, `figures/topics/`                                                                                                              |
| `ground_truth_400.csv` with both annotators + consensus                    | ✅                    | `data/merged/` — **verified 400/400 consensus filled, zero unresolved**                                                                                                                              |
| Inter-annotator kappa report with the <0.5 flag rule                       | ✅                    | `docs/week4/interannotator_kappa.md` — κ 0.822 sentiment, 0.884 gratitude                                                                                                                            |
| Topic overlap review + min_topic_size record (v4 addition)                 | ✅                    | `docs/week4/topic_review.md`, `docs/week4/bertopic_run_log.md`                                                                                                                                       |

### Week 5 — Hypothesis Testing (H1–H7)

| Deliverable                                                          | Status | Location / note                                                                                       |
| -------------------------------------------------------------------- | ------ | ----------------------------------------------------------------------------------------------------- |
| Complete statistical results table: 7 hypotheses × 2 methods         | ✅     | `data/merged/hypothesis_tests_all7_jose.csv` (93 rows), `docs/week5/statistical_results_table.md`     |
| Temporal sentiment curves figure (key paper figure)                  | ✅     | `figures/h2_temporal_curves.{png,pdf}` + RoBERTa variant                                              |
| `statistical_results_summary.md`                                     | ✅     | `docs/week5/` — hand-written, no generator                                                            |
| Method validation report + gratitude inflation estimate              | ✅     | `docs/week5/method_validation_report.md`                                                              |
| Data validity: no White House duplicates in Reddit across all stages | ✅     | Verified — 0 White House IDs in processed Reddit files; all three stages reconcile at 3,413 / 121,053 |
| Organize GitHub (code by week, data storage)                         | ✅     | `code/week1…week8` + `code/common`; docs by week                                                      |

### Week 6 — Publication-Quality Figures and Results Documentation

| Deliverable                                                        | Status | Location / note                                                                                                                                                |
| ------------------------------------------------------------------ | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 8–9 publication-quality figures with captions                      | ✅     | 42 files in `figures/` (PNG + PDF pairs), 300 dpi, project color convention                                                                                    |
| `results_documentation.md` incl. White House case study section    | ✅     | `docs/week6/hypothesis_results_analysis.md` serves this role (renamed from the plan's `results_documentation.md`), plus `docs/week6/h7_pooled_helene_check.md` |
| Master results summary table (7 × 2), in detail                    | ✅     | `docs/week5/statistical_results_table.md`                                                                                                                      |
| Written sign-off on White House day-0 count and 973-row root cause | ✅     | Both independently verified; evidence package retained (gitignored, sent by email)                                                                             |
| Methodology + results sections of paper draft 1                    | ✅     | In the shared Drive document (not a repo artifact)                                                                                                             |

### Week 7 — Paper Drafts

| Deliverable                        | Status     | Location / note                                                                                                                                                                                                                                          |
| ---------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Detailed methodology section draft | ✅         | Drive document;maintained                                                                                                                                                                                                                                |
| 5-page literature review           | ⚠️ Partial | In the shared Google Drive (**Week1 Deliverables/"final literature review"**, Google Doc; local PDF `final literature review.pdf`). **Not in the repo.** Note: 4 papers / 5 themes — below the plan's "6 themes," so may need expansion before the paper |
| Results narrative draft (H1–H7)    | ✅         | Drive document — H1–H7 plus synthesis, Figures 1–12                                                                                                                                                                                                      |
| Complete reference list            | ❌         | **Not done.** No assembled bibliography                                                                                                                                                                                                                  |

### Week 8 — Reproducibility, Archive, Advisor Handoff

| Deliverable                                  | Status | Location / note                                                                                                                                                                                            |
| -------------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Full pipeline re-run verified from scratch   | ✅     | `docs/week8/rerun_verification.md`, `rerun_log.md` — 32/32 stages, 132 outputs byte-identical; RoBERTa bit-identical on Colab; BERTopic verified against saved models; collection re-run with 0.004% drift |
| All code documented with README              | ✅     | 50/50 modules, 184/184 functions; `README.md` + `code/README.md`                                                                                                                                           |
| `requirements.txt` with pinned versions      | ✅     | Fully pinned including all six GPU packages                                                                                                                                                                |
| `decision_log.md`                            | ✅     | **`docs/decision_log.md`**                                                                                                                                                                                 |
| `advisor_summary.md` (3–4 pages)             | ✅     | **`docs/advisor_summary.md`**                                                                                                                                                                              |
| Complete verified archive and file inventory | ✅     | **This document**                                                                                                                                                                                          |

---

## Part 2 — Verification results

### Row-count reconciliation — all pass

Recomputed with pandas (not `wc -l`, which inflates counts because comment text contains embedded newlines):

| File                                | Rows        | Expected    |     |
| ----------------------------------- | ----------- | ----------- | --- |
| facebook_posts                      | 952         | 952         | ✅  |
| facebook_comments                   | 59,736      | 59,736      | ✅  |
| reddit_relevant_posts               | 3,413       | 3,413       | ✅  |
| reddit_relevant_comments            | 121,053     | 121,053     | ✅  |
| whitehouse_threads_posts            | 12          | 12          | ✅  |
| whitehouse_threads_comments         | 2,193       | 2,193       | ✅  |
| **Sum of six**                      | **187,359** | **187,359** | ✅  |
| **master_vader_roberta_topics.csv** | **187,359** | **187,359** | ✅  |

`ground_truth_400.csv`: 400 rows, `label_consensus` and `gratitude_consensus` both **400/400 filled** — the gold standard is intact and carries no unresolved items.

### Gaps found

**Missing outright (1):**

1. **Assembled reference list** — not done. No bibliography section.

**Named differently than the plan (2):** `results_documentation.md` → `hypothesis_results_analysis.md`; `reddit_collection_log.md` → `subreddit_selection_and_counts.md`. Content is present; only the filenames differ.

**Superseded by advisor decision (2):** `master_vader.csv` and `master_vader_roberta.csv` were never built, because the six-separate-files decision replaced them. Not gaps.

**Not committed (1):** `agreement_metrics.txt` only lives in the Colab run rather than the repository; regenerate from the corrected files and commit it.

**Not run (1):** the full combined BERTopic model from the master. Recommended to leave undone unless requested — it is a heavy job and the per-corpus models already feed the codebook.

---

## Part 3 — File inventory

### Top level

| Path               | Contents                                                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `README.md`        | Master reproduction guide — 19-stage ordered table with commands, inputs, outputs, expected row counts, and the Colab boundary |
| `requirements.txt` | Fully pinned, including the six GPU packages captured from Colab                                                               |
| `.gitignore`       | Excludes `backups/`, `models/`, `__pycache__/`, and the two Week 8 evidence directories                                        |

### `code/` — 55 tracked files, 52 Python modules + 2 notebooks

| Directory                  | Files                | Purpose                                                                                                                                                                               |
| -------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `common/`                  | `vader_sentiment.py` | Shared scorer — standalone `vaderSentiment`, ±0.05 thresholds. Single source of truth for all VADER scoring                                                                           |
| `week1_setup_exploration/` | 4                    | `build_facebook_master.py` (rebuilds Facebook from raw xlsx), `collect_subreddit.py`, `use_arctic_shift.py`, `explore_queries.py`                                                     |
| `week2_collection_vader/`  | 16                   | Merge, relevance, normalization, White House cleaning, splits, and the four VADER runners. Both authors' variants retained and suffixed; canonical versions noted in `code/README.md` |
| `week3_roberta_agreement/` | 4 + `RoBERTa.ipynb`  | Window-extension collectors, 400-item sampler, agreement metrics, GPU scoring notebook                                                                                                |
| `week4_bertopic/`          | 4 + `BERTopic.ipynb` | `build_master.py` (with both guardrails), `label_topics.py`, `topic_distributions.py`, `plot_topics.py`                                                                               |
| `week5_hypotheses/`        | 10 + `tests/`        | All seven hypothesis tests, ground-truth builder, method evaluation, results tables, `verify_data.py`                                                                                 |
| `week6_figures/`           | 9                    | Figure generators F1–F9 plus `h7_per_hurricane.py`                                                                                                                                    |
| `week8_reproducibility/`   | 4                    | `rerun_pipeline.py`, `snapshot_outputs.py`, `recollect.py`, `collection_drift_report.py`                                                                                              |

### `data/` — 537 tracked files, 758 MB

| Directory                         | Contents                                                                                                                                                  |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `facebook/`                       | `facebook_master.csv` (60,688), VADER-scored copy, `raw_xlsx/` (6 source workbooks), `student_originals/`                                                 |
| `reddit/`                         | Per-storm collections (`debby/`, `helene/`, `milton/`, `helene_ext/`, `milton_ext/`), `whitehouse/`, and `combined/` (raw, clean, flagged, relevant)      |
| `vader/`                          | VADER-scored per-source files                                                                                                                             |
| `roberta/`                        | VADER + RoBERTa scored per-source files; `disagreement_examples_100.csv`                                                                                  |
| `processed/`                      | **The six canonical labeled files** — scores plus topic assignments. This is the source of truth                                                          |
| `merged/`                         | Master file, gold standard, hypothesis results (both authors), topic distributions, chi-square results, three-way comparison tables, manual label samples |
| `reddit_rerun/`, `roberta_rerun/` | Week 8 reproducibility evidence — **gitignored by design**; the write-ups in `docs/week8/` are the kept record                                            |

Largest tracked artifacts: `master_vader_roberta_topics.csv` (72 MB), `reddit_comments_all.csv` (65 MB), `reddit_clean_flagged.csv` (49 MB). The master exceeds GitHub's 50 MB soft warning but pushes successfully.

### `docs/` — 31 tracked files

| Directory | Key contents                                                                                                                                          |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| root      | `README.md` (by-week index), **`decision_log.md`**, **`advisor_summary.md`**                                                                          |
| `week1/`  | `subreddit_selection_and_counts.md`, `facebook_build_log.txt`                                                                                         |
| `week2/`  | `vader_reproduction_50row.csv` — _no markdown; the thinnest folder in the repo_                                                                       |
| `week3/`  | `roberta_processing_log.md`                                                                                                                           |
| `week4/`  | `Topic Codebook.md`, `bertopic_run_log.md`, `interannotator_kappa.md`, `topic_review.md`                                                              |
| `week5/`  | Hypothesis results, H2/H5 results, method validation, statistical summary and table, data verification                                                |
| `week6/`  | Per-figure result docs (F1, F3, F4, F6, F7, F8, F9), `figures_status.md`, `hypothesis_results_analysis.md`, `h7_pooled_helene_check.md`               |
| `week8/`  | `rerun_verification.md`, `rerun_log.md`, `collection_drift_report.md`, `colab_reproducibility_run.md`, `output_manifest.csv`, **`file_inventory.md`** |

### `figures/` — 42 files, 300 dpi PNG + vector PDF

F1 dataset overview · F3 three-way comparison (VADER + RoBERTa) · F4 sentiment distribution (both scorers) · F6 agreement heatmap · F7 topic distribution by source · F8 topic evolution · F9 White House case study · H2 temporal curves (both scorers) · H5 subreddit box plots · plus `topics/` and `landfall_trajectories/` subdirectories.

Color convention holds throughout: Facebook blue, Reddit community orange, White House green.

---
