# Method Validation Report (Week 5, Student B)

Gold standard: `ground_truth_400.csv` — 400 stratified items (Facebook 161, Reddit 188, White House 51).
Adjudicated (consensus label present): 400; unresolved annotator disagreements excluded: 0.
Rows matched to a scored record: 400/400

## 1. Accuracy and per-class precision / recall / F1

### VADER — accuracy 0.487 (n=400)

| class | precision | recall | F1 | support |
|---|---|---|---|---|
| negative | 0.448 | 0.465 | 0.456 | 101 |
| neutral | 0.864 | 0.416 | 0.562 | 245 |
| positive | 0.260 | 0.852 | 0.398 | 54 |
| **macro avg** | 0.524 | 0.578 | 0.472 | 400 |
| **weighted avg** | 0.678 | 0.487 | 0.513 | 400 |

Confusion matrix (rows = true, cols = predicted):

| true \ pred | negative | neutral | positive |
|---|---|---|---|
| negative | 47 | 12 | 42 |
| neutral | 54 | 102 | 89 |
| positive | 4 | 4 | 46 |

### RoBERTa — accuracy 0.728 (n=400)

| class | precision | recall | F1 | support |
|---|---|---|---|---|
| negative | 0.588 | 0.792 | 0.675 | 101 |
| neutral | 0.879 | 0.710 | 0.786 | 245 |
| positive | 0.561 | 0.685 | 0.617 | 54 |
| **macro avg** | 0.676 | 0.729 | 0.692 | 400 |
| **weighted avg** | 0.762 | 0.728 | 0.735 | 400 |

Confusion matrix (rows = true, cols = predicted):

| true \ pred | negative | neutral | positive |
|---|---|---|---|
| negative | 80 | 13 | 8 |
| neutral | 50 | 174 | 21 |
| positive | 6 | 11 | 37 |

**Higher accuracy vs gold standard: RoBERTa** (VADER 0.487, RoBERTa 0.728). Note VADER is the project's primary method for continuity with Fall-2024 student work; this is the validation evidence for that decision.

## 2. Gratitude-inflation estimate (Facebook comments)

Facebook comments in gold sample: 150; gratitude-tagged (consensus=1): 15.

Among Facebook comments each method labels **positive**, the fraction carrying the human gratitude tag:

| method | FB comments labeled positive | of those, gratitude-tagged | inflation rate |
|---|---|---|---|
| VADER | 62 | 15 | 24.2% |
| RoBERTa | 42 | 14 | 33.3% |

For reference, among human-labeled-positive FB comments (35), 40.0% are gratitude-tagged.

Interpretation: a non-trivial share of Facebook 'positive' sentiment is gratitude directed at the communicator (thanking Denis Phillips) rather than positive feeling about the storm — so the Facebook–Reddit positivity gap (H1) is partly a person-directed-thanks artifact. Sample is small (gold-standard FB comments only); report as an estimate, not a population rate.
