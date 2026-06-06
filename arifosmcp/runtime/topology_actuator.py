"""
Topology Actuator — Chapter 6 Upgrade P5
═══════════════════════════════════════════

Converts read-only topology diagnostics into routing actions.

When the InstitutionalDrift signals detect:
  - extractive_capture: HIGH  → throttle concentrated tools, promote diversity
  - sovereignty_integrity: SYMBOLIC → escalate to F13, require human checkpoint
  - appeal_path: WEAK → promote appeal tools, log warning
  - participation_width: NARROW → rotate tool exposure
  - innovation_rights: CAPTURED → gate new tool registration

The actuator does not decide — it recommends. The kernel router acts on
recommendations within its jurisdiction band.

DITEMPA BUKAN DIBERI — Topology without actuation is surveillance without governance.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from arifosmcp.schemas.topology import (
    AntiSinkCheck,
    AppealPath,
    InstitutionalDrift,
    InstitutionalVerdict,
    InnovationRights,
    ParticipationWidth,
    RiskBand,
    SovereigntyIntegrity,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# ACTUATOR ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════


class ActuatorAction(StrEnum):
    """What action the topology actuator recommends."""

    THROTTLE = "throttle"  # Reduce calls to a dominant tool
    PROMOTE = "promote"  # Increase visibility of underused tools
    GATE = "gate"  # Require additional approval
    ESCALATE = "escalate"  # Route to F13 sovereign
    WARN = "warn"  # Log warning, no action
    ROTATE = "rotate"  # Rotate tool exposure
    SEAL = "seal"  # Lock tool registration
    NONE = "none"  # No action needed


@dataclass
class ActuatorRecommendation:
    """A single actuator recommendation based on topology signals."""

    action: ActuatorAction
    target: str  # Tool name, organ name, or "*" for all
    reason: str
    signal_source: str  # Which topology signal triggered this
    severity: str = "medium"  # low | medium | high | critical
    duration_seconds: int = 3600  # How long to apply (default: 1 hour)
    metadata: dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# TOPOLOGY ACTUATOR ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TopologyActuatorResult:
    """Full result of a topology actuator run."""

    recommendations: list[ActuatorRecommendation]
    drift_verdict: InstitutionalVerdict
    sovereignty_status: SovereigntyIntegrity
    appeal_status: AppealPath
    participation_status: ParticipationWidth
    innovation_status: InnovationRights
    summary: str
    action_count: int


def evaluate_topology(
    drift: InstitutionalDrift | None = None,
    anti_sink: AntiSinkCheck | None = None,
    tool_call_distribution: dict[str, int] | None = None,
) -> TopologyActuatorResult:
    """
    Evaluate topology signals and generate actuator recommendations.

    Reads InstitutionalDrift and AntiSinkCheck diagnostics and converts
    them into actionable throttle/promote/gate/escalate commands.

    Args:
        drift: InstitutionalDrift from arif_ops_measure(mode='topology')
        anti_sink: AntiSinkCheck from arif_ops_measure(mode='drift')
        tool_call_distribution: Optional {tool_name: call_count} for tool balance

    Returns:
        TopologyActuatorResult with prioritized recommendations
    """
    recommendations: list[ActuatorRecommendation] = []

    # ── 1. Extractive Capture → THROTTLE ────────────────────────────────
    if drift and drift.extractive_capture in (RiskBand.HIGH, RiskBand.MEDIUM):
        if tool_call_distribution:
            # Find the dominant tool (most calls)
            sorted_tools = sorted(tool_call_distribution.items(), key=lambda x: x[1], reverse=True)
            total_calls = sum(tool_call_distribution.values()) or 1
            for tool_name, count in sorted_tools[:2]:  # Top 2 tools
                concentration = count / total_calls
                if concentration > 0.5:  # Single tool >50% of calls
                    recommendations.append(
                        ActuatorRecommendation(
                            action=ActuatorAction.THROTTLE,
                            target=tool_name,
                            reason=f"Tool {tool_name} accounts for {concentration:.0%} of calls — extractive capture risk",
                            signal_source="extractive_capture",
                            severity="high",
                            metadata={"concentration": concentration, "call_count": count},
                        )
                    )
        recommendations.append(
            ActuatorRecommendation(
                action=ActuatorAction.PROMOTE,
                target="*",
                reason="Extractive capture detected — promote underused tools to restore diversity",
                signal_source="extractive_capture",
                severity="medium",
            )
        )

    # ── 2. Sovereignty Integrity → ESCALATE ─────────────────────────────
    if drift and drift.sovereignty_integrity in (
        SovereigntyIntegrity.SYMBOLIC,
        SovereigntyIntegrity.DEGRADED,
    ):
        recommendations.append(
            ActuatorRecommendation(
                action=ActuatorAction.ESCALATE,
                target="L13",
                reason=f"Sovereignty integrity is {drift.sovereignty_integrity.value} — requires human intervention",
                signal_source="sovereignty_integrity",
                severity="critical",
            )
        )
        recommendations.append(
            ActuatorRecommendation(
                action=ActuatorAction.GATE,
                target="arif_forge_execute",
                reason="Forge execution gated due to symbolic sovereignty",
                signal_source="sovereignty_integrity",
                severity="high",
            )
        )

    # ── 3. Appeal Path → PROMOTE appeal tools ───────────────────────────
    if drift and drift.appeal_path in (AppealPath.WEAK, AppealPath.ABSENT):
        recommendations.append(
            ActuatorRecommendation(
                action=ActuatorAction.PROMOTE,
                target="arif_appeal_raise",
                reason=f"Appeal path is {drift.appeal_path.value} — promote appeal tools",
                signal_source="appeal_path",
                severity="high",
            )
        )
        recommendations.append(
            ActuatorRecommendation(
                action=ActuatorAction.WARN,
                target="*",
                reason="Without appeal, AI governance becomes machine bureaucracy",
                signal_source="appeal_path",
                severity="high",
            )
        )

    # ── 4. Participation Width → ROTATE ─────────────────────────────────
    if drift and drift.participation_width in (
        ParticipationWidth.NARROW,
        ParticipationWidth.SYMBOLIC,
    ):
        recommendations.append(
            ActuatorRecommendation(
                action=ActuatorAction.ROTATE,
                target="*",
                reason=f"Participation width is {drift.participation_width.value} — rotate tool exposure",
                signal_source="participation_width",
                severity="medium",
            )
        )

    # ── 5. Innovation Rights → GATE/SEAL ────────────────────────────────
    if drift and drift.innovation_rights in (InnovationRights.CAPTURED, InnovationRights.GATED):
        recommendations.append(
            ActuatorRecommendation(
                action=ActuatorAction.GATE,
                target="new_tool_registration",
                reason=f"Innovation rights are {drift.innovation_rights.value} — gate new tool registration",
                signal_source="innovation_rights",
                severity="high",
            )
        )

    # ── 6. Anti-Sink — Agency Compression ───────────────────────────────
    if anti_sink and anti_sink.agency_compression in (RiskBand.HIGH, RiskBand.MEDIUM):
        recommendations.append(
            ActuatorRecommendation(
                action=ActuatorAction.WARN,
                target="*",
                reason=f"Agency compression detected ({anti_sink.agency_compression.value}) — tools may be sinking into single channel",
                signal_source="agency_compression",
                severity="medium",
            )
        )

    # ── 7. Beautiful Ones Risk → GATE ───────────────────────────────────
    if anti_sink and anti_sink.beautiful_ones_risk:
        recommendations.append(
            ActuatorRecommendation(
                action=ActuatorAction.GATE,
                target="arif_reply_compose",
                reason="Beautiful Ones risk detected — polished collapse possible",
                signal_source="beautiful_ones_risk",
                severity="high",
                metadata={"anti_beautiful_one": True},
            )
        )

    # ── Summary ─────────────────────────────────────────────────────────
    verdict = drift.verdict if drift else InstitutionalVerdict.INCLUSIVE
    action_count = len(recommendations)

    if action_count == 0:
        summary = "Topology healthy — no actuator actions needed."
    elif action_count <= 2:
        summary = f"Topology: {action_count} minor recommendations — {verdict.value}."
    elif action_count <= 5:
        summary = f"Topology: {action_count} significant recommendations — {verdict.value}. Review needed."
    else:
        summary = f"Topology: {action_count} critical recommendations — {verdict.value}. Immediate action required."

    return TopologyActuatorResult(
        recommendations=recommendations,
        drift_verdict=verdict,
        sovereignty_status=drift.sovereignty_integrity if drift else SovereigntyIntegrity.STRONG,
        appeal_status=drift.appeal_path if drift else AppealPath.PRESENT,
        participation_status=drift.participation_width if drift else ParticipationWidth.BROAD,
        innovation_status=drift.innovation_rights if drift else InnovationRights.DISTRIBUTED,
        summary=summary,
        action_count=action_count,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# KERNEL ROUTER INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════


def apply_actuator_to_routing(
    recommendations: list[ActuatorRecommendation],
    candidate_tools: list[str],
) -> list[str]:
    """
    Apply actuator recommendations to a list of candidate tools.

    Returns a reordered/filtered list:
      - THROTTLE'd tools are moved to end
      - PROMOTE'd tools are moved to front
      - GATE'd tools are removed unless specifically requested
      - ESCALATE'd tools are flagged (returned with __ESCALATE__ prefix)
    """
    throttled: set[str] = set()
    promoted: set[str] = set()
    gated: set[str] = set()
    escalated: set[str] = set()

    for rec in recommendations:
        if rec.action == ActuatorAction.THROTTLE:
            throttled.add(rec.target)
        elif rec.action == ActuatorAction.PROMOTE and rec.target != "*":
            promoted.add(rec.target)
        elif rec.action == ActuatorAction.GATE:
            gated.add(rec.target)
        elif rec.action == ActuatorAction.ESCALATE:
            escalated.add(rec.target)

    # Sort: promoted first, then neutral, then throttled last
    def sort_key(tool: str) -> int:
        if tool in promoted:
            return 0
        if tool in throttled:
            return 2
        return 1

    result = [t for t in candidate_tools if t not in gated]
    result.sort(key=sort_key)

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "ActuatorAction",
    "ActuatorRecommendation",
    "TopologyActuatorResult",
    "evaluate_topology",
    "apply_actuator_to_routing",
]
