"""
arifOS Tool Discovery Resource Registration
═══════════════════════════════════════════════════════════════

Registers the tool discovery resource so LLMs can find the right tool.

DITEMPA BUKAN DIBERI — Discovered, not guessed.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from .tool_discovery_resource import (
    get_tool_discovery_resource_text,
    get_full_affordance_resource_text,
    resolve_tool_name,
    find_tools_by_query,
)


def register_tool_discovery(mcp: FastMCP) -> list[str]:
    """Register tool discovery resource and alias resolver.

    MCP tools (arif_resolve_tool, arif_get_affordance) are gated behind
    ARIFOS_MCP_EXPOSE_DEV_TOOLS=true (F13 canonical13 enforcement).
    Resources (arif://...) are always registered — they don't appear in tools/list.
    """
    import os

    _EXPOSE_DEV_TOOLS = os.getenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "false").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    registered = []

    # DISABLED 2026-06-28 (zen of resources — meta about tool interface, not domain data).
    # AI gets all tools via tools/list (MCP spec). Tool selection guidance is meta,
    # not domain operational data. Keep the gated tools (arif_resolve_tool, arif_get_affordance)
    # since they are actual tools with domain utility.
    #
    # @mcp.resource(uri="arif://tools/discovery", ...)
    # def tool_discovery_resource() -> dict: ...
    # registered.append("arif://tools/discovery")

    # Register alias resolution tool (diagnostic utility — always available in expanded45)
    # Removed ARIFOS_MCP_EXPOSE_DEV_TOOLS gate 2026-06-28: this is a read-only diagnostic
    # that agents need for tool alias resolution. F4 CLARITY: better to resolve than guess.
    # 9-Tool Audit Fix 2 (2026-06-29): absorbs _envelope/actor_id/session_id to prevent
    # FastMCP 3 Pydantic validation errors from transport-injected fields. The resolver
    # ignores these — it only cares about `name`. But it MUST accept them in the signature.

    @mcp.tool(
        name="arif_resolve_tool",
        description=(
            "Resolve a tool name or alias to the canonical arifOS tool name. "
            "Use when you have a tool name but aren't sure if it's the canonical name. "
            "Returns: canonical_name, aliases, callable, schema_valid, authority_class, "
            "use_when, examples. Only `name` is used — all other fields are absorbed and ignored."
        ),
        tags={"discovery", "utility", "read-only"},
    )
    def resolve_tool(
        name: str,
        _envelope: Any = None,
        actor_id: str | None = None,
        session_id: str | None = None,
    ) -> dict:
        """Resolve a tool name or alias to canonical form — pure resolution.

        Takes name (required). Absorbs _envelope, actor_id, session_id from
        transport without using them — prevents FastMCP 3 Pydantic validation
        errors from unexpected keyword injection. The resolver is clean: it only
        cares about the tool name. Everything else is envelope noise.
        """
        # Normalize — strip whitespace, handle empty/None
        normalized = (name or "").strip()
        if not normalized:
            return {
                "found": False,
                "query": name,
                "error": "Empty tool name — provide a non-empty string.",
                "callable": False,
                "schema_valid": True,
                "registered_in_graph": False,
                "authority_class": "unknown",
                "suggestions": [],
            }
        canonical = resolve_tool_name(normalized)
        if canonical:
            from .tool_discovery_resource import TOOL_DISCOVERY

            meta = TOOL_DISCOVERY.get(canonical, {})
            return {
                "found": True,
                "canonical_name": canonical,
                "aliases": meta.get("aliases", []),
                "use_when": meta.get("use_when", ""),
                "examples": meta.get("examples", []),
                "category": meta.get("category", ""),
                "callable": True,
                "schema_valid": True,
                "registered_in_graph": True,
                "authority_class": meta.get("tier", "public"),
            }
        return {
            "found": False,
            "query": normalized,
            "suggestions": find_tools_by_query(normalized)[:3],
            "callable": False,
            "schema_valid": True,
            "registered_in_graph": False,
            "authority_class": "unknown",
        }

    registered.append("arif_resolve_tool")

    # DISABLED 2026-06-28 (zen of resources — tool affordance metadata, not domain data).
    # Tool affordances are about the MCP tool interface itself. The gated tool
    # arif_get_affordance still provides this for agents that need it.
    #
    # @mcp.resource(uri="arif://tools/affordance", ...)
    # def affordance_contracts_resource() -> dict: ...
    # registered.append("arif://tools/affordance")

    # Tool to get affordance for one name (cognitive pre-call helper, gated)
    if _EXPOSE_DEV_TOOLS:

        @mcp.tool(
            name="arif_get_affordance",
            description=(
                "Return the complete constitutional affordance contract for a tool name. "
                "Use this to decide 'why this tool', 'why not others', risk, agency level, "
                "and expected metacognition shape. Preferred over guessing from name alone."
            ),
            tags={"discovery", "governance", "metacognition", "read-only"},
        )
        def get_affordance(name: str, _envelope: Any = None, actor_id: str = "", session_id: str = "") -> dict:
            try:
                from arifosmcp.runtime.tools import get_full_affordance

                return {"tool": name, "affordance": get_full_affordance(name)}
            except Exception as e:
                return {"tool": name, "error": str(e)}

        registered.append("arif_get_affordance")

    # DISABLED 2026-06-28 (zen of resources — pipeline metadata, not domain data).
    # Core 7 pipeline description is meta about the tool interface, not domain data.
    # Agents discover tools via tools/list and tool descriptions.
    #
    # @mcp.resource(uri="arif://core/seven", ...)
    # def core_seven_pipeline_resource() -> dict: ...
    # registered.append("arif://core/seven")

    return registered
