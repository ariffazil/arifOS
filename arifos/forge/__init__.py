"""arifos.forge — thin MCP client for the A-FORGE gateway.

CLIENT ONLY. Never re-implements the TypeScript runtime.
Speaks MCP streamable-http JSON-RPC to http://localhost:7072/mcp
(override via ``AFORGE_MCP_URL``).

Usage::

    from arifos.forge import ForgeClient, connect
    c = connect()               # initialize handshake
    tools = c.list_tools()      # [{name, description, ...}, ...]
    out = c.call("forge_health_check")

CLI probe::

    python -m arifos.forge probe
"""

from __future__ import annotations

import itertools
import json
import os
from typing import Any

import httpx

DEFAULT_URL = os.environ.get("AFORGE_MCP_URL", "http://localhost:7072/mcp")
PROTOCOL_VERSION = "2025-03-26"

__all__ = ["ForgeClient", "connect", "list_tools", "call", "DEFAULT_URL"]


def _extract_json(body: str) -> dict:
    """Handle both plain JSON and SSE-framed (``data:``) responses."""
    body = body.strip()
    if body.startswith("{"):
        return json.loads(body)
    for line in body.splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:].strip())
    raise ValueError(f"Unparseable MCP response: {body[:200]!r}")


class ForgeClient:
    """Minimal MCP streamable-http client (initialize / tools/list / tools/call)."""

    def __init__(self, url: str = DEFAULT_URL, timeout: float = 60.0) -> None:
        self.url = url
        self._ids = itertools.count(1)
        self._session_id: str | None = None
        self._http = httpx.Client(
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )

    # -- transport ---------------------------------------------------------
    def _post(self, payload: dict) -> httpx.Response:
        headers = {}
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        resp = self._http.post(self.url, json=payload, headers=headers)
        sid = resp.headers.get("mcp-session-id")
        if sid:
            self._session_id = sid
        return resp

    def _rpc(self, method: str, params: dict | None = None) -> Any:
        resp = self._post(
            {"jsonrpc": "2.0", "id": next(self._ids), "method": method, "params": params or {}}
        )
        resp.raise_for_status()
        data = _extract_json(resp.text)
        if "error" in data:
            raise RuntimeError(f"MCP error from {method}: {data['error']}")
        return data.get("result")

    def _notify(self, method: str, params: dict | None = None) -> None:
        self._post({"jsonrpc": "2.0", "method": method, "params": params or {}})

    # -- MCP surface ---------------------------------------------------------
    def connect(self) -> dict:
        result = self._rpc(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "arifos.forge", "version": "1.0.0"},
            },
        )
        self._notify("notifications/initialized")
        return result

    def list_tools(self) -> list[dict]:
        result = self._rpc("tools/list")
        return result.get("tools", []) if isinstance(result, dict) else []

    def call(self, tool: str, **arguments: Any) -> Any:
        return self._rpc("tools/call", {"name": tool, "arguments": arguments})

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> ForgeClient:
        self.connect()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


# -- module-level conveniences ------------------------------------------------
def connect(url: str = DEFAULT_URL) -> ForgeClient:
    client = ForgeClient(url)
    client.connect()
    return client


def list_tools(url: str = DEFAULT_URL) -> list[dict]:
    with ForgeClient(url) as client:
        return client.list_tools()


def call(tool: str, url: str = DEFAULT_URL, **arguments: Any) -> Any:
    with ForgeClient(url) as client:
        return client.call(tool, **arguments)
