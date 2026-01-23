"""
arifOS API Application - FastAPI app factory.

This module provides the FastAPI application for the arifOS v38.2 API.
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

from fastapi import FastAPI

from .routes import health, pipeline, memory, ledger, metrics, federation, body
from .middleware import setup_middleware
from .exceptions import setup_exception_handlers

# SSE Integration
from arifos.mcp.sse import create_sse_app
from arifos.mcp.trinity_server import TOOLS, TOOL_DESCRIPTIONS

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
        title="arifOS v50.5.24 API (The Body)",
        description=(
            "Constitutional Governance Oracle. "
            "Exposes the Trinity Metabolic Loop (AGI-ASI-APEX) over HTTP and SSE. "
            "DITEMPA BUKAN DIBERI."
        ),
        version="50.5.24",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Setup middleware (CORS, logging, etc.)
    setup_middleware(app)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Register route modules
    app.include_router(health.router)
    app.include_router(pipeline.router)
    app.include_router(memory.router)
    app.include_router(ledger.router)
    app.include_router(metrics.router)
    app.include_router(federation.router)
    app.include_router(body.router)

    # Register MCP SSE routes
    sse_app = create_sse_app(
        tools=TOOLS,
        tool_descriptions=TOOL_DESCRIPTIONS,
        server_name="arifOS-Trinity",
        version="50.5.24"
    )
    # Mount SSE sub-app or manually proxy?
    # Simpler: just use the routes from sse_app
    app.mount("/mcp", sse_app)

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> dict:
        """API root - returns version and basic info."""
        return {
            "name": "arifOS API",
            "version": "50.5.24",
            "description": "Constitutional Governance Oracle (The Body)",
            "docs": "/docs",
            "govern": "/v1/govern",
            "mcp_sse": "/mcp/sse",
            "health": "/v1/health",
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
