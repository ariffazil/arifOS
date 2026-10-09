"""
PRESENT — Epistemic state wrapper. Reads reality class from session context.
DITEMPA BUKAN DIBERI — Forged, Not Given.

EPISTEMIC AXES (P1 extension 2026-09-19, additive)
─────────────────────────────────────────────────
The session epistemic state is a multi-axis record. Two axes now live here:

  axis 1  reality_class   LIVE | CACHED | INFERRED | HYPOTHESIZED | UNKNOWN
                          — HOW the claim was obtained (existing axis; read by
                            akal_wiring.PRESENT).
  axis 2  claim_class     MEASURED | MECHANISM | PATTERN | NARRATIVE | UNCLASSIFIED
                          — WHAT KIND of explanation the claim is (new axis;
                            vocabularies owned by AAA/lib/claim_kernel, NOT
                            redeclared here).

Why axis 2 lives IN this module rather than beside it: both axes describe the
same object (a claim/verdict in a session) from orthogonal angles. A separate
registry would let a session hold a `reality_class` with no corresponding
`claim_class` and no single place to ask "what does this session actually know
and how?". One cache, one record, two axes.

The mutation-authorising consumer of axis 2 is
`arifosmcp.core.claim_class_gate` (read by the V2 response envelope).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_epistemic_cache: dict[str, dict[str, Any]] = {}

# Canonical key names for the two axes (single source; consumers import these)
AXIS_REALITY_CLASS = "reality_class"
AXIS_CLAIM_CLASS = "claim_class"
EPISTEMIC_AXES = (AXIS_REALITY_CLASS, AXIS_CLAIM_CLASS)


def set_epistemic_state(session_id: str, state: dict[str, Any]) -> None:
    """Store epistemic state for a session.

    NOTE: whole-record replace (pre-existing semantics — unchanged). Use
    `record_claim_class` to add axis 2 without clobbering axis 1.
    """
    _epistemic_cache[session_id] = state


def get_epistemic_state(session_id: str | None) -> dict[str, Any] | None:
    """Return reality_class and other epistemic metadata from session.

    Returns dict with keys like:
        reality_class: "LIVE" | "CACHED" | "INFERRED" | "HYPOTHESIZED" | "UNKNOWN"
        claim_class:   "MEASURED" | "MECHANISM" | "PATTERN" | "NARRATIVE" | "UNCLASSIFIED"
    Returns None if no state for this session.
    """
    if not session_id:
        return None
    return _epistemic_cache.get(session_id)


# ── Axis 2 — claim_class (additive, 2026-09-19) ──────────────────────────────


def record_claim_class(
    session_id: str | None,
    claim_class: str | None,
    *,
    claim_text: str | None = None,
    source: str | None = None,
) -> dict[str, Any] | None:
    """Merge axis 2 (claim_class) into a session's epistemic record.

    Merges — never replaces — so an existing `reality_class` (axis 1) survives.
    Returns the updated record, or None when session_id is falsy / wrong type.

    Declared class is normalised (upper/strip) but NOT validated against the
    vocabulary here: `claim_kernel.classify` is the authority for membership and
    it coerces unknown strings to UNCLASSIFIED (fail-closed). Re-validating here
    would be a second, drifting taxonomy.
    """
    if not session_id or not isinstance(session_id, str):
        return None
    try:
        record = _epistemic_cache.get(session_id)
        if not isinstance(record, dict):
            record = {}
        normalised = (claim_class or "").upper().strip()
        if normalised:
            record[AXIS_CLAIM_CLASS] = normalised
        if claim_text is not None:
            record["claim_text_excerpt"] = str(claim_text)[:500]
        if source is not None:
            record["claim_class_source"] = str(source)
        _epistemic_cache[session_id] = record
        return record
    except Exception as exc:  # never let the witness break the caller
        logger.warning("record_claim_class failed for session=%r: %s", session_id, exc)
        return None


def get_claim_class(session_id: str | None) -> str | None:
    """Return axis 2 (claim_class) for a session, or None if undeclared."""
    record = get_epistemic_state(session_id)
    if not isinstance(record, dict):
        return None
    value = record.get(AXIS_CLAIM_CLASS)
    return str(value) if value else None


def get_reality_class(session_id: str | None) -> str | None:
    """Return axis 1 (reality_class) for a session, or None if undeclared."""
    record = get_epistemic_state(session_id)
    if not isinstance(record, dict):
        return None
    value = record.get(AXIS_REALITY_CLASS)
    return str(value) if value else None


def snapshot_epistemic_axes(session_id: str | None) -> dict[str, Any]:
    """Both axes in one read — for receipts that must show the full state."""
    record = get_epistemic_state(session_id) or {}
    return {
        AXIS_REALITY_CLASS: record.get(AXIS_REALITY_CLASS),
        AXIS_CLAIM_CLASS: record.get(AXIS_CLAIM_CLASS),
        "claim_class_source": record.get("claim_class_source"),
        "session_id": session_id,
    }
