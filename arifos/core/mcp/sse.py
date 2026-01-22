"""
arifOS SSE Web Adapter (v50.5.0)
Cloud Bridge for MCP Protocol via Server-Sent Events

Supports both:
- Unified 16-tool server (unified_server.py)
- Trinity 5-tool server (trinity_server.py)

DITEMPA BUKAN DIBERI
"""
import logging
import os
from typing import Any, Callable, Dict, Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Configure logging early
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# SSE APP FACTORY (Reusable for any tool set)
# =============================================================================

def create_sse_app(
    tools: Dict[str, Callable],
    tool_descriptions: Dict[str, Dict[str, Any]],
    server_name: str = "arifOS-MCP",
    version: str = "v50.5.0"
) -> FastAPI:
    """
    Create a FastAPI app with MCP SSE endpoints.

    Args:
        tools: Dict mapping tool names to callable functions
        tool_descriptions: Dict with MCP-compliant tool descriptions
        server_name: Name of the server
        version: Version string

    Returns:
        FastAPI app with /sse, /messages, /health endpoints
    """
    from mcp.server import Server
    from mcp.server.sse import SseServerTransport
    import mcp.types

    tools_count = len(tools)

    # Create MCP Server
    mcp_server = Server(server_name)

    @mcp_server.list_tools()
    async def list_tools():
        tools_list = []
        for name in tools:
            desc = tool_descriptions.get(name, {})
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
        tool = tools.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")

        try:
            import inspect
            if inspect.iscoroutinefunction(tool):
                return await tool(**arguments)
            else:
                return tool(**arguments)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return {"status": "VOID", "error": str(e), "tool": name}

    # Create FastAPI app
    app = FastAPI(
        title=f"{server_name} Cloud Interface",
        description=f"Constitutional Cloud Bridge. Exposes {tools_count} MCP tools via SSE.",
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
        return {
            "status": "healthy",
            "mode": "SSE",
            "server": server_name,
            "tools": tools_count,
            "tool_names": list(tools.keys()),
            "version": version,
            "framework": "arifOS Constitutional Kernel",
            "doc_url": "/docs"
        }

    @app.get("/")
    async def handle_root():
        """Root endpoint with service info."""
        return {
            "service": server_name,
            "version": version,
            "status": "healthy",
            "tools": tools_count,
            "tool_names": list(tools.keys()),
            "endpoints": {
                "/health": "Health check (Railway)",
                "/sse": "MCP SSE connection",
                "/messages": "MCP message handler",
                "/docs": "API documentation"
            },
            "constitutional_framework": "DITEMPA BUKAN DIBERI"
        }

    return app


# =============================================================================
# LEGACY: Default unified server SSE (16 tools)
# =============================================================================

# Only create default app when imported directly (not via create_sse_app)
_default_app: Optional[FastAPI] = None

def _get_default_app() -> FastAPI:
    """Lazy-load the default unified server app."""
    global _default_app
    if _default_app is None:
        try:
            from arifos.core.mcp.unified_server import TOOLS, TOOL_DESCRIPTIONS
            _default_app = create_sse_app(
                tools=TOOLS,
                tool_descriptions=TOOL_DESCRIPTIONS,
                server_name="arifOS-Unified",
                version="v50.5.0"
            )
            logger.info(f"✅ Default SSE app created with {len(TOOLS)} tools")
        except ImportError as e:
            logger.error(f"❌ Failed to import unified_server: {e}")
            # Create minimal fallback app
            _default_app = FastAPI(title="arifOS (Degraded)")

            @_default_app.get("/health")
            async def degraded_health():
                return {"status": "degraded", "error": "unified_server import failed"}

            @_default_app.get("/")
            async def degraded_root():
                return {"status": "degraded", "error": "unified_server import failed"}

    return _default_app


# For backward compatibility: expose app at module level
app = property(lambda self: _get_default_app())


def main():
    """Run the default unified server via SSE."""
    port = int(os.environ.get("PORT", os.environ.get("AAA_MCP_PORT", 8000)))
    logger.info(f"Starting arifOS SSE Server v50.5.0 on port {port}...")

    fastapi_app = _get_default_app()
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
