"""Language bridge helper for @PROMPT organ (v42.1).

Provides a simple C_budi computation: clarity × respect × cultural_fit ÷ jargon_penalty.
"""

from __future__ import annotations

def compute_c_budi(
    prompt: str,
    response: str,
    anti_hantu_score: float | None = None,
    respect: float = 1.0,
    cultural_fit: float = 1.0,
    jargon_penalty: float = 1.0,
) -> float:
    """Compute a bounded C_budi score (0.0-1.0)."""
    clarity = 0.9 if response else 0.5
    if anti_hantu_score is not None:
        clarity = max(0.0, min(1.0, clarity * anti_hantu_score))
    base = clarity * respect * cultural_fit
    if jargon_penalty <= 0:
        jargon_penalty = 1.0
    score = base / jargon_penalty
    return float(max(0.0, min(1.0, score)))


__all__ = ["compute_c_budi"]
