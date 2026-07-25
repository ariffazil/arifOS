"""
Tests for APEX Verification Pipeline — Canonical Runtime

Verifies:
  - Each primitive measurement law
  - G = A · P · E · X · Φ computation
  - C_dark = A · (1-P) · (1-X) shadow term
  - Verdict matrix (SEAL/SABAR/HOLD/VOID)
  - Axiom enforcement
  - Edge cases (zero-collapse, boundary values)
"""

import math
import unittest

from arifosmcp.runtime.apex_canonical import (
    APEXResult,
    PrimitiveInputs,
    Verdict,
    compute_A,
    compute_C_dark,
    compute_E,
    compute_G,
    compute_P,
    compute_Phi,
    compute_X,
    compute_apex,
    quick_verdict,
)


class TestArifThinkModeApex(unittest.TestCase):
    """G-fold lives only in arif_think(mode='apex') + apex_canonical helpers."""

    def test_mode_apex_derives_g_not_stored_primitive(self):
        from arifosmcp.tools.reason import arif_think

        out = arif_think(
            mode="apex",
            query="entropy map probe",
            context={
                "apex_inputs": {
                    "valid_leases": 1,
                    "total_leases": 1,
                    "floor_compliance": 13,
                    "p_well": 0.9,
                    "p_seis": 0.8,
                    "p_geo": 0.7,
                    "clarity": 0.9,
                    "uncertainty": 0.05,
                    "successful_steps": 3,
                    "total_steps": 3,
                    "h_witness": 0.8,
                    "ai_witness": 0.85,
                    "ext_witness": 0.75,
                    "entropy_rate": -0.01,
                }
            },
        )
        data = out.model_dump() if hasattr(out, "model_dump") else dict(out)
        apex = data.get("apex_scalars") or (data.get("result") or {}).get("apex_scalars")
        self.assertIsNotNone(apex)
        self.assertTrue(apex.get("derived") is True)
        self.assertEqual(apex.get("source"), "arif_think.mode=apex")
        self.assertEqual(apex.get("canonical_module"), "arifosmcp.runtime.apex_canonical")
        self.assertIsInstance(apex.get("G"), (int, float))
        self.assertGreaterEqual(apex["G"], 0.0)
        self.assertLessEqual(apex["G"], 1.0)

    def test_scalar_collector_rejects_confidence_as_g(self):
        from arifosmcp.core.scalar_collector import ScalarCollector, UNMEASURED_SOURCE

        # Confidence alone must NOT invent G
        sc = ScalarCollector(evidence={"confidence": 0.95, "reasoning_confidence": 0.88})
        g = sc.collect_G()
        self.assertEqual(g.source, UNMEASURED_SOURCE)
        self.assertIsNone(g.value)

        # apex_scalars from arif_think mode=apex is accepted
        sc2 = ScalarCollector(
            evidence={
                "apex_scalars": {
                    "G": 0.42,
                    "derived": True,
                    "source": "arif_think.mode=apex",
                }
            }
        )
        g2 = sc2.collect_G()
        self.assertTrue(g2.is_measured)
        self.assertAlmostEqual(g2.value, 0.42)
        self.assertEqual(g2.source, "arif_think.mode=apex")


class TestComputeA(unittest.TestCase):
    """Test A — Authority measurement law."""

    def test_full_authority(self):
        """All leases valid, all floors satisfied."""
        self.assertEqual(compute_A(valid_leases=5, total_leases=5, floor_compliance=13), 1.0)

    def test_partial_leases(self):
        """Some leases valid."""
        self.assertAlmostEqual(compute_A(valid_leases=3, total_leases=5, floor_compliance=13), 0.6)

    def test_floor_violation(self):
        """Any floor violated → A = 0."""
        self.assertEqual(compute_A(valid_leases=5, total_leases=5, floor_compliance=12), 0.0)

    def test_sovereign_override(self):
        """F13 sovereign override → A = 1."""
        self.assertEqual(
            compute_A(valid_leases=0, total_leases=0, floor_compliance=0, sovereign_override=True),
            1.0,
        )

    def test_no_leases_observational(self):
        """No leases = pure read authority."""
        result = compute_A(valid_leases=0, total_leases=0, floor_compliance=13)
        self.assertAlmostEqual(result, 1.0)


class TestComputeP(unittest.TestCase):
    """Test P — Physics measurement law."""

    def test_well_only(self):
        """Well evidence provided, seis/geo get defaults."""
        result = compute_P(p_well=0.99, p_seis=0.0, p_geo=0.0)
        # p_seis=0 → default 0.50, p_geo=0 → default 0.70
        expected = 0.4 * 0.99 + 0.3 * 0.50 + 0.3 * 0.70
        self.assertAlmostEqual(result, expected, places=2)

    def test_weighted_average(self):
        """Weighted average of all three."""
        result = compute_P(p_well=0.99, p_seis=0.50, p_geo=0.70)
        expected = 0.4 * 0.99 + 0.3 * 0.50 + 0.3 * 0.70
        self.assertAlmostEqual(result, expected, places=2)

    def test_well_contradicts_seis(self):
        """Well contradicts seismic → P = P_well."""
        result = compute_P(p_well=0.95, p_seis=0.50, well_contradicts_seis=True)
        self.assertAlmostEqual(result, 0.95)

    def test_seis_contradicts_geo(self):
        """Seismic contradicts model → P = P_seis."""
        result = compute_P(p_seis=0.60, seis_contradicts_geo=True)
        self.assertAlmostEqual(result, 0.60)


class TestComputeE(unittest.TestCase):
    """Test E — Evidence measurement law."""

    def test_high_clarity(self):
        """High clarity, low uncertainty."""
        result = compute_E(clarity=0.95, uncertainty=0.05)
        self.assertAlmostEqual(result, 0.95 / 1.05, places=2)

    def test_merkle_break(self):
        """Merkle chain broken → E = 0."""
        self.assertEqual(compute_E(clarity=0.95, merkle_chain_intact=False), 0.0)

    def test_humility_floor(self):
        """Uncertainty below 0.03 → clamped to 0.03."""
        result = compute_E(clarity=0.90, uncertainty=0.001)
        self.assertAlmostEqual(result, 0.90 / 1.03, places=2)

    def test_zero_clarity(self):
        """Zero clarity → E = 0."""
        self.assertEqual(compute_E(clarity=0.0), 0.0)


class TestComputeX(unittest.TestCase):
    """Test X — Execution measurement law."""

    def test_perfect_execution(self):
        """All steps successful, no entropy increase."""
        result = compute_X(successful_steps=10, total_steps=10, delta_s_t=0.0)
        self.assertAlmostEqual(result, 1.0, places=2)

    def test_partial_execution(self):
        """8/10 steps successful."""
        result = compute_X(successful_steps=8, total_steps=10, delta_s_t=0.0)
        self.assertAlmostEqual(result, 0.8, places=2)

    def test_forge_evaluate_fails(self):
        """forge_evaluate fails → X = 0."""
        self.assertEqual(
            compute_X(successful_steps=10, total_steps=10, forge_evaluate_passed=False),
            0.0,
        )

    def test_high_entropy(self):
        """High entropy increase → consequence stability drops."""
        result = compute_X(successful_steps=10, total_steps=10, delta_s_t=5.0)
        expected = 1.0 * math.exp(-5.0)
        self.assertAlmostEqual(result, expected, places=4)

    def test_no_steps_observational(self):
        """No execution = default 0.5."""
        self.assertEqual(compute_X(successful_steps=0, total_steps=0), 0.5)


class TestComputePhi(unittest.TestCase):
    """Test Φ — Witness measurement law."""

    def test_full_witness(self):
        """All three witnesses present."""
        result = compute_Phi(h_witness=0.9, ai_witness=0.8, ext_witness=0.7)
        expected = (0.9 * 0.8 * 0.7) ** (1 / 3)
        self.assertAlmostEqual(result, expected, places=4)

    def test_zero_witness_collapses(self):
        """Any witness = 0 → Φ = 0."""
        self.assertEqual(compute_Phi(h_witness=0.0, ai_witness=0.8, ext_witness=0.7), 0.0)
        self.assertEqual(compute_Phi(h_witness=0.9, ai_witness=0.0, ext_witness=0.7), 0.0)
        self.assertEqual(compute_Phi(h_witness=0.9, ai_witness=0.8, ext_witness=0.0), 0.0)

    def test_nash_bargaining(self):
        """Cubic root of product = Nash bargaining."""
        result = compute_Phi(h_witness=1.0, ai_witness=1.0, ext_witness=1.0)
        self.assertAlmostEqual(result, 1.0)


class TestCanonicalFormula(unittest.TestCase):
    """Test G = A · P · E · X · Φ and C_dark."""

    def test_perfect_intelligence(self):
        """All primitives = 1.0 → G = 1.0, C_dark = 0.0."""
        self.assertAlmostEqual(compute_G(1.0, 1.0, 1.0, 1.0, 1.0), 1.0)
        self.assertAlmostEqual(compute_C_dark(1.0, 1.0, 1.0), 0.0)

    def test_zero_collapse(self):
        """Any primitive = 0 → G = 0."""
        self.assertEqual(compute_G(0.0, 1.0, 1.0, 1.0, 1.0), 0.0)
        self.assertEqual(compute_G(1.0, 0.0, 1.0, 1.0, 1.0), 0.0)
        self.assertEqual(compute_G(1.0, 1.0, 0.0, 1.0, 1.0), 0.0)
        self.assertEqual(compute_G(1.0, 1.0, 1.0, 0.0, 1.0), 0.0)
        self.assertEqual(compute_G(1.0, 1.0, 1.0, 1.0, 0.0), 0.0)

    def test_multiplicative(self):
        """G is multiplicative, not additive."""
        a, p, e, x, phi = 0.8, 0.9, 0.7, 0.6, 0.85
        expected = a * p * e * x * phi
        self.assertAlmostEqual(compute_G(a, p, e, x, phi), expected)

    def test_shadow_term(self):
        """C_dark = A · (1-P) · (1-X)."""
        a, p, x = 0.9, 0.8, 0.7
        expected = 0.9 * 0.2 * 0.3
        self.assertAlmostEqual(compute_C_dark(a, p, x), expected)

    def test_shadow_zero_when_perfect(self):
        """C_dark = 0 when P = 1 (perfect perception)."""
        self.assertAlmostEqual(compute_C_dark(0.9, 1.0, 0.5), 0.0)


class TestVerdictMatrix(unittest.TestCase):
    """Test verdict determination."""

    def test_seal(self):
        """G ≥ 0.80, C_dark < 0.30, dS ≤ 0 → SEAL."""
        verdict, _ = quick_verdict(1.0, 1.0, 1.0, 1.0, 1.0)
        self.assertEqual(verdict, Verdict.SEAL)

    def test_void_zero_primitive(self):
        """Any primitive = 0 → VOID."""
        verdict, _ = quick_verdict(0.0, 1.0, 1.0, 1.0, 1.0)
        self.assertEqual(verdict, Verdict.VOID)

    def test_hold_high_c_dark(self):
        """C_dark ≥ 0.30 → HOLD."""
        # A=0.9, P=0.3, X=0.3 → C_dark = 0.9 * 0.7 * 0.7 = 0.441
        verdict, _ = quick_verdict(0.9, 0.3, 0.9, 0.3, 0.9)
        self.assertEqual(verdict, Verdict.HOLD)

    def test_sabar_partial(self):
        """G ≥ 0.50 but < 0.80 → SABAR."""
        # Need G between 0.50 and 0.80 with C_dark < 0.30
        verdict, _ = quick_verdict(0.9, 0.9, 0.9, 0.9, 0.9)
        G = 0.9 ** 5
        if G >= 0.80:
            self.assertEqual(verdict, Verdict.SEAL)
        else:
            self.assertEqual(verdict, Verdict.SABAR)


class TestFullPipeline(unittest.TestCase):
    """Test compute_apex with PrimitiveInputs."""

    def test_perfect_inputs(self):
        """Perfect inputs → SEAL with G ≥ 0.80."""
        inputs = PrimitiveInputs(
            valid_leases=5,
            total_leases=5,
            floor_compliance=13,
            p_well=0.99,
            p_seis=0.99,
            p_geo=0.99,
            clarity=0.95,
            uncertainty=0.05,
            merkle_chain_intact=True,
            successful_steps=10,
            total_steps=10,
            delta_s_t=0.0,
            forge_evaluate_passed=True,
            h_witness=0.9,
            ai_witness=0.9,
            ext_witness=0.9,
            entropy_rate=-0.01,
        )
        result = compute_apex(inputs)
        self.assertEqual(result.verdict, Verdict.SEAL)
        self.assertGreater(result.G, 0.80)
        self.assertLess(result.C_dark, 0.30)

    def test_zero_witness_void(self):
        """Zero human witness → VOID."""
        inputs = PrimitiveInputs(
            valid_leases=5,
            total_leases=5,
            floor_compliance=13,
            p_well=0.99,
            clarity=0.95,
            h_witness=0.0,  # zero human witness
            ai_witness=0.9,
            ext_witness=0.9,
        )
        result = compute_apex(inputs)
        self.assertEqual(result.verdict, Verdict.VOID)

    def test_floor_violation_void(self):
        """Floor violation → A = 0 → VOID."""
        inputs = PrimitiveInputs(
            floor_compliance=12,  # one floor violated
            p_well=0.99,
            h_witness=0.9,
            ai_witness=0.9,
            ext_witness=0.9,
        )
        result = compute_apex(inputs)
        self.assertEqual(result.verdict, Verdict.VOID)

    def test_sovereign_override(self):
        """Sovereign override → A = 1.0."""
        inputs = PrimitiveInputs(
            sovereign_override=True,
            floor_compliance=0,
            p_well=0.99,
            clarity=0.95,
            successful_steps=10,
            total_steps=10,
            h_witness=0.9,
            ai_witness=0.9,
            ext_witness=0.9,
        )
        result = compute_apex(inputs)
        self.assertEqual(result.A, 1.0)

    def test_json_output(self):
        """Result serializes to JSON."""
        inputs = PrimitiveInputs(
            p_well=0.99,
            h_witness=0.8,
            ai_witness=0.8,
            ext_witness=0.8,
        )
        result = compute_apex(inputs)
        json_str = result.to_json()
        self.assertIn("G", json_str)
        self.assertIn("C_dark", json_str)
        self.assertIn("verdict", json_str)


if __name__ == "__main__":
    unittest.main()
