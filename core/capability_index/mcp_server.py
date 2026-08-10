#!/usr/bin/env python3
"""Capability Index MCP Server — contextual tool discovery for all agents.

Exposes tools:
  • capability_search — semantic retrieval over all indexed MCP tools
  • capability_select — ranked, filtered, reasoned candidate selection
  • capability_reindex — triggers discovery and constitutional classification sweep

Run via stdio (for agent MCP clients):
    python3 mcp_server.py

Run via HTTP (for remote agents):
    python3 mcp_server.py --port 18084

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import argparse
import logging
from typing import Literal, Optional

from capability_index.models import CapabilityRecord
from capability_index.store import CapabilityStore
from capability_index.indexer import auto_reindex
from fastmcp import FastMCP
from pydantic import BaseModel, Field

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
    action_class: str
    effective_class: str
    authority_ceiling: str
    relevance_score: float = Field(..., description="Cosine similarity score")
    reason: str = Field(..., description="Why this tool was selected")


def _rank_and_filter(
    records: list[CapabilityRecord],
    scores: list[float],
    risk_tier: Literal["low", "medium", "high"] | None,
    action_class: Optional[str],
    max_candidates: int,
) -> list[Candidate]:
    """Apply ranking heuristics + constitutional policy filters."""
    candidates: list[Candidate] = []

    for rec, score in zip(records, scores):
        # Action class filter
        if action_class and rec.effective_class != action_class and rec.action_class != action_class:
            continue

        # Risk filter
        if risk_tier == "low":
            if rec.effective_class in ("MUTATE", "SEAL"):
                continue
            if rec.epistemic_tag in ("HYPOTHESIS",):
                continue
            if rec.tool_name in (
                "arif_vault_seal",
                "arif_forge_execute",
                "wealth_ledger_write",
                "forge_execute",
                "forge_shell",
            ):
                continue

        reason = f"Semantic match (score={score:.3f})"
        if rec.epistemic_tag == "CLAIM":
            reason += " | High-evidence tool"
        elif rec.epistemic_tag == "ESTIMATE":
            reason += " | Model-based estimate"

        if rec.effective_class == "OBSERVE":
            reason += " | Stateless/Safe (OBSERVE)"
        elif rec.effective_class == "GOVERN":
            reason += " | Governed/Session-bound (GOVERN)"
        elif rec.effective_class == "MUTATE":
            reason += " | Mutating/Lease-bound (MUTATE)"
        elif rec.effective_class == "SEAL":
            reason += " | Constitutional Seal (SEAL)"

        candidates.append(
            Candidate(
                tool_name=rec.tool_name,
                server=rec.server,
                description=rec.description,
                tags=rec.tags,
                epistemic_tag=rec.epistemic_tag,
                action_class=rec.action_class,
                effective_class=rec.effective_class,
                authority_ceiling=rec.authority_ceiling,
                relevance_score=score,
                reason=reason,
            )
        )

    # Sort by relevance score desc
    candidates.sort(key=lambda c: c.relevance_score, reverse=True)
    return candidates[:max_candidates]


# ── MCP Tools ────────────────────────────────────────────────────────────────


@mcp.tool()
def capability_search(
    query: str,
    limit: int = 10,
    action_class: Optional[Literal["OBSERVE", "GOVERN", "MUTATE", "SEAL"]] = None,
    server: Optional[str] = None,
) -> str:
    """Semantic search over the federation's full tool index.

    Use this when you need to find which tool can handle a task,
    without bloating prompt context with raw schemas.
    """
    results = store.search(query, limit=limit, action_class=action_class, server=server)
    lines = [f"Found {len(results)} tools for query: {query!r}", ""]
    for idx, r in enumerate(results, 1):
        lines.append(
            f"{idx}. {r.tool_name} ({r.server}) [{r.effective_class}]\n"
            f"   {r.description}\n"
            f"   Tags: {', '.join(r.tags)} | Quality: {r.epistemic_tag} | Ceiling: {r.authority_ceiling}"
        )
    return "\n".join(lines)


@mcp.tool()
def capability_select(
    intent: str,
    context: str = "",
    risk_tier: Literal["low", "medium", "high"] = "medium",
    action_class: Optional[Literal["OBSERVE", "GOVERN", "MUTATE", "SEAL"]] = None,
    max_candidates: int = 7,
) -> str:
    """Ranked, filtered tool selection with constitutional reasons.

    Filters by risk tier and constitutional class, ranks by evidence quality,
    and returns a shortlist with justification.

    Args:
        intent: What you want to accomplish
        context: Extra context (repo, file, current task)
        risk_tier: low | medium | high — filters out irreversible tools at low
        action_class: Optional filter: OBSERVE | GOVERN | MUTATE | SEAL
        max_candidates: How many tools to return (default 7)
    """
    query = f"{intent}. Context: {context}".strip()
    raw_results = store.search(query, limit=30, action_class=action_class)

    if not raw_results:
        return f"No matching capabilities found for intent: {intent!r}"

    encoder = store._get_encoder()
    if encoder is not None:
        try:
            import numpy as np
            query_vec = encoder.encode([query], show_progress_bar=False)[0]
            texts = [r.to_embedding_text() for r in raw_results]
            result_vecs = encoder.encode(texts, show_progress_bar=False)

            scores = np.dot(result_vecs, query_vec) / (
                np.linalg.norm(result_vecs, axis=1) * np.linalg.norm(query_vec) + 1e-9
            )
            scores = scores.tolist()
        except Exception:
            scores = [1.0 / (idx + 1) for idx in range(len(raw_results))]
    else:
        scores = [1.0 / (idx + 1) for idx in range(len(raw_results))]

    candidates = _rank_and_filter(raw_results, scores, risk_tier, action_class, max_candidates)

    lines = [
        f"Intent: {intent!r}",
        f"Risk tier: {risk_tier} | Class filter: {action_class or 'ANY'} | Max: {max_candidates}",
        f"Selected {len(candidates)} tools:",
        "",
    ]
    for idx, c in enumerate(candidates, 1):
        lines.append(
            f"{idx}. {c.tool_name} ({c.server}) [{c.effective_class}]\n"
            f"   {c.description}\n"
            f"   Tags: {', '.join(c.tags)} | Quality: {c.epistemic_tag}\n"
            f"   Score: {c.relevance_score:.3f} | Reason: {c.reason}"
        )
    return "\n".join(lines)


@mcp.tool()
def capability_reindex(force: bool = False) -> str:
    """Trigger an immediate discovery and classification sweep across all MCP servers."""
    res = auto_reindex(force=force)
    return (
        f"Capability Index Reindexed: Status={res.get('status')} | "
        f"Tools={res.get('tool_count')} | Digest={res.get('digest', '')[:12]} | "
        f"VectorStoreOk={res.get('vector_store_ok')}"
    )


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
