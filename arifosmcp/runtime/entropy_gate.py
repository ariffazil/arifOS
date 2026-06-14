"""
arifosmcp/runtime/entropy_gate.py
═══════════════════════════════════════════════════════════════════════════════
EUREKA 4: Entropy Gate

Measures output entropy to detect behaviour-sink (over-optimisation for
predictability). Uses character-level Shannon entropy normalised to [0.0, 1.0].

The normalisation constant is log2(128) = 7.0, representing the maximum
entropy of 7-bit ASCII text. This gives sensible scores for English-language
agent output:

Entropy score interpretation:
  - < 0.3 : Too repetitive / predictable → EXPLORE
  - 0.3–0.7 : Healthy variation          → PROCEED
  - > 0.7  : Too chaotic                  → HOLD

Constitutional Floors: F8 (GENIUS), F9 (ANTIHANTU)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import math

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

EXPLORE_THRESHOLD: float = 0.3
HOLD_THRESHOLD: float = 0.7

# Maximum possible Shannon entropy for a byte: log2(256) = 8.0.
# This normaliser gives scores in [0.0, 1.0] such that natural English
# prose lands in the 0.3–0.7 band, repetitive text falls below 0.3, and
# cryptographic / highly-random text rises above 0.7.
_MAX_BYTE_ENTROPY: float = 8.0


# ──────────────────────────────────────────────────────────────────────────────
# Core computation
# ──────────────────────────────────────────────────────────────────────────────


def _shannon_entropy(text: str) -> float:
    """
    Compute normalised Shannon entropy for the given text.

    Character-level: counts the frequency of each distinct character,
    computes raw Shannon entropy H = -Σ p(i) · log2(p(i)), then normalises
    by the maximum possible entropy for a byte (log2(256) ≈ 8.0).

    Returns a float in [0.0, 1.0].
    """
    if not text:
        return 0.0

    length = len(text)
    freq: dict[str, int] = {}

    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1

    raw_h: float = 0.0
    for count in freq.values():
        p = count / length
        raw_h -= p * math.log2(p)

    normalised = raw_h / _MAX_BYTE_ENTROPY
    # Clamp to [0.0, 1.0] against floating-point drift
    return max(0.0, min(1.0, normalised))


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────


def check_entropy(agent_output: str) -> tuple[float, str]:
    """
    Measure output entropy to detect behaviour-sink.

    Parameters
    ----------
    agent_output : str
        The text produced by the agent to evaluate.

    Returns
    -------
    tuple[float, str]
        ``(score, action)`` where:

        - **score** is the normalised Shannon entropy in [0.0, 1.0]
        - **action** is one of ``"EXPLORE"`` (score < 0.3),
          ``"PROCEED"`` (0.3 <= score <= 0.7), or ``"HOLD"`` (score > 0.7).
    """
    score = _shannon_entropy(agent_output)

    if score < EXPLORE_THRESHOLD:
        action = "EXPLORE"
    elif score > HOLD_THRESHOLD:
        action = "HOLD"
    else:
        action = "PROCEED"

    return (round(score, 4), action)
