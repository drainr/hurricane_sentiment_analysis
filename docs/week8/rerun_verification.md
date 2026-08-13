# Week 8 — Pipeline re-run verification

**Result: the pipeline reproduces. 32/32 stages exit clean and all 132 tracked
outputs are byte-identical across consecutive runs** (2,107,663 rows over 63 CSVs).

Reproduce it with:

```bash
python3 code/week8_reproducibility/snapshot_outputs.py --out before.csv
python3 code/week8_reproducibility/rerun_pipeline.py
python3 code/week8_reproducibility/snapshot_outputs.py --out after.csv
python3 code/week8_reproducibility/snapshot_outputs.py --compare before.csv after.csv
```

Local lane runtime is about 3 minutes.

## What "from scratch" means here

The frozen inputs are the **raw collected files**: the six Facebook xlsx now in
`data/facebook/raw_xlsx/` and the Reddit / White House pulls in `data/reddit/`.
Everything downstream is re-executed.

Collection is deliberately not re-run. The collectors query the Arctic Shift
archive, whose contents have changed since June — posts deleted, edited, or
removed by moderators — so a fresh pull cannot byte-match the corpus the
analysis was built on. Re-collecting would produce a different dataset, which
tests nothing about whether this analysis is reproducible. The collectors are
kept runnable and documented instead. _(Boundary confirmed with the advisor —
see the Week 8 email.)_

Two stages run on Colab GPU and sit outside the local lane: RoBERTa scoring
(week 3) and BERTopic (week 4). See `docs/week8/colab_reproducibility_run.md`.

## Bugs found and fixed

The re-run was worth doing: eight real defects surfaced, three of which would
have affected results.

### 1. The gold standard was being silently destroyed — most serious

`build_ground_truth.py` fills `label_consensus` only where the two annotators
already agreed. The 38 sentiment and 4 gratitude disagreements were adjudicated
by hand by José and Angelo afterwards. Re-running the script blanked all 42,
dropping the gold standard from 400 adjudicated items to 362 — and every
accuracy figure in `method_validation_report.md` is computed on it.

`ground_truth_400.csv` is a curated artifact, not a reproducible output. The
script now refuses to overwrite an already-adjudicated file unless
`REBUILD_GROUND_TRUTH=1` is set, and it is excluded from `rerun_pipeline.py`.
Once the file was restored, `evaluate_methods.py` reproduced every number
exactly (VADER 0.487 / RoBERTa 0.728, macro-F1 0.472 / 0.692).

### 2. H3 bootstrap confidence intervals were not reproducible

`hypothesis_tests.py` seeded its 10,000-resample bootstrap with
`100 + hash(hurricane) % 100`. Python randomises string hashing per process, so
the seed differed on every run and the 95% CI bounds moved in the third decimal
each time (Helene VADER `[0.106, 0.123]` vs `[0.106, 0.122]`).

Replaced with fixed per-hurricane seeds (`H3_BOOTSTRAP_SEEDS`). Gaps and
p-values were never affected — only the CI bounds, by at most 0.001.

### 3. No script produced the White House VADER scores

`run_vader_wh.py` was a byte-identical copy of `run_vader_facebook.py`,
committed under the wrong name in `dfa5587`. It never touched White House data,
so nothing in the repo generated `data/vader/whitehouse_threads_*_vader.csv` —
a hole in the middle of the pipeline that H7 rests on.

Added `run_vader_whitehouse.py`, modelled on `run_vader_reddit.py` and using the
same shared scorer. It reproduces both canonical outputs byte for byte (12
posts, 2,193 comments). The misnamed duplicate was removed.

### 4. `clean_whitehouse_data.py` consumed its own output

Its input glob was `*_comments.csv` / `*_posts.csv`, which on a second run also
matched `whitehouse_threads_comments.csv` and `whitehouse_threads_posts.csv` —
the files it writes. Those carry the unified schema, not the raw one, so the
re-run died on `KeyError: 'author'`. The script was only ever idempotent against
a clean directory. Now it names its two source files explicitly.

### 5. Three scripts had broken or stale paths

- `clean_whitehouse_data.py` used a bare relative path (`../../data/...`), so it
  only ran from its own folder — the one script breaking the repo's documented
  "run from anywhere" convention.
- `plot_landfall_trajectories.py` resolved its repo root one level short, making
  every path `code/data/...`; the script could not run at all. It also still
  referenced the old Reddit filenames, which no longer exist.
- `three_way_comparison.py` hardcoded its output next to the script and always
  named it `_posts`, so regenerating the comments table meant editing the source
  between runs. It now takes `--out` and defaults into `data/merged/`.

### 6. The three-way comparison tables were stale

Regenerating them changed Reddit Milton posts 2,289 → 2,284 and comments
80,312 → 79,339. That is exactly the 5 White House posts and 973 White House
comments removed in the 2026-06-26 de-duplication: the committed tables predated
that fix. The regenerated tables are correct and now reconcile with every other
file at 3,413 / 121,053.

### 7. The master file was the only CSV written with CRLF

`build_master.py` uses `csv.DictWriter`, which defaults to `\r\n` on every
platform, while every other output goes through pandas `to_csv` (LF). Content
was identical but the master hashed differently on each rebuild, which would
have masked real diffs. Now written with `lineterminator="\n"`.

## Known benign divergence

`reddit_clean_flagged.csv` and `reddit_relevant.csv` as committed carry CRLF line
terminators — they were generated on a Windows machine. Our re-run writes LF, so
they differ by exactly one byte per row (185,669 and 124,467 bytes). Verified
content-identical: same row count, same ids in the same order, and zero differing
cells across every column. The re-run's LF versions are what the repo now holds.

## Reproducibility gaps closed

Five scripts existed only as `.pyc` and were listed in `code/README.md` as
"recover from Drive". All five were recovered and are now in the repo with
repo-relative paths:

| script                     | now at                          |
| -------------------------- | ------------------------------- |
| `build_facebook_master.py` | `code/week1_setup_exploration/` |
| `explore_queries.py`       | `code/week1_setup_exploration/` |
| `pull_comments.py`         | `code/week2_collection_vader/`  |
| `pull_whitehouse.py`       | `code/week2_collection_vader/`  |
| `pull_org_mentions.py`     | `code/week2_collection_vader/`  |

The Facebook standardizer had hardcoded absolute paths into a scratch folder and
an Obsidian vault. Repointed to the repo root and confirmed: it rebuilds
`facebook_master.csv` byte for byte (60,688 rows = 952 posts + 59,736 comments),
including the logged Milton `Post_ID=9` year-typo fix. Its six source xlsx are
now committed under `data/facebook/raw_xlsx/`, so the Facebook stage is
reproducible from raw for the first time.

## Verified counts

Every canonical count in the decision log holds after a full re-run:

| file                          | rows    |
| ----------------------------- | ------- |
| `facebook_posts`              | 952     |
| `facebook_comments`           | 59,736  |
| `reddit_relevant_posts`       | 3,413   |
| `reddit_relevant_comments`    | 121,053 |
| `whitehouse_threads_posts`    | 12      |
| `whitehouse_threads_comments` | 2,193   |
| `master_vader_roberta_topics` | 187,359 |

`verify_data.py` reports **ALL CHECKS PASSED**; `pytest` passes 2/2.

## RoBERTa GPU re-run (Colab) — verified 2026-07-22

The one heavy stage the local lane cannot run — RoBERTa scoring on the Colab T4
GPU — was re-executed and compared against the committed scores. The re-run read
the **clean** reddit VADER inputs (3,413 / 121,053, freshly re-uploaded to Drive
to overwrite any stale copy carrying the June White House leak), wrote to
separate `*_roberta_rerun.csv` files, and was diffed row-by-row on `id`.

| file                       | rows    | max \|Δ prob\| | label flips | verdict    |
| -------------------------- | ------- | -------------- | ----------- | ---------- |
| `reddit_relevant_posts`    | 3,413   | 0.00e+00       | 0           | reproduces |
| `reddit_relevant_comments` | 121,053 | 0.00e+00       | 0           | reproduces |

Every `roberta_neg/neu/pos` probability matched **bit-identically** (0.00e+00,
well inside the 1e-6 GPU-float tolerance) with zero `roberta_label` flips across
all 124,466 rows. RoBERTa inference runs under `torch.no_grad()` with no
sampling, so this confirms empirically what the design implies: the scoring stage
is deterministic and reproducible. Re-run driver + comparison in the Week 8
Colab lane (`docs/week8/colab_reproducibility_run.md`, Job 2); the `_rerun` files
are evidence only and are not kept in the repo.

## BERTopic (Colab) — verified against saved models 2026-07-23

BERTopic is **not** re-fit. UMAP + HDBSCAN are not guaranteed identical across
library versions, and the saved June models are the artifact the paper's topics
were drawn from — re-fitting on a drifted `sentence-transformers` (Colab now
resolves 5.6.0; the original run used 5.5.1) would produce *different* topics than
the analysis uses. So the reproducibility check loads each saved model's
serialized topic table (`topic_sizes` in its `topics.json`) and confirms the topic
count and outlier rate still match the Week-4 run log. No embedding, no torch, no
re-fit — a plain JSON read of the five saved model folders in Drive
(`Week4 Deliverables/models/bertopic/`).

| model | min_topic_size | topics | outlier rate | modeled n | verdict |
|---|---|---|---|---|---|
| `facebook_posts`    | 10  | 11 | 0.002 | 944     | matches run log |
| `facebook_comments` | 150 | 44 | 0.442 | 49,939  | matches run log |
| `reddit_posts`      | 30  | 14 | 0.341 | 3,293   | matches run log |
| `reddit_comments`   | 250 | 46 | 0.493 | 114,248 | matches run log |
| `whitehouse`        | 10  | 5  | 0.002 | 2,086   | matches run log |

Every modeled `n` reconciles to the file minus its `<5`-word exclusions (FB posts
952−8, reddit comments 122,026−7,778, etc.). The White House model stays
degenerate by design — 5 topics with ~95% of comments in one FEMA/political
cluster (low outliers, one dominant topic), the documented WH homogeneity finding.

Models were saved under bertopic 0.17.4 / sentence-transformers 5.5.1 (June run).
This closes the BERTopic half of the Week-8 pipeline verification; the topic JSONs
were also renamed by source in Drive (Tania v4 item 4).
