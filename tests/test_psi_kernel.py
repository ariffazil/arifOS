"""
Test PsiKernel (Ψ) - APEX Soul

Tests F8 (Genius), F10-F12 (Hypervisor), and final verdict rendering.

Coverage:
- F8 (Genius) evaluation
- Hypervisor integration (F10-F12)
- Verdict hierarchy (SABAR > VOID > HOLD_888 > PARTIAL > SEAL)
- Trinity integration (Δ + Ω + Ψ)
"""

import pytest

from arifos.core.agi.delta_kernel import DeltaKernel, DeltaVerdict
from arifos.core.apex.psi_kernel import PsiKernel, PsiVerdict, Verdict, render_apex_verdict
from arifos.core.asi.omega_kernel import OmegaKernel, OmegaVerdict


class TestF8Genius:
    """Test F8 (Genius) evaluation."""

    def test_f8_passes_with_sufficient_genius(self):
        """F8 should pass when G ≥ 0.80."""
        delta = DeltaVerdict(passed=True, f1_amanah=True, f2_clarity=True)
        omega = OmegaVerdict(
            passed=True, f3_tri_witness=True, f4_peace_squared=True,
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True
        )

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=True,
            hypervisor_failures=[]
        )

        assert verdict.f8_genius is True
        assert "F8 Genius PASS" in verdict.metadata["f8_reason"]

    def test_f8_fails_with_low_genius(self):
        """F8 should fail when G < 0.80."""
        delta = DeltaVerdict(passed=True, f1_amanah=True, f2_clarity=True)
        omega = OmegaVerdict(
            passed=True, f3_tri_witness=True, f4_peace_squared=True,
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True
        )

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.70,
            hypervisor_passed=True,
            hypervisor_failures=[]
        )

        assert verdict.f8_genius is False
        assert verdict.verdict == Verdict.VOID
        assert any("F8 Genius FAIL" in f for f in verdict.failures)


class TestHypervisorIntegration:
    """Test Hypervisor (F10-F12) integration."""

    def test_hypervisor_pass_allows_seal(self):
        """Hypervisor pass should allow SEAL verdict."""
        delta = DeltaVerdict(passed=True, f1_amanah=True, f2_clarity=True)
        omega = OmegaVerdict(
            passed=True, f3_tri_witness=True, f4_peace_squared=True,
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True
        )

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=True,
            hypervisor_failures=[]
        )

        assert verdict.hypervisor_passed is True
        assert verdict.verdict == Verdict.SEAL

    def test_hypervisor_fail_triggers_sabar(self):
        """Hypervisor failure should trigger SABAR verdict (highest priority)."""
        delta = DeltaVerdict(passed=True, f1_amanah=True, f2_clarity=True)
        omega = OmegaVerdict(
            passed=True, f3_tri_witness=True, f4_peace_squared=True,
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True
        )

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=False,
            hypervisor_failures=["F12 Injection Defense FAIL: Injection pattern detected"]
        )

        assert verdict.hypervisor_passed is False
        assert verdict.verdict == Verdict.SABAR
        assert "F12 Injection Defense FAIL" in verdict.failures[0]


class TestVerdictHierarchy:
    """Test verdict hierarchy (SABAR > VOID > HOLD_888 > PARTIAL > SEAL)."""

    def test_seal_verdict_when_all_pass(self):
        """All floors passing should result in SEAL."""
        delta = DeltaVerdict(passed=True, f1_amanah=True, f2_clarity=True)
        omega = OmegaVerdict(
            passed=True, f3_tri_witness=True, f4_peace_squared=True,
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True
        )

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=True,
            hypervisor_failures=[]
        )

        assert verdict.verdict == Verdict.SEAL
        assert verdict.passed is True

    def test_void_verdict_for_hard_floor_failure(self):
        """Hard floor failure should result in VOID."""
        delta = DeltaVerdict(passed=False, f1_amanah=False, f2_clarity=True)
        omega = OmegaVerdict(
            passed=True, f3_tri_witness=True, f4_peace_squared=True,
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True
        )

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=True,
            hypervisor_failures=[]
        )

        assert verdict.verdict == Verdict.VOID
        assert verdict.passed is False

    def test_partial_verdict_for_soft_floor_warning(self):
        """Soft floor warning should result in PARTIAL."""
        delta = DeltaVerdict(passed=True, f1_amanah=True, f2_clarity=True)
        omega = OmegaVerdict(
            passed=False, f3_tri_witness=True, f4_peace_squared=False,  # F4 soft fail
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True
        )

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=True,
            hypervisor_failures=[]
        )

        assert verdict.verdict == Verdict.PARTIAL
        assert verdict.passed is False

    def test_sabar_overrides_void(self):
        """SABAR (hypervisor) should override VOID (hard floor failure)."""
        delta = DeltaVerdict(passed=False, f1_amanah=False, f2_clarity=True)
        omega = OmegaVerdict(
            passed=True, f3_tri_witness=True, f4_peace_squared=True,
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True
        )

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=False,
            hypervisor_failures=["F12 Injection detected"]
        )

        # SABAR (highest) should override VOID
        assert verdict.verdict == Verdict.SABAR


class TestTrinityIntegration:
    """Test Trinity integration (Δ + Ω + Ψ)."""

    def test_aggregates_delta_failures(self):
        """PsiKernel should aggregate failures from DeltaKernel."""
        delta = DeltaVerdict(
            passed=False, f1_amanah=False, f2_clarity=True,
            failures=["F1 Amanah FAIL: Not reversible"]
        )
        omega = OmegaVerdict(
            passed=True, f3_tri_witness=True, f4_peace_squared=True,
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True
        )

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=True,
            hypervisor_failures=[]
        )

        assert "F1 Amanah FAIL" in verdict.failures[0]
        assert verdict.verdict == Verdict.VOID

    def test_aggregates_omega_failures(self):
        """PsiKernel should aggregate failures from OmegaKernel."""
        delta = DeltaVerdict(passed=True, f1_amanah=True, f2_clarity=True)
        omega = OmegaVerdict(
            passed=False, f3_tri_witness=False, f4_peace_squared=True,
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True,
            failures=["F3 Tri-Witness FAIL: 0.85 < 0.95"]
        )

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=True,
            hypervisor_failures=[]
        )

        assert "F3 Tri-Witness FAIL" in verdict.failures[0]
        assert verdict.verdict == Verdict.PARTIAL

    def test_metadata_contains_all_contexts(self):
        """PsiVerdict should contain metadata from all kernels."""
        delta = DeltaVerdict(passed=True, f1_amanah=True, f2_clarity=True)
        omega = OmegaVerdict(
            passed=True, f3_tri_witness=True, f4_peace_squared=True,
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True
        )

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=True,
            hypervisor_failures=[]
        )

        assert "f8_genius" in verdict.metadata
        assert "verdict_reason" in verdict.metadata


class TestConvenienceFunction:
    """Test convenience function."""

    def test_render_apex_verdict(self):
        """render_apex_verdict should work as shortcut."""
        delta = DeltaVerdict(passed=True, f1_amanah=True, f2_clarity=True)
        omega = OmegaVerdict(
            passed=True, f3_tri_witness=True, f4_peace_squared=True,
            f5_kappa_r=True, f6_omega_0=True, f7_rasa=True, f9_c_dark=True
        )

        verdict = render_apex_verdict(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=True
        )

        assert isinstance(verdict, PsiVerdict)
        assert verdict.verdict == Verdict.SEAL


class TestRealWorldScenario:
    """Test real-world end-to-end scenario."""

    def test_complete_trinity_evaluation(self):
        """Test complete evaluation through all three kernels."""
        # Step 1: Evaluate AGI (Delta)
        delta_kernel = DeltaKernel()
        delta = delta_kernel.evaluate(
            query="What is arifOS?",
            response="arifOS is a constitutional AI governance framework.",
            reversible=True,
            within_mandate=True,
            skip_clarity=True  # Skip for simplicity
        )

        # Step 2: Evaluate ASI (Omega)
        omega_kernel = OmegaKernel()
        omega = omega_kernel.evaluate(
            tri_witness=0.98,
            peace_squared=1.0,
            kappa_r=0.96,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )

        # Step 3: Evaluate APEX (Psi)
        psi_kernel = PsiKernel()
        psi = psi_kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=True,
            hypervisor_failures=[]
        )

        # Final verdict should be SEAL
        assert psi.verdict == Verdict.SEAL
        assert psi.passed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
