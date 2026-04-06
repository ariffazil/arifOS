"""
arifOS MCP Context Contracts
═══════════════════════════════════════════════════════════════════════════════

Shared JSON schemas for tools, resources, and prompts.
These contracts ensure type safety and consistency across the MCP surface.

Aligned with SPEC.md: Functional naming, canonical fields, and strict typing.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class VerdictCode(str, Enum):
    """Canonical constitutional verdict codes."""
    SEAL = "SEAL"       # Approved, attested
    PARTIAL = "PARTIAL" # Approved with reservations
    VOID = "VOID"       # Rejected, failed floors
    SABAR = "SABAR"     # Pending, needs more info
    HOLD = "888_HOLD"   # High-risk, requires human


class RiskTier(str, Enum):
    """Risk classification tiers."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

class SessionAnchor(BaseModel):
    """
    SessionAnchor — Established by init_session_anchor.
    Used by: init_session_anchor, session resources, prompts.
    """
    session_id: str = Field(..., description="Unique session identifier (UUID)")
    actor_id: str = Field(..., description="Human sovereign or agent identity")
    declared_name: str | None = Field(None, description="Optional display name")
    intent: str | None = Field(None, description="Session purpose statement")
    token: str | None = Field(None, description="Short-lived session token")
    created_at: str | None = Field(None, description="ISO 8601 creation time")
    expires_at: str | None = Field(None, description="ISO 8601 expiration time")


class TelemetryEnvelope(BaseModel):
    """
    TelemetryEnvelope — Standard telemetry packet.
    Used by: sense_reality, estimate_ops, judge_verdict, vitals resources.
    """
    session_id: str = Field(..., description="Source session")
    epoch: str = Field(default="2026-04-06", description="Governance epoch")
    tau_truth: float = Field(default=0.95, ge=0.0, le=1.0, description="F2: Truth alignment")
    omega_0: float = Field(default=0.05, ge=0.0, description="F7: Humility level")
    delta_s: float = Field(default=0.0, description="F4: Entropy delta")
    peace2: float = Field(default=1.0, ge=0.0, description="F5: Peace² factor")
    kappa_r: float = Field(default=0.9, ge=0.0, le=1.0, description="F6: Empathy/Care level")
    tri_witness: float = Field(default=0.0, ge=0.0, le=1.0, description="F3: Witness coherence")
    psi_le: float | None = Field(None, description="Ψ Life-Energy index")
    verdict_hint: VerdictCode | None = Field(None, description="Indicative verdict")


class EvidenceBundle(BaseModel):
    """
    EvidenceBundle — Structured evidence for handoffs.
    Used by: multi-agent handoff, reasoning, memory, vault record.
    """
    bundle_id: str = Field(..., description="Unique bundle identifier")
    session_id: str = Field(..., description="Source session")
    sources: list[dict[str, Any]] = Field(default_factory=list, description="List of evidence sources")
    synthesized: str | None = Field(None, description="Synthesized summary")
    tau_truth: float | None = Field(None, description="Aggregate truth confidence")
    tri_witness: float | None = Field(None, description="Cross-source coherence")


class VerdictRecord(BaseModel):
    """
    VerdictRecord — Immutable vault record.
    Used by: judge_verdict, record_vault_entry, vault/recent resource.
    """
    record_id: str = Field(..., description="Unique record identifier")
    session_id: str = Field(..., description="Source session")
    timestamp: str = Field(..., description="ISO 8601 seal time")
    verdict: VerdictCode
    candidate_action: str = Field(..., description="What was evaluated")
    risk_tier: RiskTier
    floors_checked: list[str] = Field(default_factory=list)
    floors_failed: list[str] = Field(default_factory=list)
    telemetry_at_verdict: TelemetryEnvelope
    bls_aggregate_signature: str | None = Field(None, description="BLS12-381 hex signature")
    seal_status: str = Field(default="PENDING")


class ConstitutionalHealthView(BaseModel):
    """
    ConstitutionalHealthView — Dashboard view.
    Used by: ChatGPT render path and widget.
    """
    session_id: str
    status: str = Field(..., enum=["HEALTHY", "DEGRADED", "CRITICAL", "VOID"])
    floors_active: int = Field(default=13, ge=0, le=13)
    telemetry: TelemetryEnvelope | None = None
    recent_verdicts: list[VerdictRecord] = Field(default_factory=list)
    widget_uri: str | None = Field(None, description="Widget render URI")


class ToolAuthContext(BaseModel):
    """
    ToolAuthContext — Restricted tool authorization.
    Used by: restricted tools (memory, vault, VPS execution).
    """
    session_id: str = Field(..., description="Bound session ID")
    token: str = Field(..., description="Session token")
    actor_id: str = Field(..., description="Verified actor identity")
    access_class: Literal["public", "authenticated", "sovereign"] = Field(default="authenticated")
    scopes: list[str] = Field(default_factory=list, description="Granted capability scopes")


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL INPUT CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

class InitSessionAnchorInput(BaseModel):
    actor_id: str = Field(..., description="Identity claim (human or agent)")
    intent: str = Field(..., description="Session purpose statement")
    declared_name: str | None = Field(None, description="Optional display name")


class JudgeVerdictInput(BaseModel):
    candidate_action: str = Field(..., description="The action to evaluate")
    risk_tier: RiskTier = Field(default=RiskTier.MEDIUM)
    telemetry: TelemetryEnvelope | None = None


class SenseRealityInput(BaseModel):
    query: str = Field(..., description="What to verify in physical reality")
    operation: Literal["search", "ingest", "compass", "atlas", "time"] = Field(default="search")


class ReasonSynthesisInput(BaseModel):
    query: str = Field(..., description="Reasoning task or synthesis target")
    context: str | None = Field(None, description="Additional context or evidence")


class CritiqueSafetyInput(BaseModel):
    content: str = Field(..., description="Content or proposal to critique")
    mode: Literal["critique", "simulate"] = Field(default="critique")


class LoadMemoryContextInput(BaseModel):
    query: str = Field(..., description="Memory search query")
    project_id: str = Field(default="default")


class EstimateOpsInput(BaseModel):
    action_description: str = Field(..., description="Planned action to estimate")


class RecordVaultEntryInput(BaseModel):
    verdict_record: VerdictRecord
    auth_context: ToolAuthContext


class ExecuteVpsTaskInput(BaseModel):
    command: str = Field(..., description="VPS command to execute")
    auth_context: ToolAuthContext


class RouteExecutionInput(BaseModel):
    query: str = Field(..., description="User request to route")


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT INPUT CONTRACTS
# ═══════════════════════════════════════════════════════════════════════════════

class PromptJudgeVerdictInput(BaseModel):
    task: str = Field(..., description="The task to judge")
    risk_tier: str = Field(..., description="Risk tier classification")
    telemetry_json: str | None = Field(None, description="Optional telemetry JSON string")


__all__ = [
    "VerdictCode", "RiskTier",
    "SessionAnchor", "TelemetryEnvelope", "EvidenceBundle", 
    "VerdictRecord", "ConstitutionalHealthView", "ToolAuthContext",
    "InitSessionAnchorInput", "JudgeVerdictInput", "SenseRealityInput",
    "ReasonSynthesisInput", "CritiqueSafetyInput", "LoadMemoryContextInput",
    "EstimateOpsInput", "RecordVaultEntryInput", "ExecuteVpsTaskInput",
    "RouteExecutionInput", "PromptJudgeVerdictInput"
]
