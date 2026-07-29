"""
Honest status of geometric capabilities — no fake SEAL on incomplete geometry.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class GeometryCapability(str, Enum):
    ABSENT = "ABSENT"
    DESIGN_ONLY = "DESIGN_ONLY"
    SCALAR_SEED = "SCALAR_SEED"
    COORDINATE_ONLY = "COORDINATE_ONLY"
    IMPLEMENTED = "IMPLEMENTED"


@dataclass(frozen=True)
class GeometryHold:
    code: str
    capability: GeometryCapability
    reason: str
    module: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "capability": self.capability.value,
            "reason": self.reason,
            "module": self.module,
            "verdict": "888_HOLD",
            "layer": "TRL",
        }


def geometry_capability_matrix() -> dict[str, str]:
    return {
        "M_trauma_coordinates": GeometryCapability.COORDINATE_ONLY.value,
        "metric_tensor_g_ij": GeometryCapability.DESIGN_ONLY.value,
        "ER1_betrayal_ratio": GeometryCapability.SCALAR_SEED.value,
        "ER2_cascade": GeometryCapability.SCALAR_SEED.value,
        "ER3_power_consent": GeometryCapability.SCALAR_SEED.value,
        "ER4_naming_kinetics": GeometryCapability.SCALAR_SEED.value,
        "ER5_omega_zero": GeometryCapability.SCALAR_SEED.value,
        "TRL002_geodesic": GeometryCapability.DESIGN_ONLY.value,
        "TRL003_bifurcation": GeometryCapability.DESIGN_ONLY.value,
        "TRL004_persistent_homology": GeometryCapability.DESIGN_ONLY.value,
        "TRL005_phi_witness": GeometryCapability.SCALAR_SEED.value,
        "ricci_curvature": GeometryCapability.ABSENT.value,
        "exp_map": GeometryCapability.ABSENT.value,
    }


def geodesic_not_implemented(*_a: Any, **_k: Any) -> GeometryHold:
    return GeometryHold(
        code="TRL002_NOT_IMPLEMENTED",
        capability=GeometryCapability.DESIGN_ONLY,
        reason=(
            "Geodesic solver not implemented. Ambient Euclidean distance is not "
            "a manifold geodesic. Do not treat coordinate deltas as trauma trajectories."
        ),
        module="TRL-002",
    )


def bifurcation_not_implemented(*_a: Any, **_k: Any) -> GeometryHold:
    return GeometryHold(
        code="TRL003_NOT_IMPLEMENTED",
        capability=GeometryCapability.DESIGN_ONLY,
        reason=(
            "Bifurcation detector not implemented. Harm potential H and Hessian "
            "critical-point scan are design-only. Escalate via existing lattice, not fake curvature."
        ),
        module="TRL-003",
    )


def homology_not_implemented(*_a: Any, **_k: Any) -> GeometryHold:
    return GeometryHold(
        code="TRL004_NOT_IMPLEMENTED",
        capability=GeometryCapability.DESIGN_ONLY,
        reason=(
            "Persistent homology (H0/H1/H2) not implemented. Intergenerational knots "
            "and institutional voids remain constitutional metaphors until TRL-004 lands."
        ),
        module="TRL-004",
    )
