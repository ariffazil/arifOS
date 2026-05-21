"""
arifosmcp/schemas/claim.py — Shared Claim Protocol (SCP v1.0)
════════════════════════════════════════════════════════════

Canonical data structure for domain witnesses (GEOX, WEALTH, WELL).
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class UncertaintyClass(StrEnum):
    FACT = "FACT"
    ESTIMATE = "ESTIMATE"
    SPECULATION = "SPECULATION"


class RiskPotential(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DomainWitness(StrEnum):
    GEOX = "GEOX"
    WEALTH = "WEALTH"
    WELL = "WELL"
    ARIFOS = "arifOS"


class ClaimPolarity(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    UNCERTAIN = "uncertain"


class EpistemicEventType(StrEnum):
    ASSERTION = "assertion"
    VERIFICATION = "verification"
    WITNESS = "witness"
    DECISION = "decision"
    OUTCOME = "outcome"
    RETRACTION = "retraction"
    SEAL = "seal"


class AuthorityClass(StrEnum):
    GROUND_EVIDENCE = "ground_evidence"
    CAPITAL_ANALYSIS = "capital_analysis"
    DELIBERATIVE_JUDGMENT = "deliberative_judgment"
    GOVERNANCE_CONTROL = "governance_control"
    HUMAN_SUBSTRATE = "human_substrate"
    EXECUTION_REALITY = "execution_reality"
    OPS_TELEMETRY = "ops_telemetry"
    MEMORY_LINEAGE = "memory_lineage"


class Uncertainty(BaseModel):
    uncertainty_class: UncertaintyClass = Field(..., alias="class")
    confidence: float = Field(..., ge=0.0, le=1.0)


class Risk(BaseModel):
    reversible: bool
    harm_potential: RiskPotential
    human_decision_required: bool


class Authority(BaseModel):
    ai_decides: bool
    final_authority: str = "ARIF"


class GovernedClaim(BaseModel):
    claim: str
    domain: DomainWitness
    evidence: list[str] = []
    uncertainty: Uncertainty
    risk: Risk
    authority: Authority
    next_safe_action: str

    class Config:
        populate_by_name = True


class FederationEpistemicEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    subject_id: str
    subject_name: str | None = None
    claim_id: str
    claim_text: str
    predicate: str
    object_value: str = ""
    event_type: EpistemicEventType = EpistemicEventType.ASSERTION
    polarity: ClaimPolarity = ClaimPolarity.SUPPORTS
    node_id: str
    agent_role: str
    domain: str = "federation"
    authority_class: AuthorityClass = AuthorityClass.MEMORY_LINEAGE
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence_refs: list[str] = Field(default_factory=list)
    supporting_claim_ids: list[str] = Field(default_factory=list)
    contradicting_claim_ids: list[str] = Field(default_factory=list)
    decision_refs: list[str] = Field(default_factory=list)
    outcome_refs: list[str] = Field(default_factory=list)
    witness_required: bool = False
    claim_status: str = "proposed"
    seal_level: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class FederationBeliefQuery(BaseModel):
    query: str | None = None
    subject_id: str | None = None
    claim_id: str | None = None
    include_events: bool = False
    include_lineage: bool = True
