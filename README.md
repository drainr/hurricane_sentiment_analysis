# Hurricane Sentiment Analysis

Cross-platform NLP study of public sentiment during three 2024 Atlantic hurricanes
(Debby, Helene, Milton), comparing Facebook (Denis Phillips), organic Reddit
communities, and White House Reddit posts. VADER + RoBERTa sentiment, BERTopic
topics, seven hypotheses (H1–H7). Target: FLAIRS-40 (2027).

Advisor: Tania Roy. Two interns, 8-week summer project.

## Repository layout

Code is organized **by project week** (see the research plan). Data, docs, and
figures stay grouped by kind and are indexed per week below.

```
code/
  common/                 shared library imported across weeks (VADER scorer)
  week1_setup_exploration/  Reddit access testing + collection setup
  week2_collection_vader/   Reddit/WH collection, cleaning, merge, unified VADER
  week3_roberta_agreement/  RoBERTa scoring, VADER↔RoBERTa agreement, 400-item sample
  week4_bertopic/           BERTopic on each corpus, labels, master build
  week5_hypotheses/         H1–H7 tests, method validation, data verification
  week6_figures/            publication figures
data/                     source CSVs (kept in git) — see data/README.md
docs/                     result write-ups, logs
figures/                  exported PNG + PDF (300 dpi)
requirements.txt          pinned dependencies (Python 3.12)
```

See **[code/README.md](code/README.md)** for the file-by-file breakdown of each
week (including which of the two authors' duplicate scripts is canonical) and
**[data/README.md](data/README.md)** for the data manifest.

## Week index

| Week | Focus                                        | Code                            | Key outputs                                                                           |
| ---- | -------------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------- |
| 1    | Setup, data audit, Reddit exploration        | `code/week1_setup_exploration/` | Reddit access decision, `facebook_master.csv`                                         |
| 2    | Reddit + WH collection, unified VADER, merge | `code/week2_collection_vader/`  | `reddit_relevant*`, `whitehouse_threads*`, `*_vader.csv`, three-way tables            |
| 3    | RoBERTa scoring + inter-method agreement     | `code/week3_roberta_agreement/` | `*_vader_roberta.csv`, `docs/interannotator_kappa.md`, 400-item sample                |
| 4    | BERTopic topic modeling                      | `code/week4_bertopic/`          | topic-labeled files, `docs/Topic Codebook.md`, master file                            |
| 5    | Hypothesis testing (H1–H7)                   | `code/week5_hypotheses/`        | `docs/hypothesis_tests_results.md`, `docs/method_validation_report.md`, H2/H5 figures |
| 6    | Publication figures + results docs           | `code/week6_figures/`           | `figures/*`, results documentation                                                    |
| 7    | Paper drafts                                 | —                               | (writing)                                                                             |
| 8    | Reproducibility, archive, handoff            | —                               | full re-run, README, `requirements.txt`, `docs/decision_log.md`                       |

## Running

```bash
pip install -r requirements.txt          # Python 3.12
# scripts anchor paths to the repo root, so run them from anywhere, e.g.:
python3 "code/week5_hypotheses/h2_temporal.py"
python3 -m pytest code/week5_hypotheses/tests/
```

RoBERTa (`week3`) and BERTopic (`week4`) run as notebooks on Google Colab's GPU
tier; the scored CSVs are downloaded back into `data/`.

## Conventions

- Colors: Facebook = blue, Reddit community = orange, White House = green.
- `days_from_landfall = 0` on landfall day (Debby Aug 5, Helene Sep 26, Milton Oct 9).
- Sources kept as six separate files (facebook/reddit/whitehouse × posts/comments);
  the master file is a derived snapshot, rebuilt not hand-edited.
