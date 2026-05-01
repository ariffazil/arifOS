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
from arifosmcp.constitutional_map import (
    CANONICAL_TOOLS,
    list_authenticated_tools,
    list_canonical_tools,
    list_constitutional_tools,
    list_probe_tools,
    list_public_tools,
    list_sovereign_tools,
)
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

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


mcp = FastMCP(
    "ARIFOS MCP",
    version="2026.04.26-KANON",
    website_url="https://arifosmcp.arif-fazil.com",
    instructions=(
        "Constitutional AI orchestration kernel — arifOS.\n\n"
        "Golden path: init → sense → mind → heart → judge → vault\n\n"
        "Runtime surface: 13 public capability tools.\n"
        f"Tools (arif_noun_verb):\n  {_canonical_tool_names_text}\n\n"
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
    from arifosmcp.prompts import CANONICAL_PROMPTS, register_prompts
    from arifosmcp.resources import CANONICAL_RESOURCES, register_resources
    from arifosmcp.runtime.tools import register_tools

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


# ── MCP Apps registration ───────────────────────────────────────────────────
# Each app in its own try block so one failure doesn't cascade
def _safe_register(mcp, module_path: str, name: str) -> None:
    import sys

    try:
        import importlib

        mod = importlib.import_module(module_path)
        print(f"[arif-register] Importing {module_path}...", flush=True)
        mod._register(mcp)
        v2_apps_registered.append(name)
        print(f"[arif-register] Registered: {name} OK", flush=True)
        logger.info(f"  Registered app: {name}")
    except Exception as e:
        import traceback

        print(f"[arif-register] FAILED {name}: {e}", flush=True)
        traceback.print_exc(file=sys.stdout)
        logger.warning(f"  Skipped app {name} ({module_path}): {e}")


try:
    _safe_register(mcp, "arifosmcp.apps.command_center.forge_app", "forge")
    # vault_app removed — vault_audit handles vault surface
    _safe_register(mcp, "arifosmcp.apps.command_center.judge_app", "judge")
    _safe_register(mcp, "arifosmcp.apps.vault_audit", "vault_audit")
    _safe_register(mcp, "arifosmcp.apps.command_center", "command_center")
    print(
        f"[arif-register] Total apps registered: {len(v2_apps_registered)} — {v2_apps_registered}",
        flush=True,
    )
    logger.info(
        f"ARIFOS MCP KANON Phase 2: {len(v2_apps_registered)} apps registered — {v2_apps_registered}"
    )
except Exception as e:
    logger.error(f"App registration failed: {e}")

PUBLIC_TOOLS = list_public_tools()
AUTHENTICATED_TOOLS = list_authenticated_tools()
SOVEREIGN_TOOLS = list_sovereign_tools()


async def horizon_health(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "status": "healthy",
            "service": "arifos-mcp-kanon",
            "version": "2026.04.26-KANON",
            "gateway": "unified",
            "tools": len(v2_tools_registered),
            "prompts": len(v2_prompts_registered),
            "resources": len(v2_resources_registered),
            "apps": len(v2_apps_registered),
            "canonical_surface": len(_constitutional_tool_names),
            "probe_surface": len(_probe_tool_names),
            "registered_surface": len(v2_tools_registered),
            "timestamp": __import__("datetime")
            .datetime.now(__import__("datetime").timezone.utc)
            .isoformat(),
        }
    )


async def horizon_ready(request: Request) -> JSONResponse:
    from arifosmcp.runtime.tools import _runtime_selftest

    readiness = _runtime_selftest()
    verdict = str(readiness.get("verdict", "FAIL")).lower()
    return JSONResponse(
        {
            "status": verdict,
            "checks": readiness.get("checks", {}),
            "failures": readiness.get("failed_checks", []),
            "warnings": readiness.get("warnings", []),
            "timestamp": readiness.get("timestamp"),
        },
        status_code=200 if verdict in {"pass", "partial"} else 503,
    )


async def horizon_metadata(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "name": "ARIFOS MCP",
            "version": "2026.04.26-KANON",
            "protocol": "MCP 2025-03-26",
            "gateway": {
                "type": "unified",
                "capabilities": ["tools", "prompts", "resources", "apps", "webmcp"],
                "surface": {
                    "registered": len(v2_tools_registered),
                    "constitutional": len(_constitutional_tool_names),
                    "probes": len(_probe_tool_names),
                },
                "tool_access": {
                    "public": PUBLIC_TOOLS,
                    "authenticated": AUTHENTICATED_TOOLS,
                    "sovereign_only": SOVEREIGN_TOOLS,
                },
            },
            "endpoints": {
                "mcp": "/mcp",
                "health": "/health",
                "ready": "/ready",
                "metadata": "/metadata",
                "tools": "/tools",
                "webmcp_discovery": "/.well-known/mcp",
            },
            "motto": "DITEMPA BUKAN DIBERI — Forged, Not Given",
        }
    )


async def webmcp_discovery(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "name": "arifOS WebMCP Gateway",
            "version": "v2026.04.26",
            "endpoints": {
                "health": "/health",
                "tools": "/tools",
                "execute": "/mcp",
                "metadata": "/metadata",
            },
            "capabilities": ["tools:list", "execute", "metadata"],
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
        # Define tools_with_meta before registration
        async def tools_with_meta(request: Request) -> JSONResponse:
            from arifosmcp.tool_manifest import TOOL_MANIFEST

            tool_summaries = []
            try:
                # Iterate over all providers (LocalProvider, AppProvider, etc.)
                for provider in mcp.providers:
                    # Access the internal _components map
                    # Some providers have it at the top level, others (like FastMCPApp) have it in _local
                    raw_components = getattr(provider, "_components", None)
                    if raw_components is None:
                        local = getattr(provider, "_local", None)
                        if local:
                            raw_components = getattr(local, "_components", None)

                    if not raw_components:
                        continue

                    raw_tools = {k: v for k, v in raw_components.items() if k.startswith("tool:")}

                    for name, tool in raw_tools.items():
                        tool_name = name.replace("tool:", "").rstrip("@")
                        base = {
                            "description": tool.description or "",
                            "parameters": tool.parameters or {},
                        }
                        manifest = TOOL_MANIFEST.get(tool_name, {})
                        meta_dict = getattr(tool, "meta", None) or {}
                        arifos_m = meta_dict.get("arifos_manifest", {}) or manifest
                        entry = {
                            "name": tool_name,
                            "description": base["description"],
                            "parameters": base["parameters"],
                            "stage": arifos_m.get("stage_code", ""),
                            "lane": arifos_m.get("lane", ""),
                            "meta": {
                                "arifos_manifest": arifos_m,
                                "stage_code": meta_dict.get(
                                    "stage_code", arifos_m.get("stage_code", "")
                                ),
                                "stage_name": meta_dict.get(
                                    "stage_name", arifos_m.get("stage_name", "")
                                ),
                                "risk_tier": meta_dict.get(
                                    "risk_tier", arifos_m.get("risk", {}).get("tier", "low")
                                ),
                                "irreversible": meta_dict.get(
                                    "irreversible",
                                    arifos_m.get("risk", {}).get("irreversible", False),
                                ),
                                "requires_human_ack": meta_dict.get(
                                    "requires_human_ack",
                                    arifos_m.get("risk", {}).get("requires_human_ack", False),
                                ),
                                "use_when": arifos_m.get("use_when", []),
                                "do_not_use_when": arifos_m.get("do_not_use_when", []),
                                "next_recommended_tools": arifos_m.get(
                                    "next_recommended_tools", []
                                ),
                                "authority_boundary": arifos_m.get("authority_boundary", {}),
                                "privacy_scope": arifos_m.get("privacy_scope", []),
                                "canonical_order": meta_dict.get(
                                    "canonical_order", arifos_m.get("canonical_order", [])
                                ),
                                "ui": meta_dict.get("ui", {}),
                            },
                        }
                        tool_summaries.append(entry)
            except Exception as e:
                logger.warning(f"Failed to build meta-enriched tools response: {e}")
                tool_summaries = []
            return JSONResponse({"tools": tool_summaries, "count": len(tool_summaries)})

        app.add_middleware(GlobalPanicMiddleware)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
            allow_headers=["X-API-Key", "Content-Type", "Authorization", "X-MCP-Protocol"],
        )
        app.add_route("/health", horizon_health, methods=["GET"])
        app.add_route("/ready", horizon_ready, methods=["GET"])
        app.add_route("/metadata", horizon_metadata, methods=["GET"])
        app.add_route("/humans.txt", serve_humans_txt, methods=["GET"])
        app.add_route("/.well-known/mcp", webmcp_discovery, methods=["GET"])

        # WebMCP Aliases
        app.add_route("/webmcp/health", horizon_health, methods=["GET"])
        app.add_route("/webmcp/tools", tools_with_meta, methods=["GET"])
        app.add_route("/webmcp/metadata", horizon_metadata, methods=["GET"])
        app.add_route("/webmcp/.well-known/mcp", webmcp_discovery, methods=["GET"])

        # Overwrite Starlette routes list with our prioritized meta-enriched /tools
        app.add_route("/tools", tools_with_meta, methods=["GET"])
        app.add_route("/health", horizon_health, methods=["GET"])
        app.add_route("/ready", horizon_ready, methods=["GET"])
        app.add_route("/metadata", horizon_metadata, methods=["GET"])
        app.add_route("/humans.txt", serve_humans_txt, methods=["GET"])
        app.add_route("/.well-known/mcp", webmcp_discovery, methods=["GET"])

        # WebMCP Aliases
        app.add_route("/webmcp/health", horizon_health, methods=["GET"])
        app.add_route("/webmcp/tools", tools_with_meta, methods=["GET"])
        app.add_route("/webmcp/metadata", horizon_metadata, methods=["GET"])
        app.add_route("/webmcp/.well-known/mcp", webmcp_discovery, methods=["GET"])
        logger.info("HTTP app configured with gateway endpoints + meta-enriched /tools")
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
        print("ARIFOS MCP v2026.04.26-KANON — CANONICAL SURFACE")
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
