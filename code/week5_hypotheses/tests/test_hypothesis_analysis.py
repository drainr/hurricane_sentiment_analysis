"""
Unit tests for the pure helper functions in hypothesis_tests.py.

Covers the two helpers with fixed, hand-checkable expected values: the RoBERTa
label encoding and the rank-biserial effect size. Run with:

    python3 -m pytest code/week5_hypotheses/tests/
"""
import sys
from pathlib import Path
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from hypothesis_tests import encode_roberta_labels, rank_biserial_effect_size


class HypothesisTestsHelpersTest(unittest.TestCase):
    """Unit tests for the pure helper functions in hypothesis_tests.py."""
    def test_encode_roberta_labels_maps_known_values(self):
        """Both label casings map onto the same {-1, 0, +1} encoding."""
        self.assertEqual(encode_roberta_labels(["POS", "NEG", "NEUTRAL", "positive", "negative"]), [1, -1, 0, 1, -1])

    def test_rank_biserial_effect_size_matches_expected(self):
        """Rank-biserial spans -1 to +1 at the extremes of U and is 0 at the midpoint."""
        self.assertAlmostEqual(rank_biserial_effect_size(0, 3, 3), -1.0)
        self.assertAlmostEqual(rank_biserial_effect_size(9, 3, 3), 1.0)


if __name__ == "__main__":
    unittest.main()
