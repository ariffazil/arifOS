"""
arifosmcp/runtime/server.py — arifOS MCP Server

Complete MCP package:
- 11 canonical tools (arifos_init through arifos_vps_monitor)
- Structured prompts
- Constitutional resources
- Well-known manifest + canonical index

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
import platform
import sys
import traceback
from typing import Any

import fastmcp
from fastapi import FastAPI
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
from arifosmcp.runtime.prompts import register_v2_prompts
from arifosmcp.runtime.resources import register_v2_resources
from arifosmcp.runtime.rest_routes import register_rest_routes
from arifosmcp.runtime.public_registry import public_tool_names as _public_tool_names

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL PANIC MIDDLEWARE
# ═══════════════════════════════════════════════════════════════════════════════


def _security_check() -> dict[str, Any]:
    """Verify runtime hardening before starting server."""

    checks = {
        "user": "unknown",
        "uid": -1,
        "is_root": False,
        "filesystem_writable": True,
        "shell_available": True,
        "forge_key_set": False,
        "hardened": False,
        "warnings": [],
    }

    # Platform-specific UID/Root check
    if hasattr(os, "getuid"):
        checks["uid"] = os.getuid()
        checks["is_root"] = checks["uid"] == 0
    else:
        # Windows fallback: attempt to detect admin status if needed
        # For now, we assume non-root/non-admin behavior for the check
        checks["uid"] = -1
        checks["is_root"] = False

    checks["user"] = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))

    if checks["is_root"]:
        checks["warnings"].append("Running as root (blast radius = unlimited)")

    # Check filesystem (hardened environments should be read-only at /app or equivalent)
    try:
        # Use a platform-aware test path or local temp
        test_dir = os.environ.get("ARIFOS_HOME", os.getcwd())
        test_file = os.path.join(test_dir, ".security_test")

        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        checks["filesystem_writable"] = True

        # If we are in a production-like path, warn if it's writable
        if "/app" in test_dir or "arifosmcp" in test_dir:
            checks["warnings"].append(
                f"Project directory {test_dir} is writable (should be read-only in PROD)"
            )
    except (PermissionError, OSError):
        checks["filesystem_writable"] = False

    # Check for shell binaries (Attack surface)
    if platform.system() == "Windows":
        shell_available = any(
            os.path.exists(os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), p))
            for p in ["System32\\cmd.exe", "System32\\WindowsPowerShell\\v1.0\\powershell.exe"]
        )
    else:
        shell_paths = ["/bin/sh", "/bin/bash", "/usr/bin/sh", "/usr/bin/bash"]
        shell_available = any(os.path.exists(p) for p in shell_paths)

    checks["shell_available"] = shell_available
    if checks["shell_available"]:
        checks["warnings"].append("Shell binaries present (attack surface)")

    # Check FORGE signing key
    checks["forge_key_set"] = bool(os.environ.get("FORGE_SIGNING_KEY"))

    if not checks["forge_key_set"]:
        checks["warnings"].append("FORGE_SIGNING_KEY not set (ephemeral key)")

    checks["hardened"] = (
        not checks["is_root"]
        and not checks["filesystem_writable"]
        and not checks["shell_available"]
        and checks["forge_key_set"]
    )

    return checks


_SECURITY_STATUS = _security_check()

if _SECURITY_STATUS["hardened"]:
    logger.info("✅ SECURITY: Hardened deployment verified (LAYER 2 active)")
else:
    logger.warning("⚠️  SECURITY: Development mode — hardening incomplete")
    for warning in _SECURITY_STATUS["warnings"]:
        logger.warning(f"   - {warning}")


# ═══════════════════════════════════════════════════════════════════════════════
# FASTMCP SERVER
# ═══════════════════════════════════════════════════════════════════════════════


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
            return JSONResponse(
                {
                    "status": "void",
                    "tool": "kernel_panic_handler",
                    "error_message": "F13: System halt due to unhandled kernel exception.",
                    "action": "HALT",
                },
                status_code=500,
            )


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

Public tools are derived from tool_specs.py and exposed with canonical underscore ids.
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

from arifosmcp.runtime.tools import register_v2_tools, CANONICAL_TOOL_HANDLERS
from arifosmcp.runtime.prompts import register_v2_prompts
from arifosmcp.runtime.resources import register_v2_resources
from arifosmcp.runtime.manifest import build_manifest_v2
from arifosmcp.runtime.build_info import get_build_info

# Register v2 components
v2_tools_registered = register_v2_tools(mcp)
v2_prompts_registered = register_v2_prompts(mcp)
v2_resources_registered = register_v2_resources(mcp)

logger.info(
    f"ARIFOS MCP v2 initialized: {len(v2_tools_registered)} tools, "
    f"{len(v2_prompts_registered)} prompts, {len(v2_resources_registered)} resources"
)

# ═══════════════════════════════════════════════════════════════════════════════
# REST TOOL EXECUTION ENDPOINT (Horizon Gateway Compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

# Horizon → v2 tool name mapping (for REST proxy compatibility)
HORIZON_TO_V2_MAP: dict[str, str] = {
    "init_anchor": "arifos_init",
    "arifOS_kernel": "arifos_route",
    "physics_reality": "arifos_sense",
    "agi_mind": "arifos_mind",
    "asi_heart": "arifos_heart",
    "math_estimator": "arifos_ops",
    "apex_soul": "arifos_judge",
    "engineering_memory": "arifos_memory",
    "vault_ledger": "arifos_vault",
    "code_engine": "arifos_forge",
    "vps_monitor": "arifos_vps_monitor",
    "architect_registry": "arifos_init",
    # v2 names also accepted directly
    "arifos_init": "arifos_init",
    "arifos_route": "arifos_route",
    "arifos_sense": "arifos_sense",
    "arifos_mind": "arifos_mind",
    "arifos_heart": "arifos_heart",
    "arifos_ops": "arifos_ops",
    "arifos_judge": "arifos_judge",
    "arifos_memory": "arifos_memory",
    "arifos_vault": "arifos_vault",
    "arifos_forge": "arifos_forge",
    "arifos_vps_monitor": "arifos_vps_monitor",
}


async def rest_tool_handler(request: Request) -> JSONResponse:
    """REST endpoint for tool execution - enables Horizon gateway proxy.

    POST /tools/{tool_name}
    Body: JSON arguments for the tool
    """
    import json

    tool_name = request.path_params.get("tool_name") or ""

    # Map Horizon name to v2 name, normalizing dots to underscores
    from arifosmcp.runtime.tool_specs import normalize_tool_name
    normalized_name = normalize_tool_name(tool_name)
    v2_name = HORIZON_TO_V2_MAP.get(normalized_name, normalized_name)

    # Get handler
    handler = CANONICAL_TOOL_HANDLERS.get(v2_name)
    if not handler:
        return JSONResponse(
            {
                "error": f"Tool not found: {tool_name}",
                "available_tools": list(HORIZON_TO_V2_MAP.keys()),
            },
            status_code=404,
        )

    # Parse body
    try:
        body = await request.json()
    except Exception:
        body = {}

    # Extract common params
    session_id = body.pop("session_id", None)
    risk_tier = body.pop("risk_tier", "medium")
    dry_run = body.pop("dry_run", True)
    debug = body.pop("debug", False)

    # Parameter normalization: map common aliases to expected names
    # arifos_sense expects "query", arifos_ops expects "action"
    # But callers may send "query" for any tool
    if v2_name == "arifos_sense" and "query" not in body:
        body.setdefault("query", body.pop("input", None))
    elif v2_name == "arifos_ops":
        # For ops, accept "query" as alias for "action"
        if "action" not in body:
            body["action"] = body.pop("query", "") or ""
    elif v2_name in ("arifos_mind", "arifos_heart") and "content" not in body:
        # mind and heart expect "content"
        if "query" in body:
            body.setdefault("content", body.pop("query", ""))
        elif "input" in body:
            body.setdefault("content", body.pop("input", ""))
    elif v2_name == "arifos_judge" and "candidate" not in body:
        # judge expects "candidate"
        body.setdefault("candidate", body.pop("query", ""))
    elif v2_name == "arifos_route":
        # arifos_route expects "request" but callers may send "intent", "query", "input"
        if "request" not in body:
            for key in ["intent", "query", "input", "content", "text"]:
                if key in body:
                    body["request"] = body.pop(key)
                    break
    elif v2_name == "arifos_mind" and "query" not in body:
        # arifos_mind expects "query" but callers may send "content"
        if "content" in body:
            body["query"] = body.pop("content")

    try:
        # Call handler
        result = await handler(
            session_id=session_id,
            risk_tier=risk_tier,
            dry_run=dry_run,
            debug=debug,
            **body,
        )

        # Convert RuntimeEnvelope to dict if needed
        if hasattr(result, "model_dump"):
            response_data = result.model_dump()
        elif hasattr(result, "__dict__"):
            response_data = dict(result.__dict__)
        else:
            response_data = result

        return JSONResponse(response_data)

    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        return JSONResponse(
            {
                "error": str(e),
                "tool": tool_name,
                "v2_tool": v2_name,
                "message": "Tool execution failed",
            },
            status_code=500,
        )


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
    landing_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "static", "landing", "dynamic-index.html"
    )
    if os.path.exists(landing_path):
        with open(landing_path, "r") as f:
            content = f.read()
        return HTMLResponse(content=content)

    # Fallback to simple status
    return JSONResponse(
        {
            "service": "arifOS MCP v2",
            "status": "operational",
            "endpoint": "/health for status, /tools for capabilities",
            "motto": "DITEMPA, BUKAN DIBERI.",
        }
    )


async def health_handler(request: Request) -> JSONResponse:
    """Health check endpoint — runtime truth for what is running right now."""
    import datetime

    build = get_build_info()
    return JSONResponse(
        {
            "status": "healthy",
            "service": "arifos-mcp",
            "version": build["server_version"],
            "release_tag": build["release_tag"],
            "namespace": "arifos",
            "transport": "streamable-http",
            "canonical_tools": len(v2_tools_registered),
            "total_tools": len(v2_tools_registered),
            "prompts_loaded": len(v2_prompts_registered),
            "resources_loaded": len(v2_resources_registered),
            "protocol_version": build["protocol_version"],
            "governance_version": build["governance_version"],
            "floors_active": build["floors_active"],
            # Source-of-Truth linkage: ties this runtime back to canonical doctrine
            "source_repo": build["source_repo"],
            "source_commit": build["build"]["commit_short"],
            "warnings": [],
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    )


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

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static")


# Static file handlers
async def llms_txt_handler(request: Request) -> Response:
    """Serve llms.txt for LLM/agent discovery."""
    file_path = os.path.join(STATIC_DIR, "llms.txt")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return Response(content=content, media_type="text/plain")
    return Response("LLMs.txt not found", status_code=404)


async def humans_txt_handler(request: Request) -> Response:
    """Serve humans.txt for human contact info."""
    file_path = os.path.join(STATIC_DIR, "humans.txt")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return Response(content=content, media_type="text/plain")
    return Response("humans.txt not found", status_code=404)


async def robots_txt_handler(request: Request) -> Response:
    """Serve robots.txt for crawler guidance."""
    file_path = os.path.join(STATIC_DIR, "robots.txt")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return Response(content=content, media_type="text/plain")
    return Response("User-agent: *\nAllow: /", media_type="text/plain")


async def well_known_handler(request: Request, filename: str) -> Response:
    """Serve .well-known files."""
    file_path = os.path.join(STATIC_DIR, ".well-known", filename)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        # Determine content type
        if filename.endswith(".json"):
            media_type = "application/json"
        elif filename.endswith(".txt"):
            media_type = "text/plain"
        else:
            media_type = "application/octet-stream"
        return Response(content=content, media_type=media_type)
    return Response(f"{filename} not found", status_code=404)


async def version_handler(request: Request) -> JSONResponse:
    """Version and capability endpoint."""
    return JSONResponse(
        {
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
                "security": "/.well-known/security.txt",
            },
        }
    )


async def tools_handler(request: Request) -> JSONResponse:
    """Tool catalog endpoint for discovery."""
    return JSONResponse(
        {
            "count": len(v2_tools_registered),
            "tools": v2_tools_registered,
            "version": "2.0.0",
            "motto": "DITEMPA, BUKAN DIBERI.",
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# A2A (Agent-to-Agent) ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════


async def a2a_agent_card_handler(request: Request) -> JSONResponse:
    """A2A Agent Card endpoint for agent discovery."""
    # Try to serve from static file first
    file_path = os.path.join(STATIC_DIR, ".well-known", "agent.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            import json

            return JSONResponse(json.load(f))

    # Fallback to generated card
    return JSONResponse(
        {
            "name": "arifOS MCP",
            "version": "2.0.0",
            "description": "Constitutional AI Governance System",
            "url": "https://arifosmcp.arif-fazil.com",
            "endpoints": {
                "mcp": "https://arifosmcp.arif-fazil.com/mcp",
                "health": "https://arifosmcp.arif-fazil.com/health",
                "tools": "https://arifosmcp.arif-fazil.com/tools",
            },
            "protocols": {
                "mcp": {"version": "2025-11-05", "transport": ["streamable-http", "sse"]},
                "a2a": {"version": "1.0", "capabilities": ["task-delegation"]},
            },
            "motto": "DITEMPA, BUKAN DIBERI.",
        }
    )


async def a2a_tasks_handler(request: Request) -> JSONResponse:
    """A2A Task delegation endpoint."""
    import json

    try:
        body = await request.json()
        task_id = body.get("id", "unknown")
        task_type = body.get("type", "unknown")

        # Handle different task types
        if task_type == "governance":
            return JSONResponse(
                {
                    "id": task_id,
                    "status": "accepted",
                    "verdict": "SEAL",
                    "note": "Task delegated to arifOS governance layer",
                }
            )
        elif task_type == "execution":
            return JSONResponse(
                {
                    "id": task_id,
                    "status": "requires_verdict",
                    "note": "Execution requires judge verdict. Route through arifos_judge first.",
                }
            )
        else:
            return JSONResponse(
                {
                    "id": task_id,
                    "status": "accepted",
                    "note": "Task received. Use MCP protocol for execution.",
                }
            )
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)}, status_code=400)


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
        },
    )


async def webmcp_manifest_handler(request: Request) -> JSONResponse:
    """WebMCP manifest for discovery."""
    return JSONResponse(
        {
            "schema_version": "1.0",
            "name": "ARIFOS WebMCP",
            "transport": "http-sse",
            "endpoint": "/mcp",
            "capabilities": ["tools", "prompts", "resources"],
        }
    )


async def webmcp_tools_handler(request: Request) -> JSONResponse:
    """WebMCP specific tools list."""
    # Maps canonical tools to WebMCP format if needed
    return await tools_handler(request)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER ALL ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

# Main routes
app.add_route("/", landing_page_handler, methods=["GET"])
app.add_route("/health", health_handler, methods=["GET", "OPTIONS"])
app.add_route("/version", version_handler, methods=["GET"])
app.add_route("/tools", tools_handler, methods=["GET"])
app.add_route("/tools/{tool_name}", rest_tool_handler, methods=["POST"])

# Discovery files
app.add_route("/llms.txt", llms_txt_handler, methods=["GET"])
app.add_route("/humans.txt", humans_txt_handler, methods=["GET"])
app.add_route("/robots.txt", robots_txt_handler, methods=["GET"])

# Well-known endpoints
app.add_route("/.well-known/mcp", manifest_handler, methods=["GET"])
app.add_route("/.well-known/mcp/server.json", manifest_handler, methods=["GET"])
app.add_route("/.well-known/manifest.json", manifest_handler, methods=["GET"])
app.add_route("/.well-known/agent.json", a2a_agent_card_handler, methods=["GET"])
app.add_route("/.well-known/webmcp", webmcp_manifest_handler, methods=["GET"])
app.add_route("/webmcp/tools.json", webmcp_tools_handler, methods=["GET"])


async def canonical_index_handler(request: Request) -> JSONResponse:
    """Canonical index — ties this runtime back to the arifOS SoT repo."""
    build = get_build_info()
    return JSONResponse(
        {
            "name": "arifOS MCP Runtime",
            "source_of_truth": {
                "repo": build["source_repo"],
                "declaration": "Canonical doctrine, Floors F1-F13, and architecture live in the arifOS repository.",
            },
            "runtime_truth": {
                "health": "https://arifosmcp.arif-fazil.com/health",
                "tools": "https://arifosmcp.arif-fazil.com/tools",
                "note": "Live /health and /tools are the canonical surface for what is running right now.",
            },
            "version": build["server_version"],
            "release_tag": build["release_tag"],
            "source_commit": build["build"]["commit_short"],
            "namespace": "arifos",
            "tools_loaded": len(v2_tools_registered),
            "links": {
                "source_repo": build["source_repo"],
                "docs": "https://arifos.arif-fazil.com/mcp-server",
                "pypi": "https://pypi.org/project/arifosmcp/",
                "canonical_index": "https://arifosmcp.arif-fazil.com/.well-known/arifos-index.json",
            },
        }
    )


async def security_txt_handler(request: Request) -> Response:
    """Serve security.txt."""
    return await well_known_handler(request, "security.txt")


async def belief_state_handler(request: Request) -> Response:
    """
    GET /api/belief/{actor_id} — introspect current belief state for an actor.
    F11-read: public read for transparency (no secrets exposed — only inferred signals).
    """
    actor_id = request.path_params.get("actor_id", "").strip()
    if not actor_id:
        return JSONResponse({"error": "actor_id required"}, status_code=400)
    try:
        from arifosmcp.runtime.belief_registry import get_registry
        state = get_registry().load(actor_id)
        return JSONResponse(state.to_dict(), headers={"Access-Control-Allow-Origin": "*"})
    except Exception as exc:
        logger.exception("belief_state_handler failed")
        return JSONResponse({"error": str(exc)}, status_code=500)


app.add_route("/.well-known/security.txt", security_txt_handler, methods=["GET"])
app.add_route("/.well-known/arifos-index.json", canonical_index_handler, methods=["GET"])

# ToM: belief state introspection (F11-read)
app.add_route("/api/belief/{actor_id}", belief_state_handler, methods=["GET"])

# A2A endpoints
app.add_route("/a2a/agent", a2a_agent_card_handler, methods=["GET"])
app.add_route("/a2a/tasks", a2a_tasks_handler, methods=["POST", "OPTIONS"])

# WebMCP CORS
app.add_route("/mcp", webmcp_options_handler, methods=["OPTIONS"])

# v2 manifest
app.add_route("/v2/manifest", v2_manifest_handler, methods=["GET"])


# ─── Vault-Seal Widget (ChatGPT Apps SDK) ─────────────────────────────────────
_WIDGET_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "project", "static", "widgets", "vault-seal-widget.html",
)
_WIDGET_CSP = (
    "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
    "font-src 'self'; img-src 'self' data:; "
    "frame-ancestors https://chat.openai.com https://chatgpt.com; connect-src 'self';"
)
_WIDGET_HEADERS = {
    "Content-Security-Policy": _WIDGET_CSP,
    "X-Frame-Options": "ALLOW-FROM https://chat.openai.com",
    "Access-Control-Allow-Origin": "https://chat.openai.com",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Cache-Control": "public, max-age=3600",
}


async def vault_seal_widget_handler(request: Request) -> Response:
    """Vault-Seal widget for ChatGPT Apps SDK iframe embedding."""
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=_WIDGET_HEADERS)
    widget_path = _WIDGET_FILE
    if not os.path.exists(widget_path):
        # Fallback absolute path (container ro-mount)
        widget_path = "/usr/src/project/static/widgets/vault-seal-widget.html"
    if not os.path.exists(widget_path):
        return Response("Widget not found", status_code=404)
    with open(widget_path, "r", encoding="utf-8") as fh:
        html = fh.read()
    return HTMLResponse(html, headers=_WIDGET_HEADERS)


app.add_route("/widget/vault-seal", vault_seal_widget_handler, methods=["GET", "OPTIONS"])
app.add_route("/widget/", vault_seal_widget_handler, methods=["GET"])


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
