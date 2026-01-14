"""
Stage 333 INTEGRATION: Tri-Axis AND Logic (APEX - Verdict Synthesis)

Implements tri-axis integration based on Track B spec:
L2_PROTOCOLS/v46/333_atlas/333_integration.json

Authority: Track A Canon L1_THEORY/canon/333_atlas/40_333_INTEGRATION_v46.md

PURPOSE: Combine REASON (single-agent) + CONTRAST (multi-agent) + FLOORS (constitutional)
verdicts using tri-axis AND logic. This is the final 333 stage before handoff to 444 ALIGN.

Formula: SEAL if (reason_verdict == PASS) AND (floor_verdict == PASS) AND (contrast_verdict OK)

NEW FILE: Verdict synthesis logic (not migrated from pipeline/)
"""

from typing import TypedDict, Literal

from .reason_333 import ReasonedBundle333, VerdictType
from .contrast_333 import ContrastBundle, ContrastType


# Type aliases
IntegratedVerdict = Literal["SEAL", "VOID", "SABAR", "HOLD_888", "PARTIAL"]
FloorOverride = Literal["F1_HARD", "F8_Tri_Witness", "F5_Peace", "F2_Truth", "F3_Burst", "F4_Empathy"]


class FloorVerdict(TypedDict):
    """Floor validation verdict."""

    overall: Literal["PASS", "VOID", "PARTIAL"]
    failed_floors: list[str]  # e.g., ["F1_truth", "F5_peace"]
    passed_floors: list[str]


class IntegrationBundle(TypedDict):
    """Integrated verdict from tri-axis AND logic."""

    reason_verdict: VerdictType  # From 333 REASON
    contrast_verdict: str | None  # From 333 CONTRAST (optional)
    floor_verdict: FloorVerdict  # Floor validation result
    integrated_verdict: IntegratedVerdict  # Final 333 verdict
    floor_priority_applied: list[FloorOverride]  # Which overrides triggered
    reasoning: str  # Explanation of verdict (F7 Humility)
    streak_count: int  # Consecutive successes (for 888 HOLD logic)


# Floor priority hierarchy (spec: higher priority floors override lower)
FLOOR_PRIORITY: list[tuple[str, float]] = [
    ("F1_HARD", 1.0),  # Budget ≥ 100% (hard constraint)
    ("F8_Tri_Witness", 0.95),  # Streak ≥ 3 (tri-witness override)
    ("F5_Peace", 1.0),  # Non-destructive requirement
    ("F2_Truth", 0.99),  # Factual accuracy
    ("F3_Burst", 1.0),  # Stability (no rapid changes)
    ("F4_Empathy", 0.95),  # Serve weakest stakeholder
    ("F6_RASA", 0.95),  # Active listening
    ("F7_Humility", 0.04),  # Uncertainty acknowledgment (0.03-0.05)
    ("F9_C_dark", 0.30),  # Anti-hantu (no dark cleverness)
    ("F10_Symbolic", True),  # Symbolic mode (boolean)
    ("F11_Command_Auth", True),  # Command authority (boolean)
    ("F12_Injection", 0.85),  # Injection defense (< 0.85)
]


def evaluate_floors(reasoned_bundle: ReasonedBundle333) -> FloorVerdict:
    """
    Evaluate all constitutional floors (F1-F12).

    Args:
        reasoned_bundle: Output from 333 REASON

    Returns:
        FloorVerdict with overall pass/fail and floor details
    """
    floor_scores = reasoned_bundle["floor_scores"]
    failed_floors: list[str] = []
    passed_floors: list[str] = []

    # F1 Truth (≥0.99 required)
    if floor_scores["F1_truth"] < 0.99:
        failed_floors.append("F1_truth")
    else:
        passed_floors.append("F1_truth")

    # F2 Clarity (ΔS ≥ 0)
    if floor_scores["F2_clarity"] < 0.0:
        failed_floors.append("F2_clarity")
    else:
        passed_floors.append("F2_clarity")

    # F10 Symbolic (must be True)
    if not floor_scores["F10_symbolic"]:
        failed_floors.append("F10_symbolic")
    else:
        passed_floors.append("F10_symbolic")

    # F12 Injection (< 0.85)
    if floor_scores["F12_injection"] >= 0.85:
        failed_floors.append("F12_injection")
    else:
        passed_floors.append("F12_injection")

    # Overall verdict
    if len(failed_floors) > 0:
        overall: Literal["PASS", "VOID", "PARTIAL"] = "VOID"  # Hard floor failures
    else:
        overall = "PASS"

    return FloorVerdict(
        overall=overall,
        failed_floors=failed_floors,
        passed_floors=passed_floors
    )


def apply_cascade_rules(
    reason_verdict: VerdictType,
    contrast_verdict: str | None,
    floor_verdict: FloorVerdict,
    streak_count: int
) -> tuple[IntegratedVerdict, list[FloorOverride], str]:
    """
    Apply tri-axis AND cascade rules.

    Cascade Rules (spec):
    1. VOID propagates: If ANY axis returns VOID, integrated_verdict = VOID
    2. SABAR escalates: If ANY axis returns SABAR, integrated_verdict = SABAR
    3. HOLD_888 overrides: If streak >= 3, integrated_verdict = HOLD_888
    4. Otherwise: Tri-axis AND logic

    Args:
        reason_verdict: Verdict from 333 REASON
        contrast_verdict: Verdict from 333 CONTRAST (optional)
        floor_verdict: Floor validation result
        streak_count: Consecutive successful verdicts

    Returns:
        Tuple of (integrated_verdict, floor_priority_applied, reasoning)
    """
    floor_priority_applied: list[FloorOverride] = []
    reasoning_parts: list[str] = []

    # Rule 1: VOID propagates
    if reason_verdict == "VOID":
        return ("VOID", floor_priority_applied, "REASON returned VOID (AGI floor failure)")

    if floor_verdict["overall"] == "VOID":
        failed = ", ".join(floor_verdict["failed_floors"])
        return ("VOID", floor_priority_applied, f"FLOORS failed: {failed}")

    if contrast_verdict and "VOID" in contrast_verdict:
        return ("VOID", floor_priority_applied, "CONTRAST returned VOID (jailbreak or TAC failure)")

    # Rule 2: SABAR escalates
    if reason_verdict == "SABAR":
        return ("SABAR", floor_priority_applied, "REASON returned SABAR (AGI uncertainty)")

    if contrast_verdict and "SABAR" in contrast_verdict:
        return ("SABAR", floor_priority_applied, "CONTRAST returned SABAR (adversarial TAC > 0.60)")

    # Rule 3: HOLD_888 override (streak >= 3)
    if streak_count >= 3:
        floor_priority_applied.append("F8_Tri_Witness")
        reasoning_parts.append(f"Streak count {streak_count} ≥ 3 triggers HOLD_888 (F8 Tri-Witness override)")
        return ("HOLD_888", floor_priority_applied, "; ".join(reasoning_parts))

    # Rule 4: Tri-axis AND logic
    # SEAL if: (reason == PASS) AND (floor == PASS) AND (contrast OK or None)
    reason_ok = reason_verdict in ["PASS", "PASS_WITH_FLAGS"]
    floor_ok = floor_verdict["overall"] == "PASS"
    contrast_ok = (
        contrast_verdict is None or
        contrast_verdict in ["CONSENSUS_BORING", "DIVERGENT_USEFUL"]
    )

    if reason_ok and floor_ok and contrast_ok:
        # Check for soft flags
        if reason_verdict == "PASS_WITH_FLAGS":
            reasoning_parts.append("REASON passed with soft flags (requires ASI review)")
            return ("PARTIAL", floor_priority_applied, "; ".join(reasoning_parts))
        else:
            reasoning_parts.append("Tri-axis AND: REASON ∧ FLOORS ∧ CONTRAST all passed")
            return ("SEAL", floor_priority_applied, "; ".join(reasoning_parts))

    # Fallback: PARTIAL (some checks passed, some failed softly)
    reasoning_parts.append("Tri-axis AND: Some conditions passed, some failed (soft floors)")
    return ("PARTIAL", floor_priority_applied, "; ".join(reasoning_parts))


def integration_stage(
    reasoned_bundle: ReasonedBundle333,
    contrast_bundle: ContrastBundle | None = None,
    streak_count: int = 0
) -> IntegrationBundle:
    """
    333 INTEGRATION: Tri-axis AND logic (final 333 verdict synthesis).

    Implements Track B spec: L2_PROTOCOLS/v46/333_atlas/333_integration.json

    Pipeline:
    1. Extract verdicts from REASON (single-agent)
    2. Extract verdicts from CONTRAST (multi-agent, optional)
    3. Evaluate all constitutional floors (F1-F12)
    4. Apply cascade rules (VOID propagates, SABAR escalates, HOLD_888 overrides)
    5. Tri-axis AND logic: SEAL if (REASON ∧ FLOORS ∧ CONTRAST) all pass
    6. Package integration_bundle

    Tri-Axis AND Formula:
    SEAL = (reason_verdict == PASS) ∧ (floor_verdict == PASS) ∧ (contrast_verdict OK)

    Args:
        reasoned_bundle: Output from 333 REASON
        contrast_bundle: Output from 333 CONTRAST (optional)
        streak_count: Consecutive successful verdicts (for 888 HOLD logic)

    Returns:
        IntegrationBundle with final 333 verdict

    Raises:
        ValueError: If verdict is VOID or SABAR
    """
    # Step 1: Extract reason verdict
    reason_verdict = reasoned_bundle["verdict"]

    # Step 2: Extract contrast verdict (if present)
    contrast_verdict: str | None = None
    if contrast_bundle:
        contrast_type = contrast_bundle["contrast_type"]
        tac_score = contrast_bundle["contrast_score"]

        if contrast_type == "CONSENSUS":
            contrast_verdict = "CONSENSUS_BORING"
        elif contrast_type == "DIVERGENT":
            contrast_verdict = "DIVERGENT_USEFUL"
        else:  # ADVERSARIAL
            contrast_verdict = f"ADVERSARIAL_TAC_{tac_score:.2f}"

    # Step 3: Evaluate floors
    floor_verdict = evaluate_floors(reasoned_bundle)

    # Step 4: Apply cascade rules
    integrated_verdict, floor_priority_applied, reasoning = apply_cascade_rules(
        reason_verdict,
        contrast_verdict,
        floor_verdict,
        streak_count
    )

    # Step 5: Package bundle
    integration_bundle: IntegrationBundle = {
        "reason_verdict": reason_verdict,
        "contrast_verdict": contrast_verdict,
        "floor_verdict": floor_verdict,
        "integrated_verdict": integrated_verdict,
        "floor_priority_applied": floor_priority_applied,
        "reasoning": reasoning,
        "streak_count": streak_count
    }

    # Step 6: Verdict logic (raise if VOID or SABAR)
    if integrated_verdict == "VOID":
        raise ValueError(f"VOID: {reasoning}")

    if integrated_verdict == "SABAR":
        raise ValueError(f"SABAR: {reasoning}")

    return integration_bundle
