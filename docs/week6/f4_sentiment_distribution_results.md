# F4 — Sentiment Distribution (comment-level)

100% stacked % negative/neutral/positive by source × hurricane, from the master (comments only). White House has no Debby data.

## VADER

| source           | hurricane | n      | % neg | % neu | % pos |
| ---------------- | --------- | ------ | ----- | ----- | ----- |
| Facebook         | debby     | 16,199 | 15.7  | 35.4  | 48.9  |
| Reddit community | debby     | 8,766  | 29.6  | 26.0  | 44.4  |
| Facebook         | helene    | 14,229 | 15.5  | 36.9  | 47.7  |
| Reddit community | helene    | 32,948 | 29.6  | 27.6  | 42.8  |
| White House      | helene    | 1,963  | 36.4  | 21.8  | 41.8  |
| Facebook         | milton    | 29,308 | 19.3  | 38.2  | 42.5  |
| Reddit community | milton    | 79,339 | 32.4  | 26.5  | 41.1  |
| White House      | milton    | 230    | 33.9  | 18.7  | 47.4  |

## RoBERTa

| source           | hurricane | n      | % neg | % neu | % pos |
| ---------------- | --------- | ------ | ----- | ----- | ----- |
| Facebook         | debby     | 16,199 | 19.7  | 49.6  | 30.7  |
| Reddit community | debby     | 8,766  | 39.6  | 46.8  | 13.6  |
| Facebook         | helene    | 14,229 | 18.7  | 53.9  | 27.5  |
| Reddit community | helene    | 32,948 | 38.6  | 48.0  | 13.4  |
| White House      | helene    | 1,963  | 54.8  | 35.5  | 9.8   |
| Facebook         | milton    | 29,308 | 24.4  | 53.2  | 22.4  |
| Reddit community | milton    | 79,339 | 41.7  | 47.2  | 11.1  |
| White House      | milton    | 230    | 47.0  | 36.5  | 16.5  |

Figures: `figures/f4_sentiment_distribution_{vader,roberta}.png/.pdf` (300 dpi).
