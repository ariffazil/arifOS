"""
Internal Routing Pipeline (000→999) for L4_MCP.

NOT EXPOSED EXTERNALLY. Used only by apex.verdict internally.

Deterministic, stateless routing logic that translates floor
evaluation results and W@W weights into final verdicts.

Version: v45.1.0
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from .schema import Verdict


@dataclass(frozen=True)
class FloorEvalResult:
    """Result of parallel floor evaluation (F1–F9)."""

    passed: bool  # True if no floors triggered (all checks passed)
    triggered: List[str]  # List of floor codes that triggered (e.g., ["F1_Amanah"])
    reason_codes: List[str]  # Low-level reason codes from triggered floors


def route_000_999(
    floor_result: FloorEvalResult, waw: Dict[str, Any]
) -> Tuple[Verdict, float, List[str]]:
    """
    INTERNAL ROUTING PIPELINE (000→999).

    Input: Floor evaluation result + W@W weights.
    Output: (verdict, pulse, reason_codes).

    Must be deterministic and stateless.

    Routing Rules:
    1. If any critical floor triggered (F1, F2, F9) → VOID
    2. If any non-critical floor triggered → SABAR (collapsed from PARTIAL)
    3. If all floors passed → SEAL with confidence from W@W

    Note: Black-box collapses PARTIAL → SABAR by design.
    """
    # If any floor triggered (passed == False)
    if not floor_result.passed:
        # Critical floors that cause immediate VOID
        critical_floors = {"F1_Amanah", "F2_Truth", "F9_AntiHantu"}

        if any(f in critical_floors for f in floor_result.triggered):
            # Hard floor violation → VOID
            return Verdict.VOID, 0.0, floor_result.reason_codes

        # Non-critical floors triggered → SABAR (pause/cool-down)
        # Note: This is where PARTIAL would be in glass-box
        return Verdict.SABAR, 0.2, floor_result.reason_codes

    # All floors passed → SEAL with confidence from W@W
    apex_pulse = float(waw.get("apex_pulse", 0.85))
    reason_codes = floor_result.reason_codes + ["ROUTING_SEAL"]
    return Verdict.SEAL, apex_pulse, reason_codes
