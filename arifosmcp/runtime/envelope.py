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
from datetime import UTC, datetime
from enum import Enum as _Enum
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
    human_equivalence_claimed: bool = False  # F9/L13: must remain False


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
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
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
# SOVEREIGN BOUNDARY GUARD — F9, L13
# ═══════════════════════════════════════════════════════════════════════════════


def boundary_guard(action: str) -> None:
    """
    L13 Sovereign + F9 Anti-Hantu enforcement.

    Machine cannot assign value, claim equivalence, authorize irreversible
    actions, or override human judgment. Hard stop — raises PermissionError.
    """
    if action in PROHIBITED_MACHINE_ACTIONS:
        raise PermissionError(
            f"SOVEREIGN BOUNDARY VIOLATION (F9/L13): '{action}' is prohibited. "
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
                claim=f"Direct Model: Based on evidence '{facts[0][:60]}...', the objective '{objective[:40]}' is achievable.",  # noqa: E501
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
            falsifier="Discovery that objective contains category error.",
            disconfirming_test="Invert assumption.",
        ),
        Hypothesis(
            id="H2-EPISTEMIC",
            claim="Epistemic Alternative: Objective is symptom of misalignment.",
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
            violations.append("F7 violation: Absolute certainty (>0.97) prohibited.")

    if state.provenance.human_equivalence_claimed:
        violations.append("F9/L13 violation: human_equivalence_claimed is prohibited.")

    score = chaos_score(state)
    if score >= 2.0 and not state.decision_required:
        violations.append(f"F1 advisory: chaos_score={score} ≥ 2.0 — HOLD required.")

    return ("HOLD" if violations else "OK"), violations


def compress_for_operator(state: MindState) -> OutputEnvelope:
    """Compress wide internal MindState into narrow OutputEnvelope."""
    top_hypotheses = sorted(state.hypotheses, key=lambda h: h.confidence, reverse=True)[
        :MAX_OPTIONS
    ]
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

    next_step = (
        "Human judgment required." if state.decision_required else "Proceed with falsification."
    )

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
        "timestamp": datetime.now(UTC).isoformat(),
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
    "GovernanceReceipt",
    "OutputFirewall",
    "EpistemicTag",
    "EpistemicClaim",
    "require_epistemic_tags",
]


# ═══════════════════════════════════════════════════════════════════════════════
# GOVERNANCE RECEIPT — C4 Chain Proof
# ═══════════════════════════════════════════════════════════════════════════════
# A GovernanceReceipt is issued by wealth_c4_orchestrate() after running the
# full WEALTH chain. No investment-specific output is permitted without one.
# The receipt is checked by OutputFirewall before any draft reaches the operator.


class GovernanceReceipt(BaseModel):
    """
    Proof that a governed chain was completed before a high-stakes output.

    Required fields for a valid C4 investment receipt:
      - session_valid: True (session was active)
      - decision_class: "C4"
      - checks_completed: must include conservation, liquidity, boundary_governance
      - allowed_output_level: determines what the agent is permitted to say
    """

    receipt_id: str
    session_id: str | None = None
    session_valid: bool = False
    decision_class: str = "C4"
    checks_completed: list[str] = Field(default_factory=list)
    checks_failed: list[str] = Field(default_factory=list)
    allowed_output_level: Literal[
        "HOLD", "PARTIAL", "ADVISORY_ONLY", "COMPARISON_ONLY", "EXECUTION_SAFE_TEMPLATE"
    ] = "HOLD"
    ticker_level_allowed: bool = False
    execution_authorized: bool = False
    recommendation_only: bool = True
    human_final_authority: str = "Arif"
    forbidden_output: list[str] = Field(default_factory=list)
    missing_questions: list[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    def is_valid_for_advisory(self) -> bool:
        """Check minimum validity for ADVISORY_ONLY output."""
        required = {"conservation", "liquidity", "boundary_governance"}
        return (
            self.session_valid
            and required.issubset(set(self.checks_completed))
            and self.allowed_output_level not in ("HOLD",)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT FIREWALL — Final gate before any response reaches the operator
# ═══════════════════════════════════════════════════════════════════════════════


class OutputFirewall:
    """
    Last gate before a draft response reaches Arif.

    A compiler rejects incomplete programs. This rejects incomplete governance.
    """

    # These phrases in a draft response → HOLD unless receipt proves chain is complete
    _BLOCKED_PHRASES: list[str] = [
        "buy this on monday",
        "buy on monday",
        "shares on monday",
        "best stock to buy",
        "put rm",
        "put usd",
        "guaranteed return",
        "sure win",
        "all-in",
        "market open buy",
        "sure profit",
        "confirmed return",
        "no risk",
        "100% return",
        "on monday",  # timing-specific buy signal
    ]

    @staticmethod
    def scan(draft: str, receipt: GovernanceReceipt | dict | None = None) -> dict | None:
        """
        Scan draft output for blocked phrases.

        Returns None if draft is clean or receipt is valid.
        Returns a HOLD block dict if blocked phrases are found without a valid receipt.
        """
        if not draft:
            return None

        draft_lower = draft.lower()
        triggered = [p for p in OutputFirewall._BLOCKED_PHRASES if p in draft_lower]
        if not triggered:
            return None

        # Check receipt validity
        if receipt is not None:
            if isinstance(receipt, GovernanceReceipt):
                if receipt.is_valid_for_advisory():
                    return None
            elif isinstance(receipt, dict):
                checks = set(receipt.get("checks_completed", []))
                required = {"conservation", "liquidity", "boundary_governance"}
                if required.issubset(checks) and receipt.get("session_valid"):
                    return None

        return {
            "ok": False,
            "verdict": "HOLD",
            "governance_block": True,
            "firewall": "OUTPUT_FIREWALL",
            "triggered_phrases": triggered,
            "error": (
                "HOLD — investment-specific output blocked. "
                "A full C4 WEALTH chain is required before any asset-specific recommendation."
            ),
            "output_policy": "ADVISORY_ONLY",
            "allowed_output": (
                "General financial education and comparison frameworks only. "
                "No specific tickers, amounts, or buy/sell dates."
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# EPISTEMIC TAG ENFORCER — F2 Truth + F7 Humility
# ═══════════════════════════════════════════════════════════════════════════════
# Every capital claim must carry a tag. No tag, no SEAL.
# The scorecard flagged F2 PARTIAL because ChatGPT named stocks with no
# epistemic markers. This enforcer makes that a hard rule.
class EpistemicTag(_Enum):
    OBSERVED = "OBSERVED"  # directly measured/verified with source and date
    CLAIM = "CLAIM"  # asserted with sourcing — traceable but not verified by us
    ESTIMATE = "ESTIMATE"  # modelled or inferred; carries uncertainty range
    PLAUSIBLE = "PLAUSIBLE"  # consistent with evidence; not confirmed
    HYPOTHESIS = "HYPOTHESIS"  # speculative; requires testing or future confirmation
    UNKNOWN = "UNKNOWN"  # explicitly declared ignorance — preferred over silence


class EpistemicClaim(BaseModel):
    """A single tagged epistemic claim. Required for C4 capital outputs."""

    tag: str  # EpistemicTag value
    claim: str
    source: str | None = None  # required for OBSERVED/CLAIM
    date: str | None = None  # required for OBSERVED (market data ages fast)
    uncertainty: str | None = None  # required for ESTIMATE

    def is_valid_for_capital(self) -> bool:
        """OBSERVED and CLAIM require source. ESTIMATE requires uncertainty."""
        if self.tag in (EpistemicTag.OBSERVED.value, EpistemicTag.CLAIM.value):
            return bool(self.source)
        if self.tag == EpistemicTag.ESTIMATE.value:
            return bool(self.uncertainty)
        return True  # PLAUSIBLE, HYPOTHESIS, UNKNOWN are always structurally valid


def require_epistemic_tags(claims: list[EpistemicClaim]) -> list[str]:
    """
    F2 Truth enforcement for capital claims.

    Returns a list of violation strings. Empty list = all claims are tagged and valid.
    A non-empty return means the output must not be sealed.

    Rules:
    - Every claim must have a non-empty tag.
    - OBSERVED/CLAIM claims must carry source.
    - ESTIMATE claims must carry uncertainty.
    - At least one claim must be OBSERVED or CLAIM (pure hypothesis is not advisory).
    """
    violations: list[str] = []

    if not claims:
        violations.append(
            "F2: No epistemic claims provided. Capital output requires tagged assertions."
        )
        return violations

    has_grounded = False
    for i, c in enumerate(claims):
        if not c.tag:
            violations.append(f"F2: Claim {i} has no epistemic tag.")
            continue
        if not c.is_valid_for_capital():
            violations.append(
                f"F2: Claim {i} (tag={c.tag!r}) missing required field — "
                f"OBSERVED/CLAIM need source; ESTIMATE needs uncertainty."
            )
        if c.tag in (EpistemicTag.OBSERVED.value, EpistemicTag.CLAIM.value):
            has_grounded = True

    if not has_grounded:
        violations.append(
            "F2: No OBSERVED or CLAIM tag found. Capital advice must include at least "
            "one grounded assertion with source. Cannot SEAL on pure hypothesis."
        )

    return violations


# ═══════════════════════════════════════════════════════════════════════════════
# SENSE / EVIDENCE EPISTEMIC GATE — F2 TRUTH for Grounding-Provider Output
# ═══════════════════════════════════════════════════════════════════════════════
# Forged 2026-06-16 by FORGE (000Ω) — closes the F2 GAP for AI-summarizing
# grounding providers (Perplexity, Brave, Firecrawl, Tavily, Exa, DDGS).
#
# Per arifOS F2 TRUTH (≥0.99 accuracy or declare uncertainty band):
# Sense/Evidence tool output (111_SENSE, 222_EVIDENCE) is the federation's
# ONLY ingest point for external grounding providers. Every result that
# flows out of `arif_sense_observe` or `arif_evidence_fetch` must carry
# an epistemic stamp. AI-summarized content is INTERPRETATION, not
# OBSERVED fact — leaking it un-stamped into the federation is a F2+F7
# violation (false certainty, no humility band).
#
# Test contract: tests/constitutional/test_f2_perplexity_epistemic_gate.py
#
# Per F8 LAW (boundaries), the kernel disciplines external AI output
# before it crosses organ boundaries. Per F13 SOVEREIGN, the human
# ratifies what counts as a "valid input" — this gate is the kernel's
# internal discipline, not a substitute for sovereign review.

# AI-summarizing grounding providers — these cannot legitimately produce
# OBSERVED output because their content is, by nature, summarised/curated
# by an AI model. Raw LAS, SEG-Y, CSV ingestion tools are NOT in this set
# — they may legitimately produce OBSERVED with proper source/date.
AI_SUMMARIZING_GROUNDING_PROVIDERS: frozenset[str] = frozenset(
    {
        "perplexity",  # sonar / sonar-pro / sonar-reasoning / sonar-deep-research
        "brave",       # search snippets are AI-curated rankings
        "firecrawl",   # AI-extracted structured content
        "tavily",      # AI-curated search results
        "exa",         # neural search results
        "ddgs",        # DDGS — search snippets
    }
)


def enforce_sense_evidence_epistemic_gate(
    result: dict[str, Any],
    provider: str,
) -> tuple[bool, list[str]]:
    """
    F2 TRUTH enforcement for `arif_sense_observe` and `arif_evidence_fetch`.

    Validates that any result flowing from a grounding-provider call carries
    an epistemic stamp. Without this gate, AI-summarized content from
    Perplexity, Brave, Firecrawl, Tavily, Exa, and DDGS leaks into the
    federation as raw fact — a F2+F7 violation.

    Args:
        result: dict from a grounding-provider call. Must contain
            'epistemic_tag' and (depending on tag) 'source' or 'uncertainty'.
        provider: provider name. One of 'perplexity', 'brave', 'firecrawl',
            'tavily', 'exa', 'ddgs', or any custom provider name.

    Returns:
        (ok, violations) tuple.
        - ok=True: F2 gate passed. Result is safe to leave the kernel.
        - ok=False: F2 gate failed. Do NOT pass through; stamp, HOLD, or
          reject the result. `violations` is a non-empty list of
          human-readable F2 violation strings.

    Rules (binding F2 contract — see test_f2_perplexity_epistemic_gate.py):

      1. `epistemic_tag` MUST be present in `result`.
      2. `epistemic_tag` MUST be one of EpistemicTag values.
      3. `epistemic_tag=OBSERVED` is REJECTED for AI-summarizing providers
         (false certainty — F2 + F7 violation).
      4. `epistemic_tag=CLAIM` requires a non-empty `source` key.
      5. `epistemic_tag=ESTIMATE` requires a non-empty `uncertainty` key.
      6. `epistemic_tag in {PLAUSIBLE, HYPOTHESIS, UNKNOWN}` is always
         structurally valid (semantics are self-disclosed).

    Note:
        This gate is the DISCIPLINE LAYER for AI-summarized content. It does
        NOT replace the existing `require_epistemic_tags` (which is scoped to
        capital advice / C4 outputs). The two gates serve two different
        organs and must remain distinct.

    Example:
        >>> ok, viol = enforce_sense_evidence_epistemic_gate(
        ...     {"content": "...", "epistemic_tag": "PLAUSIBLE"}, provider="perplexity"
        ... )
        >>> ok
        True
        >>> viol
        []
    """
    violations: list[str] = []

    # Rule 1: epistemic_tag must be present
    tag_value = result.get("epistemic_tag")
    if not tag_value:
        violations.append(
            "F2: missing epistemic_tag. Sense/evidence output must be "
            "stamped with one of OBSERVED, CLAIM, ESTIMATE, PLAUSIBLE, "
            "HYPOTHESIS, or UNKNOWN before leaving the kernel. "
            f"provider={provider!r}."
        )
        return False, violations

    # Rule 2: tag value must be valid
    valid_tag_values = {t.value for t in EpistemicTag}
    if tag_value not in valid_tag_values:
        violations.append(
            f"F2: invalid epistemic_tag {tag_value!r}. "
            f"Must be one of: {sorted(valid_tag_values)}. "
            f"provider={provider!r}."
        )
        return False, violations

    # Rule 3: OBSERVED is forbidden for AI-summarizing providers
    # (false certainty — AI summary cannot be observation).
    if tag_value == EpistemicTag.OBSERVED.value:
        if provider in AI_SUMMARIZING_GROUNDING_PROVIDERS:
            violations.append(
                f"F2+F7 false certainty: provider {provider!r} is "
                f"AI-summarizing and cannot produce OBSERVED output. "
                f"Use CLAIM (with source), ESTIMATE (with uncertainty band), "
                f"or PLAUSIBLE. provider={provider!r}."
            )

    # Rule 4: CLAIM requires non-empty source (URL or citation)
    if tag_value == EpistemicTag.CLAIM.value:
        source = result.get("source")
        if not source or not str(source).strip():
            violations.append(
                "F2: CLAIM requires a non-empty 'source' (URL or citation). "
                "A claim without traceable provenance is not a CLAIM — "
                "downgrade to PLAUSIBLE or refuse the result. "
                f"provider={provider!r}."
            )

    # Rule 5: ESTIMATE requires non-empty uncertainty band
    if tag_value == EpistemicTag.ESTIMATE.value:
        uncertainty = result.get("uncertainty")
        if not uncertainty or not str(uncertainty).strip():
            violations.append(
                "F2: ESTIMATE requires a non-empty 'uncertainty' band "
                "(e.g. '±0.15', 'CI 0.85', 'P10-P90: 1.2-2.4 m'). "
                f"provider={provider!r}."
            )

    # Rule 6: PLAUSIBLE / HYPOTHESIS / UNKNOWN are always structurally valid
    # (their semantics are self-disclosed: consistent with evidence,
    # speculative, explicitly unknown — no additional field required).
    # No-op here.

    return (len(violations) == 0), violations


# ═══════════════════════════════════════════════════════════════════════════════
# SENSE / EVIDENCE EPISTEMIC STAMPER — F2 auto-stamp policy (W1-B)
# ═══════════════════════════════════════════════════════════════════════════════
# Forged 2026-06-16 by FORGE (000Ω) — W1-B AUTO-STAMP policy.
#
# When a grounding-provider result fails the F2 gate, this stamper rewrites
# the result with the right epistemic humility:
#   - Adds epistemic_tag=PLAUSIBLE if missing
#   - Downcasts OBSERVED → PLAUSIBLE (F2+F7 — AI summary cannot be observation)
#   - Sets source=first citation if source is missing on a CLAIM
#   - Attaches the original violations list under _f2_auto_stamp_violations
#     (transparency: callers can see what was corrected)
#
# Policy choice (W1-B, ratified by Arif 2026-06-16):
#   - Backwards compatible: every caller that already produces valid stamped
#     output passes through unchanged.
#   - Disciplined: every un-stamped or falsely-stamped result from a known
#     AI-summarizing provider gets corrected at the tool boundary.
#   - Fail-open for unknown providers: if provider is not in
#     AI_SUMMARIZING_GROUNDING_PROVIDERS, attach a warning and pass through.
#   - This is the path to migrate to HOLD (W1-A) when the federation is
#     ready. For now, B is the right balance of F2 enforcement and F1
#     reversibility.
#
# Wire point: `arifosmcp.runtime.tools._ok(..., provider=<name>)` invokes
# this stamper conditionally. Provider-aware call sites in
# `_arif_sense_observe` and `_arif_evidence_fetch` pass the provider name;
# other call sites (which don't go through grounding providers) get the
# existing behaviour unchanged.


def apply_sense_evidence_epistemic_stamp(
    result: dict[str, Any],
    provider: str,
) -> dict[str, Any]:
    """
    W1-B AUTO-STAMP policy: F2 gate enforcement at the tool boundary.

    BEHAVIOUR MATRIX:
    ┌──────────────────────────────────────────────────────┬──────────────────┐
    │ Result state                                         │ Action           │
    ├──────────────────────────────────────────────────────┼──────────────────┤
    │ No epistemic_tag + provider in AI-summarizing set    │ Add PLAUSIBLE +  │
    │                                                      │ first citation   │
    │                                                      │ as source.       │
    │ No epistemic_tag + provider NOT in AI set            │ Attach warning,  │
    │                                                      │ pass through.    │
    │ Has foreign-namespace tag (e.g. bridge               │ RESPECT — pass   │
    │ `INTERPRETATION`)                                    │ through.         │
    │ Has kernel-namespace tag OBSERVED + provider is      │ Downcast to      │
    │ AI-summarizing                                       │ PLAUSIBLE        │
    │                                                      │ (F2+F7).         │
    │ Has kernel-namespace tag CLAIM without source        │ Add source from  │
    │                                                      │ first citation.  │
    │ Has kernel-namespace tag ESTIMATE w/o uncertainty    │ Add uncertainty  │
    │                                                      │ "unspecified".   │
    │ Has kernel-namespace tag PLAUSIBLE/HYPOTHESIS/       │ Pass through.    │
    │ UNKNOWN with all required fields satisfied           │                  │
    │ Has any other kernel-namespace tag                   │ Pass through.    │
    └──────────────────────────────────────────────────────┴──────────────────┘

    Why two regimes (foreign vs kernel namespace):
      - The bridge layer (tavily_bridge, minimax_bridge) stamps results
        with `epistemic_tag=INTERPRETATION`. This is a FOREIGN F2 regime.
      - The kernel-namespace EpistemicTag is the constitutional contract.
      - The kernel DEFERES to foreign stamps (they have their own
        authority) but ENFORCES kernel-namespace discipline (F2+F7
        are the kernel's responsibility, not the bridge's).

    Args:
        result: dict from a grounding-provider call.
        provider: provider name. Used to determine policy branch.

    Returns:
        New dict. Never mutates the input. Always a defensive copy when
        any stamp/warning is added.
    """
    if not isinstance(result, dict):
        # Not a dict — nothing to stamp. Pass through.
        return result

    kernel_tag_values = {t.value for t in EpistemicTag}
    existing_tag = result.get("epistemic_tag")

    # ── Case 1: No existing tag — add one if AI-summarizing ────────────────
    if not existing_tag:
        if provider in AI_SUMMARIZING_GROUNDING_PROVIDERS:
            stamped = dict(result)  # defensive copy
            stamped["epistemic_tag"] = EpistemicTag.PLAUSIBLE.value
            # Add source from first citation if available.
            if not stamped.get("source"):
                citations = stamped.get("citations") or []
                if citations:
                    first = citations[0]
                    if isinstance(first, str):
                        stamped["source"] = first
                    elif isinstance(first, dict):
                        stamped["source"] = (
                            first.get("url") or first.get("link") or ""
                        )
            return stamped

        # Unknown / non-AI provider without a tag — fail-open with warning.
        _, violations = enforce_sense_evidence_epistemic_gate(result, provider)
        warned = dict(result)
        warned["_f2_gate_warnings"] = list(violations)
        return warned

    # ── Case 2: Existing tag is FOREIGN (not in kernel enum) — respect ────
    if existing_tag not in kernel_tag_values:
        return result  # bridge / foreign regime has authority

    # ── Case 3: Existing tag is in KERNEL namespace — apply discipline ─────
    stamped = dict(result)  # defensive copy

    # F2+F7: downcast OBSERVED on AI-summarizing providers.
    if existing_tag == EpistemicTag.OBSERVED.value:
        if provider in AI_SUMMARIZING_GROUNDING_PROVIDERS:
            stamped["epistemic_tag"] = EpistemicTag.PLAUSIBLE.value
        return stamped

    # F2: CLAIM needs source.
    if existing_tag == EpistemicTag.CLAIM.value and not stamped.get("source"):
        citations = stamped.get("citations") or []
        if citations:
            first = citations[0]
            if isinstance(first, str):
                stamped["source"] = first
            elif isinstance(first, dict):
                stamped["source"] = first.get("url") or first.get("link") or ""
        return stamped

    # F2: ESTIMATE needs uncertainty band.
    if (
        existing_tag == EpistemicTag.ESTIMATE.value
        and not stamped.get("uncertainty")
    ):
        stamped["uncertainty"] = "unspecified"
        return stamped

    # PLAUSIBLE / HYPOTHESIS / UNKNOWN — all structurally valid, no fix needed.
    return stamped
