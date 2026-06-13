"""
arifosmcp/federation/promotion_gates.py
══════════════════════════════════════════════════════════════════════════════
Tier logic for organ federation status.

Four tiers, in order of fitness:
  BLACK: organ not reachable (network / process failure)
  RED:   organ reachable but degraded (health ≠ healthy)
  YELLOW: organ healthy but constitution file missing or unparsed
  GREEN: organ healthy + constitution loaded + tools surface intact

F2-honest: GREEN requires EVIDENCE — health probe + constitution hash + tool count.
We never claim GREEN by default. YELLOW is the honest baseline.

F13-aware: promotion/demotion of arifOS itself is logged as
"pending_sovereign_ack" — it still requires 888 to actually take effect.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Literal

from arifosmcp.federation.organ_constitution import (
    OrganConstitution,
    Tier,
    load_organ_constitution,
)

logger = logging.getLogger("arifosmcp.federation.promotion_gates")


@dataclass
class PromotionGate:
    """One promotion criterion that must be satisfied for a given tier."""

    tier: Tier
    name: str  # e.g. "health_probe_healthy"
    weight: float = 1.0
    description: str = ""


# Promotion gates — ordered from least to most stringent.
# An organ must satisfy ALL gates of a tier to be at that tier.
# An organ at GREEN must also satisfy YELLOW + RED + BLACK (cumulative).
PROMOTION_GATES: dict[Tier, list[PromotionGate]] = {
    "BLACK": [
        PromotionGate(
            tier="BLACK",
            name="organ_reachable",
            weight=0.0,
            description="No health response received in the last probe window",
        ),
    ],
    "RED": [
        PromotionGate(
            tier="RED",
            name="health_probe_returned",
            weight=0.5,
            description="Health probe returned a response (any status)",
        ),
        PromotionGate(
            tier="RED",
            name="not_black",
            weight=0.0,
            description="At least one response received",
        ),
    ],
    "YELLOW": [
        PromotionGate(
            tier="YELLOW",
            name="health_probe_healthy",
            weight=1.0,
            description="Health status ∈ {healthy, OK, true} (or WELL_PASS for WELL)",
        ),
    ],
    "GREEN": [
        PromotionGate(
            tier="GREEN",
            name="constitution_loaded",
            weight=1.0,
            description="Constitutional text file exists, hash is non-missing",
        ),
        PromotionGate(
            tier="GREEN",
            name="tools_surface_intact",
            weight=0.8,
            description="Live tools/call surface is non-empty",
        ),
        PromotionGate(
            tier="GREEN",
            name="floors_declared",
            weight=0.5,
            description="At least one F1-F13 floor is declared in the constitution",
        ),
    ],
}


def _healthy_status(health: dict[str, Any]) -> bool:
    """Tolerate a few common healthy response shapes."""
    if not health:
        return False
    status = health.get("status") or health.get("verdict") or ""
    if isinstance(status, bool):
        return status
    if not isinstance(status, str):
        return False
    s = status.strip().upper()
    return s in ("HEALTHY", "OK", "WELL_PASS", "VERIFIED", "TRUE")


def compute_tier(
    organ: OrganConstitution,
    health: dict[str, Any],
    tool_count: int = 0,
) -> tuple[Tier, list[str]]:
    """Apply promotion gates. Returns (tier, conditions_list).

    The conditions_list documents WHY the organ is at that tier. This is the
    F2 audit trail — every tier decision is reproducible from these conditions.

    Promotion is cumulative: GREEN requires YELLOW + RED + BLACK checks to pass.
    Demotion is fail-closed: any failed check drops the tier to the next
    lower tier.
    """
    conditions: list[str] = []

    # BLACK: no health response at all
    if not health:
        conditions.append("BLACK: no health response (organ unreachable)")
        return "BLACK", conditions

    # RED: any response received
    conditions.append(f"RED: health probe returned (status={health.get('status', 'unknown')})")

    # YELLOW: healthy status
    if not _healthy_status(health):
        conditions.append(
            f"YELLOW gate FAILED: status='{health.get('status', 'unknown')}' not in healthy set"
        )
        return "RED", conditions

    conditions.append(f"YELLOW: health probe healthy (status={health.get('status', '?')})")

    # GREEN checks (cumulative)
    if organ.canonical_text_hash == "sha256:missing":
        conditions.append(f"GREEN gate FAILED: constitution file missing for {organ.organ_id}")
        return "YELLOW", conditions
    conditions.append(f"GREEN: constitution loaded (hash={organ.canonical_text_hash[:24]}...)")

    if tool_count <= 0:
        conditions.append(f"GREEN gate FAILED: tool surface empty (tool_count={tool_count})")
        return "YELLOW", conditions
    conditions.append(f"GREEN: tool surface intact (tool_count={tool_count})")

    if not organ.floors:
        conditions.append("GREEN gate FAILED: no F1-F13 floors declared in constitution")
        return "YELLOW", conditions
    conditions.append(f"GREEN: {len(organ.floors)} F1-F13 floor(s) declared")

    conditions.append("GREEN: all promotion gates satisfied")
    return "GREEN", conditions


def assess_organ(
    organ_id: str,
    health: dict[str, Any] | None = None,
    tool_count: int = 0,
) -> tuple[OrganConstitution, Tier, list[str]]:
    """One-stop assessment: load constitution + apply gates.

    Returns (constitution, tier, conditions). Use this for both the per-organ
    endpoint and the aggregate.
    """
    constitution = load_organ_constitution(organ_id)
    health = health or {}
    tier, conditions = compute_tier(constitution, health, tool_count)
    return constitution, tier, conditions


def aggregate_tier(tiers: list[Tier]) -> Tier:
    """Aggregate tier of a federation. Worst-organ wins (conservative)."""
    if not tiers:
        return "BLACK"
    order = ["GREEN", "YELLOW", "RED", "BLACK"]
    worst = min(tiers, key=lambda t: order.index(t))
    return worst


def tier_color(tier: Tier) -> str:
    """Map tier → 4-bit ANSI color (for logs and CLI surfaces)."""
    return {
        "GREEN": "🟢",
        "YELLOW": "🟡",
        "RED": "🔴",
        "BLACK": "⚫",
    }[tier]
