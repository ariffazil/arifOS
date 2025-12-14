"""
arifOS API Application - FastAPI app factory.

This module provides the FastAPI application for the arifOS v38.2 API.
All endpoints are stateless, fail-open, and read-only or append-only.

Usage:
    # Development
    uvicorn arifos_core.api.app:app --reload --host 0.0.0.0 --port 8000

    # Production
    uvicorn arifos_core.api.app:app --host 0.0.0.0 --port 8000

    # In Python
    from arifos_core.api import create_app
    app = create_app()
"""

from __future__ import annotations

from fastapi import FastAPI

from .routes import health, pipeline, memory, ledger, metrics, federation
from .middleware import setup_middleware
from .exceptions import setup_exception_handlers


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns a FastAPI app with:
    - All routes registered (health, pipeline, memory, ledger, metrics)
    - Middleware configured (CORS, logging)
    - Exception handlers set up
    """
    app = FastAPI(
        title="arifOS v41.3 API",
        description=(
            "Constitutional Governance API for AI. "
            "Wraps the governed pipeline with 9 constitutional floors, "
            "L7 Federation Router (multi-endpoint SEA-LION), "
            "L7 memory (Mem0 + Qdrant), and cooling ledger access."
        ),
        version="0.2.0",
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

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root() -> dict:
        """API root - returns version and basic info."""
        return {
            "name": "arifOS API",
            "version": "v41.3Omega",
            "description": "Constitutional Governance API for AI",
            "docs": "/docs",
            "health": "/health",
            "federation": "/federation/status",
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
        "arifos_core.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
