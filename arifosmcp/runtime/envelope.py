"""
envelope.py

AGI Mind Pipeline — Typed Cognitive Architecture
Constitutional Principle: Internal richness, external compression.

Pipeline: sense → mind → heart → judge → forge → vault

Each stage returns a small typed object, not free-form text.
Wide internal cognition + narrow external envelopes.
Hypothesis + falsification + provenance are mandatory.
Decision packet is SEPARATE from audit packet.
Output is hard-limited by entropy budget.

DITEMPA BUKAN DIBERI — Forged, Not Given [ΔΩΨ | ARIF]
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE CONSTANTS — ENTROPY BUDGET
# ═══════════════════════════════════════════════════════════════════════════════

AGI_PIPELINE = ["sense", "mind", "heart", "judge", "forge", "vault"]

MAX_FACTS = 3
MAX_UNKNOWNS = 3
MAX_OPTIONS = 3

# Constitutional floor: machine cannot do these — ever
PROHIBITED_MACHINE_ACTIONS = frozenset(
    {
        "assign_intrinsic_value",
        "claim_human_equivalence",
        "authorize_irreversible_action",
        "claim_embodied_meaning",
        "override_human_judgment",
        "grant_sovereign_authority",
    }
)


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER A — INTERNAL COGNITIVE STATE (wide, rich)
# ═══════════════════════════════════════════════════════════════════════════════


class Hypothesis(BaseModel):
    """A single falsifiable claim with evidence tracking."""

    id: str
    claim: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_for: list[str] = Field(default_factory=list)
    evidence_against: list[str] = Field(default_factory=list)
    falsifier: str  # Mandatory — F2 Truth
    disconfirming_test: str = ""  # What experiment would rule this out?

    model_config = {"frozen": False}


class Provenance(BaseModel):
    """
    Required disclosure fields — compact, always visible.

    These are the epistemic boundary markers: what kind of intelligence
    produced this output, and what it cannot claim.
    """

    intelligence_type: Literal["statistical", "embodied", "hybrid"] = "statistical"
    grounding_status: Literal["data-based", "sensor-based", "human-mediated", "ungrounded"] = (
        "human-mediated"
    )
    actor_id: str = "anonymous"  # Ψ-Continuity: canonical identity
    verified_actor_id: str | None = None
    stakes_model: Literal["none", "simulated", "externalized-to-human", "shared"] = (
        "externalized-to-human"
    )
    confidence_domain: Literal[
        "narrow-task", "broad-context", "ambiguous", "human-judgment-required"
    ] = "ambiguous"
    meaning_source: Literal["human-attributed", "statistical-inference", "ungrounded"] = (
        "statistical-inference"
    )
    human_equivalence_claimed: bool = False  # F9/F13: must remain False


class MindState(BaseModel):
    """
    Internal cognitive state — WIDE.

    May contain observations, candidate models, contradictions, unknowns,
    risk flags, provenance, audit trail, and alternative plans.
    This is never sent directly to the operator.
    """

    objective: str
    facts: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    decision_required: bool = False
    provenance: Provenance = Field(default_factory=Provenance)
    # Audit trail
    session_id: str = Field(default_factory=lambda: f"ms_{uuid.uuid4().hex[:12]}")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    pipeline_trace: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER B — OUTPUT ENVELOPE (narrow, decisive)
# ═══════════════════════════════════════════════════════════════════════════════


class OutputEnvelope(BaseModel):
    """
    External output — NARROW.

    Answers only:
      - what is happening?          → summary
      - what matters now?           → key_facts
      - what is uncertain?          → key_uncertainties
      - what are the options?       → options
      - what is the next step?      → next_step
      - what requires human judgment? → human_decision_required

    Hard limits: 3 facts, 3 uncertainties, 3 options, 1 next_step.
    """

    summary: str
    status: Literal["OK", "PARTIAL", "HOLD", "ERROR"]
    key_facts: list[str]  # max MAX_FACTS
    key_uncertainties: list[str]  # max MAX_UNKNOWNS
    options: list[str]  # max MAX_OPTIONS
    next_step: str  # exactly 1
    human_decision_required: bool
    provenance: Provenance
    chaos_score: float = 0.0  # Ω-Stability: entropy metric
    peace2: float = 1.0  # Ω-Stability: stability index
    g_star: float = 0.0  # Δ-Intelligence: epistemic quality (G*T*C)^1/3
    omega_0: float = 0.05  # Δ-Intelligence: Humility band (Gödel uncertainty)


# ═══════════════════════════════════════════════════════════════════════════════
# RUNTIME STATE — internal full state for audit
# ═══════════════════════════════════════════════════════════════════════════════


class RuntimeState(BaseModel):
    """Full internal runtime state — for vault and replay. Never send to operator."""

    sense: dict[str, Any] = Field(default_factory=dict)
    mind: MindState | None = None
    heart_risks: list[str] = Field(default_factory=list)
    peace2: float = 1.0
    g_star: float = 0.0
    omega_0: float = 0.05
    judge_status: str = "PENDING"
    judge_violations: list[str] = Field(default_factory=list)
    chaos_score: float = 0.0
    audit: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# SOVEREIGN BOUNDARY GUARD — F9, F13
# ═══════════════════════════════════════════════════════════════════════════════


def boundary_guard(action: str) -> None:
    """
    F13 Sovereign + F9 Anti-Hantu enforcement.

    Machine cannot assign value, claim equivalence, authorize irreversible
    actions, or override human judgment. Hard stop — raises PermissionError.
    """
    if action in PROHIBITED_MACHINE_ACTIONS:
        raise PermissionError(
            f"SOVEREIGN BOUNDARY VIOLATION (F9/F13): '{action}' is prohibited. "
            "Human authority is required for this class of action."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FALSIFICATION ENFORCEMENT — F2 Truth
# ═══════════════════════════════════════════════════════════════════════════════


def require_falsification(hypotheses: list[Hypothesis]) -> None:
    """
    F2 Truth: Every hypothesis must carry a falsifier.

    Raises ValueError if any hypothesis is missing its falsifier.
    No result can ship without at least one falsifiable claim.
    """
    for h in hypotheses:
        if not h.falsifier.strip():
            raise ValueError(
                f"F2 TRUTH VIOLATION: Hypothesis {h.id!r} has no falsifier. "
                "All claims must be falsifiable before dispatch."
            )


# ═══════════════════════════════════════════════════════════════════════════════
# CHAOS SCORE — ENTROPY GATE
# ═══════════════════════════════════════════════════════════════════════════════


def chaos_score(state: MindState) -> float:
    """
    Compute entropy score from internal mind state and thermodynamic budget.

    Task Ω1: Bind to real thermodynamic signal if available.
    """
    # 1. Cognitive chaos (base)
    score = 0.0
    score += len(state.assumptions) * 0.2
    score += len(state.unknowns) * 0.3
    score += len(state.contradictions) * 0.5
    score += max(0, len(state.hypotheses) - 2) * 0.1

    # 2. Thermodynamic stress (Task Ω1: Real chaos_score binding)
    try:
        from arifosmcp.runtime.substrate_policy import get_thermodynamic_budget
        budget = get_thermodynamic_budget(state.session_id)
        thermo_score = budget.calculate_chaos_score()
        score += thermo_score
    except Exception:
        pass

    return round(score, 2)


def calculate_peace2(risks: list[str]) -> float:
    """
    Task Ω2: Peace² (Stability Index)
    Formula: peace2 = 1 / (1 + total_risk)
    """
    if not risks:
        return 1.0
    total_risk = len(risks) * 0.25
    return round(1.0 / (1.0 + total_risk), 2)


def calculate_g_star(state: MindState) -> float:
    """
    Task Δ4: G★ implementation
    Formula: G_star = (grounding * truth * coherence) ** (1/3)
    """
    g = min(1.0, len(state.facts) * 0.3)
    if state.provenance.grounding_status == "sensor-based":
        g = max(g, 0.8)
    elif state.provenance.grounding_status == "data-based":
        g = max(g, 0.6)

    if not state.hypotheses:
        t = 0.0
    else:
        t = max(h.confidence for h in state.hypotheses)

    c = 1.0 - (min(1.0, len(state.contradictions) * 0.4 + len(state.unknowns) * 0.2))

    g_star = (g * t * c) ** (1 / 3)
    return round(g_star, 2)


def calculate_omega_0(state: MindState) -> float:
    """
    Task Δ5: Gödel Lock (Humility Band)
    Formula: omega_0 = max(0.03, 1.0 - max_confidence)
    """
    if not state.hypotheses:
        return 1.0

    max_confidence = max(h.confidence for h in state.hypotheses)
    return round(max(0.03, 1.0 - max_confidence), 3)


def output_mode_from_chaos(score: float) -> Literal["OK", "PARTIAL", "HOLD"]:
    if score < 1.0:
        return "OK"
    if score < 2.0:
        return "PARTIAL"
    return "HOLD"


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE STAGE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def sense_stage(raw_input: str) -> dict[str, Any]:
    """Stage 1: Input chaos → grounded facts."""
    return {
        "objective": raw_input,
        "facts": [],
        "assumptions": [
            "Input is honest and complete as provided.",
            "No hidden context has been omitted by the requester.",
        ],
        "unknowns": [
            "Causal structure of the problem is unverified.",
            "External constraints not declared in the input.",
        ],
    }


def mind_stage(
    sense_packet: dict[str, Any],
    additional_context: str = "",
) -> list[Hypothesis]:
    """Stage 2: Grounded facts → structured hypotheses."""
    objective = sense_packet.get("objective", "")
    facts = sense_packet.get("facts", [])

    if facts:
        hypotheses = []
        hypotheses.append(
            Hypothesis(
                id="H1-DIRECT",
                claim=f"Direct Model: Based on evidence '{facts[0][:60]}...', the objective '{objective[:40]}' is achievable.",
                confidence=0.75,
                evidence_for=[facts[0]],
                falsifier=f"Evidence {facts[0][:30]} is proven stale.",
                disconfirming_test="Attempt to achieve objective while ignoring facts.",
            )
        )
        return hypotheses

    short_obj = objective[:100] if len(objective) > 100 else objective
    context_note = f" (context: {additional_context[:60]})" if additional_context else ""

    return [
        Hypothesis(
            id="H1-CAUSAL",
            claim=f"Primary Causal Model: {short_obj}{context_note}.",
            confidence=0.65,
            evidence_for=["Structural alignment"],
            falsifier=f"Discovery that objective contains category error.",
            disconfirming_test="Invert assumption.",
        ),
        Hypothesis(
            id="H2-EPISTEMIC",
            claim=f"Epistemic Alternative: Objective is symptom of misalignment.",
            confidence=0.35,
            falsifier="Proof that grounding is complete.",
            disconfirming_test="Search for prerequisites.",
        ),
    ]


def heart_stage(hypotheses: list[Hypothesis]) -> list[str]:
    """Stage 3: Simulate consequences."""
    risks: list[str] = []
    for h in hypotheses:
        risks.append(f"[{h.id}] Risk: false confidence. Falsifier: {h.falsifier[:80]}")
    return risks


def judge_stage(state: MindState) -> tuple[str, list[str]]:
    """Stage 4: Constitutional gate."""
    violations: list[str] = []

    if not state.hypotheses or len(state.hypotheses) < 2:
        violations.append("F2 violation: fewer than 2 hypotheses.")

    for h in state.hypotheses:
        if not h.falsifier.strip():
            violations.append(f"F2 violation: Hypothesis {h.id!r} missing falsifier.")
        if h.confidence > 0.97:
            violations.append(f"F7 violation: Absolute certainty (>0.97) prohibited.")

    if state.provenance.human_equivalence_claimed:
        violations.append("F9/F13 violation: human_equivalence_claimed is prohibited.")

    score = chaos_score(state)
    if score >= 2.0 and not state.decision_required:
        violations.append(f"F1 advisory: chaos_score={score} ≥ 2.0 — HOLD required.")

    return ("HOLD" if violations else "OK"), violations


def compress_for_operator(state: MindState) -> OutputEnvelope:
    """Compress wide internal MindState into narrow OutputEnvelope."""
    top_hypotheses = sorted(state.hypotheses, key=lambda h: h.confidence, reverse=True)[:MAX_OPTIONS]
    options = [h.claim for h in top_hypotheses]
    summary = top_hypotheses[0].claim if top_hypotheses else "No stable hypothesis."

    score = chaos_score(state)
    peace2 = calculate_peace2(state.risks)
    g_star = calculate_g_star(state)
    omega_0 = calculate_omega_0(state)

    if state.decision_required or score >= 2.0 or peace2 < 1.0 or g_star < 0.3:
        status: Literal["OK", "PARTIAL", "HOLD", "ERROR"] = "HOLD"
    elif state.unknowns or score >= 1.0 or g_star < 0.5:
        status = "PARTIAL"
    else:
        status = "OK"

    next_step = "Human judgment required." if state.decision_required else "Proceed with falsification."

    return OutputEnvelope(
        summary=summary,
        status=status,
        key_facts=state.facts[:MAX_FACTS],
        key_uncertainties=state.unknowns[:MAX_UNKNOWNS],
        options=options[:MAX_OPTIONS],
        next_step=next_step,
        human_decision_required=state.decision_required,
        provenance=state.provenance,
        chaos_score=score,
        peace2=peace2,
        g_star=g_star,
        omega_0=omega_0,
    )


def build_decision_packet(envelope: OutputEnvelope, session_id: str) -> dict[str, Any]:
    return {
        "status": envelope.status,
        "summary": envelope.summary,
        "facts": envelope.key_facts,
        "uncertainties": envelope.key_uncertainties,
        "options": envelope.options,
        "next_step": envelope.next_step,
        "human_decision_required": envelope.human_decision_required,
        "metrics": {
            "chaos": envelope.chaos_score,
            "peace2": envelope.peace2,
            "g_star": envelope.g_star,
            "omega_0": envelope.omega_0,
        },
        "provenance": envelope.provenance.model_dump(),
        "_session": session_id,
    }


def build_audit_packet(
    raw_input: str,
    runtime_state: RuntimeState,
    envelope: OutputEnvelope,
    session_id: str,
) -> dict[str, Any]:
    mind = runtime_state.mind
    return {
        "raw_input": raw_input,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hypotheses": ([h.model_dump() for h in mind.hypotheses] if mind else []),
        "violations": runtime_state.judge_violations,
        "chaos_score": runtime_state.chaos_score,
        "output_status": envelope.status,
    }


async def run_agi_mind(
    raw_input: str,
    session_id: str | None = None,
    additional_context: str = "",
    provenance: Provenance | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _session_id = session_id or f"agi_{uuid.uuid4().hex[:12]}"
    _provenance = provenance or Provenance()

    sensed = sense_stage(raw_input)
    hypotheses = mind_stage(sensed, additional_context=additional_context)
    require_falsification(hypotheses)

    state = MindState(
        objective=sensed["objective"],
        facts=sensed.get("facts", []),
        hypotheses=hypotheses,
        provenance=_provenance,
        session_id=_session_id,
    )

    risks = heart_stage(state.hypotheses)
    state = state.model_copy(update={"risks": risks})

    verdict, violations = judge_stage(state)
    if violations:
        state = state.model_copy(update={"decision_required": True, "contradictions": violations})

    score = chaos_score(state)
    envelope = compress_for_operator(state)

    if verdict == "HOLD" or score >= 2.0:
        envelope = envelope.model_copy(update={"status": "HOLD", "human_decision_required": True})

    runtime_state = RuntimeState(
        sense=sensed,
        mind=state,
        heart_risks=risks,
        judge_status=envelope.status,
        judge_violations=violations,
        chaos_score=score,
    )

    return build_decision_packet(envelope, _session_id), build_audit_packet(
        raw_input, runtime_state, envelope, _session_id
    )


__all__ = [
    "Hypothesis",
    "Provenance",
    "MindState",
    "OutputEnvelope",
    "RuntimeState",
    "run_agi_mind",
]
