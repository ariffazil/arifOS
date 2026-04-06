"""
arifOS arifOS_kernel Tool
=========================

Canonical arifOS_kernel implementation.

Stage: 444_ROUTER
Trinity: ΔΩΨ (Routing layer)
Floors: F4, F11

Status: PHASE 3 - Migration to Tool base class
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from typing import Any

from arifosmcp.tools.base import Tool
from arifosmcp.abi.v1_0 import ArifOSKernelRequest, ArifOSKernelResponse
from core.shared.types import Verdict, RuntimeStatus


_tool_instance = None


def get_instance() -> Tool:
    """Get or create the arifOS_kernel tool instance."""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = _ArifOSKernelTool()
    return _tool_instance


class _ArifOSKernelTool(Tool):
    """
    arifOS_kernel - Primary metabolic conductor.

    Routes queries through the 000-999 metabolic pipeline.
    """

    name = "arifOS_kernel"
    stage = "444_ROUTER"
    floors = ["F4", "F11"]
    readonly = False

    async def execute(self, payload: dict) -> dict:
        """Execute arifOS_kernel via kernel_router."""
        from arifosmcp.runtime.kernel_router import kernel_intelligent_route
        from arifosmcp.runtime.compat import CurrentContext

        query = payload.get("query", "")
        session_id = payload.get("session_id")
        risk_tier = payload.get("risk_tier", "medium")
        dry_run = payload.get("dry_run", True)
        allow_execution = payload.get("allow_execution", False)
        auth_context = payload.get("auth_context")
        intent = payload.get("intent")
        use_memory = payload.get("use_memory", True)
        use_heart = payload.get("use_heart", True)

        result = await kernel_intelligent_route(
            query=query,
            session_id=session_id,
            payload=payload,
            auth_context=auth_context,
            risk_tier=risk_tier,
            dry_run=dry_run,
            allow_execution=allow_execution,
            ctx=CurrentContext(),
            intent=intent,
            use_memory=use_memory,
            use_heart=use_heart,
            debug=payload.get("debug", False),
        )

        # Convert RuntimeEnvelope to dict
        if hasattr(result, 'model_dump'):
            return result.model_dump()
        elif hasattr(result, 'dict'):
            return result.dict()
        return result


# Auto-register with ToolRegistry
from arifosmcp.tools.base import ToolRegistry
ToolRegistry.register(_ArifOSKernelTool())
