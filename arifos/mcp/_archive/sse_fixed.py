import logging
import os
import sys
import traceback

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Configure logging early to catch import errors
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# arifOS SSE Web Adapter (Stage 000 Cloud Bridge) v50.0.0-railway-fix
# =============================================================================

# ============================================================================
# CRITICAL: Import MCP server - FAIL FAST if errors (Railway diagnostics)
# ============================================================================

MCP_AVAILABLE = False
TOOLS_COUNT = 0
mcp_server = None
TOOLS = {}
MCP_ERROR = None

try:
    logger.info("[000] Initializing MCP server imports...")
    
    from mcp.server.sse import SseServerTransport
    logger.info("[000] SUCCESS MCP SSE transport loaded")
    
    from arifos.core.mcp.unified_server import TOOLS, mcp_server
    logger.info(f"[000] SUCCESS arifOS unified_server loaded with {len(TOOLS)} tools")
    
    MCP_AVAILABLE = True
    TOOLS_COUNT = len(TOOLS)
    logger.info(f"[000] SUCCESS MCP Server ready: {TOOLS_COUNT} tools available")
    
except ImportError as e:
    MCP_ERROR = f"ImportError: {str(e)}"
    logger.error(f"[000] FAILED IMPORT: {MCP_ERROR}")
    logger.error(f"[000] Stack trace:\n{traceback.format_exc()}")
    
    # FAIL FAST: Exit so Railway knows service is broken
    logger.error("[000] Exiting due to MCP import failure (Railway will retry)")
    sys.exit(1)  # EXIT CODE 1: Railway container crash
    
except Exception as e:
    MCP_ERROR = f"Exception: {type(e).__name__}: {str(e)}"
    logger.error(f"[000] FAILED INIT: {MCP_ERROR}")
    logger.error(f"[000] Stack trace:\n{traceback.format_exc()}")
    sys.exit(1)

# ============================================================================
# FastAPI App Setup (only reaches here if MCP init succeeded)
# ============================================================================

app = FastAPI(
    title="arifOS Unified Cloud Interface",
    description=f"Constitutional Kernel MCP Server. {TOOLS_COUNT} tools via SSE.",
    version="v50.0.0-railway-fix",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Allow all origins for remote access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SSE transport (guaranteed MCP_AVAILABLE is True here)
sse = SseServerTransport("/messages")
logger.info("[000] SUCCESS SSE transport initialized")

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/health")
async def handle_health():
    """
    Railway healthcheck probe.
    Returns 200 OK only when MCP is fully operational.
    """
    return {
        "status": "healthy",
        "mode": "SSE",
        "tools": TOOLS_COUNT,
        "mcp_available": MCP_AVAILABLE,
        "framework": "FastAPI",
        "version": "v50.0.0-railway-fix",
        "vault_path": os.getenv("VAULT_PATH", "/app/vault_999"),
        "doc_url": "/docs"
    }

@app.get("/sse")
async def handle_sse(request: Request):
    """
    SSE Endpoint for MCP Protocol connection.
    """
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())

@app.post("/messages")
async def handle_messages(request: Request):
    """
    Message endpoint for MCP protocol.
    """
    return await sse.handle_post_message(request.scope, request.receive, request._send)

@app.get("/")
async def handle_root():
    """
    Root endpoint with service info.
    """
    return {
        "service": "arifOS Constitutional Kernel",
        "version": "v50.0.0-railway-fix",
        "status": "healthy",
        "tools": TOOLS_COUNT,
        "endpoints": {
            "/health": "Railway healthcheck",
            "/sse": "MCP SSE connection",
            "/messages": "MCP message handler",
            "/docs": "API documentation (Swagger)",
            "/redoc": "API documentation (ReDoc)"
        }
    }

@app.get("/diagnostics")
async def handle_diagnostics():
    """
    Diagnostics endpoint for Railway troubleshooting.
    """
    return {
        "mcp_available": MCP_AVAILABLE,
        "mcp_error": MCP_ERROR,
        "tools_count": TOOLS_COUNT,
        "vault_path": os.getenv("VAULT_PATH", "/app/vault_999"),
        "port": os.getenv("PORT", "8000"),
        "environment": {
            "VAULT_PATH": os.getenv("VAULT_PATH"),
            "ARIFOS_HUMAN_SOVEREIGN": os.getenv("ARIFOS_HUMAN_SOVEREIGN"),
            "RAILWAY_REGION": os.getenv("RAILWAY_REGION"),
            "PORT": os.getenv("PORT"),
        }
    }

def main():
    """
    Run the server.
    """
    port = int(os.environ.get("PORT", 8000))
    vault_path = os.environ.get("VAULT_PATH", "/app/vault_999")
    
    logger.info(f"\n" + "="*70)
    logger.info("[000] Starting arifOS SSE Server v50.0.0-railway-fix")
    logger.info(f"[000] Port: {port}")
    logger.info(f"[000] Vault: {vault_path}")
    logger.info(f"[000] MCP Tools: {TOOLS_COUNT}")
    logger.info(f"[000] Docs: http://0.0.0.0:{port}/docs")
    logger.info(f"[000] Diagnostics: http://0.0.0.0:{port}/diagnostics")
    logger.info("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
