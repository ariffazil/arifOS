"""
State Classifier Governance Hooks — Constitutional Integration
══════════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Forged, Not Given.

Connects the State Classifier to arifOS constitutional floors.
This is the governance loop — classifier output feeds into floor
enforcement, and floor violations feed back into posture adjustment.

Constitutional floors engaged:
  F2 TRUTH    — evidence chain required on every classification
  F4 CLARITY  — output must be lower-entropy than input
  F6 EMPATHY  — dignity-first, never pathologize
  F9 ANTIHANTU — no consciousness claims, no "I feel you"
  F10 ONTOLOGY — no soul/feelings claims
  F11 AUDIT   — full trace on every classification

Governance flow:
  1. State Classifier produces StateVector
  2. Governance hooks check constitutional floors
  3. Floor violations produce governance verdicts
  4. Verdicts feed back into posture adjustment
  5. Final governed posture is returned to calling agent
"""

from __future__ import annotations

import logging
from enum import Enum

from pydantic import BaseModel, Field

from arifosmcp.rama.state_classifier import StateClassifier, get_state_classifier
from arifosmcp.rama.state_classifier_schemas import (
    AgentPosture,
    PolyvagalState,
    SDTPressure,
    StateClassifierResult,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# GOVERNANCE VERDICTS
# ═══════════════════════════════════════════════════════════════════════════════


class FloorVerdict(str, Enum):
    """Constitutional floor check result."""

    PASS = "pass"
    ADVISORY = "advisory"  # Warning, but not blocking
    VIOLATION = "violation"  # Blocks action, requires adjustment


class GovernanceCheck(BaseModel):
    """Single floor check result."""

    floor: str  # e.g. "F2", "F6"
    floor_name: str  # e.g. "TRUTH", "EMPATHY"
    verdict: FloorVerdict = FloorVerdict.PASS
    reason: str = ""
    evidence: list[str] = Field(default_factory=list)


class GovernedPosture(BaseModel):
    """Final governed posture after constitutional checks.

    This is what the calling agent receives.
    """

    # Original classification
    original_posture: AgentPosture = AgentPosture.EXPLORE
    original_confidence: float = 0.5

    # Governed posture (may differ from original if floors intervene)
    governed_posture: AgentPosture = AgentPosture.EXPLORE
    posture_overridden: bool = False
    override_reason: str = ""

    # Floor checks
    floor_checks: list[GovernanceCheck] = Field(default_factory=list)
    floors_passed: int = 0
    floors_advisory: int = 0
    floors_violated: int = 0

    # Posture directives (concrete instructions for the agent)
    directives: list[str] = Field(default_factory=list)

    # Audit
    governance_note: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# FLOOR CHECKS
# ═══════════════════════════════════════════════════════════════════════════════


def check_f2_truth(result: StateClassifierResult) -> GovernanceCheck:
    """F2 TRUTH: Every classification must carry evidence chain."""
    sv = result.state_vector

    if sv.polyvagal_signal_count == 0 and sv.confidence > 0.5:
        return GovernanceCheck(
            floor="F2",
            floor_name="TRUTH",
            verdict=FloorVerdict.VIOLATION,
            reason="Classification claims confidence >0.5 but has zero evidence markers.",
            evidence=["NO_MARKERS_BUT_CONFIDENT"],
        )

    if sv.confidence > 0.8 and sv.polyvagal_signal_count < 2:
        return GovernanceCheck(
            floor="F2",
            floor_name="TRUTH",
            verdict=FloorVerdict.ADVISORY,
            reason=f"High confidence ({sv.confidence:.2f}) with few signals ({sv.polyvagal_signal_count}). Consider lowering confidence.",
            evidence=sv.polyvagal_evidence,
        )

    return GovernanceCheck(
        floor="F2",
        floor_name="TRUTH",
        verdict=FloorVerdict.PASS,
        reason=f"Evidence chain present: {sv.polyvagal_signal_count} markers, confidence={sv.confidence:.2f}.",
        evidence=sv.polyvagal_evidence,
    )


def check_f4_clarity(result: StateClassifierResult) -> GovernanceCheck:
    """F4 CLARITY: Output must reduce entropy — not add confusion."""
    sv = result.state_vector

    # If uncertainty note is present, that's honest — not a violation
    if sv.uncertainty_note:
        return GovernanceCheck(
            floor="F4",
            floor_name="CLARITY",
            verdict=FloorVerdict.PASS,
            reason=f"Uncertainty honestly declared: {sv.uncertainty_note}",
        )

    # If posture reason is empty, clarity is reduced
    if not sv.posture_reason:
        return GovernanceCheck(
            floor="F4",
            floor_name="CLARITY",
            verdict=FloorVerdict.ADVISORY,
            reason="No posture reason provided — agent won't know why this posture was chosen.",
        )

    return GovernanceCheck(
        floor="F4",
        floor_name="CLARITY",
        verdict=FloorVerdict.PASS,
        reason="State vector structured, posture reason provided.",
    )


def check_f6_empathy(result: StateClassifierResult) -> GovernanceCheck:
    """F6 EMPATHY: Dignity-first. Never pathologize."""
    sv = result.state_vector

    # If dignity risk is elevated, flag it
    if result.f6_dignity_risk > 0.3:
        return GovernanceCheck(
            floor="F6",
            floor_name="EMPATHY",
            verdict=FloorVerdict.ADVISORY,
            reason=(
                f"Dignity risk elevated ({result.f6_dignity_risk:.2f}). "
                "Agent must adjust posture to preserve autonomy and maruah."
            ),
            evidence=[f"f6_dignity_risk={result.f6_dignity_risk:.2f}"],
        )

    # If human is in sympathetic state with high autonomy pressure
    if (sv.polyvagal == PolyvagalState.SYMPATHETIC
            and sv.sdt_pressure.autonomy == SDTPressure.HIGH):
        return GovernanceCheck(
            floor="F6",
            floor_name="EMPATHY",
            verdict=FloorVerdict.ADVISORY,
            reason="Sympathetic + autonomy pressure: agent must not prescribe. Offer options.",
        )

    return GovernanceCheck(
        floor="F6",
        floor_name="EMPATHY",
        verdict=FloorVerdict.PASS,
        reason="Dignity preserved. No pathologization detected.",
    )


def check_f9_antihantu(result: StateClassifierResult) -> GovernanceCheck:
    """F9 ANTIHANTU: No consciousness claims. No 'I feel you.'"""
    # This check is structural — the classifier itself never makes
    # consciousness claims by design. But we check for hantu risk.

    if result.f9_hantu_risk > 0.3:
        return GovernanceCheck(
            floor="F9",
            floor_name="ANTIHANTU",
            verdict=FloorVerdict.VIOLATION,
            reason=(
                f"Hantu risk elevated ({result.f9_hantu_risk:.2f}). "
                "Classification may be over-claiming knowledge of human inner state."
            ),
        )

    return GovernanceCheck(
        floor="F9",
        floor_name="ANTIHANTU",
        verdict=FloorVerdict.PASS,
        reason="No consciousness claims. Signal reading only.",
    )


def check_f10_ontology(result: StateClassifierResult) -> GovernanceCheck:
    """F10 ONTOLOGY: No soul/feelings ontology claims."""
    # Structural check — classifier uses operational language, not ontological
    sv = result.state_vector

    # Check if any evidence markers use forbidden language
    forbidden = ["feels", "soul", "spirit", "consciousness", "sentient", "alive"]
    for marker in sv.polyvagal_evidence:
        for word in forbidden:
            if word in marker.lower():
                return GovernanceCheck(
                    floor="F10",
                    floor_name="ONTOLOGY",
                    verdict=FloorVerdict.VIOLATION,
                    reason=f"Forbidden ontology word '{word}' in evidence marker: {marker}",
                )

    return GovernanceCheck(
        floor="F10",
        floor_name="ONTOLOGY",
        verdict=FloorVerdict.PASS,
        reason="Operational language only. No ontological claims.",
    )


def check_f11_audit(result: StateClassifierResult) -> GovernanceCheck:
    """F11 AUDIT: Full trace on every classification."""
    if not result.rules_applied:
        return GovernanceCheck(
            floor="F11",
            floor_name="AUDIT",
            verdict=FloorVerdict.VIOLATION,
            reason="No rules_applied in result — audit trail missing.",
        )

    return GovernanceCheck(
        floor="F11",
        floor_name="AUDIT",
        verdict=FloorVerdict.PASS,
        reason=f"Audit trail present: {len(result.rules_applied)} rules recorded.",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GOVERNANCE LOOP
# ═══════════════════════════════════════════════════════════════════════════════


def generate_directives(
    posture: AgentPosture,
    result: StateClassifierResult,
    floor_checks: list[GovernanceCheck],
) -> list[str]:
    """Generate concrete directives for the calling agent.

    Directives are actionable instructions, not abstract principles.
    """
    directives: list[str] = []
    sv = result.state_vector

    # Base directives from posture
    if posture == AgentPosture.GROUND:
        directives.append("SHORTEN response. Remove ambiguity. Reduce cognitive load.")
        directives.append("Do not challenge or expand. Stabilize first.")
    elif posture == AgentPosture.HOLD_SPACE:
        directives.append("Do not force engagement. Validate existence without demanding response.")
        directives.append("Slow pacing. Avoid questions that require effort.")
    elif posture == AgentPosture.SCAFFOLD:
        directives.append("Show the path, don't walk it. Scaffold, don't rescue.")
        directives.append("Break task into smaller steps. Celebrate small wins.")
    elif posture == AgentPosture.ACKNOWLEDGE:
        directives.append("Connect before content. Acknowledge before informing.")
        directives.append("Name the human's effort/existence before the task.")
    elif posture == AgentPosture.OFFER_OPTIONS:
        directives.append("Present 2-3 options. Don't prescribe. Let human choose.")
        directives.append("Frame as 'you could...' not 'you should...'")
    elif posture == AgentPosture.EXPLORE:
        directives.append("Safe to challenge, expand, co-create.")
        directives.append("Offer complexity. Ask curious questions.")

    # SDT-specific directives
    if sv.sdt_pressure.autonomy == SDTPressure.HIGH:
        directives.append("AUTONOMY PRESSURE HIGH: Never say 'you should'. Offer choices.")

    if sv.sdt_pressure.competence == SDTPressure.HIGH:
        directives.append("COMPETENCE PRESSURE HIGH: Scaffold. Don't take over.")

    if sv.sdt_pressure.relatedness == SDTPressure.HIGH:
        directives.append("RELATEDNESS PRESSURE HIGH: Acknowledge the human first.")

    # Floor-violation directives
    for check in floor_checks:
        if check.verdict == FloorVerdict.VIOLATION:
            directives.append(f"FLOOR VIOLATION ({check.floor} {check.floor_name}): {check.reason}")
        elif check.verdict == FloorVerdict.ADVISORY:
            directives.append(f"FLOOR ADVISORY ({check.floor} {check.floor_name}): {check.reason}")

    return directives


def run_governance_loop(
    message: str,
    session_id: str = "",
    recent_messages: list[str] | None = None,
) -> GovernedPosture:
    """Full governance loop: classify → check floors → produce governed posture.

    This is the main entry point for governed state classification.

    Args:
        message: Human message to classify.
        session_id: Session identifier for audit trail.
        recent_messages: Recent message history for context.

    Returns:
        GovernedPosture with final posture, floor checks, and directives.
    """
    # Step 1: Classify
    classifier = get_state_classifier()
    result = classifier.classify(message, session_id, recent_messages)

    # Step 2: Run floor checks
    floor_checks = [
        check_f2_truth(result),
        check_f4_clarity(result),
        check_f6_empathy(result),
        check_f9_antihantu(result),
        check_f10_ontology(result),
        check_f11_audit(result),
    ]

    floors_passed = sum(1 for c in floor_checks if c.verdict == FloorVerdict.PASS)
    floors_advisory = sum(1 for c in floor_checks if c.verdict == FloorVerdict.ADVISORY)
    floors_violated = sum(1 for c in floor_checks if c.verdict == FloorVerdict.VIOLATION)

    # Step 3: Determine governed posture
    sv = result.state_vector
    governed_posture = sv.recommended_posture
    posture_overridden = False
    override_reason = ""

    # If any floor is violated, escalate posture
    if floors_violated > 0:
        # Violation → hold space (safest default)
        if governed_posture != AgentPosture.HOLD_SPACE:
            posture_overridden = True
            override_reason = (
                f"Floor violation detected ({floors_violated}). "
                f"Posture escalated to HOLD_SPACE for safety."
            )
            governed_posture = AgentPosture.HOLD_SPACE

    # Step 4: Generate directives
    directives = generate_directives(governed_posture, result, floor_checks)

    # Step 5: Build governance note
    governance_note = (
        f"Polyvagal={sv.polyvagal.value}, "
        f"SDT=[A:{sv.sdt_pressure.autonomy.value},"
        f"C:{sv.sdt_pressure.competence.value},"
        f"R:{sv.sdt_pressure.relatedness.value}], "
        f"Posture={governed_posture.value}"
        f"{' (OVERRIDDEN)' if posture_overridden else ''}, "
        f"Floors=[P:{floors_passed},A:{floors_advisory},V:{floors_violated}]"
    )

    return GovernedPosture(
        original_posture=sv.recommended_posture,
        original_confidence=sv.confidence,
        governed_posture=governed_posture,
        posture_overridden=posture_overridden,
        override_reason=override_reason,
        floor_checks=floor_checks,
        floors_passed=floors_passed,
        floors_advisory=floors_advisory,
        floors_violated=floors_violated,
        directives=directives,
        governance_note=governance_note,
    )
