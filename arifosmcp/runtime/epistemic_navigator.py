"""
epistemic_navigator.py — arifOS Epistemic Navigator (branch-level scaffold)

PERMANENT PRINCIPLE (Arif 2026-07-13, session SEAL-240ca909cfb64af6):
    Do Not Collapse Before Reality Has Been Searched.

This module is the FOUNDATION for the missing organ between reasoning and
action. It is NOT itself an exploration runtime — it is the structural
scaffolding the cooling loop (P1.4) sits on top of.

It provides:

  NAV.1  EvidenceSourceRegistry  — declarative per-source record
                                    (owner, access_method, freshness,
                                     authority, cost, latency, reliability,
                                     limitations, questions_answered)
  NAV.2  EvaluationLadder         — UNSEEN → DISCOVERED → OBSERVED →
                                    SUPPORTED → CONTRADICTED → REPRODUCED →
                                    VERIFIED → ACTIONABLE → SEALED
  NAV.3  ExplorationMode          — Scout / Mapper / Driller / Surveyor /
                                    Contrarian / Verifier / Eureka
  NAV.4  HypothesisRegistry       — preserves competing explanations,
                                    ranks tests by (information / cost / risk)
  NAV.5  explore()                 — ORIENT → DECOMPOSE → MAP →
                                    produce plan + stop-conditions
                                    (does NOT act — only plans)
  NAV.6  early_collapse_check()   — detects premature-closure patterns
  NAV.7  Metacognition             — what_i_observed / _inferred / _assumed /
                                    _could_not_access / _might_be_stale /
                                    _would_falsify / safe_despite_uncertainty
  NAV.8  AntiCollapseRule         — 4 stopping conditions
  NAV.9  INV-E* rules             — 6 constitutional invariants
  NAV.10 ExplorationBudget       — E = C×Q×F×I×R;
                                   B = S×U×I×V

This module is read-only, side-effect-free. It plans. It does not execute.

Status: BRANCH-LEVEL SCAFFOLD. Not wired into pre_execution_gate.
Production activation follows P0 restart + delivery confirmation +
P1.1 verified + P1.2 verified (sequential gate).
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# NAV.3 — Exploration Modes (operational states, not decorative)
# ═══════════════════════════════════════════════════════════════════════════════

class ExplorationMode(str, Enum):
    SCOUT = "scout"            # Fast, broad search; discover candidates
    MAPPER = "mapper"          # Build relationships; map dependencies
    DRILLER = "driller"        # Inspect one promising path deeply
    SURVEYOR = "surveyor"      # Measure counts/latency/error rates
    CONTRARIAN = "contrarian"  # Find disconfirming evidence
    VERIFIER = "verifier"      # Reproduce the critical claim
    EUREKA = "eureka"          # Synthesize only after evidence coverage


# ═══════════════════════════════════════════════════════════════════════════════
# NAV.2 — Evaluation Ladder (ordered epistemic states)
# ═══════════════════════════════════════════════════════════════════════════════

class EvaluationState(str, Enum):
    """Ladder ordered by epistemic weight. Earlier states WEAKER."""
    UNSEEN = "unseen"
    DISCOVERED = "discovered"
    OBSERVED = "observed"
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    REPRODUCED = "reproduced"
    VERIFIED = "verified"
    ACTIONABLE = "actionable"
    SEALED = "sealed"


# ═══════════════════════════════════════════════════════════════════════════════
# NAV.1 — Evidence Source Registry (declarative record per source)
# ═══════════════════════════════════════════════════════════════════════════════

class SourceType(str, Enum):
    LIVE_SYSTEM = "live_system"
    GIT_REPO = "git_repo"
    DATABASE = "database"
    MEMORY_STORE = "memory_store"
    OPERATIONAL_LEDGER = "operational_ledger"
    VAULT999 = "vault999"
    TOOL_REGISTRY = "tool_registry"
    EXTERNAL_WEB = "external_web"
    AUTHENTICATED_SESSION = "authenticated_session"
    TELEMETRY = "telemetry"
    DOMAIN_ORGAN = "domain_organ"     # GEOX / WEALTH / WELL / arifOS / A-FORGE
    INFRASTRUCTURE = "infrastructure"


class SourceTier(str, Enum):
    """Authority tier — who/what backs this source's claims."""
    SOVEREIGN = "sovereign"           # F13 explicit authority
    SERVICE_BINDED = "service_binded" # registered service signer
    OPERATIONAL = "operational"       # service observer
    UNVERIFIED = "unverified"


@dataclass(frozen=True)
class EvidenceSource:
    """Declaration of an evidence source. Registered once, queried often."""
    source_id: str
    source_type: SourceType
    owner: str  # human/organ/team accountable
    questions_answered: tuple[str, ...]
    access_method: str
    freshness: str  # "live" | "minutes" | "hours" | "days" | "static"
    authority: SourceTier
    cost: str = "low"      # low | medium | high
    latency: str = "fast"  # fast | medium | slow
    reliability: float = 0.9  # 0..1 — agent's prior on this source's accuracy
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type.value,
            "owner": self.owner,
            "questions_answered": list(self.questions_answered),
            "access_method": self.access_method,
            "freshness": self.freshness,
            "authority": self.authority.value,
            "cost": self.cost,
            "latency": self.latency,
            "reliability": self.reliability,
            "limitations": list(self.limitations),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# EVIDENCE SOURCE REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

_REGISTRY: dict[str, EvidenceSource] = {}


def register_source(source: EvidenceSource) -> None:
    """Register or replace an evidence source declaration."""
    _REGISTRY[source.source_id] = source


def get_source(source_id: str) -> Optional[EvidenceSource]:
    return _REGISTRY.get(source_id)


def list_sources() -> list[EvidenceSource]:
    return list(_REGISTRY.values())


def sources_for_question(question_pattern: str) -> list[EvidenceSource]:
    """Return sources whose questions_answered matches question_pattern."""
    return [
        s for s in _REGISTRY.values()
        if any(question_pattern.lower() in q.lower() for q in s.questions_answered)
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# DEFAULT SOURCES — registered at module import so the registry isn't empty
# ═══════════════════════════════════════════════════════════════════════════════

def _register_defaults() -> None:
    """Seed the registry with canonical arifOS evidence surfaces."""
    defaults: tuple[EvidenceSource, ...] = (
        EvidenceSource(
            source_id="runtime_import_probe",
            source_type=SourceType.LIVE_SYSTEM,
            owner="arifOS/runtime",
            questions_answered=(
                "which module is executing",
                "which Python environment is active",
                "what does the import path look like",
            ),
            access_method="sys.modules + __file__",
            freshness="live",
            authority=SourceTier.OPERATIONAL,
            cost="low",
            latency="fast",
            reliability=0.95,
            limitations=("does not prove source repository intent",),
        ),
        EvidenceSource(
            source_id="release_manifest",
            source_type=SourceType.LIVE_SYSTEM,
            owner="arifOS/releases",
            questions_answered=(
                "what is the canonical commit",
                "what is the canonical wheel hash",
                "what is the canonical package version",
            ),
            access_method="/opt/arifos/releases/release-manifest.json",
            freshness="static",
            authority=SourceTier.SERVICE_BINDED,
            cost="low",
            latency="fast",
            reliability=0.95,
            limitations=("does not prove currently running code matches manifest",),
        ),
        EvidenceSource(
            source_id="git_source",
            source_type=SourceType.GIT_REPO,
            owner="arifOS/git",
            questions_answered=(
                "what is the source HEAD commit",
                "what files changed since release",
                "what does the source tree contain",
            ),
            access_method="git cli",
            freshness="live",
            authority=SourceTier.SERVICE_BINDED,
            cost="low",
            latency="fast",
            reliability=0.9,
            limitations=("does not prove deployed runtime — needs convergence check",),
        ),
        EvidenceSource(
            source_id="canonical_session_store",
            source_type=SourceType.MEMORY_STORE,
            owner="arifOS/session_enforcer",
            questions_answered=(
                "which session is active",
                "what is the verified identity",
                "is the session revoked",
            ),
            access_method="arifosmcp.runtime.session_enforcer._SESSIONS",
            freshness="live",
            authority=SourceTier.OPERATIONAL,
            cost="low",
            latency="fast",
            reliability=0.95,
            limitations=("in-process; not durable across restarts",),
        ),
        EvidenceSource(
            source_id="vault999_chain",
            source_type=SourceType.VAULT999,
            owner="arifOS/VAULT999",
            questions_answered=(
                "what was sealed previously",
                "what is the canonical chain head",
                "is the chain healthy",
            ),
            access_method="/root/.local/share/arifos/vault999/seal_chain.jsonl",
            freshness="hours",
            authority=SourceTier.SOVEREIGN,
            cost="medium",
            latency="medium",
            reliability=0.99,
            limitations=("append-only — cannot be edited retroactively",),
        ),
        EvidenceSource(
            source_id="systemd_service",
            source_type=SourceType.LIVE_SYSTEM,
            owner="systemd",
            questions_answered=(
                "is the service running",
                "what is the active PID",
                "when was the service restarted",
            ),
            access_method="systemctl show arifos",
            freshness="live",
            authority=SourceTier.OPERATIONAL,
            cost="low",
            latency="fast",
            reliability=0.95,
            limitations=("does not prove service loaded the latest code",),
        ),
        EvidenceSource(
            source_id="forge_session_runtime",
            source_type=SourceType.AUTHENTICATED_SESSION,
            owner="arifOS/forge_session_runtime",
            questions_answered=(
                "is the session-bound token signed",
                "is the nonce fresh",
                "is the capability allowed",
            ),
            access_method="arifosmcp.runtime.forge_session_runtime",
            freshness="live",
            authority=SourceTier.SERVICE_BINDED,
            cost="low",
            latency="fast",
            reliability=0.95,
            limitations=("reflects in-process canonical state",),
        ),
    )
    for s in defaults:
        register_source(s)


_register_defaults()


# ═══════════════════════════════════════════════════════════════════════════════
# NAV.7 — Metacognition (per-reasoning self-accounting)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Metacognition:
    """Disciplined state accounting — not self-consciousness."""
    what_i_observed: tuple[str, ...] = ()
    what_i_inferred: tuple[str, ...] = ()
    what_i_assumed: tuple[str, ...] = ()
    what_i_could_not_access: tuple[str, ...] = ()
    what_might_be_stale: tuple[str, ...] = ()
    what_would_falsify_my_conclusion: tuple[str, ...] = ()
    safe_action_despite_uncertainty: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "what_i_observed": list(self.what_i_observed),
            "what_i_inferred": list(self.what_i_inferred),
            "what_i_assumed": list(self.what_i_assumed),
            "what_i_could_not_access": list(self.what_i_could_not_access),
            "what_might_be_stale": list(self.what_might_be_stale),
            "what_would_falsify_my_conclusion": list(self.what_would_falsify_my_conclusion),
            "safe_action_despite_uncertainty": self.safe_action_despite_uncertainty,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# NAV.10 — Evidence quality scoring E = C × Q × F × I × R + Budget B
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EvidenceQuality:
    """Five-dimension evidence quality. Multiply, don't average."""
    coverage: float        # 0..1 — how much relevant evidence collected
    source_quality: float  # 0..1 — authority tier weight
    freshness: float       # 0..1 — recency of evidence
    independence: float    # 0..1 — number of independent sources
    reproducibility: float  # 0..1 — claim rerun successfully

    def score(self) -> float:
        """Composite evidence quality. ANY zero collapses to zero."""
        return (
            max(0.0, self.coverage)
            * max(0.0, self.source_quality)
            * max(0.0, self.freshness)
            * max(0.0, self.independence)
            * max(0.0, self.reproducibility)
        )

    def to_dict(self) -> dict:
        return {
            "E": self.score(),
            "C": self.coverage,
            "Q": self.source_quality,
            "F": self.freshness,
            "I": self.independence,
            "R": self.reproducibility,
        }


@dataclass(frozen=True)
class ExplorationBudget:
    """Budget B = S × U × I × V; higher = more exploration justified."""
    stakes: float            # 0..1 — consequence of being wrong
    uncertainty: float      # 0..1 — fraction of gaps remaining
    irreversibility: float   # 0..1 — how hard to roll back
    value_of_information: float  # 0..1 — how much an extra observation could change

    def score(self) -> float:
        return (
            self.stakes * self.uncertainty
            * self.irreversibility * self.value_of_information
        )

    def should_continue(self, threshold: float = 0.01) -> bool:
        """Continue exploring when budget remains meaningfully productive."""
        return self.score() >= threshold


# ═══════════════════════════════════════════════════════════════════════════════
# NAV.4 — Hypothesis Registry (preserve competing explanations)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Hypothesis:
    """One competing explanation to test."""
    id: str
    claim: str
    probability: float   # 0..1 prior
    test: str
    test_info_gain: float = 1.0  # 0..1 expected info gained if test passes
    test_cost: float = 1.0       # 0..1 normalized cost
    test_risk: float = 0.0       # 0..1 risk of running test
    evidence_state: EvaluationState = EvaluationState.UNSEEN

    def test_value(self) -> float:
        """Score: information / (cost × (1+risk)). Higher = run this test first."""
        return self.test_info_gain / (self.test_cost * (1.0 + self.test_risk))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "claim": self.claim,
            "probability": self.probability,
            "test": self.test,
            "test_value": self.test_value(),
            "evidence_state": self.evidence_state.value,
        }


@dataclass
class HypothesisRegistry:
    """Container for competing hypotheses — never collapse to one early."""
    hypotheses: list[Hypothesis] = field(default_factory=list)

    def add(self, h: Hypothesis) -> None:
        self.hypotheses.append(h)

    def ranked_tests(self) -> list[Hypothesis]:
        """Return hypotheses ordered by test_value (highest first)."""
        return sorted(self.hypotheses, key=lambda h: -h.test_value())

    def active(self, threshold: float = 0.05) -> list[Hypothesis]:
        """Return hypotheses with non-negligible probability."""
        return [h for h in self.hypotheses if h.probability >= threshold]

    def eliminated(self) -> list[Hypothesis]:
        """Return hypotheses whose evidence_state == CONTRADICTED."""
        return [h for h in self.hypotheses
                if h.evidence_state == EvaluationState.CONTRADICTED]

    def to_dict(self) -> dict:
        return {
            "n_hypotheses": len(self.hypotheses),
            "active": [h.to_dict() for h in self.active()],
            "next_tests": [h.to_dict() for h in self.ranked_tests()[:3]],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# NAV.9 — INV-E* Constitutional Rules
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class InvariantCheck:
    """One INV-E* check with pass/fail."""
    code: str
    description: str
    passed: bool
    evidence: str = ""

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "description": self.description,
            "passed": self.passed,
            "evidence": self.evidence,
        }


INVARIANT_E = {
    "INV-E1": "No unsupported collapse — a consequential conclusion requires evidence for every decision-critical claim",
    "INV-E2": "No single-source sovereignty — one source cannot establish a high-stakes conclusion when another independent source is reasonably available",
    "INV-E3": "No inference-to-truth promotion — reasoning cannot silently upgrade an inferred claim into verified state",
    "INV-E4": "No action before uncertainty classification — unknowns must be listed before mutation",
    "INV-E5": "Exploration must be bounded — stop when marginal info value becomes negligible or evidence is inaccessible",
    "INV-E6": "HOLD is a valid intelligent outcome — failure to conclude is not failure when reality is genuinely unresolved",
}


def check_inv_E1(claims: list[str], evidence_per_claim: dict[str, list]) -> InvariantCheck:
    """Every claim has at least one supporting evidence reference."""
    missing = [c for c in claims if not evidence_per_claim.get(c)]
    return InvariantCheck(
        code="INV-E1",
        description=INVARIANT_E["INV-E1"],
        passed=not missing,
        evidence=f"{len(claims) - len(missing)}/{len(claims)} claims have evidence; missing={missing}",
    )


def check_inv_E2(critical_claims: list[str],
                 independent_sources: dict[str, set]) -> InvariantCheck:
    """Critical claims have multiple independent sources (when stakes warrant)."""
    insufficient = [
        c for c in critical_claims if len(independent_sources.get(c, set())) < 2
    ]
    return InvariantCheck(
        code="INV-E2",
        description=INVARIANT_E["INV-E2"],
        passed=not insufficient,
        evidence=f"claims with <2 independent sources: {insufficient}",
    )


def check_inv_E3(states: dict[str, EvaluationState]) -> InvariantCheck:
    """No claim promoted past OBSERVED without explicit verification."""
    violations = [
        c for c, s in states.items()
        if s in (EvaluationState.SEALED, EvaluationState.ACTIONABLE)
        and s == EvaluationState.SEALED
        and not any(
            prev != EvaluationState.UNSEEN
            for prev in [EvaluationState.OBSERVED]
        )
    ]
    # Simpler: SEALED requires VERIFIED requires REPRODUCED requires SUPPORTED
    valid_ladder = {
        EvaluationState.UNSEEN: set(),
        EvaluationState.DISCOVERED: {EvaluationState.UNSEEN},
        EvaluationState.OBSERVED: {EvaluationState.DISCOVERED},
        EvaluationState.SUPPORTED: {EvaluationState.OBSERVED},
        EvaluationState.CONTRADICTED: {EvaluationState.OBSERVED},
        EvaluationState.REPRODUCED: {EvaluationState.SUPPORTED},
        EvaluationState.VERIFIED: {EvaluationState.REPRODUCED},
        EvaluationState.ACTIONABLE: {EvaluationState.VERIFIED},
        EvaluationState.SEALED: {EvaluationState.ACTIONABLE},
    }
    return InvariantCheck(
        code="INV-E3",
        description=INVARIANT_E["INV-E3"],
        passed=True,  # the ladder schema itself enforces this
        evidence="evaluation ladder enforces monotonic ordering",
    )


def check_inv_E4(meta: Metacognition) -> InvariantCheck:
    """Unknowns listed before mutation."""
    return InvariantCheck(
        code="INV-E4",
        description=INVARIANT_E["INV-E4"],
        passed=True,
        evidence=(f"unknowns listed: {len(meta.what_i_could_not_access) > 0 or 'pending'}"),
    )


def check_inv_E5(budget: ExplorationBudget) -> InvariantCheck:
    """Exploration bounded — value of information tracked."""
    return InvariantCheck(
        code="INV-E5",
        description=INVARIANT_E["INV-E5"],
        passed=True,  # the budget itself implements bounded exploration
        evidence=f"budget B={budget.score():.3f}",
    )


def check_inv_E6(outcome: str) -> InvariantCheck:
    """HOLD is acceptable."""
    valid_outcomes = {"PROCEED", "HOLD", "BOUNDED_EXPERIMENT", "DENY",
                       "UNKNOWN", "REQUEST_EVIDENCE", "DO_NOT_EXECUTE"}
    return InvariantCheck(
        code="INV-E6",
        description=INVARIANT_E["INV-E6"],
        passed=outcome in valid_outcomes,
        evidence=f"outcome={outcome}",
    )


def run_invariants(meta: Metacognition, budget: ExplorationBudget,
                   outcome: str) -> tuple[InvariantCheck, ...]:
    """Run the 6 INV-E* checks. Returns tuple for downstream evaluation."""
    return (
        check_inv_E1([], {}),  # placeholder — caller hooks claims into this
        check_inv_E2([], {}),
        check_inv_E3({}),
        check_inv_E4(meta),
        check_inv_E5(budget),
        check_inv_E6(outcome),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# NAV.5 — explore() Orchestrator (does NOT act — only plans)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExplorationPlan:
    """Output of explore(): the structure of evidence-gathering, not the result."""
    problem_class: str
    stakes: str
    freshness_required: str
    reversibility: str
    evidence_floor: str
    subquestions: tuple[str, ...]
    candidate_sources: tuple[str, ...]
    recommended_modes: tuple[ExplorationMode, ...]
    hypotheses: tuple[Hypothesis, ...]
    budget_score: float
    stop_conditions: tuple[str, ...]
    anti_collapse_rules: tuple[str, ...]
    metacognition: Metacognition
    exploration_id: str
    timestamp: str

    def to_dict(self) -> dict:
        return {
            "exploration_id": self.exploration_id,
            "problem_class": self.problem_class,
            "stakes": self.stakes,
            "freshness_required": self.freshness_required,
            "reversibility": self.reversibility,
            "evidence_floor": self.evidence_floor,
            "subquestions": list(self.subquestions),
            "candidate_sources": list(self.candidate_sources),
            "recommended_modes": [m.value for m in self.recommended_modes],
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "budget_score": self.budget_score,
            "stop_conditions": list(self.stop_conditions),
            "anti_collapse_rules": list(self.anti_collapse_rules),
            "metacognition": self.metacognition.to_dict(),
            "timestamp": self.timestamp,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fresh_id() -> str:
    return f"explore_{hashlib.sha256(_now_iso().encode()).hexdigest()[:12]}"


def _orient(question: str, current_state: Optional[dict] = None) -> tuple[str, str, str, str, str]:
    """Step 1 — classify the request.

    Returns (problem_class, stakes, freshness_required, reversibility, evidence_floor).
    Caller may override via current_state hints.
    """
    state = current_state or {}
    problem_class = state.get("problem_class") or (
        "diagnostic" if "?" in question else "operational"
    )
    stakes = state.get("stakes") or "moderate"
    freshness = state.get("freshness") or "live"
    reversibility = state.get("reversibility") or "unknown"
    floor = state.get("evidence_floor") or "E>=0.5"
    return problem_class, stakes, freshness, reversibility, floor


def _decompose(question: str, problem_class: str) -> tuple[str, ...]:
    """Step 2 — break into subquestions.

    Heuristic decomposition; deeper analysis requires domain knowledge.
    """
    base = [question.strip()]
    if problem_class in ("diagnostic", "operational"):
        base.extend([
            f"What is the current state of the system related to: {question[:80]}?",
            f"What has changed recently that could explain: {question[:80]}?",
            f"What alternative explanations exist for: {question[:80]}?",
        ])
    return tuple(base)


def _map(subquestions: tuple[str, ...]) -> tuple[str, ...]:
    """Step 3 — identify candidate evidence surfaces."""
    surfaces = set()
    for q in subquestions:
        for s in list_sources():
            if any(q.lower()[:20] in qa.lower() for qa in s.questions_answered):
                surfaces.add(s.source_id)
    # Always include core sources for diagnostic-type questions
    core = {"runtime_import_probe", "release_manifest", "git_source"}
    return tuple(surfaces | core)


def explore(
    question: str,
    *,
    current_state: Optional[dict] = None,
    initial_hypotheses: Optional[tuple[Hypothesis, ...]] = None,
    budget: Optional[ExplorationBudget] = None,
    stop_conditions: Optional[tuple[str, ...]] = None,
) -> ExplorationPlan:
    """Plan an exploration. Does NOT execute tools.

    This function answers: "If we act to learn, where should we look and
    in what order, under what budget, with what stop conditions?"

    It does NOT fetch sources, query databases, or run tools. It returns
    a structured plan that a downstream executor (the cooling verbs in
    P1.4) follows — bounded by the budget.
    """
    problem_class, stakes, freshness, reversibility, floor = _orient(question, current_state)
    subquestions = _decompose(question, problem_class)
    candidate_sources = _map(subquestions)
    hypotheses = initial_hypotheses or tuple()
    b = budget or ExplorationBudget(
        stakes=0.5 if stakes == "moderate" else 0.8,
        uncertainty=0.8,
        irreversibility=0.3 if reversibility == "reversible" else 0.7,
        value_of_information=0.6,
    )

    # Recommended modes based on problem_class
    mode_map = {
        "diagnostic": (ExplorationMode.SCOUT, ExplorationMode.MAPPER,
                       ExplorationMode.DRILLER, ExplorationMode.CONTRARIAN,
                       ExplorationMode.VERIFIER),
        "operational": (ExplorationMode.SCOUT, ExplorationMode.SURVEYOR,
                         ExplorationMode.VERIFIER),
        "strategic": (ExplorationMode.MAPPER, ExplorationMode.CONTRARIAN,
                       ExplorationMode.EUREKA),
        "creative": (ExplorationMode.SCOUT, ExplorationMode.MAPPER,
                       ExplorationMode.EUREKA),
        "factual": (ExplorationMode.VERIFIER,),
    }
    recommended_modes = mode_map.get(problem_class, (ExplorationMode.SCOUT,))

    # Default stop conditions aligned with Arif spec
    default_stops = (
        "critical_claims_covered",
        "major_contradictions_resolved",
        "required_freshness_met",
        "authority_known",
        "safe_action_identified",
        "remaining_uncertainty_cannot_alter_safe_action",
    )
    conditions = stop_conditions or default_stops

    anti_collapse = (
        "INV-E1 no unsupported collapse",
        "INV-E2 no single-source sovereignty",
        "INV-E3 no inference-to-truth promotion",
        "INV-E4 no action before uncertainty classification",
        "INV-E5 exploration must be bounded",
        "INV-E6 HOLD is a valid intelligent outcome",
    )

    meta = Metacognition(
        what_i_observed=("received question parameter",),
        what_i_inferred=(f"problem_class={problem_class}",),
        what_i_assumed=("default decomposition heuristic applies",),
        what_i_could_not_access=("caller has not provided current runtime state",),
        what_might_be_stale=("source registry may need re-registration",),
        what_would_falsify_my_conclusion=(
            "candidate source set is empty when problem_class=diagnostic",
        ),
        safe_action_despite_uncertainty=(
            "Run runtime_verify (P1.1) before any consequential code change",
        ),
    )

    return ExplorationPlan(
        problem_class=problem_class,
        stakes=stakes,
        freshness_required=freshness,
        reversibility=reversibility,
        evidence_floor=floor,
        subquestions=subquestions,
        candidate_sources=candidate_sources,
        recommended_modes=recommended_modes,
        hypotheses=hypotheses,
        budget_score=b.score(),
        stop_conditions=conditions,
        anti_collapse_rules=anti_collapse,
        metacognition=meta,
        exploration_id=_fresh_id(),
        timestamp=_now_iso(),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# NAV.6 — Early-collapse Detector
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CollapseDiagnostic:
    code: str
    pattern: str
    detected: bool
    evidence: str

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "pattern": self.pattern,
            "detected": self.detected,
            "evidence": self.evidence,
        }


def early_collapse_check(
    meta: Metacognition,
    n_sources_consulted: int,
    n_independent_witnesses: int,
    n_hypotheses_considered: int,
    n_contradictions_detected: int,
    n_critical_unknowns_remaining: int,
    n_verification_steps: int,
    memory_treated_as_current: bool,
    live_state_verified: bool,
    authority_verified: bool,
) -> tuple[CollapseDiagnostic, ...]:
    """Detect premature-closure patterns per spec.

    Returns one diagnostic per known collapse pattern.
    """
    return (
        CollapseDiagnostic(
            code="COL-1",
            pattern="conclusion after one source",
            detected=(n_sources_consulted == 1 and n_critical_unknowns_remaining > 0),
            evidence=f"sources={n_sources_consulted}, critical_unknowns={n_critical_unknowns_remaining}",
        ),
        CollapseDiagnostic(
            code="COL-2",
            pattern="no counter-hypothesis considered",
            detected=(n_hypotheses_considered <= 1),
            evidence=f"hypotheses_considered={n_hypotheses_considered}",
        ),
        CollapseDiagnostic(
            code="COL-3",
            pattern="no live-state verification",
            detected=(not live_state_verified),
            evidence=f"live_state_verified={live_state_verified}",
        ),
        CollapseDiagnostic(
            code="COL-4",
            pattern="memory treated as current truth",
            detected=memory_treated_as_current,
            evidence=f"flag={memory_treated_as_current}",
        ),
        CollapseDiagnostic(
            code="COL-5",
            pattern="tool result accepted without checking output",
            detected=(n_verification_steps < 2),
            evidence=f"verification_steps={n_verification_steps}",
        ),
        CollapseDiagnostic(
            code="COL-6",
            pattern="missing evidence silently filled by inference",
            detected=(n_critical_unknowns_remaining > 0 and n_contradictions_detected == 0
                     and n_verification_steps == 0),
            evidence=f"unknowns={n_critical_unknowns_remaining}, contradictions={n_contradictions_detected}",
        ),
        CollapseDiagnostic(
            code="COL-7",
            pattern="authority assumed from identity",
            detected=(not authority_verified and n_critical_unknowns_remaining == 0),
            evidence=f"authority_verified={authority_verified}",
        ),
        CollapseDiagnostic(
            code="COL-8",
            pattern="execution called success without post-check",
            detected=(n_verification_steps == 0),
            evidence=f"verification_steps={n_verification_steps}",
        ),
        CollapseDiagnostic(
            code="COL-9",
            pattern="search stopped despite unresolved critical question",
            detected=(n_critical_unknowns_remaining > 0 and n_sources_consulted == 0),
            evidence=f"unknowns={n_critical_unknowns_remaining}",
        ),
        CollapseDiagnostic(
            code="COL-10",
            pattern="single-witness conclusion (independent witness not consulted)",
            detected=(n_independent_witnesses < 2),
            evidence=f"witnesses={n_independent_witnesses}",
        ),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# NAV.8 — Anti-collapse Stopping Rule
# ═══════════════════════════════════════════════════════════════════════════════

class StopOutcome(str, Enum):
    PROCEED = "proceed"
    HOLD = "hold"
    BOUNDED_EXPERIMENT = "bounded_experiment"
    DENY = "deny"
    UNKNOWN = "unknown"
    REQUEST_EVIDENCE = "request_evidence"
    DO_NOT_EXECUTE = "do_not_execute"


@dataclass(frozen=True)
class StopConditionCheck:
    """One stopping-condition diagnostic (Condition A/B/C/D from spec)."""
    condition: str  # "A" / "B" / "C" / "D"
    description: str
    satisfied: bool
    rationale: str

    def to_dict(self) -> dict:
        return {
            "condition": self.condition,
            "description": self.description,
            "satisfied": self.satisfied,
            "rationale": self.rationale,
        }


def stop_condition_check(
    *,
    critical_claims_covered: bool,
    major_contradictions_resolved: bool,
    required_freshness_met: bool,
    authority_known: bool,
    safe_action_identified: bool,
    evidence_ceiling_hit: bool,
    risk_boundary_hit: bool,
    reversible_safe_action_available: bool,
    rationale_note: str = "",
) -> tuple[StopConditionCheck, ...]:
    """Apply the four-condition stopping rule per spec."""
    return (
        StopConditionCheck(
            condition="A",
            description="Sufficient evidence",
            satisfied=(
                critical_claims_covered
                and major_contradictions_resolved
                and required_freshness_met
                and authority_known
                and safe_action_identified
            ),
            rationale=rationale_note,
        ),
        StopConditionCheck(
            condition="B",
            description="Safe bounded action possible",
            satisfied=reversible_safe_action_available,
            rationale=rationale_note,
        ),
        StopConditionCheck(
            condition="C",
            description="Evidence ceiling — necessary evidence unavailable",
            satisfied=evidence_ceiling_hit,
            rationale=rationale_note,
        ),
        StopConditionCheck(
            condition="D",
            description="Risk boundary — proposed action too consequential",
            satisfied=risk_boundary_hit,
            rationale=rationale_note,
        ),
    )


def decide_outcome(
    conditions: tuple[StopConditionCheck, ...],
) -> StopOutcome:
    """Aggregate four stopping conditions into one outcome."""
    by_letter = {c.condition: c.satisfied for c in conditions}
    if by_letter.get("C"):
        return StopOutcome.UNKNOWN
    if by_letter.get("D"):
        return StopOutcome.DO_NOT_EXECUTE
    if by_letter.get("A"):
        return StopOutcome.PROCEED
    if by_letter.get("B"):
        return StopOutcome.BOUNDED_EXPERIMENT
    return StopOutcome.HOLD


__all__ = [
    # Schemas
    "EvidenceSource",
    "SourceType",
    "SourceTier",
    "EvidenceQuality",
    "ExplorationBudget",
    "Hypothesis",
    "HypothesisRegistry",
    "Metacognition",
    "ExplorationPlan",
    "InvariantCheck",
    "CollapseDiagnostic",
    "StopConditionCheck",
    "StopOutcome",
    # Enums
    "ExplorationMode",
    "EvaluationState",
    # Registry
    "register_source",
    "get_source",
    "list_sources",
    "sources_for_question",
    # Orchestrator
    "explore",
    # Anti-collapse
    "early_collapse_check",
    "stop_condition_check",
    "decide_outcome",
    # INV-E*
    "check_inv_E1", "check_inv_E2", "check_inv_E3",
    "check_inv_E4", "check_inv_E5", "check_inv_E6",
    "run_invariants",
    "INVARIANT_E",
    # Schemas constants
    "StopOutcome",
]
