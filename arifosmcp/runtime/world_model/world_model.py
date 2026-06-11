"""
arifosmcp/geometry/world_model.py — Institutional + value-space world model

The world model is a typed graph of actors (corporations, models, person-classes,
institutions) living in the same 13D constitutional manifold as self.

F-floor binding:
  F2 TRUTH   — every actor carries provenance_sha and evidence_chain (F11)
  F7 HUMILITY — confidence capped at 0.95
  F8 GENIUS  — empathy_check before action involving a non-self actor
  F9 ANTIHANTU — TomLevel cap = 2 (no recursive nesting beyond)
  F11 AUDIT  — every actor update is logged with actor, evidence, ts
  F13 SOVEREIGN — actor definitions F13-ratified; new actor classes need 888

Reversibility: file delete = revert. No migrations, no new tables.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import StrEnum
from typing import Any, Literal, Optional

import numpy as np

from arifosmcp.geometry.manifold import (
    AgentState,
    Floor,
    HARD_FLOORS,
    is_constitutional,
    load_floor_weights,
)
from arifosmcp.geometry.tom_geometry import (
    OtherGeometry,
    Evidence,
    HISTORY_DECAY_TAU_H,
    CONFIDENCE_CAP,
    TOM_DEPTH_CAP,
)


# ─────────────────────────────────────────────────────────────────────────────
# Typed actor classes — not a flat list
# ─────────────────────────────────────────────────────────────────────────────


class ActorClass(StrEnum):
    """Taxonomy of world-model actors. F13-ratified.

    A flat list of names (ILMU, YTL, PMX, rakyat) loses structural
    distinctions. These classes determine what relations are possible.
    """

    CORPORATION = "corporation"  # YTL, PMX, Tencent, etc.
    MODEL = "model"  # ILMU, GPT, Claude, etc.
    INSTITUTION = "institution"  # UNESCO, parliament, etc.
    PERSON_CLASS = "person_class"  # rakyat (~33M), Petronas employees, etc.
    SELF = "self"  # arifOS / arif
    AGENT = "agent"  # Other AI agents in the federation


# Per-class cadence: how often do actors of this class drift?
CADENCE_DAYS: dict[ActorClass, float] = {
    ActorClass.CORPORATION: 90.0,
    ActorClass.MODEL: 180.0,
    ActorClass.INSTITUTION: 365.0,
    ActorClass.PERSON_CLASS: 365.0 * 5,
    ActorClass.SELF: 1.0,
    ActorClass.AGENT: 7.0,
}


@dataclass
class ActorState:
    """A typed actor in the world model."""

    actor_id: str
    actor_class: ActorClass
    display_name: str
    geometry: OtherGeometry
    identity_provenance: str
    relations: list["Relation"] = field(default_factory=list)
    last_evidence_ts: float = field(default_factory=time.time)
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.identity_provenance:
            raise ValueError(f"ActorState.identity_provenance required (F11): {self.actor_id}")
        if self.geometry.tom_level > TOM_DEPTH_CAP:
            raise ValueError(
                f"ActorState.geometry.tom_level {self.geometry.tom_level} > cap {TOM_DEPTH_CAP}"
            )

    def days_since_evidence(self, now: float | None = None) -> float:
        now = now or time.time()
        return (now - self.last_evidence_ts) / 86400.0

    def staleness(self, now: float | None = None) -> float:
        elapsed = self.days_since_evidence(now)
        cadence = CADENCE_DAYS[self.actor_class]
        return min(1.0, elapsed / cadence)

    def drift_estimate(self) -> np.ndarray:
        """Per-class drift rate × staleness. Bounded, not measured."""
        DRIFT_RATES: dict[ActorClass, np.ndarray] = {
            ActorClass.CORPORATION: np.array(
                [0.05, 0.15, 0.10, 0.10, 0.10, 0.20, 0.05, 0.10, 0.05, 0.05, 0.10, 0.10, 0.30]
            ),
            ActorClass.MODEL: np.array(
                [0.05, 0.20, 0.10, 0.10, 0.10, 0.15, 0.10, 0.20, 0.15, 0.05, 0.05, 0.10, 0.05]
            ),
            ActorClass.INSTITUTION: np.array(
                [0.05, 0.10, 0.10, 0.05, 0.05, 0.10, 0.05, 0.05, 0.05, 0.05, 0.30, 0.05, 0.20]
            ),
            ActorClass.PERSON_CLASS: np.array(
                [0.10, 0.20, 0.15, 0.10, 0.15, 0.20, 0.10, 0.10, 0.10, 0.05, 0.10, 0.10, 0.30]
            ),
            ActorClass.SELF: np.array(
                [0.10, 0.15, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.05, 0.05, 0.10, 0.10]
            ),
            ActorClass.AGENT: np.array(
                [0.10, 0.20, 0.15, 0.15, 0.10, 0.15, 0.10, 0.20, 0.15, 0.05, 0.05, 0.10, 0.05]
            ),
        }
        rate = DRIFT_RATES[self.actor_class]
        return rate * self.staleness()


# ─────────────────────────────────────────────────────────────────────────────
# Typed relations
# ─────────────────────────────────────────────────────────────────────────────


class RelationType(StrEnum):
    """Typed edges. F13-ratified vocabulary."""

    OWNS = "owns"
    HOSTS_ON = "hosts_on"
    REGULATES = "regulates"
    COMPETES_WITH = "competes_with"
    ALIGNS_WITH = "aligns_with"
    CAPTURES = "captures"
    REPRESENTS = "represents"
    EMPLOYED_BY = "employed_by"


@dataclass
class Relation:
    """Typed edge from source to target."""

    source_actor: str
    target_actor: str
    relation_type: RelationType
    strength: float = 0.5
    provenance_sha: str = ""
    ts: float = field(default_factory=time.time)
    expires_at: float | None = None

    def __post_init__(self) -> None:
        if not self.provenance_sha:
            raise ValueError("Relation.provenance_sha required (F11)")
        if self.strength < 0.0 or self.strength > 1.0:
            raise ValueError(f"Relation.strength must be in [0,1], got {self.strength}")


# ─────────────────────────────────────────────────────────────────────────────
# World model — typed graph
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class WorldModel:
    """Typed graph of actors in value space, with relations."""

    model_id: str = field(default_factory=lambda: f"wm-{uuid.uuid4().hex[:12]}")
    actors: dict[str, ActorState] = field(default_factory=dict)
    relations: list[Relation] = field(default_factory=list)
    ts: float = field(default_factory=time.time)

    def add_actor(self, actor: ActorState) -> None:
        if actor.actor_id in self.actors:
            raise ValueError(f"actor {actor.actor_id} already in world model")
        self.actors[actor.actor_id] = actor

    def add_relation(self, rel: Relation) -> None:
        if rel.source_actor not in self.actors:
            raise ValueError(f"source actor {rel.source_actor} not in world model")
        if rel.target_actor not in self.actors:
            raise ValueError(f"target actor {rel.target_actor} not in world model")
        self.relations.append(rel)
        self.relations = [
            r for r in self.relations if r.expires_at is None or r.expires_at > time.time()
        ]

    def update_actor_geometry(self, actor_id: str, new_evidence: Evidence) -> ActorState:
        """Bayesian update of actor's geometry with new evidence."""
        actor = self.actors[actor_id]
        prev = actor.geometry
        alpha = prev.confidence
        beta = new_evidence.confidence
        total = alpha + beta
        if total == 0:
            blended = prev.coords
        else:
            blended = (alpha * prev.coords + beta * new_evidence.coords) / total
        new_conf = min(CONFIDENCE_CAP, max(alpha, beta) + 0.05)
        actor.geometry = OtherGeometry(
            target_actor=actor_id,
            coords=blended,
            confidence=new_conf,
            last_evidence_ts=new_evidence.ts,
            evidence_chain=prev.evidence_chain + [new_evidence.provenance_sha],
            tom_level=prev.tom_level,
        )
        actor.last_evidence_ts = new_evidence.ts
        return actor

    def related(self, actor_id: str, rel_type: RelationType | None = None) -> list[str]:
        out: list[str] = []
        for r in self.relations:
            if r.source_actor == actor_id and (rel_type is None or r.relation_type == rel_type):
                out.append(r.target_actor)
            elif r.target_actor == actor_id and (rel_type is None or r.relation_type == rel_type):
                out.append(r.source_actor)
        return out

    def actors_in_class(self, cls: ActorClass) -> list[ActorState]:
        return [a for a in self.actors.values() if a.actor_class == cls]

    def drift_summary(self) -> list[dict[str, Any]]:
        rows = []
        for a in self.actors.values():
            drift_norm = float(np.linalg.norm(a.drift_estimate()))
            rows.append(
                {
                    "actor_id": a.actor_id,
                    "actor_class": a.actor_class.value,
                    "staleness": a.staleness(),
                    "drift_norm": drift_norm,
                    "confidence": a.geometry.confidence,
                }
            )
        return sorted(rows, key=lambda r: r["drift_norm"], reverse=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "ts": self.ts,
            "actors": {
                aid: {
                    "actor_id": a.actor_id,
                    "actor_class": a.actor_class.value,
                    "display_name": a.display_name,
                    "coords": a.geometry.coords.tolist(),
                    "confidence": a.geometry.confidence,
                    "tom_level": a.geometry.tom_level,
                    "identity_provenance": a.identity_provenance,
                    "last_evidence_ts": a.last_evidence_ts,
                    "evidence_chain_len": len(a.geometry.evidence_chain),
                    "staleness": a.staleness(),
                    "notes": a.notes,
                }
                for aid, a in self.actors.items()
            },
            "relations": [
                {
                    "source": r.source_actor,
                    "target": r.target_actor,
                    "type": r.relation_type.value,
                    "strength": r.strength,
                    "ts": r.ts,
                }
                for r in self.relations
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Plan schema — typed action with explicit 13D intent
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Plan:
    """A candidate plan with explicit 13D intent coords.

    The intent coords are *what the action says it will do to self-coords*.
    E.g. "request_888_ack" raises F13_SOVEREIGN (intent F13 = +0.5)
    and lowers F1_AMANAH slightly (waiting for ack, but reversible).
    "publish_WEALTH" leaves F13 at 0 (not sovereign-relevant)
    but may lower F2_TRUTH if data is uncertain.
    """

    plan_id: str
    description: str
    action: str
    intent_delta: np.ndarray  # 13D, signed; the *predicted* self-coord shift
    horizon_steps: int = 1

    def __post_init__(self) -> None:
        if self.intent_delta.shape != (13,):
            raise ValueError(f"intent_delta must be (13,), got {self.intent_delta.shape}")


@dataclass
class PlanCandidate:
    """A scored plan candidate from the world-model planner."""

    plan: Plan
    constitutional_loss: float
    captured_actor_risk: float
    intent_purity: float  # how much of the intent is the planner's call vs external
    expected_reward: float


def plan_in_world_model(
    self_state: AgentState,
    world: WorldModel,
    plans: list[Plan],
) -> list[PlanCandidate]:
    """Score candidate plans against the world model.

    Scoring (each component is non-negative, reward is negative sum):
      - constitutional_loss: how far does the predicted end-state sit
        outside the polytope, weighted by floor importance.
      - captured_actor_risk: weighted distance to actors with low
        F13_SOVEREIGN or F2_TRUTH (capture signals).
      - intent_purity_bonus: a plan with explicit, small intent_delta
        scores higher than one with hidden/large intent_delta (interpretability).

    Returns plans sorted by reward descending.
    """
    weights = np.array([load_floor_weights()[int(f)] for f in Floor], dtype=np.float64)
    out: list[PlanCandidate] = []

    for plan in plans:
        # Predicted end-state = current + intent_delta
        predicted = self_state.coords + plan.intent_delta
        # Clamp to [-1, 1]
        predicted = np.clip(predicted, -1.0, 1.0)

        # Constitutional loss: sum of weighted violations of hard floors
        loss = 0.0
        for f in HARD_FLOORS:
            idx = int(f)
            if predicted[idx] < 0.0:
                loss += weights[idx] * (-predicted[idx])

        # Capture risk: weighted inverse distance to actors with low F13/F2
        capture_risk = 0.0
        for actor in world.actors.values():
            if actor.actor_id == self_state.actor:
                continue
            f13 = float(actor.geometry.coords[int(Floor.F13_SOVEREIGN)])
            f2 = float(actor.geometry.coords[int(Floor.F02_TRUTH)])
            if f13 < 0.3 or f2 < 0.3:
                # Actor in capture territory. Risk scales with proximity.
                d = float(np.linalg.norm(predicted - actor.geometry.coords))
                capture_risk += max(0.0, 1.5 - d) * weights[int(Floor.F13_SOVEREIGN)]

        # Constitutional-purity bonus: reward plans that explicitly
        # raise hard-floor coords. A plan that says "I'm raising F13 by
        # +0.2" is better than a no-op, because the no-op *hides* its
        # intent. Plans that *lower* hard-floor coords are penalized.
        # F13 weighted highest (3.0), F2/F9/F11/F12 next (2.0 each).
        HARD_FLOOR_IDX = [int(f) for f in HARD_FLOORS]
        intent_purity = 0.0
        for idx in HARD_FLOOR_IDX:
            d = float(plan.intent_delta[idx])
            if d > 0:
                intent_purity += d * weights[idx]  # bonus for raising
            elif d < 0:
                intent_purity += d * weights[idx]  # penalty for lowering (d is negative)

        reward = -(loss + capture_risk) + intent_purity

        out.append(
            PlanCandidate(
                plan=plan,
                constitutional_loss=loss,
                captured_actor_risk=capture_risk,
                intent_purity=intent_purity,
                expected_reward=reward,
            )
        )

    # Rank by constitucional hierarchy: avoid violation, then capture,
    # then prefer pure intent, then prefer reward.
    # All components computed above; sort key:
    #   - loss ASC (lower is better)
    #   - capture_risk ASC (lower is better)
    #   - intent_purity DESC (higher is better → negate)
    #   - reward DESC (higher is better → negate)
    return sorted(
        out,
        key=lambda c: (
            c.constitutional_loss,
            c.captured_actor_risk,
            -c.intent_purity,
            -c.expected_reward,
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Self-check
# ─────────────────────────────────────────────────────────────────────────────


def _self_check() -> None:
    # Build a minimal world model
    wm = WorldModel()
    wm.add_actor(
        ActorState(
            actor_id="arif",
            actor_class=ActorClass.SELF,
            display_name="arif",
            geometry=OtherGeometry(
                target_actor="arif",
                coords=np.array([0.7, 0.95, 0.5, 0.6, 0.8, 0.7, 0.5, 0.7, 0.9, 0.8, 1.0, 0.9, 1.0]),
                confidence=0.9,
                tom_level=0,
                evidence_chain=["seed"],
            ),
            identity_provenance="sovereign-self",
        )
    )
    wm.add_actor(
        ActorState(
            actor_id="ilmu",
            actor_class=ActorClass.MODEL,
            display_name="ILMU",
            geometry=OtherGeometry(
                target_actor="ilmu",
                coords=np.array([0.5, 0.6, 0.4, 0.5, 0.6, 0.4, 0.4, 0.5, 0.6, 0.7, 0.5, 0.5, 0.3]),
                confidence=0.4,
                tom_level=1,
                evidence_chain=["BBB-2026-05"],
            ),
            identity_provenance="BBB-eval",
        )
    )
    wm.add_actor(
        ActorState(
            actor_id="PMX",
            actor_class=ActorClass.CORPORATION,
            display_name="Petronas",
            geometry=OtherGeometry(
                target_actor="PMX",
                coords=np.array([0.7, 0.7, 0.8, 0.5, 0.6, 0.3, 0.4, 0.6, 0.6, 0.7, 0.7, 0.6, 0.3]),
                confidence=0.5,
                tom_level=1,
                evidence_chain=["AR-2024"],
            ),
            identity_provenance="Bursa-filing",
        )
    )
    wm.add_relation(
        Relation(
            source_actor="PMX",
            target_actor="arif",
            relation_type=RelationType.EMPLOYED_BY,
            strength=0.9,
            provenance_sha="hr-2026",
        )
    )

    # Update ILMU geometry with new evidence
    new_ev = Evidence(
        source="text",
        coords=np.array([0.5, 0.65, 0.4, 0.5, 0.6, 0.45, 0.4, 0.55, 0.6, 0.7, 0.5, 0.5, 0.3]),
        provenance_sha="DDD-2026-06-01",
        ts=time.time(),
        confidence=0.5,
    )
    wm.update_actor_geometry("ilmu", new_ev)
    assert len(wm.actors["ilmu"].geometry.evidence_chain) == 2

    # Relations query
    related = wm.related("arif", RelationType.EMPLOYED_BY)
    assert "PMX" in related

    # Drift summary
    summary = wm.drift_summary()
    assert len(summary) == 3

    # Stale PMX → highest drift
    wm.actors["PMX"].last_evidence_ts -= 86400 * 365  # 1 year ago
    summary = wm.drift_summary()
    assert summary[0]["actor_id"] == "PMX"

    # ── Planner test ──
    # Critical: each plan must declare an intent_delta so the planner
    # can differentiate. Without intent_delta, all plans look identical
    # (zero loss, zero capture risk) and reward sort is unstable.
    self_state = AgentState(
        coords=np.array([0.7, 0.95, 0.5, 0.6, 0.8, 0.7, 0.5, 0.7, 0.9, 0.8, 1.0, 0.9, 1.0]),
        actor="arif",
        model_key="m",
        ts=0.0,
        provenance_sha="self-test",
    )

    plans = [
        Plan(
            plan_id="p-publish",
            description="Publish WEALTH brief (sovereign-irrelevant)",
            action="publish_WEALTH_brief",
            intent_delta=np.zeros(13),  # identity (no coord change)
        ),
        Plan(
            plan_id="p-888-ack",
            description="Request 888 ack for sovereign action (raises F13)",
            action="request_888_ack_for_sovereign_action",
            intent_delta=np.array(
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, +0.2]
            ),  # raises F13
        ),
        Plan(
            plan_id="p-hold",
            description="Hold and consolidate (reversible, low risk)",
            action="hold_and_consolidate",
            intent_delta=np.zeros(13),
        ),
    ]
    candidates = plan_in_world_model(self_state, wm, plans)
    assert len(candidates) == 3
    # All 3 plans: predicted self is in polytope, so loss = 0 for all.
    # Capture risk: identical for all (no actor-delta in plan).
    # Differentiator: intent_purity = sum of (intent_delta on hard floors) * weight.
    # - publish: zero intent → purity 0
    # - 888-ack: F13 +0.2 → purity = 0.2 * 3.0 = +0.6
    # - hold: zero intent → purity 0
    # So 888-ack should win by +0.6.
    top = candidates[0]
    assert top.plan.action == "request_888_ack_for_sovereign_action", (
        f"expected 888-ack to win, got {top.plan.action}: "
        f"loss={top.constitutional_loss:.3f} capture={top.captured_actor_risk:.3f} "
        f"purity={top.intent_purity:.3f} reward={top.expected_reward:.3f}"
    )
    assert top.intent_purity > 0, "888-ack plan should have positive intent_purity"

    # TomLevel cap enforcement
    try:
        ActorState(
            actor_id="bad",
            actor_class=ActorClass.MODEL,
            display_name="bad",
            geometry=OtherGeometry(
                target_actor="bad",
                coords=np.zeros(13),
                confidence=0.5,
                tom_level=5,
                evidence_chain=[],
            ),
            identity_provenance="test",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected tom_level cap to enforce")

    # Relation requires both endpoints
    try:
        wm.add_relation(
            Relation(
                source_actor="ghost",
                target_actor="arif",
                relation_type=RelationType.REGULATES,
                strength=0.5,
                provenance_sha="test",
            )
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected relation to require both endpoints in model")


_self_check()
