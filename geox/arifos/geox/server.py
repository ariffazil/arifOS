#!/usr/bin/env python3
"""
GEOX MCP Server — DITEMPA BUKAN DIBERI
Arif Fazil | PETRONAS Exploration

A minimal, self-contained GEOX MCP server exposing:
  geox_evaluate_prospect  — Full prospect evaluation pipeline
  geox_query_memory       — Geological memory retrieval
  geox_health             — Server health and readiness check

Run: python server.py [--host 0.0.0.0] [--port 8100] [--log-level info]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Bootstrap — add arifOS/geox to path
# ---------------------------------------------------------------------------
_ROOT = Path("/root/arifOS/geox/arifos")
if _ROOT.exists():
    sys.path.insert(0, str(_ROOT.parent))

try:
    from arifos.geox.geox_agent import GeoXAgent, GeoXConfig
    from arifos.geox.geox_memory import GeoMemoryStore
    from arifos.geox.geox_reporter import GeoXReporter
    from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest
    from arifos.geox.geox_tools import ToolRegistry
    from arifos.geox.geox_validator import GeoXValidator

    _HAS_GEOX = True
except ImportError as exc:
    logging.warning("GEOX modules not found: %s", exc)
    _HAS_GEOX = False

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("geox.server")

# ---------------------------------------------------------------------------
# Server singletons (lazy)
# ---------------------------------------------------------------------------

_config: GeoXConfig | None = None
_tool_registry: ToolRegistry | None = None
_validator: GeoXValidator | None = None
_memory_store: GeoMemoryStore | None = None
_reporter: GeoXReporter | None = None
_agent: GeoXAgent | None = None
_initialized = False


def _ensure_init() -> None:
    global \
        _initialized, \
        _config, \
        _tool_registry, \
        _validator, \
        _memory_store, \
        _reporter, \
        _agent
    if _initialized:
        return
    if not _HAS_GEOX:
        raise RuntimeError("GEOX modules not available — cannot start server")
    _config = GeoXConfig()
    _tool_registry = ToolRegistry.default_registry()
    _validator = GeoXValidator()
    _memory_store = GeoMemoryStore()
    _reporter = GeoXReporter()
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
# Tool specs
# ---------------------------------------------------------------------------

_TOOL_SPECS: dict[str, dict[str, Any]] = {
    "geox_evaluate_prospect": {
        "name": "geox_evaluate_prospect",
        "description": (
            "Full GEOX geological prospect evaluation pipeline. "
            "Accepts a GeoRequest and returns a GeoResponse with "
            "insights, predictions, verdict (SEAL/PARTIAL/SABAR/VOID), "
            "and arifOS telemetry block. "
            "Primary GEOX tool for arifOS integration."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural-language geological evaluation query.",
                },
                "prospect_name": {
                    "type": "string",
                    "description": "Name of the geological prospect or feature.",
                },
                "latitude": {
                    "type": "number",
                    "description": "Prospect latitude in decimal degrees (WGS-84).",
                },
                "longitude": {
                    "type": "number",
                    "description": "Prospect longitude in decimal degrees (WGS-84).",
                },
                "depth_m": {
                    "type": "number",
                    "description": "Target depth below surface in metres (optional).",
                },
                "basin": {"type": "string", "description": "Sedimentary basin name."},
                "play_type": {
                    "type": "string",
                    "description": "Play type: stratigraphic, structural, or combination.",
                    "enum": [
                        "stratigraphic",
                        "structural",
                        "combination",
                        "carbonate_buildup",
                        "deltaic",
                    ],
                },
                "available_data": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Available data types: seismic_2d, seismic_3d, well_logs, core, eo, gravity.",
                },
                "risk_tolerance": {
                    "type": "string",
                    "description": "Risk tolerance: low, medium, or high.",
                    "enum": ["low", "medium", "high"],
                },
                "requester_id": {
                    "type": "string",
                    "description": "Unique ID of the requesting user or system.",
                },
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
    },
    "geox_query_memory": {
        "name": "geox_query_memory",
        "description": (
            "Query the GEOX geological memory store for past prospect evaluations. "
            "Supports keyword search and optional basin filter. "
            "Returns up to `limit` most relevant memory entries."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (geological terms, prospect name, etc.).",
                },
                "basin": {
                    "type": "string",
                    "description": "Optional basin name to filter results.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default 5).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    "geox_health": {
        "name": "geox_health",
        "description": (
            "GEOX server health check. Returns server status, tool registry health, "
            "memory store entry count, and uptime. "
            "Use to verify GEOX is ready before calling geox_evaluate_prospect."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
}

_SERVER_START_TIME = time.time()

# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


async def _handle_geox_evaluate_prospect(args: dict[str, Any]) -> dict[str, Any]:
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
        return {
            "error": f"Pipeline execution error: {exc}",
            "verdict": "VOID",
            "success": False,
        }

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
        "markdown_report": _reporter.generate_markdown_report(response, request),  # type: ignore
        "human_brief": _reporter.generate_human_brief(response),  # type: ignore
    }


async def _handle_geox_query_memory(args: dict[str, Any]) -> dict[str, Any]:
    _ensure_init()
    query = args.get("query", "")
    basin = args.get("basin")
    limit = int(args.get("limit", 5))

    try:
        entries = await _memory_store.retrieve(query, basin=basin, limit=limit)  # type: ignore
        return {
            "success": True,
            "count": len(entries),
            "entries": [e.to_dict() for e in entries],
        }
    except Exception as exc:
        return {"success": False, "error": str(exc), "entries": []}


async def _handle_geox_health(_args: dict[str, Any]) -> dict[str, Any]:
    _ensure_init()
    tool_health = _tool_registry.health_check_all() if _tool_registry else {}  # type: ignore
    uptime_s = round(time.time() - _SERVER_START_TIME, 1)
    return {
        "success": True,
        "status": "healthy",
        "version": "0.1.0",
        "pipeline_id": _config.pipeline_id if _config else "unknown",
        "uptime_seconds": uptime_s,
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


_TOOL_HANDLERS = {
    "geox_evaluate_prospect": _handle_geox_evaluate_prospect,
    "geox_query_memory": _handle_geox_query_memory,
    "geox_health": _handle_geox_health,
}

# ---------------------------------------------------------------------------
# ASGI app
# ---------------------------------------------------------------------------


async def _send_json(send: Any, data: dict[str, Any], status: int = 200) -> None:
    body = json.dumps(data, default=str, ensure_ascii=False).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", b"application/json"],
                [b"content-length", str(len(body)).encode()],
                [b"access-control-allow-origin", b"*"],
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def app(scope: dict, receive: Any, send: Any) -> None:
    """
    Minimal ASGI application implementing MCP JSON-RPC 2.0 protocol.

    Endpoints:
      GET  /health       — health check shortcut
      POST /mcp          — MCP JSON-RPC 2.0 dispatcher
      GET  /mcp/tools    — list available tools
    """
    if scope["type"] != "http":
        return

    method = scope.get("method", "GET")
    path = scope.get("path", "/")

    body_chunks = []
    while True:
        event = await receive()
        if event["type"] == "http.request":
            body_chunks.append(event.get("body", b""))
            if not event.get("more_body", False):
                break
    raw_body = b"".join(body_chunks)

    # GET /health
    if path == "/health" and method == "GET":
        result = await _handle_geox_health({})
        await _send_json(send, result)
        return

    # GET /mcp/tools
    if path in ("/mcp/tools", "/mcp/list_tools") and method == "GET":
        await _send_json(
            send,
            {
                "tools": list(_TOOL_SPECS.values()),
                "server": "geox-mcp-v0.1",
                "seal": "DITEMPA BUKAN DIBERI",
            },
        )
        return

    # POST /mcp
    if path == "/mcp" and method == "POST":
        try:
            rpc = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            await _send_json(
                send,
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {exc}"},
                },
                status=400,
            )
            return

        rpc_id = rpc.get("id")
        rpc_method = rpc.get("method", "")
        rpc_params = rpc.get("params", {})

        if rpc_method == "tools/call":
            tool_name = rpc_params.get("name")
            tool_args = rpc_params.get("arguments", {})

            if tool_name not in _TOOL_HANDLERS:
                await _send_json(
                    send,
                    {
                        "jsonrpc": "2.0",
                        "id": rpc_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool '{tool_name}' not found.",
                            "data": {"available_tools": list(_TOOL_HANDLERS.keys())},
                        },
                    },
                )
                return

            try:
                result = await _TOOL_HANDLERS[tool_name](tool_args)
                await _send_json(
                    send,
                    {
                        "jsonrpc": "2.0",
                        "id": rpc_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, default=str),
                                }
                            ]
                        },
                    },
                )
            except Exception as exc:
                logger.exception("Tool '%s' handler error: %s", tool_name, exc)
                await _send_json(
                    send,
                    {
                        "jsonrpc": "2.0",
                        "id": rpc_id,
                        "error": {"code": -32603, "message": str(exc)},
                    },
                    status=500,
                )

        elif rpc_method == "tools/list":
            await _send_json(
                send,
                {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "result": {"tools": list(_TOOL_SPECS.values())},
                },
            )

        elif rpc_method == "initialize":
            await _send_json(
                send,
                {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "geox",
                            "version": "0.1.0",
                            "description": "GEOX Geological Intelligence Coprocessor for arifOS. DITEMPA BUKAN DIBERI.",
                        },
                    },
                },
            )

        else:
            await _send_json(
                send,
                {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{rpc_method}' not found.",
                    },
                },
                status=404,
            )
        return

    await _send_json(send, {"error": "Not found", "path": path}, status=404)


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="GEOX MCP Server — DITEMPA BUKAN DIBERI"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    parser.add_argument("--port", type=int, default=8100, help="Bind port")
    parser.add_argument("--log-level", default="info", help="Log level")
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level.upper())

    logger.info("=" * 60)
    logger.info("GEOX MCP Server v0.1.0 — DITEMPA BUKAN DIBERI")
    logger.info("Muhammad Arif bin Fazil | PETRONAS Exploration")
    logger.info("=" * 60)
    logger.info("Host: %s | Port: %d", args.host, args.port)
    logger.info("Endpoints:")
    logger.info("  GET  /health        — health check")
    logger.info("  GET  /mcp/tools      — list tools")
    logger.info("  POST /mcp           — MCP JSON-RPC dispatcher")
    logger.info("=" * 60)

    try:
        import uvicorn

        uvicorn.run(
            "server:app", host=args.host, port=args.port, log_level=args.log_level
        )
    except ImportError:
        logger.warning("uvicorn not installed — running minimal asyncio server")

        async def _serve() -> None:
            import os
            from asyncio import Event
            from functools import partial

            async def _asgi_handler(scope: dict, receive: Any, send: Any) -> None:
                await app(scope, receive, send)

            server = await asyncio.start_server(_asgi_handler, args.host, args.port)
            addr = server.sockets[0].getsockname()
            logger.info("Listening on %s", addr)
            logger.info("GEOX ready — DITEMPA BUKAN DIBERI")

            # Run health check to confirm init
            health = await _handle_geox_health({})
            logger.info("Health check: %s", health["status"])
            if _tool_registry:
                logger.info("Tools registered: %s", _tool_registry.list_tools())

            await Event().wait()

        asyncio.run(_serve())
