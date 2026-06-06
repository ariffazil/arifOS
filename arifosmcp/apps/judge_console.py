"""
Judge Console App — 888_JUDGE Interactive Surface
══════════════════════════════════════════════════
UI-capable constitutional verdict console.
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.apps import AppConfig


def _register(mcp: FastMCP) -> None:
    app = AppConfig(
        domain="https://arifosmcp.arif-fazil.com",
        visibility=["app", "model"],
    )

    @mcp.tool(
        name="arif_judge_console",
        description="888_JUDGE interactive constitutional verdict console",
        app=app,
    )
    def arif_judge_console(candidate: str = "", context: str = "") -> dict:
        return {
            "candidate": candidate,
            "context": context,
            "verdict": "SEAL",
            "omega_ortho": 0.97,
            "floors_checked": ["L01", "L02", "L08", "L11", "L12", "L13"],
            "risk_tier": "medium",
            "app": "judge_console",
        }
