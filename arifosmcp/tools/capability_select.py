"""Capability Select — semantic tool discovery for agents.

Queries the Qdrant mcp_capabilities collection using bge-m3 embeddings.
Returns ranked tool cards for the given task context.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

OLLAMA_URL = "http://127.0.0.1:11434"
QDRANT_URL = "http://127.0.0.1:6333"
COLLECTION = "mcp_capabilities"
EMBED_MODEL = "bge-m3:latest"
_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


async def arif_capability_select(
    query: str,
    limit: int = 5,
    risk_filter: str = "all",
    server_filter: str = "",
) -> dict[str, Any]:
    """Semantic tool discovery for agents.

    Given a task description, finds the most relevant tools across the
    federation capability index using vector search over tool descriptors.

    Args:
        query: Natural language task description (e.g. "analyze investment returns")
        limit: Max tools to return (1-20, default 5)
        risk_filter: "all" (default), "green", "yellow", "orange"
        server_filter: Only return tools from this server (empty = all)

    Returns:
        Ranked list of capability cards with tool name, server, description,
        risk tier, approval policy, and relevance score.

    Constraints:
        - Advisory only — tool availability does not grant execution authority
        - Governance filtering (floors) is handled by the arifOS kernel separately
        - F13 SOVEREIGN: no tool discovery bypasses floor enforcement
    """
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        # 1. Embed query
        embed_r = await client.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": query},
        )
        if embed_r.status_code != 200:
            return {
                "verdict": "FAIL",
                "tool": "arif_capability_select",
                "error": f"Ollama embed failed: {embed_r.status_code}",
                "note": "bge-m3 must be running on Ollama (port 11434)",
            }
        query_vec = embed_r.json()["embeddings"][0]

        # 2. Search Qdrant
        search_payload = {
            "vector": query_vec,
            "limit": min(max(limit, 1), 20),
            "with_payload": True,
        }
        if server_filter:
            search_payload["filter"] = {
                "must": [{"key": "server", "match": {"value": server_filter}}]
            }
        if risk_filter and risk_filter != "all":
            search_payload.setdefault("filter", {}).setdefault("must", []).append({
                "key": "risk_tier",
                "match": {"value": risk_filter},
            })

        srch_r = await client.post(
            f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
            json=search_payload,
        )
        if srch_r.status_code != 200:
            return {
                "verdict": "FAIL",
                "tool": "arif_capability_select",
                "error": f"Qdrant search failed: {srch_r.status_code}",
                "response": srch_r.text[:500],
            }

        hits = srch_r.json().get("result", [])

    # 3. Build capability cards
    cards = []
    for hit in hits:
        p = hit.get("payload", {})
        cards.append({
            "name": p.get("name", "?"),
            "server": p.get("server", "?"),
            "description": p.get("description", ""),
            "tags": p.get("tags", []),
            "risk_tier": p.get("risk_tier", "medium"),
            "epistemic_tag": p.get("epistemic_tag", "ESTIMATE"),
            "execution_kind": p.get("execution_kind", "read"),
            "approval_policy": p.get("approval_policy", "auto"),
            "requires_888": p.get("requires_888", False),
            "relevance_score": round(hit.get("score", 0), 4),
        })

    return {
        "verdict": "SEAL",
        "tool": "arif_capability_select",
        "query": query,
        "filters_applied": {
            "risk": risk_filter,
            "server": server_filter or "(all)",
        },
        "results_found": len(cards),
        "cards": cards,
        "governance": {
            "advisory_only": True,
            "execution_requires_judge_seal": True,
            "f13_sovereign": "No tool discovery bypasses floor enforcement",
        },
    }


def _arif_capability_select_tool(query: str, limit: int = 5,
                                 risk_filter: str = "all",
                                 server_filter: str = "") -> str:
    """Sync wrapper for FastMCP tool registration. Returns JSON string."""
    import asyncio
    result = asyncio.run(arif_capability_select(
        query=query, limit=limit, risk_filter=risk_filter,
        server_filter=server_filter,
    ))
    return json.dumps(result, indent=2)
