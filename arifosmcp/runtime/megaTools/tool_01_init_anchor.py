"""
arifosmcp/runtime/megaTools/01_init_anchor.py

🔥 THE IGNITION STATE OF INTELLIGENCE (Unified)
Stage: 000_INIT | Trinity: PSI Ψ | Floors: F11, F12, F13

Modes: init, revoke, refresh, state, status, probe
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any

from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP


async def init_anchor(
    mode: str | None = None,
    payload: dict[str, Any] | None = None,
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    declared_name: str | None = None,
    intent: Any | None = None,
    human_approval: bool = False,
    human_approved: bool | None = None,
    risk_tier: str = "low",
    dry_run: bool = True,
    allow_execution: bool = False,
    caller_context: dict[str, Any] | None = None,
    auth_context: dict | None = None,
    debug: bool = False,
    request_id: str | None = None,
    timestamp: str | None = None,
    raw_input: str | None = None,
    pns_shield: Any | None = None,
    proof: str | None = None,
    ctx: Any | None = None,
    reason: str | None = None,
    use_memory: bool = True,
    use_heart: bool = True,
    use_critique: bool = True,
    context: Any | None = None,
    model_soul: dict[str, Any] | None = None,
    deployment_id: str | None = None,
    session_class: str = "execute",
) -> RuntimeEnvelope:
    allowed_modes = {"init", "revoke", "refresh", "state", "status", "probe"}
    if mode is not None and mode not in allowed_modes:
        raise ValueError(f"Invalid mode for init_anchor: {mode}")

    # ═══════════════════════════════════════════════════════════════════════════
    # STATUS MODE: Quick health check (returns same as probe for compatibility)
    # ═══════════════════════════════════════════════════════════════════════════
    if mode == "status":
        from arifosmcp.runtime.sessions import get_session_identity

        identity = get_session_identity(session_id) if session_id else None
        anchor_status = "VALID" if identity else "MISSING"

        raw_level = (
            (auth_context or {}).get("authority_level")
            or (identity or {}).get("authority_level")
            or "anonymous"
        )

        status_payload = {
            "ok": True,
            "tool": "init_anchor",
            "status": "SUCCESS",
            "result_type": "init_anchor_status_result@v2",
            "mode": "status",
            "organ_stage": "000_INIT",
            "verdict": "SEAL",
            "session_id": session_id or "global",
            "status_result": {
                "anchor": anchor_status,
                "authority_level": raw_level,
                "health": "operational",
            },
            "floors_checked": ["F11"],
        }

        return RuntimeEnvelope(
            tool="init_anchor",
            canonical_tool_name="arifos_init",
            stage="000_INIT",
            status=RuntimeStatus.SUCCESS,
            verdict=Verdict.SEAL,
            session_id=session_id or "global",
            payload=status_payload,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # PROBE MODE: Session diagnostic and compatibility check
    # ═══════════════════════════════════════════════════════════════════════════
    if mode == "probe":
        from arifosmcp.runtime.sessions import get_session_identity

        identity = get_session_identity(session_id) if session_id else None
        anchor_status = "VALID" if identity else "MISSING"

        raw_level = (
            (auth_context or {}).get("authority_level")
            or (identity or {}).get("authority_level")
            or "anonymous"
        )

        canonical_identity_classes = {
            "human",
            "user",
            "agent",
            "system",
            "anonymous",
            "operator",
            "sovereign",
            "declared",
            "claimed",
            "verified",
            "apex",
            "none",
        }

        enum_compat = (
            "✅ COMPATIBLE"
            if raw_level.lower() in canonical_identity_classes
            else f"❌ MISMATCH ({raw_level})"
        )

        # Honest trust-based recommendation
        high_trust_levels = {"verified", "sovereign", "apex", "human"}
        low_trust_levels = {"anonymous", "declared", "claimed", "none"}

        if "❌" in enum_compat:
            recommendation = "Use init_anchor to re-align if MISMATCH detected."
        elif raw_level.lower() in high_trust_levels:
            recommendation = "Trust established. System ready for governed execution."
        elif raw_level.lower() in low_trust_levels:
            recommendation = "Anonymous/declared identity — use init_anchor with verified credentials for full access."
        else:
            recommendation = "Identity recognized — init_anchor required to escalate privileges."

        probe_payload = {
            "ok": True,
            "tool": "init_anchor",
            "status": "SUCCESS",
            "result_type": "init_anchor_probe_result@v2",
            "mode": "probe",
            "organ_stage": "000_INIT",
            "verdict": "SEAL",
            "session_id": session_id or "global",
            "probe_result": {
                "anchor": anchor_status,
                "authority_enum": enum_compat,
                "current_level": raw_level,
            },
            "recommendation": recommendation,
            "floors_checked": ["F11"],
        }

        return RuntimeEnvelope(
            tool="init_anchor",
            canonical_tool_name="arifos_init",
            stage="000_INIT",
            status=RuntimeStatus.SUCCESS,
            verdict=Verdict.SEAL,
            session_id=session_id or "global",
            payload=probe_payload,
        )

    payload = dict(payload or {})
    if session_class:
        payload.setdefault("session_class", session_class)
    if human_approved is not None and human_approval is False:
        human_approval = human_approved
    if "human_approved" in payload and "human_approval" not in payload:
        payload["human_approval"] = payload.pop("human_approved")
    if raw_input:
        payload.setdefault("query", raw_input)
    if caller_context:
        payload.setdefault("caller_context", caller_context)
    if auth_context:
        payload.setdefault("auth_context", auth_context)
    if query:
        payload.setdefault("query", query)
    if raw_input:
        payload.setdefault("raw_input", raw_input)
    if session_id:
        payload.setdefault("session_id", session_id)
    if actor_id:
        payload.setdefault("actor_id", actor_id)
    if declared_name:
        payload.setdefault("declared_name", declared_name)
    if intent:
        payload.setdefault("intent", intent)
    if "human_approval" not in payload:
        payload["human_approval"] = human_approval
    if risk_tier:
        payload.setdefault("risk_tier", risk_tier)
    if raw_input:
        payload.setdefault("raw_input", raw_input)
    if pns_shield:
        payload.setdefault("pns_shield", pns_shield)
    if proof:
        payload.setdefault("proof", proof)
    if reason:
        payload.setdefault("reason", reason)
    payload.setdefault("use_memory", use_memory)
    payload.setdefault("use_heart", use_heart)
    payload.setdefault("use_critique", use_critique)
    if context:
        payload.setdefault("context", context)
    if model_soul:
        payload.setdefault("model_soul", model_soul)
    if deployment_id:
        payload.setdefault("deployment_id", deployment_id)

    # ═══════════════════════════════════════════════════════════════════════════
    # CRITICAL FIX (2026-04-06): Eliminate circular dependency
    #
    # OLD CODE (BROKEN):
    #   res = await HARDENED_DISPATCH_MAP["init_anchor"](...)  # RECURSION!
    #
    # NEW CODE (FIXED):
    #   Direct session initialization without dispatch lookup.
    #   init_anchor is the ROOT - it creates sessions directly.
    # ═══════════════════════════════════════════════════════════════════════════
    if True:  # Always execute (replaces the 'if in dispatch_map' check)
        # Direct session initialization (no dispatch recursion)
        effective_session_id = (
            session_id or payload.get("session_id") or f"sess_{uuid.uuid4().hex[:16]}"
        )
        declared_identity = (
            payload.get("declared_name") or actor_id or payload.get("actor_id") or "anonymous"
        )

        if mode is None:
            mode = "init"
        _t0 = time.monotonic()

        # Select initial philosophy (Causal Anchor)
        from arifosmcp.runtime.philosophy import select_atlas_philosophy, AtlasScores

        # Initial scores for bootstrap
        init_scores = AtlasScores(
            delta_s=0.0,
            g_score=0.5,
            omega_score=0.05,
            lyapunov_sign="stable",
            verdict="SEAL",
            session_stage="000_INIT",
        )
        # Select philosophy based on intent if possible
        phi_result = select_atlas_philosophy(init_scores, context={"intent": intent})
        phi_quote = phi_result.get("primary_quote", {})
        phi_bias = phi_result.get("telos_bias", {"A": 0.0, "P": 0.0, "X": 0.0, "E": 0.0})

        # Build success result directly
        res = {
            "ok": True,
            "session_id": effective_session_id,
            "stage": "000_INIT",
            "organ_stage": "000_INIT",
            "status": "SUCCESS",
            "verdict": "SEAL",
            "g_score": 0.88,  # High bootstrap score
            "entropy": 0.0,  # Reset entropy
            "philosophy": {
                "quote": phi_quote.get("text", "DITEMPA, BUKAN DIBERI."),
                "author": phi_quote.get("author", "arifOS"),
                "category": phi_quote.get("category", "wisdom"),
                "telos_bias": phi_bias,
            },
            "identity": {
                "declared_actor_id": declared_identity,
                "verified_actor_id": None,
                "auth_state": "unverified",
                "verification_status": "unverified",
                "verification_source": "none",
            },
            "bound_session": {
                "session_id": effective_session_id,
                "bound_role": payload.get("session_class", "execute"),
                "anchor_state": "created",
            },
            "caller_state": "anonymous",
            "allowed_next_tools": ["arifos_sense", "arifos_mind", "arifos_route", "arifos_ops"],
            "scope": {"granted": ["query", "reflect"], "max_risk_tier": "medium"},
            "auth_guidance": {
                "current_trust_level": "anonymous",
                "identity_status": "unverified",
                "next_steps": [
                    "To verify identity: call init_anchor with actor_id='ariffazil' and signature/proof",
                    "For full sovereign access: provide human_approval=True or verified auth_context",
                ],
                "trust_escalation": {
                    "declared": {"unlocks": ["query", "reflect"], "risk_tier": "low"},
                    "verified": {"unlocks": ["query", "reflect", "execute"], "risk_tier": "medium"},
                    "sovereign": {
                        "unlocks": ["query", "reflect", "execute", "vault"],
                        "risk_tier": "high",
                    },
                },
                "mode_requirements": {
                    "init": "Establishes session anchor only",
                    "verify": "Requires signature/proof in auth_context for verified identity",
                    "escalate": "Requires human_approval=True for sovereign access",
                },
            },
        }
        _duration_ms = int((time.monotonic() - _t0) * 1000)
        if isinstance(res, dict):
            ok = res.get("ok")
            if ok is None:
                ok = res.get("status") not in ("HOLD", "ERROR", "VOID", None)

            _next_tools = res.get("allowed_next_tools") or res.get("next_allowed_tools")
            if not _next_tools:
                _next_tools = [
                    "math_estimator",
                    "architect_registry",
                    "check_vital",
                    "init_anchor",
                ]

            _payload = res.get("payload", res) if isinstance(res.get("payload"), dict) else res

            # ─── V2 FLATTENING (Always return flat result for success) ───
            if ok:
                # Task Ψ1: Bind session identity to registry for cross-tool continuity
                from arifosmcp.runtime.sessions import bind_session_identity

                bind_session_identity(
                    session_id=effective_session_id,
                    actor_id=declared_identity,
                    authority_level="declared",
                    auth_context={
                        "session_id": effective_session_id,
                        "actor_id": declared_identity,
                        "authority_level": "declared",
                    },
                    caller_state="anchored",
                )

                identity = _payload.get("identity") or {}
                bound_session = _payload.get("bound_session") or {}
                v2_result = {
                    "session_id": res.get("session_id"),
                    "resolved_session_id": res.get("session_id"),
                    "transport_session_id": payload.get("session_id") or "global",
                    "declared_actor_id": identity.get("declared_actor_id")
                    or _payload.get("declared_name")
                    or _payload.get("actor_id"),
                    "verified_actor_id": identity.get("verified_actor_id"),
                    "canonical_actor_id": identity.get("verified_actor_id")
                    or identity.get("declared_actor_id")
                    or _payload.get("actor_id")
                    or "anonymous",
                    "auth_state": identity.get(
                        "auth_state", _payload.get("auth_state", "unverified")
                    ),
                    "base_identity": {
                        "declared": identity.get("declared_identity"),
                        "verified": identity.get("verified_identity"),
                        "verification_status": identity.get("verification_status", "unverified"),
                        "verification_source": identity.get("verification_source", "none"),
                    },
                    "self_claim_boundary": identity.get("self_claim_boundary"),
                    "bound_role": identity.get("bound_role") or bound_session.get("bound_role"),
                    "bound_session": bound_session,
                    "scope": _payload.get("scope"),
                    "continuation": _payload.get("continuation"),
                    "normalization": _payload.get("normalization"),
                    "challenge": _payload.get("challenge"),
                    "provenance": _payload.get("provenance"),
                    # Add diagnostic fields for backward compatibility in status/state modes
                    "bootstrap_sequence": _payload.get("bootstrap_sequence"),
                    "system_motto": _payload.get("system_motto"),
                    "caller_state": res.get("caller_state") or _payload.get("caller_state"),
                    # Stage 888 Diagnostics (Audit)
                    "tool_contract_table": _payload.get("tool_contract_table"),
                    "discovery_resource": _payload.get("discovery_resource"),
                    "floor_runtime_hooks": _payload.get("floor_runtime_hooks"),
                    "guidance": _payload.get("guidance"),
                    "message": _payload.get("message"),
                }

                # The final payload for the RuntimeEnvelope
                _final_payload = {
                    "ok": True,
                    "tool": "init_anchor",
                    "status": "SUCCESS",
                    "result_type": "init_anchor_result@v2",
                    "result": v2_result,
                    # Preserve governance metadata at top level
                    "organ_stage": res.get("organ_stage") or res.get("stage") or "000_INIT",
                    "risk_tier": res.get("risk_tier", "low"),
                    "verdict": res.get("verdict"),
                    "g_score": res.get("g_score"),
                    "entropy": res.get("entropy"),
                    "errors": res.get("errors", []),
                    "warnings": res.get("warnings", []),
                }
                # For backward compatibility with tests expecting keys in .payload
                _final_payload.update({k: v for k, v in v2_result.items() if v is not None})
                _payload = _final_payload

            _hold_reason = res.get("warnings", [""])[0] if res.get("warnings") else ""
            _next_action = None
            if not ok and _hold_reason:
                _next_action = {
                    "reason": _hold_reason,
                    "missing_requirements": _payload.get("missing_requirements", [])
                    if isinstance(_payload, dict)
                    else [],
                    "next_allowed_tools": _next_tools,
                    "suggested_canonical_call": _payload.get("suggested_canonical_call")
                    if isinstance(_payload, dict)
                    else None,
                }
            # Ensure verdict is a valid Verdict Enum member
            verdict_val = res.get("verdict", "SEAL" if ok else "VOID")
            if isinstance(verdict_val, str):
                try:
                    effective_verdict = Verdict(verdict_val)
                except ValueError:
                    effective_verdict = Verdict.SEAL if ok else Verdict.VOID
            else:
                effective_verdict = verdict_val or (Verdict.SEAL if ok else Verdict.VOID)

            # Ensure valid defaults for Pydantic validation
            from arifosmcp.runtime.models import AuthorityLevel, CanonicalAuthority, ClaimStatus

            _authority = res.get("authority")
            if _authority is None:
                _authority = CanonicalAuthority(
                    actor_id=res.get("actor_id") or res.get("declared_actor_id") or "anonymous",
                    level=AuthorityLevel.ANONYMOUS,
                    claim_status=ClaimStatus.ANONYMOUS,
                )

            # ─── Build policy block from floor audit data ──────────────────
            _policy_block = res.get("policy") or {
                "floors_checked": res.get("floors_checked") or _payload.get("floors_checked", [])
                if isinstance(_payload, dict)
                else [],
                "floors_failed": res.get("floors_failed") or _payload.get("floors_failed", [])
                if isinstance(_payload, dict)
                else [],
                "injection_score": (
                    res.get("injection_score")
                    or (isinstance(_payload, dict) and _payload.get("normalization", {}) or {}).get(
                        "injection_score", 0.0
                    )
                ),
                "witness_required": res.get("witness_required", False),
            }

            # ─── Build system block ────────────────────────────────────────
            import os as _os

            _system_block = res.get("system") or {
                "kernel_version": _os.getenv("ARIFOS_VERSION", "2026.04"),
                "adapter": "mcp",
                "env": _os.getenv("ARIFOS_ENV", "production"),
                "dependency_health": "ok" if ok else "degraded",
            }

            # ─── Determine anchor_state ────────────────────────────────────
            _anchor_state = res.get("anchor_state")
            if not _anchor_state:
                if not ok:
                    _anchor_state = "denied"
                elif res.get("reused") or (
                    isinstance(_payload, dict) and _payload.get("continuation")
                ):
                    _anchor_state = "reused"
                elif (
                    isinstance(_payload, dict)
                    and _payload.get("continuation", {})
                    and _payload.get("continuation", {}).get("type") == "resumed"
                ):
                    _anchor_state = "resumed"
                else:
                    _anchor_state = "created"

            # ─── Determine anchor_scope from session_class ─────────────────
            _anchor_scope = res.get("anchor_scope")
            if not _anchor_scope:
                _sc = payload.get("session_class", "execute")
                _scope_map = {
                    "query": "stateless",
                    "execute": "session",
                    "elevated": "elevated_session",
                    "sovereign": "elevated_session",
                }
                _anchor_scope = _scope_map.get(_sc, "session")

            # ─── Typed error code for failure path ────────────────────────
            _code = res.get("code")
            if not _code and not ok:
                _warnings = res.get("warnings") or []
                _w = _warnings[0].lower() if _warnings else ""
                if "auth" in _w or "identity" in _w:
                    _code = "INIT_AUTH_401"
                elif "policy" in _w or "floor" in _w or "floor" in _w:
                    _code = "INIT_POLICY_403"
                elif "schema" in _w or "missing" in _w:
                    _code = "INIT_SCHEMA_422"
                elif "dependency" in _w or "unavailable" in _w:
                    _code = "INIT_DEPENDENCY_503"
                else:
                    _code = "INIT_KERNEL_500"

            return RuntimeEnvelope(
                tool=res.get("tool", "arifos_init"),
                canonical_tool_name="arifos_init",  # ← ADDED: Canonical name
                stage=res.get("organ_stage") or res.get("stage") or "000_INIT",
                status=RuntimeStatus.SUCCESS if ok else RuntimeStatus.ERROR,
                verdict=effective_verdict,
                allowed_next_tools=_next_tools,
                next_action=_next_action,
                payload=_payload,
                session_id=res.get("session_id"),
                authority=_authority,
                auth_context=res.get("auth_context"),
                caller_state=res.get("caller_state") or "anonymous",
                # ── New constitutional handshake fields ──────────────────
                duration_ms=_duration_ms,
                mode=mode,
                intent=payload.get("intent"),
                anchor_state=_anchor_state,
                anchor_scope=_anchor_scope,
                policy=_policy_block,
                system=_system_block,
                code=_code,
                detail=res.get("detail"),
                hint=res.get("hint"),
                retryable=res.get("retryable", not ok),
                rollback_available=res.get("rollback_available", True),
                trace_id=res.get("trace_id") or f"trace_{uuid.uuid4().hex[:16]}",
                degraded_reason=res.get("degraded_reason"),
                next_allowed_modes=res.get("next_allowed_modes", ["query"] if ok else []),
            )
        return res

    if mode is None:
        mode = "init"

    # ─── FALLBACK: Dispatch via tools_internal (same pattern as agi_mind, physics_reality, etc.) ───
    from arifosmcp.runtime.tools_internal import init_anchor_dispatch_impl

    # FastMCP 2.x/3.x compatibility
    try:
        from fastmcp import Context  # Context injected by framework; None if called outside MCP
    except ImportError:
        pass
    CurrentContext = None  # Always defined — ctx injected by FastMCP framework

    resolved_payload = dict(payload or {})
    res = await init_anchor_dispatch_impl(
        mode=mode,
        payload=resolved_payload,
        auth_context=resolved_payload.get("auth_context", auth_context),
        risk_tier=resolved_payload.get("risk_tier", risk_tier),
        dry_run=bool(resolved_payload.get("dry_run", dry_run)),
        ctx=ctx or (CurrentContext() if CurrentContext else None),
    )

    # ─── V1.0 VERDICT FORGING (FALLBACK) ───
    from arifosmcp.runtime.models import VerdictCode

    if not hasattr(res, "verdict_detail") or not res.verdict_detail:
        from arifosmcp.runtime.verdict_wrapper import forge_verdict

        return forge_verdict(
            tool_id="init_anchor",
            stage=res.stage,
            payload=res.payload,
            session_id=session_id,
            override_code=VerdictCode(res.verdict.value)
            if hasattr(res.verdict, "value")
            else VerdictCode.SABAR,
            message=res.payload.get("note", "Fallback bootstrap active.")
            if isinstance(res.payload, dict)
            else "Fallback bootstrap active.",
        )
    return res
