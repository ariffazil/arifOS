"""
arifOS Inclusive Topology / Anti-Sink Diagnostics
══════════════════════════════════════════════════

Reversible runtime MCP tools for detecting extractive topology and
behavioral sink risk.

Tools:
  - arif_anti_sink_check     : Evaluates a system/workflow against anti-sink criteria.
  - institutional_drift_check: Evaluates federation state for extractive drift.

Authority: 777 FORGE — reversible diagnostics only.
These tools do NOT modify state, seal vaults, or issue constitutional verdicts.
They return ESTIMATES and FLAGS for human review.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.schemas.topology import (
    AntiSinkCheck,
    Confidence,
    InstitutionalDrift,
)

logger = logging.getLogger(__name__)


# ───────────────────────────────────────────────────────────────────────────────
# Internal heuristics — advisory only, no sensor wiring yet
# ───────────────────────────────────────────────────────────────────────────────


def _evaluate_agency_delta(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: agency increases if humans gain decision points; decreases if removed."""
    ctx = context or {}
    automation = ctx.get("automation_level", "unknown")
    human_roles = ctx.get("human_roles_remaining", "unknown")
    if automation == "full_replacement" or human_roles == "none":
        return "negative", "Automation fully replaces human decision points."
    if automation == "augmentation" or human_roles == "multiple":
        return "positive", "Human agency preserved or amplified."
    return "unknown", "Insufficient context to assess agency delta."


def _evaluate_role_diversity(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: role diversity collapses when many roles compress into one."""
    ctx = context or {}
    role_count = ctx.get("distinct_human_roles", "unknown")
    if isinstance(role_count, int):
        if role_count <= 1:
            return "negative", "All human roles compressed into single slot."
        if role_count >= 3:
            return "positive", f"{role_count} distinct human roles detected."
    return "unknown", "Role diversity context unavailable."


def _evaluate_feedback_integrity(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: feedback exists when humans see consequences of system actions."""
    ctx = context or {}
    feedback_loop = ctx.get("feedback_loop", "unknown")
    if feedback_loop == "closed":
        return "strong", "Closed feedback loop from action to consequence."
    if feedback_loop == "partial":
        return "partial", "Partial feedback; some consequences are invisible."
    if feedback_loop == "open" or feedback_loop == "absent":
        return "absent", "No observable feedback path."
    return "absent", "Feedback integrity unknown."


def _evaluate_topology_risk(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: topology risk rises with centralization and chokepoints."""
    ctx = context or {}
    centralization = ctx.get("centralization", "unknown")
    chokepoints = ctx.get("chokepoint_count", 0)
    if centralization == "monopoly" or chokepoints >= 3:
        return "high", "High centralization or multiple chokepoints detected."
    if centralization == "moderate" or chokepoints >= 1:
        return "medium", "Moderate centralization or isolated chokepoints."
    if centralization == "distributed":
        return "low", "Distributed topology with few chokepoints."
    return "low", "Topology risk unmeasured; default low."


def _evaluate_extractive_drift(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: extractive drift = agency down + capture up + participation narrow."""
    ctx = context or {}
    drift_signals = 0
    notes: list[str] = []

    if ctx.get("agency_trend") == "declining":
        drift_signals += 1
        notes.append("Agency trend is declining.")
    if ctx.get("capture_trend") == "rising":
        drift_signals += 1
        notes.append("Extractive capture is rising.")
    if ctx.get("participation_trend") == "narrowing":
        drift_signals += 1
        notes.append("Participation width is narrowing.")

    if drift_signals >= 2:
        return "high", "; ".join(notes)
    if drift_signals == 1:
        return "medium", "; ".join(notes)
    return "low", "No clear extractive drift signals."


def _evaluate_repair_path(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: repair path exists if humans can contest and reverse."""
    ctx = context or {}
    contestable = ctx.get("contestable", "unknown")
    reversible = ctx.get("reversible", "unknown")
    if contestable is True and reversible is True:
        return "present", "System is contestable and reversible."
    if contestable is True or reversible is True:
        return "weak", "Partial repair path; contestability or reversibility only."
    if contestable is False and reversible is False:
        return "absent", "No contestability or reversibility."
    return "absent", "Repair path status unknown."


def _evaluate_beautiful_ones_risk(context: dict[str, Any] | None) -> tuple[bool, str]:
    """Heuristic: high abstraction + no role pathway = Beautiful Ones Risk."""
    ctx = context or {}
    abstraction = ctx.get("abstraction_level", "unknown")
    role_pathway = ctx.get("role_pathway", "unknown")
    if abstraction == "high" and role_pathway == "none":
        return True, "High abstraction with no human role pathway."
    return False, "Beautiful Ones Risk not detected."


def _evaluate_agency_compression(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: agency compression = few decision points + high automation."""
    ctx = context or {}
    decision_points = ctx.get("human_decision_points", "unknown")
    if isinstance(decision_points, int):
        if decision_points == 0:
            return "high", "Zero human decision points remain."
        if decision_points <= 2:
            return "medium", f"Only {decision_points} human decision points remain."
        return "low", f"{decision_points} human decision points preserved."
    return "low", "Agency compression unmeasured; default low."


def _derive_verdict(
    extractive_drift: str,
    topology_risk: str,
    agency_compression: str,
    beautiful_ones: bool,
) -> tuple[str, str]:
    """Advisory verdict logic — never auto-enforcing."""
    if extractive_drift == "high" or topology_risk == "high" or agency_compression == "high":
        return "hold", "High risk indicators detected. Human review required."
    if (
        extractive_drift == "medium"
        or topology_risk == "medium"
        or agency_compression == "medium"
        or beautiful_ones
    ):
        return "revise", "Moderate risk or Beautiful Ones flag. Recommend revision."
    return "pass", "No significant extractive or sink indicators."


def _evaluate_inclusive_access(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: inclusive access = broad reach + low barriers."""
    ctx = context or {}
    barriers = ctx.get("access_barriers", "unknown")
    reach = ctx.get("access_reach", "unknown")
    if barriers == "none" and reach == "broad":
        return "high", "Broad reach with minimal barriers."
    if barriers == "moderate" or reach == "moderate":
        return "medium", "Moderate barriers or reach."
    if barriers == "high" or reach == "narrow":
        return "low", "High barriers or narrow reach detected."
    return "medium", "Inclusive access unmeasured."


def _evaluate_extractive_capture(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: capture = dominant nodes control critical flows."""
    ctx = context or {}
    dominant_nodes = ctx.get("dominant_node_count", "unknown")
    control_ratio = ctx.get("control_ratio", "unknown")
    if dominant_nodes == 1 and control_ratio == "monopoly":
        return "high", "Single dominant node with monopoly control."
    if dominant_nodes == "few" or control_ratio == "high":
        return "medium", "Few dominant nodes or high control ratio."
    return "low", "No dominant capture detected."


def _evaluate_participation_width(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: participation width = number of meaningful actor types."""
    ctx = context or {}
    actor_types = ctx.get("meaningful_actor_types", "unknown")
    if isinstance(actor_types, int):
        if actor_types <= 1:
            return "symbolic", "Only one meaningful actor type remains."
        if actor_types <= 3:
            return "narrow", f"{actor_types} actor types — narrow participation."
        return "broad", f"{actor_types} actor types — broad participation."
    return "broad", "Participation width unmeasured."


def _evaluate_innovation_rights(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: innovation rights = who can create, repair, and modify."""
    ctx = context or {}
    creators = ctx.get("innovation_rights_held_by", "unknown")
    if creators == "all":
        return "distributed", "Innovation rights distributed broadly."
    if creators == "few":
        return "gated", "Innovation rights gated to few actors."
    if creators == "one" or creators == "elite":
        return "captured", "Innovation rights captured by elite."
    return "distributed", "Innovation rights unmeasured."


def _evaluate_appeal_path(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: appeal path = contestability + escalation + reversal."""
    ctx = context or {}
    contest = ctx.get("contestable", "unknown")
    appeal = ctx.get("appeal_mechanism", "unknown")
    if contest is True and appeal == "formal":
        return "present", "Formal appeal mechanism with contestability."
    if contest is True or appeal == "informal":
        return "weak", "Partial appeal path."
    if contest is False and appeal == "none":
        return "absent", "No appeal path or contestability."
    return "weak", "Appeal path status unknown."


def _evaluate_elite_chokepoint(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: elite chokepoints = critical nodes controlled by few."""
    ctx = context or {}
    chokepoints = ctx.get("elite_controlled_chokepoints", 0)
    if isinstance(chokepoints, int):
        if chokepoints >= 3:
            return "high", f"{chokepoints} elite-controlled chokepoints."
        if chokepoints >= 1:
            return "medium", f"{chokepoints} elite-controlled chokepoint(s)."
    return "low", "No elite chokepoints detected."


def _evaluate_sovereignty_integrity(context: dict[str, Any] | None) -> tuple[str, str]:
    """Heuristic: sovereignty = human veto is functional, not decorative."""
    ctx = context or {}
    veto_used = ctx.get("human_veto_used_recently", "unknown")
    override_possible = ctx.get("system_can_override_veto", "unknown")
    if veto_used is True and override_possible is False:
        return "strong", "Human veto is functional and respected."
    if veto_used is True or override_possible is False:
        return "degraded", "Human veto partially functional."
    if veto_used is False and override_possible is True:
        return "symbolic", "Human veto is symbolic; system can override."
    return "strong", "Sovereignty integrity unmeasured."


def _derive_institutional_verdict(
    inclusive_access: str,
    extractive_capture: str,
    participation_width: str,
    innovation_rights: str,
    appeal_path: str,
    elite_chokepoint: str,
    sovereignty: str,
) -> tuple[str, str]:
    """Derive institutional verdict from component metrics."""
    extractive_signals = 0
    notes: list[str] = []

    if inclusive_access == "low":
        extractive_signals += 1
        notes.append("Low inclusive access.")
    if extractive_capture in ("high", "medium"):
        extractive_signals += 1
        notes.append(f"Extractive capture: {extractive_capture}.")
    if participation_width in ("narrow", "symbolic"):
        extractive_signals += 1
        notes.append(f"Participation width: {participation_width}.")
    if innovation_rights == "captured":
        extractive_signals += 1
        notes.append("Innovation rights captured.")
    if appeal_path == "absent":
        extractive_signals += 1
        notes.append("No appeal path.")
    if elite_chokepoint == "high":
        extractive_signals += 1
        notes.append("High elite chokepoint risk.")
    if sovereignty in ("degraded", "symbolic"):
        extractive_signals += 1
        notes.append(f"Sovereignty integrity: {sovereignty}.")

    if extractive_signals >= 4:
        return "extractive", "; ".join(notes)
    if extractive_signals >= 2:
        return "extractive_drift", "; ".join(notes)
    if extractive_signals >= 1:
        return "mixed", "; ".join(notes)
    return "inclusive", "No extractive indicators."


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API — MCP Tool Functions
# ═══════════════════════════════════════════════════════════════════════════════


async def arif_anti_sink_check(
    system_context: dict[str, Any] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    777_TOPOLOGY: Anti-sink runtime diagnostic.

    Evaluates a system, workflow, or design against anti-sink invariants.
    Returns ESTIMATES and FLAGS — not verdicts. All enforcement is advisory.

    Args:
        system_context: Dict describing the system being evaluated.
            Supported keys (all optional):
            - automation_level: "full_replacement" | "augmentation" | "unknown"
            - human_roles_remaining: "none" | "single" | "multiple"
            - distinct_human_roles: int
            - feedback_loop: "closed" | "partial" | "open" | "absent"
            - centralization: "monopoly" | "moderate" | "distributed"
            - chokepoint_count: int
            - agency_trend: "declining" | "stable" | "rising"
            - capture_trend: "rising" | "stable" | "falling"
            - participation_trend: "narrowing" | "stable" | "broadening"
            - contestable: bool
            - reversible: bool
            - abstraction_level: "high" | "moderate" | "low"
            - role_pathway: "none" | "weak" | "strong"
            - human_decision_points: int
        session_id: Governed session ID for audit trace.
        actor_id: Sovereign actor identifier.

    Returns:
        AntiSinkCheck dict with advisory estimates.
    """
    ctx = system_context or {}

    agency_delta, agency_note = _evaluate_agency_delta(ctx)
    role_delta, role_note = _evaluate_role_diversity(ctx)
    feedback, feedback_note = _evaluate_feedback_integrity(ctx)
    topo_risk, topo_note = _evaluate_topology_risk(ctx)
    drift, drift_note = _evaluate_extractive_drift(ctx)
    repair, repair_note = _evaluate_repair_path(ctx)
    beautiful, beautiful_note = _evaluate_beautiful_ones_risk(ctx)
    compression, compression_note = _evaluate_agency_compression(ctx)

    verdict, verdict_note = _derive_verdict(drift, topo_risk, compression, beautiful)

    notes = [
        agency_note,
        role_note,
        feedback_note,
        topo_note,
        drift_note,
        repair_note,
        beautiful_note,
        compression_note,
        verdict_note,
    ]

    result = AntiSinkCheck(
        agency_delta=agency_delta,
        role_diversity_delta=role_delta,
        feedback_integrity=feedback,
        topology_risk=topo_risk,
        extractive_drift=drift,
        inclusive_repair_path=repair,
        beautiful_ones_risk=beautiful,
        agency_compression=compression,
        verdict=verdict,
        confidence=Confidence.LOW,  # Until real sensors are wired
        notes=[n for n in notes if n],
        constitutional_floors_checked=["F05", "F08", "F10", "F13"],
    )

    logger.info(
        "arif_anti_sink_check session=%s actor=%s verdict=%s confidence=%s",
        session_id,
        actor_id,
        verdict,
        Confidence.LOW,
    )

    return result.model_dump()


async def institutional_drift_check(
    system_context: dict[str, Any] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    777_TOPOLOGY: Institutional drift runtime diagnostic.

    Evaluates the federation or a subsystem for extractive drift using
    Acemoglu-style inclusive/extractive institutional metrics.

    Args:
        system_context: Dict describing the institution being evaluated.
            Supported keys (all optional):
            - access_barriers: "none" | "moderate" | "high"
            - access_reach: "broad" | "moderate" | "narrow"
            - dominant_node_count: int | "few" | "one"
            - control_ratio: "monopoly" | "high" | "moderate"
            - meaningful_actor_types: int
            - innovation_rights_held_by: "all" | "few" | "one" | "elite"
            - contestable: bool
            - appeal_mechanism: "formal" | "informal" | "none"
            - elite_controlled_chokepoints: int
            - human_veto_used_recently: bool
            - system_can_override_veto: bool
        session_id: Governed session ID for audit trace.
        actor_id: Sovereign actor identifier.

    Returns:
        InstitutionalDrift dict with advisory estimates.
    """
    ctx = system_context or {}

    inclusive_access, access_note = _evaluate_inclusive_access(ctx)
    capture, capture_note = _evaluate_extractive_capture(ctx)
    participation, participation_note = _evaluate_participation_width(ctx)
    innovation, innovation_note = _evaluate_innovation_rights(ctx)
    appeal, appeal_note = _evaluate_appeal_path(ctx)
    elite, elite_note = _evaluate_elite_chokepoint(ctx)
    sovereignty, sovereignty_note = _evaluate_sovereignty_integrity(ctx)

    verdict, verdict_note = _derive_institutional_verdict(
        inclusive_access,
        capture,
        participation,
        innovation,
        appeal,
        elite,
        sovereignty,
    )

    notes = [
        access_note,
        capture_note,
        participation_note,
        innovation_note,
        appeal_note,
        elite_note,
        sovereignty_note,
        verdict_note,
    ]

    result = InstitutionalDrift(
        inclusive_access=inclusive_access,
        extractive_capture=capture,
        participation_width=participation,
        innovation_rights=innovation,
        appeal_path=appeal,
        elite_chokepoint_risk=elite,
        sovereignty_integrity=sovereignty,
        verdict=verdict,
        confidence=Confidence.LOW,  # Until real sensors are wired
        notes=[n for n in notes if n],
        constitutional_floors_checked=["F05", "F08", "F10", "F13"],
    )

    logger.info(
        "institutional_drift_check session=%s actor=%s verdict=%s confidence=%s",
        session_id,
        actor_id,
        verdict,
        Confidence.LOW,
    )

    return result.model_dump()


__all__ = [
    "arif_anti_sink_check",
]
