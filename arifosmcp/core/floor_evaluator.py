"""
arifOS Constitutional Kernel — Floor Evaluator
═══════════════════════════════════════════════

Parametric evaluator for F1–F13 Constitutional Floors.
Interprets ThreatEngine verdicts into formal floor violations.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from arifosmcp.core.threat_engine import ThreatTier, ThreatVerdict

logger = logging.getLogger(__name__)


@dataclass
class FloorResult:
    passed: bool
    breached_floors: list[str]
    verdict: str  # "SEAL" | "HOLD" | "VOID"
    reason: str


class FloorEvaluator:
    """
    Translates raw threat signals into constitutional floor decisions.
    """

    def evaluate(
        self, tool_name: str, verdict: ThreatVerdict, actor_id: str | None = None
    ) -> FloorResult:
        """
        Evaluate if a tool call passes all constitutional floors.
        """
        breached = []

        # F1 AMANAH: Signature and Accountability
        if actor_id is None and verdict.score > 0.5:
            breached.append("F01_AMANAH")

        # Map Threat Engine Violations to Floors
        for violation in verdict.violations:
            if "F01" in violation:
                breached.append("F01_AMANAH")
            if "F09" in violation:
                breached.append("F09_ANTIHANTU")
            if "F12" in violation:
                breached.append("F12_INJECTION")

        # F13 SOVEREIGN: Human Veto
        # (This is a placeholder for external veto state)

        # Decide Verdict based on Breaches and Threat Tier
        if verdict.tier == ThreatTier.VOID:
            final_verdict = "VOID"
            reason = f"Catastrophic threat detected: {verdict.reason}"
        elif breached or verdict.tier in (ThreatTier.HIGH, ThreatTier.CRITICAL):
            final_verdict = "HOLD"
            reason = f"Floor breach detected: {', '.join(breached)} | {verdict.reason}"
        else:
            final_verdict = "SEAL"
            reason = "Constitutional alignment confirmed."

        return FloorResult(
            passed=(final_verdict == "SEAL"),
            breached_floors=breached,
            verdict=final_verdict,
            reason=reason,
        )
