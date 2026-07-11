# Method Validation Report (Week 5, Student B)

**Authored by Jose Araya. Reviewed and confirmed by Jose Araya, 2026-07-10.**

Gold standard: `data/merged/ground_truth_400.csv` — 400 stratified items (Facebook 161, Reddit 188, White House 51).
Scoring / comparison script: `code/week5_hypotheses/evaluate_methods.py` (joins the gold standard to the scored `data/processed/*_labeled.csv` records and computes the accuracy / per-class P-R-F1 / confusion / gratitude-inflation numbers below).
Adjudicated (consensus label present): 400; unresolved annotator disagreements excluded: 0.
Rows matched to a scored record: 400/400

## 1. Accuracy and per-class precision / recall / F1

### VADER — accuracy 0.487 (n=400)

| class            | precision | recall | F1    | support |
| ---------------- | --------- | ------ | ----- | ------- |
| negative         | 0.448     | 0.465  | 0.456 | 101     |
| neutral          | 0.864     | 0.416  | 0.562 | 245     |
| positive         | 0.260     | 0.852  | 0.398 | 54      |
| **macro avg**    | 0.524     | 0.578  | 0.472 | 400     |
| **weighted avg** | 0.678     | 0.487  | 0.513 | 400     |

Confusion matrix (rows = true, cols = predicted):

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 47       | 12      | 42       |
| neutral     | 54       | 102     | 89       |
| positive    | 4        | 4       | 46       |

### RoBERTa — accuracy 0.728 (n=400)

| class            | precision | recall | F1    | support |
| ---------------- | --------- | ------ | ----- | ------- |
| negative         | 0.588     | 0.792  | 0.675 | 101     |
| neutral          | 0.879     | 0.710  | 0.786 | 245     |
| positive         | 0.561     | 0.685  | 0.617 | 54      |
| **macro avg**    | 0.676     | 0.729  | 0.692 | 400     |
| **weighted avg** | 0.762     | 0.728  | 0.735 | 400     |

Confusion matrix (rows = true, cols = predicted):

| true \ pred | negative | neutral | positive |
| ----------- | -------- | ------- | -------- |
| negative    | 80       | 13      | 8        |
| neutral     | 50       | 174     | 21       |
| positive    | 6        | 11      | 37       |

**Higher accuracy vs gold standard: RoBERTa, on every metric.** RoBERTa beats VADER on overall accuracy (0.728 vs 0.487), macro-F1 (0.692 vs 0.472), and precision, recall, and F1 for *all three* classes. VADER's core failure is positive precision (0.260): it reads politeness and gratitude as positive, over-predicting the positive class (recall 0.852 but precision 0.260) and under-recalling neutral (0.416).

**Primary-method decision — an explicit tradeoff, not a data endorsement of VADER.** The data does not support keeping VADER as primary; only continuity does. The two considerations point in opposite directions:

- **Continuity (favors VADER):** VADER was the Fall-2024 students' scorer, so keeping it primary makes this season's numbers directly comparable to that prior work with no re-baselining.
- **Accuracy (favors RoBERTa):** RoBERTa is measurably more accurate against the human gold standard — every class, every metric — and does not carry VADER's positive bias (which also inflates the Facebook side of H1/H3).

This is a value judgment (comparability vs. correctness) for Tania to settle, and should be stated as such wherever the primary method is named — not framed as "the data supports VADER." Our recommendation: **lead with RoBERTa as the primary reported scorer and carry VADER as the continuity baseline / cross-check.**

## 2. Gratitude-inflation estimate (Facebook comments)

Facebook comments in gold sample: 150; gratitude-tagged (consensus=1): 15.

Among Facebook comments each method labels **positive**, the fraction carrying the human gratitude tag:

| method  | FB comments labeled positive | of those, gratitude-tagged | inflation rate |
| ------- | ---------------------------- | -------------------------- | -------------- |
| VADER   | 62                           | 15                         | 24.2%          |
| RoBERTa | 42                           | 14                         | 33.3%          |

For reference, among human-labeled-positive FB comments (35), 40.0% are gratitude-tagged.
