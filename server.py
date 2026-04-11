"""
arifOS MCP Server — Unified Entry Point
═══════════════════════════════════════════════════════════════════════════════

Single canonical server for all arifOS deployments:
- VPS sovereign execution (full F1-F13 floors)
- Horizon gateway/proxy mode
- Local development
- A2A Agent-to-Agent protocol
- WebMCP web-facing gateway

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
import sys
import traceback
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════════════════════════

# Ensure project root is in path
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Load .env early
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

Public tools: arifos_init, arifos_sense, arifos_mind, arifos_route, 
arifos_memory, arifos_heart, arifos_ops, arifos_judge, arifos_vault, 
arifos_forge, arifos_vps_monitor, arifos_reply

Use prompts for structured workflows:
- constitutional.analysis: Full pipeline
- governance.audit: Compliance review
- execution.planning: Costed execution
- minimal.response: Direct answer
- reply_protocol_v3: AGI Reply Protocol v3

DITEMPA, BUKAN DIBERI — Forged, Not Given
""",
)


def create_aaa_mcp_server() -> FastMCP:
    """Factory for arifOS MCP Server (AAA = Aligned, Autonomous, Audit-able)."""
    return mcp


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER TOOLS, PROMPTS, RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from arifosmcp.runtime.tools import register_v2_tools, CANONICAL_TOOL_HANDLERS
    from arifosmcp.runtime.prompts import register_v2_prompts
    from arifosmcp.runtime.resources import register_v2_resources
    from arifosmcp.runtime.rest_routes import register_rest_routes
    from arifosmcp.runtime.build_info import get_build_info
    from arifosmcp.runtime.fastmcp_version import IS_FASTMCP_2, IS_FASTMCP_3

    # Register v2 components
    v2_tools_registered = register_v2_tools(mcp)
    v2_prompts_registered = register_v2_prompts(mcp)
    v2_resources_registered = register_v2_resources(mcp)
    v2_routes_registered = register_rest_routes(mcp, CANONICAL_TOOL_HANDLERS)

    # PromptsAsTools
    try:
        from fastmcp.server.transforms import prompts_as_tools
        mcp.add_transform(prompts_as_tools())
        logger.info("PromptsAsTools transform registered")
    except Exception as _pat_err:
        logger.warning(f"PromptsAsTools unavailable: {_pat_err}")

    logger.info(
        f"ARIFOS MCP v2 initialized: {len(v2_tools_registered)} tools, "
        f"{len(v2_prompts_registered)} prompts, {len(v2_resources_registered)} resources"
    )

except Exception as e:
    logger.error(f"Failed to initialize runtime components: {e}")
    v2_tools_registered = []
    v2_prompts_registered = []
    v2_resources_registered = []


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
    from arifosmcp.runtime.build_info import get_build_info

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
        raise BootIntegrityError(f"Constitutional boot check failed: {report.error_message}")

    logger.info("✅ BOOT INTEGRITY SEALED — arifOS Kernel ready")

except Exception as e:
    logger.warning(f"Boot integrity check skipped: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

try:
    if IS_FASTMCP_3:
        app = mcp.http_app(stateless_http=False)
    elif IS_FASTMCP_2:
        try:
            app = mcp.streamable_http_app()
        except AttributeError:
            app = mcp._mcp_server.app
    else:
        from fastapi import FastAPI
        app = FastAPI()

    # Add middleware
    app.add_middleware(GlobalPanicMiddleware)
    app.add_middleware(SSEKeepAliveMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["X-API-Key", "Content-Type", "Authorization", "X-MCP-Protocol"],
    )

except Exception as e:
    logger.error(f"Failed to setup HTTP app: {e}")
    app = None


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = ["mcp", "create_aaa_mcp_server", "app"]


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
