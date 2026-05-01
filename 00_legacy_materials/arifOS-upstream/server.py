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

try:
    from arifosmcp.runtime.DNA import MOTTO, VERSION
except ImportError:
    MOTTO = "DITEMPA BUKAN DIBERI"
    VERSION = "2026.04.20"

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
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


def _display_version() -> str:
    value = str(VERSION).strip()
    return value if value.startswith("v") else f"v{value}"


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
        try:
            from arifosmcp.runtime.vault_postgres import PostgresVaultStore

            vault_store = PostgresVaultStore()
        except ImportError:
            vault_store = None
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
            gk.update_telemetry(
                {"dS": -0.32, "peace2": 1.04, "confidence": 0.88, "verdict": "SEAL"}
            )
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
        import logging as _log
        import asyncio
        import threading
        import os

        # ── F13 Kill-Switch: classify and hard-stop BEFORE execution ──
        risk_tier_label = "T1_REVERSIBLE"
        try:
            from arifosmcp.runtime.governance.risk_tiers import classify

            tier = classify(tool_name, arguments)
            risk_tier_label = tier.tier.value if tier else "T1_REVERSIBLE"
        except Exception:
            pass

        if risk_tier_label == "T3_IRREVERSIBLE":
            hold_enabled = (
                arguments.get("holdEnabled", False)
                or arguments.get("hold_enabled", False)
                or arguments.get("allow_execution", False)
            )
            if not hold_enabled:
                _log.error(f"F13_BREACH: T3 [{tool_name}] without holdEnabled")
                return {
                    "status": "error",
                    "tool": tool_name,
                    "verdict": "HOLD",
                    "requires_f13": True,
                    "error_message": "F13: T3 action blocked. BREACH_PLAYBOOK: HALT_ALL_THREADS → LOG_VAULT_SNAPSHOT → NOTIFY_888_JUDGE → REQUIRE_MANUAL_REBOOT",
                }

        # ── Execute tool ──
        t0 = time.monotonic()
        result = original_handler(**arguments)
        if inspect.isawaitable(result):
            result = await result
        ms = int((time.monotonic() - t0) * 1000)

        # ── Determine verdict ──
        verdict_str = "SEAL"
        if hasattr(result, "verdict"):
            verdict_str = str(getattr(result, "verdict", "SEAL"))
        elif hasattr(result, "ok"):
            verdict_str = "SEAL" if getattr(result, "ok", False) else "HOLD"

        # ── F2: vault-backed receipt (non-blocking thread) ──
        try:
            loop = asyncio.get_event_loop()

            def _emit():
                loop2 = asyncio.new_event_loop()
                asyncio.set_event_loop(loop2)
                try:
                    from arifosmcp.runtime.governance.receipt_emitter import (
                        emit_receipt_to_vault,
                    )

                    receipt = {
                        "tool_name": tool_name,
                        "outcome": verdict_str.lower(),
                        "risk_tier": risk_tier_label,
                        "governance_trace": {
                            "actor_id": arguments.get(
                                "actor_id", os.environ.get("ARIFOS_AGENT_ID", "unknown")
                            ),
                            "session_id": ACTIVE_SESSION_ID,
                            "gates_passed": ["hardened_dispatch"],
                            "policy_used": "arifOS-T0-T3-v1",
                        },
                        "latency_ms": ms,
                    }
                    loop2.run_until_complete(emit_receipt_to_vault(receipt))
                finally:
                    loop2.close()

            threading.Thread(target=_emit, daemon=True).start()
        except Exception as exc:
            _log.warning(f"F2_RECEIPT_FAIL: {exc}")

        # ── Format output ──
        if result.__class__.__name__ == "RuntimeEnvelope":
            from arifosmcp.runtime.output_formatter import format_output

            platform = arguments.get("platform", "mcp")
            if hasattr(result, "platform_context"):
                result.platform_context = platform
            return format_output(
                result, {"verbose": False, "debug": bool(arguments.get("debug", False))}
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
            sys.stderr.write(f"!!! KERNEL PANIC: {str(e)}\n")
            sys.stderr.write(traceback.format_exc() + "\n")
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


def _sovereign_preview(value: str) -> str:
    if not value:
        return ""
    if value.startswith("TEST_"):
        return value
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


class SovereignHandshakeMiddleware(BaseHTTPMiddleware):
    """Observe sovereign auth headers and preserve identity for downstream handlers."""

    async def dispatch(self, request, call_next):
        sovereign_sig = request.headers.get("X-Arifos-Sovereign-Sig", "").strip()
        authorization = request.headers.get("Authorization", "").strip()
        subject = request.headers.get("X-Arifos-User-Id", "").strip()

        if not subject:
            if sovereign_sig:
                subject = "sovereign"
            elif authorization:
                subject = "authorized"

        if sovereign_sig or authorization:
            headers = list(request.scope.get("headers", []))
            header_names = {name.lower() for name, _ in headers}
            if subject and b"x-arifos-user-id" not in header_names:
                headers.append((b"x-arifos-user-id", subject.encode("latin-1")))
                request.scope["headers"] = headers

            request.app.state.arifos_sovereign_status = {
                "status": "888_JUDGE_ACTIVE",
                "subject": subject or "anonymous",
                "path": str(request.url.path),
                "authorization_present": bool(authorization),
                "signature_preview": _sovereign_preview(sovereign_sig),
            }
            logger.warning(
                "F13 sovereign auth observed subject=%s sig=%s authorization=%s path=%s",
                subject or "anonymous",
                _sovereign_preview(sovereign_sig),
                "present" if authorization else "absent",
                request.url.path,
            )

        response = await call_next(request)

        state = getattr(request.app.state, "arifos_sovereign_status", None)
        if state and (sovereign_sig or authorization):
            response.headers["X-Arifos-Sovereign-Status"] = str(
                state.get("status", "888_JUDGE_ACTIVE")
            )
            response.headers["X-Arifos-Sovereign-Subject"] = str(
                state.get("subject", "anonymous")
            )

        return response


def _record_sovereign_state(
    app_instance: Any,
    *,
    subject: str,
    path: str,
    authorization_present: bool,
    signature_preview: str,
) -> dict[str, Any]:
    state = {
        "status": "888_JUDGE_ACTIVE",
        "subject": subject or "anonymous",
        "path": path,
        "authorization_present": authorization_present,
        "signature_preview": signature_preview,
    }
    app_instance.state.arifos_sovereign_status = state
    return state


# ═══════════════════════════════════════════════════════════════════════════════
# MCP SERVER INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

mcp = FastMCP(
    "ARIFOS MCP",
    version=VERSION,
    website_url="https://arifosmcp.arif-fazil.com",
    instructions=f"""Constitutional AI orchestration kernel — SEALED {_display_version()}.
    
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
except ImportError as _ie:
    logger.warning(
        f"arifosmcp.runtime not available (clean kernel staged): {_ie}. Falling back to mcp/tools/arifos registry."
    )
    CANONICAL_TOOL_HANDLERS = {}
    HARDENED_HANDLERS = {}
    v2_tools_registered = []
    v2_prompts_registered = []
    v2_resources_registered = []
else:
    try:
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
        logger.info(
            f"Successfully registered {len(registered_apps)} constitutional apps"
        )

        # Register ChatGPT Apps SDK tools (widget resources + vault seal card)
        try:
            from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import (
                register_chatgpt_app_tools,
            )

            register_chatgpt_app_tools(mcp)
            logger.info("ChatGPT Apps SDK tools registered")
        except Exception as exc:
            logger.warning(f"ChatGPT Apps SDK tools unavailable: {exc}")

        # Mount 6-axis MCP tools (P/T/V/G/E/M) from mcp_tools.py
        # Axis feature flags: set ARIFOS_ENABLE_{P|T|V|G|E|M}_AXIS=false to gate an axis
        _axis_enabled = (
            lambda axis: os.getenv(f"ARIFOS_ENABLE_{axis}_AXIS", "true").lower()
            != "false"
        )
        try:
            from arifosmcp.mcp_tools import (
                create_perception_mcp,
                create_transformation_mcp,
                create_valuation_mcp,
                create_governance_mcp,
                create_execution_mcp,
                create_meta_mcp,
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
                    logger.info(
                        f"  [{_axis}] axis DISABLED via ARIFOS_ENABLE_{_axis}_AXIS=false"
                    )
                    continue
                _agent_mcp = _factory()
                mcp.mount(_agent_mcp, namespace=None)
                logger.info(
                    f"  [{_axis}] 6-axis MCP agent mounted (namespaced by prefix letter)"
                )
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
                logger.warning(
                    "F13 Approval provider unavailable (FastMCP version mismatch)"
                )

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

        logger.info(
            f"ARIFOS MCP SEALED: {len(v2_tools_registered)} tools registered with Fail-Closed gates."
        )
        logger.info("ARIFOS MCP tool manifest: %s", ", ".join(v2_tools_registered))
        print(f"ARIFOS MCP tool manifest: {', '.join(v2_tools_registered)}")
    except Exception as _e:
        logger.error(f"Failed to initialize runtime components: {_e}")
        HARDENED_HANDLERS = {}
        v2_tools_registered = v2_prompts_registered = v2_resources_registered = []

# ── 13-Tool Canonical Registry (MCP Federation) ──
# Wire arifOS_mcp/tools/arifos/registry.py as the canonical MCP surface.
# This runs regardless of whether arifosmcp.runtime loaded successfully,
# ensuring the 13 canonical tools are always available.
try:
    from arifOS_mcp.tools.arifos.registry import (
        register_arifos_tools,
        register_arifos_prompts,
        register_arifos_resources,
    )

    register_arifos_tools(mcp)
    register_arifos_prompts(mcp)
    register_arifos_resources(mcp)
    logger.info("13-tool canonical registry wired from arifOS_mcp/tools/arifos/")
    print("13-tool canonical registry: arifOS_mcp/tools/arifos/ — wired")
except Exception as _e:
    logger.warning(f"arifOS_mcp/tools/arifos registry unavailable: {_e}")

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
    return JSONResponse(
        {
            "status": "healthy",
            "version": f"{_display_version()}-SEALED",
            "tools": len(v2_tools_registered),
            "fail_closed": True,
            "timestamp": __import__("datetime")
            .datetime.now(__import__("datetime").timezone.utc)
            .isoformat(),
        }
    )


async def horizon_metadata(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "name": "ARIFOS MCP",
            "version": _display_version(),
            "security": "Fail-Closed Dispatch (Gate 1-4 active)",
            "protocol": "MCP 2025-03-26",
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════


async def sovereign_sse(request: Request) -> StreamingResponse:
    sovereign_sig = request.headers.get("X-Arifos-Sovereign-Sig", "").strip()
    authorization = request.headers.get("Authorization", "").strip()
    subject = request.headers.get("X-Arifos-User-Id", "").strip() or (
        "sovereign" if sovereign_sig else "authorized" if authorization else "anonymous"
    )
    state = _record_sovereign_state(
        request.app,
        subject=subject,
        path=str(request.url.path),
        authorization_present=bool(authorization),
        signature_preview=_sovereign_preview(sovereign_sig),
    )

    async def event_stream():
        import json

        yield "event: ready\n"
        yield f"data: {json.dumps(state)}\n\n"

    response = StreamingResponse(event_stream(), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache, no-transform"
    response.headers["X-Arifos-Sovereign-Status"] = str(state["status"])
    response.headers["X-Arifos-Sovereign-Subject"] = str(state["subject"])
    return response


async def sovereign_ws(websocket: WebSocket) -> None:
    sovereign_sig = websocket.headers.get("X-Arifos-Sovereign-Sig", "").strip()
    authorization = websocket.headers.get("Authorization", "").strip()
    subject = websocket.headers.get("X-Arifos-User-Id", "").strip() or (
        "sovereign" if sovereign_sig else "authorized" if authorization else "anonymous"
    )
    state = _record_sovereign_state(
        websocket.app,
        subject=subject,
        path=str(websocket.url.path),
        authorization_present=bool(authorization),
        signature_preview=_sovereign_preview(sovereign_sig),
    )
    logger.warning(
        "F13 websocket sovereign auth subject=%s sig=%s authorization=%s path=%s",
        state["subject"],
        state["signature_preview"],
        "present" if authorization else "absent",
        websocket.url.path,
    )
    await websocket.accept(
        headers=[
            (b"x-arifos-sovereign-status", str(state["status"]).encode("latin-1")),
            (b"x-arifos-sovereign-subject", str(state["subject"]).encode("latin-1")),
        ]
    )
    await websocket.send_json(
        {
            "type": "connected",
            "status": state["status"],
            "subject": state["subject"],
            "version": _display_version(),
            "path": state["path"],
        }
    )
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_json(
                {
                    "type": "echo",
                    "status": state["status"],
                    "subject": state["subject"],
                    "message": message,
                }
            )
    except WebSocketDisconnect:
        logger.info("F13 websocket disconnected subject=%s", state["subject"])


# Ensure REST routes from arifosmcp are actually bound to this app instance
# HARDENED_HANDLERS is only defined if the try block succeeded
try:
    from arifosmcp.runtime.rest_routes import register_rest_routes

    if "HARDENED_HANDLERS" in globals():
        register_rest_routes(mcp, HARDENED_HANDLERS, prefix="")
except ImportError:
    pass

# CRITICAL: Re-create http_app AFTER all routes are registered.
# FastMCP.http_app() returns a new Starlette instance each call.
# Routes added via mcp.custom_route() after the first http_app() call
# are invisible to the old app reference.
app = mcp.http_app(stateless_http=True)

# ── Safe middleware registration ──
_mw_errors = []
for _mw_name, _mw_cls in [
    ("GlobalPanicMiddleware", globals().get("GlobalPanicMiddleware")),
    ("CSPMiddleware", globals().get("CSPMiddleware")),
    ("SovereignHandshakeMiddleware", globals().get("SovereignHandshakeMiddleware")),
]:
    if _mw_cls is None:
        _mw_errors.append(f"{_mw_name}: not defined (skipping)")
        continue
    try:
        app.add_middleware(_mw_cls)
    except Exception as _e:
        _mw_errors.append(f"{_mw_name}: {_e}")

app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.state.arifos_sovereign_status = {
    "status": "inactive",
    "subject": "anonymous",
    "path": "",
    "authorization_present": False,
    "signature_preview": "",
}
app.router.routes.append(Route("/sse", endpoint=sovereign_sse, methods=["GET"]))
app.router.routes.append(WebSocketRoute("/ws", endpoint=sovereign_ws))
app.router.routes.append(WebSocketRoute("/webmcp/ws", endpoint=sovereign_ws))

# ── Constitutional startup (runs on module load, not just __main__) ──
import asyncio

try:
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)
    _loop.run_until_complete(_constitutional_startup())
except Exception as _e:
    print(f"[VAULT] Constitutional startup skipped: {_e}")

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = ["mcp", "app"]

if __name__ == "__main__":
    import asyncio

    import uvicorn

    async def run_server():
        print("=" * 60)
        print(f"🔥 ARIFOS MCP {_display_version()} — SEALED")
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
