#!/usr/bin/env python3
"""
Formal Week-5 statistical results table: 7 hypotheses x 2 methods, with explicit
test statistic / p-value / effect-size columns (plan deliverable #1).

Adds the omnibus Kruskal-Wallis effect size epsilon^2 = (H - k + 1)/(n - k) for
H4 and H5, which the per-test docs reported only as pairwise rank-biserial.

Reuses the same processed files as the other Week-5 scripts. Read-only.
Writes docs/week5/statistical_results_table.md.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import mannwhitneyu, kruskal, levene, chi2_contingency

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "data" / "processed"
OUT = REPO / "docs" / "week5" / "statistical_results_table.md"
OUT.parent.mkdir(parents=True, exist_ok=True)
ROBERTA_MAP = {"NEG": "negative", "NEU": "neutral", "NEUTRAL": "neutral", "POS": "positive"}
HUR = ["debby", "helene", "milton"]


def load(name):
    d = pd.read_csv(PROC / name, low_memory=False)
    d["hurricane"] = d["hurricane"].str.lower()
    d["vader_compound"] = pd.to_numeric(d["vader_compound"], errors="coerce")
    d["roberta_compound"] = pd.to_numeric(d["roberta_pos"], errors="coerce") - pd.to_numeric(d["roberta_neg"], errors="coerce")
    d["roberta_label"] = d["roberta_label"].map(ROBERTA_MAP).fillna(d["roberta_label"])
    return d


fb = load("facebook_comments_vader_roberta_topics_labeled.csv")
rd = load("reddit_relevant_comments_vader_roberta_topics_labeled.csv")
wh = load("whitehouse_threads_comments_vader_roberta_topics_labeled.csv")

TIERS = {"expert": ["TropicalWeather", "hurricane", "HurricaneHelene"],
         "local": ["tampa", "sarasota", "asheville"],
         "statewide": ["florida", "Georgia", "NorthCarolina"]}
S2T = {s: t for t, subs in TIERS.items() for s in subs}
rd["tier"] = rd["subreddit"].map(S2T)


def rank_biserial(x, y):
    U, p = mannwhitneyu(x, y, alternative="two-sided")
    return U, p, 2 * U / (len(x) * len(y)) - 1


def kw_eps2(groups):
    H, p = kruskal(*groups)
    n = sum(len(g) for g in groups)
    k = len(groups)
    eps2 = (H - k + 1) / (n - k)
    return H, p, eps2


rows = []  # (H, method, test, statistic, p, effect_size)


def add(hlabel, method, test, stat, p, eff):
    pstr = "—" if p is None else ("<1e-300" if p == 0 else f"{p:.2e}")
    rows.append((hlabel, method, test, stat, pstr, eff))


for method, col in [("VADER", "vader_compound"), ("RoBERTa", "roberta_compound")]:
    lab = "vader_label" if method == "VADER" else "roberta_label"
    # H1 overall MWU + chi2
    U, p, r = rank_biserial(fb[col].dropna().values, rd[col].dropna().values)
    add("H1 platform (overall)", method, "Mann-Whitney U", f"U={U:.3g}", p, f"rank-biserial {r:+.3f}")
    tab = pd.crosstab(pd.Series(["FB"]*len(fb)+["RD"]*len(rd)), pd.concat([fb[lab], rd[lab]], ignore_index=True))
    chi2, pc, dof, _ = chi2_contingency(tab)
    V = np.sqrt(chi2 / (tab.values.sum() * (min(tab.shape)-1)))
    add("H1 platform×label", method, "Chi-square", f"χ²({dof})={chi2:.0f}", pc, f"Cramér's V {V:.3f}")
    # H2 interaction
    both = pd.concat([fb[[col, "days_from_landfall"]].assign(plat="fb"),
                      rd[[col, "days_from_landfall"]].assign(plat="rd")], ignore_index=True)
    m = smf.ols(f"{col} ~ days_from_landfall * C(plat, Treatment('fb'))", data=both).fit()
    iname = [c for c in m.params.index if "days_from_landfall:" in c][0]
    add("H2 temporal (interaction)", method, "OLS interaction", f"β={m.params[iname]:+.5f}", m.pvalues[iname], f"R²={m.rsquared:.4f}")
    # H3 descriptive
    gaps = {h: fb[fb.hurricane==h][col].mean()-rd[rd.hurricane==h][col].mean() for h in HUR}
    add("H3 intensity gap", method, "Descriptive (gap order)", f"gaps D/H/M={gaps['debby']:.3f}/{gaps['helene']:.3f}/{gaps['milton']:.3f}", None, "Debby not smallest → n.s.")
    # H4 KW within each platform
    for plat, df in [("Reddit", rd), ("Facebook", fb)]:
        H, p, e = kw_eps2([df[df.hurricane==h][col].dropna().values for h in HUR])
        add(f"H4 cross-storm ({plat})", method, "Kruskal-Wallis", f"H={H:.1f}", p, f"ε²={e:.4f}")
    # H5 KW per storm (full data)
    for h in HUR:
        d = rd[rd.hurricane==h]
        H, p, e = kw_eps2([d[d.tier==t][col].dropna().values for t in TIERS])
        add(f"H5 tiers ({h})", method, "Kruskal-Wallis", f"H={H:.1f}", p, f"ε²={e:.4f}")
    # H7 three comparisons
    U, p, r = rank_biserial(wh[col].dropna().values, rd[col].dropna().values)
    W, pl = levene(wh[col].dropna(), rd[col].dropna())
    add("H7 WH vs Reddit", method, "MWU (+ Levene)", f"U={U:.3g}; Levene W={W:.1f} (p={pl:.1e})", p, f"rank-biserial {r:+.3f}")
    U, p, r = rank_biserial(wh[col].dropna().values, fb[col].dropna().values)
    add("H7 WH vs FB", method, "Mann-Whitney U", f"U={U:.3g}", p, f"rank-biserial {r:+.3f}")
    pol = wh["text"].fillna("").str.lower().str.contains("fema|biden|trump|government|conspiracy")
    U, p, r = rank_biserial(wh[pol][col].dropna().values, wh[~pol][col].dropna().values)
    add("H7 WH political vs not", method, "Mann-Whitney U", f"U={U:.3g}", p, f"rank-biserial {r:+.3f}")

lines = ["# Statistical Results Table — 7 hypotheses × 2 methods (Week 5)", "",
         "Formal companion to `statistical_results_summary.md`. Comment-level; FB=Phillips, "
         "Reddit=community, WH=government_response. Effect sizes: rank-biserial (MWU), Cramér's V "
         "(χ²), ε² (Kruskal-Wallis omnibus; small≈0.01, medium≈0.06, large≈0.14), R²/β (OLS). "
         "Note: at n=60k–120k, p-values are near-zero everywhere — **effect sizes are the meaningful column.**",
         "",
         "| Hypothesis / test | Method | Test | Statistic | p | Effect size |",
         "|---|---|---|---|---|---|"]
for hlabel, method, test, stat, p, eff in rows:
    lines.append(f"| {hlabel} | {method} | {test} | {stat} | {p} | {eff} |")
OUT.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
print(f"\nWrote {OUT}")
