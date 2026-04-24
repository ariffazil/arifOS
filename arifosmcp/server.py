"""
arifOS MCP Server — Canonical Entry Point
═══════════════════════════════════════════

13-tool canonical surface | 13 Floors (F1–F13) | Trinity ΔΩΨ
FastMCP 3.2.0 + MCP Apps + Streamable HTTP
DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

import logging
import os
import sys
import traceback
from typing import Any

# Ensure project root is on path
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(_project_root), ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path, override=True)

import fastmcp
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response
from starlette.requests import Request

from arifosmcp.constitutional_map import (
    CANONICAL_TOOLS,
    list_authenticated_tools,
    list_canonical_tools,
    list_public_tools,
    list_sovereign_tools,
)

logger = logging.getLogger(__name__)

_canonical_tool_names = list_canonical_tools()
_canonical_tool_names_text = ", ".join(_canonical_tool_names)


class GlobalPanicMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            print(f"!!! KERNEL PANIC: {e}", file=sys.stderr)
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


mcp = FastMCP(
    "ARIFOS MCP",
    version="2026.04.24-KANON",
    website_url="https://arifosmcp.arif-fazil.com",
    instructions=(
        "Constitutional AI orchestration kernel — arifOS.\n\n"
        "Golden path: init → sense → mind → heart → judge → vault\n\n"
        f"Canonical 13 tools (arif_noun_verb):\n  {_canonical_tool_names_text}\n\n"
        "DITEMPA BUKAN DIBERI — Forged, Not Given"
    ),
)

_engineering_lock_path = os.path.join(os.path.dirname(_project_root), ".ENGINEERING_LOCK")
if not os.path.exists(_engineering_lock_path):
    logger.warning("Engineering lock missing at startup: %s", _engineering_lock_path)


def create_arifos_mcp_server() -> FastMCP:
    return mcp


def _assert_registered_surface(registered_names: list[str]) -> None:
    registered_set = set(registered_names)
    expected_set = set(CANONICAL_TOOLS)

    if len(registered_names) != len(expected_set):
        raise RuntimeError(
            f"Surface drift detected: expected {len(expected_set)} tools, got {len(registered_names)}"
        )

    if any(name.startswith("arifos_") for name in registered_names):
        raise RuntimeError("Legacy surface detected in registered MCP tools")

    if registered_set != expected_set:
        missing = sorted(expected_set - registered_set)
        extra = sorted(registered_set - expected_set)
        raise RuntimeError(
            f"Ontology mismatch detected: missing={missing or '[]'} extra={extra or '[]'}"
        )


v2_tools_registered: list[str] = []
v2_prompts_registered: list[str] = []
v2_resources_registered: list[str] = []
v2_apps_registered: list[str] = []

IS_FASTMCP_3 = fastmcp.__version__.startswith("3")

try:
    from arifosmcp.runtime.tools import register_tools
    from arifosmcp.prompts import CANONICAL_PROMPTS, register_prompts
    from arifosmcp.resources import CANONICAL_RESOURCES, register_resources

    v2_tools_registered = register_tools(mcp)
    _assert_registered_surface(v2_tools_registered)
    v2_prompts_registered = register_prompts(mcp)
    if tuple(v2_prompts_registered) != CANONICAL_PROMPTS:
        raise RuntimeError(
            f"Prompt drift detected: expected {list(CANONICAL_PROMPTS)}, got {v2_prompts_registered}"
        )
    v2_resources_registered = register_resources(mcp)
    if tuple(v2_resources_registered) != CANONICAL_RESOURCES:
        raise RuntimeError(
            "Resource drift detected: "
            f"expected {list(CANONICAL_RESOURCES)}, got {v2_resources_registered}"
        )
    logger.info(
        f"ARIFOS MCP KANON Phase 1: {len(v2_tools_registered)} tools, "
        f"{len(v2_prompts_registered)} prompts, {len(v2_resources_registered)} resources"
    )
except Exception as e:
    logger.error(f"Failed to initialize runtime components: {e}")
    raise


PUBLIC_TOOLS = list_public_tools()
AUTHENTICATED_TOOLS = list_authenticated_tools()
SOVEREIGN_TOOLS = list_sovereign_tools()


async def horizon_health(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "status": "healthy",
            "service": "arifos-mcp-kanon",
            "version": "2026.04.24-KANON",
            "gateway": "unified",
            "tools": len(v2_tools_registered),
            "prompts": len(v2_prompts_registered),
            "resources": len(v2_resources_registered),
            "apps": len(v2_apps_registered),
            "canonical_surface": 13,
            "timestamp": __import__("datetime")
            .datetime.now(__import__("datetime").timezone.utc)
            .isoformat(),
        }
    )


async def horizon_metadata(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "name": "ARIFOS MCP",
            "version": "2026.04.24-KANON",
            "protocol": "MCP 2025-03-26",
            "gateway": {
                "type": "unified",
                "capabilities": ["tools", "prompts", "resources", "apps"],
                "tool_access": {
                    "public": PUBLIC_TOOLS,
                    "authenticated": AUTHENTICATED_TOOLS,
                    "sovereign_only": SOVEREIGN_TOOLS,
                },
            },
            "endpoints": {
                "mcp": "/mcp",
                "health": "/health",
                "metadata": "/metadata",
                "tools": "/tools",
            },
            "motto": "DITEMPA BUKAN DIBERI — Forged, Not Given",
        }
    )


async def serve_humans_txt(request: Request) -> Response:
    content = (
        "/* TEAM */\n"
        "Sovereign: Arif Fazil\n"
        "Contact: arif@arif-fazil.com\n"
        "Site: https://arif-fazil.com\n\n"
        "/* THANKS */\n"
        "All contributors to the arifOS project\n\n"
        "/* SITE */\n"
        "Standards: MCP, FastMCP, Constitutional AI\n"
        "Components: FastAPI, Starlette, Pydantic\n\n"
        "DITEMPA BUKAN DIBERI — Forged, Not Given\n"
    )
    return Response(content=content, media_type="text/plain")


app: Any = None

try:
    if IS_FASTMCP_3:
        app = mcp.http_app(stateless_http=True)
    else:
        app = mcp._mcp_server.app

    if app is not None:
        app.add_middleware(GlobalPanicMiddleware)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
            allow_headers=["X-API-Key", "Content-Type", "Authorization", "X-MCP-Protocol"],
        )
        app.add_route("/health", horizon_health, methods=["GET"])
        app.add_route("/metadata", horizon_metadata, methods=["GET"])
        app.add_route("/humans.txt", serve_humans_txt, methods=["GET"])
        logger.info("HTTP app configured with gateway endpoints")
    else:
        logger.warning("HTTP app is None")
except Exception as e:
    logger.error(f"Failed to setup HTTP app: {e}")


__all__ = ["mcp", "create_arifos_mcp_server", "app", "v2_tools_registered"]


def main() -> None:
    import asyncio
    import uvicorn

    async def run_server():
        print("=" * 60)
        print("ARIFOS MCP v2026.04.24-KANON — CANONICAL SURFACE")
        print("=" * 60)
        print(f"   Server: {mcp.name}")
        print(f"   Version: {mcp.version}")
        print(f"   Tools: {len(v2_tools_registered)}")
        print(f"   Prompts: {len(v2_prompts_registered)}")
        print(f"   Resources: {len(v2_resources_registered)}")
        print(f"   Apps: {len(v2_apps_registered)}")
        print("=" * 60)

        if app is None:
            print("HTTP app not available — falling back to mcp.run()")
            mcp.run()
            return

        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=int(os.getenv("ARIFOS_PORT", "8080")),
            timeout_graceful_shutdown=2,
            lifespan="on",
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
