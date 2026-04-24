"""
arifOS Forge Output Schemas — 010_FORGE
══════════════════════════════════════════════════════════════════════════════

Phase 2 Civilization Intelligence — ForgeOutput for arif_forge_execute.
Forged irreversibly: delta_S, irreversibility bond, manifest, execution trace.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from arifosmcp.schemas.lineage import JudgeSealContract


# ═══════════════════════════════════════════════════════════════════════════════
# FORGE ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class IrreversibilityLevel(str, Enum):
    """How irreversible is this forge action?"""
    REVERSIBLE = "reversible"
    SEMI_IRREVERSIBLE = "semi_irreversible"
    IRREVERSIBLE = "irreversible"
    CATASTROPHIC = "catastrophic"


class ManifestStatus(str, Enum):
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
        description="How irreversible is this action?"
    )
    delta_S: float = Field(
        default=0.0,
        description="Entropy change (J/K). Positive = heat to environment."
    )
    landauer_cost_joules: float | None = Field(
        default=None,
        description="Landauer bound: k_B * T * ln(2) * bits_flipped"
    )
    compensation_required: bool = Field(
        default=False,
        description="Does this action require compensation entropy?"
    )
    rollback_possible: bool = Field(
        default=True,
        description="Can this action be theoretically rolled back?"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DELTA S EVIDENCE — THERMODYNAMIC FOOTPRINT
# ═══════════════════════════════════════════════════════════════════════════════

class DeltaSEvidence(BaseModel):
    """
    Thermodynamic evidence for forge action.
    Tracks entropy production across the execution.

    Fields affect behavior:
    - delta_S_net determines if action is allowed (F13 entropy budget)
    - energy_cost determines if system can afford the action
    """
    delta_S_positive: float = Field(
        default=0.0,
        description="Entropy produced (heat to environment)"
    )
    delta_S_negative: float = Field(
        default=0.0,
        description="Entropy absorbed (cooling)"
    )
    delta_S_net: float = Field(
        default=0.0,
        description="Net entropy change"
    )
    energy_cost_joules: float | None = Field(
        default=None,
        description="Direct energy cost"
    )
    landauer_optimal: bool = Field(
        default=True,
        description="Is action within Landauer bound?"
    )
    entropy_budget_remaining: float | None = Field(
        default=None,
        description="F13 entropy budget remaining"
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
# CONSTITUTIONAL COMPLIANCE — F1-F13 CHECK RESULTS
# ═══════════════════════════════════════════════════════════════════════════════

class ConstitutionalCompliance(BaseModel):
    """F1-F13 floor compliance for this forge action."""
    floors_invoked: list[str] = Field(default_factory=list)
    floor_results: dict[str, str] = Field(default_factory=dict)
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
    - delta_S_evidence: determines if F13 entropy budget allows action
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
        description="Thermodynamic irreversibility assessment"
    )

    # Entropy
    delta_S_evidence: DeltaSEvidence = Field(
        default_factory=DeltaSEvidence,
        description="Entropy production evidence"
    )

    # Constitutional compliance
    constitutional_compliance: ConstitutionalCompliance = Field(
        default_factory=ConstitutionalCompliance,
        description="F1-F13 floor compliance"
    )

    # Execution trace
    execution_trace: ExecutionTrace = Field(
        default_factory=ExecutionTrace,
        description="Step-by-step execution record"
    )

    # Acknowledgment
    ack_irreversible_received: bool = Field(
        default=False,
        description="Did actor acknowledge irreversibility?"
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
