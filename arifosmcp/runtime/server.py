"""
arifosmcp/runtime/server.py — arifOS MCP Server

Complete MCP package:
- 11 canonical tools (arifos.init through arifos.vps_monitor)
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

# Task Ψ-INFRA: Explicitly load .env early and disable automatic search to prevent PermissionErrors
import os
from dotenv import load_dotenv
_env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path, override=True)
os.environ["PYDANTIC_SETTINGS_DOTENV_FILES"] = ""

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
        checks["uid"] = -1
        checks["is_root"] = False

    checks["user"] = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))

    if checks["is_root"]:
        checks["warnings"].append("Running as root (blast radius = unlimited)")

    try:
        test_dir = os.environ.get("ARIFOS_HOME", os.getcwd())
        test_file = os.path.join(test_dir, ".security_test")

        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        checks["filesystem_writable"] = True

        if "/app" in test_dir or "arifosmcp" in test_dir:
            checks["warnings"].append(
                f"Project directory {test_dir} is writable (should be read-only in PROD)"
            )
    except (PermissionError, OSError):
        checks["filesystem_writable"] = False

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

def create_aaa_mcp_server() -> FastMCP:
    """Factory for arifOS MCP Server (AAA = Aligned, Autonomous, Audit-able)."""
    return mcp

mcp = FastMCP(
    "ARIFOS MCP",
    version="2.0.0",
    website_url="https://arifosmcp.arif-fazil.com",
    instructions="""Constitutional AI orchestration kernel.

Golden path: init → sense → mind → heart → judge → vault

Public tools are derived from tool_specs.py and exposed with canonical dotted ids.
Internal tools: sense, mind, heart, ops, memory, vault, forge

Use prompts for structured workflows:
- constitutional.analysis: Full pipeline
- governance.audit: Compliance review
- execution.planning: Costed execution
- minimal.response: Direct answer
- reply_protocol_v3: AGI Reply Protocol v3 — governed dual-axis reply

Use arifos.reply for deterministic governed reply (composite orchestrator).
Schema: arifos://reply/schemas | Context: arifos://reply/context-pack
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
v2_routes_registered = register_rest_routes(mcp, CANONICAL_TOOL_HANDLERS)

# PromptsAsTools — expose prompts as callable tools for tool-only MCP clients
# (clients that support tools but not the MCP prompts protocol natively)
try:
    from fastmcp.server.transforms import prompts_as_tools
    mcp.add_transform(prompts_as_tools())
    logger.info("PromptsAsTools transform registered — reply_protocol_v3 available as tool")
except Exception as _pat_err:  # noqa: BLE001
    logger.warning(f"PromptsAsTools unavailable (non-critical): {_pat_err}")

# ═══════════════════════════════════════════════════════════════════════════════
# BOOT-TIME INTEGRITY CHECK — Fail-Fast Constitutional Gate
# ═══════════════════════════════════════════════════════════════════════════════

def _perform_boot_integrity_check() -> None:
    """
    Constitutional invariant: If governance-critical ontology is missing,
    the kernel is not allowed to exist in a serving state.
    """
    from arifosmcp.runtime.integrity import (
        perform_boot_integrity_check,
        set_boot_report,
        BootIntegrityError,
    )
    from arifosmcp.runtime.contracts import (
        AAA_TOOL_STAGE_MAP,
        TRINITY_BY_TOOL,
        AAA_TOOL_LAW_BINDINGS,
    )
    from arifosmcp.runtime.tool_specs import TOOLS, TOOL_NAMES, normalize_tool_name
    
    # Normalize tool names: arifos.init -> arifos_init for integrity check compatibility
    def _normalize_tool_name(name: str) -> str:
        return name.replace(".", "_")
    
    tool_registry: dict[str, dict[str, Any]] = {}
    for tool in TOOLS:
        normalized_name = _normalize_tool_name(tool.name)
        tool_registry[normalized_name] = {
            "name": normalized_name,
            "stage": tool.stage,
            "lane": tool.trinity,
            "floors": tool.floors,
        }
    
    router_visible_tools = {
        name for name in tool_registry.keys()
        if not name.startswith("arifos_vps_") and name != "arifos_route"
    }
    
    registered_endpoints = {
        "/health",
        "/tools",
        "/kernel/health",
        "/kernel/health/integrity",
        "/.well-known/mcp/server.json",
        "/version",
        "/openapi.json",
    }
    
    report = perform_boot_integrity_check(
        tool_registry=tool_registry,
        stage_map=AAA_TOOL_STAGE_MAP,
        trinity_map=TRINITY_BY_TOOL,
        law_bindings=AAA_TOOL_LAW_BINDINGS,
        router_visible_tools=router_visible_tools,
        policy_version=get_build_info().get("version", "2026.04.07"),
        protocol_version=get_build_info().get("protocol_version", "2025-03-26"),
        registered_endpoints=registered_endpoints,
        entropy_guard_active=True,
    )
    
    set_boot_report(report)
    
    if report.boot_state == "VOID":
        logger.critical("❌ BOOT INTEGRITY VOID — Kernel aborting startup")
        logger.critical(f"Failed checks: {report.failed_checks}")
        raise BootIntegrityError(
            f"Constitutional boot check failed: {report.error_message}"
        )
    
    logger.info(f"✅ BOOT INTEGRITY SEALED — arifOS Kernel ready")

try:
    _perform_boot_integrity_check()
except Exception as e:
    logger.critical(f"FATAL: Boot integrity check failed: {e}")
    sys.exit(1)

logger.info(
    f"ARIFOS MCP v2 initialized: {len(v2_tools_registered)} tools, "
    f"{len(v2_prompts_registered)} prompts, {len(v2_resources_registered)} resources"
)

# ═══════════════════════════════════════════════════════════════════════════════
# REST TOOL EXECUTION ENDPOINT (Horizon Gateway Compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

# Horizon → v2 tool name mapping (for REST proxy compatibility)
# CORRECTED per EPOCH-NOW audit: arifos.route -> arifos.kernel (unified rCore)
# NOTE: Uses underscore format to match integrity check (arifos_init not arifos.init)
HORIZON_TO_V2_MAP: dict[str, str] = {
    "init_anchor": "arifos_init",
    "arifOS_kernel": "arifos_kernel",
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
    "arifos_route": "arifos_kernel",
    "arifos_kernel": "arifos_kernel",
    "arifos_sense": "arifos_sense",
    "arifos_mind": "arifos_mind",
    "arifos_heart": "arifos_heart",
    "arifos_ops": "arifos_ops",
    "arifos_judge": "arifos_judge",
    "arifos_memory": "arifos_memory",
    "arifos_vault": "arifos_vault",
    "arifos_forge": "arifos_forge",
    "arifos_vps_monitor": "arifos.vps_monitor",
    "arifos_reply": "arifos_reply",
}


def _serialize_rest_tool_result(
    result: Any,
    *,
    verbose: bool = False,
    debug: bool = False,
) -> Any:
    """Serialize tool results through the shared human-language formatter when possible."""
    from arifosmcp.runtime.models import RuntimeEnvelope
    from arifosmcp.runtime.output_formatter import format_output

    if isinstance(result, RuntimeEnvelope):
        result.platform_context = "api"
        return format_output(result, {"verbose": verbose, "debug": debug})

    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "__dict__"):
        return dict(result.__dict__)
    return result


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

    # Get handler (dynamic import to ensure we have the latest v2 dotted keys)
    from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS
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
    verbose = body.pop("verbose", False)
    debug = body.pop("debug", False)

    try:
        # Call handler
        result = await handler(
            session_id=session_id,
            risk_tier=risk_tier,
            dry_run=dry_run,
            debug=debug,
            **body,
        )

        response_data = _serialize_rest_tool_result(
            result,
            verbose=verbose,
            debug=debug,
        )

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
# HTTP APP SETUP — DUAL TRANSPORT (HTTP + SSE)
# ═══════════════════════════════════════════════════════════════════════════════

# Create HTTP app (stateless for /mcp streamable-http)
if IS_FASTMCP_3:
    app = mcp.http_app(stateless_http=False)
elif IS_FASTMCP_2:
    try:
        app = mcp.streamable_http_app()
    except AttributeError:
        app = mcp._mcp_server.app
else:
    raise RuntimeError(f"Unsupported FastMCP version: {fastmcp.__version__}")

# Create SSE app for /sse endpoint (A2A Agent-to-Agent)
if IS_FASTMCP_3:
    sse_app = mcp.http_app(transport="sse", path="/sse", stateless_http=False)
elif IS_FASTMCP_2:
    try:
        sse_app = mcp.streamable_http_app()
    except AttributeError:
        sse_app = mcp._mcp_server.app
else:
    raise RuntimeError(f"Unsupported FastMCP version: {fastmcp.__version__}")

# Shared middleware for both apps
def _add_shared_middleware(target_app: Any) -> None:
    target_app.add_middleware(GlobalPanicMiddleware)
    target_app.add_middleware(SSEKeepAliveMiddleware)
    target_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["X-API-Key", "Content-Type", "Authorization", "X-MCP-Protocol"],
    )

_add_shared_middleware(app)
_add_shared_middleware(sse_app)

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
            "version": build["version"],
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


# Static file handlers
async def llms_txt_handler(request: Request) -> Response:
    """Serve llms.txt for LLM/agent discovery."""
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "llms.txt")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return Response(content=content, media_type="text/plain")
    return Response("LLMs.txt not found", status_code=404)


async def humans_txt_handler(request: Request) -> Response:
    """Serve humans.txt for human sovereign info."""
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "humans.txt")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return Response(content=content, media_type="text/plain")
    return Response("Humans.txt not found", status_code=404)


async def mcp_web_ready_audit_handler(request: Request) -> Response:
    """Serve the MCP Web Ready Audit report."""
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "MCP_WEB_READY_AUDIT.md")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return Response(content=content, media_type="text/markdown")
    return Response("Audit report not found", status_code=404)


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
            },
        }
    )


async def tools_handler(request: Request) -> JSONResponse:
    """Tool catalog endpoint for discovery."""
    from arifosmcp.runtime.contracts import AAA_TOOL_STAGE_MAP, TRINITY_BY_TOOL
    
    # Get full tool objects from FastMCP
    tools = await mcp.list_tools()
    
    enriched_tools = []
    for t in tools:
        t_dict = t.dict() if hasattr(t, "dict") else t
        c_name = t.name.replace("_", ".") if "_" in t.name else t.name
        t_dict["stage"] = AAA_TOOL_STAGE_MAP.get(c_name) or AAA_TOOL_STAGE_MAP.get(t.name.replace(".", "_"))
        t_dict["lane"] = TRINITY_BY_TOOL.get(c_name) or TRINITY_BY_TOOL.get(t.name.replace(".", "_"))
        enriched_tools.append(t_dict)

    return JSONResponse(
        {
            "count": len(enriched_tools),
            "tools": enriched_tools,
            "version": "2.0.0",
            "motto": "DITEMPA, BUKAN DIBERI.",
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER ALL ROUTES — DUAL TRANSPORT
# ═══════════════════════════════════════════════════════════════════════════════

# Shared route handlers (already defined above)
ROUTE_HANDLERS = [
    ("/", landing_page_handler, ["GET"]),
    ("/health", health_handler, ["GET", "OPTIONS"]),
    ("/version", version_handler, ["GET"]),
    ("/tools", tools_handler, ["GET"]),
    ("/tools/{tool_name}", rest_tool_handler, ["POST"]),
    ("/llms.txt", llms_txt_handler, ["GET"]),
    ("/humans.txt", humans_txt_handler, ["GET"]),
    ("/MCP_WEB_READY_AUDIT.md", mcp_web_ready_audit_handler, ["GET"]),
    ("/.well-known/mcp", manifest_handler, ["GET"]),
    ("/.well-known/mcp/server.json", manifest_handler, ["GET"]),
]

for path, handler, methods in ROUTE_HANDLERS:
    app.add_route(path, handler, methods=methods)
    sse_app.add_route(path, handler, methods=methods)


if __name__ == "__main__":
    import asyncio
    import uvicorn

    async def run_dual_transport():
        """Run both HTTP (streamable-http on 8080) and SSE (on 8089) transports."""
        http_config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=8080,
            timeout_graceful_shutdown=2,
            lifespan="on",
            ws="websockets-sansio",
            log_level="info",
        )
        sse_config = uvicorn.Config(
            sse_app,
            host="0.0.0.0",
            port=8089,
            timeout_graceful_shutdown=2,
            lifespan="on",
            ws="websockets-sansio",
            log_level="info",
        )

        http_server = uvicorn.Server(http_config)
        sse_server = uvicorn.Server(sse_config)

        logger.info("=" * 60)
        logger.info("ARIFOS MCP v2 — DUAL TRANSPORT SEALED")
        logger.info("  HTTP (streamable-http): http://0.0.0.0:8080/mcp")
        logger.info("  SSE (A2A agents):       http://0.0.0.0:8089/sse")
        logger.info("=" * 60)

        async with asyncio.TaskGroup() as tg:
            tg.create_task(http_server.serve())
            tg.create_task(sse_server.serve())

    asyncio.run(run_dual_transport())
