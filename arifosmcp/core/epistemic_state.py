"""
PRESENT — Epistemic state wrapper. Reads reality class from session context.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from typing import Any

_epistemic_cache: dict[str, dict[str, Any]] = {}


def set_epistemic_state(session_id: str, state: dict[str, Any]) -> None:
    """Store epistemic state for a session."""
    _epistemic_cache[session_id] = state


def get_epistemic_state(session_id: str | None) -> dict[str, Any] | None:
    """Return reality_class and other epistemic metadata from session.

    Returns dict with keys like:
        reality_class: "LIVE" | "CACHED" | "INFERRED" | "HYPOTHESIZED" | "UNKNOWN"
    Returns None if no state for this session.
    """
    if not session_id:
        return None
    return _epistemic_cache.get(session_id)
