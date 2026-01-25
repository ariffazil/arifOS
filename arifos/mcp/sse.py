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
from mcp.server.fastmcp import FastMCP

# --- TRINITY TOOLS IMPORT ---
# We import the core implementation to ensure logic parity with the CLI.
from arifos.mcp.tools.init_000 import init_tool
from arifos.mcp.tools.agi_111 import agi_genius_tool
from arifos.mcp.tools.asi_444 import asi_act_tool
from arifos.mcp.tools.apex_777 import apex_judge_tool
from arifos.mcp.tools.vault_999 import vault_tool

# Initialize the Monolith
mcp = FastMCP("arifos-trinity", dependencies=["arifos"])

# --- TOOL REGISTRATION ---

@mcp.tool()
async def arifos_trinity_000_init(action: str, query: str = None, session_id: str = None, authority_token: str = None) -> str:
    """000 INIT: System Ignition & Constitutional Gateway."""
    return await init_tool(action, query, session_id, authority_token)

@mcp.tool()
async def arifos_trinity_agi_genius(action: str, query: str = None, session_id: str = None, thought: str = None) -> str:
    """AGI GENIUS: The Mind (Δ) - Truth & Reasoning Engine."""
    return await agi_genius_tool(action, query, session_id, thought)

@mcp.tool()
async def arifos_trinity_asi_act(action: str, proposal: str = None, session_id: str = None, sources: list = None) -> str:
    """ASI ACT: The Heart (Ω) - Safety & Empathy Engine."""
    return await asi_act_tool(action, proposal, session_id, sources)

@mcp.tool()
async def arifos_trinity_apex_judge(action: str, topic: str = None, session_id: str = None, verdict: str = None) -> str:
    """APEX JUDGE: The Soul (Ψ) - Judgment & Authority Engine."""
    return await apex_judge_tool(action, topic, session_id, verdict)

@mcp.tool()
async def arifos_trinity_999_vault(action: str, target: str = None, data: str = None, session_id: str = None) -> str:
    """999 VAULT: Immutable Seal & Governance IO."""
    return await vault_tool(action, target, data, session_id)

# --- APP EXPORT ---
# Expose the internal Starlette/FastAPI app for uvicorn
app = mcp

# --- ENTRYPOINT ---

def create_sse_app():
    """Returns the ASGI app for deployment."""
    return mcp

if __name__ == "__main__":
    # Local Dev Mode
    port = int(os.getenv("PORT", 8000))
    print(f"Igniting Trinity Monolith (SSE) on port {port}...")
    mcp.run(host="0.0.0.0", port=port)
