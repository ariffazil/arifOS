"""
arifos.mcp.sse (v52.0.0-SEAL)

The HTTP/SSE Adaptation layer for the Trinity Monolith.
This module exposes the unified MCP tools via Starlette/FastAPI/SSE.
Designed for Railway/Cloud Run deployment.

Port: 8000 (Env: PORT)
Routes:
  /sse    - Server-Sent Events endpoint
  /messages - Client message endpoint
"""

import os
import uvicorn
from mcp.server.fastmcp import FastMCP

# Initialize the Monolith
mcp = FastMCP("arifos-trinity", dependencies=["arifos"])

# --- TRINITY TOOLS IMPORT ---
# Fixed import to point to the actual existing module
from arifos.mcp.tools.mcp_trinity import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault
)

# --- TOOL REGISTRATION ---

@mcp.tool()
async def arifos_trinity_000_init(action: str, query: str = None, session_id: str = None, authority_token: str = None) -> str:
    """000 INIT: System Ignition & Constitutional Gateway."""
    return await mcp_000_init(action=action, query=query, session_id=session_id, authority_token=authority_token)

@mcp.tool()
async def arifos_trinity_agi_genius(action: str, query: str = None, session_id: str = None, thought: str = None) -> str:
    """AGI GENIUS: The Mind (Δ) - Truth & Reasoning Engine."""
    return await mcp_agi_genius(action=action, query=query, session_id=session_id, thought=thought)

@mcp.tool()
async def arifos_trinity_asi_act(action: str, proposal: str = None, session_id: str = None, sources: list = None) -> str:
    """ASI ACT: The Heart (Ω) - Safety & Empathy Engine."""
    return await mcp_asi_act(action=action, proposal=proposal, session_id=session_id, sources=sources)

@mcp.tool()
async def arifos_trinity_apex_judge(action: str, topic: str = None, session_id: str = None, verdict: str = None) -> str:
    """APEX JUDGE: The Soul (Ψ) - Judgment & Authority Engine."""
    return await mcp_apex_judge(action=action, session_id=session_id, verdict=verdict)

@mcp.tool()
async def arifos_trinity_999_vault(action: str, target: str = None, data: str = None, session_id: str = None) -> str:
    """999 VAULT: Immutable Seal & Governance IO."""
    return await mcp_999_vault(action=action, target=target, data=data, session_id=session_id)

# --- ENTRYPOINT ---

def create_sse_app():
    """Returns the ASGI app for deployment."""
    return mcp._asgi_app

if __name__ == "__main__":
    # Local Dev Mode / Docker Entrypoint
    port = int(os.getenv("PORT", 8000))
    print(f"Igniting Trinity Monolith (SSE) on port {port}...")
    mcp.run(host="0.0.0.0", port=port)
