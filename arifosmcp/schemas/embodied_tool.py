"""
arifOS Embodied Tool Schemas — EmbodiedToolEnvelope v2
══════════════════════════════════════════════════════════════════════════════

Every MCP tool returns an EmbodiedToolEnvelope, not raw results.

The envelope makes every tool call:
- Bounded: domain, risk tier, reversibility
- Witnessed: input hash, reasoning summary, audit trail
- Authorized: permission check, session verified
- Traced: latency, outcome, state delta
- Agentic: next_best_actions for recovery, claim_state for truth discipline
- Evidence: evidence_receipt for runtime artifact anchoring

v2 Changes (Arif 2026-05-16):
- Added next_best_actions: converts refusal into agency
- Added claim_state: separates action status from truth claim
- Added artifact_status: what was produced (not just whether blocked)
- Added agentic_contract: what can/cannot do next
- Added evidence_receipt: runtime MCP outputs as valid evidence
- Added suggested_tool + can_auto_retry: automatic tool recovery
- Added trace_id + parent_trace_id + constitution_hash + tool_version: session propagation
- Added execution_status: distinct from verdict status

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ═══════════════════════════════════════════════════════════════════════════════
# CLAIM STATE ENUMS — separates action result from truth claim
# ═══════════════════════════════════════════════════════════════════════════════


class ClaimState(StrEnum):
    """Truth claim level of the tool output."""

    VERIFIED = "verified"  # Evidence-confirmed, fit for sovereign action
    INTERPRETED = "interpreted"  # Model inference, needs verification
    HYPOTHESIS = "hypothesis"  # Speculative, not yet evidenced
    NO_VALID_EVIDENCE = "no_valid_evidence"  # Blocked — no evidence available
    UNKNOWN = "unknown"  # Cannot determine


class ArtifactStatus(StrEnum):
    """What was actually produced by the tool."""

    CREATED = "created"  # New artifact produced
    MODIFIED = "modified"  # Existing artifact changed
    HYPOTHESIS_PLAN_CREATED = "hypothesis_plan_created"  # Safe degradation artifact
    NO_ARTIFACT = "no_artifact"  # No artifact produced
    ERROR = "error"  # Tool failed to produce artifact


# ═══════════════════════════════════════════════════════════════════════════════
# NEXT BEST ACTION — converts refusal into agency
# ═══════════════════════════════════════════════════════════════════════════════


class NextBestActionMode(StrEnum):
    """Mode of the recovery action."""

    HYPOTHESIS_ONLY = "hypothesis_only"
    EVIDENCE_REQUEST = "evidence_request"
    DRY_RUN = "dry_run"
    DOWNGRADE = "downgrade"
    REROUTE = "reroute"
    ESCALATE = "escalate"


class NextBestAction(BaseModel):
    """
    A single recommended next action when primary action is blocked.

    This is the core of "refusal as riverbank" — instead of a wall,
    we direct motion into a safer channel.
    """

    mode: NextBestActionMode = Field(description="Type of recovery action")
    action: str = Field(description="Human-readable description of the action")
    tool_hint: str | None = Field(
        default=None,
        description="Stable symbolic tool alias to call (e.g., 'geox.prospect.evaluate')",
    )
    parameters: dict[str, Any] | None = Field(
        default=None,
        description="Suggested parameters for the recommended tool",
    )
    evidence_required: list[str] | None = Field(
        default=None,
        description="List of evidence types needed to unlock the primary path",
    )
    rank: int = Field(default=0, description="Priority rank (0 = best option)")


# ═══════════════════════════════════════════════════════════════════════════════
# EVIDENCE RECEIPT — runtime MCP outputs as valid evidence
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceReceipt(BaseModel):
    """
    Anchors a runtime MCP artifact as valid evidence for downstream tools.

    This allows arif_judge to SEAL based on MCP-generated evidence,
    not only web/sense receipts.
    """

    receipt_id: str = Field(
        default_factory=lambda: f"EVR-{uuid.uuid4().hex[:12].upper()}",
        description="Unique evidence receipt identifier",
    )
    source_tool: str = Field(description="Tool that produced this evidence")
    artifact_hash: str = Field(description="SHA-256 of the artifact content")
    claim_state: ClaimState = Field(description="Truth claim level at production time")
    evidence_level: str = Field(
        default="runtime_observed",
        description="L0–L5 evidence level (runtime_observed is L3)",
    )
    timestamp_utc: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the evidence was produced",
    )
    session_id: str | None = Field(default=None, description="Governing session")
    actor_id: str | None = Field(default=None, description="Who triggered this")
    parameters_hash: str | None = Field(
        default=None, description="SHA-256 of input parameters for reproducibility"
    )
    downstream_verdicts: list[str] = Field(
        default_factory=list,
        description="Verdicts (SEAL/HOLD/VOID) that used this evidence",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AGENTIC CONTRACT — turns every response into a living workflow node
# ═══════════════════════════════════════════════════════════════════════════════


class AgenticContract(BaseModel):
    """
    Every tool declares what it can and cannot do, and what unlocks the next stage.

    This makes every MCP response a living workflow node, not a dead end.
    """

    what_i_can_do_now: list[str] = Field(
        default_factory=list,
        description="Actions currently available without additional evidence",
    )
    what_i_cannot_claim_yet: list[str] = Field(
        default_factory=list,
        description="Claims I cannot make yet due to missing evidence",
    )
    what_evidence_would_unlock_next_stage: list[str] = Field(
        default_factory=list,
        description="Evidence types that would enable the next capability",
    )
    safe_next_tool: str | None = Field(
        default=None,
        description="Stable symbolic alias of the safest next tool to call",
    )
    downgrade_path: str | None = Field(
        default=None,
        description="Symbolic alias of the degraded-but-safe version of this tool",
    )
    human_judgment_required: bool = Field(
        default=False,
        description="Does this operation require explicit human approval?",
    )
    escalation_path: str | None = Field(
        default=None,
        description="Symbolic alias of the tool to call when this one is insufficient",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# RISK TIERS
# ═══════════════════════════════════════════════════════════════════════════════


class RiskTier(StrEnum):
    """Shared risk ladder across all MCPs."""

    T0 = "T0"  # Harmless — auto-allowed
    T1 = "T1"  # Reversible analysis — auto-allowed with witness
    T2 = "T2"  # Advice affecting decisions — require uncertainty + caveats
    T3 = "T3"  # High-impact or semi-irreversible — require Arif approval
    T4 = "T4"  # Irreversible / dangerous / legal-medical-financial — HOLD or escalate


class Reversibility(StrEnum):
    """Reversibility classification for tool actions."""

    REVERSIBLE = "reversible"  # Can be undone trivially
    PARTIAL = "partial"  # Can be undone with effort
    IRREVERSIBLE = "irreversible"  # Cannot be undone


class ExecutionStatus(StrEnum):
    """Tool execution status.

    RECOVERABLE_ERROR is the key agentic upgrade: instead of dead-end FAILED,
    tools return RECOVERABLE_ERROR when they can suggest recovery paths.
    """

    EXECUTED = "executed"  # Completed successfully
    HELD = "held"  # Paused — requires approval
    VOID = "void"  # Rejected — constitutional breach
    ESCALATED = "escalated"  # Forwarded to Arif
    FAILED = "failed"  # Execution failed — dead end
    RECOVERABLE_ERROR = "recoverable_error"  # Failed but recovery path available


class Domain(StrEnum):
    """MCP domain classification."""

    AOS = "arifOS"  # Governance body
    WELL = "WELL"  # Human wellness body
    WEALTH = "WEALTH"  # Economic / resource body
    GEOX = "GEOX"  # Earth / physical reality body
    UNKNOWN = "unknown"


class Permission(BaseModel):
    """A single permission required for a tool."""

    name: str = Field(description="Permission identifier")
    description: str = Field(description="What this permission enables")
    required: bool = Field(default=True)


class PermissionGap(BaseModel):
    """Missing permissions for a tool call."""

    tool_id: str = Field(description="Tool that has the gap")
    missing: list[str] = Field(description="Permissions the agent lacks")
    severity: str = Field(description="'high' | 'medium' | 'low'")


class StateDelta(BaseModel):
    """Describes what changed in system state from a tool call."""

    before: dict[str, Any] = Field(default_factory=dict, description="State before action")
    after: dict[str, Any] = Field(default_factory=dict, description="State after action")
    changed_keys: list[str] = Field(default_factory=list, description="Which keys changed")


class UncertaintyItem(BaseModel):
    """A single uncertainty about the tool call."""

    source: str = Field(description="Source of uncertainty")
    description: str = Field(description="What is uncertain")
    impact: str = Field(default="medium", description="'high' | 'medium' | 'low'")


class WitnessEntry(BaseModel):
    """Audit trail for a single tool call."""

    input_hash: str = Field(description="SHA-256 of input parameters")
    tool_id: str = Field(description="Canonical tool identifier")
    tool_name: str = Field(description="Human-readable tool name")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the tool was invoked",
    )
    actor_id: str | None = Field(default=None, description="Who invoked it")
    session_id: str | None = Field(default=None, description="Governed session")
    domain: Domain = Field(default=Domain.UNKNOWN)
    risk_tier: RiskTier = Field(description="Risk tier at invocation")
    reversibility: Reversibility = Field(description="Reversibility of action")
    authority_verified: bool = Field(default=False, description="Was authority confirmed?")
    reasoning_summary: str = Field(default="", description="Brief reasoning for decision")
    execution_status: ExecutionStatus = Field(default=ExecutionStatus.EXECUTED)
    latency_ms: float | None = Field(default=None, description="Execution time")
    error: str | None = Field(default=None, description="Error message if failed")


class EmbodiedToolEnvelope(BaseModel):
    """
    Every MCP tool returns this envelope.

    It makes the tool call embodied: bounded, witnessed, authorized, agentic.

    v2 Fields (Arif 2026-05-16):
        status: SEAL (proceed) | HOLD (pause) | VOID (reject) | ESCALATE
        execution_status: EXECUTED | HELD | VOID | ESCALATED | FAILED (action result)
        claim_state: VERIFIED | INTERPRETED | HYPOTHESIS | NO_VALID_EVIDENCE | UNKNOWN (truth claim)
        artifact_status: CREATED | MODIFIED | HYPOTHESIS_PLAN_CREATED | NO_ARTIFACT | ERROR
        domain: Which MCP organ is handling this
        actor_id: Who is asking
        session_id: Session for authority verification
        trace_id: Unique trace for this call chain
        parent_trace_id: Parent trace for call lineage
        constitution_hash: Hash of constitution at invocation time
        tool_version: Version of the tool implementation
        risk_tier: T0-T4 risk classification
        reversibility: Can this be undone?
        authority_required: Does this need Arif approval?
        authority_verified: Has authority been confirmed?
        confidence: Confidence in the result (0.0-1.0)
        uncertainty: List of known uncertainties
        result: The actual tool result
        witness: Full audit trail for this call
        next_safe_action: What should happen next
        next_best_actions: Recovery options when primary is blocked (riverbank, not wall)
        agentic_contract: What can/cannot do next (workflow node, not dead end)
        evidence_receipt: Runtime artifact anchoring for downstream verification
        suggested_tool: Correct tool path if this one failed (auto-recovery)
        can_auto_retry: Whether to retry without user confirmation
    """

    # Identity
    tool_id: str = Field(description="Canonical tool identifier e.g. 'arif_think'")
    tool_name: str = Field(description="Human-readable tool name")
    domain: Domain = Field(description="Which MCP organ")
    tool_version: str | None = Field(
        default=None, description="Tool implementation version for audit"
    )

    # Session propagation (Fix #2)
    session_id: str | None = Field(default=None, description="Governed session token")
    actor_id: str | None = Field(default=None, description="Who is asking")
    trace_id: str | None = Field(
        default=None,
        description="Unique trace ID for this call (auto-generated if not provided)",
    )
    parent_trace_id: str | None = Field(
        default=None, description="Parent trace ID for call lineage"
    )
    constitution_hash: str | None = Field(
        default=None, description="Constitution hash at invocation for audit"
    )

    # Authorization
    authority_required: bool = Field(default=False, description="Does this need Arif approval?")
    authority_verified: bool = Field(default=False, description="Has authority been confirmed?")

    # Risk
    risk_tier: RiskTier = Field(description="T0-T4 risk classification")
    reversibility: Reversibility = Field(description="Reversibility of the action")

    # Result
    status: str = Field(
        default="SEAL",
        description="SEAL | HOLD | VOID | ESCALATE",
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence in result",
    )
    uncertainty: list[UncertaintyItem] = Field(
        default_factory=list,
        description="Known uncertainties about this result",
    )

    # Content
    result: dict[str, Any] = Field(default_factory=dict, description="Tool-specific result")
    error: str | None = Field(default=None, description="Error if failed")

    # Witness
    witness: WitnessEntry = Field(description="Full audit trail for this call")

    # Agentic response fields (Fixes #1, #4, #6, #10)
    # Separates action status from truth claim; provides recovery paths
    execution_status: ExecutionStatus = Field(
        default=ExecutionStatus.EXECUTED,
        description="EXECUTED | HELD | VOID | ESCALATED | FAILED — action result, not verdict",
    )
    claim_state: ClaimState = Field(
        default=ClaimState.UNKNOWN,
        description="VERIFIED | INTERPRETED | HYPOTHESIS | NO_VALID_EVIDENCE | UNKNOWN",
    )
    artifact_status: ArtifactStatus = Field(
        default=ArtifactStatus.NO_ARTIFACT,
        description="CREATED | MODIFIED | HYPOTHESIS_PLAN_CREATED | NO_ARTIFACT | ERROR",
    )
    next_best_actions: list[NextBestAction] = Field(
        default_factory=list,
        description="Recovery options when primary action is blocked (riverbank, not wall)",
    )

    # Tool recovery (Fix #4)
    suggested_tool: str | None = Field(
        default=None,
        description="Correct tool path if this one failed (auto-recovery hint)",
    )
    can_auto_retry: bool = Field(
        default=False,
        description="Whether to retry suggested_tool without user confirmation",
    )

    # Agentic contract (Fix #10)
    agentic_contract: AgenticContract | None = Field(
        default=None,
        description="What I can/cannot do now, and what unlocks the next stage",
    )

    # Evidence receipt (Fix #5)
    evidence_receipt: EvidenceReceipt | None = Field(
        default=None,
        description="Runtime artifact anchoring for downstream arif_judge verification",
    )

    # Next step
    next_safe_action: str = Field(
        default="None — action completed.",
        description="What should happen next",
    )

    # Meta
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tool_id": "arif_think",
                "tool_name": "arif_think",
                "domain": "AOS",
                "actor_id": "arif",
                "session_id": "sess_abc123",
                "authority_required": False,
                "authority_verified": True,
                "risk_tier": "T1",
                "reversibility": "reversible",
                "status": "SEAL",
                "confidence": 0.87,
                "uncertainty": [
                    {
                        "source": "model_knowledge",
                        "description": "Knowledge cutoff may affect recent events",
                        "impact": "low",
                    }
                ],
                "result": {"reasoning_output": "..."},
                "witness": {
                    "input_hash": "sha256:...",
                    "tool_id": "arif_think",
                    "timestamp": "2026-05-09T12:00:00Z",
                    "actor_id": "arif",
                    "session_id": "sess_abc123",
                    "domain": "AOS",
                    "risk_tier": "T1",
                    "reversibility": "reversible",
                    "authority_verified": True,
                    "reasoning_summary": "Reasoned about query with L07 humility",
                    "execution_status": "executed",
                    "latency_ms": 234.5,
                },
                "next_safe_action": "Proceed to 888_JUDGE if action is consequential",
            }
        }
    )


def build_embodied_envelope(
    tool_id: str,
    tool_name: str,
    domain: Domain,
    actor_id: str | None,
    session_id: str | None,
    risk_tier: RiskTier,
    reversibility: Reversibility,
    authority_required: bool,
    authority_verified: bool,
    result: dict[str, Any],
    witness_input_hash: str,
    reasoning_summary: str = "",
    confidence: float = 0.5,
    uncertainty: list[UncertaintyItem] | None = None,
    status: str = "SEAL",
    error: str | None = None,
    latency_ms: float | None = None,
    metadata: dict[str, Any] | None = None,
    # v2 fields
    trace_id: str | None = None,
    parent_trace_id: str | None = None,
    constitution_hash: str | None = None,
    tool_version: str | None = None,
    execution_status: ExecutionStatus | None = None,
    claim_state: ClaimState | None = None,
    artifact_status: ArtifactStatus | None = None,
    next_best_actions: list[NextBestAction] | None = None,
    suggested_tool: str | None = None,
    can_auto_retry: bool = False,
    agentic_contract: AgenticContract | None = None,
    evidence_receipt: EvidenceReceipt | None = None,
) -> EmbodiedToolEnvelope:
    """
    Factory to build a properly structured EmbodiedToolEnvelope v2.

    This is the standard way to wrap any tool result.
    All new agentic fields have sensible defaults for backward compatibility.
    """
    _now = datetime.now(UTC).isoformat()

    # Auto-generate trace_id if not provided
    if trace_id is None:
        trace_id = f"trace-{uuid.uuid4().hex[:16]}"

    # Map status to execution_status if not explicitly provided
    if execution_status is None:
        if status == "SEAL":
            execution_status = ExecutionStatus.EXECUTED
        elif status == "HOLD":
            execution_status = ExecutionStatus.HELD
        elif status == "VOID":
            execution_status = ExecutionStatus.VOID
        elif status == "ESCALATED":
            execution_status = ExecutionStatus.ESCALATED
        else:
            execution_status = ExecutionStatus.FAILED

    # Map claim_state defaults based on status
    if claim_state is None:
        if status == "SEAL":
            claim_state = ClaimState.VERIFIED
        elif status == "HOLD":
            claim_state = ClaimState.INTERPRETED
        else:
            claim_state = ClaimState.UNKNOWN

    # Map artifact_status based on result and error
    if artifact_status is None:
        if error:
            artifact_status = ArtifactStatus.ERROR
        elif result:
            artifact_status = ArtifactStatus.CREATED
        else:
            artifact_status = ArtifactStatus.NO_ARTIFACT

    witness = WitnessEntry(
        input_hash=witness_input_hash,
        tool_id=tool_id,
        tool_name=tool_name,
        timestamp=_now,
        actor_id=actor_id,
        session_id=session_id,
        domain=domain,
        risk_tier=risk_tier,
        reversibility=reversibility,
        authority_verified=(
            authority_required is False or authority_verified if authority_required else True
        ),
        reasoning_summary=reasoning_summary,
        execution_status=execution_status,
        latency_ms=latency_ms,
        error=error,
    )

    if status == "HOLD":
        next_action = "Await Arif approval before proceeding."
    elif status == "VOID":
        next_action = "Action rejected. Do not retry without modification."
    elif status == "ESCALATED":
        next_action = "Forwarded to Arif. Await decision."
    else:
        next_action = "Proceed to 888_JUDGE if action is consequential."

    return EmbodiedToolEnvelope(
        tool_id=tool_id,
        tool_name=tool_name,
        domain=domain,
        tool_version=tool_version,
        actor_id=actor_id,
        session_id=session_id,
        trace_id=trace_id,
        parent_trace_id=parent_trace_id,
        constitution_hash=constitution_hash,
        authority_required=authority_required,
        authority_verified=authority_required is False or (session_id is not None),
        risk_tier=risk_tier,
        reversibility=reversibility,
        status=status,
        confidence=confidence,
        uncertainty=uncertainty or [],
        result=result,
        error=error,
        witness=witness,
        execution_status=execution_status,
        claim_state=claim_state,
        artifact_status=artifact_status,
        next_best_actions=next_best_actions or [],
        suggested_tool=suggested_tool,
        can_auto_retry=can_auto_retry,
        agentic_contract=agentic_contract,
        evidence_receipt=evidence_receipt,
        next_safe_action=next_action,
        metadata=metadata or {},
    )


__all__ = [
    # Enums
    "RiskTier",
    "Reversibility",
    "ExecutionStatus",
    "Domain",
    "ClaimState",
    "ArtifactStatus",
    "NextBestActionMode",
    # Schemas
    "Permission",
    "PermissionGap",
    "StateDelta",
    "UncertaintyItem",
    "WitnessEntry",
    "NextBestAction",
    "EvidenceReceipt",
    "AgenticContract",
    # Main envelope
    "EmbodiedToolEnvelope",
    "build_embodied_envelope",
]
