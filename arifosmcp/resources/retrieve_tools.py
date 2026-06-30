"""
arifosmcp/resources/retrieve_tools.py — BM25 Tool Retrieval Registration
═══════════════════════════════════════════════════════════════════════════

Registers arif_retrieve_tools on the MCP surface.
Diagnostic tool — always available in expanded45 surface.
Read-only, deterministic, zero-infra BM25 retrieval.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP


def register_retrieve_tools(mcp: FastMCP) -> list[str]:
    """Register arif_retrieve_tools — BM25 lexical tool retrieval.

    Read-only diagnostic. Internal operator aid only; hidden from the default
    public 7-verb MCP facade unless dev tools are explicitly enabled.
    F2 TRUTH: scores are lexical match, not confidence.
    F7 HUMILITY: term-frequency ranking, not semantic relevance.
    """
    import os

    expose_dev_tools = os.getenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "false").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    if not expose_dev_tools:
        return []

    from arifosmcp.tools.retrieve_tools import arif_retrieve_tools as _handler

    @mcp.tool(
        name="arif_retrieve_tools",
        description=(
            "BM25 lexical tool retrieval across the arifOS federation tool catalog. "
            "Schema-aware text projection: tool name + description + parameter names + enum values, "
            "JSON syntax stripped. k1=0.9 b=0.4 tuned for short tool descriptions (Ratel ADR-0004). "
            "Cross-organ by default; set organ= to restrict to one organ. "
            "F2 TRUTH: BM25 scores are TERM FREQUENCY lexical match, NOT confidence. "
            "F7 HUMILITY: Scores measure keyword overlap, not semantic relevance. "
            "Use as DISCOVERY hints to find the right tool, then verify with arif_resolve_tool. "
            "Pair with arif_route for the full pipeline: intent → organ → BM25 rank → select. "
            "Parameters: query (natural language intent), organ (optional, restrict to organ), "
            "top_k (1-20, default 5), include_scores (default true)."
        ),
        tags={"retrieval", "discovery", "bm25", "lexical", "read-only"},
    )
    async def _arif_retrieve_tools_wrapped(
        query: str,
        organ: str | None = None,
        top_k: int = 5,
        include_scores: bool = True,
        _envelope: Any = None,
        actor_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        return await _handler(
            query=query,
            organ=organ,
            top_k=top_k,
            include_scores=include_scores,
            _envelope=_envelope,
            actor_id=actor_id,
            session_id=session_id,
        )

    return ["arif_retrieve_tools"]
