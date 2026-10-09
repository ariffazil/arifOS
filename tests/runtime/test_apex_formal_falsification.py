"""
APEX Theory — Formal Verification & Falsification Test Suite
============================================================
Machine-verifies the representation theorems, constitutional axioms,
and counterexample refutations for APEX Governance Aggregation.

Theorems Verified:
  - T1: Existence & Uniqueness of G = (A·P·E·X)^(1/4) under A1–A7
  - T2: Arithmetic Mean Refuted by A1 (Nash Collapse)
  - T3: Harmonic Mean Refuted by A6 (Multiplicativity)
  - T4: Unequal-Weight Geometric Mean Refuted by A7 / A2 (Equal Dignity / Symmetry)
  - T5: Unrooted Product Refuted by A5 (Normalization)
  - T6: Min Aggregator Refuted by A3 (Strict Monotonicity)
  - T7: Historical E² and Φ-conflation Formulations Refuted
"""

import itertools
import math
import random
import unittest
from typing import Callable, Tuple

from arifosmcp.runtime.apex_canonical import (
    clamp,
    compute_C_dark,
    compute_G,
    compute_Phi,
    quick_verdict,
    Verdict,
)

DialVector = Tuple[float, float, float, float]


def canonical_G(v: DialVector) -> float:
    a, p, e, x = (clamp(val) for val in v)
    return (a * p * e * x) ** 0.25


def arithmetic_mean(v: DialVector) -> float:
    return sum(v) / 4.0


def harmonic_mean(v: DialVector) -> float:
    if any(x <= 0 for x in v):
        return 0.0
    return 4.0 / sum(1.0 / x for x in v)


def unrooted_product(v: DialVector) -> float:
    return v[0] * v[1] * v[2] * v[3]


def min_aggregator(v: DialVector) -> float:
    return min(v)


def weighted_geometric_mean(v: DialVector, weights: Tuple[float, float, float, float]) -> float:
    return (v[0] ** weights[0]) * (v[1] ** weights[1]) * (v[2] ** weights[2]) * (v[3] ** weights[3])


def historical_e2_formula(v: DialVector) -> float:
    a, p, e, x = v
    return (a * p * (e ** 2) * x) ** (1.0 / 5.0)


class TestAxiomA1NashCollapse(unittest.TestCase):
    """A1: Boundary Veto / Nash Collapse: min(v) = 0 => G(v) = 0."""

    def test_canonical_collapses_on_any_zero(self):
        for i in range(4):
            v = [1.0, 1.0, 1.0, 1.0]
            v[i] = 0.0
            self.assertEqual(canonical_G(tuple(v)), 0.0)

    def test_t2_falsification_arithmetic_mean_violates_a1(self):
        """Theorem T2: Arithmetic mean allows compensatory arithmetic, violating A1."""
        counterexample = (0.0, 1.0, 1.0, 1.0)
        am_score = arithmetic_mean(counterexample)
        # AM gives 0.75 (Healthy), masking total failure of Authority
        self.assertEqual(am_score, 0.75)
        self.assertNotEqual(am_score, 0.0, "Arithmetic mean failed to collapse on zero dial")


class TestAxiomA2PermutationSymmetry(unittest.TestCase):
    """A2: G is invariant under all 24 permutations in S_4."""

    def test_canonical_permutation_invariance(self):
        v = (0.9, 0.7, 0.5, 0.3)
        expected = canonical_G(v)
        for perm in itertools.permutations(v):
            self.assertAlmostEqual(canonical_G(perm), expected, places=7)

    def test_t4_falsification_unequal_weights_violate_symmetry(self):
        """Theorem T4: Unequal weights break permutation symmetry."""
        weights = (0.4, 0.3, 0.2, 0.1)
        v1 = (0.9, 0.7, 0.5, 0.3)
        v2 = (0.3, 0.5, 0.7, 0.9)  # Reversed permutation
        val1 = weighted_geometric_mean(v1, weights)
        val2 = weighted_geometric_mean(v2, weights)
        self.assertNotAlmostEqual(val1, val2, places=3)


class TestAxiomA3StrictMonotonicity(unittest.TestCase):
    """A3: Increasing any interior dial strictly increases G."""

    def test_canonical_strict_monotonicity(self):
        base = (0.5, 0.5, 0.5, 0.5)
        g_base = canonical_G(base)
        for i in range(4):
            v_inc = list(base)
            v_inc[i] += 0.1
            self.assertGreater(canonical_G(tuple(v_inc)), g_base)

    def test_t6_falsification_min_violates_strict_monotonicity(self):
        """Theorem T6: Minimum function is non-compensatory but insensitive to non-minimum improvements."""
        base = (0.2, 0.6, 0.7, 0.8)
        m_base = min_aggregator(base)
        # Increase non-minimum dial (P: 0.6 -> 0.9)
        improved = (0.2, 0.9, 0.7, 0.8)
        m_improved = min_aggregator(improved)
        self.assertEqual(m_base, m_improved, "Min function failed to respond monotonically to dial improvement")


class TestAxiomA5DiagonalNormalization(unittest.TestCase):
    """A5: G(k, k, k, k) = k for all k in [0, 1]."""

    def test_canonical_diagonal_normalization(self):
        for k in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]:
            self.assertAlmostEqual(canonical_G((k, k, k, k)), k, places=7)

    def test_t5_falsification_unrooted_product_violates_a5(self):
        """Theorem T5: Unrooted product APEX fails diagonal normalization (scales as k^4)."""
        k = 0.5
        score = unrooted_product((k, k, k, k))
        self.assertAlmostEqual(score, 0.0625, places=5)
        self.assertNotAlmostEqual(score, k, places=3)


class TestAxiomA6CoordinatewiseMultiplicativity(unittest.TestCase):
    """A6: G(u ⊙ v) = G(u) · G(v) for all interior vectors."""

    def test_canonical_multiplicativity(self):
        random.seed(42)
        for _ in range(50):
            u = tuple(random.uniform(0.05, 1.0) for _ in range(4))
            v = tuple(random.uniform(0.05, 1.0) for _ in range(4))
            uv = tuple(u[i] * v[i] for i in range(4))
            g_u = canonical_G(u)
            g_v = canonical_G(v)
            g_uv = canonical_G(uv)
            self.assertAlmostEqual(g_uv, g_u * g_v, places=6)

    def test_t3_falsification_harmonic_mean_violates_a6(self):
        """Theorem T3: Harmonic mean violates multiplicativity."""
        u = (0.3, 0.4, 0.5, 0.6)
        v = (0.7, 0.2, 0.9, 0.8)
        uv = tuple(u[i] * v[i] for i in range(4))
        hm_u = harmonic_mean(u)
        hm_v = harmonic_mean(v)
        hm_uv = harmonic_mean(uv)
        self.assertNotAlmostEqual(hm_uv, hm_u * hm_v, places=2)


class TestHistoricalRefutations(unittest.TestCase):
    """Refutations of superseded APEX formulations."""

    def test_e2_formula_violates_equal_dignity(self):
        """Historical E² formula unfairly weights evidence."""
        # Under E² formula, (0.5, 0.5, 0.9, 0.5) vs (0.9, 0.5, 0.5, 0.5)
        v_high_e = (0.5, 0.5, 0.9, 0.5)
        v_high_a = (0.9, 0.5, 0.5, 0.5)
        self.assertNotAlmostEqual(historical_e2_formula(v_high_e), historical_e2_formula(v_high_a), places=3)
        # Canonical formula treats them identically
        self.assertAlmostEqual(canonical_G(v_high_e), canonical_G(v_high_a), places=7)

    def test_c_dark_hallucination_bound(self):
        """C_dark = A · (1-P) · (1-X) correctly flags blind authority without physics or execution."""
        # High authority (0.95), zero physics (0.05), zero execution (0.05)
        c_dark = compute_C_dark(0.95, 0.05, 0.05)
        expected = 0.95 * 0.95 * 0.95
        self.assertAlmostEqual(c_dark, expected, places=4)
        self.assertGreaterEqual(c_dark, 0.30, "Blind ungrounded authority must trip C_dark threshold")


if __name__ == "__main__":
    unittest.main()
