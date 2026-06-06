"""
arifOS Forge Output Schemas — 010_FORGE
══════════════════════════════════════════════════════════════════════════════

Phase 2 Civilization Intelligence — ForgeOutput for arif_forge_execute.
Forged irreversibly: delta_S, irreversibility bond, manifest, execution trace.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

from arifosmcp.schemas.lineage import JudgeSealContract

# ═══════════════════════════════════════════════════════════════════════════════
# FORGE ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class IrreversibilityLevel(StrEnum):
    """How irreversible is this forge action?"""

    REVERSIBLE = "reversible"
    SEMI_IRREVERSIBLE = "semi_irreversible"
    IRREVERSIBLE = "irreversible"
    CATASTROPHIC = "catastrophic"


class ManifestStatus(StrEnum):
    """What happened to the manifest?"""

    PENDING = "pending"
    FORGED = "forged"
    COMMITTED = "committed"
    SEALED = "sealed"
    VOID = "void"
    HOLD = "hold"  # Constitutional floor gate — not yet authorized


# ═══════════════════════════════════════════════════════════════════════════════
# IRREVERSIBILITY BOND — ENTROPY COST OF THIS ACTION
# ═══════════════════════════════════════════════════════════════════════════════


class IrreversibilityBond(BaseModel):
    """
    Landauer-aware irreversibility assessment.
    Every irreversible computation has a thermodynamic cost.
    Delta_S_positive = heat generated to environment.

    Mandatory in: 999_VAULT, 010_FORGE
    """

    level: IrreversibilityLevel = Field(
        default=IrreversibilityLevel.REVERSIBLE,
        description="How irreversible is this action?",
    )
    delta_S: float = Field(
        default=0.0, description="Entropy change (J/K). Positive = heat to environment."
    )
    landauer_cost_joules: float | None = Field(
        default=None, description="Landauer bound: k_B * T * ln(2) * bits_flipped"
    )
    compensation_required: bool = Field(
        default=False, description="Does this action require compensation entropy?"
    )
    rollback_possible: bool = Field(
        default=True, description="Can this action be theoretically rolled back?"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DELTA S EVIDENCE — THERMODYNAMIC FOOTPRINT
# ═══════════════════════════════════════════════════════════════════════════════


class DeltaSEvidence(BaseModel):
    """
    Thermodynamic evidence for forge action.
    Tracks entropy production across the execution.

    Fields affect behavior:
    - delta_S_net determines if action is allowed (L13 entropy budget)
    - energy_cost determines if system can afford the action
    """

    delta_S_positive: float = Field(
        default=0.0, description="Entropy produced (heat to environment)"
    )
    delta_S_negative: float = Field(default=0.0, description="Entropy absorbed (cooling)")
    delta_S_net: float = Field(default=0.0, description="Net entropy change")
    energy_cost_joules: float | None = Field(default=None, description="Direct energy cost")
    landauer_optimal: bool = Field(default=True, description="Is action within Landauer bound?")
    entropy_budget_remaining: float | None = Field(
        default=None, description="L13 entropy budget remaining"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTION TRACE — WHAT HAPPENED DURING FORGE
# ═══════════════════════════════════════════════════════════════════════════════


class ExecutionNode(BaseModel):
    """Single step in the forge execution trace."""

    step: int = Field(default=0, description="Step number")
    action: str = Field(default="", description="What was done")
    artifact_id: str | None = Field(default=None, description="ID of artifact produced")
    delta_S: float = Field(default=0.0, description="Entropy change at this step")
    reversible: bool = Field(default=True, description="Whether this step can be undone")
    meta: dict[str, Any] = Field(default_factory=dict)


class ExecutionTrace(BaseModel):
    """Full trace of what happened during forge."""

    steps: list[ExecutionNode] = Field(default_factory=list)
    total_steps: int = Field(default=0)
    final_artifact_id: str | None = Field(default=None)
    final_status: ManifestStatus = Field(default=ManifestStatus.PENDING)
    final_delta_S: float = Field(default=0.0)
    rollbacks_attempted: int = Field(default=0)
    rollbacks_succeeded: int = Field(default=0)


# ═══════════════════════════════════════════════════════════════════════════════
# FORGE MANIFEST — THE THING BEING FORGED
# ═══════════════════════════════════════════════════════════════════════════════


class ForgeManifest(BaseModel):
    """The artifact being forged."""

    artifact_id: str = Field(default="", description="Unique identifier")
    name: str = Field(default="", description="Human-readable name")
    type: str = Field(default="", description="artifact_type")
    size_bytes: int = Field(default=0)
    checksum: str | None = Field(default=None)
    manifest_raw: str = Field(default="", description="Raw manifest content")
    status: ManifestStatus = Field(default=ManifestStatus.PENDING)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL COMPLIANCE — F1-L13 CHECK RESULTS
# ═══════════════════════════════════════════════════════════════════════════════


class ConstitutionalCompliance(BaseModel):
    """F1-L13 floor compliance for this forge action."""

    floors_invoked: list[str] = Field(default_factory=list)
    law_results: dict[str, str] = Field(default_factory=dict)
    violations_found: list[str] = Field(default_factory=list)
    genius_score: float = Field(default=0.0, description="Elegance under constraint")
    amanah_score: float = Field(default=0.0, description="Accountability")


# ═══════════════════════════════════════════════════════════════════════════════
# FORGE OUTPUT — PRIMARY OUTPUT FOR arif_forge_execute
# ═══════════════════════════════════════════════════════════════════════════════


class ForgeOutput(BaseModel):
    """
    Full output for arif_forge_execute (010_FORGE).

    Every field affects reasoning behavior:
    - irreversibility_bond: determines if actor can ack_irreversible
    - delta_S_evidence: determines if L13 entropy budget allows action
    - constitutional_compliance: determines if floors pass/fail
    - execution_trace: shows exactly what happened (accountability)

    Stage: 010_FORGE
    Pillar: Thermodynamic + Amanah Genius + Constitutional Law
    """

    # Core
    manifest: ForgeManifest = Field(default_factory=ForgeManifest)
    status: str = Field(default="OK", description="'OK' | 'HOLD' | 'VOID'")
    result: dict[str, Any] = Field(default_factory=dict)

    # Irreversibility
    irreversibility_bond: IrreversibilityBond = Field(
        default_factory=IrreversibilityBond,
        description="Thermodynamic irreversibility assessment",
    )

    # Entropy
    delta_S_evidence: DeltaSEvidence = Field(
        default_factory=DeltaSEvidence, description="Entropy production evidence"
    )

    # Constitutional compliance
    constitutional_compliance: ConstitutionalCompliance = Field(
        default_factory=ConstitutionalCompliance, description="F1-L13 floor compliance"
    )

    # Execution trace
    execution_trace: ExecutionTrace = Field(
        default_factory=ExecutionTrace, description="Step-by-step execution record"
    )

    # Acknowledgment
    ack_irreversible_received: bool = Field(
        default=False, description="Did actor acknowledge irreversibility?"
    )
    ack_irreversible_timestamp: str | None = Field(default=None)

    constitutional_chain_id: str | None = Field(
        default=None,
        description="Lineage ID shared with Judge and Vault packets",
    )
    judge_state_hash: str | None = Field(
        default=None,
        description="Judge packet hash used to authorize this forge action",
    )
    vault_entry_id: str | None = Field(
        default=None,
        description="Vault ledger entry authorizing this forge action",
    )
    judge_contract: JudgeSealContract | None = Field(
        default=None,
        description="Structured judge packet propagated into forge lineage",
    )

    # Metadata
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None

    # Nine-Signal / F2 addendum — reasons[] required for HOLD/VOID/SABAR
    reasons: list[str] = Field(default_factory=list)

    # Constitutional health signal (delta/psi/omega/overall)
    nine_signal: dict[str, Any] | None = Field(default=None)


# ═══════════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE ENVELOPE
# ═══════════════════════════════════════════════════════════════════════════════


class ForgeEnvelope(BaseModel):
    """Backward-compatible forge envelope."""

    status: str = "OK"
    tool: str = "arif_forge_execute"
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None


# Alias
ForgeManifest2 = ForgeManifest

# ═══════════════════════════════════════════════════════════════════════════════
# FORGE ERROR CODES — EXACT REASONS, NOT VAGUE STRINGS
# ═══════════════════════════════════════════════════════════════════════════════


class ForgeErrorCode(StrEnum):
    """Exact error codes for forge operations. Never return vague strings."""

    # Stage / progression errors
    E_STAGE_TOOL_MISMATCH = "E_STAGE_TOOL_MISMATCH"
    E_VERDICT_PLANE_CONFLICT = "E_VERDICT_PLANE_CONFLICT"

    # Identity / auth errors
    E_IDENTITY_UNVERIFIED = "E_IDENTITY_UNVERIFIED"
    E_LEGACY_WRAP_ATOMIC_DENIED = "E_LEGACY_WRAP_ATOMIC_DENIED"
    E_CAPABILITY_MEMBRANE_VIOLATION = "E_CAPABILITY_MEMBRANE_VIOLATION"

    # Execution errors
    E_FORGE_MODE_NOT_ALLOWED = "E_FORGE_MODE_NOT_ALLOWED"
    E_JUDGE_STATE_HASH_REQUIRED = "E_JUDGE_STATE_HASH_REQUIRED"
    E_ACK_IRREVERSIBLE_REQUIRED = "E_ACK_IRREVERSIBLE_REQUIRED"
    E_SIDE_EFFECTS_BLOCKED = "E_SIDE_EFFECTS_BLOCKED"
    E_SELF_AUTHORIZE_DETECTED = "E_SELF_AUTHORIZE_DETECTED"
    E_DRY_RUN_ONLY = "E_DRY_RUN_ONLY"

    # Schema / output errors
    E_SCHEMA_UNSTRUCTURED_OUTPUT = "E_SCHEMA_UNSTRUCTURED_OUTPUT"
    E_SYNTHESIS_EMPTY = "E_SYNTHESIS_EMPTY"
    E_CONFIDENCE_MISCALIBRATED = "E_CONFIDENCE_MISCALIBRATED"

    # Workspace / filesystem errors
    E_WORKSPACE_ESCAPE = "E_WORKSPACE_ESCAPE"
    E_COMMAND_NOT_ALLOWLISTED = "E_COMMAND_NOT_ALLOWLISTED"
    E_TIMEOUT = "E_TIMEOUT"

    # Unknown / fallback
    E_UNKNOWN = "E_UNKNOWN"


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL MANIFEST — SIGNED (EVENTUALLY) INSPECTABLE METADATA PER TOOL
# ═══════════════════════════════════════════════════════════════════════════════


class ToolManifest(BaseModel):
    """
    Every tool carries a manifest describing its capabilities, risks, and requirements.

    Unsigned for now. Eventually signed with constitutional_chain_id.
    This makes the kernel inspectable — you can ask "what can this tool do?"
    and get a structured, machine-readable answer.
    """

    name: str = Field(description="Canonical tool name")
    version: str = Field(default="0.2.0", description="Manifest version")
    stage: str = Field(description="Constitutional stage code")
    lane: str = Field(default="AGI", description="Trinity lane")
    safe_modes: list[str] = Field(default_factory=list, description="Modes that are read-only")
    dangerous_modes: list[str] = Field(default_factory=list, description="Modes that mutate state")
    requires_identity: bool = Field(default=False)
    requires_state_hash: bool = Field(default=False)
    requires_approval_for: list[str] = Field(default_factory=list)
    side_effects: list[str] = Field(default_factory=list)
    max_blast_radius: str = Field(default="none", description="none | workspace | system | network")
    schema_hash: str | None = Field(default=None)
    implementation_hash: str | None = Field(default=None)


# ═══════════════════════════════════════════════════════════════════════════════
# FORGE LADDER RESULTS — STRUCTURED OUTPUTS FOR EACH RUNG
# ═══════════════════════════════════════════════════════════════════════════════


class ForgeQueryResult(BaseModel):
    """010_FORGE_QUERY: Read-only system introspection."""

    verdict: Literal["SEAL", "HOLD"] = Field(default="SEAL")
    error_code: ForgeErrorCode | None = Field(default=None)
    query: str = Field(default="")
    result: dict[str, Any] = Field(default_factory=dict)
    workspace_tree: list[dict[str, Any]] = Field(default_factory=list)
    system_state: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = Field(default=0)
    timestamp: str | None = None


class ForgePlanResult(BaseModel):
    """010_FORGE_PLAN: Action classification and blast radius estimation."""

    verdict: Literal["SEAL", "HOLD"] = Field(default="SEAL")
    error_code: ForgeErrorCode | None = Field(default=None)
    plan_id: str = Field(default="")
    goal: str = Field(default="")
    action_class: Literal["OBSERVE", "REASON", "MUTATE", "ATOMIC"] = Field(default="OBSERVE")
    risk_tier: Literal["low", "medium", "high", "critical"] = Field(default="low")
    required_approval: bool = Field(default=False)
    required_tools: list[str] = Field(default_factory=list)
    estimated_blast_radius: str = Field(default="none")
    plan: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = Field(default=0)
    timestamp: str | None = None


class ForgeDryRunResult(BaseModel):
    """010_FORGE_DRY_RUN: Simulation of planned action without mutation."""

    verdict: Literal["SEAL", "HOLD"] = Field(default="SEAL")
    error_code: ForgeErrorCode | None = Field(default=None)
    plan_id: str = Field(default="")
    dry_run: bool = Field(default=True)
    commands: list[list[str]] = Field(default_factory=list)
    files_to_create: list[str] = Field(default_factory=list)
    files_to_modify: list[str] = Field(default_factory=list)
    files_to_delete: list[str] = Field(default_factory=list)
    external_effects: list[str] = Field(default_factory=list)
    rollback_plan: list[str] = Field(default_factory=list)
    diff_preview: str = Field(default="")
    duration_ms: int = Field(default=0)
    timestamp: str | None = None


# Backward-compatible aliases
ForgeManifest2 = ForgeManifest
