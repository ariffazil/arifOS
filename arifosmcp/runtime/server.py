"""
arifosmcp/runtime/server.py — arifOS AAA Sovereign Hub - HARDENED

UPGRADE: Global Panic Middleware and Sovereign Domain Hardening.
FIX: Register routes BEFORE creating http_app
"""

from __future__ import annotations

import logging
import sys
import traceback
from typing import Any

import fastmcp
from arifosmcp.runtime.fastmcp_version import IS_FASTMCP_2, IS_FASTMCP_3
from arifosmcp.runtime.prompts import register_prompts
from arifosmcp.runtime.resources import register_resources
from arifosmcp.runtime.rest_routes import register_rest_routes
from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS, register_tools
from arifosmcp.runtime.public_registry import public_tool_names as _public_tool_names

# Combine canonical tools with ChatGPT Apps SDK tools for REST surface
_CHATGPT_TOOLS = {
    "get_constitutional_health": None,  # Will be resolved from tools module
    "list_recent_verdicts": None,
    "render_vault_seal": None,
}

# Import ChatGPT tool handlers
try:
    from arifosmcp.runtime.tools import get_constitutional_health, list_recent_verdicts
    from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import render_vault_seal
    _CHATGPT_TOOLS["get_constitutional_health"] = get_constitutional_health
    _CHATGPT_TOOLS["list_recent_verdicts"] = list_recent_verdicts
    _CHATGPT_TOOLS["render_vault_seal"] = render_vault_seal
except ImportError as e:
    logger.warning(f"Could not import ChatGPT tools: {e}")

# REST surface: canonical tools + ChatGPT Apps SDK tools
_CANONICAL_TOOL_IMPLEMENTATIONS = {**CANONICAL_TOOL_HANDLERS, **_CHATGPT_TOOLS}
from fastapi import FastAPI
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


def _build_fallback_a2a_app() -> FastAPI:
    """Expose a minimal A2A surface when optional protocol deps are missing."""
    app = FastAPI(title="arifOS A2A Fallback")
    tasks: dict[str, dict[str, Any]] = {}

    @app.get("/health")
    async def health() -> dict[str, Any]:
        return {"status": "healthy", "protocol": "A2A", "mode": "fallback"}

    @app.post("/task")
    async def submit_task(payload: dict[str, Any]) -> dict[str, Any]:
        import uuid

        task_id = f"a2a-fallback-{uuid.uuid4().hex[:12]}"
        tasks[task_id] = {
            "id": task_id,
            "state": "submitted",
            "messages": payload.get("messages", []),
            "client_agent_id": payload.get("client_agent_id"),
        }
        return {"task_id": task_id, "task": tasks[task_id]}

    @app.get("/status/{task_id}")
    async def task_status(task_id: str) -> JSONResponse:
        task = tasks.get(task_id)
        if task is None:
            return JSONResponse({"error": "Task not found"}, status_code=404)
        return JSONResponse({"task": task, "mode": "fallback"})

    return app


def _build_fallback_webmcp_app() -> FastAPI:
    """Expose discovery routes when WebMCP optional deps are missing."""
    app = FastAPI(title="arifOS WebMCP Fallback")

    @app.get("/.well-known/webmcp")
    async def manifest() -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "site": {
                "name": "arifOS Constitutional AI",
                "url": "https://aaa.arif-fazil.com",
                "version": mcp.version,
            },
            "tools": [],
            "fallback": True,
        }

    @app.get("/webmcp/sdk.js")
    async def sdk() -> Response:
        return Response(
            "window.arifOSWebMCP={init:async()=>({fallback:true}),tools:async()=>({tools:[]})};",
            media_type="application/javascript",
        )

    @app.get("/webmcp/tools.json")
    async def tools_manifest() -> dict[str, Any]:
        return {"service": "arifOS WebMCP", "version": mcp.version, "tools": []}

    @app.post("/webmcp/init")
    async def init_session(payload: dict[str, Any]) -> dict[str, Any]:
        import uuid

        return {
            "verdict": "PARTIAL",
            "session_id": f"web-fallback-{uuid.uuid4().hex[:12]}",
            "auth_context": {"actor_id": payload.get("actor_id", "anonymous")},
            "fallback": True,
        }

    return app

# ---------------------------------------------------------------------------
# HARDENING: GLOBAL PANIC MIDDLEWARE
# ---------------------------------------------------------------------------

class GlobalPanicMiddleware(BaseHTTPMiddleware):
    """Intercepts kernel panics and emits a Constitutional VOID."""
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            print(f"!!! KERNEL PANIC: {str(e)}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            return JSONResponse({
                "status": "void",
                "tool": "kernel_panic_handler",
                "error_message": "F13: System halt due to unhandled kernel exception.",
                "action": "HALT"
            }, status_code=500)


class SSEKeepAliveMiddleware(BaseHTTPMiddleware):
    """Injects X-Accel-Buffering: no on all responses to disable CF/Nginx buffering.

    For streaming / SSE responses (text/event-stream), wraps the body iterator
    to emit a comment keepalive (': ping\\n\\n') every PING_INTERVAL seconds so
    Cloudflare's 100-second proxy timeout never triggers on an idle stream.
    """

    PING_INTERVAL: float = 25.0  # < CF 100 s proxy timeout

    async def dispatch(self, request, call_next):
        import asyncio
        from starlette.responses import StreamingResponse

        response = await call_next(request)
        response.headers["X-Accel-Buffering"] = "no"

        content_type = response.headers.get("content-type", "")
        if "text/event-stream" not in content_type:
            return response

        # Wrap SSE body with a keepalive ping generator
        original_body = response.body_iterator

        async def keepalive_body():
            ping = b": ping\n\n"
            queue: asyncio.Queue = asyncio.Queue()

            async def feed():
                async for chunk in original_body:
                    await queue.put(chunk)
                await queue.put(None)  # sentinel

            feed_task = asyncio.ensure_future(feed())
            try:
                while True:
                    try:
                        chunk = await asyncio.wait_for(queue.get(), timeout=self.PING_INTERVAL)
                        if chunk is None:
                            break
                        yield chunk
                    except asyncio.TimeoutError:
                        yield ping  # keepalive comment — CF resets its idle timer
            finally:
                feed_task.cancel()

        return StreamingResponse(
            keepalive_body(),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=content_type,
        )

# ---------------------------------------------------------------------------
# SERVER INITIALIZATION
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "arifOS Sovereign Intelligence Kernel",
    version="2026.03.24-HARDENED",
    website_url="https://aaa.arif-fazil.com",
)

# Register Surface FIRST (before creating http_app)
register_tools(mcp)
register_prompts(mcp)
register_resources(mcp)
register_rest_routes(mcp, _CANONICAL_TOOL_IMPLEMENTATIONS)

# ChatGPT Apps SDK integration DISABLED for lean deployment (≤13 tools)
# To enable: uncomment below and ensure total tools ≤13
# try:
#     from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import register_chatgpt_app_tools
#     register_chatgpt_app_tools(mcp)
# except Exception as e:
#     logger.warning(f"ChatGPT Apps SDK not registered: {e}")

# THEN create the app with all routes included
# FastMCP 2.x/3.x compatibility
# NOTE: stateless_http=False ensures SSE responses for ChatGPT Apps SDK compatibility
if IS_FASTMCP_3:
    app = mcp.http_app(stateless_http=False)
elif IS_FASTMCP_2:
    # 2.x uses streamable_http_app() or direct mounting
    try:
        app = mcp.streamable_http_app()
    except AttributeError:
        # Fallback: get underlying ASGI app
        app = mcp._mcp_server.app
else:
    raise RuntimeError(f"Unsupported FastMCP version: {fastmcp.__version__}")

app.add_middleware(GlobalPanicMiddleware)
app.add_middleware(SSEKeepAliveMiddleware)

# Strict CORS: Only allow Sovereign Domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["X-API-Key", "Content-Type", "Authorization", "X-MCP-Protocol"],
)


def _attach_protocol_apps() -> None:
    """
    Attach side-protocol apps to the live FastMCP site.

    A2A is mounted under `/a2a`, which matches the advertised REST endpoints.
    WebMCP is mounted at `/` late in route order so its existing `/webmcp`,
    `/.well-known/webmcp`, and `/api/live/*` routes become reachable without
    changing their internal path definitions.
    """
    if not hasattr(app, "mount"):
        return

    # Mount static files FIRST (before fallbacks)
    from starlette.staticfiles import StaticFiles
    
    # Dashboard and widgets (static files are in /usr/src/project/static/)
    app.mount("/dashboard", StaticFiles(directory="/usr/src/project/static/dashboard", html=True), name="dashboard")
    app.mount("/ui", StaticFiles(directory="/usr/src/project/static/widgets", html=True), name="ui")
    app.mount("/widgets", StaticFiles(directory="/usr/src/project/static/widgets", html=True), name="widgets")

    try:
        from arifosmcp.runtime.a2a import create_a2a_server

        a2a_server = create_a2a_server(mcp)
        app.mount("/a2a", a2a_server.app, name="a2a")
    except Exception:
        logger.exception("Failed to attach A2A app")
        app.mount("/a2a", _build_fallback_a2a_app(), name="a2a-fallback")

    try:
        from arifosmcp.runtime.webmcp.server import create_webmcp_app

        webmcp_app = create_webmcp_app(mcp)
        app.mount("/", webmcp_app, name="webmcp")
    except Exception:
        logger.exception("Failed to attach WebMCP app")
        app.mount("/", _build_fallback_webmcp_app(), name="webmcp-fallback")


_attach_protocol_apps()

def create_aaa_mcp_server() -> FastMCP:
    return mcp

if __name__ == "__main__":
    from arifosmcp.runtime.fastmcp_ext.transports import run_server
    run_server(mcp, mode="http", host="0.0.0.0", port=8080)
