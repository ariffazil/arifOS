"""
arifOS Output Formatter — 3-Tier Clarity Model
═══════════════════════════════════════════════════════════════════════════════

Implements the clean output schema for human/AI operator clarity.

Usage:
    from arifosmcp.runtime.output_formatter import format_output

    # In any tool handler:
    return format_output(
        envelope=runtime_envelope,
        options={"verbose": False, "debug": False},
    )
"""

from __future__ import annotations

from typing import Any

import hashlib

from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
from arifosmcp.runtime.schemas import (
    CleanOutput,
    ExecutionResult,
    GovernanceVerdict,
    OperatorAction,
    ContextSummary,
    HumanLanguageBlock,
    UniversalContext,
    CleanError,
    DebugForensics,
    build_system_view,
    build_forensic_view,
    AgiReplyHeader,
    AgiReplyRACI,
    AgiReplySeal,
    AgiReplyGovernanceTrace,
    AgiReplyEnvelopeHuman,
    AgiReplyEnvelopeAgent,
)


def format_output(
    envelope: RuntimeEnvelope,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Format RuntimeEnvelope into platform-specific clean output.

    Args:
        envelope: The raw runtime envelope from tool execution
        options: Output control options
            - verbose: Include system/governance details
            - debug: Include full forensic state

    Returns:
        Platform-dispatched formatted data
    """
    options = options or {}
    verbose = options.get("verbose", False)
    debug = options.get("debug", False)
    platform = envelope.platform_context or "unknown"

    # ── Platform Dispatch ─────────────────────────────────────────────────────

    # 1. chatgpt_apps — widget-renderable JSON
    if platform == "chatgpt_apps":
        clean = _build_base_output(envelope)
        return _build_transport_envelope(
            envelope,
            clean.model_dump(exclude_none=True),
            platform="chatgpt_apps",
            render_hint="widget",
        )

    # 2. api — flat JSON, no MCP envelope
    if platform == "api":
        clean = _build_base_output(envelope)
        return {
            "human_language": clean.human_language.model_dump(exclude_none=True),
            "universal_context": clean.universal_context.model_dump(exclude_none=True),
            "execution": clean.execution.model_dump(exclude_none=True),
            "governance": clean.governance.model_dump(exclude_none=True),
            "error": clean.error.model_dump(exclude_none=True) if clean.error else None,
        }

    # 3. stdio — human-readable text
    if platform == "stdio":
        clean = _build_base_output(envelope)
        text = clean.human_language.summary
        context = clean.universal_context
        text += (
            f"\nContext: actor {context.actor}, session {context.session or 'unknown'}, "
            f"risk {context.risk}, platform {context.platform}, tool {context.tool}."
        )
        text += f"\nVerdict: {clean.governance.verdict} ({clean.execution.status})"
        if clean.human_language.next_step:
            text += f"\nNext: {clean.human_language.next_step}"
        return {"output": text}

    # 4. agi_reply — AGI Reply Protocol v3 dual-axis envelope
    if platform == "agi_reply":
        return _format_agi_reply(envelope)

    # 5. mcp (default) — 3-tier structure
    # Build base operator view
    clean = _build_base_output(envelope)

    # Add system view if verbose
    if verbose and not debug:
        return _build_transport_envelope(
            envelope,
            build_system_view(
                base=clean,
                kernel_version=_extract_kernel_version(envelope),
                adapter="mcp",
                env=_extract_env(envelope),
                authority=_extract_authority(envelope),
                operational_status=_extract_operational_status(envelope),
                proof_status=_extract_proof_status(envelope),
            ),
            platform="mcp",
        )

    # Add forensic view if debug
    if debug:
        base_dict = build_system_view(
            base=clean,
            kernel_version=_extract_kernel_version(envelope),
            adapter="mcp",
            env=_extract_env(envelope),
            authority=_extract_authority(envelope),
            operational_status=_extract_operational_status(envelope),
            proof_status=_extract_proof_status(envelope),
        )
        return _build_transport_envelope(
            envelope,
            build_forensic_view(
                base=CleanOutput(**base_dict),
                caller_state=envelope.caller_state,
                allowed_next_tools=list(envelope.allowed_next_tools)
                if envelope.allowed_next_tools
                else [],
                blocked_tools=envelope.blocked_tools if envelope.blocked_tools else [],
                raw_payload=envelope.payload if isinstance(envelope.payload, dict) else None,
                trace=envelope.trace,
                telemetry=envelope.metrics.model_dump() if envelope.metrics else None,
                continuity=envelope.payload.get("continuity")
                if isinstance(envelope.payload, dict)
                else None,
                handoff=envelope.handoff,
                diagnostics=envelope.diagnostics,
            ),
            platform="mcp",
        )

    # Return minimal operator view
    return _build_transport_envelope(
        envelope,
        clean.model_dump(exclude_none=True),
        platform="mcp",
    )


def _build_transport_envelope(
    envelope: RuntimeEnvelope,
    payload: dict[str, Any],
    *,
    platform: str | None = None,
    render_hint: str | None = None,
) -> dict[str, Any]:
    """Wrap formatted output in the required transport envelope without dropping clean blocks."""
    tool = envelope.canonical_tool_name or envelope.tool or "unknown"
    verdict = _map_verdict(envelope.verdict)
    allowed_next_tools = list(getattr(envelope, "allowed_next_tools", []) or [])
    next_step = (
        payload.get("human_language", {}).get("next_step")
        if isinstance(payload.get("human_language"), dict)
        else None
    )
    wrapped = {
        "tool": tool,
        "stage": envelope.stage,
        "status": _map_transport_status(envelope, verdict),
        "summary": (
            payload.get("human_language", {}).get("summary")
            if isinstance(payload.get("human_language"), dict)
            else _build_summary(envelope)
        ),
        "result": payload,
        "governance": {
            "risk_tier": envelope.risk_class.value if envelope.risk_class else "low",
            "verdict": verdict,
            "requires_human_confirmation": verdict == "HOLD",
            "candidate_action": next_step,
            "conditions": allowed_next_tools,
        },
        "context_out": {
            "memory_write_candidates": [],
            "vault_seal_candidate": verdict == "SEAL",
            "next_recommended_tools": allowed_next_tools,
            "stage_progression": allowed_next_tools,
        },
    }
    wrapped.update(payload)
    if platform:
        wrapped["platform"] = platform
    if render_hint:
        wrapped["render_hint"] = render_hint
    required_fields = ["tool", "stage", "status", "result"]
    for field in required_fields:
        if field not in wrapped:
            raise ValueError(f"Missing required MCP field: {field}")
    return wrapped


def _format_agi_reply(envelope: RuntimeEnvelope) -> dict[str, Any]:
    """
    AGI Reply Protocol v3 — DITEMPA EDITION output formatter.

    Routes to AgiReplyEnvelopeHuman or AgiReplyEnvelopeAgent based on
    envelope.payload["recipient"]. Ambiguous → human envelope + agent block appended.

    Builds:
      - AgiReplyHeader  (TO / CC / TITLE / KEY_CONTEXT)
      - AgiReplyRACI    (R/A/C/I principal roles)
      - AgiReplySeal    (cryptographic + governance signoff)
      - Full envelope   (human or agent)
    """
    from datetime import datetime, timezone

    p = envelope.payload if isinstance(envelope.payload, dict) else {}
    recipient = p.get("recipient", "auto")
    depth = p.get("depth", "ENGINEER")
    compression = p.get("compression_mode", "DELTA")
    actor = envelope.authority.actor_id if envelope.authority else "anonymous"
    session = envelope.session_id

    # ── Verdict mapping ───────────────────────────────────────────────────────
    _verdict_token_map = {
        "SEAL": "CLAIM",
        "PARTIAL": "PLAUSIBLE",
        "HOLD": "888 HOLD",
        "VOID": "UNKNOWN",
        "APPROVED": "CLAIM",
        "PAUSE": "UNKNOWN",
    }
    raw_verdict = _map_verdict(envelope.verdict)
    verdict_token = _verdict_token_map.get(raw_verdict, "UNKNOWN")

    # ── τ score — ONE canonical source, in priority order ────────────────────
    # 1. payload.tau (explicitly computed by judge from reasoning atoms)
    # 2. metrics.tau (AF-FORGE F7 proxy attached post-completion)
    # 3. fallback 0.5 (no atoms available — mark as tau_source="fallback")
    # Do NOT read from metrics.confidence — that is a separate signal.
    tau_source = "fallback"
    tau = 0.5
    if p.get("tau") is not None:
        tau = float(p["tau"])
        tau_source = p.get("tau_source", "computed")
    elif envelope.metrics and hasattr(envelope.metrics, "tau"):
        tau = float(envelope.metrics.tau)
        tau_source = "computed"
    elif envelope.metrics and hasattr(envelope.metrics, "confidence"):
        # legacy path — treat confidence as tau proxy but mark as fallback
        tau = float(envelope.metrics.confidence) * 0.85  # discount: confidence != tau
        tau_source = "fallback"

    # ── Floors ────────────────────────────────────────────────────────────────
    floors_triggered: list[str] = p.get("floors_triggered", [])
    floors_passed: list[str] = p.get("floors_passed", [])

    # ── Verdict statement ─────────────────────────────────────────────────────
    verdict_statement = (
        p.get("verdict_statement") or envelope.detail or envelope.hint or _build_summary(envelope)
    )

    # ── TITLE for header ──────────────────────────────────────────────────────
    title = f"{verdict_token} τ={tau:.2f} — {verdict_statement}"

    # ── SEAL signoff ──────────────────────────────────────────────────────────
    timestamp = datetime.now(timezone.utc).isoformat()
    forged_by = p.get("forged_by", envelope.tool or "arifos.mind")
    judge_verdict_raw = p.get("judge_verdict", raw_verdict)
    judge_verdict_seal: Any = (
        judge_verdict_raw if judge_verdict_raw in ("SEAL", "PARTIAL", "HOLD", "VOID") else "HOLD"
    )

    audit_input = f"{title}{timestamp}{forged_by}{judge_verdict_seal}"
    audit_hash = hashlib.sha256(audit_input.encode()).hexdigest()[:16]

    seal = AgiReplySeal(
        forged_by=forged_by,
        judge_verdict=judge_verdict_seal,
        tau=tau,
        tau_source=tau_source,
        floors_passed=floors_passed,
        floors_triggered=floors_triggered,
        audit_hash=audit_hash,
        timestamp=timestamp,
        vault_ref=p.get("vault_ref"),
    )

    # ── RACI ──────────────────────────────────────────────────────────────────
    raci = AgiReplyRACI(
        responsible=forged_by,
        accountable=f"arifos.judge + human:{actor}",
        consulted=p.get("consulted_tools", ["arifos.heart", "arifos.ops", "arifos.memory"]),
        informed=p.get("informed_agents", ["arifos.vault"]),
    )

    # ── Header ────────────────────────────────────────────────────────────────
    cc_list: list[str] = p.get("cc", [])
    if verdict_token in ("CLAIM", "888 HOLD") and "arifos.vault" not in cc_list:
        cc_list.append("arifos.vault")

    header = AgiReplyHeader(
        TO=p.get("to", actor),
        CC=cc_list,
        TITLE=title,
        KEY_CONTEXT=(p.get("key_context") or f"{_build_summary(envelope)} Session: {session}."),
        reply_to=p.get("reply_to"),
    )

    # ── Context state ─────────────────────────────────────────────────────────
    prior_state = p.get("prior_state")
    delta = p.get("delta") or p.get("suggested_delta")

    # ── Direct answer + reasoning ─────────────────────────────────────────────
    direct_answer_raw = p.get("direct_answer", [])
    reasoning_snapshot = p.get("reasoning_snapshot", [])

    # ── Governance trace (F1/F13) — typed model ──────────────────────────────
    governance_trace: AgiReplyGovernanceTrace | None = None
    if floors_triggered and any(f in floors_triggered for f in ("F1", "F13")):
        governance_trace = AgiReplyGovernanceTrace(
            floors_triggered=floors_triggered,
            verdict="888_HOLD",
            escalate_to=f"human:{actor}",
            audit_ref=audit_hash,
            rights_impact="F7" in floors_triggered,
            reversible=p.get("reversible", "PARTIAL"),
            human_confirmed=bool(p.get("human_confirmed", False)),
        )

    # ── Guard: never emit structurally valid but empty direct_answer ──────────
    fallback_answer = _build_summary(envelope)
    if not direct_answer_raw:
        direct_answer_raw = (
            [fallback_answer] if recipient != "agent" else {"summary": fallback_answer}
        )

    # ── Route to human or agent envelope ─────────────────────────────────────
    if recipient == "agent":
        direct_answer_kv: dict[str, Any] = (
            direct_answer_raw
            if isinstance(direct_answer_raw, dict)
            else {"answer": direct_answer_raw}
        )
        env_agent = AgiReplyEnvelopeAgent(
            header=header,
            raci=raci,
            prior_state=prior_state,
            delta=delta,
            depth=depth,
            recipient="agent",
            verdict_token=verdict_token,
            tau=tau,
            verdict_statement=verdict_statement,
            floors_triggered=floors_triggered,
            direct_answer=direct_answer_kv,
            reasoning_snapshot=reasoning_snapshot,
            action_output=p.get("action_output"),
            resource_envelope={
                "compression_mode": compression,
                "tokens_estimated": (
                    envelope.metrics.tokens_used
                    if envelope.metrics and hasattr(envelope.metrics, "tokens_used")
                    else p.get("tokens_estimated")
                ),
                "cache_stable_prefix": p.get("cache_stable_prefix", True),
                "parallel_ok": p.get("parallel_ok", True),
                "next_agent": (
                    envelope.handoff.get("next_agent")
                    if isinstance(envelope.handoff, dict)
                    else p.get("next_agent")
                ),
            },
            governance_trace=governance_trace,
            telemetry=p.get("telemetry"),
            seal=seal,
        )
        return env_agent.model_dump(exclude_none=True)

    # Human envelope (default + ambiguous)
    direct_answer_bullets: list[str] = (
        direct_answer_raw if isinstance(direct_answer_raw, list) else [str(direct_answer_raw)]
    )
    env_human = AgiReplyEnvelopeHuman(
        header=header,
        raci=raci,
        prior_state=prior_state,
        delta=delta,
        depth=depth,
        verdict_token=verdict_token,
        tau=tau,
        verdict_statement=verdict_statement,
        floors_triggered=floors_triggered,
        direct_answer=direct_answer_bullets or [_build_summary(envelope)],
        reasoning_snapshot=reasoning_snapshot,
        action_output=p.get("action_output"),
        clarifying_question=p.get("clarifying_question"),
        seal=seal,
    )
    result = env_human.model_dump(exclude_none=True)

    # Ambiguous → also append compact agent block
    if recipient == "auto" and p.get("include_agent_block", False):
        result["_agent_block"] = {
            "action_output": p.get("action_output"),
            "resource_envelope": {
                "compression_mode": compression,
                "cache_stable_prefix": True,
                "parallel_ok": True,
                "next_agent": p.get("next_agent"),
            },
            "governance_trace": governance_trace,
            "seal": seal.model_dump(),
        }

    return result


def _build_base_output(envelope: RuntimeEnvelope) -> CleanOutput:
    """Build minimal operator view from RuntimeEnvelope."""

    # Map status
    status = _map_status(getattr(envelope, "status", None) or getattr(envelope, "execution_status", None))

    # Map verdict
    verdict = _map_verdict(envelope.verdict)

    # Extract error info
    error = None
    if not envelope.ok or status == "ERROR":
        payload_error = (
            envelope.payload.get("error") if isinstance(envelope.payload, dict) else None
        )
        error = CleanError(
            code=envelope.code or "UNKNOWN_ERROR",
            message=envelope.detail or payload_error or "Unknown error",
        )

    # Build operator summary
    summary = _build_summary(envelope)
    next_step = _extract_next_step(envelope)
    explanation = _build_explanation(envelope)
    actor = envelope.authority.actor_id if envelope.authority else "anonymous"
    session = envelope.session_id
    verified = envelope.authority.claim_status == "verified" if envelope.authority else False
    risk = envelope.risk_class.value if envelope.risk_class else "low"
    platform = envelope.platform_context or "unknown"
    tool = envelope.canonical_tool_name or envelope.tool or "unknown"

    return CleanOutput(
        human_language=HumanLanguageBlock(
            summary=summary,
            explanation=explanation,
            next_step=next_step,
        ),
        universal_context=UniversalContext(
            actor=actor,
            session=session,
            verified=verified,
            risk=risk,
            platform=platform,
            tool=tool,
            stage=envelope.stage,
        ),
        execution=ExecutionResult(
            ok=envelope.ok,
            status=status,
            stage=envelope.stage,
        ),
        governance=GovernanceVerdict(
            verdict=verdict,
            reason=envelope.verdict_detail.message if envelope.verdict_detail else None,
        ),
        operator=OperatorAction(
            summary=summary,
            next_step=next_step,
            retryable=envelope.retryable if envelope.retryable is not None else not envelope.ok,
        ),
        context=ContextSummary(
            actor=actor,
            session=session,
            verified=verified,
            risk=risk,
            platform=platform,
        ),
        error=error,
        debug=None,  # Never in base view
    )


def _map_status(status: RuntimeStatus | str | None) -> str:
    """Map internal status to clean status."""
    if status is None:
        return "ERROR"
    status_map = {
        RuntimeStatus.SUCCESS: "OK",
        RuntimeStatus.ERROR: "ERROR",
        RuntimeStatus.TIMEOUT: "TIMEOUT",
        RuntimeStatus.HOLD: "HOLD",
        RuntimeStatus.DRY_RUN: "PARTIAL",
        RuntimeStatus.DEGRADED: "PARTIAL",
        RuntimeStatus.SABAR: "HOLD",
        "SUCCESS": "OK",
        "ERROR": "ERROR",
        "TIMEOUT": "TIMEOUT",
        "HOLD": "HOLD",
    }
    if isinstance(status, RuntimeStatus):
        return status_map.get(status, "ERROR")
    return status_map.get(status, "ERROR")


def _map_verdict(verdict: Verdict | str | None) -> str:
    """Map internal verdict to clean verdict."""
    if verdict is None:
        return "VOID"
    verdict_map = {
        Verdict.SEAL: "SEAL",
        Verdict.PROVISIONAL: "PARTIAL",
        Verdict.HOLD: "HOLD",
        Verdict.VOID: "VOID",
        Verdict.ALIVE: "APPROVED",
        Verdict.SABAR: "PAUSE",
        "SEAL": "SEAL",
        "PARTIAL": "PARTIAL",
        "HOLD": "HOLD",
        "VOID": "VOID",
    }
    if isinstance(verdict, Verdict):
        return verdict_map.get(verdict, "VOID")
    return verdict_map.get(verdict, "VOID")


def _map_transport_status(envelope: RuntimeEnvelope, verdict: str) -> str:
    """Map internal envelope state to the public response-envelope status enum."""
    execution_status = _map_status(getattr(envelope, "status", None) or getattr(envelope, "execution_status", None))
    if verdict == "VOID":
        return "void"
    if verdict == "HOLD" or execution_status == "HOLD":
        return "hold"
    if execution_status == "ERROR" or not envelope.ok:
        return "error"
    return "ok"


def _build_summary(envelope: RuntimeEnvelope) -> str:
    """Build plain-language summary of what happened."""
    tool_names = {
        "arifos_init": "Session initialization",
        "arifos_sense": "Reality grounding",
        "arifos_mind": "Reasoning",
        "arifos_kernel": "Routing",
        "arifos_heart": "Safety critique",
        "arifos_ops": "Cost estimation",
        "arifos_judge": "Constitutional judgment",
        "arifos_memory": "Memory recall",
        "arifos_vault": "Vault sealing",
        "arifos_forge": "Execution",
        "arifos_gateway": "Orthogonality guard",
        "arifos_reply": "Governed reply",
        "arifos_health": "Telemetry",
        "arifos_fetch": "Fetch",
        "arifos_repo_read": "Git status",
        "arifos_repo_seal": "Git commit",
    }

    tool = tool_names.get(
        envelope.canonical_tool_name or envelope.tool, envelope.canonical_tool_name or envelope.tool
    )

    operator_summary = envelope.operator_summary or {}
    if isinstance(operator_summary, dict) and operator_summary:
        pieces = []
        if operator_summary.get("identity"):
            pieces.append(operator_summary["identity"])
        if operator_summary.get("session"):
            pieces.append(f"Session is {operator_summary['session']}")
        if operator_summary.get("authority"):
            pieces.append(f"Authority allows {operator_summary['authority']}")
        if operator_summary.get("governance"):
            pieces.append(f"Governance is {operator_summary['governance']}")
        if pieces:
            prefix = f"{tool} completed." if envelope.ok else f"{tool} stopped."
            return f"{prefix} {' '.join(pieces)}"

    if envelope.verdict_detail and envelope.verdict_detail.message:
        return envelope.verdict_detail.message
    if envelope.detail and envelope.ok:
        return envelope.detail
    if envelope.ok:
        return f"{tool} completed successfully."
    if envelope.code:
        return f"{tool} failed with {envelope.code}."
    return f"{tool} failed."


def _build_explanation(envelope: RuntimeEnvelope) -> str | None:
    """Build a universal plain-language explanation."""
    if envelope.verdict_detail and envelope.verdict_detail.message:
        return envelope.verdict_detail.message
    if envelope.detail:
        return envelope.detail
    if envelope.hint:
        return envelope.hint
    return None


def _extract_next_step(envelope: RuntimeEnvelope) -> str | None:
    """Extract actionable next step from envelope."""
    if envelope.next_action:
        if isinstance(envelope.next_action, dict):
            return envelope.next_action.get("reason") or envelope.next_action.get("next_step")
    if envelope.hint:
        return envelope.hint
    if not envelope.ok:
        if envelope.code == "INIT_KERNEL_500":
            return "Register init_anchor in tools_hardened_dispatch.py"
        if envelope.code == "INIT_AUTH_401":
            return "Complete identity verification"
        if envelope.code == "INIT_POLICY_403":
            return "Review policy requirements"
    return None


def _extract_kernel_version(envelope: RuntimeEnvelope) -> str:
    """Extract kernel version from system block."""
    if envelope.system and isinstance(envelope.system, dict):
        return envelope.system.get("kernel_version", "2026.04")
    return "2026.04"


def _extract_env(envelope: RuntimeEnvelope) -> str:
    """Extract environment from system block."""
    if envelope.system and isinstance(envelope.system, dict):
        return envelope.system.get("env", "production")
    return "production"


def _extract_authority(envelope: RuntimeEnvelope) -> str:
    """Extract authority level."""
    if envelope.authority:
        return (
            envelope.authority.level.value
            if hasattr(envelope.authority.level, "value")
            else str(envelope.authority.level)
        )
    return "anonymous"


def _extract_operational_status(envelope: RuntimeEnvelope) -> str:
    """Extract operational status from governance closure."""
    if envelope.state and isinstance(envelope.state, dict):
        closure = envelope.state.get("governance_closure", {})
        return closure.get("operational_status", "pass" if envelope.ok else "restricted")
    return "pass" if envelope.ok else "restricted"


def _extract_proof_status(envelope: RuntimeEnvelope) -> str:
    """Extract proof status from governance closure."""
    if envelope.state and isinstance(envelope.state, dict):
        closure = envelope.state.get("governance_closure", {})
        return closure.get("proof_status", "incomplete")
    return "incomplete"


# Legacy compatibility
def format_output_legacy(
    envelope: RuntimeEnvelope,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Format output in legacy format for backward compatibility.
    Use this only during migration period.
    """
    from arifosmcp.runtime.schemas import migrate_to_legacy_output

    clean = format_output(envelope, options)
    return migrate_to_legacy_output(CleanOutput(**clean))


__all__ = [
    "format_output",
    "format_output_legacy",
    "_format_agi_reply",
]
