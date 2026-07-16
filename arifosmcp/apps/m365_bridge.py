"""
Microsoft 365 / Teams Copilot bridge scaffold for arifOS.

Exposes a small HTTPS/OpenAPI surface with one operation per public arifOS verb,
then forwards those requests into the canonical MCP endpoint.

This is intentionally an adapter, not a replacement public contract.
The source of truth remains:
  runtime/public_surface.py -> tool_registry.json -> .well-known/mcp/server.json
"""

from __future__ import annotations

import os
import uuid
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

PUBLIC_VERBS: tuple[str, ...] = (
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_judge",
    "arif_act",
    "arif_seal",
)

DEFAULT_UPSTREAM_URL = os.getenv("ARIFOS_M365_UPSTREAM_URL", "https://mcp.arif-fazil.com/mcp")
DEFAULT_BRIDGE_HOST = os.getenv("ARIFOS_M365_BRIDGE_HOST", "127.0.0.1")
DEFAULT_BRIDGE_PORT = int(os.getenv("ARIFOS_M365_BRIDGE_PORT", "8091"))
DEFAULT_TIMEOUT_SECONDS = float(os.getenv("ARIFOS_M365_TIMEOUT_SECONDS", "30"))


class ToolInvokeRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)
    actor_id: str | None = None
    session_id: str | None = None
    mcp_session_id: str | None = None


class ToolInvokeEnvelope(BaseModel):
    tool: str
    upstream: str
    mcp_session_id: str
    result: dict[str, Any]


def _derive_health_url(mcp_url: str) -> str | None:
    parts = urlsplit(mcp_url)
    if not parts.scheme or not parts.netloc:
        return None
    path = parts.path or ""
    if path.endswith("/mcp"):
        path = f"{path[:-4]}/health"
    elif path == "/mcp":
        path = "/health"
    else:
        path = "/health"
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))


class ArifM365Bridge:
    def __init__(self, upstream_url: str = DEFAULT_UPSTREAM_URL) -> None:
        self.upstream_url = upstream_url
        self.timeout_seconds = DEFAULT_TIMEOUT_SECONDS

    async def _call_mcp(
        self, method: str, params: dict[str, Any], mcp_session_id: str
    ) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "mcp-session-id": mcp_session_id,
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
            response = await client.post(self.upstream_url, json=payload, headers=headers)
        if response.status_code >= 400:
            detail = response.text[:500]
            try:
                detail = response.json().get("error", {}).get("message", detail)
            except Exception:
                pass
            raise HTTPException(
                status_code=502,
                detail=f"Upstream MCP HTTP {response.status_code}: {detail}",
            )
        try:
            parsed = response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=502, detail=f"Upstream MCP returned non-JSON: {exc}"
            ) from exc
        if parsed.get("error"):
            raise HTTPException(status_code=502, detail=parsed["error"])
        result = parsed.get("result")
        if not isinstance(result, dict):
            raise HTTPException(
                status_code=502,
                detail="Upstream MCP returned malformed result payload",
            )
        return result

    async def call_tool(self, tool_name: str, request: ToolInvokeRequest) -> ToolInvokeEnvelope:
        arguments = dict(request.arguments)
        if request.actor_id is not None and "actor_id" not in arguments:
            arguments["actor_id"] = request.actor_id
        if request.session_id is not None and "session_id" not in arguments:
            arguments["session_id"] = request.session_id
        mcp_session_id = request.mcp_session_id or f"m365-{uuid.uuid4().hex[:16]}"
        result = await self._call_mcp(
            "tools/call",
            {
                "name": tool_name,
                "arguments": arguments,
            },
            mcp_session_id=mcp_session_id,
        )
        return ToolInvokeEnvelope(
            tool=tool_name,
            upstream=self.upstream_url,
            mcp_session_id=mcp_session_id,
            result=result,
        )

    async def list_public_tools(self) -> dict[str, Any]:
        mcp_session_id = f"m365-list-{uuid.uuid4().hex[:12]}"
        result = await self._call_mcp("tools/list", {}, mcp_session_id=mcp_session_id)
        tools = result.get("tools", [])
        if not isinstance(tools, list):
            raise HTTPException(
                status_code=502,
                detail="Upstream MCP tools/list returned malformed tools payload",
            )
        return {
            "upstream": self.upstream_url,
            "mcp_session_id": mcp_session_id,
            "tools": tools,
        }

    async def health(self) -> dict[str, Any]:
        health_url = _derive_health_url(self.upstream_url)
        if not health_url:
            return {
                "status": "degraded",
                "bridge": "m365",
                "upstream_mcp": self.upstream_url,
                "reason": "could_not_derive_health_url",
            }
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(health_url, headers={"Accept": "application/json"})
        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"Upstream health HTTP {response.status_code}: {response.text[:500]}",
            )
        try:
            upstream_health = response.json()
        except ValueError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Upstream health returned non-JSON: {exc}",
            ) from exc
        return {
            "status": "ok",
            "bridge": "m365",
            "upstream_mcp": self.upstream_url,
            "public_verbs": list(PUBLIC_VERBS),
            "upstream_health": upstream_health,
        }


bridge = ArifM365Bridge()

app = FastAPI(
    title="arifOS Microsoft 365 Bridge",
    version="2026.07.03-teams-bridge",
    summary="OpenAPI/HTTPS adapter from Teams Copilot-style actions to arifOS MCP public verbs.",
)


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "name": "arifOS Microsoft 365 Bridge",
        "upstream_mcp": bridge.upstream_url,
        "public_verbs": list(PUBLIC_VERBS),
        "routes": {
            "health": "/health",
            "discover": "/public-tools",
            "init_session": "/init-session",
            "observe": "/observe",
            "think": "/think",
            "route": "/route",
            "judge": "/judge",
            "act": "/act",
            "seal": "/seal",
        },
    }


@app.get("/health")
async def health() -> dict[str, Any]:
    return await bridge.health()


@app.get("/public-tools")
async def public_tools() -> dict[str, Any]:
    return await bridge.list_public_tools()


@app.post("/init-session", response_model=ToolInvokeEnvelope)
async def init_session(request: ToolInvokeRequest) -> ToolInvokeEnvelope:
    return await bridge.call_tool("arif_init", request)


@app.post("/observe", response_model=ToolInvokeEnvelope)
async def observe(request: ToolInvokeRequest) -> ToolInvokeEnvelope:
    return await bridge.call_tool("arif_observe", request)


@app.post("/think", response_model=ToolInvokeEnvelope)
async def think(request: ToolInvokeRequest) -> ToolInvokeEnvelope:
    return await bridge.call_tool("arif_think", request)


@app.post("/route", response_model=ToolInvokeEnvelope)
async def route(request: ToolInvokeRequest) -> ToolInvokeEnvelope:
    return await bridge.call_tool("arif_route", request)


@app.post("/judge", response_model=ToolInvokeEnvelope)
async def judge(request: ToolInvokeRequest) -> ToolInvokeEnvelope:
    return await bridge.call_tool("arif_judge", request)


@app.post("/act", response_model=ToolInvokeEnvelope)
async def act(request: ToolInvokeRequest) -> ToolInvokeEnvelope:
    return await bridge.call_tool("arif_act", request)


@app.post("/seal", response_model=ToolInvokeEnvelope)
async def seal(request: ToolInvokeRequest) -> ToolInvokeEnvelope:
    return await bridge.call_tool("arif_seal", request)


def main() -> None:
    uvicorn.run(app, host=DEFAULT_BRIDGE_HOST, port=DEFAULT_BRIDGE_PORT, log_level="info")  # nosec B104


if __name__ == "__main__":
    main()
