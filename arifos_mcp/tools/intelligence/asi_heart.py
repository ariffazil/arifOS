"""
arifOS asi_heart Tool
=====================

Canonical asi_heart implementation.

Stage: 666_HEART
Trinity: Ω (Safety and empathy)
Floors: F5, F6, F9

Status: PHASE 3 - Migration to Tool base class
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from typing import Any

from arifos_mcp.tools.base import Tool
from arifos_mcp.abi.v1_0 import AsiHeartRequest, AsiHeartResponse
from core.shared.types import Verdict, RuntimeStatus


_tool_instance = None


def get_instance() -> Tool:
    """Get or create the asi_heart tool instance."""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = _AsiHeartTool()
    return _tool_instance


class _AsiHeartTool(Tool):
    """
    asi_heart - Safety, empathy, and consequence modeling.

    Applies F5/F6/F9 to content.
    """

    name = "asi_heart"
    stage = "666_HEART"
    floors = ["F5", "F6", "F9"]
    readonly = False

    async def execute(self, payload: dict) -> dict:
        """Execute asi_heart via hardened dispatch or internal impl."""
        from arifos_mcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
        from arifos_mcp.runtime.tools_internal import asi_heart_dispatch_impl
        from arifos_mcp.runtime.compat import CurrentContext

        mode = payload.get("mode", "critique")
        content = payload.get("content", payload.get("query", ""))
        session_id = payload.get("session_id")
        risk_tier = payload.get("risk_tier", "medium")
        dry_run = payload.get("dry_run", True)
        auth_context = payload.get("auth_context")

        if "asi_heart" in HARDENED_DISPATCH_MAP:
            res = await HARDENED_DISPATCH_MAP["asi_heart"](mode=mode, payload=payload)
            if hasattr(res, 'model_dump'):
                return res.model_dump()
            elif hasattr(res, 'dict'):
                return res.dict()
            return res
        else:
            result = await asi_heart_dispatch_impl(
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
ToolRegistry.register(_AsiHeartTool())
