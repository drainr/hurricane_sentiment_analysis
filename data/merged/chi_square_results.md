# Week 4 Chi-Square Results -- topic_category

Source: `data/merged/master_vader_roberta_topics.csv` (187,359 rows).
Tests run on the nine shared categories; `excluded` and the four WH-only categories are omitted (structural zeros for FB/Reddit). `government` (WH posts, n=12) excluded as too few.

## 1. source_type x topic_category (primary)

_facebook vs community_discussion vs government_response._

Contingency table (counts):

| source_bucket        |   emotional response |   evacuation logistics |   forecast analysis |   government resources |   gratitude |   personal experience |   political / FEMA criticism |   preparedness |
|:---------------------|---------------------:|-----------------------:|--------------------:|-----------------------:|------------:|----------------------:|-----------------------------:|---------------:|
| community_discussion |                 2096 |                   3195 |               17872 |                    111 |           0 |                 18002 |                        14354 |           3885 |
| facebook             |                 4966 |                   1163 |                9729 |                    216 |        2492 |                  9768 |                            0 |            458 |
| government_response  |                    0 |                      0 |                   0 |                      0 |           0 |                     0 |                         1972 |              0 |

- chi-square = **26,713.22**
- dof = 14
- p-value = **0.000e+00**  (significant at .05)
- Cramer's V = **0.3846**

## 2. source_type x topic_category within Reddit (community vs government_response)

_Both are Reddit; isolates the WH-comment effect from the platform effect._

Contingency table (counts):

| source_bucket        |   emotional response |   evacuation logistics |   forecast analysis |   government resources |   personal experience |   political / FEMA criticism |   preparedness |
|:---------------------|---------------------:|-----------------------:|--------------------:|-----------------------:|----------------------:|-----------------------------:|---------------:|
| community_discussion |                 2096 |                   3195 |               17872 |                    111 |                 18002 |                        14354 |           3885 |
| government_response  |                    0 |                      0 |                   0 |                      0 |                     0 |                         1972 |              0 |

- chi-square = **5,635.70**
- dof = 6
- p-value = **0.000e+00**  (significant at .05)
- Cramer's V = **0.3027**

## 3. hurricane x topic_category

_All shared-category rows. Note: WH account did not exist for Debby, so any WH-specific cut excludes Debby; this overall table spans all sources._

Contingency table (counts):

| hurricane   |   emotional response |   evacuation logistics |   forecast analysis |   government resources |   gratitude |   personal experience |   political / FEMA criticism |   preparedness |
|:------------|---------------------:|-----------------------:|--------------------:|-----------------------:|------------:|----------------------:|-----------------------------:|---------------:|
| debby       |                 1330 |                    144 |                2812 |                     88 |         780 |                  4674 |                          808 |            415 |
| helene      |                 1513 |                   1020 |                6139 |                     96 |         692 |                  8738 |                         3966 |           1833 |
| milton      |                 4219 |                   3194 |               18650 |                    155 |        1020 |                 14358 |                        11552 |           2095 |

- chi-square = **4,842.20**
- dof = 14
- p-value = **0.000e+00**  (significant at .05)
- Cramer's V = **0.1638**
