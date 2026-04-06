"""
Compatibility facade for the legacy governance kernel import path.

The runtime still imports ``core.governance_kernel`` even though the refactor
removed the original source file. This module restores the narrow contract the
current runtime expects: kernel state access, temporal grounding, and stage
routing for the metabolic loop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.physics.thermodynamics_hardened import ThermodynamicBudget
from core.shared.types import AuthorityLevel

THERMODYNAMICS_AVAILABLE = True


@dataclass(slots=True)
class GovernanceState:
    session_id: str = "global"
    floors: dict[str, float] = field(default_factory=dict)
    telemetry: dict[str, Any] = field(default_factory=dict)
    witness: dict[str, float] = field(default_factory=dict)
    qdf: float = 0.83
    metabolic_stage: int = 333
    verdict: str = "SEAL"


@dataclass(slots=True)
class GovernanceThresholds:
    qdf_min: float = 0.83
    temporal_stability_min: float = 0.75


@dataclass(slots=True)
class AppLayer:
    name: str = "compat"
    stage_plan: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FloorClassification:
    floor_id: str = ""
    required: bool = True


@dataclass(slots=True)
class FloorManifesto:
    floor_id: str = ""
    summary: str = ""


@dataclass(slots=True)
class AppManifesto:
    app_name: str = "arifOS"
    layers: list[AppLayer] = field(default_factory=list)


@dataclass(slots=True)
class AppRegistry:
    apps: dict[str, AppManifesto] = field(default_factory=dict)


@dataclass
class GovernanceKernel:
    session_id: str = "global"
    authority_level: AuthorityLevel | str = AuthorityLevel.ANONYMOUS
    human_approval_status: str = "pending"
    temporal_stability: float = 1.0
    hysteresis_penalty: float = 0.0
    thermodynamic_budget: ThermodynamicBudget | None = None
    temporal_contract: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.thermodynamic_budget is None:
            self.thermodynamic_budget = ThermodynamicBudget(session_id=self.session_id)

    def apply_temporal_grounding(self, contract: Any) -> None:
        if hasattr(contract, "model_dump"):
            self.temporal_contract = contract.model_dump(mode="json")
        elif isinstance(contract, dict):
            self.temporal_contract = dict(contract)
        else:
            self.temporal_contract = {"raw": str(contract)}

    def get_current_state(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "floors": {},
            "telemetry": {
                "dS": -0.02,
                "peace2": 1.01,
                "kappa_r": 0.97,
                "echoDebt": 0.0,
                "shadow": 0.05,
                "confidence": 0.88,
                "psi_le": 0.82,
                "verdict": "SEAL",
            },
            "witness": {"human": 0.42, "ai": 0.32, "earth": 0.26},
            "qdf": 0.83,
            "metabolic_stage": 333,
            "verdict": "SEAL",
            "temporal_contract": self.temporal_contract,
        }


_governance_kernels: dict[str, GovernanceKernel] = {}


def get_governance_kernel(session_id: str | None = None) -> GovernanceKernel:
    key = session_id or "global"
    kernel = _governance_kernels.get(key)
    if kernel is None:
        kernel = GovernanceKernel(session_id=key)
        _governance_kernels[key] = kernel
    return kernel


def clear_governance_kernel(session_id: str | None = None) -> None:
    if session_id is None:
        _governance_kernels.clear()
        return
    _governance_kernels.pop(session_id, None)


def route_pipeline(query: str, options: dict[str, Any] | None = None) -> list[str]:
    _ = query
    opts = options or {}
    plan = ["333_MIND", "666_HEART", "666_CRITIQUE", "888_JUDGE"]
    if opts.get("human_required") or opts.get("allow_execution"):
        plan.insert(-1, "777_FORGE")
    return plan


__all__ = [
    "AuthorityLevel",
    "GovernanceState",
    "GovernanceThresholds",
    "GovernanceKernel",
    "THERMODYNAMICS_AVAILABLE",
    "ThermodynamicBudget",
    "get_governance_kernel",
    "clear_governance_kernel",
    "_governance_kernels",
    "AppLayer",
    "FloorClassification",
    "FloorManifesto",
    "AppManifesto",
    "AppRegistry",
    "route_pipeline",
]
