"""
arifOS math_estimator Tool
===========================

Canonical math_estimator implementation.

Stage: 777_OPS
Trinity: Δ (Quantitative estimation)
Floors: F4, F5

Status: PHASE 3 - Migration to Tool base class
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from typing import Any

from arifosmcp.tools.base import Tool
from arifosmcp.abi.v1_0 import MathEstimatorRequest, MathEstimatorResponse
from core.shared.types import Verdict, RuntimeEnvelope


_tool_instance = None


def get_instance() -> Tool:
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = _MathEstimatorTool()
    return _tool_instance


class _MathEstimatorTool(Tool):
    """math_estimator - Thermodynamic cost and health estimation."""

    name = "math_estimator"
    stage = "777_OPS"
    floors = ["F4", "F5"]
    readonly = True

    async def execute(self, payload: dict) -> dict:
        from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
        from arifosmcp.runtime.tools_internal import math_estimator_dispatch_impl
        from arifosmcp.runtime.compat import CurrentContext

        mode = payload.get("mode", "health")
        session_id = payload.get("session_id")
        risk_tier = payload.get("risk_tier", "low")
        dry_run = payload.get("dry_run", True)
        auth_context = payload.get("auth_context")

        if "math_estimator" in HARDENED_DISPATCH_MAP:
            res = await HARDENED_DISPATCH_MAP["math_estimator"](mode=mode, payload=payload)
        else:
            res = await math_estimator_dispatch_impl(
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
ToolRegistry.register(_MathEstimatorTool())
