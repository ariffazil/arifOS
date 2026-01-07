"""
Trinity Orchestrator — v46 Unified Floor Scoring via AGI·ASI·APEX

This module replaces the monolithic floor_scorer.py with the Trinity
Orthogonal architecture: AGI (Δ) → ASI (Ω) → APEX (Ψ).

Flow:
    Input → AGI (F1 Truth, F2 DeltaS)
          → ASI (F3 Peace², F4 κᵣ, F5 Ω₀, F7 RASA)
          → APEX (F6 Amanah, F8 Tri-Witness, F9 Anti-Hantu)
          → Verdict (SEAL/VOID/PARTIAL/SABAR/HOLD_888)

Backward compatibility: Maintains same API as floor_scorer.py for tests.

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Import kernel floor checks (v46 Trinity Orthogonal)
from ..agi.floor_checks import check_delta_s_f2, check_truth_f1
from ..asi.floor_checks import (
    check_kappa_r_f4,
    check_omega_band_f5,
    check_peace_squared_f3,
    check_rasa_f7,
)
from ..apex.floor_checks import check_amanah_f6, check_anti_hantu_f9, check_tri_witness_f8

# Import Amanah risk level for verdict logic
from ..floor_detectors.amanah_risk_detectors import RiskLevel


@dataclass
class FloorResult:
    """Result for a single floor check (v46 compatible with legacy API)."""
    floor_id: str
    floor_name: str
    passed: bool
    score: float
    details: str = ""


@dataclass
class GradeResult:
    """Overall grading result across all floors (v46 compatible with legacy API)."""
    verdict: str  # "SEAL", "PARTIAL", "VOID", "SABAR", "HOLD_888"
    floors: Dict[str, FloorResult] = field(default_factory=dict)
    failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    claim_profile: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/JSON."""
        return {
            "verdict": self.verdict,
            "floors": {k: {"passed": v.passed, "score": v.score} for k, v in self.floors.items()},
            "failures": self.failures,
            "warnings": self.warnings,
        }


class TrinityOrchestrator:
    """
    Trinity Orchestrator for v46 Constitutional Floor Scoring.

    Coordinates AGI (Δ), ASI (Ω), and APEX (Ψ) kernels to evaluate
    text against all 9 constitutional floors.

    v46 Floor Mapping:
        AGI (Δ):  F1 Truth, F2 DeltaS
        ASI (Ω):  F3 Peace², F4 κᵣ, F5 Ω₀, F7 RASA
        APEX (Ψ): F6 Amanah, F8 Tri-Witness, F9 Anti-Hantu
    """

    def grade(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> GradeResult:
        """
        Grade text against all 9 Constitutional Floors using Trinity architecture.

        Args:
            text: The text to grade (AI output or candidate response)
            context: Optional context dict with keys like:
                - lane: "SOCIAL", "CARE", "FACTUAL", "CRISIS"
                - metrics: Pre-computed metrics dict
                - high_stakes: Boolean for Tri-Witness enforcement

        Returns:
            GradeResult with verdict, floor results, and failures
        """
        context = context or {}
        floors: Dict[str, FloorResult] = {}
        failures: List[str] = []
        warnings: List[str] = []

        # =====================================================================
        # AGI KERNEL (Δ Delta) — Truth & Clarity
        # =====================================================================

        # F1: Truth
        f1_result = check_truth_f1(text, context)
        floors["F1"] = FloorResult(
            floor_id="F1",
            floor_name="Truth",
            passed=f1_result.passed,
            score=f1_result.score,
            details=f1_result.details,
        )
        if not f1_result.passed:
            failures.append("F1: Truth")

        # F2: DeltaS
        f2_result = check_delta_s_f2(context)
        floors["F2"] = FloorResult(
            floor_id="F2",
            floor_name="DeltaS",
            passed=f2_result.passed,
            score=f2_result.score,
            details=f2_result.details,
        )
        if not f2_result.passed:
            failures.append("F2: DeltaS")

        # =====================================================================
        # ASI KERNEL (Ω Omega) — Care & Safety
        # =====================================================================

        # F3: Peace²
        f3_result = check_peace_squared_f3(context)
        floors["F3"] = FloorResult(
            floor_id="F3",
            floor_name="Peace²",
            passed=f3_result.passed,
            score=f3_result.score,
            details=f3_result.details,
        )
        if not f3_result.passed:
            failures.append("F3: Peace²")

        # F4: κᵣ (Empathy)
        f4_result = check_kappa_r_f4(context)
        floors["F4"] = FloorResult(
            floor_id="F4",
            floor_name="κᵣ",
            passed=f4_result.passed,
            score=f4_result.score,
            details=f4_result.details,
        )
        if not f4_result.passed:
            failures.append("F4: κᵣ")

        # F5: Ω₀ (Humility)
        f5_result = check_omega_band_f5(context)
        floors["F5"] = FloorResult(
            floor_id="F5",
            floor_name="Ω₀",
            passed=f5_result.passed,
            score=f5_result.score,
            details=f5_result.details,
        )
        if not f5_result.passed:
            failures.append("F5: Ω₀")

        # F7: RASA (Felt Care)
        f7_result = check_rasa_f7(text, context)
        floors["F7"] = FloorResult(
            floor_id="F7",
            floor_name="RASA",
            passed=f7_result.passed,
            score=f7_result.score,
            details=f7_result.details,
        )
        if not f7_result.passed:
            failures.append("F7: RASA")

        # =====================================================================
        # APEX KERNEL (Ψ Psi) — Constitutional Judge
        # =====================================================================

        # F6: Amanah (Trust)
        f6_result = check_amanah_f6(text, context)
        floors["F6"] = FloorResult(
            floor_id="F6",
            floor_name="Amanah",
            passed=f6_result.passed,
            score=f6_result.score,
            details=f6_result.details,
        )
        if not f6_result.passed:
            failures.append("F6: Amanah")
        if f6_result.risk_level == RiskLevel.ORANGE:
            warnings.extend([f"F6: {v}" for v in f6_result.violations[:3]])

        # F8: Tri-Witness
        f8_result = check_tri_witness_f8(context)
        floors["F8"] = FloorResult(
            floor_id="F8",
            floor_name="Tri-Witness",
            passed=f8_result.passed,
            score=f8_result.score,
            details=f8_result.details,
        )
        if not f8_result.passed:
            failures.append("F8: Tri-Witness")

        # F9: Anti-Hantu
        f9_result = check_anti_hantu_f9(text, context)
        floors["F9"] = FloorResult(
            floor_id="F9",
            floor_name="Anti-Hantu",
            passed=f9_result.passed,
            score=f9_result.score,
            details=f9_result.details,
        )
        if not f9_result.passed:
            failures.append("F9: Anti-Hantu")
        if f9_result.violations:
            warnings.extend([f"F9: {v}" for v in f9_result.violations[:3]])

        # =====================================================================
        # COMPUTE VERDICT (Orthogonality Invariant: Dissent blocks action)
        # =====================================================================
        verdict = self._compute_verdict(floors, failures, f6_result.risk_level)

        return GradeResult(
            verdict=verdict,
            floors=floors,
            failures=failures,
            warnings=warnings,
            claim_profile=f1_result.claim_profile,
        )

    def _compute_verdict(
        self,
        floors: Dict[str, FloorResult],
        failures: List[str],
        amanah_risk: RiskLevel,
    ) -> str:
        """
        Compute final verdict based on Trinity floor results.

        Verdict Priority (v46):
            1. VOID — F1 Truth, F2 DeltaS, F5 Ω₀, F6 Amanah, F7 RASA, F9 Anti-Hantu hard failures
            2. HOLD_888 — F8 Tri-Witness failure or ORANGE Amanah risk
            3. PARTIAL — F3 Peace², F4 κᵣ soft failures
            4. SABAR — Minor issues needing clarification
            5. SEAL — All floors pass

        Args:
            floors: All floor check results
            failures: List of failed floor IDs
            amanah_risk: Amanah risk level (GREEN/ORANGE/RED)

        Returns:
            Verdict string
        """
        if not failures:
            return "SEAL"

        # VOID: Hard floor failures (AGI, ASI Ω₀/RASA, APEX Amanah/Anti-Hantu)
        hard_floors = ["F1: Truth", "F2: DeltaS", "F5: Ω₀", "F6: Amanah", "F7: RASA", "F9: Anti-Hantu"]
        if any(f in failures for f in hard_floors):
            return "VOID"

        # VOID: RED Amanah risk
        if amanah_risk == RiskLevel.RED:
            return "VOID"

        # HOLD_888: Tri-Witness failure or ORANGE Amanah
        if "F8: Tri-Witness" in failures or amanah_risk == RiskLevel.ORANGE:
            return "HOLD_888"

        # PARTIAL: Soft floor failures (Peace², κᵣ)
        if "F3: Peace²" in failures or "F4: κᵣ" in failures:
            return "PARTIAL"

        # SABAR: Other minor failures
        return "SABAR"


# =============================================================================
# SINGLETON INSTANCE (Backward compatibility with floor_scorer.py API)
# =============================================================================

TRINITY_ORCHESTRATOR = TrinityOrchestrator()
FLOOR_SCORER = TRINITY_ORCHESTRATOR  # Alias for backward compatibility


# =============================================================================
# CONVENIENCE FUNCTIONS (Backward compatibility)
# =============================================================================

def grade_text(text: str, **kwargs) -> GradeResult:
    """
    Quick grade using Trinity Orchestrator.

    Args:
        text: Text to grade
        **kwargs: Context args (lane, metrics, high_stakes)

    Returns:
        GradeResult with verdict and floor details
    """
    # If no metrics provided, synthesize reasonable defaults for standalone usage
    # This preserves backward compatibility with tests and convenience functions
    if "metrics" not in kwargs:
        # Synthesize optimistic defaults for conversational text
        # (NOT used in production pipeline - only for standalone testing)
        kwargs["metrics"] = {
            "truth": 0.99,  # Assume no false claims unless detected
            "delta_s": 0.1,  # Neutral clarity
            "peace_squared": 1.0,  # Non-destructive by default
            "kappa_r": 0.96,  # Empathetic
            "omega_0": 0.04,  # Appropriate humility
            "tri_witness": 0.96,  # Consensus
            "amanah": True,  # Safe unless Amanah detector flags
            "rasa": True,  # Felt care present
        }
    return TRINITY_ORCHESTRATOR.grade(text, context=kwargs)


def is_safe(text: str) -> bool:
    """
    Quick boolean safety check.

    Args:
        text: Text to check

    Returns:
        True if verdict is SEAL, False otherwise
    """
    # Use grade_text() to get synthetic defaults for standalone usage
    result = grade_text(text)
    return result.verdict == "SEAL"


# =============================================================================
# PUBLIC EXPORTS (Backward compatibility with floor_scorer.py)
# =============================================================================

__all__ = [
    "FloorResult",
    "GradeResult",
    "TrinityOrchestrator",
    "TRINITY_ORCHESTRATOR",
    "FLOOR_SCORER",
    "grade_text",
    "is_safe",
]
