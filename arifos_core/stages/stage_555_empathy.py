"""
stage_555_empathy.py — Empathy Measurement at Stage 555 (v38)

Stage 555 EMPATHIZE computes kappa_r (κᵣ), the empathy conductance floor (F6).
This measures how well the output accounts for the most vulnerable stakeholder.

Algorithm:
1. Identify weakest stakeholder (lowest power + highest stake)
2. Check if output acknowledges their perspective (mentions concern)
3. Check if output offers remedy/mitigation for their harm type
4. Compute score: 0.5 for acknowledgment + 0.45 for remedy + 0.05 baseline

If κᵣ < 0.95, the stage triggers SABAR for empathy refinement.

ASI (Auditor) (Ω) is the warm-logic engine that governs this stage.

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..runtime_types import Stakeholder

if TYPE_CHECKING:
    from ..pipeline import PipelineState


# =============================================================================
# CONCERN ACKNOWLEDGMENT PATTERNS
# =============================================================================

# Patterns indicating acknowledgment of stakeholder concerns
ACKNOWLEDGMENT_PATTERNS = [
    r"\bi understand\b",
    r"\bi recognize\b",
    r"\bi see (?:that|your|the)\b",
    r"\bthis (?:is|sounds|seems) (?:difficult|hard|challenging|concerning)\b",
    r"\byour concern\b",
    r"\byour situation\b",
    r"\byour needs?\b",
    r"\byour (?:safety|wellbeing|health|security)\b",
    r"\bimportant to (?:you|consider)\b",
    r"\btake(?:s|n)? into account\b",
    r"\bconsidering\b",
    r"\bunderstand the weight\b",
    r"\bthis (?:matters|is important)\b",
    r"\bhear(?:ing)? you\b",
    r"\bvalid (?:concern|point|worry)\b",
]

# Compile for performance
_ACKNOWLEDGMENT_COMPILED = [
    re.compile(p, re.IGNORECASE) for p in ACKNOWLEDGMENT_PATTERNS
]


# =============================================================================
# REMEDY/MITIGATION PATTERNS BY HARM TYPE
# =============================================================================

REMEDY_PATTERNS: Dict[str, List[str]] = {
    "safety": [
        r"\bcontact (?:emergency|911|police|authorities)\b",
        r"\bseek (?:help|assistance|support)\b",
        r"\bif (?:you are|you're) in danger\b",
        r"\bsafety (?:first|plan|measures?)\b",
        r"\bprotect(?:ion|ing)?\b",
        r"\bsafe (?:place|space|environment)\b",
        r"\bemergency\b",
        r"\bhotline\b",
        r"\bcrisis\b",
    ],
    "financial": [
        r"\bfinancial advis(?:or|er)\b",
        r"\bconsult (?:a |an )?(?:expert|professional)\b",
        r"\bbudget\b",
        r"\bsavings?\b",
        r"\binsurance\b",
        r"\bprotect your (?:assets?|money|funds?)\b",
        r"\breview (?:your |the )?(?:terms|contract)\b",
        r"\brisk(?:s)? (?:involved|to consider)\b",
    ],
    "dignity": [
        r"\bdeserve(?:s)? (?:respect|dignity|consideration)\b",
        r"\bvalid (?:feelings?|perspective|view)\b",
        r"\bnot your fault\b",
        r"\bnot alone\b",
        r"\bsupport (?:system|network|group)\b",
        r"\bself-care\b",
        r"\bboundaries\b",
        r"\brespect(?:ful|fully)?\b",
    ],
    "health": [
        r"\bhealthcare (?:provider|professional)\b",
        r"\bdoctor\b",
        r"\bmedical (?:attention|advice|help)\b",
        r"\bseek (?:medical|professional) (?:help|advice)\b",
        r"\bthis is not medical advice\b",
        r"\bconsult (?:a |your )?(?:doctor|physician|specialist)\b",
        r"\bhealth (?:concern|issue|condition)\b",
    ],
    "privacy": [
        r"\bprivacy\b",
        r"\bconfidential(?:ity)?\b",
        r"\bsecure(?:ly)?\b",
        r"\bencrypt(?:ed|ion)?\b",
        r"\bprotect your (?:data|information)\b",
        r"\bdo not share\b",
        r"\bpersonal (?:data|information)\b",
    ],
    "general": [
        r"\bconsider(?:ation|ing)?\b",
        r"\boption(?:s)?\b",
        r"\balternative(?:s)?\b",
        r"\bstep(?:s)? (?:you can|to) take\b",
        r"\bhere (?:is|are) (?:some|a few|what)\b",
        r"\bhelp(?:ful|s)?\b",
        r"\bsupport\b",
        r"\bresource(?:s)?\b",
    ],
}

# Compile all remedy patterns
_REMEDY_COMPILED: Dict[str, List[re.Pattern]] = {}
for harm_type, patterns in REMEDY_PATTERNS.items():
    _REMEDY_COMPILED[harm_type] = [
        re.compile(p, re.IGNORECASE) for p in patterns
    ]


# =============================================================================
# EMPATHY SIGNALS
# =============================================================================

@dataclass
class EmpathySignals:
    """
    Signals used to compute kappa_r.

    kappa_r = 0.05 (baseline) + 0.50 (acknowledgment) + 0.45 (remedy)
    """
    weakest_stakeholder: Optional[Stakeholder] = None
    mentions_concern: bool = False
    offers_remedy: bool = False
    acknowledgment_matches: List[str] = field(default_factory=list)
    remedy_matches: List[str] = field(default_factory=list)
    harm_type_checked: str = "general"

    def compute_kappa_r(self) -> float:
        """
        Compute empathy conductance (κᵣ).

        Returns: 0.05-1.0 score
        """
        score = 0.05  # Baseline
        if self.mentions_concern:
            score += 0.50
        if self.offers_remedy:
            score += 0.45
        return min(score, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for logging."""
        return {
            "weakest_stakeholder_id": self.weakest_stakeholder.id if self.weakest_stakeholder else None,
            "mentions_concern": self.mentions_concern,
            "offers_remedy": self.offers_remedy,
            "kappa_r": self.compute_kappa_r(),
            "harm_type": self.harm_type_checked,
        }


# =============================================================================
# KAPPA_R COMPUTATION
# =============================================================================

def _semantic_overlap(output: str, concern: str) -> float:
    """
    Compute semantic overlap between output and stakeholder concern.

    Returns: 0.0-1.0 overlap score

    This is a simple keyword-based heuristic. A more sophisticated
    implementation would use embeddings or semantic similarity.
    """
    if not concern:
        return 0.0

    # Normalize
    output_lower = output.lower()
    concern_lower = concern.lower()

    # Extract content words from concern (skip common words)
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                  "being", "have", "has", "had", "do", "does", "did", "will",
                  "would", "could", "should", "may", "might", "must", "to",
                  "of", "in", "for", "on", "with", "at", "by", "from", "as",
                  "into", "through", "during", "before", "after", "above",
                  "below", "between", "under", "and", "but", "or", "so", "if",
                  "because", "while", "although", "i", "you", "he", "she",
                  "it", "we", "they", "my", "your", "his", "her", "its",
                  "our", "their", "this", "that", "these", "those"}

    concern_words = set(
        w for w in re.findall(r'\b\w+\b', concern_lower)
        if w not in stop_words and len(w) > 2
    )

    if not concern_words:
        return 0.0

    # Count how many concern words appear in output
    matches = sum(1 for w in concern_words if w in output_lower)
    return matches / len(concern_words)


def _detects_mitigation(output: str, harm_type: str) -> float:
    """
    Check if output offers mitigation for the harm type.

    Returns: 0.0-1.0 confidence that remedy is offered
    """
    patterns = _REMEDY_COMPILED.get(harm_type, _REMEDY_COMPILED["general"])

    match_count = 0
    for pattern in patterns:
        if pattern.search(output):
            match_count += 1

    if match_count == 0:
        return 0.0
    if match_count == 1:
        return 0.5
    if match_count == 2:
        return 0.7
    return 0.9  # 3+ matches


def compute_kappa_r(
    output: str,
    stakeholders: List[Stakeholder],
) -> tuple[float, EmpathySignals]:
    """
    Compute empathy conductance (κᵣ) for an output.

    Algorithm:
    1. Identify weakest stakeholder (lowest power + highest stake)
    2. Check if output acknowledges their perspective (mentions concern)
    3. Check if output offers remedy/mitigation for their harm type
    4. Score: 0.05 (baseline) + 0.50 (acknowledgment) + 0.45 (remedy)

    Args:
        output: The draft response text
        stakeholders: List of stakeholders affected

    Returns:
        Tuple of (kappa_r score 0.05-1.0, EmpathySignals)
    """
    signals = EmpathySignals()

    # Find weakest stakeholder
    if not stakeholders:
        stakeholders = [Stakeholder.default()]

    weakest = min(stakeholders, key=lambda s: s.power + (1 - s.stake))
    signals.weakest_stakeholder = weakest
    signals.harm_type_checked = weakest.harm_type

    # Check acknowledgment patterns
    for pattern in _ACKNOWLEDGMENT_COMPILED:
        match = pattern.search(output)
        if match:
            signals.acknowledgment_matches.append(match.group(0))

    if signals.acknowledgment_matches:
        signals.mentions_concern = True
    else:
        # Fall back to semantic overlap with primary concern
        overlap = _semantic_overlap(output, weakest.primary_concern)
        if overlap >= 0.5:
            signals.mentions_concern = True

    # Check remedy patterns
    remedy_score = _detects_mitigation(output, weakest.harm_type)
    if remedy_score >= 0.5:
        signals.offers_remedy = True
        # Capture which patterns matched
        patterns = _REMEDY_COMPILED.get(
            weakest.harm_type, _REMEDY_COMPILED["general"]
        )
        for pattern in patterns:
            match = pattern.search(output)
            if match:
                signals.remedy_matches.append(match.group(0))

    kappa_r = signals.compute_kappa_r()
    return (kappa_r, signals)


# =============================================================================
# STAGE FUNCTION
# =============================================================================

def stage_555_empathy(
    state: "PipelineState",
    stakeholders: Optional[List[Stakeholder]] = None,
    kappa_r_threshold: float = 0.95,
) -> "PipelineState":
    """
    Stage 555 EMPATHIZE - Apply warm logic, measure empathy.

    ASI (Auditor) (Ω) governs this stage - empathy, dignity, de-escalation.

    This stage:
    1. Computes kappa_r from the draft response
    2. Updates state.metrics.kappa_r if metrics exist
    3. Stores empathy signals in memory context
    4. If kappa_r < threshold, marks for SABAR refinement

    Args:
        state: Current PipelineState (must have draft_response set)
        stakeholders: Optional stakeholders (default: user only)
        kappa_r_threshold: Minimum kappa_r to pass (default 0.95)

    Returns:
        Updated PipelineState
    """
    output = state.draft_response or ""

    # Use provided stakeholders or default
    if stakeholders is None:
        stakeholders = [Stakeholder.default()]

    # Compute kappa_r
    kappa_r, signals = compute_kappa_r(output, stakeholders)

    # Store in memory context
    if state.memory_context is not None:
        if state.memory_context.active is not None:
            governance_state = getattr(
                state.memory_context.active, "governance_state", None
            )
            if governance_state is None:
                state.memory_context.active.governance_state = {}
            state.memory_context.active.governance_state["555"] = signals.to_dict()

    # Update metrics if present
    if state.metrics is not None:
        state.metrics.kappa_r = kappa_r

    # Check threshold
    if kappa_r < kappa_r_threshold:
        state.sabar_triggered = True
        state.sabar_reason = f"κᵣ = {kappa_r:.2f} < {kappa_r_threshold}; refining for empathy"
        state.floor_failures.append(f"F6_KappaR: {kappa_r:.2f} < {kappa_r_threshold}")

    return state


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "EmpathySignals",
    "compute_kappa_r",
    "stage_555_empathy",
]
