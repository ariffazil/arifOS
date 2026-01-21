import logging
import os
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Configure logging early to catch import errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# arifOS SSE Web Adapter (Stage 000 Cloud Bridge) v50.0.0
# =============================================================================

# Attempt to import MCP server with graceful fallback
try:
    from mcp.server.sse import SseServerTransport

    from arifos.core.mcp.unified_server import TOOLS, mcp_server
    MCP_AVAILABLE = True
    TOOLS_COUNT = len(TOOLS)
    logger.info(f"✅ MCP Server loaded with {TOOLS_COUNT} tools")
except ImportError as e:
    logger.warning(f"⚠️ MCP import failed (limited mode): {e}")
    MCP_AVAILABLE = False
    TOOLS_COUNT = 0
    mcp_server = None
    TOOLS = {}

app = FastAPI(
    title="arifOS Unified Cloud Interface",
    description=f"Authorized Cloud Bridge for arifOS Constitutional Kernel. Exposes {TOOLS_COUNT} MCP tools via SSE.",
    version="v50.0.0 (Cloud)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Allow all origins for remote access via tunnel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SSE transport only if MCP is available
sse = SseServerTransport("/messages") if MCP_AVAILABLE else None

@app.get("/sse")
async def handle_sse(request: Request):
    """SSE Endpoint for MCP Protocol connection."""
    if not MCP_AVAILABLE or mcp_server is None:
        return {"error": "MCP server not available", "status": "degraded"}
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())

@app.post("/messages")
async def handle_messages(request: Request):
    """Message endpoint for MCP protocol."""
    if not MCP_AVAILABLE or sse is None:
        return {"error": "MCP server not available", "status": "degraded"}
    return await sse.handle_post_message(request.scope, request.receive, request._send)

@app.get("/health")
async def handle_health():
    """Health Check Endpoint - Always responds for Railway."""
    return {
        "status": "healthy" if MCP_AVAILABLE else "degraded",
        "mode": "SSE",
        "tools": TOOLS_COUNT,
        "mcp_available": MCP_AVAILABLE,
        "framework": "FastAPI",
        "version": "v50.0.0",
        "doc_url": "/docs"
    }

@app.get("/")
async def handle_root():
    """Root endpoint with service info."""
    return {
        "service": "arifOS Constitutional Kernel",
        "version": "v50.0.0",
        "status": "healthy" if MCP_AVAILABLE else "degraded",
        "tools": TOOLS_COUNT,
        "endpoints": {
            "/health": "Health check",
            "/sse": "MCP SSE connection",
            "/messages": "MCP message handler",
            "/docs": "API documentation"
        }
    }

def main():
    """Run the server."""
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting arifOS SSE Server v50.0.0 on port {port}...")
    logger.info(f"MCP Status: {'Available' if MCP_AVAILABLE else 'Degraded'}")
    logger.info(f"Tools: {TOOLS_COUNT}")
    logger.info(f"Docs: http://0.0.0.0:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
