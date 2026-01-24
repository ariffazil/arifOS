import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Request
from fastmcp import FastMCP
from pydantic import BaseModel

# Integration Imports
from arifos.core.integration.composio.client import client as composio_client

from .governance import governance
from .tool_registry import registry

# =============================================================================
# 1. MCP SERVER (The "Universal" Protocol for Cursor/Windsurf)
# =============================================================================

# Initialize FastMCP Server
mcp = FastMCP(
    "arifOS-Gateway",
    dependencies=["composio-core", "composio-openai"],
    description="Universal Gateway for arifOS (Supports MCP + REST)"
)

@mcp.tool()
async def governed_execution(tool_name: str, arguments: Dict[str, Any], approval_token: str = None) -> str:
    """
    Execute ANY tool via the arifOS Governance Engine.

    Args:
        tool_name: The slug of the tool to run (e.g. 'github_get_repo')
        arguments: The arguments dictionary for the tool
        approval_token: (Optional) Token for '888_HOLD' overrides
    """
    # 1. Preflight
    pre = governance.preflight(tool_name, arguments, approval_token)

    if pre["verdict"] in ["VOID", "888_HOLD"]:
        governance.log_to_ledger(tool_name, arguments, pre["verdict"], pre["reason"])
        return f"STOP: Verdict {pre['verdict']}. Reason: {pre['reason']}"

    # 2. Execution
    try:
        slug = registry.get_composio_slug(tool_name)
        result = composio_client.execute(slug, arguments)
    except Exception as e:
        governance.log_to_ledger(tool_name, arguments, "VOID", f"Execution error: {str(e)}")
        return f"ERROR: Execution failed. {str(e)}"

    # 3. Postflight
    post = governance.postflight(tool_name, result)

    # 4. Final Ledger
    final_verdict = "SEAL" if post["verdict"] == "SEAL" else post["verdict"]
    governance.log_to_ledger(tool_name, arguments, final_verdict, str(result)[:100])

    return f"SUCCESS: {result} (Verdict: {final_verdict})"

# =============================================================================
# 2. REST API (The "Legacy" Protocol for ChatGPT)
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load settings/tools on startup
    print(f"[INIT] Loaded {len(registry.get_openai_tools())} tools into Registry")
    yield

app = FastAPI(title="arifOS Universal Gateway", version="v50.0.0", lifespan=lifespan)

# Mount MCP SSE Endpoint (The Magic Link for Cursor)
# FastMCP exposes an ASGI app, but we need to mount it correctly or route it.
# Ideally, we run FastMCP as the main app, but we need custom REST routes too.
# Strategy: We mount FastMCP's SSE handler manually if needed, OR we just expose the tool wrapper.
# Simpler: We keep the REST routes below and run `mcp.run()` in a way that includes them?
# NO: We will use FastAPI as the MAIN app, and mount FastMCP.

# NOTE: FastMCP doesn't have a simple "mount" yet in v0.1.0, so we used the decorator pattern.
# We will expose the standard REST routes manually to keep ChatGPT working.

class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    approval_token: Optional[str] = None

@app.get("/sse")
async def handle_sse(request: Request):
    """MCP SSE Endpoint for Cursor/Windsurf"""
    return await mcp.sse_handler(request)

@app.post("/messages")
async def handle_messages(request: Request):
    """MCP Messages Endpoint for Cursor/Windsurf"""
    return await mcp.messages_handler(request)

@app.get("/health")
def health_check():
    return {
        "status": "SEAL",
        "protocols": ["REST", "MCP-SSE"],
        "mcp_endpoint": "/sse",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/tools")
def list_tools():
    """ChatGPT Format"""
    return registry.get_openai_tools()

@app.post("/call")
async def call_tool_rest(req: ToolCallRequest):
    """ChatGPT Format"""
    # Re-use the MCP logic function
    result_str = await governed_execution(req.tool_name, req.arguments, req.approval_token)
    return {"result": result_str}

if __name__ == "__main__":
    # If run directly: use Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
