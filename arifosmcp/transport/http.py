"""
Streamable HTTP Transport Entrypoint
═════════════════════════════════════
Runs the arifOS MCP server over streamable HTTP (stateless).
"""
from __future__ import annotations

import os

import uvicorn
from starlette.middleware.cors import CORSMiddleware

from arifosmcp.server import mcp, GlobalPanicMiddleware


def create_http_app():
    """Create and configure the HTTP ASGI app with gateway endpoints."""
    app = mcp.http_app(stateless_http=True)

    app.add_middleware(GlobalPanicMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["X-API-Key", "Content-Type", "Authorization", "X-MCP-Protocol"],
    )
    return app


def run_http(host: str = "0.0.0.0", port: int | None = None) -> None:
    """Run the MCP server over streamable HTTP."""
    if port is None:
        port = int(os.getenv("ARIFOS_PORT", "8080"))

    app = create_http_app()
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        timeout_graceful_shutdown=2,
        lifespan="on",
        log_level="info",
    )
    server = uvicorn.Server(config)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_http()
