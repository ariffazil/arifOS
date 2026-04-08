"""
arifosmcp/runtime/continuity_contract.py — Shared cross-tool continuity contract.

This module seals public RuntimeEnvelope responses with a canonical continuity
surface so every tool exposes the same identity, session, authorization, and
handoff semantics.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from arifosmcp.runtime.models import ClaimStatus, RuntimeEnvelope
from arifosmcp.runtime.sessions import (
    get_session_continuity_state,
    set_session_continuity_state,
)

logger = logging.getLogger(__name__)

CONTINUITY_CONTRACT_VERSION = "0.1.0"
_RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3, "sovereign": 4}


def seal_runtime_envelope(
    envelope: RuntimeEnvelope,
    tool_id: str,
    *,
    input_payload: dict[str, Any] | None = None,
    mode: str | None = None,
    output_options: dict[str, Any] | None = None,
) -> RuntimeEnvelope | dict[str, Any]:
    """
    Attach the canonical continuity contract to a RuntimeEnvelope.

    The seal is idempotent for the same tool/contract version pair.
    
    NEW (2026-04-06): If output_options is provided, returns clean formatted output
    following the 3-tier clarity model (operator/system/forensic views).
    """

    existing_handoff = getattr(envelope, "handoff", None) or {}
    if (
        getattr(envelope, "contract_version", None) == CONTINUITY_CONTRACT_VERSION
        and existing_handoff.get("produced_by") == tool_id
        and not output_options  # Don't short-circuit if formatting requested
    ):
        return envelope

    # ═══════════════════════════════════════════════════════════════════════
    # PATCH (2026-04-06): Fix canonical_tool_name
    # Set both canonical_tool_name AND override tool field to prevent legacy leakage
    # ═══════════════════════════════════════════════════════════════════════
    envelope.canonical_tool_name = tool_id
    envelope.tool = tool_id  # Override any legacy internal name
    
    # Sanitize payload to remove legacy name leakage
    if isinstance(envelope.payload, dict):
        envelope.payload.pop("internal_tool_name", None)
        envelope.payload.pop("backend_tool_name", None)
        envelope.payload["canonical_tool_name"] = tool_id

    # ═══════════════════════════════════════════════════════════════════════
    # NEW (2026-04-06): 3-Tier Output Model
    # If output_options specified, return clean formatted output instead of raw envelope
    # ═══════════════════════════════════════════════════════════════════════
    if output_options:
        from arifosmcp.runtime.output_formatter import format_output
        return format_output(envelope, output_options)

    payload = _as_dict(envelope.payload)
    input_payload = dict(input_payload or {})
    session_id = envelope.session_id or input_payload.get("session_id") or "global"
    previous_state = get_session_continuity_state(session_id) or {}

    # ── Task Ψ3: State Hash Enforcement (Continuity Phase) ─────────────
    # If we have a previous state, verify its hash before generating next state
    prev_state_data = previous_state.get("state")
    prev_hash = previous_state.get("state_hash")
    state_integrity = "VALID"
    if prev_state_data and prev_hash:
        recomputed = _hash_dict(prev_state_data)
        if recomputed != prev_hash:
            logger.error(f"Ψ-BREACH: State hash mismatch for session {session_id}!")
            state_integrity = "FAILED"
        else:
            logger.info(f"Ψ-VERIFIED: State hash check PASS for session {session_id}")

    declared_identity = _build_declared_identity(envelope, payload, input_payload, previous_state)
    verified_identity = _build_verified_identity(envelope, payload, previous_state)
    session_binding = _build_session_binding(
        envelope, payload, input_payload, previous_state, session_id, tool_id
    )
    authorization = _build_authorization(
        envelope, payload, input_payload, previous_state, mode
    )
    policy_checks = _build_policy_checks(envelope, payload)
    governance_closure = _build_governance_closure(envelope, payload)
    reasoning = _build_reasoning_state(envelope, payload)

    state = {
        "session": session_binding,
        "declared_identity": declared_identity,
        "verified_identity": verified_identity,
        "authorization": authorization,
        "governance_closure": governance_closure,
        "policy_checks": policy_checks,
        "reasoning": reasoning,
    }

    state_hash = _hash_dict(state)
    transitions = _compute_transitions(previous_state.get("state"), state)
    state_origin = {
        "produced_at": datetime.now(timezone.utc).isoformat(),
        "produced_by": tool_id,
        "source_of_truth": "canonical_runtime_state",
    }
    handoff = {
        "handoff_status": "valid" if envelope.ok else "restricted",
        "produced_by": tool_id,
        "consumable_by": list(envelope.allowed_next_tools or []),
        "state_hash": f"sha256:{state_hash}",
        "issued_at": state_origin["produced_at"],
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
        "trace_id": envelope.trace_id,
        "parent_trace_id": _parent_trace_id(envelope),
    }
    diagnostics = _build_diagnostics(envelope, payload, transitions, state_integrity)
    operator_summary = _build_operator_summary(
        declared_identity,
        verified_identity,
        session_binding,
        authorization,
        handoff,
        diagnostics,
        governance_closure,
    )

    envelope.contract_version = CONTINUITY_CONTRACT_VERSION
    envelope.operator_summary = operator_summary
    envelope.state = state
    envelope.state_origin = state_origin
    envelope.transitions = transitions
    envelope.handoff = handoff
    envelope.diagnostics = diagnostics

    payload.setdefault(
        "continuity",
        {
            "contract_version": CONTINUITY_CONTRACT_VERSION,
            "state": state,
            "handoff": handoff,
        },
    )
    envelope.payload = payload

    set_session_continuity_state(
        session_id,
        {
            "contract_version": CONTINUITY_CONTRACT_VERSION,
            "tool": tool_id,
            "state": state,
            "state_hash": state_hash,
            "trace_id": envelope.trace_id,
            "parent_trace_id": _parent_trace_id(envelope),
        },
    )
    return envelope


def _build_declared_identity(
    envelope: RuntimeEnvelope,
    payload: dict[str, Any],
    input_payload: dict[str, Any],
    previous_state: dict[str, Any],
) -> dict[str, Any]:
    prev = _nested_dict(previous_state, "state", "declared_identity")
    actor_id = (
        _deep_get(payload, "result", "declared_actor_id")
        or _deep_get(payload, "declared_actor_id")
        or _deep_get(payload, "provenance", "actor_id")
        or _deep_get(payload, "decision_packet", "provenance", "actor_id")
        or input_payload.get("actor_id")
        or input_payload.get("declared_name")
        or envelope.authority.actor_id
        or prev.get("declared_actor_id")
        or "anonymous"
    )
    return {
        "declared_actor_id": actor_id,
        "declared_name": input_payload.get("declared_name") or actor_id,
        "claim_source": "request" if actor_id != "anonymous" else "anonymous",
    }


def _build_verified_identity(
    envelope: RuntimeEnvelope,
    payload: dict[str, Any],
    previous_state: dict[str, Any],
) -> dict[str, Any]:
    prev = _nested_dict(previous_state, "state", "verified_identity")
    verification_status = (
        _deep_get(payload, "result", "base_identity", "verification_status")
        or _deep_get(payload, "base_identity", "verification_status")
        or _deep_get(payload, "identity", "verification_status")
        or prev.get("identity_verification_state")
        or "unverified"
    )
    verified_actor_id = (
        _deep_get(payload, "result", "verified_actor_id")
        or _deep_get(payload, "verified_actor_id")
        or _deep_get(payload, "provenance", "verified_actor_id")
        or _deep_get(payload, "decision_packet", "provenance", "verified_actor_id")
        or prev.get("verified_actor_id")
    )
    if (
        not verified_actor_id
        and envelope.authority.claim_status == ClaimStatus.VERIFIED
        and envelope.authority.actor_id != "anonymous"
    ):
        verified_actor_id = envelope.authority.actor_id

    return {
        "verified_actor_id": verified_actor_id,
        "identity_verification_state": verification_status,
        "verification_source": (
            _deep_get(payload, "result", "base_identity", "verification_source")
            or _deep_get(payload, "base_identity", "verification_source")
            or "none"
        ),
        "verification_confidence": _verification_confidence(verification_status),
    }


def _build_session_binding(
    envelope: RuntimeEnvelope,
    payload: dict[str, Any],
    input_payload: dict[str, Any],
    previous_state: dict[str, Any],
    session_id: str,
    tool_id: str,
) -> dict[str, Any]:
    prev = _nested_dict(previous_state, "state", "session")
    continuity_version = int(prev.get("continuity_version", 0)) + 1
    transport_session_id = (
        _deep_get(payload, "result", "transport_session_id")
        or _deep_get(payload, "transport_session_id")
        or input_payload.get("session_id")
        or session_id
    )
    anchor_state = envelope.anchor_state or prev.get("anchor_state")
    binding_state = "bound"
    if session_id == "global":
        binding_state = "global_fallback"
    elif anchor_state == "denied":
        binding_state = "unbound"

    return {
        "session_id": session_id,
        "anchor_id": prev.get("anchor_id") or f"anch-{session_id}",
        "continuity_version": continuity_version,
        "transport_session_id": transport_session_id,
        "resolved_session_id": session_id,
        "session_binding_state": binding_state,
        "anchor_state": anchor_state,
        "continuity_status": "stable" if envelope.ok else "degraded",
        "previous_tool": previous_state.get("tool"),
        "current_tool": tool_id,
        "trace_id": envelope.trace_id,
        "parent_trace_id": _parent_trace_id(envelope),
    }


def _build_authorization(
    envelope: RuntimeEnvelope,
    payload: dict[str, Any],
    input_payload: dict[str, Any],
    previous_state: dict[str, Any],
    mode: str | None,
) -> dict[str, Any]:
    prev = _nested_dict(previous_state, "state", "authorization")
    auth_context = _as_dict(envelope.auth_context)
    boundary = (
        _deep_get(payload, "result", "self_claim_boundary")
        or _deep_get(payload, "self_claim_boundary")
        or _deep_get(payload, "identity", "self_claim_boundary")
        or {}
    )
    if not isinstance(boundary, dict):
        boundary = {}
    tools_boundary = _as_dict(boundary.get("tools"))
    identity_boundary = _as_dict(boundary.get("identity"))
    granted_scope = (
        _deep_get(payload, "result", "scope", "granted")
        or _deep_get(payload, "scope", "granted")
        or auth_context.get("approval_scope")
        or envelope.authority.approval_scope
        or prev.get("granted_scope")
        or []
    )
    if isinstance(granted_scope, str):
        granted_scope = [granted_scope]

    authorization = {
        "bound_role": (
            _deep_get(payload, "result", "bound_role")
            or _deep_get(payload, "bound_role")
            or _deep_get(payload, "bound_session", "bound_role")
            or prev.get("bound_role")
            or envelope.authority.level.value
        ),
        "trust_tier": identity_boundary.get("trust_tier")
        or prev.get("trust_tier")
        or _derive_trust_tier(envelope),
        "granted_scope": granted_scope,
        "max_risk_tier": tools_boundary.get("max_risk_tier")
        or prev.get("max_risk_tier")
        or envelope.risk_class.value,
        "allowed_modes": tools_boundary.get("allowed_modes")
        or prev.get("allowed_modes")
        or envelope.next_allowed_modes
        or ([mode] if mode else []),
        "authorization_state": (
            "bounded"
            if envelope.authority.actor_id == "anonymous"
            else "active"
        ),
    }
    return authorization


def _build_policy_checks(envelope: RuntimeEnvelope, payload: dict[str, Any]) -> dict[str, Any]:
    policy = _as_dict(envelope.policy)
    floors_checked = policy.get("floors_checked") or _deep_get(payload, "audit", "floors_checked") or []
    floors_failed = policy.get("floors_failed") or _deep_get(payload, "audit", "floors_failed") or []
    floors_failed = [floor for floor in floors_failed if floor]
    return {
        "floors_checked": floors_checked,
        "floors_failed": floors_failed,
        "injection_score": policy.get("injection_score", 0.0),
        "witness_required": policy.get("witness_required", False),
    }


def _build_governance_closure(envelope: RuntimeEnvelope, payload: dict[str, Any]) -> dict[str, Any]:
    quad_witness_valid = _deep_get(payload, "data", "quad_witness_valid")
    if quad_witness_valid is None:
        quad_witness_valid = _deep_get(payload, "quad_witness_valid")
    operational_status = "pass" if envelope.ok else "restricted"
    proof_status = "complete" if quad_witness_valid is True else "incomplete"
    return {
        "operational_status": operational_status,
        "proof_status": proof_status,
        "verdict": envelope.verdict_detail.code.value if envelope.verdict_detail else envelope.verdict.value,
    }


def _build_reasoning_state(envelope: RuntimeEnvelope, payload: dict[str, Any]) -> dict[str, Any]:
    telemetry = _as_dict(envelope.metrics.telemetry)
    data = _as_dict(payload.get("data"))
    return {
        "reasoning_quality_state": "stable"
        if telemetry.get("confidence", 0.0) >= 0.7
        else "caution",
        "confidence": telemetry.get("confidence", 0.0),
        "entropy_delta": telemetry.get("ds", 0.0),
        "coherence": data.get("coherence") or payload.get("coherence"),
        "session_continuity": data.get("session_continuity") or payload.get("session_continuity"),
    }


def _compute_transitions(previous_state: dict[str, Any] | None, current_state: dict[str, Any]) -> list[dict[str, Any]]:
    if not previous_state:
        return [
            {
                "type": "observed_update",
                "field": "state.session.continuity_version",
                "from": 0,
                "to": current_state["session"]["continuity_version"],
                "reason": "initial continuity seal",
            }
        ]

    transitions: list[dict[str, Any]] = []
    prev_auth = _nested_dict(previous_state, "authorization")
    curr_auth = _nested_dict(current_state, "authorization")
    if prev_auth and curr_auth:
        for field in ("bound_role", "trust_tier", "granted_scope", "max_risk_tier", "allowed_modes"):
            prev_value = prev_auth.get(field)
            curr_value = curr_auth.get(field)
            if prev_value != curr_value:
                transitions.append(
                    {
                        "type": "authority_transition",
                        "field": f"state.authorization.{field}",
                        "from": prev_value,
                        "to": curr_value,
                        "reason": "authorization snapshot changed",
                    }
                )

    prev_tool = _nested_dict(previous_state, "session").get("current_tool")
    curr_tool = _nested_dict(current_state, "session").get("current_tool")
    if prev_tool != curr_tool:
        transitions.append(
            {
                "type": "observed_update",
                "field": "state.session.current_tool",
                "from": prev_tool,
                "to": curr_tool,
                "reason": "tool handoff completed",
            }
        )
    return transitions


def _build_diagnostics(
    envelope: RuntimeEnvelope,
    payload: dict[str, Any],
    transitions: list[dict[str, Any]],
    state_integrity: str = "VALID",
) -> dict[str, Any]:
    telemetry = _as_dict(envelope.metrics.telemetry)
    entropy = payload.get("entropy") or {}
    privilege_drift = any(t["type"] == "authority_transition" for t in transitions)
    return {
        "hard_guardrails": {
            "typed_error_code": envelope.code,
            "floors_failed": _as_dict(envelope.policy).get("floors_failed", []),
            "privilege_drift_detected": privilege_drift,
            "state_integrity": state_integrity,
        },
        "advisory_signals": {
            "warnings": list(payload.get("warnings") or []),
            "machine_status": envelope.machine_status.value,
            "confidence": telemetry.get("confidence", 0.0),
            "entropy": entropy,
        },
        "symbolic_metrics": {
            "peace2": telemetry.get("peace2"),
            "psi_le": telemetry.get("psi_le"),
            "g_star": telemetry.get("G_star"),
        },
        "interpretation_warnings": [
            "Session binding does not imply verified identity.",
            "Authorization scope does not imply trust elevation.",
            "Operational success does not imply full governance proof.",
        ],
    }


def _build_operator_summary(
    declared_identity: dict[str, Any],
    verified_identity: dict[str, Any],
    session_binding: dict[str, Any],
    authorization: dict[str, Any],
    handoff: dict[str, Any],
    diagnostics: dict[str, Any],
    governance_closure: dict[str, Any],
) -> dict[str, Any]:
    verified_actor = verified_identity.get("verified_actor_id")
    if verified_actor:
        identity_text = f"Declared as {declared_identity['declared_actor_id']}; verified as {verified_actor}"
    else:
        identity_text = f"Declared as {declared_identity['declared_actor_id']}; not verified"

    authority = authorization.get("allowed_modes") or []
    authority_text = f"{', '.join(authority) if authority else 'no'} modes, max risk {authorization.get('max_risk_tier', 'unknown')}"

    return {
        "identity": identity_text,
        "session": f"{session_binding.get('session_binding_state', 'unknown')} and {session_binding.get('continuity_status', 'unknown')}",
        "authority": authority_text,
        "privilege_drift": "Detected"
        if diagnostics["hard_guardrails"]["privilege_drift_detected"]
        else "None",
        "next_action": (handoff.get("consumable_by") or [None])[0],
        "governance": f"{governance_closure['operational_status']} / proof {governance_closure['proof_status']}",
    }


def _derive_trust_tier(envelope: RuntimeEnvelope) -> str:
    if envelope.authority.claim_status == ClaimStatus.VERIFIED:
        return "verified"
    if envelope.authority.claim_status in {ClaimStatus.ANCHORED, ClaimStatus.CLAIMED}:
        return "bounded"
    return "untrusted"


def _verification_confidence(status: str) -> float:
    mapping = {
        "verified": 1.0,
        "runtime_attested": 0.9,
        "mood_matched": 0.75,
        "claimed_only": 0.4,
        "identity_mismatch": 0.1,
        "unverified": 0.0,
    }
    return mapping.get(status, 0.0)


def _parent_trace_id(envelope: RuntimeEnvelope) -> str | None:
    trace = _as_dict(envelope.trace)
    return trace.get("parent_trace_id")


def _deep_get(data: Any, *path: str) -> Any:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _nested_dict(data: Any, *path: str) -> dict[str, Any]:
    result = _deep_get(data, *path)
    return result if isinstance(result, dict) else {}


def _as_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    return {}


def _hash_dict(value: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()
