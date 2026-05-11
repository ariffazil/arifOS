"""
skills/wealth/__init__.py — WEALTH Domain Skill

Post-AGI verification-first capital governance kernel.
Exports: financial primitives + audit entropy + score kernel + decision packets.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from .allocation import allocation_rank, budget_optimize, civilization_sustainability
from .dscr import dscr
from .emv import emv
from .irr import irr, mirr
from .npv import npv, profitability_index
from .payback import payback
from .verify import (
    VerificationSurface,
    AuditEntropyResult,
    JuniorLoopImpact,
    CodifierCurse,
    LiabilityRoute,
    wealth_measure_delta_m,
    wealth_assess_junior_loop,
    wealth_track_codifier_curse,
    wealth_route_liability,
    wealth_audit_entropy_from_cashflow,
)
from .score_kernel import (
    WealthScore,
    wealth_score_kernel,
    wealth_decision_packet,
)

__all__ = [
    # Financial primitives
    "npv",
    "irr",
    "mirr",
    "emv",
    "dscr",
    "payback",
    "profitability_index",
    "allocation_rank",
    "budget_optimize",
    "civilization_sustainability",
    # Verification kernel
    "VerificationSurface",
    "AuditEntropyResult",
    "JuniorLoopImpact",
    "CodifierCurse",
    "LiabilityRoute",
    "wealth_measure_delta_m",
    "wealth_assess_junior_loop",
    "wealth_track_codifier_curse",
    "wealth_route_liability",
    "wealth_audit_entropy_from_cashflow",
    # Score kernel
    "WealthScore",
    "wealth_score_kernel",
    "wealth_decision_packet",
]
