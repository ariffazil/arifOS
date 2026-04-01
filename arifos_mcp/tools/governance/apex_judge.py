"""
arifOS apex_judge Tool
======================

Canonical apex_judge implementation.

Stage: 888_JUDGE
Trinity: Ω (Constitutional law)
Floors: F3, F12, F13

Status: PHASE 3 - Migration to Tool base class
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from typing import Any

from arifos_mcp.tools.base import Tool
from arifos_mcp.abi.v1_0 import ApexJudgeRequest, ApexJudgeResponse
from core.shared.types import Verdict, RuntimeStatus


_tool_instance = None


def get_instance() -> Tool:
    """Get or create the apex_judge tool instance."""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = _ApexJudgeTool()
    return _tool_instance


class _ApexJudgeTool(Tool):
    """
    apex_judge - Constitutional verdict engine.

    Applies F3/F12/F13 to candidate actions and returns verdicts.
    """

    name = "apex_judge"
    stage = "888_JUDGE"
    floors = ["F3", "F12", "F13"]
    readonly = False

    async def execute(self, payload: dict) -> dict:
        """Execute apex_judge."""
        from arifos_mcp.runtime.megaTools.tool_03_apex_soul import apex_judge as apex_judge_fn
        from arifos_mcp.runtime.compat import CurrentContext

        mode = payload.get("mode", "judge")
        candidate = payload.get("candidate") or payload.get("proposal", "")
        session_id = payload.get("session_id")
        risk_tier = payload.get("risk_tier", "medium")
        dry_run = payload.get("dry_run", True)
        auth_context = payload.get("auth_context")

        result = await apex_judge_fn(
            mode=mode,
            proposal=candidate,
            session_id=session_id,
            risk_tier=risk_tier,
            dry_run=dry_run,
            auth_context=auth_context,
            ctx=CurrentContext(),
        )

        if hasattr(result, 'model_dump'):
            return result.model_dump()
        elif hasattr(result, 'dict'):
            return result.dict()
        return result


# Auto-register
from arifos_mcp.tools.base import ToolRegistry
ToolRegistry.register(_ApexJudgeTool())
