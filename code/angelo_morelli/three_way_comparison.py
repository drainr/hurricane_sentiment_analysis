"""
vader_comparison_table.py
--------------------------
Generates a comparison table across up to three VADER-scored CSV files.
 
Columns in output:
  data_source, hurricane, N, mean_compound,
  pct_positive, pct_negative, pct_neutral
 
Usage:
  python three_way_comparison.py file1.csv file2.csv file3.csv
 
Each file must have columns: hurricane, vader_compound, vader_label.
A label for each file is inferred from its filename, but you can override
them with the LABELS list below.
"""
from __future__ import annotations
import os, sys
import pandas as pd
 
# ── Optional: override auto-labels (set to None to use filenames) ─────────────
LABELS: list[str | None] = [None, None, None]
 
# Output path — written next to this script by default
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT  = os.path.join(OUT_DIR, "vader_comparison_table_comments.csv")
 
# ── Helpers ───────────────────────────────────────────────────────────────────
 
def infer_label(path: str, override: str | None) -> str:
    if override:
        return override
    # e.g. "reddit_relevant_posts_vader.csv" -> "reddit_relevant_posts"
    return os.path.splitext(os.path.basename(path))[0].replace("_vader", "")
 
 
def summarise(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """Return one row per hurricane for this data source."""
    rows = []
 
    hurricanes = sorted(df["hurricane"].dropna().unique())
    for h in hurricanes:
        sub = df[df["hurricane"] == h]
        n   = len(sub)
        if n == 0:
            continue
 
        counts = sub["vader_label"].value_counts()
        rows.append({
            "data_source":   label,
            "hurricane":     h,
            "N":             n,
            "mean_compound": round(sub["vader_compound"].mean(), 4),
            "pct_positive":  round(counts.get("positive", 0) / n * 100, 1),
            "pct_negative":  round(counts.get("negative", 0) / n * 100, 1),
            "pct_neutral":   round(counts.get("neutral",  0) / n * 100, 1),
        })
 
    return pd.DataFrame(rows)
 
 
# ── Main ──────────────────────────────────────────────────────────────────────
 
def main(paths: list[str]) -> None:
    if not 1 <= len(paths) <= 3:
        sys.exit("Usage: python vader_comparison_table.py file1.csv [file2.csv] [file3.csv]")
 
    parts = []
    for i, path in enumerate(paths):
        label = infer_label(path, LABELS[i] if i < len(LABELS) else None)
        print(f"Loading [{label}] from {path}")
        df = pd.read_csv(path)
 
        for col in ("hurricane", "vader_compound", "vader_label"):
            if col not in df.columns:
                sys.exit(f"  ERROR: column '{col}' not found in {path}")
 
        summary = summarise(df, label)
        parts.append(summary)
        print(f"  {len(df)} rows | hurricanes: {sorted(df['hurricane'].dropna().unique())}")
 
    table = pd.concat(parts, ignore_index=True)
 
    # Sort: hurricane first, then data source — easy to scan across sources
    table = table.sort_values(["hurricane", "data_source"]).reset_index(drop=True)
 
    table.to_csv(OUTPUT, index=False)
    print(f"\nSaved: {OUTPUT}")
    print()
    print(table.to_string(index=False))
 
 
if __name__ == "__main__":
    main(sys.argv[1:])