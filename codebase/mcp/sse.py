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
    """Interactive Discovery Hub - Trinity Primary Color Edition."""
    from starlette.responses import HTMLResponse
    m = get_full_metrics()
    version = m.get('version', VERSION)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>arifOS Hub | Trinity v53</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #000000;
                --card: #0a0a0a;
                --text: #ffffff;
                --text-dim: #a0a0a0;
                --trinity-blue: #0070f3;  /* Mind (AGI) */
                --trinity-red: #ff0000;   /* Heart (ASI) */
                --trinity-yellow: #ffcc00; /* Soul (APEX) */
                --border: #1a1a1a;
            }}
            * {{ box-sizing: border-box; transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1); }}
            body {{
                font-family: 'Inter', sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                line-height: 1.6;
                overflow-x: hidden;
            }}
            .container {{ max-width: 1000px; margin: 0 auto; padding: 60px 20px; }}
            
            /* High-Contrast Header */
            header {{
                text-align: center;
                padding: 80px 20px;
                border: 1px solid var(--border);
                border-radius: 32px;
                margin-bottom: 60px;
                background: linear-gradient(180deg, #050505 0%, #000 100%);
            }}
            .logo-section {{
               margin-bottom: 30px;
            }}
            .trinity-ring {{
                width: 120px; height: 120px;
                margin: 0 auto;
                position: relative;
                border-radius: 50%;
                background: conic-gradient(
                    var(--trinity-blue) 0deg 120deg, 
                    var(--trinity-red) 120deg 240deg, 
                    var(--trinity-yellow) 240deg 360deg
                );
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0 0 50px rgba(255, 255, 255, 0.05);
            }}
            .trinity-ring::after {{
                content: '';
                position: absolute;
                width: 100px; height: 100px;
                background: #000;
                border-radius: 50%;
            }}
            .trinity-ring span {{
                position: relative; z-index: 10; font-size: 2rem; font-weight: 800;
                background: linear-gradient(135deg, #fff 0%, #a0a0a0 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            }}

            h1 {{ font-size: 3.5rem; margin: 20px 0 10px; font-weight: 800; letter-spacing: -2px; }}
            .tagline {{ color: var(--trinity-yellow); font-family: 'JetBrains Mono', monospace; font-size: 1.2rem; text-transform: uppercase; letter-spacing: 4px; }}
            .bio {{ color: var(--text-dim); margin-top: 25px; font-size: 1.1rem; max-width: 650px; margin-left: auto; margin-right: auto; }}

            /* Status & Version */
            .meta-strip {{
                display: flex; gap: 30px; justify-content: center; margin-top: 40px;
                font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
            }}
            .meta-item {{ display: flex; align-items: center; gap: 10px; color: var(--text-dim); }}
            .status-dot {{ width: 10px; height: 10px; border-radius: 2px; background: var(--trinity-yellow); box-shadow: 0 0 15px var(--trinity-yellow); }}

            /* Grid Layout */
            .section-label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 5px; color: #444; margin-bottom: 30px; display: block; text-align: center; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-bottom: 60px; }}
            .card {{
                background: var(--card);
                padding: 40px;
                border-radius: 24px;
                border: 1px solid var(--border);
                position: relative;
            }}
            .card:hover {{ border-color: #333; transform: scale(1.02); }}
            .card.blue {{ border-left: 6px solid var(--trinity-blue); }}
            .card.red {{ border-left: 6px solid var(--trinity-red); }}
            .card.yellow {{ border-left: 6px solid var(--trinity-yellow); }}
            
            .card h3 {{ margin: 0 0 15px 0; font-size: 1.5rem; font-weight: 700; }}
            .card p {{ margin: 0; font-size: 1rem; color: var(--text-dim); }}
            
            /* Connection Box */
            .hub-card {{ background: #050505; border: 1px solid #1a1a1a; padding: 40px; border-radius: 32px; }}
            .connection-box {{
                background: #000;
                padding: 30px;
                border-radius: 20px;
                border: 1px solid var(--trinity-blue);
                margin: 25px 0;
            }}
            code {{ font-family: 'JetBrains Mono', monospace; color: var(--trinity-blue); font-size: 1rem; }}
            .copy-row {{ display: flex; align-items: center; justify-content: space-between; margin-top: 15px; }}
            .copy-btn {{ background: #fff; color: #000; border: none; padding: 8px 20px; border-radius: 6px; font-weight: 800; cursor: pointer; }}

            /* Utility classes */
            .text-blue {{ color: var(--trinity-blue); }}
            .text-red {{ color: var(--trinity-red); }}
            .text-yellow {{ color: var(--trinity-yellow); }}

            footer {{ text-align: center; margin-top: 100px; color: #333; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }}
            .footer-links {{ display: flex; justify-content: center; gap: 40px; margin-bottom: 30px; }}
            .footer-links a {{ color: var(--text-dim); text-decoration: none; }}
            .footer-links a:hover {{ color: #fff; }}

            @media (max-width: 600px) {{
                h1 {{ font-size: 2.5rem; }}
                .grid {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="logo-section">
                    <div class="trinity-ring"><span>ΔΩΨ</span></div>
                </div>
                <h1>arifOS v53</h1>
                <div class="tagline">DITEMPA BUKAN DIBERI</div>
                <p class="bio">The Supreme Constitutional AI Framework. Absolute truth through metabolic isolation of Mind, Heart, and Soul.</p>
                <div class="meta-strip">
                    <div class="meta-item"><span class="status-dot"></span> SYSTEM_LIVE</div>
                    <div class="meta-item">KERNEL: {version}</div>
                    <div class="meta-item">MODE: TRINITY_PRIMARY</div>
                </div>
            </header>

            <span class="section-label">THE SUPREME ENGINES</span>
            <div class="grid">
                <div class="card blue">
                    <h3 class="text-blue">Δ MIND</h3>
                    <p>Analytical cold logic. High-fidelity reasoning and pattern recognition. Enforces Truth and Factual Integrity.</p>
                </div>
                <div class="card red">
                    <h3 class="text-red">Ω HEART</h3>
                    <p>Ethical validation. Empathetic alignment and safety auditing. Enforces Amanah and Peace.</p>
                </div>
                <div class="card yellow">
                    <h3 class="text-yellow">Ψ SOUL</h3>
                    <p>Constitutional judgment. Final judicial verdict and cryptographic sealing. Absolute Authority.</p>
                </div>
            </div>

            <div class="hub-card">
                <span class="section-label" style="text-align:left">GATEWAY_ACCESS</span>
                <h2 style="font-size: 2rem; margin: 10px 0;">Unified MCP Protocol</h2>
                <div class="connection-box">
                    <div class="copy-row">
                        <code>https://arif-fazil.com/mcp</code>
                        <button class="copy-btn" onclick="navigator.clipboard.writeText('https://arif-fazil.com/mcp')">COPY HUB_URL</button>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;">
                    <a href="/dashboard" style="text-decoration:none">
                        <div class="card" style="padding: 25px; border-color: var(--trinity-yellow);">
                            <h3 class="text-yellow">DASHBOARD</h3>
                            <p>Live metrics and decision stream.</p>
                        </div>
                    </a>
                    <a href="/metrics/json" style="text-decoration:none">
                        <div class="card" style="padding: 25px; border-color: var(--trinity-blue);">
                            <h3 class="text-blue">METRICS API</h3>
                            <p>Raw constitutional telemetry JSON.</p>
                        </div>
                    </a>
                </div>
            </div>

            <footer>
                <div class="footer-links">
                    <a href="https://github.com/ariffazil/arifOS">GITHUB_SOURCE</a>
                    <a href="/health">HEALTH_CHECK</a>
                    <a href="https://arif-fazil.com">CANON_SITE</a>
                </div>
                <p>&copy; 2026 GOVERNOR ARIF FAZIL // SEALED IN VAULT_999</p>
            </footer>
        </div>
    </body>
    </html>
    """)

@mcp.custom_route("/dashboard", methods=["GET"])
async def live_dashboard(request):
    """Trinity Monitor v53 (Primary Palette)."""
    from starlette.responses import HTMLResponse
    m = get_full_metrics()
    
    active_count = m.get('active_sessions', 0)
    verdicts_total = m.get('total_verdicts', 0)
    rps = m.get('rps', 0.0)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>arifOS Monitor | Trinity</title>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #000;
                --blue: #0070f3;
                --red: #ff0000;
                --yellow: #ffcc00;
            }}
            body {{ background: var(--bg); color: #fff; font-family: 'JetBrains Mono', monospace; padding: 40px; }}
            h1 {{ border-left: 10px solid var(--yellow); padding-left: 20px; font-size: 2.5rem; letter-spacing: -2px; margin-bottom: 50px; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; }}
            .stat-card {{ background: #050505; padding: 30px; border: 1px solid #111; border-radius: 20px; }}
            .stat-card.blue {{ border-bottom: 4px solid var(--blue); }}
            .stat-card.red {{ border-bottom: 4px solid var(--red); }}
            .stat-card.yellow {{ border-bottom: 4px solid var(--yellow); }}
            .label {{ color: #444; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; }}
            .metric {{ font-size: 3rem; font-weight: 800; margin-top: 10px; }}
            .footer {{ margin-top: 60px; color: #222; font-size: 0.7rem; }}
        </style>
    </head>
    <body>
        <h1>[TRINITY_MONITOR_v53]</h1>
        <div class="stat-grid">
            <div class="stat-card yellow">
                <div class="label">Total Verdicts</div>
                <div class="metric">{verdicts_total}</div>
            </div>
            <div class="stat-card blue">
                <div class="label">Active Sessions</div>
                <div class="metric">{active_count}</div>
            </div>
            <div class="stat-card red">
                <div class="label">Metabolic Rate</div>
                <div class="metric">{rps:.2f}</div>
            </div>
        </div>
        <div class="footer">STREAMS COOLING IN VAULT_999 // AUTO_REFRESH_5S</div>
        <script>setTimeout(() => location.reload(), 5000);</script>
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
    print("   Tools: 6 (init_000, agi_genius, asi_act, apex_judge, vault_999, trinity_loop)")
    print("   Endpoints: /mcp (protocol), /health (liveness), /metrics/json (telemetry)")
    print(f"   Host: 0.0.0.0:{port}")
    print("   Compatible: ChatGPT Dev Mode, Codex, any MCP HTTP client")

    uvicorn.run(app, host="0.0.0.0", port=port)


def create_sse_app() -> Any:
    """
    Create app for compatibility with trinity_server.py.

    Returns the FastMCP server's ASGI application.
    """
    return app


if __name__ == "__main__":
    main()
