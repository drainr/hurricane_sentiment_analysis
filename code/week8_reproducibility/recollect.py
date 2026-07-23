"""
recollect.py — Week 8, re-execute Reddit/White House collection into a SEPARATE
tree so the frozen corpus the analysis is built on is never touched.

Why this exists
---------------
The Week 8 plan (task 1) says "re-run the entire pipeline from scratch ...
Reddit collection ...". The 2026-07-21 reproducibility pass deliberately froze
the raw collected files, because the collectors query the Arctic Shift archive
and its contents have drifted since June (posts deleted / edited / removed by
moderators), so a fresh pull cannot byte-match the corpus. The advisor asked for
collection to actually be re-run anyway.

This driver does that safely: it re-runs the real collectors, but redirects each
one's output into data/reddit_rerun/ instead of data/reddit/. Nothing under
data/reddit/<storm>/ is opened or written. collection_drift_report.py then diffs
the fresh pull against the frozen corpus to quantify the drift; the frozen corpus
stays the analysis basis unless José + the advisor decide to adopt the new pull.

What it re-collects (the four collectors that write via a redirectable OUT_DIR):
  - Debby + Helene whole-subreddit posts + comment trees  (collect_subreddit)
  - Helene early-window extension (Sep 21-22)              (collect_helene_ext)
  - Milton early-window extension                          (collect_milton_ext)
  - White House account posts + comment trees              (pull_whitehouse)

Not re-collected here: Milton's PRIMARY pull was the teammate's out-of-repo
keyword-first collection (its in-repo analogue, use_arctic_shift.py, hardcodes
its output path rather than exposing OUT_DIR). Re-running it whole-subreddit
would conflate a method-shape change with archive drift, so it is left out of the
1:1 drift diff and noted in the report.

Usage:
    python3 code/week8_reproducibility/recollect.py               # all collectors
    python3 code/week8_reproducibility/recollect.py --only debby_helene,wh
    python3 code/week8_reproducibility/recollect.py --list

This is a live network pull with 1.5s politeness sleeps and full comment-tree
fetches; expect tens of minutes. The collectors' own 422/429 backoff is reused.
"""
from __future__ import annotations
import argparse
import importlib.util
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RERUN_ROOT = os.path.join(REPO, "data", "reddit_rerun")

# name -> (repo-relative script path, OUT_DIR to force before calling main())
COLLECTORS = {
    "debby_helene": ("code/week1_setup_exploration/collect_subreddit.py", RERUN_ROOT),
    "helene_ext":   ("code/week3_roberta_agreement/collect_helene_ext.py",
                     os.path.join(RERUN_ROOT, "helene_ext")),
    "milton_ext":   ("code/week3_roberta_agreement/collect_milton_ext.py",
                     os.path.join(RERUN_ROOT, "milton_ext")),
    "wh":           ("code/week2_collection_vader/pull_whitehouse.py", RERUN_ROOT),
}


def load_module(rel_path: str):
    """Import a collector by file path without polluting sys.path permanently."""
    abs_path = os.path.join(REPO, rel_path)
    mod_name = "recollect_" + os.path.splitext(os.path.basename(abs_path))[0]
    spec = importlib.util.spec_from_file_location(mod_name, abs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_one(name: str) -> dict:
    """Run one collector with its OUT_DIR forced into data/reddit_rerun/."""
    rel_path, out_dir = COLLECTORS[name]
    module = load_module(rel_path)

    # Every collector computes OUT_DIR at import from sys.path[0], which is wrong
    # once imported here. main() reads the module global at call time, so
    # reassigning it now is what actually redirects the output.
    if not hasattr(module, "OUT_DIR"):
        raise AttributeError(f"{rel_path} has no OUT_DIR to redirect")
    module.OUT_DIR = out_dir
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n{'#'*70}\n#  {name}: {rel_path}\n#  OUT_DIR -> {os.path.relpath(out_dir, REPO)}\n{'#'*70}")
    start = time.time()
    module.main()
    elapsed = time.time() - start
    print(f"\n[{name}] done in {elapsed/60:.1f} min")
    return {"name": name, "seconds": elapsed}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help=f"comma-separated subset of: {','.join(COLLECTORS)}")
    ap.add_argument("--list", action="store_true", help="list collectors and exit")
    args = ap.parse_args()

    if args.list:
        for name, (path, out) in COLLECTORS.items():
            print(f"  {name:14} {path}  ->  {os.path.relpath(out, REPO)}")
        return

    wanted = args.only.split(",") if args.only else list(COLLECTORS)
    unknown = [w for w in wanted if w not in COLLECTORS]
    if unknown:
        sys.exit(f"unknown collector(s): {unknown}; choose from {list(COLLECTORS)}")

    # Guardrail: never let a redirect resolve back into the frozen corpus.
    # Compare on path components (commonpath), not string prefixes — "data/reddit"
    # is a string prefix of "data/reddit_rerun" but not a parent directory of it.
    rerun_root = os.path.abspath(RERUN_ROOT)
    frozen = os.path.abspath(os.path.join(REPO, "data", "reddit"))
    for name in wanted:
        out = os.path.abspath(COLLECTORS[name][1])
        under_rerun = os.path.commonpath([out, rerun_root]) == rerun_root
        under_frozen = os.path.commonpath([out, frozen]) == frozen
        if not under_rerun or under_frozen:
            sys.exit(f"REFUSING: {name} OUT_DIR {out} is not safely inside data/reddit_rerun/")

    print(f"Re-collecting {wanted} into {os.path.relpath(RERUN_ROOT, REPO)}/ "
          f"(frozen data/reddit/ untouched)")
    results = [run_one(name) for name in wanted]

    total = sum(r["seconds"] for r in results)
    print(f"\n{'='*70}\nRe-collection complete: {len(results)} collectors, "
          f"{total/60:.1f} min total.\nNext: "
          f"python3 code/week8_reproducibility/collection_drift_report.py")


if __name__ == "__main__":
    main()
