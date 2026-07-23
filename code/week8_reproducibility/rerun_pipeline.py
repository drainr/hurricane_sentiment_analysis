"""
rerun_pipeline.py — re-run the analysis pipeline end to end and log every stage.

This is the Week 8 "re-run the entire pipeline from scratch" deliverable. It
executes each stage in dependency order as a subprocess, records the command,
exit code, duration and tail of output, and writes docs/week8/rerun_log.md.

Scope of "from scratch"
-----------------------
The frozen inputs are the RAW COLLECTED FILES: the six Facebook xlsx in
data/facebook/raw_xlsx/ and the Reddit/White House pulls in data/reddit/.
Everything downstream of those is re-executed here.

Collection itself is deliberately NOT re-run. The collectors hit the Arctic
Shift API, whose backing archive has changed since June (posts deleted, edited,
or removed by moderators), so a fresh pull cannot byte-match the corpus the
analysis was built on — a re-collection would be a different experiment, not a
verification of this one. The collectors are kept runnable and documented
(explore_queries, pull_comments, pull_whitehouse, pull_org_mentions,
collect_subreddit, use_arctic_shift, collect_helene_ext, collect_milton_ext).

Two stages run on Google Colab GPU and are skipped by default: RoBERTa scoring
(week3) and BERTopic (week4). Their outputs are the *_vader_roberta.csv and
*_vader_roberta_topics.csv files. See
docs/week8/colab_reproducibility_run.md for how those are verified.

Usage:
    python3 code/week8_reproducibility/rerun_pipeline.py            # local lane
    python3 code/week8_reproducibility/rerun_pipeline.py --list     # show stages
    python3 code/week8_reproducibility/rerun_pipeline.py --stages facebook,reddit
"""

from __future__ import annotations
import argparse
import glob
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = os.path.join(REPO, "docs", "week8", "rerun_log.md")

PY = sys.executable


def step(script: str, *args: str) -> list[str]:
    """Build one subprocess command from a repo-relative script path."""
    return [PY, os.path.join(REPO, script), *args]


# (group, human label, command). Order is dependency order.
STAGES: list[tuple[str, str, list[str]]] = [
    ("facebook", "Facebook standardization (6 raw xlsx -> facebook_master.csv)",
     step("code/week1_setup_exploration/build_facebook_master.py")),
    ("facebook", "Split Facebook into posts / comments",
     step("code/week2_collection_vader/split_facebook.py")),
    ("facebook", "VADER on the split Facebook files",
     step("code/week2_collection_vader/run_vader_facebook_split.py")),

    ("reddit", "Merge Reddit pulls -> reddit_clean.csv (window filter)",
     step("code/week2_collection_vader/merge_reddit_angelo.py")),
    ("reddit", "Thread relevance + bot removal -> reddit_relevant.csv",
     step("code/week2_collection_vader/build_relevant_angelo_fixed.py")),
    ("reddit", "VADER on the Reddit relevant corpus",
     step("code/week2_collection_vader/run_vader_reddit.py")),
    ("reddit", "Split Reddit into posts / comments",
     step("code/week2_collection_vader/split_reddit.py")),

    ("whitehouse", "Clean White House threads",
     step("code/week2_collection_vader/clean_whitehouse_data.py")),
    ("whitehouse", "VADER on the White House files",
     step("code/week2_collection_vader/run_vader_whitehouse.py")),

    ("tables", "Three-way comparison table (posts)",
     step("code/week2_collection_vader/three_way_comparison.py",
          "--out", os.path.join(REPO, "data/merged/vader_comparison_table_posts.csv"),
          os.path.join(REPO, "data/vader/facebook_posts_vader.csv"),
          os.path.join(REPO, "data/vader/reddit_relevant_vader_posts.csv"),
          os.path.join(REPO, "data/vader/whitehouse_threads_posts_vader.csv"))),
    ("tables", "Three-way comparison table (comments)",
     step("code/week2_collection_vader/three_way_comparison.py",
          "--out", os.path.join(REPO, "data/merged/vader_comparison_table_comments.csv"),
          os.path.join(REPO, "data/vader/facebook_comments_vader.csv"),
          os.path.join(REPO, "data/vader/reddit_relevant_vader_comments.csv"),
          os.path.join(REPO, "data/vader/whitehouse_threads_comments_vader.csv"))),

    # --- Colab boundary: RoBERTa (week3) then BERTopic (week4) run on GPU ---
    ("colab", "RoBERTa scoring (Colab GPU notebook)",
     ["COLAB", "code/week3_roberta_agreement/RoBERTa.ipynb"]),
    ("colab", "BERTopic topic modelling (Colab GPU notebook)",
     ["COLAB", "code/week4_bertopic/BERTopic.ipynb"]),

    # Needs the BERTopic per-corpus outputs (*_vader_roberta_topics.csv), which
    # are produced on Colab and live on Drive — only the *_labeled.csv results
    # are kept in the repo. Skipped automatically when those inputs are absent.
    ("topics", "Stamp human topic labels onto the six files",
     step("code/week4_bertopic/label_topics.py",
          "--codebook", os.path.join(REPO, "docs/week4/Topic Codebook.md"),
          "--in_dir", os.path.join(REPO, "data/processed"),
          "--out_dir", os.path.join(REPO, "data/processed"))),
    ("topics", "Build the master snapshot (guardrail: 187,359 rows)",
     step("code/week4_bertopic/build_master.py",
          "--in_dir", os.path.join(REPO, "data/processed"),
          "--out", os.path.join(REPO, "data/merged/master_vader_roberta_topics.csv"))),
    ("topics", "Topic distributions + chi-square",
     step("code/week4_bertopic/topic_distributions.py")),
    ("topics", "Topic figures",
     step("code/week4_bertopic/plot_topics.py")),

    ("stats", "Data integrity verification (expects ALL CHECKS PASSED)",
     step("code/week5_hypotheses/verify_data.py")),
    ("stats", "Hypotheses H1/H3/H4/H7 (Jose)",
     step("code/week5_hypotheses/hypothesis_tests_jose.py")),
    ("stats", "Hypotheses H1/H3/H4/H7 (Angelo, independent cross-check)",
     step("code/week5_hypotheses/hypothesis_tests.py")),
    ("stats", "H2 temporal trajectory",
     step("code/week5_hypotheses/h2_temporal.py")),
    ("stats", "H5 subreddit tiers",
     step("code/week5_hypotheses/h5_subreddit.py")),
    ("stats", "Method validation vs the 400-item gold standard",
     step("code/week5_hypotheses/evaluate_methods.py")),
    ("stats", "Results grid",
     step("code/week5_hypotheses/results_table.py")),
    ("stats", "Combine all 7 hypotheses into one CSV",
     step("code/week5_hypotheses/combine_results_jose.py")),

    ("figures", "F1 dataset overview", step("code/week6_figures/f1_dataset_overview.py")),
    ("figures", "F3 three-way means", step("code/week6_figures/f3_three_way.py")),
    ("figures", "F4 sentiment distribution", step("code/week6_figures/f4_sentiment_distribution.py")),
    ("figures", "F6 VADER x RoBERTa agreement", step("code/week6_figures/f6_agreement_heatmap.py")),
    ("figures", "F7 topic distribution by source", step("code/week6_figures/f7_topic_distribution_by_source_type.py")),
    ("figures", "F8 topic evolution", step("code/week6_figures/f8_topic_evolution.py")),
    ("figures", "F9 White House case study", step("code/week6_figures/f9_whitehouse_case_study.py")),
    ("figures", "H7 per-hurricane check", step("code/week6_figures/h7_per_hurricane.py")),
    ("figures", "Landfall trajectories", step("code/week6_figures/plot_landfall_trajectories.py")),

    ("tests", "Unit tests",
     [PY, "-m", "pytest", os.path.join(REPO, "code/week5_hypotheses/tests/"), "-q"]),
]

# build_ground_truth.py is intentionally absent. It rebuilds ground_truth_400.csv
# from the two annotators' raw label files, which blanks the 38 sentiment + 4
# gratitude disagreements that Jose and Angelo adjudicated by hand. The file is a
# curated artifact, not a reproducible output; the script now refuses to
# overwrite an adjudicated copy unless REBUILD_GROUND_TRUTH=1 is set.


def run(label: str, cmd: list[str]) -> dict:
    """Run one stage, returning a record of how it went."""
    print(f"\n=== {label}")
    print(f"    {' '.join(os.path.relpath(c, REPO) if c.startswith(REPO) else c for c in cmd)}")
    start = time.time()
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    elapsed = time.time() - start
    out = (proc.stdout or "") + (proc.stderr or "")
    status = "ok" if proc.returncode == 0 else "FAILED"
    print(f"    -> {status} in {elapsed:.1f}s")
    if proc.returncode != 0:
        print("\n".join(out.strip().splitlines()[-15:]))
    return {"label": label, "cmd": cmd, "returncode": proc.returncode,
            "seconds": elapsed, "tail": "\n".join(out.strip().splitlines()[-12:])}


def main() -> None:
    """Run the selected stages and write the run log."""
    groups = sorted({g for g, _, _ in STAGES}, key=lambda g: [x[0] for x in STAGES].index(g))
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stages", help=f"comma-separated subset of: {','.join(groups)}")
    ap.add_argument("--list", action="store_true", help="list stages and exit")
    ap.add_argument("--include-colab", action="store_true",
                    help="do not skip the two Colab notebook stages (they cannot run locally)")
    args = ap.parse_args()

    if args.list:
        for g, label, _ in STAGES:
            print(f"  [{g:10}] {label}")
        return

    wanted = set(args.stages.split(",")) if args.stages else set(groups)

    results, skipped = [], []
    for group, label, cmd in STAGES:
        if group not in wanted:
            continue
        if cmd[0] == "COLAB" and not args.include_colab:
            skipped.append((label, cmd[1]))
            print(f"\n=== {label}\n    SKIPPED (Colab GPU stage) — see docs/week8/colab_reproducibility_run.md")
            continue
        # label_topics consumes BERTopic's per-corpus output, which is produced
        # on Colab and kept on Drive. Skip rather than fail when it is absent.
        if "label_topics.py" in cmd[1] and not glob.glob(
                os.path.join(REPO, "data/processed", "*_vader_roberta_topics.csv")):
            skipped.append((label, "needs BERTopic *_vader_roberta_topics.csv from Colab/Drive"))
            print(f"\n=== {label}\n    SKIPPED — BERTopic per-corpus outputs not present locally "
                  f"(only the *_labeled.csv results are kept in the repo)")
            continue
        results.append(run(label, cmd))

    failed = [r for r in results if r["returncode"] != 0]

    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("# Week 8 — pipeline re-run log\n\n")
        f.write(f"Stages run: {len(results)} | failed: {len(failed)} | "
                f"skipped (Colab): {len(skipped)}\n")
        f.write(f"Total runtime: {sum(r['seconds'] for r in results):.1f}s\n\n")
        f.write("| # | stage | result | seconds |\n|---|---|---|---|\n")
        for i, r in enumerate(results, 1):
            f.write(f"| {i} | {r['label']} | {'ok' if r['returncode'] == 0 else 'FAILED'} "
                    f"| {r['seconds']:.1f} |\n")
        if skipped:
            f.write("\n## Skipped (Colab GPU)\n\n")
            for label, nb in skipped:
                f.write(f"- {label} — `{nb}`\n")
        f.write("\n## Stage output (tail)\n\n")
        for r in results:
            f.write(f"### {r['label']}\n\n```\n{r['tail']}\n```\n\n")

    print(f"\nWrote {os.path.relpath(LOG, REPO)}")
    print(f"{len(results) - len(failed)}/{len(results)} stages OK"
          + (f", {len(failed)} FAILED" if failed else ""))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
