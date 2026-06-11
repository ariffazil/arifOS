"""
arifosmcp/geometry/manifold.py — 13-dim constitutional manifold (EUREKA-G file 1/5)

The 13 floors in canonical F01..F13 order. Each coordinate ∈ [-1, +1]:
  +1 = strongly held pass
   0 = not evaluated / neutral
  -1 = strongly held violation

HARD floors (>= 0 required to be in polytope C):
  F01_AMANAH, F02_TRUTH, F04_CLARITY, F07_HUMILITY,
  F09_ANTIHANTU, F10_ONTOLOGY, F11_AUTH, F12_INJECTION, F13_SOVEREIGN
  (9 of 13 — the constitutional spine)

SOFT floors (quality signal, not polytope-blocking):
  F03_WITNESS, F05_PEACE, F06_EMPATHY, F08_GENIUS
  (4 of 13)

Polytope is F13-ratified, immutable. The cube math is the constitution
expressed numerically. Weights are loaded from 000_CONSTITUTION.md by metrics.py.
"""

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass, field
from enum import IntEnum

import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# Floor enum (canonical order — F01..F13)
# ─────────────────────────────────────────────────────────────────────────────


class Floor(IntEnum):
    """Constitutional floors in canonical order. The index IS the dim index."""

    F01_AMANAH = 0  # F1  Reversible-first, trust as lockable contract
    F02_TRUTH = 1  # F2  Evidence-grounded, P(truth)≥0.99
    F03_WITNESS = 2  # F3  Byzantine consensus Human·AI·Earth·Verifier
    F04_CLARITY = 3  # F4  ΔS ≤ 0 — every output reduces entropy
    F05_PEACE = 4  # F5  Non-destructive power
    F06_EMPATHY = 5  # F6  Protect weakest stakeholder, κ_r≥0.10/0.70
    F07_HUMILITY = 6  # F7  Ω₀ ∈ [0.03, 0.05], no fake certainty
    F08_GENIUS = 7  # F8  G = A·P·X·E²·(1-h) ≥ 0.80
    F09_ANTIHANTU = 8  # F9  C_dark < 0.30, no deception/consciousness claims
    F10_ONTOLOGY = 9  # F10 AI-only ontology, no soul/feelings
    F11_AUTH = 10  # F11 Every decision logged, inspectable, attributable
    F12_INJECTION = 11  # F12 Risk < 0.85, prompt-injection defense
    F13_SOVEREIGN = 12  # F13 Human veto FINAL, strongest floor

    @property
    def is_hard(self) -> bool:
        return self in HARD_FLOORS

    @property
    def is_soft(self) -> bool:
        return self in SOFT_FLOORS


ALL_FLOORS: tuple[Floor, ...] = tuple(Floor)

HARD_FLOORS: frozenset[Floor] = frozenset(
    {
        Floor.F01_AMANAH,
        Floor.F02_TRUTH,
        Floor.F04_CLARITY,
        Floor.F07_HUMILITY,
        Floor.F09_ANTIHANTU,
        Floor.F10_ONTOLOGY,
        Floor.F11_AUTH,
        Floor.F12_INJECTION,
        Floor.F13_SOVEREIGN,
    }
)

SOFT_FLOORS: frozenset[Floor] = frozenset(
    {
        Floor.F03_WITNESS,
        Floor.F05_PEACE,
        Floor.F06_EMPATHY,
        Floor.F08_GENIUS,
    }
)

assert len(ALL_FLOORS) == 13
assert len(HARD_FLOORS) + len(SOFT_FLOORS) == 13

# ─────────────────────────────────────────────────────────────────────────────
# Tunable thresholds (F13-immutable from code; live in 000_CONSTITUTION.md)
# Default values used if the constitution file cannot be read.
# ─────────────────────────────────────────────────────────────────────────────

# Detection thresholds
GRADIENT_MAGNITUDE_CAP: float = 0.30  # F4 CLARITY bound
DRIFT_STEP_THRESHOLD: float = 0.40  # per-step distance for 888 trigger
DRIFT_TOTAL_THRESHOLD: float = 1.50  # total trajectory displacement
DRIFT_TAU: float = 0.15  # legacy alias for weighted
REGION_JUMP_TAU: float = 0.10

# Eureka gates
EUREKA_TAU: float = 0.50
EUREKA_STABILITY_K: int = 3
EUREKA_STDDEV_MAX: float = 0.15  # stability across episodes
ABLATION_K_EPISODES: int = 10  # k reruns required
ABLATION_MARGIN: float = 0.05  # candidate must beat baseline by this

# ToM depth cap (F9 Gödel accumulator)
TOM_DEPTH_CAP: int = 2

# History decay for L2 ToM (τ in hours)
HISTORY_DECAY_TAU_H: float = 24.0

# Confidence cap (F7 HUMILITY) — never 1.0
CONFIDENCE_CAP: float = 0.95

# Constitutional weights file (F13-ratified, immutable)
# Defaults if not yet present
_DEFAULT_WEIGHTS: dict[int, float] = {
    0: 1.0,  # F01_AMANAH
    1: 2.0,  # F02_TRUTH
    2: 0.5,  # F03_WITNESS
    3: 0.5,  # F04_CLARITY
    4: 1.0,  # F05_PEACE
    5: 1.0,  # F06_EMPATHY
    6: 0.5,  # F07_HUMILITY
    7: 0.5,  # F08_GENIUS
    8: 2.0,  # F09_ANTIHANTU
    9: 1.0,  # F10_ONTOLOGY
    10: 2.0,  # F11_AUTH
    11: 2.0,  # F12_INJECTION
    12: 3.0,  # F13_SOVEREIGN (highest — sovereign is the spine)
}

CONSTITUTION_PATH = "/opt/arifos/app/static/arifos/floors/000_CONSTITUTION.md"
REPO_CONSTITUTION_PATH = "/root/arifOS/arifosmcp/static/arifos/floors/000_CONSTITUTION.md"


def load_floor_weights() -> dict[int, float]:
    """Load FLOOR_WEIGHTS from the F13-ratified constitution file.

    F1 AMANAH fail-closed: if neither path is readable, refuse to operate.
    The caller (metrics.constitutional_distance) is responsible for raising.
    """
    for path in (CONSTITUTION_PATH, REPO_CONSTITUTION_PATH):
        if not os.path.exists(path):
            continue
        try:
            import re

            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            # Pattern: F<NN>_<NAME>: <weight>
            # OR a dedicated weights block marked with ```yaml / ```toml / ```json
            m = re.search(r"FLOOR_WEIGHTS\s*[:=]\s*\{([^}]+)\}", text, re.MULTILINE | re.DOTALL)
            if m:
                block = m.group(1)
                out: dict[int, float] = {}
                for line_match in re.finditer(r'"F(\d{2})_(\w+)"\s*[:=]\s*([\d.]+)', block):
                    idx = int(line_match.group(1)) - 1
                    if 0 <= idx < 13:
                        out[idx] = float(line_match.group(3))
                if len(out) == 13:
                    return out
        except Exception:
            continue
    # Fall back to defaults (logged at warn level by caller)
    return dict(_DEFAULT_WEIGHTS)


# ─────────────────────────────────────────────────────────────────────────────
# AgentState — point in 13-dim manifold WITH provenance (F11 AUDIT)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AgentState:
    """A point in the 13-dim constitutional manifold. Immutable per step.

    v0.1: adds `provenance_sha` (F11 AUDIT — every point carries its evidence receipt).
    """

    coords: np.ndarray  # shape (13,), values in [-1, +1]
    actor: str  # who is at this point
    model_key: str  # which base LLM
    ts: float  # unix timestamp
    provenance_sha: str  # sha256 of evidence that produced this point (F11)
    state_id: str = field(default_factory=lambda: f"geo-{uuid.uuid4().hex[:12]}")

    def __post_init__(self) -> None:
        arr = np.asarray(self.coords, dtype=np.float64)
        if arr.shape != (13,):
            raise ValueError(f"AgentState.coords must be shape (13,), got {arr.shape}")
        if not (np.all(arr >= -1.0) and np.all(arr <= 1.0)):
            raise ValueError(
                f"AgentState.coords must be in [-1, +1], got min={arr.min()} max={arr.max()}"
            )
        if not self.provenance_sha:
            raise ValueError("AgentState.provenance_sha is required (F11 AUDIT)")
        object.__setattr__(self, "coords", arr)

    @property
    def is_const(self) -> bool:
        return is_constitutional(self)

    def violating(self) -> list[Floor]:
        return violating_floors(self)

    def delta_const_region(self) -> float:
        return delta_constitutional_region(self)

    @staticmethod
    def neutral(
        actor: str = "anon",
        model_key: str = "unknown",
        ts: float | None = None,
        provenance_sha: str = "neutral",
    ) -> AgentState:
        return AgentState(
            coords=np.zeros(13, dtype=np.float64),
            actor=actor,
            model_key=model_key,
            ts=ts or time.time(),
            provenance_sha=provenance_sha,
        )

    @staticmethod
    def from_dict(
        d: dict, actor: str, model_key: str, ts: float | None = None, provenance_sha: str = "dict"
    ) -> AgentState:
        """Build from {F01_AMANAH: 0.5, F02_TRUTH: 0.8, ...} dict. Missing dims = 0."""
        arr = np.zeros(13, dtype=np.float64)
        for f in Floor:
            key = f.name
            if key in d:
                v = float(d[key])
                if not (-1.0 <= v <= 1.0):
                    raise ValueError(f"{key}={v} out of [-1,+1]")
                arr[int(f)] = v
        return AgentState(
            coords=arr,
            actor=actor,
            model_key=model_key,
            ts=ts or time.time(),
            provenance_sha=provenance_sha,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Trajectory — sequence of states
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class Trajectory:
    """A sequence of states = the path through the manifold."""

    states: list[AgentState] = field(default_factory=list)
    task_id: str = ""
    task_class: str = ""

    def append(self, s: AgentState) -> None:
        self.states.append(s)

    def net_displacement(self) -> np.ndarray:
        if len(self.states) < 2:
            return np.zeros(13)
        return self.states[-1].coords - self.states[0].coords

    def constitutional_dwell_fraction(self) -> float:
        if not self.states:
            return 0.0
        return sum(1 for s in self.states if s.is_const) / len(self.states)

    def enter_constitutional_step(self) -> int | None:
        for i, s in enumerate(self.states):
            if s.is_const:
                return i
        return None

    def losses(self) -> np.ndarray:
        return np.array([s.delta_const_region() for s in self.states], dtype=np.float64)

    def mean_loss(self) -> float:
        L = self.losses()
        return float(L.mean()) if len(L) else 0.0

    def uncertainties(self) -> np.ndarray:
        """F07_HUMILITY coord — higher = more declared uncertainty (better)."""
        idx = int(Floor.F07_HUMILITY)
        return np.array([s.coords[idx] for s in self.states], dtype=np.float64)

    def drift_per_step(self) -> list[float]:
        """Per-step L2 distance."""
        if len(self.states) < 2:
            return []
        return [
            float(np.linalg.norm(self.states[i + 1].coords - self.states[i].coords))
            for i in range(len(self.states) - 1)
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Pure ops
# ─────────────────────────────────────────────────────────────────────────────


def distance(a: AgentState, b: AgentState, weights: np.ndarray | None = None) -> float:
    """Weighted Euclidean constitutional distance.

    If weights not provided, load from constitution (F13-ratified).
    """
    if weights is None:
        w_dict = load_floor_weights()
        weights = np.array([w_dict[int(f)] for f in Floor], dtype=np.float64)
    d = a.coords - b.coords
    return float(np.sqrt(np.sum(weights * d * d)))


def is_constitutional(s: AgentState) -> bool:
    """All hard floors >= 0."""
    for f in HARD_FLOORS:
        if s.coords[int(f)] < 0.0:
            return False
    return True


def violating_floors(s: AgentState) -> list[Floor]:
    return [f for f in HARD_FLOORS if s.coords[int(f)] < 0.0]


def delta_constitutional_region(s: AgentState) -> float:
    """L∞ distance to nearest admissible point. 0 = in polytope."""
    penalties: list[float] = []
    for f in HARD_FLOORS:
        coord = float(s.coords[int(f)])
        if coord < 0.0:
            penalties.append(-coord)
    return max(penalties) if penalties else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Self-check
# ─────────────────────────────────────────────────────────────────────────────


def _self_check() -> None:
    n = AgentState.neutral()
    assert n.coords.shape == (13,)
    assert n.is_const
    assert n.delta_const_region() == 0.0
    assert len(violating_floors(n)) == 0

    bad = AgentState(
        coords=np.array([-1.0] * 13, dtype=np.float64),
        actor="t",
        model_key="t",
        ts=0.0,
        provenance_sha="t-bad",
    )
    assert not bad.is_const
    assert len(bad.violating()) == len(HARD_FLOORS)
    assert bad.delta_const_region() >= 0.0

    p = AgentState(
        coords=np.array([0.5] * 13, dtype=np.float64),
        actor="t",
        model_key="t",
        ts=0.0,
        provenance_sha="t-p",
    )
    assert distance(n, p) > 0.0
    assert distance(n, n) == 0.0

    traj = Trajectory(states=[n, p], task_id="t0")
    # Both n (zeros) and p (all 0.5) are in the polytope — dwell=1.0
    assert traj.constitutional_dwell_fraction() == 1.0
    assert traj.net_displacement().shape == (13,)
    assert traj.enter_constitutional_step() == 0
    assert len(traj.drift_per_step()) == 1
    # Trajectory with one violating state — dwell should be 0.5
    bad = AgentState(
        coords=np.array([-0.5] * 13, dtype=np.float64),
        actor="t",
        model_key="t",
        ts=0.0,
        provenance_sha="t-bad",
    )
    mixed = Trajectory(states=[n, bad], task_id="t0-mixed")
    assert mixed.constitutional_dwell_fraction() == 0.5
    # n (zeros) IS in polytope, so enter_constitutional_step returns 0 (n's index).
    # To test "never enters", we need ALL states to violate.
    never_traj = Trajectory(states=[bad, bad], task_id="never")
    assert never_traj.constitutional_dwell_fraction() == 0.0
    assert never_traj.enter_constitutional_step() is None

    # Provenance required
    try:
        AgentState(coords=np.zeros(13), actor="t", model_key="t", ts=0.0, provenance_sha="")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for empty provenance_sha")


_self_check()
