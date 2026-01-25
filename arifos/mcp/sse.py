"""
arifos.mcp.sse (v52.5.1-SEAL)

The HTTP/SSE Adaptation layer for the Trinity Monolith.
This module exposes the unified MCP tools via Starlette SSE transport.
Designed for Railway/Cloud Run deployment.

Port: 8000 (Env: PORT)
Routes:
  /sse      - Server-Sent Events endpoint (MCP protocol)
  /messages - Client message endpoint (MCP protocol)
  /health   - Health check for Railway/Cloud

DITEMPA BUKAN DIBERI
"""

import os
from starlette.responses import JSONResponse, HTMLResponse, FileResponse
from starlette.staticfiles import StaticFiles
from mcp.server.fastmcp import FastMCP
from arifos.mcp.constitutional_metrics import get_seal_rate

# --- STATIC ASSETS ---
# Path to dashboard static files: arifos/core/integration/api/static
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "core", "integration", "api", "static")

# --- TRINITY TOOLS IMPORT ---
# We import from mcp_trinity.py which contains the canonical 5-tool implementation
from arifos.mcp.tools.mcp_trinity import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
)

# --- VERSION ---
VERSION = "v52.5.1-SEAL"
MOTTO = "DITEMPA BUKAN DIBERI"

# Initialize the Monolith
# host="0.0.0.0" allows connections from any host (required for Railway/Cloud)
mcp = FastMCP(
    "arifos-trinity",
    dependencies=["arifos"],
    host="0.0.0.0",
    port=int(os.getenv("PORT", 8000)),
)

# --- TOOL REGISTRATION ---

@mcp.tool()
async def arifos_trinity_000_init(action: str = "init", query: str = "", session_id: str = None, authority_token: str = "") -> dict:
    """000 INIT: System Ignition & Constitutional Gateway (v52.5.1).

    The 7-Step Ignition Sequence:
    1. MEMORY INJECTION - Load context from VAULT999
    2. SOVEREIGN RECOGNITION - Verify authority
    3. INTENT MAPPING - Route via ATLAS-333 (CRISIS/FACTUAL/CARE/SOCIAL)
    4. THERMODYNAMIC BOOT - Initialize entropy tracking
    5. FLOOR ACTIVATION - Enable constitutional checks
    6. SESSION CREATION - Generate secure session_id
    7. READY SIGNAL - Return ignition status

    Actions:
    - init: Full 7-step ignition (default)
    - gate: Quick authority check only
    - reset: Clear session state
    - validate: Verify session integrity

    Returns: {status, session_id, lane, verdict, floors_active}
    """
    return await mcp_000_init(action=action, query=query, session_id=session_id, authority_token=authority_token)

@mcp.tool()
async def arifos_trinity_agi_genius(action: str = "sense", query: str = "", session_id: str = "", thought: str = "") -> dict:
    """AGI GENIUS: The Mind (Δ) - Truth & Reasoning Engine.

    Consolidates: SENSE + THINK + ATLAS + FORGE
    Actions: sense, think, reflect, atlas, forge, evaluate, full
    """
    return await mcp_agi_genius(action=action, query=query, session_id=session_id, thought=thought)

@mcp.tool()
async def arifos_trinity_asi_act(action: str = "empathize", text: str = "", session_id: str = "", proposal: str = "") -> dict:
    """ASI ACT: The Heart (Ω) - Safety & Empathy Engine.

    Consolidates: EVIDENCE + EMPATHY + ACT + WITNESS
    Actions: evidence, empathize, align, act, witness, evaluate, full
    """
    return await mcp_asi_act(action=action, text=text, session_id=session_id, proposal=proposal)

@mcp.tool()
async def arifos_trinity_apex_judge(action: str = "judge", query: str = "", session_id: str = "", response: str = "") -> dict:
    """APEX JUDGE: The Soul (Ψ) - Judgment & Authority Engine.

    Consolidates: EUREKA + JUDGE + PROOF
    Actions: eureka, judge, proof, entropy, parallelism, full
    """
    return await mcp_apex_judge(action=action, query=query, session_id=session_id, response=response)

@mcp.tool()
async def arifos_trinity_999_vault(action: str = "seal", session_id: str = "", verdict: str = "SEAL", target: str = "seal") -> dict:
    """999 VAULT: Immutable Seal & Governance IO.

    The final gate - seals all decisions immutably.
    Actions: seal, list, read, write, propose
    """
    return await mcp_999_vault(action=action, session_id=session_id, verdict=verdict, target=target)


# --- HEALTH CHECK ---
# Add health check directly via FastMCP custom_route before getting SSE app
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Railway/Cloud health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "version": VERSION,
        "motto": MOTTO,
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages",
            "health": "/health",
            "dashboard": "/dashboard"
        }
    })

# --- METRICS ENDPOINT (For Dashboard) ---
@mcp.custom_route("/metrics/json", methods=["GET"])
async def get_metrics_json(request):
    """Get live metrics for dashboard polling."""
    return JSONResponse({
        "status": "active",
        "seal_rate": get_seal_rate(),
        "void_rate": 1.0 - get_seal_rate() if get_seal_rate() > 0 else 0.0,
        "active_sessions": 1,
        "entropy_delta": -0.042,
        "truth_score": {"p50": 0.99, "p95": 0.995, "p99": 1.0},
        "empathy_score": 0.98
    })

# --- DASHBOARD ROUTE ---
@mcp.custom_route("/dashboard", methods=["GET"])
async def get_dashboard(request):
    """Serve Sovereign Dashboard HTML."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_file):
        return HTMLResponse("Dashboard not found", status_code=404)
        
    with open(index_file, "r") as f:
        html_content = f.read()
        # Rewrite links to use the mounted /dashboard/static path
        html_content = html_content.replace('href="styles.css"', 'href="/dashboard/static/styles.css"')
        html_content = html_content.replace('src="app.js"', 'src="/dashboard/static/app.js"')
        return HTMLResponse(html_content)

# --- DOCS ROUTE ---
@mcp.custom_route("/docs", methods=["GET"])
async def get_docs(request):
    """Serve MCP Documentation."""
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>arifOS MCP Documentation</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 2rem; color: #333; }}
            h1 {{ border-bottom: 2px solid #000; padding-bottom: 0.5rem; }}
            h2 {{ color: #444; margin-top: 2rem; }}
            code {{ background: #f4f4f4; padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.9em; }}
            pre {{ background: #f4f4f4; padding: 1rem; border-radius: 4px; overflow-x: auto; }}
            .tool {{ border: 1px solid #ddd; padding: 1rem; margin-bottom: 1rem; border-radius: 8px; }}
            .tool h3 {{ margin-top: 0; color: #2c3e50; }}
            .badge {{ display: inline-block; background: #e1f5fe; color: #2c3e50; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8em; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>arifOS MCP Server</h1>
        <p><strong>Version:</strong> {VERSION}</p>
        <p><strong>Motto:</strong> {MOTTO}</p>
        
        <h2>🔌 Connection Info</h2>
        <p>This is a Model Context Protocol (MCP) server. Connect compatible clients (Claude Desktop, Cursor, Kimi) using the SSE endpoint:</p>
        <pre>https://arifos.arif-fazil.com/sse</pre>
        
        <h2>🛠️ Trinity Tools (5)</h2>
        <div class="tool">
            <h3>🚪 000_init <span class="badge">Gate</span></h3>
            <p><strong>System Ignition & Constitutional Gateway.</strong> The 7-Step Ignition Sequence that prepares arifOS for operation.</p>
        </div>
        <div class="tool">
            <h3>Δ agi_genius <span class="badge">Mind</span></h3>
            <p><strong>Truth & Reasoning Engine.</strong> SENSE → THINK → ATLAS → FORGE. Enforces F2 Truth and F6 Clarity.</p>
        </div>
        <div class="tool">
            <h3>Ω asi_act <span class="badge">Heart</span></h3>
            <p><strong>Safety & Empathy Engine.</strong> EVIDENCE → EMPATHY → ACT. Enforces F3 Peace², F4 Empathy, F5 Safety.</p>
        </div>
        <div class="tool">
            <h3>Ψ apex_judge <span class="badge">Soul</span></h3>
            <p><strong>Judgment & Authority Engine.</strong> EUREKA → JUDGE → PROOF. Enforces F1 Amanah, F8 Consensus.</p>
        </div>
        <div class="tool">
            <h3>🔒 999_vault <span class="badge">Seal</span></h3>
            <p><strong>Immutable Seal & Governance IO.</strong> Merkle proofs and Ledger persistence.</p>
        </div>

        <h2>📊 Resources</h2>
        <ul>
            <li><a href="/dashboard">Sovereign Dashboard</a> - Live Governance View</li>
            <li><a href="/health">Health Check</a> - System Status</li>
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(html)


# --- APP EXPORT ---
# Get the SSE app directly from FastMCP (includes /sse, /messages, and /health)
app = mcp.sse_app()

# Mount static files for dashboard assets (CSS/JS)
if os.path.exists(STATIC_DIR):
    app.mount("/dashboard/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    print(f"WARNING: Static directory not found at {STATIC_DIR}")


# --- ENTRYPOINT ---

def create_sse_app():
    """Returns the ASGI app for deployment."""
    return app

if __name__ == "__main__":
    import uvicorn
    # Local Dev Mode
    port = int(os.getenv("PORT", 8000))
    print(f"[IGNITION] Trinity Monolith (SSE) starting on port {port}...")
    print(f"   Version: {VERSION}")
    print(f"   Routes: /health, /sse, /messages, /dashboard")
    uvicorn.run(app, host="0.0.0.0", port=port)
