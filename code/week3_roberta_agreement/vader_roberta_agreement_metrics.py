"""
agreement_metrics.py
--------------------
Computes VADER vs. RoBERTa agreement metrics across all six vader_roberta CSVs.

Data is read from ../../data/vader/ relative to this script's location.

Metrics produced:
  - Per file: raw agreement rate, Cohen's kappa, confusion matrix
  - Pooled across all files: same three metrics
  - By hurricane: summary table + per-hurricane confusion matrices
  - By source type (source_type column): summary table + per-source-type confusion matrices

Usage:
  python agreement_metrics.py [--output-dir PATH]

Default output dir: current directory.
"""

import argparse
import os
import sys
import textwrap

import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

# -- Paths ---------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "data"))
OUTPUT_DIR = os.path.normpath(os.path.join("..", "..", "data", "roberta"))

FILE_PATTERNS = [
    "roberta/reddit_relevant_posts_vader_roberta.csv",
    "roberta/reddit_relevant_comments_vader_roberta.csv",
    "roberta/facebook_posts_vader_roberta.csv",
    "roberta/facebook_comments_vader_roberta.csv",
    "roberta/whitehouse_threads_posts_vader_roberta.csv",
    "roberta/whitehouse_threads_comments_vader_roberta.csv",
]

# -- Label normalisation -------------------------------------------------------

LABEL_MAP = {
    "positive": "positive",
    "neutral":  "neutral",
    "negative": "negative",
    "pos":      "positive",
    "neg":      "negative",
}

ORDERED_LABELS = ["negative", "neutral", "positive"]


def normalise(series: pd.Series) -> pd.Series:
    """Lower-case and map to the canonical {negative, neutral, positive} vocabulary."""
    mapped = series.str.lower().map(LABEL_MAP)
    unknown = mapped.isna()
    if unknown.any():
        bad = series[unknown].unique().tolist()
        raise ValueError(f"Unrecognised label values: {bad}")
    return mapped


# -- File discovery ------------------------------------------------------------

def locate_files() -> dict[str, str]:
    """Return {pattern: full_path} for every file found; warn about missing ones."""
    found = {}
    missing = []
    for rel in FILE_PATTERNS:
        path = os.path.join(DATA_DIR, rel)
        if os.path.isfile(path):
            found[rel] = path
        else:
            missing.append(rel)
    if missing:
        print(f"[WARNING] {len(missing)} file(s) not found under '{DATA_DIR}':")
        for m in missing:
            print(f"  - {m}")
        print()
    return found


# -- Core metrics --------------------------------------------------------------

def compute_metrics(vader: pd.Series, roberta: pd.Series) -> dict:
    """Return raw_agreement, kappa, and a labelled confusion matrix DataFrame."""
    n = len(vader)
    raw_agreement = (vader == roberta).sum() / n
    kappa = cohen_kappa_score(vader, roberta, labels=ORDERED_LABELS)
    cm = confusion_matrix(vader, roberta, labels=ORDERED_LABELS)
    conf_df = pd.DataFrame(
        cm,
        index=[f"VADER_{lbl}" for lbl in ORDERED_LABELS],
        columns=[f"RoBERTa_{lbl}" for lbl in ORDERED_LABELS],
    )
    return {"n": n, "raw_agreement": raw_agreement, "kappa": kappa, "conf_matrix": conf_df}


# -- Reporting -----------------------------------------------------------------

KAPPA_INTERP = [
    (0.81, "Almost perfect"),
    (0.61, "Substantial"),
    (0.41, "Moderate"),
    (0.21, "Fair"),
    (0.00, "Slight"),
    (-1.0, "Poor / less than chance"),
]


def interpret_kappa(k: float) -> str:
    """Map a kappa value onto its conventional strength label."""
    for threshold, label in KAPPA_INTERP:
        if k > threshold:
            return label
    return "Poor / less than chance"


def section_header(title: str) -> str:
    """Format a title as a bar-delimited section header."""
    bar = "=" * 60
    return f"\n{bar}\n  {title}\n{bar}"


def format_block(title: str, metrics: dict) -> str:
    """Format one file's agreement metrics as an indented text block."""
    lines = [
        "-" * 60,
        f"  {title}",
        "-" * 60,
        f"  Rows analysed   : {metrics['n']:,}",
        f"  Raw agreement   : {metrics['raw_agreement']:.4f}  "
        f"({metrics['raw_agreement']*100:.1f}%)",
        f"  Cohen's kappa   : {metrics['kappa']:.4f}  "
        f"[{interpret_kappa(metrics['kappa'])}]",
        "",
        "  Confusion matrix (rows = VADER, columns = RoBERTa):",
    ]
    for row in metrics["conf_matrix"].to_string().splitlines():
        lines.append("    " + row)
    lines.append("")
    return "\n".join(lines)


def breakdown_blocks(df: pd.DataFrame, group_col: str, label: str) -> list[str]:
    """
    Summary table + per-group confusion matrices for a single grouping column.
    Skips the breakdown silently if the column is absent.
    """
    if group_col not in df.columns:
        return [f"\n[INFO] Column '{group_col}' not present -- breakdown skipped.\n"]

    groups = sorted(df[group_col].dropna().unique())
    lines  = [section_header(f"By {label}")]

    # Per-group confusion matrices
    for val in groups:
        mask    = df[group_col] == val
        vader   = normalise(df.loc[mask, "vader_label"])
        roberta = normalise(df.loc[mask, "roberta_label"])
        m       = compute_metrics(vader, roberta)
        lines.append(format_block(f"{label}: {val}", m))

    return lines


# -- Main ----------------------------------------------------------------------

def main():
    """Compute VADER vs RoBERTa agreement for each scored file and write the report.

    Reports raw label agreement, Cohen's kappa and a confusion matrix. Note that
    this is method-vs-method agreement, distinct from the human inter-annotator
    kappa in build_ground_truth.py.
    """
    parser = argparse.ArgumentParser(
        description="Compute VADER vs. RoBERTa agreement metrics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(__doc__),
    )
    parser.add_argument(
        "--output-dir", default=".",
        help="Directory to write the results text file (default: current dir)",
    )
    args = parser.parse_args()

    print(f"Data directory: {DATA_DIR}\n")

    files = locate_files()
    if not files:
        print("[ERROR] No input files found. Exiting.")
        sys.exit(1)

    all_frames   = []
    report_lines = ["VADER vs. RoBERTa Agreement Metrics\n"]

    # -- Per-file blocks -------------------------------------------------------
    report_lines.append(section_header("Per-file Results"))

    for rel, path in files.items():
        print(f"Processing: {rel}")
        df = pd.read_csv(path)

        for col in ("vader_label", "roberta_label"):
            if col not in df.columns:
                raise KeyError(f"Column '{col}' missing from {rel}")

        before = len(df)
        df = df.dropna(subset=["vader_label", "roberta_label"])
        dropped = before - len(df)
        if dropped:
            print(f"  [INFO] Dropped {dropped} row(s) with null labels.")

        df["_vader_norm"]   = normalise(df["vader_label"])
        df["_roberta_norm"] = normalise(df["roberta_label"])

        m = compute_metrics(df["_vader_norm"], df["_roberta_norm"])
        report_lines.append(format_block(rel, m))

        all_frames.append(df)

    # -- Pooled ----------------------------------------------------------------
    combined = pd.concat(all_frames, ignore_index=True)
    
    if "hurricane" in combined.columns:
        combined["hurricane"] = (
            combined["hurricane"]
            .astype(str)
            .str.strip()
            .str.lower()
    )
        
    if "source_type" not in combined.columns:
        combined["source_type"] = pd.NA

    if "platform" in combined.columns:
        facebook_mask = (
            combined["platform"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("facebook")
    )

    combined.loc[
        facebook_mask,
        "source_type"
    ] = "community_discussion"

    combined["source_type"] = (
        combined["source_type"]
        .astype(str)
        .str.strip()
        .str.lower()
)

    if len(files) > 1:
        report_lines.append(section_header(f"Pooled (all {len(files)} files)"))
        pooled_m = compute_metrics(combined["_vader_norm"], combined["_roberta_norm"])
        report_lines.append(format_block("POOLED", pooled_m))

    # -- By hurricane ----------------------------------------------------------
    report_lines.extend(breakdown_blocks(combined, "hurricane", "Hurricane"))

    # -- By source type --------------------------------------------------------
    report_lines.extend(breakdown_blocks(combined, "source_type", "Source type"))


    # -- Disagreement sample ---------------------------------------------------
    disagreements = combined[combined["_vader_norm"] != combined["_roberta_norm"]].copy()
    if len(disagreements):
        sample_n = min(100, len(disagreements))
        review_cols = [c for c in [
            "id", "hurricane", "source_type", "platform", "type",
            "text", "vader_label", "roberta_label"
        ] if c in disagreements.columns]
        disagreements[review_cols].sample(
            n=sample_n, random_state=42
        ).to_csv(
            os.path.join(OUTPUT_DIR, "disagreement_examples_100.csv"),
            index=False
        )

    # -- Write output ----------------------------------------------------------
    report = "\n".join(report_lines)
    print()
    print(report)

    out_path = os.path.join(OUTPUT_DIR, "agreement_metrics.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nResults written to: {out_path}")


if __name__ == "__main__":
    main()