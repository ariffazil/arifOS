#!/usr/bin/env python3
"""Capability Index MCP Server — contextual tool discovery for all agents.

Exposes two tools:
  • capability_search — semantic retrieval over the 97-tool index
  • capability_select — ranked, filtered, reasoned candidate selection

Run via stdio (for agent MCP clients):
    python3 mcp_server.py

Run via HTTP (for remote agents):
    python3 mcp_server.py --port 18084

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import argparse
import logging
from typing import Literal

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from capability_index.store import CapabilityStore
from capability_index.models import CapabilityRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("capability-index-mcp")

mcp = FastMCP("capability-index")
store = CapabilityStore()


# ── Internal helpers ─────────────────────────────────────────────────────────

class Candidate(BaseModel):
    tool_name: str
    server: str
    description: str
    tags: list[str]
    epistemic_tag: str
    relevance_score: float = Field(..., description="Cosine similarity score")
    reason: str = Field(..., description="Why this tool was selected")


def _rank_and_filter(
    records: list[CapabilityRecord],
    scores: list[float],
    risk_tier: Literal["low", "medium", "high"] | None,
    max_candidates: int,
) -> list[Candidate]:
    """Apply ranking heuristics + policy filters."""
    candidates: list[Candidate] = []

    for rec, score in zip(records, scores):
        # Risk filter
        if risk_tier == "low" and rec.epistemic_tag in ("HYPOTHESIS",):
            continue
        if risk_tier == "low" and rec.tool_name in (
            "arif_vault_seal",
            "arif_forge_execute",
            "wealth_ledger_write",
        ):
            continue

        reason = f"Semantic match (score={score:.3f})"
        if rec.epistemic_tag == "CLAIM":
            reason += " | High-evidence tool"
        elif rec.epistemic_tag == "ESTIMATE":
            reason += " | Model-based estimate"

        candidates.append(
            Candidate(
                tool_name=rec.tool_name,
                server=rec.server,
                description=rec.description,
                tags=rec.tags,
                epistemic_tag=rec.epistemic_tag,
                relevance_score=score,
                reason=reason,
            )
        )

    # Sort by relevance score desc
    candidates.sort(key=lambda c: c.relevance_score, reverse=True)
    return candidates[:max_candidates]


# ── MCP Tools ────────────────────────────────────────────────────────────────

@mcp.tool()
def capability_search(query: str, limit: int = 10) -> str:
    """Semantic search over the federation's 97 MCP tools.

    Use this when you need to find which tool can handle a task,
    but you don't want to load all tool schemas into context.
    """
    results = store.search(query, limit=limit)
    lines = [f"Found {len(results)} tools for query: {query!r}", ""]
    for idx, r in enumerate(results, 1):
        lines.append(
            f"{idx}. {r.tool_name} ({r.server})\n"
            f"   {r.description}\n"
            f"   Tags: {', '.join(r.tags)} | Quality: {r.epistemic_tag}"
        )
    return "\n".join(lines)


@mcp.tool()
def capability_select(
    intent: str,
    context: str = "",
    risk_tier: Literal["low", "medium", "high"] = "medium",
    max_candidates: int = 7,
) -> str:
    """Ranked, filtered tool selection with reasons.

    This is the smarter cousin of capability_search:
    it filters by risk tier, ranks by evidence quality,
    and returns a shortlist with justification.

    Args:
        intent: What you want to accomplish
        context: Extra context (repo, file, current task)
        risk_tier: low | medium | high — filters out irreversible tools at low
        max_candidates: How many tools to return (default 7)
    """
    # Combine intent + context for embedding
    query = f"{intent}. Context: {context}".strip()

    # Fetch top-20 from vector search, then filter/rank
    raw_results = store.search(query, limit=20)

    # Re-compute scores for transparency (store.search doesn't return scores)
    encoder = store._get_encoder()
    query_vec = encoder.encode([query], show_progress_bar=False)[0]
    texts = [r.to_embedding_text() for r in raw_results]
    result_vecs = encoder.encode(texts, show_progress_bar=False)

    import numpy as np

    scores = np.dot(result_vecs, query_vec) / (
        np.linalg.norm(result_vecs, axis=1) * np.linalg.norm(query_vec)
    )
    scores = scores.tolist()

    candidates = _rank_and_filter(raw_results, scores, risk_tier, max_candidates)

    lines = [
        f"Intent: {intent!r}",
        f"Risk tier: {risk_tier} | Max candidates: {max_candidates}",
        f"Selected {len(candidates)} tools:",
        "",
    ]
    for idx, c in enumerate(candidates, 1):
        lines.append(
            f"{idx}. {c.tool_name} ({c.server})\n"
            f"   {c.description}\n"
            f"   Tags: {', '.join(c.tags)} | Quality: {c.epistemic_tag}\n"
            f"   Score: {c.relevance_score:.3f} | Reason: {c.reason}"
        )
    return "\n".join(lines)


# ── Entrypoint ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Capability Index MCP Server")
    parser.add_argument("--port", type=int, default=None, help="HTTP port (stdio if omitted)")
    args = parser.parse_args()

    if args.port:
        logger.info("Starting Capability Index MCP on HTTP port %d", args.port)
        mcp.run(transport="http", port=args.port)
    else:
        logger.info("Starting Capability Index MCP on stdio")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
