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

from dataclasses import dataclass
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

CANONICAL_VERDICTS = frozenset({OBSERVE_ONLY, SEAL, SABAR, VOID, HOLD, HOLD_888})


# Status values. Closed taxonomy.
# P0 2026-08-09 (G1): status = *tool execution* outcome, NOT governance.
# effective_verdict carries SEAL/HOLD/VOID. Agents were reading status=pending
# on completed HOLD/OBSERVE responses as "tool still running" → re-call loops.
STATUS_COMPLETED = "completed"
STATUS_OK = "ok"  # schema alias of completed (response.envelope.schema.json)
STATUS_FAILED = "failed"
STATUS_BLOCKED = "blocked"
STATUS_PENDING = "pending"  # ONLY for true async / not-yet-finished work

CANONICAL_STATUSES = frozenset(
    {STATUS_COMPLETED, STATUS_OK, STATUS_FAILED, STATUS_BLOCKED, STATUS_PENDING}
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


# Status per verdict = did the tool *finish executing*?
# Governance restraint (HOLD / OBSERVE_ONLY) is expressed via effective_verdict
# + next_action, never by leaving status=pending after a completed call.
_STATUS_BY_VERDICT: dict[str, str] = {
    SEAL: STATUS_COMPLETED,
    SABAR: STATUS_COMPLETED,
    HOLD: STATUS_COMPLETED,
    HOLD_888: STATUS_COMPLETED,
    OBSERVE_ONLY: STATUS_COMPLETED,
    VOID: STATUS_BLOCKED,
}

# execution_state axis (schema v2) — lifecycle of the requested action.
# Distinct from status (transport/execution ok) and effective_verdict (governance).
_EXECUTION_STATE_BY_VERDICT: dict[str, str] = {
    SEAL: "COMPLETED",
    SABAR: "COMPLETED",
    HOLD: "COMPLETED",  # tool finished; next_action may still be AWAIT_INPUT
    HOLD_888: "COMPLETED",
    OBSERVE_ONLY: "COMPLETED",
    VOID: "FAILED",
}


@dataclass(frozen=True)
class EffectiveVerdict:
    status: str
    verdict: str
    reason_code: str
    next_action: str
    execution_state: str = "COMPLETED"
    state_version: int = VERDICT_STATE_VERSION


def compose_effective_verdict(
    inner_verdict: str | None = None,
    *,
    session_authority_band: str | None = None,
    drift: list[str] | None = None,
    explicit_reason: str | None = None,
    g_score: float | None = None,
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
      g_score: APEX G scalar [0-1]. If provided and < SEAL_THRESHOLD (0.80),
        SEAL is downgraded to SABAR per F8 GENIUS gate.
        FIX 2026-08-06 (Claude audit #4): G was computed but never gated.

    Output: EffectiveVerdict with status / verdict / reason_code / next_action.
    """
    # F8 GENIUS gate constants (single source, matches apex_canonical.py)
    _G_SEAL_THRESHOLD = 0.80
    _G_SABAR_THRESHOLD = 0.50
    _G_DEGRADED_THRESHOLD = 0.30

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

    # F8 GENIUS: G gate — computed but previously never wired.
    # G below SEAL threshold blocks SEAL. G below DEGRADED downgrades to HOLD.
    if g_score is not None and canonical == SEAL:
        if g_score < _G_DEGRADED_THRESHOLD:
            canonical = HOLD
            explicit_reason = (
                explicit_reason
                or f"F8_GENIUS: G={g_score:.3f} < {_G_DEGRADED_THRESHOLD} DEGRADED threshold"
            )
        elif g_score < _G_SABAR_THRESHOLD:
            canonical = SABAR
            explicit_reason = (
                explicit_reason
                or f"F8_GENIUS: G={g_score:.3f} < {_G_SABAR_THRESHOLD} SABAR threshold"
            )
        elif g_score < _G_SEAL_THRESHOLD:
            canonical = SABAR
            explicit_reason = (
                explicit_reason
                or f"F8_GENIUS: G={g_score:.3f} < {_G_SEAL_THRESHOLD} SEAL threshold"
            )

    # Void cannot be downgraded by anything except 888_HOLD.
    if canonical == VOID and session_authority_band is None:
        # no change — VOID stays
        pass

    reason_code = explicit_reason or REASON_BY_VERDICT[canonical]
    next_action = NEXT_ACTION_BY_VERDICT[canonical]
    status = _STATUS_BY_VERDICT[canonical]
    execution_state = _EXECUTION_STATE_BY_VERDICT[canonical]

    return EffectiveVerdict(
        status=status,
        verdict=canonical,
        reason_code=reason_code,
        next_action=next_action,
        execution_state=execution_state,
        state_version=VERDICT_STATE_VERSION,
    )


def verdict_to_envelope(effective: EffectiveVerdict) -> dict[str, Any]:
    """Serialize the EffectiveVerdict into the agent-facing envelope.

    status = execution finished?  (completed | blocked | failed | pending)
    effective_verdict = governance (SEAL | HOLD | …)
    execution_state = lifecycle axis (COMPLETED | FAILED | …)
    """
    return {
        "status": effective.status,
        "effective_verdict": effective.verdict,
        "reason_code": effective.reason_code,
        "next_action": effective.next_action,
        "execution_state": effective.execution_state,
        "status_scope": "execution",
    }


# ── Wrapper helper: strip legacy verdict fields, attach canonical ──────────

# Every legacy verdict-shaped field name we have seen in tool responses.
# The strip removes them at every nesting level. Empty legacy containers
# are removed entirely.
_LEGACY_VERDICT_TOP_LEVEL = (
    "verdict",
    "verdict_code",
    # STEP 2 (2026-08-05): canonical_verdict RE-ADDED to strip list.
    # Was: "preserve canonical transparency" — this created a second
    # authoritative verdict field that disagreed with effective_verdict.
    # Now: effective_verdict is the SINGLE root. Canonical transparency
    # is preserved through effective_verdict's 6-class taxonomy.
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
    response["execution_state"] = effective.execution_state
    response["status_scope"] = "execution"
    # P0 G1: never leave status=pending after a completed tool call unless
    # the handler explicitly set async pending. Governance HOLD is not pending.
    if (
        str(response.get("status", "")).lower() == "pending"
        and effective.execution_state == "COMPLETED"
        and response.get("result") is not None
    ):
        response["status"] = STATUS_COMPLETED
    # STAB-2026-08-07b: this is the LAST writer of effective_verdict.
    # Re-derive floor_passed HERE so it cannot disagree with the verdict
    # that just landed. effective_verdict in {HOLD, VOID, 888_HOLD} → False.
    # failed_floors populated → False. This is the single source of truth;
    # every other writer must defer to this one.
    cc = response.get("constitutional_check")
    if isinstance(cc, dict):
        _ev = effective.verdict
        _ff = (
            response.get("failed_floors")
            or response.get("violated_floors")
            or (response.get("meta", {}) or {}).get("violated_laws")
            or (cc.get("failed_floors") or [])
            or []
        )
        _has_hold = _ev in ("HOLD", "VOID", "888_HOLD") or bool(_ff)
        # STAB-2026-08-08j: FLOOR_HONESTY.
        # floor_passed is now a genuine sensor: None = unmeasured,
        # True = floors measured and passed, False = floors failed.
        # If no floors were checked (_ff empty AND no nine_signal floor data),
        # floor_passed = None — honest absence, not silent True/False.
        _floors_actually_checked = bool(_ff)
        if _floors_actually_checked:
            cc["floor_passed"] = False  # if we got here, floors DID fail
        elif _has_hold and not _ff:
            # HOLD without specific floor failures = unmeasured
            cc["floor_passed"] = None
        else:
            # No hold, no failed floors, but also no measured floors
            cc["floor_passed"] = None  # not measured, not assumed
        cc["_floor_measurement"] = "measured" if _floors_actually_checked else "unmeasured"
        cc["hold_required"] = _has_hold
        cc["failed_floors"] = list(_ff) if _ff else cc.get("failed_floors", [])
        if _has_hold and not cc.get("hold_reason"):
            cc["hold_reason"] = (
                f"STAB-2026-08-07b canonical: effective_verdict={_ev} "
                f"failed_floors={list(_ff)}"
            )
        cc["_derivation"] = "attach_effective_verdict:last_writer"

    # STAB-2026-08-09: single source for mutation_allowed — derived from
    # effective_verdict (and authority band if present). Never leave
    # OBSERVE_ONLY/HOLD/VOID with mutation_allowed=true in any nest.
    _ev_u = str(effective.verdict or "").upper()
    _mut_ok = _ev_u in ("SEAL", "SABAR", "FULL", "LIMITED_MUTATE", "OK", "APPROVED")
    # Conservative: only SEAL with non-observe authority allows mutation flags
    # downstream. HOLD/VOID/OBSERVE_ONLY force false everywhere.
    if _ev_u in ("HOLD", "VOID", "888_HOLD", "OBSERVE_ONLY", "SABAR"):
        _force_mut = False
    else:
        # SEAL-ish verdict still needs non-OBSERVE band if present
        _force_mut = None  # leave existing unless observe band found

    def _sync_mut(d: dict, *, force: bool | None) -> None:
        if not isinstance(d, dict):
            return
        band = str(
            d.get("authority_band")
            or d.get("authority_mode")
            or d.get("authority")
            or ""
        ).upper()
        if force is False or band in ("OBSERVE_ONLY", "VOID", "ANONYMOUS", ""):
            # Always write the field — clients must not see missing = ambiguous
            d["mutation_allowed"] = False
            if force is False:
                d["seal_allowed"] = False
        es = d.get("effective_state")
        if isinstance(es, dict):
            eband = str(es.get("authority_band") or "").upper()
            if force is False or eband in ("OBSERVE_ONLY", "VOID", "ANONYMOUS", ""):
                es["mutation_allowed"] = False
                if force is False:
                    es["seal_allowed"] = False
            elif eband in ("LIMITED_MUTATE", "FULL", "SOVEREIGN", "MUTATE"):
                es["mutation_allowed"] = True
        # nested session_birth / result
        for nest in ("session_birth", "result"):
            nested = d.get(nest)
            if isinstance(nested, dict):
                _sync_mut(nested, force=force)

    if _force_mut is False:
        _sync_mut(response, force=False)
        res = response.get("result")
        if isinstance(res, dict):
            _sync_mut(res, force=False)
        standing = response.get("standing")
        if isinstance(standing, dict):
            auth = standing.get("authority")
            if isinstance(auth, dict):
                auth["mutation_allowed"] = False
                auth["seal_allowed"] = False

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
