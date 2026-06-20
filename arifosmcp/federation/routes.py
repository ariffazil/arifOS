"""
arifosmcp/federation/routes.py
══════════════════════════════════════════════════════════════════════════════
FastAPI REST routes exposing the FederationConstitution.

Three endpoints:
  GET /federation/constitution           — full aggregate (all organs)
  GET /federation/constitution/{organ}   — single organ constitution + live tier
  GET /federation/promotion-gates       — gate criteria + tier color legend

All endpoints are read-only (F1 AMANAH: no mutation, no auth required for
read; the data is already public via /health). The aggregate is cached
30s by default to keep organ probes light.

Mounted on the main FastAPI app at import time, with no new tool surface.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from arifosmcp.federation.constitution_aggregator import (
    as_dict,
    get_federation_constitution,
)
from arifosmcp.federation.organ_constitution import (
    list_known_organs,
)
from arifosmcp.federation.promotion_gates import (
    PROMOTION_GATES,
    assess_organ,
    tier_color,
)

logger = logging.getLogger("arifosmcp.federation.routes")

router = APIRouter(prefix="/federation", tags=["federation"])


# ═════════════════════════════════════════════════════════════════════════════
# GET /federation/constitution
# ═════════════════════════════════════════════════════════════════════════════


@router.get("/constitution")
def get_constitution(force_refresh: bool = False) -> dict[str, Any]:
    """Full FederationConstitution aggregate. Hashable, F2-auditable.

    Optional query param `force_refresh=true` bypasses the 30s cache.
    """
    fc = get_federation_constitution(force_refresh=force_refresh)
    return as_dict(fc)


@router.get("/constitution/summary")
def get_constitution_summary() -> dict[str, Any]:
    """Compact summary — no per-organ payload, just counts + aggregate hash.

    Cheaper to poll. Useful for liveness dashboards.
    """
    fc = get_federation_constitution()
    return {
        "federation_id": fc.federation_id,
        "version": fc.version,
        "as_of": fc.as_of.isoformat(),
        "aggregate_tier": fc.aggregate_tier,
        "aggregate_color": tier_color(fc.aggregate_tier),
        "total_organs": fc.total_organs,
        "green_organs": fc.green_organs,
        "yellow_organs": fc.yellow_organs,
        "red_organs": fc.red_organs,
        "black_organs": fc.black_organs,
        "federation_constitution_hash": fc.federation_constitution_hash,
        "pending_promotions_count": len(fc.pending_promotions),
        "pending_demotions_count": len(fc.pending_demotions),
    }


# ═════════════════════════════════════════════════════════════════════════════
# GET /federation/constitution/{organ_id}
# ═════════════════════════════════════════════════════════════════════════════


@router.get("/constitution/{organ_id}")
def get_organ_constitution(organ_id: str) -> dict[str, Any]:
    """Single organ's constitution + live tier + promotion conditions.

    Includes the LIVE health probe and tool count (synchronous, not cached
    per-organ — only the aggregate is cached).
    """
    if organ_id not in list_known_organs():
        raise HTTPException(
            status_code=404,
            detail={
                "error": "unknown_organ",
                "organ_id": organ_id,
                "known_organs": list_known_organs(),
            },
        )

    # Get live health via the synchronous fallback in the aggregator
    from arifosmcp.federation.constitution_aggregator import (
        _call_organ_health_sync,
        _list_organ_tools_sync,
    )

    health = _call_organ_health_sync(organ_id)
    tools = _list_organ_tools_sync(organ_id)
    tool_count = len(tools or [])

    constitution, tier, conditions = assess_organ(organ_id, health, tool_count)
    return {
        "organ_id": organ_id,
        "tier": tier,
        "tier_color": tier_color(tier),
        "constitution": constitution.model_dump(mode="json"),
        "live": {
            "health": health,
            "tool_count": tool_count,
        },
        "promotion_conditions": conditions,
    }


# ═════════════════════════════════════════════════════════════════════════════
# GET /federation/promotion-gates
# ═════════════════════════════════════════════════════════════════════════════


@router.get("/promotion-gates")
def get_promotion_gates() -> dict[str, Any]:
    """The promotion gate criteria. Documents WHY an organ is at a given tier.

    Useful for governance audits and for the bench (P2) to reference.
    """
    return {
        "tiers": {
            tier: [
                {
                    "name": g.name,
                    "weight": g.weight,
                    "description": g.description,
                }
                for g in gates
            ]
            for tier, gates in PROMOTION_GATES.items()
        },
        "color_legend": {
            "GREEN": "🟢 healthy + constitution loaded + tools surface intact",
            "YELLOW": "🟡 healthy but constitution file missing",
            "RED": "🔴 organ reachable but degraded",
            "BLACK": "⚫ organ not reachable",
        },
        "note": (
            "Cumulative: GREEN requires YELLOW + RED + BLACK checks to pass. "
            "Any failed check drops the organ to the next lower tier. "
            "F2-honest: YELLOW is the honest baseline; GREEN requires evidence."
        ),
    }


# ═════════════════════════════════════════════════════════════════════════════
# GET /federation/organs
# ═════════════════════════════════════════════════════════════════════════════


@router.get("/organs")
def list_organs() -> dict[str, Any]:
    """List known organs (no live data — just declarations)."""
    return {
        "organs": list_known_organs(),
        "count": len(list_known_organs()),
    }
