
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mcp.server.sse import SseServerTransport

from arifos_core.mcp.unified_server import mcp_server

# =============================================================================
# arifOS SSE Web Adapter (Stage 000 Cloud Bridge)
# =============================================================================
# This adapter wraps the existing Unified Server (17 Tools) in a FastAPI Shell.
# It allows:
# 1. Cloudflare Tunnel access (arif-fazil.com)
# 2. Remote Claude Desktop connection
# 3. Interactive Documentation (/docs)
# =============================================================================

# Initialize FastAPI with metadata for Swagger UI
app = FastAPI(
    title="arifOS Unified Cloud Interface",
    description="Authorized Cloud Bridge for arifOS Constitutional Kernel. Exposes 17 MCP tools via SSE.",
    version="v46.1.0 (Cloud)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware (CORS for remote access)
# This allows Claude Desktop (or any origin) to connect remotely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP Transport
# Connection endpoint: /sse
# Message endpoint: /messages
sse = SseServerTransport("/messages")

async def handle_sse(scope, receive, send):
    """
    **SSE Endpoint for MCP Protocol connection.**
    """
    async with sse.connect_sse(scope, receive, send) as streams:
        await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())

app.add_route("/sse", handle_sse, methods=["GET"])

@app.get("/health")
async def handle_health():
    """
    **Health Check Endpoint.**

    Verifies that the server and tunnel are operational.
    """
    return {
        "status": "healthy",
        "mode": "SSE",
        "tools": 17,
        "framework": "FastAPI",
        "doc_url": "/docs"
    }

# Mount the message handler for POST requests (part of MCP spec)
app.add_route("/messages", sse.handle_post_message, methods=["POST"])

if __name__ == "__main__":
    print("===============================================================", file=sys.stderr)
    print("[arifOS Cloud] Starting FastAPI server on port 8000...", file=sys.stderr)
    print("[arifOS Cloud] Docs available at: http://localhost:8000/docs", file=sys.stderr)
    print("[arifOS Cloud] Tunnel this port to use: https://vault999.arif-fazil.com/sse", file=sys.stderr)
    print("===============================================================", file=sys.stderr)

    # Run Uvicorn
    # F5 (Peace): Loop handling
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
