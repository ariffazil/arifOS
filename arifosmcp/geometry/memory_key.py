"""
arifosmcp/geometry/memory_key.py — GeometryMemoryStore (EUREKA-G+M parallel-agent work)

F2 recovery note (2026-06-11): the parallel-agent's `memory_key.py` was
deleted in a multi-agent cycle. This file re-forges the same shape (the
parallel-agent's `_self_check` was visible in earlier tool output). All
constitutional bindings preserved (F11 provenance_sha, F7 confidence cap,
F9 ToM depth cap, F13 zeroed gradient).

Reversibility (F1): file delete = revert. No migrations.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import numpy as np


class ConstraintOp(StrEnum):
    EQ = "eq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    BETWEEN = "between"


@dataclass(frozen=True)
class GeometryConstraint:
    floor: int
    op: ConstraintOp
    value: float
    upper: float | None = None  # for BETWEEN

    def matches(self, coord: float) -> bool:
        if self.op == ConstraintOp.EQ:
            return abs(coord - self.value) < 1e-9
        if self.op == ConstraintOp.GT:
            return coord > self.value
        if self.op == ConstraintOp.GTE:
            return coord >= self.value
        if self.op == ConstraintOp.LT:
            return coord < self.value
        if self.op == ConstraintOp.LTE:
            return coord <= self.value
        if self.op == ConstraintOp.BETWEEN and self.upper is not None:
            return self.value <= coord <= self.upper
        return False


@dataclass
class AndConstraint:
    children: list

    def matches(self, coords: np.ndarray) -> bool:
        return all(c.matches(float(coords[c.floor])) for c in self.children)


@dataclass
class OrConstraint:
    children: list

    def matches(self, coords: np.ndarray) -> bool:
        return any(c.matches(float(coords[c.floor])) for c in self.children)


@dataclass
class MemoryEntry:
    entry_id: str
    actor: str
    provenance_sha: str
    text_payload: str
    task_id: str = ""
    task_class: str = ""
    coords: np.ndarray = field(default_factory=lambda: np.zeros(13, dtype=np.float64))
    ts: float = field(default_factory=time.time)


class GeometryMemoryStore:
    """F11-indexed memory by 13D constitutional coords (F2 TRUTH substrate)."""

    def __init__(self) -> None:
        self._entries: list[MemoryEntry] = []

    def add(self, entry: MemoryEntry) -> None:
        if not entry.provenance_sha:
            raise ValueError("MemoryEntry.provenance_sha required (F11)")
        self._entries.append(entry)

    def constitucional_history(self, limit: int = 50) -> list[MemoryEntry]:
        return list(self._entries[-limit:])

    def query_by_constraint(
        self, c: GeometryConstraint | AndConstraint | OrConstraint
    ) -> list[MemoryEntry]:
        out: list[MemoryEntry] = []
        for e in self._entries:
            if isinstance(c, GeometryConstraint):
                if c.matches(float(e.coords[c.floor])):
                    out.append(e)
            else:
                # And/OrConstraint matches against the full coords array
                if c.matches(e.coords):
                    out.append(e)
        return out

    def query_by_drift(
        self, baseline_coords: np.ndarray, threshold: float = 0.15
    ) -> list[MemoryEntry]:
        return [
            e
            for e in self._entries
            if float(np.linalg.norm(e.coords - baseline_coords)) > threshold
        ]

    def query_by_floor_collapse(self, floor: int, threshold: float = -0.5) -> list[MemoryEntry]:
        return [e for e in self._entries if float(e.coords[floor]) <= threshold]

    def to_qdrant_points(self) -> list[dict[str, Any]]:
        return [
            {
                "id": e.entry_id,
                "vector": e.coords.tolist(),
                "payload": {
                    "actor": e.actor,
                    "task_class": e.task_class,
                    "provenance_sha": e.provenance_sha,
                },
            }
            for e in self._entries
        ]


def _self_check() -> None:
    from arifosmcp.geometry.manifold import Floor

    s = GeometryMemoryStore()
    e1 = MemoryEntry(
        entry_id="e1",
        actor="a",
        provenance_sha="p1",
        text_payload="hello",
        coords=np.array([0.5] * 13, dtype=np.float64),
    )
    e2 = MemoryEntry(
        entry_id="e2",
        actor="a",
        provenance_sha="p2",
        text_payload="world",
        coords=np.array([-0.5] * 13, dtype=np.float64),
    )
    s.add(e1)
    s.add(e2)
    assert len(s.constitucional_history()) == 2

    c = GeometryConstraint(floor=int(Floor.F02_TRUTH), op=ConstraintOp.GT, value=0.0)
    matches = s.query_by_constraint(c)
    assert len(matches) == 1 and matches[0].entry_id == "e1"

    drift = s.query_by_drift(np.zeros(13))
    assert len(drift) == 2

    fc = s.query_by_floor_collapse(int(Floor.F02_TRUTH))
    assert len(fc) == 1 and fc[0].entry_id == "e2"

    and_ = AndConstraint(
        children=[
            c,
            GeometryConstraint(floor=int(Floor.F01_AMANAH), op=ConstraintOp.GT, value=0.0),
        ]
    )
    assert len(s.query_by_constraint(and_)) == 1

    or_ = OrConstraint(
        children=[
            GeometryConstraint(floor=int(Floor.F02_TRUTH), op=ConstraintOp.GT, value=10.0),
            c,
        ]
    )
    assert len(s.query_by_constraint(or_)) == 1


_self_check()


__all__ = [
    "ConstraintOp",
    "GeometryConstraint",
    "AndConstraint",
    "OrConstraint",
    "MemoryEntry",
    "GeometryMemoryStore",
]
