"""
Tests for codebase.agi.precision — v53 Kalman-style precision weighting.

Validates:
- PrecisionEstimate dataclass constraints
- Source/temporal/semantic variance estimation
- Kalman-gain belief updates
- Convenience functions (estimate_precision, update_belief_with_precision)

DITEMPA BUKAN DIBERI
"""

import unittest
import math
from datetime import datetime, timedelta, timezone

from codebase.agi.precision import (
    PrecisionEstimate,
    PrecisionWeighter,
    estimate_precision,
    update_belief_with_precision,
    cosine_similarity,
)


class TestPrecisionEstimate(unittest.TestCase):
    """F7 Humility: precision values never collapse to zero."""

    def test_clamp_minimum(self):
        pe = PrecisionEstimate(pi_likelihood=0.0, pi_prior=0.0, kalman_gain=0.5)
        self.assertGreaterEqual(pe.pi_likelihood, 0.01)
        self.assertGreaterEqual(pe.pi_prior, 0.01)

    def test_normal_values_unchanged(self):
        pe = PrecisionEstimate(pi_likelihood=2.0, pi_prior=1.0, kalman_gain=0.67)
        self.assertAlmostEqual(pe.pi_likelihood, 2.0)
        self.assertAlmostEqual(pe.pi_prior, 1.0)


class TestPrecisionWeighter(unittest.TestCase):
    """Core precision engine tests."""

    def setUp(self):
        self.pw = PrecisionWeighter()

    # -- Source variance --
    def test_source_variance_no_sources(self):
        var = self.pw.estimate_source_variance([])
        self.assertEqual(var, 1.0)  # max uncertainty

    def test_source_variance_single(self):
        var = self.pw.estimate_source_variance(["wiki"])
        # unique/total = 1/1 = 1.0 → 1.0*0.5 + 0.1 = 0.6
        self.assertAlmostEqual(var, 0.6)

    def test_source_variance_duplicates_reduce(self):
        var_dup = self.pw.estimate_source_variance(["wiki", "wiki", "wiki"])
        var_uniq = self.pw.estimate_source_variance(["wiki", "arxiv", "gov"])
        # Duplicates → fewer unique → lower agreement ratio → lower variance
        self.assertLess(var_dup, var_uniq)

    # -- Temporal variance --
    def test_temporal_variance_insufficient(self):
        var = self.pw.estimate_temporal_variance([])
        self.assertEqual(var, 0.3)

    def test_temporal_variance_recent_consistent(self):
        now = datetime.now(timezone.utc)
        ts = [now - timedelta(seconds=i) for i in range(5)]
        var = self.pw.estimate_temporal_variance(ts)
        # Very recent, low scatter → low variance
        self.assertLess(var, 0.5)

    # -- Semantic variance --
    def test_semantic_variance_identical(self):
        vec = [1.0, 0.0, 0.0]
        var = self.pw.estimate_semantic_variance([vec, vec, vec])
        # Identical vectors → cosine=1.0 → variance=0.0
        self.assertAlmostEqual(var, 0.0)

    def test_semantic_variance_orthogonal(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        var = self.pw.estimate_semantic_variance([a, b])
        # Orthogonal → cosine=0.0 → variance=1.0
        self.assertAlmostEqual(var, 1.0)

    # -- Full precision estimation --
    def test_estimate_precision_returns_valid(self):
        now = datetime.now(timezone.utc)
        pe = self.pw.estimate_precision(
            sources=["wiki", "wiki"],
            timestamps=[now, now - timedelta(seconds=10)],
        )
        self.assertIsInstance(pe, PrecisionEstimate)
        self.assertGreater(pe.pi_likelihood, 0)
        self.assertGreater(pe.kalman_gain, 0)
        self.assertLessEqual(pe.kalman_gain, 1.0)

    # -- Belief update --
    def test_update_belief_strong_evidence(self):
        pe = PrecisionEstimate(pi_likelihood=10.0, pi_prior=1.0, kalman_gain=10.0 / 11.0)
        new = self.pw.update_belief(0.5, 0.9, pe)
        # High K → pulls strongly toward evidence
        self.assertGreater(new, 0.8)
        self.assertLessEqual(new, 1.0)

    def test_update_belief_weak_evidence(self):
        pe = PrecisionEstimate(pi_likelihood=0.1, pi_prior=10.0, kalman_gain=0.1 / 10.1)
        new = self.pw.update_belief(0.5, 0.9, pe)
        # Low K → barely moves
        self.assertLess(new, 0.55)

    def test_update_belief_clamps(self):
        pe = PrecisionEstimate(pi_likelihood=100.0, pi_prior=0.01, kalman_gain=0.9999)
        new = self.pw.update_belief(0.9, 1.5, pe)  # evidence > 1.0
        self.assertLessEqual(new, 1.0)


class TestConvenienceFunctions(unittest.TestCase):
    """Module-level convenience wrappers."""

    def test_estimate_precision_module(self):
        now = datetime.now(timezone.utc)
        pe = estimate_precision(
            sources=["a"], timestamps=[now, now - timedelta(seconds=1)]
        )
        self.assertIsInstance(pe, PrecisionEstimate)

    def test_update_belief_with_precision_module(self):
        pe = PrecisionEstimate(pi_likelihood=5.0, pi_prior=1.0, kalman_gain=5.0 / 6.0)
        val = update_belief_with_precision(0.4, 0.8, pe)
        self.assertGreater(val, 0.6)
        self.assertLessEqual(val, 1.0)


class TestCosineSimilarity(unittest.TestCase):
    """Vector similarity used by semantic variance."""

    def test_identical(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [1, 0]), 1.0)

    def test_orthogonal(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)

    def test_opposite(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [-1, 0]), -1.0)

    def test_empty(self):
        self.assertEqual(cosine_similarity([], []), 0.0)

    def test_mismatched_length(self):
        self.assertEqual(cosine_similarity([1, 0], [1, 0, 0]), 0.0)


if __name__ == "__main__":
    unittest.main()
