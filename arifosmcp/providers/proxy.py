"""
ProxyProvider — External MCP Bridge
════════════════════════════════════

FastMCPProvider subclass for external MCP bridges.
"""
from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.providers import FastMCPProvider

logger = logging.getLogger(__name__)


class ProxyProvider(FastMCPProvider):
    """
    Wraps an external FastMCP server as a provider for the arifOS mesh.

    Useful for mounting third-party MCP surfaces behind constitutional
    transforms and floor checks.
    """

    def __init__(self, server: FastMCP[Any], namespace: str | None = None) -> None:
        super().__init__(server)
        self.namespace = namespace
        if namespace:
            from fastmcp.server.transforms import Namespace

            self.add_transform(Namespace(namespace))
            logger.info(f"[ProxyProvider] Mounted external server with namespace '{namespace}'")
        else:
            logger.info("[ProxyProvider] Mounted external server")
