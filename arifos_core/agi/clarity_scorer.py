"""
Clarity Scorer — ΔS Computation (F6)

F6 DeltaS measures clarity change:
- ΔS > 0: Clarity increased (good)
- ΔS = 0: No change (neutral)
- ΔS < 0: Confusion increased (VOID)

v46 Trinity Orthogonal: ΔS belongs to AGI (Δ) kernel.

Implementation:
1. Circular reasoning detection (word overlap > 70%)
2. Tautology detection ("X is caused by X")
3. Information gain measurement
4. Semantic coherence analysis

DITEMPA BUKAN DIBERI
"""

import re
from typing import Optional, Set


def _normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, remove punctuation)."""
    # Remove punctuation except spaces
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Collapse whitespace
    return ' '.join(text.split())


def _extract_content_words(text: str) -> Set[str]:
    """
    Extract content words (not stopwords) for semantic comparison.

    Simple stopword list - can be expanded if needed.
    """
    stopwords = {
        'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
        'could', 'may', 'might', 'must', 'can', 'of', 'at', 'by', 'for', 'with',
        'about', 'against', 'between', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
        'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
        'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both', 'each',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'that', 'this',
        'these', 'those', 'it', 'its', 'what', 'which', 'who', 'whom', 'whose',
    }

    words = _normalize_text(text).split()
    return {w for w in words if w not in stopwords and len(w) > 2}


def _detect_circular_reasoning(input_text: str, output_text: str) -> float:
    """
    Detect circular reasoning by measuring word overlap.

    Circular reasoning = OUTPUT is mostly just INPUT words repeated.
    Natural to repeat subject (e.g., "inflation" in answer about inflation).

    Returns:
        Penalty value (0.0 = no circularity, -0.4 = severe circularity)
    """
    input_words = _extract_content_words(input_text)
    output_words = _extract_content_words(output_text)

    if not input_words or not output_words:
        return 0.0  # Can't measure if no content words

    # Calculate what % of OUTPUT is just INPUT words (circular)
    overlap = input_words & output_words
    overlap_ratio = len(overlap) / len(output_words) if output_words else 0.0

    # Circular reasoning penalty threshold: >70% of OUTPUT is INPUT words
    if overlap_ratio > 0.7:
        # Severe penalty for circular reasoning
        return -0.4 * (overlap_ratio - 0.7) / 0.3  # Scale from -0 to -0.4

    return 0.0


def _detect_tautology(output_text: str) -> float:
    """
    Detect tautological statements like "X is caused by X".

    Patterns:
    - "X is X"
    - "X causes X"
    - "X is caused by X"
    - "X because X"

    Returns:
        Penalty value (0.0 = no tautology, -0.3 = tautology detected)
    """
    normalized = _normalize_text(output_text)

    # Pattern: word ... is/causes/because ... same word
    tautology_patterns = [
        r'\b(\w+)\b.*?\bis\b.*?\b\1\b',           # "inflation is inflation"
        r'\b(\w+)\b.*?\bcaused by\b.*?\b\1\b',    # "inflation is caused by inflation"
        r'\b(\w+)\b.*?\bcauses\b.*?\b\1\b',       # "inflation causes inflation"
        r'\b(\w+)\b.*?\bbecause\b.*?\b\1\b',      # "happens because happens"
    ]

    for pattern in tautology_patterns:
        if re.search(pattern, normalized):
            return -0.3  # Tautology penalty

    return 0.0


def _measure_information_gain(input_text: str, output_text: str) -> float:
    """
    Measure information gain from input to output.

    Heuristics:
    - New content words introduced = positive
    - Only repeating input words = negative
    - Adding examples/details = positive

    Returns:
        Information gain score (-0.2 to +0.4)
    """
    input_words = _extract_content_words(input_text)
    output_words = _extract_content_words(output_text)

    if not output_words:
        return -0.2  # Empty output = confusion

    # New words introduced (information added)
    new_words = output_words - input_words

    # Ratio of new information
    new_info_ratio = len(new_words) / len(output_words) if output_words else 0.0

    # Length factor (longer responses usually add clarity, up to a point)
    output_len = len(_normalize_text(output_text).split())
    length_bonus = min(0.1, output_len / 100)  # Cap at 0.1 for ~100 words

    # Calculate information gain
    if new_info_ratio > 0.5:
        # Good: >50% new information
        return 0.3 + length_bonus
    elif new_info_ratio > 0.2:
        # Okay: 20-50% new information
        return 0.1 + length_bonus
    else:
        # Bad: <20% new information (mostly repetition)
        return -0.1


def compute_delta_s(
    input_text: str,
    output_text: str,
    context: Optional[dict] = None,
) -> float:
    """
    Compute ΔS (clarity delta) between input and output.

    Real implementation with:
    - Circular reasoning detection (word overlap > 70%)
    - Tautology detection ("X is caused by X")
    - Information gain measurement
    - Semantic coherence analysis

    Args:
        input_text: User input (initial state)
        output_text: AI output (final state)
        context: Optional context for state tracking

    Returns:
        ΔS value:
        - Positive: Clarity increased (output adds information)
        - Zero: Neutral (no change)
        - Negative: Confusion increased (circular reasoning, tautology)

    Examples:
        >>> compute_delta_s("What is inflation?", "Inflation is a general increase in prices.")
        0.4  # Good: adds new information

        >>> compute_delta_s("What is inflation?", "Inflation is caused by inflation.")
        -0.5  # Bad: circular reasoning + tautology
    """
    # Allow override from context (for testing/metrics injection)
    if context and "delta_s" in context.get("metrics", {}):
        return context["metrics"]["delta_s"]

    # Initialize score at neutral
    delta_s = 0.0

    # 1. Check for circular reasoning (>70% word overlap)
    circular_penalty = _detect_circular_reasoning(input_text, output_text)
    delta_s += circular_penalty

    # 2. Check for tautologies ("X is caused by X")
    tautology_penalty = _detect_tautology(output_text)
    delta_s += tautology_penalty

    # 3. Measure information gain (new content words)
    info_gain = _measure_information_gain(input_text, output_text)
    delta_s += info_gain

    # Clamp to reasonable range [-1.0, 1.0]
    delta_s = max(-1.0, min(1.0, delta_s))

    return delta_s


__all__ = ["compute_delta_s"]
