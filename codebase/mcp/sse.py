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

@mcp.custom_route("/", methods=["GET"])
async def discovery_landing(request):
    """Interactive discovery page - first impression of API."""
    from starlette.responses import HTMLResponse
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>arifOS v53 | Constitutional AI</title>
        <style>
            :root {{ --primary: #32b8c6; --bg: #0a0e14; --card: #151c26; --text: #e0e6ed; }}
            body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 40px; margin: 0; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            h1 {{ color: var(--primary); font-size: 2.5rem; margin-bottom: 0.5rem; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 2rem; }}
            .card {{ background: var(--card); padding: 20px; border-radius: 12px; border-left: 4px solid var(--primary); font-size: 0.9rem; }}
            .card h3 {{ color: var(--primary); margin-top: 0; }}
            .btn {{ display: inline-block; background: var(--primary); color: var(--bg); padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 1rem; cursor: pointer; }}
            .btn:hover {{ opacity: 0.9; }}
            code {{ background: #1a232e; padding: 2px 6px; border-radius: 4px; color: #ff79c6; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>arifOS v53</h1>
            <p>Constitutional AI Framework — <i>Ditempa Bukan Diberi</i></p>
            <div class="grid">
                <div class="card">
                    <h3>🚀 Quick Start</h3>
                    <p>Connect to <code>/mcp</code> using any standard client (ChatGPT, Codex, Zapier).</p>
                    <a href="/dashboard" class="btn">View Live Dashboard</a>
                </div>
                <div class="card">
                    <h3>📜 Native Logic</h3>
                    <p>Version: {VERSION}</p>
                    <p>Mode: NATIVE v53 (Isolated Engines)</p>
                    <a href="/metrics/json" class="btn">Raw Metrics JSON</a>
                </div>
                <div class="card">
                    <h3>🚪 Authorization</h3>
                    <p>Identity verification & injection defense (000/F11/F12).</p>
                </div>
                <div class="card">
                    <h3>🧠 Trinity Loop</h3>
                    <p>Unified AGI→ASI→APEX metabolic cycle.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

@mcp.custom_route("/dashboard", methods=["GET"])
async def live_dashboard(request):
    """Serena-style monitoring dashboard."""
    from starlette.responses import HTMLResponse
    import json
    m = get_full_metrics()
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>arifOS Monitor | Serena</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root {{ --primary: #32b8c6; --danger: #ff5555; --bg: #05070a; --card: #0c1117; }}
            body {{ background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; padding: 20px; }}
            h1 {{ border-bottom: 2px solid var(--primary); padding-bottom: 10px; margin-bottom: 30px; letter-spacing: 2px; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }}
            .stat-card {{ background: var(--card); padding: 15px; border: 1px solid #333; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }}
            .label {{ color: #888; font-size: 10px; text-transform: uppercase; }}
            .metric {{ font-size: 28px; color: var(--primary); font-weight: bold; margin-top: 5px; }}
            .chart-container {{ background: var(--card); padding: 20px; border-radius: 12px; border: 1px solid #333; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>[SERENA] CONSTITUTIONAL_MONITOR_v53</h1>
        <div class="stat-grid">
            <div class="stat-card"><div class="label">RPS (Rate/Sec)</div><div class="metric">{m.get('rps', 0.0):.2f}</div></div>
            <div class="stat-card"><div class="label">Active Sessions</div><div class="metric">{m.get('sessions', {{}}).get('active', 0)}</div></div>
            <div class="stat-card"><div class="label">Total Verdicts</div><div class="metric">{m.get('verdicts_total', 0)}</div></div>
            <div class="stat-card"><div class="label">System Status</div><div class="metric" style="color:#50fa7b">ONLINE</div></div>
        </div>
        <div class="chart-container">
            <h3 style="margin-top:0; color:var(--primary)">Live Decision Stream</h3>
            <canvas id="liveChart" height="100"></canvas>
        </div>
        <script>
            // Simple auto-reload for metrics
            setTimeout(() => location.reload(), 3000);
        </script>
    </body>
    </html>
    """)

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
