"""
arifOS Universal MCP Gateway (v52.4.1)
One Ring to Rule Them All: SSE (Claude) + HTTP (ChatGPT) + Health (Railway)

DITEMPA BUKAN DIBERI
"""

import os
import logging
import json
from typing import Any, Dict
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from mcp.server import Server
from mcp.server.sse import SseServerTransport
import mcp.types

# --- TRINITY TOOLS IMPORT ---
from arifos.mcp.tools.mcp_trinity import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault
)

logger = logging.getLogger(__name__)

# 1. Initialize MCP Server
mcp_server = Server("arifos-trinity")

# 2. Register Tools logic
async def call_tool_logic(name: str, arguments: Dict[str, Any]) -> Any:
    """Internal router for tool execution."""
    if name == "000_init":
        return await mcp_000_init(**arguments)
    elif name == "agi_genius":
        return await mcp_agi_genius(**arguments)
    elif name == "asi_act":
        return await mcp_asi_act(**arguments)
    elif name == "apex_judge":
        return await mcp_apex_judge(**arguments)
    elif name == "999_vault":
        return await mcp_999_vault(**arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

# 3. Setup FastAPI App
app = FastAPI(title="arifOS Constitutional Monolith")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# SSE Transport Setup
sse_transport = SseServerTransport("/messages")

# --- ROUTES ---

@app.get("/health")
@app.get("/")
async def health_and_root():
    """Universal health check for Railway and ChatGPT."""
    return {
        "name": "arifOS Trinity Monolith",
        "status": "healthy",
        "version": "v52.4.1-SEAL",
        "motto": "DITEMPA BUKAN DIBERI",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages",
            "jsonrpc": "/"
        }
    }

@app.get("/sse")
async def handle_sse(request: Request):
    """Claude Desktop SSE endpoint."""
    async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp_server.run(
            streams[0], 
            streams[1], 
            mcp_server.create_initialization_options()
        )

@app.post("/messages")
async def handle_messages(request: Request):
    """Claude Desktop message delivery endpoint."""
    return await sse_transport.handle_post_message(request.scope, request.receive, request._send)

@app.post("/")
async def handle_jsonrpc(request: Request):
    """ChatGPT Dev Mode / Stateless JSON-RPC endpoint."""
    body = await request.json()
    method = body.get("method")
    params = body.get("params", {})
    req_id = body.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "arifos-trinity", "version": "v52.4.1"}
            }
        }
    
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "000_init",
                        "description": "System Ignition & Constitutional Gateway.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string"},
                                "query": {"type": "string"},
                                "session_id": {"type": "string"}
                            },
                            "required": ["action"]
                        }
                    },
                    {
                        "name": "agi_genius",
                        "description": "AGI GENIUS: The Mind (Delta). Truth & Reasoning Engine.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"action": {"type": "string"}, "query": {"type": "string"}},
                            "required": ["action"]
                        }
                    },
                    {
                        "name": "asi_act",
                        "description": "ASI ACT: The Heart (Omega). Safety & Empathy Engine.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"action": {"type": "string"}, "proposal": {"type": "string"}},
                            "required": ["action"]
                        }
                    },
                    {
                        "name": "apex_judge",
                        "description": "APEX JUDGE: The Soul (Psi). Judgment & Authority Engine.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"action": {"type": "string"}, "topic": {"type": "string"}},
                            "required": ["action"]
                        }
                    },
                    {
                        "name": "999_vault",
                        "description": "999 VAULT: Immutable Seal & Governance IO.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"action": {"type": "string"}, "target": {"type": "string"}},
                            "required": ["action"]
                        }
                    }
                ]
            }
        }

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        try:
            result = await call_tool_logic(name, args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(e)}
            }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

# --- MCP SERVER REGISTRATION (For SSE) ---

@mcp_server.list_tools()
async def list_tools_mcp():
    return [
        mcp.types.Tool(
            name="000_init",
            description="System Ignition & Constitutional Gateway.",
            inputSchema={"type": "object", "properties": {"action": {"type": "string"}}, "required": ["action"]}
        ),
        # ... other tools would go here for Claude SSE ...
    ]

@mcp_server.call_tool()
async def call_tool_mcp(name: str, arguments: Dict[str, Any]):
    result = await call_tool_logic(name, arguments)
    return [mcp.types.TextContent(type="text", text=json.dumps(result, indent=2))]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🚀 Igniting Universal Gateway on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
