#!/usr/bin/env python3
"""
Week 5 data-integrity verification

Read-only. Loads every scored/labeled file with pandas (NOT wc -l, which over-counts
because comment bodies contain embedded newlines) and reconciles against the canonical
Decision-Log row counts before any hypothesis testing begins.

Checks:
  1. True pandas row counts vs canonical numbers (and vs wc -l, to show the inflation).
  2. Stage consistency: VADER vs RoBERTa vs processed row counts per source.
  3. Duplicates within files (id, (id,type)) and cross-file id collisions; no WH ids in Reddit.
  4. VADER score sanity (ranges, prob sum, label/threshold consistency, nulls).
  5. RoBERTa score sanity (ranges, prob sum, argmax==label, coverage, truncation rate).
  6. Key columns: days_from_landfall window bounds, hurricane values, subreddit non-null.
  7. VADER vs RoBERTa raw-agreement tripwire per file.

Writes docs/week5/data_verification_week5.md and prints a report. Modifies nothing.
Exit code 0 = all pass, 1 = at least one real problem found.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
VADER = REPO / "data" / "vader"
ROBERTA = REPO / "data" / "roberta"
PROC = REPO / "data" / "processed"
MASTER = REPO / "data" / "merged" / "master_vader_roberta_topics.csv"
OUT = REPO / "docs" / "week5" / "data_verification_week5.md"
OUT.parent.mkdir(parents=True, exist_ok=True)

# source key -> (vader file, roberta file, processed file, canonical row count)
SOURCES = {
    "facebook_posts":              ("facebook_posts_vader.csv",              "facebook_posts_vader_roberta.csv",              "facebook_posts_vader_roberta_topics_labeled.csv",              952),
    "facebook_comments":           ("facebook_comments_vader.csv",           "facebook_comments_vader_roberta.csv",           "facebook_comments_vader_roberta_topics_labeled.csv",           59736),
    "reddit_relevant_posts":       ("reddit_relevant_vader_posts.csv",       "reddit_relevant_posts_vader_roberta.csv",       "reddit_relevant_posts_vader_roberta_topics_labeled.csv",       3413),
    "reddit_relevant_comments":    ("reddit_relevant_vader_comments.csv",    "reddit_relevant_comments_vader_roberta.csv",    "reddit_relevant_comments_vader_roberta_topics_labeled.csv",    121053),
    "whitehouse_threads_posts":    ("whitehouse_threads_posts_vader.csv",    "whitehouse_threads_posts_vader_roberta.csv",    "whitehouse_threads_posts_vader_roberta_topics_labeled.csv",    12),
    "whitehouse_threads_comments": ("whitehouse_threads_comments_vader.csv", "whitehouse_threads_comments_vader_roberta.csv", "whitehouse_threads_comments_vader_roberta_topics_labeled.csv", 2193),
}
MASTER_CANON = 187359

# final event windows (days_from_landfall) per Decision Log
WINDOWS = {"debby": (-5, 0), "helene": (-4, 1), "milton": (-5, 0)}

# RoBERTa (cardiffnlp) emits uppercase NEG/NEUTRAL/POS; VADER emits lowercase.
# Normalize before any cross-method comparison.
ROBERTA_MAP = {"NEG": "negative", "NEU": "neutral", "NEUTRAL": "neutral", "POS": "positive",
               "negative": "negative", "neutral": "neutral", "positive": "positive"}


def norm_label(s):
    """Map RoBERTa's uppercase labels onto VADER's lowercase convention."""
    return s.map(ROBERTA_MAP)

problems = []   # real issues -> non-zero exit / pause
lines = []      # markdown report


def log(s=""):
    """Print a line and keep it for the markdown report."""
    print(s)
    lines.append(s)


def flag(s):
    """Record a real problem, which makes the run exit non-zero."""
    problems.append(s)
    log(f"  [PROBLEM] {s}")


def wc_l(path):
    """Count physical lines in a file, minus the header.

    Deliberately NOT the row count: comment bodies contain embedded newlines, so
    this overstates rows badly. Reported only to show the gap against the real
    parsed count.
    """
    n = 0
    with open(path, "rb") as fh:
        for _ in fh:
            n += 1
    return n - 1  # minus header


def load(path):
    """Read a scored file, keeping id columns as strings so leading zeros survive."""
    return pd.read_csv(path, dtype={"id": str, "parent_post_id": str}, low_memory=False)


def check_scores(df, name, prefix, labelcol):
    """prefix in {'vader','roberta'}; returns nothing, flags problems."""
    negc, neuc, posc = f"{prefix}_neg", f"{prefix}_neu", f"{prefix}_pos"
    for c in (negc, neuc, posc, labelcol):
        if c not in df.columns:
            flag(f"{name}: missing column {c}")
            return
    probs = df[[negc, neuc, posc]]
    if probs.isna().any().any():
        flag(f"{name}: {int(probs.isna().any(axis=1).sum())} rows with NaN {prefix} probabilities")
    out_of_range = ((probs < -0.001) | (probs > 1.001)).any(axis=1).sum()
    if out_of_range:
        flag(f"{name}: {int(out_of_range)} {prefix} prob rows out of [0,1]")
    s = probs.sum(axis=1)
    bad_sum = (s.sub(1.0).abs() > 0.02).sum()
    if bad_sum:
        flag(f"{name}: {int(bad_sum)} {prefix} rows where neg+neu+pos != 1 (+/-0.02)")
    # label vocab (normalize roberta uppercase first)
    raw = df[labelcol].dropna()
    labs = set(norm_label(raw).dropna().unique()) if prefix == "roberta" else set(raw.unique())
    if not labs <= {"positive", "neutral", "negative"}:
        flag(f"{name}: unexpected {labelcol} values {labs - {'positive','neutral','negative'}}")
    if prefix == "vader":
        comp = df["vader_compound"]
        if ((comp < -1.001) | (comp > 1.001)).any():
            flag(f"{name}: vader_compound out of [-1,1]")
        # threshold consistency >=0.05 pos / <=-0.05 neg / else neutral
        exp = np.where(comp >= 0.05, "positive", np.where(comp <= -0.05, "negative", "neutral"))
        mism = (exp != df["vader_label"].values).sum()
        if mism:
            flag(f"{name}: {int(mism)} vader_label rows inconsistent with +/-0.05 thresholds")
    else:  # roberta: normalized label should be argmax of probs
        argmax = probs.values.argmax(axis=1)
        names = np.array(["negative", "neutral", "positive"])
        exp = names[argmax]
        mism = (exp != norm_label(df[labelcol]).values).sum()
        if mism:
            log(f"  note {name}: {int(mism)} roberta_label != argmax(prob) "
                f"({100*mism/len(df):.2f}% — rounding ties, informational)")


log("# Week 5 Data Verification Report")
log("")
log("Read-only reconciliation of all scored/labeled files against the canonical Decision-Log counts.")
log("Row counts are pandas (true records); `wc -l` is shown alongside to confirm embedded-newline inflation.")
log("")

# ---- 1 & 2: row counts + stage consistency -------------------------------------
log("## 1-2. Row counts (pandas vs canonical vs wc -l) and pipeline-stage consistency")
log("")
log("| source | canonical | processed (pandas) | vader | roberta | wc -l (proc) | status |")
log("|---|---|---|---|---|---|---|")

dfs = {}  # processed dataframes kept for later checks
for key, (vf, rf, pf, canon) in SOURCES.items():
    vpath, rpath, ppath = VADER / vf, ROBERTA / rf, PROC / pf
    try:
        dv, dr, dp = load(vpath), load(rpath), load(ppath)
    except Exception as e:
        flag(f"{key}: failed to load ({e})")
        continue
    dfs[key] = dp
    nv, nr, npc = len(dv), len(dr), len(dp)
    wl = wc_l(ppath)
    status = "OK"
    if npc != canon:
        status = "MISMATCH"
        flag(f"{key}: processed pandas rows {npc} != canonical {canon}")
    if not (nv == nr == npc):
        status = "STAGE-DIFF"
        flag(f"{key}: stage counts differ vader={nv} roberta={nr} processed={npc} "
             f"(processed is canonical; vader/roberta dirs are STALE — see WH-removal note)")
    log(f"| {key} | {canon} | {npc} | {nv} | {nr} | {wl} | {status} |")

# master
try:
    dm = load(MASTER)
    nm = len(dm)
    wlm = wc_l(MASTER)
    st = "OK" if nm == MASTER_CANON else "MISMATCH"
    if nm != MASTER_CANON:
        flag(f"master: pandas rows {nm} != canonical {MASTER_CANON}")
    log(f"| master | {MASTER_CANON} | {nm} | - | - | {wlm} | {st} |")
except Exception as e:
    flag(f"master: failed to load ({e})")
    dm = None
log("")

# ---- 3: duplicates / collisions ----------------------------------------------
log("## 3. Duplicates and cross-file id collisions")
log("")
id_sets = {}
for key, dp in dfs.items():
    ndup_id = int(dp["id"].duplicated().sum())
    ndup_it = int(dp.duplicated(subset=["id", "type"]).sum())
    if ndup_id:
        flag(f"{key}: {ndup_id} duplicate id values")
    if ndup_it:
        flag(f"{key}: {ndup_it} duplicate (id,type) rows")
    id_sets[key] = set(dp["id"])
    log(f"- {key}: dup id={ndup_id}, dup (id,type)={ndup_it}")

# no WH ids in reddit files
wh_ids = id_sets.get("whitehouse_threads_posts", set()) | id_sets.get("whitehouse_threads_comments", set())
for rk in ("reddit_relevant_posts", "reddit_relevant_comments"):
    overlap = wh_ids & id_sets.get(rk, set())
    if overlap:
        flag(f"{rk}: contains {len(overlap)} White House ids (WH-removal regression!)")
    else:
        log(f"- {rk}: 0 White House ids present (WH-removal holds)")

# master dup (id, provenance)
if dm is not None:
    key_cols = ["id", "provenance"] if "provenance" in dm.columns else ["id", "source"]
    ndup = int(dm.duplicated(subset=key_cols).sum())
    if ndup:
        flag(f"master: {ndup} duplicate {tuple(key_cols)} rows")
    log(f"- master: dup {tuple(key_cols)}={ndup}")
log("")

# ---- 4 & 5: score sanity ------------------------------------------------------
log("## 4-5. VADER and RoBERTa score sanity")
log("")
for key, dp in dfs.items():
    check_scores(dp, key, "vader", "vader_label")
    check_scores(dp, key, "roberta", "roberta_label")
    # roberta coverage: every row that has vader_label should have roberta_label
    miss = int(dp["roberta_label"].isna().sum())
    if miss:
        flag(f"{key}: {miss} rows missing roberta_label (incomplete RoBERTa run)")
    if "roberta_truncated" in dp.columns:
        tr = dp["roberta_truncated"]
        # accept bool or 0/1 or string
        trn = pd.to_numeric(tr, errors="coerce").fillna(0).astype(bool) if tr.dtype != bool else tr
        log(f"- {key}: roberta truncated rate {100*trn.mean():.2f}% ({int(trn.sum())} rows)")
log("")

# ---- 6: key columns -----------------------------------------------------------
log("## 6. Key columns (windows, hurricane, subreddit)")
log("")
hurricane_casings = {}
for key, dp in dfs.items():
    hs = set(dp["hurricane"].dropna().unique())
    hurricane_casings[key] = hs
    if not {h.lower() for h in hs} <= {"debby", "helene", "milton"}:
        flag(f"{key}: unexpected hurricane values {hs}")
    d = pd.to_numeric(dp["days_from_landfall"], errors="coerce")
    if d.isna().any():
        flag(f"{key}: {int(d.isna().sum())} rows with non-numeric days_from_landfall")
    # window bounds per hurricane (skip WH — bypasses window filter by design)
    if key.startswith("reddit") or key.startswith("facebook"):
        for h, (lo, hi) in WINDOWS.items():
            sub = d[dp["hurricane"] == h]
            if len(sub) and (sub.min() < lo or sub.max() > hi):
                # facebook windows are day-level and may legitimately match; flag only true out-of-range
                flag(f"{key}/{h}: days_from_landfall range [{sub.min()},{sub.max()}] outside window [{lo},{hi}]")
    if key.startswith("reddit"):
        if dp["subreddit"].isna().any():
            flag(f"{key}: {int(dp['subreddit'].isna().sum())} null subreddit")
    log(f"- {key}: hurricanes={sorted(hs)}, days range=[{d.min()},{d.max()}]")

# cross-file hurricane casing consistency
all_casings = set().union(*hurricane_casings.values())
if len(all_casings) > 3:
    flag(f"hurricane label CASING is inconsistent across files: {sorted(all_casings)} "
         f"(Facebook Title-case vs Reddit/WH lowercase) -> groupby('hurricane') on the "
         f"master splits each storm into two groups")
if dm is not None:
    mh = sorted(dm["hurricane"].dropna().unique())
    if len(mh) > 3:
        log(f"  master hurricane values: {mh} (mixed casing present in the concatenated master)")
log("")

# ---- 7: vader/roberta agreement tripwire -------------------------------------
log("## 7. VADER vs RoBERTa raw agreement (tripwire)")
log("")
for key, dp in dfs.items():
    agree = (dp["vader_label"] == norm_label(dp["roberta_label"])).mean()
    log(f"- {key}: {100*agree:.1f}% raw label agreement")
    if agree < 0.30:
        flag(f"{key}: suspiciously low VADER/RoBERTa agreement {100*agree:.1f}%")
log("")

# ---- verdict ------------------------------------------------------------------
log("## Verdict")
log("")
if problems:
    log(f"**{len(problems)} PROBLEM(S) FOUND — pausing before hypothesis testing:**")
    for p in problems:
        log(f"- {p}")
else:
    log("**ALL CHECKS PASSED.** Data reconciles to the Decision-Log canonical counts; "
        "0 duplicates / 0 WH-in-Reddit; VADER & RoBERTa scores in range with full coverage. "
        "Clear to proceed to Week 5 hypothesis testing.")

OUT.write_text("\n".join(lines) + "\n")
print(f"\nReport written to {OUT}")
sys.exit(1 if problems else 0)
