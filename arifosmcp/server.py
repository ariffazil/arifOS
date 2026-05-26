"""
arifOS MCP Server — Canonical Entry Point
═══════════════════════════════════════════

FastMCP 3.2.0 + MCP Apps + Streamable HTTP
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

try:
    import uvloop

    uvloop.install()
except ImportError:
    pass  # Windows / dev fallback

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

# ── Dev-mode gate: expose wiki + diagnostic tools on the public surface ───────
_EXPOSE_DEV_TOOLS = os.getenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "false").lower() in (
    "true",
    "1",
    "yes",
)


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


class StatelessGetRejectMiddleware(BaseHTTPMiddleware):
    """
    PHOENIX-73C: Reject GET requests to /mcp in stateless HTTP mode.

    Root cause: MCP SDK's StreamableHTTPSessionManager uses a singleton
    GET_STREAM_KEY for SSE streams. When 2 clients connect simultaneously
    with GET (SSE), the second gets 409 Conflict.

    In stateless_http=True mode, GET requests should return JSON-RPC
    responses directly, NOT establish SSE streams. This middleware rejects
    GET at the gateway layer before it reaches the SDK's SSE handler,
    forcing clients to use POST for JSON-RPC calls.

    Clients receiving 405 will know to retry with POST.
    """

    async def dispatch(self, request: Request, call_next):
        # Only guard the /mcp endpoint
        if request.url.path.rstrip("/") == "/mcp" and request.method == "GET":
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32005,
                        "message": "Method not allowed in stateless mode. "
                        "Use POST for JSON-RPC calls. "
                        "SSE streams are not supported in stateless_http mode "
                        "(PHOENIX-73C).",
                        "data": {
                            "hint": "Retry this request using POST with "
                            '{"jsonrpc":"2.0","method":"...","params":{}}'
                        },
                    },
                },
                status_code=405,
                headers={"Allow": "POST, DELETE"},
            )
        return await call_next(request)


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
        "Membrane Principle:\n"
        "- Language is lossy compression, not the world.\n"
        "- Intelligence is uncertainty reduction under constraint and human judgment.\n"
        "- Truth survives falsification, not assertion.\n"
        "- Meaning is sovereign-anchored; the machine carries structure, not sense.\n"
        "- Paradox is the boundary scream — the correct response is HOLD.\n\n"
        "Golden path: init → sense → mind → heart → judge → vault\n\n"
        "Canonical surface: 13 public capability tools (arif_noun_verb naming).\n"
        f"Tools:\n  {', '.join(sorted(list_canonical_tools()))}\n\n"
        "DITEMPA BUKAN DIBERI — Forged, Not Given"
    ),
)


def create_arifos_mcp_server() -> FastMCP:
    return mcp


def _assert_registered_surface(registered_names: list[str]) -> None:
    """Assert the registered surface matches exactly the 13 canonical tools."""
    expected_set = set(CANONICAL_TOOLS)
    registered_set = set(registered_names)
    if registered_set != expected_set:
        unexpected = registered_set - expected_set
        missing = expected_set - registered_set
        if unexpected or missing:
            raise RuntimeError(
                f"Surface drift detected: unexpected={sorted(unexpected)}, "
                f"missing={sorted(missing)}. Expected exactly {len(expected_set)} canonical tools."
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
    from arifosmcp.tools.embodied import register_all_arifos_tools
    from arifosmcp.tools.embodied_instances.arif_mind_reason_handler import (
        embodied_mind_reason_handler,
    )

    register_all_arifos_tools()

    _CANONICAL_HANDLERS["arif_mind_reason"] = embodied_mind_reason_handler

    v2_tools_registered = register_tools(mcp)
    _assert_registered_surface(v2_tools_registered)
    v2_prompts_registered = register_prompts(mcp)
    v2_resources_registered = register_resources(mcp)

    # Refresh the public registry cache after all canonical tools are registered
    from arifosmcp.runtime.public_registry import _runtime_contracts
    _runtime_contracts.cache_clear()

    # ── arifOS Wiki Tools Forge (repo comprehension) ─────────────────────────
    # PHOENIX-72 / canonical13: wiki tools are absorbed as modes of canonical13.
    # They remain registered ONLY when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.
    if _EXPOSE_DEV_TOOLS:
        try:
            from arifos_wiki_tools.indexer import ingest_repo as _ingest_repo
            from arifos_wiki_tools.search import search_index as _search_index
            from arifos_wiki_tools.synthesis import ask_repo as _ask_repo, map_repo as _map_repo

            # arif_wiki_ingest — index a repo, produce wiki index + optional markdown pages
            mcp.tool(
                name="arif_wiki_ingest",
                description=(
                    "Index a local repository into the wiki. "
                    "Run this FIRST before map, search, or ask."
                ),
                tags={"utility", "write"},
            )(_ingest_repo)

            # arif_wiki_map — structural map of the repo
            mcp.tool(
                name="arif_wiki_map",
                description=(
                    "Get a structural map of an indexed repository. "
                    "Run arif_wiki_ingest first."
                ),
                tags={"utility", "read-only"},
            )(_map_repo)

            # arif_wiki_search — lexical evidence retrieval
            mcp.tool(
                name="arif_wiki_search",
                description=(
                    "Search the wiki index for scored evidence chunks. "
                    "Run arif_wiki_ingest first."
                ),
                tags={"utility", "read-only"},
            )(_search_index)

            # arif_wiki_ask — evidence-grounded Q&A
            mcp.tool(
                name="arif_wiki_ask",
                description=(
                    "Ask a natural-language question over the wiki index. "
                    "Run arif_wiki_ingest first."
                ),
                tags={"utility", "read-only"},
            )(_ask_repo)

            logger.info(
                "Registered arifOS Wiki Tools Forge: arif_wiki_ingest, arif_wiki_map, arif_wiki_search, arif_wiki_ask"
            )
        except Exception as e:
            logger.warning(f"Failed to register arifOS Wiki Tools: {e}")
    else:
        logger.info("Wiki tools absorbed into canonical13 modes (dev mode disabled).")

    # ── Diagnostic tools registered as FastMCP tools ─────────────────────────
    # PHOENIX-72 / canonical13: diagnostics are absorbed as modes of canonical13.
    # They remain registered ONLY when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.
    if _EXPOSE_DEV_TOOLS:
        try:
            from arifosmcp.tools.health import arif_stack_health_probe as _arif_stack_health_probe

            mcp.tool(
                name="arif_stack_health_probe",
                description=(
                    "Probe federation health: arifOS, organs, vault, and model registry."
                ),
                tags={"diagnostic", "read-only"},
            )(_arif_stack_health_probe)

            from arifosmcp.tools.organ_consensus import arif_organ_consensus as _arif_organ_consensus

            mcp.tool(
                name="arif_organ_consensus",
                description=(
                    "Request cross-organ consensus from WELL, WEALTH, and GEOX."
                ),
                tags={"diagnostic", "read-only"},
            )(_arif_organ_consensus)

            from arifosmcp.tools.governance_scan import (
                arif_scan_local_instructions as _arif_scan_local_instructions,
            )

            mcp.tool(
                name="arif_scan_local_instructions",
                description=(
                    "Scan files for hidden instructions or governance violations."
                ),
                tags={"diagnostic", "read-only"},
            )(_arif_scan_local_instructions)

            from arifosmcp.tools.session_budget import arif_session_budget as _arif_session_budget

            mcp.tool(
                name="arif_session_budget",
                description=(
                    "Check token, compute, and financial budget for this session."
                ),
                tags={"diagnostic", "read-only"},
            )(_arif_session_budget)

            # ── arif_floor_status (constitutional floor report) ───────────────────
            try:
                from arifosmcp.runtime.floor import get_floor_status as _get_floor_status

                def _arif_floor_status(
                    session_id: str | None = None,
                    actor_id: str | None = None,
                ):
                    """Report the current state of constitutional floor enforcement."""
                    result = _get_floor_status()
                    result["session_id"] = session_id
                    result["actor_id"] = actor_id
                    return result

                mcp.tool(
                    name="arif_floor_status",
                    description=(
                        "Report the current state of all 13 constitutional floors."
                    ),
                    tags={"diagnostic", "read-only", "perception"},
                )(_arif_floor_status)
                logger.info("Registered arif_floor_status")
            except Exception as e:
                logger.warning(f"Failed to register arif_floor_status: {e}")

            # ── mcp_drift_check (PHOENIX-72 readiness) ──────────────────────────
            try:
                from arifosmcp.tools.drift_check import arif_mcp_drift_check as _arif_mcp_drift_check

                mcp.tool(
                    name="mcp_drift_check",
                    description=(
                        "Compare live tool registry against canonical manifest for drift."
                    ),
                    tags={"diagnostic", "read-only", "phoenix72"},
                )(_arif_mcp_drift_check)
                logger.info("Registered mcp_drift_check (PHOENIX-72)")
            except Exception as e:
                logger.warning(f"Failed to register mcp_drift_check: {e}")

            logger.info(
                "Registered diagnostic tools: arif_stack_health_probe, arif_organ_consensus, "
                "arif_scan_local_instructions, arif_session_budget, arif_floor_status, mcp_drift_check"
            )
        except Exception as e:
            logger.warning(f"Failed to register arifOS diagnostic tools: {e}")
    else:
        logger.info("Diagnostic tools absorbed into canonical13 modes (dev mode disabled).")

    # ── Memory Janitor (Phoenix-72) ──────────────────────────────────────────
    try:
        from arifosmcp.runtime.workers.memory_janitor import MemoryJanitor

        janitor = MemoryJanitor.start(interval_seconds=3600)
        logger.info("Phoenix-72 Memory Janitor: ACTIVE")
    except Exception as e:
        logger.warning(f"Failed to start Memory Janitor: {e}")
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
    # PHOENIX-73C: StatelessGetRejectMiddleware MUST be first — it intercepts
    # GET /mcp before the MCP SDK's singleton SSE stream handler is reached.
    app.add_middleware(StatelessGetRejectMiddleware)
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
