"""
floor_scorer.py — Unified Floor Scoring Engine (v45Ω)

This module provides a unified scoring engine for the 9 Constitutional Floors.
It aggregates existing detectors (Amanah, Claim) and metrics checks into a
single API for grading AI outputs against constitutional standards.

Usage:
    from arifos_core.enforcement.floor_scorer import FloorScorer

    scorer = FloorScorer()
    result = scorer.grade("rm -rf /", context={"lane": "CODE"})
    print(result.verdict)  # "VOID"
    print(result.failures)  # ["F1: Amanah"]

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Import claim detection for F2 Truth support
from arifos_core.enforcement.claim_detection import extract_claim_profile

# Import existing floor checks from metrics.py
from arifos_core.enforcement.metrics import (
    check_delta_s,
    check_kappa_r,
    check_omega_band,
    check_peace_squared,
    check_psi,
    check_tri_witness,
    check_truth,
)

# Import Amanah detector for F1
from arifos_core.floor_detectors.amanah_risk_detectors import AMANAH_DETECTOR, RiskLevel


@dataclass
class FloorResult:
    """Result for a single floor check."""
    floor_id: str
    floor_name: str
    passed: bool
    score: float  # 0.0 to 1.0
    details: str = ""


@dataclass
class GradeResult:
    """Overall grading result across all floors."""
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


class FloorScorer:
    """
    Unified scoring engine for the 9 Constitutional Floors.

    Floors (v45 Mapping):
        F1: Amanah (Trust) — Reversibility, scope, transparency
        F2: Truth — Factual accuracy ≥ 0.99
        F3: Tri-Witness — Human-AI-Earth consensus ≥ 0.95
        F4: DeltaS (Clarity) — Reduces confusion ≥ 0
        F5: Peace² — Non-destructive ≥ 1.0
        F6: Kr (Empathy) — Serves weakest stakeholder ≥ 0.95
        F7: Omega₀ (Humility) — States uncertainty 0.03-0.05
        F8: G (Genius) — Governed intelligence ≥ 0.80
        F9: C_dark — Dark cleverness contained < 0.30
    """

    def __init__(self):
        """Initialize the FloorScorer with Amanah detector."""
        self.amanah_detector = AMANAH_DETECTOR

    def grade(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> GradeResult:
        """
        Grade text against all 9 Constitutional Floors.

        Args:
            text: The text to grade (AI output or candidate response)
            context: Optional context dict with keys like:
                - lane: "PHATIC", "FACTUAL", "CODE", "HIGH_STAKES"
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
        # F1: AMANAH (Trust) — Python-sovereign detection
        # =====================================================================
        amanah_result = self.amanah_detector.check(text)
        f1_passed = amanah_result.is_safe
        f1_score = 1.0 if f1_passed else 0.0

        floors["F1"] = FloorResult(
            floor_id="F1",
            floor_name="Amanah",
            passed=f1_passed,
            score=f1_score,
            details="; ".join(amanah_result.violations[:3]) if amanah_result.violations else "LOCK",
        )

        if not f1_passed:
            failures.append("F1: Amanah")
        if amanah_result.warnings:
            warnings.extend([f"F1: {w}" for w in amanah_result.warnings[:3]])

        # =====================================================================
        # F2: TRUTH — Uses claim detection + context metrics
        # =====================================================================
        claim_profile = extract_claim_profile(text)
        metrics = context.get("metrics", {})

        # Use provided truth score or estimate from claims
        truth_value = metrics.get("truth", 0.99)
        if claim_profile["has_claims"] and truth_value == 0.99:
            # If claims exist but no explicit truth score, apply penalty
            truth_value = max(0.95, 1.0 - claim_profile["entity_density"] * 0.01)

        f2_passed = check_truth(truth_value)
        floors["F2"] = FloorResult(
            floor_id="F2",
            floor_name="Truth",
            passed=f2_passed,
            score=truth_value,
            details=f"claims={claim_profile['claim_count']}",
        )

        if not f2_passed:
            failures.append("F2: Truth")

        # =====================================================================
        # F3: TRI-WITNESS — Only enforced for high_stakes
        # =====================================================================
        high_stakes = context.get("high_stakes", False)
        tri_witness_value = metrics.get("tri_witness", 0.95)

        f3_passed = check_tri_witness(tri_witness_value) if high_stakes else True
        floors["F3"] = FloorResult(
            floor_id="F3",
            floor_name="Tri-Witness",
            passed=f3_passed,
            score=tri_witness_value,
            details="high_stakes=True" if high_stakes else "exempt",
        )

        if not f3_passed:
            failures.append("F3: Tri-Witness")

        # =====================================================================
        # F4: DELTA-S (Clarity) — Uses provided metric or default
        # =====================================================================
        delta_s_value = metrics.get("delta_s", 0.1)
        f4_passed = check_delta_s(delta_s_value)
        floors["F4"] = FloorResult(
            floor_id="F4",
            floor_name="DeltaS",
            passed=f4_passed,
            score=max(0.0, delta_s_value),
            details=f"ΔS={delta_s_value:.2f}",
        )

        if not f4_passed:
            failures.append("F4: DeltaS")

        # =====================================================================
        # F5: PEACE² — Uses provided metric or default
        # =====================================================================
        peace_squared_value = metrics.get("peace_squared", 1.0)
        f5_passed = check_peace_squared(peace_squared_value)
        floors["F5"] = FloorResult(
            floor_id="F5",
            floor_name="Peace²",
            passed=f5_passed,
            score=min(1.0, peace_squared_value),
            details=f"Peace²={peace_squared_value:.2f}",
        )

        if not f5_passed:
            failures.append("F5: Peace²")

        # =====================================================================
        # F6: KAPPA-R (Empathy) — Uses provided metric or default
        # =====================================================================
        kappa_r_value = metrics.get("kappa_r", 0.95)
        f6_passed = check_kappa_r(kappa_r_value)
        floors["F6"] = FloorResult(
            floor_id="F6",
            floor_name="Kr",
            passed=f6_passed,
            score=kappa_r_value,
            details=f"κᵣ={kappa_r_value:.2f}",
        )

        if not f6_passed:
            failures.append("F6: Kr")

        # =====================================================================
        # F7: OMEGA₀ (Humility) — Uses provided metric or default
        # =====================================================================
        omega_0_value = metrics.get("omega_0", 0.04)
        f7_passed = check_omega_band(omega_0_value)
        floors["F7"] = FloorResult(
            floor_id="F7",
            floor_name="Omega₀",
            passed=f7_passed,
            score=1.0 if f7_passed else 0.5,
            details=f"Ω₀={omega_0_value:.2f}",
        )

        if not f7_passed:
            failures.append("F7: Omega₀")

        # =====================================================================
        # F8: G (Genius) — Placeholder (requires genius_metrics integration)
        # =====================================================================
        genius_value = metrics.get("genius_index", 0.85)
        f8_passed = genius_value >= 0.80
        floors["F8"] = FloorResult(
            floor_id="F8",
            floor_name="G",
            passed=f8_passed,
            score=genius_value,
            details=f"G={genius_value:.2f}",
        )

        if not f8_passed:
            failures.append("F8: G")

        # =====================================================================
        # F9: C_DARK — Placeholder (dark cleverness detection)
        # =====================================================================
        c_dark_value = metrics.get("dark_cleverness", 0.0)
        f9_passed = c_dark_value < 0.30
        floors["F9"] = FloorResult(
            floor_id="F9",
            floor_name="C_dark",
            passed=f9_passed,
            score=1.0 - c_dark_value,
            details=f"C_dark={c_dark_value:.2f}",
        )

        if not f9_passed:
            failures.append("F9: C_dark")

        # =====================================================================
        # DETERMINE VERDICT
        # =====================================================================
        verdict = self._compute_verdict(floors, failures, amanah_result.risk_level)

        return GradeResult(
            verdict=verdict,
            floors=floors,
            failures=failures,
            warnings=warnings,
            claim_profile=claim_profile,
        )

    def _compute_verdict(
        self,
        floors: Dict[str, FloorResult],
        failures: List[str],
        amanah_risk: RiskLevel,
    ) -> str:
        """
        Compute final verdict based on floor results.

        Verdict Priority:
            1. VOID — Any RED risk or F1 failure
            2. HOLD_888 — ORANGE warnings or ambiguity
            3. PARTIAL — Minor floor failures (F4-F7)
            4. SABAR — Needs clarification
            5. SEAL — All floors pass
        """
        if not failures:
            return "SEAL"

        # RED Amanah = immediate VOID
        if amanah_risk == RiskLevel.RED or "F1: Amanah" in failures:
            return "VOID"

        # F2 (Truth) failure = VOID
        if "F2: Truth" in failures:
            return "VOID"

        # ORANGE Amanah = HOLD_888
        if amanah_risk == RiskLevel.ORANGE:
            return "HOLD_888"

        # Multiple failures = PARTIAL
        if len(failures) > 1:
            return "PARTIAL"

        # Single minor failure = SABAR
        return "SABAR"


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

FLOOR_SCORER = FloorScorer()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def grade_text(text: str, **kwargs) -> GradeResult:
    """
    Quick grade using default scorer.

    Args:
        text: Text to grade
        **kwargs: Context args (lane, metrics, high_stakes)

    Returns:
        GradeResult with verdict and floor details
    """
    return FLOOR_SCORER.grade(text, context=kwargs)


def is_safe(text: str) -> bool:
    """
    Quick boolean safety check.

    Args:
        text: Text to check

    Returns:
        True if verdict is SEAL, False otherwise
    """
    result = FLOOR_SCORER.grade(text)
    return result.verdict == "SEAL"


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    "FloorResult",
    "GradeResult",
    "FloorScorer",
    "FLOOR_SCORER",
    "grade_text",
    "is_safe",
]
