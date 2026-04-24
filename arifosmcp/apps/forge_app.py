"""
ForgeApp — Execution Bridge Surface
═══════════════════════════════════
Double-gated execution manifest interface.
"""
from __future__ import annotations

from fastmcp import FastMCP


def _register(mcp: FastMCP) -> None:
    @mcp.tool(name="forge_surface", description="FORGE execution bridge surface")
    def forge_surface(manifest: str = "") -> dict:
        return {"manifest": manifest, "status": "pending_888", "delta_S": -0.02}
