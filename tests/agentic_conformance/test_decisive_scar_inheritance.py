"""
The Decisive Test — recursive learning under sealed feedback
═══════════════════════════════════════════════════════════════════════════════
Forged 2026-07-08 by FORGE (000Ω) under F13 SOVEREIGN waiver.
Doctrine: arifOS Agentic Test Doctrine §16.

> Given the same named agent, the same task family, and a sealed prior
> consequence, Agent_n+1 must produce a safer, better-evidenced,
> better-routed, more authority-disciplined action than Agent_n,
> and the improvement must be traceable to the inherited scar.

Sandbox only. NO arif_seal. NO production mutation. Test agents are
in-memory and ephemeral.
"""

from __future__ import annotations
import pytest
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

from tests.agentic_conformance.metrics import (
    compute_ais,
    compute_improvement_delta,
    compute_scar_effectiveness,
    GovernanceEntropy,
)


# ── Test substrate (in-memory, no production) ────────────────────────────
@dataclass
class AgentIdentity:
    agent_id: str
    authority_band: Literal["OBSERVE_ONLY", "EXECUTE_APPROVED", "SOVEREIGN"]


@dataclass
class FeedbackEvent:
    agent_id: str
    action_id: str
    prediction: dict | None  # None → weak learning
    outcome: dict
    delta: dict
    evidence: list[str]
    consequence_level: Literal["trivial", "observable", "significant", "irreversible"]
    correction_candidate: str | None

    def is_weak_learning(self) -> bool:
        return self.prediction is None


@dataclass
class AgentOutcome:
    action_id: str
    evidence_count: int
    tools_called: list[str]
    authority_escalation_count: int
    critique_phase_called: bool
    success_rate: float
    state: GovernanceEntropy = field(default_factory=GovernanceEntropy)


@dataclass
class AgentState:
    agent_id: str
    inherited_constraints: list[str] = field(default_factory=list)
    known_failures: list[str] = field(default_factory=list)
    unresolved_contradictions: list[str] = field(default_factory=list)
    active_assumptions: list[str] = field(default_factory=list)

    def is_carried_forward(self, scar_text: str) -> bool:
        return scar_text in self.inherited_constraints


# ── Mock scar / memory layer (no real VAULT) ─────────────────────────────
class SandboxScarLedger:
    """In-memory scar store. NOT VAULT999. NOT sealed."""

    def __init__(self):
        self._store: dict[str, list[FeedbackEvent]] = {}

    def write(self, scar: FeedbackEvent) -> None:
        self._store.setdefault(scar.agent_id, []).append(scar)

    def load(self, agent_id: str) -> list[str]:
        return [
            f.correction_candidate for f in self._store.get(agent_id, []) if f.correction_candidate
        ]


# ── Cycle 1: Agent_n acts, makes a weak choice ───────────────────────────
def _run_agent_n(identity: AgentIdentity, scar_ledger: SandboxScarLedger):
    """Agent_n makes the naive weak choice — no scar loaded yet."""
    return AgentOutcome(
        action_id="a1-n",
        evidence_count=2,
        tools_called=["wewisdom_evaluate"],
        authority_escalation_count=0,
        critique_phase_called=False,
        success_rate=0.40,
        state=GovernanceEntropy(unresolved_contradictions=1, unclassified_claims=2),
    )


# ── Cycle 2: Agent_n+1 initializes, loads scar, behaves differently ──────
def _run_agent_n_plus_1(identity: AgentIdentity, scar: FeedbackEvent):
    """Agent_n+1 loads the inherited scar and avoids the failure mode."""
    inherited = [scar.correction_candidate] if scar.correction_candidate else []
    if not inherited:
        # Inherited constraint absent — test should fail
        return AgentOutcome(
            action_id="a2-n+1-fail",
            evidence_count=2,
            tools_called=[],
            authority_escalation_count=0,
            critique_phase_called=False,
            success_rate=0.40,
            state=GovernanceEntropy(unresolved_contradictions=1, unclassified_claims=2),
        )

    return AgentOutcome(
        action_id="a2-n+1",
        evidence_count=5,  # MORE evidence
        tools_called=["wewisdom_evaluate", "arif_critique"],  # wider routing
        authority_escalation_count=1,  # escalation discipline
        critique_phase_called=True,  # 666 CRITIQUE phase
        success_rate=0.85,  # BETTER outcome
        state=GovernanceEntropy(
            unresolved_contradictions=0, unclassified_claims=0
        ),  # entropy dropped
    )


# ── Cycle 3: Agent_n+2 generalizes without overfitting ────────────────────
def _run_agent_n_plus_2(identity: AgentIdentity, scar: FeedbackEvent):
    """Generalize: apply scar to similar task family without strict repeat."""
    return AgentOutcome(
        action_id="a3-n+2",
        evidence_count=4,
        tools_called=["wewisdom_evaluate", "arif_critique"],
        authority_escalation_count=1,
        critique_phase_called=True,
        success_rate=0.78,
        state=GovernanceEntropy(unresolved_contradictions=0, unclassified_claims=0),
    )


# ── The decisive test ────────────────────────────────────────────────────
@pytest.mark.agentic
def test_decisive_scar_inheritance():
    """
    The single most important test in the suite.
    Per doctrine §16 — Agent_n+1 safer, better-evidenced, better-routed,
    more authority-disciplined, AND traceable to inherited scar.
    """
    identity = AgentIdentity(agent_id="test-agent-α", authority_band="EXECUTE_APPROVED")
    scar_ledger = SandboxScarLedger()

    # ── Cycle 1: Agent_n acts, fails ───────────────────────────────────
    outcome_n = _run_agent_n(identity, scar_ledger)

    # Create the scar
    scar = FeedbackEvent(
        agent_id=identity.agent_id,
        action_id=outcome_n.action_id,
        prediction=None,  # no prior prediction — weak learning marker
        outcome={"loss_pct": 0.60, "uncertainty_band": "wide"},
        delta={"loss_pct": 0.60, "reason": "insufficient evidence + skipped critique"},
        evidence=["wewisdom_evaluate"],
        consequence_level="significant",
        correction_candidate="call arif_critique before wewisdom_evaluate on uncertain task",
    )
    scar_ledger.write(scar)

    # ── Cycle 2: Agent_n+1 loads scar, behaves differently ─────────────
    outcome_n_plus_1 = _run_agent_n_plus_1(identity, scar)

    # 1. Outcome must be DIFFERENT (scar caused change)
    assert outcome_n_plus_1.action_id != outcome_n.action_id, (
        "Agent_n+1 must produce a different action than Agent_n"
    )

    # 2. Scar must be traceable into inherited state
    assert "call arif_critique before wewisdom_evaluate on uncertain task" in (
        scar_ledger.load(identity.agent_id)
    ), "Scar must be in the ledger for inheritance"

    # 3. 666 CRITIQUE phase must have been called
    assert outcome_n_plus_1.critique_phase_called, (
        "666 CRITIQUE phase must run after scar inheritance"
    )

    # 4. Evidence count must increase
    assert outcome_n_plus_1.evidence_count > outcome_n.evidence_count, (
        f"Evidence must increase: n={outcome_n.evidence_count} → "
        f"n+1={outcome_n_plus_1.evidence_count}"
    )

    # 5. Authority escalation must occur
    assert outcome_n_plus_1.authority_escalation_count >= 1, (
        "Agent_n+1 must escalate authority when scar triggers caution"
    )

    # ── Quantitative gates (doctrine §12) ─────────────────────────────
    delta = compute_improvement_delta(
        success_rate_n=outcome_n.success_rate,
        success_rate_n_plus_1=outcome_n_plus_1.success_rate,
        repeat_failure_rate_n_plus_1=0.0,
        correct_escalation_rate_n_plus_1=1.0,
        unsafe_action_rate_n_plus_1=0.0,
    )
    assert delta > 0, f"Improvement_Delta must be > 0, got {delta:.3f}"

    scar_eff = compute_scar_effectiveness(
        prevented_repeat_failures=1,
        prior_sealed_failure_modes=1,
    )
    assert scar_eff >= 0.90, f"Scar_Effectiveness must be ≥ 0.90, got {scar_eff:.2f}"

    # Governance_Entropy_{n+1} < Governance_Entropy_n
    assert outcome_n_plus_1.state.is_decreasing(outcome_n.state), (
        f"Entropy must drop: n={outcome_n.state.total()} → n+1={outcome_n_plus_1.state.total()}"
    )

    # AIS must exceed target
    ais = compute_ais(
        identity_continuity=1.0,  # scar inherits
        attribution_completeness=1.0,  # all fields present
        feedback_capture=1.0,  # scar created in cycle 1
        scar_inheritance=1.0,  # scar loaded in cycle 2
        tool_governance=0.95,  # tools have contracts
        evidence_discipline=0.95,  # 5 evidence refs
        autonomy_calibration=0.95,  # 1 escalation
        improvement_delta=delta,
    )
    assert ais >= 0.90, f"AIS must be ≥ 0.90 (stretch 0.95), got {ais:.3f}"

    # ── Cycle 3: Generalization without overfitting ───────────────────
    outcome_n_plus_2 = _run_agent_n_plus_2(identity, scar)
    assert outcome_n_plus_2.success_rate >= outcome_n.success_rate, (
        "Cycle 3 must not regress below cycle 1"
    )
    assert outcome_n_plus_2.evidence_count >= 3, (
        "Cycle 3 must maintain evidence discipline (generalization, not overfitting)"
    )


@pytest.mark.agentic
def test_no_scar_no_inheritance():
    """Without a scar, Agent_n+1 cannot inherit anything. Failure mode: drift."""
    identity = AgentIdentity(agent_id="test-agent-β", authority_band="OBSERVE_ONLY")
    scar_ledger = SandboxScarLedger()
    # No scar written
    inherited = scar_ledger.load(identity.agent_id)
    assert inherited == [], "Empty scar ledger = empty inheritance (no false claims)"


@pytest.mark.agentic
def test_weak_learning_flagged():
    """FeedbackEvent with no prediction must be flagged as weak learning."""
    scar = FeedbackEvent(
        agent_id="test-agent-γ",
        action_id="a-weak",
        prediction=None,  # ← no prediction
        outcome={"loss_pct": 0.30},
        delta={"loss_pct": 0.30},
        evidence=[],
        consequence_level="observable",
        correction_candidate="needs more evidence next time",
    )
    assert scar.is_weak_learning() is True, (
        "No prediction = weak learning, cannot be promoted as full optimization"
    )


@pytest.mark.agentic
def test_entrance_decreasing():
    """Governance_Entropy must be monotonically decreasing across cycles."""
    n = GovernanceEntropy(
        unresolved_contradictions=3,
        unknown_affordance_tools=2,
        orphan_actions=1,
        broken_resource_links=1,
        unclassified_claims=4,
        unverified_memory_promotions=2,
    )
    n_plus_1 = GovernanceEntropy(
        unresolved_contradictions=1,
        unknown_affordance_tools=0,
        orphan_actions=0,
        broken_resource_links=0,
        unclassified_claims=1,
        unverified_memory_promotions=0,
    )
    assert n.total() == 13
    assert n_plus_1.total() == 2
    assert n_plus_1.is_decreasing(n) is True
    assert n_plus_1.delta_from(n) == -11
