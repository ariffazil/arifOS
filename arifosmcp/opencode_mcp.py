from __future__ import annotations

import sys
from typing import Any

from fastmcp import FastMCP


def _iter_tools(mcp: FastMCP) -> list[Any]:
    tool_manager = getattr(mcp, "_tool_manager", None)
    if tool_manager is not None and getattr(tool_manager, "tools", None):
        return list(tool_manager.tools.values())

    provider = getattr(mcp, "_local_provider", None)
    components = getattr(provider, "_components", {}) if provider is not None else {}
    return [component for key, component in components.items() if key.startswith("tool:")]


def _mount_tools(target: FastMCP, source: FastMCP, seen: set[str] | None = None) -> set[str]:
    names = seen or set()
    for tool in _iter_tools(source):
        name = getattr(tool, "name", "")
        if not name or name in names:
            continue
        target.add_tool(tool)
        names.add(name)
    return names


def create_kernel_mcp() -> FastMCP:
    from arifosmcp.server import create_arifos_mcp_server

    return create_arifos_mcp_server()


def create_intelligence_mcp() -> FastMCP:
    from arifosmcp.g02_router import create_router_mcp
    from arifosmcp.mcp_tools import create_unified_mcp

    mcp = FastMCP("arifOS-OpenCode-Intelligence")
    seen: set[str] = set()
    seen = _mount_tools(mcp, create_unified_mcp(), seen)
    _mount_tools(mcp, create_router_mcp(), seen)

    @mcp.tool(name="opencode_intelligence_surface", tags={"system", "public"})
    def opencode_intelligence_surface() -> dict[str, Any]:
        return {
            "surface": "intelligence",
            "router": "G02",
            "guidance": "Route cross-axis work through G02_route before direct organ execution.",
            "axes": ["P", "T", "V", "G", "E", "M"],
        }

    return mcp


def create_well_mcp() -> FastMCP:
    from arifosmcp.mcp_tools import create_perception_mcp

    mcp = FastMCP("arifOS-OpenCode-WELL")
    _mount_tools(mcp, create_perception_mcp())

    @mcp.tool(name="opencode_well_surface", tags={"system", "public"})
    def opencode_well_surface() -> dict[str, Any]:
        return {
            "surface": "WELL",
            "primary_tool": "arifos_oracle_bio",
            "recommended_modes": ["snapshot_read", "readiness_check", "floor_scan", "deltascan"],
        }

    return mcp


def create_wealth_mcp() -> FastMCP:
    from arifosmcp.mcp_tools import create_valuation_mcp

    mcp = FastMCP("arifOS-OpenCode-WEALTH")
    _mount_tools(mcp, create_valuation_mcp())

    @mcp.tool(name="opencode_wealth_surface", tags={"system", "public"})
    def opencode_wealth_surface() -> dict[str, Any]:
        return {
            "surface": "WEALTH",
            "primary_tool": "arifos_compute_finance",
            "recommended_modes": ["npv", "irr", "mirr", "emv", "dscr", "allocation_rank"],
        }

    return mcp


def create_geox_mcp() -> FastMCP:
    from arifosmcp.g02_router import create_router_mcp
    from arifosmcp.mcp_tools import create_execution_mcp, create_transformation_mcp

    mcp = FastMCP("arifOS-OpenCode-GEOX")
    seen: set[str] = set()
    seen = _mount_tools(mcp, create_transformation_mcp(), seen)
    seen = _mount_tools(mcp, create_execution_mcp(), seen)
    _mount_tools(mcp, create_router_mcp(), seen)

    @mcp.tool(name="opencode_geox_surface", tags={"system", "public"})
    def opencode_geox_surface() -> dict[str, Any]:
        return {
            "surface": "GEOX",
            "primary_tools": ["arifos_compute_physics", "arifos_oracle_world", "G02_route"],
            "guidance": "Use G02_route for T-to-E or E-to-T geoscience workflows.",
        }

    return mcp


def create_sovereign_mcp() -> FastMCP:
    mcp = FastMCP("arifOS-OpenCode-Sovereign")
    seen: set[str] = set()
    seen = _mount_tools(mcp, create_kernel_mcp(), seen)
    seen = _mount_tools(mcp, create_intelligence_mcp(), seen)

    @mcp.tool(name="opencode_sovereign_surface", tags={"system", "public"})
    def opencode_sovereign_surface() -> dict[str, Any]:
        return {
            "surface": "sovereign",
            "kernel": "canonical_13",
            "intelligence": "P/T/V/G/E/M + G02",
            "guidance": [
                "Use arif_* tools for constitutional governance and judgment.",
                "Use G02_route before cross-axis intelligence work.",
                "Use organ-specific profiles for tight domain-focused sessions.",
            ],
        }

    return mcp


SURFACES = {
    "kernel": create_kernel_mcp,
    "intelligence": create_intelligence_mcp,
    "well": create_well_mcp,
    "wealth": create_wealth_mcp,
    "geox": create_geox_mcp,
    "sovereign": create_sovereign_mcp,
}


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] in {"-h", "--help", "help"}:
        sys.stderr.write(
            "Usage: python -m arifosmcp.opencode_mcp [kernel|intelligence|well|wealth|geox|sovereign]\n"
        )
        return

    surface = args[0].strip().lower()
    factory = SURFACES.get(surface)
    if factory is None:
        sys.stderr.write(f"Unknown surface: {surface}\n")
        sys.exit(2)

    mcp = factory()
    mcp.run()


if __name__ == "__main__":
    main()
