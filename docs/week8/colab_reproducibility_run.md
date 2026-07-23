# Week 8 — Colab reproducibility run

Two stages need a GPU and cannot run in the local lane: **RoBERTa scoring**
(`code/week3_roberta_agreement/RoBERTa.ipynb`) and **BERTopic**
(`code/week4_bertopic/BERTopic.ipynb`). This documents how both were verified on
Colab, in three jobs. All three are complete; the results feed
`docs/week8/rerun_verification.md` and the pinned `requirements.txt`.

---

## Job 1 — Capture the six missing version pins (both notebooks)

`requirements.txt` pins everything that runs locally, but the six GPU packages
were unpinned because both notebooks installed them with a bare `!pip install`,
so a future Colab run would silently resolve different versions. To close that,
the exact versions the original analysis ran on were captured from the live Colab
runtime and written into `requirements.txt`.

Each notebook's setup cells were run as normal, then this cell was added and run:

```python
import sys, platform
print("python  ", sys.version.split()[0], "|", platform.platform())

for mod in ["transformers", "torch", "bertopic", "sentence_transformers",
            "umap", "hdbscan", "numpy", "pandas", "sklearn"]:
    try:
        m = __import__(mod)
        print(f"{mod:22} {getattr(m, '__version__', '?')}")
    except ImportError:
        print(f"{mod:22} (not installed in this notebook)")

try:
    import torch
    print("cuda    ", torch.version.cuda,
          "| gpu", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")
except Exception as e:
    print("cuda     n/a:", e)
```

`RoBERTa.ipynb` reports `transformers` and `torch`; `BERTopic.ipynb` reports
`bertopic`, `sentence_transformers`, `umap`, `hdbscan`.

**Captured (2026-07-22, Colab T4, Python 3.12.13, CUDA 12.8):** transformers
5.13.1, torch 2.11.0+cu128, bertopic 0.17.4, sentence-transformers 5.5.1,
umap-learn 0.5.12, hdbscan 0.8.44. These six were written into `requirements.txt`
(the `bertopic`/`sentence-transformers` pins are the original-run versions that
produced the saved models — a fresh install today resolves sentence-transformers
5.6.0, which is why the models are *verified*, not regenerated; see Job 3).

---

## Job 2 — Re-run RoBERTa and confirm it reproduces

RoBERTa inference is deterministic: the notebook runs under `torch.no_grad()`
with no sampling anywhere, so re-scoring the same text with the same checkpoint
must return the same probabilities. That makes it worth actually re-running — and
it does reproduce, so the heaviest stage in the project is verified rather than
assumed.

The re-run wrote to new files rather than over the existing ones. In the cell that
saves each output, the filename was given a `_rerun` suffix:

```python
OUT = OUT.replace("_vader_roberta.csv", "_vader_roberta_rerun.csv")
```

All six files were re-scored (Facebook posts/comments, Reddit posts/comments,
White House posts/comments) and the six `*_rerun.csv` downloaded into
`data/roberta_rerun/` locally, then compared against the committed scores from the
repo root:

```bash
python3 - <<'EOF'
import pandas as pd, pathlib
REPO = pathlib.Path(".")
pairs = [
    ("facebook_posts", 952), ("facebook_comments", 59736),
    ("reddit_relevant_posts", 3413), ("reddit_relevant_comments", 121053),
    ("whitehouse_threads_posts", 12), ("whitehouse_threads_comments", 2193),
]
cols = ["roberta_neg", "roberta_neu", "roberta_pos", "roberta_label"]
allok = True
for stem, expected in pairs:
    a = pd.read_csv(REPO/"data/roberta"/f"{stem}_vader_roberta.csv", low_memory=False)
    b = pd.read_csv(REPO/"data/roberta_rerun"/f"{stem}_vader_roberta_rerun.csv", low_memory=False)
    a, b = a.sort_values("id").reset_index(drop=True), b.sort_values("id").reset_index(drop=True)
    ok = len(a) == len(b) == expected and (a["id"] == b["id"]).all()
    for c in cols:
        same = a[c].equals(b[c]) if c == "roberta_label" else \
               (a[c] - b[c]).abs().max() < 1e-6
        ok &= bool(same)
        print(f"  {stem:30} {c:14} {'match' if same else 'DIFFERS'}")
    allok &= ok
print("\nRoBERTa re-run reproduces exactly." if allok else "\nDifferences found — investigate.")
EOF
```

Probabilities are compared to 1e-6 rather than exactly, because GPU floating-point
reduction order can vary between runs; a difference larger than that, or any label
flip, would be a real finding.

**Result (2026-07-22):** every probability matched bit-identically (max |Δ| =
0.00e+00) with zero label flips across all 124,466 rows — reproduces exactly. The
result is recorded in `docs/week8/rerun_verification.md`; `data/roberta_rerun/`
was evidence only and is not kept in the repo.

---

## Job 3 — Verify BERTopic against the saved models (no re-run)

BERTopic was **not** re-fit. `RANDOM_SEED` is wired into `UMAP(random_state=...)`,
so a re-run on identical library versions should be stable, but UMAP and HDBSCAN
do not guarantee identical output across versions, and Colab now resolves
sentence-transformers 5.6.0 versus the 5.5.1 the models were built on. A shifted
topic assignment would produce different topics than the paper uses and force
re-labeling and re-signing the codebook in the final week. The saved June models
are the artifact of record, so the check verifies them rather than regenerating
them.

The verification reads each saved model's serialized topic table directly — the
`topic_sizes` map inside the model's `topics.json` — and confirms the topic count
and outlier rate still match the Week-4 run log. This needs only a JSON read (no
`bertopic`/`torch` import, no re-embedding), which also sidesteps a torch import
error from the version drift on the current runtime:

```python
import json, os

MODELS = "/content/drive/MyDrive/SentimentofHurricanes/Summer2026/Week4 Deliverables/models/bertopic"

EXPECTED = {   # from docs/week4/bertopic_run_log.md + the saved model configs
    "facebook_posts":    dict(min_topic_size=10,  topics=11),
    "facebook_comments": dict(min_topic_size=150, topics=44, outliers=0.442),
    "reddit_posts":      dict(min_topic_size=30,  topics=14, outliers=0.341),
    "reddit_comments":   dict(min_topic_size=250, outliers=0.493),
    "whitehouse":        dict(min_topic_size=10,  topics=5),
}

for name, exp in EXPECTED.items():
    p = os.path.join(MODELS, name)
    if not os.path.isdir(p):
        print(f"{name:20} DIR MISSING"); continue
    js = [f for f in os.listdir(p) if f.startswith("topics_") and f.endswith(".json")]
    if not js:
        print(f"{name:20} no topics json -> {os.listdir(p)}"); continue
    d = json.load(open(os.path.join(p, js[0])))
    sizes = {int(k): v for k, v in d["topic_sizes"].items()}
    total = sum(sizes.values())
    n_topics = sum(1 for k in sizes if k >= 0)
    outliers = sizes.get(-1, 0) / total if total else float("nan")
    print(f"{name:20} topics={n_topics:3}  outliers={outliers:.3f}  (modeled n={total})   expected={exp}")
```

**Result (2026-07-23):** all five models match the run log — FB posts 11 topics /
0.002 outliers (n=944), FB comments 44 / 0.442 (n=49,939), reddit posts 14 / 0.341
(n=3,293), reddit comments 46 / 0.493 (n=114,248), WH 5 / 0.002 (n=2,086). Each
modeled `n` reconciles to its file minus the `<5`-word exclusions. Recorded in
`docs/week8/rerun_verification.md`.

Two things to know when reading the result:

- **The White House model is meant to look degenerate.** ~95% of its comments sit
  in one FEMA/government/political topic, and no `min_topic_size` splits it. That
  is the data, not a tuning bug, and it is reported as a finding. H7 rests on
  sentiment polarization, which is measured separately.
- **The Reddit outlier rates have a known 0.1 pp discrepancy.** The saved models
  give 34.1% and 49.3%; the methodology draft says 34.2% and 49.4%. The models are
  right — worth correcting in the draft.

The topic JSON files were also renamed by source in Drive (Tania v4 plan item 4):
`topics_facebook_posts.json`, `topics_facebook_comments.json`,
`topics_reddit_posts.json`, `topics_reddit_comments.json`, `topics_wh.json`. Note
that these are each model's internal `topics.json`; a copy under the original name
`topics.json` must be kept inside every model folder for `BERTopic.load()` to work.

---

## Summary

1. Version pins captured (Job 1) → six GPU packages pinned in `requirements.txt`.
2. RoBERTa re-run (Job 2) → bit-identical, recorded in `rerun_verification.md`.
3. BERTopic verified against saved models (Job 3) → all five match the run log.
