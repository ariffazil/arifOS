"""
arifOS MCP Streamable HTTP Transport (FastMCP)
HTTP transport for remote clients and production deployment.

v55.1: Streamable HTTP (spec 2025-03-26+), stateless mode,
       localhost binding for local dev.
       Fixed resource/prompt registration to use FastMCP types.
"""

import os
import logging
import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.resources import FunctionResource
from mcp.server.fastmcp.prompts import Prompt as FastMCPPrompt
from starlette.responses import JSONResponse, HTMLResponse

from .base import BaseTransport
from ..core.tool_registry import ToolRegistry
from ..services.rate_limiter import rate_limited
from ..services.constitutional_metrics import get_full_metrics

logger = logging.getLogger(__name__)

# Security: bind to localhost for local dev, 0.0.0.0 only when HOST env is set
_DEFAULT_HOST = os.getenv("HOST", "127.0.0.1")
_DEFAULT_PORT = int(os.getenv("PORT", 8080))


# Dashboard HTML as a constant to avoid escape issues
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>arifOS - Constitutional AI Governance</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 800px; margin: 40px auto; padding: 20px; 
               background: #0d1117; color: #e6edf3; line-height: 1.6; }
        h1 { color: #58a6ff; font-size: 2.5rem; }
        .badge { display: inline-block; background: #238636; color: white; 
                 padding: 8px 16px; border-radius: 20px; font-weight: 600; }
        a { color: #58a6ff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        ul { line-height: 2; }
        .motto { color: #d29922; font-style: italic; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>arifOS</h1>
    <p><span class="badge">v55.1 ONLINE</span></p>
    <p>Constitutional AI Governance System</p>
    <hr>
    <ul>
        <li><a href="/health">Health Check (JSON)</a></li>
        <li><a href="/metrics/json">Metrics (JSON)</a></li>
    </ul>
    <p class="motto">DITEMPA BUKAN DIBERI - Forged, Not Given</p>
</body>
</html>"""


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

        # Register MCP Resources and Prompts
        self._register_resources()
        self._register_prompts()

        logger.info(f"Starting Streamable HTTP Transport on {_DEFAULT_HOST}:{_DEFAULT_PORT}")

        # Run using uvicorn programmatically
        asgi_app = self.mcp.streamable_http_app()
        config = uvicorn.Config(
            asgi_app,
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
        """Register custom routes (Health, Metrics, Dashboard)."""

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

        @self.mcp.custom_route("/", methods=["GET"])
        async def root(request):
            """Root endpoint - serve the arifOS dashboard."""
            return HTMLResponse(content=DASHBOARD_HTML)

    def _register_resources(self):
        """Register MCP Resources using FastMCP FunctionResource."""
        for res_def in self.resource_registry.list_resources():
            # Capture uri in closure to avoid late-binding bug
            uri = res_def.uri
            resource = FunctionResource(
                uri=uri,
                name=res_def.name,
                description=res_def.description,
                mime_type=res_def.mime_type,
                fn=lambda _uri=uri: self.resource_registry.read_resource(_uri),
            )
            self.mcp.add_resource(resource)
            logger.info(f"Registered resource: {uri}")

    def _register_prompts(self):
        """Register MCP Prompts using FastMCP Prompt type."""
        for prompt_def in self.prompt_registry.list_prompts():
            # Capture name in closure
            pname = prompt_def.name
            prompt = FastMCPPrompt(
                name=pname,
                description=prompt_def.description,
                fn=lambda _name=pname, **kwargs: self.prompt_registry.render_prompt(
                    _name, kwargs if kwargs else None
                ),
            )
            self.mcp.add_prompt(prompt)
            logger.info(f"Registered prompt: {pname}")
