"""
arifOS physics_reality Tool
===========================

Canonical physics_reality implementation.

Stage: 111_SENSE
Trinity: Δ (Reality grounding)
Floors: F2, F3, F10

Status: PHASE 3 - Migration to Tool base class
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from typing import Any

from arifosmcp.tools.base import Tool
from arifosmcp.abi.v1_0 import PhysicsRealityRequest, PhysicsRealityResponse
from arifosmcp.runtime.models import RuntimeEnvelope, Verdict


_tool_instance = None


def get_instance() -> Tool:
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = _PhysicsRealityTool()
    return _tool_instance


class _PhysicsRealityTool(Tool):
    """physics_reality - Earth-witness fact acquisition and mapping."""

    name = "physics_reality"
    stage = "111_SENSE"
    floors = ["F2", "F3", "F10"]
    readonly = False

    async def execute(self, payload: dict) -> dict:
        from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
        from arifosmcp.runtime.tools_internal import physics_reality_dispatch_impl
        from arifosmcp.runtime.compat import CurrentContext

        mode = payload.get("mode", "time")
        query = payload.get("query")
        session_id = payload.get("session_id")
        risk_tier = payload.get("risk_tier", "medium")
        dry_run = payload.get("dry_run", True)
        auth_context = payload.get("auth_context")

        if "physics_reality" in HARDENED_DISPATCH_MAP:
            res = await HARDENED_DISPATCH_MAP["physics_reality"](mode=mode, payload=payload)
        else:
            res = await physics_reality_dispatch_impl(
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
ToolRegistry.register(_PhysicsRealityTool())
