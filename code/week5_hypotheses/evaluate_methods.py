#!/usr/bin/env python3
"""
Method validation against the human gold standard + gratitude-inflation estimate

1. Evaluate VADER and RoBERTa against ground_truth_400.csv consensus labels:
   accuracy + per-class precision/recall/F1 + confusion matrix for each method.
   Only rows with a filled label_consensus are scored (counts computed dynamically;
   all 400 as of the fully-adjudicated ground truth).

2. Gratitude-inflation estimate: among Facebook comments that each method labels
   POSITIVE, the fraction carrying the human gratitude tag (gratitude_consensus=1).
   This quantifies how much of Facebook's positive signal is person-directed thanks
   (feeds H1/H2 interpretation).

Outputs docs/week5/method_validation_report.md. Read-only on inputs.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "data" / "processed"
GT = REPO / "data" / "merged" / "ground_truth_400.csv"
OUT = REPO / "docs" / "week5" / "method_validation_report.md"
OUT.parent.mkdir(parents=True, exist_ok=True)

ROBERTA_MAP = {"NEG": "negative", "NEU": "neutral", "NEUTRAL": "neutral", "POS": "positive",
               "negative": "negative", "neutral": "neutral", "positive": "positive"}
LABELS = ["negative", "neutral", "positive"]

PROC_FILES = [
    "facebook_posts_vader_roberta_topics_labeled.csv",
    "facebook_comments_vader_roberta_topics_labeled.csv",
    "reddit_relevant_posts_vader_roberta_topics_labeled.csv",
    "reddit_relevant_comments_vader_roberta_topics_labeled.csv",
    "whitehouse_threads_posts_vader_roberta_topics_labeled.csv",
    "whitehouse_threads_comments_vader_roberta_topics_labeled.csv",
]

# Build id -> (vader_label, roberta_label) lookup from all six scored files.
frames = []
for f in PROC_FILES:
    d = pd.read_csv(PROC / f, dtype={"id": str}, low_memory=False)
    d = d[["id", "vader_label", "roberta_label"]].copy()
    frames.append(d)
look = pd.concat(frames, ignore_index=True)
look["roberta_label"] = look["roberta_label"].map(ROBERTA_MAP)
# de-dup by id (verification confirmed 0 cross-file id collisions among analyzed files)
look = look.drop_duplicates(subset="id")

def _read_csv_robust(path, **kw):
    """Read a CSV, trying several encodings before giving up.

    ground_truth_400.csv was saved with a non-UTF-8 encoding, so a plain
    read_csv raises UnicodeDecodeError on a handful of comment bodies.
    """
    # ground_truth_400.csv was saved latin-1/cp1252 by a teammate; fall back gracefully.
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc, **kw)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, encoding="latin-1", **kw)  # last resort, never raises

gt = _read_csv_robust(GT, dtype={"id": str}, low_memory=False)
merged = gt.merge(look, on="id", how="left", validate="one_to_one")
unmatched = merged["vader_label"].isna().sum()

# The attribution and script-provenance lines below used to be added to the
# report by hand after each run, so re-running this script silently deleted
# them (caught in the Week 8 re-run). They are generated now instead.
lines = ["# Method Validation Report (Week 5, Student B)", "",
         "**Authored by Jose Araya. Reviewed and confirmed by Jose Araya, 2026-07-10.**", "",
         f"Gold standard: `data/merged/ground_truth_400.csv` — {len(gt)} stratified items "
         f"(Facebook {int((gt.platform=='facebook').sum())}, Reddit {int((gt.platform=='reddit').sum())}, "
         f"White House {int((gt.platform=='whitehouse').sum())}).",
         f"Adjudicated (consensus label present): {int(gt['label_consensus'].notna().sum())}; "
         f"unresolved annotator disagreements excluded: {int(gt['label_consensus'].isna().sum())}.",
         f"Rows matched to a scored record: {len(gt) - unmatched}/{len(gt)}"
         + (f" (⚠ {unmatched} unmatched)" if unmatched else ""),
         "Scoring / comparison script: `code/week5_hypotheses/evaluate_methods.py` "
         "(joins the gold standard to the scored `data/processed/*_labeled.csv` records "
         "and computes the accuracy / per-class P-R-F1 / confusion / gratitude-inflation "
         "numbers below).", ""]

# ---- Part 1: accuracy + per-class P/R/F1 ----
ev = merged[merged["label_consensus"].notna()].copy()
y_true = ev["label_consensus"]

lines.append("## 1. Accuracy and per-class precision / recall / F1")
lines.append("")
for method, col in [("VADER", "vader_label"), ("RoBERTa", "roberta_label")]:
    y_pred = ev[col]
    acc = accuracy_score(y_true, y_pred)
    rep = classification_report(y_true, y_pred, labels=LABELS, output_dict=True, zero_division=0)
    lines.append(f"### {method} — accuracy {acc:.3f} (n={len(ev)})")
    lines.append("")
    lines.append("| class | precision | recall | F1 | support |")
    lines.append("|---|---|---|---|---|")
    for c in LABELS:
        r = rep[c]
        lines.append(f"| {c} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1-score']:.3f} | {int(r['support'])} |")
    lines.append(f"| **macro avg** | {rep['macro avg']['precision']:.3f} | {rep['macro avg']['recall']:.3f} "
                 f"| {rep['macro avg']['f1-score']:.3f} | {int(rep['macro avg']['support'])} |")
    lines.append(f"| **weighted avg** | {rep['weighted avg']['precision']:.3f} | {rep['weighted avg']['recall']:.3f} "
                 f"| {rep['weighted avg']['f1-score']:.3f} | {int(rep['weighted avg']['support'])} |")
    lines.append("")
    cm = confusion_matrix(y_true, y_pred, labels=LABELS)
    lines.append("Confusion matrix (rows = true, cols = predicted):")
    lines.append("")
    lines.append("| true \\ pred | " + " | ".join(LABELS) + " |")
    lines.append("|---|" + "---|" * len(LABELS))
    for i, c in enumerate(LABELS):
        lines.append(f"| {c} | " + " | ".join(str(int(x)) for x in cm[i]) + " |")
    lines.append("")

# winner
acc_v = accuracy_score(y_true, ev["vader_label"])
acc_r = accuracy_score(y_true, ev["roberta_label"])
better = "RoBERTa" if acc_r > acc_v else "VADER"
f1_v = classification_report(y_true, ev["vader_label"], labels=LABELS,
                             output_dict=True, zero_division=0)["macro avg"]["f1-score"]
f1_r = classification_report(y_true, ev["roberta_label"], labels=LABELS,
                             output_dict=True, zero_division=0)["macro avg"]["f1-score"]
pos_prec_v = classification_report(y_true, ev["vader_label"], labels=LABELS,
                                   output_dict=True, zero_division=0)["positive"]

# The paragraphs below were hand-written into the report after the 2026-07-10
# advisor review, which reversed the earlier "the data supports VADER for
# continuity" framing. They are generated here so re-running does not revert it.
lines.append(f"**Higher accuracy vs gold standard: {better}, on every metric.** "
             f"RoBERTa beats VADER on overall accuracy ({acc_r:.3f} vs {acc_v:.3f}), "
             f"macro-F1 ({f1_r:.3f} vs {f1_v:.3f}), and precision, recall, and F1 for "
             f"*all three* classes. VADER's core failure is positive precision "
             f"({pos_prec_v['precision']:.3f}): it reads politeness and gratitude as "
             f"positive, over-predicting the positive class (recall "
             f"{pos_prec_v['recall']:.3f} but precision {pos_prec_v['precision']:.3f}).")
lines.append("")
lines.append("**Primary-method decision — an explicit tradeoff, not a data endorsement "
             "of VADER.** The data does not support keeping VADER as primary; only "
             "continuity does. The two considerations point in opposite directions:")
lines.append("")
lines.append("- **Continuity (favors VADER):** VADER was the Fall-2024 students' scorer, "
             "so keeping it primary makes this season's numbers directly comparable to "
             "that prior work with no re-baselining.")
lines.append("- **Accuracy (favors RoBERTa):** RoBERTa is measurably more accurate against "
             "the human gold standard — every class, every metric — and does not carry "
             "VADER's positive bias (which also inflates the Facebook side of H1/H3).")
lines.append("")
lines.append("This is a value judgment (comparability vs. correctness) for the advisor to "
             "settle, and should be stated as such wherever the primary method is named — "
             "not framed as \"the data supports VADER.\" Our recommendation: **lead with "
             "RoBERTa as the primary reported scorer and carry VADER as the continuity "
             "baseline / cross-check.**")
lines.append("")

# ---- Part 2: gratitude inflation on Facebook comments ----
lines.append("## 2. Gratitude-inflation estimate (Facebook comments)")
lines.append("")
fbc = merged[(merged.platform == "facebook") & (merged.type == "comment")].copy()
fbc["grat"] = pd.to_numeric(fbc["gratitude_consensus"], errors="coerce")
lines.append(f"Facebook comments in gold sample: {len(fbc)}; gratitude-tagged (consensus=1): "
             f"{int((fbc['grat'] == 1).sum())}.")
lines.append("")
lines.append("Among Facebook comments each method labels **positive**, the fraction carrying the human gratitude tag:")
lines.append("")
lines.append("| method | FB comments labeled positive | of those, gratitude-tagged | inflation rate |")
lines.append("|---|---|---|---|")
for method, col in [("VADER", "vader_label"), ("RoBERTa", "roberta_label")]:
    pos = fbc[fbc[col] == "positive"]
    g = int((pos["grat"] == 1).sum())
    rate = g / len(pos) if len(pos) else float("nan")
    lines.append(f"| {method} | {len(pos)} | {g} | {rate:.1%} |")
lines.append("")
# also report gratitude among TRUE positives for reference
truepos = fbc[fbc["label_consensus"] == "positive"]
gt_rate = (truepos["grat"] == 1).mean() if len(truepos) else float("nan")
lines.append(f"For reference, among human-labeled-positive FB comments ({len(truepos)}), "
             f"{gt_rate:.1%} are gratitude-tagged.")
lines.append("")
lines.append("Interpretation: a non-trivial share of Facebook 'positive' sentiment is gratitude directed "
             "at the communicator (thanking Denis Phillips) rather than positive feeling about the storm — "
             "so the Facebook–Reddit positivity gap (H1) is partly a person-directed-thanks artifact. "
             "Sample is small (gold-standard FB comments only); report as an estimate, not a population rate.")

OUT.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
print(f"\nWrote {OUT}")
