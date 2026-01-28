"""
codebase.mcp.sse (v53.2.0-CODEBASE)
The HTTP Transport for the Codebase MCP Server.
Deployable on Railway, Render, Fly.io, or any Docker host.

Supports:
  - Streamable HTTP transport (/mcp) — NEW STANDARD (MCP protocol 2024-11-05+)
  - Legacy SSE transport (/sse + /messages) — BACKWARD COMPAT
  - Health check (/health) — Railway/Docker liveness
  - Metrics (/metrics/json) — Constitutional telemetry

Compatible with:
  - ChatGPT Developer Mode (HTTP)
  - OpenAI Codex (HTTP)
  - Any MCP HTTP client

Note: stdio clients (Claude Code, Claude Desktop, Kimi, Gemini CLI)
use codebase.mcp.server instead.

Host: 0.0.0.0
Port: $PORT (default 8000)
"""

import os
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

# Import Codebase Routers (Bridge) — v53.2.0 Simplified 6-Tool Architecture
from codebase.mcp.bridge import (
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
    bridge_trinity_loop_router,
)
from codebase.mcp.constitutional_metrics import get_full_metrics

logger = logging.getLogger(__name__)

VERSION = "v53.2.0-CODEBASE"

# =============================================================================
# FASTMCP SERVER (6-Tool Architecture)
# =============================================================================

mcp = FastMCP(
    "AAA-MCP-CODEBASE",
    dependencies=["arifos"],
    host="0.0.0.0",
    port=int(os.getenv("PORT", 8000)),
    stateless_http=True,
    json_response=True,
)

# --- TOOL 1: init_000 ---

@mcp.tool(name="init_000", description=(
    "000 INIT: Constitutional Ignition, Identity Verification & Session Management. "
    "Actions: init (start session), gate (checkpoint), reset (clear session), "
    "validate (verify state), authorize (verify identity)."
))
async def tool_init(
    action: str = "init",
    query: str = "",
    session_id: str = "",
    user_token: str = "",
) -> dict:
    """Initialize constitutional session or verify identity."""
    return await bridge_init_router(
        action=action, query=query, session_id=session_id, user_token=user_token
    )

# --- TOOL 2: agi_genius ---

@mcp.tool(name="agi_genius", description=(
    "AGI Mind Engine (F2,F4,F7,F10): SENSE → THINK → REASON → FORGE. "
    "Actions: sense (perceive), think (deliberate), reflect (introspect), "
    "reason (logical analysis), atlas (knowledge mapping), forge (create), "
    "full (complete pipeline), physics (quantum constitutional)."
))
async def tool_agi(
    action: str = "sense",
    query: str = "",
    session_id: str = "",
    context: dict = None,
) -> dict:
    """Route reasoning tasks to AGI Mind Kernel."""
    kwargs = {}
    if context:
        kwargs["context"] = context
    return await bridge_agi_router(
        action=action, query=query, session_id=session_id, **kwargs
    )

# --- TOOL 3: asi_act ---

@mcp.tool(name="asi_act", description=(
    "ASI Heart Engine (F1,F5,F6,F9): EVIDENCE → EMPATHY → EVALUATE → ACT. "
    "Actions: evidence (gather facts), empathize (stakeholder analysis), "
    "evaluate (safety check), act (execute), witness (observe), "
    "stakeholder (semantic reasoning), diffusion (impact propagation), "
    "audit (constitutional audit), full (complete pipeline)."
))
async def tool_asi(
    action: str = "empathize",
    text: str = "",
    query: str = "",
    session_id: str = "",
    reasoning: str = "",
    agi_context: dict = None,
) -> dict:
    """Route ethical tasks to ASI Heart Kernel."""
    kwargs = {}
    if reasoning:
        kwargs["reasoning"] = reasoning
    if agi_context:
        kwargs["agi_context"] = agi_context
    if not query and text:
        kwargs["query"] = text
    return await bridge_asi_router(
        action=action, text=text, query=query, session_id=session_id, **kwargs
    )

# --- TOOL 4: apex_judge ---

@mcp.tool(name="apex_judge", description=(
    "APEX Soul Engine (F3,F8,F11,F12,F13): EUREKA → DECIDE → PROOF. "
    "Actions: eureka (insight), judge (evaluate), decide (synthesize verdict), "
    "proof (generate evidence), entropy (measure), full (complete pipeline)."
))
async def tool_apex(
    action: str = "judge",
    query: str = "",
    response: str = "",
    session_id: str = "",
    reasoning: str = "",
    safety_evaluation: dict = None,
    authority_check: dict = None,
) -> dict:
    """Route judicial tasks to APEX Soul Kernel."""
    kwargs = {}
    if reasoning:
        kwargs["reasoning"] = reasoning
    if safety_evaluation:
        kwargs["safety_evaluation"] = safety_evaluation
    if authority_check:
        kwargs["authority_check"] = authority_check
    return await bridge_apex_router(
        action=action, query=query, response=response,
        session_id=session_id, **kwargs
    )

# --- TOOL 5: vault_999 ---

@mcp.tool(name="vault_999", description=(
    "VAULT-999 Immutable Memory (F1,F8): Seal decisions, read/write governance "
    "artifacts. Actions: seal (immutable record), list (enumerate artifacts), "
    "read (retrieve), write (store), propose (suggest canon)."
))
async def tool_vault(
    action: str = "seal",
    session_id: str = "",
    verdict: str = "",
    target: str = "",
    query: str = "",
    response: str = "",
    decision_data: dict = None,
) -> dict:
    """Route archival tasks to VAULT-999."""
    kwargs = {}
    if target:
        kwargs["target"] = target
    if query:
        kwargs["query"] = query
    if response:
        kwargs["response"] = response
    if decision_data:
        kwargs["decision_data"] = decision_data
    return await bridge_vault_router(
        action=action, session_id=session_id, verdict=verdict, **kwargs
    )

# --- TOOL 6: trinity_loop ---

@mcp.tool(name="trinity_loop", description=(
    "Trinity Metabolic Loop: Complete AGI→ASI→APEX→VAULT pipeline in one call. "
    "Runs full constitutional governance cycle."
))
async def tool_trinity_loop(
    query: str,
    session_id: str = "",
) -> dict:
    """Run complete Trinity constitutional governance pipeline."""
    return await bridge_trinity_loop_router(
        query=query,
        session_id=session_id or None,
    )

# =============================================================================
# CUSTOM ENDPOINTS
# =============================================================================

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Railway/Docker health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "version": VERSION,
        "mode": "CODEBASE",
        "transport": "streamable-http",
        "tools": 6,
        "architecture": "v53.2.0-simplified",
    })

@mcp.custom_route("/metrics/json", methods=["GET"])
async def metrics_endpoint(request):
    """Constitutional telemetry metrics."""
    return JSONResponse(get_full_metrics())

# =============================================================================
# APP EXPORT — Streamable HTTP (with legacy SSE fallback)
# =============================================================================

# Try Streamable HTTP first (MCP protocol 2024-11-05+), fall back to SSE
try:
    app = mcp.streamable_http_app()
    _transport_mode = "streamable-http"
except AttributeError:
    # Older mcp SDK version — fall back to legacy SSE
    app = mcp.sse_app()
    _transport_mode = "sse-legacy"

# =============================================================================
# ENTRY POINTS
# =============================================================================

def main():
    """
    Main entry point for codebase-mcp-sse command.

    Used by:
      - pyproject.toml: codebase-mcp-sse = "codebase.mcp.sse:main"
      - railway.toml: startCommand = "codebase-mcp-sse"
      - Dockerfile: CMD ["codebase-mcp-sse"]
    """
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    print(f"[BOOT] AAA MCP Server {VERSION}")
    print(f"   Transport: {_transport_mode}")
    print(f"   Tools: 6 (init_000, agi_genius, asi_act, apex_judge, vault_999, trinity_loop)")
    print(f"   Endpoints: /mcp (protocol), /health (liveness), /metrics/json (telemetry)")
    print(f"   Host: 0.0.0.0:{port}")
    print(f"   Compatible: ChatGPT Dev Mode, Codex, any MCP HTTP client")

    uvicorn.run(app, host="0.0.0.0", port=port)


def create_sse_app() -> Any:
    """
    Create app for compatibility with trinity_server.py.

    Returns the FastMCP server's ASGI application.
    """
    return app


if __name__ == "__main__":
    main()
