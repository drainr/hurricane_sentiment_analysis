# Statistical Results Summary — Week 5 (H1–H7 × VADER + RoBERTa)

Comments-level analysis on the canonical `data/processed/*_labeled.csv` files
(FB Phillips = 59,736; Reddit community = 121,053; WH government_response = 2,193).
VADER compound vs RoBERTa (pos − neg). Detail in `hypothesis_tests_results.md`,
`h2_temporal_results.md`, `method_validation_report.md`.

Owner key: **H2, H5** = Student B (Jose). **H1/H3/H4/H7** = Student A (Angelo) hypotheses,
computed here for the 7×2 table + RoBERTa cross-check — reconcile exact framing with Angelo.
**H5 subreddit grouping locked by Tania 2026-06-30 (all 9 community subs in 3 tiers); H5 run — results below.**

See `statistical_results_table.md` for the **formal 7×2 grid** (test statistic / p-value / effect size
per hypothesis×method, incl. Kruskal-Wallis ε² for H4/H5). This file is the interpretive/verdict view.

## Master table

| H                                                | Test                                      | VADER result                                                                                                                                    | RoBERTa result                                                                                                                                | Methods agree?                            |
| ------------------------------------------------ | ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| **H1** Platform diff (FB>Reddit)                 | MWU + χ²                                  | **Supported**: FB 0.170 > Reddit 0.059, U-test p≈0, rank-biserial +0.129; χ² V=0.158                                                            | **Supported (stronger)**: FB 0.048 > Reddit −0.232, p≈0, r=+0.295; χ² V=0.224                                                                 | ✅ yes                                    |
| **H2** Temporal decline (Reddit steeper)         | OLS slopes + interaction                  | **Not supported**: interaction (Reddit−FB) +0.0054, p=6e-4 (Reddit declines _less_); R²≈0                                                       | **Not supported**: interaction +0.0036, p=0.045; R²≈0                                                                                         | ✅ yes (both reject)                      |
| **H3** Gap grows with intensity (Debby smallest) | gap by storm                              | **Not supported**: gaps 0.113 / 0.114 / 0.096 (Debby not smallest)                                                                              | **Not supported**: 0.318 / 0.286 / 0.240 (gap _shrinks_ Debby→Milton)                                                                         | ✅ yes (both reject)                      |
| **H4** Cross-storm shift within platform         | Kruskal-Wallis + pairwise                 | **Partial** — test significant both platforms (Reddit H=116 p≈8e-26; FB H=249 p≈1e-54) but mechanism fails: Milton most negative and FB shifts _more_ than Reddit, not the predicted "Reddit accumulates / FB stable" | **Partial** — significant (Reddit H=245; FB H=644 p≈1e-140), same pattern, FB shift larger                                                    | ✅ direction agrees                       |
| **H5** Subreddit tiers (expert/local/statewide)  | KW + pairwise, per storm, ±largest-thread | **Mixed**: Milton sig; Debby n.s. on full data (→ sig when largest threads excluded); Helene n.s. both ways                                     | **Significant all three storms** both variants                                                                                                | ⚠ disagree on Debby & Helene              |
| **H7** WH polarization                           | MWU + Levene's                            | **Partial**: WH (0.024) < Reddit (0.059) p=9e-3 r=−0.03; WH > variance (Levene p=2e-15); WH < FB p≈0; WH political < non (p=0.02)               | **Partial/strong**: WH (−0.363) < Reddit (−0.232) p≈0 r=−0.17; variance ≈ equal (Levene p=0.30); WH ≪ FB r=−0.44; political ≪ non p≈0 r=−0.16 | ⚠ mostly (variance/polarization diverges) |

## RoBERTa cross-check — agreements & divergences

- **Agreements (all qualitative conclusions match):** H1 supported, H2 rejected, H3 rejected, H4 partial (significant across-storm shift both platforms, same Debby→Milton direction, but FB moves more than Reddit so the "Reddit accumulates / FB stable" mechanism fails), H7 WH more negative than both Reddit and Facebook and political WH comments more negative than non-political. The two methods agree on **every hypothesis verdict** computed so far.
- **Systematic offset:** RoBERTa scores the whole corpus more negatively than VADER (e.g. Reddit mean −0.232 vs +0.059), because VADER over-labels _positive_ (validated below). This shifts levels but not the between-group **directions**, so the hypothesis verdicts are robust to method choice.
- **One genuine divergence (H7 polarization mechanism):** VADER finds WH comment **variance** significantly higher than Reddit (Levene p=2e-15) — the "polarization" reading; RoBERTa finds variance essentially equal (p=0.30). Under RoBERTa, H7's signal is a strong **negativity shift**, not a variance/polarization difference. Report both; the polarization claim is method-dependent, the negativity claim is not.

## Method validation vs gold standard (`ground_truth_400`, all 400 adjudicated)

|         | Accuracy  | Macro-F1 | Notes                                                                      |
| ------- | --------- | -------- | -------------------------------------------------------------------------- |
| VADER   | **0.487** | 0.472    | over-predicts positive (P=0.260, R=0.852); under-recalls neutral (R=0.416) |
| RoBERTa | **0.728** | 0.692    | better on every class                                                      |

RoBERTa is substantially more accurate against the human gold standard. VADER remains the
project's _primary_ method for Fall-2024 continuity, but this is the evidence for the
primary-method decision to settle with Tania, and it explains H1/H3 level differences
(VADER's positive bias inflates Facebook).

## Gratitude inflation (Facebook comments, gold sample n=150)

Of FB comments each method labels positive, the share that are person-directed gratitude
(thanking the communicator, not positive about the storm): **VADER 24.2%, RoBERTa 33.3%**
(40% among human-positive). So part of the Facebook–Reddit positivity gap (H1) is a
gratitude-toward-Phillips artifact rather than positive storm sentiment.

## H5 detail (`h5_subreddit_results.md`)

Nine community subreddits in three tiers (expert=TropicalWeather/hurricane/HurricaneHelene,
local=tampa/sarasota/asheville, statewide=florida/Georgia/NorthCarolina); per hurricane;
KW + pairwise Bonferroni; both methods; ± largest-thread-per-subreddit. Effect sizes are
small throughout (rank-biserial ≈ 0.02–0.17). **Milton robust** (sig both methods/variants).
**Debby & Helene flagged**: VADER n.s. where RoBERTa is significant, and Debby's VADER verdict
flips to significant once the largest threads are removed — to discuss with Tania before the
paper, per her rule. Confirmed the four excluded subs (southcarolina/Tennessee/Virginia/pics)
are 0 rows in the H5 corpus (WH-only, government_response).
