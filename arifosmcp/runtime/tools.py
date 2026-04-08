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
from typing import Any

from arifosmcp.runtime.continuity_contract import seal_runtime_envelope

# RuntimeEnvelope is a dict type for tool outputs
RuntimeEnvelope = dict[str, Any]
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
            tool="arifos_init",
            canonical_tool_name="arifos_init",
            stage="000_INIT",
            status=RuntimeStatus.READY if syscall_verdict == "SEAL" else RuntimeStatus.BLOCKED,
            verdict=syscall_verdict,
            session_id=session_id or "kernel_syscall",
            payload={"mode": mode, "syscall_result": result, "kernel_version": "0.2.0"},
            policy={"floors_checked": ["F11", "F12"], "syscall": mode, "reason": syscall_reason},
        )
        return seal_runtime_envelope(envelope, "arifos_init")

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
    return seal_runtime_envelope(envelope, "arifos_init")


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
        from arifosmcp.runtime.sensing_protocol import (
            TimeScope,
            normalize_query,
        )
        from arifosmcp.runtime.sensing_protocol import (
            governed_sense as _governed_sense,
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
            },
        )
        if debug:
            envelope.debug = {
                "intel_state_full": intel_state.to_dict(),
                "truth_vector": intel_state.truth_vector.to_dict(),
            }
        _stamp_platform(envelope, platform)
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
    query: str,
    context: str | None = None,
    mode: str = "reason",
    session_id: str | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    debug: bool = False,
    platform: str = "unknown",
) -> RuntimeEnvelope:
    """Structured reasoning with typed cognitive pipeline.

    Runs the constitutional AGI pipeline (sense → mind → heart → judge)
    producing a narrow decision_packet for the operator and a full
    audit_packet for the vault.  Internal richness, external compression.
    """
    from arifosmcp.runtime.arifos_runtime_envelope import run_agi_mind

    # ── Typed pipeline: sense → mind → heart → judge ─────────────────────
    decision_packet, audit_packet = await run_agi_mind(
        raw_input=query,
        session_id=session_id,
        additional_context=context or "",
    )

    # ── Forward enriched payload through mega tool ────────────────────────
    envelope = await _mega_agi_mind(
        mode=mode,
        payload={
            "query": query,
            "context": context,
            "decision_packet": decision_packet,
        },
        session_id=session_id,
        risk_tier=risk_tier,
        dry_run=dry_run,
        debug=debug,
    )

    # ── Seal and inject typed packets into intelligence_state ─────────────
    sealed = seal_runtime_envelope(envelope, "arifos_mind")

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


async def arifos_route(
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
    return seal_runtime_envelope(envelope, "arifos_route")


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
            sealed.intelligence_state = intel
            sealed.platform_context = platform

    return sealed


async def arifos_ops(
    action: str,
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
    return seal_runtime_envelope(envelope, "arifos_ops")


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
    return seal_runtime_envelope(envelope, "arifos_judge")


async def arifos_memory(
    query: str,
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
                    tool="arifos_vps_monitor",
                    canonical_tool_name="arifos_vps_monitor",
                    stage="111_SENSE",
                    verdict=Verdict.VOID,
                    status=RuntimeStatus.ERROR,
                    detail=f"F12_BLOCKED: Action '{action}' not permitted.",
                ),
                "arifos_vps_monitor",
            )

        if dry_run:
            return seal_runtime_envelope(
                RE(
                    ok=True,
                    tool="arifos_vps_monitor",
                    canonical_tool_name="arifos_vps_monitor",
                    stage="111_SENSE",
                    verdict=Verdict.SEAL,
                    status=RuntimeStatus.SUCCESS,
                    payload={"mode": "dry_run", "action": action},
                ),
                "arifos_vps_monitor",
            )

        return seal_runtime_envelope(
            RE(
                ok=True,
                tool="arifos_vps_monitor",
                canonical_tool_name="arifos_vps_monitor",
                stage="111_SENSE",
                verdict=Verdict.SEAL,
                status=RuntimeStatus.SUCCESS,
                payload={"output": output, "success": True},
            ),
            "arifos_vps_monitor",
        )
    except Exception as e:
        return seal_runtime_envelope(
            RE(
                ok=False,
                tool="arifos_vps_monitor",
                canonical_tool_name="arifos_vps_monitor",
                stage="111_SENSE",
                verdict=Verdict.VOID,
                status=RuntimeStatus.ERROR,
                detail=str(e),
            ),
            "arifos_vps_monitor",
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


# ═══════════════════════════════════════════════════════════════════════════════
# V2 TOOL HANDLER REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

# Import the 10th tool (Delegated Execution Bridge)
from arifosmcp.runtime.tools_forge import arifos_forge

CANONICAL_TOOL_HANDLERS: dict[str, Any] = {
    "arifos_init": arifos_init,
    "arifos_sense": arifos_sense,
    "arifos_mind": arifos_mind,
    "arifos_route": arifos_route,
    "arifos_heart": arifos_heart,
    "arifos_ops": arifos_ops,
    "arifos_judge": arifos_judge,
    "arifos_memory": arifos_memory,
    "arifos_vault": arifos_vault,
    "arifos_forge": arifos_forge,  # The 10th Tool — Delegated Execution
    "arifos_vps_monitor": arifos_vps_monitor,
}


# Backward-compatible aliases for older runtime imports.
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
V2_TOOL_HANDLERS = CANONICAL_TOOL_HANDLERS

# Legacy Horizon/v1 aliases for tests
init_anchor = arifos_init
arifOS_kernel = arifos_route
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


def register_v2_tools(mcp: FastMCP) -> list[str]:
    """Register all v2 tools on the MCP instance."""
    from fastmcp.tools.function_tool import FunctionTool

    from arifosmcp.runtime.tool_specs import V2_TOOLS

    registered = []
    for spec in V2_TOOLS:
        handler = CANONICAL_TOOL_HANDLERS.get(spec.name)
        if not handler:
            logger.warning(f"No handler for v2 tool: {spec.name}")
            continue

        ft = FunctionTool.from_function(
            handler,
            name=spec.name,
            description=spec.description,
        )
        ft.parameters = dict(spec.input_schema)
        mcp.add_tool(ft)
        registered.append(spec.name)

    logger.info(f"Registered {len(registered)} v2 tools: {registered}")
    return registered


__all__ = [
    "CANONICAL_TOOL_HANDLERS",
    "V2_TOOL_HANDLERS",
    "register_v2_tools",
    "arifos_init",
    "arifos_sense",
    "arifos_mind",
    "arifos_route",
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
