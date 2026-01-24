"""
AAA MCP SSE Web Adapter (v51.0.0)
Cloud Bridge for MCP Protocol via Server-Sent Events

Usage:
  uvicorn AAA_MCP.sse:app --host 0.0.0.0 --port $PORT

DITEMPA BUKAN DIBERI
"""
import logging
import os
from typing import Any, Callable, Dict

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import bridge routers
from AAA_MCP.bridge import (
    ENGINES_AVAILABLE,
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
)
from AAA_MCP.server import TOOL_DESCRIPTIONS
from arifos.core.enforcement.governance.rate_limiter import get_rate_limiter


# =============================================================================
# TOOL ROUTER MAPPING
# =============================================================================

TOOL_ROUTERS = {
    "000_init": bridge_init_router,
    "agi_genius": bridge_agi_router,
    "asi_act": bridge_asi_router,
    "apex_judge": bridge_apex_router,
    "999_vault": bridge_vault_router,
}


# =============================================================================
# SSE APP CREATION
# =============================================================================

def create_aaa_sse_app() -> FastAPI:
    """
    Create a FastAPI app with MCP SSE endpoints for AAA.

    Returns:
        FastAPI app with /sse, /messages, /health, /mcp endpoints
    """
    from mcp.server import Server
    from mcp.server.sse import SseServerTransport
    import mcp.types

    server_name = "AAA-MCP"
    version = "v51.0"
    tools_count = len(TOOL_ROUTERS)

    # Create MCP Server
    mcp_server = Server(server_name)

    @mcp_server.list_tools()
    async def list_tools():
        tools_list = []
        for name in TOOL_ROUTERS:
            desc = TOOL_DESCRIPTIONS.get(name, {})
            tools_list.append(
                mcp.types.Tool(
                    name=name,
                    description=desc.get("description", f"Tool {name}"),
                    inputSchema=desc.get("inputSchema", {"type": "object", "properties": {}})
                )
            )
        return tools_list

    @mcp_server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]):
        router = TOOL_ROUTERS.get(name)
        if not router:
            raise ValueError(f"Unknown tool: {name}")

        # F11: Rate limit check (Command Authority floor)
        session_id = arguments.get("session_id", "")
        rate_limiter = get_rate_limiter()
        rate_result = rate_limiter.check(name, session_id)
        if not rate_result.allowed:
            logger.warning(f"Rate limit exceeded for {name}: {rate_result.reason}")
            return {
                "status": "VOID",
                "reason": rate_result.reason,
                "rate_limit": {
                    "exceeded": True,
                    "limit_type": rate_result.limit_type,
                    "reset_in_seconds": rate_result.reset_in_seconds
                },
                "floors_checked": ["F11_CommandAuth"]
            }

        # Extract action and remove from arguments to avoid passing twice
        action = arguments.pop("action", "full")
        try:
            return router(action=action, **arguments)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return {"status": "VOID", "error": str(e), "tool": name}

    # Create FastAPI app
    app = FastAPI(
        title=f"{server_name} Cloud Interface",
        description=f"AAA MCP Constitutional Cloud Bridge. {tools_count} tools via SSE.",
        version=version,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS for remote access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # SSE Transport
    sse = SseServerTransport("/messages")

    @app.get("/sse")
    async def handle_sse(request: Request):
        """SSE Endpoint for MCP Protocol connection."""
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())

    @app.post("/messages")
    async def handle_messages(request: Request):
        """Message endpoint for MCP protocol."""
        return await sse.handle_post_message(request.scope, request.receive, request._send)

    @app.get("/health")
    async def handle_health():
        """Health Check Endpoint - Railway requires this."""
        from arifos.core.enforcement.governance.rate_limiter import get_rate_limiter

        rate_limiter = get_rate_limiter()

        return {
            "status": "healthy",
            "mode": "SSE",
            "server": server_name,
            "tools": tools_count,
            "tool_names": list(TOOL_ROUTERS.keys()),
            "version": version,
            "engines_available": ENGINES_AVAILABLE,
            "framework": "arifOS Constitutional Kernel",
            "doc_url": "/docs",
            "rate_limiter": rate_limiter.get_stats()
        }

    @app.get("/")
    async def handle_root():
        """Root endpoint with service info."""
        return {
            "service": server_name,
            "version": version,
            "status": "healthy",
            "tools": tools_count,
            "tool_names": list(TOOL_ROUTERS.keys()),
            "engines_available": ENGINES_AVAILABLE,
            "endpoints": {
                "/health": "Health check (Railway)",
                "/sse": "MCP SSE connection",
                "/mcp": "MCP SSE connection (ChatGPT compatible)",
                "/messages": "MCP message handler",
                "/docs": "API documentation"
            },
            "motto": "DITEMPA BUKAN DIBERI"
        }

    # ==========================================================================
    # CHATGPT DEVELOPER MODE COMPATIBILITY
    # ==========================================================================

    @app.get("/mcp")
    async def handle_mcp_sse(request: Request):
        """MCP SSE Endpoint - ChatGPT Developer Mode compatible."""
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())

    @app.post("/mcp")
    async def handle_mcp_messages(request: Request):
        """MCP Message endpoint - ChatGPT Developer Mode compatible."""
        return await sse.handle_post_message(request.scope, request.receive, request._send)

    return app


# =============================================================================
# APP INSTANCE (for uvicorn)
# =============================================================================

app = create_aaa_sse_app()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Run the AAA MCP server via SSE."""
    port = int(os.environ.get("PORT", os.environ.get("AAA_MCP_PORT", 8000)))

    logger.info("=" * 70)
    logger.info("AAA MCP SERVER (v51.0) - Constitutional Intelligence")
    logger.info("Artifact · Authority · Architecture")
    logger.info("=" * 70)
    logger.info(f"Mode: SSE")
    logger.info(f"Port: {port}")
    logger.info(f"Tools: {list(TOOL_ROUTERS.keys())}")
    logger.info(f"Engines: {'Available' if ENGINES_AVAILABLE else 'Fallback'}")
    logger.info("=" * 70)

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
