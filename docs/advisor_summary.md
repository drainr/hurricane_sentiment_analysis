# Advisor Summary

**Hurricane Sentiment Analysis — Summer 2026**
Jose Araya, Angelo Morelli
End-of-project summary for advisor review

---

## Headline finding

**What a platform _hosts_ is a stronger signal than how positively it _talks_: the association between source and topic (Cramér's V = 0.385) is larger than any sentiment difference we measured (V = 0.158–0.224), meaning Facebook, Reddit, and government threads differ more in the kind of hurricane discourse they carry than in its emotional tone.**

The corollary is the practically useful part: a communicator reading "how the public feels" from Facebook comments is not measuring public sentiment. They are measuring an audience that self-selected into a gratitude-oriented, communicator-facing space, one that structurally excludes most of the political and forecast-uncertainty discourse happening elsewhere.

---

## The seven hypotheses

|        | Hypothesis                                                                 | Verdict                                                | Basis                                                                                                                                                                         |
| ------ | -------------------------------------------------------------------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **H1** | Reddit shows lower sentiment than Facebook                                 | **Supported**                                          | Both scorers, every storm and pooled, all p < .001. Rank-biserial VADER +0.129, RoBERTa +0.295                                                                                |
| **H2** | Reddit declines more sharply than Facebook toward landfall                 | **Not supported**                                      | Interaction term positive under both scorers — the opposite direction. R² ≈ 0 in every pooled model                                                                           |
| **H3** | The Facebook–Reddit gap widens for stronger storms                         | **Not supported**                                      | Under RoBERTa the gap declines monotonically in storm _sequence_: 0.318 → 0.286 → 0.240. Ordered by intensity it is not monotonic — Helene, the strongest, sits in the middle |
| **H4** | Reddit accumulates negativity while Facebook stays stable                  | **Partial**                                            | Cross-storm movement is significant everywhere, but Facebook moved _more_ (RoBERTa H = 644.0 vs Reddit 245.1)                                                                 |
| **H5** | Expert subreddits are more neutral than local/statewide                    | **Supported, method-sensitive**                        | RoBERTa significant in all three storms; VADER only in Milton                                                                                                                 |
| **H6** | Facebook centers on gratitude/preparedness, Reddit on forecasts/evacuation | **Supported strongly**                                 | χ² = 26,713, V = 0.385 — the largest effect in the study                                                                                                                      |
| **H7** | White House comments are more polarized and differ from Facebook           | **Supported for negativity, partial for polarization** | Negativity holds under both scorers, clearest under RoBERTa; polarization is VADER-only                                                                                       |

**Three of the seven ran against prediction (H2, H3, and the mechanism half of H4), and we recommend reporting them as findings rather than softening them.** Both H2 and H3 fail in a specific, interpretable direction, and H2's near-zero R² indicates the failure is structural: sentiment change during these events is storm-specific and non-linear, so a linear "anxiety rises as landfall nears" model is simply the wrong shape. Milton's sentiment _rises_ into landfall on both platforms, plausibly relief once track and intensity became clear.

**Helene, not Milton, was the most intense storm** (Cat 4 at landfall, against Milton's Cat 3 and Debby's Cat 1), and that single fact does real work in interpreting H3 and H4. Intensity order is Debby < Milton < Helene; sequence order is Debby → Helene → Milton. The two orderings therefore **disagree**, which means they are partially separable rather than fully confounded — and every result we have follows sequence, not intensity:

- **H3.** The RoBERTa gap declines monotonically in _sequence_ (0.318 → 0.286 → 0.240). Ordered by _intensity_ it is not even monotonic (Debby 0.318, Milton 0.240, Helene 0.286). The most intense storm sits in the middle.
- **H4.** Milton produced the most negative discourse despite being a category weaker than Helene. If intensity drove sentiment, Helene should be the negative extreme; it is not.

So the honest claim is stronger than a confound disclaimer: **across these three storms, sentiment tracks storm sequence and recency, not storm strength.** That is a cleaner finding and should be stated as such.

Two cautions. Three storms cannot fully separate sequence from intensity, since a partial dissociation is not a controlled comparison, and Milton carries other storm-specific factors (rapid intensification, landfall two weeks after Helene). And **the paper must state which intensity measure it uses**: Milton peaked at Cat 5 over the Gulf before weakening to Cat 3 at landfall, so a reader using peak intensity would rank the storms differently. We use landfall category throughout, consistent with the research plan.

---

## The White House story

The White House Reddit account (`u/whitehouse46`, 12 posts and 2,193 comments during Helene and Milton only) behaved like neither of the other two sources, and it is the closest thing the project has to a natural experiment separating the communicator effect from the platform effect. It is an institutional communicator posting into an open, unmoderated community space — the same _content_ type as Phillips's Facebook updates, delivered in the same _venue_ as organic Reddit. Under RoBERTa, White House comments are the most negative source in the dataset (M = −0.363, against Reddit −0.232 and Facebook +0.048), and the White House–Facebook contrast (rank-biserial −0.436) is among the largest effects anywhere in the study. They are also the most topically concentrated source we measured: 95.3% political/FEMA criticism. Rather than the gratitude-and-reassurance pattern seen on a trusted local meteorologist's page, an official federal account **inherited Reddit's critical register and amplified it.** The most robust component is the within-thread comparison, which holds under both scorers: comments containing politicized language (FEMA, Biden, Trump, government, conspiracy) are reliably more negative than comments in the same threads without it, indicating politicization is a mechanism operating inside the threads rather than an artifact of who chose to comment. Two caveats belong in any write-up: the polarization claim rests on VADER alone (Levene W = 62.7, p < .001) and does not replicate under RoBERTa (W = 1.1, ns); and the pooled result is roughly 90% Helene, with the White House–Reddit gap disappearing for Milton (p = .482).

---

## The three or four most important figures

1. **Topic distribution by source type** _(currently Figure 10 in the results draft; file `f7_topic_distribution_by_source_type`)_ — carries the headline finding. Shows gratitude as essentially Facebook-exclusive, Reddit split across personal experience / forecast analysis / political criticism, and the White House at 95.3% political-FEMA. This is the single most important figure in the paper.
2. **Mean sentiment by source and hurricane, RoBERTa** _(Figure 3; `f3_three_way_roberta`)_ — carries H1, H3, and H7 simultaneously in one panel, with significance brackets and the White House bars visible against both baselines.
3. **VADER × RoBERTa agreement heatmap** _(Figure 2; `f6_vader_roberta_agreement`)_ — 54.7% agreement, with the large VADER-positive / RoBERTa-neutral cell making the gratitude-inflation mechanism visible rather than asserted. This figure carries the methodological contribution.
4. **Temporal trajectories by days from landfall** _(Figures 7–8; `h2_temporal_curves`)_ — the honest null. Three storms with three different shapes is exactly why the pooled linear model fails, and the figure shows that better than the regression table does.

If the 6-page limit forces a cut, drop the fourth and describe H2 in text.

---

## Novelty claim

Three components, in descending order of strength:

1. **A three-way cross-source comparison holding the event constant.** Prior disaster-sentiment work is overwhelmingly Twitter-based and single-platform. Comparing a trusted individual communicator's audience, organic peer-to-peer community discussion, and official government communication _for the same storms in the same windows_ isolates venue as a variable in a way single-platform studies cannot.
2. **The government-account-in-a-community-space natural experiment.** The White House posting into Reddit holds the platform fixed while changing who is speaking, which partially disentangles the communicator effect from the platform effect. We are not aware of prior hurricane work using this configuration.
3. **A quantified, mechanistically explained lexicon-scorer failure.** We do not merely report that VADER and RoBERTa disagree; we show _where_ (positive precision 0.260 against recall 0.852), _why_ (politeness and gratitude read as positive sentiment), and _what it distorts_ (the Facebook side of H1 and H3, compounding with Facebook's engagement-ranked comment sort). This is directly useful to anyone applying VADER to communicator-facing social data.

The 400-item adjudicated gold standard (κ = 0.822 sentiment, 0.884 gratitude) is what makes claim 3 defensible rather than anecdotal.

---

## Biggest limitations

1. **Facebook comments are engagement-sorted, not random.** They were collected under "Most Relevant" ordering, capped at ~200 per post, which favors high-engagement replies — on a trusted meteorologist's page, the appreciative ones. The Facebook corpus is plausibly biased toward positive sentiment, and this pushes the _same direction_ as VADER's gratitude bias. H1 and H3 should be read as upper bounds on the Facebook–Reddit gap.
2. **Facebook comments are one communicator's audience.** Greg Dee contributes posts only; every comment-level result comes from Phillips's audience alone.
3. **Corpus composition is unbalanced by storm.** Milton is roughly two-thirds of the Reddit relevant corpus.
4. **Intensity and sequence are only partially separable.** They dissociate here (Helene is the most intense but middle in the sequence) and every result follows sequence, but three storms is not a controlled comparison, and Milton carries storm-specific factors beyond its position in the season.
5. **H7 is largely Helene.** The White House account has 1,963 Helene comments against 230 for Milton, and several H7 results do not hold for Milton alone.
6. **Facebook comments inherit their post's timestamp**, so Facebook's temporal resolution in H2 is coarser than Reddit's genuine per-comment timestamps.
7. **BERTopic outlier rates are high for comments** (~44–49%). That's normal for short social text, but it means the topic results describe only the clustered subset — roughly 91,000 rows.
8. **English-only, three storms, one season** — no claim to generalize beyond the 2024 Atlantic season.

---

## Suggested paper title

**Preferred:** _Venue Shapes Discourse: A Cross-Source Sentiment and Topic Analysis of Three 2024 Atlantic Hurricanes_

Alternatives:

- _Who Is Speaking to Whom: Platform, Communicator, and Government Voice in Hurricane Social Media_
- _Gratitude Is Not Sentiment: Cross-Platform Sentiment and Topic Structure During Hurricanes Debby, Helene, and Milton_

---

## Rough abstract draft

> Social media sentiment is widely used as a proxy for public response during hurricanes, but most studies draw on a single platform, leaving open whether observed sentiment reflects the public or the venue. We analyze 187,359 posts and comments spanning three 2024 Atlantic hurricanes (Debby, Helene, Milton) across three communication settings that differ in who is speaking to whom: comments on a trusted local meteorologist's Facebook page, organic discussion across nine hurricane-relevant subreddits, and comments on posts by the official White House Reddit account. Every record is scored independently by VADER and a RoBERTa transformer and assigned a topic with BERTopic, and both scorers are evaluated against a 400-item human gold standard adjudicated by two annotators (Cohen's κ = 0.822). Facebook sentiment is significantly more positive than Reddit's in every storm, but the larger effect is topical rather than emotional: the association between source and topic (Cramér's V = 0.385) exceeds every sentiment-based effect we measure, and it persists when platform is held constant by comparing organic Reddit against government-response threads on the same platform (V = 0.303). Gratitude content is nearly exclusive to Facebook, while White House threads are the most topically concentrated and, under RoBERTa, the most negative source in the corpus. Hypotheses predicting that sentiment would track storm intensity or decline linearly toward landfall were not supported: negativity followed the order in which the storms arrived rather than their strength, with the most intense storm of the three falling in the middle on every sentiment measure. We further show that the lexicon scorer systematically misreads politeness as positive sentiment (positive precision 0.260 against recall 0.852), inflating exactly the platform where person-directed gratitude concentrates. Our results indicate that the sentiment and topic profile of hurricane social media is shaped first by the structure of the venue and only secondarily by the severity of the storm, with direct implications for how agencies interpret social media during crises.

Roughly 245 words; trim the penultimate sentence if the venue caps at 150–200.

---

## Recommendation: White House as a Results subsection

**Keep the White House analysis as H7 within Results, and carry its interpretation into the Discussion.** Three reasons:

1. **It is a hypothesis with real statistics behind it**, not a vignette — Mann–Whitney comparisons against two baselines, Levene's test for polarization, a within-thread political-language contrast, and a per-storm breakdown. Moving it to Discussion would strand those tests outside the section where every other test lives, and a reader looking for H7 would not find it alongside H1–H6.
2. **Its value depends on comparison.** The White House result is only meaningful _against_ the Facebook and Reddit baselines, which live in Results. Presented separately it becomes a description of one account rather than the third arm of a three-way design.
3. **The 6-page limit.** A standalone section would duplicate framing already carried by Figures 3 and 10.

The natural-experiment framing — an institutional communicator in a community space, holding platform fixed while varying who speaks — is genuinely the most novel thing in the paper, and it belongs in the **Discussion**, where it can do interpretive work without pulling the statistics out of Results. This is also how the current results draft is already written, so no restructuring is required.

**One caveat if the advisor prefers a standalone treatment:** it would be defensible if H7 were reframed around the _communicator-versus-platform_ question rather than the polarization prediction, since the polarization half is the weakest result in the study (VADER-only, not replicated under RoBERTa). That would be a larger rewrite and is not our recommendation.

---
