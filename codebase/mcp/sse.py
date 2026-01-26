"""
codebase.mcp.sse (v53.1.0-CODEBASE)
The HTTP/SSE Transport for the Codebase Microservices.
Deployable on Railway.

Host: 0.0.0.0
Port: $PORT (default 8000)
"""

import os
import asyncio
from typing import Dict, Any, List
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

# Import Codebase Routers (Bridge)
from codebase.mcp.bridge import (
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
)
# Import v53 Tools
from codebase.mcp.tools.mcp_tools_v53 import (
    authorize, reason, evaluate, decide, seal
)
from codebase.system.constitution import execute_constitutional_physics
from codebase.enforcement.metrics import record_stage_metrics, record_verdict_metrics
from codebase.mcp.constitutional_metrics import get_full_metrics

VERSION = "v53.1.0-CODEBASE"

mcp = FastMCP(
    "codebase-mcp",
    dependencies=["arifos"],
    host="0.0.0.0",
    port=int(os.getenv("PORT", 8000)),
)

# --- TRINITY TOOLS (Bridged) ---

@mcp.tool(name="init_000")
async def tool_init(action: str = "init", query: str = "", session_id: str = ""):
    return await bridge_init_router(action=action, query=query, session_id=session_id)

@mcp.tool(name="agi_genius")
async def tool_agi(action: str = "sense", query: str = "", session_id: str = "", **kwargs):
    return await bridge_agi_router(action=action, query=query, session_id=session_id, **kwargs)

@mcp.tool(name="asi_act")
async def tool_asi(action: str = "empathize", text: str = "", session_id: str = "", **kwargs):
    # Map 'text' to 'query' if needed by bridge
    kwargs["query"] = kwargs.get("query") or text
    return await bridge_asi_router(action=action, text=text, session_id=session_id, **kwargs)

@mcp.tool(name="apex_judge")
async def tool_apex(action: str = "judge", query: str = "", response: str = "", session_id: str = "", **kwargs):
    return await bridge_apex_router(action=action, query=query, response=response, session_id=session_id, **kwargs)

@mcp.tool(name="vault_999")
async def tool_vault(action: str = "seal", session_id: str = "", verdict: str = "", **kwargs):
    return await bridge_vault_router(action=action, session_id=session_id, verdict=verdict, **kwargs)

# --- v53 TOOLS ---

@mcp.tool(name="physics")
async def tool_physics(query: str, user_id: str = "anonymous"):
    """Run Quantum Constitutional Physics."""
    return await execute_constitutional_physics(query=query, user_id=user_id)

@mcp.tool(name="authorize")
async def tool_authorize(query: str, user_token: str = "", session_id: str = ""):
    return await authorize(query=query, user_token=user_token, session_id=session_id)

@mcp.tool(name="reason")
async def tool_reason(query: str, session_id: str, context: Dict = None, style: str = "logical"):
    return await reason(query=query, session_id=session_id, context=context, style=style)

@mcp.tool(name="decide")
async def tool_decide(query: str, reasoning: str, safety_evaluation: Dict, authority_check: Dict, session_id: str):
    return await decide(query, reasoning, safety_evaluation, authority_check, session_id)

# --- ENDPOINTS ---

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({
        "status": "healthy",
        "version": VERSION,
        "mode": "CODEBASE",
        "physics": "ACTIVE"
    })

@mcp.custom_route("/metrics/json", methods=["GET"])
async def metrics_endpoint(request):
    return JSONResponse(get_full_metrics())

# Entry point
def main():
    print(f"[BOOT] Codebase SSE (v53) starting on port {mcp.port}")
    mcp.run()

if __name__ == "__main__":
    main()
