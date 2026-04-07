"""
arifOS MCP Clean Schema v0.2 — 3-Tier Output Model
═══════════════════════════════════════════════════════════════════════════════

Design Principle: "One screen = one decision"

Three views:
- Operator (default): Action-oriented, minimal, clean
- System (verbose=true): Engineering + governance details  
- Forensic (debug=true): Full investigation state

Input: Small, explicit, unambiguous
Output: Fixed blocks [result, action, context, error, debug]

Author: Operator Feedback Integration
Version: 2026.04.06-v0.2
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class QueryOptions(BaseModel):
    """Optional controls for output verbosity."""
    verbose: bool = Field(default=False, description="Include governance + system details")
    debug: bool = Field(default=False, description="Include full forensic state")
    include: list[str] = Field(default_factory=list, description="Specific sections to include")


class CleanInput(BaseModel):
    """
    Minimal, explicit input schema.
    
    Before (noisy):
        actor_id, declared_name, risk_tier, session_id, human_approved, ...
    
    After (clean):
        actor, intent, risk, session, options
    """
    actor: str = Field(default="anonymous", description="Who is asking")
    intent: str = Field(description="What they want to accomplish")
    risk: Literal["low", "medium", "high", "critical"] = Field(default="low")
    session: str | None = Field(default=None, description="Session identifier")
    options: QueryOptions = Field(default_factory=QueryOptions)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT SCHEMAS — FIXED BLOCKS
# ═══════════════════════════════════════════════════════════════════════════════

class ExecutionResult(BaseModel):
    """
    Execution truth: Did the tool run successfully?
    Separated from governance truth to avoid confusion.
    """
    ok: bool = Field(description="Did the tool execute without error?")
    status: Literal["OK", "ERROR", "PARTIAL", "HOLD", "TIMEOUT"] = Field(
        description="Execution status"
    )
    stage: str = Field(description="Which stage processed this")


class GovernanceVerdict(BaseModel):
    """
    Governance truth: Should this proceed?
    Constitutional judgment separate from execution.
    """
    verdict: Literal["APPROVED", "PARTIAL", "PAUSE", "VOID", "HOLD", "SEAL"] = Field(
        description="Constitutional verdict"
    )
    reason: str | None = Field(default=None, description="Why this verdict")


class OperatorAction(BaseModel):
    """
    Operator truth: What do I do now?
    Action-oriented summary for human decision.
    """
    summary: str = Field(description="What happened in plain language")
    next_step: str | None = Field(default=None, description="What to do next")
    retryable: bool = Field(default=False, description="Can operator retry?")


class ContextSummary(BaseModel):
    """
    Minimal context: Who, what, where, verified?
    No internals, no handoff, no continuity state.
    """
    actor: str = Field(description="Who made the request")
    session: str | None = Field(default=None, description="Session ID")
    verified: bool = Field(default=False, description="Identity verified?")
    risk: str = Field(default="low", description="Risk tier")


class CleanError(BaseModel):
    """
    Error details when things fail.
    Only present when execution.ok = false.
    """
    code: str = Field(description="Typed error code")
    message: str = Field(description="Human-readable error")


class DebugForensics(BaseModel):
    """
    Full forensic state — only when options.debug = true.
    
    Includes everything hidden in default view:
    - telemetry, trace, handoff, continuity
    - raw_payload, diagnostics, state
    - blocked_tools, allowed_next_tools
    """
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    caller_state: str | None = None
    allowed_next_tools: list[str] = Field(default_factory=list)
    blocked_tools: list[dict] = Field(default_factory=list)
    raw_payload: dict | None = None
    trace: dict | None = None
    telemetry: dict | None = None
    continuity: dict | None = None
    handoff: dict | None = None
    diagnostics: dict | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# CLEAN OUTPUT — FIXED STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

class CleanOutput(BaseModel):
    """
    Clean 3-tier output following fixed block structure.
    
    Structure: [execution, governance, operator, context, error, debug]
    
    Example (operator view, default):
        {
          "execution": {"ok": false, "status": "ERROR", "stage": "INIT"},
          "governance": {"verdict": "VOID", "reason": "Init unavailable"},
          "operator": {
            "summary": "Session init failed",
            "next_step": "Register init_anchor",
            "retryable": false
          },
          "context": {"actor": "arif", "session": "sess-123", "verified": false, "risk": "low"},
          "error": {"code": "INIT_KERNEL_500", "message": "Dispatch map missing init_anchor"}
        }
    """
    execution: ExecutionResult
    governance: GovernanceVerdict
    operator: OperatorAction
    context: ContextSummary
    error: CleanError | None = None
    debug: DebugForensics | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# VIEW GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def build_operator_view(
    ok: bool,
    status: str,
    stage: str,
    verdict: str,
    summary: str,
    actor: str,
    session: str | None,
    risk: str = "low",
    verified: bool = False,
    next_step: str | None = None,
    retryable: bool = False,
    error_code: str | None = None,
    error_message: str | None = None,
    reason: str | None = None,
) -> CleanOutput:
    """
    Build minimal operator view (default).
    
    Answers only:
    - Did it work?
    - What stage failed?
    - What is the verdict?
    - Why?
    - What to do next?
    """
    return CleanOutput(
        execution=ExecutionResult(ok=ok, status=status, stage=stage),
        governance=GovernanceVerdict(verdict=verdict, reason=reason),
        operator=OperatorAction(
            summary=summary,
            next_step=next_step,
            retryable=retryable,
        ),
        context=ContextSummary(
            actor=actor,
            session=session,
            verified=verified,
            risk=risk,
        ),
        error=CleanError(code=error_code, message=error_message) if error_code else None,
        debug=None,  # Never in operator view
    )


def build_system_view(
    base: CleanOutput,
    kernel_version: str = "2026.04",
    adapter: str = "mcp",
    env: str = "production",
    authority: str = "anonymous",
    operational_status: str = "pass",
    proof_status: str = "incomplete",
) -> dict[str, Any]:
    """
    Add system/governance details for verbose=true.
    
    Extends operator view with:
    - system block (kernel_version, adapter, env)
    - governance authority
    - operational/proof status
    """
    output = base.model_dump(exclude_none=True)
    output["system"] = {
        "kernel_version": kernel_version,
        "adapter": adapter,
        "env": env,
    }
    output["governance"]["authority"] = authority
    output["governance"]["operational_status"] = operational_status
    output["governance"]["proof_status"] = proof_status
    return output


def build_forensic_view(
    base: CleanOutput,
    caller_state: str | None = None,
    allowed_next_tools: list[str] | None = None,
    blocked_tools: list[dict] | None = None,
    raw_payload: dict | None = None,
    trace: dict | None = None,
    telemetry: dict | None = None,
    continuity: dict | None = None,
    handoff: dict | None = None,
    diagnostics: dict | None = None,
) -> dict[str, Any]:
    """
    Add full forensic state for debug=true.
    
    Includes everything:
    - telemetry, trace, handoff
    - raw_payload, continuity
    - diagnostics, blocked_tools
    """
    output = base.model_dump(exclude_none=True)
    output["debug"] = DebugForensics(
        caller_state=caller_state,
        allowed_next_tools=allowed_next_tools or [],
        blocked_tools=blocked_tools or [],
        raw_payload=raw_payload,
        trace=trace,
        telemetry=telemetry,
        continuity=continuity,
        handoff=handoff,
        diagnostics=diagnostics,
    ).model_dump(exclude_none=True)
    return output


# ═══════════════════════════════════════════════════════════════════════════════
# MIGRATION UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def migrate_from_legacy_input(legacy: dict[str, Any]) -> CleanInput:
    """
    Migrate old verbose input to clean input.
    
    Legacy: actor_id, declared_name, risk_tier, session_id, dry_run, debug
    Clean:  actor, intent, risk, session, options
    """
    return CleanInput(
        actor=legacy.get("declared_name") or legacy.get("actor_id", "anonymous"),
        intent=legacy.get("intent", legacy.get("query", "")),
        risk=legacy.get("risk_tier", "low"),
        session=legacy.get("session_id"),
        options=QueryOptions(
            verbose=legacy.get("verbose", False),
            debug=legacy.get("debug", False),
        ),
    )


def migrate_to_legacy_output(clean: CleanOutput) -> dict[str, Any]:
    """
    Convert clean output back to legacy format for backward compatibility.
    """
    return {
        "ok": clean.execution.ok,
        "status": clean.execution.status,
        "stage": clean.execution.stage,
        "verdict": clean.governance.verdict,
        "verdict_detail": {"reason": clean.governance.reason},
        "session_id": clean.context.session,
        "actor_id": clean.context.actor,
        "risk_tier": clean.context.risk,
        "error": {
            "code": clean.error.code if clean.error else None,
            "message": clean.error.message if clean.error else None,
        } if clean.error else None,
        "debug": clean.debug.model_dump() if clean.debug else None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════

def example_failed_init() -> CleanOutput:
    """Example: Clean output for failed arifos.init"""
    return build_operator_view(
        ok=False,
        status="ERROR",
        stage="INIT",
        verdict="VOID",
        summary="Session initialization failed due to missing dispatch registration.",
        actor="arif",
        session="arif-human-mind-20260406",
        risk="low",
        verified=False,
        next_step="Register init_anchor in tools_hardened_dispatch.py",
        retryable=False,
        error_code="INIT_KERNEL_500",
        error_message="HARDENED_DISPATCH_MAP has no init_anchor entry",
        reason="Init tool unavailable due to dispatch misconfiguration",
    )


def example_successful_mind() -> CleanOutput:
    """Example: Clean output for successful arifos.mind"""
    return build_operator_view(
        ok=True,
        status="OK",
        stage="MIND",
        verdict="SEAL",
        summary="Multi-source reasoning complete with 3 alternative hypotheses generated.",
        actor="arif",
        session="arif-human-mind-20260406",
        risk="low",
        verified=True,
        next_step="Review reasoning output and proceed to heart critique",
        retryable=True,
        reason="Grounded reasoning with falsification query included",
    )


__all__ = [
    # Input
    "CleanInput",
    "QueryOptions",
    # Output blocks
    "CleanOutput",
    "ExecutionResult",
    "GovernanceVerdict", 
    "OperatorAction",
    "ContextSummary",
    "CleanError",
    "DebugForensics",
    # Builders
    "build_operator_view",
    "build_system_view",
    "build_forensic_view",
    # Migration
    "migrate_from_legacy_input",
    "migrate_to_legacy_output",
    # Examples
    "example_failed_init",
    "example_successful_mind",
]
