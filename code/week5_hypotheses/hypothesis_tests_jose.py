#!/usr/bin/env python3
"""
Hypothesis tests H1, H3, H4, H7 on BOTH methods (VADER + RoBERTa) — Week 5.

H2 lives in h2_temporal.py; H5 lives in h5_subreddit.py.
H1/H3/H4/H7 mirror Student A's (Angelo's) owned hypotheses; computed here for the
required 7-hypothesis x 2-method results table and the RoBERTa cross-check duty.

Unit: comments. Facebook = Phillips comments; Reddit community = community_discussion;
White House = government_response comments.

Outputs docs/hypothesis_tests_results.md (consumed by statistical_results_summary.md).
Read-only on inputs.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, kruskal, levene, chi2_contingency

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "data" / "processed"
OUT = REPO / "docs" / "hypothesis_tests_results.md"

ROBERTA_MAP = {"NEG": "negative", "NEU": "neutral", "NEUTRAL": "neutral", "POS": "positive",
               "negative": "negative", "neutral": "neutral", "positive": "positive"}
HURRICANES = ["debby", "helene", "milton"]
METHODS = [("VADER", "vader_compound"), ("RoBERTa", "roberta_compound")]


def load(name):
    df = pd.read_csv(PROC / name, low_memory=False)
    df["hurricane"] = df["hurricane"].str.lower()
    df["vader_compound"] = pd.to_numeric(df["vader_compound"], errors="coerce")
    df["roberta_compound"] = (pd.to_numeric(df["roberta_pos"], errors="coerce")
                              - pd.to_numeric(df["roberta_neg"], errors="coerce"))
    df["vader_label"] = df["vader_label"]
    df["roberta_label"] = df["roberta_label"].map(ROBERTA_MAP)
    return df


fb = load("facebook_comments_vader_roberta_topics_labeled.csv")
rd = load("reddit_relevant_comments_vader_roberta_topics_labeled.csv")
wh = load("whitehouse_threads_comments_vader_roberta_topics_labeled.csv")


def mwu(x, y):
    """Mann-Whitney U (two-sided) + rank-biserial effect size (positive => x stochastically > y)."""
    x = pd.Series(x).dropna().values
    y = pd.Series(y).dropna().values
    if len(x) == 0 or len(y) == 0:
        return None
    U, p = mannwhitneyu(x, y, alternative="two-sided")
    rrb = 2 * U / (len(x) * len(y)) - 1   # rank-biserial
    return dict(U=U, p=p, rrb=rrb, n1=len(x), n2=len(y), m1=np.mean(x), m2=np.mean(y))


lines = ["# Hypothesis Tests — H1, H3, H4, H7 (VADER + RoBERTa)", "",
         "Comments only. FB=Phillips, Reddit=community_discussion, WH=government_response.",
         "Effect size = rank-biserial (MWU); positive ⇒ first group scores higher.", ""]

# ===================== H1 — platform difference =====================
lines += ["## H1 — FB (Phillips) vs Reddit community compound", "",
          "Prediction: Reddit shows significantly LOWER compound than Facebook.", ""]
for method, col in METHODS:
    lines.append(f"### {method}")
    lines.append("| scope | n(FB) | n(Reddit) | mean FB | mean Reddit | U | p | rank-biserial |")
    lines.append("|---|---|---|---|---|---|---|---|")
    r = mwu(fb[col], rd[col])
    lines.append(f"| overall | {r['n1']:,} | {r['n2']:,} | {r['m1']:.3f} | {r['m2']:.3f} | "
                 f"{r['U']:.0f} | {r['p']:.2e} | {r['rrb']:+.3f} |")
    for h in HURRICANES:
        rh = mwu(fb[fb.hurricane == h][col], rd[rd.hurricane == h][col])
        lines.append(f"| {h} | {rh['n1']:,} | {rh['n2']:,} | {rh['m1']:.3f} | {rh['m2']:.3f} | "
                     f"{rh['U']:.0f} | {rh['p']:.2e} | {rh['rrb']:+.3f} |")
    # chi-square platform x label
    lab = "vader_label" if method == "VADER" else "roberta_label"
    tab = pd.crosstab(
        pd.concat([pd.Series(["FB"] * len(fb)), pd.Series(["Reddit"] * len(rd))], ignore_index=True),
        pd.concat([fb[lab], rd[lab]], ignore_index=True))
    chi2, p, dof, _ = chi2_contingency(tab)
    n = tab.values.sum()
    V = np.sqrt(chi2 / (n * (min(tab.shape) - 1)))
    lines.append(f"\nChi-square platform×{lab}: χ²({dof})={chi2:.1f}, p={p:.2e}, Cramér's V={V:.3f}.\n")

# ===================== H3 — storm-intensity gap =====================
lines += ["## H3 — FB−Reddit compound gap by storm (Debby < Helene, Debby < Milton)", ""]
for method, col in METHODS:
    gaps = {h: fb[fb.hurricane == h][col].mean() - rd[rd.hurricane == h][col].mean() for h in HURRICANES}
    cond = (gaps["debby"] < gaps["helene"]) and (gaps["debby"] < gaps["milton"])
    lines.append(f"### {method}")
    lines.append("| gap_debby | gap_helene | gap_milton | Debby smallest? |")
    lines.append("|---|---|---|---|")
    lines.append(f"| {gaps['debby']:.3f} | {gaps['helene']:.3f} | {gaps['milton']:.3f} | "
                 f"{'YES → supports H3' if cond else 'NO → not supported'} |")
    lines.append("")

# ===================== H4 — sequential exposure (within platform) =====================
lines += ["## H4 — Cross-storm differences within each platform (Kruskal-Wallis)", "",
          "Prediction: Reddit accumulates negativity across the sequence while FB stays stable.", ""]
for method, col in METHODS:
    lines.append(f"### {method}")
    for plat, df in [("Reddit community", rd), ("Facebook", fb)]:
        groups = [df[df.hurricane == h][col].dropna().values for h in HURRICANES]
        H, p = kruskal(*groups)
        means = {h: df[df.hurricane == h][col].mean() for h in HURRICANES}
        lines.append(f"- **{plat}**: KW H={H:.1f}, p={p:.2e}; means "
                     f"debby={means['debby']:.3f}, helene={means['helene']:.3f}, milton={means['milton']:.3f}.")
        if p < 0.05:
            # pairwise MWU + Bonferroni (3 comparisons)
            pairs = [("debby", "helene"), ("debby", "milton"), ("helene", "milton")]
            parts = []
            for a, b in pairs:
                rr = mwu(df[df.hurricane == a][col], df[df.hurricane == b][col])
                parts.append(f"{a}vs{b} p={min(rr['p']*3,1):.1e} (r={rr['rrb']:+.2f})")
            lines.append(f"  - pairwise (Bonferroni×3): " + "; ".join(parts))
    lines.append("")

# ===================== H7 — government communication =====================
lines += ["## H7 — White House thread comments polarization", "",
          "(1) WH vs Reddit community, (2) WH vs FB Phillips, (3) within WH political vs non-political.", ""]
POL = ["fema", "biden", "trump", "government", "conspiracy"]
wh["_pol"] = wh["text"].fillna("").str.lower().str.contains("|".join(POL))
for method, col in METHODS:
    lines.append(f"### {method}")
    # (1) WH vs Reddit + Levene's for variance/polarization
    r1 = mwu(wh[col], rd[col])
    W, pv = levene(wh[col].dropna(), rd[col].dropna())
    lines.append(f"- **WH vs Reddit community**: MWU U={r1['U']:.0f}, p={r1['p']:.2e}, r={r1['rrb']:+.3f} "
                 f"(mean WH={r1['m1']:.3f}, Reddit={r1['m2']:.3f}); "
                 f"variance SD WH={wh[col].std():.3f} vs Reddit={rd[col].std():.3f}, "
                 f"Levene W={W:.1f}, p={pv:.2e}.")
    # (2) WH vs FB
    r2 = mwu(wh[col], fb[col])
    lines.append(f"- **WH vs FB Phillips**: MWU U={r2['U']:.0f}, p={r2['p']:.2e}, r={r2['rrb']:+.3f} "
                 f"(mean WH={r2['m1']:.3f}, FB={r2['m2']:.3f}).")
    # (3) within WH political vs not
    r3 = mwu(wh[wh._pol][col], wh[~wh._pol][col])
    lines.append(f"- **Within WH, political-keyword vs not** ({int(wh._pol.sum())} vs {int((~wh._pol).sum())}): "
                 f"MWU U={r3['U']:.0f}, p={r3['p']:.2e}, r={r3['rrb']:+.3f} "
                 f"(mean political={r3['m1']:.3f}, non={r3['m2']:.3f}).")
    lines.append("")

OUT.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
print(f"\nWrote {OUT}")
