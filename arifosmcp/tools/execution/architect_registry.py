"""
arifOS architect_registry Tool
================================

Canonical architect_registry implementation.

Stage: M-4_ARCH
Trinity: Δ (Tool/Resource discovery)
Floors: F10

Status: PHASE 3 - Migration to Tool base class
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from typing import Any

from arifosmcp.tools.base import Tool
from arifosmcp.abi.v1_0 import ArchitectRegistryRequest, ArchitectRegistryResponse
from core.shared.types import Verdict, RuntimeEnvelope


_tool_instance = None


def get_instance() -> Tool:
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = _ArchitectRegistryTool()
    return _tool_instance


class _ArchitectRegistryTool(Tool):
    """architect_registry - Tool and resource discovery."""

    name = "architect_registry"
    stage = "M-4_ARCH"
    floors = ["F10"]
    readonly = True

    async def execute(self, payload: dict) -> dict:
        from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
        from arifosmcp.runtime.tools_internal import architect_registry_dispatch_impl
        from arifosmcp.runtime.compat import CurrentContext

        mode = payload.get("mode", "list")
        tool_name = payload.get("tool_name")
        session_id = payload.get("session_id")
        risk_tier = payload.get("risk_tier", "low")
        dry_run = payload.get("dry_run", True)
        auth_context = payload.get("auth_context")

        if "architect_registry" in HARDENED_DISPATCH_MAP:
            res = await HARDENED_DISPATCH_MAP["architect_registry"](mode=mode, payload=payload)
        else:
            res = await architect_registry_dispatch_impl(
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
ToolRegistry.register(_ArchitectRegistryTool())
