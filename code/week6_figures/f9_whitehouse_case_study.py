#!/usr/bin/env python3
"""
F9 — White House case study.

Two-panel timeline for White House Reddit threads:
    - Engagement: daily comment volume.
    - Sentiment: daily mean VADER compound with a dashed RoBERTa line.

The x-axis uses calendar dates and includes vertical markers for hurricane
landfall dates.

Outputs figures/f9_whitehouse_case_study.png/.pdf
+ docs/week6/f9_whitehouse_case_study_results.md. Read-only on inputs.
"""
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[2]
MERGED = REPO / "data" / "merged"
DOCS = REPO / "docs" / "week6"
DOCS.mkdir(parents=True, exist_ok=True)
FIGS = REPO / "figures"

LANDFALL_DATES = {
    "debby": pd.Timestamp("2024-08-05"),
    "helene": pd.Timestamp("2024-09-26"),
    "milton": pd.Timestamp("2024-10-09"),
}

m = pd.read_csv(MERGED / "master_vader_roberta_topics.csv", low_memory=False)
m["hurricane"] = m["hurricane"].astype(str).str.lower()
m["days_from_landfall"] = pd.to_numeric(m["days_from_landfall"], errors="coerce")
m = m[(m["platform"] == "reddit") & (m["source_type"].isin(["government", "government_response"])) & (m["type"] == "comment")].copy()

if m.empty:
    raise RuntimeError("No White House rows found for F9")

# Sentiment values.
m["vader_compound"] = pd.to_numeric(m["vader_compound"], errors="coerce")
m["roberta_compound"] = pd.to_numeric(m["roberta_pos"], errors="coerce") - pd.to_numeric(m["roberta_neg"], errors="coerce")

# Build event_date from hurricane-specific landfall date + day offset.
m["event_date"] = pd.NaT
for h, landfall_dt in LANDFALL_DATES.items():
    mask = m["hurricane"].eq(h) & m["days_from_landfall"].notna()
    m.loc[mask, "event_date"] = landfall_dt + pd.to_timedelta(m.loc[mask, "days_from_landfall"], unit="D")
m = m[m["event_date"].notna()].copy()

# Daily engagement and sentiment.
daily = m.groupby("event_date").agg(
    comments=("id", "size"),
    mean_vader=("vader_compound", "mean"),
    mean_roberta=("roberta_compound", "mean"),
).sort_index()

# Focus plotting on the main activity period (up to 98% cumulative comments)
# so sparse long-tail dates do not flatten the trend.
cum_share = (daily["comments"].cumsum() / daily["comments"].sum())
main_end = cum_share[cum_share <= 0.98].index.max()
if pd.isna(main_end):
    main_end = daily.index.max()
plot_start = daily.index.min() - pd.Timedelta(days=1)
plot_end = main_end + pd.Timedelta(days=1)
plot_daily = daily[(daily.index >= plot_start) & (daily.index <= plot_end)]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12.5, 8.2), sharex=True, gridspec_kw={"height_ratios": [1.1, 1.0]})

# Panel 1: engagement.
ax1.bar(plot_daily.index, plot_daily["comments"], color="#4c78a8", width=0.9, alpha=0.85, label="Comments/day")
ax1.legend(loc="upper right", frameon=False)

ax1.set_ylabel("White House comments")
ax1.set_title("Figure 9 — White House thread engagement and sentiment trajectory")
ax1.grid(axis="y", alpha=0.2)

# Panel 2: sentiment.
ax2.plot(plot_daily.index, plot_daily["mean_vader"], color="#1f77b4", lw=2.0, marker="o", ms=3.5, label="Mean VADER compound")
ax2.plot(plot_daily.index, plot_daily["mean_roberta"], color="#2ca02c", lw=1.8, ls="--", marker="s", ms=3.0, label="Mean RoBERTa compound")
ax2.axhline(0, color="gray", lw=0.8, ls=":")
ax2.set_ylabel("Mean sentiment")
ax2.set_xlabel("Date")
ax2.grid(axis="y", alpha=0.2)
ax2.legend(loc="upper right", frameon=False)

# Landfall date markers.
for h, dt in LANDFALL_DATES.items():
    if plot_daily.index.min() <= dt <= plot_daily.index.max():
        ax1.axvline(dt, color="#555555", lw=1.0, ls="--", alpha=0.7)
        ax2.axvline(dt, color="#555555", lw=1.0, ls="--", alpha=0.7)
        ax2.text(dt, ax2.get_ylim()[1] * 0.95, f"{h.capitalize()} landfall", rotation=90,
                 ha="right", va="top", fontsize=8, color="#444444")

ax2.set_xlim(plot_daily.index.min() - pd.Timedelta(days=1), plot_daily.index.max() + pd.Timedelta(days=1))

fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(FIGS / f"f9_whitehouse_case_study.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)

lines = [
    "# F9 — White House Case Study",
    "",
    "Two-panel timeline summarizing White House Reddit thread activity: daily comment volume and daily mean sentiment (VADER + RoBERTa).",
    "",
    f"Total White House comment rows used: {len(m):,}.",
    f"Plotted main-activity date window: {plot_daily.index.min().strftime('%Y-%m-%d')} to {plot_daily.index.max().strftime('%Y-%m-%d')} (covers 98% cumulative comments).",
    "Landfall markers shown for Debby (2024-08-05), Helene (2024-09-26), and Milton (2024-10-09).",
    "",
    "| date | comments | mean VADER | mean RoBERTa |",
    "|---|---:|---:|---:|",
]
for dt, row in plot_daily.iterrows():
    lines.append(f"| {dt.strftime('%Y-%m-%d')} | {int(row['comments']):,} | {row['mean_vader']:+.4f} | {row['mean_roberta']:+.4f} |")
lines += [
    "",
    "Figure: `figures/f9_whitehouse_case_study.png/.pdf` (300 dpi).",
    "",
    "Status: **built**.",
]
(DOCS / "f9_whitehouse_case_study_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

print("\n".join(lines))
print("\nWrote figures/f9_whitehouse_case_study.png/.pdf + docs/week6/f9_whitehouse_case_study_results.md")
