"""Our shared VADER scorer, used for every source (Facebook, Reddit, White
House). VADER is built for social-media text and returns neg/neu/pos plus a
compound score from -1 to +1; we call compound >= 0.05 positive, <= -0.05
negative, and anything in between neutral.

Built with help from Claude. See https://github.com/cjhutto/vaderSentiment.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Create the analyzer once (it loads the lexicon into memory).
# Reusing one instance is faster than creating a new one per call.
_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict:
    """Run VADER sentiment analysis on a text string.

    Args:
        text: A text string (ideally cleaned first, but VADER handles raw text too).

    Returns:
        Dictionary with keys: neg, neu, pos, compound.
        - neg/neu/pos: proportions that sum to 1.0
        - compound: normalized score from -1 (most negative) to +1 (most positive)
    """
    if not isinstance(text, str) or not text.strip():
        return {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0}

    return _analyzer.polarity_scores(text)


def label_sentiment(compound: float) -> str:
    """Convert a compound score to a human-readable label.

    Uses standard VADER thresholds from the original paper:
        compound >= 0.05  -> "positive"
        compound <= -0.05 -> "negative"
        otherwise         -> "neutral"

    Args:
        compound: VADER compound score (-1 to +1).

    Returns:
        One of: "positive", "negative", "neutral".
    """
    if compound >= 0.05:
        return "positive"
    elif compound <= -0.05:
        return "negative"
    else:
        return "neutral"
