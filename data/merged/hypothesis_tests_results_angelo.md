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
| roberta | overall | facebook | 59736 | +0.00592 | [+0.00209, +0.00975] | 2.478e-03 | 0.0002 |
| roberta | overall | reddit | 121053 | +0.00913 | [+0.00646, +0.01180] | 2.093e-11 | 0.0004 |
| roberta | debby | facebook | 16199 | -0.02593 | [-0.03356, -0.01829] | 2.909e-11 | 0.0027 |
| roberta | debby | reddit | 8766 | -0.00492 | [-0.01538, +0.00553] | 3.559e-01 | 0.0001 |
| roberta | helene | facebook | 14229 | -0.01421 | [-0.02390, -0.00452] | 4.059e-03 | 0.0006 |
| roberta | helene | reddit | 32948 | -0.02770 | [-0.03382, -0.02158] | 7.853e-19 | 0.0024 |
| roberta | milton | facebook | 29308 | +0.03529 | [+0.03002, +0.04057] | 3.860e-39 | 0.0058 |
| roberta | milton | reddit | 79339 | +0.01523 | [+0.01168, +0.01879] | 4.709e-17 | 0.0009 |

### Interaction model: compound ~ days_from_landfall × platform

| model | subset | interaction coef (reddit − facebook slope) | interaction p | R² |
| --- | --- | ---: | ---: | ---: |
| vader | overall | +0.00535 | 6.133e-04 | 0.0137 |
| roberta | overall | +0.00321 | 1.731e-01 | 0.0503 |

## H3: Storm intensity interaction

| model | hurricane | mean Facebook-Reddit gap | bootstrap p-value | 95% CI |
| --- | --- | ---: | ---: | --- |
| vader | debby | 0.113 | 0.000e+00 | [0.101, 0.124] |
| vader | helene | 0.114 | 0.000e+00 | [0.106, 0.122] |
| vader | milton | 0.096 | 0.000e+00 | [0.090, 0.101] |
| roberta | debby | 0.369 | 0.000e+00 | [0.351, 0.387] |
| roberta | helene | 0.340 | 0.000e+00 | [0.327, 0.354] |
| roberta | milton | 0.285 | 0.000e+00 | [0.277, 0.295] |


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
| roberta | reddit | Kruskal-Wallis | 150.079 | 2.575e-33 | 3 storms |
| roberta | reddit | pairwise MW | 143464559.500 | 2.998e-01 | debby vs helene (Bonferroni p = 8.994e-01) |
| roberta | reddit | pairwise MW | 359316175.500 | 1.627e-08 | debby vs milton (Bonferroni p = 4.880e-08) |
| roberta | reddit | pairwise MW | 1359484712.000 | 1.517e-31 | helene vs milton (Bonferroni p = 4.550e-31) |
| roberta | facebook | Kruskal-Wallis | 458.023 | 3.480e-100 | 3 storms |
| roberta | facebook | pairwise MW | 117414920.000 | 1.871e-03 | debby vs helene (Bonferroni p = 5.613e-03) |
| roberta | facebook | pairwise MW | 260850088.500 | 5.782e-82 | debby vs milton (Bonferroni p = 1.735e-81) |
| roberta | facebook | pairwise MW | 225704527.000 | 1.272e-53 | helene vs milton (Bonferroni p = 3.816e-53) |

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
| roberta | debby | full | Kruskal-Wallis | — | — | H = 17.982 | 1.245e-04 | — | — |
| roberta | debby | full | pairwise MW | expert | local | U = 1210094.500 | 3.191e-02 | 9.573e-02 | 0.041 |
| roberta | debby | full | pairwise MW | expert | statewide | U = 3216264.500 | 1.853e-05 | 5.558e-05 | 0.065 |
| roberta | debby | full | pairwise MW | local | statewide | U = 1854092.500 | 2.359e-01 | 7.078e-01 | 0.022 |
| roberta | debby | excl_largest_thread | Kruskal-Wallis | — | — | H = 69.209 | 9.363e-16 | — | — |
| roberta | debby | excl_largest_thread | pairwise MW | expert | local | U = 406016.000 | 3.037e-01 | 9.110e-01 | 0.025 |
| roberta | debby | excl_largest_thread | pairwise MW | expert | statewide | U = 1337934.000 | 1.181e-13 | 3.542e-13 | 0.153 |
| roberta | debby | excl_largest_thread | pairwise MW | local | statewide | U = 1332146.000 | 2.209e-08 | 6.628e-08 | 0.115 |
| roberta | helene | full | Kruskal-Wallis | — | — | H = 48.469 | 2.987e-11 | — | — |
| roberta | helene | full | pairwise MW | expert | local | U = 17479062.000 | 7.154e-01 | 1.000e+00 | 0.004 |
| roberta | helene | full | pairwise MW | expert | statewide | U = 31978399.500 | 7.144e-12 | 2.143e-11 | 0.059 |
| roberta | helene | full | pairwise MW | local | statewide | U = 10322390.000 | 7.072e-06 | 2.122e-05 | 0.052 |
| roberta | helene | excl_largest_thread | Kruskal-Wallis | — | — | H = 49.894 | 1.464e-11 | — | — |
| roberta | helene | excl_largest_thread | pairwise MW | expert | local | U = 4839111.000 | 3.791e-04 | 1.137e-03 | 0.048 |
| roberta | helene | excl_largest_thread | pairwise MW | expert | statewide | U = 8258049.500 | 1.105e-12 | 3.314e-12 | 0.086 |
| roberta | helene | excl_largest_thread | pairwise MW | local | statewide | U = 7955469.000 | 2.801e-03 | 8.404e-03 | 0.036 |
| roberta | milton | full | Kruskal-Wallis | — | — | H = 635.636 | 9.405e-139 | — | — |
| roberta | milton | full | pairwise MW | expert | local | U = 232750386.000 | 1.937e-132 | 5.810e-132 | 0.128 |
| roberta | milton | full | pairwise MW | expert | statewide | U = 220709163.000 | 2.931e-57 | 8.792e-57 | 0.084 |
| roberta | milton | full | pairwise MW | local | statewide | U = 126152608.500 | 2.547e-12 | 7.642e-12 | -0.041 |
| roberta | milton | excl_largest_thread | Kruskal-Wallis | — | — | H = 331.486 | 1.044e-72 | — | — |
| roberta | milton | excl_largest_thread | pairwise MW | expert | local | U = 96896465.500 | 3.207e-37 | 9.621e-37 | 0.081 |
| roberta | milton | excl_largest_thread | pairwise MW | expert | statewide | U = 112735213.000 | 8.784e-69 | 2.635e-68 | 0.109 |
| roberta | milton | excl_largest_thread | pairwise MW | local | statewide | U = 86927406.000 | 1.877e-05 | 5.632e-05 | 0.028 |

## H7: Government communication

| model | comparison | statistic | p-value | details |
| --- | --- | ---: | ---: | --- |
| vader | WH comments vs Reddit community | U = 128427604.500; Levene statistic = 62.722 | p(U) = 8.559e-03; p(Levene) = 2.400e-15 | variance/polarization check |
| vader | WH comments vs Phillips Facebook | U = 55524380.000 | p = 2.043e-35 | direct platform comparison |
| vader | WH comments with political keywords vs without | U = 466718.000 | p = 1.716e-02 | n(keyword) = 644; n(non-keyword) = 1549 |
| roberta | WH comments vs Reddit community | U = 116088881.000; Levene statistic = 13.295 | p(U) = 1.247e-28; p(Levene) = 2.662e-04 | variance/polarization check |
| roberta | WH comments vs Phillips Facebook | U = 41992197.500 | p = 1.865e-215 | direct platform comparison |
| roberta | WH comments with political keywords vs without | U = 429232.500 | p = 7.990e-09 | n(keyword) = 644; n(non-keyword) = 1549 |
