"""
TRL-001 seed — Trauma state-space coordinates.

These are coordinates on a *declared* 5-manifold M_trauma.
They are NOT yet a full Riemannian implementation (no geodesic solver,
no estimated metric from data, no curvature).

Ranges follow the design doctrine:
  x1 A1 Trust/Betrayal     ∈ [-1, 1]
  x2 A2 Causality/cascade  ∈ [0, ∞)  (operational cap for numerics)
  x3 A3 Power/Consent      ∈ [-1, 1]
  x4 A4 Truth/Naming       ∈ [0, 1]
  x5 A5 Epistemic humility ∈ [0, 1]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

AXIS_BOUNDS: dict[str, tuple[float, float]] = {
    "x1_trust_betrayal": (-1.0, 1.0),
    "x2_causality": (0.0, 1e6),  # unbounded theoretically; soft cap operational
    "x3_power_consent": (-1.0, 1.0),
    "x4_truth_naming": (0.0, 1.0),
    "x5_epistemic_humility": (0.0, 1.0),
}

AXIS_TO_SCHEMA = {
    "x1_trust_betrayal": "A1",
    "x2_causality": "A2",
    "x3_power_consent": "A3",
    "x4_truth_naming": "A4",
    "x5_epistemic_humility": "A5",
}


def axis_index(name: str) -> int:
    keys = list(AXIS_BOUNDS.keys())
    return keys.index(name)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def clamp_coordinates(**kwargs: float) -> dict[str, float]:
    out: dict[str, float] = {}
    for k, (lo, hi) in AXIS_BOUNDS.items():
        if k in kwargs:
            out[k] = _clamp(kwargs[k], lo, hi)
    return out


@dataclass(frozen=True)
class TraumaCoordinates:
    """Point x ∈ M_trauma (design coordinates).

    epistemic_class: always INTERPRETATION / SPEC for agent-derived placements
    unless sourced from OBS receipts.
    """

    x1_trust_betrayal: float = 0.0
    x2_causality: float = 0.0
    x3_power_consent: float = 0.0
    x4_truth_naming: float = 0.0
    x5_epistemic_humility: float = 0.5
    epistemic_class: str = "SPEC"
    confidence: float = 0.3
    provenance: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # frozen dataclass: use object.__setattr__
        for k, (lo, hi) in AXIS_BOUNDS.items():
            v = getattr(self, k)
            object.__setattr__(self, k, _clamp(v, lo, hi))
        if not (0.0 <= self.confidence <= 1.0):
            object.__setattr__(self, "confidence", _clamp(self.confidence, 0.0, 1.0))

    def as_vector(self) -> tuple[float, float, float, float, float]:
        return (
            self.x1_trust_betrayal,
            self.x2_causality,
            self.x3_power_consent,
            self.x4_truth_naming,
            self.x5_epistemic_humility,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "coordinates": {
                "x1_trust_betrayal": self.x1_trust_betrayal,
                "x2_causality": self.x2_causality,
                "x3_power_consent": self.x3_power_consent,
                "x4_truth_naming": self.x4_truth_naming,
                "x5_epistemic_humility": self.x5_epistemic_humility,
            },
            "axis_map": dict(AXIS_TO_SCHEMA),
            "epistemic_class": self.epistemic_class,
            "confidence": self.confidence,
            "provenance": list(self.provenance),
            "manifold": "M_trauma",
            "metric": "diagonal_placeholder",
            "geometry_status": "COORDINATE_ONLY",
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TraumaCoordinates:
        coords = data.get("coordinates") or data
        return cls(
            x1_trust_betrayal=float(coords.get("x1_trust_betrayal", 0.0)),
            x2_causality=float(coords.get("x2_causality", 0.0)),
            x3_power_consent=float(coords.get("x3_power_consent", 0.0)),
            x4_truth_naming=float(coords.get("x4_truth_naming", 0.0)),
            x5_epistemic_humility=float(coords.get("x5_epistemic_humility", 0.5)),
            epistemic_class=str(data.get("epistemic_class", "SPEC")),
            confidence=float(data.get("confidence", 0.3)),
            provenance=tuple(data.get("provenance") or ()),
        )


# Diagonal metric placeholder g_ij — NOT estimated from data
# λ2 weight on causality axis (cascade magnitude)
DEFAULT_METRIC_DIAGONAL: tuple[float, float, float, float, float] = (
    1.0,  # A1 orthogonal
    1.0,  # A2 — caller may set λ2 > 1 for cascade weight
    1.0,  # A3
    1.0,  # A4
    1.0,  # A5
)


def euclidean_distance(a: TraumaCoordinates, b: TraumaCoordinates, metric_diag: tuple[float, ...] | None = None) -> float:
    """Ambient R^5 distance with diagonal weights — NOT true geodesic length on M_trauma.

    Explicitly sub-geometric. True geodesic requires TRL-002 (not implemented).
    """
    g = metric_diag or DEFAULT_METRIC_DIAGONAL
    va, vb = a.as_vector(), b.as_vector()
    s = 0.0
    for i in range(5):
        d = va[i] - vb[i]
        s += float(g[i]) * d * d
    return s**0.5
