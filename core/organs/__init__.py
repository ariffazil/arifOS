"""
core/organs/__init__.py — Organ Exports (Unified)
Simplified for SabarLoop Ignition v2026.04.16
"""

from core.shared.types import InitOutput

from . import _1_agi as mind
from . import _2_asi as heart
from . import _3_apex as soul
from . import _4_vault as memory

from ._0_init import (
    AuthorityLevel,
    get_authority_name,
    init,
    requires_sovereign,
    scan_injection,
    validate_token,
    verify_auth,
)
from ._1_agi import agi, reason, sense, think
from ._2_asi import align, asi, empathize
from ._3_apex import apex, forge, judge, sync
from ._4_vault import SealRecord, seal, vault
from ._5_wealth import calculate_npv, wealth
from ._6_geox import evaluate_prospect, geox, verify_geospatial

# Humanized aliases
anchor = init
feel = empathize

__all__ = [
    "mind",
    "heart",
    "soul",
    "memory",
    "init",
    "agi",
    "asi",
    "apex",
    "vault",
    "wealth",
    "geox",
    # Humanized aliases
    "anchor",
    "feel",
    # Actions
    "scan_injection",  # F12
    "verify_auth",  # F11
    "requires_sovereign",
    "sense",  # Stage 111
    "think",  # Stage 222
    "reason",  # Stage 333
    "empathize",  # Stage 555
    "align",  # Stage 666
    "sync",  # Stage 444
    "forge",  # Stage 777
    "judge",  # Stage 888
    "seal",  # Stage 999
    "vault",  # Unified vault interface
    "wealth", # Economic Organ
    "geox",   # Earth Witness Organ
    "calculate_npv",
    "verify_geospatial",
    "evaluate_prospect",
    # Types
    "InitOutput",
    "AuthorityLevel",
    "SealRecord",
    "validate_token",
    "get_authority_name",
]
