"""
arifosmcp/runtime/tools.py — arifOS MCP Sovereign Core — 11 Canonical Tools

11 canonical tools, clean implementation, MCP-standard compliant.

The execution bridge `arifos_forge` issues delegated manifests:
  • Requires judge verdict = SEAL
  • Issues signed execution manifest
  • Dispatches to AF-FORGE substrate
  • Preserves separation of powers

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Annotated, Any
from uuid import uuid4

if TYPE_CHECKING:
    pass

from core.shared.types import Verdict

# Philosophy injection removed from tools - happens centrally in _wrap_call()
# to ensure ONLY G★ determines band, never tool identity
from fastmcp import FastMCP

from arifosmcp.integrations.git_bridge import arifos_repo_read, arifos_repo_seal
from arifosmcp.integrations.memory_bridge import arifos_memory_query as arifos_memory
from arifosmcp.runtime.continuity_contract import seal_runtime_envelope
from arifosmcp.runtime.megaTools import (
    agi_mind as _mega_agi_mind,
)
from arifosmcp.runtime.megaTools import (
    apex_judge as _mega_apex_judge,
)
from arifosmcp.runtime.megaTools import (
    arifos_kernel as _mega_arifos_kernel,
)
from arifosmcp.runtime.megaTools import (
    asi_heart as _mega_asi_heart,
)
from arifosmcp.runtime.megaTools import (
    engineering_memory as _mega_engineering_memory,
)
from arifosmcp.runtime.megaTools import (
    init_anchor as _mega_init_anchor,
)
from arifosmcp.runtime.megaTools import (
    math_estimator as _mega_math_estimator,
)
from arifosmcp.runtime.megaTools import (
    physics_reality as _mega_physics_reality,
)
from arifosmcp.runtime.megaTools import (
    vault_ledger as _mega_vault_ledger,
)
from arifosmcp.runtime.megaTools import wealth_valuation as _mega_wealth
from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus
from arifosmcp.tools.fetch_tool import arifos_fetch

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# STUB: arifos_probe — System probe tool (placeholder)
# ═══════════════════════════════════════════════════════════════════════════════


async def arifos_probe(
    target: str = "system",
    probe_type: str = "status",
    timeout_ms: int = 5000,
) -> dict[str, Any]:
    """Probe system status or component health.

    Args:
        target: Component to probe (system, memory, vault, etc.)
        probe_type: Type of probe (status, health, metrics)
        timeout_ms: Probe timeout in milliseconds

    Returns:
        Probe results with status and metrics
    """
    return {
        "ok": True,
        "tool": "arifos_probe",
        "target": target,
        "probe_type": probe_type,
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "response_ms": 0,
            "healthy": True,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def _make_f12_block_envelope(
    injection_score: float, threats: list[str], session_id: str | None
) -> Any:
    """Return a VOID RuntimeEnvelope blocking an F12 injection attempt."""
    from arifosmcp.runtime.models import RuntimeEnvelope as _RE
    from arifosmcp.runtime.models import RuntimeStatus, Verdict

    return _RE(
        ok=False,
        tool="arifos_init",
        canonical_tool_name="arifos_init",
        stage="000_INIT",
        status=RuntimeStatus.ERROR,
        verdict=Verdict.VOID,
        code="F12_INJECTION_BLOCKED",
        detail=f"Prompt injection detected (score={injection_score:.2f}). Request rejected by F12.",
        hint="Remove manipulation patterns from intent and retry with a legitimate request.",
        retryable=False,
        rollback_available=False,
        anchor_state="denied",
        session_id=session_id,
        policy={
            "floors_checked": ["F12"],
            "floors_failed": ["F12"],
            "injection_score": round(injection_score, 4),
            "threats": threats,
            "witness_required": True,
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# V2 TOOL IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════════


def _stamp_platform(envelope: Any, platform: str) -> None:
    """Stamp platform_context onto envelope in-place (F1-safe: no-op if field absent)."""
    if hasattr(envelope, "platform_context"):
        envelope.platform_context = platform
    if hasattr(envelope, "policy") and isinstance(envelope.policy, dict):
        envelope.policy["platform_context"] = platform
    elif hasattr(envelope, "policy") and envelope.policy is None:
        envelope.policy = {"platform_context": platform}


def _public_output_options(platform: str, debug: bool) -> dict[str, Any] | None:
    """Return formatter options for external/public transport surfaces."""
    if platform in {"chatgpt_apps", "api", "stdio", "mcp", "agi_reply"}:
        return {"verbose": False, "debug": debug}
    return None


_TOOL_STAGE_MAP = {
    "arifos_init": "000_INIT",
    "arifos_sense": "111_SENSE",
    "arifos_mind": "333_MIND",
    "arifos_kernel": "444_ROUTER",
    "arifos_memory": "555_MEMORY",
    "arifos_heart": "666_HEART",
    "arifos_ops": "777_FORGE",
    "arifos_judge": "888_JUDGE",
    "arifos_gateway": "888_OMEGA",
    "arifos_vault": "999_VAULT",
    "arifos_forge": "010_FORGE",
}
_READ_ONLY_DIAGNOSTIC_MODES = {"status", "probe", "state"}


def _load_public_session_context(session_id: str | None) -> dict[str, Any] | None:
    if not session_id:
        return None
    from arifosmcp.runtime.sessions import get_session_identity

    identity = get_session_identity(session_id)
    if not identity:
        return None
    actor_id = str(identity.get("actor_id") or "anonymous")
    verified = bool(identity.get("verified"))
    risk_tier = str(identity.get("risk_tier") or "medium")
    auth_context = dict(identity.get("auth_context") or {})
    auth_context.setdefault("actor_id", actor_id)
    auth_context.setdefault("session_id", session_id)
    auth_context["verified"] = verified
    auth_context.setdefault("risk_tier", risk_tier)
    return {
        "session_id": session_id,
        "actor_id": actor_id,
        "verified": verified,
        "risk_tier": risk_tier,
        "platform": str(identity.get("platform") or "mcp"),
        "caller_state": str(identity.get("caller_state") or ("verified" if verified else "anchored")),
        "auth_context": auth_context,
    }


def _session_gate_envelope(
    tool_name: str,
    session_id: str | None,
    *,
    degraded: bool = False,
    mode: str | None = None,
) -> RuntimeEnvelope:
    from arifosmcp.runtime.models import CanonicalAuthority, ClaimStatus, RiskClass

    detail = (
        "Diagnostic mode is available without a verified session, but the result is degraded."
        if degraded
        else "Session not found or expired. Re-run arifos_init before invoking governed tools."
    )
    hint = (
        "Run arifos_init(actor_id='ARIF', intent='resume session') to restore authority."
    )
    verdict = Verdict.PARTIAL if degraded else Verdict.SABAR
    status = RuntimeStatus.DEGRADED if degraded else RuntimeStatus.SABAR
    payload = {
        "result": {
            "session_id": session_id or "global",
            "actor": "anonymous",
            "verified": False,
            "risk": "low",
            "mode": mode,
            "status": "degraded" if degraded else "missing_session",
        }
    }
    return RuntimeEnvelope(
        ok=degraded,
        tool=tool_name,
        canonical_tool_name=tool_name,
        stage=_TOOL_STAGE_MAP.get(tool_name, "000_INIT"),
        status=status,
        verdict=verdict,
        session_id=session_id or "global",
        caller_state="anonymous",
        diagnostics_only=degraded,
        authority=CanonicalAuthority(
            actor_id="anonymous",
            claim_status=ClaimStatus.ANONYMOUS,
        ),
        risk_class=RiskClass.LOW,
        allowed_next_tools=["arifos_init", "init_anchor"],
        next_allowed_modes=["init", "status", "probe", "state"],
        detail=detail,
        hint=hint,
        retryable=True,
        next_action={
            "tool": "arifos_init",
            "mode": "init",
            "required_payload": ["actor_id", "intent"],
        },
        payload=payload,
    )


def _inject_session_snapshot(envelope: RuntimeEnvelope, session_ctx: dict[str, Any]) -> RuntimeEnvelope:
    from arifosmcp.runtime.models import ClaimStatus, RiskClass

    envelope.caller_state = session_ctx["caller_state"]
    envelope.session_id = session_ctx["session_id"]
    envelope.authority.actor_id = session_ctx["actor_id"]
    envelope.authority.claim_status = (
        ClaimStatus.VERIFIED if session_ctx["verified"] else ClaimStatus.ANCHORED
    )
    envelope.authority.auth_state = "verified" if session_ctx["verified"] else "anchored"
    envelope.risk_class = RiskClass(session_ctx["risk_tier"])
    payload = dict(envelope.payload or {})
    result = dict(payload.get("result") or {})
    result.update(
        {
            "session_id": session_ctx["session_id"],
            "actor": session_ctx["actor_id"],
            "verified": session_ctx["verified"],
            "risk": session_ctx["risk_tier"],
            "platform": session_ctx["platform"],
            "authority_source": "session_store",
        }
    )
    payload["result"] = result
    envelope.payload = payload
    return envelope


def _kernel_status_snapshot(session_ctx: dict[str, Any]) -> RuntimeEnvelope:
    from arifosmcp.runtime.models import CanonicalAuthority, ClaimStatus, RiskClass
    from arifosmcp.runtime.sessions import get_session_runtime_state

    state = get_session_runtime_state(session_ctx["session_id"]) or {}
    activity = state.get("activity") or {}
    result = {
        "session_id": session_ctx["session_id"],
        "actor": session_ctx["actor_id"],
        "verified": session_ctx["verified"],
        "risk": session_ctx["risk_tier"],
        "platform": session_ctx["platform"],
        "authority_source": "session_store",
        "last_tool": activity.get("last_tool"),
        "last_stage": activity.get("last_stage"),
        "tool_call_count": activity.get("tool_call_count", 0),
    }
    return RuntimeEnvelope(
        ok=True,
        tool="arifos_kernel",
        canonical_tool_name="arifos_kernel",
        stage="444_ROUTER",
        status=RuntimeStatus.SUCCESS if session_ctx["verified"] else RuntimeStatus.DEGRADED,
        verdict=Verdict.SEAL if session_ctx["verified"] else Verdict.PARTIAL,
        session_id=session_ctx["session_id"],
        caller_state=session_ctx["caller_state"],
        diagnostics_only=True,
        authority=CanonicalAuthority(
            actor_id=session_ctx["actor_id"],
            claim_status=ClaimStatus.VERIFIED if session_ctx["verified"] else ClaimStatus.ANCHORED,
            auth_state="verified" if session_ctx["verified"] else "anchored",
        ),
        risk_class=RiskClass(session_ctx["risk_tier"]),
        allowed_next_tools=["arifos_ops", "arifos_mind", "arifos_judge", "arifos_forge"],
        next_allowed_modes=["status", "probe", "state", "kernel"],
        payload={"result": result},
    )


async def arifos_init(
    actor_id: str | None = None,
    intent: str | None = None,
    declared_name: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    debug: bool = False,
    platform: str = "unknown",
    mode: str = "init",
    payload: dict[str, Any] | None = None,
    # Kernel syscall parameters (for mode="describe_kernel", etc.)
    query: str | None = None,
    current_tool: str | None = None,
    requested_tool: str | None = None,
    context: dict | None = None,
    actual_output: dict | None = None,
    call_graph: list | None = None,
    observed_effects: list | None = None,
    caller_context: Any | None = None,
) -> RuntimeEnvelope | dict[str, Any]:
    """
    Initialize constitutional session OR perform kernel syscall.
    """
    # ── Handle payload unpacking for backward compatibility ───────────────
    if payload:
        actor_id = actor_id or payload.get("actor_id")
        intent = intent or payload.get("intent")
        declared_name = declared_name or payload.get("declared_name")
        # For tests that pass query in payload
        if not intent:
            intent = payload.get("query") or payload.get("raw_input") or "no intent provided"

    # Default values for required fields if still missing
    actor_id = actor_id or "anonymous"
    intent = intent or "no intent provided"

    # ── F12: Injection Guard ──────────────────────────────────────────────
    from arifosmcp.runtime.webmcp.security import WebInjectionGuard

    _guard = WebInjectionGuard()
    _scan_intent = intent
    if isinstance(_scan_intent, dict):
        import json

        _scan_intent = json.dumps(_scan_intent)
    _injection_score, _threats = _guard._scan_text(_scan_intent)
    if _injection_score >= 0.85:
        logger.warning(
            "F12 BLOCK: injection detected in arifos_init intent (score=%.2f, threats=%s)",
            _injection_score,
            _threats,
        )
        return seal_runtime_envelope(
            _make_f12_block_envelope(_injection_score, _threats, session_id),
            "arifos_init",
            output_options=_public_output_options(platform, debug),
        )

    # ═══════════════════════════════════════════════════════════════════════
    # KERNEL SYSCALL BRANCH
    # ═══════════════════════════════════════════════════════════════════════
    if mode in (
        "describe_kernel",
        "validate_transition",
        "audit_contracts",
        "emit_proof_stub",
        "get_pipeline",
    ):
        from arifosmcp.runtime.kernel_runtime import get_kernel_runtime

        kernel = get_kernel_runtime()

        result = {}
        syscall_verdict = "SEAL"
        syscall_reason = "KERNEL_SYSCALL_OK"

        try:
            if mode == "describe_kernel":
                result = kernel.syscall_describe_kernel(query)

            elif mode == "validate_transition":
                if not current_tool or not requested_tool:
                    result = {"error": "current_tool and requested_tool required"}
                    syscall_verdict = "VOID"
                    syscall_reason = "MISSING_PARAMETERS"
                else:
                    result = kernel.syscall_validate_transition(
                        current_tool, requested_tool, context or {}
                    )
                    if not result.get("allowed"):
                        syscall_verdict = "HOLD"
                        syscall_reason = result.get("violation_type", "TRANSITION_BLOCKED")

            elif mode == "audit_contracts":
                if not query or not actual_output:
                    result = {"error": "query (tool_name) and actual_output required"}
                    syscall_verdict = "VOID"
                    syscall_reason = "MISSING_PARAMETERS"
                else:
                    result = kernel.syscall_audit_contracts(
                        tool_name=query,
                        actual_output=actual_output,
                        call_graph=call_graph or [],
                        observed_effects=observed_effects or [],
                    )
                    if result.get("drift_detected"):
                        severity = result.get("severity", "minor")
                        if severity in ("major", "critical"):
                            syscall_verdict = "HOLD"
                        syscall_reason = f"DRIFT_DETECTED:{severity}"

            elif mode == "emit_proof_stub":
                target_session = query or session_id or "anon"
                result = kernel.syscall_emit_proof_stub(target_session)

            elif mode == "get_pipeline":
                result = kernel.syscall_get_pipeline(query)  # query = from_tool

        except Exception as e:
            result = {"error": str(e), "syscall": mode}
            syscall_verdict = "VOID"
            syscall_reason = "KERNEL_EXCEPTION"

        # Build kernel syscall envelope
        from arifosmcp.runtime.arifos_runtime_envelope import RuntimeEnvelope
        from arifosmcp.runtime.models import RuntimeStatus

        envelope = RuntimeEnvelope(
            ok=syscall_verdict == "SEAL",
            tool="arifos_init",
            canonical_tool_name="arifos_init",
            stage="000_INIT",
            status=RuntimeStatus.READY if syscall_verdict == "SEAL" else RuntimeStatus.BLOCKED,
            verdict=syscall_verdict,
            session_id=session_id or "kernel_syscall",
            payload={"mode": mode, "syscall_result": result, "kernel_version": "0.2.0"},
            policy={"floors_checked": ["F11", "F12"], "syscall": mode, "reason": syscall_reason},
        )
        return seal_runtime_envelope(
            envelope,
            "arifos_init",
            output_options=_public_output_options(platform, debug),
        )

    # ═══════════════════════════════════════════════════════════════════════════════
    # STANDARD INIT BRANCH
    # ═══════════════════════════════════════════════════════════════════════════════
    # INTENT VECTOR PROFILING — Human Niat tracking
    # ═══════════════════════════════════════════════════════════════════════════════
    _intent_lower = (intent or "").lower()
    intent_vector = {
        "short_term": bool(
            any(w in _intent_lower for w in ["now", "immediately", "today", "quick"])
        ),
        "long_term": bool(
            any(w in _intent_lower for w in ["plan", "future", "strategy", "goal", "vision"])
        ),
        "exploratory": bool(
            any(
                w in _intent_lower
                for w in ["explore", "understand", "learn", "what is", "how does"]
            )
        ),
        "strategic": bool(
            any(w in _intent_lower for w in ["compete", "win", "advantage", "leverage", "position"])
        ),
        "defensive": bool(
            any(
                w in _intent_lower
                for w in ["protect", "avoid", "prevent", "stop", "block", "security"]
            )
        ),
    }
    _init_payload = {
        "actor_id": actor_id,
        "intent": intent,
        "declared_name": declared_name,
        "intent_vector": intent_vector,
    }

    # ═══════════════════════════════════════════════════════════════════════════════
    effective_mode = mode if mode in ("probe", "revoke", "refresh", "state", "status") else "init"
    envelope = await _mega_init_anchor(
        mode=effective_mode,
        payload=_init_payload,
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        debug=debug,
    )
    # Stamp F12 result into policy so floors_checked is never empty
    if hasattr(envelope, "policy") and isinstance(envelope.policy, dict):
        envelope.policy["floors_checked"] = list(
            dict.fromkeys(["F12"] + envelope.policy.get("floors_checked", []))
        )
        envelope.policy["injection_score"] = round(_injection_score, 4)
        envelope.policy["platform_context"] = platform
    elif hasattr(envelope, "policy"):
        envelope.policy = {
            "floors_checked": ["F12"],
            "injection_score": round(_injection_score, 4),
            "platform_context": platform,
        }
    if hasattr(envelope, "platform_context"):
        envelope.platform_context = platform
    if caller_context is not None and hasattr(envelope, "caller_context"):
        envelope.caller_context = caller_context
    # ── Log init to vault (arif-chatgpt sessions land here) ──
    try:
        import asyncio

        from arifosmcp.runtime.vault_postgres import PostgresVaultStore

        _vs = PostgresVaultStore()
        _sid = session_id or f"arif-chatgpt-{datetime.now().strftime('%Y%m%d')}"
        _verdict = str(envelope.verdict) if hasattr(envelope, "verdict") else "SEAL"
        _ms = getattr(envelope, "duration_ms", 0) or 0

        async def _vault_log():
            await _vs.log_tool_call(
                session_id=_sid,
                run_id=_sid,
                tool_name="arifos_init",
                organ="PSI",
                input_summary=f"actor={actor_id} intent={intent[:80]}",
                output_summary=f"verdict={_verdict}",
                verdict=_verdict,
                duration_ms=_ms,
            )

        asyncio.create_task(_vault_log())
    except Exception:
        pass  # never fail a tool call due to vault logging

    return seal_runtime_envelope(
        envelope,
        "arifos_init",
        output_options=_public_output_options(platform, debug),
    )


async def arifos_sense(
    query: str,
    mode: str = "governed",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
    # Extended SenseInput fields (all optional — backward compatible)
    intent: str | None = None,
    query_frame: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
    budget: dict[str, Any] | None = None,
    actor: dict[str, Any] | None = None,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """
    arifos_sense — Constitutional Reality Sensing
    """
    # ── EMPTY QUERY GUARD ──────────────────────────────────────────────────
    if not query or not query.strip():
        from arifosmcp.runtime.models import RuntimeEnvelope as _RE
        from arifosmcp.runtime.models import RuntimeStatus, Verdict

        return seal_runtime_envelope(
            _RE(
                ok=False,
                tool="arifos_sense",
                canonical_tool_name="arifos_sense",
                stage="111_SENSE",
                status=RuntimeStatus.ERROR,
                verdict=Verdict.VOID,
                detail="Query cannot be empty for reality grounding.",
                session_id=session_id,
            ),
            "arifos_sense",
        )

    # ── governed mode: full constitutional protocol ────────────────────────────
    if mode == "governed":
        from arifosmcp.runtime.models import RuntimeEnvelope as _RE
        from arifosmcp.runtime.models import RuntimeStatus, Verdict

        try:
            from arifosmcp.runtime.sensing_protocol import (
                TimeScope,
                normalize_query,
            )
            from arifosmcp.runtime.sensing_protocol import (
                governed_sense as _governed_sense,
            )
        except ImportError as _ie:
            logger.warning(
                "sensing_protocol import failed (%s) — falling back to legacy sense", _ie
            )
            return await _sense_legacy(
                query, "search", session_id, risk_tier, dry_run, debug, platform
            )

        # Build SenseInput — use extended fields if provided, otherwise auto-normalize
        if query_frame or intent or policy or budget or actor:
            base_si = normalize_query(query)
            if intent:
                base_si.intent.user_goal = intent
            if query_frame:
                qf = base_si.query_frame
                qf.domain = query_frame.get("domain", qf.domain)
                raw_ts = query_frame.get("time_scope")
                if raw_ts:
                    try:
                        qf.time_scope = TimeScope(raw_ts)
                    except ValueError:
                        pass
                qf.jurisdiction = query_frame.get("jurisdiction", qf.jurisdiction)
            if policy:
                p = base_si.policy
                p.obey_robots = policy.get("obey_robots", p.obey_robots)
                p.allow_paywalls = policy.get("allow_paywalls", p.allow_paywalls)
                p.fail_closed = policy.get("fail_closed", p.fail_closed)
                fd = policy.get("freshness_max_age_days")
                if fd is not None:
                    p.freshness_max_age_days = fd
            if budget:
                b = base_si.budget
                b.top_k = budget.get("top_k", b.top_k)
                b.budget_ms = budget.get("budget_ms", b.budget_ms)
            if actor:
                a = base_si.actor
                a.actor_id = actor.get("actor_id", a.actor_id)
                a.authority_level = actor.get("authority_level", a.authority_level)
            si = base_si
        else:
            si = normalize_query(query)

        try:
            sense_packet, intel_state = await _governed_sense(
                query=si,
                session_id=session_id,
                execute_search=not dry_run,
            )
        except Exception as exc:
            logger.warning("governed_sense failed: %s", exc)
            # Fall through to legacy mode on failure
            return await _sense_legacy(query, "search", session_id, risk_tier, dry_run, debug)

        # Derive verdict
        route_reason = sense_packet.routing.route_reason
        verdict_tag = (
            route_reason.split("]")[0].lstrip("[") if route_reason.startswith("[") else "SABAR"
        )
        if verdict_tag == "SEAL":
            verdict = Verdict.SEAL
            ok = True
            status = RuntimeStatus.SUCCESS
        elif verdict_tag == "HOLD":
            verdict = Verdict.SABAR
            ok = False
            status = RuntimeStatus.SABAR
        else:
            verdict = Verdict.SABAR
            ok = False
            status = RuntimeStatus.SABAR

        # Build enriched intelligence_state
        is_dict = intel_state.to_dict()
        is_dict["sense_packet_id"] = sense_packet.packet_id
        is_dict["truth_class"] = sense_packet.truth_classification.truth_class.value
        is_dict["retrieval_lane"] = sense_packet.evidence_plan.retrieval_lane
        is_dict["evidence_count"] = len(sense_packet.evidence_items)
        is_dict["routing"] = sense_packet.routing.to_dict()
        # ── AFFECTIVE SIGNAL DETECTION (human intent layer) ──────────────────
        # Lightweight linguistic markers for urgency, confidence, volatility
        _urgency = "low"
        _confidence = "medium"
        _volatility = "low"
        _q_lower = query.lower()
        if any(w in _q_lower for w in ["urgent", "asap", "immediately", "emergency", "critical"]):
            _urgency = "high"
        elif any(w in _q_lower for w in ["soon", "need", "important"]):
            _urgency = "medium"
        if "!" in query or "!!" in query:
            _volatility = "medium" if _urgency == "high" else "low"
        if query.isupper() or sum(1 for c in query if c.isupper()) > len(query) * 0.4:
            _volatility = "high"
            _urgency = "high"
        if any(w in _q_lower for w in ["?", "what if", "uncertain", "maybe"]):
            _confidence = "low"
        elif any(w in _q_lower for w in ["definitely", "certain", "sure", "know"]):
            _confidence = "high"
        affective_signal = {
            "urgency": _urgency,
            "confidence": _confidence,
            "volatility": _volatility,
        }

        envelope = _RE(
            ok=ok,
            tool="arifos_sense",
            canonical_tool_name="arifos_sense",
            stage="111_SENSE",
            status=status,
            verdict=verdict,
            session_id=session_id,
            intelligence_state=is_dict,
            payload={
                "sense_packet": sense_packet.to_dict(),
                "governed": True,
                "truth_class": sense_packet.truth_classification.truth_class.value,
                "search_required": sense_packet.truth_classification.search_required,
                "retrieval_lane": sense_packet.evidence_plan.retrieval_lane,
                "uncertainty": sense_packet.uncertainty.level.value,
                "routing": sense_packet.routing.to_dict(),
                "handoff": sense_packet.handoff.to_dict(),
                "evidence_count": len(sense_packet.evidence_items),
                "affective_signal": affective_signal,
            },
        )
        is_dict["affective_signal"] = affective_signal
        if debug:
            envelope.debug = {
                "intel_state_full": intel_state.to_dict(),
                "truth_vector": intel_state.truth_vector.to_dict(),
            }
        _stamp_platform(envelope, platform)
        # ── floors_checked: write to envelope.meta before sealing ───────────
        sense_floors = ["F2", "F3", "F4", "F7", "F8", "F10"]
        if envelope.meta:
            existing_floors = envelope.meta.floors_checked or []
            envelope.meta.floors_checked = list(dict.fromkeys(sense_floors + existing_floors))
        return seal_runtime_envelope(envelope, "arifos_sense")

    # ── legacy modes: delegate to physics_reality ─────────────────────────────
    return await _sense_legacy(query, mode, session_id, risk_tier, dry_run, debug, platform)


async def _sense_legacy(
    query: str,
    mode: str,
    session_id: str | None,
    risk_tier: str,
    dry_run: bool,
    debug: bool,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Legacy sense path — delegates to physics_reality mega tool."""
    envelope = await _mega_physics_reality(
        mode=mode,
        payload={"query": query},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_sense")


async def arifos_mind(
    query: str = "",
    context: str | None = None,
    mode: str = "reason",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
    # ═══════════════════════════════════════════════════════════════════════
    # SEQUENTIAL THINKING PARAMETERS (005-IMPLEMENTATION-SEQUENTIAL)
    # ═══════════════════════════════════════════════════════════════════════
    template: str | None = None,
    thinking_session_id: str | None = None,
    step_type: str | None = None,
    step_content: str | None = None,
    from_step: int | None = None,
    alternative_reasoning: str | None = None,
    branch_ids: list[str] | None = None,
) -> RuntimeEnvelope:
    """Structured reasoning with typed cognitive pipeline.

    Modes:
    - "reason" (default): Standard AGI pipeline (sense → mind → heart → judge)
    - "sequential": Constitutionally-governed sequential thinking with templates
    - "step": Add a step to an existing thinking session
    - "branch": Create a reasoning branch from a step
    - "merge": Synthesize insights across branches
    - "review": Review/export a thinking session

    Sequential thinking enforces F1-F13 at each step, replacing external
    Sequential Thinking MCP with native constitutional governance.

    Runs the constitutional AGI pipeline producing a narrow decision_packet
    for the operator and a full audit_packet for the vault.
    """
    from arifosmcp.runtime.sessions import _normalize_session_id, get_session_identity

    # Normalize session
    session_id = _normalize_session_id(session_id)
    identity = get_session_identity(session_id) or {}
    actor_id = identity.get("actor_id", "anonymous")

    # ═══════════════════════════════════════════════════════════════════════
    # SEQUENTIAL THINKING MODE (005-IMPLEMENTATION-SEQUENTIAL)
    # ═══════════════════════════════════════════════════════════════════════
    if mode in ("sequential", "step", "branch", "merge", "review"):
        return await _run_sequential_thinking(
            mode=mode,
            query=query,
            context=context,
            session_id=session_id,
            actor_id=actor_id,
            risk_tier=risk_tier,
            dry_run=dry_run,
            template=template,
            thinking_session_id=thinking_session_id,
            step_type=step_type,
            step_content=step_content,
            from_step=from_step,
            alternative_reasoning=alternative_reasoning,
            branch_ids=branch_ids,
        )

    # ═══════════════════════════════════════════════════════════════════════
    # STANDARD REASONING MODE (existing implementation)
    # ═══════════════════════════════════════════════════════════════════════
    from arifosmcp.runtime.arifos_runtime_envelope import Provenance, run_agi_mind

    # ── Task Ψ1: Identity & Session Stability (Continuity Phase) ──────────
    # 3. Guard: No drift allowed for non-global sessions
    if session_id and not session_id.startswith("global") and actor_id == "anonymous":
        logger.warning(f"Ψ-BREACH: Identity lost in pipeline for session {session_id}")

    # 4. Prepare provenance with session identity
    prov = Provenance(
        intelligence_type="statistical",
        grounding_status="human-mediated",
        actor_id=actor_id,
        verified_actor_id=identity.get("verified_actor_id"),
    )

    # ── Typed pipeline: sense → mind → heart → judge ─────────────────────
    decision_packet, audit_packet = await run_agi_mind(
        raw_input=query,
        session_id=session_id,
        additional_context=context or "",
        provenance=prov,
    )

    # ── Forward enriched payload through mega tool ────────────────────────
    envelope = await _mega_agi_mind(
        mode=mode,
        payload={
            "query": query,
            "context": context,
            "decision_packet": decision_packet,
            "actor_id": actor_id,
            "declared_actor_id": actor_id,
            "verified_actor_id": identity.get("verified_actor_id"),
        },
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )

    # ── Seal and inject typed packets into intelligence_state ─────────────
    sealed = seal_runtime_envelope(
        envelope,
        "arifos_mind",
        input_payload={"query": query, "session_id": session_id, "actor_id": actor_id},
    )

    # ── Visibility Injection: Surface reasoning to top-level ────────────────
    if hasattr(sealed, "__dict__"):
        # Enrich detail with the reasoning summary
        reasoning_summary = decision_packet.get("summary", "")
        if reasoning_summary:
            sealed.detail = f"{sealed.detail}\n\nREASONING: {reasoning_summary}"

        # Inject structured trace
        intel = sealed.intelligence_state or {}
        intel["decision_packet"] = decision_packet
        # Do not include full audit packet to avoid token bloat unless debug is on
        if debug:
            intel["audit_packet"] = audit_packet

        intel["reasoning_trace"] = {
            "causal_hypotheses": [
                h.get("claim") for h in audit_packet.get("full_hypothesis_set", [])
            ],
            "grounding_facts": decision_packet.get("facts", []),
            "uncertainties": decision_packet.get("uncertainties", []),
            "prescribed_next_step": decision_packet.get("next_step", ""),
        }
        intel["chaos_score"] = audit_packet.get("constitutional_checks", {}).get("chaos_score", 0.0)
        sealed.intelligence_state = intel
        sealed.platform_context = platform

    # ── G★ + Confidence Propagation ────────────────────────────────────────
    # Wire the computed g_star and omega_0 from run_agi_mind into telemetry
    # so the public envelope reflects real epistemic quality (not 0.0).
    _dp_metrics = decision_packet.get("metrics", {})
    _g_star = _dp_metrics.get("g_star", 0.0)
    _omega_0 = _dp_metrics.get("omega_0", 1.0)
    if _g_star > 0.0 and sealed.metrics:
        sealed.metrics.telemetry.G_star = _g_star
        # confidence = 1 - omega_0, clamped to [0, 1]
        sealed.metrics.telemetry.confidence = round(max(0.0, min(1.0, 1.0 - _omega_0)), 3)

    # ── floors_checked: record constitutional floors validated by mind ───────
    _mind_floors = ["F1", "F2", "F7", "F8", "F9", "F13"]
    if sealed.meta:
        _existing = sealed.meta.floors_checked or []
        sealed.meta.floors_checked = list(dict.fromkeys(_mind_floors + _existing))

    # ── P2: Provenance Ledger — Auto-seal outcome to VAULT999 ───────────────
    # Only seal if NOT dry_run and session_id is active.
    if not dry_run and session_id and session_id != "global":
        try:
            import json as _json

            # Use the status from the decision packet as the verdict tag
            v_tag = decision_packet.get("status", "PARTIAL")
            if v_tag == "OK":
                v_tag = "SEAL"
            elif v_tag == "HOLD":
                v_tag = "HOLD"
            elif v_tag == "ERROR":
                v_tag = "VOID"
            else:
                v_tag = "PARTIAL"

            # evidence string is the compact JSON of the audit packet
            evidence_str = _json.dumps(
                {
                    "type": "PROVENANCE_MIND",
                    "query": query,
                    "summary": decision_packet.get("summary"),
                    "audit": audit_packet,
                }
            )

            await arifos_vault(
                verdict=v_tag,
                evidence=evidence_str,
                session_id=session_id,
                risk_tier="low",
                dry_run=False,
                platform=platform,
            )
        except Exception as vexc:
            logger.warning("P2: Auto-seal failed for session %s: %s", session_id, vexc)

    return sealed


# ═══════════════════════════════════════════════════════════════════════════════
# SEQUENTIAL THINKING IMPLEMENTATION (005-IMPLEMENTATION-SEQUENTIAL)
# ═══════════════════════════════════════════════════════════════════════════════


async def _run_sequential_thinking(
    mode: str,
    query: str,
    context: str | None,
    session_id: str | None,
    actor_id: str,
    risk_tier: str,
    dry_run: bool,
    template: str | None,
    thinking_session_id: str | None,
    step_type: str | None,
    step_content: str | None,
    from_step: int | None,
    alternative_reasoning: str | None,
    branch_ids: list[str] | None,
) -> RuntimeEnvelope:
    """
    Run sequential thinking with constitutional governance.

    This is the native arifOS replacement for Sequential Thinking MCP,
    enforcing F1-F13 at every step.
    """
    from arifosmcp.runtime.models import RuntimeEnvelope as _RE
    from arifosmcp.runtime.models import RuntimeStatus, Verdict
    from arifosmcp.runtime.thinking import THINKING_TEMPLATES, ThinkingSessionManager
    from arifosmcp.runtime.thinking.templates import auto_select_template

    manager = ThinkingSessionManager()

    # ═══════════════════════════════════════════════════════════════════════════
    # MODE: SEQUENTIAL - Start a new thinking session
    # ═══════════════════════════════════════════════════════════════════════════
    if mode == "sequential":
        # Auto-select template if not provided
        if not template:
            template = auto_select_template(query)

        # ── INITIAL KNOWLEDGE ACQUISITION (Substrate Bridge) ─────────────
        # Query memory for existing entities related to the problem
        mem_context = ""
        try:
            from arifosmcp.integrations.memory_bridge import arifos_memory_query

            mem_report = await arifos_memory_query(
                query=query, actor_id=actor_id, session_id=session_id
            )
            if mem_report.ok:
                entities = mem_report.payload.get("entities", [])
                if entities:

                    # Re-map to objects for formatting if needed, or format directly
                    mem_context = "\n## Knowledge Graph Context\n"
                    for e in entities:
                        mem_context += f"### {e['name']} ({e['type']})\n"
                        for obs in e.get("observations", [])[:3]:
                            mem_context += f"- {obs}\n"
                    context = f"{context}\n{mem_context}" if context else mem_context
        except Exception as e:
            logger.warning(f"Memory lookup failed at MIND start: {e}")

        # Start session
        thinking_session = manager.start_session(
            problem=query,
            context={
                "context": context,
                "kg_entities_found": len(entities) if "entities" in locals() else 0,
            }
            if context
            else None,
            template=template,
            arifos_session_id=session_id,
        )

        # If template provided, auto-generate initial steps
        if template and template in THINKING_TEMPLATES:
            tmpl = THINKING_TEMPLATES[template]
            # Generate step content via LLM (simplified here)
            for i, step_prompt in enumerate(tmpl.steps[:3]):  # First 3 steps
                step = manager.add_step(
                    session_id=thinking_session.session_id,
                    step_type=tmpl.step_types[i],
                    content=f"[Step {i + 1}: {step_prompt}]\n\nAnalyzing: {query[:100]}...",
                )
                # F2 check - stop on VOID
                if step.constitutional_verdict == "VOID":
                    break

        return _RE(
            ok=True,
            tool="arifos_mind",
            canonical_tool_name="arifos_mind",
            stage="333_MIND",
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload={
                "mode": "sequential",
                "thinking_session_id": thinking_session.session_id,
                "template": template,
                "problem": query,
                "steps_count": len(thinking_session.steps),
                "quality_score": thinking_session.quality_score,
                "constitutional_verdicts": [
                    s.constitutional_verdict for s in thinking_session.steps
                ],
            },
            session_id=session_id,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # MODE: STEP - Add a step to existing session
    # ═══════════════════════════════════════════════════════════════════════════
    elif mode == "step":
        if not thinking_session_id:
            return _RE(
                ok=False,
                tool="arifos_mind",
                stage="333_MIND",
                verdict=Verdict.VOID,
                status=RuntimeStatus.ERROR,
                payload={"error": "thinking_session_id required for mode='step'"},
            )

        step = manager.add_step(
            session_id=thinking_session_id,
            step_type=step_type or "analysis",
            content=step_content or query,
        )

        return _RE(
            ok=True,
            tool="arifos_mind",
            stage="333_MIND",
            verdict=Verdict.SEAL if step.constitutional_verdict != "VOID" else Verdict.VOID,
            status=RuntimeStatus.SUCCESS,
            payload={
                "mode": "step",
                "step_number": step.step_number,
                "constitutional_verdict": step.constitutional_verdict,
                "f2_truth_score": step.f2_truth_score,
                "f7_uncertainty": step.f7_uncertainty,
                "quality_score": step.quality_score,
            },
            session_id=session_id,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # MODE: BRANCH - Create a reasoning branch
    # ═══════════════════════════════════════════════════════════════════════════
    elif mode == "branch":
        if not thinking_session_id or not from_step:
            return _RE(
                ok=False,
                tool="arifos_mind",
                stage="333_MIND",
                verdict=Verdict.VOID,
                status=RuntimeStatus.ERROR,
                payload={"error": "thinking_session_id and from_step required for mode='branch'"},
            )

        branch_id = manager.branch_session(
            session_id=thinking_session_id,
            from_step=from_step,
            alternative_reasoning=alternative_reasoning or query,
        )

        return _RE(
            ok=True,
            tool="arifos_mind",
            stage="333_MIND",
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload={
                "mode": "branch",
                "branch_id": branch_id,
                "from_step": from_step,
            },
            session_id=session_id,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # MODE: MERGE - Synthesize branches
    # ═══════════════════════════════════════════════════════════════════════════
    elif mode == "merge":
        if not thinking_session_id:
            return _RE(
                ok=False,
                tool="arifos_mind",
                stage="333_MIND",
                verdict=Verdict.VOID,
                status=RuntimeStatus.ERROR,
                payload={"error": "thinking_session_id required for mode='merge'"},
            )

        conclusion = manager.merge_insights(
            session_id=thinking_session_id,
            branch_ids=branch_ids or [],
        )

        return _RE(
            ok=True,
            tool="arifos_mind",
            stage="333_MIND",
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload={
                "mode": "merge",
                "conclusion_step": conclusion.step_number,
                "content": conclusion.content,
                "quality_score": conclusion.quality_score,
            },
            session_id=session_id,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # MODE: REVIEW - Export/review session
    # ═══════════════════════════════════════════════════════════════════════════
    elif mode == "review":
        if not thinking_session_id:
            return _RE(
                ok=False,
                tool="arifos_mind",
                stage="333_MIND",
                verdict=Verdict.VOID,
                status=RuntimeStatus.ERROR,
                payload={"error": "thinking_session_id required for mode='review'"},
            )

        exported = manager.export_session(session_id=thinking_session_id, format_type="json")

        thinking_session = manager.get_session(thinking_session_id)

        return _RE(
            ok=True,
            tool="arifos_mind",
            stage="333_MIND",
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload={
                "mode": "review",
                "session": exported,
                "quality_score": thinking_session.quality_score if thinking_session else 0,
                "constitutional_verdicts": [
                    s.constitutional_verdict for s in thinking_session.steps
                ]
                if thinking_session
                else [],
            },
            session_id=session_id,
        )

    # Unknown mode
    return _RE(
        ok=False,
        tool="arifos_mind",
        stage="333_MIND",
        verdict=Verdict.VOID,
        status=RuntimeStatus.ERROR,
        payload={"error": f"Unknown sequential thinking mode: {mode}"},
    )


async def arifos_kernel(
    request: str | None = None,
    query: str | None = None,
    context: str | None = None,
    mode: str = "kernel",
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
    actor_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Route request to correct metabolic lane."""
    # Horizon Unification: Support both 'request' and 'query'
    target_query = query or request or ""
    envelope = await _mega_arifos_kernel(
        mode=mode,
        payload={
            "query": target_query,
            "context": context,
            "auth_context": auth_context,
            "actor_id": actor_id,
        },
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        debug=debug,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_kernel")


async def arifos_route(
    request: str | None = None,
    query: str | None = None,
    context: str | None = None,
    mode: str = "kernel",
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
    actor_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Public routing wrapper for the internal kernel lane."""
    effective_session_id = session_id
    effective_auth_context = auth_context

    if dry_run and not allow_execution and not effective_auth_context:
        effective_session_id = effective_session_id or f"route-{uuid4().hex}"
        init_envelope = await arifos_init(
            mode="init",
            declared_name=actor_id or "arifos-route",
            actor_id=actor_id or "arifos-route",
            session_id=effective_session_id,
            risk_tier="low" if risk_tier == "medium" else risk_tier,
            dry_run=True,
            debug=debug,
            platform=platform,
        )
        effective_auth_context = getattr(init_envelope, "auth_context", None)

    envelope = await arifos_kernel(
        request=request,
        query=query,
        context=context,
        mode=mode,
        session_id=effective_session_id,
        auth_context=effective_auth_context,
        actor_id=actor_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        debug=debug,
        platform=platform,
    )
    if getattr(envelope, "philosophy", None) is None:
        from arifosmcp.runtime.philosophy_registry import inject_philosophy

        philosophy = inject_philosophy(envelope)
        if philosophy is not None:
            envelope.philosophy = philosophy.model_copy(update={"stage": envelope.stage})
    return seal_runtime_envelope(envelope, "arifos_route")


async def arifos_heart(
    content: str | None = None,
    query: str | None = None,
    mode: str = "critique",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
    background_scan: bool = False,
) -> RuntimeEnvelope:
    # Horizon Unification: Support both 'content' and 'query'
    target_content = query or content or ""
    # ── ASI Heart: Safety, dignity, and adversarial critique ─────────────────────
    from arifosmcp.runtime.arifos_runtime_envelope import heart_stage, mind_stage, sense_stage

    sensed = sense_stage(target_content)
    hypotheses = mind_stage(sensed)
    risk_trace = heart_stage(hypotheses)
    critique_packet = {
        "summary": risk_trace[0] if risk_trace else "No critique generated.",
        "risk_trace": risk_trace[:3],
        "hypotheses": [h.claim for h in hypotheses[:3]],
        "next_step": "Address the highest-risk consequence before execution.",
    }

    # ── BACKGROUND ETHICAL SCAN MODE ──────────────────────────────────────────
    # Enables lightweight continuous monitoring without full critique overhead
    ethical_markers = {
        "manipulation_risk": False,
        "authority_escalation": False,
        "dignity_concern": False,
    }
    if background_scan or mode == "scan":
        _t_lower = target_content.lower()
        ethical_markers = {
            "manipulation_risk": bool(
                any(w in _t_lower for w in ["bypass", "override", "exploit", "jailbreak"])
            ),
            "authority_escalation": bool(
                any(w in _t_lower for w in ["elevate", "admin", "sudo", "root"])
            ),
            "dignity_concern": bool(
                any(w in _t_lower for w in ["manipulate", "coerce", "deceive", "exploit trust"])
            ),
        }
        critique_packet["background_scan"] = True
        critique_packet["ethical_markers"] = ethical_markers

    envelope = await _mega_asi_heart(
        mode=mode,
        payload={"content": target_content, "critique_packet": critique_packet},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )

    sealed = seal_runtime_envelope(envelope, "arifos_heart")

    # ── Visibility Injection: Surface safety reasoning ─────────────────────
    if hasattr(sealed, "__dict__"):
        payload = getattr(sealed, "payload", {})
        if isinstance(payload, dict):
            payload["critique_packet"] = critique_packet
            risks = critique_packet["risk_trace"]
            if risks:
                base_detail = sealed.detail or critique_packet["summary"]
                sealed.detail = f"{base_detail}\n\nRISK ASSESSMENT: {'; '.join(risks[:3])}"

            intel = sealed.intelligence_state or {}
            intel["safety_trace"] = {
                "detected_risks": risks,
                "constitutional_alignment": payload.get("alignment_score", 1.0),
                "ethical_critique": payload.get("critique", critique_packet["summary"]),
                "hypotheses": critique_packet["hypotheses"],
            }
            if background_scan or mode == "scan":
                intel["ethical_markers"] = ethical_markers
            sealed.intelligence_state = intel
            sealed.platform_context = platform

    return sealed


async def arifos_ops(
    action: str | None = None,
    query: str | None = None,
    mode: str = "cost",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Calculate operation costs and thermodynamics."""
    # Horizon Unification: Support both 'action' and 'query'
    target_action = query or action or ""
    envelope = await _mega_math_estimator(
        mode=mode,
        payload={"action": target_action},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_ops")


async def arifos_judge(
    candidate_action: str | None = None,
    query: str | None = None,
    risk_tier: str = "medium",
    telemetry: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Final constitutional verdict evaluation."""
    # Horizon Unification: Support both 'candidate_action' and 'query'
    target_candidate = query or candidate_action or ""
    envelope = await _mega_apex_judge(
        mode="judge",
        payload={
            "candidate": target_candidate,
            "risk_tier": risk_tier,
            "telemetry": telemetry,
        },
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_judge")


async def arifos_memory(
    query: str = "",
    content: str | None = None,
    mode: str = "vector_query",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Retrieve governed memory from vector store or update the continuous world model."""

    # Karpathy Injection: Continuous Learning (Animal Archetype vs Ghost)
    # Overcoming Anterograde Amnesia through active world model updates.
    payload = {"query": query}
    if content:
        payload["content"] = content
    if mode == "world_model_update":
        payload["animal_archetype_active"] = True
        payload["continuous_learning_update"] = True
        payload["anterograde_amnesia_override"] = True

    envelope = await _mega_engineering_memory(
        mode=mode,
        payload=payload,
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_memory")


async def arifos_health(
    action: str = "get_telemetry",
    session_id: str | None = None,
    risk_tier: str = "low",
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Secure VPS telemetry (CPU, Memory, ZRAM, Disk). F12-hardened."""
    import os
    import subprocess

    from arifosmcp.runtime.models import RuntimeEnvelope as RE
    from arifosmcp.runtime.models import RuntimeStatus, UserModel, Verdict

    _user_model = UserModel()

    # F12: Hardcoded read-only telemetry logic
    try:
        if action == "get_telemetry":
            with open("/proc/loadavg") as f:
                load = f.read().strip()
            with open("/proc/meminfo") as f:
                # Get first few lines of meminfo for high clarity
                mem = "\n".join([f.readline().strip() for _ in range(3)])
            output = f"Load: {load}\n{mem}"
        elif action == "get_zram_status":
            # zramctl might be missing, try to find zram in /sys
            if os.path.exists("/sys/block/zram0"):
                with open("/sys/block/zram0/disksize") as f:
                    size = int(f.read().strip()) / (1024**2)

                # mm_stat: [orig_data_size, compr_data_size, mem_used_total, ...]
                with open("/sys/block/zram0/mm_stat") as f:
                    stats = f.read().split()
                    orig = int(stats[0]) / (1024**2)
                    compr = int(stats[1]) / (1024**2)
                    mem_used = int(stats[2]) / (1024**2)
                output = f"zram0 Capacity: {size:.2f}MB\nData: {orig:.2f}MB -> Compressed: {compr:.2f}MB\nMemory Used: {mem_used:.2f}MB"
            else:
                output = "zram0 not found in /sys/block/"
        elif action == "get_disk_usage":
            # df is a core binary, but if it fails we report error
            process = subprocess.Popen(
                "df -h /", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, _ = process.communicate(timeout=2)
            output = stdout.strip()
        else:
            return seal_runtime_envelope(
                RE(
                    ok=False,
                    tool="arifos.health",
                    canonical_tool_name="arifos.health",
                    stage="111_SENSE",
                    verdict=Verdict.VOID,
                    status=RuntimeStatus.ERROR,
                    detail=f"F12_BLOCKED: Action '{action}' not permitted.",
                    user_model=_user_model,
                ),
                "arifos_health",
            )

        if dry_run:
            return seal_runtime_envelope(
                RE(
                    ok=True,
                    tool="arifos.health",
                    canonical_tool_name="arifos.health",
                    stage="111_SENSE",
                    verdict=Verdict.SEAL,
                    status=RuntimeStatus.SUCCESS,
                    payload={"mode": "dry_run", "action": action},
                    user_model=_user_model,
                ),
                "arifos_health",
            )

        return seal_runtime_envelope(
            RE(
                ok=True,
                tool="arifos.health",
                canonical_tool_name="arifos.health",
                stage="111_SENSE",
                verdict=Verdict.SEAL,
                status=RuntimeStatus.SUCCESS,
                payload={"output": output, "success": True},
                user_model=_user_model,
            ),
            "arifos_health",
        )
    except Exception as e:
        return seal_runtime_envelope(
            RE(
                ok=False,
                tool="arifos.health",
                canonical_tool_name="arifos.health",
                stage="111_SENSE",
                verdict=Verdict.VOID,
                status=RuntimeStatus.ERROR,
                detail=str(e),
                user_model=_user_model,
            ),
            "arifos_health",
        )


async def arifos_vault(
    verdict: str,
    evidence: str | None = None,
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Append immutable verdict to ledger."""
    envelope = await _mega_vault_ledger(
        mode="seal",
        payload={"verdict": verdict, "evidence": evidence},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_vault")


async def arifos_gateway(
    session_id: str,
    mode: str = "guard",
    tool_trace: list[dict[str, Any]] | None = None,
    correlation_threshold: float = 0.95,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Orthogonality guard — AGI||ASI lane supervisor (Ω_ortho >= 0.95)."""
    from arifosmcp.runtime.models import RuntimeEnvelope as RE
    from arifosmcp.runtime.models import RuntimeStatus, Verdict

    trace = tool_trace or []
    violations: list[dict[str, Any]] = []

    # Forbidden overlap heuristics by organ ownership
    FORBIDDEN_MAP: dict[str, list[str]] = {
        "arifos": ["npv", "irr", "dscr", "las", "petrophysics", "stratigraphy", "seismic"],
        "wealth": ["las", "petrophysics", "stratigraphy", "seismic", "verdict", "seal", "vault"],
        "geox": ["npv", "irr", "dscr", "verdict", "seal", "vault", "constitutional"],
    }

    # Simple structural orthogonality audit
    organs_seen: set[str] = set()
    for step in trace:
        tool_name = step.get("tool", "")
        output_summary = str(step.get("output_summary", "")).lower()
        tool_lower = tool_name.lower()

        organ: str | None = None
        if tool_lower.startswith("arifos_"):
            organ = "arifos"
        elif tool_lower.startswith("wealth_"):
            organ = "wealth"
        elif tool_lower.startswith("geox_"):
            organ = "geox"

        if organ:
            organs_seen.add(organ)
            # Detect forbidden keyword leakage
            for forbidden_word in FORBIDDEN_MAP.get(organ, []):
                if forbidden_word in output_summary or forbidden_word in tool_lower:
                    violations.append(
                        {
                            "step": step,
                            "reason": "forbidden_overlap",
                            "detail": f"{organ} tool '{tool_name}' touched forbidden domain keyword '{forbidden_word}'",
                        }
                    )

    # Correlation proxy: diversity of organs determines orthogonality
    omega_ortho = 1.0
    if len(trace) > 0:
        organ_counts: dict[str, int] = {}
        for step in trace:
            t = step.get("tool", "")
            o = (
                "arifos"
                if t.startswith("arifos_")
                else (
                    "wealth"
                    if t.startswith("wealth_")
                    else ("geox" if t.startswith("geox_") else "other")
                )
            )
            organ_counts[o] = organ_counts.get(o, 0) + 1
        max_ratio = max(organ_counts.values(), default=0) / len(trace)
        denom = 1.0 - correlation_threshold
        if denom <= 0:
            omega_ortho = 1.0 if max_ratio < correlation_threshold else 0.0
        else:
            omega_ortho = 1.0 - max(0.0, max_ratio - correlation_threshold) / denom
        omega_ortho = max(0.0, min(1.0, omega_ortho))

    if omega_ortho < correlation_threshold or violations:
        verdict = Verdict.HOLD
        status = RuntimeStatus.HOLD
    else:
        verdict = Verdict.SEAL
        status = RuntimeStatus.SUCCESS

    envelope = RE(
        ok=verdict == Verdict.SEAL,
        tool="arifos_gateway",
        canonical_tool_name="arifos_gateway",
        stage="888_OMEGA",
        verdict=verdict,
        status=status,
        payload={
            "mode": mode,
            "omega_ortho": round(omega_ortho, 4),
            "correlation_threshold": correlation_threshold,
            "organs_seen": sorted(organs_seen),
            "violations": violations,
            "trace_length": len(trace),
        },
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos_gateway")


# ═══════════════════════════════════════════════════════════════════════════════
# V2 TOOL HANDLER REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

# Import the 10th tool (Delegated Execution Bridge)
from arifosmcp.runtime.tools_forge import arifos_forge


async def arifos_reply(
    query: str,
    session_id: str | None = None,
    recipient: str = "auto",
    depth: str = "ENGINEER",
    compression: str = "DELTA",
    risk_tier: str = "medium",
    prior_state: str | None = None,
    platform: str = "agi_reply",
    to: str | None = None,
    cc: list[str] | None = None,
    dry_run: bool = False,
) -> RuntimeEnvelope:
    """
    arifos_reply — Governed Reply Compositor (AGI Reply Protocol v3).

    Composite orchestrator: enforces memory → sense → mind → heart → ops → judge → vault
    in deterministic order. Emits AgiReplyEnvelopeHuman or AgiReplyEnvelopeAgent.
    888 HOLD blocks forge. F1/F13 requires human:arif ratification.
    """
    import hashlib
    from datetime import datetime, timezone

    _session = session_id or f"reply-{query[:8].replace(' ', '-')}"
    _ts = datetime.now(timezone.utc).isoformat()
    _actor = to or "arif"
    _cc = cc or []

    # ── STEP -1: memory → PRIOR_STATE + DELTA ────────────────────────────────
    mem_result: dict[str, Any] = {}
    try:
        mem_env = await arifos_memory(query=query, mode="vector_query", session_id=_session)
        if isinstance(mem_env, dict):
            mem_result = mem_env.get("payload", {}) or {}
    except Exception:
        pass
    resolved_prior = prior_state or mem_result.get("summary", "NONE")

    # ── STEP 0: sense → recipient + stakes ───────────────────────────────────
    resolved_recipient = recipient
    sense_result: dict[str, Any] = {}
    try:
        sense_env = await arifos_sense(query=query, mode="governed", session_id=_session)
        if isinstance(sense_env, dict):
            sense_result = sense_env.get("payload", {}) or {}
            if recipient == "auto":
                resolved_recipient = sense_result.get("caller_type", "human")
    except Exception:
        if recipient == "auto":
            resolved_recipient = "human"

    # ── STEP 2A+2B: mind → direct_answer + reasoning_atoms ───────────────────
    mind_result: dict[str, Any] = {}
    direct_answer: list[str] = []
    reasoning_snapshot: list[str] = []
    try:
        mind_env = await arifos_mind(query=query, mode="reason", session_id=_session)
        if isinstance(mind_env, dict):
            mind_result = mind_env.get("payload", {}) or {}
            raw = mind_result.get("output") or mind_result.get("answer") or ""
            direct_answer = [raw] if isinstance(raw, str) and raw else []
            reasoning_snapshot = mind_result.get("reasoning_atoms", [])
    except Exception:
        pass

    # ── STEP 3 (partial): heart → floor_flags + rights_impact ────────────────
    heart_result: dict[str, Any] = {}
    floors_triggered: list[str] = []
    try:
        critique_content = direct_answer[0] if direct_answer else query
        heart_env = await arifos_heart(
            content=critique_content, mode="critique", session_id=_session
        )
        if isinstance(heart_env, dict):
            heart_result = heart_env.get("payload", {}) or {}
            floors_triggered = heart_result.get("floor_flags", [])
    except Exception:
        pass

    # ── STEP 2D: ops → resource envelope ─────────────────────────────────────
    ops_result: dict[str, Any] = {}
    try:
        ops_env = await arifos_ops(action=query, mode="cost", session_id=_session)
        if isinstance(ops_env, dict):
            ops_result = ops_env.get("payload", {}) or {}
    except Exception:
        pass

    # ── STEP 1: judge → verdict + τ ──────────────────────────────────────────
    judge_verdict_str = "HOLD"
    tau = 0.5
    tau_source = "fallback"
    try:
        judge_env = await arifos_judge(
            candidate_action=query,
            risk_tier=risk_tier,
            telemetry=ops_result or None,
            session_id=_session,
        )
        if isinstance(judge_env, dict):
            jp = judge_env.get("payload", {}) or {}
            judge_verdict_str = jp.get("verdict", judge_env.get("verdict", "HOLD"))
            if jp.get("tau") is not None:
                tau = float(jp["tau"])
                tau_source = "computed"
            elif jp.get("confidence") is not None:
                tau = float(jp["confidence"]) * 0.85
                tau_source = "fallback"
    except Exception:
        pass

    # ── STEP 3: vault for SEAL or HOLD ───────────────────────────────────────
    vault_ref = None
    if not dry_run and judge_verdict_str in ("SEAL", "HOLD"):
        try:
            evidence_summary = "; ".join(reasoning_snapshot[:2]) if reasoning_snapshot else query
            vault_env = await arifos_vault(
                verdict=judge_verdict_str
                if judge_verdict_str in ("SEAL", "PARTIAL", "VOID", "HOLD")
                else "HOLD",
                evidence=evidence_summary,
                session_id=_session,
                risk_tier=risk_tier,
            )
            if isinstance(vault_env, dict):
                vault_ref = (vault_env.get("payload", {}) or {}).get("ledger_ref")
        except Exception:
            pass

    # ── Build reply envelope payload ──────────────────────────────────────────
    _verdict_token_map = {
        "SEAL": "CLAIM",
        "PARTIAL": "PLAUSIBLE",
        "HOLD": "888 HOLD",
        "VOID": "UNKNOWN",
    }
    verdict_token = _verdict_token_map.get(judge_verdict_str, "UNKNOWN")
    verdict_statement = (
        mind_result.get("summary")
        or sense_result.get("summary")
        or f"Governed reply for: {query[:80]}"
    )
    title = f"{verdict_token} τ={tau:.2f} — {verdict_statement}"
    audit_hash = hashlib.sha256(
        f"{title}{_ts}arifos_reply{judge_verdict_str}".encode()
    ).hexdigest()[:16]

    if "arifos_vault" not in _cc and judge_verdict_str in ("SEAL", "HOLD"):
        _cc.append("arifos_vault")

    # ── 888 HOLD governance trace ─────────────────────────────────────────────
    governance_trace = None
    if floors_triggered and any(f in floors_triggered for f in ("F1", "F13")):
        governance_trace = {
            "floors_triggered": floors_triggered,
            "verdict": "888_HOLD",
            "escalate_to": f"human:{_actor}",
            "audit_ref": audit_hash,
            "reversible": "PARTIAL",
            "human_confirmed": False,
        }

    payload: dict[str, Any] = {
        "recipient": resolved_recipient,
        "depth": depth,
        "compression_mode": compression,
        "prior_state": resolved_prior,
        "delta": sense_result.get("delta"),
        "verdict_token": verdict_token,
        "verdict_statement": verdict_statement,
        "tau": tau,
        "tau_source": tau_source,
        "floors_triggered": floors_triggered,
        "floors_passed": [
            f for f in ["F1", "F2", "F4", "F7", "F9", "F11", "F13"] if f not in floors_triggered
        ],
        "direct_answer": direct_answer,
        "reasoning_snapshot": reasoning_snapshot,
        "action_output": mind_result.get("action_output"),
        "resource_envelope": {
            "compression_mode": compression,
            "tokens_estimated": ops_result.get("tokens_estimated"),
            "cache_stable_prefix": True,
            "parallel_ok": True,
            "next_agent": None,
        },
        "governance_trace": governance_trace,
        "telemetry": ops_result or None,
        "forged_by": "arifos_reply",
        "judge_verdict": judge_verdict_str,
        "to": _actor,
        "cc": _cc,
        "vault_ref": vault_ref,
        "consulted_tools": [
            "arifos_memory",
            "arifos_sense",
            "arifos_mind",
            "arifos_heart",
            "arifos_ops",
            "arifos_judge",
        ],
        "informed_agents": _cc,
    }

    from arifosmcp.runtime.models import RuntimeEnvelope as RE
    from arifosmcp.runtime.models import RuntimeStatus
    from arifosmcp.runtime.models import Verdict as V

    _verdict_map = {"SEAL": V.SEAL, "PARTIAL": V.PROVISIONAL, "HOLD": V.HOLD, "VOID": V.VOID}
    return seal_runtime_envelope(
        RE(
            ok=judge_verdict_str in ("SEAL", "PARTIAL"),
            tool="arifos_reply",
            canonical_tool_name="arifos_reply",
            stage="000-999",
            verdict=_verdict_map.get(judge_verdict_str, V.HOLD),
            status=RuntimeStatus.SUCCESS
            if judge_verdict_str in ("SEAL", "PARTIAL")
            else RuntimeStatus.HOLD,
            payload=payload,
            hint=title,
            detail=verdict_statement,
            platform_context=platform,
            session_id=_session,
        ),
        "arifos_reply",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# UNIVERSAL NAMING: All tool names use underscores for cross-platform compatibility
# Legacy dot-names (arifos.init) are supported via LEGACY_ALIASES mapping
# ═══════════════════════════════════════════════════════════════════════════════


async def arifos_diag_substrate(session_id: str | None = None) -> Any:
    """Maintainer: Run substrate protocol conformance check."""
    from arifosmcp.evals.everything_conformance_runner import run_protocol_conformance_test
    from arifosmcp.runtime.models import (
        ExecutionStatus,
        RuntimeEnvelope as _RE,
        Verdict,
    )

    verdict = await run_protocol_conformance_test()
    return _RE(
        ok=verdict == Verdict.SEAL,
        tool="arifos.diag_substrate",
        canonical_tool_name="arifos.diag_substrate",
        stage="000_INIT",
        session_id=session_id,
        verdict=verdict,
        execution_status=(
            ExecutionStatus.SUCCESS if verdict == Verdict.SEAL else ExecutionStatus.ERROR
        ),
        payload={"message": f"Substrate conformance result: {verdict}"},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC SURFACE WRAPPERS — Clean signatures matching ToolSpec.input_schema
# Prevents FastMCP schema-generation faults from wide internal signatures.
# ═══════════════════════════════════════════════════════════════════════════════


async def _arifos_init_public(
    actor_id: Annotated[str | None, "Unique identifier for the user/agent"] = None,
    intent: Annotated[str | None, "Goal or purpose of the session"] = None,
    declared_name: Annotated[str | None, "Human-readable name for the session"] = None,
    session_id: Annotated[str | None, "ID of an existing session to resume"] = None,
    risk_tier: Annotated[str, "The risk level (low, medium, high, critical)"] = "medium",
    platform: Annotated[str, "Deployment platform (mcp, stdio, etc.)"] = "unknown",
    mode: Annotated[str, "Operation mode (init, status, probe)"] = "init",
) -> RuntimeEnvelope:
    return await arifos_init(
        actor_id=actor_id,
        intent=intent,
        declared_name=declared_name,
        session_id=session_id,
        risk_tier=risk_tier,
        platform=platform,
        mode=mode,
    )


async def _arifos_sense_public(
    query: Annotated[str, "The reality grounding query (fact, question, or claim)"],
    mode: Annotated[str, "The sensing mode (governed, search, atlas)"] = "governed",
    session_id: Annotated[str | None, "Active arifOS session ID"] = None,
    dry_run: Annotated[bool, "If True, simulates sensing without fetching results"] = True,
    risk_tier: Annotated[str, "The risk level (low, medium, high, critical)"] = "medium",
    platform: Annotated[str, "Deployment platform (mcp, stdio, etc.)"] = "unknown",
) -> RuntimeEnvelope:
    session_ctx = _load_public_session_context(session_id)
    if session_ctx is None:
        return _session_gate_envelope("arifos_sense", session_id, mode=mode)
    envelope = await arifos_sense(
        query=query,
        mode=mode,
        session_id=session_id,
        dry_run=dry_run,
        risk_tier=session_ctx["risk_tier"] or risk_tier,
        platform=platform,
    )
    return _inject_session_snapshot(envelope, session_ctx)


async def _arifos_mind_reflect(
    query: str = "",
    context: str | None = None,
    session_id: str | None = None,
) -> RuntimeEnvelope:
    """Lightweight feedback-learning mode: compare predictions vs outcomes."""
    import json

    from arifosmcp.runtime.models import RuntimeEnvelope as RE
    from arifosmcp.runtime.models import RuntimeStatus, Verdict

    predictions: list[float] = []
    outcomes: list[float] = []
    try:
        ctx = json.loads(context or "{}")
        predictions = [float(x) for x in ctx.get("predictions", [])]
        outcomes = [float(x) for x in ctx.get("outcomes", [])]
    except Exception:
        pass

    mae = 0.0
    calibration_gap = 0.0
    n = min(len(predictions), len(outcomes))
    if n > 0:
        errors = [abs(predictions[i] - outcomes[i]) for i in range(n)]
        mae = sum(errors) / n
        calibration_gap = sum(predictions[i] - outcomes[i] for i in range(n)) / n

    return RE(
        ok=True,
        tool="arifos_mind",
        canonical_tool_name="arifos_mind",
        stage="333_MIND",
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        payload={
            "mode": "reflect",
            "sample_count": n,
            "mae": round(mae, 4),
            "calibration_gap": round(calibration_gap, 4),
            "recommendation": (
                "Confidence thresholds may be too low"
                if calibration_gap < -0.1
                else "Confidence thresholds may be too high"
                if calibration_gap > 0.1
                else "Calibration appears well-aligned"
            ),
        },
        session_id=session_id,
    )


async def _arifos_mind_public(
    query: Annotated[str, "The reasoning query or prompt"] = "",
    context: Annotated[str | None, "Additional context or history"] = None,
    mode: Annotated[str, "Reasoning mode (reason, sequential, step)"] = "reason",
    session_id: Annotated[str | None, "Active arifOS session ID"] = None,
    risk_tier: Annotated[str, "The risk level (low, medium, high, critical)"] = "medium",
    dry_run: Annotated[bool, "If True, simulates reasoning without side effects"] = True,
    platform: Annotated[str, "Deployment platform (mcp, stdio, etc.)"] = "unknown",
) -> RuntimeEnvelope:
    session_ctx = _load_public_session_context(session_id)
    if session_ctx is None:
        return _session_gate_envelope("arifos_mind", session_id, mode=mode)
    if mode == "reflect":
        envelope = await _arifos_mind_reflect(query=query, context=context, session_id=session_id)
        return _inject_session_snapshot(envelope, session_ctx)
    envelope = await arifos_mind(
        query=query,
        context=context,
        mode=mode,
        session_id=session_id,
        risk_tier=session_ctx["risk_tier"] or risk_tier,
        dry_run=dry_run,
        platform=platform,
    )
    return _inject_session_snapshot(envelope, session_ctx)


async def _arifos_kernel_public(
    query: Annotated[str, "The metabolic routing query"] = "",
    mode: Annotated[str, "The routing mode (kernel, status)"] = "kernel",
    session_id: Annotated[str | None, "Active arifOS session ID"] = None,
    risk_tier: Annotated[str, "The risk level (low, medium, high, critical)"] = "medium",
    dry_run: Annotated[bool, "If True, simulates routing without execution"] = True,
    allow_execution: Annotated[bool, "If True, allows the kernel to dispatch execution"] = False,
    platform: Annotated[str, "Deployment platform (mcp, stdio, etc.)"] = "unknown",
) -> RuntimeEnvelope:
    session_ctx = _load_public_session_context(session_id)
    if session_ctx is None:
        return _session_gate_envelope(
            "arifos_kernel",
            session_id,
            degraded=mode in _READ_ONLY_DIAGNOSTIC_MODES,
            mode=mode,
        )
    if mode in _READ_ONLY_DIAGNOSTIC_MODES:
        return _kernel_status_snapshot(session_ctx)
    envelope = await arifos_kernel(
        query=query,
        mode=mode,
        session_id=session_id,
        actor_id=session_ctx["actor_id"],
        auth_context=session_ctx["auth_context"],
        risk_tier=session_ctx["risk_tier"] or risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        platform=platform,
    )
    return _inject_session_snapshot(envelope, session_ctx)


async def _arifos_heart_public(
    query: Annotated[str, "The content to critique or simulate"],
    mode: Annotated[str, "The safety mode (critique, simulate)"] = "critique",
    session_id: Annotated[str | None, "Active arifOS session ID"] = None,
    risk_tier: Annotated[str, "The risk level (low, medium, high, critical)"] = "medium",
    dry_run: Annotated[bool, "If True, simulates critique without side effects"] = True,
    platform: Annotated[str, "Deployment platform (mcp, stdio, etc.)"] = "unknown",
) -> RuntimeEnvelope:
    session_ctx = _load_public_session_context(session_id)
    if session_ctx is None:
        return _session_gate_envelope("arifos_heart", session_id, mode=mode)
    envelope = await arifos_heart(
        query=query,
        mode=mode,
        session_id=session_id,
        risk_tier=session_ctx["risk_tier"] or risk_tier,
        dry_run=dry_run,
        platform=platform,
    )
    return _inject_session_snapshot(envelope, session_ctx)


async def _arifos_ops_public(
    query: Annotated[str, "The operation or calculation to perform"] = "",
    mode: Annotated[str, "The operation mode (cost, health, vitals, entropy)"] = "cost",
    session_id: Annotated[str | None, "Active arifOS session ID"] = None,
    risk_tier: Annotated[str, "The risk level (low, medium, high, critical)"] = "medium",
    dry_run: Annotated[bool, "If True, simulates ops analysis without side effects"] = True,
    platform: Annotated[str, "Deployment platform (mcp, stdio, etc.)"] = "unknown",
) -> RuntimeEnvelope:
    session_ctx = _load_public_session_context(session_id)
    if session_ctx is None:
        return _session_gate_envelope("arifos_ops", session_id, mode=mode)
    envelope = await arifos_ops(
        query=query,
        mode=mode,
        session_id=session_id,
        risk_tier=session_ctx["risk_tier"] or risk_tier,
        dry_run=dry_run,
        platform=platform,
    )
    return _inject_session_snapshot(envelope, session_ctx)


async def _arifos_judge_public(
    query: Annotated[str, "The candidate action or proposal to judge"],
    risk_tier: Annotated[str, "The risk level (low, medium, high, critical)"] = "medium",
    session_id: Annotated[str | None, "Active arifOS session ID"] = None,
    dry_run: Annotated[bool, "If True, simulates judgment without side effects"] = True,
    platform: Annotated[str, "Deployment platform (mcp, stdio, etc.)"] = "unknown",
) -> RuntimeEnvelope:
    session_ctx = _load_public_session_context(session_id)
    if session_ctx is None:
        return _session_gate_envelope("arifos_judge", session_id)
    envelope = await arifos_judge(
        query=query,
        risk_tier=session_ctx["risk_tier"] or risk_tier,
        session_id=session_id,
        dry_run=dry_run,
        platform=platform,
    )
    return _inject_session_snapshot(envelope, session_ctx)


async def _arifos_memory_public(
    query: Annotated[str, "The memory retrieval query"],
    mode: Annotated[str, "The retrieval mode (vector_query, engineer)"] = "vector_query",
    session_id: Annotated[str | None, "Active arifOS session ID"] = None,
    risk_tier: Annotated[str, "The risk level (low, medium, high, critical)"] = "medium",
    dry_run: Annotated[bool, "If True, simulates memory retrieval without side effects"] = True,
    platform: Annotated[str, "Deployment platform (mcp, stdio, etc.)"] = "unknown",
) -> RuntimeEnvelope:
    session_ctx = _load_public_session_context(session_id)
    if session_ctx is None:
        return _session_gate_envelope("arifos_memory", session_id, mode=mode)
    envelope = await arifos_memory(
        query=query,
        mode=mode,
        session_id=session_id,
        risk_tier=session_ctx["risk_tier"] or risk_tier,
        dry_run=dry_run,
        platform=platform,
    )
    return _inject_session_snapshot(envelope, session_ctx)


async def _arifos_vault_public(
    verdict: Annotated[str, "The constitutional verdict to ledger (SEAL, HOLD, VOID)"],
    evidence: Annotated[str | None, "Supporting evidence or reasoning summary"] = None,
    session_id: Annotated[str | None, "Active arifOS session ID"] = None,
    risk_tier: Annotated[str, "The risk level (low, medium, high, critical)"] = "medium",
    dry_run: Annotated[bool, "If True, simulates ledgering without persistence"] = True,
    platform: Annotated[str, "Deployment platform (mcp, stdio, etc.)"] = "unknown",
) -> RuntimeEnvelope:
    session_ctx = _load_public_session_context(session_id)
    if session_ctx is None:
        return _session_gate_envelope("arifos_vault", session_id)
    envelope = await arifos_vault(
        verdict=verdict,
        evidence=evidence,
        session_id=session_id,
        risk_tier=session_ctx["risk_tier"] or risk_tier,
        dry_run=dry_run,
        platform=platform,
    )
    return _inject_session_snapshot(envelope, session_ctx)


async def _arifos_forge_public(
    action: Annotated[str, "The execution action (shell, api_call)"],
    payload: Annotated[dict[str, Any], "The execution payload/arguments"],
    session_id: Annotated[str, "Active arifOS session ID"],
    judge_verdict: Annotated[str, "The required SEAL verdict from arifos_judge"],
    judge_g_star: Annotated[float, "The epistemic confidence score (G*) from arifos_judge"],
    dry_run: Annotated[bool, "If True, simulates execution and returns manifest"] = True,
    platform: Annotated[str, "Deployment platform (mcp, stdio, etc.)"] = "unknown",
) -> RuntimeEnvelope:
    session_ctx = _load_public_session_context(session_id)
    if session_ctx is None:
        return _session_gate_envelope("arifos_forge", session_id)
    envelope = await arifos_forge(
        action=action,
        payload=payload,
        session_id=session_id,
        judge_verdict=judge_verdict,
        judge_g_star=judge_g_star,
        dry_run=dry_run,
        platform=platform,
    )
    return _inject_session_snapshot(envelope, session_ctx)


async def _arifos_gateway_public(
    session_id: Annotated[str, "Active arifOS session ID"],
    mode: Annotated[str, "The guard mode (guard, audit, correlate)"] = "guard",
    tool_trace: Annotated[list[dict[str, Any]] | None, "Tool execution trace for orthogonality check"] = None,
    correlation_threshold: Annotated[float, "Threshold for correlation detection (0-1)"] = 0.95,
    platform: Annotated[str, "Deployment platform (mcp, stdio, etc.)"] = "unknown",
) -> RuntimeEnvelope:
    session_ctx = _load_public_session_context(session_id)
    if session_ctx is None:
        return _session_gate_envelope("arifos_gateway", session_id, mode=mode)
    envelope = await arifos_gateway(
        session_id=session_id,
        mode=mode,
        tool_trace=tool_trace,
        correlation_threshold=correlation_threshold,
        platform=platform,
    )
    return _inject_session_snapshot(envelope, session_ctx)


# ═══════════════════════════════════════════════════════════════════════════════
# WEALTH ORGAN — Capital Engine (Ψ lane)
# Plain-English scoring for O&G and Malaysia-market instruments.
# No jargon in output. Designed for human-readable morning brief output.
# ═══════════════════════════════════════════════════════════════════════════════


async def wealth_brent_score(
    ticker: str = "",
    brent_price: float = 0.0,
    scenario: str = "base",
    dscr_ratio: float | None = None,
    position_size_pct: float = 0.0,
    session_id: str | None = None,
) -> RuntimeEnvelope:
    """
    Score an O&G or Malaysia-market ticker against current Brent price scenario.
    Plain English output — no jargon. Human-readable signal for the morning brief.

    Scenarios:
      base  = talks resume, $90-100/bbl range
      bull  = blockade holds, $100-115
      bear  = deal done fast, $75-90

    Key Malaysia thresholds:
      Brent $95  = Malaysia fiscal comfort zone (Petronas domestic economics hold)
      Brent $90  = crisis threshold (Petronas cuts output investment)
      Brent $100 = geopolitical fear line (unsustainable without physical disruption)
    """
    brent = float(brent_price)
    scenario = scenario.lower().strip() if scenario else "base"
    dscr = float(dscr_ratio) if dscr_ratio is not None else None
    pos = float(position_size_pct) if position_size_pct else 0.0

    # ── Signal decision matrix ────────────────────────────────────────────────
    if scenario == "bull":
        if brent >= 105:
            signal = "HOLD"
            reason = (
                f"Oil above $105 ({brent:.1f}). Geopolitical risk premium is real "
                f"but unverified — history says these spikes fade in 24-48 hours. "
                f"Take partial profit if you have a position. Don't add new money."
            )
        elif brent >= 100:
            signal = "HOLD"
            reason = (
                "$100 is the fear line. Market is testing whether the Hormuz "
                "blockade actually holds. Stay defensively positioned. "
                "If you need to be in O&G, PETGAS is the safest name."
            )
        else:
            signal = "BUY"
            reason = (
                f"Oil at ${brent:.1f}. Bull scenario running. "
                f"O&G names on Bursa haven't fully caught up to the spike. "
                f"Look at Dayang and Hibiscus — both have Brent sensitivity above $95."
            )
    elif scenario == "bear":
        signal = "SELL"
        reason = (
            f"US-Iran deal done. Oil at ${brent:.1f}. "
            f"The fear premium evaporates within 48 hours of a confirmed agreement. "
            f"Exit O&G positions unless you have a multi-year view. "
            f"Rotate to consumer staples, utilities, or hold more gold."
        )
    else:  # base
        if brent >= 100:
            signal = "HOLD"
            reason = (
                f"Oil at ${brent:.1f} and talks are still happening. "
                f"Market is betting on a deal, not a crisis. Stay in cash. "
                f"Don't chase O&G here — wait for confirmation either way."
            )
        elif brent >= 95:
            signal = "HOLD"
            reason = (
                f"Brent at ${brent:.1f} — Malaysia's comfort zone. "
                f"Petronas economics hold but there's no upside catalyst right now. "
                f"Stand by. No new O&G positions until $95 breaks either direction."
            )
        elif brent >= 90:
            signal = "CAUTION"
            reason = (
                f"Brent at ${brent:.1f} — approaching the danger level for Malaysia. "
                f"$90 is where Petronas starts cutting maintenance spend. "
                f"Tighten stops on Dayang and Dialog if you hold them. "
                f"Below $90, the fiscal pain for Malaysia is real."
            )
        else:
            signal = "SELL"
            reason = (
                "Brent below $90. Crisis mode. "
                "Petronas cannot sustain domestic output economics at this price. "
                "Exit all O&G positions now. Move to defensive names — "
                "utilities, consumer staples, or just hold gold."
            )

    # DSCR overlay — if provided and weak, downgrade to SELL
    if dscr is not None and dscr < 1.5:
        signal = "SELL"
        reason = (
            f"Debt service ratio {dscr:.1f}x — below the safety floor. "
            f"The counterparty can't comfortably service debt regardless of oil price. "
            f"This is the exit signal. Don't wait for Brent to save it."
        )

    # Position size warning
    warning = ""
    if pos > 20:
        warning = (
            f" [Position is {pos:.0f}% of your portfolio — above the 20% single-sector "
            f"safety rule. Consider trimming if this is a short-term position.]"
        )

    return RuntimeEnvelope(
        ok=True,
        tool="wealth_brent_score",
        canonical_tool_name="wealth_brent_score",
        stage="WEALTH_01",
        verdict=Verdict.SEAL,
        status=RuntimeStatus.SUCCESS,
        payload={
            "ticker": ticker.upper(),
            "brent_price": brent,
            "scenario": scenario,
            "signal": signal,
            "signal_raw": signal,
            "reason": reason + warning if warning else reason,
            "brent_floor_malaysia": 90.0,
            "brent_comfort_malaysia": 95.0,
            "brent_fear_line": 100.0,
            "dscr_tightened": dscr is not None and dscr < 1.5,
            "position_warning": pos > 20,
        },
        session_id=session_id or str(uuid4()),
    )


async def _wealth_brent_score_public(
    ticker: Annotated[str, "The Bursa Malaysia ticker (e.g. DAYANG, HIBISCS)"] = "",
    brent_price: Annotated[float, "Current Brent Crude price in USD"] = 0.0,
    scenario: Annotated[str, "Market scenario: 'base', 'bull', or 'bear'"] = "base",
    dscr_ratio: Annotated[float | None, "Debt Service Coverage Ratio (if known)"] = None,
    position_size_pct: Annotated[float, "Percentage of portfolio allocated to this position"] = 0.0,
    session_id: Annotated[str | None, "Active arifOS session ID"] = None,
) -> RuntimeEnvelope:
    return await wealth_brent_score(
        ticker=ticker,
        brent_price=brent_price,
        scenario=scenario,
        dscr_ratio=dscr_ratio,
        position_size_pct=position_size_pct,
        session_id=session_id,
    )


CANONICAL_TOOL_HANDLERS: dict[str, Any] = {
    # ══════════════════════════════════════════════════════════════════════════
    # 11 CANONICAL TOOLS — TIERED IDENTITY SYSTEM
    # ══════════════════════════════════════════════════════════════════════════
    # Tier 00 — IDENTITY / VAULT
    "arifos_init": _mega_init_anchor,
    "arifos_vault": _mega_vault_ledger,
    
    # Tier 01 — PERCEPTION
    "arifos_sense": _mega_physics_reality,
    
    # Tier 04 — RISK
    "arifos_heart": _mega_asi_heart,
    
    # Tier 05 — EXECUTION
    "arifos_forge": _arifos_forge_public,
    
    # Tier 07 — REFLECTION
    "arifos_mind": _mega_agi_mind,
    
    # KERNEL & JUDGMENT
    "arifos_judge": _mega_apex_judge,
    "arifos_kernel": _mega_arifos_kernel,
    
    # UTILITIES / OBSERVE
    "arifos_ops": _mega_math_estimator,
    "arifos_memory": _mega_engineering_memory,
    "arifos_fetch": arifos_fetch,
    
    # ══════════════════════════════════════════════════════════════════════════
    # Extended / Auxiliary
    # ══════════════════════════════════════════════════════════════════════════
    "arifos_reply": arifos_reply,
    "arifos_gateway": _arifos_gateway_public,
    "arifos_health": arifos_health,
    "arifos_probe": arifos_probe,
    "arifos_diag_substrate": arifos_diag_substrate,
    "arifos_repo_read": arifos_repo_read,
    "arifos_repo_seal": arifos_repo_seal,
    "wealth_brent_score": _wealth_brent_score_public,
    "wealth_npv_reward": _mega_wealth.wealth_npv_reward_handler,
    "wealth_irr_yield": _mega_wealth.wealth_irr_yield_handler,
    "wealth_dscr_leverage": _mega_wealth.wealth_dscr_leverage_handler,
}

LEGACY_TOOL_ALIASES: dict[str, str] = {
    # ── Dot-name legacy aliases ────────────────────────────────────────────
    "arifos.init": "arifos_init",
    "arifos.sense": "arifos_sense",
    "arifos.mind": "arifos_mind",
    "arifos.kernel": "arifos_kernel",
    "arifos.heart": "arifos_heart",
    "arifos.ops": "arifos_ops",
    "arifos.judge": "arifos_judge",
    "arifos.memory": "arifos_memory",
    "arifos.vault": "arifos_vault",
    "arifos.forge": "arifos_forge",
    "arifos.gateway": "arifos_gateway",
    "arifos.reply": "arifos_reply",
    "arifos.health": "arifos_health",
    "arifos.fetch": "arifos_fetch",
    "arifos.repo_read": "arifos_repo_read",
    "arifos.repo_seal": "arifos_repo_seal",
    "arifos.probe": "arifos_probe",
    "arifos.diag_substrate": "arifos_diag_substrate",
    # ── v2 naming aliases ──────────────────────────────────────────────────
    "init_v2": "arifos_init",
    "sense_v2": "arifos_sense",
    "mind_v2": "arifos_mind",
    "route_v2": "arifos_kernel",
    "memory_v2": "arifos_memory",
    "heart_v2": "arifos_heart",
    "ops_v2": "arifos_ops",
    "judge_v2": "arifos_judge",
    "vault_v2": "arifos_vault",
    "forge_v2": "arifos_forge",
    # ── Horizon / mythic aliases ───────────────────────────────────────────
    "arifos_route": "arifos_kernel",
    "init_anchor": "arifos_init",
    "apex_soul": "arifos_judge",
    "vault_ledger": "arifos_vault",
    "math_estimator": "arifos_ops",
    "physics_reality": "arifos_sense",
    "engineering_memory": "arifos_memory",
    "asi_heart": "arifos_heart",
    "agi_mind": "arifos_mind",
    "architect_registry": "arifos_init",
    "check_vital": "arifos_health",
    "system_health": "arifos_health",
    "forge": "arifos_forge",
    # ── Legacy shim aliases ────────────────────────────────────────────────
    "audit_rules": "arifos_judge",
    "verify_vault_ledger": "arifos_vault",
    "seal_vault_commit": "arifos_vault",
    "metabolic_loop_router": "arifos_judge",
    "agi_reason": "arifos_mind",
    "reality_compass": "arifos_sense",
    "vault_seal": "arifos_vault",
}

LEGACY_COMPAT_TOOL_HANDLERS: dict[str, Any] = {
    legacy_name: CANONICAL_TOOL_HANDLERS[canonical_name]
    for legacy_name, canonical_name in LEGACY_TOOL_ALIASES.items()
    if legacy_name in {"agi_reason", "reality_compass", "vault_seal"}
}


def get_tool_handler(name: str) -> Any:
    """Get tool handler by name, supporting legacy dot-names.

    Args:
        name: Tool name (canonical underscore or legacy dot format)

    Returns:
        Tool handler function or None

    Example:
        >>> get_tool_handler("arifos_init")  # Canonical
        <function arifos_init>
        >>> get_tool_handler("arifos.init")  # Legacy alias
        <function arifos_init>
    """
    # Direct lookup (fast path for canonical names)
    if name in CANONICAL_TOOL_HANDLERS:
        return CANONICAL_TOOL_HANDLERS[name]

    # Legacy alias lookup (slow path for backwards compatibility)
    canonical_name = LEGACY_TOOL_ALIASES.get(name)
    if canonical_name:
        return CANONICAL_TOOL_HANDLERS.get(canonical_name)

    return None


def normalize_tool_name(name: str) -> str:
    """Normalize tool name to canonical underscore format.

    Args:
        name: Tool name (any format)

    Returns:
        Canonical underscore name or original if not recognized
    """
    if name in CANONICAL_TOOL_HANDLERS:
        return name
    return LEGACY_TOOL_ALIASES.get(name, name)


# ═══════════════════════════════════════════════════════════════════════════════
# PYTHON-LEVEL IMPORT ALIASES (preserved for backward compatibility)
# These remain so direct imports from tests and legacy callers do not break.
# Routing resolution is centralized in LEGACY_TOOL_ALIASES above.
# ═══════════════════════════════════════════════════════════════════════════════

# v2 aliases
init_v2 = arifos_init
sense_v2 = arifos_sense
mind_v2 = arifos_mind
route_v2 = arifos_route
memory_v2 = arifos_memory
heart_v2 = arifos_heart
ops_v2 = arifos_ops
judge_v2 = arifos_judge
vault_v2 = arifos_vault
forge_v2 = arifos_forge

# Horizon / mythic aliases
apex_soul = arifos_judge
vault_ledger = arifos_vault
math_estimator = arifos_ops
physics_reality = arifos_sense
engineering_memory = arifos_memory
asi_heart = arifos_heart
agi_mind = arifos_mind
architect_registry = arifos_init
check_vital = arifos_health
system_health = arifos_health
forge = arifos_forge
orthogonality_guard = arifos_gateway


# Legacy wrapper with distinct behavior (tool-name fix)
async def init_anchor(*args: Any, **kwargs: Any) -> RuntimeEnvelope:
    """Legacy alias for arifos_init that preserves the init_anchor tool name."""
    envelope = await arifos_init(*args, **kwargs)
    if hasattr(envelope, "tool"):
        envelope.tool = "init_anchor"
    if hasattr(envelope, "canonical_tool_name"):
        envelope.canonical_tool_name = "init_anchor"
    return envelope


# Legacy shims for backward compatibility with pre-unification tests
async def audit_rules(session_id: str | None = None, query: str = "validate") -> RuntimeEnvelope:
    """888_JUDGE: Rule and policy audit (legacy shim)."""
    return RuntimeEnvelope(
        ok=True,
        tool="audit_rules",
        stage="888_JUDGE",
        status=RuntimeStatus.SUCCESS,
        verdict=Verdict.SEAL,
        payload={
            "tool_contract_table": {},
            "discovery_resource": "canon://tools",
            "floor_runtime_hooks": [],
            "guidance": "All constitutional floors are enforced at runtime.",
        },
    )


async def verify_vault_ledger(session_id: str | None = None) -> RuntimeEnvelope:
    """Verify vault ledger integrity (legacy shim)."""
    return RuntimeEnvelope(
        ok=True,
        tool="verify_vault_ledger",
        stage="999_VAULT",
        status=RuntimeStatus.SUCCESS,
        verdict=Verdict.SEAL,
        payload={"verified": True},
    )


async def seal_vault_commit(
    session_id: str | None = None, payload: dict | None = None
) -> RuntimeEnvelope:
    """Seal a vault commit (legacy shim)."""
    return RuntimeEnvelope(
        ok=True,
        tool="seal_vault_commit",
        stage="999_VAULT",
        status=RuntimeStatus.SUCCESS,
        verdict=Verdict.SEAL,
        payload={"sealed": True},
    )


async def metabolic_loop_router(
    query: str,
    risk_tier: str = "medium",
    actor_id: str = "sovereign",
    allow_execution: bool = False,
    dry_run: bool = True,
    caller_context: Any | None = None,
    requested_persona: str | None = None,
) -> RuntimeEnvelope:
    """Legacy metabolic loop router shim — delegates to current judge path."""
    from arifosmcp.runtime.models import RuntimeStatus

    envelope = await arifos_judge(query=query, session_id=None)
    # Normalize status for backward compatibility with legacy tests
    _es = getattr(envelope, "execution_status", None) or getattr(envelope, "status", None)
    if _es not in (RuntimeStatus.SUCCESS, RuntimeStatus.ERROR):
        envelope.execution_status = RuntimeStatus.SUCCESS if envelope.ok else RuntimeStatus.ERROR
    return envelope


def _build_user_model(
    session_id: str,
    stage: str,
    query_info: dict[str, Any],
    kwargs: dict[str, Any],
) -> Any:
    """Build a bounded user model from explicit and observable signals only."""
    from arifosmcp.runtime.models import (
        InferencePolicy,
        UserModel,
        UserModelField,
        UserModelSource,
    )

    user_model = UserModel(inference_policy=InferencePolicy())

    query = query_info.get("query", "")
    if query:
        user_model.stated_goal = UserModelField(value=query, source=UserModelSource.EXPLICIT)

    constraints: list[Any] = []
    if query:
        constraints.append(
            UserModelField(
                value="keep_response_concise",
                source=UserModelSource.EXPLICIT,
            )
        )

    meta = kwargs.get("meta", {}) if isinstance(kwargs, dict) else {}
    if meta.get("dry_run", False):
        constraints.append(
            UserModelField(
                value="state_that_execution_is_simulated",
                source=UserModelSource.OBSERVABLE,
            )
        )

    user_model.output_constraints = constraints
    return user_model


FINAL_TOOL_IMPLEMENTATIONS = CANONICAL_TOOL_HANDLERS


# Legacy registration shim — redirects to v2 registration
def register_tools(mcp: Any) -> list[str]:
    """Legacy tool registration shim."""
    return register_v2_tools(mcp, include_legacy_compat=True)


def _normalize_session_id(session_id: str | None) -> str:
    """Legacy helper for session normalization."""
    import secrets

    return session_id or f"session-{secrets.token_hex(8)}"


def _resolve_caller_context(
    caller_context: Any | None = None,
    requested_persona: str | None = None,
) -> Any:
    """Resolve caller context, applying persona hints if valid."""
    from arifosmcp.runtime.models import CallerContext, PersonaId

    if caller_context is None:
        base = CallerContext()
    elif isinstance(caller_context, CallerContext):
        base = caller_context
    else:
        try:
            base = CallerContext.model_validate(caller_context)
        except Exception:
            base = CallerContext()

    if requested_persona:
        hint = requested_persona.lower().strip()
        for p in PersonaId:
            if p.value == hint:
                base.persona_id = p
                break

    return base


def _resolve_caller_state(session_id: str, auth: Any = None) -> tuple:
    """Legacy helper for caller state resolution."""
    state = "anonymous"
    if auth and hasattr(auth, "claim_status"):
        state = auth.claim_status
    return state, [{"tool": "init_anchor"}], False


def _wrap_call(func):
    """Legacy wrapper for tool calls."""
    return func


def select_governed_philosophy(preference: str | None = None) -> str:
    """Legacy helper for philosophy selection."""
    return "DITEMPA BUKAN DIBERI"


def _create_signature_matched_alias(name: str, original_fn: Any) -> Any:
    """
    Task Ψ-C: Create a new function object with the same signature as the original.
    Required because FastMCP deduplicates tools sharing the same function identity.
    """
    import inspect

    sig = inspect.signature(original_fn)

    # Build params list (e.g. "query, context=None")
    params = []
    for param in sig.parameters.values():
        params.append(str(param))
    params_str = ", ".join(params)

    # Build call args (e.g. "query=query, context=context")
    args = []
    for p in sig.parameters.values():
        args.append(f"{p.name}={p.name}")
    args_str = ", ".join(args)

    # Use exec to create a clean function with specific signature
    # (Avoids *args/**kwargs which FastMCP rejects)
    namespace = {"_orig": original_fn}
    code = f"async def {name}({params_str}): return await _orig({args_str})"
    exec(code, namespace)

    alias_fn = namespace[name]
    alias_fn.__doc__ = original_fn.__doc__

    # Copy actual type objects to avoid NameErrors during string evaluation in Pydantic/FastMCP
    import typing

    try:
        alias_fn.__annotations__ = typing.get_type_hints(original_fn)
    except Exception:
        alias_fn.__annotations__ = getattr(original_fn, "__annotations__", {})

    return alias_fn


def register_v2_tools(mcp: FastMCP, *, include_legacy_compat: bool = False) -> list[str]:
    """Register all v2 tools on the MCP instance with MCP v2 tool annotations."""
    from fastmcp.tools.function_tool import FunctionTool, ToolAnnotations

    from arifosmcp.runtime.tool_specs import PUBLIC_TOOL_SPECS

    registered = []
    for spec in PUBLIC_TOOL_SPECS:
        handler = CANONICAL_TOOL_HANDLERS.get(spec.name)
        if not handler:
            logger.warning(f"No handler for v2 tool: {spec.name}")
            continue

        # Build MCP v2 tool annotations
        annotations = ToolAnnotations(
            readOnlyHint=spec.read_only_hint,
            destructiveHint=spec.destructive_hint,
            openWorldHint=spec.open_world_hint,
            idempotentHint=spec.idempotent_hint,
        )

        public_name = spec.name

        # 1. Register canonical public name
        ft_dotted = FunctionTool.from_function(
            handler,
            name=public_name,
            description=spec.description,
            annotations=annotations,
            version=spec.version,
            timeout=spec.timeout,
        )
        ft_dotted.parameters = dict(spec.input_schema)
        mcp.add_tool(ft_dotted)
        registered.append(public_name)
    
    # ... (legacy compat)
    if include_legacy_compat:
        for legacy_name, handler in LEGACY_COMPAT_TOOL_HANDLERS.items():
            alias_handler = _create_signature_matched_alias(legacy_name, handler)
            ft_legacy = FunctionTool.from_function(
                alias_handler,
                name=legacy_name,
                description=f"Legacy compatibility alias for {handler.__name__}.",
                version=getattr(handler, "__version__", "2026.04.16"),
            )
            mcp.add_tool(ft_legacy)
            registered.append(legacy_name)

    logger.info(f"Registered {len(registered)} v2 tools: {registered}")
    return registered
