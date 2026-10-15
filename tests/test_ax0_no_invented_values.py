"""AX-0: no APEX path invents values from missing data.

Feed zero/missing inputs to every compute_* and compute_apex →
zero numeric outputs, zero SEAL/SABAR from missing data.

Falsifier: any numeric output from zero inputs → lane fails.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo-local import wins

from arifosmcp.runtime.apex_canonical import (
    compute_A,
    compute_P,
    compute_X,
    compute_G,
    compute_C_dark,
    _determine_verdict,
    Verdict,
)


class TestComputeA:
    """compute_A: no leases → None (UNMEASURED), not 1.0."""

    def test_zero_leases_returns_none(self):
        result = compute_A(valid_leases=0, total_leases=0, floor_compliance=13)
        assert result is None, f"expected None from zero leases, got {result}"

    def test_zero_leases_low_compliance_returns_none(self):
        result = compute_A(valid_leases=0, total_leases=0, floor_compliance=5)
        assert result is None, f"expected None from zero leases, got {result}"

    def test_sovereign_override_returns_one(self):
        result = compute_A(sovereign_override=True)
        assert result == 1.0

    def test_floor_violation_returns_zero(self):
        result = compute_A(valid_leases=1, total_leases=1, floor_compliance=5)
        assert result == 0.0

    def test_normal_computation(self):
        result = compute_A(valid_leases=2, total_leases=4, floor_compliance=13)
        assert result == 0.5


class TestComputeP:
    """compute_P: all-zero inputs → None. No 0.99/0.50/0.70 defaults."""

    def test_all_zero_inputs_returns_none(self):
        result = compute_P(p_well=0, p_seis=0, p_geo=0)
        assert result is None, f"expected None from all-zero inputs, got {result}"

    def test_well_contradicts_seis_with_zero_well_returns_none(self):
        result = compute_P(p_well=0, well_contradicts_seis=True)
        assert result is None

    def test_seis_contradicts_geo_with_zero_seis_returns_none(self):
        result = compute_P(p_seis=0, seis_contradicts_geo=True)
        assert result is None

    def test_normal_computation(self):
        result = compute_P(p_well=0.8, p_seis=0.6, p_geo=0.7)
        assert result is not None
        assert 0.6 <= result <= 0.8


class TestComputeX:
    """compute_X: total_steps == 0 → None, not 0.5."""

    def test_zero_steps_returns_none(self):
        result = compute_X(successful_steps=0, total_steps=0)
        assert result is None, f"expected None from zero steps, got {result}"

    def test_forge_fail_returns_zero(self):
        result = compute_X(successful_steps=5, total_steps=10, forge_evaluate_passed=False)
        assert result == 0.0

    def test_normal_computation(self):
        result = compute_X(successful_steps=8, total_steps=10)
        assert result is not None
        assert 0.7 <= result <= 0.9


class TestComputeG:
    """compute_G: None propagates — nil times anything is nil."""

    def test_none_input_returns_none(self):
        result = compute_G(None, 0.5, 0.5, 0.5, 0.5)
        assert result is None

    def test_all_none_returns_none(self):
        result = compute_G(None, None, None, None, 0.5)
        assert result is None

    def test_normal_computation(self):
        result = compute_G(0.8, 0.8, 0.8, 0.8, 0.5)
        assert result is not None
        assert 0.7 <= result <= 0.9


class TestComputeCDark:
    """compute_C_dark: None propagates."""

    def test_none_input_returns_none(self):
        result = compute_C_dark(None, 0.5, 0.5)
        assert result is None

    def test_normal_computation(self):
        result = compute_C_dark(0.8, 0.2, 0.9)
        assert result is not None


class TestDetermineVerdict:
    """_determine_verdict: None G or C_dark → INCONCLUSIVE (HOLD), never SEAL."""

    def test_none_g_returns_inconclusive(self):
        verdict, reason = _determine_verdict(None, 0.1, 0.0, 0.5, 0.5, 0.5, 0.5, 0.5)
        assert verdict == Verdict.HOLD
        assert "INCONCLUSIVE" in reason

    def test_none_c_dark_returns_inconclusive(self):
        verdict, reason = _determine_verdict(0.9, None, 0.0, 0.5, 0.5, 0.5, 0.5, 0.5)
        assert verdict == Verdict.HOLD
        assert "INCONCLUSIVE" in reason

    def test_zero_g_returns_void(self):
        verdict, reason = _determine_verdict(0.0, 0.1, 0.0, 0.5, 0.5, 0.5, 0.5, 0.5)
        assert verdict == Verdict.VOID

    def test_normal_seal(self):
        verdict, reason = _determine_verdict(0.85, 0.1, -0.1, 0.9, 0.9, 0.9, 0.9, 0.5)
        assert verdict == Verdict.SEAL


class TestAxiomCheck:
    """AX-0, D5: axioms count only when condition is evaluated true."""

    def test_axioms_not_vacuous_with_none_inputs(self):
        """When G is None, axioms 1/3 must not count (multiplicativity, Nash)."""
        from arifosmcp.runtime.apex_canonical import (
            PrimitiveInputs,
            compute_apex,
            FalsifiablePrediction,
        )

        inputs = PrimitiveInputs(
            valid_leases=0,
            total_leases=0,
            p_well=0,
            p_seis=0,
            p_geo=0,
            successful_steps=0,
            total_steps=0,
            entropy_rate=0.0,
        )
        prediction = FalsifiablePrediction(
            claim="AX-0 test: zero inputs must yield UNMEASURED",
            falsifier="any numeric output from zero inputs",
            deadline="2026-10-14",
        )
        result = compute_apex(inputs, prediction=prediction)
        # With all-zero inputs, G is None → axioms 1, 2, 3, 4 must not count
        # Only axioms 5 (dS<=0), 6 (witness), 7 (F13) can count
        assert result.axioms_satisfied <= 4, (
            f"axioms={result.axioms_satisfied}, expected ≤4 with None G"
        )
