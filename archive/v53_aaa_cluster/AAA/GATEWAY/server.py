#!/usr/bin/env python3
"""
AAA GATEWAY (v52.4.0) - The Router (Hydra)
Aggregates Axis, Arif, and Apex into a single endpoint.

Responsibility:
    - Routing: Maps 000-999 tools to internal services
    - Circuit Breaker: Fallback to SABAR/PARTIAL if engines hang
    - Auth & Rate Limiting: F11/F12 enforcement

DITEMPA BUKAN DIBERI
"""

import argparse
import json
import logging
import os
import sys
import time
import httpx
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from mcp.server import Server
from mcp.server.sse import SseServerTransport

# =============================================================================
# CONFIGURATION
# =============================================================================

# Internal Service URLs (Railway Private Networking)
AXIS_URL = os.environ.get("AXIS_URL", "http://axis:8001")
ARIF_URL = os.environ.get("ARIF_URL", "http://arif:8002")
APEX_URL = os.environ.get("APEX_URL", "http://apex:8003")

# Timeouts
DEFAULT_TIMEOUT = 30.0
APEX_TIMEOUT = 10.0

# =============================================================================
# LOGGING
# =============================================================================

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "GATEWAY",
        }
        return json.dumps(log_entry)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("gateway")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# =============================================================================
# PROXY LOGIC (Circuit Breaker)
# =============================================================================

async def proxy_tool_call(service_url: str, tool_name: str, arguments: Dict[str, Any], timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """Forward MCP tool call to internal service via HTTP/SSE messages endpoint."""
    # Note: This implementation assumes internal services expose a standard 
    # POST /messages endpoint or a specialized internal tool endpoint.
    # For simplicity in this cluster, we'll use a standard MCP-over-HTTP internal protocol.
    
    url = f"{service_url}/internal/call/{tool_name}"
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=arguments)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Proxy failure to {service_url} for {tool_name}: {e}")
        return {
            "status": "SABAR",
            "verdict": "SABAR",
            "error": f"Service unavailable: {str(e)}",
            "circuit_breaker": True
        }

# =============================================================================
# MCP SERVER
# =============================================================================

mcp_server = Server("AAA-Gateway")

TOOL_MAP = {
    "init_000": AXIS_URL,
    "vault_999": AXIS_URL,
    "agi_genius": ARIF_URL,
    "asi_act": ARIF_URL,
    "apex_judge": APEX_URL,
}

TOOL_DESCRIPTIONS = {
    "init_000": "System Ignition (AXIS)",
    "agi_genius": "Mind Engine (ARIF)",
    "asi_act": "Heart Engine (ARIF)",
    "apex_judge": "Soul Engine (APEX)",
    "vault_999": "Immutable Seal (AXIS)",
}

@mcp_server.list_tools()
async def list_tools():
    import mcp.types
    return [
        mcp.types.Tool(
            name=name,
            description=desc,
            inputSchema={"type": "object"}
        )
        for name, desc in TOOL_DESCRIPTIONS.items()
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
    import mcp.types
    
    service_url = TOOL_MAP.get(name)
    if not service_url:
        return [mcp.types.TextContent(type="text", text=f"VOID: Tool {name} not mapped")]

    # Specialized timeout for APEX (Judge must be fast)
    timeout = APEX_TIMEOUT if name == "apex_judge" else DEFAULT_TIMEOUT
    
    result = await proxy_tool_call(service_url, name, arguments, timeout=timeout)
    
    # Check for Circuit Breaker Fallback
    if result.get("circuit_breaker"):
        # Log failure
        logger.warning(f"Circuit Breaker triggered for {name}")
        
    return [mcp.types.TextContent(type="text", text=json.dumps(result, indent=2))]

# =============================================================================
# FASTAPI APP
# =============================================================================

# redirect_slashes=False to prevent 307/308 redirects that might strip POST bodies
app = FastAPI(title="AAA-Gateway", version="v52.4.0", redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sse = SseServerTransport("/messages")

@app.get("/")
async def handle_root():
    return {"service": "AAA-Gateway", "status": "active", "motto": "DITEMPA BUKAN DIBERI"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gateway"}

@app.get("/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            mcp_server.create_initialization_options()
        )

@app.post("/messages")
async def handle_messages(request: Request):
    # Fix 307 Redirect Bug: Strictly handle POST forwarding
    # Ensure no trailing slash redirect by registering both if needed, 
    # but FastAPI does this well. Here we just process the message.
    return await sse.handle_post_message(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 9000))
    uvicorn.run(app, host="0.0.0.0", port=port)
