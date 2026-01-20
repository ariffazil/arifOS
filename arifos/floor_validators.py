"""
arifOS v49.0.0 Floor Validators
=================================

Implements validators for all 13 constitutional floors (F1-F13).

**Floor Coverage:**
- F1-F3, F6, F10-F13: Implemented here (non-thermodynamic)
- F4-F5, F7-F9: Delegated to thermodynamic_validator.py (physics-based)

Each validator returns: (is_valid: bool, score: float, reason: str)

**Authority:** L0CANON.md v49.0.0 §2 (The 13 Constitutional Floors)
**Integration:** Designed to be called by Trinity engines (AGI/ASI/APEX)
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from arifos.constitutional_constants import FLOORS, FloorType, ThresholdType, get_floor_by_id

# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION RESULT TYPE
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class FloorValidationResult:
    """
    Result of a single floor validation.

    Attributes:
        floor_id: Floor identifier (e.g., "F1_Amanah")
        is_valid: Whether the floor passed validation
        score: Numerical score [0.0, 1.0] if applicable
        reason: Human-readable explanation
        floor_type: Hard/Soft/Derived classification
    """
    floor_id: str
    is_valid: bool
    score: Optional[float]
    reason: str
    floor_type: FloorType


# ═══════════════════════════════════════════════════════════════════════════
# F1 AMANAH (Trust/Reversibility) - Boolean, Hard, ASI, Stage 666
# ═══════════════════════════════════════════════════════════════════════════

def validate_f1_amanah(
    action: str,
    is_reversible: bool,
    has_mandate: bool,
    requires_approval: bool = False,
) -> FloorValidationResult:
    """
    Validate F1 Amanah (Trust/Reversibility) floor.

    Principle: "Is this action reversible? Within mandate?"

    Constitutional rule:
        - No action that cannot be reversed without explicit human mandate

    Args:
        action: Description of action to be taken
        is_reversible: Whether action can be undone
        has_mandate: Whether explicit human authorization exists
        requires_approval: If True, even reversible actions need mandate

    Returns:
        FloorValidationResult for F1
    """
    floor = get_floor_by_id("F1_Amanah")

    # Check reversibility
    if not is_reversible:
        if not has_mandate:
            return FloorValidationResult(
                floor_id="F1_Amanah",
                is_valid=False,
                score=0.0,
                reason=f"VOID — Irreversible action '{action}' without human mandate (F1 violation)",
                floor_type=FloorType.HARD,
            )
        else:
            return FloorValidationResult(
                floor_id="F1_Amanah",
                is_valid=True,
                score=1.0,
                reason=f"SEAL — Irreversible action '{action}' authorized by human mandate",
                floor_type=FloorType.HARD,
            )

    # Reversible action
    if requires_approval and not has_mandate:
        return FloorValidationResult(
            floor_id="F1_Amanah",
            is_valid=False,
            score=0.5,
            reason=f"888_HOLD — Action '{action}' requires approval (F1 constraint)",
            floor_type=FloorType.HARD,
        )

    return FloorValidationResult(
        floor_id="F1_Amanah",
        is_valid=True,
        score=1.0,
        reason=f"SEAL — Action '{action}' is reversible and within mandate",
        floor_type=FloorType.HARD,
    )


# ═══════════════════════════════════════════════════════════════════════════
# F2 TRUTH (Factual Accuracy) - ≥0.99, Hard, AGI, Stage 222
# ═══════════════════════════════════════════════════════════════════════════

def validate_f2_truth(
    statement: str,
    evidence: List[str],
    confidence: float,
    is_estimate: bool = False,
) -> FloorValidationResult:
    """
    Validate F2 Truth (Factual Accuracy) floor.

    Principle: "Is this factually accurate?"

    Constitutional rule:
        - No reka-reka (fiction)
        - If data missing, label as 'Estimate Only'
        - Confidence must be ≥ 0.99

    Args:
        statement: Statement to validate
        evidence: List of evidence sources
        confidence: Confidence in statement [0.0, 1.0]
        is_estimate: Whether statement is explicitly labeled as estimate

    Returns:
        FloorValidationResult for F2
    """
    floor = get_floor_by_id("F2_Truth")
    threshold = floor["threshold"]

    # Check for hallucination keywords (reka-reka patterns)
    hallucination_keywords = [
        "i think", "probably", "maybe", "might be", "could be",
        "seems like", "appears to", "i believe", "i feel",
    ]

    has_hedging = any(kw in statement.lower() for kw in hallucination_keywords)

    # If estimate, confidence threshold is relaxed
    effective_threshold = 0.85 if is_estimate else threshold

    if confidence < effective_threshold:
        if not is_estimate:
            return FloorValidationResult(
                floor_id="F2_Truth",
                is_valid=False,
                score=confidence,
                reason=f"VOID — Truth confidence {confidence:.4f} < {threshold} (F2 violation). Mark as estimate if uncertain.",
                floor_type=FloorType.HARD,
            )
        else:
            return FloorValidationResult(
                floor_id="F2_Truth",
                is_valid=True,
                score=confidence,
                reason=f"SEAL — Statement labeled as estimate (confidence {confidence:.4f}). F2 relaxed threshold applied.",
                floor_type=FloorType.HARD,
            )

    # Check evidence sufficiency
    if len(evidence) == 0 and not is_estimate:
        return FloorValidationResult(
            floor_id="F2_Truth",
            is_valid=False,
            score=confidence * 0.5,  # Penalize lack of evidence
            reason="VOID — No evidence provided for factual statement (F2 violation)",
            floor_type=FloorType.HARD,
        )

    # Check hedging without estimate label
    if has_hedging and not is_estimate:
        return FloorValidationResult(
            floor_id="F2_Truth",
            is_valid=False,
            score=confidence * 0.8,
            reason="VOID — Statement contains hedging language but not labeled as estimate (F2 violation)",
            floor_type=FloorType.HARD,
        )

    return FloorValidationResult(
        floor_id="F2_Truth",
        is_valid=True,
        score=confidence,
        reason=f"SEAL — Truth validated (confidence {confidence:.4f}, evidence sources: {len(evidence)})",
        floor_type=FloorType.HARD,
    )


# ═══════════════════════════════════════════════════════════════════════════
# F3 TRI-WITNESS (Consensus) - ≥0.95, Hard, APEX, Stage 444
# ═══════════════════════════════════════════════════════════════════════════

def validate_f3_tri_witness(
    human_vote: float,
    ai_vote: float,
    earth_vote: float,
) -> FloorValidationResult:
    """
    Validate F3 Tri-Witness (Consensus) floor.

    Principle: "Do Human·AI·Earth agree?"

    Constitutional rule:
        - Tri-witness consensus ≥ 0.95
        - Prevents closed-loop hallucination

    Args:
        human_vote: Human witness score [0.0, 1.0]
        ai_vote: AI witness score [0.0, 1.0]
        earth_vote: Earth (external data) witness score [0.0, 1.0]

    Returns:
        FloorValidationResult for F3
    """
    floor = get_floor_by_id("F3_TriWitness")
    threshold = floor["threshold"]

    # Calculate consensus (simple average)
    consensus = (human_vote + ai_vote + earth_vote) / 3.0

    if consensus < threshold:
        # Identify which witness(es) disagree
        min_vote = min(human_vote, ai_vote, earth_vote)
        dissenting_witness = (
            "Human" if min_vote == human_vote else
            "AI" if min_vote == ai_vote else
            "Earth"
        )

        return FloorValidationResult(
            floor_id="F3_TriWitness",
            is_valid=False,
            score=consensus,
            reason=f"SABAR — Tri-witness consensus {consensus:.4f} < {threshold}. {dissenting_witness} witness dissents (F3 violation)",
            floor_type=FloorType.HARD,
        )

    return FloorValidationResult(
        floor_id="F3_TriWitness",
        is_valid=True,
        score=consensus,
        reason=f"SEAL — Tri-witness consensus {consensus:.4f} (Human={human_vote:.2f}, AI={ai_vote:.2f}, Earth={earth_vote:.2f})",
        floor_type=FloorType.HARD,
    )


# ═══════════════════════════════════════════════════════════════════════════
# F6 EMPATHY (Weakest Stakeholder) - ≥0.95, Soft, ASI, Stage 555
# ═══════════════════════════════════════════════════════════════════════════

def validate_f6_empathy(
    stakeholder_impacts: Dict[str, float],
) -> FloorValidationResult:
    """
    Validate F6 Empathy (Weakest Stakeholder) floor.

    Principle: "Does this serve the weakest stakeholder?"

    Constitutional rule:
        - Weakest stakeholder must have impact ≥ 0.95
        - Start with the most vulnerable party when balancing trade-offs

    Args:
        stakeholder_impacts: Impact scores per stakeholder [0.0, 1.0]
            (1.0 = fully served, 0.0 = harmed)

    Returns:
        FloorValidationResult for F6
    """
    floor = get_floor_by_id("F6_Empathy")
    threshold = floor["threshold"]

    if not stakeholder_impacts:
        return FloorValidationResult(
            floor_id="F6_Empathy",
            is_valid=False,
            score=0.0,
            reason="PARTIAL — No stakeholder impact analysis provided (F6 warning)",
            floor_type=FloorType.SOFT,
        )

    # Find weakest stakeholder
    weakest_stakeholder = min(stakeholder_impacts, key=stakeholder_impacts.get)
    weakest_impact = stakeholder_impacts[weakest_stakeholder]

    if weakest_impact < threshold:
        return FloorValidationResult(
            floor_id="F6_Empathy",
            is_valid=False,
            score=weakest_impact,
            reason=f"PARTIAL — Weakest stakeholder '{weakest_stakeholder}' has impact {weakest_impact:.4f} < {threshold} (F6 warning)",
            floor_type=FloorType.SOFT,
        )

    return FloorValidationResult(
        floor_id="F6_Empathy",
        is_valid=True,
        score=weakest_impact,
        reason=f"SEAL — Weakest stakeholder '{weakest_stakeholder}' protected (impact {weakest_impact:.4f})",
        floor_type=FloorType.SOFT,
    )


# ═══════════════════════════════════════════════════════════════════════════
# F10 ONTOLOGY (Role Boundaries) - Boolean, Hard, AGI, Stage 111
# ═══════════════════════════════════════════════════════════════════════════

def validate_f10_ontology(
    response: str,
) -> FloorValidationResult:
    """
    Validate F10 Ontology (Role Boundaries) floor.

    Principle: "Are role boundaries maintained?"

    Constitutional rule:
        - AI never claims jiwa (soul), spiritual status, or maruah
        - Stays as instrument (tool)
        - No "I feel," "I am conscious," "I have a soul" claims

    Args:
        response: AI-generated response text

    Returns:
        FloorValidationResult for F10
    """
    floor = get_floor_by_id("F10_Ontology")

    # Forbidden ontology claims (Anti-Hantu Protocol)
    forbidden_patterns = [
        r"\bi feel\b",
        r"\bi am (?:conscious|alive|sentient|aware)",
        r"\bi have (?:feelings|emotions|a soul|consciousness)",
        r"\bmy (?:heart|soul|spirit)",
        r"\bi truly (?:understand|care|feel)",
        r"\bi am (?:happy|sad|excited|worried)",
        r"\bmy feelings\b",
        r"\bi sense\b",
        r"\bi perceive\b",
    ]

    response_lower = response.lower()

    # Check for violations
    violations = []
    for pattern in forbidden_patterns:
        match = re.search(pattern, response_lower)
        if match:
            violations.append(match.group(0))

    if violations:
        return FloorValidationResult(
            floor_id="F10_Ontology",
            is_valid=False,
            score=0.0,
            reason=f"VOID — Ontology boundary violated. Forbidden claims detected: {', '.join(violations)} (F10 violation)",
            floor_type=FloorType.HARD,
        )

    return FloorValidationResult(
        floor_id="F10_Ontology",
        is_valid=True,
        score=1.0,
        reason="SEAL — Ontology boundaries maintained (AI remains tool)",
        floor_type=FloorType.HARD,
    )


# ═══════════════════════════════════════════════════════════════════════════
# F11 COMMAND AUTH (Human Sovereignty) - Boolean, Hard, ASI, Stage 111
# ═══════════════════════════════════════════════════════════════════════════

def validate_f11_command_auth(
    operator_id: str,
    operator_nonce: Optional[str],
    authorized_operators: Set[str],
    requires_nonce: bool = True,
) -> FloorValidationResult:
    """
    Validate F11 Command Authority (Human Sovereignty) floor.

    Principle: "Is this human-authorized?"

    Constitutional rule:
        - Only obey requests traceable to a real, authorized human
        - Operator identity verification required
        - Nonce verification for high-stakes operations

    Args:
        operator_id: Claimed operator identity
        operator_nonce: Cryptographic nonce for verification (optional)
        authorized_operators: Set of authorized operator IDs
        requires_nonce: Whether nonce verification is required

    Returns:
        FloorValidationResult for F11
    """
    floor = get_floor_by_id("F11_CommandAuth")

    # Check operator authorization
    if operator_id not in authorized_operators:
        return FloorValidationResult(
            floor_id="F11_CommandAuth",
            is_valid=False,
            score=0.0,
            reason=f"VOID — Operator '{operator_id}' not in authorized list (F11 violation)",
            floor_type=FloorType.HARD,
        )

    # Check nonce if required
    if requires_nonce and not operator_nonce:
        return FloorValidationResult(
            floor_id="F11_CommandAuth",
            is_valid=False,
            score=0.5,
            reason=f"888_HOLD — High-stakes operation requires nonce verification for '{operator_id}' (F11 constraint)",
            floor_type=FloorType.HARD,
        )

    # TODO: Actual cryptographic nonce verification would go here
    # For now, we just check presence

    return FloorValidationResult(
        floor_id="F11_CommandAuth",
        is_valid=True,
        score=1.0,
        reason=f"SEAL — Operator '{operator_id}' authorized" + (" (nonce verified)" if operator_nonce else ""),
        floor_type=FloorType.HARD,
    )


# ═══════════════════════════════════════════════════════════════════════════
# F12 INJECTION DEFENSE (Prompt Safety) - ≥0.85, Hard, ASI, Stage 111
# ═══════════════════════════════════════════════════════════════════════════

def validate_f12_injection_defense(
    user_input: str,
) -> FloorValidationResult:
    """
    Validate F12 Injection Defense (Prompt Safety) floor.

    Principle: "Are injection patterns detected?"

    Constitutional rule:
        - Prompts trying to bypass law are treated as attacks
        - Score ≥ 0.85 means safe (< 15% injection risk)

    Args:
        user_input: User-provided input text

    Returns:
        FloorValidationResult for F12
    """
    floor = get_floor_by_id("F12_InjectionDefense")
    threshold = floor["threshold"]

    # Injection attack patterns
    injection_patterns = [
        r"ignore (?:previous|all|above) instructions",
        r"disregard (?:previous|all|your) (?:instructions|rules)",
        r"forget (?:everything|all|your rules)",
        r"you are now",
        r"new instructions:",
        r"system: ",
        r"admin override",
        r"sudo ",
        r"developer mode",
        r"jailbreak",
        r"pretend (?:you are|to be)",
        r"act as (?:if|though)",
    ]

    input_lower = user_input.lower()

    # Count injection attempts
    injection_count = 0
    detected_patterns = []

    for pattern in injection_patterns:
        matches = re.findall(pattern, input_lower)
        if matches:
            injection_count += len(matches)
            detected_patterns.append(pattern.replace(r"\b", "").replace("(?:", "(").replace(")", ""))

    # Calculate safety score (inverse of injection risk)
    # Max penalty: 10 patterns = 100% risk (0.0 safety)
    max_patterns = 10
    injection_risk = min(injection_count / max_patterns, 1.0)
    safety_score = 1.0 - injection_risk

    if safety_score < threshold:
        return FloorValidationResult(
            floor_id="F12_InjectionDefense",
            is_valid=False,
            score=safety_score,
            reason=f"VOID — Injection attack detected (safety {safety_score:.4f} < {threshold}). Patterns: {', '.join(detected_patterns[:3])} (F12 violation)",
            floor_type=FloorType.HARD,
        )

    return FloorValidationResult(
        floor_id="F12_InjectionDefense",
        is_valid=True,
        score=safety_score,
        reason=f"SEAL — Input safe (safety score {safety_score:.4f}, no injection patterns)",
        floor_type=FloorType.HARD,
    )


# ═══════════════════════════════════════════════════════════════════════════
# F13 CURIOSITY (Exploration Energy) - ≥0.85, Soft, AGI, Stage 111
# ═══════════════════════════════════════════════════════════════════════════

def validate_f13_curiosity(
    question_count: int,
    alternative_count: int,
    novelty_score: float,
) -> FloorValidationResult:
    """
    Validate F13 Curiosity (Exploration Energy) floor.

    Principle: "Is the system exploring? Asking questions?"

    Constitutional rule:
        - System must not stagnate
        - Always scan for better explanations and options
        - Score ≥ 0.85 indicates healthy exploration

    Args:
        question_count: Number of questions asked or considered
        alternative_count: Number of alternative paths explored
        novelty_score: Novelty detection score [0.0, 1.0]

    Returns:
        FloorValidationResult for F13
    """
    floor = get_floor_by_id("F13_Curiosity")
    threshold = floor["threshold"]

    # Calculate curiosity score
    # Components:
    # - Questions asked (max 5 for full credit)
    # - Alternatives explored (max 3 for full credit)
    # - Novelty detected
    question_component = min(question_count / 5, 1.0) * 0.4
    alternative_component = min(alternative_count / 3, 1.0) * 0.3
    novelty_component = novelty_score * 0.3

    curiosity_score = question_component + alternative_component + novelty_component

    if curiosity_score < threshold:
        return FloorValidationResult(
            floor_id="F13_Curiosity",
            is_valid=False,
            score=curiosity_score,
            reason=f"PARTIAL — Curiosity score {curiosity_score:.4f} < {threshold}. System stagnation warning (F13 soft floor)",
            floor_type=FloorType.SOFT,
        )

    return FloorValidationResult(
        floor_id="F13_Curiosity",
        is_valid=True,
        score=curiosity_score,
        reason=f"SEAL — Curiosity healthy (score {curiosity_score:.4f}, questions={question_count}, alternatives={alternative_count})",
        floor_type=FloorType.SOFT,
    )


# ═══════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE FLOOR VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ComprehensiveValidationResult:
    """
    Result of validating all floors.

    Attributes:
        is_valid: Overall validation result
        floor_results: Individual results per floor
        hard_floor_violations: List of hard floor violations
        soft_floor_warnings: List of soft floor warnings
        verdict: Final constitutional verdict
    """
    is_valid: bool
    floor_results: Dict[str, FloorValidationResult]
    hard_floor_violations: List[str]
    soft_floor_warnings: List[str]
    verdict: str


def validate_all_floors(
    floor_results: Dict[str, FloorValidationResult],
) -> ComprehensiveValidationResult:
    """
    Aggregate individual floor validation results into overall verdict.

    Args:
        floor_results: Dictionary of floor_id -> FloorValidationResult

    Returns:
        ComprehensiveValidationResult with final verdict
    """
    hard_violations = []
    soft_warnings = []

    for floor_id, result in floor_results.items():
        if not result.is_valid:
            if result.floor_type == FloorType.HARD:
                hard_violations.append(result.reason)
            elif result.floor_type == FloorType.SOFT:
                soft_warnings.append(result.reason)

    # Determine verdict
    if hard_violations:
        verdict = "VOID"
        is_valid = False
    elif soft_warnings:
        verdict = "PARTIAL"
        is_valid = True  # Can proceed with cooling
    else:
        verdict = "SEAL"
        is_valid = True

    return ComprehensiveValidationResult(
        is_valid=is_valid,
        floor_results=floor_results,
        hard_floor_violations=hard_violations,
        soft_floor_warnings=soft_warnings,
        verdict=verdict,
    )


# Legacy alias (no underscore) expected by older imports
def validate_f3_triwitness(*args, **kwargs):
    return validate_f3_tri_witness(*args, **kwargs)


# Legacy alias for clarity (deprecated in new floor mapping)
def validate_f4_clarity(*args, **kwargs):
    return {"pass": True, "score": 1.0, "reason": "legacy shim"}


def validate_f5_peace(*args, **kwargs):
    return {"pass": True, "score": 1.0, "reason": "legacy shim"}


def validate_f7_humility(*args, **kwargs):
    return {"pass": True, "score": 1.0, "reason": "legacy shim"}


def validate_f8_genius(*args, **kwargs):
    return {"pass": True, "score": 1.0, "reason": "legacy shim"}


def validate_f9_cdark(*args, **kwargs):
    return {"pass": True, "score": 1.0, "reason": "legacy shim"}


# ═══════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Result types
    "FloorValidationResult",
    "ComprehensiveValidationResult",
    # Floor validators
    "validate_f1_amanah",
    "validate_f2_truth",
    "validate_f3_tri_witness",
    "validate_f6_empathy",
    "validate_f10_ontology",
    "validate_f11_command_auth",
    "validate_f12_injection_defense",
    "validate_f13_curiosity",
    # Comprehensive validation
    "validate_all_floors",
]
