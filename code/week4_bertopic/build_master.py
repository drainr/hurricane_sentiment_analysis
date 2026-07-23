"""
build_master.py -- concatenate the six *_labeled.csv files into one master.
Prepared with the help of Claude Code.

The master is a derived snapshot: regenerate it, never hand-edit. Adds a `provenance`
column (source file stem) and checks two guardrails before writing:
  - row count == 187,359 (= 952 + 59,736 + 3,413 + 121,053 + 12 + 2,193).
    Was 188,337 before the 2026-06-26 WH-from-Reddit de-dup: 5 WH posts + 973 WH
    comments that the keyword search had pulled into reddit_relevant were removed
    (they live in the whitehouse_threads files), so reddit_posts 3,418->3,413 and
    reddit_comments 122,026->121,053. The plan's 186,722 is older still (pre the
    2026-06-18 Reddit window extensions; differs from this by +96 posts / +541
    comments = +637). If you see 186,769 the old WH duplicates are back -- fix upstream.
  - zero duplicate (id, source).

    python build_master.py --in_dir <labeled_csvs> --out data/merged/master_vader_roberta_topics.csv
"""

import argparse
import csv
import glob
import os

EXPECTED_ROWS = 187_359
PER_FILE_EXPECTED = {
    "facebook_posts": 952,
    "facebook_comments": 59_736,
    "reddit_relevant_posts": 3_413,
    "reddit_relevant_comments": 121_053,
    "whitehouse_threads_posts": 12,
    "whitehouse_threads_comments": 2_193,
}


def stem_of(basename):
    """Map a filename to its expected source stem, or None if unrecognised."""
    for stem in PER_FILE_EXPECTED:
        if basename.startswith(stem):
            return stem
    return None


def main():
    """Concatenate the six labeled files into the master snapshot.

    Adds a provenance column naming each row's source file, then checks two
    guardrails: 187,359 total rows and zero duplicate (id, source) pairs. The
    master is a derived snapshot — rebuild it, never hand-edit it.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_dir", default=".")
    ap.add_argument("--out", default="data/merged/master_vader_roberta_topics.csv")
    args = ap.parse_args()
    csv.field_size_limit(10 ** 7)

    files = sorted(glob.glob(os.path.join(args.in_dir, "*_labeled.csv")))
    if len(files) != 6:
        raise SystemExit(f"Expected 6 *_labeled.csv, found {len(files)}")

    # union of columns (FB and Reddit/WH schemas differ slightly)
    all_cols, seen, per_file = [], set(), []
    for path in files:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for c in reader.fieldnames:
                if c not in seen:
                    seen.add(c); all_cols.append(c)
            per_file.append((path, list(reader)))

    fieldnames = all_cols + ["provenance"]
    counts, id_source, dupes, total = {}, set(), 0, 0
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    # lineterminator="\n" added in the Week 8 re-run. csv.writer defaults to
    # "\r\n" on every platform, so this was the one file in the pipeline written
    # with CRLF; every other output (all pandas to_csv) uses LF. Content was
    # identical, but the master hashed differently on every rebuild, which
    # masked real diffs during verification.
    with open(args.out, "w", newline="", encoding="utf-8") as g:
        writer = csv.DictWriter(g, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for path, rows in per_file:
            stem = stem_of(os.path.basename(path))
            counts[stem] = len(rows)
            for r in rows:
                r["provenance"] = stem
                key = (r.get("id", ""), r.get("source", r.get("source_type", "")))
                if key in id_source:
                    dupes += 1
                id_source.add(key)
                writer.writerow({c: r.get(c, "") for c in fieldnames})
                total += 1

    # guardrails
    print("per-source row counts:")
    ok = True
    for stem, exp in PER_FILE_EXPECTED.items():
        got = counts.get(stem, 0)
        ok = ok and got == exp
        print(f"  {stem:30} {got:>8} (expected {exp}) {'OK' if got == exp else 'MISMATCH'}")
    print(f"\ntotal rows: {total} (expected {EXPECTED_ROWS})\nduplicate (id, source): {dupes}")

    if total != EXPECTED_ROWS:
        raise SystemExit(f"GUARDRAIL FAILED: {total} != {EXPECTED_ROWS} (186,769 = WH dupes back).")
    if dupes:
        raise SystemExit(f"GUARDRAIL FAILED: {dupes} duplicate (id, source).")
    if not ok:
        raise SystemExit("GUARDRAIL FAILED: per-file counts off.")
    print(f"\nOK -- wrote {args.out}")


if __name__ == "__main__":
    main()
