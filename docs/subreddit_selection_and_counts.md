# Subreddit selection and comment counts

This document covers which subreddits were collected, why each one was included, and how many comments each holds per hurricane.

## Where the subreddits come from

They come from two separate collections, and that split is the easiest way to read the list.

The first group is the subreddits searched on purpose. For each storm we pulled nine subreddits over that storm's date window. This is most of the data, about 210,000 comments.

The second group comes from the White House account. We collected everything u/whitehouse46 posted, plus the replies. That account posted in subreddits we never searched ourselves, including r/southcarolina, r/Tennessee, r/Virginia, and r/pics. Those show up because the White House posted there, not because we went looking in them.

## Why these subreddits

We started with four:

- r/TropicalWeather: the serious weather sub, with real meteorologists and big storm threads. Our cleanest source.
- r/tampa: same area as Denis Phillips' Facebook audience, so we can compare Facebook and Reddit on even footing.
- r/florida: the whole state reacting.
- r/sarasota: where Milton came ashore.

Then we added more, mostly to follow where each storm actually hit and where people were talking:

- r/hurricane: another general weather sub, busy for all three storms.
- r/HurricaneHelene: a sub made just for Helene. Small, but almost all of it is on topic.
- r/asheville: the big one. Helene's worst damage was inland flooding around Asheville, not the coast, and the state sub barely covered it. Most of the Helene conversation in North Carolina lives here.
- r/Georgia: both Debby and Helene moved through Georgia.
- r/NorthCarolina: Debby flooded the Carolinas, but only a small slice of this sub is actually about the storm, so we're keeping it for now and watching it.

The White House also posted recovery info into the inland states Helene hit hardest (r/southcarolina, r/Tennessee, r/Virginia) and into r/pics, where it shared relief photos. We kept those to see how the government communicated during the storms. The account also posted unrelated things in places like r/MadeMeSmile and r/aviation, and we drop those.

## Comment counts

Raw counts straight from collection, before any cleaning. A blank means we didn't pull that subreddit for that storm. Full file: `data/merged/subreddit_comment_counts.csv`.

| Subreddit | Category | Debby | Helene | Milton | Total |
|---|---|--:|--:|--:|--:|
| r/florida | statewide | 15,889 | 17,731 | 20,326 | 53,946 |
| r/TropicalWeather | meteorological | 2,515 | 11,530 | 27,024 | 41,069 |
| r/tampa | local | 4,151 | 7,182 | 16,845 | 28,178 |
| r/NorthCarolina | statewide | 8,143 | 9,736 | 5,111 | 22,990 |
| r/hurricane | meteorological | 766 | 5,761 | 16,341 | 22,868 |
| r/Georgia | statewide | 8,658 | 10,499 | 2,660 | 21,817 |
| r/asheville | local | — | 11,910 | — | 11,910 |
| r/sarasota | local | 2,943 | 1,902 | 2,955 | 7,800 |
| r/HurricaneHelene | meteorological | — | 244 | — | 244 |
| **Total** | | **43,065** | **76,495** | **91,262** | **210,822** |

These are raw numbers. After cleaning and keeping only storm-related comments, the set drops to about 124,000. The table can be rebuilt on the cleaned set if needed.

The White House counts are kept separate: 18 posts and 5,381 comments in total. Those can be broken down by subreddit if needed.
