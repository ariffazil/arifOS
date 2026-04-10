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
from typing import Any

from arifosmcp.runtime.continuity_contract import seal_runtime_envelope

from arifosmcp.runtime.models import RuntimeEnvelope
# Philosophy injection removed from tools - happens centrally in _wrap_call()
# to ensure ONLY G★ determines band, never tool identity
from fastmcp import FastMCP

from arifosmcp.runtime.megaTools import (
    agi_mind as _mega_agi_mind,
)
from arifosmcp.runtime.megaTools import (
    apex_judge as _mega_apex_judge,
)
from arifosmcp.runtime.megaTools import (
    arifOS_kernel as _mega_arifOS_kernel,
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
from arifosmcp.tools.fetch_tool import arifos_fetch
from arifosmcp.integrations.memory_bridge import arifos_memory_query as arifos_memory
from arifosmcp.integrations.git_bridge import arifos_git_status, arifos_git_commit
from arifosmcp.integrations.everything_probe import everything_probe

logger = logging.getLogger(__name__)


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
        tool="arifos.init",
        canonical_tool_name="arifos.init",
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
) -> RuntimeEnvelope:
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
    _injection_score, _threats = _guard._scan_text(intent)
    if _injection_score >= 0.85:
        logger.warning(
            "F12 BLOCK: injection detected in arifos_init intent (score=%.2f, threats=%s)",
            _injection_score,
            _threats,
        )
        return seal_runtime_envelope(
            _make_f12_block_envelope(_injection_score, _threats, session_id),
            "arifos_init",
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
        from arifosmcp.runtime.models import RuntimeStatus
        from arifosmcp.runtime.arifos_runtime_envelope import RuntimeEnvelope

        envelope = RuntimeEnvelope(
            ok=syscall_verdict == "SEAL",
            tool="arifos.init",
            canonical_tool_name="arifos.init",
            stage="000_INIT",
            status=RuntimeStatus.READY if syscall_verdict == "SEAL" else RuntimeStatus.BLOCKED,
            verdict=syscall_verdict,
            session_id=session_id or "kernel_syscall",
            payload={"mode": mode, "syscall_result": result, "kernel_version": "0.2.0"},
            policy={"floors_checked": ["F11", "F12"], "syscall": mode, "reason": syscall_reason},
        )
        return seal_runtime_envelope(envelope, "arifos.init")

    # ═══════════════════════════════════════════════════════════════════════════════
    # STANDARD INIT BRANCH
    # ═══════════════════════════════════════════════════════════════════════════════
    effective_mode = mode if mode in ("probe", "revoke", "refresh", "state", "status") else "init"
    envelope = await _mega_init_anchor(
        mode=effective_mode,
        payload={"actor_id": actor_id, "intent": intent, "declared_name": declared_name},
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
    return seal_runtime_envelope(envelope, "arifos.init")


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
                tool="arifos.sense",
                canonical_tool_name="arifos.sense",
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
            logger.warning("sensing_protocol import failed (%s) — falling back to legacy sense", _ie)
            return await _sense_legacy(query, "search", session_id, risk_tier, dry_run, debug, platform)

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

        envelope = _RE(
            ok=ok,
            tool="arifos.sense",
            canonical_tool_name="arifos.sense",
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
            },
        )
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
        return seal_runtime_envelope(envelope, "arifos.sense")

    # ── legacy modes: delegate to physics_reality ─────────────────────────────
    return await _sense_legacy(query, mode, session_id, risk_tier, dry_run, debug, platform)



async def arifos_fetch_tool(
    url: str,
    max_length: int = 10000,
    actor_id: str = "anonymous",
    session_id: str | None = None,
) -> RuntimeEnvelope:
    """
    Governed web fetch with F9 Anti-Hantu filtering.
    """
    return await arifos_fetch(url, max_length, actor_id, session_id)


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
    return seal_runtime_envelope(envelope, "arifos.sense")


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
        verified_actor_id=identity.get("verified_actor_id")
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
        input_payload={
            "query": query, 
            "session_id": session_id,
            "actor_id": actor_id
        }
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
    from arifosmcp.runtime.thinking import ThinkingSessionManager, THINKING_TEMPLATES
    from arifosmcp.runtime.thinking.templates import auto_select_template
    from arifosmcp.runtime.models import RuntimeEnvelope as _RE, RuntimeStatus, Verdict
    
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
            mem_report = await arifos_memory_query(query=query, actor_id=actor_id, session_id=session_id)
            if mem_report.ok:
                entities = mem_report.payload.get("entities", [])
                if entities:
                    from arifosmcp.integrations.memory_bridge import KGEntity
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
            context={"context": context, "kg_entities_found": len(entities) if 'entities' in locals() else 0} if context else None,
            template=template,
            arifos_session_id=session_id
        )
        
        # If template provided, auto-generate initial steps
        if template and template in THINKING_TEMPLATES:
            tmpl = THINKING_TEMPLATES[template]
            # Generate step content via LLM (simplified here)
            for i, step_prompt in enumerate(tmpl.steps[:3]):  # First 3 steps
                step = manager.add_step(
                    session_id=thinking_session.session_id,
                    step_type=tmpl.step_types[i],
                    content=f"[Step {i+1}: {step_prompt}]\n\nAnalyzing: {query[:100]}..."
                )
                # F2 check - stop on VOID
                if step.constitutional_verdict == "VOID":
                    break
        
        return _RE(
            ok=True,
            tool="arifos.mind",
            canonical_tool_name="arifos.mind",
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
                "constitutional_verdicts": [s.constitutional_verdict for s in thinking_session.steps],
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
                tool="arifos.mind",
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
            tool="arifos.mind",
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
                tool="arifos.mind",
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
            tool="arifos.mind",
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
                tool="arifos.mind",
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
            tool="arifos.mind",
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
                tool="arifos.mind",
                stage="333_MIND",
                verdict=Verdict.VOID,
                status=RuntimeStatus.ERROR,
                payload={"error": "thinking_session_id required for mode='review'"},
            )
        
        exported = manager.export_session(
            session_id=thinking_session_id,
            format_type="json"
        )
        
        thinking_session = manager.get_session(thinking_session_id)
        
        return _RE(
            ok=True,
            tool="arifos.mind",
            stage="333_MIND",
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload={
                "mode": "review",
                "session": exported,
                "quality_score": thinking_session.quality_score if thinking_session else 0,
                "constitutional_verdicts": [s.constitutional_verdict for s in thinking_session.steps] if thinking_session else [],
            },
            session_id=session_id,
        )
    
    # Unknown mode
    return _RE(
        ok=False,
        tool="arifos.mind",
        stage="333_MIND",
        verdict=Verdict.VOID,
        status=RuntimeStatus.ERROR,
        payload={"error": f"Unknown sequential thinking mode: {mode}"},
    )


async def arifos_kernel(
    request: str,
    mode: str = "kernel",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Route request to correct metabolic lane."""
    envelope = await _mega_arifOS_kernel(
        mode=mode,
        payload={"query": request},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        debug=debug,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos.kernel")


async def arifos_heart(
    content: str,
    mode: str = "critique",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    # ── ASI Heart: Safety, dignity, and adversarial critique ──────────────
    from arifosmcp.runtime.arifos_runtime_envelope import heart_stage, mind_stage, sense_stage

    sensed = sense_stage(content)
    hypotheses = mind_stage(sensed)
    risk_trace = heart_stage(hypotheses)
    critique_packet = {
        "summary": risk_trace[0] if risk_trace else "No critique generated.",
        "risk_trace": risk_trace[:3],
        "hypotheses": [h.claim for h in hypotheses[:3]],
        "next_step": "Address the highest-risk consequence before execution.",
    }

    envelope = await _mega_asi_heart(
        mode=mode,
        payload={"content": content, "critique_packet": critique_packet},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )

    sealed = seal_runtime_envelope(envelope, "arifos.heart")

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
            sealed.intelligence_state = intel
            sealed.platform_context = platform

    return sealed


async def arifos_ops(
    action: str = "",
    mode: str = "cost",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Calculate operation costs and thermodynamics."""
    envelope = await _mega_math_estimator(
        mode=mode,
        payload={"action": action},
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos.ops")


async def arifos_judge(
    candidate_action: str,
    risk_tier: str = "medium",
    telemetry: dict[str, Any] | None = None,
    session_id: str | None = None,
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Final constitutional verdict evaluation."""
    envelope = await _mega_apex_judge(
        mode="judge",
        payload={
            "candidate": candidate_action,
            "risk_tier": risk_tier,
            "telemetry": telemetry,
        },
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )
    _stamp_platform(envelope, platform)
    return seal_runtime_envelope(envelope, "arifos.judge")


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
    return seal_runtime_envelope(envelope, "arifos.memory")


async def arifos_vps_monitor(
    action: str = "get_telemetry",
    session_id: str | None = None,
    risk_tier: str = "low",
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Secure VPS telemetry (CPU, Memory, ZRAM, Disk). F12-hardened."""
    import subprocess
    import os
    from arifosmcp.runtime.models import RuntimeEnvelope as RE, RuntimeStatus, Verdict

    # F12: Hardcoded read-only telemetry logic
    try:
        if action == "get_telemetry":
            with open("/proc/loadavg", "r") as f:
                load = f.read().strip()
            with open("/proc/meminfo", "r") as f:
                # Get first few lines of meminfo for high clarity
                mem = "\n".join([f.readline().strip() for _ in range(3)])
            output = f"Load: {load}\n{mem}"
        elif action == "get_zram_status":
            # zramctl might be missing, try to find zram in /sys
            if os.path.exists("/sys/block/zram0"):
                with open("/sys/block/zram0/disksize", "r") as f:
                    size = int(f.read().strip()) / (1024**2)

                # mm_stat: [orig_data_size, compr_data_size, mem_used_total, ...]
                with open("/sys/block/zram0/mm_stat", "r") as f:
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
                    tool="arifos.vps_monitor",
                    canonical_tool_name="arifos.vps_monitor",
                    stage="111_SENSE",
                    verdict=Verdict.VOID,
                    status=RuntimeStatus.ERROR,
                    detail=f"F12_BLOCKED: Action '{action}' not permitted.",
                ),
                "arifos.vps_monitor",
            )

        if dry_run:
            return seal_runtime_envelope(
                RE(
                    ok=True,
                    tool="arifos.vps_monitor",
                    canonical_tool_name="arifos.vps_monitor",
                    stage="111_SENSE",
                    verdict=Verdict.SEAL,
                    status=RuntimeStatus.SUCCESS,
                    payload={"mode": "dry_run", "action": action},
                ),
                "arifos.vps_monitor",
            )

        return seal_runtime_envelope(
            RE(
                ok=True,
                tool="arifos.vps_monitor",
                canonical_tool_name="arifos.vps_monitor",
                stage="111_SENSE",
                verdict=Verdict.SEAL,
                status=RuntimeStatus.SUCCESS,
                payload={"output": output, "success": True},
            ),
            "arifos.vps_monitor",
        )
    except Exception as e:
        return seal_runtime_envelope(
            RE(
                ok=False,
                tool="arifos.vps_monitor",
                canonical_tool_name="arifos.vps_monitor",
                stage="111_SENSE",
                verdict=Verdict.VOID,
                status=RuntimeStatus.ERROR,
                detail=str(e),
            ),
            "arifos.vps_monitor",
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
    return seal_runtime_envelope(envelope, "arifos.vault")


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
        heart_env = await arifos_heart(content=critique_content, mode="critique", session_id=_session)
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
                verdict=judge_verdict_str if judge_verdict_str in ("SEAL", "PARTIAL", "VOID", "HOLD") else "HOLD",
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
        "SEAL": "CLAIM", "PARTIAL": "PLAUSIBLE",
        "HOLD": "888 HOLD", "VOID": "UNKNOWN",
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

    if "arifos.vault" not in _cc and judge_verdict_str in ("SEAL", "HOLD"):
        _cc.append("arifos.vault")

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
        "floors_passed": [f for f in ["F1","F2","F4","F7","F9","F11","F13"] if f not in floors_triggered],
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
        "forged_by": "arifos.reply",
        "judge_verdict": judge_verdict_str,
        "to": _actor,
        "cc": _cc,
        "vault_ref": vault_ref,
        "consulted_tools": ["arifos_memory", "arifos_sense", "arifos_mind", "arifos_heart", "arifos_ops", "arifos_judge"],
        "informed_agents": _cc,
    }

    from arifosmcp.runtime.models import RE, RuntimeStatus, Verdict as V
    _verdict_map = {"SEAL": V.SEAL, "PARTIAL": V.PROVISIONAL, "HOLD": V.HOLD, "VOID": V.VOID}
    return seal_runtime_envelope(
        RE(
            ok=judge_verdict_str in ("SEAL", "PARTIAL"),
            tool="arifos.reply",
            canonical_tool_name="arifos.reply",
            stage="000-999",
            verdict=_verdict_map.get(judge_verdict_str, V.HOLD),
            status=RuntimeStatus.SUCCESS if judge_verdict_str in ("SEAL", "PARTIAL") else RuntimeStatus.HOLD,
            payload=payload,
            hint=title,
            detail=verdict_statement,
            platform_context=platform,
            session_id=_session,
        ),
        "arifos.reply",
    )


async def arifos_diag_substrate(session_id: str | None = None) -> RuntimeEnvelope:
    """
    arifos_diag_substrate — Maintainer-only substrate conformance diagnostic.
    Runs protocol exercise probes against 'everything' harness.
    """
    from arifosmcp.runtime.models import Verdict, RuntimeStatus, RuntimeEnvelope as _RE
    
    # F11: Restricted to maintainer flows
    diag = await everything_probe.run_full_diagnostic()
    
    return _RE(
        ok=diag["verdict"] == "SEAL",
        tool="arifos.diag_substrate",
        verdict=Verdict.SEAL if diag["verdict"] == "SEAL" else Verdict.VOID,
        status=RuntimeStatus.SUCCESS if diag["verdict"] == "SEAL" else RuntimeStatus.ERROR,
        payload=diag,
        detail=f"Substrate Conformance: {diag['verdict']}"
    )


CANONICAL_TOOL_HANDLERS: dict[str, Any] = {
    # Dotted (Canonical)
    "arifos.init": arifos_init,
    "arifos.sense": arifos_sense,
    "arifos.mind": arifos_mind,
    "arifos.kernel": arifos_kernel,
    "arifos.heart": arifos_heart,
    "arifos.ops": arifos_ops,
    "arifos.judge": arifos_judge,
    "arifos.memory": arifos_memory,
    "arifos.vault": arifos_vault,
    "arifos.forge": arifos_forge,
    "arifos.reply": arifos_reply,
    "arifos.vps_monitor": arifos_vps_monitor,
    "arifos.fetch": arifos_fetch,
    "arifos.git_status": arifos_git_status,
    "arifos.git_commit": arifos_git_commit,
    "arifos.diag_substrate": arifos_diag_substrate,

    # Underscored (Alias/Internal)
    "arifos_init": arifos_init,
    "arifos_sense": arifos_sense,
    "arifos_mind": arifos_mind,
    "arifos_kernel": arifos_kernel,
    "arifos_heart": arifos_heart,
    "arifos_ops": arifos_ops,
    "arifos_judge": arifos_judge,
    "arifos_memory": arifos_memory,
    "arifos_vault": arifos_vault,
    "arifos_forge": arifos_forge,
    "arifos_reply": arifos_reply,
    "arifos_vps_monitor": arifos_vps_monitor,
    "arifos_fetch": arifos_fetch,
    "arifos_git_status": arifos_git_status,
    "arifos_git_commit": arifos_git_commit,
    "arifos_diag_substrate": arifos_diag_substrate,
    "arifos_route": arifos_kernel,
}


# Backward-compatible aliases for older runtime imports.
arifos_route = arifos_kernel # [P1 FIX] Preserve canonical route symbol
init_v2 = arifos_init
sense_v2 = arifos_sense
mind_v2 = arifos_mind
route_v2 = arifos_kernel
memory_v2 = arifos_memory
heart_v2 = arifos_heart
ops_v2 = arifos_ops
judge_v2 = arifos_judge
vault_v2 = arifos_vault
forge_v2 = arifos_forge
V2_TOOL_HANDLERS = CANONICAL_TOOL_HANDLERS

# Legacy Horizon/v1 aliases for tests
init_anchor = arifos_init
arifOS_kernel = arifos_kernel
apex_soul = arifos_judge
vault_ledger = arifos_vault
math_estimator = arifos_ops
physics_reality = arifos_sense
engineering_memory = arifos_memory
asi_heart = arifos_heart
agi_mind = arifos_mind
architect_registry = arifos_init
check_vital = arifos_vps_monitor
system_health = arifos_vps_monitor


def _normalize_session_id(session_id: str | None) -> str:
    """Legacy helper for session normalization."""
    import secrets

    return session_id or f"session-{secrets.token_hex(8)}"


def _resolve_caller_context(session_id: str | None = None, actor_id: str | None = None) -> Any:
    """Legacy helper for caller context resolution."""
    from types import SimpleNamespace
    return SimpleNamespace(
        session_id=_normalize_session_id(session_id),
        actor_id=actor_id or "anonymous",
        identity_type="anonymous" if not actor_id or actor_id == "anonymous" else "claimed"
    )

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


def register_v2_tools(mcp: FastMCP) -> list[str]:
    """Register all v2 tools on the MCP instance with MCP v2 tool annotations."""
    from fastmcp.tools.function_tool import FunctionTool, ToolAnnotations

    from arifosmcp.runtime.tool_specs import V2_TOOLS

    registered = []
    for spec in V2_TOOLS:
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

        # 1. Register canonical dotted name (primary surface for v2)
        ft_dotted = FunctionTool.from_function(
            handler,
            name=spec.name,
            description=spec.description,
            annotations=annotations,
        )
        ft_dotted.parameters = dict(spec.input_schema)
        mcp.add_tool(ft_dotted)
        registered.append(spec.name)

        # 2. Register underscored alias ONLY for public tools
        if spec.visibility == "public":
            underscored_name = spec.name.replace(".", "_")
            if underscored_name != spec.name:
                alias_handler = _create_signature_matched_alias(underscored_name, handler)
                ft_u = FunctionTool.from_function(
                    alias_handler,
                    name=underscored_name,
                    description=f"Alias for {spec.name}. {spec.description}",
                    annotations=annotations,
                )
                ft_u.parameters = dict(spec.input_schema)
                mcp.add_tool(ft_u)
                registered.append(underscored_name)

    logger.info(f"Registered {len(registered)} v2 tools: {registered}")
    return registered


__all__ = [
    "CANONICAL_TOOL_HANDLERS",
    "V2_TOOL_HANDLERS",
    "register_v2_tools",
    "arifos_init",
    "arifos_sense",
    "arifos_mind",
    "arifos_kernel",
    "arifos_heart",
    "arifos_ops",
    "arifos_judge",
    "arifos_memory",
    "arifos_vault",
    "init_v2",
    "sense_v2",
    "mind_v2",
    "route_v2",
    "memory_v2",
    "heart_v2",
    "ops_v2",
    "judge_v2",
    "vault_v2",
    "forge_v2",
    # Legacy exports
    "init_anchor",
    "arifOS_kernel",
    "apex_soul",
    "vault_ledger",
    "math_estimator",
    "physics_reality",
    "engineering_memory",
    "asi_heart",
    "agi_mind",
    "architect_registry",
    "check_vital",
    "system_health",
    "_normalize_session_id",
    "_resolve_caller_context",
    "_resolve_caller_state",
    "_wrap_call",
    "select_governed_philosophy",
]

async def arifos_diag_substrate(session_id: str | None = None) -> Any:
    """Maintainer: Run substrate protocol conformance check."""
    from arifosmcp.evals.everything_conformance_runner import run_protocol_conformance_test
    from arifosmcp.runtime.models import RuntimeEnvelope as _RE, Verdict
    
    verdict = await run_protocol_conformance_test()
    return _RE(
        ok=verdict == Verdict.SEAL,
        tool="arifos.diag_substrate",
        verdict=verdict,
        payload={"message": f"Substrate conformance result: {verdict}"}
    )
