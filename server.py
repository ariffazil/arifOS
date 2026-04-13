"""
arifOS MCP Server — Unified Entry Point
═══════════════════════════════════════════════════════════════════════════════

Single canonical server for ALL arifOS deployments:
- VPS sovereign execution (full F1-F13 floors)
- Horizon gateway/proxy mode (public tools + VPS proxy)
- Local development
- A2A Agent-to-Agent protocol
- WebMCP web-facing gateway

Features:
- 17 canonical tools (arifos_init, arifos_sense, etc.)
- 10 legacy tool aliases (init_anchor, apex_soul, etc.)
- Gateway metadata endpoints (/metadata, /health)
- VPS proxy capability for sovereign tools
- Constitutional governance (F1-F13)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
import sys
import traceback
from typing import Any, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════════════════════════

_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv
_env_path = os.path.join(_project_root, ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path, override=True)
os.environ["PYDANTIC_SETTINGS_DOTENV_FILES"] = ""

# ═══════════════════════════════════════════════════════════════════════════════
# FASTMCP IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════

import fastmcp
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response, HTMLResponse
from starlette.requests import Request

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

Canonical tools: arifos_init, arifos_sense, arifos_mind, arifos_route,
arifos_memory, arifos_heart, arifos_ops, arifos_judge, arifos_vault,
arifos_forge, arifos_health, arifos_reply, arifos_fetch, etc.

Legacy aliases: init_anchor, apex_soul, agi_mind, asi_heart,
physics_reality, math_estimator, architect_registry, vault_ledger,
engineering_memory, code_engine

DITEMPA, BUKAN DIBERI — Forged, Not Given
""",
)


def create_aaa_mcp_server() -> FastMCP:
    """Factory for arifOS MCP Server."""
    return mcp


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER CANONICAL TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

# Default version flags to prevent NameError in case of import failure
IS_FASTMCP_2 = False
IS_FASTMCP_3 = False
v2_tools_registered = []
v2_prompts_registered = []
v2_resources_registered = []
CANONICAL_TOOL_HANDLERS = {}

try:
    from arifosmcp.runtime.tools import register_v2_tools, CANONICAL_TOOL_HANDLERS
    from arifosmcp.runtime.prompts import register_v2_prompts
    from arifosmcp.runtime.resources import register_v2_resources
    from arifosmcp.runtime.rest_routes import register_rest_routes
    from arifosmcp.runtime.build_info import get_build_info
    from arifosmcp.runtime.fastmcp_version import IS_FASTMCP_2, IS_FASTMCP_3

    v2_tools_registered = register_v2_tools(mcp)
    v2_prompts_registered = register_v2_prompts(mcp)
    v2_resources_registered = register_v2_resources(mcp)
    v2_routes_registered = register_rest_routes(mcp, CANONICAL_TOOL_HANDLERS)

    try:
        from fastmcp.server.transforms import prompts_as_tools
        mcp.add_transform(prompts_as_tools())
        logger.info("PromptsAsTools transform registered")
    except Exception as _pat_err:
        logger.warning(f"PromptsAsTools unavailable: {_pat_err}")

    logger.info(
        f"ARIFOS MCP v2: {len(v2_tools_registered)} tools, "
        f"{len(v2_prompts_registered)} prompts, {len(v2_resources_registered)} resources"
    )

except Exception as e:
    logger.error(f"Failed to initialize runtime components: {e}")
    v2_tools_registered = []
    v2_prompts_registered = []
    v2_resources_registered = []


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY TOOL ALIASES (Horizon Compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

# Legacy → Canonical tool name mapping
LEGACY_TOOL_MAP: dict[str, str] = {
    "init_anchor": "arifos_init",
    "apex_soul": "arifos_judge",
    "agi_mind": "arifos_mind",
    "asi_heart": "arifos_heart",
    "physics_reality": "arifos_sense",
    "math_estimator": "arifos_ops",
    "architect_registry": "arifos_init",
    "vault_ledger": "arifos_vault",
    "engineering_memory": "arifos_memory",
    "code_engine": "arifos_forge",
    "arifOS_kernel": "arifos_kernel",
}


def _register_legacy_aliases():
    """Register legacy tool names as aliases to canonical tools."""
    for legacy_name, canonical_name in LEGACY_TOOL_MAP.items():
        if canonical_name in CANONICAL_TOOL_HANDLERS:
            handler = CANONICAL_TOOL_HANDLERS[canonical_name]
            try:
                # Register with legacy name
                mcp.tool(name=legacy_name)(handler)
                logger.debug(f"Registered legacy alias: {legacy_name} → {canonical_name}")
            except Exception as e:
                logger.warning(f"Failed to register legacy alias {legacy_name}: {e}")


# Register legacy aliases
try:
    _register_legacy_aliases()
    logger.info(f"Registered {len(LEGACY_TOOL_MAP)} legacy tool aliases")
except Exception as e:
    logger.warning(f"Legacy alias registration skipped: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY ENDPOINTS (Horizon Compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

async def _build_gateway_metadata() -> dict:
    """Build gateway metadata for /metadata endpoint."""
    from arifosmcp.runtime.build_info import get_build_info
    
    build = get_build_info()
    
    # Tool access classification
    public_tools = [
        "arifos_init", "arifos_sense", "arifos_mind", "arifos_route",
        "arifos_ops", "arifos_memory", "arifos_health"
    ]
    authenticated_tools = ["arifos_heart", "arifos_judge", "arifos_vault"]
    sovereign_tools = ["arifos_forge"]
    
    return {
        "name": "ARIFOS MCP",
        "version": build.get("version", "2.0.0"),
        "protocol": "MCP 2025-03-26",
        "gateway": {
            "type": "unified",
            "capabilities": ["tools", "prompts", "resources"],
            "tool_access": {
                "public": public_tools,
                "authenticated": authenticated_tools,
                "sovereign_only": sovereign_tools,
            }
        },
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "metadata": "/metadata",
            "tools": "/tools",
        },
        "motto": "DITEMPA, BUKAN DIBERI — Forged, Not Given",
    }


async def horizon_health(request: Request) -> JSONResponse:
    """Health check with gateway status."""
    from arifosmcp.runtime.build_info import get_build_info
    
    build = get_build_info()
    
    return JSONResponse({
        "status": "healthy",
        "service": "arifos-mcp-unified",
        "version": build.get("version", "2.0.0"),
        "gateway": "unified",
        "tools": len(v2_tools_registered),
        "prompts": len(v2_prompts_registered),
        "resources": len(v2_resources_registered),
        "legacy_aliases": len(LEGACY_TOOL_MAP),
        "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
    })


async def horizon_metadata(request: Request) -> JSONResponse:
    """Gateway metadata endpoint."""
    metadata = await _build_gateway_metadata()
    return JSONResponse(metadata)


async def serve_humans_txt(request: Request) -> Response:
    """Serve humans.txt for sovereign info."""
    content = """/* TEAM */
Sovereign: Arif Fazil
Contact: arif@arif-fazil.com
Site: https://arif-fazil.com

/* THANKS */
All contributors to the arifOS project

/* SITE */
Standards: MCP, FastMCP, Constitutional AI
Components: FastAPI, Starlette, Pydantic

DITEMPA, BUKAN DIBERI — Forged, Not Given
"""
    return Response(content=content, media_type="text/plain")


# ═══════════════════════════════════════════════════════════════════════════════
# BOOT-TIME INTEGRITY CHECK
# ═══════════════════════════════════════════════════════════════════════════════

try:
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
    from arifosmcp.runtime.tool_specs import TOOLS

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
        "/metadata",
        "/kernel/health",
        "/kernel/health/integrity",
        "/.well-known/mcp/server.json",
        "/version",
        "/openapi.json",
        "/humans.txt",
    }

    report = perform_boot_integrity_check(
        tool_registry=tool_registry,
        stage_map=AAA_TOOL_STAGE_MAP,
        trinity_map=TRINITY_BY_TOOL,
        law_bindings=AAA_TOOL_LAW_BINDINGS,
        router_visible_tools=router_visible_tools,
        policy_version=get_build_info().get("version", "2026.04.11"),
        protocol_version=get_build_info().get("protocol_version", "2025-03-26"),
        registered_endpoints=registered_endpoints,
        entropy_guard_active=True,
    )

    set_boot_report(report)

    if report.boot_state == "VOID":
        logger.critical("❌ BOOT INTEGRITY VOID — Kernel aborting startup")
        raise BootIntegrityError(f"Constitutional boot check failed: {report.error_message}")

    logger.info("✅ BOOT INTEGRITY SEALED — arifOS Kernel ready")

except Exception as e:
    logger.warning(f"Boot integrity check skipped: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP APP SETUP
from fastapi import FastAPI
app = FastAPI()
# ═══════════════════════════════════════════════════════════════════════════════

# Initialize fallback app early
from fastapi import FastAPI
app = FastAPI()

try:
    if IS_FASTMCP_3:
        # Use stateless HTTP for ChatGPT compatibility
        # ChatGPT doesn't properly negotiate SSE, so stateless mode works better
        app = mcp.http_app(stateless_http=True)
    elif IS_FASTMCP_2:
        try:
            app = mcp.streamable_http_app()
        except AttributeError:
            app = mcp._mcp_server.app
    else:
        # Already initialized above
        pass

    # Add middleware
    app.add_middleware(GlobalPanicMiddleware)
    app.add_middleware(SSEKeepAliveMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["X-API-Key", "Content-Type", "Authorization", "X-MCP-Protocol"],
    )

    # Add gateway endpoints
    if app:
        app.add_route("/health", horizon_health, methods=["GET"])
        app.add_route("/metadata", horizon_metadata, methods=["GET"])
        app.add_route("/humans.txt", serve_humans_txt, methods=["GET"])

except Exception as e:
    logger.error(f"Failed to setup HTTP app: {e}")
    # app = None


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = ["mcp", "create_aaa_mcp_server", "app", "LEGACY_TOOL_MAP"]


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import asyncio
    import uvicorn

    async def run_server():
        """Run the unified MCP server."""
        print("=" * 60)
        print("🔥 ARIFOS MCP v2 — UNIFIED SERVER")
        print("=" * 60)
        print(f"   Server: {mcp.name}")
        print(f"   Version: {mcp.version}")
        print(f"   Tools: {len(v2_tools_registered)}")
        print(f"   Legacy Aliases: {len(LEGACY_TOOL_MAP)}")
        print(f"   Prompts: {len(v2_prompts_registered)}")
        print(f"   Resources: {len(v2_resources_registered)}")
        print("=" * 60)

        if app:
            config = uvicorn.Config(
                app,
                host="0.0.0.0",
                port=8080,
                timeout_graceful_shutdown=2,
                lifespan="on",
                ws="websockets-sansio",
                log_level="info",
            )
            server = uvicorn.Server(config)
            await server.serve()
        else:
            print("❌ HTTP app not available")
            sys.exit(1)

    asyncio.run(run_server())
