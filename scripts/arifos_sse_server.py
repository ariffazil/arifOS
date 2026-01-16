#!/usr/bin/env python3
"""
arifOS SSE Server - Unified MCP Entry Point
Exposes 17 constitutional tools via Server-Sent Events (SSE)

Connects:
  - unified_server.py (core 17 tools)
  - FastAPI (HTTP wrapper)
  - Railway.app (cloud deployment)
  - Claude Desktop + ChatGPT (clients)

Run locally:
  python scripts/arifos_sse_server.py

Run in Docker:
  docker build -t arifos . && docker run -p 8000:8000 arifos

Deploy to Railway:
  git push origin main  # Trigger auto-deploy
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, AsyncGenerator, Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="arifOS MCP Server",
    description="Constitutional Governance for AI Systems - Unified MCP Interface",
    version="46.3"
)

# Enable CORS (for Claude Desktop, ChatGPT integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize unified server (17 tools)
server_registry = None
try:
    # Use functional interface from unified_server.py
    import arifos_core.mcp.unified_server as unified
    server_registry = unified
    logger.info("✅ Unified tool registry initialized with 17 constitutional tools")
except ImportError as e:
    logger.warning(f"⚠️ Unified tool registry not found: {e} — running in demo mode")
    server_registry = None
except Exception as e:
    logger.error(f"❌ Failed to initialize UnifiedServer: {e}")
    server_registry = None

# ============================================================================
# HEALTH & LIVENESS ENDPOINTS
# ============================================================================

@app.get("/health")
async def health() -> Dict[str, Any]:
    """
    Health check endpoint (Railway pings this to detect if server is alive)

    Returns:
      {"status": "healthy", "vault": "VAULT999", "tools": 17, ...}
    """
    return {
        "status": "healthy" if server_registry else "degraded",
        "vault": "VAULT999",
        "tools": 17 if server_registry else 0,
        "timestamp": datetime.now().isoformat(),
        "version": "46.3",
        "server": "online" if server_registry else "demo_mode"
    }

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint - returns service info"""
    return {
        "message": "arifOS MCP Server v46.3 (Constitutional Governance)",
        "status": "healthy" if server_registry else "degraded",
        "endpoints": {
            "/health": "Liveness probe",
            "/sse": "Server-Sent Events stream",
            "/tools": "List all 17 constitutional tools",
            "/invoke": "Execute a tool (POST)",
            "/judge": "Full constitutional judgment (POST)",
            "/docs": "OpenAPI documentation"
        }
    }

# ============================================================================
# TOOL LISTING ENDPOINT
# ============================================================================

@app.get("/tools")
async def list_tools() -> Dict[str, Any]:
    """
    List all 17 constitutional tools available

    Returns:
      {
        "count": 17,
        "tools": [
          {"name": "arifos_live", "description": "..."},
          ...
        ]
      }
    """
    if not server_registry:
        # Static list if server not loaded
        return {
            "count": 17,
            "tools": [
                {"name": "arifos_live", "description": "Full constitutional pipeline (000→999)"},
                {"name": "agi_think", "description": "Mind: Sense → Think → Reflect"},
                {"name": "agi_reflect", "description": "Meta-reflection, track coherence"},
                {"name": "asi_act", "description": "Heart: Empathize & bridge"},
                {"name": "apex_seal", "description": "Soul: Judge & cryptographic seal"},
                {"name": "agi_search", "description": "Knowledge acquisition"},
                {"name": "asi_search", "description": "Claim validation (tri-witness)"},
                {"name": "vault999_query", "description": "Universal memory retrieval"},
                {"name": "vault999_store", "description": "EUREKA storage"},
                {"name": "vault999_seal", "description": "Integrity proofs & ZKPC receipts"},
                {"name": "fag_read", "description": "Governed file reading"},
                {"name": "fag_write", "description": "Governed file writing"},
                {"name": "fag_list", "description": "Governed directory listing"},
                {"name": "fag_stats", "description": "Governance health metrics"},
                {"name": "arifos_executor", "description": "The Hand: shell execution"},
                {"name": "github_govern", "description": "Governed GitHub operations"},
                {"name": "arifos_meta_select", "description": "Meta-router for specialization"},
            ],
            "vault": "VAULT999"
        }

    try:
        # Use functional list_tools from unified_server
        tools = server_registry.list_tools()
        # Get descriptions
        descriptions = []
        import arifos_core.mcp.unified_server as unified
        for name in tools:
            desc = unified.TOOL_DESCRIPTIONS.get(name, {})
            descriptions.append({
                "name": desc.get("name", name),
                "description": desc.get("description", ""),
                "parameters": desc.get("parameters", {})
            })
        return {
            "count": len(descriptions),
            "tools": descriptions,
            "vault": "VAULT999"
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SSE ENDPOINT (Core MCP Integration)
# ============================================================================

@app.get("/sse")
async def sse_endpoint(user_id: str = "anonymous") -> StreamingResponse:
    """
    Server-Sent Events (SSE) endpoint for streaming constitutional verdicts

    Claude Desktop / ChatGPT connects here to:
    1. Get real-time tool responses
    2. Stream constitutional verdicts (SEAL/PARTIAL/VOID)
    3. Receive audit trail updates

    Args:
      user_id: Identifier for audit trail

    Returns:
      text/event-stream (infinite stream until client closes)
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events"""
        try:
            # Send initial connection event
            yield "event: connection\n"
            yield f"data: {json.dumps({'status': 'connected', 'user_id': user_id, 'timestamp': datetime.now().isoformat(), 'tools': 17})}\n\n"
            logger.info(f"SSE client connected: {user_id}")

            # Keep connection alive, stream tool responses
            while True:
                # Heartbeat (keeps connection warm for Railway free tier)
                yield ":\n"  # SSE comment
                await asyncio.sleep(30)  # Heartbeat every 30s

        except asyncio.CancelledError:
            logger.info(f"SSE client disconnected: {user_id}")
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield "event: error\n"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ============================================================================
# TOOL INVOCATION ENDPOINT
# ============================================================================

@app.post("/invoke")
async def invoke_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a constitutional tool synchronously

    Args:
      tool_name: Name of tool (e.g., "arifos_live", "vault999_query")
      params: Tool parameters

    Returns:
      {
        "tool": "arifos_live",
        "result": {...},
        "verdict": "SEAL",
        "timestamp": "..."
      }
    """
    if not server_registry:
        raise HTTPException(status_code=503, detail="Unified tool registry not initialized (demo mode)")

    try:
        logger.info(f"Invoking tool: {tool_name} with params: {params}")

        # Use functional run_tool from unified_server
        # Note: run_tool in unified_server is synchronous
        result = server_registry.run_tool(tool_name, params)

        return {
            "tool": tool_name,
            "result": result,
            "vault": "VAULT999",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Tool invocation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# JUDGE ENDPOINT (Constitutional Governance)
# ============================================================================

@app.post("/judge")
async def judge(query: str, response: str, lane: str = "default") -> Dict[str, Any]:
    """
    Full 000→999 constitutional judgment pipeline

    Args:
      query: Original query
      response: Response to judge
      lane: Judgment lane (default, strict, permissive)

    Returns:
      {
        "verdict": "SEAL" | "PARTIAL" | "VOID",
        "reasoning": [...],
        "timestamp": "..."
      }
    """
    if not server_registry:
        return {
            "verdict": "VOID",
            "reason": "Server not initialized (demo mode)",
            "timestamp": datetime.now().isoformat()
        }

    try:
        logger.info(f"Judge invoked: query={query[:50]}..., lane={lane}")

        # arifos_judge is the function used by arifos_live
        from arifos_core.mcp.models import JudgeRequest
        from arifos_core.mcp.tools.judge import arifos_judge

        request = JudgeRequest(query=f"Judging response to: {query}\nResponse: {response}")
        result = arifos_judge(request)

        return {
            "verdict": result.verdict,
            "reasoning": result.reasoning,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Judge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup info"""
    logger.info("=" * 80)
    logger.info("🔥 arifOS MCP Server v46.3 Starting")
    logger.info(f"   Unified Server: {'✅ Ready' if server_registry else '⚠️ Demo Mode'}")
    logger.info(f"   Constitutional Tools: 17")
    logger.info(f"   Endpoints: /health, /sse, /tools, /invoke, /judge, /docs")
    logger.info(f"   Vault: VAULT999")
    logger.info("=" * 80)

@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown"""
    logger.info("🛑 arifOS MCP Server Shutting Down")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Respect Railway PORT env variable (mandatory for Railway)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting uvicorn on {host}:{port}")
    logger.info(f"Railway deployment: {bool(os.getenv('RAILWAY_ENVIRONMENT'))}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
