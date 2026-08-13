# Decision Log

**Hurricane Sentiment Analysis — Summer 2026**
Jose Araya, Angelo Morelli

Every methodological choice made during the project, why it was made, and what the alternative was. Organized by topic rather than chronologically, so a reader who was not present can find the reasoning behind any single decision. Where a choice was later revised, both the original and the revision are given — the revisions are part of the record.

Bugs and data-integrity problems are included deliberately. Three of them changed published numbers, and a decision log that omits them would misrepresent how the corpus reached its final state.

---

## 1. Reddit collection: how the method was decided and what was tried in Week 1

This was the critical unknown at the start of the project. The plan committed to trying four options in Week 1 and locking the method before Week 2 began.

### What was tried

**Arctic Shift** — a third-party archive of Reddit data exposing an HTTP API with `after`/`before` parameters. Tested with a small query against r/TropicalWeather for the Debby window. It ran cleanly start to finish. Returns up to 100 results per request in ascending order, so paging through a date window is straightforward, and the date parameters mean we can pull exactly the storm window rather than filtering a larger pull afterward. Tested against all three hurricanes across r/TropicalWeather, r/florida, and r/tampa; it worked every time.

**Pushshift dumps via Academic Torrents** — the same underlying data, distributed as per-subreddit `.zst` archives. Works, but requires a BitTorrent client. An early estimate of a ~100 GB, 12–24 hour download turned out to be wrong: `aria2c --select-file` pulls a single subreddit file selectively (`TropicalWeather_submissions.zst` is 7.4 MB), and `zstd --long=31` decompresses it locally.

**PRAW (official Reddit API)** — closed to us. Reddit's November 2025 Responsible Builder Policy requires pre-approval before the app-creation form will succeed, so obtaining API keys the conventional way no longer works. Both students filed the Data Access Request Form through the researcher track, with the faculty advisor listed as supervisor and institutional `.edu` email addresses. **The request was denied.** This ruled PRAW out entirely for historical date-range discovery.

**Apify Reddit scraper** — did not run at all. It requires a proxy, and the proxies it supplies do not get past Reddit's anti-scraping protections. It also costs $0.50 per 1,000 results.

### The decision, and how it was validated

**Arctic Shift as the primary collection method; Pushshift dumps retained as a validation cross-check and offline archival backup.**

The choice was validated empirically rather than asserted. We pulled `TropicalWeather_submissions.zst` selectively, decompressed it, filtered to the Debby window, and compared the resulting post IDs against the Arctic Shift CSV for the same window. **Exact match: 49 IDs = 49 IDs, zero discrepancies.** Because data quality is identical between the two sources, the choice reduces to workflow friction, and Arctic Shift wins on that: one script, windows specified directly, clean CSV output. Pushshift is kept because it is rate-limit-proof and works offline, which makes it a genuine reproducibility backup rather than a discarded alternative.

PRAW and Apify remain listed as secondary tools only for pulling White House comment trees by known URL — neither can do historical date-range discovery, which is what the project actually needed.

### Consequence for the White House lane

White House data was collected by Arctic Shift **author search** on the account `u/whitehouse46`, with the full comment tree pulled for each post. This is functionally equivalent to a PRAW thread pull and yields complete comment trees, and the resulting comment volume clears the 200-comment threshold the plan set for full statistical testing rather than the descriptive-only fallback.

---

## 2. Why these subreddits

Nine community subreddits, grouped into the three tiers H5 tests:

| Tier      | Subreddits                                        |
| --------- | ------------------------------------------------- |
| Expert    | r/TropicalWeather, r/hurricane, r/HurricaneHelene |
| Local     | r/tampa, r/sarasota, r/asheville                  |
| Statewide | r/florida, r/Georgia, r/NorthCarolina             |

The plan named r/TropicalWeather, r/tampa, r/florida, and r/sarasota as the starting set. The others were added because the storms demanded them: r/HurricaneHelene and r/asheville exist for Helene only, and r/Georgia and r/NorthCarolina cover Helene's inland track and Debby's Carolina flooding.

**r/asheville is classified as local, not statewide.** Helene's worst damage was the inland flooding around Asheville, which makes it a locally affected community in exactly the sense the tier is meant to capture. Without it the local tier for Helene would be Tampa and Sarasota alone, both of which were near-misses for that storm — the tier would not contain a single genuinely affected local community.

**Four subreddits were excluded from H5:** r/southcarolina, r/Tennessee, r/Virginia, and r/pics. These entered the corpus only through the White House–targeted pull — they are reactions to a government account, which is H7-type data, not organic community discussion. Verified rather than assumed: those four subreddits account for **0 rows** in `reddit_relevant_comments` and `reddit_relevant_posts`. They exist only in the `whitehouse_threads_*` files (558 comments, all `government_response`). Nothing organic was swept in by the exclusion.

**One subreddit was kept despite low yield.** r/NorthCarolina is the weakest query in the set: only 11.5% (Helene) to 18% (Debby) of its in-window rows are thread-relevant, roughly 2,000 rows after filtering. Helene's North Carolina story actually lives in r/asheville (4,946 relevant rows), not the state subreddit. It was kept rather than dropped because Debby genuinely did flood the Carolinas, but it is flagged as a watch-list item that could affect the H5 tier comparison.

### Event windows, and the day that was removed

Reddit is filtered to the event window using **each row's own timestamp**. This matters because Reddit comments carry real per-comment timestamps, unlike Facebook, where a comment inherits its parent post's date. Hurricane threads keep collecting replies for months; before filtering, `days_from_landfall` ran as high as **+648**. A comment posted 21 months after landfall is not sentiment during the hurricane. Filtering is required for cross-platform comparability in H1 and for `days_from_landfall` to function as a meaningful axis in H2.

| Storm  | Dates           | Days from landfall |
| ------ | --------------- | ------------------ |
| Debby  | Jul 31 – Aug 5  | −5 … 0             |
| Helene | Sep 22 – Sep 27 | −4 … +1            |
| Milton | Oct 4 – Oct 9   | −5 … 0             |

Helene and Milton were originally collected at −3…+1 and −4…0. Both were extended back to −5 to match Debby, with append-only collection into separate `helene_ext/` and `milton_ext/` folders so existing files were untouched, and each storm replicating its own original collection method. Comments on the new early posts that were dated after the new days were dropped, so per-day counts for existing days did not change.

**Helene's day −5 was then removed again.** Hurricane Helene did not begin forming until September 22, and manual review of the 11 storm-relevant posts dated September 21 found **none genuinely Helene-related** — the matches were posts about the country Georgia, a tax-ballot item, and other-basin tropical systems. Rather than carry noisy rows, day −5 was dropped for Helene alone, giving the −4…+1 window above. The +1 day was retained. Sept 21 rows remain in the raw layer, so the decision is reversible.

---

## 3. Why `min_topic_size` was set to the values it was

`min_topic_size` sets the smallest cluster BERTopic may form. It has to scale with corpus size: the library default of 20 fragments a 120,000-row corpus into many tiny near-duplicate topics. It was therefore set per corpus, and it is the only clustering parameter we varied — HDBSCAN otherwise runs at library defaults.

| Corpus                        | min_topic_size | Topics | Outlier rate |
| ----------------------------- | -------------- | ------ | ------------ |
| facebook_posts                | 10             | 11     | 0.2%         |
| facebook_comments             | 150            | 44     | 44.2%        |
| reddit_posts                  | 30             | 14     | 34.1%        |
| reddit_comments               | 250            | 46     | 49.3%        |
| whitehouse (posts + comments) | 10             | 5      | 0.2%         |

**Facebook comments raised to 150.** At the default, roughly 50,000 comments fragmented into many small near-duplicate topics. At 150 the model yields 44 interpretable topics that map cleanly onto the codebook.

**Reddit floors scale with corpus size** — 30 for the ~3,400-post file, 250 for the ~121,000-comment file, the largest corpus in the project.

**White House lowered to 10, overriding the plan's suggested 20.** The reason is not topic quality in the main cluster — neither 10 nor 20 splits the dominant blob. At 10, the moderation and bot boilerplate separates into its own small clusters, which makes those rows easy to label and exclude from the H7 sentiment cut without editing the data.

### Pooling

Facebook posts and comments are modeled separately, and Reddit posts and comments are modeled separately, because they are different text types — broadcast forecast posts against short audience replies, which a shared model would blur. **White House posts and comments are modeled together**, because the post file holds only 12 rows, far too few to cluster on their own; the 12 posts are folded in with the 2,193 comments and the topic assignments split back out afterward. This matches the plan's stated default; the plan asked for confirmation before running, and the choice is documented here for that purpose.

### Preprocessing floor

Rows with fewer than five words are excluded from topic modeling but **kept in the sentiment analysis**, since HDBSCAN cannot meaningfully cluster "stay safe" or "prayers." Facebook comments lose the most to this floor: 9,797 of 59,736.

Note that this five-word floor is a BERTopic-only step. The general Reddit cleaning threshold is **fewer than three words**, applied earlier in the pipeline. The two are easy to confuse and are not the same rule.

### Outlier convention

HDBSCAN assigns documents it cannot cluster to topic −1. **We keep those excluded from the topic analyses, report the rate as a descriptive result, and apply the same convention uniformly across all six files.** We do not call `reduce_outliers()`.

The rate is high — near half of all comments — but this is normal for short social text and reflects the data rather than a tuning failure. Roughly 91,000 rows stay clustered, far more than the chi-square tests need. Three alternatives were considered and rejected: `reduce_outliers()` forces the model's honest "don't know" into a guess; tuning `min_samples` and switching to k-means likewise hide uncertainty rather than resolving it (k-means zeroes the outlier count by construction). One uniform convention across files also keeps the cross-source comparison fair, which a per-file choice would not.

This convention was not specified in the plan, so it is flagged here as an addition. It is reversible.

---

## 4. How `source_type` was assigned, including edge cases

`source_type` encodes **who is speaking to whom**, which is the distinction the entire cross-source comparison rests on. It has three values:

| Value                  | Meaning                                                           |
| ---------------------- | ----------------------------------------------------------------- |
| `government`           | Posts made by the White House account                             |
| `government_response`  | Comments on White House posts — the public replying to government |
| `community_discussion` | Organic Reddit posts and comments, no institutional communicator  |

**The field is not collected.** It is injected downstream as a constant per source, set while each source's data is prepared. The reason: it only ever _varies_ on the White House data. For all community Reddit it is the constant `community_discussion`, so requiring it in every raw collector would be redundant. It remains a required derived column, not a deleted one.

**Facebook is the edge case.** Facebook rows carry no `source_type` and are treated as Facebook via the `platform` column. Analysis code that groups by source bucket them explicitly rather than letting them fall through as null.

**The White House is a separate lane throughout.** WH data is normalized by its own script, bypasses the thread-relevance filter entirely (a White House hurricane thread is on-topic by definition, so a keyword cut would be meaningless), and joins the other sources only at the final merge. Folding it into the Reddit corpus was rejected: it has different tagging, different cleaning, and merging would destroy the community-versus-government distinction that H7 depends on.

### Two data-integrity bugs in this area — both changed the numbers

**Bug 1 — one post tagged to two storms at once.** The White House collector pulled the account over one wide date range, then tagged each post by searching its text for a storm name, in two independent passes. One post — an update on the response to Hurricane Milton — happens to name _both_ Milton and Helene, so it was written to both storms along with its 46 comments. Under Helene it sat at day **+16**, far outside any storm window; because White House data deliberately skips the window filter, it stayed in and padded Helene's comment count, directly inflating H7.

Fixed by deleting the Helene copies of all three cross-tagged posts (the other two are r/pics image posts excluded from analysis; all three are Milton-era), re-running the pipeline, and adding a single-storm assignment rule plus a seen-ID guard to the collector so it cannot recur. Corrected counts: **12 WH posts** (Helene 10, Milton 2) and **2,193 WH comments** (Helene 1,963, Milton 230).

**Bug 2 — White House content leaked into the Reddit corpus.** The Reddit keyword search had independently caught 5 White House posts and 973 of their comments, which already lived in the White House files. Those rows were counted twice under two different `source_type` values, which breaks any government-versus-community comparison by construction. Removed by matching on White House post IDs: Reddit posts **3,418 → 3,413**, Reddit comments **122,026 → 121,053**. All 973 removed rows were confirmed at row level to be White House comments parented to White House posts — not inferred from a total.

A residual of this bug persisted for several weeks: the removal was initially applied only to the processed and master files, leaving the intermediate `vader/` and `roberta/` directories still carrying the 978 rows. That was corrected later so that all three stages reconcile at 3,413 / 121,053.

**Reading the numbers:** any figure citing 122,026 Reddit comments or 3,418 posts is pre-deduplication. The correct counts are 121,053 and 3,413. Both appear in project history, and the difference is exactly this bug.

---

## 5. Facebook "Most Relevant" sort bias

This is a confound inherited from the Fall 2024 collection, and it is the most important limitation on the Facebook side of the corpus.

The Facebook data was collected by hand by three ISP students — one per storm — because Facebook's restrictions on scraping public pages blocked the automated attempts they tried first. Each copied material from two Florida meteorologist pages into spreadsheets. **Comments were taken under Facebook's "Most Relevant" ordering, capped at roughly 200 per post and 10 replies per thread**, and images were skipped.

"Most Relevant" is an engagement-ranked ordering, not a chronological or random one, and Facebook's ranking favors comments with high engagement. On a trusted local meteorologist's page, engagement skews toward supportive and appreciative replies — the "thank you Denis" genre. **The Facebook corpus is therefore plausibly biased toward positive and neutral sentiment relative to a random sample of the same threads.**

This is not a hypothetical concern. It compounds with a measured scorer bias: VADER's positive precision against the gold standard is 0.260 against a recall of 0.852, meaning it reads politeness and gratitude as positive sentiment. The sort over-samples exactly the comments the scorer mislabels, and both push the same direction on the Facebook side of H1 and H3.

Other Facebook constraints carried forward as limitations: hand entry, and timestamps recorded at the post level rather than per comment.

**Comment threads were collected from Phillips only.** Posts come from both pages — Phillips 545, Dee 407 — but Dee contributes zero comments; his threads were never collected. **Every comment-level result in this project is drawn from Phillips's audience alone**, and the paper should label the 59,736 Facebook comments accordingly. Re-collecting Dee's comment threads was considered and rejected as out of scope for the timeline.

### Other Facebook standardization choices

- **`author` is set to the page name** ("Denis Phillips" / "Greg Dee"). The raw data does not preserve commenter usernames, so the channel is the only available author signal. For Facebook this duplicates `source`, but it keeps the column non-null and consistent across the multi-source dataset.
- **A comment's `created_date` is its parent post's date.** The raw data has no per-comment timestamps. Day-level granularity is sufficient for `days_from_landfall`; the alternative (null dates) would have broken that column for about 99% of rows.
- **A year typo was corrected in the standardizer, not the raw file** — one Milton post dated 2025-10-05 instead of 2024-10-05. Fixing it in code preserves raw provenance and keeps the correction reproducible and logged. It is the only October 5 Milton post on file.
- **Placeholder strings** ("N/A", "none", "-", and similar) are normalized to empty during cleaning, because pandas otherwise round-trips them into ghost rows.

---

## 6. Where VADER and RoBERTa diverged

Both scorers run independently over the same rows, with both sets of columns stored side by side in every file. **Neither is designated primary.** Every claim is labeled with the scorer that supports it, and where the two disagree we report the disagreement rather than picking a winner. Method disagreement is one of this project's findings, not an inconvenience.

### Overall divergence

The two methods agree on the three-way label for **54.7%** of the corpus (102,483 of 187,359). The largest single off-diagonal cell is VADER-positive / RoBERTa-neutral at 18.9%. VADER-positive rows agree with RoBERTa only about a third of the time. Because this is measured on labels rather than scores, it is independent of scoring convention.

### Validated against humans, not against each other

Agreement between two automated scorers measures their similarity, not their correctness, so neither can validate the other. We built a 400-item human gold standard: 150 Facebook comments, 150 Reddit community comments, 50 White House thread comments, and 50 posts drawn proportionally to post-source size, sampled with a fixed seed. Both authors labeled all 400 independently in sessions of roughly 50, with no discussion during labeling.

Inter-annotator agreement: **Cohen's κ = 0.822 for sentiment** (raw agreement 90.5%) and **0.884 for the gratitude tag** (raw agreement 99.0%). Both are conventionally "almost perfect" and both sit far above the 0.5 threshold at which the plan pre-committed to flagging the advisor. The 38 sentiment and 4 gratitude disagreements were **not auto-resolved**; they were adjudicated jointly, and the gold standard carries a consensus label for all 400 items with none unresolved.

Evaluated against that consensus:

|                    | VADER     | RoBERTa   |
| ------------------ | --------- | --------- |
| Accuracy           | 0.487     | **0.728** |
| Macro F1           | 0.472     | **0.692** |
| Positive precision | **0.260** | 0.561     |
| Positive recall    | 0.852     | 0.685     |
| Neutral recall     | 0.416     | 0.710     |

**RoBERTa wins every class on every metric.** VADER's 0.487 sits below the majority-class baseline: always guessing neutral would score 245/400 = 0.61.

**VADER's failure is specific and mechanistically important.** Its positive class has recall 0.852 against precision 0.260 — it labels almost everything genuinely positive as positive, and a great deal that is not positive as positive, because it reads politeness and gratitude as positive sentiment. Its neutral recall drops to 0.416 as a direct consequence: the neutral comments it misses are being pulled into the positive class. This is the gratitude-inflation mechanism visible in the confusion matrix rather than inferred, and it matters beyond the method comparison, because it inflates the Facebook side of H1 and H3 and compounds with the "Most Relevant" sort bias described above.

**The data favors RoBERTa; only continuity with the Fall 2024 student work favors VADER.** An earlier version of the validation report implied the evidence supported keeping VADER for continuity; that was rewritten, because it did not. The recommendation is to lead with RoBERTa and keep VADER as a continuity baseline, but the choice is the advisor's and has not been formalized.

### Where divergence changed conclusions

- **H5** is the most method-sensitive test in the study. RoBERTa supports it in every storm; VADER supports it clearly only for Milton. Under the pre-agreed protocol (method disagreement, or a verdict that changes under the robustness check, goes to the advisor before write-up), Debby and Helene are flagged.
- **H7 splits across scorers, and its two sub-claims rest on different ones.** The negativity finding is clear under RoBERTa (WH mean −0.363 versus Reddit −0.232 and Facebook +0.048) but weak under VADER, where the pooled WH mean is **+0.024 — positive**. An earlier draft stated "White House more negative" as a general, both-methods result; that was wrong and was corrected to a RoBERTa-specific claim. Conversely the polarization claim is **VADER-only**: Levene's test finds White House comments significantly more dispersed than Reddit's under VADER (W = 62.7, p < .001) but not under RoBERTa (W = 1.1, ns). Neither sub-claim holds under both scorers.
- **The within-thread comparison is consistent across both scorers**, which makes it the most robust part of H7: comments mentioning FEMA, Biden, Trump, government, or conspiracy are reliably more negative than comments in the same threads that do not.

### The scoring-convention bug

RoBERTa emits three probabilities, but the statistical tests need one scalar per row comparable to VADER's compound. The two authors independently implemented this differently — one as the continuous difference `roberta_pos − roberta_neg`, the other by encoding the discrete label as {negative −1, neutral 0, positive +1}.

The result: **every VADER statistic matched to full precision; every RoBERTa statistic differed.** The gap ran through all seven hypotheses and was worst in Levene's test for H7, where the statistic came out 13.3 one way and 1.09 the other — the variance of a three-value label behaves nothing like the variance of a continuous score. A suspected data-path difference was ruled out by verifying the two source files were identical row for row; convention was the sole cause.

**Standardized on the continuous difference**, for three reasons: it is directly comparable to VADER's compound score, which is also continuous on [−1, +1]; the H2 regression slopes and H3 mean gaps have no meaning on a three-value encoding; and it preserves the model's confidence, which label encoding discards (0.95-positive and 0.51-positive both collapse to +1). The label encoding is not wrong as standard classification practice — it simply throws away magnitude. Once both authors used the continuous form, every shared statistic agreed.

Scoring details: `cardiffnlp/twitter-roberta-base-sentiment-latest`, with the model's recommended preprocessing (@mentions → `@user`, URLs → `http`). Inputs truncated at 512 tokens, with a per-row flag recording whether truncation occurred so its effect can be reported rather than assumed: **386 rows, 0.21% of the corpus** — concentrated in posts, negligible overall.

VADER uses the standalone `vaderSentiment` package rather than NLTK's bundled copy. The difference is emoji: NLTK scores emoji as 0.0, the standalone package feeds them into the compound score, and our corpus is emoji-heavy, so the two libraries genuinely disagree on this data. Thresholds are the standard ±0.05, matching what the Fall 2024 students used, and scoring is document-level.

### The Fall 2024 re-scoring finding

Re-scoring the original Facebook data through our pipeline reproduces **90.9%** of the students' saved scores exactly (40,390 of 44,447). The remaining 9.1% is fully accounted for: 2,199 rows differ because of the emoji lexicon, 1,453 because of version drift in the word lexicon and punctuation between VADER builds, 304 because of text-cleaning differences, and 101 because of a parsing bug in one student's code.

Auditing their code surfaced a finding in its own right, which their report does not mention: **the three students each used a different threshold.** Paige (Milton) used ≥0.05 / ≤−0.05, matching ours. Ivy (Debby) used a stricter >0.05 / <−0.05, so a score of exactly 0.05 counts as neutral rather than positive. Nicholas (Helene) used **≥0.5 / ≤−0.5 — ten times the standard cutoff** — and fed VADER the entire dataframe row (`row.to_string()`) instead of the cleaned comment text, saving only daily totals, so no per-comment scores exist at all.

Consequences: Helene cannot be reproduced at the comment level from what the students saved, and Debby's labels disagree with ours precisely at the 0.05 boundary. Both point to the same fix — re-score every comment ourselves with one consistent setup, which is what we did.

---

## 7. Topics merged or relabeled

BERTopic returns top-word representations, not names. Each author independently drafted readable labels for their own corpora, then reconciled them into one shared codebook **before any cross-source comparison ran**. That ordering is load-bearing: a Reddit topic called "evacuation" and a Facebook topic called "leaving town" have to land under the same label, or the comparison measures vocabulary instead of content.

Labels roll up into nine categories: _gratitude, preparedness, forecast analysis, evacuation logistics, political / FEMA criticism, government resources, personal experience, emotional response, misinformation_. Every label maps to exactly one category, verified across all six files with zero conflicts.

### Merge groups identified per file

- **Facebook comments** — gratitude (topics 5, 17, 24, 33, 34, 38), prayers (10, 14, 31, 32), location mentions (11, 13, 28, 42), travel (1, 9), preparation (36, 37)
- **Facebook posts** — the county-by-county automatically issued NWS/ABC tornado warnings (topics 1–9) collapse into a single "Tornado warning alert" label
- **Reddit posts** — general discussion (0, 1, 11)
- **Reddit comments** — model talk (19, 24, 40), location (3, 25, 34), political (0, 5, 27)
- **White House** — no merges; the corpus is homogeneous

Assessed per file: posts cluster cleanly, comments fragment, and the White House corpus is too homogeneous to split.

### Relabeling decisions

**Tornado-alert posts classified as `government resources`.** These are automatically issued warnings and account for roughly 22.7% of Facebook posts. Excluding them as automated non-discourse was considered and rejected for now; the decision is reversible.

**White House comment categories broken out six ways.** The advisor flagged that every substantive White House comment sat in a single `political / FEMA criticism` bucket — too coarse for H7. The category was remapped from the finer-grained labels: political and FEMA reaction → `political / FEMA criticism` (1,972); moderation and trolling → `subreddit moderation removal` (29); misinformation-removal notices → `misinformation removal` (28); comments about which subreddit posted → `reaction to government Reddit presence` (21); the Georgia moderator link-removal incident → `Georgia moderator incident` (19); too-short and outlier rows → `excluded` (124). H7 can now show moderation and gatekeeping at distinct rates. Note that `misinformation removal` means **moderator removal notices**, not the misinformation stance itself.

These four White House–only categories are structural zeros for Facebook and Reddit, so the cross-source chi-square runs on the nine shared categories only.

**Moderation and bot boilerplate kept in the data, handled at label time.** Roughly 50–100 AutoMod and removal-notice rows remain in the White House comments file. Rather than re-clean after scoring, `min_topic_size = 10` isolates them into their own small topics, which are labeled non-substantive and excluded from the H7 sentiment cut without editing data.

**Misinformation is not a standalone topic category.** BERTopic produced no misinformation topic in any file. The reason is conceptual rather than a tuning failure: misinformation is a cross-cutting _stance_ that rides on FEMA, political, and weather content, not a semantically distinct cluster, so it absorbs into the political/FEMA blob. H6 and H7 name misinformation explicitly, so this was raised with the advisor, who resolved it: **misinformation will not be used as a standalone topic category**; H6 and H7 refer to political and FEMA-critical discourse instead. A keyword-flag plus manual-review pass was designed as an alternative and is not being run. A directional signal from raw keyword rates (an upper bound only) is consistent with H7: White House 0.96% > Reddit 0.24% > Facebook 0.06%.

**White House topical homogeneity is reported as a finding, not tuned away.** About 95% of White House comments cluster into one FEMA/government/political topic, and no `min_topic_size` value splits it. The cause is the data — near-identical FEMA-aid posts and same-vein political reactions embed as one dense blob. Forcing sub-topics via seeding was rejected as manufacturing arbitrary structure. H7 rests on sentiment polarization, which is measured directly, rather than on topic variety, so the homogeneity does not weaken it.

### Two findings that fell out of reconciliation

- **Gratitude is Facebook-only.** Reddit and White House gratitude shares are approximately zero.
- **Political / FEMA criticism is Reddit and White House only**, approximately zero on Facebook.

---

## 8. Corpus structure and the master file

**The dataset is maintained as six separate files split by source and unit**, not one merged table:

| File                        | Rows        |
| --------------------------- | ----------- |
| facebook_posts              | 952         |
| facebook_comments           | 59,736      |
| reddit_relevant_posts       | 3,413       |
| reddit_relevant_comments    | 121,053     |
| whitehouse_threads_posts    | 12          |
| whitehouse_threads_comments | 2,193       |
| **Total**                   | **187,359** |

The advisor's instruction was to keep the six files separate rather than build a unified master, for cleaner provenance and so each source is analyzed in its own right; cross-source comparisons read the relevant files side by side. The written plan, however, specifies a `master_vader_roberta_topics.csv`. Both exist: the six files are the source of truth, and a derived master is built last by concatenating them with a `provenance` column, used for cross-source analysis. The master is never edited directly — it is regenerated. **Which of the two is canonical remains an open question for the advisor.**

Two guardrails run on every rebuild: a row-count assertion (187,359) and a duplicate-ID check keyed on id + source. Both pass. **The plan's stated guardrail of 186,722 is stale** — it predates the Reddit window extensions, and the difference (+637) is exactly those extensions.

A `hurricane` label casing bug was found and fixed here: Facebook stored Title case while Reddit and White House stored lowercase, so the concatenated master carried six values for three storms and any `groupby('hurricane')` silently split each storm in two.

---

## 9. Statistical methods

- **Mann–Whitney U** for two-group comparisons (H1, H7), chosen over a t-test because sentiment scores are bounded on [−1, +1], concentrated near zero, and not normally distributed.
- **Rank-biserial correlation** as the effect size alongside every Mann–Whitney test, computed as `2U / (n₁n₂) − 1`. **Treated as the headline number instead of the p-value.** At 60,000–120,000 comments essentially any difference clears p < .001, so the p-value carries almost no information; the rank-biserial gives the size of a difference on a bounded, interpretable scale.
- **Kruskal–Wallis H** for three or more groups (H4, H5), reported with epsilon-squared as the omnibus effect size. Pairwise Mann–Whitney tests follow only when the omnibus is significant, Bonferroni-corrected.
- **Chi-square tests of independence** on categorical labels and topic categories, reported with Cramér's V, uncorrected for bias.
- **Levene's test** centered on the median (the Brown–Forsythe variant) for equality of variance, which is how polarization is measured in H7 — a group can have an unremarkable mean while being far more internally divided.
- **OLS regression** of sentiment against `days_from_landfall` per platform for H2, with an interaction model testing whether the slopes differ. This is the one test that strictly requires a continuous score.
- **Bootstrap** with 10,000 resamples for the H3 Facebook–Reddit gap confidence intervals.

**Unit of analysis is the comment unless otherwise stated.** Comments are the audience-response unit and the only unit available in sufficient volume across all three sources; post-level analysis is reported only where posts are numerous enough, which excludes the 12 White House posts. All seven hypotheses are tested twice, once per scorer.

---

## 10. Reproducibility defects found in the Week 8 re-run

The Week 8 pass re-ran the pipeline from scratch and verified outputs byte-for-byte (32 of 32 stages, 132 outputs identical). It also surfaced eight defects. **Three affected results and are recorded here in full**, because a decision log that lists only intended choices would misrepresent the corpus.

**Result-affecting:**

1. **`build_ground_truth.py` was silently destroying the gold standard.** The script fills `label_consensus` only where the two annotators agreed, so re-running it blanked the 38 sentiment and 4 gratitude hand-adjudications and cut `ground_truth_400.csv` from 400 rows to 362. Every accuracy figure in the method validation depends on that file. The file was restored, the script now refuses to overwrite an adjudicated copy without an explicit environment flag, and it is excluded from the re-run driver. **`ground_truth_400.csv` is a curated artifact, not a reproducible output**, and should be treated as such.
2. **The H3 bootstrap confidence intervals were never reproducible.** They were seeded with `100 + hash(hurricane) % 100`, and Python randomizes string hashing per process, so the CI bounds moved in the third decimal on every run. Replaced with fixed seeds. Gaps and p-values were unaffected.
3. **Nothing in the repository generated the White House VADER files.** `run_vader_wh.py` was a byte-identical copy of the Facebook runner, misnamed in an earlier commit. A correct script was written and reproduces both White House files exactly.

**Also fixed:** `evaluate_methods.py` reverted an advisor-review wording change on every run; `clean_whitehouse_data.py` consumed its own output on a second run and used a bare relative path; `plot_landfall_trajectories.py` had a broken repository root and stale filenames and could not run at all; `three_way_comparison.py` hardcoded its output path; `build_master.py` wrote the repository's only CRLF file, re-hashing the master on every rebuild.

**Stale data corrected:** the three-way comparison tables were pre-deduplication, stale by exactly the 978 White House rows.

**Benign divergence documented:** two Reddit files were committed with Windows line endings while the re-run writes Unix ones. Verified content-identical — same rows, same IDs, same order, zero differing cells.

**Five collection scripts existed only as compiled `.pyc` files** and were recovered from local backups. The six raw Facebook workbooks are now committed, so the Facebook stage is reproducible from raw for the first time and rebuilds its output byte-identically.

### Collection reproducibility

Collection was re-executed live against Arctic Shift into a separate directory, leaving the frozen corpus untouched. Drift over roughly two months: **community Reddit 135,780 → 135,783 rows, one removed and four added, 0.004%.** Every post file and both window extensions were identical. The apparent White House delta (+8 posts, +660 comments, 0 removed) is a raw-versus-filtered method difference, not drift — the raw pull retains non-storm White House posts that the storm-tagged files exclude.

**Decision: the frozen corpus remains the analysis basis.** The re-collection _validates_ the corpus by proving it re-collects faithfully; adopting the fresh pull would force regenerating every figure and statistic for a five-row difference. The GPU stages were verified separately: RoBERTa re-scoring on Colab was **bit-identical** across all 124,466 Reddit rows (0.00e+00 maximum probability difference, zero label flips), and the five saved BERTopic models were verified against the Week 4 run log rather than re-fit, because UMAP and HDBSCAN are not version-stable and a re-fit would shift topics away from what the paper reports.

---

## Standing conventions

- Target venue: FLAIRS-40 (2027), 6 pages plus references.
- Colors: Facebook blue, Reddit community orange, White House / government green. All figures exported at 300 dpi PNG and vector PDF.
- `days_from_landfall = 0` on the landfall date: Debby Aug 5, Helene Sep 26, Milton Oct 9.
- White House account handle: `u/whitehouse46`.
- White House threads are reported factually, with no editorial commentary, keeping the focus on communication dynamics rather than politics.
