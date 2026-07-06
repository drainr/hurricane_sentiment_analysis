#!/usr/bin/env python3
"""
H2 — Temporal trajectory

H2: "Reddit sentiment will decline more sharply approaching landfall than Facebook,
where Phillips moderates audience anxiety."

Unit = audience comments (Facebook Phillips comments vs Reddit community comments),
which is where audience anxiety shows up. WH government_response comments are added to
the figure where in-window data exists (Milton only).

For each method (VADER compound; RoBERTa compound = pos - neg):
  - OLS  compound ~ days_from_landfall  fit SEPARATELY for Facebook and Reddit
    (slope, p, 95% CI, R^2). A more-negative slope = sentiment worsening toward landfall.
  - Combined interaction model  compound ~ days_from_landfall * platform.
    The interaction term tests H2 directly (do the slopes differ by platform?).
  - Per-hurricane slopes for context.

Outputs:
  docs/h2_temporal_results.md
  figures/h2_temporal_curves.png / .pdf   (3 panels, one per hurricane)

Reads the canonical processed/*_labeled.csv files. Read-only on inputs.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "data" / "processed"
DOCS = REPO / "docs"
FIGS = REPO / "figures"
FIGS.mkdir(exist_ok=True)

WINDOWS = {"debby": (-5, 0), "helene": (-4, 1), "milton": (-5, 0)}
HURRICANES = ["debby", "helene", "milton"]
COLORS = {"facebook": "#1f77b4", "reddit": "#ff7f0e", "whitehouse": "#2ca02c"}


def load(name):
    df = pd.read_csv(PROC / name, low_memory=False)
    df["hurricane"] = df["hurricane"].str.lower()
    df["days_from_landfall"] = pd.to_numeric(df["days_from_landfall"], errors="coerce")
    df["vader_compound"] = pd.to_numeric(df["vader_compound"], errors="coerce")
    # RoBERTa continuous score
    df["roberta_compound"] = (pd.to_numeric(df["roberta_pos"], errors="coerce")
                              - pd.to_numeric(df["roberta_neg"], errors="coerce"))
    return df


def in_window(df):
    keep = pd.Series(False, index=df.index)
    for h, (lo, hi) in WINDOWS.items():
        keep |= (df["hurricane"] == h) & df["days_from_landfall"].between(lo, hi)
    return df[keep].copy()


fb = in_window(load("facebook_comments_vader_roberta_topics_labeled.csv"))
rd = in_window(load("reddit_relevant_comments_vader_roberta_topics_labeled.csv"))
wh = load("whitehouse_threads_comments_vader_roberta_topics_labeled.csv")
fb["platform"] = "facebook"
rd["platform"] = "reddit"

lines = ["# H2 — Temporal Trajectory Results", "",
         "Unit: audience comments. Facebook = Phillips comments; Reddit = community_discussion comments.",
         "Compound scores in event windows (Debby -5..0, Helene -4..+1, Milton -5..0).",
         f"N: Facebook comments = {len(fb):,}; Reddit community comments = {len(rd):,}.", ""]


def ols_one(df, ycol, label):
    m = smf.ols(f"{ycol} ~ days_from_landfall", data=df).fit()
    b = m.params["days_from_landfall"]
    p = m.pvalues["days_from_landfall"]
    lo, hi = m.conf_int().loc["days_from_landfall"]
    return dict(label=label, n=int(m.nobs), slope=b, p=p, ci=(lo, hi), r2=m.rsquared)


def report_method(ycol, method):
    lines.append(f"## {method}")
    lines.append("")
    # separate slopes
    res_fb = ols_one(fb, ycol, "Facebook")
    res_rd = ols_one(rd, ycol, "Reddit")
    lines.append("| platform | N | slope (per day toward +) | 95% CI | p | R^2 |")
    lines.append("|---|---|---|---|---|---|")
    for r in (res_fb, res_rd):
        lines.append(f"| {r['label']} | {r['n']:,} | {r['slope']:+.5f} | "
                     f"[{r['ci'][0]:+.5f}, {r['ci'][1]:+.5f}] | {r['p']:.2e} | {r['r2']:.4f} |")
    lines.append("")
    # interaction model
    both = pd.concat([fb[[ycol, "days_from_landfall", "platform"]],
                      rd[[ycol, "days_from_landfall", "platform"]]], ignore_index=True)
    m = smf.ols(f"{ycol} ~ days_from_landfall * C(platform, Treatment('facebook'))", data=both).fit()
    # interaction term name
    iname = [c for c in m.params.index if "days_from_landfall:" in c][0]
    ib, ip = m.params[iname], m.pvalues[iname]
    ici = m.conf_int().loc[iname]
    # H2 predicts Reddit declines MORE steeply approaching landfall than FB,
    # i.e. Reddit slope < FB slope -> interaction (Reddit-FB) significantly NEGATIVE.
    if ip >= 0.05:
        verdict = "no significant slope difference between platforms ⇒ H2 NOT supported"
    elif ib < 0:
        verdict = "Reddit slope significantly more negative than Facebook ⇒ supports H2"
    else:
        verdict = ("Reddit slope significantly more POSITIVE than Facebook (Reddit declines "
                   "LESS / rises) ⇒ H2 NOT supported; runs opposite to the prediction")
    lines.append(f"**Interaction (Reddit slope − Facebook slope):** {ib:+.5f} "
                 f"[{ici[0]:+.5f}, {ici[1]:+.5f}], p = {ip:.2e} → {verdict}.")
    lines.append(f"  (Facebook slope {res_fb['slope']:+.5f}, Reddit slope {res_rd['slope']:+.5f}; "
                 f"R² ≈ {res_fb['r2']:.4f}/{res_rd['r2']:.4f} — the linear day-effect is very weak either way.)")
    lines.append("")
    # per-hurricane slopes
    lines.append("Per-hurricane slopes:")
    lines.append("")
    lines.append("| hurricane | FB slope (p) | Reddit slope (p) |")
    lines.append("|---|---|---|")
    for h in HURRICANES:
        f1 = ols_one(fb[fb.hurricane == h], ycol, h) if (fb.hurricane == h).any() else None
        r1 = ols_one(rd[rd.hurricane == h], ycol, h) if (rd.hurricane == h).any() else None
        fc = f"{f1['slope']:+.5f} ({f1['p']:.1e})" if f1 else "—"
        rc = f"{r1['slope']:+.5f} ({r1['p']:.1e})" if r1 else "—"
        lines.append(f"| {h} | {fc} | {rc} |")
    lines.append("")
    return res_fb, res_rd, (ib, ip)


vader_res = report_method("vader_compound", "VADER (compound)")
roberta_res = report_method("roberta_compound", "RoBERTa (pos − neg)")

# cross-method agreement note
lines.append("## VADER vs RoBERTa cross-check")
lines.append("")
agree_dir = (np.sign(vader_res[2][0]) == np.sign(roberta_res[2][0]))
lines.append(f"- Interaction sign agrees across methods: {'YES' if agree_dir else 'NO'} "
             f"(VADER {vader_res[2][0]:+.5f} p={vader_res[2][1]:.1e}; "
             f"RoBERTa {roberta_res[2][0]:+.5f} p={roberta_res[2][1]:.1e}).")
lines.append("- Both methods give a **positive** Reddit−Facebook interaction, i.e. Reddit does NOT "
             "decline more steeply than Facebook over the window — **H2 is not supported** in the "
             "pooled linear model (and R² is ~0, so the linear day-trend is weak for both).")
lines.append("- The picture is storm-dependent (see per-hurricane tables): Debby shows a Facebook "
             "decline, Helene a sharp Reddit decline, Milton a rise on both — so a single pooled "
             "slope conflates approach and post-landfall recovery (Helene/Milton windows include day +1 / day 0).")
lines.append("")

# -------- in-window WH comment counts per hurricane (the F2 green squares) --------
# WH government_response comments are only added to the figure where they fall inside
# a storm's event window. Emit the per-day counts so the plotted N is explicit/traceable.
wh["hurricane"] = wh["hurricane"].str.lower()
wh["days_from_landfall"] = pd.to_numeric(wh["days_from_landfall"], errors="coerce")
lines.append("## In-window White House comments (plotted on F2)")
lines.append("")
print("\nIn-window WH comment counts (the F2 green squares):")
for h in HURRICANES:
    lo, hi = WINDOWS[h]
    sub = wh[(wh.hurricane == h) & wh.days_from_landfall.between(lo, hi)]
    days = sub["days_from_landfall"].value_counts().sort_index()
    if len(sub):
        by_day = ", ".join(f"day {int(d)}: {int(n)}" for d, n in days.items())
        msg = f"{h.capitalize()} window {(lo, hi)}: {len(sub)} in-window ({by_day})"
    else:
        msg = f"{h.capitalize()} window {(lo, hi)}: 0 in-window (WH activity outside window)"
    print("  " + msg)
    lines.append(f"- {msg}")
lines.append("")

# -------- figure: 3 panels, mean compound by day with 95% CI --------
def daily(df, ycol, h, lo, hi):
    sub = df[(df.hurricane == h) & df.days_from_landfall.between(lo, hi)]
    g = sub.groupby("days_from_landfall")[ycol]
    mean = g.mean()
    sem = g.sem()
    return mean.index.values, mean.values, (1.96 * sem).values


for ycol, suffix, mlabel in [("vader_compound", "", "VADER"),
                             ("roberta_compound", "_roberta", "RoBERTa (pos−neg)")]:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    for ax, h in zip(axes, HURRICANES):
        lo, hi = WINDOWS[h]
        for src, df in [("facebook", fb), ("reddit", rd)]:
            x, y, e = daily(df, ycol, h, lo, hi)
            if len(x):
                ax.plot(x, y, "-o", color=COLORS[src], label=src.capitalize(), lw=2, ms=4)
                ax.fill_between(x, y - e, y + e, color=COLORS[src], alpha=0.15)
        # WH where in-window data exists
        xw, yw, ew = daily(wh, ycol, h, lo, hi)
        if len(xw):
            ax.plot(xw, yw, "-s", color=COLORS["whitehouse"], label="White House", lw=2, ms=4)
            ax.fill_between(xw, yw - ew, yw + ew, color=COLORS["whitehouse"], alpha=0.15)
        ax.axvline(0, ls="--", color="gray", lw=1)
        ax.axhline(0, ls=":", color="lightgray", lw=0.8)
        ax.set_title(h.capitalize())
        ax.set_xlabel("Days from landfall")
    axes[0].set_ylabel(f"Mean {mlabel} compound")
    axes[0].legend(loc="best", fontsize=9)
    fig.suptitle(f"H2 — Temporal sentiment trajectory ({mlabel}), 95% CI shading", y=1.02)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"h2_temporal_curves{suffix}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)

lines.append("## Figures")
lines.append("- `figures/h2_temporal_curves.png/.pdf` (VADER) — 3 panels, FB+Reddit all panels, WH on Milton only.")
lines.append("- `figures/h2_temporal_curves_roberta.png/.pdf` (RoBERTa cross-check).")
lines.append("- Note: in-window WH comments exist only for Milton (day 0 only — the 140 government_response "
             "comments on landfall day; the other 90 WH Milton comments fall on days 1–7, post-landfall and "
             "outside the −5..0 window, so they are correctly clipped from this figure). "
             "Helene WH activity is outside the −4..+1 window.")

(DOCS / "h2_temporal_results.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
print("\nWrote docs/h2_temporal_results.md and figures/h2_temporal_curves*.{png,pdf}")
