"""
arifOS API Application - FastAPI app factory.

This module provides the FastAPI application for the arifOS v51.2.0 API.
All endpoints are stateless, fail-open, and read-only or append-only.

Usage:
    # Development
    uvicorn arifos.core.integration.api.app:app --reload --host 0.0.0.0 --port 8000

    # Production
    uvicorn arifos.core.integration.api.app:app --host 0.0.0.0 --port 8000

    # In Python
    from arifos.core.integration.api import create_app
    app = create_app()
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

from .routes import health, pipeline, memory, ledger, metrics, federation, body
from .middleware import setup_middleware
from .exceptions import setup_exception_handlers

# SSE Integration
from arifos.mcp.sse import create_sse_app
from arifos.mcp.server import TOOL_DESCRIPTIONS, TOOL_ROUTERS as TOOLS

# MCP Server for direct endpoint
from mcp.server import Server
from mcp.server.sse import SseServerTransport
import mcp.types

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns a FastAPI app with:
    - All routes registered (health, pipeline, memory, ledger, metrics, body)
    - MCP SSE endpoints (/sse, /messages)
    - Middleware configured (CORS, logging)
    - Exception handlers set up
    """
    app = FastAPI(
        title="arifOS v51.2.0 API (The Body)",
        description=(
            "Constitutional Governance Oracle. "
            "Exposes the Trinity Metabolic Loop (AGI-ASI-APEX) over HTTP and SSE. "
            "DITEMPA BUKAN DIBERI."
        ),
        version="51.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Setup middleware (CORS, logging, etc.)
    setup_middleware(app)

    # Setup exception handlers
    setup_exception_handlers(app)

    # ==========================================================================
    # SOVEREIGN DASHBOARD (Phase 2)
    # ==========================================================================
    import os
    static_path = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/dashboard/static", StaticFiles(directory=static_path), name="static")

    @app.get("/dashboard", response_class=HTMLResponse)
    async def get_dashboard():
        """Serve the Sovereign Dashboard."""
        index_file = os.path.join(static_path, "index.html")
        with open(index_file, "r") as f:
            html_content = f.read()
            # Rewrite links to use the mounted /dashboard/static path
            html_content = html_content.replace('href="styles.css"', 'href="/dashboard/static/styles.css"')
            html_content = html_content.replace('src="app.js"', 'src="/dashboard/static/app.js"')
            return html_content

    # ==========================================================================
    # SECURITY: API KEY AUTHENTICATION
    # ==========================================================================
    @app.middleware("http")
    async def security_middleware(request: Request, call_next):
        """
        Global security middleware to enforce ARIFOS_API_KEY.
        Skips public routes (health, docs).
        """
        expected_key = os.environ.get("ARIFOS_API_KEY")
        if not expected_key:
            # Unsecured mode (warn in logs in real app, but for now just pass)
            return await call_next(request)

        # Allow public paths (health, docs, liveness probes)
        path = request.url.path
        public_paths = (
            path == "/" or
            path == "/health" or
            path == "/ready" or
            path == "/live" or
            path == "/v1/health" or
            path.startswith("/docs") or
            path.startswith("/redoc") or
            path.startswith("/openapi.json") or
            "/health" in path  # Catch-all for any health-related path
        )
        if public_paths:
            return await call_next(request)
            
        # Check Header
        client_key = request.headers.get("X-API-Key")
        # Check Query (useful for SSE/Browser)
        if not client_key:
            client_key = request.query_params.get("api_key")
            
        if client_key == expected_key:
             return await call_next(request)
             
        return JSONResponse(
            status_code=403, 
            content={"detail": "Access Denied: ARIFOS_API_KEY required"}
        )

    # Register route modules
    app.include_router(health.router)
    app.include_router(pipeline.router)
    app.include_router(memory.router)
    app.include_router(ledger.router)
    app.include_router(metrics.router)
    app.include_router(federation.router)
    app.include_router(body.router)

    # Register MCP SSE routes (sub-app for /sse and /messages endpoints)
    sse_app = create_sse_app()

    # ==========================================================================
    # CHATGPT DEVELOPER MODE: Direct /mcp endpoint
    # ChatGPT expects /mcp to be the SSE endpoint directly, not /mcp/sse
    # ==========================================================================
    mcp_server = Server("arifOS-Trinity-MCP")

    @mcp_server.list_tools()
    async def list_mcp_tools():
        tools_list = []
        for name in TOOLS:
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
    async def call_mcp_tool(name: str, arguments: dict):
        import inspect
        tool = TOOLS.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        if inspect.iscoroutinefunction(tool):
            return await tool(**arguments)
        return tool(**arguments)

    # SSE Transport for /mcp endpoint
    mcp_sse = SseServerTransport("/mcp")

    @app.get("/mcp")
    async def handle_mcp_get(request: Request):
        """MCP SSE Endpoint - ChatGPT Developer Mode compatible."""
        async with mcp_sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())

    @app.post("/mcp")
    async def handle_mcp_post(request: Request):
        """MCP Message Endpoint - ChatGPT Developer Mode compatible."""
        return await mcp_sse.handle_post_message(request.scope, request.receive, request._send)

    # Also mount the SSE sub-app at /sse for Claude Desktop compatibility
    app.mount("/sse", sse_app)

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> dict:
        """API root - returns version and basic info."""
        return {
            "name": "arifOS API",
            "version": "51.2.0",
            "description": "Constitutional Governance Oracle (The Body)",
            "docs": "/docs",
            "govern": "/v1/govern",
            "mcp_chatgpt": "/mcp",
            "mcp_claude": "/sse",
            "health": "/v1/health",
            "tools": list(TOOLS.keys()),
            "motto": "DITEMPA BUKAN DIBERI - Forged, not given",
        }

    return app


# Create the default app instance
app = create_app()


# =============================================================================
# OPTIONAL: CLI ENTRYPOINT
# =============================================================================

def main() -> None:
    """CLI entrypoint for running the server directly."""
    import uvicorn

    uvicorn.run(
        "arifos.core.integration.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
