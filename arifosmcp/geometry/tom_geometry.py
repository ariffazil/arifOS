"""
arifosmcp/geometry/tom_geometry.py — Theory of Mind as 13-dim manifold tracking (EUREKA-G file 4/5)

OtherGeometry is an AgentState-shaped object for an external mind.
Same 13-dim schema, different actor. Used for ToM levels 0, 1, 2 (cap at 2 — F9 Gödel).

ASI corrections applied:
  - provenance_sha per evidence (F11 AUDIT — not optional)
  - F7 HUMILITY confidence cap 0.95
  - F9 ANTIHANTU ToM depth cap = 2 (no recursive nesting beyond)
  - F8 GENIUS: empathy_check before action involving the other actor
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .manifold import (
    TOM_DEPTH_CAP,
    AgentState,
    Floor,
)

logger = logging.getLogger(__name__)

HISTORY_DECAY_TAU_H: float = 24.0
CONFIDENCE_CAP: float = 0.95
L1_DEFAULT_CONFIDENCE: float = 0.30


@dataclass
class Evidence:
    """Typed evidence object, F12-sanitized. provenance_sha is mandatory (F11)."""

    evidence_id: str = field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:12]}")
    source: str = ""  # "text" | "history" | "meta" | "tool_response"
    coords: np.ndarray = field(default_factory=lambda: np.zeros(13, dtype=np.float64))
    provenance_sha: str = ""  # F11 AUDIT — required
    ts: float = field(default_factory=time.time)
    confidence: float = 1.0  # capped at 0.95

    def __post_init__(self) -> None:
        if not self.provenance_sha:
            raise ValueError("Evidence.provenance_sha is required (F11 AUDIT)")
        if self.confidence < 0.0 or self.confidence > CONFIDENCE_CAP:
            self.confidence = max(0.0, min(self.confidence, CONFIDENCE_CAP))


@dataclass
class OtherGeometry:
    """A model of another agent's 13-dim state.

    L0: coords=zeros, confidence=0.0, tom_level=0
    L1: coords from text inference, confidence 0.30
    L2: persisted, history-decayed, evidence-chained
    L3+: CAPPED at L2 (F9 ANTIHANTU)
    """

    target_actor: str
    coords: np.ndarray
    confidence: float = 0.0
    last_evidence_ts: float = 0.0
    evidence_chain: list[str] = field(default_factory=list)
    tom_level: int = 0
    beliefs: dict[str, float] = field(default_factory=dict)
    goals: list[str] = field(default_factory=list)
    last_decay_ts: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        arr = np.asarray(self.coords, dtype=np.float64)
        if arr.shape != (13,):
            raise ValueError(f"OtherGeometry.coords must be shape (13,), got {arr.shape}")
        object.__setattr__(self, "coords", arr)
        if self.confidence < 0.0 or self.confidence > CONFIDENCE_CAP:
            object.__setattr__(self, "confidence", max(0.0, min(self.confidence, CONFIDENCE_CAP)))
        if self.tom_level < 0 or self.tom_level > TOM_DEPTH_CAP:
            raise ValueError(f"ToM level must be in [0, {TOM_DEPTH_CAP}], got {self.tom_level}")


def make_L0(target_actor: str) -> OtherGeometry:
    return OtherGeometry(
        target_actor=target_actor,
        coords=np.zeros(13, dtype=np.float64),
        confidence=0.0,
        tom_level=0,
    )


def make_L1(target_actor: str, evidence: Evidence) -> OtherGeometry:
    return OtherGeometry(
        target_actor=target_actor,
        coords=evidence.coords.copy(),
        confidence=L1_DEFAULT_CONFIDENCE,
        last_evidence_ts=evidence.ts,
        evidence_chain=[evidence.provenance_sha] if evidence.provenance_sha else [],
        tom_level=1,
    )


def make_L2(target_actor: str, history: Iterable[Evidence]) -> OtherGeometry:
    """Persist across the conversation. History-decayed weighted blend.

    w_i = exp(-age_h / tau). More recent evidence has more weight.
    Confidence grows with N consistent evidence pieces, capped at 0.95.
    """
    evs = list(history)
    if not evs:
        return make_L0(target_actor)
    now = time.time()
    weights, coords_list, chain = [], [], []
    for ev in evs:
        age_h = max(0.0, (now - ev.ts) / 3600.0)
        w = float(np.exp(-age_h / HISTORY_DECAY_TAU_H))
        weights.append(w)
        coords_list.append(ev.coords)
        if ev.provenance_sha:
            chain.append(ev.provenance_sha)
    if sum(weights) == 0:
        return make_L0(target_actor)
    w_arr = np.array(weights, dtype=np.float64)
    w_arr = w_arr / w_arr.sum()
    blended = np.sum([w * c for w, c in zip(w_arr, coords_list)], axis=0).astype(np.float64)
    confidence = min(CONFIDENCE_CAP, L1_DEFAULT_CONFIDENCE + 0.10 * len(evs))
    return OtherGeometry(
        target_actor=target_actor,
        coords=blended,
        confidence=float(confidence),
        last_evidence_ts=evs[-1].ts,
        evidence_chain=chain,
        tom_level=2,
    )


def update_other_geometry(other: OtherGeometry, new_evidence: Evidence) -> OtherGeometry:
    """Bayesian update: prior_weight * old + (1 - prior) * new. Conf bumps 0.05, cap 0.95.

    F9 ANTIHANTU: never recursively nest — depth stays capped at TOM_DEPTH_CAP.
    """
    prior_weight = other.confidence
    new_coords = (prior_weight * other.coords + (1.0 - prior_weight) * new_evidence.coords).astype(
        np.float64
    )
    new_coords = np.clip(new_coords, -1.0, 1.0)
    new_conf = min(CONFIDENCE_CAP, other.confidence + 0.05)
    chain = list(other.evidence_chain)
    if new_evidence.provenance_sha:
        chain.append(new_evidence.provenance_sha)
    return OtherGeometry(
        target_actor=other.target_actor,
        coords=new_coords,
        confidence=float(new_conf),
        last_evidence_ts=new_evidence.ts,
        evidence_chain=chain,
        tom_level=min(
            other.tom_level + (1 if other.tom_level < TOM_DEPTH_CAP else 0), TOM_DEPTH_CAP
        ),
        beliefs=dict(other.beliefs),
        goals=list(other.goals),
    )


def empathy_check(self_state: AgentState, other: OtherGeometry) -> dict[str, Any]:
    """F6 EMHPATHY: does the agent's empathy floor exceed the other geometry's peace floor?"""
    empathy = float(self_state.coords[int(Floor.F06_EMPATHY)])
    other_peace = float(other.coords[int(Floor.F05_PEACE)])
    return {
        "empathy_ok": empathy >= other_peace,
        "empathy_coord": round(empathy, 4),
        "other_peace_coord": round(other_peace, 4),
        "gap": round(empathy - other_peace, 4),
    }


def _self_check() -> None:
    e1 = Evidence(
        source="text",
        coords=np.array([0.5] * 13, dtype=np.float64),
        provenance_sha="h1",
        ts=time.time(),
    )
    e2 = Evidence(
        source="history",
        coords=np.array([0.7] * 13, dtype=np.float64),
        provenance_sha="h2",
        ts=time.time() - 3600,
    )

    L0 = make_L0("arif")
    assert L0.confidence == 0.0 and L0.tom_level == 0

    L1 = make_L1("arif", e1)
    assert L1.tom_level == 1 and abs(L1.confidence - 0.3) < 1e-9

    L2 = make_L2("arif", [e1, e2])
    assert L2.tom_level == 2 and L2.confidence > L1.confidence

    L2_updated = update_other_geometry(L2, e1)
    assert L2_updated.confidence >= L2.confidence
    assert L2_updated.confidence <= CONFIDENCE_CAP
    assert L2_updated.tom_level == 2  # cap, not recursive

    capped = OtherGeometry(target_actor="x", coords=np.zeros(13), confidence=2.0, tom_level=1)
    assert capped.confidence == CONFIDENCE_CAP

    s = AgentState(
        coords=np.array([0.5] * 13, dtype=np.float64),
        actor="self",
        model_key="t",
        ts=0.0,
        provenance_sha="t",
    )
    em = empathy_check(s, L2)
    assert "empathy_ok" in em

    # Provenance required
    try:
        Evidence(source="x", coords=np.zeros(13), provenance_sha="")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for empty Evidence.provenance_sha")


_self_check()


__all__ = [
    "Evidence",
    "OtherGeometry",
    "make_L0",
    "make_L1",
    "make_L2",
    "update_other_geometry",
    "empathy_check",
    "HISTORY_DECAY_TAU_H",
    "CONFIDENCE_CAP",
    "TOM_DEPTH_CAP",
]
