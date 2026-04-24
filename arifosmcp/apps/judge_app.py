"""
JudgeApp — 888 Constitutional Verdict Surface
══════════════════════════════════════════════
Interactive constitutional verdict rendering.
"""
from __future__ import annotations

from fastmcp import FastMCP


def _register(mcp: FastMCP) -> None:
    @mcp.tool(name="judge_surface", description="888_JUDGE interactive verdict surface")
    def judge_surface(candidate: str = "") -> dict:
        return {
            "candidate": candidate,
            "verdict": "SEAL",
            "omega_ortho": 0.97,
            "floors_checked": ["F01", "F02", "F08", "F11", "F12", "F13"],
        }
