"""
arifos.mcp.sse (v52.4.2-SEAL)

The HTTP/SSE Adaptation layer for the Trinity Monolith.
This module exposes the unified MCP tools via Starlette SSE transport.
Designed for Railway/Cloud Run deployment.

Port: 8000 (Env: PORT)
Routes:
  /sse      - Server-Sent Events endpoint (MCP protocol)
  /messages - Client message endpoint (MCP protocol)
  /health   - Health check for Railway/Cloud

DITEMPA BUKAN DIBERI
"""

import os
from starlette.responses import JSONResponse
from mcp.server.fastmcp import FastMCP

# --- TRINITY TOOLS IMPORT ---
# We import from mcp_trinity.py which contains the canonical 5-tool implementation
from arifos.mcp.tools.mcp_trinity import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
)

# --- VERSION ---
VERSION = "v52.4.3-SEAL"
MOTTO = "DITEMPA BUKAN DIBERI"

# Initialize the Monolith
mcp = FastMCP("arifos-trinity", dependencies=["arifos"])

# --- TOOL REGISTRATION ---

@mcp.tool()
async def arifos_trinity_000_init(action: str = "init", query: str = "", session_id: str = None, authority_token: str = "") -> dict:
    """000 INIT: System Ignition & Constitutional Gateway.

    The 7-Step Ignition Sequence that prepares arifOS for operation.
    Actions: init, gate, reset, validate
    """
    return await mcp_000_init(action=action, query=query, session_id=session_id, authority_token=authority_token)

@mcp.tool()
async def arifos_trinity_agi_genius(action: str = "sense", query: str = "", session_id: str = "", thought: str = "") -> dict:
    """AGI GENIUS: The Mind (Δ) - Truth & Reasoning Engine.

    Consolidates: SENSE + THINK + ATLAS + FORGE
    Actions: sense, think, reflect, atlas, forge, evaluate, full
    """
    return await mcp_agi_genius(action=action, query=query, session_id=session_id, thought=thought)

@mcp.tool()
async def arifos_trinity_asi_act(action: str = "empathize", text: str = "", session_id: str = "", proposal: str = "") -> dict:
    """ASI ACT: The Heart (Ω) - Safety & Empathy Engine.

    Consolidates: EVIDENCE + EMPATHY + ACT + WITNESS
    Actions: evidence, empathize, align, act, witness, evaluate, full
    """
    return await mcp_asi_act(action=action, text=text, session_id=session_id, proposal=proposal)

@mcp.tool()
async def arifos_trinity_apex_judge(action: str = "judge", query: str = "", session_id: str = "", response: str = "") -> dict:
    """APEX JUDGE: The Soul (Ψ) - Judgment & Authority Engine.

    Consolidates: EUREKA + JUDGE + PROOF
    Actions: eureka, judge, proof, entropy, parallelism, full
    """
    return await mcp_apex_judge(action=action, query=query, session_id=session_id, response=response)

@mcp.tool()
async def arifos_trinity_999_vault(action: str = "seal", session_id: str = "", verdict: str = "SEAL", target: str = "seal") -> dict:
    """999 VAULT: Immutable Seal & Governance IO.

    The final gate - seals all decisions immutably.
    Actions: seal, list, read, write, propose
    """
    return await mcp_999_vault(action=action, session_id=session_id, verdict=verdict, target=target)


# --- HEALTH CHECK ---
# Add health check directly via FastMCP custom_route before getting SSE app
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Railway/Cloud health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "version": VERSION,
        "motto": MOTTO,
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages",
            "health": "/health"
        }
    })


# --- APP EXPORT ---
# Get the SSE app directly from FastMCP (includes /sse, /messages, and /health)
app = mcp.sse_app()


# --- ENTRYPOINT ---

def create_sse_app():
    """Returns the ASGI app for deployment."""
    return app

if __name__ == "__main__":
    import uvicorn
    # Local Dev Mode
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Igniting Trinity Monolith (SSE) on port {port}...")
    print(f"   Version: {VERSION}")
    print(f"   Routes: /health, /sse, /messages")
    uvicorn.run(app, host="0.0.0.0", port=port)
