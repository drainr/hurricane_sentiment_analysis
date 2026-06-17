# RoBERTa Processing Log — Week 3

*Prepared with the help of Claude*

Record of the RoBERTa sentiment scoring run for the hurricane sentiment project.

## Setup
- **Model:** `cardiffnlp/twitter-roberta-base-sentiment-latest` (TweetEval; trained on ~124M tweets, 2018–2021)
- **Approach:** `AutoTokenizer` + `AutoModelForSequenceClassification` + `scipy.special.softmax`; labels read from `config.id2label` → `{0: negative, 1: neutral, 2: positive}`
- **Preprocessing:** `@mentions → @user`, URLs → `http` (the CardiffNLP-recommended social-media preprocessing; applied to every text before scoring)
- **Truncation:** `truncation=True, max_length=512`; each row carries a `roberta_truncated` flag if its input exceeded 512 tokens
- **Batching:** batch size 128
- **Environment:** Google Colab, NVIDIA Tesla T4 GPU · transformers 5.10.2 · torch 2.11.0+cu128

## Data layout
Each source file is scored and saved separately (the dataset is kept as six files, not merged into one master). RoBERTa runs as a validation pass on the same rows already scored by VADER, so both methods' columns sit side by side in each output file.

**Output files:**
`facebook_posts_vader_roberta.csv`, `facebook_comments_vader_roberta.csv`, `reddit_relevant_posts_vader_roberta.csv`, `reddit_relevant_comments_vader_roberta.csv`, `whitehouse_threads_posts_vader_roberta.csv`, `whitehouse_threads_comments_vader_roberta.csv`

**Added columns:** `roberta_neg`, `roberta_neu`, `roberta_pos` (softmax probabilities), `roberta_label` (argmax), `roberta_truncated` (bool).

## Row counts + truncation
| File | Rows | Truncated >512 | % truncated |
|---|---|---|---|
| facebook_posts | 952 | 37 | 3.9% |
| facebook_comments | 59,736 | 7 | 0.01% |
| reddit_relevant_posts | 3,317 | 84 | 2.5% |
| reddit_relevant_comments | 120,512 | 237 | 0.2% |
| whitehouse_threads_posts | 13 | 2 | 15.4% |
| whitehouse_threads_comments | 2,239 | 11 | 0.5% |
| **Total** | **186,769** | **378** | **0.2%** |

Truncation is negligible (0.2% overall) and concentrated in *posts* (longer text) rather than comments, so the 512-token cap has no material effect on results. The White House posts show a high percentage only because the file is tiny (2 of 13).

## RoBERTa label distribution (per file)
| File | neg | neu | pos |
|---|---|---|---|
| facebook_posts | 0.101 | 0.837 | 0.062 |
| facebook_comments | 0.218 | 0.524 | 0.259 |
| reddit_relevant_posts | 0.314 | 0.627 | 0.059 |
| reddit_relevant_comments | 0.403 | 0.478 | 0.119 |
| whitehouse_threads_posts | 0.077 | 0.692 | 0.231 |
| whitehouse_threads_comments | 0.536 | 0.360 | 0.104 |

RoBERTa labels lean more neutral than VADER across every file (most strongly on `facebook_posts`, which are largely factual forecast posts). The VADER-vs-RoBERTa comparison is covered in the separate agreement analysis.

## Quality check
A random sample of 20 rows (text + VADER label + RoBERTa label) was inspected across all six files. No scoring errors observed; the model produces sensible labels. Disagreements between the two methods are systematic and explainable (e.g. VADER assigns polarity to factual/weather-specific text that RoBERTa reads as neutral) — these feed the disagreement analysis, not a defect in this run.

## Runtime
Total wall-clock ≈ 49 minutes on the T4, dominated by `reddit_relevant_comments` (120,512 rows, ~38 minutes). All other files combined ran in under 12 minutes.

## Issues
None. The run completed without errors across all six files.
