
import os
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.sse import SseServerTransport

from arifos_core.mcp.unified_server import mcp_server

# =============================================================================
# arifOS SSE Web Adapter (Stage 000 Cloud Bridge)
# =============================================================================

app = FastAPI(
    title="arifOS Unified Cloud Interface",
    description="Authorized Cloud Bridge for arifOS Constitutional Kernel. Exposes 17 MCP tools via SSE.",
    version="v47.0.0 (Cloud)",
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
    """Health Check Endpoint."""
    return {
        "status": "healthy",
        "mode": "SSE",
        "tools": 17,
        "framework": "FastAPI",
        "doc_url": "/docs"
    }

def main():
    """Run the server."""
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting arifOS SSE Server on port {port}...")
    print(f"Docs: http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
