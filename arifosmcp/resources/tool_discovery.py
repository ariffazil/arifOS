"""
arifOS Tool Discovery Resource Registration
═══════════════════════════════════════════════════════════════

Registers the tool discovery resource so LLMs can find the right tool.

DITEMPA BUKAN DIBERI — Discovered, not guessed.
"""

from __future__ import annotations

from fastmcp import FastMCP

from .tool_discovery_resource import (
    TOOL_DISCOVERY,
    TOOL_DISCOVERY_RESOURCE,
    get_tool_discovery_resource_text,
    resolve_tool_name,
    find_tools_by_query,
)


def register_tool_discovery(mcp: FastMCP) -> list[str]:
    """Register tool discovery resource and alias resolver."""
    registered = []

    # Register the discovery resource
    @mcp.resource(
        uri="arif://tools/discovery",
        name="arifOS Tool Discovery",
        description=(
            "Quick reference for selecting the correct arifOS tool. "
            "Use this when unsure which tool to call. "
            "Each tool has 'use_when' guidance, aliases, and examples."
        ),
        mime_type="application/json",
    )
    def tool_discovery_resource() -> dict:
        return get_tool_discovery_resource_text()

    registered.append("arif://tools/discovery")

    # Register alias resolution tool
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

    return registered
