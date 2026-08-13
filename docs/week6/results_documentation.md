# Consolidated Hypothesis Tables And Analysis

This report consolidates the project's hypothesis-test tables into one place and adds a detailed interpretation of what the results mean. It combines the comment-level sentiment tests for H1, H2, H3, H4, H5, and H7 with the topic-distribution chi-square tests used for H6.

Method conventions:
- VADER score = `vader_compound`
- RoBERTa score = `roberta_pos - roberta_neg`
- Facebook = Phillips Facebook comments
- Reddit = organic `community_discussion` comments
- White House = `government_response` comments
- At this sample size, p-values are often effectively zero. Effect sizes and direction are more informative than significance alone.

## Interpreting statistics

| Statistic | Meaning | How to interpret it here |
|---|---|---|
| Mann-Whitney U | Nonparametric two-group comparison | Tests whether one group's scores tend to be higher/lower than the other's |
| Rank-biserial | Effect size for Mann-Whitney | Positive means first group tends to score higher; negative means first group tends to score lower |
| Chi-square | Association test for counts in categories | Here it tests whether label/topic composition differs by platform/source |
| Cramer's V | Effect size for chi-square | Rough guide: around 0.10 small, 0.30 medium, 0.50 large |
| OLS slope | Linear day-to-day trend | Positive means sentiment becomes more positive later in the window |
| OLS interaction | Difference in slope between Reddit and Facebook | Positive here means Reddit gets more positive faster, or declines less steeply, than Facebook |
| R^2 | Fraction of variance explained by the linear model | Very low values here mean day-to-day linear trends are weak |
| Kruskal-Wallis H | Nonparametric omnibus test across 3+ groups | Significant result means at least one storm/tier differs from another |
| Levene W | Equality-of-variance test | Significant here means one group's spread/variance is different |

## Master Verdict Table

| Hypothesis | Core prediction | VADER verdict | RoBERTa verdict 
|---|---|---|---|---|
| H1 | Reddit community discussions will show significantly lower compound sentiment than Facebook/Phillips comments during the same time windows | Supported | Supported, stronger 
| H2 | Reddit sentiment will decline more sharply approaching landfall than Facebook, where Phillips moderates audience anxiety | Not supported | Not supported
| H3 | The Facebook-Reddit sentiment gap will be larger for higher-intensity storms (Debby < Helene, Milton) | Not supported | Not supported 
| H4 |  Across the sequential storms, Reddit will show cumulative negativity while Facebook/Phillips remains stable | Partial at best | Partial at best 
| H5 | Within Reddit, r/TropicalWeather (expert) will show more neutral sentiment than local community subreddits | Mixed | Supported | 
| H6 | Facebook will center on gratitude and preparedness; Reddit will center on forecast models, evacuation, and misinformation | Supported | Topic analysis, not scorer-specific 
| H7 | Comments on White House Reddit posts will show a more polarized sentiment profile than organic community posts, and will differ from Phillips’ Facebook comments | Partial | Partial to strong 

## H1 — Platform Difference

Prediction: Reddit community comments should have lower compound sentiment than Facebook comments overall and within each hurricane.

### H1 table

| method | scope | n(FB) | n(Reddit) | mean FB | mean Reddit | U | p | rank-biserial |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| VADER | overall | 59,736 | 121,053 | 0.170 | 0.059 | 4,080,853,682 | 0.00e+00 | +0.129 |
| VADER | Debby | 16,199 | 8,766 | 0.199 | 0.086 | 80,092,146 | 1.06e-64 | +0.128 |
| VADER | Helene | 14,229 | 32,948 | 0.192 | 0.078 | 266,146,258 | 6.92e-124 | +0.135 |
| VADER | Milton | 29,308 | 79,339 | 0.144 | 0.048 | 1,288,405,580 | 3.62e-169 | +0.108 |
| RoBERTa | overall | 59,736 | 121,053 | 0.048 | -0.232 | 4,683,262,614 | 0.00e+00 | +0.295 |
| RoBERTa | Debby | 16,199 | 8,766 | 0.115 | -0.203 | 94,042,964 | 0.00e+00 | +0.325 |
| RoBERTa | Helene | 14,229 | 32,948 | 0.087 | -0.199 | 305,703,714 | 0.00e+00 | +0.304 |
| RoBERTa | Milton | 29,308 | 79,339 | -0.008 | -0.248 | 1,464,275,248 | 0.00e+00 | +0.259 |

### H1 label-composition chi-square

| method | test | statistic | p | effect size |
|---|---|---:|---:|---:|
| VADER | platform × `vader_label` | χ²(2)=4492.4 | 0.00e+00 | Cramer's V = 0.158 |
| RoBERTa | platform × `roberta_label` | χ²(2)=9059.5 | 0.00e+00 | Cramer's V = 0.224 |

### H1 analysis

H1 is strongly supported by the hypothesis test. Both scorers show Facebook comments are systematically more positive than Reddit comments in every storm and in the overall sample. The direction is perfectly stable; every rank-biserial effect is positive because Facebook is the first group in the comparison.

The size of the effect is modest under VADER and clearly stronger under RoBERTa. VADER's overall rank-biserial of +0.129 is a real but small-to-moderate separation. RoBERTa's +0.295 indicates a meaningfully stronger platform gap. That pattern matters because it suggests VADER's tends to have a positivity bias which compresses the difference between the platforms rather than creating it. The chi-square results reinforce the same point from a different angle: it is not just that the average score differs, but that the entire label distribution differs by platform.

Substantively, the Facebook side appears to be inflated by gratitude and communicator-directed positivity, while Reddit community discussions contain more criticism, conflict, and anxiety. 

## H2 — Temporal Trajectory

Prediction: Reddit sentiment should decline more steeply as landfall approaches than Facebook sentiment.

### H2 overall slopes and interaction

| method | platform | N | slope per day | 95% CI | p | R^2 |
|---|---|---:|---:|---|---:|---:|
| VADER | Facebook | 59,736 | -0.00279 | [-0.00500, -0.00057] | 1.36e-02 | 0.0001 |
| VADER | Reddit | 121,053 | +0.00256 | [+0.00068, +0.00444] | 7.50e-03 | 0.0001 |
| RoBERTa | Facebook | 59,736 | +0.00436 | [+0.00132, +0.00741] | 4.99e-03 | 0.0001 |
| RoBERTa | Reddit | 121,053 | +0.00800 | [+0.00597, +0.01003] | 1.09e-14 | 0.0005 |

| method | interaction term | estimate | 95% CI | p | interpretation |
|---|---|---:|---|---:|---|
| VADER | Reddit slope − Facebook slope | +0.00535 | [+0.00229, +0.00841] | 6.13e-04 | Reddit gets more positive faster, or declines less |
| RoBERTa | Reddit slope − Facebook slope | +0.00364 | [+0.00008, +0.00721] | 4.54e-02 | Same direction as VADER |

### H2 per-hurricane slopes

| hurricane | VADER FB slope (p) | VADER Reddit slope (p) | RoBERTa FB slope (p) | RoBERTa Reddit slope (p) |
|---|---|---|---|---|
| Debby | -0.01370 (4.0e-10) | -0.00663 (7.1e-02) | -0.02290 (2.0e-13) | -0.00512 (2.1e-01) |
| Helene | -0.00814 (4.4e-03) | -0.01617 (2.9e-14) | -0.01086 (5.9e-03) | -0.02234 (4.6e-21) |
| Milton | +0.00642 (5.4e-05) | +0.00488 (1.7e-04) | +0.03022 (5.0e-46) | +0.01230 (4.6e-19) |

### H2 analysis

H2 is not supported. The decisive statistic is the interaction term, not the individual slopes. In both methods, the Reddit-minus-Facebook interaction is positive, which means Reddit is not becoming more negative faster than Facebook. If anything, the pooled fit says Reddit becomes slightly more positive relative to Facebook over the modeled window.

The stronger interpretive point is that the linear model barely explains anything. R^2 is effectively zero in every pooled fit. That means the day-to-day trajectory is weak, noisy, or non-linear across these short event windows. The per-hurricane slopes show why: Debby trends downward, Helene has a sharper Reddit decline, but Milton rises on both platforms. When those distinct shapes are pooled into one straight-line model, the net result cannot support the hypothesis.

So the correct conclusion is not just non-significant, rather wrong direction in the pooled interaction, with weak linear explanatory power overall. That is a stronger rejection than merely failing to reach significance.

## H3 — Storm Intensity Interaction

Prediction: the Facebook-Reddit sentiment gap should be smallest for Debby and larger for Helene and Milton.

### H3 gap table

| method | gap Debby | gap Helene | gap Milton | Debby smallest? |
|---|---:|---:|---:|---|
| VADER | 0.113 | 0.114 | 0.096 | No |
| RoBERTa | 0.318 | 0.286 | 0.240 | No |

### H3 analysis

H3 is not supported in either scoring system. The gap does not widen with the later, stronger storms. Under VADER, Debby and Helene are essentially tied, while Milton is smaller. Under RoBERTa, the pattern is even clearer, with the gap steadily shrinking from Debby to Helene to Milton.

This is a direct contradiction of the hypothesis. The result suggests that whatever drives the Facebook-Reddit gap is not simply storm intensity. A more plausible interpretation is that platform behavior is shaped by audience norms and discussion style more than by storm strength alone. The later storms also confound intensity with sequence effects and broader political context, so there is no clean way to attribute the shrinking gap to intensity by itself.

## H4 — Sequential Exposure Across Storms

Prediction: Reddit should show cumulative negativity across Debby, Helene, and Milton, while Facebook should remain comparatively stable.

### H4 omnibus tests

| method | platform | Kruskal-Wallis H | p |
|---|---|---:|---:|
| VADER | Reddit | 115.6 | 7.80e-26 |
| VADER | Facebook | 248.7 | 1.01e-54 |
| RoBERTa | Reddit | 245.1 | 5.95e-54 |
| RoBERTa | Facebook | 644.0 | 1.41e-140 |

### H4 pairwise comparisons

| method | platform | pair | Bonferroni p | rank-biserial |
|---|---|---|---:|---:|
| VADER | Reddit | Debby vs Helene | 1.9e-01 | +0.01 |
| VADER | Reddit | Debby vs Milton | 2.1e-12 | +0.05 |
| VADER | Reddit | Helene vs Milton | 2.6e-19 | +0.03 |
| VADER | Facebook | Debby vs Helene | 2.6e-01 | +0.01 |
| VADER | Facebook | Debby vs Milton | 7.5e-44 | +0.08 |
| VADER | Facebook | Helene vs Milton | 7.1e-31 | +0.07 |
| RoBERTa | Reddit | Debby vs Helene | 1.0e+00 | -0.01 |
| RoBERTa | Reddit | Debby vs Milton | 4.9e-14 | +0.05 |
| RoBERTa | Reddit | Helene vs Milton | 8.4e-49 | +0.06 |
| RoBERTa | Facebook | Debby vs Helene | 2.8e-06 | +0.03 |
| RoBERTa | Facebook | Debby vs Milton | 4.4e-119 | +0.13 |
| RoBERTa | Facebook | Helene vs Milton | 3.7e-67 | +0.10 |

### H4 analysis

The omnibus tests are strongly significant on both platforms and both scorers, so there is definitely cross-storm movement. The problem for the original hypothesis is that Facebook is not stable at all. In fact, Facebook often shifts more strongly than Reddit, especially under RoBERTa where Facebook's H statistic is far larger than Reddit's.

The pairwise pattern is also consistent: the big separation is mostly Milton versus the earlier storms, not a smooth monotonic Reddit-only accumulation. Debby and Helene are often similar, especially on Reddit. So the data support a broad statement like "Milton produced the most negative environment" but not the narrower claim that Reddit uniquely accumulates negativity while Facebook remains steady.

## H5 — Subreddit-Tier Differences

Prediction: expert weather subreddits should be less negative than local or statewide subreddits.

### H5 Debby

| method | variant | n expert | n local | n statewide | KW H | p | significant? | pairwise |
|---|---:|---:|---:|---:|---:|---:|---|---|
| VADER | full data | 2,379 | 1,182 | 5,205 | 0.1 | 9.68e-01 | no | n/a |
| VADER | largest thread excl. | 1,220 | 903 | 4,279 | 13.3 | 1.30e-03 | yes | expert-local p=1.0e+00 r=+0.01; expert-statewide p=4.9e-03 r=+0.06; local-statewide p=4.8e-02 r=+0.05 |
| RoBERTa | full data | 2,379 | 1,182 | 5,205 | 39.9 | 2.19e-09 | yes | expert-local p=6.6e-01 r=+0.03; expert-statewide p=1.7e-09 r=+0.09; local-statewide p=1.2e-02 r=+0.05 |
| RoBERTa | largest thread excl. | 1,220 | 903 | 4,279 | 112.5 | 3.66e-25 | yes | expert-local p=1.0e+00 r=-0.02; expert-statewide p=1.5e-18 r=+0.17; local-statewide p=4.0e-13 r=+0.16 |

### H5 Helene

| method | variant | n expert | n local | n statewide | KW H | p | significant? | pairwise |
|---|---:|---:|---:|---:|---:|---:|---|---|
| VADER | full data | 13,913 | 8,229 | 10,806 | 1.7 | 4.20e-01 | no | n/a |
| VADER | largest thread excl. | 6,299 | 6,532 | 8,729 | 1.3 | 5.31e-01 | no | n/a |
| RoBERTa | full data | 13,913 | 8,229 | 10,806 | 35.1 | 2.41e-08 | yes | expert-local p=5.4e-01 r=-0.01; expert-statewide p=2.6e-06 r=+0.04; local-statewide p=5.5e-07 r=+0.04 |
| RoBERTa | largest thread excl. | 6,299 | 6,532 | 8,729 | 42.4 | 6.32e-10 | yes | expert-local p=8.1e-03 r=-0.03; expert-statewide p=1.7e-03 r=+0.03; local-statewide p=5.6e-10 r=+0.06 |

### H5 Milton

| method | variant | n expert | n local | n statewide | KW H | p | significant? | pairwise |
|---|---:|---:|---:|---:|---:|---:|---|---|
| VADER | full data | 40,209 | 16,326 | 22,804 | 38.3 | 4.80e-09 | yes | expert-local p=5.8e-05 r=+0.02; expert-statewide p=5.7e-08 r=+0.03; local-statewide p=1.0e+00 r=+0.00 |
| VADER | largest thread excl. | 29,099 | 12,209 | 19,703 | 46.0 | 1.03e-10 | yes | expert-local p=9.5e-01 r=-0.01; expert-statewide p=5.0e-09 r=+0.03; local-statewide p=7.7e-08 r=+0.04 |
| RoBERTa | full data | 40,209 | 16,326 | 22,804 | 904.3 | 4.29e-197 | yes | expert-local p=2.4e-114 r=+0.12; expert-statewide p=6.5e-148 r=+0.12; local-statewide p=1.0e+00 r=+0.00 |
| RoBERTa | largest thread excl. | 29,099 | 12,209 | 19,703 | 590.4 | 6.21e-129 | yes | expert-local p=6.2e-10 r=+0.04; expert-statewide p=1.6e-129 r=+0.13; local-statewide p=8.6e-40 r=+0.09 |

### H5 analysis

H5 is the most method-sensitive of the sentiment hypotheses. RoBERTa supports the hypothesis across all three storms, while VADER supports it clearly only for Milton. Debby becomes significant under VADER only after removing the largest thread per subreddit, which means that result is sensitive to thread concentration rather than broadly distributed across the corpus. Helene remains non-significant under VADER regardless.

Decision timing and justification for largest-thread exclusion: treat this as a post-hoc sensitivity analysis rather than a pre-registered primary test. The defensible rationale is robustness, not confirmation: Reddit thread-level concentration can let one unusually large post dominate a storm-level subgroup signal, so the exclusion checks whether conclusions hold when each subreddit's single largest thread is removed. In reporting, the full-data result should remain primary, and the exclusion variant should be labeled explicitly as a robustness check prompted by concentration risk.

The direction of the means is still informative. Expert subreddits tend to look calmer or less negative than statewide ones, especially under RoBERTa, but the effect sizes are small. That means H5 is not a huge practical effect even when significant. The cleanest way to report it is that expert-vs-general differences are real but modest, and they are detected more reliably by RoBERTa than by VADER.

## H6 — Topic Distribution By Source

Prediction: Facebook should over-index in gratitude/preparedness-type discussion, while Reddit and White House comments should over-index in forecast, politics/FEMA criticism, and misinformation-related categories.

### H6 source-type × topic-category chi-square

| comparison | chi-square | dof | p | Cramer's V |
|---|---:|---:|---:|---:|
| Facebook vs Reddit community vs government_response | 26,713.22 | 14 | 0.000e+00 | 0.3846 |
| Reddit community vs government_response only | 5,635.70 | 6 | 0.000e+00 | 0.3027 |
| Hurricane × topic_category | 23,108.64 | 35 | 0.000e+00 | 0.2262 |

### H6 primary source-type contingency table

| source bucket | emotional response | evacuation logistics | forecast analysis | government resources | gratitude | personal experience | political / FEMA criticism | preparedness |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| community_discussion | 2,096 | 3,195 | 17,872 | 111 | 0 | 18,002 | 14,354 | 3,885 |
| facebook | 4,966 | 1,163 | 9,729 | 216 | 2,492 | 9,768 | 0 | 458 |
| government_response | 0 | 0 | 0 | 0 | 0 | 0 | 1,972 | 0 |

### H6 analysis

H6 is strongly supported. The source-type × topic-category association is one of the largest effects in the whole project, with Cramer's V = 0.3846. That is much stronger than the platform differences in H1, which means source differences in what people talk about are even more pronounced than source differences in how positive or negative they sound.

The table shows a very sharp structural split. Facebook contains all of the gratitude counts and a large share of emotional-response content, which matches the interpretation that Phillips' audience often responds directly to the communicator. Reddit community discussions concentrate on forecast analysis, personal experience, and political/FEMA criticism. White House comments are almost entirely concentrated in political/FEMA criticism, which is exactly the pattern that makes H7 plausible on the sentiment side.

The within-Reddit comparison is also important because it isolates the government-response effect from the broader platform effect. Even when both groups are Reddit comments, White House threads are topically different from organic community discussions.

## H7 — Government Communication

Prediction: White House thread comments should be more negative or more polarized than organic Reddit and Facebook comments, and White House comments with political keywords should be more negative than those without.

### H7 table

| method | comparison | U | p | rank-biserial | additional test |
|---|---|---:|---:|---:|---|
| VADER | WH vs Reddit | 128,427,604 | 8.56e-03 | -0.032 | Levene W=62.7, p=2.40e-15 |
| VADER | WH vs Facebook | 55,524,380 | 2.04e-35 | -0.152 | — |
| VADER | WH political vs non-political | 466,718 | 1.72e-02 | -0.064 | 644 vs 1,549 comments |
| RoBERTa | WH vs Reddit | 109,785,884 | 6.51e-44 | -0.173 | Levene W=1.1, p=2.97e-01 |
| RoBERTa | WH vs Facebook | 36,921,021 | 1.04e-264 | -0.436 | — |
| RoBERTa | WH political vs non-political | 417,404 | 1.69e-09 | -0.163 | 644 vs 1,549 comments |

### H7 mean levels

| method | mean WH | mean Reddit | mean Facebook | mean WH political | mean WH non-political |
|---|---:|---:|---:|---:|---:|
| VADER | 0.024 | 0.059 | 0.170 | -0.022 | 0.043 |
| RoBERTa | -0.363 | -0.232 | 0.048 | -0.476 | -0.316 |

### H7 sensitivity by hurricane (pooled-result check)

Comment-level re-check by hurricane shows the pooled WH-vs-Reddit contrast is primarily Helene-driven in both methods.

| method | comparison | Helene p | Milton p | interpretation |
|---|---|---:|---:|---|
| VADER | WH vs Reddit | 1.05e-05 | 4.82e-01 | Helene-driven; Milton n.s. |
| RoBERTa | WH vs Reddit | 3.20e-60 | 1.25e-01 | Helene-driven; Milton n.s. |
| VADER | WH vs Facebook | 1.31e-41 | 7.02e-02 | Mostly Helene-driven |
| RoBERTa | WH vs Facebook | 5.22e-269 | 1.23e-14 | Both storms contribute; Helene stronger |

The direction split across storms for White House means supports this reading: White House comments are much more negative in Helene (VADER +0.0196 vs Reddit +0.0780; RoBERTa -0.374 vs Reddit -0.199), while Milton is closer to Reddit (VADER +0.0624 vs +0.0480; RoBERTa -0.268 vs -0.248). This is why pooled WH-vs-Reddit significance is not a uniform all-storm effect.

### H7 analysis

H7 is supported more strongly for negativity than for polarization, and the conclusion depends somewhat on the scorer. RoBERTa gives the clearest substantive result: White House comments are substantially more negative than both Reddit community comments and Facebook comments, and the White House vs Facebook contrast is one of the largest effects in the dataset at rank-biserial -0.436.

VADER points in the same relative direction but much more weakly. Under VADER, White House comments are only slightly less positive than Reddit and clearly less positive than Facebook. That difference is statistically significant because the sample is large, but the effect on WH vs Reddit is very small at -0.032.

The polarization part of H7 is the least stable component. VADER finds a strong variance difference between White House and Reddit comments, which supports a polarization-style interpretation. RoBERTa does not replicate that variance result. So the safest interpretation is: White House threads are more negative than the comparison groups, especially under RoBERTa, but the stronger claim that they are more polarized in the variance sense is method-dependent.

The within-White-House keyword comparison is consistent across both scorers. Comments mentioning FEMA, Biden, Trump, government, or conspiracy are more negative than White House comments without those terms. That supports the idea that politicized discourse is a key mechanism inside the White House threads themselves.

## Overall Interpretation

Taken together, the results tell a coherent story.

First, platform matters a lot. Facebook comments are consistently more positive than Reddit comments, and that is reinforced by the topic-distribution results showing Facebook is structurally richer in gratitude and emotional-response content. Second, the later storms did not simply make Reddit more negative in a cumulative way. Instead, both platforms shift across storms, with Milton emerging as the most negative period in both systems. Third, subreddit specialization matters, but modestly: expert weather communities are calmer than local/statewide communities, and RoBERTa detects that pattern more reliably than VADER.

The strongest thematic split is not just sentiment but discourse type. H6 shows that Facebook, Reddit community threads, and White House responses are talking about materially different things. That matters for interpretation because some of the sentiment gap in H1 is probably compositional: audiences are not only feeling differently, they are discussing different topics in different communicative settings.

Finally, the White House result is real but should be framed carefully. The safest claim is that White House-comment environments are more negative than Phillips Facebook comments and, under RoBERTa, also more negative than organic Reddit community comments. The stronger claim that they are more polarized depends on VADER's variance result and is not equally supported by RoBERTa.

## Recommended conclusions

- H1: Supported. Facebook comments are consistently more positive than Reddit community comments, with a stronger separation under RoBERTa than under VADER.
- H2: Not supported. The pooled day-trend interaction runs in the opposite direction of the hypothesis and explains almost none of the variance.
- H3: Not supported. The Facebook-Reddit gap does not widen with stronger storms; if anything, it shrinks.
- H4: Partial. Sentiment differs significantly across storms on both platforms, but Facebook is not stable, so the hypothesized Reddit-specific accumulation mechanism fails.
- H5: Mixed but generally supportive. Expert subreddits are calmer than local/statewide subreddits, especially under RoBERTa, though effects are small and some VADER results are thread-sensitive.
- H6: Strongly supported. Topic distributions differ sharply by source, with Facebook, Reddit community, and White House comment environments occupying distinct discourse niches.
- H7: Supported for negativity more than polarization. White House comments are especially negative under RoBERTa, but the variance-based polarization claim is method-dependent.

## Numeric source files

- `docs/week5/hypothesis_tests_results.md`
- `docs/week5/h2_temporal_results.md`
- `docs/week5/h5_subreddit_results.md`
- `docs/week5/statistical_results_summary.md`
- `data/merged/chi_square_results.md`
- `data/merged/hypothesis_tests_all7_jose.csv`
