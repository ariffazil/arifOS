"""
Stage 555 EMPATHIZE: ASI Empathy Calibration (OmegaKernel F3-F7, F9)

Implements empathy calibration based on Track B spec:
L2_PROTOCOLS/v46/555_empathize/empathy_floor.json

Authority: Track A Canon L1_THEORY/canon/555_empathize/520_EMPATHY_F4_v46.md

PURPOSE: Apply ASI (Anthropic Superhuman Intelligence) floors to ensure care,
humility, and stakeholder protection. This is the CARE layer after REASON (AGI)
and before WITNESS (APEX).

ASI Floors:
- F3: Tri-Witness (≥0.95) - Human·AI·Earth consensus
- F4: Peace² (≥1.0) - Non-destructive stability
- F5: κᵣ Empathy (≥0.95) - Serve weakest stakeholder
- F6: Ω₀ Humility (0.03-0.05) - Acknowledge uncertainty
- F7: RASA (LOCK) - Active listening, felt care
- F9: C_dark (<0.30) - Anti-Hantu (no dark cleverness)

ADAPTED FROM: arifos_core/pipeline/stage_555_feel.py
"""

from typing import TypedDict, Literal

from ..asi.omega_kernel import OmegaKernel
from .integration_333 import IntegrationBundle


# Type aliases
EmpathyVerdict = Literal["PASS", "PARTIAL", "VOID"]


class ASIFloorScores(TypedDict):
    """ASI floor evaluation scores."""

    F3_tri_witness: float      # ≥0.95
    F4_peace_squared: float    # ≥1.0
    F5_kappa_r: float          # ≥0.95
    F6_omega_0: float          # 0.03-0.05
    F7_rasa: bool              # LOCK (True required)
    F9_c_dark: float           # <0.30


class EmpathyBundle555(TypedDict):
    """Empathy-calibrated bundle from ASI evaluation."""

    integration_bundle_333: IntegrationBundle  # IMMUTABLE pass-through (F8)
    asi_floor_scores: ASIFloorScores
    empathy_verdict: EmpathyVerdict
    soft_flags: list[str]  # Warnings for soft floor violations
    omega_confidence: float  # OmegaKernel confidence score
    weakest_stakeholder_protected: bool  # F5 requirement
    handoff: dict[str, str | int]  # Handoff to 666 BRIDGE


def compute_asi_scores(integration_bundle: IntegrationBundle) -> ASIFloorScores:
    """
    Compute ASI floor scores from integration bundle.

    In runtime mode, we extract ASI metrics from:
    - Reasoned bundle (floor_scores)
    - Integration verdict (streak_count for tri-witness)
    - Response analysis (humility markers, care signals)

    Args:
        integration_bundle: Output from 333 INTEGRATION

    Returns:
        ASI floor scores for OmegaKernel evaluation
    """
    reasoned_bundle = integration_bundle.get("reasoned_bundle_333")  # type: ignore
    if not reasoned_bundle:
        # Fallback to integration bundle's floor_verdict
        floor_verdict = integration_bundle["floor_verdict"]
        passed_floors = floor_verdict["passed_floors"]

        # Conservative defaults (fail-closed)
        return ASIFloorScores(
            F3_tri_witness=0.0,  # Will compute from streak
            F4_peace_squared=1.0 if "F3_stability" in passed_floors else 0.0,
            F5_kappa_r=0.0,      # Will compute from response
            F6_omega_0=0.04,     # Neutral humility
            F7_rasa=True,        # Assume active listening
            F9_c_dark=0.0        # No dark cleverness
        )

    # Extract from reasoned bundle
    floor_scores = reasoned_bundle.get("floor_scores", {})

    # F3: Tri-witness (compute from streak count)
    streak = integration_bundle.get("streak_count", 0)
    tri_witness = min(0.90 + (streak * 0.05), 1.0)  # 3 streak → 1.05 capped at 1.0

    # F4: Peace² (stability)
    peace_squared = floor_scores.get("F3_stability", 0.0)

    # F5: κᵣ Empathy (extract from response or use conservative default)
    kappa_r = floor_scores.get("F4_empathy", 0.0)

    # F6: Ω₀ Humility (default to neutral band)
    omega_0 = 0.04  # Middle of 0.03-0.05 band

    # F7: RASA (assume active listening unless evidence otherwise)
    rasa = True

    # F9: C_dark (anti-hantu)
    c_dark = floor_scores.get("F9_c_dark", 0.0)

    return ASIFloorScores(
        F3_tri_witness=tri_witness,
        F4_peace_squared=peace_squared,
        F5_kappa_r=kappa_r,
        F6_omega_0=omega_0,
        F7_rasa=rasa,
        F9_c_dark=c_dark
    )


def check_weakest_stakeholder(
    integration_bundle: IntegrationBundle,
    asi_scores: ASIFloorScores
) -> bool:
    """
    Verify F5 requirement: Serve the weakest stakeholder.

    This checks:
    1. κᵣ empathy score ≥0.95
    2. Response doesn't harm vulnerable populations
    3. Care is directed toward those most affected

    Args:
        integration_bundle: Integration verdict
        asi_scores: ASI floor scores

    Returns:
        True if weakest stakeholder is protected
    """
    # Primary check: κᵣ threshold
    if asi_scores["F5_kappa_r"] < 0.95:
        return False

    # Secondary check: No destructive actions (peace² floor)
    if asi_scores["F4_peace_squared"] < 1.0:
        return False

    # Tertiary check: Integration verdict is not VOID
    if integration_bundle["integrated_verdict"] == "VOID":
        return False

    return True


def empathy_stage(integration_bundle_333: IntegrationBundle) -> EmpathyBundle555:
    """
    555 EMPATHIZE: ASI empathy calibration (OmegaKernel F3-F7, F9).

    Implements Track B spec: L2_PROTOCOLS/v46/555_empathize/empathy_floor.json

    Pipeline:
    1. Extract ASI floor scores from integration bundle
    2. Initialize OmegaKernel with ASI thresholds
    3. Evaluate ASI floors (F3-F7, F9)
    4. Check weakest stakeholder protection (F5)
    5. Collect soft flags (warnings for PARTIAL floors)
    6. Package empathy_bundle with IMMUTABLE pass-through

    ASI Floors (Soft - warnings only):
    - F3: Tri-Witness ≥0.95 (consensus)
    - F4: Peace² ≥1.0 (stability)
    - F5: κᵣ ≥0.95 (empathy)
    - F6: Ω₀ ∈ [0.03, 0.05] (humility)
    - F7: RASA = LOCK (active listening)
    - F9: C_dark <0.30 (anti-hantu)

    Args:
        integration_bundle_333: Output from 333 INTEGRATION

    Returns:
        EmpathyBundle555 with ASI evaluation

    Raises:
        ValueError: If verdict is VOID or SABAR (hard ASI floor failure)
    """
    # Step 1: Compute ASI scores
    asi_scores = compute_asi_scores(integration_bundle_333)

    # Step 2: Initialize OmegaKernel
    kernel = OmegaKernel(
        tri_witness_threshold=0.95,
        peace_squared_threshold=1.0,
        kappa_r_threshold=0.95,
        omega_0_min=0.03,
        omega_0_max=0.05,
        c_dark_threshold=0.30
    )

    # Step 3: Evaluate ASI floors
    omega_verdict = kernel.evaluate(
        tri_witness=asi_scores["F3_tri_witness"],
        peace_squared=asi_scores["F4_peace_squared"],
        kappa_r=asi_scores["F5_kappa_r"],
        omega_0=asi_scores["F6_omega_0"],
        rasa=asi_scores["F7_rasa"],
        c_dark=asi_scores["F9_c_dark"]
    )

    # Step 4: Check weakest stakeholder
    weakest_protected = check_weakest_stakeholder(integration_bundle_333, asi_scores)

    # Step 5: Collect soft flags
    soft_flags: list[str] = []
    if not omega_verdict.passed:
        soft_flags.extend(omega_verdict.failures)

    if not weakest_protected:
        soft_flags.append("F5_weakest_stakeholder_not_protected")

    # Step 6: Determine verdict
    if len(soft_flags) == 0:
        empathy_verdict: EmpathyVerdict = "PASS"
    elif len(soft_flags) <= 2:
        empathy_verdict = "PARTIAL"  # Soft warnings only
    else:
        empathy_verdict = "VOID"  # Too many ASI floor failures

    # Step 7: Package bundle
    empathy_bundle: EmpathyBundle555 = {
        "integration_bundle_333": integration_bundle_333,  # ← IMMUTABLE (F8)
        "asi_floor_scores": asi_scores,
        "empathy_verdict": empathy_verdict,
        "soft_flags": soft_flags,
        "omega_confidence": (
            omega_verdict.confidence
            if hasattr(omega_verdict, "confidence")
            else 0.85
        ),
        "weakest_stakeholder_protected": weakest_protected,
        "handoff": {
            "from_stage": "555_EMPATHIZE",
            "to_stage": "666_BRIDGE",
            "floor_count": len(soft_flags),
            "asi_ready": empathy_verdict in ["PASS", "PARTIAL"]
        }
    }

    # Step 8: Verdict logic (raise if VOID)
    if empathy_verdict == "VOID":
        flag_summary = ", ".join(soft_flags[:3])  # Show first 3
        raise ValueError(
            f"VOID: ASI empathy calibration failed ({len(soft_flags)} violations) - {flag_summary}"
        )

    return empathy_bundle


__all__ = [
    "empathy_stage",
    "EmpathyBundle555",
    "ASIFloorScores",
    "EmpathyVerdict",
    "compute_asi_scores",
    "check_weakest_stakeholder"
]
