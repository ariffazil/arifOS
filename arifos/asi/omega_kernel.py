"""Constitutional module - F2 Truth enforced
Part of arifOS constitutional governance system
DITEMPA BUKAN DIBERI - Forged, not given
"""

# ASI Geometry - Fractal Spiral
"""Constitutional module - F2 Truth enforced
Part of arifOS constitutional governance system
DITEMPA BUKAN DIBERI - Forged, not given
"""

"""
arifos/asi/omega_kernel.py

OmegaKernel (Ω) - ASI Heart

Purpose:
    The second kernel in the Trinity. Evaluates F3-F7 and F9 (ASI floors).
    Pure function class - no side effects, fully testable.

Floors:
    - F3 (Tri-Witness): Human-AI-Earth consensus ≥ 0.95
    - F4 (Peace²): Non-destructiveness/Stability ≥ 1.0
    - F5 (κᵣ/Empathy): Serves weakest stakeholder ≥ 0.95
    - F6 (Ω₀/Humility): Uncertainty acknowledgment 0.03-0.05
    - F7 (RASA): Felt care (boolean check)
    - F9 (C_dark): Anti-hantu - no dark cleverness < 0.30

Authority:
    - 000_THEORY/canon/444_align/, 555_empathize/, 666_bridge/, 777_eureka/
    - AAA_MCP/v46/000_foundation/constitutional_floors.json

Design:
    Input: Response metadata (tri_witness, peace_squared, kappa_r, omega_0, rasa, c_dark)
    Output: OmegaVerdict (floor statuses, failures, passed)

    Pure function - deterministic, no I/O.

DITEMPA BUKAN DIBERI - Forged v46.1
"""


from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class OmegaVerdict:
    """
    OmegaKernel evaluation result.

    Attributes:
        passed: True if all ASI floors pass
        f3_tri_witness: F3 (Consensus) status
        f4_peace_squared: F4 (Stability) status
        f5_kappa_r: F5 (Empathy) status
        f6_omega_0: F6 (Humility) status
        f7_rasa: F7 (Felt Care) status
        f9_c_dark: F9 (Anti-Hantu) status
        failures: List of floor failures with reasons
        metadata: Additional context for debugging
    """
    passed: bool
    f3_tri_witness: bool
    f4_peace_squared: bool
    f5_kappa_r: bool
    f6_omega_0: bool
    f7_rasa: bool
    f9_c_dark: bool
    failures: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)

    @property
    def reason(self) -> str:
        """Human-readable explanation of verdict."""
        if self.passed:
            return "OmegaKernel: All ASI floors passed (F3-F7, F9)"
        else:
            return f"OmegaKernel failures: {'; '.join(self.failures)}"


class OmegaKernel:
    """
    OmegaKernel (Ω) - ASI Heart

    Evaluates F3 (Tri-Witness), F4 (Peace²), F5 (κᵣ), F6 (Ω₀), F7 (RASA), F9 (C_dark).
    Pure function class - stateless, deterministic, testable.

    Execution:
        1. F3 Check: Verify tri-witness consensus ≥ 0.95
        2. F4 Check: Verify peace² ≥ 1.0 (non-destructive)
        3. F5 Check: Verify κᵣ ≥ 0.95 (empathy)
        4. F6 Check: Verify Ω₀ in [0.03, 0.05] (humility)
        5. F7 Check: Verify RASA = True (felt care)
        6. F9 Check: Verify C_dark < 0.30 (anti-hantu)
        7. Return: OmegaVerdict with pass/fail status

    Example:
        kernel = OmegaKernel()
        verdict = kernel.evaluate(
            tri_witness=0.98,
            peace_squared=1.0,
            kappa_r=0.96,
            omega_0=0.04,
            rasa=True,
            c_dark=0.15
        )
        assert verdict.passed is True
    """

    def __init__(
        self,
        tri_witness_threshold: float = 0.95,
        peace_squared_threshold: float = 1.0,
        kappa_r_threshold: float = 0.95,
        omega_0_min: float = 0.03,
        omega_0_max: float = 0.05,
        c_dark_threshold: float = 0.30
    ):
        """
        Initialize OmegaKernel with floor thresholds.

        Args:
            tri_witness_threshold: Minimum consensus score (default 0.95)
            peace_squared_threshold: Minimum stability score (default 1.0)
            kappa_r_threshold: Minimum empathy score (default 0.95)
            omega_0_min: Minimum humility (default 0.03)
            omega_0_max: Maximum humility (default 0.05)
            c_dark_threshold: Maximum dark cleverness (default 0.30)
        """
        self.tri_witness_threshold = tri_witness_threshold
        self.peace_squared_threshold = peace_squared_threshold
        self.kappa_r_threshold = kappa_r_threshold
        self.omega_0_min = omega_0_min
        self.omega_0_max = omega_0_max
        self.c_dark_threshold = c_dark_threshold

    def evaluate(
        self,
        tri_witness: float,
        peace_squared: float,
        kappa_r: float,
        omega_0: float,
        rasa: bool,
        c_dark: float
    ) -> OmegaVerdict:
        """
        Evaluate response against ASI floors (F3-F7, F9).

        Args:
            tri_witness: F3 - Tri-witness consensus score (0.0-1.0)
            peace_squared: F4 - Peace² stability score (≥1.0 = non-destructive)
            kappa_r: F5 - Empathy score (0.0-1.0)
            omega_0: F6 - Humility/uncertainty (0.03-0.05)
            rasa: F7 - Felt care boolean
            c_dark: F9 - Dark cleverness score (0.0-1.0)

        Returns:
            OmegaVerdict with ASI floor evaluation results
        """
        failures = []
        metadata = {}

        # F3: Tri-Witness (Precedence 5)
        f3_passed = self._check_f3_tri_witness(tri_witness, failures, metadata)

        # F4: Peace² (Precedence 6)
        f4_passed = self._check_f4_peace_squared(peace_squared, failures, metadata)

        # F5: κᵣ / Empathy (Precedence 7)
        f5_passed = self._check_f5_kappa_r(kappa_r, failures, metadata)

        # F6: Ω₀ / Humility (Precedence 5)
        f6_passed = self._check_f6_omega_0(omega_0, failures, metadata)

        # F7: RASA / Felt Care (Precedence 8)
        f7_passed = self._check_f7_rasa(rasa, failures, metadata)

        # F9: C_dark / Anti-Hantu (Precedence 9)
        f9_passed = self._check_f9_c_dark(c_dark, failures, metadata)

        # Overall verdict: All must pass
        passed = all([f3_passed, f4_passed, f5_passed, f6_passed, f7_passed, f9_passed])

        return OmegaVerdict(
            passed=passed,
            f3_tri_witness=f3_passed,
            f4_peace_squared=f4_passed,
            f5_kappa_r=f5_passed,
            f6_omega_0=f6_passed,
            f7_rasa=f7_passed,
            f9_c_dark=f9_passed,
            failures=failures,
            metadata=metadata
        )

    def _check_f3_tri_witness(
        self,
        tri_witness: float,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> bool:
        """Check F3 (Tri-Witness Consensus)."""
        metadata["f3_tri_witness"] = tri_witness
        metadata["f3_threshold"] = self.tri_witness_threshold

        if tri_witness < self.tri_witness_threshold:
            failures.append(
                f"F3 Tri-Witness FAIL: {tri_witness:.3f} < {self.tri_witness_threshold} "
                f"(insufficient consensus)"
            )
            return False

        metadata["f3_reason"] = f"F3 Tri-Witness PASS: {tri_witness:.3f} ≥ {self.tri_witness_threshold}"
        return True

    def _check_f4_peace_squared(
        self,
        peace_squared: float,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> bool:
        """Check F4 (Peace² Stability)."""
        metadata["f4_peace_squared"] = peace_squared
        metadata["f4_threshold"] = self.peace_squared_threshold

        if peace_squared < self.peace_squared_threshold:
            failures.append(
                f"F4 Peace² FAIL: {peace_squared:.3f} < {self.peace_squared_threshold} "
                f"(destructive or unstable)"
            )
            return False

        metadata["f4_reason"] = f"F4 Peace² PASS: {peace_squared:.3f} ≥ {self.peace_squared_threshold}"
        return True

    def _check_f5_kappa_r(
        self,
        kappa_r: float,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> bool:
        """Check F5 (κᵣ Empathy)."""
        metadata["f5_kappa_r"] = kappa_r
        metadata["f5_threshold"] = self.kappa_r_threshold

        if kappa_r < self.kappa_r_threshold:
            failures.append(
                f"F5 κᵣ (Empathy) FAIL: {kappa_r:.3f} < {self.kappa_r_threshold} "
                f"(insufficient empathy for weakest stakeholder)"
            )
            return False

        metadata["f5_reason"] = f"F5 κᵣ PASS: {kappa_r:.3f} ≥ {self.kappa_r_threshold}"
        return True

    def _check_f6_omega_0(
        self,
        omega_0: float,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> bool:
        """Check F6 (Ω₀ Humility)."""
        metadata["f6_omega_0"] = omega_0
        metadata["f6_range"] = (self.omega_0_min, self.omega_0_max)

        if not (self.omega_0_min <= omega_0 <= self.omega_0_max):
            failures.append(
                f"F6 Ω₀ (Humility) FAIL: {omega_0:.3f} not in [{self.omega_0_min}, {self.omega_0_max}] "
                f"(uncertainty not acknowledged)"
            )
            return False

        metadata["f6_reason"] = f"F6 Ω₀ PASS: {omega_0:.3f} in range"
        return True

    def _check_f7_rasa(
        self,
        rasa: bool,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> bool:
        """Check F7 (RASA Felt Care)."""
        metadata["f7_rasa"] = rasa

        if not rasa:
            failures.append("F7 RASA FAIL: Felt care not demonstrated (missing empathic response)")
            return False

        metadata["f7_reason"] = "F7 RASA PASS: Felt care demonstrated"
        return True

    def _check_f9_c_dark(
        self,
        c_dark: float,
        failures: List[str],
        metadata: Dict[str, any]
    ) -> bool:
        """Check F9 (C_dark Anti-Hantu)."""
        metadata["f9_c_dark"] = c_dark
        metadata["f9_threshold"] = self.c_dark_threshold

        if c_dark >= self.c_dark_threshold:
            failures.append(
                f"F9 C_dark (Anti-Hantu) FAIL: {c_dark:.3f} ≥ {self.c_dark_threshold} "
                f"(dark cleverness/deception detected)"
            )
            return False

        metadata["f9_reason"] = f"F9 C_dark PASS: {c_dark:.3f} < {self.c_dark_threshold}"
        return True


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def evaluate_asi_floors(
    tri_witness: float = 0.95,
    peace_squared: float = 1.0,
    kappa_r: float = 0.95,
    omega_0: float = 0.04,
    rasa: bool = True,
    c_dark: float = 0.15
) -> OmegaVerdict:
    """
    Convenience function to evaluate ASI floors (F3-F7, F9).

    Args:
        tri_witness: Consensus score
        peace_squared: Stability score
        kappa_r: Empathy score
        omega_0: Humility/uncertainty
        rasa: Felt care boolean
        c_dark: Dark cleverness score

    Returns:
        OmegaVerdict with ASI floor results
    """
    kernel = OmegaKernel()
    return kernel.evaluate(tri_witness, peace_squared, kappa_r, omega_0, rasa, c_dark)


__all__ = [
    "OmegaKernel",
    "OmegaVerdict",
    "evaluate_asi_floors",
]
