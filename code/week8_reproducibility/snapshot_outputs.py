"""
snapshot_outputs.py — fingerprint every pipeline output so a re-run can be verified.

Walks the canonical output locations and records, per file: size in bytes, a
SHA-256 of the contents, and (for CSVs) the parsed row count. Row counts come
from pandas, never `wc -l` — Reddit comment bodies contain embedded newlines, so
line counts overstate rows by ~65% on the big files (see the 2026-06-30
data-verification entry in the decision log).

Usage:
    python3 code/week8_reproducibility/snapshot_outputs.py --out before.csv
    ... run the pipeline ...
    python3 code/week8_reproducibility/snapshot_outputs.py --out after.csv
    python3 code/week8_reproducibility/snapshot_outputs.py --compare before.csv after.csv

Comparison rules follow what the Week 8 re-run established:
  - CSV / Markdown outputs are expected to match byte for byte.
  - PNG and PDF figures are NOT hash-compared. Matplotlib stamps a creation date
    into the file, so identical plots hash differently on every run; these are
    checked on existence and size band instead.
"""

from __future__ import annotations
import argparse
import hashlib
import os
import sys

import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Directories walked, relative to the repo root.
TARGETS = [
    "data/facebook",
    "data/reddit/combined",
    "data/reddit/whitehouse",
    "data/vader",
    "data/roberta",
    "data/processed",
    "data/merged",
    "docs",
    "figures",
]

# Skipped wholesale: raw inputs and third-party originals are not outputs.
SKIP_DIRS = {"student_originals", "raw_xlsx", "__pycache__", ".ipynb_checkpoints"}

# The re-run log records the run that is being verified, so it necessarily
# differs every time (timings). Excluding it keeps the diff meaningful.
SKIP_FILES = {"docs/week8/rerun_log.md", "docs/week8/output_manifest.csv"}

# Figures are compared on existence/size, not hash (see module docstring).
NON_DETERMINISTIC_SUFFIXES = (".png", ".pdf")


def sha256(path: str) -> str:
    """Return the SHA-256 hex digest of a file, read in 1 MB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def row_count(path: str) -> int | str:
    """Parsed row count for a CSV, or "" for any other file type.

    Uses pandas so quoted newlines inside comment text do not inflate the count.
    """
    if not path.endswith(".csv"):
        return ""
    try:
        return len(pd.read_csv(path, dtype=str, keep_default_na=False,
                               encoding="utf-8", encoding_errors="replace",
                               low_memory=False))
    except Exception as exc:                      # unparseable file is itself a finding
        return f"ERROR: {type(exc).__name__}"


def walk() -> pd.DataFrame:
    """Fingerprint every output file under TARGETS into one DataFrame."""
    rows = []
    for target in TARGETS:
        root = os.path.join(REPO, target)
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in sorted(filenames):
                if name.startswith("."):
                    continue
                full = os.path.join(dirpath, name)
                rel = os.path.relpath(full, REPO)
                if rel in SKIP_FILES:
                    continue
                hashed = not rel.endswith(NON_DETERMINISTIC_SUFFIXES)
                rows.append({
                    "path": rel,
                    "bytes": os.path.getsize(full),
                    "sha256": sha256(full) if hashed else "",
                    "rows": row_count(full),
                    "hash_compared": hashed,
                })
    return pd.DataFrame(rows).sort_values("path").reset_index(drop=True)


def compare(before_path: str, after_path: str) -> int:
    """Diff two snapshots and print a report. Returns a shell exit code."""
    before = pd.read_csv(before_path).set_index("path")
    after = pd.read_csv(after_path).set_index("path")

    added = sorted(set(after.index) - set(before.index))
    removed = sorted(set(before.index) - set(after.index))
    common = sorted(set(before.index) & set(after.index))

    changed, figures_changed = [], []
    for p in common:
        b, a = before.loc[p], after.loc[p]
        if not bool(a["hash_compared"]):
            if b["bytes"] != a["bytes"]:
                figures_changed.append(p)
            continue
        if b["sha256"] != a["sha256"]:
            changed.append((p, b["rows"], a["rows"], b["bytes"], a["bytes"]))

    print(f"snapshot compare: {before_path} -> {after_path}")
    print(f"  files: {len(common)} common, {len(added)} added, {len(removed)} removed")
    print(f"  hash-compared files that changed: {len(changed)}")
    print(f"  figures that changed size: {len(figures_changed)}")

    for p in added:
        print(f"    ADDED    {p}")
    for p in removed:
        print(f"    REMOVED  {p}")
    for p, rb, ra, bb, ba in changed:
        note = "row count changed" if str(rb) != str(ra) else "same rows, bytes differ"
        print(f"    CHANGED  {p}  rows {rb} -> {ra}  bytes {bb:,} -> {ba:,}  ({note})")

    if not changed and not added and not removed:
        print("\n  VERIFIED: every hash-compared output is byte-identical.")
        return 0
    print("\n  Investigate each CHANGED entry before accepting the re-run.")
    return 1


def main() -> None:
    """Parse arguments and either write a snapshot or compare two."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", help="write a snapshot CSV to this path")
    ap.add_argument("--compare", nargs=2, metavar=("BEFORE", "AFTER"),
                    help="compare two snapshot CSVs")
    args = ap.parse_args()

    if args.compare:
        sys.exit(compare(*args.compare))

    if not args.out:
        ap.error("pass either --out or --compare")

    df = walk()
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    df.to_csv(args.out, index=False)
    csvs = df[df["path"].str.endswith(".csv")]
    print(f"snapshot: {len(df)} files -> {args.out}")
    print(f"  {len(csvs)} CSVs, {int(pd.to_numeric(csvs['rows'], errors='coerce').sum()):,} total rows")


if __name__ == "__main__":
    main()
