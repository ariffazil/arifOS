
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

@app.get("/sse")
async def handle_sse(request: Request):
    """
    **SSE Endpoint for MCP Protocol connection.**

    Connect here with your MCP client (Claude Desktop).
    - Mode: Server-Sent Events
    - Capacity: 17 Tools
    - Governance: Active
    """
    async with mcp_server.create_initialization_options() as options:
        await mcp_server.run(sse, sse, options)

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
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    # F5 (Peace): Loop handling
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
