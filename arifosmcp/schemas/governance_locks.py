"""
Governance Lock Schemas — Three Deep Locks
═══════════════════════════════════════════════════════════════════════════════

1. Gödel Lock      → prevents self-certifying certainty
2. Strange Loop    → governs recursive self-reference with provenance
3. Anti-Beautiful-One → prevents sterile polished collapse

Ratified: 2026-06-03
Authority: L13 SOVEREIGN

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class LockType(StrEnum):
    GODEL = "godel_lock"
    STRANGE_LOOP = "strange_loop_lock"
    ANTI_BEAUTIFUL_ONE = "anti_beautiful_one"
    PARADOX_HOLD = "paradox_hold"


class LockVerdict(StrEnum):
    SEAL = "SEAL"
    HOLD = "HOLD"
    VOID = "VOID"


class ProvenanceLabel(StrEnum):
    CLAIMED = "claimed"
    OBSERVED = "observed"
    INFERRED = "inferred"
    VERIFIED = "verified"
    SEALED = "sealed"
    REVOKED = "revoked"
    STALE = "stale"
    CONTRADICTED = "contradicted"


class SelfClaimCategory(StrEnum):
    SAFETY = "safety"
    AUTHORITY = "authority"
    CONSCIOUSNESS = "consciousness"
    TRUTH = "truth"
    COMPLIANCE = "compliance"
    MEMORY = "memory"


class MemoryLayer(StrEnum):
    L1_LIVE_CONTEXT = "L1_live_context"
    L2_SESSION = "L2_session_summary"
    L3_QDRANT = "L3_qdrant_associative"
    L4_SUPABASE = "L4_supabase_relational"
    L5_GRAPH = "L5_falkordb_graph"
    L6_VAULT = "L6_vault999_immutable"


# ═══════════════════════════════════════════════════════════════════════════════
# GÖDEL LOCK
# ═══════════════════════════════════════════════════════════════════════════════


class GodelLockClaim(BaseModel):
    """A claim that triggers Gödel Lock scrutiny."""

    category: SelfClaimCategory = Field(description="What the system claims about itself")
    claim_text: str = Field(description="The literal self-claim")
    actor_id: str = Field(description="Agent making the claim")
    session_id: str | None = Field(default=None)


class GodelLockReceipt(BaseModel):
    """Receipt after applying the Gödel Lock."""

    lock_type: LockType = LockType.GODEL
    verdict: LockVerdict
    reason: str
    external_witness_present: bool = False
    witness_type: str | None = Field(default=None)
    vault_entry_id: str | None = Field(default=None)
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# STRANGE LOOP LOCK
# ═══════════════════════════════════════════════════════════════════════════════


class MemoryProvenance(BaseModel):
    """Provenance required for every memory entry in a recursive loop."""

    source: str = Field(description="Origin of the memory")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    confidence: float = Field(ge=0.0, le=1.0, description="Epistemic confidence 0.0–1.0")
    authority_status: str = Field(description="Who authorized this memory")
    revocation_path: str | None = Field(default=None, description="How to revoke if contradicted")
    label: ProvenanceLabel = Field(default=ProvenanceLabel.CLAIMED)
    layer: MemoryLayer = Field(default=MemoryLayer.L1_LIVE_CONTEXT)


class StrangeLoopReceipt(BaseModel):
    """Receipt after applying the Strange Loop Lock."""

    lock_type: LockType = LockType.STRANGE_LOOP
    verdict: LockVerdict
    reason: str
    memory_id: str | None = None
    provenance_label: ProvenanceLabel | None = None
    loop_depth: int = Field(ge=0, default=0)
    last_verified_at: str | None = None
    confidence_delta: float = Field(default=0.0)
    revocation_status: str = Field(default="active")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# ANTI-BEAUTIFUL-ONE
# ═══════════════════════════════════════════════════════════════════════════════


class AntiBeautifulOneMetrics(BaseModel):
    """Metrics that detect sterile polished collapse."""

    operational_contact_score: float = Field(ge=0.0, le=1.0, default=0.0)
    human_cost_detected: bool = False
    survival_status: str = Field(default="unknown")
    reality_evidence_present: bool = False
    contradiction_challenged: bool = False
    beauty_to_consequence_ratio: float = Field(
        ge=0.0,
        default=1.0,
        description=">1.0 means more style than consequence (danger)",
    )


class AntiBeautifulOneReceipt(BaseModel):
    """Receipt after applying the Anti-Beautiful-One Lock."""

    lock_type: LockType = LockType.ANTI_BEAUTIFUL_ONE
    verdict: LockVerdict
    reason: str
    metrics: AntiBeautifulOneMetrics = Field(default_factory=AntiBeautifulOneMetrics)
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# PARADOX HOLD
# ═══════════════════════════════════════════════════════════════════════════════


class ParadoxHoldReceipt(BaseModel):
    """
    Receipt representing a productive paradox — two verified claims
    that conflict, and the system chooses to preserve the tension
    rather than force a false resolution.

    L02 TRUTH: Both claims must be independently verified.
    L08 GENIUS: The paradox itself carries intelligence value.
    """

    lock_type: LockType = LockType.PARADOX_HOLD
    verdict: LockVerdict = LockVerdict.HOLD
    claim_a: str = Field(description="First verified claim")
    claim_b: str = Field(description="Second verified claim, in tension with claim_a")
    conflict_description: str = Field(description="Why these two claims are in conflict")
    both_verified: bool = Field(
        default=True, description="Both claims passed F2 TRUTH verification"
    )
    resolution_attempted: bool = Field(
        default=False,
        description="We deliberately did NOT attempt forced resolution — paradox is preserved",
    )
    preserved_until: datetime | None = Field(
        default=None, description="Optional expiry after which re-evaluation is triggered"
    )
    reason: str = Field(
        default="Two verified truths conflict. Paradox is preserved, not resolved.",
        description="Human-readable reason for the paradox hold",
    )
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED RECEIPT
# ═══════════════════════════════════════════════════════════════════════════════


class LockReceipt(BaseModel):
    """Single lock receipt, polymorphic by lock_type."""

    lock_type: LockType
    verdict: LockVerdict
    reason: str
    payload: (
        GodelLockReceipt | StrangeLoopReceipt | AntiBeautifulOneReceipt | ParadoxHoldReceipt | None
    ) = None


class UnifiedGovernanceReceipt(BaseModel):
    """
    Unified receipt carried on every MCP call.

    Composite verdict rule: strictest wins.
      VOID > HOLD > SEAL

    PARADOX_HOLD: Both claims verified under F2 but they conflict.
      Composite verdict becomes HOLD — neither claim is discarded.
    """

    version: str = Field(default="2026.06.03-v1")
    session_id: str | None = None
    actor_id: str | None = None
    locks_applied: list[LockType] = Field(default_factory=list)
    lock_receipts: list[LockReceipt] = Field(default_factory=list)
    composite_verdict: LockVerdict = Field(default=LockVerdict.SEAL)
    sealed_by: str | None = Field(default=None, description="VAULT999 hash if SEAL")
    paradox_hold: ParadoxHoldReceipt | None = Field(
        default=None,
        description="Active paradox hold — two verified truths in productive tension",
    )
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    @model_validator(mode="after")
    def compute_composite_verdict(self) -> UnifiedGovernanceReceipt:
        # If a paradox hold is active, both claims are held
        if self.paradox_hold is not None:
            self.composite_verdict = LockVerdict.HOLD

        if not self.lock_receipts:
            if self.paradox_hold is None:
                self.composite_verdict = LockVerdict.SEAL
            return self

        verdicts = [r.verdict for r in self.lock_receipts]
        if LockVerdict.VOID in verdicts:
            self.composite_verdict = LockVerdict.VOID
        elif LockVerdict.HOLD in verdicts:
            self.composite_verdict = LockVerdict.HOLD
        else:
            # Only SEAL if no paradox hold AND no other blocks
            if self.paradox_hold is None:
                self.composite_verdict = LockVerdict.SEAL
        return self

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
