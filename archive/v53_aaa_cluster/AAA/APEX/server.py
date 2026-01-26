#!/usr/bin/env python3
"""
APEX SERVER (v52.4.0) - The Summit (Judge)
Judicial Engine (Judge/Verdict).
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
            "service": "APEX",
        })

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("apex")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# =============================================================================
# CORE IMPORTS
# =============================================================================

try:
    from arifos.mcp.tools.mcp_trinity import mcp_apex_judge
    CORE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Core import failed: {e}")
    CORE_AVAILABLE = False

# =============================================================================
# MCP SERVER LOGIC
# =============================================================================

server = Server("APEX")

@server.list_tools()
async def list_tools() -> List[mcp.types.Tool]:
    return [
        mcp.types.Tool(
            name="apex_judge",
            description="Soul Engine: EUREKA → JUDGE → PROOF",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["eureka", "judge", "proof", "entropy", "parallelism", "full"]},
                    "query": {"type": "string"},
                    "response": {"type": "string"},
                    "session_id": {"type": "string"}
                },
                "required": ["action"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    if name == "apex_judge":
        result = await mcp_apex_judge(**arguments)
    else:
        return [mcp.types.TextContent(type="text", text=f"Unknown tool: {name}")]
    
    return [mcp.types.TextContent(type="text", text=json.dumps(result))]

# =============================================================================
# FASTAPI WRAPPER
# =============================================================================

app = FastAPI(title="APEX")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

sse = SseServerTransport("/messages")

@app.post("/internal/call/{tool_name}")
async def internal_call(tool_name: str, arguments: Dict[str, Any]):
    if tool_name == "apex_judge":
        return await mcp_apex_judge(**arguments)
    raise ValueError(f"Unknown tool {tool_name}")

@app.get("/health")
async def health():
    return {"status": "ready", "role": "APEX", "version": "v52.4.0"}

@app.get("/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

@app.post("/messages")
async def handle_messages(request: Request):
    return await sse.handle_post_message(request.scope, request.receive, request._send)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)