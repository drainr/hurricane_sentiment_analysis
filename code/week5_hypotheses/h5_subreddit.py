#!/usr/bin/env python3
"""
H5 — Subreddit-tier sentiment differences.

Tiers (all 9 community subreddits; WH/excluded subs are NOT here):
expert    = TropicalWeather, hurricane, HurricaneHelene
local     = tampa, sarasota, asheville
statewide = florida, Georgia, NorthCarolina
Comment-level, each hurricane separately.

  Step 1: Kruskal-Wallis across the 3 tiers, once on VADER compound, once on RoBERTa
          (pos-neg). If significant -> pairwise Mann-Whitney U + Bonferroni (x3).
  Step 2 (always, all 3 hurricanes): exclude the single largest thread (by comment
          count) in EACH subreddit and re-run, to check no one thread drives the
          tier averages. Report 4 versions: VADER full / VADER excl / RoBERTa full /
          RoBERTa excl, side by side, with method-agreement + exclusion-effect lines.

Outputs docs/week5/h5_subreddit_results.md + figures/h5_subreddit_box.png/.pdf.
Read-only on inputs.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import kruskal, mannwhitneyu
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[2]
PROC = REPO / "data" / "processed"
DOCS = REPO / "docs" / "week5"
DOCS.mkdir(parents=True, exist_ok=True)
FIGS = REPO / "figures"

TIERS = {
    "expert":    ["TropicalWeather", "hurricane", "HurricaneHelene"],
    "local":     ["tampa", "sarasota", "asheville"],
    "statewide": ["florida", "Georgia", "NorthCarolina"],
}
SUB2TIER = {s: t for t, subs in TIERS.items() for s in subs}
TIER_ORDER = ["expert", "local", "statewide"]
HURRICANES = ["debby", "helene", "milton"]
ALPHA = 0.05

rc = pd.read_csv(PROC / "reddit_relevant_comments_vader_roberta_topics_labeled.csv", low_memory=False)
rc["hurricane"] = rc["hurricane"].str.lower()
rc["vader_compound"] = pd.to_numeric(rc["vader_compound"], errors="coerce")
rc["roberta_compound"] = (pd.to_numeric(rc["roberta_pos"], errors="coerce")
                          - pd.to_numeric(rc["roberta_neg"], errors="coerce"))
rc["tier"] = rc["subreddit"].map(SUB2TIER)
assert rc["tier"].notna().all(), f"unmapped subreddits: {rc[rc.tier.isna()].subreddit.unique()}"

METHODS = [("VADER", "vader_compound"), ("RoBERTa", "roberta_compound")]


def largest_thread_ids(df):
    """For each subreddit in df, the parent_post_id with the most comments. Returns set of thread ids."""
    ids = set()
    for sub, g in df.groupby("subreddit"):
        counts = g["parent_post_id"].value_counts()
        if len(counts):
            ids.add(counts.index[0])
    return ids


def run_tests(df, col):
    """KW across tiers (with data) + pairwise MWU Bonferroni if significant. Returns dict."""
    groups = {t: df[df.tier == t][col].dropna().values for t in TIER_ORDER}
    present = {t: v for t, v in groups.items() if len(v) > 0}
    ns = {t: len(v) for t, v in groups.items()}
    means = {t: (float(np.mean(v)) if len(v) else float("nan")) for t, v in groups.items()}
    if len(present) < 2:
        return dict(H=float("nan"), p=float("nan"), ns=ns, means=means, pairwise=None, k=len(present))
    H, p = kruskal(*present.values())
    pairwise = None
    if p < ALPHA:
        pairwise = {}
        tiers_p = list(present.keys())
        pairs = [(a, b) for i, a in enumerate(tiers_p) for b in tiers_p[i + 1:]]
        m = len(pairs)
        for a, b in pairs:
            U, pu = mannwhitneyu(present[a], present[b], alternative="two-sided")
            rrb = 2 * U / (len(present[a]) * len(present[b])) - 1
            pairwise[f"{a} vs {b}"] = (min(pu * m, 1.0), rrb)
    return dict(H=H, p=p, ns=ns, means=means, pairwise=pairwise, k=len(present))


lines = ["# H5 — Subreddit-Tier Differences (Student B)", "",
         "Tiers (Tania 2026-06-30): "
         "**expert**=TropicalWeather/hurricane/HurricaneHelene, "
         "**local**=tampa/sarasota/asheville, "
         "**statewide**=florida/Georgia/NorthCarolina. Comment-level, per hurricane.",
         "",
         "**Data-integrity confirmation for Tania:** the four excluded subs "
         "(r/southcarolina, r/Tennessee, r/Virginia, r/pics) appear in **0 rows** of the H5 corpus "
         "(`reddit_relevant_comments`); they exist only in the White House files, all tagged "
         "`government_response` (558 comments) — i.e. purely WH-reaction data in the H7 lane, "
         "nothing organic swept in.",
         ""]

# overall corpus sizes
lines.append("Corpus (community comments): "
             + ", ".join(f"{t} n={int((rc.tier==t).sum()):,}" for t in TIER_ORDER) + ".")
lines.append("")

results = {}  # (hurricane, method, variant) -> dict
h5_rows = []  # CSV rows for the combined 7-hypothesis results file
for h in HURRICANES:
    dfh = rc[rc.hurricane == h]
    thread_ids = largest_thread_ids(dfh)
    dfh_excl = dfh[~dfh["parent_post_id"].isin(thread_ids)]
    excluded_n = len(dfh) - len(dfh_excl)
    lines.append(f"## {h.capitalize()}")
    lines.append(f"Comments: {len(dfh):,}. Largest-thread-per-subreddit exclusion removes "
                 f"{excluded_n:,} comments across {len(thread_ids)} threads.")
    lines.append("")
    lines.append("| method | variant | n expert | n local | n statewide | KW H | p | significant? | pairwise (Bonferroni) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for method, col in METHODS:
        for variant, d in [("full data", dfh), ("largest thread excl.", dfh_excl)]:
            r = run_tests(d, col)
            results[(h, method, variant)] = r
            vtag = "full" if variant == "full data" else "excl_largest_thread"
            if not np.isnan(r["H"]):
                h5_rows.append(dict(hypothesis="H5", model=method.lower(), hurricane=h,
                                    variant=vtag, test="kruskal_wallis", stat=r["H"], p=r["p"]))
            if r["pairwise"]:
                for pair, (pbonf, rrb) in r["pairwise"].items():
                    a, b = pair.split(" vs ")
                    h5_rows.append(dict(hypothesis="H5", model=method.lower(), hurricane=h,
                                        variant=vtag, test="pairwise_mann_whitney",
                                        group_a=a, group_b=b, p_bonferroni=pbonf, rank_biserial=rrb))
            sig = "—" if np.isnan(r["p"]) else ("YES" if r["p"] < ALPHA else "no")
            pw = ""
            if r["pairwise"]:
                pw = "; ".join(f"{k}: p={v[0]:.1e}, r={v[1]:+.2f}" for k, v in r["pairwise"].items())
            elif sig == "no":
                pw = "n/a (KW n.s.)"
            pstr = "nan" if np.isnan(r["p"]) else f"{r['p']:.2e}"
            Hstr = "nan" if np.isnan(r["H"]) else f"{r['H']:.1f}"
            lines.append(f"| {method} | {variant} | {r['ns']['expert']:,} | {r['ns']['local']:,} "
                         f"| {r['ns']['statewide']:,} | {Hstr} | {pstr} | {sig} | {pw} |")
    # tier means for context (full data, both methods)
    rv = results[(h, "VADER", "full data")]["means"]
    rr = results[(h, "RoBERTa", "full data")]["means"]
    lines.append("")
    lines.append(f"Tier means (full data): VADER "
                 + ", ".join(f"{t}={rv[t]:.3f}" for t in TIER_ORDER if not np.isnan(rv[t]))
                 + "; RoBERTa "
                 + ", ".join(f"{t}={rr[t]:.3f}" for t in TIER_ORDER if not np.isnan(rr[t])) + ".")
    # agreement + exclusion-effect summary lines
    def verdict(method):
        full = results[(h, method, "full data")]["p"]
        excl = results[(h, method, "largest thread excl.")]["p"]
        sf = (not np.isnan(full)) and full < ALPHA
        se = (not np.isnan(excl)) and excl < ALPHA
        return sf, se
    vf, ve = verdict("VADER")
    rf, re_ = verdict("RoBERTa")
    methods_agree = (vf == rf)
    excl_changes = (vf != ve) or (rf != re_)
    lines.append(f"- **VADER vs RoBERTa agree on significance:** {'YES' if methods_agree else 'NO'} "
                 f"(VADER full {'sig' if vf else 'n.s.'}, RoBERTa full {'sig' if rf else 'n.s.'}).")
    lines.append(f"- **Excluding the largest thread changes the verdict:** {'YES — FLAG' if excl_changes else 'no'} "
                 f"(VADER {'sig' if vf else 'n.s.'}→{'sig' if ve else 'n.s.'}, "
                 f"RoBERTa {'sig' if rf else 'n.s.'}→{'sig' if re_ else 'n.s.'}).")
    if not methods_agree or excl_changes:
        lines.append("  - ⚠ **Flag for Tania before paper** (method disagreement or exclusion-sensitive).")
    lines.append("")

# ---------------- figure: box plots of compound by tier, per hurricane (VADER) ----------------
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
tier_colors = {"expert": "#9467bd", "local": "#ff7f0e", "statewide": "#1f77b4"}
for ax, h in zip(axes, HURRICANES):
    dfh = rc[rc.hurricane == h]
    data = [dfh[dfh.tier == t]["vader_compound"].dropna().values for t in TIER_ORDER]
    bp = ax.boxplot(data, tick_labels=TIER_ORDER, showfliers=False, patch_artist=True, showmeans=True)
    for patch, t in zip(bp["boxes"], TIER_ORDER):
        patch.set_facecolor(tier_colors[t]); patch.set_alpha(0.5)
    ax.axhline(0, ls=":", color="gray", lw=0.8)
    ax.set_title(h.capitalize())
axes[0].set_ylabel("VADER compound")
fig.suptitle("H5 — Sentiment by subreddit tier (VADER compound), per hurricane", y=1.02)
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(FIGS / f"h5_subreddit_box.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)

lines.append("## Figure")
lines.append("- `figures/h5_subreddit_box.png/.pdf` — box plots of VADER compound by tier, per hurricane.")

(DOCS / "h5_subreddit_results.md").write_text("\n".join(lines) + "\n")

pd.DataFrame(h5_rows).to_csv(REPO / "data" / "merged" / "h5_results_jose.csv", index=False)

print("\n".join(lines))
print("\nWrote docs/week5/h5_subreddit_results.md + figures/h5_subreddit_box.*")
print(f"Wrote data/merged/h5_results_jose.csv ({len(h5_rows)} rows)")
