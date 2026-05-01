"""
InitApp — 000 Session Anchoring Surface
═══════════════════════════════════════
Session ignition and identity binding UI.
"""
from __future__ import annotations

from fastmcp import FastMCP


def _register(mcp: FastMCP) -> None:
    @mcp.tool(name="init_surface", description="000_INIT session anchor surface")
    def init_surface(actor_id: str = "") -> dict:
        return {"actor_id": actor_id, "stage": "000", "status": "ready"}
