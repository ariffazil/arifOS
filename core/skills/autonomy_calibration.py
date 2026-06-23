"""
AUTONOMY CALIBRATION — Implementation Stub
===========================================
Forged: 2026-06-14 by FORGE (000Ω)
Target: arifOS core/skills/autonomy_calibration.py
Status: STUB — data model + calibration rules complete.
        Full implementation requires governance log query integration.

Spec reference: /root/arifOS/core/skills/AUTONOMY_CALIBRATION_SPEC.md
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class BandDirection(str, Enum):
    TIGHTEN = "TIGHTEN"
    LOOSEN = "LOOSEN"
    MAINTAIN = "MAINTAIN"


@dataclass
class ToolRiskMetrics:
    tool_name: str
    action_class: str
    current_band: str  # FULL_AUTO | APPROVE_ONLY | PROPOSE_ONLY | HUMAN_ONLY
    total_invocations: int
    hold_count: int
    override_count: int
    false_positive_count: int = 0
    false_negative_count: int = 0
    hold_rate: float = 0.0
    override_rate: float = 0.0
    fp_rate: float = 0.0
    fn_rate: float = 0.0
    last_evaluated: Optional[datetime] = None


@dataclass
class CalibrationProposal:
    tool_name: str
    current_band: str
    proposed_band: str
    direction: BandDirection
    evidence: str
    confidence: float = 0.8
    recommended_action: str = "REVIEW"  # IMPLEMENT | REVIEW | DEFER


BANDS = ["FULL_AUTO", "APPROVE_ONLY", "PROPOSE_ONLY", "HUMAN_ONLY"]


def tighten_band(current: str) -> str:
    idx = BANDS.index(current) if current in BANDS else 0
    return BANDS[min(idx + 1, len(BANDS) - 1)]


def loosen_band(current: str) -> str:
    idx = BANDS.index(current) if current in BANDS else 0
    return BANDS[max(idx - 1, 0)]


def evaluate_tool_metrics(metrics: ToolRiskMetrics) -> CalibrationProposal:
    """
    Evaluate a single tool's metrics and propose a band change if warranted.
    """
    # Rule 1: Hold rate too high → policy too strict → LOOSEN
    if metrics.hold_rate > 0.30 and metrics.override_rate > 0.20:
        return CalibrationProposal(
            tool_name=metrics.tool_name,
            current_band=metrics.current_band,
            proposed_band=loosen_band(metrics.current_band),
            direction=BandDirection.LOOSEN,
            evidence=f"HOLD rate {metrics.hold_rate:.1%} with {metrics.override_rate:.1%} override rate — policy may be too strict",
            confidence=0.7,
            recommended_action="REVIEW",
        )

    # Rule 2: False negatives → policy too loose → TIGHTEN
    if metrics.fn_rate > 0.05:
        return CalibrationProposal(
            tool_name=metrics.tool_name,
            current_band=metrics.current_band,
            proposed_band=tighten_band(metrics.current_band),
            direction=BandDirection.TIGHTEN,
            evidence=f"False negative rate {metrics.fn_rate:.1%} — dangerous calls slipping through",
            confidence=0.85,
            recommended_action="IMPLEMENT",
        )

    # Rule 3: Zero HOLDs in 100+ invocations → consider loosening
    if metrics.hold_rate == 0.0 and metrics.total_invocations > 100:
        return CalibrationProposal(
            tool_name=metrics.tool_name,
            current_band=metrics.current_band,
            proposed_band=loosen_band(metrics.current_band),
            direction=BandDirection.LOOSEN,
            evidence=f"Zero HOLDs in {metrics.total_invocations} invocations — tool may be safe for higher autonomy",
            confidence=0.6,
            recommended_action="REVIEW",
        )

    return CalibrationProposal(
        tool_name=metrics.tool_name,
        current_band=metrics.current_band,
        proposed_band=metrics.current_band,
        direction=BandDirection.MAINTAIN,
        evidence="Metrics within normal range",
        confidence=0.9,
        recommended_action="DEFER",
    )


def calibrate_all(metrics_list: list[ToolRiskMetrics]) -> list[CalibrationProposal]:
    """Evaluate all tools and return actionable proposals only."""
    proposals = [evaluate_tool_metrics(m) for m in metrics_list]
    return [p for p in proposals if p.direction != BandDirection.MAINTAIN]


# ─── SELF-TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Tool with too many HOLDs → should LOOSEN
    strict_tool = ToolRiskMetrics(
        tool_name="forge_execute",
        action_class="ATOMIC",
        current_band="HUMAN_ONLY",
        total_invocations=50,
        hold_count=20,
        override_count=6,
        hold_rate=0.40,
        override_rate=0.30,
    )
    prop = evaluate_tool_metrics(strict_tool)
    assert prop.direction == BandDirection.LOOSEN, f"Expected LOOSEN, got {prop.direction}"
    print(f"✅ Strict tool: {prop.direction} → {prop.proposed_band} ({prop.evidence})")

    # Safe tool with 0 HOLDs → should LOOSEN
    safe_tool = ToolRiskMetrics(
        tool_name="docker.ps",
        action_class="OBSERVE",
        current_band="APPROVE_ONLY",
        total_invocations=200,
        hold_count=0,
        override_count=0,
        hold_rate=0.0,
        override_rate=0.0,
    )
    prop2 = evaluate_tool_metrics(safe_tool)
    assert prop2.direction == BandDirection.LOOSEN, f"Expected LOOSEN, got {prop2.direction}"
    print(f"✅ Safe tool: {prop2.direction} → {prop2.proposed_band} ({prop2.evidence})")

    # Normal tool → MAINTAIN
    normal = ToolRiskMetrics(
        tool_name="arif_sense_observe",
        action_class="OBSERVE",
        current_band="FULL_AUTO",
        total_invocations=20,
        hold_count=1,
        override_count=0,
        hold_rate=0.05,
        override_rate=0.0,
    )
    prop3 = evaluate_tool_metrics(normal)
    assert prop3.direction == BandDirection.MAINTAIN
    print(f"✅ Normal tool: {prop3.direction}")

    print("DITEMPA BUKAN DIBERI — autonomy_calibration stub verified.")
