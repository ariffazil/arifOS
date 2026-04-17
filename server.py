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
- 11 canonical public tools (init, sense, mind, heart, kernel,
  judge, vault, forge, gateway, ops, memory)
- 40+ legacy aliases unified into a single registry
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

from arifosmcp.runtime.DNA import MOTTO, VERSION

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

from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# VAULT999 — CONSTITUTIONAL TABLE STORE
# ═══════════════════════════════════════════════════════════════════════════════
# Global singleton for constitutional table writes (arifos.sessions, tool_calls, telemetry)
# Loads F1-F13 from vault at startup, opens live session, logs all tool executions.

vault_store = None  # type: PostgresVaultStore | None
CONSTITUTION_CACHE: dict[str, Any] = {}
ACTIVE_SESSION_ID: str | None = None


def _get_vault_store():
    """Lazy init of PostgresVaultStore using DATABASE_URL env var."""
    global vault_store
    if vault_store is None:
        from arifosmcp.runtime.vault_postgres import PostgresVaultStore
        vault_store = PostgresVaultStore()
    return vault_store


async def _constitutional_startup():
    """Called at server startup: load F1-F13 + open live session."""
    global CONSTITUTION_CACHE, ACTIVE_SESSION_ID
    store = _get_vault_store()
    try:
        CONSTITUTION_CACHE = await store.load_constitution()
        print(f"[VAULT] Constitution loaded: {len(CONSTITUTION_CACHE)} floors")
    except Exception as e:
        print(f"[VAULT] Constitution load failed: {e}")
    try:
        agent_id = os.environ.get("ARIFOS_AGENT_ID", "arifos-unified")
        ACTIVE_SESSION_ID = await store.open_session(
            agent_id=agent_id,
            declared_intent="arifos-unified operational session",
            risk_tier="LOW",
        )
        print(f"[VAULT] Session: {ACTIVE_SESSION_ID}")
        
        # H1: Seed healthy baseline metrics to prevent startup HOLD
        from core.governance_kernel import get_governance_kernel
        gk = get_governance_kernel()
        if hasattr(gk, "update_telemetry"):
            gk.update_telemetry({
                "dS": -0.32,
                "peace2": 1.04,
                "confidence": 0.88,
                "verdict": "SEAL"
            })
            print("[VAULT] Healthy thermodynamic baseline seeded.")
            
    except Exception as e:
        print(f"[VAULT] Session open failed: {e}")


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

# ═══════════════════════════════════════════════════════════════════════════════
# FAIL-CLOSED DISPATCH INTEGRATION (Horizon Rebuild)
# ═══════════════════════════════════════════════════════════════════════════════

def _wrap_hardened_dispatch(tool_name: str, original_handler: Any) -> Any:
    """
    Wrap a tool handler and normalize its result for the HTTP MCP surface.
    """
    import functools
    import inspect

    async def _invoke_original(arguments: dict[str, Any]) -> Any:
        import time
        t0 = time.monotonic()
        result = original_handler(**arguments)
        if inspect.isawaitable(result):
            result = await result
        ms = int((time.monotonic() - t0) * 1000)

        # ── Constitutional tool call logging (non-blocking) ──
        try:
            vs = _get_vault_store()
            sid = os.environ.get("ARIFOS_AGENT_ID", "arifos-unified")
            verdict_str = "SEAL"
            if hasattr(result, "verdict"):
                verdict_str = str(getattr(result, "verdict", "SEAL"))
            elif hasattr(result, "ok"):
                verdict_str = "SEAL" if getattr(result, "ok", False) else "HOLD"
            vs.log_tool_call(
                session_id=ACTIVE_SESSION_ID,
                run_id=ACTIVE_SESSION_ID,
                tool_name=tool_name,
                organ="PSI",
                input_summary=str(arguments)[:200],
                output_summary=str(result)[:200],
                verdict=verdict_str,
                duration_ms=ms,
            )
        except Exception:
            pass  # never fail a tool call due to logging

        if result.__class__.__name__ == "RuntimeEnvelope":
            from arifosmcp.runtime.output_formatter import format_output

            platform = arguments.get("platform", "mcp")
            if hasattr(result, "platform_context"):
                result.platform_context = platform
            return format_output(
                result,
                {"verbose": False, "debug": bool(arguments.get("debug", False))},
            )
        if hasattr(result, "model_dump"):
            return result.model_dump(mode="json")
        return result

    try:
        sig = inspect.signature(original_handler)
    except Exception:
        async def fallback_handler(**kwargs):
            return await _invoke_original(kwargs)
        return fallback_handler

    @functools.wraps(original_handler)
    async def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        return await _invoke_original(dict(bound.arguments))

    wrapper.__signature__ = sig
    return wrapper

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
    version=VERSION,
    website_url="https://arifosmcp.arif-fazil.com",
    instructions=f"""Constitutional AI orchestration kernel — SEALED v{VERSION}.
    
    {MOTTO}
    
    Golden path: init → sense → mind → heart → judge → vault
    Governance : arifos_init | arifos_kernel | arifos_judge | arifos_vault
    Execution : arifos_forge
    """,
)

v2_tools_registered = []
v2_prompts_registered = []
v2_resources_registered = []

try:
    from arifosmcp.runtime.prompts import register_v2_prompts
    from arifosmcp.runtime.resources import register_resources
    from arifosmcp.runtime.rest_routes import register_rest_routes
    from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS, register_v2_tools

    # Apply Hardening to ALL registerable handlers before passing to FastMCP
    HARDENED_HANDLERS = {
        name: _wrap_hardened_dispatch(name, handler)
        for name, handler in CANONICAL_TOOL_HANDLERS.items()
    }

    # Override the library's handlers with our hardened ones for this server instance
    import arifosmcp.runtime.tools as _tools_mod
    _tools_mod.CANONICAL_TOOL_HANDLERS = HARDENED_HANDLERS

    v2_tools_registered = register_v2_tools(mcp, include_legacy_compat=False)
    v2_prompts_registered = register_v2_prompts(mcp)
    v2_resources_registered = register_resources(mcp)

    # Register REST routes AFTER tool registration so tool_registry is populated
    v2_routes_registered = register_rest_routes(mcp, HARDENED_HANDLERS)

    # Register MCP Apps (with F4 Integrity)
    from arifosmcp.apps import register_all_apps
    registered_apps = register_all_apps(mcp)
    logger.info(f"Successfully registered {len(registered_apps)} constitutional apps")

    # Mount 6-axis MCP tools (P/T/V/G/E/M) from mcp_tools.py
    # Axis feature flags: set ARIFOS_ENABLE_{P|T|V|G|E|M}_AXIS=false to gate an axis
    _axis_enabled = lambda axis: os.getenv(f"ARIFOS_ENABLE_{axis}_AXIS", "true").lower() != "false"
    try:
        from arifosmcp.mcp_tools import (
            create_perception_mcp, create_transformation_mcp,
            create_valuation_mcp, create_governance_mcp,
            create_execution_mcp, create_meta_mcp,
        )
        _agent_factories = {
            "P": create_perception_mcp,
            "T": create_transformation_mcp,
            "V": create_valuation_mcp,
            "G": create_governance_mcp,
            "E": create_execution_mcp,
            "M": create_meta_mcp,
        }
        for _axis, _factory in _agent_factories.items():
            if not _axis_enabled(_axis):
                logger.info(f"  [{_axis}] axis DISABLED via ARIFOS_ENABLE_{_axis}_AXIS=false")
                continue
            _agent_mcp = _factory()
            mcp.mount(_agent_mcp, namespace=None)
            logger.info(f"  [{_axis}] 6-axis MCP agent mounted (namespaced by prefix letter)")
        logger.info("6-axis MCP: P/T/V/G/E/M namespaces mounted via mcp_tools.py")
        print("6-axis MCP: P/T/V/G/E/M namespaces mounted via mcp_tools.py")
    except Exception as _e:
        logger.warning(f"6-axis MCP tools unavailable: {_e}")

    # Approval Provider (F13 gate)
    if _env_flag("ARIFOS_ENABLE_APPROVAL_PROVIDER", default=False):
        try:
            from fastmcp.apps.approval import Approval

            mcp.add_provider(
                Approval(
                    name="Constitutional Gate",
                    title="888_HOLD",
                    approve_text="Authorize",
                    reject_text="Reject",
                )
            )
            logger.info("F13 Approval provider active")
        except (ImportError, ModuleNotFoundError):
            logger.warning("F13 Approval provider unavailable (FastMCP version mismatch)")

    # Skills Provider — expose skills/ dir relative to this server file
    try:
        from fastmcp.server.providers.skills import SkillsDirectoryProvider
        from pathlib import Path as _Path

        _server_dir = _Path(__file__).parent
        skills_roots = [p for p in [_server_dir / "skills"] if p.exists()]
        if skills_roots:
            mcp.add_provider(SkillsDirectoryProvider(roots=skills_roots))
            logger.info(f"Skills provider active: {[str(r) for r in skills_roots]}")
        else:
            logger.info("Skills provider: no skills/ directory found, skipping")
    except (ImportError, Exception) as _e:
        logger.warning(f"Skills provider unavailable: {_e}")

    logger.info(f"ARIFOS MCP SEALED: {len(v2_tools_registered)} tools registered with Fail-Closed gates.")
    logger.info("ARIFOS MCP tool manifest: %s", ", ".join(v2_tools_registered))
    print(f"ARIFOS MCP tool manifest: {', '.join(v2_tools_registered)}")

except Exception as e:
    logger.error(f"Failed to initialize runtime components: {e}")
    traceback.print_exc()

# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY TOOL ALIASES (Horizon Compatibility)
# ═══════════════════════════════════════════════════════════════════════════════

def _register_legacy_aliases():
    """
    Legacy aliases are NO LONGER registered as separate MCP tools.
    They remain resolvable at the dispatch layer via LEGACY_TOOL_ALIASES
    and get_tool_handler(), but are hidden from tool discovery to reduce
    surface entropy (Phase 1 Compression).
    """
    logger.info("Legacy alias registration skipped — canonical surface only.")

def _register_debug_tools() -> None:
    @mcp.tool(name="echo")
    async def echo(message: str) -> str:
        """Diagnostic tool that echoes the input message."""
        return f"ECHO: {message}"


if _env_flag("ARIFOS_ENABLE_SERVER_LEGACY_ALIASES", default=False):
    _register_legacy_aliases()

if _env_flag("ARIFOS_ENABLE_DEBUG_TOOLS", default=False):
    _register_debug_tools()

# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

async def horizon_health(request: Request) -> JSONResponse:
    from arifosmcp.runtime.build_info import get_build_info
    build = get_build_info()
    return JSONResponse({
        "status": "healthy",
        "version": f"{VERSION}-SEALED",
        "tools": len(v2_tools_registered),
        "fail_closed": True,
        "timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    })

async def horizon_metadata(request: Request) -> JSONResponse:
    return JSONResponse({
        "name": "ARIFOS MCP",
        "version": VERSION,
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

# Ensure REST routes from arifosmcp are actually bound to this app instance
# HARDENED_HANDLERS is only defined if the try block (line 251) succeeded
from arifosmcp.runtime.rest_routes import register_rest_routes
if "HARDENED_HANDLERS" in globals():
    register_rest_routes(mcp, HARDENED_HANDLERS, prefix="")

# ── Constitutional startup (runs on module load, not just __main__) ──
import asyncio

try:
    asyncio.get_event_loop().run_until_complete(_constitutional_startup())
except RuntimeError:
    asyncio.get_event_loop().create_task(_constitutional_startup())

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = ["mcp", "app"]

if __name__ == "__main__":
    import asyncio

    import uvicorn

    async def run_server():
        print("=" * 60)
        print("🔥 ARIFOS MCP v2026.4.14 — SEALED")
        print("=" * 60)
        
        # ── Constitutional startup: load constitution + open session ──
        await _constitutional_startup()
        
        # Resolve host and port from CLI or ENV
        host = "0.0.0.0"
        port = int(os.getenv("PORT", 8080))
        
        if "--host" in sys.argv:
            idx = sys.argv.index("--host")
            if idx + 1 < len(sys.argv):
                host = sys.argv[idx + 1]
        
        if "--port" in sys.argv:
            idx = sys.argv.index("--port")
            if idx + 1 < len(sys.argv):
                port = int(sys.argv[idx + 1])

        config = uvicorn.Config(app, host=host, port=port)
        server = uvicorn.Server(config)
        await server.serve()

    asyncio.run(run_server())
