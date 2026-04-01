#!/usr/bin/env python3
"""
GEOX MCP Server — DITEMPA BUKAN DIBERI

A unified MCP server for GEOX (Geological Intelligence Coprocessor).
Supports both STDIO (for Claude Desktop) and HTTP (for web/Prefect) transports.

Run:
    python server.py                    # STDIO mode
    python server.py --http             # HTTP mode on port 8100
    python server.py --port 8080        # HTTP on custom port

Author: Muhammad Arif bin Fazil <ariffazil@gmail.com>
License: AGPL-3.0
Status: PRE-PRODUCTION — API may change
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

# Configure logging before anything else
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("geox.server")

# =============================================================================
# Bootstrap — ensure arifos.geox is importable
# =============================================================================

_REPO_ROOT = Path(__file__).parent.resolve()
_ARIFOS_PATH = _REPO_ROOT / "arifos"

if _ARIFOS_PATH.exists() and str(_ARIFOS_PATH.parent) not in sys.path:
    sys.path.insert(0, str(_ARIFOS_PATH.parent))

# =============================================================================
# Import GEOX modules (with graceful fallback)
# =============================================================================

_HAS_GEOX = False
_GEOX_IMPORT_ERROR = None

try:
    from arifos.geox.geox_agent import GeoXAgent, GeoXConfig
    from arifos.geox.geox_memory import GeoMemoryStore
    from arifos.geox.geox_reporter import GeoXReporter
    from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest
    from arifos.geox.geox_tools import ToolRegistry
    from arifos.geox.geox_validator import GeoXValidator

    _HAS_GEOX = True
    logger.debug("GEOX modules loaded successfully")
except ImportError as exc:
    _GEOX_IMPORT_ERROR = str(exc)
    logger.warning("GEOX modules not available: %s", exc)
    logger.warning("Server will run in LIMITED MODE (health checks only)")

# =============================================================================
# Server State (singletons, lazy-initialized)
# =============================================================================

_config: GeoXConfig | None = None
_tool_registry: ToolRegistry | None = None
_validator: GeoXValidator | None = None
_memory_store: GeoMemoryStore | None = None
_reporter: GeoXReporter | None = None
_agent: GeoXAgent | None = None
_initialized = False
_SERVER_START_TIME = time.time()


def _ensure_init() -> None:
    """Lazy initialization of GEOX singletons."""
    global _initialized, _config, _tool_registry, _validator, _memory_store, _reporter, _agent

    if _initialized:
        return

    if not _HAS_GEOX:
        raise RuntimeError(f"GEOX modules not available: {_GEOX_IMPORT_ERROR}")

    try:
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
        logger.info("✅ GEOX initialized — DITEMPA BUKAN DIBERI")
    except Exception as exc:
        logger.exception("Failed to initialize GEOX: %s", exc)
        raise RuntimeError(f"GEOX initialization failed: {exc}") from exc


# =============================================================================
# Tool Specifications (JSON Schema for MCP)
# =============================================================================

_TOOL_SPECS: dict[str, dict[str, Any]] = {
    "geox_evaluate_prospect": {
        "name": "geox_evaluate_prospect",
        "description": (
            "Full GEOX geological prospect evaluation pipeline. "
            "Evaluates hydrocarbon prospectivity using multi-source data fusion "
            "(seismic, well logs, satellite, gravity). "
            "Returns verdict (SEAL/PARTIAL/SABAR/VOID), confidence, and geological insights. "
            "Requires human signoff for high-risk evaluations."
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
                    "minimum": -90,
                    "maximum": 90,
                },
                "longitude": {
                    "type": "number",
                    "description": "Prospect longitude in decimal degrees (WGS-84).",
                    "minimum": -180,
                    "maximum": 180,
                },
                "depth_m": {
                    "type": "number",
                    "description": "Target depth below surface in meters (optional).",
                    "minimum": 0,
                },
                "basin": {
                    "type": "string",
                    "description": "Sedimentary basin name (e.g., 'Malay Basin', 'North Sea').",
                },
                "play_type": {
                    "type": "string",
                    "description": "Geological play type.",
                    "enum": [
                        "stratigraphic",
                        "structural",
                        "combination",
                        "carbonate_buildup",
                        "deltaic",
                        "deep_water",
                        "unconventional",
                    ],
                },
                "available_data": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Available data types.",
                    "enum": [
                        ["seismic_2d", "seismic_3d", "well_logs", "core", "eo", "gravity", "magnetic"]
                    ],
                },
                "risk_tolerance": {
                    "type": "string",
                    "description": "Risk tolerance level.",
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
            "Supports semantic keyword search and optional basin filter. "
            "Returns up to `limit` most relevant memory entries with provenance."
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
                    "description": "Maximum number of results (default 5).",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 50,
                },
            },
            "required": ["query"],
        },
    },
    "geox_health": {
        "name": "geox_health",
        "description": (
            "GEOX server health check. Returns server status, tool registry health, "
            "memory store stats, and constitutional floor status. "
            "Use this to verify GEOX is ready before calling geox_evaluate_prospect."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
}


# =============================================================================
# Tool Handlers
# =============================================================================

async def _handle_geox_evaluate_prospect(args: dict[str, Any]) -> dict[str, Any]:
    """Handle geox_evaluate_prospect tool call."""
    _ensure_init()

    # Validate and build GeoRequest
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
        logger.error("Invalid GeoRequest parameters: %s", exc)
        return {
            "success": False,
            "error": f"Invalid parameters: {exc}",
            "verdict": "VOID",
            "constitutional_floor_violated": "F4",
        }

    # Execute evaluation pipeline
    try:
        response = await _agent.evaluate_prospect(request)  # type: ignore
    except Exception as exc:
        logger.exception("Pipeline execution failed: %s", exc)
        return {
            "success": False,
            "error": f"Pipeline error: {exc}",
            "verdict": "VOID",
        }

    # Store in memory (non-blocking, log failure)
    try:
        await _memory_store.store(response, request)  # type: ignore
    except Exception as exc:
        logger.warning("Memory store failed (non-critical): %s", exc)

    # Build response
    try:
        resp_dict = response.model_dump(mode="json")  # type: ignore
    except Exception as exc:
        logger.warning("Model dump failed, using fallback: %s", exc)
        resp_dict = {
            "response_id": getattr(response, "response_id", "unknown"),
            "request_id": getattr(response, "request_id", "unknown"),
            "verdict": getattr(response, "verdict", "VOID"),
            "confidence_aggregate": getattr(response, "confidence_aggregate", 0.0),
            "human_signoff_required": getattr(response, "human_signoff_required", True),
            "arifos_telemetry": getattr(response, "arifos_telemetry", {}),
            "insight_count": len(getattr(response, "insights", [])),
        }

    # Generate human-readable reports
    try:
        markdown_report = _reporter.generate_markdown_report(response, request)  # type: ignore
        human_brief = _reporter.generate_human_brief(response)  # type: ignore
    except Exception as exc:
        logger.warning("Report generation failed: %s", exc)
        markdown_report = None
        human_brief = None

    return {
        "success": True,
        "response": resp_dict,
        "verdict": getattr(response, "verdict", "VOID"),
        "confidence_aggregate": getattr(response, "confidence_aggregate", 0.0),
        "human_signoff_required": getattr(response, "human_signoff_required", True),
        "markdown_report": markdown_report,
        "human_brief": human_brief,
        "seal": "DITEMPA BUKAN DIBERI",
    }


async def _handle_geox_query_memory(args: dict[str, Any]) -> dict[str, Any]:
    """Handle geox_query_memory tool call."""
    _ensure_init()

    query = args.get("query", "")
    basin = args.get("basin")
    limit = min(int(args.get("limit", 5)), 50)  # Cap at 50

    try:
        entries = await _memory_store.retrieve(query, basin=basin, limit=limit)  # type: ignore
        return {
            "success": True,
            "count": len(entries),
            "entries": [e.to_dict() if hasattr(e, "to_dict") else dict(e) for e in entries],
        }
    except Exception as exc:
        logger.exception("Memory query failed: %s", exc)
        return {"success": False, "error": str(exc), "entries": []}


async def _handle_geox_health(_args: dict[str, Any]) -> dict[str, Any]:
    """Handle geox_health tool call."""
    uptime_s = round(time.time() - _SERVER_START_TIME, 1)

    # If GEOX not available, return limited health
    if not _HAS_GEOX:
        return {
            "success": True,
            "status": "limited",
            "version": "0.4.0",
            "mode": "health-check-only",
            "uptime_seconds": uptime_s,
            "geox_available": False,
            "error": _GEOX_IMPORT_ERROR,
            "constitutional_floors": ["F1", "F2", "F4", "F7", "F9", "F11", "F13"],
            "seal": "DITEMPA BUKAN DIBERI",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    _ensure_init()

    tool_health = {}
    registered_tools = []
    try:
        tool_health = _tool_registry.health_check_all() if _tool_registry else {}  # type: ignore
        registered_tools = _tool_registry.list_tools() if _tool_registry else []  # type: ignore
    except Exception as exc:
        logger.warning("Tool registry health check failed: %s", exc)

    return {
        "success": True,
        "status": "healthy",
        "version": "0.4.0",
        "mode": "full",
        "pipeline_id": getattr(_config, "pipeline_id", "unknown") if _config else "unknown",
        "uptime_seconds": uptime_s,
        "geox_available": True,
        "tool_registry": {
            "registered_tools": registered_tools,
            "health": tool_health,
            "all_healthy": all(tool_health.values()) if tool_health else False,
        },
        "memory_store": {
            "backend": "in_memory",  # TODO: detect actual backend
            "entry_count": _memory_store.count() if _memory_store else 0,  # type: ignore
            "basins": _memory_store.list_basins() if _memory_store else [],  # type: ignore
        },
        "constitutional_floors": ["F1", "F2", "F4", "F7", "F9", "F11", "F13"],
        "seal": "DITEMPA BUKAN DIBERI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


_TOOL_HANDLERS = {
    "geox_evaluate_prospect": _handle_geox_evaluate_prospect,
    "geox_query_memory": _handle_geox_query_memory,
    "geox_health": _handle_geox_health,
}


# =============================================================================
# FastMCP Integration (preferred)
# =============================================================================

def _build_fastmcp_app() -> Any:
    """Build FastMCP app if available."""
    try:
        from fastmcp import FastMCP

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
            """Full GEOX geological prospect evaluation pipeline."""
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
            """Query the GEOX geological memory store."""
            return await _handle_geox_query_memory({"query": query, "basin": basin, "limit": limit})

        @mcp.tool()
        async def geox_health() -> dict[str, Any]:
            """GEOX server health check."""
            return await _handle_geox_health({})

        return mcp

    except ImportError:
        return None


# =============================================================================
# HTTP ASGI Application (fallback)
# =============================================================================

async def _send_json(send: Any, data: dict[str, Any], status: int = 200) -> None:
    """Send JSON response via ASGI."""
    body = json.dumps(data, default=str, ensure_ascii=False).encode("utf-8")
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            [b"content-type", b"application/json"],
            [b"content-length", str(len(body)).encode()],
            [b"access-control-allow-origin", b"*"],
        ],
    })
    await send({"type": "http.response.body", "body": body})


async def asgi_app(scope: dict, receive: Any, send: Any) -> None:
    """
    ASGI application implementing MCP JSON-RPC 2.0 protocol.
    
    Endpoints:
      GET  /health       → Health check
      GET  /mcp/tools    → List available tools
      POST /mcp          → MCP JSON-RPC dispatcher
    """
    if scope["type"] != "http":
        return

    method = scope.get("method", "GET")
    path = scope.get("path", "/")

    # Read body
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
        await _send_json(send, {
            "tools": list(_TOOL_SPECS.values()),
            "server": "geox-mcp-v0.4.0",
            "geox_available": _HAS_GEOX,
            "seal": "DITEMPA BUKAN DIBERI",
        })
        return

    # POST /mcp (JSON-RPC)
    if path == "/mcp" and method == "POST":
        try:
            rpc = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            await _send_json(send, {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }, status=400)
            return

        rpc_id = rpc.get("id")
        rpc_method = rpc.get("method", "")
        rpc_params = rpc.get("params", {})

        # tools/call
        if rpc_method == "tools/call":
            tool_name = rpc_params.get("name")
            tool_args = rpc_params.get("arguments", {})

            if tool_name not in _TOOL_HANDLERS:
                await _send_json(send, {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found",
                        "data": {"available": list(_TOOL_HANDLERS.keys())},
                    },
                })
                return

            try:
                result = await _TOOL_HANDLERS[tool_name](tool_args)
                await _send_json(send, {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, default=str)}]
                    },
                })
            except Exception as exc:
                logger.exception("Tool '%s' error: %s", tool_name, exc)
                await _send_json(send, {
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {"code": -32603, "message": str(exc)},
                }, status=500)
            return

        # tools/list
        if rpc_method == "tools/list":
            await _send_json(send, {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {"tools": list(_TOOL_SPECS.values())},
            })
            return

        # initialize
        if rpc_method == "initialize":
            await _send_json(send, {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "geox",
                        "version": "0.4.0",
                        "description": "GEOX Geological Intelligence Coprocessor. DITEMPA BUKAN DIBERI.",
                    },
                },
            })
            return

        # Unknown method
        await _send_json(send, {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {"code": -32601, "message": f"Method '{rpc_method}' not found"},
        }, status=404)
        return

    # Not found
    await _send_json(send, {"error": "Not found", "path": path}, status=404)


# =============================================================================
# STDIO MCP Server (low-level fallback)
# =============================================================================

async def _run_stdio_server() -> None:
    """Run STDIO MCP server (for Claude Desktop, etc.)."""
    try:
        from mcp.server import Server
        from mcp.types import Tool, TextContent
        from mcp.server.stdio import stdio_server

        app = Server("geox-mcp")

        @app.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name=spec["name"],
                    description=spec["description"],
                    inputSchema=spec["inputSchema"],
                )
                for spec in _TOOL_SPECS.values()
            ]

        @app.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            if name not in _TOOL_HANDLERS:
                return [TextContent(type="text", text=json.dumps({
                    "error": f"Unknown tool: {name}", "success": False
                }))]
            
            result = await _TOOL_HANDLERS[name](arguments)
            return [TextContent(type="text", text=json.dumps(result, default=str))]

        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())

    except ImportError as exc:
        logger.error("MCP SDK not installed: %s", exc)
        logger.error("Install: pip install mcp")
        sys.exit(1)


# =============================================================================
# Main Entrypoint
# =============================================================================

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="GEOX MCP Server — DITEMPA BUKAN DIBERI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python server.py                    # Run in STDIO mode (Claude Desktop)
  python server.py --http             # Run HTTP server on port 8100
  python server.py --http --port 8080 # HTTP on custom port
  python server.py --log-level debug  # Verbose logging

Environment:
  LOG_LEVEL=debug                     # Set logging level
  GEOX_CONFIG=/path/to/config.yaml    # Custom config file
        """
    )
    parser.add_argument("--http", action="store_true", help="Use HTTP transport (default: STDIO)")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8100, help="HTTP bind port (default: 8100)")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"],
                        help="Logging level (default: info)")
    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(args.log_level.upper())

    # Banner
    logger.info("=" * 60)
    logger.info("GEOX MCP Server v0.4.0 — DITEMPA BUKAN DIBERI")
    logger.info("Muhammad Arif bin Fazil | PETRONAS Exploration")
    logger.info("Status: PRE-PRODUCTION — API may change")
    logger.info("=" * 60)

    if args.http:
        # HTTP mode
        logger.info("Mode: HTTP transport")
        logger.info("Host: %s | Port: %d", args.host, args.port)
        logger.info("Endpoints:")
        logger.info("  GET  /health       → Health check")
        logger.info("  GET  /mcp/tools    → List tools")
        logger.info("  POST /mcp          → MCP JSON-RPC")
        logger.info("=" * 60)

        # Try FastMCP first, fall back to ASGI
        fastmcp_app = _build_fastmcp_app()
        
        if fastmcp_app is not None:
            logger.info("Using FastMCP transport")
            try:
                import uvicorn
                uvicorn.run(fastmcp_app, host=args.host, port=args.port, log_level=args.log_level)
            except ImportError:
                logger.error("uvicorn not installed. Install: pip install uvicorn")
                sys.exit(1)
        else:
            logger.info("Using native ASGI transport (FastMCP not available)")
            try:
                import uvicorn
                uvicorn.run(asgi_app, host=args.host, port=args.port, log_level=args.log_level)
            except ImportError:
                logger.warning("uvicorn not installed, using minimal asyncio server")
                await _run_minimal_http_server(args.host, args.port)
    else:
        # STDIO mode
        logger.info("Mode: STDIO transport (MCP)")
        logger.info("Ready for Claude Desktop or similar MCP clients")
        logger.info("=" * 60)

        # Try FastMCP first
        fastmcp_app = _build_fastmcp_app()
        if fastmcp_app is not None:
            logger.info("Using FastMCP STDIO transport")
            fastmcp_app.run()
        else:
            logger.info("Using native MCP SDK STDIO transport")
            await _run_stdio_server()


async def _run_minimal_http_server(host: str, port: int) -> None:
    """Minimal asyncio HTTP server (no uvicorn)."""
    from asyncio import Event
    
    async def _handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        # Minimal HTTP handler (for health checks only)
        data = await reader.read(8192)
        try:
            lines = data.decode().split("\r\n")
            if lines:
                parts = lines[0].split()
                if len(parts) >= 2:
                    method, path = parts[0], parts[1]
                    if path == "/health" and method == "GET":
                        result = await _handle_geox_health({})
                        body = json.dumps(result).encode()
                        response = (
                            b"HTTP/1.1 200 OK\r\n"
                            b"Content-Type: application/json\r\n"
                            b"Access-Control-Allow-Origin: *\r\n"
                            b"Content-Length: " + str(len(body)).encode() + b"\r\n"
                            b"\r\n" + body
                        )
                    else:
                        response = b"HTTP/1.1 404 Not Found\r\n\r\n"
                else:
                    response = b"HTTP/1.1 400 Bad Request\r\n\r\n"
            else:
                response = b"HTTP/1.1 400 Bad Request\r\n\r\n"
        except Exception:
            response = b"HTTP/1.1 500 Internal Server Error\r\n\r\n"
        
        writer.write(response)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(_handler, host, port)
    addr = server.sockets[0].getsockname()
    logger.info("Minimal HTTP server listening on %s", addr)
    logger.info("GEOX ready — DITEMPA BUKAN DIBERI")
    
    await Event().wait()


# =============================================================================
# Entrypoint
# =============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 GEOX server stopped by user")
        sys.exit(0)
    except Exception as exc:
        logger.exception("Fatal error: %s", exc)
        sys.exit(1)
