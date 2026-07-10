#!/usr/bin/env python3
"""
F3 — Three-way source comparison.

Grouped bars: mean sentiment by source × hurricane (comment-level), with 95% CI
error bars and significance stars. One figure for VADER (vader_compound) and one
for RoBERTa (continuous roberta_pos - roberta_neg, the standardized convention).

Significance:
  - FB vs Reddit within each hurricane: stars from H1 per-hurricane p
    (hypothesis_tests_all7_jose.csv).
  - WH vs FB / WH vs Reddit: H7 is pooled across storms (not per-hurricane), so it
    is reported as a footnote rather than per-storm brackets.

Outputs figures/f3_three_way_{vader,roberta}.png/.pdf
+ docs/week6/f3_three_way_results.md. Read-only on inputs.
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
m = m[m["type"] == "comment"].copy()
m["vader_compound"] = pd.to_numeric(m["vader_compound"], errors="coerce")
m["roberta_compound"] = (pd.to_numeric(m["roberta_pos"], errors="coerce")
                         - pd.to_numeric(m["roberta_neg"], errors="coerce"))


def source_bucket(st):
    if pd.isna(st):
        return "Facebook"
    if st == "community_discussion":
        return "Reddit community"
    if st in ("government", "government_response"):
        return "White House"
    return "other"


m["source_group"] = m["source_type"].map(source_bucket)

# H1 per-hurricane p (Reddit vs FB) per model
j = pd.read_csv(MERGED / "hypothesis_tests_all7_jose.csv")
h1 = j[j.hypothesis == "H1"]


def h1_p(model, hurricane):
    r = h1[(h1.model == model) & (h1.subset == hurricane)]
    return float(r["p"].iloc[0]) if len(r) else float("nan")


def stars(p):
    if np.isnan(p):
        return ""
    return "***" if p < 1e-3 else "**" if p < 1e-2 else "*" if p < 0.05 else "ns"


def stats(col):
    """(source, hurricane) -> (mean, ci95, n)."""
    out = {}
    for s in SOURCES:
        for h in HURRICANES:
            v = m[(m.source_group == s) & (m.hurricane == h)][col].dropna().values
            if len(v) == 0:
                continue
            mean = float(np.mean(v))
            ci = 1.96 * float(np.std(v, ddof=1)) / np.sqrt(len(v)) if len(v) > 1 else 0.0
            out[(s, h)] = (mean, ci, len(v))
    return out


def plot(col, model, fname):
    st = stats(col)
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    width = 0.26
    offsets = {"Facebook": -width, "Reddit community": 0.0, "White House": width}
    x = np.arange(len(HURRICANES))
    for s in SOURCES:
        xs, means, cis = [], [], []
        for i, h in enumerate(HURRICANES):
            if (s, h) in st:
                mean, ci, n = st[(s, h)]
                xs.append(i + offsets[s]); means.append(mean); cis.append(ci)
        ax.bar(xs, means, width, yerr=cis, capsize=3, color=COLORS[s], label=s,
               edgecolor="white", error_kw=dict(lw=1))
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels([h.capitalize() for h in HURRICANES])
    ax.set_ylabel(f"Mean {'VADER compound' if model == 'VADER' else 'RoBERTa (pos - neg)'}")
    ax.set_title(f"Mean sentiment by source and hurricane ({model}, comment-level)")
    ax.legend(title="Source", loc="upper right", fontsize=9)

    # FB vs Reddit significance bracket per hurricane (H1)
    ymax = max(mean + ci for mean, ci, _ in st.values())
    ymin = min(mean - ci for mean, ci, _ in st.values())
    span = ymax - ymin
    for i, h in enumerate(HURRICANES):
        if ("Facebook", h) not in st or ("Reddit community", h) not in st:
            continue
        x1 = i + offsets["Facebook"]; x2 = i + offsets["Reddit community"]
        top = max(st[("Facebook", h)][0] + st[("Facebook", h)][1],
                  st[("Reddit community", h)][0] + st[("Reddit community", h)][1])
        y = top + span * 0.06
        ax.plot([x1, x1, x2, x2], [y, y + span * 0.02, y + span * 0.02, y], color="black", lw=1)
        ax.text((x1 + x2) / 2, y + span * 0.025, stars(h1_p(model.lower(), h)),
                ha="center", va="bottom", fontsize=10)
    # y-axis: start exactly at 0 when every bar MEAN is positive (VADER) so the
    # baseline sits flush on the axis; otherwise drop below for negative bars (RoBERTa).
    # (Keyed on means, not CIs, so a wide WH error bar doesn't push the axis below 0.)
    means_min = min(mean for mean, _, _ in st.values())
    bottom = 0.0 if means_min >= 0 else ymin - span * 0.08
    ax.set_ylim(bottom, ymax + span * 0.22)
    fig.tight_layout()
    # significance-key caption placed BELOW the axes (not inside the plot area)
    fig.text(0.5, -0.02,
             "FB–Reddit brackets = H1 (per hurricane). *** p<.001   ** p<.01   * p<.05.   "
             "H7 (pooled): WH significantly more negative than both FB and Reddit.",
             ha="center", va="top", fontsize=8, style="italic", color="#555555")
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"{fname}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return st


sv = plot("vader_compound", "VADER", "f3_three_way_vader")
sr = plot("roberta_compound", "RoBERTa", "f3_three_way_roberta")

# ---------------- results doc ----------------
lines = ["# F3 — Three-Way Source Comparison (comment-level)", "",
         "Grouped bars: mean sentiment by source × hurricane, 95% CI error bars, "
         "FB–Reddit significance stars from H1 (per hurricane). WH has no Debby data.",
         "RoBERTa uses continuous `pos - neg`. H7 (WH vs FB / WH vs Reddit) is pooled "
         "across storms — see `hypothesis_tests_all7_jose.csv`.", ""]
for model, st in [("VADER", sv), ("RoBERTa", sr)]:
    lines.append(f"## {model}")
    lines.append("| source | hurricane | n | mean | 95% CI± | FB-vs-Reddit (H1) |")
    lines.append("|---|---|---|---|---|---|")
    for h in HURRICANES:
        pstar = stars(h1_p(model.lower(), h))
        for s in SOURCES:
            if (s, h) in st:
                mean, ci, n = st[(s, h)]
                note = pstar if s == "Reddit community" else ""
                lines.append(f"| {s} | {h} | {n:,} | {mean:+.4f} | {ci:.4f} | {note} |")
    lines.append("")
lines += ["Figures: `figures/f3_three_way_{vader,roberta}.png/.pdf` (300 dpi).", "",
          "Status: **built (VADER + RoBERTa).**"]
(DOCS / "f3_three_way_results.md").write_text("\n".join(lines) + "\n")

print("\n".join(lines))
print("\nWrote figures/f3_three_way_{vader,roberta}.* + docs/week6/f3_three_way_results.md")
