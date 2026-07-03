# Hypothesis Testing Results

Results generated from the VADER and RoBERTa sentiment files in the repository.

## H1: Platform difference

### Mann-Whitney U and rank-biserial effect size

| model | subset | U | p-value | rank-biserial |
| --- | --- | ---: | ---: | ---: |
| vader | overall | 4080853682.500 | 0.000e+00 | 0.129 |
| vader | debby | 80092146.000 | 1.059e-64 | 0.128 |
| vader | helene | 266146258.000 | 6.920e-124 | 0.135 |
| vader | milton | 1288405580.500 | 3.624e-169 | 0.108 |
| roberta | overall | 4516904342.000 | 0.000e+00 | 0.249 |
| roberta | debby | 90482436.000 | 0.000e+00 | 0.274 |
| roberta | helene | 295164967.500 | 0.000e+00 | 0.259 |
| roberta | milton | 1417607885.500 | 0.000e+00 | 0.219 |

### Chi-square on platform × sentiment label

| model | subset | chi-square | p-value |
| --- | --- | ---: | ---: |
| vader | overall | 4492.446 | 0.000e+00 |
| roberta | overall | 9059.514 | 0.000e+00 |

## H3: Storm intensity interaction

| hurricane | mean Facebook-Reddit gap | bootstrap p-value | 95% CI |
| --- | ---: | ---: | --- |
| debby | 0.113 | 0.000e+00 | [0.101, 0.124] |
| helene | 0.114 | 0.000e+00 | [0.106, 0.122] |
| milton | 0.096 | 0.000e+00 | [0.090, 0.102] |

- debby_vs_helene: observed gap difference = 0.002; bootstrap p = 0.000e+00
- debby_vs_milton: observed gap difference = -0.017; bootstrap p = 0.000e+00

## H4: Sequential exposure

| platform | test | stat | p-value | details |
| --- | --- | ---: | ---: | --- |
| reddit | Kruskal-Wallis | 115.626 | 7.801e-26 | 3 storms |
| reddit | pairwise MW | 146253421.000 | 6.365e-02 | debby vs helene (Bonferroni p = 1.909e-01) |
| reddit | pairwise MW | 363841188.500 | 7.027e-13 | debby vs milton (Bonferroni p = 2.108e-12) |
| reddit | pairwise MW | 1351704726.500 | 8.540e-20 | helene vs milton (Bonferroni p = 2.562e-19) |
| facebook | Kruskal-Wallis | 248.658 | 1.011e-54 | 3 storms |
| facebook | pairwise MW | 116522777.500 | 8.803e-02 | debby vs helene (Bonferroni p = 2.641e-01) |
| facebook | pairwise MW | 255662608.500 | 2.512e-44 | debby vs milton (Bonferroni p = 7.537e-44) |
| facebook | pairwise MW | 222473765.500 | 2.361e-31 | helene vs milton (Bonferroni p = 7.083e-31) |

## H7: Government communication

| comparison | statistic | p-value | details |
| --- | ---: | ---: | --- |
| WH comments vs Reddit community | U = 128427604.500; Levene statistic = 62.722 | p(U) = 8.559e-03; p(Levene) = 2.400e-15 | variance/polarization check |
| WH comments vs Phillips Facebook | U = 55524380.000 | p = 2.043e-35 | direct platform comparison |
| WH comments with political keywords vs without | U = 466718.000 | p = 1.716e-02 | n(keyword) = 644; n(non-keyword) = 1549 |
