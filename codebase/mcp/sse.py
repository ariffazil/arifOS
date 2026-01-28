"""
codebase.mcp.sse (v53.2.7-CODEBASE-AAA7)
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
# Import Codebase Routers (Bridge) — v53.2.7 AAA 7-Core Architecture
# INIT, AGI, ASI, APEX, VAULT, TRINITY, REALITY
from codebase.mcp.bridge import (
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
    bridge_trinity_loop_router,
    bridge_reality_check_router,
)
from codebase.mcp.constitutional_metrics import get_full_metrics
from codebase.mcp.rate_limiter import rate_limited

logger = logging.getLogger(__name__)

VERSION = "v53.2.7-CODEBASE-AAA7"

# =============================================================================
# FASTMCP SERVER (7-Core Tool Architecture)
# =============================================================================

mcp = FastMCP(
    "AAA-MCP-CODEBASE",
    dependencies=["arifos"],
    host="0.0.0.0",
    port=int(os.getenv("PORT", 8000)),
    stateless_http=True,
    json_response=True,
)

# --- TOOL 1: INIT ---
# MCP Resource: Session setup, authority check, budget allocation

@mcp.tool(name="_init_", description=(
    "_init_: Session initialization, authority verification, and budget allocation. "
    "Fail-closed access control and resource management. "
    "MCP Resource primitive for governance grounding."
))
@rate_limited("_init_")
async def tool_init(
    action: str = "init",
    query: str = "",
    session_id: str = "",
    user_token: str = "",
    **kwargs,
) -> dict:
    """Initialize constitutional session or verify identity."""
    return await bridge_init_router(
        action=action, query=query, session_id=session_id, user_token=user_token
    )

# --- TOOL 2: AGI ---
# MCP Tool: Deep reasoning, pattern recognition

@mcp.tool(name="_agi_", description=(
    "_agi_: Deep reasoning and pattern recognition (Mind Engine). "
    "F2 Truth, F4 Clarity, F7 Humility enforcement. "
    "MCP Tool primitive for analytical processing."
))
@rate_limited("_agi_")
async def tool_agi(
    action: str = "sense",
    query: str = "",
    session_id: str = "",
    context: dict = None,
    **kwargs,
) -> dict:
    """Route reasoning tasks to AGI Mind Kernel."""
    kwargs = {}
    if context:
        kwargs["context"] = context
    return await bridge_agi_router(
        action=action, query=query, session_id=session_id, **kwargs
    )

# --- TOOL 3: _asi_ ---
# MCP Tool: Safety, bias, empathy audit

@mcp.tool(name="_asi_", description=(
    "_asi_: Audit - Safety, bias, and empathy evaluation (Heart Engine). "
    "F1 Amanah, F5 Peace, F6 Empathy enforcement. "
    "MCP Tool primitive for ethical validation."
))
@rate_limited("_asi_")
async def tool_asi(
    action: str = "empathize",
    text: str = "",
    query: str = "",
    session_id: str = "",
    reasoning: str = "",
    agi_context: dict = None,
    **kwargs,
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

# --- TOOL 4: _apex_ ---
# MCP Tool: Judicial consensus and verdict

@mcp.tool(name="_apex_", description=(
    "_apex_: Judge - Judicial consensus and verdict (Soul Engine). "
    "F3 Consensus, F8 Tri-Witness, F9 Anti-Hantu, F10 Ontology. "
    "Verdicts: SEAL, SABAR, VOID, PARTIAL, 888_HOLD. "
    "MCP Tool primitive for final judgment."
))
@rate_limited("_apex_")
async def tool_apex(
    action: str = "judge",
    query: str = "",
    response: str = "",
    session_id: str = "",
    reasoning: str = "",
    safety_evaluation: dict = None,
    authority_check: dict = None,
    **kwargs,
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

# --- TOOL 5: _vault_ ---
# MCP Resource: Immutable ledger for audit trail

@mcp.tool(name="_vault_", description=(
    "_vault_: Seal - Immutable ledger for audit trail and governance artifacts. "
    "F1 Amanah (audit), F8 Quality (tri-witness). "
    "Merkle-tree sealed, cryptographically immutable. "
    "MCP Resource primitive for provenance."
))
@rate_limited("_vault_")
async def tool_vault(
    action: str = "seal",
    session_id: str = "",
    verdict: str = "",
    target: str = "",
    query: str = "",
    response: str = "",
    decision_data: dict = None,
    **kwargs,
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

# --- TOOL 6: _trinity_ ---
# MCP Tool + Resource: Full metabolic loop

@mcp.tool(name="_trinity_", description=(
    "_trinity_: Orchestrate - Complete metabolic cycle AGI→ASI→APEX→VAULT. "
    "Full constitutional governance cycle with all 13 floors. "
    "Combines Tool (processing) + Resource (audit) primitives."
))
async def tool_trinity_loop(
    query: str,
    session_id: str = "",
    **kwargs,
) -> dict:
    """Run complete Trinity constitutional governance pipeline."""
    return await bridge_trinity_loop_router(
        query=query,
        session_id=session_id or None,
    )

# --- TOOL 7: _reality_ ---

@mcp.tool(name="_reality_", description=(
    "_reality_: Ground - Fact-checking via external sources (Brave Search). "
    "F7 (Humility) explicit disclosure of external data. "
    "MCP Resource primitive for reality grounding."
))
async def tool_reality(
    query: str,
    session_id: str = "",
    **kwargs,
) -> dict:
    """Reality grounding and factual verification."""
    return await bridge_reality_check_router(
        query=query, session_id=session_id
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
        "tools": 7,
        "architecture": "AAA-7CORE-v53.2.7",
    })

@mcp.custom_route("/metrics/json", methods=["GET"])
async def metrics_endpoint(request):
    """Constitutional telemetry metrics."""
    return JSONResponse(get_full_metrics())

@mcp.custom_route("/arifos", methods=["GET"])
async def arifos_framework_page(request):
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
                    <div class="meta-item"><span class="status-dot"></span> AAA-7CORE</div>
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
                        <button class="copy-btn" onclick="navigator.clipboard.writeText('https://arif-fazil.com/mcp')">COPY MCP_URL</button>
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
                    <a href="/">PORTFOLIO</a>
                    <a href="/aaa">AAA_MCP</a>
                </div>
                <p>&copy; 2026 GOVERNOR ARIF FAZIL // SEALED IN VAULT_999</p>
            </footer>
        </div>
    </body>
    </html>
    """)

@mcp.custom_route("/", methods=["GET"])
async def personal_portfolio(request):
    """Muhammad Arif Fazil - Personal Portfolio."""
    from starlette.responses import HTMLResponse
    
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Arif Fazil | AI Governance Architect</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
            :root { --bg: #0a0a0a; --text: #fff; --accent: #0070f3; --dim: #888; }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }
            .container { max-width: 900px; margin: 0 auto; padding: 80px 20px; }
            header { margin-bottom: 60px; }
            h1 { font-size: 3rem; font-weight: 800; letter-spacing: -2px; margin-bottom: 10px; }
            .tagline { color: var(--accent); font-weight: 600; font-size: 1.1rem; }
            .bio { margin: 30px 0; color: var(--dim); font-size: 1.1rem; max-width: 600px; }
            .links { display: flex; gap: 30px; margin-top: 40px; flex-wrap: wrap; }
            .links a { color: var(--text); text-decoration: none; border-bottom: 2px solid var(--accent); padding-bottom: 2px; }
            .links a:hover { color: var(--accent); }
            .section { margin-top: 80px; }
            .section h2 { font-size: 1.2rem; color: var(--dim); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 30px; }
            .project { border: 1px solid #222; padding: 30px; border-radius: 12px; margin-bottom: 20px; }
            .project h3 { font-size: 1.4rem; margin-bottom: 10px; }
            .project p { color: var(--dim); }
            .project a { color: var(--accent); text-decoration: none; }
            footer { margin-top: 100px; color: #444; font-size: 0.9rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Arif Fazil</h1>
                <div class="tagline">AI Governance Architect</div>
                <p class="bio">
                    Building constitutional AI frameworks that enforce safety through 
                    thermodynamic law. Creator of arifOS — a trinity-based governance 
                    system for artificial intelligence.
                </p>
                <div class="links">
                    <a href="https://github.com/ariffazil">GitHub</a>
                    <a href="/arifos">arifOS Framework</a>
                    <a href="/aaa">AAA MCP Server</a>
                </div>
            </header>
            
            <div class="section">
                <h2>Featured Project</h2>
                <div class="project">
                    <h3>🧠 arifOS</h3>
                    <p>
                        Constitutional AI governance framework enforcing 13 immutable floors (F1-F13) 
                        through metabolic isolation of Mind (AGI), Heart (ASI), and Soul (APEX).
                    </p>
                    <p style="margin-top: 15px;">
                        <a href="/arifos">Explore the Framework →</a>
                    </p>
                </div>
            </div>
            
            <footer>
                <p>Penang, Malaysia · DITEMPA BUKAN DIBERI</p>
            </footer>
        </div>
    </body>
    </html>
    """)

@mcp.custom_route("/aaa", methods=["GET"])
async def aaa_mcp_page(request):
    """AAA MCP Server - Constitutional AI Tools."""
    from starlette.responses import HTMLResponse
    
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AAA MCP | Constitutional AI Tools</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
        <style>
            :root { --bg: #000; --card: #0a0a0a; --text: #fff; --dim: #888; --blue: #0070f3; --red: #ff0000; --yellow: #ffcc00; }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }
            .container { max-width: 1000px; margin: 0 auto; padding: 60px 20px; }
            header { text-align: center; margin-bottom: 60px; }
            h1 { font-size: 3rem; font-weight: 800; letter-spacing: -2px; }
            .subtitle { color: var(--dim); margin-top: 10px; }
            .mcp-url { background: var(--card); border: 1px solid #222; padding: 20px; border-radius: 12px; margin: 30px 0; font-family: 'JetBrains Mono', monospace; }
            .mcp-url code { color: var(--yellow); font-size: 1.1rem; }
            .tools { display: grid; gap: 20px; margin-top: 40px; }
            .tool { background: var(--card); border: 1px solid #222; padding: 25px; border-radius: 12px; border-left: 4px solid var(--blue); }
            .tool.heart { border-left-color: var(--red); }
            .tool.soul { border-left-color: var(--yellow); }
            .tool h3 { font-size: 1.2rem; margin-bottom: 10px; }
            .tool p { color: var(--dim); font-size: 0.95rem; }
            .tag { display: inline-block; background: #111; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; margin-top: 10px; margin-right: 5px; }
            footer { margin-top: 80px; text-align: center; color: #444; font-size: 0.9rem; }
            footer a { color: var(--dim); text-decoration: none; margin: 0 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>AAA MCP Server</h1>
                <p class="subtitle">Constitutional AI Governance via Model Context Protocol</p>
                <div class="mcp-url">
                    <span style="color: var(--dim);">Endpoint:</span><br>
                    <code>https://arif-fazil.com/mcp</code>
                </div>
            </header>
            
            <div class="tools">
                <div class="tool">
                    <h3>🚪 _init_</h3>
                    <p>Initialize - Session bootstrap, authority verification, budget allocation.</p>
                    <span class="tag">Resource</span>
                    <span class="tag">F1 F11 F12</span>
                </div>
                <div class="tool">
                    <h3>🧠 _agi_</h3>
                    <p>Reason - Deep logical analysis and pattern recognition (Mind Engine).</p>
                    <span class="tag">Tool</span>
                    <span class="tag">F2 F4 F7</span>
                </div>
                <div class="tool heart">
                    <h3>❤️ _asi_</h3>
                    <p>Audit - Safety, bias, and empathy evaluation (Heart Engine).</p>
                    <span class="tag">Tool</span>
                    <span class="tag">F1 F5 F6</span>
                </div>
                <div class="tool soul">
                    <h3>⚖️ _apex_</h3>
                    <p>Judge - Judicial consensus and verdict (Soul Engine).</p>
                    <span class="tag">Tool</span>
                    <span class="tag">F3 F8 F9 F10</span>
                </div>
                <div class="tool soul">
                    <h3>🔒 _vault_</h3>
                    <p>Seal - Immutable cryptographic ledger for audit trail.</p>
                    <span class="tag">Resource</span>
                    <span class="tag">F1 F8</span>
                </div>
                <div class="tool">
                    <h3>🔄 _trinity_</h3>
                    <p>Orchestrate - Full metabolic cycle AGI→ASI→APEX→VAULT.</p>
                    <span class="tag">Tool+Resource</span>
                    <span class="tag">All Floors</span>
                </div>
                <div class="tool blue">
                    <h3>🌍 _reality_</h3>
                    <p>Ground - Fact-checking via external sources (Brave Search).</p>
                    <span class="tag">Resource</span>
                    <span class="tag">F7 Humility</span>
                </div>
            </div>
            
            <footer>
                <a href="/">← Back to Portfolio</a>
                <a href="/arifos">arifOS Framework →</a>
            </footer>
        </div>
    </body>
    </html>
    """)

@mcp.custom_route("/dashboard", methods=["GET"])
async def live_dashboard(request):
    """Trinity Monitor v53.2.7 — AAA 7-Core Architecture."""
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
    print("   Tools: 7 (_init_, _agi_, _asi_, _apex_, _vault_, _trinity_, _reality_)")
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
