# BERTopic Run Log — Week 4 (Student B: Facebook + White House)

_Prepared with the help of Claude_

Record of the BERTopic topic-modeling run for the Facebook and White House corpora. Reddit (Student A) is logged separately. BERTopic runs on the Week 3 `*_vader_roberta.csv` files and writes a topic column back; it does not touch the VADER or RoBERTa scores.

## Setup

- **Library:** BERTopic (default UMAP + HDBSCAN pipeline)
- **Embedding model:** `all-MiniLM-L6-v2` (sentence-transformers)
- **UMAP:** `n_neighbors=15`, `n_components=5`, `min_dist=0.0`, `metric=cosine`, `random_state=42`
- **Vectorizer (topic words only):** `CountVectorizer(stop_words="english", ngram_range=(1,2))`
- **Short-row rule:** rows with fewer than 5 words are excluded from modeling but kept in the output with the sentinel `excluded_short` (never deleted)
- **Output columns added:** `topic_bertopic` (topic id, or `excluded_short`), `topic_label_auto` (BERTopic's auto name)
- **Environment:** Google Colab, NVIDIA T4 GPU

## Pool decision

Default from the plan is to model each unit separately, with one exception. Settled choices:

- **Facebook posts and comments: modeled separately.** They are different text types (broadcast forecast posts vs. short audience replies), so a shared model would blur them.
- **White House posts and comments: modeled together.** The posts file is only 12 rows, too small to cluster on its own, so the 12 posts are folded in with the 2,193 comments per the plan. Topic assignments are split back out to the two source files afterward.

## Preprocessing — row loss per file

| File                        | Total rows | Modeled | Dropped (<5 words) |
| --------------------------- | ---------- | ------- | ------------------ |
| facebook_posts              | 952        | 944     | 8                  |
| facebook_comments           | 59,736     | 49,939  | 9,797              |
| whitehouse (posts+comments) | 2,205      | 2,086   | 119                |

Facebook comments lose a large share (16.4%) because the file is full of short reactions like "stay safe" and "prayers" that fall under the 5-word floor. Posts and White House lose almost nothing.

## min_topic_size and results

| Corpus            | min_topic_size | Topics | % in −1 outliers |
| ----------------- | -------------- | ------ | ---------------- |
| facebook_posts    | 10             | 11     | 0.2%             |
| facebook_comments | 150            | 44     | 44.2%            |
| whitehouse        | 10             | 5      | 0.2%             |

Notes on the chosen values:

- **Facebook comments (150):** a ~50k-row corpus needs a larger floor than the default 20, otherwise it fragments into many tiny near-duplicate topics. 44 topics is interpretable and maps onto the codebook categories. The 44% outlier rate is high but normal for short, noisy social comments under HDBSCAN; whether to reduce outliers is a separate decision recorded below.
- **White House (10):** the plan suggested 20, but I lowered it to 10 after testing. This is documented on purpose because it overrides the plan.

## White House is topically homogeneous (key finding)

The White House model does not behave like the others, and no `min_topic_size` value fixes it. At both 20 and 10, one topic holds about 95% of the rows (1,984 of 2,086). Lowering the floor to 10 did not split that topic; it only let a few small clusters of moderation boilerplate form on the side.

The reason is the data, not the parameter. `min_topic_size` sets how small a cluster is allowed to be. It cannot force a dense, semantically uniform cluster to break apart. The White House posts are near-identical FEMA-aid update templates, and most of the comments are political reactions in the same semantic space (FEMA, government, Trump, disaster relief). They embed into one tight blob.

This is worth reporting as a result rather than treating as a failed run. Facebook comments spread across 44 topics; White House comments collapse into essentially one. That contrast is itself evidence for H7 framing. H7 rests on sentiment polarization (already measured by VADER and RoBERTa), not on topic variety, so the homogeneity does not weaken the hypothesis test.

I kept `min_topic_size=10` for the White House because it separates the moderation boilerplate into its own small topics, which makes them easy to label and exclude later.

## Boilerplate in the White House comments

The White House comment file still contains Reddit moderation and bot messages (AutoModerator removals, "content removed for not being civil," "misinformation / unsubstantiated claims," subreddit posting rules). About 50–100 rows. We chose not to re-clean or re-score, since VADER and RoBERTa are already done. At `min_topic_size=10` these rows land in their own small topics (WH topics 1–4), so they can be labeled as non-substantive and dropped from the H7 sentiment cut at analysis time without editing any data.

## Draft topic labels (NOT final — reconcile jointly with Student A)

Plain-English labels drafted from the top words and representative docs. These get aligned into the shared codebook before any cross-source comparison; do not lock them in alone.

**Facebook comments (44 topics — main ones)**

| Topic | Draft label                                            | Codebook category                 |
| ----- | ------------------------------------------------------ | --------------------------------- |
| 0     | Trust in Phillips / "only meteorologist I trust"       | gratitude / emotional response    |
| 1     | Travel & flight disruption (Orlando, Disney, airports) | logistics                         |
| 2     | Wind & gusts questions                                 | forecast analysis                 |
| 3     | Storm surge & tide                                     | forecast analysis                 |
| 4     | Evacuation zones & mandatory evacuation                | evacuation logistics              |
| 5     | Thanks for the updates                                 | gratitude                         |
| 6     | Snacks / Dr Pepper humor                               | emotional response (coping humor) |
| 7     | "Wondering the same thing"                             | (non-substantive / chatter)       |
| 8     | Category & landfall intensity                          | forecast analysis                 |
| 9     | Beach & coastal locations (St Pete, Clearwater)        | personal experience / location    |
| 10    | Florida / praying / prayers                            | emotional response                |
| 11    | Tampa Bay impact questions                             | forecast analysis / location      |
| 12    | "Rule #7" / don't freak out meme                       | emotional response                |
| 13    | Sarasota / Bradenton / Manatee                         | location                          |

**Facebook posts (11 topics)**

| Topic | Draft label                                       | Codebook category                 |
| ----- | ------------------------------------------------- | --------------------------------- |
| 0     | Forecast & track updates (the substantive bucket) | forecast analysis                 |
| 1–9   | Automated tornado-warning alerts by county        | automated alert (non-substantive) |
| 10    | Family hurricane prep checklist                   | preparedness                      |

The county-by-county tornado alerts (topics 1–9) are near-duplicate automated templates. Collapse them into one "automated alert" category in the codebook rather than treating each county as its own theme.

**White House (5 topics)**

| Topic | Draft label                                              | Codebook category                            |
| ----- | -------------------------------------------------------- | -------------------------------------------- |
| 0     | Government / FEMA disaster response & political reaction | government resources / political-FEMA        |
| 1–4   | Moderation / removed-content boilerplate                 | non-substantive (exclude from sentiment cut) |

## Outlier handling (open decision)

Facebook comments sit at 44.2% in the `−1` outlier bucket. Not yet reduced. Decide one convention (`reduce_outliers()` vs. leave as-is) and apply it the same way to every file, because the downstream topic-distribution and chi-square work should not have half of Facebook unassigned. Recorded here as pending.

## Issues

None blocking. Two items carried forward: the outlier convention (above) and the White House boilerplate, both handled at label/analysis time rather than by re-running upstream.
