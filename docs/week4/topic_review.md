# Topic review — overlap, quality, and parameters per file

Week 4 joint deliverable. For each of the six files, this covers three things: which topics are really the same theme split apart and should be merged before any cross-file comparison, whether the topics overall look clean or fragmented, and what `min_topic_size` was used. Topic ids and counts come from the labeled files in `data/processed/`.

---

## 1. Topics that should be merged

### facebook_comments (44 topics) — the messiest file

A lot of these topics are the same theme under different ids. The groups to collapse:

- **Gratitude/trust toward the forecaster:** topics 5, 17, 24, 34, 38, and 33. These are all people thanking Denis Phillips or saying he's the only one they trust ("only one I trust," "thank you for the updates"). This is the group Tania pointed out, and it's the clearest case: five or six topics for one idea.
- **Prayers and well-wishes:** topics 10, 14, 31, 32. Two of them are even labeled "Prayers and faith." It's all supportive/religious boilerplate.
- **Location-specific impact:** topics 11, 13, 28, 42, all with that exact label. The model split these by which town people named, not by any real difference in theme.
- **Travel and plans impact:** topics 1 and 9, same label.
- **Preparedness:** topic 36 (home prep) and 37 (supplies prep).
- **Forecast detail:** this one's looser. Storm surge is 3 and 25; track/direction/eye is 16, 29, 30, 42; timing is 23 and 26; plus 0, 8, 18, 35, 39, 41, 43. Each is a real forecast sub-theme, so forcing them into one topic doesn't make sense, but they all roll up to `forecast analysis` in the codebook anyway.

### facebook_posts (11 topics)

Topics 1 through 9 are all the same thing: the county-by-county tornado warnings that get auto-issued by NWS/ABC. They're near-identical templates, so collapse them into one "Tornado warning alert" label (already done in the codebook). Topics 0 (forecast/tracking) and 10 (prep checklist) are genuinely separate.

### reddit_relevant_posts (14 topics)

Topics 0, 1, and 11 are all "General hurricane discussion" — same label, just split by size. The rest are distinct enough (evacuation, prep/insurance, FEMA aid, FEMA/political, storm surge, formation outlook).

### reddit_relevant_comments (46 topics) — fragmented like FB comments

Same story as the Facebook comments. Groups to merge:

- Model/forecast talk: topics 19, 24, 40.
- Location-specific impact: topics 3, 25, 34.
- Past-hurricane comparison: topics 9, 39.
- Weather influencers and media: topics 15, 41.
- Politics/FEMA/climate: topic 0 (partisan reaction), 5 (FEMA and political), 27 (climate-change debate), all `political / FEMA criticism`.
- Travel/relocation: topic 4 (relocation chatter) and 35 (travel and plans).

The forecast facets (surge 13, track 14/30/42, timing, and so on) roll up to `forecast analysis` the same way they do for Facebook.

### whitehouse_threads (posts and comments, modeled together)

Nothing to merge here, and that's actually the point — see section 2. There's one substantive topic (0: FEMA/political, about 90% of the comments plus all 12 posts) and four tiny moderation/boilerplate topics (1–4) that are worth keeping separate so we can drop them from the H7 sentiment cut.

---

## 2. Do the topics look meaningful or fragmented?

- **facebook_posts:** meaningful, with one artifact. The only problem is the nine tornado-alert topics, and those aren't nine real themes — they're the same automated template repeated by county. Collapses to one and the file's fine.
- **facebook_comments:** the themes themselves are clear, but the model over-split almost everything: gratitude into five or six topics, prayers into four, location into four, forecast into about fourteen. Once you merge the groups in section 1 it cleans up into something comparable. The 44.2% outlier rate looks alarming but it's normal for short, noisy social comments under HDBSCAN.
- **reddit_relevant_posts:** mostly clean. The only duplication is "General hurricane discussion" showing up three times.
- **reddit_relevant_comments:** meaningful but fragmented, same pattern as the FB comments — real themes chopped into a lot of granular topics. About 46% outliers. Interpretable after the merges.
- **whitehouse_threads:** the opposite problem. Around 90% of the comments (and all 12 posts) sit in one FEMA/government/political topic, and no `min_topic_size` splits it. That's not a tuning failure — the data is one tight blob. The WH posts are basically the same FEMA-aid template over and over, and most of the comments are political reactions living in the same semantic space. We're reporting the homogeneity as a finding because it actually supports the H7 framing; H7 rests on the sentiment polarization we already measured, not on topic variety.

---

## 3. `min_topic_size` per file

| File                        | min_topic_size | Topics | % outliers (−1) | Notes                                                                                                                                                 |
| --------------------------- | -------------: | -----: | --------------: | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| facebook_posts              |             10 |     11 |            0.2% | small file, left near the default                                                                                                                     |
| facebook_comments           |            150 |     44 |           44.2% | raised from the default 20. At 20 the ~50k-row file shattered into a lot of tiny near-duplicate topics; 150 gives a readable 44                       |
| whitehouse (posts+comments) |             10 |      5 |            0.2% | dropped from the plan's suggested 20 to 10 so the moderation boilerplate breaks off into its own small topics. Neither value splits the main 90% blob |
| reddit_relevant_posts       |             30 |     14 |            ~33% | Angelo's Colab run; read off the saved model config. A bigger floor than FB posts, scaling with the larger corpus                                     |
| reddit_relevant_comments    |            250 |     46 |            ~46% | Angelo's run, from the saved config. The biggest floor, for the ~121k-row corpus — same idea as FB comments at 150                                    |

The Student B values and full reasoning are in `docs/bertopic_run_log.md`. The two Reddit numbers came out of Angelo's saved BERTopic configs, since they weren't in the run log. They scale with corpus size (3.4k posts → 30, 121k comments → 250), which matches the logic used for the Facebook comments. If Angelo tried other values first and changed them, that should get noted too.

---

## 4. Renaming the topic JSONs

Tania wants the saved `topics.json` files named by source so they're easy to tell apart on download:

- `topic_facebookpost.json`, `topic_facebookcomment.json`
- `topic_redditpost.json`, `topic_redditcomment.json`
- `topic_whitehouse.json` (posts and comments share one model)

These get renamed in Drive (José).
