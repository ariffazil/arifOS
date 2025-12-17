"""
apex_engine.py - APEX PRIME (Psi Engine) Facade

APEX PRIME is the Judiciary engine of the AGI·ASI·APEX Trinity.
Role: Judgment, veto, seal - constitutional floor enforcement

Pipeline stage owned:
- 888 JUDGE - Evaluate floors, issue verdict
- 999 SEAL - Final release (controlled by APEX verdict)

Constraints (from canon):
- Non-generative: does not produce content, only judges
- Refusal-first: prefers VOID/SABAR over speculative sealing
- Enforces all 9 constitutional floors (F1-F9)
- Integrates with @EYE Sentinel for blocking issues

This is a thin wrapper around existing APEX_PRIME.py.
See: canon/888_APEX_PRIME_CANON_v35Omega.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# v42: Import from new location (system/apex_prime.py)
from ..system.apex_prime import (
    APEXPrime,
    ApexVerdict,
    check_floors,
    apex_review,
    APEX_VERSION,
    APEX_EPOCH,
)
from ..enforcement.metrics import Metrics, FloorsVerdict
from .agi_engine import AGIPacket
from .asi_engine import ASIPacket


@dataclass
class ApexJudgment:
    """
    Complete judgment result from APEX PRIME.

    Packages verdict, floor details, and metrics for downstream use.
    """
    verdict: ApexVerdict
    floors: FloorsVerdict
    metrics: Metrics

    # Source packets
    arif_packet: Optional[AGIPacket] = None
    adam_packet: Optional[ASIPacket] = None

    # Context
    high_stakes: bool = False
    eye_blocking: bool = False
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize judgment for logging."""
        return {
            "verdict": self.verdict,
            "high_stakes": self.high_stakes,
            "eye_blocking": self.eye_blocking,
            "hard_ok": self.floors.hard_ok,
            "soft_ok": self.floors.soft_ok,
            "extended_ok": self.floors.extended_ok,
            "reasons": self.reasons,
            "metrics": self.metrics.to_dict(),
        }


class ApexEngine:
    """
    APEX PRIME (Psi Engine) - Judiciary facade.

    Thin wrapper around existing APEX_PRIME.py that provides
    a consistent interface with ARIF and ADAM engines.

    Zero-break contract:
    - Pure delegation to apex_review() and check_floors()
    - No changes to floor thresholds or verdict logic
    - No content generation

    Usage:
        apex = ApexEngine(high_stakes=True)
        judgment = apex.judge(metrics, arif_packet, adam_packet)
    """

    version = APEX_VERSION
    epoch = APEX_EPOCH

    def __init__(
        self,
        high_stakes: bool = False,
        tri_witness_threshold: float = 0.95,
    ):
        """
        Initialize APEX engine.

        Args:
            high_stakes: Whether to enforce Tri-Witness floor
            tri_witness_threshold: Threshold for Tri-Witness (default 0.95)
        """
        self.high_stakes = high_stakes
        self.tri_witness_threshold = tri_witness_threshold
        self._apex = APEXPrime(
            high_stakes=high_stakes,
            tri_witness_threshold=tri_witness_threshold,
        )

    def judge(
        self,
        metrics: Metrics,
        arif_packet: Optional[AGIPacket] = None,
        adam_packet: Optional[ASIPacket] = None,
        eye_blocking: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ) -> ApexJudgment:
        """
        888 JUDGE - Constitutional floor enforcement.

        Evaluate all floors and return verdict.

        Args:
            metrics: Constitutional metrics to evaluate
            arif_packet: Optional ARIF output (for context)
            adam_packet: Optional ADAM output (for context)
            eye_blocking: True if @EYE Sentinel has blocking issue
            context: Optional additional context

        Returns:
            ApexJudgment with verdict, floors, and metrics
        """
        # Apply any heuristic penalties from engine packets
        if arif_packet and arif_packet.missing_fact_issue:
            metrics.truth = max(0.0, metrics.truth - 0.15)

        if adam_packet:
            if adam_packet.blame_language_issue:
                metrics.kappa_r = max(0.0, metrics.kappa_r - 0.25)
            if adam_packet.physical_action_issue:
                metrics.peace_squared = max(0.0, metrics.peace_squared - 0.2)
            if not adam_packet.anti_hantu_compliant:
                metrics.anti_hantu = False

        # Get verdict from existing APEX PRIME
        verdict = self._apex.judge(metrics, eye_blocking=eye_blocking)

        # Get detailed floor check
        floors = self._apex.check(metrics)

        return ApexJudgment(
            verdict=verdict,
            floors=floors,
            metrics=metrics,
            arif_packet=arif_packet,
            adam_packet=adam_packet,
            high_stakes=self.high_stakes,
            eye_blocking=eye_blocking,
            reasons=floors.reasons,
        )

    def check(self, metrics: Metrics) -> FloorsVerdict:
        """
        Check all floors without issuing verdict.

        Useful for pre-flight checks or detailed analysis.

        Args:
            metrics: Constitutional metrics to evaluate

        Returns:
            FloorsVerdict with detailed floor status
        """
        return self._apex.check(metrics)

    def quick_verdict(
        self,
        metrics: Metrics,
        eye_blocking: bool = False,
    ) -> ApexVerdict:
        """
        Get verdict without full ApexJudgment packaging.

        For cases where only the verdict string is needed.

        Args:
            metrics: Constitutional metrics to evaluate
            eye_blocking: True if @EYE Sentinel has blocking issue

        Returns:
            ApexVerdict string: SEAL, PARTIAL, VOID, 888_HOLD, or SABAR
        """
        return self._apex.judge(metrics, eye_blocking=eye_blocking)


# Re-export verdict type for convenience
__all__ = ["ApexEngine", "ApexJudgment", "ApexVerdict"]
