"""
arifosmcp/integrations/playwright_bridge.py — Playwright Browser MCP Bridge

Uses the official MCP Python SDK to connect to the local playwright-mcp
service running on port 8931. Handles full MCP protocol: handshake,
capabilities exchange, and tool invocation.

Key insight: playwright-mcp requires Host header = "localhost:8931"
(not 127.0.0.1:8931) for same-origin policy compliance.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import httpx
import mcp.types as types
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

logger = logging.getLogger(__name__)

# Playwright MCP server URL
PLAYWRIGHT_MCP_URL = os.getenv("PLAYWRIGHT_MCP_URL", "http://127.0.0.1:8931")
PLAYWRIGHT_MCP_TIMEOUT = float(os.getenv("PLAYWRIGHT_MCP_TIMEOUT", "120.0"))

# Client info for MCP handshake
BRIDGE_CLIENT_INFO = types.Implementation(name="arifOS-browser-bridge", version="1.0.0")


def _create_playwright_http_client() -> httpx.AsyncClient:
    """
    Create an httpx client configured for playwright-mcp.

    playwright-mcp enforces same-origin policy requiring Host: localhost:8931.
    The default httpx client would use the IP (127.0.0.1) as the Host header,
    causing 403 Forbidden responses.
    """
    return httpx.AsyncClient(
        timeout=httpx.Timeout(PLAYWRIGHT_MCP_TIMEOUT),
        headers={
            # Required by playwright-mcp for same-origin compliance
            "Host": "localhost:8931",
            # MCP protocol requires both JSON and SSE
            "Accept": "application/json, text/event-stream",
        },
        follow_redirects=True,
    )


@asynccontextmanager
async def playwright_mcp_session(
    url: str = PLAYWRIGHT_MCP_URL,
) -> AsyncGenerator[ClientSession, None]:
    """
    Context manager for a Playwright MCP session.

    Usage:
        async with playwright_mcp_session() as session:
            await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("navigate", {"url": "https://..."})
    """
    http_client = _create_playwright_http_client()

    try:
        async with streamable_http_client(
            f"{url}/mcp",
            http_client=http_client,
        ) as (
            read_stream,
            write_stream,
            _get_session_id,
        ):
            async with ClientSession(
                read_stream,
                write_stream,
                client_info=BRIDGE_CLIENT_INFO,
            ) as session:
                # MCP protocol initialization
                await session.initialize()
                yield session
    finally:
        await http_client.aclose()


class PlaywrightBridge:
    """
    MCP client for the local Playwright browser automation server.

    Uses the official `mcp` Python SDK with a custom httpx client that
    sets the required Host header for playwright-mcp.
    """

    def __init__(self, base_url: str = PLAYWRIGHT_MCP_URL, timeout: float = PLAYWRIGHT_MCP_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def health_check(self) -> dict[str, Any]:
        """Verify playwright-mcp service is reachable and initialized."""
        try:
            async with playwright_mcp_session(self.base_url) as session:
                # Successful session creation + initialize = health OK
                return {
                    "status": "OK",
                    "service": "playwright-mcp",
                    "url": self.base_url,
                }
        except Exception as e:
            return {"status": "DOWN", "service": "playwright-mcp", "error": str(e)[:200]}

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available browser automation tools from playwright-mcp."""
        try:
            async with playwright_mcp_session(self.base_url) as session:
                tools_result = await session.list_tools()
                tools = getattr(tools_result, "tools", list(tools_result))
                return [
                    {
                        "name": getattr(t, "name", str(t)),
                        "description": getattr(t, "description", ""),
                    }
                    for t in tools
                ]
        except Exception as e:
            logger.warning(f"Failed to list playwright tools: {e}")
            return []

    async def call_browser_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """
        Invoke a browser tool on the playwright-mcp server.

        Uses the MCP SDK's session.call_tool() interface.
        """
        try:
            async with playwright_mcp_session(self.base_url) as session:
                result = await session.call_tool(tool_name, arguments)

                # Normalize result to dict
                if hasattr(result, "content"):
                    content = result.content
                    if hasattr(content, "__iter__") and not isinstance(content, str):
                        return {
                            "content": [
                                {
                                    "type": getattr(c, "type", "text"),
                                    "text": getattr(c, "text", str(c)),
                                }
                                for c in content
                            ]
                        }
                    return {"content": str(content)}
                return {"result": str(result) if result else "ok"}

        except Exception as e:
            logger.error(f"Playwright MCP tool call failed [{tool_name}]: {e}")
            return {"error": str(e)[:200]}

    async def close(self):
        """No persistent connection — each call is a new session."""
        pass


# Global bridge instance
playwright_bridge = PlaywrightBridge()


async def cleanup_playwright_bridge():
    """Cleanup bridge — no-op since sessions are stateless."""
    await playwright_bridge.close()
