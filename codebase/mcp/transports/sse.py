"""
arifOS MCP Streamable HTTP Transport (FastMCP)
HTTP transport for remote clients and production deployment.

v55.1: Streamable HTTP (spec 2025-03-26+), stateless mode,
       localhost binding for local dev.
"""

import os
import logging
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

from .base import BaseTransport
from ..core.tool_registry import ToolRegistry
from ..services.rate_limiter import rate_limited
from ..services.constitutional_metrics import get_full_metrics

logger = logging.getLogger(__name__)

# Security: bind to localhost for local dev, 0.0.0.0 only when HOST env is set
_DEFAULT_HOST = os.getenv("HOST", "127.0.0.1")
_DEFAULT_PORT = int(os.getenv("PORT", 8000))


class SSETransport(BaseTransport):
    """Streamable HTTP Transport implementation using FastMCP."""

    def __init__(self, tool_registry: ToolRegistry):
        super().__init__(tool_registry)
        self.mcp = FastMCP(
            "AAA-MCP-CODEBASE",
            host=_DEFAULT_HOST,
            port=_DEFAULT_PORT,
            stateless_http=True,
            json_response=True,
        )
        self._register_routes()

    @property
    def name(self) -> str:
        return "streamable-http"

    async def start(self) -> None:
        """Start the FastMCP server with Streamable HTTP transport."""
        # Register tools dynamically
        for tool_name, tool_def in self.tool_registry.list_tools().items():
            # Apply constitutionally mandated rate limiting
            handler = rate_limited(tool_name)(tool_def.handler)

            # FastMCP tool registration
            self.mcp.add_tool(
                handler,
                name=tool_def.name,
                description=tool_def.description,
            )
            logger.info(f"Registered HTTP tool: {tool_name}")

        # Phase 3: Register MCP Resources
        self._register_resources()

        logger.info(f"Starting Streamable HTTP Transport on {_DEFAULT_HOST}:{_DEFAULT_PORT}")

        # Run using uvicorn programmatically
        config = uvicorn.Config(
            self.mcp._asgi_app,
            host=_DEFAULT_HOST,
            port=_DEFAULT_PORT,
            log_level="info",
            loop="asyncio",
        )
        server = uvicorn.Server(config)
        await server.serve()

    async def stop(self) -> None:
        # Uvicorn handles shutdown on signal
        pass

    async def send_response(self, request_id: str, response: dict) -> None:
        pass  # Handled internally

    def _register_routes(self):
        """Register custom routes (Health, Metrics)."""

        @self.mcp.custom_route("/health", methods=["GET"])
        async def health_check(request):
            return JSONResponse(
                {
                    "status": "healthy",
                    "version": "v55.1-AAA",
                    "mode": "CODEBASE",
                    "transport": "streamable-http",
                    "tools": len(self.tool_registry.list_tools()),
                }
            )

        @self.mcp.custom_route("/metrics/json", methods=["GET"])
        async def metrics_endpoint(request):
            return JSONResponse(get_full_metrics())

    def _register_resources(self):
        """Register MCP Resources for FastMCP."""
        # Register static resources
        for res_def in self.resource_registry.list_resources():
            # Use FastMCP's resource decorator pattern
            self.mcp.add_resource(
                uri=res_def.uri,
                name=res_def.name,
                description=res_def.description,
                mime_type=res_def.mime_type,
                handler=lambda uri=res_def.uri: self.resource_registry.read_resource(uri),
            )
            logger.info(f"Registered resource: {res_def.uri}")

        # Register prompts
        self._register_prompts()

    def _register_prompts(self):
        """Register MCP Prompts for FastMCP."""
        for prompt_def in self.prompt_registry.list_prompts():
            self.mcp.add_prompt(
                name=prompt_def.name,
                description=prompt_def.description,
                handler=lambda name=prompt_def.name: self.prompt_registry.render_prompt(name),
            )
            logger.info(f"Registered prompt: {prompt_def.name}")
