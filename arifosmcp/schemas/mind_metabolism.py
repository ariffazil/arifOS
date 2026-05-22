"""
arifOS Mind Metabolism Schemas — 333_MIND v2
════════════════════════════════════════════

Cognitive Metabolism Kernel (Arif Verdict 2026-05-20)
────────────────────────────────────────────────────

Transform evidence into structured understanding without pretending to be final truth.
Core triad: Abstraction, Attestation, Abduction.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# INPUT SCHEMA (v2)
# ═══════════════════════════════════════════════════════════════════════════════


class MindIntent(StrEnum):
    EXPLAIN = "explain"
    VERIFY = "verify"
    PLAN = "plan"
    COMPARE = "compare"
    ABDUCT = "abduct"
    SYNTHESIZE = "synthesize"
    CRITIQUE = "critique"
    DECIDE_NEXT = "decide_next_observation"
    METABOLIZE = "metabolize"


class DecisionClass(StrEnum):
    C0 = "C0"
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"
    C5 = "C5"


class RiskTier(StrEnum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"
    CRITICAL = "critical"


class TaskConfig(BaseModel):
    intent: MindIntent = Field(default=MindIntent.METABOLIZE)
    decision_class: DecisionClass = Field(default=DecisionClass.C0)
    risk_tier: RiskTier = Field(default=RiskTier.GREEN)
    domain: str = Field(default="general")
    freshness_need: str = Field(default="medium")


class MindContext(BaseModel):
    user_context: str | None = None
    memory_context: list[str] = Field(default_factory=list)
    background_field: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    known_unknowns: list[str] = Field(default_factory=list)


class MindEvidence(BaseModel):
    search_decision_receipts: list[str] = Field(default_factory=list)
    source_cards: list[dict[str, Any]] = Field(default_factory=list)
    evidence_receipts: list[dict[str, Any]] = Field(default_factory=list)
    claim_cards: list[dict[str, Any]] = Field(default_factory=list)
    contradiction_reports: list[dict[str, Any]] = Field(default_factory=list)


class ReasoningControl(BaseModel):
    depth: int = Field(default=3, ge=1, le=10)
    max_layers: int = Field(default=7, ge=1, le=15)
    sequential_mode: str = Field(default="deliberate")  # fast | deliberate | exhaustive
    allow_abduction: bool = True
    allow_counterfactuals: bool = False
    require_attestation: bool = True
    require_contradiction_scan: bool = True
    confidence_threshold: float = 0.75
    stop_on_sufficient_clarity: bool = True


class OutputContract(BaseModel):
    format: str = "mind_packet_v2"
    include_metabolized_context: bool = True
    include_abstractions: bool = True
    include_abductions: bool = True
    include_attestations: bool = True
    include_next_actions: bool = True


class MindRequest(BaseModel):
    """v2 Input Schema for arif_mind_reason"""

    query: str
    mode: str = "metabolize"
    session_id: str | None = None
    actor_id: str | None = None
    task: TaskConfig = Field(default_factory=TaskConfig)
    context: MindContext = Field(default_factory=MindContext)
    evidence: MindEvidence = Field(default_factory=MindEvidence)
    reasoning_control: ReasoningControl = Field(default_factory=ReasoningControl)
    output_contract: OutputContract = Field(default_factory=OutputContract)


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT SCHEMA (v2)
# ═══════════════════════════════════════════════════════════════════════════════


class MetabolizedContext(BaseModel):
    input_summary: str
    core_problem: str
    why_it_matters: str
    decision_pressure: str = "medium"
    background_field: list[str] = Field(default_factory=list)
    known_unknowns: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)


class AbstractionCard(BaseModel):
    name: str
    type: str  # concept | object | process | constraint | metric | relation
    definition: str
    source: str  # input | evidence | memory | inference
    confidence: float = 0.0


class AttestationCard(BaseModel):
    claim_id: str
    claim: str
    evidence_level: str  # L0-L5
    source_ids: list[str] = Field(default_factory=list)
    receipt_ids: list[str] = Field(default_factory=list)
    content_hashes: list[str] = Field(default_factory=list)
    attestation_status: str = "unattested"
    allowed_language_strength: str = "unknown"


class AbductiveHypothesis(BaseModel):
    hypothesis: str
    explains: list[str] = Field(default_factory=list)
    does_not_explain: list[str] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    falsification_tests: list[str] = Field(default_factory=list)
    next_observation: str | None = None
    confidence: float = 0.0
    status: str = "hypothesis"


class CognitiveLayer(BaseModel):
    layer: int
    name: str
    operation: str
    input_refs: list[str] = Field(default_factory=list)
    output: str
    confidence_before: float = 0.0
    confidence_after: float = 0.0
    delta_confidence: float = 0.0
    delta_entropy: float = 0.0
    risk_flags: list[str] = Field(default_factory=list)


class ContradictionReport(BaseModel):
    claim_a: str
    claim_b: str
    source_a: str
    source_b: str
    conflict_type: str
    resolution: str
    preferred_source: str | None = None
    reason: str | None = None


class MindSynthesis(BaseModel):
    bounded_answer: str
    what_is_supported: list[str] = Field(default_factory=list)
    what_is_not_supported: list[str] = Field(default_factory=list)
    what_remains_unknown: list[str] = Field(default_factory=list)
    confidence: dict[str, float] = Field(
        default_factory=lambda: {
            "reasoning_confidence": 0.0,
            "evidence_confidence": 0.0,
            "overall_confidence": 0.0,
        }
    )


class NextAction(BaseModel):
    tool: str
    mode: str
    reason: str
    required: bool = True


class MindPacket(BaseModel):
    query: str
    intent: str
    claim_state: str = "unknown"
    reasoning_mode: str = "mixed"
    metabolized_context: MetabolizedContext | None = None
    abstractions: list[AbstractionCard] = Field(default_factory=list)
    attestations: list[AttestationCard] = Field(default_factory=list)
    abductions: list[AbductiveHypothesis] = Field(default_factory=list)
    sequential_layers: list[CognitiveLayer] = Field(default_factory=list)
    contradictions: list[ContradictionReport] = Field(default_factory=list)
    synthesis: MindSynthesis | None = None
    next_actions: list[NextAction] = Field(default_factory=list)


class MindGovernance(BaseModel):
    axioms_used: list[str] = Field(default_factory=list)
    floors_checked: list[str] = Field(default_factory=list)
    claim_strength_violations: list[str] = Field(default_factory=list)
    human_judgment_required: bool = False
    verdict: str = "HOLD"


class MindResponse(BaseModel):
    """v2 Output Schema for arif_mind_reason"""

    status: Literal["OK", "HOLD", "VOID"] = "OK"
    tool: str = "arif_mind_reason"
    mode: str = "metabolize"
    session_id: str | None = None
    actor_id: str | None = None
    trace_id: str | None = None
    mind_packet: MindPacket
    governance: MindGovernance = Field(default_factory=MindGovernance)
