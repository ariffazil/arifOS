"""
arifOS MCP Server — Canonical Entry Point
═══════════════════════════════════════════

13-tool capability surface | internal ping/selftest | 13 Floors (F1–F13) | Trinity ΔΩΨ
FastMCP 3.2.0 + MCP Apps + Streamable HTTP
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
import sys
import traceback


# ─── Path prioritization (runs before arifOS imports below) ─────────────────
def _prioritize_paths(*paths: str) -> None:
    for path in reversed(paths):
        if path in sys.path:
            sys.path.remove(path)
    for path in reversed(paths):
        sys.path.insert(0, path)


def _apply_path_priority() -> None:
    """Run path prioritization before arifOS package imports."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(project_root)
    parent_idx = sys.path.index(parent) if parent in sys.path else len(sys.path)
    project_root_idx = sys.path.index(project_root) if project_root in sys.path else len(sys.path)
    if parent not in sys.path or project_root not in sys.path or parent_idx > project_root_idx:
        _prioritize_paths(parent, project_root)


from dotenv import load_dotenv  # noqa: E402

_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)

# Fix sys.path so arifOS packages resolve correctly inside Docker
_apply_path_priority()


# ─── Provider env precedence audit (F1 Amanah / F4 Clarity) ─────────────────
def _log_llm_provider_health() -> None:
    """Log redacted LLM provider source at startup — never the secret value."""
    _logger = logging.getLogger("arifosmcp")
    providers = {
        "SEA_LION_API_KEY": os.getenv("SEA_LION_API_KEY"),
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL"),
    }
    for name, val in providers.items():
        if val is None:
            _logger.info("%s=missing", name)
        elif name.endswith("_KEY") and len(val) > 8:
            _logger.info("%s=present_from_env", name)
        else:
            _logger.info("%s=%s", name, val)


_log_llm_provider_health()

import fastmcp  # noqa: E402
from fastmcp import FastMCP  # noqa: E402
from starlette.middleware.base import BaseHTTPMiddleware  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402
from starlette.requests import Request  # noqa: E402
from starlette.responses import JSONResponse  # noqa: E402

from arifosmcp.constitutional_map import (  # noqa: E402
    CANONICAL_TOOLS,
    list_canonical_tools,
    list_constitutional_tools,
    list_probe_tools,
)

logger = logging.getLogger(__name__)

_canonical_tool_names = list_canonical_tools()
_canonical_tool_names_text = ", ".join(_canonical_tool_names)
_constitutional_tool_names = list_constitutional_tools()
_probe_tool_names = list_probe_tools()


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


# ─── Deployment Identity ─────────────────────────────────────────────────────
def _get_git_info() -> tuple[str, str, str]:
    import subprocess

    commit = os.environ.get("DEPLOY_GIT_COMMIT", "").strip()
    branch = os.environ.get("DEPLOY_GIT_BRANCH", "").strip()
    build_time = os.environ.get("DEPLOY_BUILD_TIME", "").strip()
    if commit:
        return commit, branch, build_time
    try:
        cwd = os.path.dirname(os.path.abspath(__file__))
        commit = (
            subprocess.check_output(
                ["git", "describe", "--always", "--long"], stderr=subprocess.DEVNULL, cwd=cwd
            )
            .decode()
            .strip()
        )
        branch = (
            subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL, cwd=cwd
            )
            .decode()
            .strip()
        )
        build_time = (
            subprocess.check_output(
                ["git", "log", "-1", "--format=%ci"], stderr=subprocess.DEVNULL, cwd=cwd
            )
            .decode()
            .strip()
        )
        return commit, branch, build_time
    except Exception:
        return "unknown", "unknown", "unknown"


_DEPLOY_GIT_COMMIT, _DEPLOY_GIT_BRANCH, _DEPLOY_BUILD_TIME = _get_git_info()
_DEPLOY_VERSION = f"kanon-{_DEPLOY_GIT_COMMIT}"


mcp = FastMCP(
    "ARIFOS MCP",
    version=f"kanon-{_DEPLOY_GIT_COMMIT}",
    website_url="https://arifosmcp.arif-fazil.com",
    instructions=(
        "Constitutional AI orchestration kernel — arifOS.\n\n"
        "Golden path: init → sense → mind → heart → judge → vault\n\n"
        "Runtime surface: 13 public capability tools.\n"
        f"Tools (arif_noun_verb):\n  {_canonical_tool_names_text}\n\n"
        "DITEMPA BUKAN DIBERI — Forged, Not Given"
    ),
)


def create_arifos_mcp_server() -> FastMCP:
    return mcp


def _assert_registered_surface(registered_names: list[str]) -> None:
    expected_set = set(CANONICAL_TOOLS)
    if len(registered_names) != len(expected_set):
        logger.warning(
            "Surface drift: expected %d tools, got %d", len(expected_set), len(registered_names)
        )
    if any(name.startswith("arifos_") for name in registered_names):
        raise RuntimeError("Legacy surface detected in registered MCP tools")


v2_tools_registered: list[str] = []
v2_prompts_registered: list[str] = []
v2_resources_registered: list[str] = []
v2_apps_registered: list[str] = []

IS_FASTMCP_3 = fastmcp.__version__.startswith("3")


try:
    from arifosmcp.prompts import register_prompts
    from arifosmcp.resources import register_resources
    from arifosmcp.runtime.tools import register_tools

    v2_tools_registered = register_tools(mcp)
    _assert_registered_surface(v2_tools_registered)
    v2_prompts_registered = register_prompts(mcp)
    v2_resources_registered = register_resources(mcp)
except Exception as e:
    logger.error(f"Failed to initialize runtime components: {e}")
    raise


# ── REST Endpoints ──────────────────────────────────────────────────────────
async def horizon_health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy", "version": _DEPLOY_VERSION})


async def horizon_ready(request: Request) -> JSONResponse:
    return JSONResponse({"status": "pass"})


async def horizon_metadata(request: Request) -> JSONResponse:
    return JSONResponse({"name": "ARIFOS MCP", "version": _DEPLOY_VERSION})


async def webmcp_discovery(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "name": "arifOS WebMCP Gateway",
            "endpoints": {"health": "/health", "tools": "/tools", "execute": "/mcp"},
        }
    )


async def tools_with_meta(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "tools": v2_tools_registered,
            "count": len(v2_tools_registered),
            "version": _DEPLOY_VERSION,
        }
    )


async def federation_status_json(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


app = mcp.http_app(transport="streamable-http", stateless_http=True, json_response=True)
if app:
    app.add_middleware(GlobalPanicMiddleware)
    app.add_middleware(CORSMiddleware, allow_origins=["*"])
    # /health is registered by register_rest_routes() below with full thermodynamic schema
    app.add_route("/ready", horizon_ready, methods=["GET"])
    app.add_route("/metadata", horizon_metadata, methods=["GET"])
    app.add_route("/tools", tools_with_meta, methods=["GET"])
    app.add_route("/status.json", federation_status_json, methods=["GET"])
    app.add_route("/.well-known/mcp", webmcp_discovery, methods=["GET"])

    # Register REST routes from rest_routes.py — /000, /999, /constitution, etc.
    try:
        from arifosmcp.runtime.rest_routes import register_rest_routes
        from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS

        register_rest_routes(app, CANONICAL_TOOL_HANDLERS)
        logger.info("REST routes registered on ASGI app")
    except Exception as e:
        logger.warning(f"REST routes registration failed: {e}")


def main() -> None:
    import uvicorn

    port = int(os.getenv("ARIFOS_PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
