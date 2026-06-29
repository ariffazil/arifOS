"""
arifOS Tool Discovery Resource Registration
═══════════════════════════════════════════════════════════════

Registers the tool discovery resource so LLMs can find the right tool.

DITEMPA BUKAN DIBERI — Discovered, not guessed.
"""

from __future__ import annotations

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

    @mcp.tool(
        name="arif_resolve_tool",
        description=(
            "Resolve a tool name or alias to the canonical arifOS tool name. "
            "Use when you have a tool name but aren't sure if it's the canonical name. "
            "Returns the canonical name, use_when guidance, and examples."
        ),
        tags={"discovery", "utility", "read-only"},
    )
    def resolve_tool(name: str) -> dict:
        """Resolve a tool name or alias to canonical form."""
        canonical = resolve_tool_name(name)
        if canonical:
            from .tool_discovery_resource import TOOL_DISCOVERY

            meta = TOOL_DISCOVERY.get(canonical, {})
            return {
                "found": True,
                "canonical_name": canonical,
                "use_when": meta.get("use_when", ""),
                "examples": meta.get("examples", []),
                "category": meta.get("category", ""),
            }
        return {
            "found": False,
            "query": name,
            "suggestions": find_tools_by_query(name)[:3],
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
        def get_affordance(name: str) -> dict:
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
