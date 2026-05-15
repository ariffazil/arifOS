"""
arifOS MCP Server — Canonical Entry Point
═══════════════════════════════════════════

13-canonical constitutional tools (arif_noun_verb) | streamable-http | F1–F13 | Trinity ΔΩΨ
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

_llm_client = sys.modules.get("arifosmcp.runtime.llm_client")
if _llm_client is not None:
    _llm_client.SEA_LION_API_KEY = os.getenv("SEA_LION_API_KEY")

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
    import subprocess  # nosec B404

    commit = os.environ.get("DEPLOY_GIT_COMMIT", "").strip()
    branch = os.environ.get("DEPLOY_GIT_BRANCH", "").strip()
    build_time = os.environ.get("DEPLOY_BUILD_TIME", "").strip()
    if commit:
        return commit, branch, build_time
    try:
        cwd = os.path.dirname(os.path.abspath(__file__))
        commit = (
            subprocess.check_output(  # nosec
                ["git", "describe", "--always", "--long"],
                stderr=subprocess.DEVNULL,
                cwd=cwd,
            )
            .decode()
            .strip()
        )
        branch = (
            subprocess.check_output(  # nosec
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.DEVNULL,
                cwd=cwd,
            )
            .decode()
            .strip()
        )
        build_time = (
            subprocess.check_output(  # nosec
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
        "Canonical surface: 13 public capability tools (arif_noun_verb naming).\n"
        f"Tools:\n  {', '.join(sorted(list_canonical_tools()))}\n\n"
        "DITEMPA BUKAN DIBERI — Forged, Not Given"
    ),
)


def create_arifos_mcp_server() -> FastMCP:
    return mcp


def _assert_registered_surface(registered_names: list[str]) -> None:
    expected_set = set(CANONICAL_TOOLS)
    if len(registered_names) != len(expected_set):
        logger.warning(
            "Surface drift: expected %d tools, got %d",
            len(expected_set),
            len(registered_names),
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
    from arifosmcp.runtime.tools import _CANONICAL_HANDLERS, register_tools
    from arifosmcp.tools.embodied_instances.arif_mind_reason_handler import (
        embodied_mind_reason_handler,
    )
    from arifosmcp.tools.embodied import register_all_arifos_tools

    register_all_arifos_tools()

    _CANONICAL_HANDLERS["arif_mind_reason"] = embodied_mind_reason_handler

    v2_tools_registered = register_tools(mcp)
    _assert_registered_surface(v2_tools_registered)
    v2_prompts_registered = register_prompts(mcp)
    v2_resources_registered = register_resources(mcp)

    # ── Inclusive Topology / Anti-Sink Diagnostics (777 FORGE) ────────────────
    # Reversible runtime diagnostics. NOT canonical constitutional tools.
    # Authority ceiling: advisory estimates only. No state mutation.
    #
    # NOTE: The public registry defines an "expanded45" mode listing 44 tool
    # names (canonical + aliases). The LIVE MCP server here registers only the
    # 13 canonical tools + these 3 diagnostics = 16 callable tools. The expanded
    # registry names are for documentation and future expansion; they are NOT
    # guaranteed to be registered at runtime. Use MCP tools/list for the
    # authoritative live count.
    from arifosmcp.tools.topology import (
        arif_anti_sink_check,
        institutional_drift_check,
    )

    mcp.tool(
        name="arif_anti_sink_check",
        description=(
            "777_TOPOLOGY: Anti-sink runtime diagnostic. "
            "Evaluates a system against anti-sink invariants (F05, F08, F10, F13). "
            "Returns advisory estimates — not verdicts. Reversible. No state mutation."
        ),
        tags={"diagnostic", "topology", "governance"},
    )(arif_anti_sink_check)

    mcp.tool(
        name="institutional_drift_check",
        description=(
            "777_TOPOLOGY: Institutional drift runtime diagnostic. "
            "Evaluates extractive vs inclusive topology (Acemoglu frame). "
            "Returns advisory estimates — not verdicts. Reversible. No state mutation."
        ),
        tags={"diagnostic", "topology", "governance"},
    )(institutional_drift_check)

    from arifosmcp.tools.health import arif_stack_health_probe

    mcp.tool(
        name="arif_stack_health_probe",
        description=(
            "777_OPS: Federation stack health and governance probe. "
            "Checks arifOS MCP, organs, model registry, risk leash, tool registry, VAULT999. "
            "Returns SELAMAT / AMANAH / VOID with per-component diagnostics."
        ),
        tags={"diagnostic", "ops", "health", "governance"},
    )(arif_stack_health_probe)

    v2_tools_registered.extend(
        [
            "arif_anti_sink_check",
            "institutional_drift_check",
            "arif_stack_health_probe",
        ]
    )
    logger.info(
        "Registered diagnostics: arif_anti_sink_check, institutional_drift_check, arif_stack_health_probe"
    )
except Exception as e:
    logger.error(f"Failed to initialize runtime components: {e}")
    raise


# ── REST Endpoints ──────────────────────────────────────────────────────────
async def horizon_health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy", "version": _DEPLOY_VERSION})


async def horizon_ready(request: Request) -> JSONResponse:
    from arifosmcp.runtime.tools import _runtime_selftest

    readiness = _runtime_selftest()
    verdict = str(readiness.get("verdict", "FAIL")).lower()
    payload = {
        "status": verdict,
        "checks": readiness.get("checks", {}),
        "failures": readiness.get("failed_checks", []),
        "warnings": readiness.get("warnings", []),
        "timestamp": readiness.get("timestamp"),
    }
    status_code = 200 if verdict in {"pass", "partial"} else 503
    return JSONResponse(payload, status_code=status_code)


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
    from arifosmcp.runtime.public_registry import public_tool_specs

    tools_payload = [
        {
            "name": spec.name,
            "canonical": spec.name,
            "description": spec.description,
            "stage": spec.stage,
            "lane": spec.trinity,
            "access": spec.access,
            "inputSchema": spec.input_schema,
            "outputSchema": spec.output_schema,
        }
        for spec in public_tool_specs()
    ]
    return JSONResponse(
        {
            "tools": tools_payload,
            "count": len(tools_payload),
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

    # Register constitutional webhook intake + Observatory SSE feed
    # Mounted as FastAPI sub-apps because mcp.http_app() returns Starlette
    try:
        from fastapi import FastAPI

        from arifosmcp.runtime.sse_router import router as sse_router
        from arifosmcp.runtime.webhook_router import router as webhook_router

        wh_app = FastAPI()
        wh_app.include_router(webhook_router)
        app.mount("/api/webhook", wh_app)

        ev_app = FastAPI()
        ev_app.include_router(sse_router)
        app.mount("/api/events", ev_app)

        logger.info("Webhook + SSE routers mounted on ASGI app")
    except Exception as e:
        logger.warning(f"Webhook/SSE mount failed: {e}")


def main() -> None:
    import uvicorn

    port = int(os.getenv("ARIFOS_PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")  # nosec B104


if __name__ == "__main__":
    main()
