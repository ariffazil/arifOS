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

    # Register full constitutional affordance contract resource (metacognitive core)
    @mcp.resource(
        uri="arif://tools/affordance",
        name="arifOS Constitutional Affordance Contracts",
        description=(
            "Full metacognitive contract per tool. purpose, use_when, do_not_use_when, "
            "L0-L5 agency_level, blast_radius, human_confirmation, decision thresholds. "
            "Agents: retrieve BEFORE calling any tool. Answers the four questions."
        ),
        mime_type="application/json",
    )
    def affordance_contracts_resource() -> dict:
        return get_full_affordance_resource_text()

    registered.append("arif://tools/affordance")

    # Tool to get affordance for one name (cognitive pre-call helper)
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

    # Core 7 pipeline resource — the kernel 7 tools done properly
    @mcp.resource(
        uri="arif://core/seven",
        name="arifOS Core 7 Pipeline",
        description=(
            "The 7 essential constitutional tools that form the primary governed loop. "
            "Each has full affordance contracts, L0-L5 classification, and produces "
            "metacognitive output (facts, inferences, unknowns, next_safe_action). "
            "Agents should reason over this pipeline."
        ),
        mime_type="application/json",
    )
    def core_seven_pipeline_resource() -> dict:
        from arifosmcp.constitutional_map import CORE_SEVEN, CORE_SEVEN_LABELS, CORE_SEVEN_STAGE_MAP
        from arifosmcp.resources.tool_discovery_resource import get_full_affordance_resource_text

        aff = get_full_affordance_resource_text()
        return {
            "core_seven": CORE_SEVEN,
            "labels": CORE_SEVEN_LABELS,
            "stage_map": CORE_SEVEN_STAGE_MAP,
            "contracts": aff.get("core_seven", {}),
            "instruction": "Follow the order. Call get_full_affordance or arif://tools/affordance before each step. Expect metacognition and next_safe_action in every response.",
        }

    registered.append("arif://core/seven")

    return registered
