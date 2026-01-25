#!/usr/bin/env python3
"""
ARIF SERVER (v52.4.0) - The Architect (Nexus)
Cognitive Engines (AGI/ASI).
"""

import argparse
import json
import logging
import os
import sys
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
            "service": "ARIF",
        })

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("arif")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# =============================================================================
# CORE IMPORTS
# =============================================================================

try:
    from arifos.mcp.tools.mcp_trinity import mcp_agi_genius, mcp_asi_act
    CORE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Core import failed: {e}")
    CORE_AVAILABLE = False

# =============================================================================
# MCP SERVER LOGIC
# =============================================================================

server = Server("ARIF")

@server.list_tools()
async def list_tools() -> List[mcp.types.Tool]:
    return [
        mcp.types.Tool(
            name="agi_genius",
            description="Mind Engine: SENSE → THINK → ATLAS → FORGE",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["sense", "think", "reflect", "atlas", "forge", "evaluate", "full"]},
                    "query": {"type": "string"},
                    "session_id": {"type": "string"}
                },
                "required": ["action"]
            }
        ),
        mcp.types.Tool(
            name="asi_act",
            description="Heart Engine: EVIDENCE → EMPATHY → ACT",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["evidence", "empathize", "align", "act", "witness", "evaluate", "full"]},
                    "text": {"type": "string"},
                    "session_id": {"type": "string"}
                },
                "required": ["action"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    if name == "agi_genius":
        result = await mcp_agi_genius(**arguments)
    elif name == "asi_act":
        result = await mcp_asi_act(**arguments)
    else:
        return [mcp.types.TextContent(type="text", text=f"Unknown tool: {name}")]
    
    return [mcp.types.TextContent(type="text", text=json.dumps(result))]

# =============================================================================
# FASTAPI WRAPPER
# =============================================================================

app = FastAPI(title="ARIF")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

sse = SseServerTransport("/messages")

@app.post("/internal/call/{tool_name}")
async def internal_call(tool_name: str, arguments: Dict[str, Any]):
    if tool_name == "agi_genius":
        return await mcp_agi_genius(**arguments)
    elif tool_name == "asi_act":
        return await mcp_asi_act(**arguments)
    raise ValueError(f"Unknown tool {tool_name}")

@app.get("/health")
async def health():
    return {"status": "ready", "role": "ARIF", "version": "v52.4.0"}

@app.get("/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

@app.post("/messages")
async def handle_messages(request: Request):
    return await sse.handle_post_message(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)