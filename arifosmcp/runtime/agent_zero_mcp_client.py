"""
arifOS → Agent-Zero MCP Client Bridge
═════════════════════════════════════

Establishes a governed MCP client session to agent-zero's streamable HTTP MCP endpoint.
arifOS acts as MCP client; agent-zero acts as MCP server.

Token (stable): jPU8o7B0zxjgAOGz (runtime_id=arif-copilot-governance-2026)
Internal MCP URL:  http://agent-zero:80/mcp/t-{token}/sse + /http
External MCP URL: https://ai.arif-fazil.com/mcp/t-{token}/sse + /http

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import uuid
from typing import Any
from urllib.parse import urljoin

import httpx
from mcp.types import CallToolResult, ListToolsResult

logger = logging.getLogger(__name__)

# ─── Configuration ──────────────────────────────────────────────────────────────

AZ_MCP_TOKEN = os.getenv(
    "AGENT_ZERO_MCP_TOKEN",
    "jPU8o7B0zxjgAOGz",
)
AZ_MCP_BASE_URL = os.getenv(
    "AGENT_ZERO_MCP_BASE_URL",
    "http://agent-zero:80",
)
AZ_MCP_TIMEOUT = float(os.getenv("AGENT_ZERO_MCP_TIMEOUT", "120"))
AZ_MCP_INIT_RETRIES = int(os.getenv("AGENT_ZERO_MCP_INIT_RETRIES", "3"))
AZ_MCP_INIT_RETRY_DELAY = float(os.getenv("AGENT_ZERO_MCP_INIT_RETRY_DELAY", "1.5"))


def _az_url(path: str) -> str:
    """Build agent-zero MCP URL with token."""
    return f"{AZ_MCP_BASE_URL}/mcp/t-{AZ_MCP_TOKEN}{path}"


# ─── Session State ─────────────────────────────────────────────────────────────

_session_lock = asyncio.Lock()
_mcp_session: Any | None = None
_initialized = False


async def _init_mcp_session() -> Any:
    """
    Initialize MCP client session to agent-zero.

    1. HTTP GET to SSE endpoint — reads ONLY the endpoint event line
       (the SSE stream never closes, so we must read one line and exit)
    2. Parse session_id + messages_url from the endpoint event
    3. Return a session wrapper that uses HTTP POST for JSON-RPC calls
    """
    global _mcp_session, _initialized

    async with _session_lock:
        if _initialized and _mcp_session is not None:
            return _mcp_session

        headers = {
            "Authorization": f"Bearer {AZ_MCP_TOKEN}",
            "Accept": "text/event-stream",
        }

        sse_url = _az_url("/sse")
        logger.info(f"[AZ-MCP] Fetching SSE endpoint → {sse_url}")

        session_id: str | None = None
        messages_url: str | None = None

        for attempt in range(1, AZ_MCP_INIT_RETRIES + 1):
            try:
                # Use httpx async client with streaming to read ONE event then close.
                # This is necessary because the SSE stream from agent-zero never closes.
                async with httpx.AsyncClient(timeout=10.0) as client:
                    async with client.stream("GET", sse_url, headers=headers) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if not line.strip():
                                continue
                            logger.debug(f"[AZ-MCP] SSE line: {line[:200]}")
                            # Parse: "data: /mcp/t-{token}/messages/?session_id=..."
                            if line.startswith("data:"):
                                data = line[5:].strip()
                                url_match = re.search(r"(https?://[^\s]+|/mcp/[^\s]+)", data)
                                sid_match = re.search(r"session_id=([a-f0-9]+)", data)
                                if url_match:
                                    messages_url = url_match.group(1)
                                if sid_match:
                                    session_id = sid_match.group(1)
                                logger.info(f"[AZ-MCP] Messages URL: {messages_url}")
                                logger.info(f"[AZ-MCP] Session ID: {session_id}")
                                break
                        # Don't wait for more — SSE stream never closes
                        break
            except Exception as e:
                logger.warning(f"[AZ-MCP] SSE attempt {attempt}/{AZ_MCP_INIT_RETRIES} failed: {e}")
                if attempt < AZ_MCP_INIT_RETRIES:
                    await asyncio.sleep(AZ_MCP_INIT_RETRY_DELAY * attempt)
        else:
            raise RuntimeError(f"[AZ-MCP] Failed to connect after {AZ_MCP_INIT_RETRIES} attempts")

        if not messages_url:
            raise RuntimeError("[AZ-MCP] Never received endpoint event from SSE")

        http_url = _az_url("/http/")

        session = _AgentZeroMCPSession(
            http_url=http_url,
            messages_url=messages_url,
            token=AZ_MCP_TOKEN,
            session_id=session_id,
        )

        _mcp_session = session
        _initialized = True
        logger.info("[AZ-MCP] Session ready")
        return session


def reset_session() -> None:
    """Reset session state (forces re-init on next call)."""
    global _mcp_session, _initialized
    _mcp_session = None
    _initialized = False


# ─── MCP Session Wrapper ───────────────────────────────────────────────────────


class _AgentZeroMCPSession:
    """
    MCP client session for agent-zero streamable HTTP.

    Protocol:
    - SSE at /sse → receives endpoint event with session_id + messages URL
    - HTTP POST /messages/?session_id=... → JSON-RPC calls
    """

    def __init__(
        self,
        http_url: str,
        messages_url: str,
        token: str,
        session_id: str | None,
    ):
        self.http_url = http_url
        self.messages_url = messages_url
        self.token = token
        self.session_id = session_id
        self._client = httpx.AsyncClient(timeout=AZ_MCP_TIMEOUT)

    def _resolve(self, url: str) -> str:
        """Resolve relative URL against the base URL."""
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return urljoin(self.http_url, url)

    def _rpc_payload(self, method: str, params: dict[str, Any] | None = None) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method,
            "params": params or {},
        }

    async def list_tools(self) -> ListToolsResult:
        """Call tools/list via HTTP POST."""
        payload = self._rpc_payload("tools/list")
        resp = await self._client.post(
            self.messages_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"JSON-RPC error: {data['error']}")
        result = data.get("result", {})
        tools_data = result.get("tools", []) if isinstance(result, dict) else []
        from mcp.types import Tool

        tools = [
            Tool(
                name=t.get("name", ""),
                description=t.get("description", ""),
                inputSchema=t.get("inputSchema", {}),
            )
            for t in tools_data
        ]
        return ListToolsResult(tools=tools)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> CallToolResult:
        """Call a tool via HTTP POST."""
        payload = self._rpc_payload("tools/call", {"name": name, "arguments": arguments})
        resp = await self._client.post(
            self.messages_url,
            json=payload,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"JSON-RPC error: {data['error']}")
        result = data.get("result", {})
        from mcp.types import TextContent

        content = []
        if isinstance(result, dict):
            for item in result.get("content", []):
                if isinstance(item, dict):
                    content.append(TextContent(type="text", text=str(item.get("text", item))))
                else:
                    content.append(TextContent(type="text", text=str(item)))
        return CallToolResult(content=content, isError=False)

    async def close(self) -> None:
        await self._client.aclose()


# ─── Public API ────────────────────────────────────────────────────────────────


async def list_az_tools() -> list[dict[str, Any]]:
    """List all tools available from agent-zero MCP server."""
    session = await _init_mcp_session()
    try:
        result = await session.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": t.inputSchema,
            }
            for t in result.tools
        ]
    finally:
        await session.close()


async def call_az_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call a tool on agent-zero via MCP."""
    session = await _init_mcp_session()
    try:
        result = await session.call_tool(tool_name, arguments or {})
        texts = [c.text for c in result.content if hasattr(c, "text")]
        return {"status": "ok", "outputs": texts, "isError": result.isError}
    finally:
        await session.close()


async def send_az_message(
    message: str,
    project_name: str | None = None,
    persistent: bool = False,
    attachments: list[Any] | None = None,
) -> dict[str, Any]:
    """Send a chat message to agent-zero via MCP (send_message tool)."""
    args: dict[str, Any] = {
        "message": message,
        "persistent": persistent,
    }
    if project_name:
        args["project_name"] = project_name
    if attachments:
        args["attachments"] = attachments
    return await call_az_tool("send_message", args)
