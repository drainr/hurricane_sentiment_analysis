#!/usr/bin/env python3
"""
F4 — Sentiment distribution.

100% stacked bars: % negative / neutral / positive by source × hurricane,
comment-level (matches H1 = comments, H7 = WH comments). One figure for VADER
(vader_label) and one for RoBERTa (roberta_label). Built from the merged master.

Outputs figures/f4_sentiment_distribution_{vader,roberta}.png/.pdf
+ docs/week6/f4_sentiment_distribution_results.md. Read-only on inputs.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[2]
MERGED = REPO / "data" / "merged"
DOCS = REPO / "docs" / "week6"
DOCS.mkdir(parents=True, exist_ok=True)
FIGS = REPO / "figures"

HURRICANES = ["debby", "helene", "milton"]
SOURCES = ["Facebook", "Reddit community", "White House"]
SENT = ["negative", "neutral", "positive"]
SENT_COLORS = {"negative": "#d62728", "neutral": "#bcbcbc", "positive": "#2ca02c"}

ROBERTA_MAP = {"neg": "negative", "neu": "neutral", "neutral": "neutral", "pos": "positive",
               "negative": "negative", "positive": "positive"}
VADER_MAP = {"neg": "negative", "neu": "neutral", "pos": "positive",
             "negative": "negative", "neutral": "neutral", "positive": "positive"}

m = pd.read_csv(MERGED / "master_vader_roberta_topics.csv", low_memory=False)
m["hurricane"] = m["hurricane"].str.lower()
m = m[m["type"] == "comment"].copy()


def source_bucket(st):
    """Map a source_type onto a display source (NaN = Facebook)."""
    if pd.isna(st):
        return "Facebook"
    if st == "community_discussion":
        return "Reddit community"
    if st in ("government", "government_response"):
        return "White House"
    return "other"


m["source_group"] = m["source_type"].map(source_bucket)
m["vlab"] = m["vader_label"].astype(str).str.strip().str.lower().map(VADER_MAP)
m["rlab"] = m["roberta_label"].astype(str).str.strip().str.lower().map(ROBERTA_MAP)


def pct_table(label_col):
    """(source, hurricane) -> {sentiment: pct}, plus n. Only groups with rows."""
    out = {}
    for s in SOURCES:
        for h in HURRICANES:
            sub = m[(m.source_group == s) & (m.hurricane == h)]
            if len(sub) == 0:
                continue
            counts = sub[label_col].value_counts()
            n = int(counts.sum())
            out[(s, h)] = ({k: counts.get(k, 0) / n * 100 for k in SENT}, n)
    return out


def plot(label_col, method, fname):
    """Draw 100% stacked bars of negative/neutral/positive share by source and hurricane."""
    table = pct_table(label_col)
    # x positions grouped by hurricane; sources within
    groups = [(s, h) for h in HURRICANES for s in SOURCES if (s, h) in table]
    x = np.arange(len(groups))
    fig, ax = plt.subplots(figsize=(10, 5.4))
    bottom = np.zeros(len(groups))
    for sent in SENT:
        vals = np.array([table[g][0][sent] for g in groups])
        ax.bar(x, vals, bottom=bottom, color=SENT_COLORS[sent], label=sent.capitalize(),
               width=0.7, edgecolor="white")
        for xi, (v, b) in enumerate(zip(vals, bottom)):
            if v >= 5:
                ax.text(xi, b + v / 2, f"{v:.0f}%", ha="center", va="center",
                        fontsize=8, color="white")
        bottom += vals
    # two-line tick labels: source (short) + n
    short = {"Facebook": "FB", "Reddit community": "Reddit", "White House": "WH"}
    ax.set_xticks(x)
    ax.set_xticklabels([f"{short[s]}\nn={table[(s, h)][1]:,}" for (s, h) in groups], fontsize=8)
    # hurricane band labels under groups
    for h in HURRICANES:
        idx = [i for i, (s, hh) in enumerate(groups) if hh == h]
        if idx:
            ax.text(np.mean(idx), -13, h.capitalize(), ha="center", va="top",
                    fontsize=11, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.set_ylabel("% of comments")
    ax.set_title(f"Sentiment distribution by source and hurricane ({method}, comment-level)")
    # legend a little below the hurricane band labels (moderate gap, not too far)
    ax.legend(title="Sentiment", loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=3)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"{fname}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return table


tv = plot("vlab", "VADER", "f4_sentiment_distribution_vader")
tr = plot("rlab", "RoBERTa", "f4_sentiment_distribution_roberta")

# ---------------- results doc ----------------
lines = ["# F4 — Sentiment Distribution (comment-level)", "",
         "100% stacked % negative/neutral/positive by source × hurricane, from the master "
         "(comments only). White House has no Debby data.", ""]
for method, table in [("VADER", tv), ("RoBERTa", tr)]:
    lines.append(f"## {method}")
    lines.append("| source | hurricane | n | % neg | % neu | % pos |")
    lines.append("|---|---|---|---|---|---|")
    for h in HURRICANES:
        for s in SOURCES:
            if (s, h) in table:
                pct, n = table[(s, h)]
                lines.append(f"| {s} | {h} | {n:,} | {pct['negative']:.1f} | "
                             f"{pct['neutral']:.1f} | {pct['positive']:.1f} |")
    lines.append("")
lines += ["Figures: `figures/f4_sentiment_distribution_{vader,roberta}.png/.pdf` (300 dpi).", "",
          "Status: **built (VADER + RoBERTa).**"]
(DOCS / "f4_sentiment_distribution_results.md").write_text("\n".join(lines) + "\n")

print("\n".join(lines))
print("\nWrote figures/f4_sentiment_distribution_{vader,roberta}.* + docs/week6/f4_sentiment_distribution_results.md")
