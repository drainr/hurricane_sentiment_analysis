# Statistical Results Table — 7 hypotheses × 2 methods (Week 5)

Formal companion to `statistical_results_summary.md`. Comment-level; FB=Phillips, Reddit=community, WH=government_response. Effect sizes: rank-biserial (MWU), Cramér's V (χ²), ε² (Kruskal-Wallis omnibus; small≈0.01, medium≈0.06, large≈0.14), R²/β (OLS). Note: at n=60k–120k, p-values are near-zero everywhere — **effect sizes are the meaningful column.**

| Hypothesis / test | Method | Test | Statistic | p | Effect size |
|---|---|---|---|---|---|
| H1 platform (overall) | VADER | Mann-Whitney U | U=4.08e+09 | <1e-300 | rank-biserial +0.129 |
| H1 platform×label | VADER | Chi-square | χ²(2)=4492 | <1e-300 | Cramér's V 0.158 |
| H2 temporal (interaction) | VADER | OLS interaction | β=+0.00535 | 6.13e-04 | R²=0.0137 |
| H3 intensity gap | VADER | Descriptive (gap order) | gaps D/H/M=0.113/0.114/0.096 | — | Debby not smallest → n.s. |
| H4 cross-storm (Reddit) | VADER | Kruskal-Wallis | H=115.6 | 7.80e-26 | ε²=0.0009 |
| H4 cross-storm (Facebook) | VADER | Kruskal-Wallis | H=248.7 | 1.01e-54 | ε²=0.0041 |
| H5 tiers (debby) | VADER | Kruskal-Wallis | H=0.1 | 9.68e-01 | ε²=-0.0002 |
| H5 tiers (helene) | VADER | Kruskal-Wallis | H=1.7 | 4.20e-01 | ε²=-0.0000 |
| H5 tiers (milton) | VADER | Kruskal-Wallis | H=38.3 | 4.80e-09 | ε²=0.0005 |
| H7 WH vs Reddit | VADER | MWU (+ Levene) | U=1.28e+08; Levene W=62.7 (p=2.4e-15) | 8.56e-03 | rank-biserial -0.032 |
| H7 WH vs FB | VADER | Mann-Whitney U | U=5.55e+07 | 2.04e-35 | rank-biserial -0.152 |
| H7 WH political vs not | VADER | Mann-Whitney U | U=4.67e+05 | 1.72e-02 | rank-biserial -0.064 |
| H1 platform (overall) | RoBERTa | Mann-Whitney U | U=4.68e+09 | <1e-300 | rank-biserial +0.295 |
| H1 platform×label | RoBERTa | Chi-square | χ²(2)=9060 | <1e-300 | Cramér's V 0.224 |
| H2 temporal (interaction) | RoBERTa | OLS interaction | β=+0.00364 | 4.54e-02 | R²=0.0604 |
| H3 intensity gap | RoBERTa | Descriptive (gap order) | gaps D/H/M=0.318/0.286/0.240 | — | Debby not smallest → n.s. |
| H4 cross-storm (Reddit) | RoBERTa | Kruskal-Wallis | H=245.1 | 5.95e-54 | ε²=0.0020 |
| H4 cross-storm (Facebook) | RoBERTa | Kruskal-Wallis | H=644.0 | 1.41e-140 | ε²=0.0107 |
| H5 tiers (debby) | RoBERTa | Kruskal-Wallis | H=39.9 | 2.19e-09 | ε²=0.0043 |
| H5 tiers (helene) | RoBERTa | Kruskal-Wallis | H=35.1 | 2.41e-08 | ε²=0.0010 |
| H5 tiers (milton) | RoBERTa | Kruskal-Wallis | H=904.3 | 4.29e-197 | ε²=0.0114 |
| H7 WH vs Reddit | RoBERTa | MWU (+ Levene) | U=1.1e+08; Levene W=1.1 (p=3.0e-01) | 6.51e-44 | rank-biserial -0.173 |
| H7 WH vs FB | RoBERTa | Mann-Whitney U | U=3.69e+07 | 1.04e-264 | rank-biserial -0.436 |
| H7 WH political vs not | RoBERTa | Mann-Whitney U | U=4.17e+05 | 1.69e-09 | rank-biserial -0.163 |
