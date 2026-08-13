# F3 — Three-Way Source Comparison (comment-level)

Grouped bars: mean sentiment by source × hurricane, 95% CI error bars, FB–Reddit significance stars from H1 (per hurricane). WH has no Debby data.
RoBERTa uses continuous `pos - neg`. H7 (WH vs FB / WH vs Reddit) is pooled across storms — see `hypothesis_tests_all7_jose.csv`.

## VADER
| source | hurricane | n | mean | 95% CI± | FB-vs-Reddit (H1) |
|---|---|---|---|---|---|
| Facebook | debby | 16,199 | +0.1990 | 0.0061 |  |
| Reddit community | debby | 8,766 | +0.0864 | 0.0098 | *** |
| Facebook | helene | 14,229 | +0.1922 | 0.0064 |  |
| Reddit community | helene | 32,948 | +0.0780 | 0.0050 | *** |
| White House | helene | 1,963 | +0.0196 | 0.0227 |  |
| Facebook | milton | 29,308 | +0.1439 | 0.0046 |  |
| Reddit community | milton | 79,339 | +0.0480 | 0.0033 | *** |
| White House | milton | 230 | +0.0624 | 0.0700 |  |

## RoBERTa
| source | hurricane | n | mean | 95% CI± | FB-vs-Reddit (H1) |
|---|---|---|---|---|---|
| Facebook | debby | 16,199 | +0.1145 | 0.0086 |  |
| Reddit community | debby | 8,766 | -0.2033 | 0.0108 | *** |
| Facebook | helene | 14,229 | +0.0866 | 0.0088 |  |
| Reddit community | helene | 32,948 | -0.1994 | 0.0055 | *** |
| White House | helene | 1,963 | -0.3744 | 0.0224 |  |
| Facebook | milton | 29,308 | -0.0082 | 0.0062 |  |
| Reddit community | milton | 79,339 | -0.2481 | 0.0035 | *** |
| White House | milton | 230 | -0.2676 | 0.0725 |  |

Figures: `figures/f3_three_way_{vader,roberta}.png/.pdf` (300 dpi).

Status: **built (VADER + RoBERTa).**
