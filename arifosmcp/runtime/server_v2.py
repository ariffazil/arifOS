"""
arifosmcp/runtime/server_v2.py — arifOS MCP v2 Clean Server

Complete MCP package:
- 10 canonical tools (v2 architecture)
- Structured prompts
- Constitutional resources
- Well-known manifest

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import sys
import traceback
from typing import Any

import fastmcp
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response, HTMLResponse
from starlette.requests import Request

from arifosmcp.runtime.fastmcp_version import (
    IS_FASTMCP_2, 
    IS_FASTMCP_3,
    custom_route,
    create_http_app,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL PANIC MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════════

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
    """Injects keepalive for SSE streams."""
    PING_INTERVAL: float = 25.0

    async def dispatch(self, request, call_next):
        import asyncio
        from starlette.responses import StreamingResponse

        response = await call_next(request)
        response.headers["X-Accel-Buffering"] = "no"

        content_type = response.headers.get("content-type", "")
        if "text/event-stream" not in content_type:
            return response

        original_body = response.body_iterator

        async def keepalive_body():
            ping = b": ping\n\n"
            queue: asyncio.Queue = asyncio.Queue()

            async def feed():
                async for chunk in original_body:
                    await queue.put(chunk)
                await queue.put(None)

            feed_task = asyncio.ensure_future(feed())
            try:
                while True:
                    try:
                        chunk = await asyncio.wait_for(queue.get(), timeout=self.PING_INTERVAL)
                        if chunk is None:
                            break
                        yield chunk
                    except asyncio.TimeoutError:
                        yield ping
            finally:
                feed_task.cancel()
                try:
                    await feed_task
                except asyncio.CancelledError:
                    pass

        return StreamingResponse(
            keepalive_body(),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MCP SERVER INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

mcp = FastMCP(
    "ARIFOS MCP",
    version="2.0.0",
    website_url="https://arifosmcp.arif-fazil.com",
    instructions="""Constitutional AI orchestration kernel.

Golden path: init → sense → mind → heart → judge → vault

Public tools: arifos.v2.init, arifos.v2.route, arifos.v2.judge
Internal tools: sense, mind, heart, ops, memory, vault, forge

Use prompts for structured workflows:
- constitutional.analysis: Full pipeline
- governance.audit: Compliance review
- execution.planning: Costed execution
- minimal.response: Direct answer
""",
)

# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER V2 SURFACE
# ═══════════════════════════════════════════════════════════════════════════════

from arifosmcp.runtime.tools_v2 import register_v2_tools
from arifosmcp.runtime.prompts_v2 import register_v2_prompts
from arifosmcp.runtime.resources_v2 import register_v2_resources
from arifosmcp.runtime.manifest_v2 import build_manifest_v2

# Register v2 components
v2_tools_registered = register_v2_tools(mcp)
v2_prompts_registered = register_v2_prompts(mcp)
v2_resources_registered = register_v2_resources(mcp)

logger.info(f"ARIFOS MCP v2 initialized: {len(v2_tools_registered)} tools, "
            f"{len(v2_prompts_registered)} prompts, {len(v2_resources_registered)} resources")

# ═══════════════════════════════════════════════════════════════════════════════
# HTTP APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

# Create HTTP app
if IS_FASTMCP_3:
    app = mcp.http_app(stateless_http=False)
elif IS_FASTMCP_2:
    try:
        app = mcp.streamable_http_app()
    except AttributeError:
        app = mcp._mcp_server.app
else:
    raise RuntimeError(f"Unsupported FastMCP version: {fastmcp.__version__}")

# Add middleware
app.add_middleware(GlobalPanicMiddleware)
app.add_middleware(SSEKeepAliveMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["X-API-Key", "Content-Type", "Authorization", "X-MCP-Protocol"],
)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

async def landing_page_handler(request: Request) -> Response:
    """Dynamic landing page reflecting AF-FORGE deployment status."""
    import os
    
    # Try to load dynamic landing page
    landing_path = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'landing', 'dynamic-index.html')
    if os.path.exists(landing_path):
        with open(landing_path, 'r') as f:
            content = f.read()
        return HTMLResponse(content=content)
    
    # Fallback to simple status
    return JSONResponse({
        "service": "arifOS MCP v2",
        "status": "operational",
        "endpoint": "/health for status, /tools for capabilities",
        "motto": "DITEMPA, BUKAN DIBERI."
    })


async def health_handler(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "service": "arifos-mcp-v2",
        "version": "2.0.0",
        "namespace": "arifos.v2",
        "tools_loaded": len(v2_tools_registered),
        "prompts_loaded": len(v2_prompts_registered),
        "resources_loaded": len(v2_resources_registered),
        "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
    })


async def manifest_handler(request: Request) -> JSONResponse:
    """MCP well-known manifest for discovery."""
    manifest = build_manifest_v2()
    return JSONResponse(manifest)


async def v2_manifest_handler(request: Request) -> JSONResponse:
    """Full MCP v2 manifest."""
    manifest = build_manifest_v2()
    return JSONResponse(manifest)


# Register routes directly on the Starlette app
from starlette.routing import Route

# Add routes to the app
app.add_route("/", landing_page_handler, methods=["GET"])
app.add_route("/health", health_handler, methods=["GET"])
app.add_route("/.well-known/manifest.json", manifest_handler, methods=["GET"])
app.add_route("/v2/manifest", v2_manifest_handler, methods=["GET"])


# ═══════════════════════════════════════════════════════════════════════════════
# SERVER CREATION
# ═══════════════════════════════════════════════════════════════════════════════

def create_v2_mcp_server() -> FastMCP:
    """Create and return the v2 MCP server instance."""
    return mcp


if __name__ == "__main__":
    from arifosmcp.runtime.fastmcp_ext.transports import run_server
    run_server(mcp, mode="http", host="0.0.0.0", port=8080)
