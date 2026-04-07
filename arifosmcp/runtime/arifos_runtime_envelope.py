"""
arifos_runtime_envelope.py

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
PROHIBITED_MACHINE_ACTIONS = frozenset({
    "assign_intrinsic_value",
    "claim_human_equivalence",
    "authorize_irreversible_action",
    "claim_embodied_meaning",
    "override_human_judgment",
    "grant_sovereign_authority",
})


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
    grounding_status: Literal[
        "data-based", "sensor-based", "human-mediated", "ungrounded"
    ] = "human-mediated"
    stakes_model: Literal[
        "none", "simulated", "externalized-to-human", "shared"
    ] = "externalized-to-human"
    confidence_domain: Literal[
        "narrow-task", "broad-context", "ambiguous", "human-judgment-required"
    ] = "ambiguous"
    meaning_source: Literal[
        "human-attributed", "statistical-inference", "ungrounded"
    ] = "statistical-inference"
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
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
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
    key_facts: list[str]        # max MAX_FACTS
    key_uncertainties: list[str]  # max MAX_UNKNOWNS
    options: list[str]          # max MAX_OPTIONS
    next_step: str              # exactly 1
    human_decision_required: bool
    provenance: Provenance


# ═══════════════════════════════════════════════════════════════════════════════
# RUNTIME STATE — internal full state for audit
# ═══════════════════════════════════════════════════════════════════════════════

class RuntimeState(BaseModel):
    """Full internal runtime state — for vault and replay. Never send to operator."""
    sense: dict[str, Any] = Field(default_factory=dict)
    mind: MindState | None = None
    heart_risks: list[str] = Field(default_factory=list)
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
    Compute entropy score from internal mind state.

    Low chaos  (< 1.0) → answer directly
    Medium     (< 2.0) → answer with uncertainty disclosure
    High       (≥ 2.0) → HOLD — narrow scope or get human judgment
    """
    score = 0.0
    score += len(state.assumptions) * 0.2
    score += len(state.unknowns) * 0.3
    score += len(state.contradictions) * 0.5
    score += max(0, len(state.hypotheses) - 2) * 0.1
    return round(score, 2)


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
    """
    Stage 1: Input chaos → grounded facts.

    Does NOT hallucinate facts. Returns structure with what is known,
    what is assumed, and what is unknown.
    """
    return {
        "objective": raw_input,
        "facts": [],           # populated by reality grounding (arifos.sense)
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
    """
    Stage 2: Grounded facts → structured hypotheses with falsifiers.
    """
    objective = sense_packet.get("objective", "")
    facts = sense_packet.get("facts", [])
    short_obj = objective[:100] if len(objective) > 100 else objective

    context_note = f" (context: {additional_context[:60]})" if additional_context else ""

    return [
        Hypothesis(
            id="H1-CAUSAL",
            claim=f"Primary Causal Model: {short_obj}{context_note}. This model assumes that the stated objective is the core requirement and uses grounding facts to synthesize a direct solution path.",
            confidence=0.65,
            evidence_for=facts[:3] if facts else ["Constitutional alignment with input directive"],
            evidence_against=[],
            falsifier=(
                f"Obtaining data that shows the core assumption of '{short_obj[:40]}' is structurally flawed or contains a category error."
            ),
            disconfirming_test=(
                "Synthesize a scenario where the grounding facts are unchanged but the desired outcome is inverted."
            ),
        ),
        Hypothesis(
            id="H2-EPISTEMIC",
            claim=(
                f"Epistemic Alternative: The objective '{short_obj[:60]}' may be a symptom of a deeper architectural misalignment or missing prerequisite context."
            ),
            confidence=0.35,
            evidence_for=[],
            evidence_against=facts[:1] if facts else [],
            falsifier=(
                "Proof that the current grounding is complete and no latent variables exist in the target domain."
            ),
            disconfirming_test=(
                "Attempt to solve the objective using only out-of-band information to check for reliance on potentially stale grounding."
            ),
        ),
    ]


def heart_stage(hypotheses: list[Hypothesis]) -> list[str]:
    """
    Stage 3: Simulate consequences — NO value assignment.

    Produces risk traces for each hypothesis. Does not decide which is
    better — that is a human judgment. Only maps consequence space.
    """
    risks: list[str] = []
    for h in hypotheses:
        risks.append(
            f"[{h.id}] If this hypothesis is wrong: false confidence, "
            f"wasted resources, possible downstream harm. "
            f"Falsifier check: {h.falsifier[:80]}"
        )
        if h.evidence_against:
            risks.append(
                f"[{h.id}] Countervailing evidence present: "
                f"{h.evidence_against[0][:80]}"
            )
    return risks


def judge_stage(state: MindState) -> tuple[str, list[str]]:
    """
    Stage 4: Constitutional gate — checks F1, F2, F9, F13.

    Returns (verdict, violations).
    verdict: "OK" or "HOLD"
    violations: list of floor breach descriptions
    """
    violations: list[str] = []

    # F2: Require ≥2 hypotheses
    if not state.hypotheses or len(state.hypotheses) < 2:
        violations.append(
            "F2 violation: fewer than 2 hypotheses — "
            "epistemic rigor requires holding multiple models simultaneously."
        )

    # F2: Falsification mandate
    for h in state.hypotheses:
        if not h.falsifier.strip():
            violations.append(
                f"F2 violation: Hypothesis {h.id!r} missing falsifier — "
                "unfalsifiable claims cannot be dispatched."
            )

    # F9 + F13: No human-equivalence claim
    if state.provenance.human_equivalence_claimed:
        violations.append(
            "F9/F13 violation: human_equivalence_claimed=True is prohibited. "
            "Statistical intelligence ≠ sovereign intelligence."
        )

    # F1: High chaos → sovereign review required
    score = chaos_score(state)
    if score >= 2.0 and not state.decision_required:
        violations.append(
            f"F1 advisory: chaos_score={score} ≥ 2.0 — "
            "irreversibility threshold exceeded; sovereign review required."
        )

    return ("HOLD" if violations else "OK"), violations


# ═══════════════════════════════════════════════════════════════════════════════
# COMPRESS FOR OPERATOR — WIDE → NARROW
# ═══════════════════════════════════════════════════════════════════════════════

def compress_for_operator(state: MindState) -> OutputEnvelope:
    """
    Compress wide internal MindState into narrow external OutputEnvelope.

    Internal state can be 500 lines.
    Operator output becomes ≤15 lines.
    This is the anti-chaos move.
    """
    top_hypotheses = sorted(
        state.hypotheses, key=lambda h: h.confidence, reverse=True
    )[:MAX_OPTIONS]

    options = [h.claim for h in top_hypotheses]

    summary = (
        top_hypotheses[0].claim
        if top_hypotheses
        else "No stable hypothesis available — insufficient evidence."
    )

    score = chaos_score(state)
    if state.decision_required or score >= 2.0:
        status: Literal["OK", "PARTIAL", "HOLD", "ERROR"] = "HOLD"
    elif state.unknowns:
        status = "PARTIAL"
    else:
        status = "OK"

    if state.decision_required:
        next_step = "Human judgment required before proceeding."
    elif top_hypotheses:
        next_step = (
            f"Test the top hypothesis against its falsifier: "
            f"{top_hypotheses[0].falsifier[:120]}"
        )
    else:
        next_step = "Gather more evidence before forming a hypothesis."

    return OutputEnvelope(
        summary=summary,
        status=status,
        key_facts=state.facts[:MAX_FACTS],
        key_uncertainties=state.unknowns[:MAX_UNKNOWNS],
        options=options[:MAX_OPTIONS],
        next_step=next_step,
        human_decision_required=state.decision_required,
        provenance=state.provenance,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PACKET SEPARATION — decision vs audit
# ═══════════════════════════════════════════════════════════════════════════════

def build_decision_packet(
    envelope: OutputEnvelope,
    session_id: str,
) -> dict[str, Any]:
    """
    For operator / user.

    Minimal decisive packet — 15 lines maximum.
    Never merged with audit data by default.
    """
    return {
        "status": envelope.status,
        "summary": envelope.summary,
        "facts": envelope.key_facts,
        "uncertainties": envelope.key_uncertainties,
        "options": envelope.options,
        "next_step": envelope.next_step,
        "human_decision_required": envelope.human_decision_required,
        "provenance": {
            "type": envelope.provenance.intelligence_type,
            "grounding": envelope.provenance.grounding_status,
            "stakes": envelope.provenance.stakes_model,
            "confidence_domain": envelope.provenance.confidence_domain,
            "meaning_source": envelope.provenance.meaning_source,
        },
        "_session": session_id,
    }


def build_audit_packet(
    raw_input: str,
    runtime_state: RuntimeState,
    envelope: OutputEnvelope,
    session_id: str,
) -> dict[str, Any]:
    """
    For vault / engineering / replay.

    Full audit trail — never send to operator directly.
    Contains full hypothesis set, risk trace, constitutional checks, timestamps.
    """
    mind = runtime_state.mind
    return {
        "raw_input": raw_input,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "full_hypothesis_set": (
            [h.model_dump() for h in mind.hypotheses] if mind else []
        ),
        "full_facts": mind.facts if mind else [],
        "full_assumptions": mind.assumptions if mind else [],
        "risk_trace": runtime_state.heart_risks,
        "constitutional_checks": {
            "judge_status": runtime_state.judge_status,
            "violations": runtime_state.judge_violations,
            "chaos_score": runtime_state.chaos_score,
            "chaos_mode": output_mode_from_chaos(runtime_state.chaos_score),
        },
        "provenance": envelope.provenance.model_dump(),
        "pipeline_trace": mind.pipeline_trace if mind else [],
        "output_summary": envelope.summary,
        "output_status": envelope.status,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

async def run_agi_mind(
    raw_input: str,
    session_id: str | None = None,
    additional_context: str = "",
    provenance: Provenance | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Run the full typed AGI pipeline.

    Returns:
        (decision_packet, audit_packet)

        decision_packet — for operator, narrow, ≤15 lines
        audit_packet    — for vault, full, unlimited

    Pipeline: sense → mind → heart → judge → compress → split

    Constitutional constraints enforced at every stage:
        F1: Chaos gate — high entropy triggers HOLD
        F2: Truth — ≥2 hypotheses, all falsifiable
        F9: Anti-Hantu — no human-equivalence claim
        F13: Sovereign — human judgment required for HOLD
    """
    _session_id = session_id or f"agi_{uuid.uuid4().hex[:12]}"
    _provenance = provenance or Provenance()

    # ── Stage 1: SENSE ──────────────────────────────────────────────────
    sensed = sense_stage(raw_input)

    # ── Stage 2: MIND ───────────────────────────────────────────────────
    hypotheses = mind_stage(sensed, additional_context=additional_context)
    require_falsification(hypotheses)  # F2 hard check

    state = MindState(
        objective=sensed["objective"],
        facts=sensed.get("facts", []),
        assumptions=sensed.get("assumptions", []),
        unknowns=sensed.get("unknowns", []),
        hypotheses=hypotheses,
        contradictions=[],
        risks=[],
        decision_required=False,
        provenance=_provenance,
        session_id=_session_id,
        pipeline_trace=["sense", "mind"],
    )

    # ── Stage 3: HEART ──────────────────────────────────────────────────
    risks = heart_stage(state.hypotheses)
    state = state.model_copy(update={
        "risks": risks,
        "pipeline_trace": state.pipeline_trace + ["heart"],
    })

    # ── Stage 4: JUDGE ──────────────────────────────────────────────────
    verdict, violations = judge_stage(state)

    if violations:
        state = state.model_copy(update={
            "decision_required": True,
            "contradictions": state.contradictions + violations,
            "pipeline_trace": state.pipeline_trace + ["judge:HOLD"],
        })
    else:
        state = state.model_copy(update={
            "pipeline_trace": state.pipeline_trace + ["judge:OK"],
        })

    # ── Chaos gate ──────────────────────────────────────────────────────
    score = chaos_score(state)

    # ── Compress → OutputEnvelope ────────────────────────────────────────
    envelope = compress_for_operator(state)

    # Override if chaos or judge forced HOLD
    if verdict == "HOLD" or score >= 2.0:
        envelope = envelope.model_copy(update={
            "status": "HOLD",
            "next_step": (
                "Narrow the scope, resolve contradictions, "
                "or obtain human judgment before proceeding."
            ),
            "human_decision_required": True,
        })

    # ── Build runtime state for audit ────────────────────────────────────
    runtime_state = RuntimeState(
        sense=sensed,
        mind=state,
        heart_risks=risks,
        judge_status=verdict,
        judge_violations=violations,
        chaos_score=score,
    )

    # ── Split packets ────────────────────────────────────────────────────
    decision_packet = build_decision_packet(envelope, _session_id)
    audit_packet = build_audit_packet(raw_input, runtime_state, envelope, _session_id)

    return decision_packet, audit_packet


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Models
    "Hypothesis",
    "Provenance",
    "MindState",
    "OutputEnvelope",
    "RuntimeState",
    # Constants
    "AGI_PIPELINE",
    "MAX_FACTS",
    "MAX_UNKNOWNS",
    "MAX_OPTIONS",
    "PROHIBITED_MACHINE_ACTIONS",
    # Guards
    "boundary_guard",
    "require_falsification",
    # Entropy
    "chaos_score",
    "output_mode_from_chaos",
    # Pipeline stages
    "sense_stage",
    "mind_stage",
    "heart_stage",
    "judge_stage",
    # Compression
    "compress_for_operator",
    # Packets
    "build_decision_packet",
    "build_audit_packet",
    # Orchestrator
    "run_agi_mind",
]
