#!/usr/bin/env python3
"""
F6 — VADER vs RoBERTa agreement.

3x3 confusion matrix of vader_label × roberta_label (negative/neutral/positive)
across all six scored files, cells annotated with count and % of total. Reports
the overall agreement rate (diagonal share). This is method-vs-method label
agreement, independent of the continuous pos-neg convention.

Outputs figures/f6_vader_roberta_agreement.png/.pdf + docs/week6/f6_agreement_results.md.
Read-only on inputs.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "data" / "processed"
DOCS = REPO / "docs" / "week6"
DOCS.mkdir(parents=True, exist_ok=True)
FIGS = REPO / "figures"

ROBERTA_MAP = {"NEG": "negative", "NEU": "neutral", "NEUTRAL": "neutral", "POS": "positive",
               "negative": "negative", "neutral": "neutral", "positive": "positive"}
VADER_MAP = {"neg": "negative", "neu": "neutral", "pos": "positive",
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

frames = []
for f in PROC_FILES:
    d = pd.read_csv(PROC / f, dtype={"id": str}, low_memory=False)
    frames.append(d[["id", "vader_label", "roberta_label"]].copy())
look = pd.concat(frames, ignore_index=True).drop_duplicates(subset="id")
look["vader_label"] = look["vader_label"].astype(str).str.strip().str.lower().map(VADER_MAP)
look["roberta_label"] = look["roberta_label"].map(ROBERTA_MAP)
look = look.dropna(subset=["vader_label", "roberta_label"])

# confusion matrix: rows = VADER, cols = RoBERTa
cm = pd.crosstab(look["vader_label"], look["roberta_label"]).reindex(
    index=LABELS, columns=LABELS, fill_value=0)
total = int(cm.values.sum())
agree = int(np.trace(cm.values))
agree_rate = agree / total

# ---------------- figure: heatmap ----------------
fig, ax = plt.subplots(figsize=(6.4, 5.4))
mat = cm.values
im = ax.imshow(mat, cmap="Blues", aspect="auto")
ax.set_xticks(range(3)); ax.set_xticklabels([l.capitalize() for l in LABELS])
ax.set_yticks(range(3)); ax.set_yticklabels([l.capitalize() for l in LABELS])
ax.set_xlabel("RoBERTa label")
ax.set_ylabel("VADER label")
ax.set_title(f"VADER vs RoBERTa label agreement\noverall agreement {agree_rate:.1%} "
             f"({agree:,} / {total:,})")
thresh = mat.max() * 0.6
for i in range(3):
    for j in range(3):
        c = mat[i, j]
        ax.text(j, i, f"{c:,}\n{c/total:.1%}", ha="center", va="center",
                color="white" if c > thresh else "black", fontsize=10,
                fontweight="bold" if i == j else "normal")
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="records")
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(FIGS / f"f6_vader_roberta_agreement.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)

# ---------------- results doc ----------------
lines = ["# F6 — VADER vs RoBERTa Agreement", "",
         f"3×3 confusion matrix of `vader_label` × `roberta_label` over all six scored "
         f"files ({total:,} records with both labels).", "",
         f"**Overall agreement (diagonal): {agree_rate:.1%}** ({agree:,} / {total:,}).", "",
         "Confusion matrix (rows = VADER, cols = RoBERTa; count / % of total):", "",
         "| VADER \\\\ RoBERTa | " + " | ".join(l.capitalize() for l in LABELS) + " | row total |",
         "|---|" + "---|" * (len(LABELS) + 1)]
for i, r in enumerate(LABELS):
    cells = " | ".join(f"{cm.values[i, j]:,} ({cm.values[i, j]/total:.1%})" for j in range(3))
    lines.append(f"| {r.capitalize()} | {cells} | {cm.values[i].sum():,} |")
lines.append("| **col total** | "
             + " | ".join(f"{cm.values[:, j].sum():,}" for j in range(3)) + f" | {total:,} |")
lines += ["",
          "Per-class agreement (VADER label = RoBERTa label, of VADER rows in that class):",
          ""]
for i, r in enumerate(LABELS):
    row_tot = cm.values[i].sum()
    lines.append(f"- {r}: {cm.values[i, i]/row_tot:.1%} ({cm.values[i, i]:,}/{row_tot:,})")
lines += ["",
          "Figure: `figures/f6_vader_roberta_agreement.png/.pdf` (300 dpi).", "",
          "Status: **built.**"]
(DOCS / "f6_agreement_results.md").write_text("\n".join(lines) + "\n")

print("\n".join(lines))
print(f"\nWrote figures/f6_vader_roberta_agreement.* + docs/week6/f6_agreement_results.md")
