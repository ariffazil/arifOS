"""
arifosmcp/runtime/schemas.py — Canonical Schemas for arifOS MCP

Combines:
  • ABI Schemas  — tool I/O contracts (IntentType, InitAnchorInput, etc.)
  • Clean Schemas — 3-tier output format (CleanInput, CleanOutput, etc.)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Union

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM CONTEXT — which caller surface invoked this tool
# ═══════════════════════════════════════════════════════════════════════════════

PlatformType = Literal["mcp", "chatgpt_apps", "cursor", "api", "stdio", "unknown"]
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
    platform: PlatformType = Field(default="unknown", description="Caller platform")


class HumanLanguageBlock(BaseModel):
    """Human-first language block shared across surfaces."""
    summary: str = Field(description="Plain-language explanation of what happened")
    explanation: str | None = Field(default=None, description="Why it happened, in plain language")
    next_step: str | None = Field(default=None, description="Actionable next step in plain language")


class UniversalContext(BaseModel):
    """Universal context block reused across external surfaces."""
    actor: str = Field(description="Who made the request")
    session: str | None = Field(default=None, description="Session ID")
    verified: bool = Field(default=False, description="Identity verified?")
    risk: str = Field(default="low", description="Risk tier")
    platform: PlatformType = Field(default="unknown", description="Caller platform")
    tool: str = Field(description="Canonical tool name")
    stage: str = Field(description="Processing stage")


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
    human_language: HumanLanguageBlock
    universal_context: UniversalContext
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
    reason: str | None = None, platform: PlatformType = "unknown", tool: str = "unknown",
) -> CleanOutput:
    """Build minimal operator view (default)."""
    return CleanOutput(
        human_language=HumanLanguageBlock(
            summary=summary,
            explanation=reason,
            next_step=next_step,
        ),
        universal_context=UniversalContext(
            actor=actor,
            session=session,
            verified=verified,
            risk=risk,
            platform=platform,
            tool=tool,
            stage=stage,
        ),
        execution=ExecutionResult(ok=ok, status=status, stage=stage),
        governance=GovernanceVerdict(verdict=verdict, reason=reason),
        operator=OperatorAction(summary=summary, next_step=next_step, retryable=retryable),
        context=ContextSummary(actor=actor, session=session, verified=verified, risk=risk, platform=platform),
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
    "GovernanceVerdict", "OperatorAction", "ContextSummary", "HumanLanguageBlock",
    "UniversalContext", "CleanError",
    "DebugForensics",
    # Builders & migration
    "build_operator_view", "build_system_view", "build_forensic_view",
    "migrate_from_legacy_input", "migrate_to_legacy_output",
    # AGI Reply Protocol v3
    "AgiReplyHeader", "AgiReplyRACI", "AgiReplySeal",
    "AgiReplyGovernanceTrace", "AgiReplyToolReturn",
    "AgiReplyEnvelopeHuman", "AgiReplyEnvelopeAgent",
]


# ═══════════════════════════════════════════════════════════════════════════════
# AGI REPLY PROTOCOL v3 — DITEMPA EDITION
# Dual-axis reply envelopes: human-cognitive + agent-machine
# Aligned with MCP resource arifos://reply/schemas
# ═══════════════════════════════════════════════════════════════════════════════

class AgiReplyHeader(BaseModel):
    """
    Email-style routing header. Every governed reply must have one.
    Encodes: who it's for, who is copied, what it is, and minimum context.
    """
    TO: str = Field(description="Primary recipient — human name or agent_id")
    CC: list[str] = Field(
        default_factory=list,
        description="Secondary recipients: audit agents, downstream agents, vault ref",
    )
    TITLE: str = Field(description="One-line verdict statement (becomes the TITLE line)")
    KEY_CONTEXT: str = Field(
        description="1-2 essential sentences — what the recipient must know to act"
    )
    reply_to: str | None = Field(
        default=None,
        description="Agent or human to route clarification back to",
    )


class AgiReplyRACI(BaseModel):
    """
    Principal role map for this reply.
    R — who forged the output.
    A — who is accountable (judge + sovereign human).
    C — who was consulted before forging.
    I — who must be informed after.
    """
    responsible: str = Field(
        description="Agent/tool that produced this output (e.g. arifos.forge, arifos.mind)"
    )
    accountable: str = Field(
        description="Constitutional authority — always arifos.judge + human:arif for F1/F13"
    )
    consulted: list[str] = Field(
        default_factory=list,
        description="Tools/agents consulted during reasoning (e.g. arifos.heart, arifos.ops)",
    )
    informed: list[str] = Field(
        default_factory=list,
        description="Recipients who must receive the output (e.g. arifos.vault, downstream agents)",
    )


class AgiReplyGovernanceTrace(BaseModel):
    """
    Typed governance trace — replaces raw dict[str, Any].
    Populated when F1 or F13 is triggered (888 HOLD path).
    Required for vault persistence and auditability.
    """
    floors_triggered: list[str] = Field(
        description="F1-F13 floor codes that fired"
    )
    verdict: Literal["888_HOLD", "SEAL", "PARTIAL", "VOID"] = Field(
        description="Constitutional verdict at time of governance check"
    )
    escalate_to: str = Field(
        description="Principal who must ratify — format: human:<actor_id>"
    )
    audit_ref: str = Field(
        description="Short audit hash from AgiReplySeal"
    )
    rights_impact: bool = Field(
        default=False,
        description="True if [F7 ADIL] triggered — recommendation affects another's rights",
    )
    reversible: Literal["YES", "NO", "PARTIAL"] = Field(
        default="YES",
        description="Can the proposed action be undone?",
    )
    human_confirmed: bool = Field(
        default=False,
        description="F13 gate: human ratification received (required before forge on F1/F13)",
    )


class AgiReplySeal(BaseModel):
    """
    Cryptographic + governance signoff from the forging agent.
    Appended to every output. Required for SEAL verdict.
    No seal = provisional output only.
    """
    forged_by: str = Field(description="agent_id that produced and signs this output")
    judge_verdict: Literal["SEAL", "PARTIAL", "HOLD", "VOID"] = Field(
        description="Verdict from arifos.judge at time of forging"
    )
    tau: float = Field(ge=0.0, le=1.0, description="Grounding score τ (F7 proxy)")
    tau_source: Literal["computed", "fallback", "manual"] = Field(
        default="fallback",
        description=(
            "computed = derived from reasoning atoms via F7_PROXY_v1; "
            "fallback = default 0.5 (no atoms available); "
            "manual = caller-supplied override"
        ),
    )
    floors_passed: list[str] = Field(default_factory=list, description="F1-F13 floors that passed")
    floors_triggered: list[str] = Field(default_factory=list, description="Floors that flagged")
    audit_hash: str = Field(
        description="sha256(TITLE + timestamp + forged_by + judge_verdict)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    vault_ref: str | None = Field(
        default=None,
        description="arifos.vault ledger reference if sealed",
    )
    seal_phrase: str = Field(
        default="DITEMPA BUKAN DIBERI — 999 SEAL ALIVE",
        description="Constitutional seal phrase — never alter",
    )


class AgiReplyToolReturn(BaseModel):
    """
    Normalized tool return envelope — every arifOS tool should return this shape.
    Enables the LLM to align output format from repeated structured signals.
    Based on external agent recommendation: status + evidence + floor_flags +
    reversible + next_recommended_tool.
    """
    status: Literal["OK", "HOLD", "VOID", "PARTIAL", "ERROR"] = Field(
        description="Execution outcome"
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="FACT/VERIFY atoms collected by this tool",
    )
    constraints: dict[str, Any] = Field(
        default_factory=dict,
        description="Resource or policy constraints active during this call",
    )
    suggested_delta: str | None = Field(
        default=None,
        description="Compressed one-line state change to carry into STEP -1 CONTEXT STATE",
    )
    floor_flags: list[str] = Field(
        default_factory=list,
        description="F1-F13 floors triggered by this tool call",
    )
    reversible: Literal["YES", "NO", "PARTIAL"] = Field(
        default="YES",
        description="Can the action taken by this tool be undone?",
    )
    next_recommended_tool: str | None = Field(
        default=None,
        description="arifOS golden-path: which tool should be called next",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Tool-specific output payload",
    )


class AgiReplyEnvelopeHuman(BaseModel):
    """
    Human-facing reply envelope.
    Cognitively aligned: narrative structure, plain bullets, optional code.
    No machine blocks. One clarifying question maximum.
    """
    # Routing
    header: AgiReplyHeader
    raci: AgiReplyRACI

    # Context state (STEP -1)
    prior_state: str | None = Field(default=None, description="Compressed prior context")
    delta: str | None = Field(default=None, description="What changed this turn")
    depth: Literal["SURFACE", "ENGINEER", "ARCHITECT"] = Field(default="ENGINEER")

    # Verdict (STEP 1)
    verdict_token: Literal[
        "CLAIM", "PLAUSIBLE", "HYPOTHESIS", "ESTIMATE", "UNKNOWN", "CONFLICT", "888 HOLD"
    ]
    tau: float = Field(ge=0.0, le=1.0)
    verdict_statement: str = Field(description="One concrete, plain-language statement")
    floors_triggered: list[str] = Field(default_factory=list)

    # Answer (STEP 2A)
    direct_answer: list[str] = Field(
        description="2-5 bullets. Strongest conclusion first. No apologies."
    )

    # Reasoning (STEP 2B) — compressed for human, not raw chain
    reasoning_snapshot: list[str] = Field(
        description="3-7 tagged bullets: FACT/ASSUME/RISK/DELTA/UNKNOWN/DERIVE/VERIFY"
    )

    # Output (STEP 2C)
    action_output: str | None = Field(
        default=None,
        description="Code block, numbered steps, or Markdown table",
    )
    clarifying_question: str | None = Field(
        default=None,
        description="ONE question only — omit if it wouldn't materially change the answer",
    )

    # Seal (always last)
    seal: AgiReplySeal


class AgiReplyEnvelopeAgent(BaseModel):
    """
    Agent-facing reply envelope.
    Machine-aligned: compact kv, explicit action block, resource envelope,
    governance trace. No prose. Full signal density.
    """
    # Routing
    header: AgiReplyHeader
    raci: AgiReplyRACI

    # Context state (STEP -1)
    prior_state: str | None = None
    delta: str | None = None
    depth: Literal["SURFACE", "ENGINEER", "ARCHITECT"] = "ENGINEER"
    recipient: str = "agent"

    # Verdict (STEP 1)
    verdict_token: Literal[
        "CLAIM", "PLAUSIBLE", "HYPOTHESIS", "ESTIMATE", "UNKNOWN", "CONFLICT", "888 HOLD"
    ]
    tau: float = Field(ge=0.0, le=1.0)
    verdict_statement: str
    floors_triggered: list[str] = Field(default_factory=list)

    # Answer (STEP 2A) — kv or JSON-compatible
    direct_answer: dict[str, Any] = Field(
        description="Compact key-value direct answer for machine consumption"
    )

    # Reasoning (STEP 2B)
    reasoning_snapshot: list[str] = Field(
        description="Tagged reasoning atoms: FACT/ASSUME/RISK/DELTA/UNKNOWN/DERIVE/VERIFY"
    )

    # Action block (STEP 2C)
    action_output: dict[str, Any] | None = Field(
        default=None,
        description=(
            "Structured action: {action, params, confidence, reversible, "
            "escalate_if, next_agent}"
        ),
    )

    # Resource envelope (STEP 2D)
    resource_envelope: dict[str, Any] = Field(
        default_factory=lambda: {
            "compression_mode": "DELTA",
            "tokens_estimated": None,
            "cache_stable_prefix": True,
            "parallel_ok": True,
            "next_agent": None,
        }
    )

    # Constitutional guard (STEP 3)
    governance_trace: AgiReplyGovernanceTrace | None = Field(
        default=None,
        description="Typed governance trace — populated when F1 or F13 triggered",
    )

    # Telemetry passthrough
    telemetry: dict[str, Any] | None = Field(
        default=None,
        description="Raw telemetry from arifos.ops / vps_monitor",
    )

    # Seal (always last)
    seal: AgiReplySeal
