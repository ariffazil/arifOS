"""One FQ object — value, measured_at, scope.

T2 (2026-10-18). Before this module a single response could carry several
FQ-shaped numbers with no way to tell them apart:

  * ``metabolic_state.quotient`` — the SESSION reading, often ``None``
    because the actor has no receipts (``UNKNOWN_ACTOR``).
  * ``apex_scalars.G`` / ``kernel_baseline.G`` — the FEDERATION baseline,
    frozen at ACT-mint in one place and recomputed live in another, so one
    payload could show G=0.2955 beside G=0.5501 (measured 2026-10-18).

Same field family, two scopes, no timestamp: a consumer could not say which
number described the session, which described the federation, or how old
either was. This module is the one place that builds the object. Producers
pass their own reading in; the shape and the vocabulary live here.

Doctrine: an absent reading is ``None``, never ``0`` and never a guess
(K2: unknown != zero). ``measured_at`` is the time the producer read the
number, not the time the response was serialised.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

FQ_SCOPE_SESSION = "session"
FQ_SCOPE_FEDERATION = "federation"
FQ_SCOPES = (FQ_SCOPE_SESSION, FQ_SCOPE_FEDERATION)

_UNMEASURED_TOKENS = frozenset({"", "UNMEASURED", "UNKNOWN", "NONE", "NULL", "N/A"})


def _number(value: Any) -> float | None:
    """Coerce a reading to float, or None. Booleans are not measurements."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def now_iso() -> str:
    """UTC instant in the same shape /health uses for measured_at."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def fq_object(
    value: Any,
    *,
    measured_at: str | None = None,
    scope: str = FQ_SCOPE_SESSION,
) -> dict[str, Any]:
    """The ONE writer of an FQ object.

    Exactly three keys, always present. ``scope`` names which system the
    reading describes; ``measured_at`` says when it was taken so a cached
    value cannot masquerade as a live one.
    """
    if isinstance(value, str) and value.strip().upper() in _UNMEASURED_TOKENS:
        value = None
    resolved_scope = scope if scope in FQ_SCOPES else FQ_SCOPE_SESSION
    return {
        "value": _number(value),
        "measured_at": str(measured_at) if measured_at else None,
        "scope": resolved_scope,
    }


def normalize_fq(
    raw: Any,
    *,
    scope: str = FQ_SCOPE_SESSION,
    measured_at: str | None = None,
) -> dict[str, Any]:
    """Coerce a legacy FQ shape into the one object.

    Accepted legacy shapes: ``{"value": x}``, ``{"quotient": x}``,
    ``{"fq": x}``, ``{"G": x}``, a bare number, or an ``"UNMEASURED"``
    token. Never invents a reading: an unrecognised shape becomes
    ``value=None`` rather than 0.
    """
    if isinstance(raw, Mapping):
        value = raw.get("value")
        if value is None and "quotient" in raw:
            value = raw.get("quotient")
        if value is None and "fq" in raw:
            value = raw.get("fq")
        if value is None and "G" in raw:
            value = raw.get("G")
        if measured_at is None:
            measured_at = raw.get("measured_at")
        if raw.get("scope") in FQ_SCOPES:
            scope = raw["scope"]
    else:
        value = raw
    coerced = fq_object(value, measured_at=measured_at, scope=scope)
    if isinstance(raw, Mapping) and isinstance(raw.get("decomposition"), Mapping):
        # P6 (F13 D2 2026-10-23): the decomposition sub-object (raw /
        # normalization / threshold / window / formula) travels WITH the
        # reading as separate fields — one writer, coerced here.
        coerced["decomposition"] = dict(raw["decomposition"])
    return coerced
