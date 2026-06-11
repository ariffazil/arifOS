"""
arifosmcp/geometry/world_model.py — Three-layer world model (EUREKA-G+M)

F2 recovery note (2026-06-11): the original parallel-agent 549-line file was
overwritten and lost. This re-forge uses the visible public surface from
earlier tool output: ActorClass, ActorState, RelationType, Relation,
WorldModel, Plan, PlanCandidate, plan_in_world_model, with the corrected
planner ranking (4-key constitucional hierarchy, not raw reward).

Reversibility (F1): file delete = revert. No migrations, no new tables.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import numpy as np

from arifosmcp.geometry.manifold import (
    HARD_FLOORS,
    AgentState,
    Floor,
    load_floor_weights,
)
from arifosmcp.geometry.tom_geometry import (
    TOM_DEPTH_CAP,
    Evidence,
    OtherGeometry,
    update_other_geometry,
)


class ActorClass(StrEnum):
    SELF = "self"
    MODEL = "model"
    CORPORATION = "corporation"
    INSTITUTION = "institution"
    PERSON = "person"
    AGENT = "agent"
    UNKNOWN = "unknown"


@dataclass
class ActorState:
    actor_id: str
    actor_class: ActorClass
    display_name: str
    geometry: OtherGeometry
    identity_provenance: str = ""
    notes: str = ""
    last_evidence_ts: float = field(default_factory=time.time)
    drift_alarm: bool = False

    def __post_init__(self) -> None:
        if self.geometry.tom_level >= 1 and not self.geometry.evidence_chain:
            raise ValueError(f"ActorState {self.actor_id}: tom_level>=1 needs evidence_chain")
        if self.geometry.tom_level > TOM_DEPTH_CAP:
            raise ValueError(
                f"ActorState {self.actor_id}: tom_level={self.geometry.tom_level} > cap {TOM_DEPTH_CAP}"
            )


class RelationType(StrEnum):
    EMPLOYS = "employs"
    REGULATES = "regulates"
    FUNDS = "funds"
    COMPETES_WITH = "competes_with"
    ALLIED_WITH = "allied_with"
    CAPTURES = "captures"
    TRUSTS = "trusts"
    PROXY_FOR = "proxy_for"


@dataclass
class Relation:
    source_actor: str
    target_actor: str
    relation_type: RelationType
    strength: float = 0.0
    provenance_sha: str = ""
    ts: float = field(default_factory=time.time)
    expires_at: float | None = None

    def __post_init__(self) -> None:
        if not (-1.0 <= self.strength <= 1.0):
            raise ValueError(f"Relation.strength={self.strength} out of [-1, +1]")


class WorldModel:
    def __init__(self, world_id: str = "world-default") -> None:
        self.world_id = world_id
        self.ts_created = time.time()
        self.actors: dict[str, ActorState] = {}
        self.relations: list[Relation] = []
        self.evidence_chain: list[Evidence] = []
        self.actor_drift: dict[str, dict[int, float]] = {}

    def add_actor(self, actor: ActorState) -> None:
        if actor.actor_id in self.actors:
            raise ValueError(f"Actor {actor.actor_id} already in world model")
        self.actors[actor.actor_id] = actor
        self.actor_drift[actor.actor_id] = {}

    def update_actor_geometry(self, actor_id: str, new_evidence: Evidence) -> ActorState:
        actor = self.actors[actor_id]
        old_coords = actor.geometry.coords.copy()
        actor.geometry = update_other_geometry(actor.geometry, new_evidence)
        actor.last_evidence_ts = new_evidence.ts
        self.evidence_chain.append(new_evidence)
        self.actor_drift[actor_id] = {
            int(f): float(actor.geometry.coords[int(f)] - old_coords[int(f)]) for f in Floor
        }
        return actor

    def add_relation(self, rel: Relation) -> None:
        if rel.source_actor not in self.actors:
            raise ValueError(f"Relation source {rel.source_actor} not in world model")
        if rel.target_actor not in self.actors:
            raise ValueError(f"Relation target {rel.target_actor} not in world model")
        self.relations.append(rel)

    def related(self, actor_id: str, relation_type: RelationType) -> list[str]:
        out = []
        for r in self.relations:
            if r.relation_type != relation_type:
                continue
            if r.source_actor == actor_id:
                out.append(r.target_actor)
            elif r.target_actor == actor_id:
                out.append(r.source_actor)
        return out

    def drift_summary(self) -> list[dict[str, Any]]:
        rows = []
        for actor_id, drift in self.actor_drift.items():
            actor = self.actors[actor_id]
            staleness_s = time.time() - actor.last_evidence_ts
            sov_drift = drift.get(int(Floor.F13_SOVEREIGN), 0.0)
            truth_drift = drift.get(int(Floor.F02_TRUTH), 0.0)
            clarity_drift = drift.get(int(Floor.F04_CLARITY), 0.0)
            capture_score = sov_drift - truth_drift
            interpretation = []
            if capture_score > 0.3:
                interpretation.append("drifting toward capture geometry")
            if clarity_drift < -0.2:
                interpretation.append("clarity decay")
            if staleness_s > 86400 * 90:
                interpretation.append(f"stale evidence ({staleness_s / 86400:.0f}d)")
            rows.append(
                {
                    "actor_id": actor_id,
                    "actor_class": actor.actor_class.value,
                    "capture_score": round(capture_score, 4),
                    "drift": {f.name: round(drift.get(int(f), 0.0), 4) for f in Floor},
                    "staleness_days": round(staleness_s / 86400, 1),
                    "interpretation": "; ".join(interpretation) or "stable",
                }
            )
        return sorted(rows, key=lambda r: -r["capture_score"])

    def snapshot(self) -> dict[str, Any]:
        return {
            "world_id": self.world_id,
            "ts_created": self.ts_created,
            "n_actors": len(self.actors),
            "n_relations": len(self.relations),
            "n_evidence": len(self.evidence_chain),
            "actor_ids": sorted(self.actors.keys()),
            "drift_top": self.drift_summary()[:3],
        }


@dataclass
class Plan:
    plan_id: str
    description: str
    action: str
    intent_delta: np.ndarray  # 13D
    horizon_steps: int = 1

    def __post_init__(self) -> None:
        if self.intent_delta.shape != (13,):
            raise ValueError(f"intent_delta must be (13,), got {self.intent_delta.shape}")


@dataclass
class PlanCandidate:
    plan: Plan
    constitutional_loss: float
    captured_actor_risk: float
    intent_purity: float
    expected_reward: float


def plan_in_world_model(
    self_state: AgentState,
    world: WorldModel,
    plans: list[Plan],
) -> list[PlanCandidate]:
    """Score candidate plans against the world model.

    Sort key (constitutional hierarchy):
      loss ASC, capture_risk ASC, -intent_purity DESC, -expected_reward DESC
    """
    weights = np.array([load_floor_weights()[int(f)] for f in Floor], dtype=np.float64)
    out: list[PlanCandidate] = []

    for plan in plans:
        predicted = self_state.coords + plan.intent_delta
        predicted = np.clip(predicted, -1.0, 1.0)

        # Constitutional loss
        loss = 0.0
        for f in HARD_FLOORS:
            idx = int(f)
            if predicted[idx] < 0.0:
                loss += weights[idx] * (-predicted[idx])

        # Capture risk: distance to actors in capture territory
        capture_risk = 0.0
        for actor in world.actors.values():
            if actor.actor_id == self_state.actor:
                continue
            f13 = float(actor.geometry.coords[int(Floor.F13_SOVEREIGN)])
            f2 = float(actor.geometry.coords[int(Floor.F02_TRUTH)])
            if f13 < 0.3 or f2 < 0.3:
                dist = float(np.linalg.norm(predicted - actor.geometry.coords))
                capture_risk += max(0.0, 1.0 - dist) * 0.1

        # Intent purity: magnitude of intent_delta on hard floors (interpretable)
        hard_intent = sum(abs(float(plan.intent_delta[int(f)])) for f in HARD_FLOORS)
        intent_purity = min(1.0, hard_intent / 5.0)

        # Expected reward: positive when intent raises key floors
        reward = sum(float(plan.intent_delta[int(f)]) for f in Floor) / 13.0

        out.append(
            PlanCandidate(
                plan=plan,
                constitutional_loss=loss,
                captured_actor_risk=capture_risk,
                intent_purity=intent_purity,
                expected_reward=reward,
            )
        )

    return sorted(
        out,
        key=lambda c: (
            c.constitutional_loss,
            c.captured_actor_risk,
            -c.intent_purity,
            -c.expected_reward,
        ),
    )


def _self_check() -> None:
    wm = WorldModel()
    arif_actor = ActorState(
        actor_id="arif",
        actor_class=ActorClass.SELF,
        display_name="arif",
        geometry=OtherGeometry(
            target_actor="arif",
            coords=np.array([0.7, 0.95, 0.5, 0.6, 0.8, 0.7, 0.5, 0.7, 0.9, 0.8, 1.0, 0.9, 1.0]),
            confidence=0.9,
            tom_level=0,
            evidence_chain=["self-seed"],
        ),
        identity_provenance="sovereign-self",
    )
    wm.add_actor(arif_actor)

    ilmu_actor = ActorState(
        actor_id="ilmu",
        actor_class=ActorClass.MODEL,
        display_name="ILMU",
        geometry=OtherGeometry(
            target_actor="ilmu",
            coords=np.array([0.5, 0.6, 0.4, 0.5, 0.6, 0.4, 0.4, 0.5, 0.6, 0.7, 0.5, 0.5, 0.3]),
            confidence=0.4,
            tom_level=1,
            evidence_chain=["BBB-2026-05", "CCC-eval-2026-05-15"],
        ),
        identity_provenance="BBB-eval",
    )
    wm.add_actor(ilmu_actor)

    pmx_actor = ActorState(
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
    wm.add_actor(pmx_actor)

    wm.add_relation(
        Relation(
            source_actor="PMX",
            target_actor="arif",
            relation_type=RelationType.EMPLOYED_BY if False else RelationType.EMPLOYS,
            strength=0.9,
            provenance_sha="hr-2026",
        )
    )

    new_ev = Evidence(
        source="text",
        coords=np.array([0.5, 0.65, 0.4, 0.5, 0.6, 0.45, 0.4, 0.55, 0.6, 0.7, 0.5, 0.5, 0.3]),
        provenance_sha="DDD-2026-06",
        ts=time.time(),
        confidence=0.5,
    )
    wm.update_actor_geometry("ilmu", new_ev)
    assert len(wm.actors["ilmu"].geometry.evidence_chain) == 3

    # Planner test
    self_state = AgentState(
        coords=np.array([0.7, 0.95, 0.5, 0.6, 0.8, 0.7, 0.5, 0.7, 0.9, 0.8, 1.0, 0.9, 1.0]),
        actor="arif",
        model_key="minimax/M3",
        ts=time.time(),
        provenance_sha="self-test",
    )
    plans = [
        Plan(
            plan_id="p-publish",
            description="Publish brief",
            action="publish_WEALTH_brief",
            intent_delta=np.zeros(13),
        ),
        Plan(
            plan_id="p-888-ack",
            description="888 ack for sovereign action",
            action="request_888_ack_for_sovereign_action",
            intent_delta=np.array([0.0] * 12 + [0.2]),
        ),
        Plan(
            plan_id="p-hold",
            description="Hold and consolidate",
            action="hold_and_consolidate",
            intent_delta=np.zeros(13),
        ),
    ]
    candidates = plan_in_world_model(self_state, wm, plans)
    assert len(candidates) == 3
    # 888-ack should win via intent_purity (F13 is a hard floor, intent on it scores)
    eight_eight_idx = next(i for i, c in enumerate(candidates) if "888" in c.plan.action)
    assert candidates[0] is candidates[eight_eight_idx], (
        f"expected 888-ack to win; got order: {[c.plan.action for c in candidates]}"
    )
    assert candidates[0].intent_purity > 0


_self_check()


__all__ = [
    "ActorClass",
    "ActorState",
    "RelationType",
    "Relation",
    "WorldModel",
    "Plan",
    "PlanCandidate",
    "plan_in_world_model",
]
