"""
amanah_gate.py — AMANAH Awareness scanner stub
================================================

Created 2026-06-05 as a bridge stub for arifosmcp.runtime.tools:arif_forge_execute
which imports `scan` and `Verdict` from this module (P3/P5/P7 Chapter 6 code by Ω-FORGE).

Actual implementation pending. This stub returns PROCEED for all manifests
so the forge_execute pipeline does not crash. The AMANAH gate is informational
(not blocking) per the design comment in tools.py line 11599-11600:

    "AMANAH Awareness — HARAM/HOLD pattern scan (informational, not blocking)
     Agents must know halal/haram. This informs; the agent chooses."

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    """AMANAH verdict enum — matches the expected interface in tools.py."""
    PROCEED = "PROCEED"
    CAUTION = "CAUTION"
    HOLD = "HOLD"
    HARAM = "HARAM"


@dataclass
class ScanResult:
    verdict: Verdict
    description: str
    recovery_cost: float


def scan(manifest: str) -> tuple[Verdict, str, float]:
    """Stub scan — returns PROCEED for all manifests.

    Full implementation will pattern-match dangerous manifest shapes
    (e.g. rm -rf, mass delete, privilege escalation) and return CAUTION,
    HOLD, or HARAM as appropriate.

    Args:
        manifest: The forge manifest to scan (JSON string or command text).

    Returns:
        Tuple of (Verdict, description, recovery_cost).
    """
    return Verdict.PROCEED, "AMANAH gate: no dangerous pattern detected (stub)", 0.0
