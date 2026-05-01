"""arifosmcp.core.physics — Thermodynamic physics module."""
from __future__ import annotations

from arifosmcp.core.physics.thermodynamics_hardened import (
    deduct_thermodynamic_budget,
    get_thermodynamic_budget,
    init_thermodynamic_budget,
)

__all__ = [
    "init_thermodynamic_budget",
    "get_thermodynamic_budget",
    "deduct_thermodynamic_budget",
]
