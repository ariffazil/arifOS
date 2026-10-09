"""
arifOS V2 Response Envelope — Shared builder for all 8 canonical tools.

Injects deterministic top-level fields (canonical_verdict, authority_scope,
receipt_state, execution_state) into every tool response. Used as middleware
in server.py, following the AKAL wrapper pattern.

Source of truth: capability_registry.json for capability_id mapping.
V2 envelope schema: arifOS.response.v2 at schema/response.envelope.schema.json.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Cache the capability registry at module level
_CAPABILITY_REGISTRY: dict[str, dict[str, Any]] | None = None
_CAPABILITY_BY_TOOL: dict[str, dict[str, Any]] | None = None


def _load_capability_registry() -> tuple[dict[str, Any], dict[str, Any]]:
    """Load and cache the capability registry. Returns (registry, by_tool)."""
    global _CAPABILITY_REGISTRY, _CAPABILITY_BY_TOOL
    if _CAPABILITY_REGISTRY is None:
        path = Path(__file__).resolve().parent.parent / "abi" / "capability_registry.json"
        try:
            with open(path) as f:
                _CAPABILITY_REGISTRY = json.load(f)
            _CAPABILITY_BY_TOOL = {}
            for cap in _CAPABILITY_REGISTRY.get("capabilities", []):
                tool_name = cap.get("provider", {}).get("tool", "")
                if tool_name:
                    _CAPABILITY_BY_TOOL[tool_name] = cap
        except Exception as e:
            logger.warning("Failed to load capability registry: %s", e)
            _CAPABILITY_REGISTRY = {"capabilities": []}
            _CAPABILITY_BY_TOOL = {}
    return _CAPABILITY_REGISTRY, _CAPABILITY_BY_TOOL


def _get_capability_id(tool_name: str) -> str:
    """Resolve capability_id from tool name using capability_registry.json."""
    _, by_tool = _load_capability_registry()
    cap = by_tool.get(tool_name)
    if cap:
        return cap.get("capability_id", f"unknown.{tool_name}")
    return f"unknown.{tool_name}"


# ── Verdict extraction helpers ──────────────────────────────────────────────


# ── Trinity: internal telemetry (4-class fidelity preserved) ──────────────
# Path 3 architectural separation — see v2_envelope.py:251 for execution_state
# and verdict.py:222 for legacy-strip list. This split prevents the 4→2
# vocabulary collapse that was previously hard-coded here.
_INTERNAL_VERDICTS_4CLASS = (
    "SEAL",
    "SABAR",
    "VOID",
    "HOLD",
    "HOLD_888",
    "OBSERVE_ONLY",
)


def _extract_internal_telemetry(response: dict[str, Any]) -> str:
    """Extract internal 4-class effective_verdict (full fidelity).

    Priority order: effective_verdict → top-level verdict → result.verdict → status → session.verdict → HOLD

    Returns one of {SEAL, SABAR, VOID, HOLD, HOLD_888, OBSERVE_ONLY} — the
    kernel's native 4-class internal vocabulary. The 2-class public envelope
    is derived separately by _extract_public_transport_envelope.
    """
    top_ev = response.get("effective_verdict") or response.get("verdict")
    if top_ev and str(top_ev).upper() in _INTERNAL_VERDICTS_4CLASS:
        return str(top_ev).upper()

    # Check result sub-object (deepest signal)
    result = response.get("result")
    if isinstance(result, dict):
        rv = result.get("verdict")
        if rv and str(rv).upper() in _INTERNAL_VERDICTS_4CLASS:
            return str(rv).upper()

    # Check session object
    session = response.get("session")
    if isinstance(session, dict):
        sv = session.get("verdict")
        if sv and str(sv).upper() in _INTERNAL_VERDICTS_4CLASS:
            return str(sv).upper()

    # Check status for fallback (last resort).
    # P0 G1: status=pending no longer means HOLD — only blocked/failed map.
    status = str(response.get("status", "")).lower()
    if status in ("blocked", "failed", "error"):
        return "VOID"
    if status in ("completed", "ok"):
        # Prefer existing effective_verdict if present; else HOLD (unknown)
        return "HOLD"

    return "HOLD"


def _extract_public_transport_envelope(response: dict[str, Any]) -> str:
    """Derive public 2-class transport envelope from internal 4-class.

    Public surface: PROCEED (SEAL|SABAR) | DENY (VOID|HOLD|HOLD_888|OBSERVE_ONLY).
    This is a DERIVATION, not a replacement — internal telemetry preserves
    4-class fidelity separately.
    """
    internal = _extract_internal_telemetry(response)
    if internal in ("SEAL", "SABAR"):
        return "PROCEED"
    return "DENY"


# Backward-compat alias — keeps existing callers working without modification
_extract_canonical_verdict = _extract_public_transport_envelope


def _extract_authority_scope(response: dict[str, Any]) -> str:
    """Extract authority scope from response or session."""
    # Check session
    session = response.get("session")
    if isinstance(session, dict):
        authority = session.get("authority", "")
        if authority in ("OBSERVE_ONLY", "LIMITED_MUTATE", "FULL"):
            return authority

    # Check actor
    actor = response.get("actor")
    if isinstance(actor, dict):
        level = actor.get("authority_level", "")
        if level == "ANONYMOUS":
            return "OBSERVE_ONLY"

    # Check meta
    meta = response.get("meta", {}) if isinstance(response.get("meta"), dict) else {}
    mode = meta.get("authority_mode", "")
    if mode in ("OBSERVE_ONLY", "LIMITED_MUTATE", "FULL"):
        return mode

    return "OBSERVE_ONLY"


def _extract_receipt_state(response: dict[str, Any]) -> str:
    """Extract receipt state based on whether a seal was written."""
    result = response.get("result", {}) if isinstance(response.get("result"), dict) else {}
    # If seal was involved and succeeded
    vault_entry = result.get("vault_entry_id") or result.get("merkle_root")
    if vault_entry:
        return "SEALED"

    # Check if session has been sealed
    session = response.get("session", {}) if isinstance(response.get("session"), dict) else {}
    if session.get("verdict") == "SEAL":
        return "SEALED"

    # Check if there's a receipt_id
    receipt_id = result.get("receipt_id")
    if receipt_id:
        return "SEALED"

    return "UNSEALED"


def _extract_reason_code(
    tool_name: str,
    canonical_verdict: str,
    response: dict[str, Any],
) -> str:
    """Extract or derive a machine-readable reason code."""
    # Check top-level response first
    top_rc = response.get("reason_code")
    if top_rc:
        return str(top_rc)

    # Check for existing reason codes in meta
    meta = response.get("meta", {}) if isinstance(response.get("meta"), dict) else {}
    reason_code = meta.get("reason_code") or meta.get("reason", "")
    if reason_code:
        return str(reason_code)

    # Check result for reason
    result = response.get("result", {}) if isinstance(response.get("result"), dict) else {}
    reason = result.get("reason", "")
    if reason:
        return str(reason)

    # Derive from verdict + tool
    if canonical_verdict == "HOLD":
        if tool_name == "arif_init":
            return "IDENTITY_UNVERIFIED"
        elif tool_name == "arif_forge":
            return "AUTHORITY_INSUFFICIENT"
        elif tool_name == "arif_judge":
            return "CONSTITUTIONAL_BLOCK"
        else:
            return "HOLD_NO_REASON"

    return "OK"


def _extract_can_mutate(canonical_verdict: str, authority_scope: str) -> bool:
    """Derive mutate permission from verdict + scope.

    UNCHANGED (2026-09-19 claim_kernel wiring is additive and lives in
    `_apply_mutation_justification_gate`, below). Authority answers WHO may
    mutate; it does not answer WHAT KIND OF CLAIM is being used as the reason.
    That second, orthogonal term is added at the envelope level so this
    function's semantics stay frozen.
    """
    if canonical_verdict in ("DENY", "VOID"):
        return False
    if canonical_verdict == "HOLD":
        return False
    return authority_scope in ("LIMITED_MUTATE", "FULL")


# ── Justification-class gate (claim_kernel bridge, additive 2026-09-19) ─────
# AuthorityGranted ∧ ScopeMatches ∧ TargetPermitted ∧ BoundaryActive says
# nothing about the KIND of claim offered as the reason for the write. A
# narrative may be published; it may never be the sole justification for a
# mutation. This gate supplies that term and can only DOWNGRADE can_mutate.

_CLAIM_TEXT_KEYS = ("claim_text", "justification", "intent_summary", "candidate")
_CLAIM_CLASS_KEYS = ("claim_class", "declared_claim_class", "explanatory_class")


def _extract_claim_justification(response: dict[str, Any]) -> dict[str, Any]:
    """Find the justification text + declared class carried by a response.

    Declaration paths, first hit wins (see core/claim_class_gate docstring):
    top level → meta → result → result.evidence → evidence → session axis.
    Absence is NOT an error here: the gate below fails closed on it.
    """
    meta_raw = response.get("meta")
    meta: dict[str, Any] = meta_raw if isinstance(meta_raw, dict) else {}
    result_raw = response.get("result")
    result: dict[str, Any] = result_raw if isinstance(result_raw, dict) else {}
    result_ev_raw = result.get("evidence")
    result_evidence: dict[str, Any] = result_ev_raw if isinstance(result_ev_raw, dict) else {}
    top_ev_raw = response.get("evidence")
    top_evidence: dict[str, Any] = top_ev_raw if isinstance(top_ev_raw, dict) else {}
    session_raw = response.get("session")
    session: dict[str, Any] = session_raw if isinstance(session_raw, dict) else {}

    declared: str | None = None
    decl_source: str | None = None
    for container, name in (
        (response, "response"),
        (meta, "response.meta"),
        (result, "response.result"),
        (result_evidence, "response.result.evidence"),
        (top_evidence, "response.evidence"),
        (session, "response.session"),
    ):
        for key in _CLAIM_CLASS_KEYS:
            value = container.get(key)
            if value:
                declared = str(value)
                decl_source = f"{name}.{key}"
                break
        if declared:
            break

    if not declared:
        # Session epistemic axis (axis 2) — declared out-of-band at init/judge.
        try:
            from arifosmcp.core.epistemic_state import get_claim_class

            session_id = (
                response.get("session_id")
                or result.get("session_id")
                or session.get("session_id")
            )
            axis_value = get_claim_class(session_id) if session_id else None
            if axis_value:
                declared = axis_value
                decl_source = "epistemic_state.claim_class"
        except Exception:
            pass

    text: str = ""
    text_source: str | None = None
    for container, name in (
        (meta, "response.meta"),
        (result, "response.result"),
        (result_evidence, "response.result.evidence"),
        (top_evidence, "response.evidence"),
        (response, "response"),
    ):
        for key in _CLAIM_TEXT_KEYS:
            value = container.get(key)
            if isinstance(value, str) and value.strip():
                text = value
                text_source = f"{name}.{key}"
                break
            if isinstance(value, dict) and value:
                text = json.dumps(value, sort_keys=True, default=str)[:4000]
                text_source = f"{name}.{key}(dict)"
                break
        if text:
            break

    if not text:
        reasons = result.get("reasons") or response.get("reasons")
        if isinstance(reasons, list) and reasons:
            text = " | ".join(str(r) for r in reasons[:5])
            text_source = "reasons[]"

    return {
        "text": text,
        "declared": declared,
        "class_source": decl_source,
        "text_source": text_source,
    }


def _apply_mutation_justification_gate(
    can_mutate: bool,
    response: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    """Add the missing term: justification class must be action-eligible.

    MONOTONE-DOWNWARD BY CONSTRUCTION — returns the input unchanged when the
    gate allows, and False when it denies. It can never grant can_mutate.

    Returns (can_mutate, gate_receipt). Never raises.
    """
    justification = _extract_claim_justification(response)
    session_id: str | None = None
    for _candidate in (
        response.get("session_id"),
        (response.get("result") or {}).get("session_id")
        if isinstance(response.get("result"), dict)
        else None,
        (response.get("session") or {}).get("session_id")
        if isinstance(response.get("session"), dict)
        else None,
    ):
        if isinstance(_candidate, str) and _candidate:
            session_id = _candidate
            break

    try:
        from arifosmcp.core.claim_class_gate import evaluate as _evaluate_claim_class

        gate = _evaluate_claim_class(
            justification["text"],
            justification["declared"],
            session_id=session_id,
            source="v2_envelope.justification",
        )
    except Exception as exc:
        # Import/shape failure must not silently OPEN the gate.
        can_mutate = False
        gate = {
            "gate": "claim_class_gate/v1",
            "kernel_available": False,
            "eligible": False,
            "allowed_for_mutation": False,
            "declared": justification["declared"] or "UNCLASSIFIED",
            "reasons": [
                f"CLAIM_CLASS_GATE_UNAVAILABLE: {type(exc).__name__}: {exc}. Fail-closed."
            ],
        }

    receipt = {
        "gate": gate.get("gate", "claim_class_gate/v1"),
        "claim_class": gate.get("class") or gate.get("declared") or "UNCLASSIFIED",
        "inferred_class": gate.get("inferred"),
        "agree": gate.get("agree"),
        "eligible": bool(gate.get("allowed_for_mutation")),
        "reasons": list(gate.get("reasons", []) or []),
        "class_source": justification["class_source"],
        "text_source": justification["text_source"],
        "base_can_mutate": can_mutate,
    }

    if not can_mutate:
        return can_mutate, receipt  # already denied upstream — nothing to add

    if receipt["eligible"]:
        return can_mutate, receipt

    if not receipt["reasons"]:
        receipt["reasons"] = [
            "CLAIM_CLASS_GATE: verdict authorises a mutation but carries no "
            "action-eligible claim_class. Publishable, not mutation-justifying."
        ]
    return False, receipt


def _extract_can_claim_success(
    canonical_verdict: str,
    execution_state: str,
    response: dict[str, Any] | None = None,
) -> bool:
    """Derive success claim permission.

    INVARIANT: can_claim_success MUST BE FALSE under HOLD, DENY, VOID, FAILED,
    or when hold_required is True.
    """
    if canonical_verdict in ("DENY", "VOID", "HOLD", "HOLD_888"):
        return False
    if execution_state in ("FAILED", "BLOCKED", "CANCELLED"):
        return False
    if response and (response.get("hold_required") is True or response.get("effective_verdict") in ("HOLD", "VOID", "HOLD_888")):
        return False
    if canonical_verdict == "PROCEED" and execution_state == "COMPLETED":
        return True
    return False


# ── Main V2 envelope builder ───────────────────────────────────────────────


# Map of known canonical tool names for validation
CANONICAL_TOOL_NAMES = frozenset(
    {
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_memory",
        "arif_judge",
        "arif_forge",
        "arif_seal",
    }
)


def build_v2_envelope(tool_name: str, response: dict[str, Any]) -> dict[str, Any]:
    """Wrap a tool response with the V2 envelope.

    The V2 envelope is always the outermost layer. It adds deterministic
    top-level fields without modifying the tool-specific result data.

    Args:
        tool_name: The canonical tool name (e.g. 'arif_init')
        response: The raw response dict from the tool handler

    Returns:
        The response dict with V2 envelope fields injected at top level.
    """
    if not isinstance(response, dict):
        return response

    # Only wrap canonical tools
    if tool_name not in CANONICAL_TOOL_NAMES:
        return response

    # ── Trinity: execution_state derived DIRECTLY from internal effective_verdict ──
    # Closes Lifecycle Clobber — was: HOLD → "pending" (status) → "RUNNING" (state)
    # Now: HOLD → "AWAITING_INPUT" directly from effective_verdict.
    # Preserves 4-class fidelity: SEAL/SABAR/VOID/HOLD/HOLD_888/OBSERVE_ONLY
    _internal_verdict = _extract_internal_telemetry(response)
    # P0 2026-08-09 G1: execution_state = did the tool finish?
    # AWAITING_INPUT / AWAITING_IDENTITY belong in next_action + effective_verdict,
    # not as a fake "still running" lifecycle when the handler already returned.
    _EXECUTION_STATE_FROM_VERDICT = {
        "SEAL": "COMPLETED",
        "SABAR": "COMPLETED",
        "VOID": "FAILED",
        "HOLD": "COMPLETED",
        "HOLD_888": "COMPLETED",
        "OBSERVE_ONLY": "COMPLETED",
    }
    # Prefer explicit execution_state from response if already set correctly
    _pre = str(response.get("execution_state") or "").upper()
    if _pre in (
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        "RUNNING",
        "READY",
        "NOT_REQUESTED",
        "AWAITING_INPUT",
        "BLOCKED",
        "AWAITING_IDENTITY",
    ):
        # Normalize legacy AWAITING_* → COMPLETED when a result payload exists
        if _pre in ("AWAITING_INPUT", "AWAITING_IDENTITY", "BLOCKED") and (
            response.get("result") is not None
            or str(response.get("status") or "").lower()
            in ("ok", "completed", "pending")
        ):
            execution_state = (
                "FAILED" if _internal_verdict == "VOID" else "COMPLETED"
            )
        else:
            execution_state = _pre if _pre not in ("AWAITING_INPUT", "AWAITING_IDENTITY") else "COMPLETED"
    else:
        execution_state = _EXECUTION_STATE_FROM_VERDICT.get(_internal_verdict, "COMPLETED")

    # Extract V2 fields from existing response
    canonical_verdict = _extract_canonical_verdict(response)
    authority_scope = _extract_authority_scope(response)
    receipt_state = _extract_receipt_state(response)
    capability_id = _get_capability_id(tool_name)
    reason_code = _extract_reason_code(tool_name, canonical_verdict, response)

    # Set permission flags
    can_mutate = _extract_can_mutate(canonical_verdict, authority_scope)
    # ── Justification-class term (additive 2026-09-19) ──────────────────────
    # Authority says WHO may mutate. This adds WHAT KIND OF CLAIM is offered as
    # the reason for the write. Monotone-downward: it can only deny.
    can_mutate, _claim_class_gate = _apply_mutation_justification_gate(can_mutate, response)
    can_claim_success = _extract_can_claim_success(canonical_verdict, execution_state, response)

    # Build the V2 envelope. Add as top-level fields directly
    # (the existing response already has 'status', 'result', 'meta' etc.)
    envelope = dict(response)

    # Inject V2 fields at top level (never override existing data)
    envelope.setdefault("schema_version", "2.0.0")
    envelope.setdefault("capability_id", capability_id)
    envelope.setdefault("implementation_tool", tool_name)
    # STEP 2 (2026-08-05): canonical_verdict REMOVED — effective_verdict is
    # the SINGLE authoritative root. All sub-signals are read-only echoes.
    # See /root/forge_work/2026-08-05/kernel-audit/ for before/after receipts.
    envelope.setdefault("reason_code", reason_code)
    envelope.setdefault("authority_scope", authority_scope)
    envelope.setdefault("receipt_state", receipt_state)
    envelope.setdefault("execution_state", execution_state)
    envelope.setdefault("can_continue_observing", True)
    # Justification-class denial is a hard downgrade: if the gate denied, the
    # flag is written False even if a handler pre-set can_mutate=True.
    if _claim_class_gate.get("base_can_mutate") and not _claim_class_gate.get("eligible"):
        envelope["can_mutate"] = False
    else:
        envelope.setdefault("can_mutate", can_mutate)
    envelope.setdefault("can_claim_success", can_claim_success)
    # ── Explanatory-class disclosure (additive 2026-09-19) ──────────────────
    # Every canonical response now declares WHAT KIND OF CLAIM justified it,
    # and whether that class is allowed to authorise a mutation.
    envelope.setdefault("claim_class", _claim_class_gate.get("claim_class", "UNCLASSIFIED"))
    envelope.setdefault("claim_class_verdict", _claim_class_gate)
    envelope.setdefault(
        "mutation_justification",
        {
            "allowed": bool(_claim_class_gate.get("eligible")),
            "claim_class": _claim_class_gate.get("claim_class"),
            "class_source": _claim_class_gate.get("class_source"),
            "text_source": _claim_class_gate.get("text_source"),
            "reasons": list(_claim_class_gate.get("reasons", []) or []),
            "gate": _claim_class_gate.get("gate"),
        },
    )

    # Extract facts/inferences/unknowns if result has them
    result = response.get("result", {})
    if isinstance(result, dict):
        envelope.setdefault("facts", result.get("facts", []))
        envelope.setdefault("inferences", result.get("inferences", []))
        envelope.setdefault("unknowns", result.get("unknowns", []))
        envelope.setdefault("warnings", result.get("warnings", []))
        envelope.setdefault("evidence_refs", result.get("evidence_refs", []))
        envelope.setdefault("recommended_next", result.get("recommended_next", []))

    # STEP 2 (2026-08-05): Strip canonical_verdict — it may have been injected
    # by internal tool handlers (tools.py, verbosity.py, judge.py, server.py).
    # effective_verdict is the single authoritative root.
    envelope.pop("canonical_verdict", None)

    return envelope
