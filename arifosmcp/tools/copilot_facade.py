"""arifosmcp/tools/copilot_facade.py — Enterprise Read Facade (Profile B).

Provides stateless, single-turn tools for enterprise orchestrators (Microsoft Copilot Studio,
Semantic Kernel, Power Platform) with automatic ephemeral session management.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# Envelope-tolerant keyword-only params every public tool must accept.
# The ingress middleware injects _envelope/actor_id/session_id into
# msg.arguments BEFORE FastMCP validates input; a tool whose signature
# rejects them dies with CONTRACT_VIOLATION on the public path while
# passing every in-process unit test (failure class observed 2026-10-28:
# all 5 coordination tools returned "Error calling tool" remotely).


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


async def arif_research(
    query: str,
    domain: str = "general",
    _envelope: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Enterprise research: execute observation and reasoning in one call.

    Gathers grounded evidence across web, literature, and kernel reality,
    then decomposes findings under epistemic truth floors.

    Honesty contract: status is "ok" ONLY when both inner passes ran and
    produced evidence. Any inner failure or empty evidence => "degraded"
    with machine-readable degraded_reasons. Never "ok" on empty truth.
    """
    sid, stok = _get_ephemeral_session(f"enterprise-research: {query}")
    facts: list[str] = []
    synthesis: str = ""
    degraded_reasons: list[str] = []

    if not sid:
        degraded_reasons.append("ephemeral_session_unavailable")

    try:
        from arifosmcp.tools.sense import arif_observe

        obs = arif_observe(
            mode="search",
            query=query,
            session_id=sid,
            session_token=stok,
            actor_id=actor_id or "copilot-facade",
        )
        if isinstance(obs, dict):
            obs_facts = obs.get("facts") or obs.get("result", {}).get("facts") or []
            if isinstance(obs_facts, list):
                facts.extend([str(f) for f in obs_facts[:8]])
            elif obs.get("status") == "error" or obs.get("isError"):
                degraded_reasons.append("observe_pass_error")
        else:
            degraded_reasons.append("observe_pass_non_dict")
    except Exception as exc:
        logger.warning("arif_research observe pass failed: %s", exc)
        degraded_reasons.append(f"observe_pass_exception: {type(exc).__name__}")

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
        else:
            degraded_reasons.append("think_pass_non_dict")
    except Exception as exc:
        logger.warning("arif_research think pass failed: %s", exc)
        degraded_reasons.append(f"think_pass_exception: {type(exc).__name__}")

    facts = list(dict.fromkeys(facts))[:10]
    if not facts and not synthesis:
        degraded_reasons.append("no_evidence_gathered")

    status = "ok" if not degraded_reasons else "degraded"
    fallback = "Observation completed. Review facts above." if status == "ok" else ""
    out: dict[str, Any] = {
        "status": status,
        "query": query,
        "domain": domain,
        "facts": facts,
        "synthesis": synthesis or fallback,
        "session_id": sid,
    }
    if degraded_reasons:
        out["degraded_reasons"] = degraded_reasons
    return out


async def arif_recall(
    query: str,
    tier: str = "L2",
    _envelope: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Enterprise memory recall: query governed knowledge tiers.

    Searches persistent knowledge, verified lessons, and constitutional canon.

    Honesty contract: "ok" only when the memory pass ran AND returned
    entries. Empty evidence or unavailable handler => "degraded".
    """
    sid, stok = _get_ephemeral_session(f"enterprise-recall: {query}")
    degraded_reasons: list[str] = []
    if not sid:
        degraded_reasons.append("ephemeral_session_unavailable")
    try:
        from arifosmcp.runtime.tools import _CANONICAL_HANDLERS

        mem_fn = _CANONICAL_HANDLERS.get("arif_memory")
        if mem_fn is None:
            return {
                "status": "degraded",
                "query": query,
                "tier": tier,
                "count": 0,
                "entries": [],
                "degraded_reasons": ["memory_handler_unavailable"],
            }
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
            if not isinstance(entries, list):
                entries = []
            if not entries:
                degraded_reasons.append("no_matching_evidence")
            out: dict[str, Any] = {
                "status": "ok" if not degraded_reasons else "degraded",
                "query": query,
                "tier": tier,
                "count": len(entries),
                "entries": entries,
            }
            if degraded_reasons:
                out["degraded_reasons"] = degraded_reasons
            return out
        return {
            "status": "degraded",
            "query": query,
            "tier": tier,
            "count": 0,
            "entries": [],
            "degraded_reasons": degraded_reasons + ["memory_pass_non_dict"],
        }
    except Exception as exc:
        logger.warning("arif_recall failed: %s", exc)
        return {"status": "error", "query": query, "error": str(exc)}


async def arif_delegate(
    query: str,
    organ: str = "",
    _envelope: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Enterprise intent routing: classify natural language query and route to organ.

    Routes intent to specialist organs: GEOX (geoscience), WEALTH (capital),
    WELL (vitality), or A-FORGE (execution).

    Honesty contract: "ok" only when the router actually classified the
    intent. Missing handler, non-dict result, or UNKNOWN organ => "degraded".
    """
    sid, stok = _get_ephemeral_session(f"enterprise-delegate: {query}")
    degraded_reasons: list[str] = []
    if not sid:
        degraded_reasons.append("ephemeral_session_unavailable")
    try:
        from arifosmcp.runtime.tools import _CANONICAL_HANDLERS

        route_fn = _CANONICAL_HANDLERS.get("arif_route")
        if route_fn is None:
            return {
                "status": "degraded",
                "intent": query,
                "target_organ": organ or "UNKNOWN",
                "degraded_reasons": ["route_handler_unavailable"],
            }
        res = route_fn(intent=query, session_id=sid, session_token=stok)
        import inspect as _inspect
        if _inspect.isawaitable(res):
            res = await res
        if isinstance(res, dict):
            result = res.get("result", {})
            target_organ = result.get("target_organ") or res.get("target_organ") or organ
            dispatch = result.get("dispatch_envelope") or res.get("dispatch_envelope") or {}
            if not target_organ or str(target_organ).upper() == "UNKNOWN":
                degraded_reasons.append("intent_unclassified")
            out: dict[str, Any] = {
                "status": "ok" if not degraded_reasons else "degraded",
                "intent": query,
                "target_organ": target_organ or "UNKNOWN",
                "dispatch_envelope": dispatch,
            }
            if degraded_reasons:
                out["degraded_reasons"] = degraded_reasons
            return out
        return {
            "status": "degraded",
            "intent": query,
            "target_organ": organ or "UNKNOWN",
            "degraded_reasons": degraded_reasons + ["route_pass_non_dict"],
        }
    except Exception as exc:
        logger.warning("arif_delegate failed: %s", exc)
        return {"status": "error", "intent": query, "error": str(exc)}


def register_copilot_facade(mcp_server: Any, *, ingress_middleware: Any | None = None) -> list[str]:
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
        from arifosmcp.runtime.ingress_middleware import register_tool_param_sets

        register_tool_param_sets(
            ingress_middleware,
            {
                "arif_research": arif_research,
                "arif_recall": arif_recall,
                "arif_delegate": arif_delegate,
            },
        )
        logger.info("COPILOT FACADE: registered arif_research, arif_recall, arif_delegate")
    except Exception as exc:
        logger.warning("Failed to register copilot facade tools: %s", exc)
    return registered
