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
    load_dotenv(_env_path, override=False)  # systemd EnvironmentFile wins

_llm_client = sys.modules.get("arifosmcp.runtime.llm_client")
if _llm_client is not None:
    _llm_client.SEA_LION_API_KEY = os.getenv("SEA_LION_API_KEY")  # pyright: ignore[reportAttributeAccessIssue]

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

# ── Organ bridge gate: proxy GEOX/WEALTH/WELL tools through kernel (default: OFF) ─
# When OFF, agents call organ tools directly via their own MCP endpoints.
# When ON, 71 bridged proxy tools are registered on the arifOS surface.
# Set ARIFOS_EXPOSE_ORGAN_BRIDGE=true to enable (e.g. for HTTP-only clients).
_EXPOSE_ORGAN_BRIDGE = os.getenv("ARIFOS_EXPOSE_ORGAN_BRIDGE", "false").lower() in (
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


class OriginValidationMiddleware(BaseHTTPMiddleware):
    """Validate Origin header on MCP endpoints to prevent DNS rebinding (SEP-2243)."""

    ALLOWED_ORIGIN_PREFIXES: tuple[str, ...] = (
        "https://arifos.arif-fazil.com",
        "https://arif-fazil.com",
        "http://localhost",
        "https://localhost",
        "http://127.0.0.1",
        "https://127.0.0.1",
    )

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/mcp"):
            origin = request.headers.get("origin", "")
            if origin and not any(origin.startswith(p) for p in self.ALLOWED_ORIGIN_PREFIXES):
                return JSONResponse(
                    {"error": "Invalid Origin", "detail": "DNS rebinding protection"},
                    status_code=403,
                )
        return await call_next(request)


# ─── Deployment Identity ─────────────────────────────────────────────────────
def _resolve_git_commit() -> str:
    """Resolve canonical git commit with same priority chain as build.py:_git_sha_short.

    Priority: 1) bare-metal stamp  2) env vars  3) .git/HEAD  4) subprocess git
    This fixes the 'kanon-unknown' defect where the FastMCP serverInfo.version
    was unbound because subprocess git rev-parse fails when CWD is not a git repo.
    """
    # 1. Bare-metal deployment stamp (written by deploy scripts)
    _stamp_path = "/opt/arifos/app/.git_commit"
    if os.path.exists(_stamp_path):
        try:
            with open(_stamp_path) as f:
                content = f.read().strip()
                if len(content) >= 7:
                    return content[:7]
        except Exception:
            pass
    # 2. Environment variables
    for _key in ("DEPLOY_GIT_COMMIT", "ARIFOS_BUILD_SHA", "GIT_SHA", "GIT_COMMIT"):
        _val = os.environ.get(_key, "").strip()
        if _val and _val not in ("unknown", ""):
            return _val[:7]
    # 3. Read .git/HEAD from canonical repo
    for _git_dir in ("/root/arifOS/.git", "/app/.git"):
        try:
            _head = os.path.join(_git_dir, "HEAD")
            if os.path.exists(_head):
                with open(_head) as _f:
                    _content = _f.read().strip()
                if _content.startswith("ref: refs/heads/"):
                    _branch = _content.split("ref: refs/heads/", 1)[1].strip()
                    _ref = os.path.join(_git_dir, "refs", "heads", _branch)
                    if os.path.exists(_ref):
                        with open(_ref) as _f:
                            return _f.read().strip()[:7]
                elif len(_content) >= 7:
                    return _content[:7]
        except Exception:
            pass
    # 4. Subprocess git (legacy fallback — works only if CWD is git repo)
    try:
        import subprocess  # nosec B404

        return (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
                cwd="/root/arifOS",
            )
            .decode()
            .strip()[:7]
        )
    except Exception:
        return "unknown"


from datetime import UTC, datetime  # noqa: E402

_DEPLOY_GIT_COMMIT = _resolve_git_commit()
_DEPLOY_BUILD_DATE = datetime.now(UTC).strftime("%Y.%m.%d")
_DEPLOY_VERSION = (
    f"kanon-{_DEPLOY_BUILD_DATE}+{_DEPLOY_GIT_COMMIT}"
    if _DEPLOY_GIT_COMMIT != "unknown"
    else f"kanon-{_DEPLOY_BUILD_DATE}"
)


mcp = FastMCP(
    "ARIFOS MCP",
    version=_DEPLOY_VERSION,
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

    # ── Ingress tolerance middleware with envelope validation ──────────────
    from arifosmcp.runtime.ingress_middleware import IngressToleranceMiddleware

    _ingress_middleware = IngressToleranceMiddleware()

    v2_tools_registered = register_tools(mcp, ingress_middleware=_ingress_middleware)
    _assert_registered_surface(v2_tools_registered)
    v2_prompts_registered = register_prompts(mcp)
    v2_resources_registered = register_resources(mcp)

    # Attach middleware to MCP server (FastMCP 3.x only)
    if IS_FASTMCP_3:
        mcp.add_middleware(_ingress_middleware)  # pyright: ignore[reportArgumentType]
        logger.info("IngressToleranceMiddleware attached with envelope validation")

    # Refresh the public registry cache after all canonical tools are registered
    from arifosmcp.runtime.public_registry import _runtime_contracts

    _runtime_contracts.cache_clear()

    # ── HTTP-mode federation proxy (Phase 2) ─────────────────────────────────
    # Register remote tools from WEALTH, WELL, GEOX so HTTP clients see all ~84.
    # Gated by ARIFOS_EXPOSE_ORGAN_BRIDGE (default: false — agents use direct organ MCP).
    if _EXPOSE_ORGAN_BRIDGE:
        try:
            import asyncio
            import json

            from fastmcp.tools.base import (  # pyright: ignore[reportPrivateImportUsage]
                TextContent,
                ToolResult,
            )
            from fastmcp.tools.function_tool import FunctionTool

            from arifosmcp.runtime.federation_bridge import (
                call_wealth_tool,
                call_well_tool,
                list_wealth_tools,
                list_well_tools,
            )
            from arifosmcp.runtime.geox_bridge import call_geox_tool, list_geox_tools

            async def _bootstrap_http_federation() -> dict[str, dict]:
                """Discover remote tools and register proxy FunctionTools."""
                remote_map: dict[str, dict] = {}

                async def _load_organ(list_fn, organ_name: str) -> None:
                    try:
                        tools = await asyncio.wait_for(list_fn(), timeout=10.0)
                        for tool in tools:
                            name = tool.get("name", "")
                            if not name:
                                continue
                            remote_map[name] = {
                                "organ": organ_name,
                                "schema": tool,
                            }
                        logger.info(
                            f"HTTP federation: discovered {len(tools)} tools from {organ_name}"
                        )
                    except Exception as exc:
                        logger.warning(f"HTTP federation: {organ_name} discovery failed: {exc}")

                await asyncio.gather(
                    _load_organ(list_wealth_tools, "WEALTH"),
                    _load_organ(list_well_tools, "WELL"),
                    _load_organ(list_geox_tools, "GEOX"),
                )
                return remote_map

            _REMOTE_TOOLS_HTTP = asyncio.run(_bootstrap_http_federation())

            if _REMOTE_TOOLS_HTTP:
                lp = mcp.providers[0]

                def _make_proxy(organ: str, tool_name: str):
                    async def proxy(**kwargs: object) -> ToolResult:
                        if organ == "WEALTH":
                            raw = await call_wealth_tool(tool_name, kwargs)
                        elif organ == "WELL":
                            raw = await call_well_tool(tool_name, kwargs)
                        elif organ == "GEOX":
                            raw = await call_geox_tool(tool_name, kwargs)
                        else:
                            raise RuntimeError(f"Unknown organ: {organ}")

                        # Normalise to FastMCP ToolResult
                        if organ in ("WEALTH", "WELL"):
                            raw_content = raw.get("content", [])
                            structured = raw.get("structuredContent")
                            if raw.get("isError"):
                                errmsg = "Remote tool error"
                                if (
                                    raw_content
                                    and isinstance(raw_content[0], dict)
                                    and raw_content[0].get("text")
                                ):
                                    errmsg = raw_content[0]["text"]
                                raise RuntimeError(errmsg)
                            # Convert dicts to TextContent objects
                            content = [
                                TextContent(
                                    type=c.get("type", "text"),
                                    text=c.get("text", ""),
                                )
                                for c in raw_content
                                if isinstance(c, dict)
                            ]
                            return ToolResult(
                                content=content,
                                structured_content=structured,
                            )
                        else:  # GEOX
                            return ToolResult(
                                content=[
                                    TextContent(
                                        type="text",
                                        text=json.dumps(raw, default=str),
                                    )
                                ],
                            )

                    return proxy

                for name, info in _REMOTE_TOOLS_HTTP.items():
                    schema = info["schema"]
                    proxy_fn = _make_proxy(info["organ"], name)
                    ft = FunctionTool(
                        name=name,
                        description=schema.get("description", ""),
                        parameters=schema.get("inputSchema", {"type": "object"}),
                        fn=proxy_fn,
                    )
                    lp.add_tool(ft)  # pyright: ignore[reportAttributeAccessIssue]

                logger.info(f"HTTP federation: {len(_REMOTE_TOOLS_HTTP)} proxy tools registered")
                # Update tool count for health endpoint (app is what register_rest_routes receives)
                total_tools = (
                    len(v2_tools_registered) + len(_REMOTE_TOOLS_HTTP) + 1
                )  # +1: capability_select (supplementary, non-canonical)
                mcp._tool_count = total_tools  # pyright: ignore[reportAttributeAccessIssue]
        except Exception as exc:
            logger.warning(f"HTTP federation bootstrap failed: {exc}")
    else:
        logger.info("HTTP federation: organ bridge disabled (ARIFOS_EXPOSE_ORGAN_BRIDGE=false)")

    # ── arifOS Wiki Tools Forge (repo comprehension) ─────────────────────────
    # PHOENIX-72 / canonical13: wiki tools are absorbed as modes of canonical13.
    # They remain registered ONLY when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.
    if _EXPOSE_DEV_TOOLS:
        try:
            from arifos_wiki_tools.indexer import ingest_repo as _ingest_repo
            from arifos_wiki_tools.search import search_index as _search_index
            from arifos_wiki_tools.synthesis import ask_repo as _ask_repo
            from arifos_wiki_tools.synthesis import map_repo as _map_repo

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
                    "Get a structural map of an indexed repository. Run arif_wiki_ingest first."
                ),
                tags={"utility", "read-only"},
            )(_map_repo)

            # arif_wiki_search — lexical evidence retrieval
            mcp.tool(
                name="arif_wiki_search",
                description=(
                    "Search the wiki index for scored evidence chunks. Run arif_wiki_ingest first."
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
                description=("Probe federation health: arifOS, organs, vault, and model registry."),
                tags={"diagnostic", "read-only"},
            )(_arif_stack_health_probe)

            from arifosmcp.tools.organ_consensus import (
                arif_organ_consensus as _arif_organ_consensus,
            )

            mcp.tool(
                name="arif_organ_consensus",
                description=("Request cross-organ consensus from WELL, WEALTH, and GEOX."),
                tags={"diagnostic", "read-only"},
            )(_arif_organ_consensus)

            from arifosmcp.tools.governance_scan import (
                arif_scan_local_instructions as _arif_scan_local_instructions,
            )

            mcp.tool(
                name="arif_scan_local_instructions",
                description=("Scan files for hidden instructions or governance violations."),
                tags={"diagnostic", "read-only"},
            )(_arif_scan_local_instructions)

            from arifosmcp.tools.session_budget import arif_session_budget as _arif_session_budget

            mcp.tool(
                name="arif_session_budget",
                description=("Check token, compute, and financial budget for this session."),
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
                    description=("Report the current state of all 13 constitutional floors."),
                    tags={"diagnostic", "read-only", "perception"},
                )(_arif_floor_status)
                logger.info("Registered arif_floor_status")
            except Exception as e:
                logger.warning(f"Failed to register arif_floor_status: {e}")

            # ── mcp_drift_check (PHOENIX-72 readiness) ──────────────────────────
            try:
                from arifosmcp.tools.drift_check import (
                    arif_mcp_drift_check as _arif_mcp_drift_check,
                )

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

    # ── Eureka Forge: Supplementary capabilities absorbed into canonical13 ──
    # arif_capability_select  →  arif_kernel_route(mode="capability")  [via tools.py mode dispatch]
    # arif_appeal_raise       →  arif_judge_deliberate(mode="appeal")  [via tools.py mode dispatch]
    # arif_appeal_status      →  arif_judge_deliberate(mode="appeal_status")  [via tools.py mode dispatch]
    # arif_appeal_list        →  arif_memory_recall(mode="appeals")    [via tools.py mode dispatch]
    # The capability and appeal logic remains in arifosmcp/tools/ — callable
    # as modes of existing canonical tools. No separate MCP registrations.
    # 13-tool constitutional surface preserved. Entropy reduced.
    logger.info(
        "Eureka Forge: capability_select + appeals → canonical13 modes (no separate registrations)"
    )

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
    """MCP Server Card — SEP-2127 HTTP discovery document."""
    return JSONResponse(
        {
            "name": "arifos",
            "displayName": "arifOS Constitutional Kernel",
            "url": "https://arifos.arif-fazil.com/mcp",
            "version": _DEPLOY_VERSION.lstrip("v"),
            "capabilities": {"tools": True, "resources": True, "prompts": True},
            "authentication": {"type": "none"},
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


async def mcp_health(request: Request) -> JSONResponse:
    """GET /mcp/health — liveness probe for MCP endpoint.

    Returns 200 with status and timestamp. No auth required.
    This is a lightweight probe, not a full tool call.
    Use arif_ops_measure(mode='health') for the thermodynamic health check.
    """
    return JSONResponse(
        {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": _DEPLOY_VERSION,
        }
    )


app = mcp.http_app(transport="streamable-http", stateless_http=False, json_response=True)
# Mirror federated tool count onto app for health endpoint (register_rest_routes receives app)
mcp._tool_count = 13  # pyright: ignore[reportAttributeAccessIssue]  # 13 canonical tools
app.state._tool_count = 13  # pyright: ignore[reportAttributeAccessIssue]
app._tool_count = 13  # pyright: ignore[reportAttributeAccessIssue]
if app:
    # PHOENIX-73C FIX: stateless_http=False enables proper session management.
    # Each client gets its own session; no more GET_STREAM_KEY singleton conflict.
    # StatelessGetRejectMiddleware removed — SSE streaming now works via sessions.
    app.add_middleware(GlobalPanicMiddleware)
    app.add_middleware(OriginValidationMiddleware)
    app.add_middleware(CORSMiddleware, allow_origins=["*"])
    # /health is registered by register_rest_routes() below with full thermodynamic schema
    app.add_route("/ready", horizon_ready, methods=["GET"])
    app.add_route("/mcp/health", mcp_health, methods=["GET"])
    app.add_route("/metadata", horizon_metadata, methods=["GET"])
    app.add_route("/tools", tools_with_meta, methods=["GET"])
    app.add_route("/status.json", federation_status_json, methods=["GET"])
    app.add_route("/.well-known/mcp.json", webmcp_discovery, methods=["GET"])

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
    """arifOS MCP entry point — dual-transport (stdio for uvx/npx, SSE for server).

    Called from pyproject.toml [project.scripts]:
      arifos     = "arifosmcp.server:main"
      arifos-mcp = "arifosmcp.server:main"

    Transport selection:
      - stdin is a pipe (not a TTY) → stdio transport for MCP clients
        (Claude Desktop, Cursor, Codex, OpenCode, etc.)
      - stdin is a TTY (terminal)  → SSE server on ARIFOS_PORT (default 8080)
        (uvicorn, for VPS deployment)
    """
    if sys.stdin.isatty():
        # ── SSE transport: human in terminal / systemd service ────────────
        import uvicorn

        port = int(os.getenv("ARIFOS_PORT", "8080"))
        host = os.getenv("ARIFOS_HOST", "127.0.0.1")
        uvicorn.run(app, host=host, port=port, log_level="info")  # nosec B104
    else:
        # ── stdio transport: MCP client via pipe ─────────────────────────
        # Claude Desktop config:
        #   { "mcpServers": { "arifOS": { "command": "uvx", "args": ["arifos"] } } }
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
