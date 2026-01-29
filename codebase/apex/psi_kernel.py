"""
arifos.core/apex/psi_kernel.py

PsiKernel (Ψ) - APEX Soul

Purpose:
    The third kernel in the Trinity. Evaluates F8 (Genius) and F10-F12 (Hypervisor).
    Renders final verdict (SEAL, VOID, PARTIAL, SABAR, HOLD_888).
    Pure function class - no side effects, fully testable.

Floors:
    - F8 (Genius): Governed intelligence G ≥ 0.80
    - F10 (Ontology): Symbolic mode enforcement (via Hypervisor)
    - F11 (Command Auth): Nonce verification (via Hypervisor)
    - F12 (Injection Defense): Input sanitization (via Hypervisor)

Verdict Hierarchy:
    SABAR > VOID > HOLD_888 > PARTIAL > SEAL

Authority:
    - 000_THEORY/canon/888_compass/ (APEX canon)
    - AAA_MCP/v46/000_foundation/constitutional_floors.json
    - arifos.core/system/hypervisor.py (F10-F12)

Design:
    Input: DeltaVerdict, OmegaVerdict, Genius score, Hypervisor result
    Output: PsiVerdict with final APEX judgment

    Pure function - deterministic, no I/O.

DITEMPA BUKAN DIBERI - Forged v53.0-HARDENED
"""


from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Verdict(str, Enum):
    """Final verdict types (hierarchy: SABAR > VOID > HOLD_888 > PARTIAL > SEAL)."""
    SABAR = "SABAR"          # Hypervisor block (F10-F12 failure)
    VOID = "VOID"            # Hard floor failure (F1-F2, F6)
    HOLD_888 = "HOLD_888"    # Soft floor failure or high-stakes escalation
    PARTIAL = "PARTIAL"      # Soft floor warning (F4-F5, F7)
    SEAL = "SEAL"            # All floors passed


@dataclass
class PsiVerdict:
    """
    PsiKernel evaluation result (final APEX judgment).

    Attributes:
        verdict: Final verdict (SEAL, VOID, PARTIAL, SABAR, HOLD_888)
        f8_genius: F8 (Genius) status
        hypervisor_passed: F10-F12 status from hypervisor
        passed: True if verdict = SEAL
        failures: List of all floor failures
        metadata: Rich debugging context
    """
    verdict: Verdict
    f8_genius: bool
    hypervisor_passed: bool
    passed: bool
    failures: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)

    @property
    def reason(self) -> str:
        """Human-readable explanation of verdict."""
        if self.verdict == Verdict.SEAL:
            return "PsiKernel: All floors passed → SEAL"
        else:
            return f"PsiKernel: {self.verdict} → {'; '.join(self.failures)}"


class PsiKernel:
    """
    PsiKernel (Ψ) - APEX Soul

    Evaluates F8 (Genius) and integrates F10-F12 (Hypervisor).
    Renders final verdict based on Trinity evaluation (Δ + Ω + Ψ).

    Execution:
        1. Check F8 (Genius): G ≥ 0.80
        2. Check Hypervisor: F10-F12 passed
        3. Aggregate Δ + Ω + Ψ failures
        4. Render verdict: SABAR > VOID > HOLD_888 > PARTIAL > SEAL
        5. Return: PsiVerdict with final judgment
    """

    def __init__(
        self,
        genius_threshold: float = 0.80
    ):
        """
        Initialize PsiKernel.

        Args:
            genius_threshold: Minimum G score (default 0.80)
        """
        self.genius_threshold = genius_threshold

    def evaluate(
        self,
        delta_verdict,  # DeltaVerdict from AGI kernel
        omega_verdict,  # OmegaVerdict from ASI kernel
        genius: float,
        hypervisor_passed: bool,
        hypervisor_failures: List[str]
    ) -> PsiVerdict:
        """
        Evaluate Trinity + Genius + Hypervisor → Final verdict.

        Args:
            delta_verdict: DeltaVerdict from AGI kernel (F1-F2)
            omega_verdict: OmegaVerdict from ASI kernel (F3-F7, F9)
            genius: F8 Genius score (0.0-1.0)
            hypervisor_passed: F10-F12 status from hypervisor
            hypervisor_failures: List of hypervisor failure reasons

        Returns:
            PsiVerdict with final APEX judgment
        """
        failures = []
        metadata = {}

        # Aggregate failures from Delta (AGI)
        if delta_verdict and not delta_verdict.passed:
            failures.extend(delta_verdict.failures)
            metadata["delta_failures"] = delta_verdict.failures

        # Aggregate failures from Omega (ASI)
        if omega_verdict and not omega_verdict.passed:
            failures.extend(omega_verdict.failures)
            metadata["omega_failures"] = omega_verdict.failures

        # F8: Genius (APEX floor)
        f8_passed = self._check_f8_genius(genius, failures, metadata)

        # F10-F12: Hypervisor (precedence 10-12)
        if not hypervisor_passed:
            failures.extend(hypervisor_failures)
            metadata["hypervisor_failures"] = hypervisor_failures

        # Render final verdict based on hierarchy
        final_verdict = self._render_verdict(
            delta_verdict=delta_verdict,
            omega_verdict=omega_verdict,
            f8_passed=f8_passed,
            hypervisor_passed=hypervisor_passed,
            failures=failures,
            metadata=metadata
        )

        return PsiVerdict(
            verdict=final_verdict,
            f8_genius=f8_passed,
            hypervisor_passed=hypervisor_passed,
            passed=(final_verdict == Verdict.SEAL),
            failures=failures,
            metadata=metadata
        )

    def _check_f8_genius(
        self,
        genius: float,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> bool:
        """Check F8 (Genius)."""
        # Ensure genius is a float
        try:
            g_score = float(genius)
        except (ValueError, TypeError):
            g_score = 0.0
            
        metadata["f8_genius"] = g_score
        metadata["f8_threshold"] = self.genius_threshold

        if g_score < self.genius_threshold:
            failures.append(
                f"F8 Genius FAIL: {g_score:.3f} < {self.genius_threshold} "
                f"(ungoverned intelligence)"
            )
            return False

        metadata["f8_reason"] = f"F8 Genius PASS: {g_score:.3f} ≥ {self.genius_threshold}"
        return True

    def _render_verdict(
        self,
        delta_verdict,
        omega_verdict,
        f8_passed: bool,
        hypervisor_passed: bool,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> Verdict:
        """
        Render final verdict based on hierarchy.

        Verdict Hierarchy (highest to lowest):
        1. SABAR: Hypervisor block (F10-F12 failure)
        2. VOID: Hard floor failure (F1 Amanah, F2 Clarity, F6 Ω₀)
        3. HOLD_888: Soft floor failure escalation OR High Stakes
        4. PARTIAL: Soft floor warning (F4 Peace², F5 κᵣ, F7 RASA)
        5. SEAL: All floors passed
        """
        # SABAR: Hypervisor block (highest priority)
        if not hypervisor_passed:
            metadata["verdict_reason"] = "Hypervisor block (F10-F12 failure)"
            return Verdict.SABAR

        # VOID: Hard floor failures
        hard_floor_failures = []
        
        # Safely check delta_verdict
        if delta_verdict:
            # F1 (Amanah) - hard
            if hasattr(delta_verdict, "f1_amanah") and not delta_verdict.f1_amanah:
                hard_floor_failures.append("F1 Amanah")

            # F2 (Clarity) - hard
            if hasattr(delta_verdict, "f2_clarity") and not delta_verdict.f2_clarity:
                hard_floor_failures.append("F2 Clarity")

        # Safely check omega_verdict
        if omega_verdict:
            # F6 (Ω₀/Humility) - hard
            if hasattr(omega_verdict, "f6_omega_0") and not omega_verdict.f6_omega_0:
                hard_floor_failures.append("F6 Ω₀")

        # F8 (Genius) - derived/hard
        if not f8_passed:
            hard_floor_failures.append("F8 Genius")

        if hard_floor_failures:
            metadata["verdict_reason"] = f"Hard floor failures: {', '.join(hard_floor_failures)}"
            return Verdict.VOID

        # PARTIAL: Soft floor warnings
        soft_floor_warnings = []

        if omega_verdict:
            # F3 (Tri-Witness) - soft/derived
            if hasattr(omega_verdict, "f3_tri_witness") and not omega_verdict.f3_tri_witness:
                soft_floor_warnings.append("F3 Tri-Witness")

            # F4 (Peace²) - soft
            if hasattr(omega_verdict, "f4_peace_squared") and not omega_verdict.f4_peace_squared:
                soft_floor_warnings.append("F4 Peace²")

            # F5 (κᵣ/Empathy) - soft
            if hasattr(omega_verdict, "f5_kappa_r") and not omega_verdict.f5_kappa_r:
                soft_floor_warnings.append("F5 κᵣ")

            # F7 (RASA) - soft
            if hasattr(omega_verdict, "f7_rasa") and not omega_verdict.f7_rasa:
                soft_floor_warnings.append("F7 RASA")

            # F9 (C_dark) - derived/soft
            if hasattr(omega_verdict, "f9_c_dark") and not omega_verdict.f9_c_dark:
                soft_floor_warnings.append("F9 C_dark")

        if soft_floor_warnings:
            metadata["verdict_reason"] = f"Soft floor warnings: {', '.join(soft_floor_warnings)}"
            return Verdict.PARTIAL

        # SEAL: All floors passed
        metadata["verdict_reason"] = "All 12 floors passed (F1-F12)"
        return Verdict.SEAL


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def render_apex_verdict(
    delta_verdict,
    omega_verdict,
    genius: float = 0.85,
    hypervisor_passed: bool = True,
    hypervisor_failures: List[str] = None
) -> PsiVerdict:
    """
    Convenience function to render APEX verdict.

    Args:
        delta_verdict: DeltaVerdict from AGI
        omega_verdict: OmegaVerdict from ASI
        genius: F8 Genius score
        hypervisor_passed: F10-F12 status
        hypervisor_failures: Hypervisor failure reasons

    Returns:
        PsiVerdict with final judgment
    """
    kernel = PsiKernel()
    return kernel.evaluate(
        delta_verdict=delta_verdict,
        omega_verdict=omega_verdict,
        genius=genius,
        hypervisor_passed=hypervisor_passed,
        hypervisor_failures=hypervisor_failures or []
    )


__all__ = [
    "PsiKernel",
    "PsiVerdict",
    "Verdict",
    "render_apex_verdict",
]


class Verdict(str, Enum):
    """Final verdict types (hierarchy: SABAR > VOID > HOLD_888 > PARTIAL > SEAL)."""
    SABAR = "SABAR"          # Hypervisor block (F10-F12 failure)
    VOID = "VOID"            # Hard floor failure (F1-F2, F6)
    HOLD_888 = "HOLD_888"    # Soft floor failure or high-stakes escalation
    PARTIAL = "PARTIAL"      # Soft floor warning (F4-F5, F7)
    SEAL = "SEAL"            # All floors passed


@dataclass
class PsiVerdict:
    """
    PsiKernel evaluation result (final APEX judgment).

    Attributes:
        verdict: Final verdict (SEAL, VOID, PARTIAL, SABAR, HOLD_888)
        f8_genius: F8 (Genius) status
        hypervisor_passed: F10-F12 status from hypervisor
        passed: True if verdict = SEAL
        failures: List of all floor failures
        metadata: Rich debugging context
    """
    verdict: Verdict
    f8_genius: bool
    hypervisor_passed: bool
    passed: bool
    failures: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)

    @property
    def reason(self) -> str:
        """Human-readable explanation of verdict."""
        if self.verdict == Verdict.SEAL:
            return "PsiKernel: All floors passed → SEAL"
        else:
            return f"PsiKernel: {self.verdict} → {'; '.join(self.failures)}"


class PsiKernel:
    """
    PsiKernel (Ψ) - APEX Soul

    Evaluates F8 (Genius) and integrates F10-F12 (Hypervisor).
    Renders final verdict based on Trinity evaluation (Δ + Ω + Ψ).

    Execution:
        1. Check F8 (Genius): G ≥ 0.80
        2. Check Hypervisor: F10-F12 passed
        3. Aggregate Δ + Ω + Ψ failures
        4. Render verdict: SABAR > VOID > HOLD_888 > PARTIAL > SEAL
        5. Return: PsiVerdict with final judgment

    Example:
        from codebase.agi.delta_kernel import DeltaKernel
        from codebase.asi.omega_kernel import OmegaKernel

        delta = DeltaKernel().evaluate(...)
        omega = OmegaKernel().evaluate(...)

        kernel = PsiKernel()
        verdict = kernel.evaluate(
            delta_verdict=delta,
            omega_verdict=omega,
            genius=0.85,
            hypervisor_passed=True,
            hypervisor_failures=[]
        )
        assert verdict.verdict == Verdict.SEAL
    """

    def __init__(
        self,
        genius_threshold: float = 0.80
    ):
        """
        Initialize PsiKernel.

        Args:
            genius_threshold: Minimum G score (default 0.80)
        """
        self.genius_threshold = genius_threshold

    def evaluate(
        self,
        delta_verdict,  # DeltaVerdict from AGI kernel
        omega_verdict,  # OmegaVerdict from ASI kernel
        genius: float,
        hypervisor_passed: bool,
        hypervisor_failures: List[str]
    ) -> PsiVerdict:
        """
        Evaluate Trinity + Genius + Hypervisor → Final verdict.

        Args:
            delta_verdict: DeltaVerdict from AGI kernel (F1-F2)
            omega_verdict: OmegaVerdict from ASI kernel (F3-F7, F9)
            genius: F8 Genius score (0.0-1.0)
            hypervisor_passed: F10-F12 status from hypervisor
            hypervisor_failures: List of hypervisor failure reasons

        Returns:
            PsiVerdict with final APEX judgment
        """
        failures = []
        metadata = {}

        # Aggregate failures from Delta (AGI)
        if not delta_verdict.passed:
            failures.extend(delta_verdict.failures)
            metadata["delta_failures"] = delta_verdict.failures

        # Aggregate failures from Omega (ASI)
        if not omega_verdict.passed:
            failures.extend(omega_verdict.failures)
            metadata["omega_failures"] = omega_verdict.failures

        # F8: Genius (APEX floor)
        f8_passed = self._check_f8_genius(genius, failures, metadata)

        # F10-F12: Hypervisor (precedence 10-12)
        if not hypervisor_passed:
            failures.extend(hypervisor_failures)
            metadata["hypervisor_failures"] = hypervisor_failures

        # Render final verdict based on hierarchy
        final_verdict = self._render_verdict(
            delta_verdict=delta_verdict,
            omega_verdict=omega_verdict,
            f8_passed=f8_passed,
            hypervisor_passed=hypervisor_passed,
            failures=failures,
            metadata=metadata
        )

        return PsiVerdict(
            verdict=final_verdict,
            f8_genius=f8_passed,
            hypervisor_passed=hypervisor_passed,
            passed=(final_verdict == Verdict.SEAL),
            failures=failures,
            metadata=metadata
        )

    def _check_f8_genius(
        self,
        genius: float,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> bool:
        """Check F8 (Genius)."""
        metadata["f8_genius"] = genius
        metadata["f8_threshold"] = self.genius_threshold

        if genius < self.genius_threshold:
            failures.append(
                f"F8 Genius FAIL: {genius:.3f} < {self.genius_threshold} "
                f"(ungoverned intelligence)"
            )
            return False

        metadata["f8_reason"] = f"F8 Genius PASS: {genius:.3f} ≥ {self.genius_threshold}"
        return True

    def _render_verdict(
        self,
        delta_verdict,
        omega_verdict,
        f8_passed: bool,
        hypervisor_passed: bool,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> Verdict:
        """
        Render final verdict based on hierarchy.

        Verdict Hierarchy (highest to lowest):
        1. SABAR: Hypervisor block (F10-F12 failure)
        2. VOID: Hard floor failure (F1 Amanah, F2 Clarity, F6 Ω₀)
        3. HOLD_888: Soft floor failure escalation
        4. PARTIAL: Soft floor warning (F4 Peace², F5 κᵣ, F7 RASA)
        5. SEAL: All floors passed
        """
        # SABAR: Hypervisor block (highest priority)
        if not hypervisor_passed:
            metadata["verdict_reason"] = "Hypervisor block (F10-F12 failure)"
            return Verdict.SABAR

        # VOID: Hard floor failures
        hard_floor_failures = []

        # F1 (Amanah) - hard
        if not delta_verdict.f1_amanah:
            hard_floor_failures.append("F1 Amanah")

        # F2 (Clarity) - hard
        if not delta_verdict.f2_clarity:
            hard_floor_failures.append("F2 Clarity")

        # F6 (Ω₀/Humility) - hard
        if not omega_verdict.f6_omega_0:
            hard_floor_failures.append("F6 Ω₀")

        # F8 (Genius) - derived/hard
        if not f8_passed:
            hard_floor_failures.append("F8 Genius")

        if hard_floor_failures:
            metadata["verdict_reason"] = f"Hard floor failures: {', '.join(hard_floor_failures)}"
            return Verdict.VOID

        # PARTIAL: Soft floor warnings
        soft_floor_warnings = []

        # F3 (Tri-Witness) - soft
        if not omega_verdict.f3_tri_witness:
            soft_floor_warnings.append("F3 Tri-Witness")

        # F4 (Peace²) - soft
        if not omega_verdict.f4_peace_squared:
            soft_floor_warnings.append("F4 Peace²")

        # F5 (κᵣ/Empathy) - soft
        if not omega_verdict.f5_kappa_r:
            soft_floor_warnings.append("F5 κᵣ")

        # F7 (RASA) - soft
        if not omega_verdict.f7_rasa:
            soft_floor_warnings.append("F7 RASA")

        # F9 (C_dark) - derived/soft
        if not omega_verdict.f9_c_dark:
            soft_floor_warnings.append("F9 C_dark")

        if soft_floor_warnings:
            metadata["verdict_reason"] = f"Soft floor warnings: {', '.join(soft_floor_warnings)}"
            return Verdict.PARTIAL

        # SEAL: All floors passed
        metadata["verdict_reason"] = "All 12 floors passed (F1-F12)"
        return Verdict.SEAL


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def render_apex_verdict(
    delta_verdict,
    omega_verdict,
    genius: float = 0.85,
    hypervisor_passed: bool = True,
    hypervisor_failures: List[str] = None
) -> PsiVerdict:
    """
    Convenience function to render APEX verdict.

    Args:
        delta_verdict: DeltaVerdict from AGI
        omega_verdict: OmegaVerdict from ASI
        genius: F8 Genius score
        hypervisor_passed: F10-F12 status
        hypervisor_failures: Hypervisor failure reasons

    Returns:
        PsiVerdict with final judgment
    """
    kernel = PsiKernel()
    return kernel.evaluate(
        delta_verdict=delta_verdict,
        omega_verdict=omega_verdict,
        genius=genius,
        hypervisor_passed=hypervisor_passed,
        hypervisor_failures=hypervisor_failures or []
    )


__all__ = [
    "PsiKernel",
    "PsiVerdict",
    "Verdict",
    "render_apex_verdict",
]
