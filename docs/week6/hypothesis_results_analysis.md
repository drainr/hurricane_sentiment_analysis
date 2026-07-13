# Hypothesis Results — Numbers, Verification, and Brief Interpretation

Jose and Angelo ran the seven hypotheses independently. This document (1) confirms our numbers agree and (2) reports the results per hypothesis with a short note on what each means.

Corpus: 187,359 records (Facebook 60,688 · Reddit 124,466 · White House 2,205) across Debby, Helene, Milton. Two scorers: **VADER** (`compound`) and **RoBERTa** (`pos − neg`), comment-level. At this sample size nearly everything is p < 0.001, so we read **effect sizes** (rank-biserial _r_), not p-values.

## 1. Independent verification — Jose vs Angelo

We wrote our code separately. Every statistic we both compute is identical to floating-point precision:

| Hypothesis | Statistic             | Rows | Max difference | Result    |
| ---------- | --------------------- | ---- | -------------- | --------- |
| H1         | rank-biserial _r_     | 8    | 0.0            | Identical |
| H1         | p-value               | 8    | ~1e-80         | Identical |
| H3         | Facebook–Reddit gap   | 6    | ~1e-16         | Identical |
| H4         | Kruskal-Wallis H      | 40   | 0.0            | Identical |
| H4         | pairwise Bonferroni p | 12   | ~1e-22         | Identical |
| H7         | p-value               | 6    | ~1e-51         | Identical |
| H7         | Levene p              | 6    | ~1e-12         | Identical |

Scope: Angelo's file covers H1/H3/H4/H7; H2 and H5 are Jose's. (An earlier RoBERTa gap was a scoring-convention difference — discrete label vs continuous `pos − neg`; standardized on `pos − neg`, both re-ran, now identical.)

## 2. Results per hypothesis

| H      | Prediction                                         | Key result (effect size)                                             | Verdict                    |
| ------ | -------------------------------------------------- | -------------------------------------------------------------------- | -------------------------- |
| **H1** | Reddit less positive than Facebook                 | RoBERTa _r_ = 0.33 / 0.30 / 0.26 (Debby/Helene/Milton); VADER ≈ 0.12 | **Supported**              |
| **H2** | Reddit declines more steeply toward landfall       | interaction slope +0.004 (RoBERTa), R² ≈ 0                           | **Not supported**          |
| **H3** | FB–Reddit gap larger for stronger storms           | gap 0.32 → 0.29 → 0.24 (Debby→Helene→Milton)                         | **Not supported**          |
| **H4** | Reddit accumulates negativity, FB stable           | across-storm KW sig. both platforms (FB _H_=644 > Reddit 245)        | **Partial**                |
| **H5** | Expert subs more neutral than local/statewide      | RoBERTa sig. all storms; VADER only Milton                           | **Supported (RoBERTa)**    |
| **H6** | FB gratitude/prep vs Reddit forecast/misinfo       | topic analysis (BERTopic), source×topic V = 0.39                     | see topic figures          |
| **H7** | WH more negative/polarized than organic + Phillips | **RoBERTa:** WH vs FB _r_ = −0.44, WH vs Reddit −0.17 (WH mean −0.36). **VADER:** WH mean is _positive_ (+0.02); less positive than FB (_r_ = −0.15) but ≈ Reddit (_r_ = −0.03) | **Supported — negativity is RoBERTa-specific** |

## 3. What the numbers mean (one line each)

- **H1:** Facebook (local-meteorologist audience) is consistently the most positive — our largest, cleanest effect. Part of it is gratitude aimed at the communicator, not the storm.
- **H2:** No "Reddit panics faster" trend; day-level sentiment is essentially flat within the short windows (R² ≈ 0).
- **H3:** The gap _shrinks_ for the stronger later storms — opposite of predicted; intensity and season-order are confounded across only three storms.
- **H4:** Sentiment shifts across storms, but _both_ platforms move (FB more, not less), so it's a general Milton-is-most-negative effect, not Reddit-specific.
- **H5:** Expert weather forums stay calmer than general geographic subs. RoBERTa detects it everywhere; VADER only for Milton (Debby/Helene RoBERTa-only, flag).
- **H7:** The negativity finding is **RoBERTa-specific — it must be labeled as such, not stated as a general result.** Under RoBERTa, reactions to the government account are markedly more negative than organic Reddit and far more negative than Facebook (WH mean −0.36; WH-vs-FB _r_ = −0.44, one of the study's largest effects). Under **VADER the direction does not hold**: WH comments are mildly _positive_ in absolute terms (+0.02 pooled, +0.06 for Milton) — less positive than Facebook (_r_ = −0.15) but essentially even with Reddit (_r_ = −0.03; for Milton VADER even puts WH slightly _above_ Reddit, n.s.). Separately, the "more polarized = higher variance" reading holds under VADER (Levene p=2e-15) but not RoBERTa (p=0.30). Net: H7's **negativity** claim rests on RoBERTa, its **polarization** claim on VADER — neither is a both-methods finding.

## 4. Method note

Against a 400-item human gold standard, **RoBERTa is 72.8% accurate vs VADER's 48.7%** (VADER over-reads politeness as positive). Where the two disagree above, RoBERTa is the more reliable read. Which method leads the paper is still your call.

---

_Sources: `data/merged/hypothesis_tests_all7_jose.csv`, `hypothesis_tests_results_angelo.csv`, `docs/week5/method_validation_report.md`._
