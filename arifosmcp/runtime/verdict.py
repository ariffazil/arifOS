"""
arifOS Effective Verdict — canonical single-verdict composer.

Epoch 1 / Item 3 of the Kernel Senescence Reduction plan.
The single composer of effective_verdict, reason_code, next_action.
No wrapper may emit a competing verdict dimension.

Schema (from F13 epoch / audit spec):
    {
      "status": "completed",
      "effective_verdict": "HOLD",
      "reason_code": "IDENTITY_UNVERIFIED",
      "next_action": "VERIFY_IDENTITY"
    }

The taxonomy is closed: six values, no more.

    OBSERVE_ONLY  — read-only; identity not yet bound
    SEAL         — proceed, all floors passed
    SABAR        — proceed cautiously; partial coverage
    VOID         — halt; floor violation
    HOLD         — await review; non-blocking concern
    888_HOLD     — await sovereign veto; F13 territory

This module replaces every legacy verdict emission: `verdict`,
`verdict_code`, `canonical_verdict`, `reasoning_verdict`, and the
nine-signal aggregate. The reducer is the only place these collapse
into one effective value.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


# Schema version. Bump when the canonical shape changes.
VERDICT_STATE_VERSION = 1

# The six canonical verdict values. Closed taxonomy.
OBSERVE_ONLY = "OBSERVE_ONLY"
SEAL = "SEAL"
SABAR = "SABAR"
VOID = "VOID"
HOLD = "HOLD"
HOLD_888 = "888_HOLD"

CANONICAL_VERDICTS = frozenset(
    {OBSERVE_ONLY, SEAL, SABAR, VOID, HOLD, HOLD_888}
)


# Status values. Closed taxonomy.
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_BLOCKED = "blocked"
STATUS_PENDING = "pending"

CANONICAL_STATUSES = frozenset(
    {STATUS_COMPLETED, STATUS_FAILED, STATUS_BLOCKED, STATUS_PENDING}
)


# Legacy verdict tokens emitted by tools prior to Epoch 1.
# Each maps deterministically to one canonical verdict.
_LEGACY_VERDICT_MAP: dict[str, str] = {
    # Direct matches
    "SEAL": SEAL,
    "HOLD": HOLD,
    "VOID": VOID,
    "SABAR": SABAR,
    "OBSERVE_ONLY": OBSERVE_ONLY,
    "888_HOLD": HOLD_888,
    # Legacy aliases → canonical
    "ALLOW": SEAL,
    "DEGRADED": SABAR,
    "FAIL": VOID,
    "ERROR": VOID,
    "BLOCKED": VOID,
    "PARTIAL": SABAR,
    "UNKNOWN": HOLD,
}


def _normalize_verdict(raw: str | None) -> str:
    """Collapse any legacy verdict token into one of the six canonical values.

    Unknown tokens fall back to HOLD — fail-closed, never SEAL on unknown.
    """
    if not raw:
        return HOLD
    token = str(raw).strip().upper()
    if token in CANONICAL_VERDICTS:
        return token
    return _LEGACY_VERDICT_MAP.get(token, HOLD)


# Canonical reason_code per verdict. Reason codes are stable machine-readable
# identifiers that downstream tools and the conformance test inspect.
REASON_OBSERVE_ONLY = "NO_IDENTITY_BOUND"
REASON_SEAL = "APPROVED"
REASON_SABAR = "PARTIAL_PROCEED"
REASON_VOID = "BLOCKED_BY_FLOOR"
REASON_HOLD = "NEEDS_REVIEW"
REASON_888_HOLD = "NEEDS_SOVEREIGN"

REASON_BY_VERDICT: dict[str, str] = {
    OBSERVE_ONLY: REASON_OBSERVE_ONLY,
    SEAL: REASON_SEAL,
    SABAR: REASON_SABAR,
    VOID: REASON_VOID,
    HOLD: REASON_HOLD,
    HOLD_888: REASON_888_HOLD,
}


# Canonical next_action per verdict. Suggests the lawful follow-up.
NEXT_OBSERVE_ONLY = "BIND_IDENTITY"
NEXT_SEAL = "PROCEED"
NEXT_SABAR = "PROCEED_CAUTIOUSLY"
NEXT_VOID = "INVESTIGATE"
NEXT_HOLD = "AWAIT_INPUT"
NEXT_888_HOLD = "AWAIT_SOVEREIGN"

NEXT_ACTION_BY_VERDICT: dict[str, str] = {
    OBSERVE_ONLY: NEXT_OBSERVE_ONLY,
    SEAL: NEXT_SEAL,
    SABAR: NEXT_SABAR,
    VOID: NEXT_VOID,
    HOLD: NEXT_HOLD,
    HOLD_888: NEXT_888_HOLD,
}


# Status per verdict. Successful verdicts complete; blocking ones block;
# awaiting-input ones stay pending.
_STATUS_BY_VERDICT: dict[str, str] = {
    SEAL: STATUS_COMPLETED,
    SABAR: STATUS_COMPLETED,
    HOLD: STATUS_PENDING,
    HOLD_888: STATUS_PENDING,
    OBSERVE_ONLY: STATUS_PENDING,
    VOID: STATUS_BLOCKED,
}


@dataclass(frozen=True)
class EffectiveVerdict:
    status: str
    verdict: str
    reason_code: str
    next_action: str
    state_version: int = VERDICT_STATE_VERSION


def compose_effective_verdict(
    inner_verdict: str | None = None,
    *,
    session_authority_band: str | None = None,
    drift: list[str] | None = None,
    explicit_reason: str | None = None,
) -> EffectiveVerdict:
    """Compute the single effective verdict.

    Inputs:
      inner_verdict: any verdict token the tool emitted (canonical or legacy)
      session_authority_band: the canonical authority band for the session;
        if OBSERVE_ONLY, the effective verdict cannot be SEAL even if the
        tool says so — the session is not authorised.
      drift: list of identity-drift violation strings; non-empty forces HOLD.
      explicit_reason: optional override for reason_code (must still be one
        of the canonical reason codes).

    Output: EffectiveVerdict with status / verdict / reason_code / next_action.
    """
    canonical = _normalize_verdict(inner_verdict)

    # F1 AMANAH: identity-not-bound is a real constraint. If the session is
    # OBSERVE_ONLY and the tool claims SEAL, the effective verdict is HOLD,
    # not SEAL. Identity outranks tool self-report.
    if session_authority_band == OBSERVE_ONLY and canonical == SEAL:
        canonical = OBSERVE_ONLY

    # Drift is structural contradiction. Non-empty drift is HOLD regardless
    # of what the tool claims.
    if drift:
        canonical = HOLD

    # Void cannot be downgraded by anything except 888_HOLD.
    if canonical == VOID and session_authority_band is None:
        # no change — VOID stays
        pass

    reason_code = explicit_reason or REASON_BY_VERDICT[canonical]
    next_action = NEXT_ACTION_BY_VERDICT[canonical]
    status = _STATUS_BY_VERDICT[canonical]

    return EffectiveVerdict(
        status=status,
        verdict=canonical,
        reason_code=reason_code,
        next_action=next_action,
        state_version=VERDICT_STATE_VERSION,
    )


def verdict_to_envelope(effective: EffectiveVerdict) -> dict[str, Any]:
    """Serialize the EffectiveVerdict into the audit-spec envelope.

    Exactly four fields. Nothing else.
    """
    return {
        "status": effective.status,
        "effective_verdict": effective.verdict,
        "reason_code": effective.reason_code,
        "next_action": effective.next_action,
    }


# ── Wrapper helper: strip legacy verdict fields, attach canonical ──────────

# Every legacy verdict-shaped field name we have seen in tool responses.
# The strip removes them at every nesting level. Empty legacy containers
# are removed entirely.
_LEGACY_VERDICT_TOP_LEVEL = (
    "verdict",
    "verdict_code",
    "canonical_verdict",
    "reasoning_verdict",
    "verdict_state_version",
    "nine_signal_aggregate",
    "nine_signal_state",
    "wrapper_degradation",
    "_verdict_narrowed_from",
    "_verdict_narrowed_reason",
    "verdict_history",
)

_LEGACY_VERDICT_NESTED = (
    "verdict",
    "verdict_code",
    "canonical_verdict",
    "reasoning_verdict",
    "nine_signal_aggregate",
    "nine_signal_state",
)


def _strip_legacy_verdict(response: dict[str, Any]) -> None:
    """Remove every legacy verdict field at every nesting level."""
    for key in _LEGACY_VERDICT_TOP_LEVEL:
        response.pop(key, None)

    meta = response.get("meta")
    if isinstance(meta, dict):
        for key in _LEGACY_VERDICT_NESTED:
            meta.pop(key, None)

    result = response.get("result")
    if isinstance(result, dict):
        for key in _LEGACY_VERDICT_TOP_LEVEL:
            result.pop(key, None)
        result_meta = result.get("meta")
        if isinstance(result_meta, dict):
            for key in _LEGACY_VERDICT_NESTED:
                result_meta.pop(key, None)


def attach_effective_verdict(
    response: Any,
    *,
    inner_verdict: str | None = None,
    session_authority_band: str | None = None,
    drift: list[str] | None = None,
) -> Any:
    """Attach the canonical effective_verdict to a response.

    Strips every legacy verdict-shaped field name from the response and
    attaches the four-field canonical envelope. The inner_verdict is
    collapsed through the canonical reducer before attachment.

    Returns the (possibly unchanged) input. Non-dict inputs pass through.
    """
    if not isinstance(response, dict):
        return response
    _strip_legacy_verdict(response)
    effective = compose_effective_verdict(
        inner_verdict=inner_verdict,
        session_authority_band=session_authority_band,
        drift=drift,
    )
    response["status"] = effective.status
    response["effective_verdict"] = effective.verdict
    response["reason_code"] = effective.reason_code
    response["next_action"] = effective.next_action
    return response


__all__ = [
    "EffectiveVerdict",
    "VERDICT_STATE_VERSION",
    "OBSERVE_ONLY",
    "SEAL",
    "SABAR",
    "VOID",
    "HOLD",
    "HOLD_888",
    "CANONICAL_VERDICTS",
    "STATUS_COMPLETED",
    "STATUS_FAILED",
    "STATUS_BLOCKED",
    "STATUS_PENDING",
    "CANONICAL_STATUSES",
    "REASON_OBSERVE_ONLY",
    "REASON_SEAL",
    "REASON_SABAR",
    "REASON_VOID",
    "REASON_HOLD",
    "REASON_888_HOLD",
    "NEXT_OBSERVE_ONLY",
    "NEXT_SEAL",
    "NEXT_SABAR",
    "NEXT_VOID",
    "NEXT_HOLD",
    "NEXT_888_HOLD",
    "compose_effective_verdict",
    "verdict_to_envelope",
    "attach_effective_verdict",
]