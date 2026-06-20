"""
arifOS OTel Wiring — Trace every canonical tool call.

Phase 1 #3: "Add OpenTelemetry spans for every MCP call."

This module provides a decorator/utility for wrapping tool calls in OTel spans.
The 13 canonical arifOS tools should use this when invoked.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any

from .arifos_observability.otel_tracer import OTelTracer, init_tracer

# Module-level tracer (initialized lazily)
_tracer: OTelTracer | None = None


def get_tracer() -> OTelTracer:
    """Lazy-init the global tracer."""
    global _tracer
    if _tracer is None:
        init_tracer(service_name="arifOS-mcp")
        _tracer = OTelTracer(service_name="arifOS-mcp")
    return _tracer


@contextmanager
def tool_span(tool_name: str, attributes: dict[str, Any] | None = None):
    """
    Context manager for tracing a tool call.

    Usage:
        with tool_span("arif_lease_issue", {"actor_id": actor_id}):
            ... tool body ...
    """
    tracer = get_tracer()
    attrs = {
        "arifos.tool": tool_name,
        "arifos.floor_compliance": "F11_AUDIT",
        "arifos.epoch": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if attributes:
        attrs.update(attributes)
    with tracer.span(tool_name, attrs):
        yield


def trace_tool(tool_name: str | None = None):
    """
    Decorator: wrap a tool function in an OTel span.

    Usage:
        @trace_tool("arif_lease_issue")
        async def arif_lease_issue(actor_id: str, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        name = tool_name or func.__name__

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tool_span(name, {"arifos.args_count": len(args), "arifos.kwargs_keys": list(kwargs.keys())}):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tool_span(name, {"arifos.args_count": len(args), "arifos.kwargs_keys": list(kwargs.keys())}):
                return func(*args, **kwargs)

        if hasattr(func, "__code__") and func.__code__.co_flags & 0x100:  # CO_COROUTINE
            return async_wrapper
        return sync_wrapper

    return decorator
