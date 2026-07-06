"""
label_topics.py -- stamp the codebook's human labels + categories into each scored file.
Prepared with the help of Claude Code.

Reads the six per-source tables in docs/Topic Codebook.md, then for each
*_vader_roberta_topics.csv writes a *_labeled.csv with two new columns
(topic_label_human, topic_category). Originals are left alone. Aborts if a topic id
in any file is missing from the codebook.

    python label_topics.py --codebook ../../docs/"Topic Codebook.md" \
        --in_dir <topic_csvs> --out_dir <topic_csvs>
"""

import argparse
import csv
import glob
import os
import re

# codebook section header -> filename prefix
SECTION_TO_FILE = {
    "Facebook posts": "facebook_posts",
    "Facebook comments": "facebook_comments",
    "White House posts": "whitehouse_threads_posts",
    "White House comments": "whitehouse_threads_comments",
    "Reddit posts": "reddit_relevant_posts",
    "Reddit comments": "reddit_relevant_comments",
}


def parse_codebook(path):
    """{section: {topic_bertopic: (label, category)}}"""
    text = open(path, encoding="utf-8").read()
    out = {}
    for chunk in re.split(r"^## ", text, flags=re.M):
        head = chunk.split("\n", 1)[0].strip()
        if head not in SECTION_TO_FILE:
            continue
        rows = {}
        for line in chunk.splitlines():
            m = re.match(r"\|\s*([^|]+?)\s*\|\s*[^|]*?\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|", line)
            if not m:
                continue
            tid = m.group(1).strip()
            if tid == "Topic" or set(tid) <= set("-"):
                continue
            rows[tid] = (m.group(2).strip(), m.group(3).strip())
        out[head] = rows
    return out


def section_for_file(basename):
    for section, stem in SECTION_TO_FILE.items():
        if basename.startswith(stem):
            return section
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codebook", required=True)
    ap.add_argument("--in_dir", default=".")
    ap.add_argument("--out_dir", default=".")
    args = ap.parse_args()
    csv.field_size_limit(10 ** 7)
    os.makedirs(args.out_dir, exist_ok=True)

    cb = parse_codebook(args.codebook)
    files = sorted(glob.glob(os.path.join(args.in_dir, "*_vader_roberta_topics.csv")))
    if not files:
        raise SystemExit(f"No *_vader_roberta_topics.csv in {args.in_dir}")

    for path in files:
        base = os.path.basename(path)
        section = section_for_file(base)
        if section is None or section not in cb:
            raise SystemExit(f"No codebook section matches {base}")
        mapping = cb[section]
        out_path = os.path.join(args.out_dir, base.replace(".csv", "_labeled.csv"))
        n = 0
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames + ["topic_label_human", "topic_category"]
            with open(out_path, "w", newline="", encoding="utf-8") as g:
                writer = csv.DictWriter(g, fieldnames=fieldnames)
                writer.writeheader()
                for r in reader:
                    tid = r["topic_bertopic"]
                    if tid not in mapping:
                        raise SystemExit(f"{base}: topic {tid!r} not in codebook '{section}'")
                    r["topic_label_human"], r["topic_category"] = mapping[tid]
                    writer.writerow(r)
                    n += 1
        print(f"{base:52} -> {os.path.basename(out_path)}  ({n} rows, {len(mapping)} topics)")


if __name__ == "__main__":
    main()
