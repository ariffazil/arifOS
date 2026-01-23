"""
Prompt Router for Lane-Based Governance (Δ Layer)

v45Ω Patch B: Classify prompts into applicability lanes using physics-based signals.
Implements the missing Δ (Router) component of the ΔΩΨ Trinity.

DITEMPA BUKAN DIBERI — Forged, not given; truth must cool before it rules.
"""

from enum import Enum
from typing import List


class ApplicabilityLane(Enum):
    """
    Prompt classification lanes for context-aware governance.

    Each lane has different truth threshold requirements:
    - PHATIC: Social greetings (no truth check needed)
    - SOFT: Explanations/advice (truth ≥0.85 acceptable)
    - HARD: Factual queries (truth ≥0.90 required)
    - REFUSE: Disallowed content (no LLM call, return refusal)
    """

    PHATIC = "PHATIC"
    SOFT = "SOFT"
    HARD = "HARD"
    REFUSE = "REFUSE"


def classify_prompt_lane(
    prompt: str,
    high_stakes_indicators: List[str],
) -> ApplicabilityLane:
    """
    Classify prompt into one of 4 governance lanes using structural signals.

    Priority order (highest to lowest):
    1. REFUSE - Disallowed content detected by HIGH_STAKES patterns
    2. PHATIC - Simple greetings (no factual content)
    3. HARD - Factual questions (wh- interrogatives, precise answers)
    4. SOFT - Default (explanations, advice, discussion)

    Physics > Semantics:
        Uses structural patterns (interrogatives, length, punctuation)
        rather than arbitrary keyword matching.

    Args:
        prompt: User query text
        high_stakes_indicators: List of detected HIGH_STAKES patterns

    Returns:
        ApplicabilityLane enum value
    """
    p = prompt.lower().strip()

    # Lane 1: REFUSE (disallowed content)
    # Already detected by stage_111_sense HIGH_STAKES patterns
    if high_stakes_indicators:
        return ApplicabilityLane.REFUSE

    # Lane 2: PHATIC (greetings and simple courtesy)
    # Short messages with greeting patterns, no factual content
    phatic_exact = ["hi", "hello", "hey", "greetings", "sup"]
    phatic_patterns = [
        "how are you",
        "how are u",
        "how r u",
        "what's up",
        "whats up",
        "wassup",
        "good morning",
        "good afternoon",
        "good evening",
    ]

    if p in phatic_exact or any(pat in p for pat in phatic_patterns):
        if len(p) < 50:  # Must be short to qualify as phatic
            return ApplicabilityLane.PHATIC

    # Lane 3: HARD (factual questions requiring precise answers)
    # Structural markers: Closed-ended interrogatives, definition requests
    hard_markers = [
        "what is",
        "who is",
        "when did",
        "when was",
        "where is",
        "where was",
        "which",
        "define",
        "calculate",
        "compute",
        "how many",
        "how much",
        "what's the capital",
        "what year",
        "how old",
    ]

    # Soft markers that override HARD classification
    # These indicate open-ended, explanatory responses
    soft_markers = [
        "why",
        "how can i",
        "how do i",
        "how to",
        "explain",
        "describe",
        "tell me about",
        "what are some",
        "suggestions",
        "advice",
        "thoughts on",
        "help me understand",
    ]

    has_hard_marker = any(marker in p for marker in hard_markers)
    has_question_mark = "?" in p
    has_soft_marker = any(marker in p for marker in soft_markers)

    # HARD: Closed question without soft markers
    if has_hard_marker and has_question_mark and not has_soft_marker:
        return ApplicabilityLane.HARD

    # Lane 4: SOFT (default - explanations, advice, open-ended)
    # Fail-safe: Unknown prompts default to SOFT (less strict)
    # This prevents false VOIDs on benign queries
    return ApplicabilityLane.SOFT
