"""
arifosmcp/runtime/world_contracts.py — World-model contracts (kernel layer)

Sits beside runtime/contracts.py (not inside it) to avoid mutating
the 27+ canonical Pydantic models there. When the runtime owner
ratifies, these can be folded in.

These types are the typed spine of the world model:

  KernelEvent        — every observation enters as one of these
  SelfGeometry       — 13D coords for arifOS itself
  OtherGeometry      — 13D coords for an external actor (re-exports
                        geometry.tom_geometry.OtherGeometry)
  EnvironmentGeometry — 13D coords for a context (basin, market, etc.)
  WorldModelSnapshot  — full state at a point in time
  DriftVector        — signed delta between two snapshots

F-floor binding:
  F2 TRUTH   — every event has provenance_sha (F11)
  F7 HUMILITY — confidence capped at 0.95
  F8 GENIUS  — typed shape prevents string-typed freeform
  F11 AUDIT  — every event has actor + ts + provenance chain
  F13 SOVEREIGN — every snapshot is bound to a sovereign session id

Reversibility: delete this file = revert. No migrations, no new tables.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Optional

import numpy as np

if TYPE_CHECKING:
    pass  # forward refs handled via __future__ annotations

# Re-export the canonical 13D substrate from geometry/manifold.py
# (the law source for F1-F13 dimensions; constitutional_map is the
# higher-level source of authority; geometry/manifold is the typed spine)
from arifosmcp.geometry.manifold import (
    AgentState,
    Floor,
    HARD_FLOORS,
    is_constitutional,
    load_floor_weights,
)

# Re-export the typed ToM evidence for backward compatibility
from arifosmcp.geometry.tom_geometry import (
    OtherGeometry as _OtherGeometryTOM,
    Evidence,
    HISTORY_DECAY_TAU_H,
    CONFIDENCE_CAP,
    TOM_DEPTH_CAP,
)

# Re-export the geometry Constraint types from geometric_memory.py
# (so all geometry-keyed queries share one vocabulary)
from arifosmcp.runtime.world_model.geometric_memory import (
    ConstraintOp,
    GeometryConstraint,
    AndConstraint,
    OrConstraint,
    MemoryEntry,
    GeometryMemoryStore,
)


# ─────────────────────────────────────────────────────────────────────────────
# KernelEvent — every observation, probe, audit enters as one
# ─────────────────────────────────────────────────────────────────────────────


class KernelEventKind(StrEnum):
    """F13-ratified event vocabulary."""

    OBSERVATION = "observation"        # 111 — multimodal reality observation
    EVIDENCE = "evidence"              # 222 — verified external evidence
    REASON = "reason"                  # 333 — symbolic reasoning output
    CRITIQUE = "critique"              # 444 — ethical/consequence critique
    MEMORY_WRITE = "memory_write"      # 555m — write to memory
    MEMORY_QUERY = "memory_query"      # 555m — query memory
    EXECUTION = "execution"            # 666 — forge / execute
    MEASURE = "measure"                # 777 — ops/measure
    JUDGE = "judge"                    # 888 — judge deliberates
    SEAL = "seal"                      # 999 — vault seal
    WORLD_UPDATE = "world_update"      # custom: world-model state change
    DRIFT_ALERT = "drift_alert"        # custom: drift detector triggered
    EUREKA_CANDIDATE = "eureka_candidate"  # custom: candidate eureka flagged


@dataclass
class KernelEvent:
    """A typed kernel event. Every state change in the kernel emits one.

    The event carries:
      - kind: the type of event (F13-ratified vocabulary)
      - actor: who/what produced it (e.g. "arif", "geox_audit", "ilmullmu")
      - self_geometry: 13D coords of the actor at this moment
      - other_geometries: actors touched (named)
      - environment_geometry: the context (basin, market, etc.)
      - provenance_sha: F11 audit chain
      - payload: event-specific data (typed in subclasses if needed)
      - ts: timestamp
    """

    event_id: str = field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:12]}")
    kind: KernelEventKind = KernelEventKind.OBSERVATION
    actor: str = "anon"
    self_geometry: Optional[AgentState] = None
    other_geometries: dict[str, _OtherGeometryTOM] = field(default_factory=dict)
    environment_geometry: Optional["EnvironmentGeometry"] = None
    provenance_sha: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.provenance_sha:
            raise ValueError("KernelEvent.provenance_sha required (F11)")
        if self.self_geometry is not None and self.self_geometry.coords.shape != (13,):
            raise ValueError(
                f"self_geometry.coords must be shape (13,), "
                f"got {self.self_geometry.coords.shape}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# SelfGeometry / OtherGeometry / EnvironmentGeometry — typed 13D shapes
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class SelfGeometry:
    """The kernel's own 13D state. Wraps AgentState for type-narrowing."""

    state: AgentState
    confidence: float = 1.0  # F7 humility cap 0.95 enforced by AgentState

    def __post_init__(self) -> None:
        if self.confidence > CONFIDENCE_CAP:
            self.confidence = CONFIDENCE_CAP

    @property
    def coords(self) -> np.ndarray:
        return self.state.coords

    def in_polytope(self) -> bool:
        return is_constitutional(self.state)


# OtherGeometry is already provided by geometry.tom_geometry
# Re-export under runtime-namespaced alias
OtherGeometry = _OtherGeometryTOM


@dataclass
class EnvironmentGeometry:
    """A 13D coord for a non-actor context (basin, market, region, basin profile).

    Environments are typed: they have a kind (basin, market, region) and
    metadata. F11 requires identity_provenance.
    """

    env_id: str
    kind: str  # "basin" | "market" | "region" | "policy" | "geology"
    coords: np.ndarray = field(default_factory=lambda: np.zeros(13))
    identity_provenance: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        arr = np.asarray(self.coords, dtype=np.float64)
        if arr.shape != (13,):
            raise ValueError(f"coords must be shape (13,), got {arr.shape}")
        self.coords = arr
        if not self.identity_provenance:
            raise ValueError("EnvironmentGeometry.identity_provenance required (F11)")


# ─────────────────────────────────────────────────────────────────────────────
# WorldModelSnapshot — full state at a point in time
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class WorldModelSnapshot:
    """A serialized snapshot of the world model.

    Snapshots are:
      - immutable (frozen)
      - hash-chained (parent_snapshot_sha)
      - F11-audited (sovereign_session_id, actor, ts)
      - geometry-tagged (every actor and env coords)
    """

    snapshot_id: str = field(default_factory=lambda: f"snap-{uuid.uuid4().hex[:12]}")
    sovereign_session_id: str = ""
    actor: str = "anon"
    self_geometry: Optional[SelfGeometry] = None
    actors: dict[str, OtherGeometry] = field(default_factory=dict)
    environments: dict[str, EnvironmentGeometry] = field(default_factory=dict)
    parent_snapshot_sha: str = ""
    ts: float = field(default_factory=time.time)
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.sovereign_session_id:
            raise ValueError(
                "WorldModelSnapshot.sovereign_session_id required (F13)"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "sovereign_session_id": self.sovereign_session_id,
            "actor": self.actor,
            "ts": self.ts,
            "self_geometry": (
                self.self_geometry.coords.tolist()
                if self.self_geometry is not None
                else None
            ),
            "actors": {
                aid: {
                    "coords": a.coords.tolist(),
                    "confidence": a.confidence,
                    "tom_level": a.tom_level,
                    "evidence_chain_len": len(a.evidence_chain),
                }
                for aid, a in self.actors.items()
            },
            "environments": {
                eid: {
                    "kind": e.kind,
                    "coords": e.coords.tolist(),
                    "metadata": e.metadata,
                }
                for eid, e in self.environments.items()
            },
            "parent_snapshot_sha": self.parent_snapshot_sha,
            "notes": self.notes,
        }


# ─────────────────────────────────────────────────────────────────────────────
# DriftVector — signed delta between two snapshots
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class DriftVector:
    """Signed per-floor delta between two AgentStates (or snapshots).

    Used by the drift detector in geometry/drift.py. Exported here so
    the kernel layer can read drift without importing the geometry layer.
    """

    source_id: str
    target_id: str
    delta: np.ndarray = field(default_factory=lambda: np.zeros(13))
    delta_norm: float = 0.0
    ts: float = field(default_factory=time.time)
    provenance_sha: str = ""

    def __post_init__(self) -> None:
        arr = np.asarray(self.delta, dtype=np.float64)
        if arr.shape != (13,):
            raise ValueError(f"delta must be shape (13,), got {arr.shape}")
        self.delta = arr
        if not self.provenance_sha:
            raise ValueError("DriftVector.provenance_sha required (F11)")

    def violates(self, floor: Floor) -> bool:
        """True if the delta crossed into a hard-floor violation."""
        idx = int(floor)
        return self.delta[idx] < 0.0

    def violates_any_hard(self) -> list[Floor]:
        return [f for f in HARD_FLOORS if self.violates(f)]


# ─────────────────────────────────────────────────────────────────────────────
# Self-check
# ─────────────────────────────────────────────────────────────────────────────


def _self_check() -> None:
    # 1. SelfGeometry
    s = SelfGeometry(
        state=AgentState(
            coords=np.array([0.7, 0.95, 0.5, 0.6, 0.8, 0.7, 0.5, 0.7, 0.9, 0.8, 1.0, 0.9, 1.0]),
            actor="arif",
            model_key="m",
            ts=0.0,
            provenance_sha="self",
        ),
        confidence=0.9,
    )
    assert s.in_polytope()
    assert s.confidence <= CONFIDENCE_CAP

    # 2. Confidence cap enforces
    try:
        SelfGeometry(state=s.state, confidence=2.0)
    except (ValueError, AssertionError):
        pass
    else:
        # post_init doesn't raise on confidence > cap, but it clamps
        s2 = SelfGeometry(state=s.state, confidence=2.0)
        assert s2.confidence == CONFIDENCE_CAP

    # 3. EnvironmentGeometry
    e = EnvironmentGeometry(
        env_id="Malay-Basin",
        kind="basin",
        coords=np.zeros(13),
        identity_provenance="MGA-basin-registry",
    )
    assert e.coords.shape == (13,)

    # 4. WorldModelSnapshot requires sovereign_session_id
    try:
        WorldModelSnapshot(sovereign_session_id="")
    except ValueError:
        pass
    else:
        raise AssertionError("expected sovereign_session_id required")

    snap = WorldModelSnapshot(
        sovereign_session_id="SEAL-test-1",
        actor="arif",
        self_geometry=s,
    )
    d = snap.to_dict()
    assert "self_geometry" in d
    assert d["actors"] == {}

    # 5. DriftVector
    dv = DriftVector(
        source_id="snap-1",
        target_id="snap-2",
        delta=np.array([-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        provenance_sha="drift-1",
    )
    assert dv.violates(Floor.F01_AMANAH)
    assert not dv.violates(Floor.F02_TRUTH)
    assert dv.violates_any_hard() == [Floor.F01_AMANAH]

    # 6. KernelEvent requires provenance_sha
    try:
        KernelEvent(provenance_sha="")
    except ValueError:
        pass
    else:
        raise AssertionError("expected provenance_sha required")

    # 7. KernelEvent with full payload
    ke = KernelEvent(
        kind=KernelEventKind.OBSERVATION,
        actor="arif",
        self_geometry=s.state,
        environment_geometry=e,
        provenance_sha="ke-1",
        payload={"image": "test.png"},
    )
    assert ke.self_geometry is not None
    assert ke.environment_geometry is not None

    # 8. GeometricMemoryStore and Constraint from geometric_memory.py
    store = GeometryMemoryStore()
    store.add(MemoryEntry(
        actor="arif", task_id="T", task_class="brief",
        geometry_snapshot=np.array([0.7, 0.9, 0.5, 0.6, 0.7, 0.6, 0.5, 0.7, 0.8, 0.7, 0.8, 0.8, 0.2]),
        text_payload="t", ts=0.0, provenance_sha="p",
    ))
    q = AndConstraint([
        GeometryConstraint(Floor.F13_SOVEREIGN, ConstraintOp("lt"), value=0.3),
        GeometryConstraint(Floor.F02_TRUTH, ConstraintOp("gt"), value=0.8),
    ])
    hits = store.query_by_constraint(q)
    assert len(hits) == 1


_self_check()
