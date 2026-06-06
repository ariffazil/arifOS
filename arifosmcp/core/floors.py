"""
arifosmcp/core/floors.py — Backward-compat shim to canonical /core/laws.py
────────────────────────────────────────────────────────────────────────
DITEMPA BUKAN DIBERI

Renamed 2026-06-06: Constitutional "Floors" → "Laws" (F01–F13).
This shim preserves legacy import paths for tools that import from
arifosmcp.core.floors. New code should import from core.laws directly.
"""

from core.laws import (
    evaluate_tool_call,      # noqa: F401
    ConstitutionalLaws,      # noqa: F401
    LAW_DESCRIPTIONS,        # noqa: F401
    THRESHOLDS,              # noqa: F401
    LawResult,               # noqa: F401
    GovernanceResult,        # noqa: F401
)

__all__ = [
    "evaluate_tool_call",
    "ConstitutionalLaws",
    "LAW_DESCRIPTIONS",
    "THRESHOLDS",
    "LawResult",
    "GovernanceResult",
]
