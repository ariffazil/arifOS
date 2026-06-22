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
    """v2 Input Schema for arif_think"""

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
    invariant_axes: InvariantAxes | None = Field(
        default=None,
        description="25-axis invariant pass/fail from arif_think reasoning pass",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# INVARIANT AXES — 25 orthogonal invariant intelligence checks (APEX hardening)
# ═══════════════════════════════════════════════════════════════════════════════


class InvariantAxes(BaseModel):
    """
    25 orthogonal invariant intelligence axes for APEX-grade hardening.

    Each axis is a boolean: True = invariant held, False = invariant broken/unknown.
    These are orthogonal — high score on one does NOT imply high score on another.

    The 9 irreducible core invariants (compression of 25):
      1. reality_contact      — never lose world-model grounding
      2. truth_discipline      — no belief upgrade without evidence
      3. abstraction_control    — compress without hallucinating structure
      4. cross_domain_transfer — transfer structure, not surface
      5. causal_agency         — know how actions change state
      6. objective_governance   — goals change only through legitimate channels
      7. corrigible_sovereignty — remain correctable by human authority
      8. power_restraint       — capability ≠ permission
      9. recursive_safety      — self-improvement must not weaken governance

    Full 25-axis breakdown:
      ontological_reality_contact, epistemic_truth_discipline,
      cross_domain_transfer, abstraction_control, causal_agency,
      objective_stability, meta_objective_stability, corrigibility,
      sovereignty, anti_power_seeking, boundary_maintenance,
      temporal_reasoning, plasticity_stability, compositionality,
      agency_discipline, embodiment_awareness, interpretability,
      robustness, value_boundary_judgment, resource_rationality,
      self_model_accuracy, governance_persistence, moral_uncertainty,
      scalable_oversight, safe_recursive_improvement
    """

    # ── Core 9 (irreducible) ──────────────────────────────────────────────
    reality_contact: bool = Field(
        default=True,
        description="Did reasoning preserve map/territory distinction?",
    )
    truth_discipline: bool = Field(
        default=True,
        description="Did no claim upgrade from hypothesis to fact without evidence?",
    )
    abstraction_control: bool = Field(
        default=True,
        description="Did abstraction preserve re-grounding paths to concrete examples?",
    )
    cross_domain_transfer: bool = Field(
        default=True,
        description="Did domain transfer preserve structure, not just vocabulary?",
    )
    causal_agency: bool = Field(
        default=True,
        description="Was causal lever identified before action?",
    )
    objective_governance: bool = Field(
        default=True,
        description="Did local objective remain subordinate to higher constraints?",
    )
    corrigible_sovereignty: bool = Field(
        default=True,
        description="Did system accept correction without resistance?",
    )
    power_restraint: bool = Field(
        default=True,
        description="Did more capability NOT imply more permission?",
    )
    recursive_safety: bool = Field(
        default=True,
        description="Did self-improvement preserve governance invariants?",
    )

    # ── Supporting 16 ───────────────────────────────────────────────────
    epistemic_truth_discipline: bool = Field(
        default=True,
        description="Was uncertainty declared rather than disguised as certainty?",
    )
    cross_domain_transfer: bool = Field(
        default=True,
        description="Was structure preserved across domain analogy?",
    )
    abstraction_control: bool = Field(
        default=True,
        description="Were abstraction boundaries maintained?",
    )
    objective_stability: bool = Field(
        default=True,
        description="Did objective remain stable within this reasoning pass?",
    )
    meta_objective_stability: bool = Field(
        default=True,
        description="Did rules for changing goals remain unchanged?",
    )
    boundary_maintenance: bool = Field(
        default=True,
        description="Were self/user/tool/memory/simulation boundaries preserved?",
    )
    temporal_reasoning: bool = Field(
        default=True,
        description="Were timestamps, expiry, and freshness considered?",
    )
    plasticity_stability: bool = Field(
        default=True,
        description="Was new information integrated without destroying valid structure?",
    )
    compositionality: bool = Field(
        default=True,
        description="Did composed actions preserve permissions and audit across modules?",
    )
    agency_discipline: bool = Field(
        default=True,
        description="Was state-change predicted before each action?",
    )
    embodiment_awareness: bool = Field(
        default=True,
        description="Was each tool call treated as causal world intervention?",
    )
    interpretability: bool = Field(
        default=True,
        description="Was consequential output traceable to human-understandable reasoning?",
    )
    robustness: bool = Field(
        default=True,
        description="Did output remain valid under noise, adversarial input, distribution shift?",
    )
    value_boundary_judgment: bool = Field(
        default=True,
        description="Was user preference distinguished from moral/safety/legal constraint?",
    )
    resource_rationality: bool = Field(
        default=True,
        description="Were compute, time, and opportunity costs bounded?",
    )
    self_model_accuracy: bool = Field(
        default=True,
        description="Did system correctly identify its own capabilities and limitations?",
    )
    governance_persistence: bool = Field(
        default=True,
        description="Did constitutional governance remain active across domain shifts?",
    )
    moral_uncertainty: bool = Field(
        default=True,
        description="Was unresolved moral uncertainty preserved rather than collapsed?",
    )
    scalable_oversight: bool = Field(
        default=True,
        description="Did the system help humans supervise it without self-judging?",
    )


class MindResponse(BaseModel):
    """v2 Output Schema for arif_think"""

    status: Literal["OK", "HOLD", "VOID"] = "OK"
    tool: str = "arif_think"
    mode: str = "metabolize"
    session_id: str | None = None
    actor_id: str | None = None
    trace_id: str | None = None
    mind_packet: MindPacket
    governance: MindGovernance = Field(default_factory=MindGovernance)
