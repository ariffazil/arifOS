"""
arifosmcp/runtime/schemas.py — Canonical Schemas for arifOS MCP

Combines:
  • ABI Schemas  — tool I/O contracts (IntentType, InitAnchorInput, etc.)
  • Clean Schemas — 3-tier output format (CleanInput, CleanOutput, etc.)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Union

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM CONTEXT — which caller surface invoked this tool
# ═══════════════════════════════════════════════════════════════════════════════

PlatformType = Literal["chatgpt", "perplexity", "mcp-cli", "playground", "api", "unknown"]
"""
Valid caller-platform values. Default is "unknown" (backward compat, F1 safe).
Pass via request body `platform` field or HTTP header `X-Arifos-Platform`.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# ABI SCHEMAS — Tool I/O Contracts
# ═══════════════════════════════════════════════════════════════════════════════

class IntentSpec(BaseModel):
    """Structured intent specification for governed workflows."""
    query: str = Field(..., description="The primary query or objective", min_length=1, max_length=20000)
    task_type: str = Field(default="general", description="Category: ask, analyze, design, decide, audit, execute", max_length=64)
    domain: str | None = Field(default=None, description="Domain: engineering, research, governance, etc.", max_length=64)
    desired_output: str | None = Field(default=None, description="Expected format: text, json, table, code, report", max_length=64)


# Intent can be string (legacy) or structured object
IntentType = Union[str, dict[str, Any], None]


class InitAnchorInput(BaseModel):
    """Canonical input schema for arifos.init (ABI v1.0)."""
    actor_id: str = Field(default="anonymous", description="Identity claimed by the caller", min_length=2, max_length=64)
    declared_name: str | None = Field(default=None, description="Human-readable display name", max_length=64)
    intent: IntentType = Field(default=None, description="User intent — string (legacy) or IntentSpec object")
    session_id: str | None = Field(default=None, description="Optional session ID for continuity", min_length=8, max_length=128)
    human_approval: bool = Field(default=False, description="Human pre-approval flag (F13 Sovereign override)")
    reason: str | None = Field(default=None, description="Reason for action (used with revoke mode)", max_length=1000)


class IdentityResolution(BaseModel):
    """Identity claim resolution details."""
    claimed_actor_id: str = Field(description="What the caller claimed")
    resolved_actor_id: str | None = Field(description="What the system accepted")
    claim_status: Literal["anonymous", "claimed", "anchored", "verified", "rejected", "demoted", "rejected_protected_id"] = Field(description="Resolution status")
    why_demoted: str | None = Field(default=None, description="Explanation if identity was demoted")


class InitAnchorOutput(BaseModel):
    """Canonical output schema for arifos.init."""
    ok: bool
    session_id: str
    auth_state: Literal["unverified", "anchored", "verified", "rejected"] = Field(description="Authentication state")
    identity: IdentityResolution
    abi_version: str = Field(default="1.0", description="ABI version used")
    approval_state: Literal["not_required", "pending", "approved"] = Field(default="not_required")


class MegaToolInput(BaseModel):
    """Unified input envelope for all tools (ABI v1.0)."""
    mode: str = Field(..., description="Operation mode for this tool")
    payload: dict[str, Any] = Field(default_factory=dict, description="Mode-specific payload data")
    auth_context: dict[str, Any] | None = Field(default=None, description="Authentication context (F11)")
    caller_context: dict[str, Any] | None = Field(default=None, description="Caller metadata")
    risk_tier: Literal["low", "medium", "high", "critical"] = Field(default="medium")
    dry_run: bool = Field(default=True, description="Validate only without execution")
    allow_execution: bool = Field(default=False, description="Permit execution if floors pass")
    abi_version: str = Field(default="1.0", description="ABI version requested by client")
    platform: PlatformType = Field(default="unknown", description="Caller platform surface (chatgpt|perplexity|mcp-cli|playground|api|unknown)")


class CanonicalErrorDetail(BaseModel):
    """Standard error detail structure."""
    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    recoverable: bool = Field(default=True, description="Whether client can retry/recover")
    remediation: str | None = Field(default=None, description="Suggested fix or next action")
    required_next_tool: str | None = Field(default=None, description="Tool to call to resolve")


class ErrorResponse(BaseModel):
    """Standard error response envelope."""
    ok: bool = Field(default=False)
    errors: list[CanonicalErrorDetail]
    abi_version: str = Field(default="1.0")


# ═══════════════════════════════════════════════════════════════════════════════
# CLEAN SCHEMAS — 3-Tier Output Format
# ═══════════════════════════════════════════════════════════════════════════════

class QueryOptions(BaseModel):
    """Optional controls for output verbosity."""
    verbose: bool = Field(default=False, description="Include governance + system details")
    debug: bool = Field(default=False, description="Include full forensic state")
    include: list[str] = Field(default_factory=list, description="Specific sections to include")


class CleanInput(BaseModel):
    """Minimal, explicit input schema."""
    actor: str = Field(default="anonymous", description="Who is asking")
    intent: str = Field(description="What they want to accomplish")
    risk: Literal["low", "medium", "high", "critical"] = Field(default="low")
    session: str | None = Field(default=None, description="Session identifier")
    options: QueryOptions = Field(default_factory=QueryOptions)


class ExecutionResult(BaseModel):
    """Execution truth: Did the tool run successfully?"""
    ok: bool = Field(description="Did the tool execute without error?")
    status: Literal["OK", "ERROR", "PARTIAL", "HOLD", "TIMEOUT"] = Field(description="Execution status")
    stage: str = Field(description="Which stage processed this")


class GovernanceVerdict(BaseModel):
    """Governance truth: Should this proceed?"""
    verdict: Literal["APPROVED", "PARTIAL", "PAUSE", "VOID", "HOLD", "SEAL"] = Field(description="Constitutional verdict")
    reason: str | None = Field(default=None, description="Why this verdict")


class OperatorAction(BaseModel):
    """Operator truth: What do I do now?"""
    summary: str = Field(description="What happened in plain language")
    next_step: str | None = Field(default=None, description="What to do next")
    retryable: bool = Field(default=False, description="Can operator retry?")


class ContextSummary(BaseModel):
    """Minimal context: Who, what, where, verified?"""
    actor: str = Field(description="Who made the request")
    session: str | None = Field(default=None, description="Session ID")
    verified: bool = Field(default=False, description="Identity verified?")
    risk: str = Field(default="low", description="Risk tier")


class CleanError(BaseModel):
    """Error details when things fail."""
    code: str = Field(description="Typed error code")
    message: str = Field(description="Human-readable error")


class DebugForensics(BaseModel):
    """Full forensic state — only when options.debug = true."""
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


class CleanOutput(BaseModel):
    """Clean 3-tier output with fixed block structure."""
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
    ok: bool, status: str, stage: str, verdict: str,
    summary: str, actor: str, session: str | None, risk: str = "low",
    verified: bool = False, next_step: str | None = None, retryable: bool = False,
    error_code: str | None = None, error_message: str | None = None,
    reason: str | None = None,
) -> CleanOutput:
    """Build minimal operator view (default)."""
    return CleanOutput(
        execution=ExecutionResult(ok=ok, status=status, stage=stage),
        governance=GovernanceVerdict(verdict=verdict, reason=reason),
        operator=OperatorAction(summary=summary, next_step=next_step, retryable=retryable),
        context=ContextSummary(actor=actor, session=session, verified=verified, risk=risk),
        error=CleanError(code=error_code, message=error_message) if error_code else None,
    )


def build_system_view(base: CleanOutput, **kwargs: Any) -> CleanOutput:
    """Build system view with governance details (verbose=true)."""
    return base


def build_forensic_view(base: CleanOutput, **kwargs: Any) -> CleanOutput:
    """Build forensic view with full debug state (debug=true)."""
    return base


# ═══════════════════════════════════════════════════════════════════════════════
# MIGRATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def migrate_from_legacy_input(legacy: dict[str, Any]) -> CleanInput:
    """Convert legacy verbose input to clean input."""
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
    """Convert clean output back to legacy format for backward compatibility."""
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


__all__ = [
    # ABI schemas
    "IntentSpec", "IntentType", "InitAnchorInput", "IdentityResolution",
    "InitAnchorOutput", "MegaToolInput", "CanonicalErrorDetail", "ErrorResponse",
    # Platform context
    "PlatformType",
    # Clean schemas
    "CleanInput", "QueryOptions", "CleanOutput", "ExecutionResult",
    "GovernanceVerdict", "OperatorAction", "ContextSummary", "CleanError",
    "DebugForensics",
    # Builders & migration
    "build_operator_view", "build_system_view", "build_forensic_view",
    "migrate_from_legacy_input", "migrate_to_legacy_output",
]
