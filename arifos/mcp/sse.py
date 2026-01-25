"""
arifOS MCP SSE Adapter (v52.0.0-SEAL)
Cloud Bridge for MCP Protocol via Server-Sent Events

Usage:
  python -m arifos.mcp.sse
  uvicorn arifos.mcp.sse:app --host 0.0.0.0 --port $PORT

DITEMPA BUKAN DIBERI
"""

import os
import logging
from typing import Any
from fastapi import FastAPI, Request
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

def create_sse_app() -> FastAPI:
    """Create the FastAPI app with MCP SSE transport."""
    
    # 1. Initialize MCP Server
    mcp_server = Server("arifos-trinity")

    # 2. Register Tools
    @mcp_server.list_tools()
    async def list_tools() -> list[mcp.types.Tool]:
        return [
            mcp.types.Tool(
                name="000_init",
                description="000 INIT: System Ignition & Constitutional Gateway. Starts session, verifies authority.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to perform (init, gate, reset)"},
                        "query": {"type": "string", "description": "User intent/query"},
                        "session_id": {"type": "string"},
                        "authority_token": {"type": "string"}
                    },
                    "required": ["action"]
                }
            ),
            mcp.types.Tool(
                name="agi_genius",
                description="AGI GENIUS: The Mind (Delta). Truth & Reasoning Engine (SENSE -> THINK -> ATLAS).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action (sense, think, atlas, forge)"},
                        "query": {"type": "string"},
                        "thought": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["action"]
                }
            ),
            mcp.types.Tool(
                name="asi_act",
                description="ASI ACT: The Heart (Omega). Safety & Empathy Engine (EVIDENCE -> EMPATHY -> ACT).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action (evidence, empathize, act)"},
                        "proposal": {"type": "string"},
                        "session_id": {"type": "string"},
                        "sources": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["action"]
                }
            ),
            mcp.types.Tool(
                name="apex_judge",
                description="APEX JUDGE: The Soul (Psi). Judgment & Authority Engine (EUREKA -> JUDGE -> PROOF).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action (eureka, judge, proof)"},
                        "topic": {"type": "string"},
                        "verdict": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["action"]
                }
            ),
            mcp.types.Tool(
                name="999_vault",
                description="999 VAULT: Immutable Seal & Governance IO.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action (seal, read, write)"},
                        "target": {"type": "string"},
                        "data": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["action"]
                }
            )
        ]

    @mcp_server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[mcp.types.TextContent]:
        try:
            result = None
            if name == "000_init":
                result = await mcp_000_init(**arguments)
            elif name == "agi_genius":
                result = await mcp_agi_genius(**arguments)
            elif name == "asi_act":
                result = await mcp_asi_act(**arguments)
            elif name == "apex_judge":
                result = await mcp_apex_judge(**arguments)
            elif name == "999_vault":
                result = await mcp_999_vault(**arguments)
            else:
                return [mcp.types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
            return [mcp.types.TextContent(type="text", text=str(result))]
        except Exception as e:
            logger.error(f"Error executing {name}: {e}")
            return [mcp.types.TextContent(type="text", text=f"Error: {str(e)}")]

    # 3. Setup FastAPI
    app = FastAPI(title="arifOS Constitutional Monolith")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    sse = SseServerTransport("/messages")

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
        return await sse.handle_post_message(request.scope, request.receive, request._send)

    @app.get("/health")
    async def handle_health():
        return {"status": "healthy", "version": "v52.0.0-SEAL"}

    return app

# Create app instance
app = create_sse_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)