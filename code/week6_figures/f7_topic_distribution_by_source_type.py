#!/usr/bin/env python3
"""
F7 — Topic distribution by source_type.

Three horizontal bar panels, one per source type:
  - community_discussion
  - facebook
  - government_response

The plot uses the top 9 substantive topic categories overall (excluding `excluded`)
and shows within-source proportions so each panel sums to 100%.

Outputs figures/f7_topic_distribution_by_source_type.png/.pdf
+ docs/week6/f7_topic_distribution_by_source_type_results.md. Read-only on inputs.
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

TOP_N = 9
SOURCE_ORDER = ["community_discussion", "facebook", "government_response"]
SOURCE_LABELS = {
    "community_discussion": "Reddit community",
    "facebook": "Facebook",
    "government_response": "White House",
}
SOURCE_COLORS = {
    "community_discussion": "#ff7f0e",
    "facebook": "#1f77b4",
    "government_response": "#2ca02c",
}

m = pd.read_csv(MERGED / "master_vader_roberta_topics.csv", low_memory=False)
m["hurricane"] = m["hurricane"].astype(str).str.lower()
m = m[m["type"] == "comment"].copy()
m["source_bucket"] = m["source_type"].fillna("facebook")
m["source_bucket"] = m["source_bucket"].replace({"government": "government_response"})

substantive = m[m["topic_category"].ne("excluded")].copy()
if substantive.empty:
    raise RuntimeError("No substantive rows found for F7")

counts = substantive["topic_category"].value_counts()
top_topics = counts.head(TOP_N).index.tolist()

# Keep a stable order by overall frequency.
ordered_topics = counts.loc[top_topics].sort_values(ascending=True).index.tolist()

summary = (
    substantive[substantive["topic_category"].isin(top_topics)]
    .groupby(["source_bucket", "topic_category"])
    .size()
    .unstack(fill_value=0)
    .reindex(index=SOURCE_ORDER, columns=ordered_topics, fill_value=0)
)

source_totals = substantive.groupby("source_bucket").size().reindex(SOURCE_ORDER)
proportions = summary.div(source_totals, axis=0).fillna(0) * 100

fig, axes = plt.subplots(1, 3, figsize=(14.8, 7.5), sharey=True)
for ax, src in zip(axes, SOURCE_ORDER):
    vals = proportions.loc[src].values
    ax.barh(ordered_topics, vals, color=SOURCE_COLORS[src], edgecolor="white", height=0.72)
    ax.set_title(SOURCE_LABELS[src])
    ax.set_xlim(0, max(100, float(np.nanmax(proportions.values)) * 1.15))
    ax.grid(axis="x", alpha=0.2)
    ax.invert_yaxis()
    for i, v in enumerate(vals):
        if v >= 2.0:
            ax.text(v + 0.8, i, f"{v:.1f}%", va="center", ha="left", fontsize=8)
    if src == "community_discussion":
        ax.set_ylabel("Topic category")
    ax.set_xlabel("Within-source share (%)")

fig.suptitle("Figure 7 — Topic distribution by source type", y=0.98, fontsize=14)
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(FIGS / f"f7_topic_distribution_by_source_type.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)

lines = [
    "# F7 — Topic Distribution by Source Type",
    "",
    "Three horizontal bar panels showing within-source topic shares for the top 9 substantive categories overall (excluding `excluded`).",
    "",
    "| topic category | Reddit community | Facebook | White House | overall count |",
    "|---|---:|---:|---:|---:|",
]
for topic in ordered_topics:
    row = summary[topic].to_dict()
    lines.append(
        f"| {topic} | {row.get('community_discussion', 0):,} | {row.get('facebook', 0):,} | {row.get('government_response', 0):,} | {int(counts[topic]):,} |"
    )
lines += [
    "",
    f"Source totals used for percentages: Reddit community {int(source_totals['community_discussion']):,}, Facebook {int(source_totals['facebook']):,}, White House {int(source_totals['government_response']):,}.",
    "",
    "Figure: `figures/f7_topic_distribution_by_source_type.png/.pdf` (300 dpi).",
    "",
    "Status: **built**.",
]
(DOCS / "f7_topic_distribution_by_source_type_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print("\n".join(lines))
print("\nWrote figures/f7_topic_distribution_by_source_type.png/.pdf + docs/week6/f7_topic_distribution_by_source_type_results.md")
