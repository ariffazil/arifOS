"""
arifOS engineering_memory Tool
==============================

Canonical engineering_memory implementation.

Stage: 555_MEMORY
Trinity: Ω (Memory/Engineering)
Floors: F10, F11, F2

Status: PHASE 3 - Migration to Tool base class
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from typing import Any

from arifosmcp.tools.base import Tool
from arifosmcp.abi.v1_0 import EngineeringMemoryRequest, EngineeringMemoryResponse
from core.shared.types import Verdict, RuntimeEnvelope


_tool_instance = None


def get_instance() -> Tool:
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = _EngineeringMemoryTool()
    return _tool_instance


class _EngineeringMemoryTool(Tool):
    """engineering_memory - Governed vector memory and engineering context."""

    name = "engineering_memory"
    stage = "555_MEMORY"
    floors = ["F10", "F11", "F2"]
    readonly = False

    async def execute(self, payload: dict) -> dict:
        from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
        from arifosmcp.runtime.tools_internal import engineering_memory_dispatch_impl
        from arifosmcp.runtime.compat import CurrentContext

        mode = payload.get("mode", "search")
        query = payload.get("query")
        session_id = payload.get("session_id")
        risk_tier = payload.get("risk_tier", "medium")
        dry_run = payload.get("dry_run", True)
        auth_context = payload.get("auth_context")

        if "engineering_memory" in HARDENED_DISPATCH_MAP:
            res = await HARDENED_DISPATCH_MAP["engineering_memory"](mode=mode, payload=payload)
        else:
            res = await engineering_memory_dispatch_impl(
                mode=mode,
                payload=payload,
                auth_context=auth_context,
                risk_tier=risk_tier,
                dry_run=dry_run,
                ctx=CurrentContext(),
            )

        if isinstance(res, RuntimeEnvelope):
            return res.model_dump() if hasattr(res, 'model_dump') else res.dict()
        if hasattr(res, 'model_dump'):
            return res.model_dump()
        if hasattr(res, 'dict'):
            return res.dict()
        return res


from arifosmcp.tools.base import ToolRegistry
ToolRegistry.register(_EngineeringMemoryTool())
