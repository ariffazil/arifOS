"""
consequence_chain.py — Consequence Chain Schema for VAULT999
═══════════════════════════════════════════════════════════

Adapted from CORE (DariuszNewecki/CORE) — consequence chain pattern.
Every enforcement action records its full lineage:
  FINDING → PROPOSAL → APPROVAL → EXECUTION → FILE CHANGE

Both autonomous and human-approval paths use the same schema.
The constitution decides which authority applies; the schema is identical.

What arifOS adds that CORE doesn't:
  - Human substrate context at time of action
  - Grief sensitivity in consequence chains
  - Hollow boundary enforcement
  - Scar sensitivity levels

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


# ── Authority ────────────────────────────────────────────────────────


class ApprovalAuthority(StrEnum):
    """Who approved this action."""

    AUTONOMOUS = "autonomous"  # Risk-classified as safe, system self-approved
    SUBSTRATE_AUTO = "substrate_auto"  # Human substrate auto-approved (low risk)
    HUMAN_888 = "human_888"  # Sovereign explicitly approved
    FLOOR_AUTO = "floor_auto"  # Floor enforcement auto-approved
    HOLD = "hold"  # Waiting for approval
    VOID = "void"  # Rejected


class RiskClassification(StrEnum):
    """Risk level of the action."""

    SAFE_AUTO = "safe_auto"  # Can be auto-approved
    LOW = "low"  # Low risk, auto-approve with logging
    MEDIUM = "medium"  # Medium risk, needs substrate check
    HIGH = "high"  # High risk, needs human approval
    CRITICAL = "critical"  # Critical, needs F13 explicit
    IRREVERSIBLE = "irreversible"  # Cannot be undone, F13 required


# ── Finding ──────────────────────────────────────────────────────────


class ConsequenceFinding(BaseModel):
    """The initial finding that triggered the chain."""

    finding_id: str = Field(..., description="Unique finding identifier")
    finding_type: str = Field(
        ...,
        description="Type: floor_violation, substrate_guard, hollow_boundary, "
        "grief_sensitivity, scar_extreme, shadow_detected",
    )
    floor_id: str | None = Field(
        default=None, description="Which floor was triggered (e.g., F05, F06)"
    )
    tool_name: str = Field(..., description="Which tool triggered this")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Tool parameters at time of finding"
    )
    severity: str = Field(
        default="advisory",
        description="advisory, warning, block, critical",
    )
    description: str = Field(..., description="Human-readable finding description")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ── Proposal ─────────────────────────────────────────────────────────


class ConsequenceProposal(BaseModel):
    """The proposed action to address the finding."""

    proposal_id: str = Field(..., description="Unique proposal identifier")
    finding_id: str = Field(..., description="References the finding")
    proposal_type: str = Field(
        ...,
        description="Type: fix, guard, block, escalate, hold, void",
    )
    description: str = Field(..., description="What the proposal does")
    risk_classification: RiskClassification = Field(
        ..., description="Risk level of the proposed action"
    )
    reversibility: str = Field(
        default="reversible",
        description="reversible, partially_reversible, irreversible",
    )
    blast_radius: str = Field(
        default="local",
        description="local, organ, federation, external",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ── Approval ─────────────────────────────────────────────────────────


class ConsequenceApproval(BaseModel):
    """Who approved the proposal and how."""

    approval_id: str = Field(..., description="Unique approval identifier")
    proposal_id: str = Field(..., description="References the proposal")
    authority: ApprovalAuthority = Field(
        ..., description="Who approved this action"
    )
    approver_id: str | None = Field(
        default=None,
        description="Specific approver (e.g., 'F13_SOVEREIGN', 'substrate_auto')",
    )
    approval_reason: str = Field(
        default="", description="Why this was approved/rejected"
    )
    conditions: list[str] = Field(
        default_factory=list,
        description="Conditions for approval (e.g., 'log_to_vault', 'notify_888')",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ── Execution ────────────────────────────────────────────────────────


class ConsequenceExecution(BaseModel):
    """The actual execution result."""

    execution_id: str = Field(..., description="Unique execution identifier")
    approval_id: str = Field(..., description="References the approval")
    status: str = Field(
        ...,
        description="completed, failed, partial, skipped, blocked",
    )
    duration_ms: float | None = Field(
        default=None, description="Execution duration in milliseconds"
    )
    error: str | None = Field(
        default=None, description="Error message if failed"
    )
    output_summary: str = Field(
        default="", description="Brief summary of execution output"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ── File Change ──────────────────────────────────────────────────────


class ConsequenceFileChange(BaseModel):
    """Files changed by the execution."""

    file_path: str = Field(..., description="Path to changed file")
    change_type: str = Field(
        ..., description="created, modified, deleted, renamed"
    )
    lines_added: int = Field(default=0)
    lines_removed: int = Field(default=0)
    old_hash: str | None = Field(default=None, description="SHA-256 before change")
    new_hash: str | None = Field(default=None, description="SHA-256 after change")


# ── Human Substrate Context ──────────────────────────────────────────


class SubstrateContext(BaseModel):
    """Human substrate state at time of action.

    This is what arifOS adds that CORE doesn't have.
    The human's scars, shadows, hollows, grief state — all recorded
    at the moment of action. Not just what happened, but WHO it
    happened to and WHAT they were carrying.
    """

    scar_density: int = Field(default=0, description="Active scar count")
    shadow_count: int = Field(default=0, description="Active shadow count")
    hollow_count: int = Field(default=0, description="Hollow count (DO_NOT_FILL)")
    grief_active: bool = Field(default=False)
    grief_sensitivity: str = Field(
        default="normal", description="normal, high, extreme"
    )
    active_scar_ids: list[str] = Field(
        default_factory=list, description="Which scars are currently active"
    )
    active_shadow_ids: list[str] = Field(
        default_factory=list, description="Which shadows are currently active"
    )
    floor_impacts: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Floor → list of substrate impacts at time of action",
    )
    substrate_verdict: str = Field(
        default="PASS",
        description="PASS, STRENGTHEN, GUARD, BLOCK",
    )
    substrate_reasons: list[str] = Field(
        default_factory=list, description="Why the substrate verdict was given"
    )


# ── Consequence Chain (Complete) ─────────────────────────────────────


class ConsequenceChain(BaseModel):
    """Complete consequence chain for a single enforcement action.

    FINDING → PROPOSAL → APPROVAL → EXECUTION → FILE CHANGE

    Every chain includes human substrate context — not just what
    happened, but who it happened to and what they were carrying.

    Adapted from CORE (DariuszNewecki/CORE).
    Enhanced with arifOS human substrate integration.
    """

    chain_id: str = Field(..., description="Unique chain identifier")
    session_id: str | None = Field(default=None)
    actor_id: str | None = Field(default=None)

    # The chain
    finding: ConsequenceFinding
    proposal: ConsequenceProposal | None = None
    approval: ConsequenceApproval | None = None
    execution: ConsequenceExecution | None = None
    file_changes: list[ConsequenceFileChange] = Field(default_factory=list)

    # Human substrate at time of action (arifOS addition)
    substrate_context: SubstrateContext = Field(default_factory=SubstrateContext)

    # Vault integration
    vault_entry_id: str | None = Field(
        default=None, description="VAULT999 entry ID after sealing"
    )
    sealed: bool = Field(default=False)

    # Timing
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime | None = None

    def to_vault_payload(self) -> dict[str, Any]:
        """Serialize for VAULT999 sealing."""
        return {
            "chain_id": self.chain_id,
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "finding": self.finding.model_dump(mode="json"),
            "proposal": self.proposal.model_dump(mode="json") if self.proposal else None,
            "approval": self.approval.model_dump(mode="json") if self.approval else None,
            "execution": self.execution.model_dump(mode="json") if self.execution else None,
            "file_changes": [fc.model_dump(mode="json") for fc in self.file_changes],
            "substrate_context": self.substrate_context.model_dump(mode="json"),
            "sealed": self.sealed,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def is_complete(self) -> bool:
        """Check if the chain has all required links."""
        return (
            self.finding is not None
            and self.proposal is not None
            and self.approval is not None
            and self.execution is not None
        )

    def is_autonomous(self) -> bool:
        """Check if this was auto-approved (no human needed)."""
        if self.approval is None:
            return False
        return self.approval.authority in (
            ApprovalAuthority.AUTONOMOUS,
            ApprovalAuthority.SUBSTRATE_AUTO,
            ApprovalAuthority.FLOOR_AUTO,
        )

    def needs_human(self) -> bool:
        """Check if this needs human approval."""
        if self.proposal is None:
            return False
        return self.proposal.risk_classification in (
            RiskClassification.HIGH,
            RiskClassification.CRITICAL,
            RiskClassification.IRREVERSIBLE,
        )


# ── Factory Functions ────────────────────────────────────────────────


def create_chain(
    finding_type: str,
    tool_name: str,
    description: str,
    floor_id: str | None = None,
    severity: str = "advisory",
    params: dict[str, Any] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> ConsequenceChain:
    """Create a new consequence chain with a finding."""
    import uuid

    chain_id = f"chain-{uuid.uuid4().hex[:12]}"
    finding_id = f"find-{uuid.uuid4().hex[:12]}"

    finding = ConsequenceFinding(
        finding_id=finding_id,
        finding_type=finding_type,
        floor_id=floor_id,
        tool_name=tool_name,
        params=params or {},
        severity=severity,
        description=description,
    )

    return ConsequenceChain(
        chain_id=chain_id,
        session_id=session_id,
        actor_id=actor_id,
        finding=finding,
    )


def auto_classify_risk(chain: ConsequenceChain) -> RiskClassification:
    """Auto-classify risk based on finding type and substrate context."""
    finding = chain.finding
    substrate = chain.substrate_context

    # Irreversible actions always need human
    if finding.finding_type in ("irreversible_action", "vault_seal"):
        return RiskClassification.IRREVERSIBLE

    # Hollow boundaries are critical
    if finding.finding_type == "hollow_boundary":
        return RiskClassification.CRITICAL

    # Grief sensitivity with extreme scar → high
    if substrate.grief_active and substrate.grief_sensitivity == "extreme":
        return RiskClassification.HIGH

    # Extreme sensitivity scars → high
    if "extreme" in substrate.grief_sensitivity:
        return RiskClassification.HIGH

    # Floor violations → medium to high
    if finding.finding_type == "floor_violation":
        if finding.severity == "block":
            return RiskClassification.HIGH
        return RiskClassification.MEDIUM

    # Substrate guards → low to medium
    if finding.finding_type == "substrate_guard":
        if substrate.substrate_verdict == "GUARD":
            return RiskClassification.MEDIUM
        return RiskClassification.LOW

    # Default → safe auto
    return RiskClassification.SAFE_AUTO


__all__ = [
    "ApprovalAuthority",
    "ConsequenceApproval",
    "ConsequenceChain",
    "ConsequenceExecution",
    "ConsequenceFileChange",
    "ConsequenceFinding",
    "ConsequenceProposal",
    "RiskClassification",
    "SubstrateContext",
    "auto_classify_risk",
    "create_chain",
]
