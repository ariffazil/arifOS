"""
arifosmcp/runtime/a_rif/parser.py — Claim String Parser
════════════════════════════════════════════════════════

Extracts claimed evidence levels from free-text candidate strings.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import re

__all__ = ["parse_claimed_evidence_level"]

EVIDENCE_LEVEL_PATTERN = re.compile(r"\b(L[0-6])\b", re.IGNORECASE)


def parse_claimed_evidence_level(candidate: str) -> str | None:
    """
    Scan a candidate string for explicit evidence-level claims.

    Returns the highest level found, or None if no level marker.
    Examples:
        "Deploy with L3 evidence" → "L3"
        "This is L1 at best" → "L1"
        "No evidence claimed" → None
    """
    if not isinstance(candidate, str) or not candidate.strip():
        return None

    matches = EVIDENCE_LEVEL_PATTERN.findall(candidate)
    if not matches:
        return None

    # Normalize to uppercase and take highest level
    levels = sorted(set(m.upper() for m in matches))
    return levels[-1]  # L6 > L5 > ... > L0
