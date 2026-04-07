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


# ═══════════════════════════════════════════════════════════════════════════════
# STATIC FILE SERVING
# ═══════════════════════════════════════════════════════════════════════════════

from starlette.staticfiles import StaticFiles
from starlette.routing import Mount, Route
import os

STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'static')

# Static file handlers
async def llms_txt_handler(request: Request) -> Response:
    """Serve llms.txt for LLM/agent discovery."""
    file_path = os.path.join(STATIC_DIR, 'llms.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return Response(content=content, media_type="text/plain")
    return Response("LLMs.txt not found", status_code=404)


async def humans_txt_handler(request: Request) -> Response:
    """Serve humans.txt for human contact info."""
    file_path = os.path.join(STATIC_DIR, 'humans.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return Response(content=content, media_type="text/plain")
    return Response("humans.txt not found", status_code=404)


async def robots_txt_handler(request: Request) -> Response:
    """Serve robots.txt for crawler guidance."""
    file_path = os.path.join(STATIC_DIR, 'robots.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return Response(content=content, media_type="text/plain")
    return Response("User-agent: *\nAllow: /", media_type="text/plain")


async def well_known_handler(request: Request, filename: str) -> Response:
    """Serve .well-known files."""
    file_path = os.path.join(STATIC_DIR, '.well-known', filename)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        # Determine content type
        if filename.endswith('.json'):
            media_type = "application/json"
        elif filename.endswith('.txt'):
            media_type = "text/plain"
        else:
            media_type = "application/octet-stream"
        return Response(content=content, media_type=media_type)
    return Response(f"{filename} not found", status_code=404)


async def version_handler(request: Request) -> JSONResponse:
    """Version and capability endpoint."""
    return JSONResponse({
        "name": "arifOS MCP",
        "version": "2.0.0",
        "registry_version": "1.2.0",
        "protocol": "MCP 2025-11-05",
        "protocols_supported": ["MCP", "WebMCP", "A2A"],
        "tools": len(v2_tools_registered),
        "prompts": len(v2_prompts_registered),
        "resources": len(v2_resources_registered),
        "floors": 13,
        "motto": "DITEMPA, BUKAN DIBERI.",
        "url": "https://arifosmcp.arif-fazil.com",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "tools": "/tools",
            "llms_txt": "/llms.txt",
            "agent_card": "/.well-known/agent.json",
            "security": "/.well-known/security.txt"
        }
    })


async def tools_handler(request: Request) -> JSONResponse:
    """Tool catalog endpoint for discovery."""
    return JSONResponse({
        "count": len(v2_tools_registered),
        "tools": v2_tools_registered,
        "version": "2.0.0",
        "motto": "DITEMPA, BUKAN DIBERI."
    })


# ═══════════════════════════════════════════════════════════════════════════════
# A2A (Agent-to-Agent) ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

async def a2a_agent_card_handler(request: Request) -> JSONResponse:
    """A2A Agent Card endpoint for agent discovery."""
    # Try to serve from static file first
    file_path = os.path.join(STATIC_DIR, '.well-known', 'agent.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            import json
            return JSONResponse(json.load(f))
    
    # Fallback to generated card
    return JSONResponse({
        "name": "arifOS MCP",
        "version": "2.0.0",
        "description": "Constitutional AI Governance System",
        "url": "https://arifosmcp.arif-fazil.com",
        "endpoints": {
            "mcp": "https://arifosmcp.arif-fazil.com/mcp",
            "health": "https://arifosmcp.arif-fazil.com/health",
            "tools": "https://arifosmcp.arif-fazil.com/tools"
        },
        "protocols": {
            "mcp": {"version": "2025-11-05", "transport": ["streamable-http", "sse"]},
            "a2a": {"version": "1.0", "capabilities": ["task-delegation"]}
        },
        "motto": "DITEMPA, BUKAN DIBERI."
    })


async def a2a_tasks_handler(request: Request) -> JSONResponse:
    """A2A Task delegation endpoint."""
    import json
    try:
        body = await request.json()
        task_id = body.get('id', 'unknown')
        task_type = body.get('type', 'unknown')
        
        # Handle different task types
        if task_type == 'governance':
            return JSONResponse({
                "id": task_id,
                "status": "accepted",
                "verdict": "SEAL",
                "note": "Task delegated to arifOS governance layer"
            })
        elif task_type == 'execution':
            return JSONResponse({
                "id": task_id,
                "status": "requires_verdict",
                "note": "Execution requires judge verdict. Route through arifos.judge first."
            })
        else:
            return JSONResponse({
                "id": task_id,
                "status": "accepted",
                "note": "Task received. Use MCP protocol for execution."
            })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "error": str(e)
        }, status_code=400)


# ═══════════════════════════════════════════════════════════════════════════════
# WEBMCP COMPATIBILITY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

async def webmcp_options_handler(request: Request) -> Response:
    """Handle CORS preflight for WebMCP."""
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-MCP-Protocol, Authorization",
            "Access-Control-Max-Age": "86400",
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER ALL ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

# Main routes
app.add_route("/", landing_page_handler, methods=["GET"])
app.add_route("/health", health_handler, methods=["GET", "OPTIONS"])
app.add_route("/version", version_handler, methods=["GET"])
app.add_route("/tools", tools_handler, methods=["GET"])

# Discovery files
app.add_route("/llms.txt", llms_txt_handler, methods=["GET"])
app.add_route("/humans.txt", humans_txt_handler, methods=["GET"])
app.add_route("/robots.txt", robots_txt_handler, methods=["GET"])

# Well-known endpoints
app.add_route("/.well-known/mcp", manifest_handler, methods=["GET"])
app.add_route("/.well-known/manifest.json", manifest_handler, methods=["GET"])
app.add_route("/.well-known/agent.json", a2a_agent_card_handler, methods=["GET"])
async def security_txt_handler(request: Request) -> Response:
    """Serve security.txt."""
    return await well_known_handler(request, "security.txt")

app.add_route("/.well-known/security.txt", security_txt_handler, methods=["GET"])

# A2A endpoints
app.add_route("/a2a/agent", a2a_agent_card_handler, methods=["GET"])
app.add_route("/a2a/tasks", a2a_tasks_handler, methods=["POST", "OPTIONS"])

# WebMCP CORS
app.add_route("/mcp", webmcp_options_handler, methods=["OPTIONS"])

# v2 manifest
app.add_route("/v2/manifest", v2_manifest_handler, methods=["GET"])


# ═══════════════════════════════════════════════════════════════════════════════
# SERVER CREATION
# ═══════════════════════════════════════════════════════════════════════════════

def create_v2_mcp_server() -> FastMCP:
    """Create and return the v2 MCP server instance."""
    return mcp


# Compatibility alias — preserves existing imports of create_aaa_mcp_server
# across __init__.py, __main__.py, tests, and CLI entry points.
create_aaa_mcp_server = create_v2_mcp_server


if __name__ == "__main__":
    from arifosmcp.runtime.fastmcp_ext.transports import run_server
    run_server(mcp, mode="http", host="0.0.0.0", port=8080)
