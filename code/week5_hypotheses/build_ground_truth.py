"""
build_ground_truth.py
Merge the two independent annotator files (Jose, Angelo) into a single
ground-truth file and compute inter-annotator agreement.

Week 4 deliverables produced:
  - data/merged/ground_truth_400.csv  (both annotators + resolved consensus)
  - docs/week4/interannotator_kappa.md      (Cohen's kappa, sentiment + gratitude tag)

Consensus rule: where the two annotators agree, that value is the consensus.
Where they disagree, the consensus is left blank and flagged for Jose + Angelo
to adjudicate together -- we do not fabricate a tie-break.

Pre-committed rule (from the research plan): if kappa < 0.5, flag for advisor.
"""

import os
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MERGED = os.path.join(ROOT, "data", "merged")
DOCS = os.path.join(ROOT, "docs", "week4")
os.makedirs(DOCS, exist_ok=True)

JOSE = os.path.join(MERGED, "manual_label_sample_jose.csv")
ANGELO = os.path.join(MERGED, "manual_label_sample_angelo.csv")
OUT_CSV = os.path.join(MERGED, "ground_truth_400.csv")
OUT_MD = os.path.join(DOCS, "interannotator_kappa.md")

KAPPA_FLAG = 0.5  # below this -> flag for advisor
LABELS = ["negative", "neutral", "positive"]


def load(path):
    """Load one annotator's labels, lowercasing sentiment and coercing the gratitude tag."""
    df = pd.read_csv(path)
    df["label"] = df["label"].astype(str).str.strip().str.lower()
    df["gratitude_tag"] = pd.to_numeric(df["gratitude_tag"], errors="coerce").astype(int)
    return df


def main():
    """Merge both annotators' labels into ground_truth_400.csv and report kappa.

    Consensus is filled only where the two agree; disagreements are left blank
    for joint adjudication rather than resolved automatically. See the guard
    below — the adjudicated file must not be silently rebuilt.
    """
    jose = load(JOSE)
    angelo = load(ANGELO)

    # alignment is guaranteed identical (same sample), but assert it
    assert list(jose["id"]) == list(angelo["id"]), "annotator id order mismatch"

    gt = jose[["id", "platform", "type", "text"]].copy()
    gt["label_jose"] = jose["label"].values
    gt["gratitude_jose"] = jose["gratitude_tag"].values
    gt["label_angelo"] = angelo["label"].values
    gt["gratitude_angelo"] = angelo["gratitude_tag"].values

    gt["label_agree"] = (gt["label_jose"] == gt["label_angelo"]).astype(int)
    gt["gratitude_agree"] = (gt["gratitude_jose"] == gt["gratitude_angelo"]).astype(int)

    # consensus only where they agree; blank (adjudication needed) otherwise
    gt["label_consensus"] = gt["label_jose"].where(gt["label_agree"] == 1, "")
    gt["gratitude_consensus"] = gt["gratitude_jose"].where(
        gt["gratitude_agree"] == 1, ""
    )

    cols = [
        "id", "platform", "type", "text",
        "label_jose", "gratitude_jose",
        "label_angelo", "gratitude_angelo",
        "label_consensus", "gratitude_consensus",
        "label_agree", "gratitude_agree",
    ]
    gt = gt[cols]

    # Guard added in the Week 8 re-run. This script only fills label_consensus
    # where the two annotators already agree; the 38 sentiment + 4 gratitude
    # disagreements were adjudicated by hand afterwards (José + Angelo). Blindly
    # rewriting the file therefore DELETES that adjudication and silently drops
    # the gold standard from 400 rows to 362. If an adjudicated file is already
    # on disk, refuse and let the caller decide.
    if os.path.exists(OUT_CSV) and not os.environ.get("REBUILD_GROUND_TRUTH"):
        existing = pd.read_csv(OUT_CSV, encoding="utf-8", encoding_errors="replace")
        # count blanks the way they land after a CSV round-trip ("" -> NaN)
        would_blank = int(gt["label_consensus"].replace("", pd.NA).isna().sum())
        if existing["label_consensus"].notna().all():
            raise SystemExit(
                f"REFUSING to overwrite {OUT_CSV}: it is fully adjudicated "
                f"({len(existing)} rows, 0 blank consensus labels) and this script "
                f"would blank the {would_blank} adjudicated disagreements again. "
                f"Set REBUILD_GROUND_TRUTH=1 to rebuild from scratch, but the "
                f"adjudication must then be re-applied by hand."
            )

    gt.to_csv(OUT_CSV, index=False, encoding="utf-8")

    # ----- agreement metrics -----
    n = len(gt)
    lab_raw = gt["label_agree"].mean()
    grat_raw = gt["gratitude_agree"].mean()
    lab_k = cohen_kappa_score(gt["label_jose"], gt["label_angelo"], labels=LABELS)
    grat_k = cohen_kappa_score(gt["gratitude_jose"], gt["gratitude_angelo"], labels=[0, 1])

    lab_cm = confusion_matrix(gt["label_jose"], gt["label_angelo"], labels=LABELS)
    grat_cm = confusion_matrix(gt["gratitude_jose"], gt["gratitude_angelo"], labels=[0, 1])

    n_label_disagree = int((gt["label_agree"] == 0).sum())
    n_grat_disagree = int((gt["gratitude_agree"] == 0).sum())

    def interp(k):
        """Landis & Koch strength label for a kappa value."""
        # Landis & Koch
        if k < 0: return "Poor"
        if k < 0.20: return "Slight"
        if k < 0.40: return "Fair"
        if k < 0.60: return "Moderate"
        if k < 0.80: return "Substantial"
        return "Almost perfect"

    # per-stratum kappa where n is large enough
    strata_lines = []
    for (plat, typ), sub in gt.groupby(["platform", "type"]):
        if len(sub) < 20:
            strata_lines.append(f"| {plat} {typ} | {len(sub)} | n/a (n<20) | {sub['label_agree'].mean():.3f} |")
            continue
        try:
            k = cohen_kappa_score(sub["label_jose"], sub["label_angelo"], labels=LABELS)
            kstr = f"{k:.4f} ({interp(k)})"
        except Exception:
            kstr = "n/a"
        strata_lines.append(f"| {plat} {typ} | {len(sub)} | {kstr} | {sub['label_agree'].mean():.3f} |")

    flagged = lab_k < KAPPA_FLAG or grat_k < KAPPA_FLAG

    def cm_md(cm, labels):
        """Format a confusion matrix as a markdown table."""
        labels = [str(x) for x in labels]
        head = "| Jose \\ Angelo | " + " | ".join(labels) + " |"
        sep = "|" + "---|" * (len(labels) + 1)
        body = "\n".join(
            "| " + str(labels[i]) + " | " + " | ".join(str(x) for x in row) + " |"
            for i, row in enumerate(cm)
        )
        return f"{head}\n{sep}\n{body}"

    md = f"""# Inter-Annotator Agreement (Cohen's kappa) -- Week 4

_Two independent annotators (Jose, Angelo) over the stratified 400-item sample.
This measures **annotator-vs-annotator** agreement on the human gold standard.
It is distinct from `data/roberta/agreement_metrics.txt`, which measures
VADER-vs-RoBERTa (Week 3)._

- Items: **{n}**
- Pre-committed flag rule: kappa < {KAPPA_FLAG} -> flag for advisor.

## Headline

| Variable | Raw agreement | Cohen's kappa | Interpretation | Below {KAPPA_FLAG}? |
|---|---|---|---|---|
| Sentiment label (3-class) | {lab_raw:.3f} | **{lab_k:.4f}** | {interp(lab_k)} | {"**YES**" if lab_k < KAPPA_FLAG else "no"} |
| Gratitude tag (binary) | {grat_raw:.3f} | **{grat_k:.4f}** | {interp(grat_k)} | {"**YES**" if grat_k < KAPPA_FLAG else "no"} |

{"> **FLAG FOR TANIA:** at least one kappa is below " + str(KAPPA_FLAG) + ". Per the plan, surface this before relying on the gold standard. Disagreements still need joint adjudication (see below)." if flagged else "> Both kappas meet the 0.5 threshold."}

## Disagreements to adjudicate (Jose + Angelo)

- Sentiment label disagreements: **{n_label_disagree}** of {n}
- Gratitude tag disagreements: **{n_grat_disagree}** of {n}

In `ground_truth_400.csv` these rows have an empty `label_consensus` /
`gratitude_consensus` and `*_agree = 0`. Resolve them jointly; do not auto-pick.

## Confusion matrix -- sentiment label

{cm_md(lab_cm, LABELS)}

## Confusion matrix -- gratitude tag

{cm_md(grat_cm, [0, 1])}

## Per-stratum sentiment kappa

| Stratum | n | Cohen's kappa | Raw agreement |
|---|---|---|---|
{chr(10).join(strata_lines)}

---
_Generated by `code/jose araya/build_ground_truth.py`._
"""
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"Wrote {OUT_CSV} ({n} rows)")
    print(f"Wrote {OUT_MD}")
    print(f"Sentiment kappa = {lab_k:.4f} ({interp(lab_k)}); raw {lab_raw:.3f}; "
          f"{n_label_disagree} disagreements")
    print(f"Gratitude kappa = {grat_k:.4f} ({interp(grat_k)}); raw {grat_raw:.3f}; "
          f"{n_grat_disagree} disagreements")
    print(f"FLAGGED (<{KAPPA_FLAG}): {flagged}")


if __name__ == "__main__":
    main()
