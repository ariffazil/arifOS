#!/usr/bin/env python3
"""
geox_mcp_server.py — GEOX MCP Server for arifOS
DITEMPA BUKAN DIBERI

GEOX Geological Intelligence Coprocessor exposed as an MCP server.
Provides tools for governed geological prospect evaluation.

Transport: HTTP (Prefect Horizon) + STDIO (local development)

Run:
    python geox_mcp_server.py                    # STDIO
    python geox_mcp_server.py --http            # HTTP on port 8081
    fastmcp run geox_mcp_server.py               # via fastmcp CLI
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("geox.mcp")

# ---------------------------------------------------------------------------
# Bootstrap arifos.geox from installed package
# ---------------------------------------------------------------------------
try:
    from arifos.geox.geox_agent import GeoXAgent, GeoXConfig
    from arifos.geox.geox_memory import GeoMemoryStore
    from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest
    from arifos.geox.geox_tools import ToolRegistry
    from arifos.geox.geox_validator import GeoXValidator

    _HAS_ARIFOS_GEOX = True
except ImportError as exc:
    logger.warning("arifos.geox not available: %s — running in minimal mode", exc)
    _HAS_ARIFOS_GEOX = False

# ---------------------------------------------------------------------------
# FastMCP server
# ---------------------------------------------------------------------------

try:
    from fastmcp import FastMCP

    _USE_FASTMCP = True
except ImportError:
    logger.warning("fastmcp not installed — falling back to low-level MCP SDK")
    _USE_FASTMCP = False

# ---------------------------------------------------------------------------
# Server singletons (lazy)
# ---------------------------------------------------------------------------

_config: GeoXConfig | None = None
_tool_registry: ToolRegistry | None = None
_validator: GeoXValidator | None = None
_memory_store: GeoMemoryStore | None = None
_agent: GeoXAgent | None = None
_initialized = False


def _ensure_init() -> None:
    global _initialized, _config, _tool_registry, _validator, _memory_store, _agent
    if _initialized or not _HAS_ARIFOS_GEOX:
        return
    _config = GeoXConfig()
    _tool_registry = ToolRegistry.default_registry()
    _validator = GeoXValidator()
    _memory_store = GeoMemoryStore()
    _agent = GeoXAgent(
        config=_config,
        tool_registry=_tool_registry,
        validator=_validator,
        llm_planner=None,
        audit_sink=None,
        memory_store=_memory_store,
    )
    _initialized = True
    logger.info("GEOX singletons initialised — DITEMPA BUKAN DIBERI")


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


async def _handle_geox_evaluate_prospect(args: dict[str, Any]) -> dict[str, Any]:
    """Full GEOX geological prospect evaluation pipeline."""
    _ensure_init()
    try:
        location = CoordinatePoint(
            latitude=float(args["latitude"]),
            longitude=float(args["longitude"]),
            depth_m=float(args["depth_m"]) if args.get("depth_m") is not None else None,
        )
        request = GeoRequest(
            query=args["query"],
            prospect_name=args["prospect_name"],
            location=location,
            basin=args["basin"],
            play_type=args["play_type"],
            available_data=list(args.get("available_data", [])),
            risk_tolerance=args["risk_tolerance"],
            requester_id=args["requester_id"],
        )
    except Exception as exc:
        return {
            "error": f"Invalid GeoRequest parameters: {exc}",
            "verdict": "VOID",
            "success": False,
        }

    try:
        response = await _agent.evaluate_prospect(request)  # type: ignore
    except Exception as exc:
        logger.exception("evaluate_prospect failed: %s", exc)
        return {"error": f"Pipeline execution error: {exc}", "verdict": "VOID", "success": False}

    try:
        await _memory_store.store(response, request)  # type: ignore
    except Exception as exc:
        logger.warning("Memory store failed: %s", exc)

    try:
        resp_dict = response.model_dump(mode="json")  # type: ignore
    except Exception:
        resp_dict = {
            "response_id": response.response_id,
            "request_id": response.request_id,
            "verdict": response.verdict,
            "confidence_aggregate": response.confidence_aggregate,
            "human_signoff_required": response.human_signoff_required,
            "arifos_telemetry": response.arifos_telemetry,
            "insight_count": len(response.insights),
        }

    return {
        "success": True,
        "response": resp_dict,
        "verdict": response.verdict,
        "confidence_aggregate": response.confidence_aggregate,
        "human_signoff_required": response.human_signoff_required,
        "seal": "DITEMPA BUKAN DIBERI",
    }


async def _handle_geox_query_memory(args: dict[str, Any]) -> dict[str, Any]:
    """Query the GEOX geological memory store."""
    _ensure_init()
    query = args.get("query", "")
    basin = args.get("basin")
    limit = int(args.get("limit", 5))

    try:
        entries = await _memory_store.retrieve(query, basin=basin, limit=limit)  # type: ignore
        return {"success": True, "count": len(entries), "entries": [e.to_dict() for e in entries]}
    except Exception as exc:
        return {"success": False, "error": str(exc), "entries": []}


async def _handle_geox_health(_args: dict[str, Any]) -> dict[str, Any]:
    """GEOX server health check."""
    _ensure_init()
    tool_health = _tool_registry.health_check_all() if _tool_registry else {}
    return {
        "success": True,
        "status": "healthy",
        "version": "0.4.0",
        "pipeline_id": _config.pipeline_id if _config else "unknown",
        "tool_registry": {
            "registered_tools": _tool_registry.list_tools() if _tool_registry else [],
            "health": tool_health,
            "all_healthy": all(tool_health.values()) if tool_health else False,
        },
        "memory_store": {
            "backend": "in_memory",
            "entry_count": _memory_store.count() if _memory_store else 0,
            "basins": _memory_store.list_basins() if _memory_store else [],
        },
        "constitutional_floors": [
            "F1_amanah",
            "F2_truth",
            "F4_clarity",
            "F7_humility",
            "F9_anti_hantu",
            "F11_authority",
            "F13_sovereign",
        ],
        "seal": "DITEMPA BUKAN DIBERI",
    }


# ---------------------------------------------------------------------------
# Build FastMCP app (preferred)
# ---------------------------------------------------------------------------

if _USE_FASTMCP:
    mcp = FastMCP("GEOX — Geological Intelligence Coprocessor")

    @mcp.tool()
    async def geox_evaluate_prospect(
        query: str,
        prospect_name: str,
        latitude: float,
        longitude: float,
        basin: str,
        play_type: str,
        risk_tolerance: str,
        requester_id: str,
        depth_m: float | None = None,
        available_data: list[str] | None = None,
    ) -> dict[str, Any]:
        """Full GEOX geological prospect evaluation pipeline.

        Args:
            query: Natural-language geological evaluation query.
            prospect_name: Name of the geological prospect or feature.
            latitude: Prospect latitude in decimal degrees (WGS-84).
            longitude: Prospect longitude in decimal degrees (WGS-84).
            depth_m: Target depth below surface in metres (optional).
            basin: Sedimentary basin name.
            play_type: Play type (stratigraphic, structural, combination, carbonate_buildup, deltaic).
            available_data: Available data types (seismic_2d, seismic_3d, well_logs, core, eo, gravity).
            risk_tolerance: Risk tolerance (low, medium, high).
            requester_id: Unique ID of the requesting user or system.
        """
        args = {
            "query": query,
            "prospect_name": prospect_name,
            "latitude": latitude,
            "longitude": longitude,
            "depth_m": depth_m,
            "basin": basin,
            "play_type": play_type,
            "available_data": available_data or [],
            "risk_tolerance": risk_tolerance,
            "requester_id": requester_id,
        }
        return await _handle_geox_evaluate_prospect(args)

    @mcp.tool()
    async def geox_query_memory(
        query: str, basin: str | None = None, limit: int = 5
    ) -> dict[str, Any]:
        """Query the GEOX geological memory store for past prospect evaluations."""
        return await _handle_geox_query_memory({"query": query, "basin": basin, "limit": limit})

    @mcp.tool()
    async def geox_health() -> dict[str, Any]:
        """GEOX server health check. Returns server status, tool registry health, and uptime."""
        return await _handle_geox_health({})

    _APP = mcp

# ---------------------------------------------------------------------------
# Build low-level MCP server (fallback)
# ---------------------------------------------------------------------------

else:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server

    app = Server("geox-mcp")

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        _ensure_init()
        tools = []
        if _tool_registry:
            for name, tool_instance in _tool_registry._tools.items():
                tools.append(
                    Tool(
                        name=name,
                        description=getattr(tool_instance, "description", f"GEOX tool: {name}"),
                        inputSchema={"type": "object", "properties": {}},
                    )
                )
        tools.extend(
            [
                Tool(
                    name="geox_evaluate_prospect",
                    description="Full GEOX geological prospect evaluation pipeline.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "prospect_name": {"type": "string"},
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"},
                            "depth_m": {"type": "number"},
                            "basin": {"type": "string"},
                            "play_type": {"type": "string"},
                            "available_data": {"type": "array", "items": {"type": "string"}},
                            "risk_tolerance": {"type": "string"},
                            "requester_id": {"type": "string"},
                        },
                        "required": [
                            "query",
                            "prospect_name",
                            "latitude",
                            "longitude",
                            "basin",
                            "play_type",
                            "risk_tolerance",
                            "requester_id",
                        ],
                    },
                ),
                Tool(
                    name="geox_query_memory",
                    description="Query the GEOX geological memory store.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "basin": {"type": "string"},
                            "limit": {"type": "integer", "default": 5},
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="geox_health",
                    description="GEOX server health check.",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]
        )
        return tools

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "geox_evaluate_prospect":
            result = await _handle_geox_evaluate_prospect(arguments)
        elif name == "geox_query_memory":
            result = await _handle_geox_query_memory(arguments)
        elif name == "geox_health":
            result = await _handle_geox_health(arguments)
        else:
            result = {"error": f"Unknown tool: {name}", "success": False}

        text = json.dumps(result, default=str, ensure_ascii=False)
        return [TextContent(type="text", text=text)]

    _APP = app


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


async def main() -> None:
    parser = argparse.ArgumentParser(description="GEOX MCP Server — DITEMPA BUKAN DIBERI")
    parser.add_argument(
        "--http", action="store_true", help="Use HTTP transport (for Prefect Horizon)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind host for HTTP")
    parser.add_argument("--port", type=int, default=8081, help="Bind port for HTTP")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("GEOX MCP Server v0.4.0 — DITEMPA BUKAN DIBERI")
    logger.info("Muhammad Arif bin Fazil | PETRONAS Exploration")
    logger.info("=" * 60)

    if args.http:
        if _USE_FASTMCP:
            logger.info("HTTP transport via FastMCP — host=%s port=%d", args.host, args.port)
            import uvicorn

            uvicorn.run("geox_mcp_server:app", host=args.host, port=args.port, log_level="info")
        else:
            logger.error("HTTP transport requires fastmcp. Install: pip install fastmcp")
            sys.exit(1)
    else:
        logger.info("STDIO transport")
        if _USE_FASTMCP:
            mcp.run()
        else:
            async with stdio_server() as (read_stream, write_stream):
                await _APP.run(
                    read_stream,
                    write_stream,
                    _APP.create_initialization_options(),
                )


if __name__ == "__main__":
    asyncio.run(main())
