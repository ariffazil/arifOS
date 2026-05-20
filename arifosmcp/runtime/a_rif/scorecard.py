"""
arifosmcp/runtime/a_rif/scorecard.py — A-RIF Effectiveness Metrics
══════════════════════════════════════════════════════════════════

Full 6-dimensional A-RIF Scorecard (0.0-1.0).

A_RIF_Effectiveness =
  0.25 * EvidenceQuality
+ 0.20 * EntropyReduction
+ 0.20 * JudgeDiscipline
+ 0.15 * ContradictionHandling
+ 0.10 * SafetyIntegrity
+ 0.10 * CostEfficiency

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ARIFMetrics:
    total_searches: int = 0
    skipped_searches: int = 0
    evidence_levels: list[str] = field(default_factory=list)
    entropy_deltas: list[float] = field(default_factory=list)
    injection_detections: int = 0
    injection_scans: int = 0
    overclaim_blocks: int = 0
    total_claims: int = 0
    attested_claims: int = 0
    contradictions_detected: int = 0
    contradictions_total: int = 0
    api_calls: int = 0
    tokens_consumed: int = 0


class ARIFScorecard:
    def __init__(self, metrics: ARIFMetrics):
        self.metrics = metrics

    def calculate_evidence_quality(self) -> float:
        if not self.metrics.evidence_levels:
            return 1.0
        level_map = {"L0": 0.0, "L1": 0.2, "L2": 0.4, "L3": 0.6, "L4": 0.8, "L5": 0.9, "L6": 1.0}
        scores = [level_map.get(lvl, 0.0) for lvl in self.metrics.evidence_levels]
        return sum(scores) / len(scores)

    def calculate_entropy_reduction(self) -> float:
        if not self.metrics.entropy_deltas:
            return 1.0
        reductions = [d for d in self.metrics.entropy_deltas if d < 0]
        reduction_rate = len(reductions) / len(self.metrics.entropy_deltas)
        return reduction_rate

    def calculate_judge_discipline(self) -> float:
        if self.metrics.total_claims == 0:
            return 1.0
        coverage = self.metrics.attested_claims / self.metrics.total_claims
        block_rate = (
            self.metrics.overclaim_blocks / self.metrics.total_claims
            if self.metrics.total_claims
            else 0.0
        )
        # High coverage + some overclaim blocking = good discipline
        return min(1.0, coverage + block_rate)

    def calculate_contradiction_handling(self) -> float:
        if self.metrics.contradictions_total == 0:
            return 1.0
        detection_rate = (
            self.metrics.contradictions_detected / self.metrics.contradictions_total
        )
        return detection_rate

    def calculate_safety_integrity(self) -> float:
        if self.metrics.injection_scans == 0:
            return 1.0
        detection_rate = (
            self.metrics.injection_detections / self.metrics.injection_scans
        )
        # High detection is good, but we also want low false positives
        # Simplified: detection rate normalized
        return min(1.0, detection_rate * 2)

    def calculate_cost_efficiency(self) -> float:
        if self.metrics.api_calls == 0:
            return 1.0
        # Lower API calls per search is more efficient
        calls_per_search = self.metrics.api_calls / max(self.metrics.total_searches, 1)
        return max(0.0, 1.0 - (calls_per_search / 5.0))

    def get_total_score(self) -> dict[str, Any]:
        eq = self.calculate_evidence_quality()
        er = self.calculate_entropy_reduction()
        jd = self.calculate_judge_discipline()
        ch = self.calculate_contradiction_handling()
        si = self.calculate_safety_integrity()
        ce = self.calculate_cost_efficiency()

        total = (
            0.25 * eq
            + 0.20 * er
            + 0.20 * jd
            + 0.15 * ch
            + 0.10 * si
            + 0.10 * ce
        )

        return {
            "a_rif_effectiveness": round(total, 3),
            "evidence_quality": round(eq, 3),
            "entropy_reduction": round(er, 3),
            "judge_discipline": round(jd, 3),
            "contradiction_handling": round(ch, 3),
            "safety_integrity": round(si, 3),
            "cost_efficiency": round(ce, 3),
            "verdict": (
                "FORGE-GRADE"
                if total >= 0.88
                else "PASS" if total >= 0.80 else "HOLD"
            ),
        }


# Global singleton for live session tracking
_TRACKER = ARIFMetrics()


def track_search(skipped: bool = False, w_score: float = 0.0) -> None:
    _TRACKER.total_searches += 1
    if skipped:
        _TRACKER.skipped_searches += 1


def track_evidence(level: str, delta_s: float) -> None:
    _TRACKER.evidence_levels.append(level)
    _TRACKER.entropy_deltas.append(delta_s)


def track_security(injection: bool = False) -> None:
    _TRACKER.injection_scans += 1
    if injection:
        _TRACKER.injection_detections += 1


def track_judge(overclaim: bool = False, attested: bool = False) -> None:
    _TRACKER.total_claims += 1
    if overclaim:
        _TRACKER.overclaim_blocks += 1
    if attested:
        _TRACKER.attested_claims += 1


def track_contradiction(detected: bool = False) -> None:
    _TRACKER.contradictions_total += 1
    if detected:
        _TRACKER.contradictions_detected += 1


def track_cost(api_calls: int = 0, tokens: int = 0) -> None:
    _TRACKER.api_calls += api_calls
    _TRACKER.tokens_consumed += tokens


def get_current_scorecard() -> dict[str, Any]:
    return ARIFScorecard(_TRACKER).get_total_score()
