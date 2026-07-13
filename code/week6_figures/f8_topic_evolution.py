#!/usr/bin/env python3
"""
F8 — Topic evolution over days_from_landfall.

Heatmaps of within-day topic proportions for the top 8 substantive topic
categories overall (excluding `excluded`), shown separately for Debby, Helene,
and Milton.

Outputs figures/f8_topic_evolution.png/.pdf
+ docs/week6/f8_topic_evolution_results.md. Read-only on inputs.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import textwrap

REPO = Path(__file__).resolve().parents[2]
MERGED = REPO / "data" / "merged"
DOCS = REPO / "docs" / "week6"
DOCS.mkdir(parents=True, exist_ok=True)
FIGS = REPO / "figures"

TOP_N = 8
HURRICANES = ["debby", "helene", "milton"]
HURRICANE_DAY_WINDOWS = {
    "debby": (-5, 0),
    "helene": (-4, 1),
    "milton": (-5, 0),
}

m = pd.read_csv(MERGED / "master_vader_roberta_topics.csv", low_memory=False)
m["hurricane"] = m["hurricane"].astype(str).str.lower()
m = m[m["type"] == "comment"].copy()
m["days_from_landfall"] = pd.to_numeric(m["days_from_landfall"], errors="coerce")

substantive = m[m["topic_category"].ne("excluded") & m["days_from_landfall"].notna()].copy()
if substantive.empty:
    raise RuntimeError("No substantive rows found for F8")

counts = substantive["topic_category"].value_counts()
top_topics = counts.head(TOP_N).index.tolist()
ordered_topics = counts.loc[top_topics].sort_values(ascending=True).index.tolist()
display_topics = [textwrap.fill(t.replace(" / ", " /\n"), width=24) for t in ordered_topics]

# Diagnostics for the requested -5 day check.
raw_comment = m[m["days_from_landfall"].notna()].copy()
day_minus5_counts = {
    h: int(((raw_comment["hurricane"] == h) & (raw_comment["days_from_landfall"] == -5)).sum())
    for h in HURRICANES
}

fig, axes = plt.subplots(1, 3, figsize=(17.5, 7.2), sharey=False, constrained_layout=True)
last_im = None
panel_stats = []

for ax, hurricane in zip(axes, HURRICANES):
    sub = substantive[substantive["hurricane"] == hurricane].copy()
    if sub.empty:
        ax.set_axis_off()
        continue

    day_min, day_max = HURRICANE_DAY_WINDOWS[hurricane]
    sub = sub[sub["days_from_landfall"].between(day_min, day_max)].copy()
    if sub.empty:
        ax.set_axis_off()
        continue

    days = np.arange(day_min, day_max + 1)
    topic_counts = (
        sub[sub["topic_category"].isin(top_topics)]
        .groupby(["days_from_landfall", "topic_category"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=days, columns=ordered_topics, fill_value=0)
    )
    day_totals = sub.groupby("days_from_landfall").size().reindex(days, fill_value=0)
    proportions = topic_counts.div(day_totals.replace(0, np.nan), axis=0).fillna(0) * 100
    mat = proportions.T.values

    last_im = ax.imshow(mat, aspect="auto", origin="lower", cmap="magma", vmin=0, vmax=max(1.0, float(np.nanmax(mat))))
    ax.set_title(hurricane.capitalize())
    ax.set_xticks(np.linspace(0, len(days) - 1, num=min(8, len(days)), dtype=int))
    ax.set_xticklabels([int(days[i]) for i in np.linspace(0, len(days) - 1, num=min(8, len(days)), dtype=int)], rotation=0, fontsize=8)
    ax.set_yticks(range(len(ordered_topics)))
    ax.set_yticklabels(display_topics, fontsize=8)
    if ax is axes[0]:
        ax.set_ylabel("Topic category")
    ax.set_xlabel("Days from landfall")
    panel_stats.append((hurricane, int(len(sub)), day_min, day_max))

cbar = fig.colorbar(last_im, ax=axes.ravel().tolist(), fraction=0.018, pad=0.02)
cbar.set_label("Within-day topic share (%)")
fig.suptitle("Figure 8 — Topic evolution by days from landfall", y=1.05, fontsize=14)
for ext in ("png", "pdf"):
    fig.savefig(FIGS / f"f8_topic_evolution.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)

lines = [
    "# F8 — Topic Evolution",
    "",
    "Heatmaps of within-day topic shares for the top 8 substantive categories overall (excluding `excluded`), separated by hurricane.",
    "",
    "| hurricane | substantive comments used | day range |",
    "|---|---:|---|",
]
for hurricane, n_rows, day_min, day_max in panel_stats:
    lines.append(f"| {hurricane} | {n_rows:,} | {day_min} to {day_max} |")
lines += [
    "",
    "| hurricane | comment rows at day -5 (raw master comments) |",
    "|---|---:|",
]
for h in HURRICANES:
    lines.append(f"| {h} | {day_minus5_counts[h]:,} |")
lines += [
    "",
    "Note: Helene day -5 is empty because upstream Reddit event-window filtering starts Helene at -4 in collection/merge logic.",
    "",
    "Figure: `figures/f8_topic_evolution.png/.pdf` (300 dpi).",
    "",
    "Status: **built**.",
]
(DOCS / "f8_topic_evolution_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print("\n".join(lines))
print("\nWrote figures/f8_topic_evolution.png/.pdf + docs/week6/f8_topic_evolution_results.md")
