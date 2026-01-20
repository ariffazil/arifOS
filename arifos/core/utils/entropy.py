"""
arifos.core/utils/entropy.py

Thermodynamic Clarity (ΔS) - The Shannon Entropy Engine.

Purpose:
    Computes the Information Entropy (S) of text states to measure Clarity (F4).
    ΔS = S_after - S_before.
    Negative ΔS means entropy reduction (clarity gained).
    Positive ΔS means entropy increase (confusion increased).

Formulas:
    S = -Σ p(i) * log2(p(i))
    where p(i) is probability of token i.

DITEMPA BUKAN DIBERI - Forged v46.1
"""

import collections
import math
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class EntropyResult:
    """Result of an entropy computation."""
    s_before: float
    s_after: float
    delta_s: float
    clarity_gained: bool

def compute_shannon_entropy(text: str, unit: str = "bit") -> float:
    """
    Compute Shannon entropy of a string.

    Args:
        text: Input string.
        unit: 'bit' (log2), 'nat' (ln), or 'dit' (log10).

    Returns:
        Entropy value (S).
    """
    if not text:
        return 0.0

    # Calculate character frequencies (simple model for now, can upgrade to token-based)
    # For Phase 1, character-level entropy is a sufficient proxy for "randomness/confusion"
    counts = collections.Counter(text)
    total_len = len(text)

    entropy = 0.0
    for count in counts.values():
        p_i = count / total_len
        if unit == "bit":
            entropy -= p_i * math.log2(p_i)
        elif unit == "nat":
            entropy -= p_i * math.log(p_i)
        else:
            entropy -= p_i * math.log10(p_i)

    return entropy

def compute_delta_s(
    input_state: str,
    output_state: str,
    threshold: float = 0.0
) -> EntropyResult:
    """
    Compute thermodynamic clarity (ΔS).

    Args:
        input_state: The prompt/context (Before).
        output_state: The response/action (After).
        threshold: Max acceptable ΔS (typically 0 or small positive for complex tasks).

    Returns:
        EntropyResult containing S_before, S_after, and ΔS.
    """
    s_before = compute_shannon_entropy(input_state)
    s_after = compute_shannon_entropy(output_state)

    # In arifOS thermodynamics:
    # We want the system to REDUCE entropy or maintain it.
    # However, generating text technically adds information (and thus might look like higher entropy locally).
    # A true ΔS measurer should compare "User Constraint vs System Compliance".
    # For Phase 1 proxy: We compare the entropy density or simply the raw transition.

    # REVISION v46:
    # ΔS = S_after - S_before
    # If output is more ordered than input, S_after < S_before -> ΔS < 0 (Good).
    # If output is chaotic/hallinating, S_after > S_before -> ΔS > 0 (Bad).

    delta_s = s_after - s_before

    # Pass if ΔS <= threshold (clarity gained or confusion within limits)
    clarity_gained = delta_s <= threshold

    return EntropyResult(
        s_before=s_before,
        s_after=s_after,
        delta_s=delta_s,
        clarity_gained=clarity_gained
    )

def evaluate_clarity_floor(delta_s: float, threshold: float = 0.0) -> tuple[bool, str]:
    """Helper for F4 Clarity floor check."""
    if delta_s <= threshold:
        return True, f"F4 Clarity PASS: ΔS {delta_s:.4f} <= {threshold}"
    else:
        return False, f"F4 Clarity FAIL: ΔS {delta_s:.4f} > {threshold} (Entropy Increased/Confusion)"
