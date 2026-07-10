# F6 — VADER vs RoBERTa Agreement

3×3 confusion matrix of `vader_label` × `roberta_label` over all six scored files (187,359 records with both labels).

**Overall agreement (diagonal): 54.7%** (102,483 / 187,359).

Confusion matrix (rows = VADER, cols = RoBERTa; count / % of total):

| VADER \\ RoBERTa | Negative       | Neutral        | Positive       | row total |
| ---------------- | -------------- | -------------- | -------------- | --------- |
| Negative         | 34,544 (18.4%) | 14,923 (8.0%)  | 1,270 (0.7%)   | 50,737    |
| Neutral          | 10,726 (5.7%)  | 42,154 (22.5%) | 3,313 (1.8%)   | 56,193    |
| Positive         | 19,306 (10.3%) | 35,338 (18.9%) | 25,785 (13.8%) | 80,429    |
| **col total**    | 64,576         | 92,415         | 30,368         | 187,359   |

Per-class agreement (VADER label = RoBERTa label, of VADER rows in that class):

- negative: 68.1% (34,544/50,737)
- neutral: 75.0% (42,154/56,193)
- positive: 32.1% (25,785/80,429)

Figure: `figures/f6_vader_roberta_agreement.png/.pdf` (300 dpi).
