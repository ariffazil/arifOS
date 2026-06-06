"""
Experiment Loop — Item 5 of the Organ Forge
═══════════════════════════════════════════

A single `experiment_id` threads together the four stages of
grounded intelligence:

  1. PROBE    — A-FORGE executes a small reversible test
  2. OBSERVE  — GEOX/WEALTH/WELL return measurements (envelope-wrapped)
  3. COMPARE  — Diff against prior belief (the experiment card)
  4. UPDATE   — arifOS judges: did evidence change belief state?
                 - YES → write to L3/L4 (memory policy gates this)
                 - NO  → close, record null result
                 - CONTRADICTION → trigger contradiction memory

You don't need a new "scientist organ." Each existing organ plays
its role in the loop. The experiment_card is the shared thread.

DITEMPA BUKAN DIBERI — belief changes by evidence, not by declaration.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from arifosmcp.schemas.envelope import EvidenceEnvelope

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT CARD — the shared thread
# ═══════════════════════════════════════════════════════════════════════════════


class ExperimentStage(StrEnum):
    PROBE = "PROBE"
    OBSERVE = "OBSERVE"
    COMPARE = "COMPARE"
    UPDATE = "UPDATE"
    CLOSED = "CLOSED"


class ExperimentVerdict(StrEnum):
    """What the UPDATE stage concluded."""

    BELIEF_CONFIRMED = "BELIEF_CONFIRMED"
    BELIEF_REVISED = "BELIEF_REVISED"
    BELIEF_REJECTED = "BELIEF_REJECTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    CONTRADICTION = "CONTRADICTION"


class Hypothesis(BaseModel):
    """The claim being tested."""

    text: str
    prior_belief: float = Field(0.5, ge=0.0, le=1.0, description="Prior confidence in [0,1]")
    falsifier: str = Field(..., description="What outcome would DISPROVE this hypothesis")
    domain: str = "general"
    organ: str = "unknown"


class ProbeSpec(BaseModel):
    """What the PROBE stage actually does."""

    tool: str
    args: dict[str, Any] = Field(default_factory=dict)
    reversibility: str = "REVERSIBLE"
    cost_estimate: Optional[dict[str, Any]] = None
    expected_signal: str = ""


class Observation(BaseModel):
    """A single OBSERVE measurement (envelope-wrapped)."""

    organ: str
    envelope: EvidenceEnvelope


class CompareResult(BaseModel):
    """Result of COMPARE stage."""

    delta_belief: float = Field(0.0, description="Change in confidence, in [-1, +1]")
    surprise: float = Field(0.0, ge=0.0, description="Information-theoretic surprise")
    matches_hypothesis: bool = True
    notes: str = ""


class ExperimentCard(BaseModel):
    """The shared thread for one experiment."""

    experiment_id: str = Field(default_factory=lambda: f"exp_{uuid4().hex[:12]}")
    hypothesis: Hypothesis
    probe: ProbeSpec
    stage: ExperimentStage = ExperimentStage.PROBE
    observations: list[Observation] = Field(default_factory=list)
    compare: Optional[CompareResult] = None
    verdict: Optional[ExperimentVerdict] = None
    opened_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    closed_at: Optional[datetime] = None
    actor_id: str = "system"
    session_id: Optional[str] = None
    parents: list[str] = Field(default_factory=list, description="Prior experiment_ids this builds on")
    content_hash: str = ""

    def recompute_hash(self) -> str:
        canon = json.dumps(
            {
                "experiment_id": self.experiment_id,
                "hypothesis": self.hypothesis.model_dump(),
                "probe": self.probe.model_dump(),
                "stage": self.stage.value,
                "n_observations": len(self.observations),
                "compare": self.compare.model_dump() if self.compare else None,
                "verdict": self.verdict.value if self.verdict else None,
                "parents": self.parents,
            },
            sort_keys=True,
        )
        self.content_hash = hashlib.sha256(canon.encode()).hexdigest()[:16]
        return self.content_hash


# ═══════════════════════════════════════════════════════════════════════════════
# THE LOOP — pure functions, no I/O. Organs wire the actual execution.
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class LoopContext:
    """The organ-side bindings."""

    actor_id: str
    session_id: Optional[str] = None
    on_write_to_L3: Any = None  # callable(envelope) -> decision
    on_write_to_L4: Any = None
    on_contradiction: Any = None  # callable(artifact_ref, envelope) -> None


def open_experiment(
    *,
    hypothesis: Hypothesis,
    probe: ProbeSpec,
    actor_id: str,
    session_id: Optional[str] = None,
    parents: Optional[list[str]] = None,
) -> ExperimentCard:
    """Begin a new experiment. Returns the card at PROBE stage."""
    card = ExperimentCard(
        hypothesis=hypothesis,
        probe=probe,
        actor_id=actor_id,
        session_id=session_id,
        parents=parents or [],
    )
    card.recompute_hash()
    logger.info(f"experiment {card.experiment_id} opened: {hypothesis.text[:60]}")
    return card


def observe(card: ExperimentCard, envelope: EvidenceEnvelope) -> ExperimentCard:
    """Record an observation. Advances PROBE → OBSERVE."""
    if card.stage not in (ExperimentStage.PROBE, ExperimentStage.OBSERVE):
        raise ValueError(f"Cannot observe at stage {card.stage.value}")
    obs = Observation(organ=envelope.source.organ, envelope=envelope)
    card.observations.append(obs)
    card.stage = ExperimentStage.OBSERVE
    card.recompute_hash()
    return card


def compare(card: ExperimentCard, prior_belief: Optional[float] = None) -> ExperimentCard:
    """Compute the diff. Advances OBSERVE → COMPARE.

    Surprise = how far observations are from the predicted signal.
    delta_belief = change in confidence (sign: +confirming, -disconfirming).
    """
    if card.stage != ExperimentStage.OBSERVE:
        raise ValueError(f"Cannot compare at stage {card.stage.value}")
    if not card.observations:
        card.compare = CompareResult(
            delta_belief=0.0, surprise=0.0, matches_hypothesis=False, notes="No observations"
        )
    else:
        # Mean quality of observations as crude signal
        qualities = [o.envelope.evidence_quality for o in card.observations]
        mean_q = sum(qualities) / len(qualities)
        # Surprise: variance across observations
        if len(qualities) > 1:
            mean = sum(qualities) / len(qualities)
            variance = sum((q - mean) ** 2 for q in qualities) / len(qualities)
        else:
            variance = 0.0
        surprise = min(1.0, variance + (1.0 - mean_q) * 0.1)
        # Δ belief heuristic: high quality + low surprise → positive
        delta = (mean_q - 0.5) * 0.5 - surprise * 0.3
        prior = prior_belief if prior_belief is not None else card.hypothesis.prior_belief
        # Matches hypothesis: positive delta when prior > 0.5 (we expected confirm)
        matches = (delta >= 0) == (prior >= 0.5)
        card.compare = CompareResult(
            delta_belief=round(delta, 4),
            surprise=round(surprise, 4),
            matches_hypothesis=matches,
            notes=f"mean_quality={mean_q:.3f} variance={variance:.3f}",
        )
    card.stage = ExperimentStage.COMPARE
    card.recompute_hash()
    return card


def update(
    card: ExperimentCard,
    ctx: LoopContext,
    contradiction_check: bool = True,
) -> ExperimentCard:
    """Decide what changed. Advances COMPARE → UPDATE → CLOSED.

    Side effects (if hooks set):
      - on_write_to_L3 / on_write_to_L4  — promote observations to memory
      - on_contradiction                  — register disagreement
    """
    if card.stage != ExperimentStage.COMPARE:
        raise ValueError(f"Cannot update at stage {card.stage.value}")
    assert card.compare is not None

    # Detect contradiction: observations that contradict the hypothesis
    has_contradiction = False
    if contradiction_check and card.compare.delta_belief < -0.2:
        # Strong disconfirmation
        for obs in card.observations:
            if obs.envelope.has_contradictions():
                has_contradiction = True
                break
            # Falsifier check: if observation label is FACT and disconfirms
            if obs.envelope.epistemic_tag.value == "FACT" and card.compare.delta_belief < -0.1:
                has_contradiction = True
                break

    if has_contradiction:
        card.verdict = ExperimentVerdict.CONTRADICTION
        if ctx.on_contradiction:
            for obs in card.observations:
                ctx.on_contradiction(card.experiment_id, obs.envelope)
    elif card.compare.matches_hypothesis and card.compare.delta_belief >= 0:
        card.verdict = ExperimentVerdict.BELIEF_CONFIRMED
    elif not card.compare.matches_hypothesis and card.compare.delta_belief < 0:
        card.verdict = ExperimentVerdict.BELIEF_REVISED
    elif abs(card.compare.delta_belief) < 0.05:
        card.verdict = ExperimentVerdict.INCONCLUSIVE
    else:
        card.verdict = ExperimentVerdict.BELIEF_CONFIRMED

    card.stage = ExperimentStage.UPDATE

    # Side effect: promote observations to memory if revised/confirmed
    if card.verdict in (ExperimentVerdict.BELIEF_CONFIRMED, ExperimentVerdict.BELIEF_REVISED):
        for obs in card.observations:
            if ctx.on_write_to_L3:
                ctx.on_write_to_L3(obs.envelope)
            if obs.envelope.evidence_quality >= 0.85 and ctx.on_write_to_L4:
                ctx.on_write_to_L4(obs.envelope)

    card.stage = ExperimentStage.CLOSED
    card.closed_at = datetime.now(UTC)
    card.recompute_hash()
    logger.info(
        f"experiment {card.experiment_id} closed: {card.verdict.value} "
        f"(Δ={card.compare.delta_belief:+.3f}, surprise={card.compare.surprise:.3f})"
    )
    return card


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE — one-call experiment for simple cases
# ═══════════════════════════════════════════════════════════════════════════════


def run_simple_experiment(
    hypothesis: Hypothesis,
    probe: ProbeSpec,
    observations: list[EvidenceEnvelope],
    ctx: LoopContext,
) -> ExperimentCard:
    """One-call: open → observe → compare → update → close."""
    card = open_experiment(
        hypothesis=hypothesis,
        probe=probe,
        actor_id=ctx.actor_id,
        session_id=ctx.session_id,
    )
    for env in observations:
        observe(card, env)
    compare(card)
    update(card, ctx)
    return card
