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
| roberta | overall | 4683262619.000 | 0.000e+00 | 0.295 |
| roberta | debby | 94042964.500 | 0.000e+00 | 0.325 |
| roberta | helene | 305703713.500 | 0.000e+00 | 0.304 |
| roberta | milton | 1464275249.000 | 0.000e+00 | 0.259 |

### Chi-square on platform × sentiment label

| model | subset | chi-square | p-value |
| --- | --- | ---: | ---: |
| vader | overall | 4492.446 | 0.000e+00 |
| roberta | overall | 9059.514 | 0.000e+00 |

## H2: Temporal trajectory (OLS)

### OLS regression: compound ~ days_from_landfall

| model | subset | platform | N | slope (per day) | 95% CI | p | R² |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| vader | overall | facebook | 59736 | -0.00279 | [-0.00500, -0.00057] | 1.364e-02 | 0.0001 |
| vader | overall | reddit | 121053 | +0.00256 | [+0.00068, +0.00444] | 7.495e-03 | 0.0001 |
| vader | debby | facebook | 16199 | -0.01370 | [-0.01800, -0.00941] | 3.989e-10 | 0.0024 |
| vader | debby | reddit | 8766 | -0.00663 | [-0.01384, +0.00057] | 7.124e-02 | 0.0004 |
| vader | helene | facebook | 14229 | -0.00814 | [-0.01374, -0.00254] | 4.405e-03 | 0.0006 |
| vader | helene | reddit | 32948 | -0.01617 | [-0.02033, -0.01200] | 2.929e-14 | 0.0018 |
| vader | milton | facebook | 29308 | +0.00642 | [+0.00331, +0.00954] | 5.371e-05 | 0.0006 |
| vader | milton | reddit | 79339 | +0.00488 | [+0.00234, +0.00742] | 1.682e-04 | 0.0002 |
| roberta | overall | facebook | 59736 | +0.00436 | [+0.00132, +0.00741] | 4.990e-03 | 0.0001 |
| roberta | overall | reddit | 121053 | +0.00800 | [+0.00597, +0.01003] | 1.086e-14 | 0.0005 |
| roberta | debby | facebook | 16199 | -0.02290 | [-0.02900, -0.01680] | 1.996e-13 | 0.0033 |
| roberta | debby | reddit | 8766 | -0.00512 | [-0.01305, +0.00281] | 2.060e-01 | 0.0002 |
| roberta | helene | facebook | 14229 | -0.01086 | [-0.01859, -0.00313] | 5.877e-03 | 0.0005 |
| roberta | helene | reddit | 32948 | -0.02234 | [-0.02698, -0.01769] | 4.641e-21 | 0.0027 |
| roberta | milton | facebook | 29308 | +0.03022 | [+0.02607, +0.03437] | 4.995e-46 | 0.0069 |
| roberta | milton | reddit | 79339 | +0.01230 | [+0.00960, +0.01500] | 4.601e-19 | 0.0010 |

### Interaction model: compound ~ days_from_landfall × platform

| model | subset | interaction coef (reddit − facebook slope) | interaction p | R² |
| --- | --- | ---: | ---: | ---: |
| vader | overall | +0.00535 | 6.133e-04 | 0.0137 |
| roberta | overall | +0.00364 | 4.537e-02 | 0.0604 |

## H3: Storm intensity interaction

| model | hurricane | mean Facebook-Reddit gap | bootstrap p-value | 95% CI |
| --- | --- | ---: | ---: | --- |
| vader | debby | 0.113 | 0.000e+00 | [0.101, 0.124] |
| vader | helene | 0.114 | 0.000e+00 | [0.106, 0.122] |
| vader | milton | 0.096 | 0.000e+00 | [0.090, 0.101] |
| roberta | debby | 0.318 | 0.000e+00 | [0.304, 0.331] |
| roberta | helene | 0.286 | 0.000e+00 | [0.276, 0.296] |
| roberta | milton | 0.240 | 0.000e+00 | [0.233, 0.247] |


## H4: Sequential exposure

| model | platform | test | stat | p-value | details |
| --- | --- | --- | ---: | ---: | --- |
| vader | reddit | Kruskal-Wallis | 115.626 | 7.801e-26 | 3 storms |
| vader | reddit | pairwise MW | 146253421.000 | 6.365e-02 | debby vs helene (Bonferroni p = 1.909e-01) |
| vader | reddit | pairwise MW | 363841188.500 | 7.027e-13 | debby vs milton (Bonferroni p = 2.108e-12) |
| vader | reddit | pairwise MW | 1351704726.500 | 8.540e-20 | helene vs milton (Bonferroni p = 2.562e-19) |
| vader | facebook | Kruskal-Wallis | 248.658 | 1.011e-54 | 3 storms |
| vader | facebook | pairwise MW | 116522777.500 | 8.803e-02 | debby vs helene (Bonferroni p = 2.641e-01) |
| vader | facebook | pairwise MW | 255662608.500 | 2.512e-44 | debby vs milton (Bonferroni p = 7.537e-44) |
| vader | facebook | pairwise MW | 222473765.500 | 2.361e-31 | helene vs milton (Bonferroni p = 7.083e-31) |
| roberta | reddit | Kruskal-Wallis | 245.111 | 5.953e-54 | 3 storms |
| roberta | reddit | pairwise MW | 143617150.000 | 4.282e-01 | debby vs helene (Bonferroni p = 1.000e+00) |
| roberta | reddit | pairwise MW | 365092500.000 | 1.619e-14 | debby vs milton (Bonferroni p = 4.857e-14) |
| roberta | reddit | pairwise MW | 1380014097.500 | 2.784e-49 | helene vs milton (Bonferroni p = 8.353e-49) |
| roberta | facebook | Kruskal-Wallis | 644.042 | 1.406e-140 | 3 storms |
| roberta | facebook | pairwise MW | 118999650.500 | 9.223e-07 | debby vs helene (Bonferroni p = 2.767e-06) |
| roberta | facebook | pairwise MW | 268575977.000 | 1.453e-119 | debby vs milton (Bonferroni p = 4.358e-119) |
| roberta | facebook | pairwise MW | 229886450.500 | 1.231e-67 | helene vs milton (Bonferroni p = 3.694e-67) |

## H5: Reddit subreddit-category differences

Subreddit mapping — expert: r/TropicalWeather; local: r/tampa, r/sarasota; statewide: r/florida.

| model | subset | variant | test | category A | category B | statistic | p-value | Bonferroni p | rank-biserial |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| vader | debby | full | Kruskal-Wallis | — | — | H = 2.112 | 3.479e-01 | — | — |
| vader | debby | excl_largest_thread | Kruskal-Wallis | — | — | H = 24.390 | 5.056e-06 | — | — |
| vader | debby | excl_largest_thread | pairwise MW | expert | local | U = 413883.000 | 9.497e-02 | 2.849e-01 | 0.045 |
| vader | debby | excl_largest_thread | pairwise MW | expert | statewide | U = 1281496.000 | 3.236e-06 | 9.708e-06 | 0.104 |
| vader | debby | excl_largest_thread | pairwise MW | local | statewide | U = 1267279.500 | 6.288e-03 | 1.886e-02 | 0.060 |
| vader | helene | full | Kruskal-Wallis | — | — | H = 2.920 | 2.323e-01 | — | — |
| vader | helene | excl_largest_thread | Kruskal-Wallis | — | — | H = 13.244 | 1.331e-03 | — | — |
| vader | milton | full | Kruskal-Wallis | — | — | H = 26.205 | 2.040e-06 | — | — |
| vader | milton | full | pairwise MW | expert | local | U = 212475212.000 | 2.877e-07 | 8.631e-07 | 0.029 |
| vader | milton | full | pairwise MW | expert | statewide | U = 206557755.500 | 1.449e-02 | 4.347e-02 | 0.014 |
| vader | milton | full | pairwise MW | local | statewide | U = 129598448.000 | 2.165e-02 | 6.495e-02 | -0.015 |
| vader | milton | excl_largest_thread | Kruskal-Wallis | — | — | H = 16.681 | 2.386e-04 | — | — |
| vader | milton | excl_largest_thread | pairwise MW | expert | local | U = 90184917.000 | 3.736e-01 | 1.000e+00 | 0.006 |
| vader | milton | excl_largest_thread | pairwise MW | expert | statewide | U = 104455101.000 | 5.875e-05 | 1.763e-04 | 0.027 |
| vader | milton | excl_largest_thread | pairwise MW | local | statewide | U = 86220103.500 | 5.808e-03 | 1.742e-02 | 0.020 |
| roberta | debby | full | Kruskal-Wallis | — | — | H = 12.977 | 1.521e-03 | — | — |
| roberta | debby | full | pairwise MW | expert | local | U = 1204341.000 | 9.031e-02 | 2.709e-01 | 0.036 |
| roberta | debby | full | pairwise MW | expert | statewide | U = 3203884.000 | 2.679e-04 | 8.036e-04 | 0.061 |
| roberta | debby | full | pairwise MW | local | statewide | U = 1853097.500 | 2.877e-01 | 8.632e-01 | 0.021 |
| roberta | debby | excl_largest_thread | Kruskal-Wallis | — | — | H = 73.171 | 1.292e-16 | — | — |
| roberta | debby | excl_largest_thread | pairwise MW | expert | local | U = 397059.000 | 9.197e-01 | 1.000e+00 | 0.003 |
| roberta | debby | excl_largest_thread | pairwise MW | expert | statewide | U = 1352960.000 | 1.811e-13 | 5.432e-13 | 0.166 |
| roberta | debby | excl_largest_thread | pairwise MW | local | statewide | U = 1358434.500 | 8.217e-10 | 2.465e-09 | 0.137 |
| roberta | helene | full | Kruskal-Wallis | — | — | H = 32.849 | 7.362e-08 | — | — |
| roberta | helene | full | pairwise MW | expert | local | U = 17331618.000 | 6.806e-01 | 1.000e+00 | -0.005 |
| roberta | helene | full | pairwise MW | expert | statewide | U = 31767029.500 | 4.945e-08 | 1.483e-07 | 0.052 |
| roberta | helene | full | pairwise MW | local | statewide | U = 10326354.500 | 3.204e-05 | 9.613e-05 | 0.052 |
| roberta | helene | excl_largest_thread | Kruskal-Wallis | — | — | H = 44.729 | 1.937e-10 | — | — |
| roberta | helene | excl_largest_thread | pairwise MW | expert | local | U = 4862158.500 | 3.830e-04 | 1.149e-03 | 0.053 |
| roberta | helene | excl_largest_thread | pairwise MW | expert | statewide | U = 8281622.000 | 1.889e-11 | 5.666e-11 | 0.089 |
| roberta | helene | excl_largest_thread | pairwise MW | local | statewide | U = 7946477.500 | 7.868e-03 | 2.360e-02 | 0.035 |
| roberta | milton | full | Kruskal-Wallis | — | — | H = 714.227 | 8.084e-156 | — | — |
| roberta | milton | full | pairwise MW | expert | local | U = 237701454.000 | 6.046e-151 | 1.814e-150 | 0.152 |
| roberta | milton | full | pairwise MW | expert | statewide | U = 222609995.000 | 2.364e-57 | 7.092e-57 | 0.093 |
| roberta | milton | full | pairwise MW | local | statewide | U = 124581301.000 | 1.854e-16 | 5.562e-16 | -0.053 |
| roberta | milton | excl_largest_thread | Kruskal-Wallis | — | — | H = 328.144 | 5.551e-72 | — | — |
| roberta | milton | excl_largest_thread | pairwise MW | expert | local | U = 97289747.500 | 1.174e-33 | 3.523e-33 | 0.086 |
| roberta | milton | excl_largest_thread | pairwise MW | expert | statewide | U = 113865466.500 | 1.168e-68 | 3.504e-68 | 0.120 |
| roberta | milton | excl_largest_thread | pairwise MW | local | statewide | U = 87675891.500 | 2.717e-07 | 8.152e-07 | 0.037 |

## H7: Government communication

| model | comparison | statistic | p-value | details |
| --- | --- | ---: | ---: | --- |
| vader | WH comments vs Reddit community | U = 128427604.500; Levene statistic = 62.722 | p(U) = 8.559e-03; p(Levene) = 2.400e-15 | variance/polarization check |
| vader | WH comments vs Phillips Facebook | U = 55524380.000 | p = 2.043e-35 | direct platform comparison |
| vader | WH comments with political keywords vs without | U = 466718.000 | p = 1.716e-02 | n(keyword) = 644; n(non-keyword) = 1549 |
| roberta | WH comments vs Reddit community | U = 109785884.000; Levene statistic = 1.086 | p(U) = 6.509e-44; p(Levene) = 2.973e-01 | variance/polarization check |
| roberta | WH comments vs Phillips Facebook | U = 36921021.000 | p = 1.042e-264 | direct platform comparison |
| roberta | WH comments with political keywords vs without | U = 417404.000 | p = 1.687e-09 | n(keyword) = 644; n(non-keyword) = 1549 |
