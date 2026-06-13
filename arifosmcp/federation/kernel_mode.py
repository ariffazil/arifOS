"""
arifosmcp/federation/kernel_mode.py
══════════════════════════════════════════════════════════════════════════════
Wire the FederationConstitution aggregate into arif_kernel_route.

This adds a NEW MODE on the EXISTING canonical tool `arif_kernel_route` —
NO new tool is added to the 13-tool surface. The 13 stays at 13.

New mode: mode="federation_status"

Returns the FederationConstitution aggregate (cached 30s by default).
Optional `force_refresh=true` bypasses the cache.

DITEMPA BUKAN DIBEI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("arifosmcp.federation.kernel_mode")


def federation_status(
    force_refresh: bool = False,
    summary_only: bool = False,
) -> dict[str, Any]:
    """The arif_kernel_route(mode='federation_status') handler.

    Returns the aggregate FederationConstitution as a dict, ready to be
    passed through the kernel envelope. The cache is 30s; pass
    force_refresh=True to bypass.
    """
    from arifosmcp.federation.constitution_aggregator import (
        as_dict,
        get_federation_constitution,
    )

    fc = get_federation_constitution(force_refresh=force_refresh)
    if summary_only:
        from arifosmcp.federation.promotion_gates import tier_color

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

    return as_dict(fc)


def list_federation_modes() -> list[str]:
    """List of mode values this module supports on arif_kernel_route."""
    return ["federation_status", "federation_summary"]
