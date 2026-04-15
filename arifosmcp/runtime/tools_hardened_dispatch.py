"""
Compatibility shim for the hardened dispatch layer.

The current runtime routes public traffic through `kernel.dispatch_with_fail_closed`,
but several megaTools and kernel helpers still import this historical module.
Keep the shim small and side-effect free so existing callers can boot and then
fall back to their local implementations when no hardened override is registered.
"""

from __future__ import annotations

from typing import Any

HARDENED_DISPATCH_MAP: dict[str, Any] = {}


async def dispatch_with_fail_closed(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Delegate to the canonical kernel fail-closed gateway."""
    from arifosmcp.runtime.kernel import kernel

    return await kernel.dispatch_with_fail_closed(tool_name, arguments)


def get_tool_handler(name: str) -> Any:
    """Resolve tool handlers through the canonical runtime registry."""
    from arifosmcp.runtime.tools import get_tool_handler as _get_tool_handler

    return _get_tool_handler(name)


def get_shadow_backends() -> dict[str, Any]:
    """Shadow comparison is optional; default to no alternate backends."""
    return {}
