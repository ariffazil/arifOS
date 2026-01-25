#!/usr/bin/env python3
"""
AXIS SERVER (v52.4.0) - Authority & Memory (Spine)
Production-ready deployment unit using raw MCP Server for maximum control.
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import mcp.types
from mcp.server import Server
from mcp.server.sse import SseServerTransport

# =============================================================================
# LOGGING
# =============================================================================

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "AXIS",
        })

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("axis")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# =============================================================================
# CORE IMPORTS
# =============================================================================

try:
    from arifos.mcp.tools.mcp_trinity import mcp_000_init, mcp_999_vault
    from arifos.core.enforcement.metrics import OMEGA_0_MIN
    from arifos.mcp.session_ledger import (
        open_session,
        close_session,
        get_orphaned_sessions,
        recover_orphaned_session,
    )
    CORE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Core import failed: {e}")
    CORE_AVAILABLE = False
    OMEGA_0_MIN = 0.03

# =============================================================================
# MCP SERVER LOGIC
# =============================================================================

server = Server("AXIS")

@server.list_tools()
async def list_tools() -> List[mcp.types.Tool]:
    return [
        mcp.types.Tool(
            name="init_000",
            description="000 INIT: Universal Ignition Protocol.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["init", "gate", "reset", "validate"], "default": "init"},
                    "query": {"type": "string"},
                    "session_id": {"type": "string"},
                    "authority_token": {"type": "string"}
                }
            }
        ),
        mcp.types.Tool(
            name="vault_999",
            description="999 VAULT: Immutable Seal.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["seal", "list", "read", "write", "propose"]},
                    "verdict": {"type": "string", "enum": ["SEAL", "SABAR", "VOID"]},
                    "session_id": {"type": "string"},
                    "target": {"type": "string", "default": "seal"},
                    "data": {"type": "object"}
                },
                "required": ["action"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    if name == "init_000":
        result = await mcp_000_init(**arguments)
    elif name == "vault_999":
        result = await mcp_999_vault(**arguments)
    else:
        return [mcp.types.TextContent(type="text", text=f"Unknown tool: {name}")]
    
    return [mcp.types.TextContent(type="text", text=json.dumps(result))]

# =============================================================================
# FASTAPI WRAPPER
# =============================================================================

app = FastAPI(title="AXIS")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

sse = SseServerTransport("/messages")

@app.post("/internal/call/{tool_name}")
async def internal_call(tool_name: str, arguments: Dict[str, Any]):
    """Internal REST endpoint for the Gateway."""
    if tool_name == "init_000":
        return await mcp_000_init(**arguments)
    elif tool_name == "vault_999":
        return await mcp_999_vault(**arguments)
    raise ValueError(f"Unknown tool {tool_name}")

@app.get("/health")
async def health():
    return {"status": "ready", "role": "AXIS", "version": "v52.4.0"}

@app.get("/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

@app.post("/messages")
async def handle_messages(request: Request):
    return await sse.handle_post_message(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)