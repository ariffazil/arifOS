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

from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
from arifosmcp.runtime.schemas import (
    CleanOutput,
    ExecutionResult,
    GovernanceVerdict,
    OperatorAction,
    ContextSummary,
    CleanError,
    DebugForensics,
    build_system_view,
    build_forensic_view,
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
        res = clean.model_dump(exclude_none=True)
        res["render_hint"] = "widget"
        res["platform"] = "chatgpt_apps"
        return res
        
    # 2. api — flat JSON, no MCP envelope
    if platform == "api":
        clean = _build_base_output(envelope)
        return {
            "ok": clean.execution.ok,
            "status": clean.execution.status,
            "verdict": clean.governance.verdict,
            "summary": clean.operator.summary,
            "next_step": clean.operator.next_step,
            "payload": envelope.payload,
            "session_id": clean.context.session,
        }
        
    # 3. stdio — human-readable text
    if platform == "stdio":
        clean = _build_base_output(envelope)
        text = f"[{clean.execution.status}] {clean.governance.verdict}: {clean.operator.summary}"
        if clean.operator.next_step:
            text += f"\nNext: {clean.operator.next_step}"
        return {"output": text}

    # 4. mcp (default) — 3-tier structure
    # Build base operator view
    clean = _build_base_output(envelope)
    
    # Add system view if verbose
    if verbose and not debug:
        return build_system_view(
            base=clean,
            kernel_version=_extract_kernel_version(envelope),
            adapter="mcp",
            env=_extract_env(envelope),
            authority=_extract_authority(envelope),
            operational_status=_extract_operational_status(envelope),
            proof_status=_extract_proof_status(envelope),
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
        return build_forensic_view(
            base=CleanOutput(**base_dict),
            caller_state=envelope.caller_state,
            allowed_next_tools=list(envelope.allowed_next_tools) if envelope.allowed_next_tools else [],
            blocked_tools=envelope.blocked_tools if envelope.blocked_tools else [],
            raw_payload=envelope.payload if isinstance(envelope.payload, dict) else None,
            trace=envelope.trace,
            telemetry=envelope.metrics.model_dump() if envelope.metrics else None,
            continuity=envelope.payload.get("continuity") if isinstance(envelope.payload, dict) else None,
            handoff=envelope.handoff,
            diagnostics=envelope.diagnostics,
        )
    
    # Return minimal operator view
    return clean.model_dump(exclude_none=True)


def _build_base_output(envelope: RuntimeEnvelope) -> CleanOutput:
    """Build minimal operator view from RuntimeEnvelope."""
    
    # Map status
    status = _map_status(envelope.status)
    
    # Map verdict
    verdict = _map_verdict(envelope.verdict)
    
    # Extract error info
    error = None
    if not envelope.ok or status == "ERROR":
        error = CleanError(
            code=envelope.code or "UNKNOWN_ERROR",
            message=envelope.detail or envelope.payload.get("error", "Unknown error"),
        )
    
    # Build operator summary
    summary = _build_summary(envelope)
    next_step = _extract_next_step(envelope)
    
    return CleanOutput(
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
            actor=envelope.authority.actor_id if envelope.authority else "anonymous",
            session=envelope.session_id,
            verified=envelope.authority.claim_status == "verified" if envelope.authority else False,
            risk=envelope.risk_class.value if envelope.risk_class else "low",
            platform=envelope.platform_context or "unknown",
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


def _build_summary(envelope: RuntimeEnvelope) -> str:
    """Build plain-language summary of what happened."""
    tool_names = {
        "arifos_init": "Session initialization",
        "arifos_sense": "Reality grounding",
        "arifos_mind": "Reasoning",
        "arifos_route": "Routing",
        "arifos_heart": "Safety critique",
        "arifos_ops": "Cost estimation",
        "arifos_judge": "Constitutional judgment",
        "arifos_memory": "Memory recall",
        "arifos_vault": "Vault sealing",
        "arifos_forge": "Execution",
        "arifos_vps_monitor": "Telemetry",
    }
    
    tool = tool_names.get(envelope.tool, envelope.tool)
    
    if envelope.ok:
        return f"{tool} completed successfully."
    elif envelope.code:
        return f"{tool} failed with {envelope.code}."
    else:
        return f"{tool} failed."


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
        return envelope.authority.level.value if hasattr(envelope.authority.level, 'value') else str(envelope.authority.level)
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
]
