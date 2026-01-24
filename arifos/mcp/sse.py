"""
arifOS MCP SSE Adapter (v52.0.0)
Cloud Bridge for MCP Protocol via Server-Sent Events

Usage:
  python -m arifos.mcp trinity-sse
  uvicorn arifos.mcp.sse:app --host 0.0.0.0 --port $PORT

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations
import logging
import os
import time
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mcp.server import Server
from mcp.server.sse import SseServerTransport

from arifos.mcp.bridge import ENGINES_AVAILABLE
from arifos.mcp.server import TOOL_DESCRIPTIONS, TOOL_ROUTERS
from arifos.core.enforcement.governance.rate_limiter import get_rate_limiter
from arifos.mcp.mode_selector import get_mcp_mode, MCPMode
from arifos.mcp.constitutional_metrics import record_verdict, get_seal_rate

logger = logging.getLogger(__name__)

def create_sse_app(mode: Optional[MCPMode] = None) -> FastAPI:
    """Create FastAPI app with MCP SSE endpoints."""
    if mode is None:
        mode = get_mcp_mode()
    
    server_name = f"arifOS-MCP-{mode.value}"
    version = "v52.0.0"
    
    # Create MCP Server
    mcp_server = Server(server_name)

    @mcp_server.list_tools()
    async def list_tools():
        import mcp.types
        return [
            mcp.types.Tool(
                name=name,
                description=desc["description"],
                inputSchema=desc["inputSchema"]
            )
            for name, desc in TOOL_DESCRIPTIONS.items()
        ]

    @mcp_server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]):
        router = TOOL_ROUTERS.get(name)
        if not router:
            raise ValueError(f"Unknown tool: {name}")

        # F11: Rate Limit Check
        session_id = arguments.get("session_id", "anonymous")
        limiter = get_rate_limiter()
        rate_result = limiter.check(name, session_id)
        
        if not rate_result.allowed:
            return {
                "status": "VOID",
                "verdict": "VOID",
                "reason": rate_result.reason,
                "violation": rate_result.constitutional_violation
            }

        start = time.time()
        try:
            action = arguments.pop("action", "full")
            result = await router(action=action, **arguments)
            
            # Record metrics
            duration = time.time() - start
            record_verdict(
                tool=name,
                verdict=result.get("verdict", "UNKNOWN"),
                duration=duration,
                mode=mode.value
            )
            return result
        except Exception as e:
            logger.error(f"Execution error in {name}: {e}")
            return {"status": "ERROR", "error": str(e), "tool": name}

    # Create FastAPI app
    app = FastAPI(title=server_name, version=version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    sse = SseServerTransport("/messages")

    @app.get("/sse")
    async def handle_sse(request: Request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())

    @app.post("/messages")
    async def handle_messages(request: Request):
        return await sse.handle_post_message(request.scope, request.receive, request._send)

    @app.get("/health")
    async def handle_health():
        seal_rate = get_seal_rate()
        return {
            "status": "healthy" if seal_rate > 0.75 else "degraded",
            "mode": mode.value,
            "seal_rate_1h": seal_rate,
            "version": version,
            "engines_available": ENGINES_AVAILABLE,
            "timestamp": time.time()
        }

    @app.get("/")
    async def handle_root():
        return {
            "service": server_name,
            "version": version,
            "status": "healthy",
            "mode": mode.value,
            "motto": "DITEMPA BUKAN DIBERI"
        }

    return app

# Default app instance
app = create_sse_app()