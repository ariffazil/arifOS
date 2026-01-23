"""
arifOS SSE Web Adapter (v50.5.1)
Cloud Bridge for MCP Protocol via Server-Sent Events

5-Tool Trinity Constitutional Framework

DITEMPA BUKAN DIBERI
"""
import logging
import os
from typing import Any, Callable, Dict

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
    version: str = "v50.5.1"
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
        from arifos.mcp.metrics import get_metrics
        from arifos.mcp.rate_limiter import get_rate_limiter

        metrics = get_metrics()
        rate_limiter = get_rate_limiter()

        return {
            "status": "healthy",
            "mode": "SSE",
            "server": server_name,
            "tools": tools_count,
            "tool_names": list(tools.keys()),
            "version": version,
            "framework": "arifOS Constitutional Kernel",
            "doc_url": "/docs",
            "rate_limiter": rate_limiter.get_stats(),
            "metrics_summary": {
                "active_sessions": metrics.active_sessions.get(),
                "total_requests": sum(metrics.requests_total._values.values()),
            }
        }

    @app.get("/metrics")
    async def handle_metrics():
        """Prometheus-compatible metrics endpoint."""
        from fastapi.responses import PlainTextResponse
        from arifos.mcp.metrics import get_metrics

        metrics = get_metrics()
        return PlainTextResponse(
            content=metrics.get_prometheus_output(),
            media_type="text/plain; version=0.0.4"
        )

    @app.get("/metrics/json")
    async def handle_metrics_json():
        """JSON metrics endpoint for debugging."""
        from arifos.mcp.metrics import get_metrics

        metrics = get_metrics()
        return metrics.get_stats()

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
                "/metrics": "Prometheus metrics",
                "/metrics/json": "Metrics as JSON",
                "/sse": "MCP SSE connection",
                "/messages": "MCP message handler",
                "/docs": "API documentation"
            },
            "constitutional_framework": "DITEMPA BUKAN DIBERI"
        }

    return app


def main():
    """Run the Trinity server via SSE (default entry point)."""
    from arifos.mcp.trinity_server import TOOLS, TOOL_DESCRIPTIONS

    port = int(os.environ.get("PORT", os.environ.get("AAA_MCP_PORT", 8000)))
    logger.info(f"Starting arifOS Trinity SSE Server v50.5.1 on port {port}...")

    app = create_sse_app(
        tools=TOOLS,
        tool_descriptions=TOOL_DESCRIPTIONS,
        server_name="arifOS-Trinity",
        version="v50.5.1"
    )
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
