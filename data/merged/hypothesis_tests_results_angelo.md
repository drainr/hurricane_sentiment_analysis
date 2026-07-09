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
| roberta | overall | 4683262614.000 | 0.000e+00 | 0.295 |
| roberta | debby | 94042964.500 | 0.000e+00 | 0.325 |
| roberta | helene | 305703713.500 | 0.000e+00 | 0.304 |
| roberta | milton | 1464275248.000 | 0.000e+00 | 0.259 |

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
| vader | helene | 0.114 | 0.000e+00 | [0.106, 0.123] |
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
| roberta | reddit | pairwise MW | 365092505.000 | 1.619e-14 | debby vs milton (Bonferroni p = 4.857e-14) |
| roberta | reddit | pairwise MW | 1380014097.500 | 2.784e-49 | helene vs milton (Bonferroni p = 8.353e-49) |
| roberta | facebook | Kruskal-Wallis | 644.042 | 1.406e-140 | 3 storms |
| roberta | facebook | pairwise MW | 118999650.500 | 9.223e-07 | debby vs helene (Bonferroni p = 2.767e-06) |
| roberta | facebook | pairwise MW | 268575977.000 | 1.453e-119 | debby vs milton (Bonferroni p = 4.358e-119) |
| roberta | facebook | pairwise MW | 229886450.500 | 1.231e-67 | helene vs milton (Bonferroni p = 3.694e-67) |

## H5: Reddit subreddit-category differences

Subreddit mapping — expert: r/TropicalWeather; local: r/tampa, r/sarasota; statewide: r/florida.

| model | subset | variant | test | category A | category B | statistic | p-value | Bonferroni p | rank-biserial |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| vader | debby | full | Kruskal-Wallis | — | — | H = 0.065 | 9.681e-01 | — | — |
| vader | debby | excl_largest_thread | Kruskal-Wallis | — | — | H = 13.290 | 1.301e-03 | — | — |
| vader | debby | excl_largest_thread | pairwise MW | expert | local | U = 555802.000 | 7.192e-01 | 1.000e+00 | 0.009 |
| vader | debby | excl_largest_thread | pairwise MW | expert | statewide | U = 2763390.500 | 1.632e-03 | 4.897e-03 | 0.059 |
| vader | debby | excl_largest_thread | pairwise MW | local | statewide | U = 2029896.500 | 1.588e-02 | 4.764e-02 | 0.051 |
| vader | helene | full | Kruskal-Wallis | — | — | H = 1.733 | 4.203e-01 | — | — |
| vader | helene | excl_largest_thread | Kruskal-Wallis | — | — | H = 1.266 | 5.311e-01 | — | — |
| vader | milton | full | Kruskal-Wallis | — | — | H = 38.308 | 4.803e-09 | — | — |
| vader | milton | full | pairwise MW | expert | local | U = 335672216.500 | 1.945e-05 | 5.834e-05 | 0.023 |
| vader | milton | full | pairwise MW | expert | statewide | U = 470698525.500 | 1.889e-08 | 5.668e-08 | 0.027 |
| vader | milton | full | pairwise MW | local | statewide | U = 186937912.000 | 4.715e-01 | 1.000e+00 | 0.004 |
| vader | milton | excl_largest_thread | Kruskal-Wallis | — | — | H = 45.992 | 1.030e-10 | — | — |
| vader | milton | excl_largest_thread | pairwise MW | expert | local | U = 176540298.000 | 3.182e-01 | 9.545e-01 | -0.006 |
| vader | milton | excl_largest_thread | pairwise MW | expert | statewide | U = 295803905.000 | 1.655e-09 | 4.965e-09 | 0.032 |
| vader | milton | excl_largest_thread | pairwise MW | local | statewide | U = 124704969.500 | 2.569e-08 | 7.708e-08 | 0.037 |
| roberta | debby | full | Kruskal-Wallis | — | — | H = 39.876 | 2.193e-09 | — | — |
| roberta | debby | full | pairwise MW | expert | local | U = 1441469.000 | 2.194e-01 | 6.583e-01 | 0.025 |
| roberta | debby | full | pairwise MW | expert | statewide | U = 6739996.000 | 5.592e-10 | 1.677e-09 | 0.089 |
| roberta | debby | full | pairwise MW | local | statewide | U = 3240979.500 | 3.975e-03 | 1.193e-02 | 0.054 |
| roberta | debby | excl_largest_thread | Kruskal-Wallis | — | — | H = 112.537 | 3.655e-25 | — | — |
| roberta | debby | excl_largest_thread | pairwise MW | expert | local | U = 542533.000 | 5.524e-01 | 1.000e+00 | -0.015 |
| roberta | debby | excl_largest_thread | pairwise MW | expert | statewide | U = 3046273.000 | 4.873e-19 | 1.462e-18 | 0.167 |
| roberta | debby | excl_largest_thread | pairwise MW | local | statewide | U = 2234439.500 | 1.321e-13 | 3.963e-13 | 0.157 |
| roberta | helene | full | Kruskal-Wallis | — | — | H = 35.080 | 2.412e-08 | — | — |
| roberta | helene | full | pairwise MW | expert | local | U = 56627577.500 | 1.792e-01 | 5.375e-01 | -0.011 |
| roberta | helene | full | pairwise MW | expert | statewide | U = 77911678.500 | 8.521e-07 | 2.556e-06 | 0.036 |
| roberta | helene | full | pairwise MW | local | statewide | U = 46420331.500 | 1.828e-07 | 5.484e-07 | 0.044 |
| roberta | helene | excl_largest_thread | Kruskal-Wallis | — | — | H = 42.364 | 6.322e-10 | — | — |
| roberta | helene | excl_largest_thread | pairwise MW | expert | local | U = 19943465.500 | 2.708e-03 | 8.125e-03 | -0.031 |
| roberta | helene | excl_largest_thread | pairwise MW | expert | statewide | U = 28397681.000 | 5.578e-04 | 1.673e-03 | 0.033 |
| roberta | helene | excl_largest_thread | pairwise MW | local | statewide | U = 30224618.000 | 1.875e-10 | 5.626e-10 | 0.060 |
| roberta | milton | full | Kruskal-Wallis | — | — | H = 904.306 | 4.290e-197 | — | — |
| roberta | milton | full | pairwise MW | expert | local | U = 368279348.500 | 8.053e-115 | 2.416e-114 | 0.122 |
| roberta | milton | full | pairwise MW | expert | statewide | U = 515389972.000 | 2.172e-148 | 6.516e-148 | 0.124 |
| roberta | milton | full | pairwise MW | local | statewide | U = 186722864.000 | 6.025e-01 | 1.000e+00 | 0.003 |
| roberta | milton | excl_largest_thread | Kruskal-Wallis | — | — | H = 590.416 | 6.207e-129 | — | — |
| roberta | milton | excl_largest_thread | pairwise MW | expert | local | U = 184665065.000 | 2.056e-10 | 6.169e-10 | 0.040 |
| roberta | milton | excl_largest_thread | pairwise MW | expert | statewide | U = 323713013.500 | 5.244e-130 | 1.573e-129 | 0.129 |
| roberta | milton | excl_largest_thread | pairwise MW | local | statewide | U = 130902239.500 | 2.853e-40 | 8.558e-40 | 0.088 |

## H7: Government communication

| model | comparison | statistic | p-value | details |
| --- | --- | ---: | ---: | --- |
| vader | WH comments vs Reddit community | U = 128427604.500; Levene statistic = 62.722 | p(U) = 8.559e-03; p(Levene) = 2.400e-15 | variance/polarization check |
| vader | WH comments vs Phillips Facebook | U = 55524380.000 | p = 2.043e-35 | direct platform comparison |
| vader | WH comments with political keywords vs without | U = 466718.000 | p = 1.716e-02 | n(keyword) = 644; n(non-keyword) = 1549 |
| roberta | WH comments vs Reddit community | U = 109785884.000; Levene statistic = 1.086 | p(U) = 6.509e-44; p(Levene) = 2.973e-01 | variance/polarization check |
| roberta | WH comments vs Phillips Facebook | U = 36921021.000 | p = 1.042e-264 | direct platform comparison |
| roberta | WH comments with political keywords vs without | U = 417404.000 | p = 1.687e-09 | n(keyword) = 644; n(non-keyword) = 1549 |
