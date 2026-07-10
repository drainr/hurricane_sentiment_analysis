#!/usr/bin/env python3
"""
F1 — Dataset overview.

Stacked bars of record counts by source × hurricane, from the merged master.
Three sources (paper color convention):
  Facebook            = blue  (source_type is NaN in the master; platform == facebook)
  Reddit community    = orange (source_type == community_discussion)
  White House         = green  (source_type in {government, government_response})

Callout: the White House Reddit account only existed for Helene and Milton
(0 records for Debby).

Outputs figures/f1_dataset_overview.png/.pdf + docs/week6/f1_dataset_overview_results.md.
Read-only on inputs.
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
COLORS = {"Facebook": "#1f77b4", "Reddit community": "#ff7f0e", "White House": "#2ca02c"}

m = pd.read_csv(MERGED / "master_vader_roberta_topics.csv", low_memory=False)
m["hurricane"] = m["hurricane"].str.lower()


def source_bucket(st):
    if pd.isna(st):
        return "Facebook"
    if st == "community_discussion":
        return "Reddit community"
    if st in ("government", "government_response"):
        return "White House"
    return "other"


m["source_group"] = m["source_type"].map(source_bucket)
assert (m["source_group"] != "other").all(), "unexpected source_type value"

# counts[source][hurricane]
counts = {s: [int(((m.source_group == s) & (m.hurricane == h)).sum()) for h in HURRICANES]
          for s in SOURCES}
totals = {s: sum(counts[s]) for s in SOURCES}
grand_total = sum(totals.values())

# ---------------- figure: stacked bars, x = hurricane, stacked by source ----------------
fig, ax = plt.subplots(figsize=(8, 5.2))
x = np.arange(len(HURRICANES))
bottom = np.zeros(len(HURRICANES))
for s in SOURCES:
    vals = np.array(counts[s], dtype=float)
    bars = ax.bar(x, vals, bottom=bottom, color=COLORS[s], label=s, width=0.6, edgecolor="white")
    # annotate each non-trivial segment with its count; thin segments get an
    # offset label to the right with a short leader so they never collide.
    for xi, (v, b) in enumerate(zip(vals, bottom)):
        if v <= 0:
            continue
        if v > grand_total * 0.03:
            ax.text(xi, b + v / 2, f"{int(v):,}", ha="center", va="center",
                    fontsize=8, color="white")
        else:
            yc = b + v / 2
            ax.annotate(f"{int(v):,}", xy=(xi + 0.30, yc), xytext=(xi + 0.42, yc),
                        ha="left", va="center", fontsize=8, color=COLORS[s],
                        arrowprops=dict(arrowstyle="-", color=COLORS[s], lw=0.7))
    bottom += vals

ax.set_xticks(x)
ax.set_xticklabels([h.capitalize() for h in HURRICANES])
ax.set_ylabel("Records (posts + comments)")
ax.set_title("Dataset overview — records by source and hurricane")
ax.legend(title="Source", loc="upper left")
# per-hurricane totals above each bar
for xi, h in enumerate(HURRICANES):
    tot = sum(counts[s][xi] for s in SOURCES)
    ax.text(xi, tot + grand_total * 0.01, f"{tot:,}", ha="center", va="bottom",
            fontsize=9, fontweight="bold")
ax.margins(y=0.12)
# callout as a footnote below the axis (keeps the plot area clean)
fig.text(0.5, -0.02,
         "White House Reddit account existed only for Helene and Milton (0 records for Debby).",
         ha="center", va="top", fontsize=8, style="italic", color="#555555")
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(FIGS / f"f1_dataset_overview.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)

# ---------------- results doc ----------------
lines = ["# F1 — Dataset Overview", "",
         "Stacked bars: record counts (posts + comments) by source × hurricane, "
         "from `data/merged/master_vader_roberta_topics.csv`.", "",
         "| source | Debby | Helene | Milton | total |", "|---|---|---|---|---|"]
for s in SOURCES:
    lines.append(f"| {s} | " + " | ".join(f"{counts[s][i]:,}" for i in range(3))
                 + f" | {totals[s]:,} |")
lines.append(f"| **total** | " + " | ".join(
    f"{sum(counts[s][i] for s in SOURCES):,}" for i in range(3)) + f" | **{grand_total:,}** |")
lines += ["",
          "Callout: the White House Reddit account only existed for Helene and Milton "
          "(0 records for Debby).",
          "",
          "Figure: `figures/f1_dataset_overview.png/.pdf` (300 dpi).",
          "",
          "Status: **FINAL**."]
(DOCS / "f1_dataset_overview_results.md").write_text("\n".join(lines) + "\n")

print("\n".join(lines))
print("\nWrote figures/f1_dataset_overview.png/.pdf + docs/week6/f1_dataset_overview_results.md")
print(f"Grand total: {grand_total:,}")
