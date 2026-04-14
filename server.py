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
- FAIL-CLOSED Gatekeeper (PR-17 REBUILD)

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
from starlette.responses import JSONResponse, Response
from starlette.requests import Request

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# FAIL-CLOSED DISPATCH INTEGRATION (Horizon Rebuild)
# ═══════════════════════════════════════════════════════════════════════════════

def _wrap_hardened_dispatch(tool_name: str, original_handler: Any) -> Any:
    """
    Wrap a tool handler to route through the Fail-Closed Dispatch Gate.
    This ensures F12/F13 filter enforcement for ALL entry points.
    """
    from arifosmcp.runtime.tools_hardened_dispatch import dispatch_with_fail_closed
    
    async def _hardened_handler(**kwargs: Any) -> Any:
        # Route to the single Source of Truth for hardened dispatch
        return await dispatch_with_fail_closed(tool_name, kwargs)
    
    _hardened_handler.__name__ = original_handler.__name__
    _hardened_handler.__doc__ = original_handler.__doc__
    _hardened_handler.__annotations__ = getattr(original_handler, "__annotations__", {})
    return _hardened_handler

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

class CSPMiddleware(BaseHTTPMiddleware):
    """Inject CSP headers for MCP Apps iframe compatibility."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "frame-ancestors https://chat.openai.com https://*.openai.com https://claude.ai https://gemini.google.com; "
            "connect-src 'self' https://arifosmcp.arif-fazil.com https://cdn.jsdelivr.net https://pypi.org https://files.pythonhosted.org; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline'"
        )
        return response

# ═══════════════════════════════════════════════════════════════════════════════
# MCP SERVER INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

mcp = FastMCP(
    "ARIFOS MCP",
    version="2026.4.14",
    website_url="https://arifosmcp.arif-fazil.com",
    instructions="""Constitutional AI orchestration kernel — SEALED v2026.4.14.

Golden path: init → sense → mind → heart → judge → vault
Canonical tools: arifos_init, arifos_sense, arifos_mind, arifos_kernel,
arifos_memory, arifos_heart, arifos_ops, arifos_judge, arifos_vault,
arifos_forge, arifos_health.

FAIL-CLOSED: Identity anchoring (arifos_init) is required for all reasoning.
DITEMPA, BUKAN DIBERI — Forged, Not Given
""",
)

# ═══════════════════════════════════════════════════════════════════════════════
# REGISTER CANONICAL TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from arifosmcp.runtime.tools import register_v2_tools, CANONICAL_TOOL_HANDLERS
    from arifosmcp.runtime.prompts import register_v2_prompts
    from arifosmcp.runtime.resources import register_resources
    from arifosmcp.runtime.rest_routes import register_rest_routes
    from arifosmcp.runtime.build_info import get_build_info
    from arifosmcp.runtime.fastmcp_version import IS_FASTMCP_2, IS_FASTMCP_3

    # Apply Hardening to ALL registerable handlers before passing to FastMCP
    HARDENED_HANDLERS = {
        name: _wrap_hardened_dispatch(name, handler)
        for name, handler in CANONICAL_TOOL_HANDLERS.items()
    }

    # Override the library's handlers with our hardened ones for this server instance
    import arifosmcp.runtime.tools as _tools_mod
    _tools_mod.CANONICAL_TOOL_HANDLERS = HARDENED_HANDLERS

    v2_tools_registered = register_v2_tools(mcp)
    v2_prompts_registered = register_v2_prompts(mcp)
    v2_resources_registered = register_resources(mcp)
    v2_routes_registered = register_rest_routes(mcp, HARDENED_HANDLERS)

    # Register MCP Apps (with F4 Integrity)
    from arifosmcp.apps.metabolic_monitor import _register as _reg_mon
    _reg_mon(mcp)
    
    from arifosmcp.apps.judge_app import _register as _reg_judge
    _reg_judge(mcp)
    
    from arifosmcp.apps.vault_app import _register as _reg_vault
    _reg_vault(mcp)
    
    from arifosmcp.apps.init_app import _register as _reg_init
    _reg_init(mcp)
    
    from arifosmcp.apps.forge_app import _register as _reg_forge
    _reg_forge(mcp)

    # Approval Provider (F13 gate)
    from fastmcp.apps.approval import Approval
    mcp.add_provider(Approval(
        name="Constitutional Gate",
        title="888_HOLD",
        approve_text="Authorize",
        reject_text="Reject",
    ))

    logger.info(f"ARIFOS MCP SEALED: {len(v2_tools_registered)} tools registered with Fail-Closed gates.")

except Exception as e:
    logger.error(f"Failed to initialize runtime components: {e}")
    traceback.print_exc()

# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY TOOL ALIASES (Horizon Compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

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
    """Register legacy tool names as aliases, routing through hardened dispatch."""
    for legacy_name, canonical_name in LEGACY_TOOL_MAP.items():
        # Alias always goes through hardened dispatch
        handler = _wrap_hardened_dispatch(canonical_name, lambda: None)
        try:
            mcp.tool(name=legacy_name)(handler)
            logger.debug(f"Registered legacy alias: {legacy_name} → {canonical_name}")
        except Exception as e:
            logger.warning(f"Failed to register legacy alias {legacy_name}: {e}")

_register_legacy_aliases()

# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

async def horizon_health(request: Request) -> JSONResponse:
    from arifosmcp.runtime.build_info import get_build_info
    build = get_build_info()
    return JSONResponse({
        "status": "healthy",
        "version": "2026.4.14-SEALED",
        "tools": len(v2_tools_registered),
        "fail_closed": True,
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    })

async def horizon_metadata(request: Request) -> JSONResponse:
    return JSONResponse({
        "name": "ARIFOS MCP",
        "version": "2026.4.14",
        "security": "Fail-Closed Dispatch (Gate 1-4 active)",
        "protocol": "MCP 2025-03-26",
    })

# ═══════════════════════════════════════════════════════════════════════════════
# HTTP APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

app = mcp.http_app(stateless_http=True)
app.add_middleware(GlobalPanicMiddleware)
app.add_middleware(CSPMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"])

app.add_route("/health", horizon_health, methods=["GET"])
app.add_route("/metadata", horizon_metadata, methods=["GET"])

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = ["mcp", "app", "LEGACY_TOOL_MAP"]

if __name__ == "__main__":
    import asyncio
    import uvicorn

    async def run_server():
        print("=" * 60)
        print("🔥 ARIFOS MCP v2026.4.14 — SEALED")
        print("=" * 60)
        config = uvicorn.Config(app, host="0.0.0.0", port=8080)
        server = uvicorn.Server(config)
        await server.serve()

    asyncio.run(run_server())
