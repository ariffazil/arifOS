"""
codebase.mcp.sse_simple (v53.1.0-CODEBASE-MINIMAL)
Simplified SSE Transport for Railway Deployment.

This is a minimal, reliable version that focuses on:
1. Health endpoint that returns 200 OK
2. Basic MCP tool registration
3. No complex dependencies that might fail

Host: 0.0.0.0
Port: $PORT (default 8000)
"""

import os
import logging
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VERSION = "v53.1.0-CODEBASE-MINIMAL"
PORT = int(os.getenv("PORT", 8000))

# Create FastMCP server
mcp = FastMCP(
    "codebase-mcp-minimal",
    dependencies=["arifos"],
    host="0.0.0.0",
    port=PORT,
)

# --- HEALTH ENDPOINT (PRIMARY - MUST WORK) ---

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """
    Health check endpoint for Railway.
    This MUST return 200 OK or deployment fails.
    """
    return JSONResponse({
        "status": "healthy",
        "version": VERSION,
        "mode": "CODEBASE-MINIMAL",
        "port": PORT,
        "message": "arifOS MCP Server is running"
    })

# --- MINIMAL TOOLS ---

@mcp.tool(name="init_000")
async def tool_init(action: str = "init", query: str = "", session_id: str = ""):
    """Basic init tool - returns minimal response"""
    return {
        "status": "SEAL",
        "action": action,
        "session_id": session_id or "default-session",
        "message": "Init successful (minimal mode)",
        "version": VERSION
    }

@mcp.tool(name="agi_genius")
async def tool_agi(action: str = "sense", query: str = "", session_id: str = "", **kwargs):
    """Basic AGI tool - returns minimal response"""
    return {
        "status": "SEAL",
        "action": action,
        "query": query,
        "session_id": session_id or "default-session",
        "message": f"AGI {action} complete (minimal mode)",
        "version": VERSION
    }

@mcp.tool(name="asi_act")
async def tool_asi(action: str = "empathize", text: str = "", session_id: str = "", **kwargs):
    """Basic ASI tool - returns minimal response"""
    return {
        "status": "SEAL",
        "action": action,
        "text": text,
        "session_id": session_id or "default-session",
        "message": f"ASI {action} complete (minimal mode)",
        "version": VERSION
    }

@mcp.tool(name="apex_judge")
async def tool_apex(action: str = "judge", query: str = "", response: str = "", session_id: str = "", **kwargs):
    """Basic APEX tool - returns minimal response"""
    return {
        "status": "SEAL",
        "verdict": "SEAL",
        "action": action,
        "session_id": session_id or "default-session",
        "message": f"APEX {action} complete (minimal mode)",
        "version": VERSION
    }

@mcp.tool(name="vault_999")
async def tool_vault(action: str = "seal", session_id: str = "", verdict: str = "", **kwargs):
    """Basic VAULT tool - returns minimal response"""
    return {
        "status": "SEAL",
        "action": action,
        "session_id": session_id or "default-session",
        "verdict": verdict or "SEAL",
        "message": f"VAULT {action} complete (minimal mode)",
        "version": VERSION
    }

# --- METRICS ENDPOINT ---

@mcp.custom_route("/metrics/json", methods=["GET"])
async def metrics_endpoint(request):
    """Basic metrics endpoint"""
    return JSONResponse({
        "version": VERSION,
        "mode": "minimal",
        "tools": ["init_000", "agi_genius", "asi_act", "apex_judge", "vault_999"],
        "status": "operational"
    })

# --- MAIN ENTRY POINT ---

def main():
    """Entry point for Railway deployment"""
    logger.info("=" * 60)
    logger.info(f"[BOOT] Codebase MCP (Minimal) starting on port {PORT}")
    logger.info(f"[BOOT] Version: {VERSION}")
    logger.info(f"[BOOT] Health: http://0.0.0.0:{PORT}/health")
    logger.info(f"[BOOT] Metrics: http://0.0.0.0:{PORT}/metrics/json")
    logger.info("=" * 60)
    
    # Start the server
    mcp.run()

if __name__ == "__main__":
    main()
