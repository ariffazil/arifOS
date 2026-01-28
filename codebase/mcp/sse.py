"""
codebase.mcp.sse (v53.2.1-CODEBASE)
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
from codebase.mcp.rate_limiter import rate_limited

logger = logging.getLogger(__name__)

VERSION = "v53.2.1-CODEBASE"

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
@rate_limited("init_000")
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
@rate_limited("agi_genius")
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
@rate_limited("asi_act")
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
@rate_limited("apex_judge")
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
@rate_limited("vault_999")
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
        "architecture": "v53.2.1-simplified",
    })

@mcp.custom_route("/metrics/json", methods=["GET"])
async def metrics_endpoint(request):
    """Constitutional telemetry metrics."""
    return JSONResponse(get_full_metrics())

@mcp.custom_route("/", methods=["GET"])
async def discovery_landing(request):
    """Interactive Discovery Hub - Unified Landing Page & Documentation."""
    from starlette.responses import HTMLResponse
    m = get_full_metrics()
    uptime = m.get('uptime_hours', 0.0)
    version = m.get('version', VERSION)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>arifOS Hub | Unified AI Governance</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #32b8c6;
                --bg: #05070a;
                --card: rgba(13, 17, 23, 0.8);
                --card-border: rgba(50, 184, 198, 0.2);
                --text: #e6edf3;
                --text-dim: #8b949e;
                --accent-green: #50fa7b;
                --accent-pink: #ff79c6;
                --accent-yellow: #f1fa8c;
            }}
            * {{ box-sizing: border-box; transition: all 0.2s ease-in-out; }}
            body {{
                font-family: 'Inter', sans-serif;
                background-color: var(--bg);
                background-image: 
                    radial-gradient(circle at 10% 10%, rgba(50, 184, 198, 0.1) 0%, transparent 30%),
                    radial-gradient(circle at 90% 90%, rgba(255, 121, 198, 0.05) 0%, transparent 30%);
                color: var(--text);
                margin: 0;
                line-height: 1.6;
                overflow-x: hidden;
            }}
            .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 20px; }}
            
            /* Glassmorphism Header */
            header {{
                text-align: center;
                padding: 60px 20px;
                background: rgba(255, 255, 255, 0.02);
                backdrop-filter: blur(20px);
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                margin-bottom: 40px;
                position: relative;
            }}
            .avatar {{
                width: 110px; height: 110px;
                background: linear-gradient(135deg, var(--primary), #1e293b);
                border-radius: 50%;
                margin: 0 auto 25px;
                display: flex; align-items: center; justify-content: center;
                font-size: 2.5rem; font-weight: 800; color: #fff;
                box-shadow: 0 0 40px rgba(50, 184, 198, 0.4);
                border: 2px solid var(--primary);
            }}
            h1 {{ font-size: 3rem; margin: 0; font-weight: 800; letter-spacing: -1px; }}
            .tagline {{ color: var(--primary); font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; margin-top: 5px; }}
            .bio {{ color: var(--text-dim); margin-top: 20px; font-size: 1.1rem; max-width: 600px; margin-left: auto; margin-right: auto; }}

            /* Status Bar */
            .status-bar {{
                display: flex; gap: 20px; justify-content: center; margin-top: 30px;
            }}
            .status-item {{ font-size: 0.8rem; display: flex; align-items: center; gap: 8px; color: var(--text-dim); }}
            .dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--accent-green); box-shadow: 0 0 10px var(--accent-green); }}

            /* Technical Grid */
            .section-label {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 3px; color: var(--primary); margin-bottom: 20px; display: block; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }}
            .card {{
                background: var(--card);
                padding: 30px;
                border-radius: 20px;
                border: 1px solid var(--card-border);
                position: relative;
                overflow: hidden;
            }}
            .card:hover {{ border-color: var(--primary); transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
            .card h3 {{ margin: 0 0 15px 0; font-size: 1.25rem; color: #fff; display: flex; align-items: center; gap: 12px; }}
            .card p {{ margin: 0; font-size: 0.95rem; color: var(--text-dim); }}
            
            /* Protocol Stack Badges */
            .stack {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 20px; }}
            .badge {{
                background: rgba(50, 184, 198, 0.1);
                padding: 5px 12px;
                border-radius: 6px;
                font-size: 0.75rem;
                font-family: 'JetBrains Mono', monospace;
                color: var(--primary);
                border: 1px solid rgba(50, 184, 198, 0.2);
            }}

            /* Connection Guide */
            .connection-box {{
                background: #0d1117;
                padding: 25px;
                border-radius: 16px;
                border: 1px solid var(--accent-pink);
                margin-top: 20px;
            }}
            code {{ font-family: 'JetBrains Mono', monospace; color: var(--accent-pink); font-size: 0.9rem; }}
            .copy-row {{ display: flex; align-items: center; justify-content: space-between; background: rgba(0,0,0,0.3); padding: 10px 15px; border-radius: 8px; margin-top: 10px; }}
            .copy-btn {{ background: var(--primary); color: var(--bg); border: none; padding: 5px 12px; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 0.7rem; }}
            .copy-btn:active {{ transform: scale(0.95); }}

            /* Footer */
            footer {{ text-align: center; margin-top: 80px; padding-top: 40px; border-top: 1px solid rgba(255,255,255,0.05); }}
            .nav-links {{ display: flex; justify-content: center; gap: 30px; margin-bottom: 20px; }}
            .nav-link {{ color: var(--text-dim); text-decoration: none; font-size: 0.9rem; font-weight: 500; }}
            .nav-link:hover {{ color: var(--primary); }}

            @media (max-width: 600px) {{
                h1 {{ font-size: 2rem; }}
                .status-bar {{ flex-direction: column; align-items: center; gap: 10px; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="avatar">AF</div>
                <h1>arifOS v53</h1>
                <div class="tagline">"DITEMPA BUKAN DIBERI" — Forged, Not Given</div>
                <p class="bio">The world's first metabolic AI governor. Bridging cold logic (Mind), warm empathy (Heart), and constitutional soul (APEX).</p>
                <div class="status-bar">
                    <div class="status-item"><span class="dot"></span> STATUS: ONLINE</div>
                    <div class="status-item">VERSION: {version}</div>
                    <div class="status-item">ARCHITECTURE: TRINITY</div>
                </div>
            </header>

            <span class="section-label">01 // The Trinity Engines</span>
            <div class="grid">
                <div class="card">
                    <h3>🧠 AGI Mind</h3>
                    <p>Delta Engine (Δ): Chain-of-thought logic and knowledge mapping. Enforces Truth (F2) and Humility (F7).</p>
                    <div class="stack">
                        <span class="badge">SENSE</span>
                        <span class="badge">THINK</span>
                        <span class="badge">REASON</span>
                    </div>
                </div>
                <div class="card">
                    <h3>❤️ ASI Heart</h3>
                    <p>Omega Engine (Ω): Safety audit and stakeholder empathy. Enforces Amanah (F1) and Empathy (F6).</p>
                    <div class="stack">
                        <span class="badge">EVIDENCE</span>
                        <span class="badge">EMPATHY</span>
                        <span class="badge">ACT</span>
                    </div>
                </div>
                <div class="card">
                    <h3>⚖️ APEX Soul</h3>
                    <p>Psi Engine (Ψ): Final metabolic judgment. Enforces Tri-Witness Consensus (F3) and Signing.</p>
                    <div class="stack">
                        <span class="badge">EUREKA</span>
                        <span class="badge">DECIDE</span>
                        <span class="badge">PROOF</span>
                    </div>
                </div>
            </div>

            <span class="section-label">02 // Universal Access Hub</span>
            <div class="card" style="border-color: var(--accent-pink);">
                <h3>🚀 Connect Anything</h3>
                <p>Use your arifOS instance as a standard Model Context Protocol (MCP) server. Works with Claude, Cursor, and ChatGPT.</p>
                
                <div class="connection-box">
                    <div class="label" style="font-size: 0.7rem; text-transform: uppercase; color: var(--accent-pink); margin-bottom: 8px;">MCP ENDPOINT URL</div>
                    <div class="copy-row">
                        <code>https://arif-fazil.com/mcp</code>
                        <button class="copy-btn" onclick="navigator.clipboard.writeText('https://arif-fazil.com/mcp')">COPY</button>
                    </div>
                </div>

                <div class="grid" style="margin-top: 30px; grid-template-columns: 1fr 1fr;">
                    <a href="/dashboard" style="text-decoration:none">
                        <div class="card" style="padding: 20px; background: rgba(255,255,255,0.03);">
                            <h3>📊 Live Monitor</h3>
                            <p>Real-time telemetry and decision stream.</p>
                        </div>
                    </a>
                    <a href="/metrics/json" style="text-decoration:none">
                        <div class="card" style="padding: 20px; background: rgba(255,255,255,0.03);">
                            <h3>📈 Metrics Hub</h3>
                            <p>Raw constitutional performance JSON.</p>
                        </div>
                    </a>
                </div>
            </div>

            <footer>
                <div class="nav-links">
                    <a href="https://github.com/ariffazil/arifOS" class="nav-link">GITHUB</a>
                    <a href="/health" class="nav-link">HEALTH</a>
                    <a href="https://arif-fazil.com" class="nav-link">WEBSITE</a>
                </div>
                <p style="color:var(--text-dim)">&copy; 2026 Governor Arif Fazil. All Floors Active.</p>
            </footer>
        </div>
    </body>
    </html>
    """)

@mcp.custom_route("/dashboard", methods=["GET"])
async def live_dashboard(request):
    """Serena-style monitoring dashboard (Fix v53.2.1)."""
    from starlette.responses import HTMLResponse
    m = get_full_metrics()
    
    # Correcting metrics access to prevent 500 error
    active_count = m.get('active_sessions', 0)
    verdicts_total = m.get('total_verdicts', 0)
    rps = m.get('rps', 0.0)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>arifOS Monitor | Serena</title>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root {{ --primary: #32b8c6; --danger: #ff5555; --bg: #05070a; --card: #0c1117; }}
            body {{ background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; padding: 20px; }}
            h1 {{ border-bottom: 2px solid var(--primary); padding-bottom: 10px; margin-bottom: 30px; letter-spacing: 2px; font-weight: 700; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
            .stat-card {{ background: var(--card); padding: 20px; border: 1px solid #333; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }}
            .label {{ color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }}
            .metric {{ font-size: 32px; color: var(--primary); font-weight: bold; margin-top: 8px; }}
            .chart-container {{ background: var(--card); padding: 20px; border-radius: 16px; border: 1px solid #333; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>[SERENA] CONSTITUTIONAL_MONITOR_v53</h1>
        <div class="stat-grid">
            <div class="stat-card">
                <div class="label">RPS (Rate/Sec)</div>
                <div class="metric">{rps:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">Active Sessions</div>
                <div class="metric">{active_count}</div>
            </div>
            <div class="stat-card">
                <div class="label">Total Verdicts</div>
                <div class="metric">{verdicts_total}</div>
            </div>
            <div class="stat-card">
                <div class="label">System Status</div>
                <div class="metric" style="color:#50fa7b">ONLINE</div>
            </div>
        </div>
        <div class="chart-container">
            <h3 style="margin-top:0; color:var(--primary)">Live Decision Stream</h3>
            <canvas id="liveChart" height="100"></canvas>
        </div>
        <script>
            // Simple auto-refresh to keep metrics live
            setTimeout(() => location.reload(), 5000);
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
