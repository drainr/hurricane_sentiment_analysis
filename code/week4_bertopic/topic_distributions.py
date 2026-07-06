"""
topic_distributions.py
Week 4 cross-source topic analysis, read from master_vader_roberta_topics.csv.

Produces:
  - data/merged/topic_dist_by_source_type.csv   (proportions)
  - data/merged/topic_dist_by_hurricane.csv      (proportions)
  - data/merged/topic_dist_by_subreddit.csv      (Reddit only, proportions)
  - data/merged/chi_square_results.md            (3 chi-square tests)

Conventions (per Decision Log):
  - source_type axis buckets: facebook (FB rows, source_type NaN),
    community_discussion (organic Reddit), government_response (WH comments).
    government (WH posts, n=12) is too few -> excluded from tests, noted.
  - Cross-source tables use only the NINE shared categories. `excluded`
    (outliers/short) is dropped; the four WH-only categories are structural
    zeros for FB/Reddit and are dropped from the shared comparison.
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MERGED = os.path.join(ROOT, "data", "merged")
MASTER = os.path.join(MERGED, "master_vader_roberta_topics.csv")

SHARED9 = [
    "gratitude", "preparedness", "forecast analysis", "evacuation logistics",
    "political / FEMA criticism", "misinformation", "government resources",
    "personal experience", "emotional response",
]
EXPECTED_MASTER_ROWS = 187359


def cramers_v(cm):
    chi2 = chi2_contingency(cm)[0]
    n = cm.values.sum()
    r, k = cm.shape
    return np.sqrt((chi2 / n) / (min(r - 1, k - 1)))


def chi_block(title, cm, note=""):
    cm = cm.loc[(cm.sum(axis=1) > 0), (cm.sum(axis=0) > 0)]
    chi2, p, dof, _ = chi2_contingency(cm)
    v = cramers_v(cm)
    lines = [f"## {title}", ""]
    if note:
        lines += [f"_{note}_", ""]
    lines += [
        "Contingency table (counts):", "",
        cm.to_markdown(), "",
        f"- chi-square = **{chi2:,.2f}**",
        f"- dof = {dof}",
        f"- p-value = **{p:.3e}**" + ("  (significant at .05)" if p < 0.05 else "  (n.s.)"),
        f"- Cramer's V = **{v:.4f}**",
        "",
    ]
    return "\n".join(lines)


def main():
    m = pd.read_csv(MASTER, low_memory=False)
    assert len(m) == EXPECTED_MASTER_ROWS, f"master row count {len(m)} != {EXPECTED_MASTER_ROWS}"

    # source_type bucket: FB rows have NaN source_type
    m["source_bucket"] = m["source_type"].fillna("facebook")

    # shared-9 frame: drop excluded + WH-only categories
    shared = m[m["topic_category"].isin(SHARED9)].copy()

    # ---- distribution tables (proportions within each group) ----
    def prop_table(df, group):
        ct = pd.crosstab(df["topic_category"], df[group])
        ct = ct.reindex(SHARED9).fillna(0).astype(int)
        prop = ct.div(ct.sum(axis=0), axis=1).round(4)
        return ct, prop

    # by source_type (3 buckets; government n=12 excluded from shared anyway)
    src = shared[shared["source_bucket"].isin(
        ["facebook", "community_discussion", "government_response"])]
    ct_src, prop_src = prop_table(src, "source_bucket")
    prop_src.to_csv(os.path.join(MERGED, "topic_dist_by_source_type.csv"))

    # by hurricane
    ct_hur, prop_hur = prop_table(shared, "hurricane")
    prop_hur.to_csv(os.path.join(MERGED, "topic_dist_by_hurricane.csv"))

    # by subreddit (Reddit community only)
    red = shared[shared["source_bucket"] == "community_discussion"].copy()
    ct_sub, prop_sub = prop_table(red, "subreddit_category")
    prop_sub.to_csv(os.path.join(MERGED, "topic_dist_by_subreddit.csv"))

    # ---- chi-square tests ----
    md = ["# Week 4 Chi-Square Results -- topic_category", "",
          f"Source: `data/merged/master_vader_roberta_topics.csv` ({len(m):,} rows).",
          "Tests run on the nine shared categories; `excluded` and the four "
          "WH-only categories are omitted (structural zeros for FB/Reddit). "
          "`government` (WH posts, n=12) excluded as too few.", ""]

    # 1. source_type x topic (primary): facebook vs community vs gov_response
    cm1 = pd.crosstab(src["source_bucket"], src["topic_category"])
    md.append(chi_block(
        "1. source_type x topic_category (primary)", cm1,
        "facebook vs community_discussion vs government_response."))

    # 2. within Reddit only: community_discussion vs government_response
    red_gov = shared[shared["source_bucket"].isin(
        ["community_discussion", "government_response"])]
    cm2 = pd.crosstab(red_gov["source_bucket"], red_gov["topic_category"])
    md.append(chi_block(
        "2. source_type x topic_category within Reddit (community vs government_response)",
        cm2,
        "Both are Reddit; isolates the WH-comment effect from the platform effect."))

    # 3. hurricane x topic
    cm3 = pd.crosstab(shared["hurricane"], shared["topic_category"])
    md.append(chi_block(
        "3. hurricane x topic_category", cm3,
        "All shared-category rows. Note: WH account did not exist for Debby, "
        "so any WH-specific cut excludes Debby; this overall table spans all sources."))

    with open(os.path.join(MERGED, "chi_square_results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # console summary
    print("Wrote topic_dist_by_source_type.csv / _by_hurricane.csv / _by_subreddit.csv")
    print("Wrote chi_square_results.md")
    print("\nTopic proportions by source_type:")
    print(prop_src.to_string())
    for name, cm in [("source x topic", cm1), ("within-Reddit", cm2), ("hurricane x topic", cm3)]:
        chi2, p, dof, _ = chi2_contingency(cm)
        print(f"  {name}: chi2={chi2:,.1f}, dof={dof}, p={p:.2e}, V={cramers_v(cm):.3f}")


if __name__ == "__main__":
    main()
