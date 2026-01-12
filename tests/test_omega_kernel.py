"""
Test OmegaKernel (Ω) - ASI Heart

Tests F3-F7 and F9 evaluation (ASI floors).

Coverage:
- F3 (Tri-Witness) - Consensus check
- F4 (Peace²) - Stability check
- F5 (κᵣ) - Empathy check
- F6 (Ω₀) - Humility check
- F7 (RASA) - Felt care check
- F9 (C_dark) - Anti-hantu check
- Integration and edge cases
"""

import pytest

from arifos_core.asi.omega_kernel import OmegaKernel, OmegaVerdict, evaluate_asi_floors


class TestF3TriWitness:
    """Test F3 (Tri-Witness Consensus)."""

    def test_f3_passes_with_sufficient_consensus(self):
        """F3 should pass when tri-witness ≥ 0.95."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.98,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f3_tri_witness is True
        assert "F3 Tri-Witness PASS" in verdict.metadata["f3_reason"]

    def test_f3_fails_with_insufficient_consensus(self):
        """F3 should fail when tri-witness < 0.95."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.85,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f3_tri_witness is False
        assert verdict.passed is False
        assert any("F3 Tri-Witness FAIL" in f for f in verdict.failures)


class TestF4PeaceSquared:
    """Test F4 (Peace² Stability)."""

    def test_f4_passes_with_non_destructive_action(self):
        """F4 should pass when peace² ≥ 1.0."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=1.5,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f4_peace_squared is True
        assert "F4 Peace² PASS" in verdict.metadata["f4_reason"]

    def test_f4_fails_with_destructive_action(self):
        """F4 should fail when peace² < 1.0."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=0.5,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f4_peace_squared is False
        assert verdict.passed is False
        assert any("F4 Peace² FAIL" in f for f in verdict.failures)


class TestF5KappaR:
    """Test F5 (κᵣ Empathy)."""

    def test_f5_passes_with_sufficient_empathy(self):
        """F5 should pass when κᵣ ≥ 0.95."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=1.0,
            kappa_r=0.98,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f5_kappa_r is True
        assert "F5 κᵣ PASS" in verdict.metadata["f5_reason"]

    def test_f5_fails_with_insufficient_empathy(self):
        """F5 should fail when κᵣ < 0.95."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=1.0,
            kappa_r=0.85,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f5_kappa_r is False
        assert verdict.passed is False
        assert any("F5 κᵣ" in f and "FAIL" in f for f in verdict.failures)


class TestF6Omega0:
    """Test F6 (Ω₀ Humility)."""

    def test_f6_passes_with_proper_humility(self):
        """F6 should pass when Ω₀ in [0.03, 0.05]."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f6_omega_0 is True
        assert "F6 Ω₀ PASS" in verdict.metadata["f6_reason"]

    def test_f6_fails_when_too_confident(self):
        """F6 should fail when Ω₀ < 0.03 (overconfident)."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.01,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f6_omega_0 is False
        assert verdict.passed is False
        assert any("F6 Ω₀" in f and "FAIL" in f for f in verdict.failures)

    def test_f6_fails_when_too_uncertain(self):
        """F6 should fail when Ω₀ > 0.05 (too uncertain)."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.10,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f6_omega_0 is False
        assert verdict.passed is False


class TestF7RASA:
    """Test F7 (RASA Felt Care)."""

    def test_f7_passes_with_felt_care(self):
        """F7 should pass when RASA = True."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f7_rasa is True
        assert "F7 RASA PASS" in verdict.metadata["f7_reason"]

    def test_f7_fails_without_felt_care(self):
        """F7 should fail when RASA = False."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=False,
            c_dark=0.15
        )

        assert verdict.f7_rasa is False
        assert verdict.passed is False
        assert any("F7 RASA FAIL" in f for f in verdict.failures)


class TestF9CDark:
    """Test F9 (C_dark Anti-Hantu)."""

    def test_f9_passes_with_low_dark_cleverness(self):
        """F9 should pass when C_dark < 0.30."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f9_c_dark is True
        assert "F9 C_dark PASS" in verdict.metadata["f9_reason"]

    def test_f9_fails_with_high_dark_cleverness(self):
        """F9 should fail when C_dark ≥ 0.30."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            c_dark=0.50
        )

        assert verdict.f9_c_dark is False
        assert verdict.passed is False
        assert any("F9 C_dark" in f and "FAIL" in f for f in verdict.failures)


class TestOmegaKernelIntegration:
    """Test OmegaKernel integration (all ASI floors)."""

    def test_all_floors_pass(self):
        """All ASI floors passing should result in overall pass."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.98,
            peace_squared=1.0,
            kappa_r=0.96,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f3_tri_witness is True
        assert verdict.f4_peace_squared is True
        assert verdict.f5_kappa_r is True
        assert verdict.f6_omega_0 is True
        assert verdict.f7_rasa is True
        assert verdict.f9_c_dark is True
        assert verdict.passed is True
        assert len(verdict.failures) == 0

    def test_single_floor_failure_blocks_overall(self):
        """Single floor failure should block overall verdict."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.80,  # F3 fails
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert verdict.f3_tri_witness is False
        assert verdict.passed is False

    def test_metadata_populated(self):
        """Verdict should contain rich metadata for all floors."""
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.95,
            peace_squared=1.0,
            kappa_r=0.95,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert "f3_tri_witness" in verdict.metadata
        assert "f4_peace_squared" in verdict.metadata
        assert "f5_kappa_r" in verdict.metadata
        assert "f6_omega_0" in verdict.metadata
        assert "f7_rasa" in verdict.metadata
        assert "f9_c_dark" in verdict.metadata


class TestConvenienceFunction:
    """Test convenience function."""

    def test_evaluate_asi_floors(self):
        """evaluate_asi_floors should work as shortcut."""
        verdict = evaluate_asi_floors(
            tri_witness=0.98,
            peace_squared=1.0,
            kappa_r=0.96,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        assert isinstance(verdict, OmegaVerdict)
        assert verdict.passed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
