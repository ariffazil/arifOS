"""ChangeAuthorityClass and OperationalRiskTier — replacing the overloaded RiskClass.

The old `RiskClass` enum conflated two orthogonal dimensions:
  - How much blast radius does this CHANGE have?   → ChangeAuthorityClass
  - How severe is the OPERATIONAL impact?          → OperationalRiskTier

This split fixes 13 duplicate definitions across the codebase.
All runtime modules should import from here, not redefine locally.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""
from __future__ import annotations

from enum import StrEnum


class ChangeAuthorityClass(StrEnum):
    """How broadly does this change affect the federation?

    C0 – grammar/naming only (safe auto-apply)
    C1 – documentation changes
    C2 – contract/schema changes (needs review)
    C3 – public surface changes (needs 888_HOLD)
    C4 – floor/constitutional logic (needs F13)
    C5 – execution authority changes (needs F13 + witness)
    """
    C0_GRAMMAR = "C0"
    C1_DOCS = "C1"
    C2_CONTRACT = "C2"
    C3_PUBLIC_SURFACE = "C3"
    C4_FLOOR_LOGIC = "C4"
    C5_EXECUTION_AUTHORITY = "C5"


class OperationalRiskTier(StrEnum):
    """How severe is the operational risk of an action?

    LOW    – reversible, no blast radius
    MEDIUM – reversible, limited blast radius
    HIGH   – partially reversible, significant blast radius
    CRITICAL – irreversible, maximum blast radius → 888_HOLD
    """
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ── Deprecated alias (migration window: 2026-08-17) ──
# Old code using `RiskClass` will still work but emit DeprecationWarning.
# New code MUST use ChangeAuthorityClass or OperationalRiskTier directly.
# CI rule: forbid `class RiskClass` in new declarations.

import warnings


class _DeprecatedRiskClass:
    """Deprecated — use ChangeAuthorityClass or OperationalRiskTier instead."""

    def __getattr__(self, name):
        warnings.warn(
            "RiskClass is deprecated. Use ChangeAuthorityClass for change authority "
            "or OperationalRiskTier for operational severity.",
            DeprecationWarning,
            stacklevel=2,
        )
        # Try both enums
        for cls in (ChangeAuthorityClass, OperationalRiskTier):
            if hasattr(cls, name):
                return getattr(cls, name)
        raise AttributeError(name)


RiskClass = _DeprecatedRiskClass()  # type: ignore
