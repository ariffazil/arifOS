"""
TransportFilter — Visibility Filter Per Transport
══════════════════════════════════════════════════

Filters tools, resources, and prompts based on the active transport
(stdio vs HTTP). Useful for hiding heavy tools over stdio.
"""
from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from fastmcp.server.transforms import Transform
from fastmcp.tools.tool import Tool

logger = logging.getLogger(__name__)

_TRANSPORT_TAG: dict[str, set[str]] = {
    "stdio": {"stdio_safe", "lightweight"},
    "http": {"http_safe", "streaming"},
}


class TransportFilter(Transform):
    """
    Hides tools that are not tagged for the current transport.

    Tools without transport tags are assumed available on all transports.
    """

    def __init__(self, transport: str = "http") -> None:
        self.transport = transport

    def __repr__(self) -> str:
        return f"TransportFilter(transport={self.transport!r})"

    def _allowed(self, tool: Tool) -> bool:
        if not tool.tags:
            return True
        transport_tags = {"stdio_safe", "http_safe", "lightweight", "streaming"}
        tool_transport_tags = tool.tags & transport_tags
        if not tool_transport_tags:
            return True
        expected = _TRANSPORT_TAG.get(self.transport, set())
        return bool(tool_transport_tags & expected)

    async def list_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        filtered = [t for t in tools if self._allowed(t)]
        logger.debug(
            f"[TransportFilter] {self.transport}: {len(filtered)}/{len(tools)} tools visible"
        )
        return filtered

    async def get_tool(
        self, name: str, call_next: Any, *, version: Any = None
    ) -> Tool | None:
        tool = await call_next(name, version=version)
        if tool is None:
            return None
        if not self._allowed(tool):
            logger.debug(f"[TransportFilter] Blocked '{name}' on {self.transport}")
            return None
        return tool
