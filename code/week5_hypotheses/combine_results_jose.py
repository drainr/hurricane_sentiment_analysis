#!/usr/bin/env python3
"""
Combine José's per-hypothesis results into ONE all-7 CSV (H1-H7 x 2 methods).

Unions the three José results files (pandas aligns by column name, so H2's slope/r2
and H5's variant columns simply appear as extra columns, blank for the others):
  hypothesis_tests_results_jose.csv  (H1, H3, H4, H7)  <- hypothesis_tests_jose.py
  h2_results_jose.csv                (H2)              <- h2_temporal.py
  h5_results_jose.csv                (H5)              <- h5_subreddit.py

Run those three producers first, then this. Output:
  data/merged/hypothesis_tests_all7_jose.csv
"""
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
M = REPO / "data" / "merged"
PARTS = ["hypothesis_tests_results_jose.csv", "h2_results_jose.csv", "h5_results_jose.csv"]

missing = [p for p in PARTS if not (M / p).exists()]
if missing:
    raise SystemExit("Missing input(s): " + ", ".join(missing)
                     + "\nRun hypothesis_tests_jose.py, h2_temporal.py, h5_subreddit.py first.")

alldf = pd.concat([pd.read_csv(M / p) for p in PARTS], ignore_index=True)

# readable column order; any unexpected columns are appended at the end
ORDER = ["hypothesis", "model", "subset", "hurricane", "comparison", "platform", "variant",
         "test", "group_a", "group_b", "u", "p", "p_bonferroni", "rank_biserial", "stat",
         "slope", "r2", "chi2", "chi2_p", "ci_low", "ci_high", "observed_diff", "gap",
         "bootstrap_p", "levene_stat", "levene_p", "keyword_n", "non_keyword_n"]
cols = [c for c in ORDER if c in alldf.columns] + [c for c in alldf.columns if c not in ORDER]
alldf = alldf[cols].sort_values(["hypothesis", "model"], kind="stable")

out = M / "hypothesis_tests_all7_jose.csv"
alldf.to_csv(out, index=False)
print(f"Wrote {out}  ({len(alldf)} rows across H1-H7)")
print(alldf.groupby("hypothesis").size().to_string())
