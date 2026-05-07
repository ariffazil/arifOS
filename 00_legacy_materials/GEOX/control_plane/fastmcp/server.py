"""
GEOX Unified MCP Server — Canonical Registry & Control Plane
═══════════════════════════════════════════════════════════════════════════════

The "GEOX" surface from your audit.
Acts as the Dashboard / MCP Apps control plane and Registry.

Version: 2.0.0-UNIFIED-SPEC
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
import logging
import sys
import argparse
import json
import uvicorn
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from datetime import datetime, timezone
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# GEOX Unified Server Configuration
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("geox.unified")

GEOX_VERSION = "2.0.0-UNIFIED-SPEC"
GEOX_SEAL = "DITEMPA BUKAN DIBERI"
GEOX_PROFILE = os.getenv("GEOX_PROFILE", "full")

mcp = FastMCP(
    name="GEOX",
    version=GEOX_VERSION,
    on_duplicate="error",
    instructions="""Canonical GEOX Registry & MCP App Control Plane.

    This server acts as the dashboard-ready entry point for all GEOX dimensions.
    It provides discovery for Prospect, Well, Earth3D, Section, Time4D, Physics, Map, and Cross.

    All tools follow the <dimension>_<action> naming convention and return
    standardized artifact envelopes.
    """,
)

# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSION REGISTRIES BOOTSTRAP
# ═══════════════════════════════════════════════════════════════════════════════

sys.path.append(os.getcwd())

DIMENSION_GATES = {
    "core": ["physics", "map"],
    "vps": ["prospect", "well", "earth3d", "map", "cross", "dashboard"],
    "full": [
        "prospect",
        "well",
        "section",
        "earth3d",
        "time4d",
        "physics",
        "map",
        "cross",
        "dashboard",
    ],
}

ENABLED_DIMENSIONS = DIMENSION_GATES.get(GEOX_PROFILE, ["physics", "map", "dashboard"])


def bootstrap_registries():
    registry_map = {
        "prospect": "contracts.tools.prospect",
        "well": "contracts.tools.well",
        "section": "contracts.tools.section",
        "earth3d": "contracts.tools.earth3d",
        "time4d": "contracts.tools.time4d",
        "physics": "contracts.tools.physics",
        "map": "contracts.tools.map",
        "cross": "contracts.tools.cross",
        "dashboard": "contracts.tools.dashboard",
    }

    for dim in ENABLED_DIMENSIONS:
        if dim in registry_map:
            module_name = registry_map[dim]
            try:
                import importlib

                module = importlib.import_module(module_name)
                func_name = f"register_{dim}_tools"
                if hasattr(module, func_name):
                    register_func = getattr(module, func_name)
                    register_func(mcp, profile=GEOX_PROFILE)
                    logger.info(f"Registered {dim.upper()} tools")
            except Exception as e:
                logger.error(f"Failed to bootstrap {dim} registry: {e}")


bootstrap_registries()

# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD / MCP APTS METADATA
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.resource("geox://registry/apps")
async def list_geox_apps() -> list[dict]:
    """Return the list of dashboard-ready GEOX applications from manifests."""
    manifest_dir = "control_plane/fastmcp/manifests"
    apps = []
    if os.path.exists(manifest_dir):
        for filename in os.listdir(manifest_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(manifest_dir, filename), "r") as f:
                        apps.append(json.load(f))
                except Exception as e:
                    logger.error(f"Failed to load manifest {filename}: {e}")
    return apps


@mcp.resource("geox://profile/status")
async def get_profile_status() -> dict:
    return {
        "status": "healthy",
        "registry": "unified",
        "profile": GEOX_PROFILE,
        "enabled_dimensions": ENABLED_DIMENSIONS,
        "version": GEOX_VERSION,
        "seal": GEOX_SEAL,
    }


@mcp.resource("ui://{app_id}")
async def get_ui_resource(app_id: str) -> str:
    """Serve UI resources from the ui/ directory for MCP Apps."""
    ui_dir = "ui"
    # Map app_id to filename if needed, or assume app_id.html
    filename = f"{app_id}.html"
    file_path = os.path.join(ui_dir, filename)

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()

    # Fallback to a generic well-dashboard if app_id not found for demo purposes
    fallback_path = os.path.join(ui_dir, "well-dashboard.html")
    if os.path.exists(fallback_path):
        with open(fallback_path, "r") as f:
            return f.read()

    return f"Error: UI resource {app_id} not found."


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH & LEGACY BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════


def build_status_payload() -> dict:
    return {
        "status": "healthy",
        "registry": "unified",
        "service": "geox-unified-mcp",
        "version": GEOX_VERSION,
        "profile": GEOX_PROFILE,
        "enabled_dimensions": ENABLED_DIMENSIONS,
        "seal": GEOX_SEAL,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def health_handler(request):
    return JSONResponse(build_status_payload())


async def run_legacy_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    # This server uses the canonical tools directly from registries
    tool_result = await mcp.call_tool(name, arguments)
    # FastMCP call_tool returns a ToolResult object
    return {"success": True, "data": tool_result.content[0].text if tool_result.content else {}}


async def legacy_mcp_handler(request):
    try:
        payload = await request.json()
    except:
        return JSONResponse({"error": "Parse error"}, status_code=400)

    method = payload.get("method")
    params = payload.get("params", {})
    response_id = payload.get("id")

    if method == "tools/list":
        tools = [{"name": t.name, "description": t.description} for t in await mcp.list_tools()]
        return JSONResponse({"jsonrpc": "2.0", "id": response_id, "result": {"tools": tools}})

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        result = await run_legacy_tool(name, args)
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": response_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
            }
        )

    return JSONResponse({"error": "Method not found"}, status_code=404)


def create_app():
    mcp_app = mcp.http_app(path="/mcp/stream", transport="streamable-http")
    return Starlette(
        routes=[
            Route("/health", health_handler, methods=["GET"]),
            Route("/mcp", legacy_mcp_handler, methods=["POST"]),
            Mount("/", mcp_app),
        ],
        lifespan=getattr(mcp_app, "lifespan", None),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
