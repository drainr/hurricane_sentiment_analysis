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
| Debby       |                 1147 |                     55 |                2087 |                     85 |         780 |                  3050 |                            0 |             54 |
| Helene      |                  903 |                    288 |                2461 |                     70 |         692 |                  2615 |                            0 |            141 |
| Milton      |                 2916 |                    820 |                5181 |                     61 |        1020 |                  4103 |                            0 |            263 |
| debby       |                  183 |                     89 |                 725 |                      3 |           0 |                  1624 |                          808 |            361 |
| helene      |                  610 |                    732 |                3678 |                     26 |           0 |                  6123 |                         3966 |           1692 |
| milton      |                 1303 |                   2374 |               13469 |                     94 |           0 |                 10255 |                        11552 |           1832 |

- chi-square = **23,108.64**
- dof = 35
- p-value = **0.000e+00**  (significant at .05)
- Cramer's V = **0.2262**

## Facebook comment coverage note

Topic distribution results for Facebook comments are based on the **27,850** comments that received a topic assignment — **46.6%** of the 59,736-comment file, or **55.8%** of the 49,939 comments that entered BERTopic after excluding 9,797 rows under five words. The remaining rows are **22,089** BERTopic outliers (37.0%, topic `-1`) and **9,797** short reactions excluded before modeling (16.4%). All 59,736 comments are retained in the VADER/RoBERTa sentiment analysis; only the topic layer drops them.
