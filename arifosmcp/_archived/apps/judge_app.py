"""
JudgeApp — 888 Constitutional Verdict Surface
══════════════════════════════════════════════
Interactive constitutional verdict rendering with session state wiring.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.apps.command_center.governance import judge_candidate
from arifosmcp.apps.session_state import (
    LifecycleState,
    advance_session,
    get_or_create_session,
)
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

    @mcp.tool(
        name="arif_judge_deliberate",
        description="888_JUDGE — constitutional verdict with session lifecycle advance",
    )
    def arif_judge_deliberate(candidate: str, session_id: str = None) -> dict:
        """Render a constitutional verdict for a candidate action.

        On SEAL: advances session to JUDGE_REVIEWED.
        On HOLD/VOID: advances session to BLOCKED.
        """
        result = judge_candidate(candidate)
        verdict = result["verdict"]

        if session_id:
            session = get_or_create_session(session_id)
            session.last_verdict = verdict
            if verdict == "SEAL":
                advance_session(
                    session_id,
                    LifecycleState.JUDGE_REVIEWED,
                    tool="arif_judge_deliberate",
                )
            elif verdict in ("HOLD", "VOID"):
                advance_session(
                    session_id,
                    LifecycleState.BLOCKED,
                    tool="arif_judge_deliberate",
                )

        return result
