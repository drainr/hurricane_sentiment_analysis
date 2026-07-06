import sys
from pathlib import Path
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from hypothesis_tests import encode_roberta_labels, rank_biserial_effect_size


class HypothesisTestsHelpersTest(unittest.TestCase):
    def test_encode_roberta_labels_maps_known_values(self):
        self.assertEqual(encode_roberta_labels(["POS", "NEG", "NEUTRAL", "positive", "negative"]), [1, -1, 0, 1, -1])

    def test_rank_biserial_effect_size_matches_expected(self):
        self.assertAlmostEqual(rank_biserial_effect_size(0, 3, 3), -1.0)
        self.assertAlmostEqual(rank_biserial_effect_size(9, 3, 3), 1.0)


if __name__ == "__main__":
    unittest.main()
