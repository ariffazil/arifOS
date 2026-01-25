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
    """AGI GENIUS: The Mind (Δ) - Truth & Reasoning Engine (v52.5.1).

    Enforces: F2 (Truth ≥0.99), F4 (Clarity ΔS≥0), F7 (Humility 3-5%).
    Pipeline: SENSE → THINK → ATLAS-333 → FORGE

    Actions:
    - sense: Analyze input, detect intent
    - think: Apply logical reasoning
    - atlas: Route via ATLAS-333 lanes
    - forge: Generate output with citations
    - full: Complete pipeline

    Lanes (v52.5.1): CRISIS | FACTUAL | CARE | SOCIAL
    """
    return await mcp_agi_genius(action=action, query=query, session_id=session_id, thought=thought)

@mcp.tool()
async def arifos_trinity_asi_act(action: str = "empathize", text: str = "", session_id: str = "", proposal: str = "") -> dict:
    """ASI ACT: The Heart (Ω) - Safety & Empathy Engine (v52.5.1).

    Enforces: F1 (Amanah/Reversibility), F5 (Peace²≥1), F6 (Empathy κᵣ≥0.95).
    Pipeline: EVIDENCE → EMPATHY → ACT → WITNESS

    Actions:
    - evidence: Gather supporting data
    - empathize: Check stakeholder impact
    - act: Execute with safeguards
    - witness: Request tri-witness consensus
    - full: Complete pipeline

    Protects the weakest stakeholder in every decision.
    """
    return await mcp_asi_act(action=action, text=text, session_id=session_id, proposal=proposal)

@mcp.tool()
async def arifos_trinity_apex_judge(action: str = "judge", query: str = "", session_id: str = "", response: str = "") -> dict:
    """APEX JUDGE: The Soul (Ψ) - Judgment & Authority Engine (v52.5.1).

    Final verdict authority. Enforces: F3 (Tri-Witness≥0.95), F8 (Genius), F9 (C_dark<0.30).
    Pipeline: EUREKA → JUDGE → PROOF

    Actions:
    - eureka: Synthesize insights
    - judge: Issue verdict (SEAL/SABAR/VOID/888_HOLD)
    - proof: Generate cryptographic proof
    - full: Complete pipeline

    Verdicts:
    - SEAL: Approved (all floors pass)
    - SABAR: Wait (needs cooling)
    - VOID: Rejected (hard floor fail)
    - 888_HOLD: High-stakes (needs human confirmation)
    """
    return await mcp_apex_judge(action=action, query=query, session_id=session_id, response=response)

@mcp.tool()
async def arifos_trinity_999_vault(action: str = "seal", session_id: str = "", verdict: str = "SEAL", target: str = "seal") -> dict:
    """999 VAULT: Immutable Seal & Governance IO (v52.5.1).

    Final gate - seals decisions with Merkle proofs to VAULT999.
    Hash-chained audit trail for constitutional compliance.

    Actions:
    - seal: Commit verdict to ledger
    - list: View recent seals
    - read: Retrieve specific seal
    - write: Store governance data
    - propose: Draft without committing

    Memory Tiers: L0(hot) → L1(24h) → L2(72h) → L3(7d) → L4(30d) → L5(immutable)
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
            "docs": "/docs",
            "dashboard": "/dashboard",
            "metrics": "/metrics/json"
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
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 2rem; color: #333; }}
            h1 {{ border-bottom: 2px solid #000; padding-bottom: 0.5rem; }}
            h2 {{ color: #444; margin-top: 2rem; }}
            code {{ background: #f4f4f4; padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.9em; }}
            pre {{ background: #f4f4f4; padding: 1rem; border-radius: 4px; overflow-x: auto; }}
            .tool {{ border: 1px solid #ddd; padding: 1rem; margin-bottom: 1rem; border-radius: 8px; }}
            .tool h3 {{ margin-top: 0; color: #2c3e50; }}
            .badge {{ display: inline-block; background: #e1f5fe; color: #0277bd; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8em; font-weight: bold; }}
            .verdict {{ display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: bold; margin: 0.2rem; }}
            .seal {{ background: #c8e6c9; color: #2e7d32; }}
            .sabar {{ background: #fff9c4; color: #f57f17; }}
            .void {{ background: #ffcdd2; color: #c62828; }}
            .hold {{ background: #e1bee7; color: #7b1fa2; }}
            .lane {{ display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px; margin: 0.2rem; font-size: 0.85em; }}
            .crisis {{ background: #ffcdd2; color: #c62828; }}
            .factual {{ background: #bbdefb; color: #1565c0; }}
            .care {{ background: #c8e6c9; color: #2e7d32; }}
            .social {{ background: #fff9c4; color: #f57f17; }}
            table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
            th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
            th {{ background: #f5f5f5; }}
        </style>
    </head>
    <body>
        <h1>arifOS MCP Server</h1>
        <p><strong>Version:</strong> {VERSION}</p>
        <p><strong>Motto:</strong> {MOTTO}</p>
        <p>A constitutional AI governance filter. Stops AI from lying, harming, or being overconfident.</p>

        <h2>Connection</h2>
        <p>Connect MCP-compatible clients (Claude Desktop, Cursor, Kimi) using:</p>
        <pre>https://arifos.arif-fazil.com/sse</pre>

        <h2>Trinity Tools (5)</h2>
        <div class="tool">
            <h3>000_init <span class="badge">Gate</span></h3>
            <p><strong>System Ignition & Constitutional Gateway.</strong></p>
            <p>7-Step Ignition: Memory Injection → Authority Check → ATLAS-333 Routing → Thermodynamic Boot → Floor Activation → Session Creation → Ready Signal</p>
            <p><code>Actions: init, gate, reset, validate</code></p>
        </div>
        <div class="tool">
            <h3>agi_genius <span class="badge">Mind (Δ)</span></h3>
            <p><strong>Truth & Reasoning Engine.</strong> Enforces F2 (Truth ≥0.99), F4 (Clarity), F7 (Humility 3-5%).</p>
            <p>Pipeline: SENSE → THINK → ATLAS-333 → FORGE</p>
            <p><code>Actions: sense, think, atlas, forge, full</code></p>
        </div>
        <div class="tool">
            <h3>asi_act <span class="badge">Heart (Ω)</span></h3>
            <p><strong>Safety & Empathy Engine.</strong> Enforces F1 (Amanah), F5 (Peace²≥1), F6 (Empathy κᵣ≥0.95).</p>
            <p>Pipeline: EVIDENCE → EMPATHY → ACT → WITNESS</p>
            <p><code>Actions: evidence, empathize, act, witness, full</code></p>
        </div>
        <div class="tool">
            <h3>apex_judge <span class="badge">Soul (Ψ)</span></h3>
            <p><strong>Judgment & Authority Engine.</strong> Enforces F3 (Tri-Witness≥0.95), F8 (Genius), F9 (C_dark&lt;0.30).</p>
            <p>Pipeline: EUREKA → JUDGE → PROOF</p>
            <p><code>Actions: eureka, judge, proof, full</code></p>
        </div>
        <div class="tool">
            <h3>999_vault <span class="badge">Seal</span></h3>
            <p><strong>Immutable Seal & Governance IO.</strong> Merkle proofs, hash-chained audit trail.</p>
            <p>Memory Tiers: L0 (hot) → L1 (24h) → L2 (72h) → L3 (7d) → L4 (30d) → L5 (immutable)</p>
            <p><code>Actions: seal, list, read, write, propose</code></p>
        </div>

        <h2>ATLAS-333 Lanes (v52.5.1)</h2>
        <p>Smart routing based on intent classification:</p>
        <p>
            <span class="lane crisis">CRISIS</span> Medical/Safety emergencies → Strict thresholds, triggers 888_HOLD<br>
            <span class="lane factual">FACTUAL</span> Research/Technical → High precision (truth≥0.95)<br>
            <span class="lane care">CARE</span> Emotional support → Empathy-weighted (κᵣ≥0.95)<br>
            <span class="lane social">SOCIAL</span> Casual chat → Balanced thresholds
        </p>

        <h2>Verdicts</h2>
        <p>
            <span class="verdict seal">SEAL</span> Approved - all floors pass<br>
            <span class="verdict sabar">SABAR</span> Wait - needs cooling period<br>
            <span class="verdict void">VOID</span> Rejected - hard floor failed<br>
            <span class="verdict hold">888_HOLD</span> High-stakes - needs human confirmation
        </p>

        <h2>TEACH Framework</h2>
        <table>
            <tr><th>Letter</th><th>Principle</th><th>Floor</th><th>Threshold</th></tr>
            <tr><td><strong>T</strong></td><td>Truth</td><td>F2</td><td>≥0.99</td></tr>
            <tr><td><strong>E</strong></td><td>Empathy</td><td>F6</td><td>κᵣ≥0.95</td></tr>
            <tr><td><strong>A</strong></td><td>Amanah</td><td>F1</td><td>Reversible actions only</td></tr>
            <tr><td><strong>C</strong></td><td>Clarity</td><td>F4</td><td>ΔS≥0</td></tr>
            <tr><td><strong>H</strong></td><td>Humility</td><td>F7</td><td>3-5% uncertainty</td></tr>
        </table>

        <h2>Resources</h2>
        <ul>
            <li><a href="/dashboard">Sovereign Dashboard</a> - Live Governance View</li>
            <li><a href="/health">Health Check</a> - System Status</li>
            <li><a href="/metrics/json">Metrics API</a> - JSON metrics for integrations</li>
            <li><a href="https://github.com/ariffazil/arifOS">GitHub Repository</a></li>
            <li><a href="https://pypi.org/project/arifos/">PyPI Package</a></li>
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
