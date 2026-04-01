"""
arifOS agi_mind Tool
====================

Canonical agi_mind implementation.

Stage: 333_MIND
Trinity: Δ (Reasoning)
Floors: F2, F4, F7, F8

Status: PHASE 3 - Migration to Tool base class
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from typing import Any

from arifos_mcp.tools.base import Tool
from arifos_mcp.abi.v1_0 import AgiMindRequest, AgiMindResponse
from core.shared.types import Verdict, RuntimeStatus


_tool_instance = None


def get_instance() -> Tool:
    """Get or create the agi_mind tool instance."""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = _AgiMindTool()
    return _tool_instance


class _AgiMindTool(Tool):
    """
    agi_mind - Core reasoning and synthesis engine.

    Applies F2/F4/F7/F8 to reasoning tasks.
    """

    name = "agi_mind"
    stage = "333_MIND"
    floors = ["F2", "F4", "F7", "F8"]
    readonly = False

    async def execute(self, payload: dict) -> dict:
        """Execute agi_mind via hardened dispatch or internal impl."""
        from arifos_mcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
        from arifos_mcp.runtime.tools_internal import agi_mind_dispatch_impl
        from arifos_mcp.runtime.verdict_wrapper import forge_verdict
        from arifos_mcp.runtime.models import CanonicalMetrics
        from arifos_mcp.runtime.compat import CurrentContext

        mode = payload.get("mode", "reason")
        query = payload.get("query", "")
        session_id = payload.get("session_id")
        risk_tier = payload.get("risk_tier", "medium")
        dry_run = payload.get("dry_run", True)
        auth_context = payload.get("auth_context")

        if "agi_mind" in HARDENED_DISPATCH_MAP:
            res_dict = await HARDENED_DISPATCH_MAP["agi_mind"](mode=mode, payload=payload)

            metrics = CanonicalMetrics()
            metrics.telemetry.ds = res_dict.get("metrics", {}).get("telemetry", {}).get("ds", 0.0)
            metrics.telemetry.confidence = res_dict.get("confidence", 0.5)

            result = forge_verdict(
                tool_id="agi_mind",
                stage="333_MIND",
                payload=res_dict.get("payload", res_dict),
                session_id=session_id,
                metrics=metrics,
                floors_checked=["F2", "F4", "F7", "F8"],
                message=res_dict.get("note")
            )
        else:
            result = await agi_mind_dispatch_impl(
                mode=mode,
                payload=payload,
                auth_context=auth_context,
                risk_tier=risk_tier,
                dry_run=dry_run,
                ctx=CurrentContext(),
            )

        if hasattr(result, 'model_dump'):
            return result.model_dump()
        elif hasattr(result, 'dict'):
            return result.dict()
        return result


# Auto-register
from arifos_mcp.tools.base import ToolRegistry
ToolRegistry.register(_AgiMindTool())
