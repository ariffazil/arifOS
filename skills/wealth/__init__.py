"""
skills/wealth/__init__.py — WEALTH Domain Skill

Economic valuation primitives ported from the arifOS canonical finance engine.
Exports: npv, irr, mirr, emv, dscr, payback, profitability_index,
         allocation_rank, budget_optimize, civilization_sustainability
"""

from __future__ import annotations

from .allocation import allocation_rank, budget_optimize, civilization_sustainability
from .dscr import dscr
from .emv import emv
from .irr import irr, mirr
from .npv import npv, profitability_index
from .payback import payback

__all__ = [
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
]
