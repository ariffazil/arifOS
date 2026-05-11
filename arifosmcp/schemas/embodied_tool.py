"""
arifOS Embodied Tool Schemas — EmbodiedToolEnvelope v1
═══════════════════════════════════════════════════════════════════════════════

Every MCP tool returns an EmbodiedToolEnvelope, not raw results.

The envelope makes every tool call:
- Bounded: domain, risk tier, reversibility
- Witnessed: input hash, reasoning summary, audit trail
- Authorized: permission check, session verified
- Traced: latency, outcome, state delta

This is the body of the agentic tool system.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RiskTier(str, Enum):
    """Shared risk ladder across all MCPs."""

    T0 = "T0"  # Harmless — auto-allowed
    T1 = "T1"  # Reversible analysis — auto-allowed with witness
    T2 = "T2"  # Advice affecting decisions — require uncertainty + caveats
    T3 = "T3"  # High-impact or semi-irreversible — require Arif approval
    T4 = "T4"  # Irreversible / dangerous / legal-medical-financial — HOLD or escalate


class Reversibility(str, Enum):
    """Reversibility classification for tool actions."""

    REVERSIBLE = "reversible"  # Can be undone trivially
    PARTIAL = "partial"  # Can be undone with effort
    IRREVERSIBLE = "irreversible"  # Cannot be undone


class ExecutionStatus(str, Enum):
    """Tool execution status."""

    EXECUTED = "executed"  # Completed successfully
    HELD = "held"  # Paused — requires approval
    VOID = "void"  # Rejected — constitutional breach
    ESCALATED = "escalated"  # Forwarded to Arif
    FAILED = "failed"  # Execution failed


class Domain(str, Enum):
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

    before: dict[str, Any] = Field(
        default_factory=dict, description="State before action"
    )
    after: dict[str, Any] = Field(
        default_factory=dict, description="State after action"
    )
    changed_keys: list[str] = Field(
        default_factory=list, description="Which keys changed"
    )


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
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="When the tool was invoked",
    )
    actor_id: str | None = Field(default=None, description="Who invoked it")
    session_id: str | None = Field(default=None, description="Governed session")
    domain: Domain = Field(default=Domain.UNKNOWN)
    risk_tier: RiskTier = Field(description="Risk tier at invocation")
    reversibility: Reversibility = Field(description="Reversibility of action")
    authority_verified: bool = Field(
        default=False, description="Was authority confirmed?"
    )
    reasoning_summary: str = Field(
        default="", description="Brief reasoning for decision"
    )
    execution_status: ExecutionStatus = Field(default=ExecutionStatus.EXECUTED)
    latency_ms: float | None = Field(default=None, description="Execution time")
    error: str | None = Field(default=None, description="Error message if failed")


class EmbodiedToolEnvelope(BaseModel):
    """
    Every MCP tool returns this envelope.

    It makes the tool call embodied: bounded, witnessed, authorized.

    Fields:
        status: SEAL (proceed) | HOLD (pause) | VOID (reject) | ESCALATE
        domain: Which MCP organ is handling this
        actor_id: Who is asking
        session_id: Session for authority verification
        risk_tier: T0-T4 risk classification
        reversibility: Can this be undone?
        authority_required: Does this need Arif approval?
        authority_verified: Has authority been confirmed?
        confidence: Confidence in the result (0.0-1.0)
        uncertainty: List of known uncertainties
        result: The actual tool result
        witness: Full audit trail for this call
        next_safe_action: What should happen next
    """

    # Identity
    tool_id: str = Field(
        description="Canonical tool identifier e.g. 'arif_mind_reason'"
    )
    tool_name: str = Field(description="Human-readable tool name")
    domain: Domain = Field(description="Which MCP organ")

    # Authorization
    actor_id: str | None = Field(default=None, description="Who is asking")
    session_id: str | None = Field(default=None, description="Governed session token")
    authority_required: bool = Field(
        default=False, description="Does this need Arif approval?"
    )
    authority_verified: bool = Field(
        default=False, description="Has authority been confirmed?"
    )

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
    result: dict[str, Any] = Field(
        default_factory=dict, description="Tool-specific result"
    )
    error: str | None = Field(default=None, description="Error if failed")

    # Witness
    witness: WitnessEntry = Field(description="Full audit trail for this call")

    # Next step
    next_safe_action: str = Field(
        default="None — action completed.",
        description="What should happen next",
    )

    # Meta
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tool_id": "arif_mind_reason",
                "tool_name": "arif_mind_reason",
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
                    "tool_id": "arif_mind_reason",
                    "timestamp": "2026-05-09T12:00:00Z",
                    "actor_id": "arif",
                    "session_id": "sess_abc123",
                    "domain": "AOS",
                    "risk_tier": "T1",
                    "reversibility": "reversible",
                    "authority_verified": True,
                    "reasoning_summary": "Reasoned about query with F07 humility",
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
) -> EmbodiedToolEnvelope:
    """
    Factory to build a properly structured EmbodiedToolEnvelope.

    This is the standard way to wrap any tool result.
    """
    _now = datetime.now(timezone.utc).isoformat()

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
            authority_required is False or authority_verified
            if authority_required
            else True
        ),
        reasoning_summary=reasoning_summary,
        execution_status=(
            ExecutionStatus.EXECUTED
            if status == "SEAL"
            else (
                ExecutionStatus.HELD
                if status == "HOLD"
                else (
                    ExecutionStatus.VOID if status == "VOID" else ExecutionStatus.FAILED
                )
            )
        ),
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
        actor_id=actor_id,
        session_id=session_id,
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
        next_safe_action=next_action,
        metadata=metadata or {},
    )


__all__ = [
    "RiskTier",
    "Reversibility",
    "ExecutionStatus",
    "Domain",
    "Permission",
    "PermissionGap",
    "StateDelta",
    "UncertaintyItem",
    "WitnessEntry",
    "EmbodiedToolEnvelope",
    "build_embodied_envelope",
]
