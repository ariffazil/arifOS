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

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

# ── Nine-Signal wiring (P0 schema-fix 2026-08-17) ─────────────────────────────
# The hardening EUREKAS (F2 addendum + L10 ONTOLOGY) require every kernel
# response to carry `output_policy` and `nine_signal.overall.{state,en}`.
# attach_effective_verdict is the envelope closer. Worse verdict dominates;
# it must not overwrite HOLD/VOID with a later SABAR/SEAL (P1.3).
# so it must close the envelope by injecting nine_signal + output_policy.
# Previously this was missing — every arif_init / arif_observe / arif_think /
# arif_route / arif_memory / arif_judge / arif_seal call returned a payload
# missing these required fields, causing the MCP client to reject the response
# with "data must have required property 'output_policy'". Surgical fix.
from arifosmcp.tools.nine_signal import (  # noqa: E402
    inject_nine_signal as _inject_nine_signal,
    output_policy_for_verdict as _output_policy_for_verdict,
)

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
    HOLD: "AWAIT_INPUT",  # KRT-2026-08-15 P1: refused action never completes.
    # Tool transport finished (status=completed) but the *action* was refused
    # by governance. execution_state=COMPLETED on a HOLD made receipts read
    # as success to status-only consumers (FORGE-RECEIPT-DISHONEST).
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


# Lower rank = worse / more degraded. Outer effective_verdict is min(gates).
_VERDICT_RANK: dict[str, int] = {
    HOLD_888: 0,
    VOID: 1,
    HOLD: 2,
    OBSERVE_ONLY: 3,
    SABAR: 4,
    SEAL: 5,
}


def _worse_verdict(left: str | None, right: str | None) -> str:
    """Return the more degraded of two verdict tokens."""
    a = _normalize_verdict(left)
    b = _normalize_verdict(right)
    return a if _VERDICT_RANK.get(a, 2) <= _VERDICT_RANK.get(b, 2) else b


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
    existing = response.get("effective_verdict")
    if isinstance(existing, str) and existing.strip():
        inner_verdict = _worse_verdict(existing, inner_verdict)
    sub = response.get("substrate")
    if not isinstance(sub, dict):
        res = response.get("result")
        sub = res.get("substrate") if isinstance(res, dict) else {}
    if isinstance(sub, dict) and (
        str(sub.get("state", "")).upper() == "DEGRADED" or sub.get("drift") is True
    ):
        # Degraded substrate cannot surface as SEAL (P1.3).
        inner_verdict = _worse_verdict(inner_verdict, HOLD)
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
    # P0 schema-fix 2026-08-17: close the envelope with nine_signal + output_policy
    # before downstream mutation_allowed sync. Pass effective.verdict (not status)
    # so output_policy_for_verdict maps SEAL→DOMAIN_SEAL, HOLD→DOMAIN_HOLD,
    # VOID/SABAR→DOMAIN_VOID, OBSERVE_ONLY→DOMAIN_OBSERVE_ONLY.
    response.update(_inject_nine_signal(response, status=effective.verdict))
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
        cc["_derivation"] = "attach_effective_verdict:degraded_dominates"

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

    # Phase 0 (2026-09-22, F13): reconcile after every writer in this
    # composer. The registration wrapper runs additional writers later and
    # re-runs reconciliation at its own return; this call covers direct
    # callers of attach_effective_verdict.
    return reconcile_decision_contract(response)


# ── Phase 0 (2026-09-22, F13 nine-point critique): decision-contract ────────
# reconciliation — the last writer.
#
# Point #1: a two-field compare (verdict vs effective_verdict) is blind.
# Live payload captured 2026-09-22: verdict == effective_verdict == HOLD
# while meta.kernel_intercept.decision = ALLOW contradicted it. The walker
# visits EVERY verdict-bearing key in the payload.
# Point #3: closed token vocabulary — an unclassifiable token in a verdict
# key is an inconsistency (fail-closed to HOLD), never a silent pass.
# Point #4: EPISTEMIC vetoes — unmeasured floor presented as passed, a
# MEASURED claim riding on derived/synthetic data, and
# verdict_channel_integrity=False all force HOLD.
# On ANY flag: effective_verdict := HOLD, authority fields forced off,
# originals preserved (contradictions are evidence — Prime Invariant #7;
# never normalized away).

_VERDICT_BEARING_KEYS = frozenset(
    {
        "verdict",
        "effective_verdict",
        "canonical_verdict",
        "verdict_code",
        "reasoning_verdict",
        "decision",
        "sufficiency_verdict",
    }
)
_KNOWN_VERDICT_TOKENS = frozenset(CANONICAL_VERDICTS) | frozenset(_LEGACY_VERDICT_MAP)
# Receipt-era alias (schemas/transition_receipt.VerdictCode.OBSERVE) — known
# but outside the six-class envelope taxonomy; normalized locally only.
_RECONCILE_TOKEN_ALIASES = {"OBSERVE": OBSERVE_ONLY}
_FLOOR_EVIDENCE_KEYS = (
    "floors_invoked",
    "law_results",
    "failed_floors",
    "violated_laws",
)
_DERIVED_DATA_MODES = frozenset(
    {"derived", "synthetic", "simulated", "estimated", "interpolated", "assumed", "inferred"}
)
# Point #2 (crack #2): a restraint verdict must never point at a transition
# action. Review 2026-09-22 widened the set beyond seal/forge/commit.
_FORBIDDEN_IN_SAFE_ACTION = re.compile(
    r"\b(seal|forge|commit|execute|deploy|send|transfer)", re.IGNORECASE
)
_RESTRAINT_VERDICTS = frozenset({HOLD, VOID, HOLD_888, OBSERVE_ONLY})
_SAFE_ACTION_BY_VERDICT = {
    HOLD: "Await input — effective_verdict=HOLD (reconciled)",
    VOID: "Investigate — effective_verdict=VOID (reconciled)",
    HOLD_888: "Await sovereign decision — effective_verdict=888_HOLD (reconciled)",
    OBSERVE_ONLY: "Bind identity before any authority-bearing action",
    SABAR: "Wait for the required evidence or authority, then reassess.",
}
_DEFAULT_SAFE_ACTION = "Hold the proposal and investigate the unresolved state."


def _derive_safe_action(final: str, *, seal_allowed: bool) -> str:
    """next_safe_action is DERIVED from reconciled state — never trusted
    from the payload (review 2026-09-22 item 5). Even a reconciled SEAL only
    points at requesting an external authority grant; it never authorizes."""
    if final == SEAL and seal_allowed:
        return "Request an external authority grant for the reconciled transaction."
    if final == SEAL:
        return _DEFAULT_SAFE_ACTION
    return _SAFE_ACTION_BY_VERDICT.get(final, _DEFAULT_SAFE_ACTION)


def _iter_verdict_bearing(node: Any, path: str = "") -> Any:
    """Yield (path, raw_string) for every EXACT verdict-bearing key holding a
    non-null non-empty string. Null/absent means unset and is skipped — a
    missing value is not a claim (prevents mass-HOLD on schema defaults).
    Substring keys such as decision_thresholds are NOT matched."""
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}" if path else str(key)
            if key in _VERDICT_BEARING_KEYS and isinstance(value, str) and value.strip():
                yield child, value
            yield from _iter_verdict_bearing(value, child)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _iter_verdict_bearing(value, f"{path}[{index}]")


def _collect_epistemic_flags(node: Any, path: str = "") -> list[str]:
    """EPISTEMIC veto conditions (F13 points #4a/#4b + channel integrity)."""
    flags: list[str] = []
    if isinstance(node, dict):
        child = path or "<root>"
        if node.get("floor_passed") is True and not any(
            node.get(k) for k in _FLOOR_EVIDENCE_KEYS
        ):
            flags.append(f"EPISTEMIC_UNMEASURED_PASS:{child}")
        if (
            str(node.get("claim_class", "")).upper() == "MEASURED"
            and str(node.get("data_mode", "")).lower() in _DERIVED_DATA_MODES
        ):
            flags.append(f"EPISTEMIC_LABEL_PROVENANCE_MISMATCH:{child}")
        if node.get("verdict_channel_integrity") is False:
            flags.append(f"EPISTEMIC_VERDICT_CHANNEL_INTEGRITY:{child}")
        for key, value in node.items():
            flags.extend(_collect_epistemic_flags(value, f"{child}.{key}"))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            flags.extend(_collect_epistemic_flags(value, f"{path}[{index}]"))
    return flags


def _disable_authority_fields(node: Any) -> None:
    """Force every PRESENT authority flag to False, recursively. Never
    invents flags where none existed (minimal surface)."""
    if isinstance(node, dict):
        for key in ("mutation_allowed", "seal_allowed"):
            if key in node:
                node[key] = False
        for value in node.values():
            _disable_authority_fields(value)
    elif isinstance(node, list):
        for value in node:
            _disable_authority_fields(value)


def reconcile_decision_contract(response: Any) -> Any:
    """Walk every verdict-bearing field; one honest verdict or HOLD.

    F13 Phase 0 (2026-09-22). Non-dict inputs pass through. Idempotent —
    safe to run at every envelope-close point. Contradictions are preserved
    in place: reconciliation ADDS the reconciled HOLD verdict plus the
    machine-readable ``meta.reconciliation`` block; it never rewrites the
    disagreeing fields into agreement. ``next_safe_action`` is derived from
    the reconciled state — with authority off it may not point at
    seal/forge/commit (crack #2).
    """
    if not isinstance(response, dict):
        return response

    claims: dict[str, str] = {}
    raw_tokens: dict[str, str] = {}
    unknown: dict[str, str] = {}
    noncanonical: dict[str, str] = {}
    for path, raw in _iter_verdict_bearing(response):
        token = str(raw).strip()
        upper = token.upper()
        raw_tokens[path] = token
        if upper in CANONICAL_VERDICTS:
            claims[path] = upper
        elif upper in _RECONCILE_TOKEN_ALIASES:
            claims[path] = _RECONCILE_TOKEN_ALIASES[upper]
        elif upper in _LEGACY_VERDICT_MAP:
            # Legacy cross-layer translation (ALLOW, DEGRADED, PARTIAL, ...).
            # Participates in divergence as its canonical value AND fails
            # closed on its own: layer vocabulary is unratified until the
            # vocabulary owners publish the admissible-combination matrix
            # (review 2026-09-22 — "heterogeneous non-identical values
            # fail closed"; raw ALLOW must never silently equal SEAL).
            claims[path] = _normalize_verdict(token)
            noncanonical[path] = token
        else:
            unknown[path] = token

    flags: list[str] = []
    for path, token in unknown.items():
        flags.append(f"UNKNOWN_VERDICT_TOKEN:{path}={token}")
    for path, token in noncanonical.items():
        flags.append(
            f"NONCANONICAL_VERDICT_TOKEN:{path}={token}->{claims.get(path)}"
        )
    if len(set(claims.values())) > 1:
        detail = ",".join(f"{p}={v}" for p, v in sorted(claims.items()))
        flags.append(f"VERDICT_FIELD_DIVERGENCE:{detail}")
    flags.extend(_collect_epistemic_flags(response))

    prior = str(response.get("effective_verdict") or response.get("verdict") or "")
    if flags:
        response["effective_verdict"] = HOLD
        response["reason_code"] = REASON_HOLD
        response["next_action"] = NEXT_HOLD
        response["status"] = STATUS_COMPLETED
        response["execution_state"] = "AWAIT_INPUT"
        response["status_scope"] = "execution"
        response["hold_required"] = True
        reasons = response.get("reasons")
        if not isinstance(reasons, list):
            reasons = []
            response["reasons"] = reasons
        if not any(str(r).startswith("INCONSISTENT_STATE") for r in reasons):
            reasons.insert(0, f"INCONSISTENT_STATE: {'; '.join(flags)}")
        meta = response.get("meta")
        if not isinstance(meta, dict):
            meta = {}
            response["meta"] = meta
        meta["reconciliation"] = {
            "inconsistent": True,
            "reason": "INCONSISTENT_VERDICT_STATE",
            "flags": flags,
            "claims": claims,
            "raw_tokens": raw_tokens,
            "unknown_tokens": unknown,
            "noncanonical_tokens": noncanonical,
            "observed_effective_verdict": prior,
            "reconciled_effective_verdict": HOLD,
            # Review 2026-09-22: the reconciler JUDGES, it never authorizes.
            # seal_eligible is a judgment-eligibility name; authority and
            # execution stay off here by construction (the authority service
            # is a separate, dependent PR).
            "seal_eligible": False,
            "authority_enabled": False,
            "execution_enabled": False,
            "reconciled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        cc = response.get("constitutional_check")
        if isinstance(cc, dict):
            cc["hold_required"] = True
            cc["hold_reason"] = f"INCONSISTENT_STATE: {flags[0]}"
        response["mutation_allowed"] = False
        response["seal_allowed"] = False
        _disable_authority_fields(response)
    else:
        # Honest hold_reason vocabulary: outer_verdict=... names the writer,
        # not the reason. Rewrite to the canonical field pair.
        cc = response.get("constitutional_check")
        if isinstance(cc, dict) and str(cc.get("hold_reason") or "").startswith(
            "outer_verdict="
        ):
            cc["hold_reason"] = (
                f"effective_verdict={response.get('effective_verdict')} "
                f"reason_code={response.get('reason_code')}"
            )

    # Point #2 (crack #2) — review 2026-09-22 item 5:
    # - INCONSISTENT payload → supplied next_safe_action must NOT survive:
    #   always derive from reconciled state; stash the supplied text in the
    #   receipt (meta.reconciliation.supplied_next_safe_action) for audit.
    # - CONSISTENT payload → handler-authored text is preserved (existing
    #   kernel contracts deliberately author it: session preflight, cognitive
    #   tier gate) but still passes the forbidden-terms guard when authority
    #   is off. Full derive-always deferred pending the vocabulary-owner
    #   decision — documented as a KNOWN LIMITATION in
    #   /root/forge_work/2026-09-22-arifos-mcp-gui-requirements-path.md.
    # Non-string next_safe_action values (structured tool pointers) are not
    # free text and are never rewritten.
    final = str(response.get("effective_verdict") or "")
    seal_off = response.get("seal_allowed") is False
    derived = _derive_safe_action(final, seal_allowed=not seal_off)
    holders: list[tuple[str, dict]] = [("response", response)]
    if isinstance(response.get("result"), dict):
        holders.append(("result", response["result"]))
    receipt = (response.get("meta") or {}).get("reconciliation")

    def _stash(key: str, original: str) -> None:
        if isinstance(receipt, dict):
            receipt.setdefault("supplied_next_safe_action", {})[key] = original

    for holder_name, holder in holders:
        text = holder.get("next_safe_action")
        if flags:
            if isinstance(text, dict):
                # Dict form ({action, tool, reason}) — preserve the shape,
                # neutralize the instruction (fixture evidence: action read
                # "Execute the capability..." on an authority-off HOLD).
                old = text.get("action")
                if isinstance(old, str) and old and old != derived:
                    _stash(f"{holder_name}.action", old)
                text["action"] = derived
                text["reason"] = "derived from reconciled state (Phase 0)"
            elif isinstance(text, str):
                if text and text != derived:
                    _stash(holder_name, text)
                holder["next_safe_action"] = derived
            else:
                holder["next_safe_action"] = derived
            continue
        # Consistent payload: preserve handler text, guard forbidden terms.
        if isinstance(text, str):
            if (final in _RESTRAINT_VERDICTS or seal_off) and _FORBIDDEN_IN_SAFE_ACTION.search(
                text
            ):
                holder["next_safe_action"] = derived
        elif isinstance(text, dict):
            old = text.get("action")
            if (
                isinstance(old, str)
                and (final in _RESTRAINT_VERDICTS or seal_off)
                and _FORBIDDEN_IN_SAFE_ACTION.search(old)
            ):
                text["action"] = derived

    return response


__all__ = [
    "EffectiveVerdict",
    "VERDICT_STATE_VERSION",
    "reconcile_decision_contract",
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
