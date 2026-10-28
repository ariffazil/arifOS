"""arifosmcp/tools/copilot_facade.py — Enterprise Read Facade (Profile B).

Provides stateless, single-turn tools for enterprise orchestrators (Microsoft Copilot Studio,
Semantic Kernel, Power Platform) with automatic ephemeral session management.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def _get_ephemeral_session(intent: str) -> tuple[str, str]:
    """Mint or retrieve an ephemeral read-only session for stateless callers."""
    try:
        from arifosmcp.runtime.tools import _arif_session_init

        res = _arif_session_init(mode="preflight", intent=intent, verbosity="minimal")
        if hasattr(res, "session_id") and hasattr(res, "session_token"):
            return str(res.session_id), str(res.session_token)
        if isinstance(res, dict):
            sid = res.get("session_id") or res.get("result", {}).get("session_id") or ""
            stok = res.get("session_token") or res.get("result", {}).get("session_token") or ""
            return str(sid), str(stok)
    except Exception as exc:
        logger.warning("Failed to mint ephemeral session: %s", exc)
    return "", ""


async def arif_research(query: str, domain: str = "general") -> dict[str, Any]:
    """Enterprise research: execute observation and reasoning in one call.

    Gathers grounded evidence across web, literature, and kernel reality,
    then decomposes findings under epistemic truth floors.
    """
    sid, stok = _get_ephemeral_session(f"enterprise-research: {query}")
    facts: list[str] = []
    synthesis: str = ""

    try:
        from arifosmcp.tools.sense import arif_observe

        obs = arif_observe(mode="search", query=query, session_id=sid, session_token=stok)
        if isinstance(obs, dict):
            obs_facts = obs.get("facts") or obs.get("result", {}).get("facts") or []
            if isinstance(obs_facts, list):
                facts.extend([str(f) for f in obs_facts[:8]])
    except Exception as exc:
        logger.warning("arif_research observe pass failed: %s", exc)

    try:
        from arifosmcp.tools.embodied_instances.arif_think_handler import (
            embodied_mind_reason_handler,
        )

        think = await embodied_mind_reason_handler(
            mode="reason", query=query, session_id=sid, session_token=stok
        )
        if isinstance(think, dict):
            synthesis = str(
                think.get("result", {}).get("synthesis")
                or think.get("synthesis")
                or think.get("result", {}).get("conclusion")
                or ""
            )
            think_facts = think.get("facts") or think.get("result", {}).get("facts") or []
            if isinstance(think_facts, list):
                facts.extend([str(f) for f in think_facts[:5]])
    except Exception as exc:
        logger.warning("arif_research think pass failed: %s", exc)

    return {
        "status": "ok",
        "query": query,
        "domain": domain,
        "facts": list(dict.fromkeys(facts))[:10],
        "synthesis": synthesis or "Observation completed. Review facts above.",
        "session_id": sid,
    }


async def arif_recall(query: str, tier: str = "L2") -> dict[str, Any]:
    """Enterprise memory recall: query governed knowledge tiers.

    Searches persistent knowledge, verified lessons, and constitutional canon.
    """
    sid, stok = _get_ephemeral_session(f"enterprise-recall: {query}")
    try:
        from arifosmcp.runtime.tools import _CANONICAL_HANDLERS

        mem_fn = _CANONICAL_HANDLERS.get("arif_memory")
        if mem_fn:
            res = mem_fn(mode="recall", query=query, tier=tier, session_id=sid, session_token=stok)
            import inspect as _inspect
            if _inspect.isawaitable(res):
                res = await res
            if isinstance(res, dict):
                entries = (
                    res.get("result", {}).get("entries")
                    or res.get("entries")
                    or res.get("result", {}).get("matches")
                    or []
                )
                return {
                    "status": "ok",
                    "query": query,
                    "tier": tier,
                    "count": len(entries) if isinstance(entries, list) else 0,
                    "entries": entries,
                }
    except Exception as exc:
        logger.warning("arif_recall failed: %s", exc)
        return {"status": "error", "query": query, "error": str(exc)}

    return {"status": "ok", "query": query, "tier": tier, "count": 0, "entries": []}


async def arif_delegate(query: str, organ: str = "") -> dict[str, Any]:
    """Enterprise intent routing: classify natural language query and route to organ.

    Routes intent to specialist organs: GEOX (geoscience), WEALTH (capital),
    WELL (vitality), or A-FORGE (execution).
    """
    sid, stok = _get_ephemeral_session(f"enterprise-delegate: {query}")
    try:
        from arifosmcp.runtime.tools import _CANONICAL_HANDLERS

        route_fn = _CANONICAL_HANDLERS.get("arif_route")
        if route_fn:
            res = route_fn(intent=query, session_id=sid, session_token=stok)
            import inspect as _inspect
            if _inspect.isawaitable(res):
                res = await res
            if isinstance(res, dict):
                target_organ = res.get("result", {}).get("target_organ") or res.get("target_organ") or organ
                dispatch = res.get("result", {}).get("dispatch_envelope") or res.get("dispatch_envelope") or {}
                return {
                    "status": "ok",
                    "intent": query,
                    "target_organ": target_organ,
                    "dispatch_envelope": dispatch,
                }
    except Exception as exc:
        logger.warning("arif_delegate failed: %s", exc)
        return {"status": "error", "intent": query, "error": str(exc)}

    return {"status": "ok", "intent": query, "target_organ": organ or "UNKNOWN"}


def register_copilot_facade(mcp_server: Any) -> list[str]:
    """Register Profile B (Enterprise Read) tools onto FastMCP server."""
    registered = []
    try:
        mcp_server.tool(
            name="arif_research",
            description="Enterprise research pass: gathers reality observations and structures reasoning under truth floors in a single call.",
            tags={"copilot", "enterprise", "research"},
            annotations={"readOnlyHint": True, "destructiveHint": False},
        )(arif_research)
        registered.append("arif_research")

        mcp_server.tool(
            name="arif_recall",
            description="Enterprise recall: retrieve persistent knowledge, verified lessons, and canon from memory tiers.",
            tags={"copilot", "enterprise", "memory"},
            annotations={"readOnlyHint": True, "destructiveHint": False},
        )(arif_recall)
        registered.append("arif_recall")

        mcp_server.tool(
            name="arif_delegate",
            description="Enterprise intent router: classifies user intent and prepares a dispatch envelope for specialist organs (GEOX, WEALTH, WELL, A-FORGE).",
            tags={"copilot", "enterprise", "routing"},
            annotations={"readOnlyHint": True, "destructiveHint": False},
        )(arif_delegate)
        registered.append("arif_delegate")
        logger.info("COPILOT FACADE: registered arif_research, arif_recall, arif_delegate")
    except Exception as exc:
        logger.warning("Failed to register copilot facade tools: %s", exc)
    return registered
