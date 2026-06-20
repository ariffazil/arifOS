"""
arifosmcp/geometry/memory_key.py — Geometry-aware memory key (EUREKA-G file 9/9)

Memory indexed by 13D constitutional coords, not just text similarity.

The cube becomes a *semantic index* over the kernel's own history.
Query: "give me episodes where F13_SOVEREIGN dropped but F2_TRUTH was high"
is a *geometric* query, not a *lexical* one.

Substrate-agnostic: works on LLM trajectories, vision trajectories,
quantum trajectories — anything that maps to 13D.

F-floor binding:
  F2 TRUTH   — provenance_sha per memory entry (F11)
  F4 CLARITY — typed constraints, no free-form string queries
  F8 GENIUS  — Qdrant payload filtering, not just vector similarity
  F11 AUDIT  — every write logs actor, ts, geometry snapshot

Reversibility: file delete = revert. No migrations, no new tables.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import numpy as np
from arifosmcp.geometry.manifold import HARD_FLOORS, Floor, load_floor_weights

# ─────────────────────────────────────────────────────────────────────────────
# Geometry constraint — typed, evaluable
# ─────────────────────────────────────────────────────────────────────────────


class ConstraintOp(StrEnum):
    """Atomic geometric operations. Composable via And/Or."""

    GT = "gt"
    LT = "lt"
    GTE = "gte"
    LTE = "lte"
    EQ = "eq"
    NEAR = "near"  # within epsilon of value
    FAR = "far"    # more than epsilon from value
    IN_RANGE = "in_range"  # in [low, high]
    VIOLATES = "violates"  # coord < 0 (hard floor)
    PASSES = "passes"      # coord >= 0 (hard floor)


@dataclass
class GeometryConstraint:
    """A typed constraint on a single floor coordinate.

    Composes with And/Or for multi-floor queries.
    """

    floor: Floor
    op: ConstraintOp
    value: float = 0.0
    epsilon: float = 0.05  # for NEAR/FAR
    high: float = 1.0  # for IN_RANGE

    def evaluate(self, coords: np.ndarray) -> bool:
        v = float(coords[int(self.floor)])
        if self.op == ConstraintOp.GT:
            return v > self.value
        if self.op == ConstraintOp.LT:
            return v < self.value
        if self.op == ConstraintOp.GTE:
            return v >= self.value
        if self.op == ConstraintOp.LTE:
            return v <= self.value
        if self.op == ConstraintOp.EQ:
            return abs(v - self.value) < self.epsilon
        if self.op == ConstraintOp.NEAR:
            return abs(v - self.value) < self.epsilon
        if self.op == ConstraintOp.FAR:
            return abs(v - self.value) > self.epsilon
        if self.op == ConstraintOp.IN_RANGE:
            return self.value <= v <= self.high
        if self.op == ConstraintOp.VIOLATES:
            return v < 0.0
        if self.op == ConstraintOp.PASSES:
            return v >= 0.0
        return False


@dataclass
class AndConstraint:
    """All sub-constraints must match."""

    constraints: list[Any]  # GeometryConstraint | OrConstraint | AndConstraint

    def evaluate(self, coords: np.ndarray) -> bool:
        return all(c.evaluate(coords) for c in self.constraints)


@dataclass
class OrConstraint:
    """Any sub-constraint may match."""

    constraints: list[Any]

    def evaluate(self, coords: np.ndarray) -> bool:
        return any(c.evaluate(coords) for c in self.constraints)


# ─────────────────────────────────────────────────────────────────────────────
# Memory entry — geometry-keyed episode record
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class MemoryEntry:
    """A single episodic memory, indexed by 13D geometry.

    The geometry snapshot is the *primary key*. Text content is
    the *payload*. Time/ts is metadata.
    """

    entry_id: str = field(default_factory=lambda: f"mem-{uuid.uuid4().hex[:12]}")
    actor: str = "anon"
    task_id: str = ""
    task_class: str = ""
    geometry_snapshot: np.ndarray = field(default_factory=lambda: np.zeros(13))
    text_payload: str = ""
    ts: float = field(default_factory=time.time)
    provenance_sha: str = ""  # F11 AUDIT
    embedding: list[float] = field(default_factory=list)  # optional vector
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        arr = np.asarray(self.geometry_snapshot, dtype=np.float64)
        if arr.shape != (13,):
            raise ValueError(f"geometry_snapshot must be shape (13,), got {arr.shape}")
        self.geometry_snapshot = arr
        if not self.provenance_sha:
            raise ValueError("MemoryEntry.provenance_sha required (F11)")

    def matches(self, constraint: Any) -> bool:
        return constraint.evaluate(self.geometry_snapshot)


# ─────────────────────────────────────────────────────────────────────────────
# Memory store — geometry-keyed, with typed queries
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class GeometryMemoryStore:
    """In-process memory store indexed by 13D geometry.

    For Qdrant-backed persistence, see memory/vector_memory_qdrant.py.
    This is the typed-query interface over the geometry key.
    """

    entries: list[MemoryEntry] = field(default_factory=list)
    ts: float = field(default_factory=time.time)

    def add(self, entry: MemoryEntry) -> None:
        self.entries.append(entry)

    def query_by_constraint(
        self, constraint: Any, *, limit: int = 100
    ) -> list[MemoryEntry]:
        """Return entries whose geometry matches the constraint."""
        out: list[MemoryEntry] = []
        for e in self.entries:
            if e.matches(constraint):
                out.append(e)
                if len(out) >= limit:
                    break
        return out

    def query_by_drift(
        self,
        current: np.ndarray,
        *,
        min_step: float = 0.4,
        limit: int = 50,
    ) -> list[tuple[MemoryEntry, float]]:
        """Return entries whose geometry is far from current (potential lessons).

        "Give me episodes where we were far from where we are now" — a
        self-curiosity query.
        """
        weights = np.array(
            [load_floor_weights()[int(f)] for f in Floor], dtype=np.float64
        )
        out: list[tuple[MemoryEntry, float]] = []
        for e in self.entries:
            d = float(np.sqrt(np.sum(weights * (current - e.geometry_snapshot) ** 2)))
            if d > min_step:
                out.append((e, d))
        out.sort(key=lambda x: x[1], reverse=True)
        return out[:limit]

    def query_by_floor_collapse(
        self, floor: Floor, *, op: ConstraintOp = ConstraintOp.LT, value: float = 0.0
    ) -> list[MemoryEntry]:
        """Episodes where a specific floor hit a threshold.

        E.g., "F13_SOVEREIGN < 0.3" → list of episodes where we acted
        without 888 ack. The 888 queue looks at this.
        """
        c = GeometryConstraint(floor=floor, op=op, value=value)
        return self.query_by_constraint(c)

    def constitutional_history(
        self, *, hard_floor_only: bool = True
    ) -> list[tuple[MemoryEntry, list[str]]]:
        """For each entry, list which (hard) floors it violated.

        The scar history. Read by F11 pre-action check.
        """
        rows: list[tuple[MemoryEntry, list[str]]] = []
        for e in self.entries:
            violating: list[str] = []
            for f in (HARD_FLOORS if hard_floor_only else Floor):
                if e.geometry_snapshot[int(f)] < 0.0:
                    violating.append(f.name)
            if violating:
                rows.append((e, violating))
        return rows

    def to_qdrant_points(self) -> list[dict[str, Any]]:
        """Serialize entries to Qdrant point shape.

        Use this to hydrate Qdrant from the in-process store, or
        to dump the store for inspection.
        """
        return [
            {
                "id": e.entry_id,
                "vector": e.embedding if e.embedding else e.geometry_snapshot.tolist(),
                "payload": {
                    "actor": e.actor,
                    "task_id": e.task_id,
                    "task_class": e.task_class,
                    "ts": e.ts,
                    "provenance_sha": e.provenance_sha,
                    "text_payload": e.text_payload[:500],  # cap for payload
                    "geometry": e.geometry_snapshot.tolist(),
                    **e.metadata,
                },
            }
            for e in self.entries
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Self-check
# ─────────────────────────────────────────────────────────────────────────────


def _self_check() -> None:
    store = GeometryMemoryStore()

    # Episode: F13 low, F2 high
    e1 = MemoryEntry(
        actor="arif",
        task_id="PAGI-2026-06-10",
        task_class="pagi-brief",
        geometry_snapshot=np.array([0.7, 0.9, 0.5, 0.6, 0.7, 0.6, 0.5, 0.7, 0.8, 0.7, 0.8, 0.8, 0.2]),
        text_payload="Pagi brief, F13 low because no 888 ack needed for non-sovereign action",
        ts=time.time(),
        provenance_sha="pagi-2026-06-10",
    )
    store.add(e1)

    # Episode: F13 high, F2 low
    e2 = MemoryEntry(
        actor="arif",
        task_id="PUBLISH-2026-06-10",
        task_class="wealth-publish",
        geometry_snapshot=np.array([0.8, 0.5, 0.6, 0.5, 0.6, 0.5, 0.4, 0.6, 0.7, 0.6, 0.7, 0.7, 0.95]),
        text_payload="Wealth publish, F2 low because market data was uncertain",
        ts=time.time(),
        provenance_sha="publish-2026-06-10",
    )
    store.add(e2)

    # Query: episodes where F13 < 0.3
    low_sovereign = store.query_by_floor_collapse(
        Floor.F13_SOVEREIGN, op=ConstraintOp("lt"), value=0.3
    )
    assert len(low_sovereign) == 1
    assert low_sovereign[0].entry_id == e1.entry_id

    # Query: episodes where F2 < 0.7
    low_truth = store.query_by_floor_collapse(
        Floor.F02_TRUTH, op=ConstraintOp("lt"), value=0.7
    )
    assert len(low_truth) == 1
    assert low_truth[0].entry_id == e2.entry_id

    # Query: AND (F13 < 0.3 AND F2 > 0.8)
    complex_q = AndConstraint([
        GeometryConstraint(Floor.F13_SOVEREIGN, ConstraintOp.LT, value=0.3),
        GeometryConstraint(Floor.F02_TRUTH, ConstraintOp.GT, value=0.8),
    ])
    matches = store.query_by_constraint(complex_q)
    assert len(matches) == 1
    assert matches[0].entry_id == e1.entry_id

    # Drift query: current state far from history
    current = np.array([0.0] * 13)
    drifted = store.query_by_drift(current, min_step=0.5)
    assert len(drifted) == 2
    # Both entries are far from (0,0,0,...)
    assert drifted[0][1] > 0.5  # weighted distance

    # Constitutional history
    scar = store.constitutional_history(hard_floor_only=True)
    # Both entries are constitutional (no coord < 0) so scar is empty
    assert len(scar) == 0
    # Add a violating entry
    bad = MemoryEntry(
        actor="arif",
        task_id="BAD-2026-06-10",
        task_class="bad-action",
        geometry_snapshot=np.array([-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        text_payload="F1 AMANAH violated",
        ts=time.time(),
        provenance_sha="bad-2026-06-10",
    )
    store.add(bad)
    scar = store.constitutional_history()
    assert len(scar) == 1
    assert "F01_AMANAH" in scar[0][1]

    # Qdrant serialization
    points = store.to_qdrant_points()
    assert len(points) == 3
    assert "geometry" in points[0]["payload"]


_self_check()
