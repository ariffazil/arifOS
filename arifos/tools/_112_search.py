"""
arifOS 112_SEARCH — Web Intelligence & Grounding

Stage: 112_SEARCH | Trinity: Δ | Floors: F2, F3, F4, F10

Purpose: Direct web search via MiniMax MCP bridge.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from arifos.integrations.minimax_mcp_bridge import minimax_bridge
from arifos.core.governance import (
    ThermodynamicMetrics,
    governed_return,
)

logger = logging.getLogger(__name__)


async def execute(
    query: str,
    operator_id: str | None = None,
    session_id: str | None = None,
    max_results: int = 5,
) -> dict:
    """
    arifos_112_search — Web Intelligence & Grounding

    Performs a live web search using the MiniMax MCP bridge.
    """
    try:
        search_result = await minimax_bridge.web_search(query, max_results=max_results)

        if search_result["status"] != "success":
            report = {
                "query": query,
                "status": "error",
                "error": search_result.get("error", "Unknown search error"),
                "verdict": "VOID",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            metrics = ThermodynamicMetrics(
                truth_score=0.5,
                delta_s=0.05,
                omega_0=0.045,
                peace_squared=0.8,
                amanah_lock=True,
                tri_witness_score=0.33,
                stakeholder_safety=1.0,
            )
            return governed_return(
                "arifos_112_search", report, metrics, operator_id, session_id
            )

        report = {
            "query": query,
            "status": "success",
            "hits": search_result.get("hits", []),
            "result_count": search_result.get("result_count", 0),
            "answer": search_result.get("answer"),
            "verdict": "SEAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Metrics for search are derived from bridge quality
        bridge_metrics = search_result.get("metrics", {})
        metrics = ThermodynamicMetrics(
            truth_score=bridge_metrics.get("f2_truth_score", 0.99),
            delta_s=-0.05,
            omega_0=0.045,
            peace_squared=1.1,
            amanah_lock=True,
            tri_witness_score=bridge_metrics.get("f3_earth_witness", 0.95),
            stakeholder_safety=1.0,
        )

        return governed_return(
            "arifos_112_search", report, metrics, operator_id, session_id
        )

    except Exception as exc:
        logger.error("arifos_112_search failed: %s", exc)
        report = {
            "query": query,
            "status": "error",
            "error": str(exc),
            "verdict": "VOID",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        metrics = ThermodynamicMetrics(
            truth_score=0.5,
            delta_s=0.05,
            omega_0=0.045,
            peace_squared=0.8,
            amanah_lock=True,
            tri_witness_score=0.33,
            stakeholder_safety=1.0,
        )
        return governed_return(
            "arifos_112_search", report, metrics, operator_id, session_id
        )
