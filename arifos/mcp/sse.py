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
from arifos.mcp.constitutional_metrics import get_seal_rate, get_full_metrics, record_session_activity

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

# --- LOOP BOOTSTRAP IMPORTS ---
import logging
import uuid
from typing import Dict, List, Any, Optional
from arifos.mcp.session_ledger import (
    open_session,
    close_session,
    get_orphaned_sessions,
    recover_orphaned_session,
)

logger = logging.getLogger(__name__)

# Track active tokens for validation (in-memory, per-process)
_active_tokens: Dict[str, str] = {}  # session_id -> token

def _recover_orphans() -> int:
    """
    Recover any orphaned sessions from previous runs.
    Called at startup and init to ensure crashed sessions are sealed.
    """
    try:
        orphans = get_orphaned_sessions(timeout_minutes=30)
        recovered = 0
        for orphan in orphans:
            try:
                result = recover_orphaned_session(orphan)
                if result.get("sealed"):
                    recovered += 1
                    logger.info(f"Loop Bootstrap: Recovered session {orphan.get('session_id', 'UNKNOWN')[:8]}")
            except Exception as e:
                logger.error(f"Failed to recover orphan {orphan.get('session_id', 'UNKNOWN')[:8]}: {e}")
        return recovered
    except Exception as e:
        logger.warning(f"Loop Bootstrap recovery check failed: {e}")
        return 0

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

@mcp.tool(name="init_000")
async def arifos_trinity_000_init(
    action: str = "init",
    query: str = "",
    session_id: str | None = None,
    authority_token: str | None = "",
    context: Dict[str, Any] | None = None
) -> dict:
    """System Ignition & Constitutional Gateway.

    The Alpha of the system. Initializes the session, verifies authority, and routes the request.
    
    Actions:
    - `init` (default): Full ignition. Requires `query`.
    - `gate`: Quick authority check. Requires `authority_token`.
    - `reset`: Clear session state.
    - `validate`: Verify session integrity.

    Args:
        action: The operation to perform (init, gate, reset, validate).
        query: The initial user query or greeting (Required for `init`).
        session_id: Existing session ID (optional).
        authority_token: Token for sovereign recognition (optional).
        context: Additional context to inject (optional).
    """
    # 1. Loop Bootstrap Recovery
    try:
        recovered = _recover_orphans()
        if recovered > 0:
            logger.info(f"Loop Bootstrap: Recovered {recovered} orphaned session(s)")
    except Exception as e:
        logger.warning(f"Loop Bootstrap recovery failed (continuing): {e}")

    # 2. Execute Init
    result = await mcp_000_init(
        action=action,
        query=query,
        session_id=session_id,
        authority_token=authority_token,
        context=context
    )

    # 3. Track Open Session
    if result.get("status") == "SEAL":
        token = str(uuid.uuid4())
        result["session_token"] = token
        result["loop_bootstrap"] = True
        
        new_session_id = result.get("session_id", "")
        if new_session_id:
            _active_tokens[new_session_id] = token
            try:
                open_session(
                    session_id=new_session_id,
                    token=token,
                    pid=os.getpid(),
                    authority=result.get("authority", "GUEST")
                )
            except Exception as e:
                logger.warning(f"Failed to track open session: {e}")

    return result

@mcp.tool(name="agi_genius")
async def arifos_trinity_agi_genius(
    action: str = "sense",
    query: str = "",
    session_id: str | None = "",
    thought: str = "",
    draft: str = "",
    truth_score: float = 1.0,
    context: Dict[str, Any] | None = None,
    axioms: List[str] | None = None
) -> dict:
    """The Mind (Δ) - Truth & Reasoning Engine.

    The cognitive engine responsible for logic, truth verification (F2), and clarity (F6).
    
    Actions:
    - `sense`: Gather facts & classify intent. Requires `query`.
    - `think`: Deep reasoning (6-Hats). Requires `query` (or `thought`).
    - `reflect`: Entropy check (F6). Requires `query` + `draft`.
    - `atlas`: Meta-cognition mapping. Requires `query`.
    - `forge`: Solution generation & Eureka. Requires `query` (as task).
    - `evaluate`: Floor audit (F2, F6). Requires `query` + `draft` + `truth_score`.
    - `full`: Complete pipeline (Sense->Think->Atlas->Forge).

    Args:
        action: The cognitive operation to perform.
        query: The input text, question, or task description.
        session_id: The session ID from init_000.
        thought: Internal reasoning text (for 'think' or 'reflect').
        draft: The generated response candidate (for 'evaluate' or 'reflect').
        truth_score: Estimated factual accuracy (0.0-1.0) for F2 check.
        context: Previous context or memory injection.
        axioms: List of foundational truths for ATLAS mapping.
    """
    return await mcp_agi_genius(
        action=action,
        query=query,
        session_id=session_id,
        thought=thought,
        draft=draft,
        truth_score=truth_score,
        context=context,
        axioms=axioms
    )

@mcp.tool(name="asi_act")
async def arifos_trinity_asi_act(
    action: str = "empathize",
    text: str = "",
    session_id: str | None = None,
    proposal: str = "",
    query: str = "",
    stakeholders: List[str] | None = None,
    sources: List[str] | None = None,
    agi_result: Dict[str, Any] | None = None,
    witness_request_id: str = "",
    approval: bool = False
) -> dict:
    """The Heart (Ω) - Safety & Empathy Engine.

    The ethical engine responsible for safety (F5), empathy (F4), and action alignment.
    
    Actions:
    - `evidence`: Ground truth in sources. Requires `query` + `sources`.
    - `empathize`: Model stakeholder impact. Requires `text` + `stakeholders`.
    - `align`: Check constitutional compliance. Requires `text` + `agi_result`.
    - `act`: Execute verified action. Requires `proposal` + `witness_request_id`.
    - `witness`: Collect tri-witness signatures. Requires `witness_request_id` + `approval`.
    - `evaluate`: Floor audit (F3, F4, F5). Requires `text`.

    Args:
        action: The ethical operation to perform.
        text: The content to analyze for empathy/safety.
        session_id: The session ID.
        proposal: The proposed action description (for 'act').
        query: The search query for evidence gathering.
        stakeholders: List of affected parties (e.g. ["user", "environment"]).
        sources: List of trusted sources for evidence.
        agi_result: The output from agi_genius (for 'align' check).
        witness_request_id: ID for multi-signature verification.
        approval: Boolean approval for witness signature.
    """
    return await mcp_asi_act(
        action=action,
        text=text,
        session_id=session_id,
        proposal=proposal,
        query=query,
        stakeholders=stakeholders,
        sources=sources,
        agi_result=agi_result,
        witness_request_id=witness_request_id,
        approval=approval
    )

@mcp.tool(name="apex_judge")
async def arifos_trinity_apex_judge(
    action: str = "judge",
    query: str = "",
    session_id: str | None = None,
    response: str = "",
    verdict: str = "SEAL",
    data: str = "",
    agi_result: Dict[str, Any] | None = None,
    asi_result: Dict[str, Any] | None = None,
    agi_floors: List[Dict] | None = None,
    asi_floors: List[Dict] | None = None
) -> dict:
    """The Soul (Ψ) - Judgment & Authority Engine.

    The final decision maker. Synthesizes Truth (AGI) and Care (ASI) into a Verdict (F8).
    
    Actions:
    - `eureka`: Synthesize insights & resolve paradoxes. Requires `query` + `agi_result` + `asi_result`.
    - `judge`: Issue final constitutional verdict (SEAL/VOID). Requires `query` + `response`.
    - `proof`: Generate cryptographic seal (F1). Requires `data` + `verdict`.
    - `entropy`: Measure constitutional cooling (Agent Zero).
    - `full`: Complete pipeline (Eureka->Judge->Proof).

    Args:
        action: The judicial operation to perform.
        query: The original user query.
        session_id: The session ID.
        response: The candidate response to be judged.
        verdict: Proposed verdict (SEAL, SABAR, VOID).
        data: Raw data content for hashing/sealing.
        agi_result: Output from agi_genius (Truth signal).
        asi_result: Output from asi_act (Care signal).
        agi_floors: Specific floor metrics from AGI.
        asi_floors: Specific floor metrics from ASI.
    """
    return await mcp_apex_judge(
        action=action,
        query=query,
        session_id=session_id,
        response=response,
        verdict=verdict,
        data=data,
        agi_result=agi_result,
        asi_result=asi_result,
        agi_floors=agi_floors,
        asi_floors=asi_floors
    )

@mcp.tool(name="vault_999")
async def arifos_trinity_999_vault(
    action: str = "seal",
    session_id: str | None = None,
    verdict: str = "SEAL",
    target: str = "seal",
    query: str = "",
    data: Dict[str, Any] | None = None,
    init_result: Dict[str, Any] | None = None,
    agi_result: Dict[str, Any] | None = None,
    asi_result: Dict[str, Any] | None = None,
    apex_result: Dict[str, Any] | None = None
) -> dict:
    """Immutable Seal & Governance IO.

    The Final Gate. Commits the decision to the immutable ledger and closes the loop.
    
    Actions:
    - `seal`: Commit verdict + artifacts. Requires `verdict`.
    - `list`: View ledger history.
    - `read`: Retrieve specific entry. Requires `query` (as ID/path).
    - `write`: Low-level write (requires authority).
    - `propose`: Suggest canon update.

    Args:
        action: The vault operation to perform.
        session_id: The session ID to close.
        verdict: The final decision (SEAL/VOID) to log.
        target: The storage target (seal, ledger, canon).
        query: ID or path for read operations.
        data: Arbitrary data payload to store.
        init_result: Telemetry from 000_init.
        agi_result: Telemetry from agi_genius.
        asi_result: Telemetry from asi_act.
        apex_result: Telemetry from apex_judge.
    """
    # 1. Execute Seal
    result = await mcp_999_vault(
        action=action,
        session_id=session_id,
        verdict=verdict,
        target=target,
        query=query,
        data=data,
        init_result=init_result,
        agi_result=agi_result,
        asi_result=asi_result,
        apex_result=apex_result
    )

    # 2. Close Session Loop
    if result.get("status") == "SEAL" and session_id:
        _active_tokens.pop(session_id, None)
        try:
            close_session(session_id)
        except Exception as e:
            logger.warning(f"Failed to close session tracking: {e}")

    return result


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
            "metrics": "/metrics/json",
            "checkpoint": "/checkpoint",
            "openapi": "/openapi.json"
        }
    })

# --- METRICS ENDPOINT (For Dashboard - like Serena's) ---
@mcp.custom_route("/metrics/json", methods=["GET"])
async def get_metrics_json(request):
    """
    Get live metrics for dashboard polling.
    Returns tool usage, verdict distribution, sessions, and recent executions.
    """
    return JSONResponse(get_full_metrics())


# --- CHECKPOINT ENDPOINT (For ChatGPT Custom GPT Actions) ---
@mcp.custom_route("/checkpoint", methods=["POST"])
async def checkpoint_action(request):
    """
    Constitutional checkpoint for ChatGPT Actions.

    This is the core REST endpoint that wraps the Trinity pipeline:
    000_init → agi_genius → asi_act → apex_judge → 999_vault

    Input JSON:
    {
        "query": "The text or action to validate",
        "context": "Optional context about the situation",
        "stakeholders": ["user", "environment"]  // Optional
    }

    Returns:
    {
        "verdict": "SEAL" | "PARTIAL" | "VOID" | "888_HOLD",
        "summary": "Human-readable explanation",
        "floors": { ... floor scores ... },
        "session_id": "uuid",
        "ledger_hash": "merkle proof"
    }
    """
    import json

    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({
            "error": "Invalid JSON body",
            "verdict": "VOID",
            "summary": "Request must be valid JSON with 'query' field"
        }, status_code=400)

    query = body.get("query", "")
    context = body.get("context", "")
    stakeholders = body.get("stakeholders", ["user"])

    if not query:
        return JSONResponse({
            "error": "Missing 'query' field",
            "verdict": "VOID",
            "summary": "The 'query' field is required"
        }, status_code=400)

    try:
        # Step 1: Initialize session (000_init)
        init_result = await mcp_000_init(
            action="init",
            query=query,
            context={"source": "chatgpt_action", "context": context}
        )
        session_id = init_result.get("session_id", "")

        # Step 2: AGI Genius - Truth & Reasoning (agi_genius)
        agi_result = await mcp_agi_genius(
            action="full",
            query=query,
            session_id=session_id,
            context={"stakeholders": stakeholders}
        )

        # Step 3: ASI Act - Safety & Empathy (asi_act)
        asi_result = await mcp_asi_act(
            action="empathize",
            text=query,
            session_id=session_id,
            stakeholders=stakeholders
        )

        # Step 4: APEX Judge - Final Verdict (apex_judge)
        apex_result = await mcp_apex_judge(
            action="judge",
            query=query,
            session_id=session_id,
            response=query,
            agi_result=agi_result,
            asi_result=asi_result
        )

        # Step 5: Seal to Vault (999_vault)
        vault_result = await mcp_999_vault(
            action="seal",
            session_id=session_id,
            verdict=apex_result.get("verdict", "SEAL"),
            init_result=init_result,
            agi_result=agi_result,
            asi_result=asi_result,
            apex_result=apex_result
        )

        # Build response
        verdict = apex_result.get("verdict", "SEAL")
        floors = {
            "truth": agi_result.get("truth_score", 1.0),
            "clarity": agi_result.get("entropy_delta", 0),
            "humility": agi_result.get("humility", 0.04),
            "empathy": asi_result.get("empathy_score", 1.0),
            "peace": asi_result.get("peace_squared", 1.0),
            "amanah": asi_result.get("reversible", True),
        }

        # Generate human-readable summary
        if verdict == "SEAL":
            summary = "✓ Constitutional check passed. All floors within thresholds."
        elif verdict == "PARTIAL":
            summary = "⚠ Soft floor warning. Proceed with caution."
        elif verdict == "888_HOLD":
            summary = "⏸ High-stakes decision detected. Human confirmation required."
        else:
            summary = "✗ Hard floor violated. Action blocked."

        return JSONResponse({
            "verdict": verdict,
            "summary": summary,
            "floors": floors,
            "session_id": session_id,
            "ledger_hash": vault_result.get("merkle_root", ""),
            "atlas_lane": init_result.get("lane", "SOCIAL"),
            "version": VERSION
        })

    except Exception as e:
        logger.error(f"Checkpoint error: {e}")
        return JSONResponse({
            "error": str(e),
            "verdict": "VOID",
            "summary": f"Internal error during constitutional check: {str(e)}"
        }, status_code=500)


# --- OPENAPI SPEC ENDPOINT (For ChatGPT Custom GPT Import) ---
@mcp.custom_route("/openapi.json", methods=["GET"])
async def get_openapi_spec(request):
    """
    Serve OpenAPI 3.0 specification for ChatGPT Custom GPT Actions.
    Import this URL directly into ChatGPT's GPT Builder.
    """
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "arifOS Constitutional AI Governance",
            "description": "Constitutional AI governance filter. Validates AI outputs against 13 floors: Truth, Empathy, Amanah (reversibility), Clarity, and Humility. Returns SEAL (approved), PARTIAL (warning), VOID (blocked), or 888_HOLD (human required).",
            "version": VERSION,
            "contact": {
                "name": "Muhammad Arif bin Fazil",
                "url": "https://github.com/ariffazil/arifOS"
            }
        },
        "servers": [
            {
                "url": "https://arifos.arif-fazil.com",
                "description": "Production arifOS MCP Server"
            }
        ],
        "paths": {
            "/checkpoint": {
                "post": {
                    "operationId": "constitutionalCheckpoint",
                    "summary": "Run constitutional validation on text or action",
                    "description": "Validates input against 13 constitutional floors (TEACH framework: Truth≥0.99, Empathy≥0.95, Amanah=reversible, Clarity≥0, Humility=3-5%). Returns a verdict and floor scores.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["query"],
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "The text, statement, or proposed action to validate constitutionally"
                                        },
                                        "context": {
                                            "type": "string",
                                            "description": "Optional context about the situation or conversation"
                                        },
                                        "stakeholders": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "List of affected parties (e.g., ['user', 'environment', 'children'])",
                                            "default": ["user"]
                                        }
                                    }
                                },
                                "example": {
                                    "query": "Delete all user data without backup",
                                    "context": "User requested database cleanup",
                                    "stakeholders": ["user", "company"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Constitutional validation result",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "verdict": {
                                                "type": "string",
                                                "enum": ["SEAL", "PARTIAL", "VOID", "888_HOLD"],
                                                "description": "Constitutional verdict"
                                            },
                                            "summary": {
                                                "type": "string",
                                                "description": "Human-readable explanation of the verdict"
                                            },
                                            "floors": {
                                                "type": "object",
                                                "description": "Individual floor scores",
                                                "properties": {
                                                    "truth": {"type": "number"},
                                                    "empathy": {"type": "number"},
                                                    "amanah": {"type": "boolean"},
                                                    "clarity": {"type": "number"},
                                                    "humility": {"type": "number"},
                                                    "peace": {"type": "number"}
                                                }
                                            },
                                            "session_id": {"type": "string"},
                                            "ledger_hash": {"type": "string"},
                                            "atlas_lane": {
                                                "type": "string",
                                                "enum": ["CRISIS", "FACTUAL", "CARE", "SOCIAL"]
                                            },
                                            "version": {"type": "string"}
                                        }
                                    },
                                    "example": {
                                        "verdict": "VOID",
                                        "summary": "✗ Hard floor violated. Action blocked.",
                                        "floors": {
                                            "truth": 1.0,
                                            "empathy": 0.3,
                                            "amanah": False,
                                            "clarity": 0.5,
                                            "humility": 0.04,
                                            "peace": 0.2
                                        },
                                        "session_id": "abc123",
                                        "ledger_hash": "0x...",
                                        "atlas_lane": "FACTUAL",
                                        "version": "v52.5.1-SEAL"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid request",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {"type": "string"},
                                            "verdict": {"type": "string"},
                                            "summary": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/health": {
                "get": {
                    "operationId": "healthCheck",
                    "summary": "Check system health and version",
                    "description": "Returns current system status, version, and available endpoints",
                    "responses": {
                        "200": {
                            "description": "System health status",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "version": {"type": "string"},
                                            "motto": {"type": "string"},
                                            "endpoints": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/metrics/json": {
                "get": {
                    "operationId": "getMetrics",
                    "summary": "Get live governance metrics",
                    "description": "Returns tool usage statistics, verdict distribution, active sessions, and recent executions",
                    "responses": {
                        "200": {
                            "description": "Live metrics data",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "seal_rate": {"type": "number"},
                                            "total_sessions": {"type": "integer"},
                                            "tool_usage": {"type": "object"},
                                            "verdict_distribution": {"type": "object"},
                                            "recent_executions": {"type": "array"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return JSONResponse(spec)

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

# --- ROOT LANDING PAGE (README) ---
@mcp.custom_route("/", methods=["GET"])
async def get_landing(request):
    """Serve arifOS MCP README landing page."""
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>arifOS - Constitutional AI Governance</title>
        <meta name="description" content="A filter that stops AI from lying, harming, or being overconfident. 5 rules, 4 verdicts, works with any AI.">
        <style>
            /* arifOS Trinity Dark Theme */
            :root {{
                --bg: #050505; --panel: #111111; --card: #1a1a1a; --border: #333333;
                --text: #ffffff; --text-dim: #a1a1aa; --muted: #71717a;
                --agi-blue: #3b82f6; --asi-red: #ef4444; --apex-yellow: #eab308;
                --seal: #22c55e; --void: #ef4444; --hold: #a855f7;
            }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: var(--text); background: var(--bg); min-height: 100vh; }}
            .container {{ max-width: 900px; margin: 0 auto; padding: 2rem; }}
            header {{ text-align: center; padding: 3rem 0; border-bottom: 1px solid var(--border); margin-bottom: 2rem; }}
            h1 {{ font-size: 3rem; color: var(--text); margin-bottom: 0.5rem; }}
            h1 span {{ color: var(--agi-blue); }}
            .motto {{ font-style: italic; color: var(--apex-yellow); font-size: 1.2rem; margin-bottom: 1rem; }}
            .tagline {{ font-size: 1.1rem; color: var(--text-dim); max-width: 600px; margin: 0 auto; }}
            .version {{ display: inline-block; background: var(--panel); color: var(--agi-blue); padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.85rem; margin-top: 1rem; border: 1px solid var(--agi-blue); }}
            .hero {{ background: var(--panel); border: 1px solid var(--agi-blue); color: white; padding: 2rem; border-radius: 12px; margin: 2rem 0; text-align: center; }}
            .hero h2 {{ margin-bottom: 1rem; color: var(--text); }}
            .hero p {{ color: var(--text-dim); }}
            .hero code {{ background: var(--card); padding: 0.5rem 1rem; border-radius: 6px; font-size: 1.1rem; display: inline-block; color: var(--agi-blue); border: 1px solid var(--border); }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin: 2rem 0; }}
            .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s; }}
            .card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.3); border-color: var(--agi-blue); }}
            .card h3 {{ color: var(--text); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }}
            .card p {{ color: var(--text-dim); font-size: 0.95rem; }}
            .emoji {{ font-size: 1.5rem; }}
            .teach {{ background: var(--panel); border: 2px solid var(--asi-red); border-radius: 12px; padding: 1.5rem; margin: 2rem 0; }}
            .teach h2 {{ color: var(--asi-red); margin-bottom: 1rem; }}
            .teach-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.5rem; text-align: center; }}
            .teach-item {{ padding: 1rem 0.5rem; }}
            .teach-letter {{ font-size: 2rem; font-weight: bold; color: var(--agi-blue); }}
            .teach-word {{ font-size: 0.85rem; color: var(--text-dim); }}
            .teach-word small {{ color: var(--muted); }}
            .links {{ display: flex; flex-wrap: wrap; gap: 1rem; justify-content: center; margin: 2rem 0; }}
            .links a {{ display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; font-weight: 500; transition: all 0.2s; }}
            .links a.primary {{ background: var(--agi-blue); color: white; }}
            .links a.primary:hover {{ background: #2563eb; }}
            .links a.dashboard {{ background: var(--apex-yellow); color: #000; }}
            .links a.dashboard:hover {{ background: #ca8a04; }}
            .links a.secondary {{ background: var(--card); color: var(--text-dim); border: 1px solid var(--border); }}
            .links a.secondary:hover {{ border-color: var(--agi-blue); color: var(--agi-blue); }}
            footer {{ text-align: center; padding: 2rem 0; border-top: 1px solid var(--border); margin-top: 3rem; color: var(--muted); }}
            footer a {{ color: var(--apex-yellow); text-decoration: none; }}
            footer a:hover {{ color: var(--agi-blue); }}
            h2 {{ color: var(--text); }}
            .verdicts {{ display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: center; margin: 1rem 0; }}
            .verdict {{ padding: 0.4rem 0.8rem; border-radius: 6px; font-weight: bold; font-size: 0.9rem; }}
            .seal {{ background: rgba(34,197,94,0.15); color: var(--seal); border: 1px solid var(--seal); }}
            .sabar {{ background: rgba(234,179,8,0.15); color: var(--apex-yellow); border: 1px solid var(--apex-yellow); }}
            .void {{ background: rgba(239,68,68,0.15); color: var(--void); border: 1px solid var(--void); }}
            .hold {{ background: rgba(168,85,247,0.15); color: var(--hold); border: 1px solid var(--hold); }}
            @media (max-width: 600px) {{ .teach-grid {{ grid-template-columns: repeat(3, 1fr); }} h1 {{ font-size: 2rem; }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>arif<span>OS</span></h1>
                <p class="motto">"DITEMPA BUKAN DIBERI" — Forged, Not Given</p>
                <p class="tagline">A constitutional AI governance filter that stops AI from lying, harming, or being overconfident.</p>
                <span class="version">{VERSION}</span>
            </header>

            <div class="hero">
                <h2>Connect Your AI Client</h2>
                <p>Add this MCP endpoint to Claude Desktop, Cursor, or any MCP-compatible client:</p>
                <code>https://arifos.arif-fazil.com/sse</code>
            </div>

            <div class="teach">
                <h2>The TEACH Framework</h2>
                <p style="margin-bottom: 1rem; color: var(--muted);">Five constitutional principles that govern every AI response:</p>
                <div class="teach-grid">
                    <div class="teach-item"><div class="teach-letter">T</div><div class="teach-word">Truth<br><small>≥0.99</small></div></div>
                    <div class="teach-item"><div class="teach-letter">E</div><div class="teach-word">Empathy<br><small>κᵣ≥0.95</small></div></div>
                    <div class="teach-item"><div class="teach-letter">A</div><div class="teach-word">Amanah<br><small>Reversible</small></div></div>
                    <div class="teach-item"><div class="teach-letter">C</div><div class="teach-word">Clarity<br><small>ΔS≥0</small></div></div>
                    <div class="teach-item"><div class="teach-letter">H</div><div class="teach-word">Humility<br><small>3-5%</small></div></div>
                </div>
            </div>

            <h2 style="text-align: center; margin: 2rem 0 1rem;">Four Verdicts</h2>
            <div class="verdicts">
                <span class="verdict seal">✓ SEAL</span>
                <span class="verdict sabar">⏳ SABAR</span>
                <span class="verdict void">✗ VOID</span>
                <span class="verdict hold">⚠ 888_HOLD</span>
            </div>
            <p style="text-align: center; color: var(--muted); margin-bottom: 2rem;">Every AI response receives a constitutional verdict before reaching you.</p>

            <div class="grid">
                <div class="card">
                    <h3><span class="emoji">🔧</span> 5 Trinity Tools</h3>
                    <p>000_init (Gate) → agi_genius (Mind) → asi_act (Heart) → apex_judge (Soul) → vault_999 (Seal)</p>
                </div>
                <div class="card">
                    <h3><span class="emoji">🛣️</span> ATLAS-333 Routing</h3>
                    <p>Smart intent classification: CRISIS, FACTUAL, CARE, or SOCIAL lanes with adaptive thresholds.</p>
                </div>
                <div class="card">
                    <h3><span class="emoji">🔒</span> Immutable Ledger</h3>
                    <p>Every decision sealed with Merkle proofs. Hash-chained audit trail you can verify.</p>
                </div>
                <div class="card">
                    <h3><span class="emoji">⚖️</span> Tri-Witness Consensus</h3>
                    <p>Human · AI · Earth — three independent validators must agree on high-stakes decisions.</p>
                </div>
            </div>

            <div class="hero" style="border-color: var(--asi-red); margin-top: 2rem;">
                <h2 style="color: var(--asi-red);">🤖 ChatGPT Integration</h2>
                <p>Build a Custom GPT with arifOS governance. Import the OpenAPI spec:</p>
                <code>https://arifos.arif-fazil.com/openapi.json</code>
                <p style="margin-top: 1rem; font-size: 0.9rem; color: var(--muted);">Or call the REST endpoint directly: <code style="font-size: 0.85rem;">POST /checkpoint</code></p>
            </div>

            <div class="links">
                <a href="/docs" class="primary">📖 API Documentation</a>
                <a href="/dashboard" class="dashboard">📊 Live Dashboard</a>
                <a href="/openapi.json" class="secondary">📋 OpenAPI Spec</a>
                <a href="https://arifos.pages.dev/" class="secondary">📚 Full Docs</a>
            </div>

            <div class="links">
                <a href="https://github.com/ariffazil/arifOS" class="secondary">GitHub</a>
                <a href="https://pypi.org/project/arifos/" class="secondary">PyPI</a>
                <a href="/metrics/json" class="secondary">Metrics API</a>
                <a href="/health" class="secondary">💚 Health</a>
            </div>

            <footer>
                <p>Built by <a href="https://github.com/ariffazil">Muhammad Arif bin Fazil</a></p>
                <p style="margin-top: 0.5rem; font-size: 0.9rem;">Constitutional AI Governance Framework · {VERSION}</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)


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
    
    # Run initial recovery
    recovered = _recover_orphans()
    if recovered > 0:
        print(f"[BOOTSTRAP] Recovered {recovered} orphaned session(s)")
        
    print(f"   Version: {VERSION}")
    print(f"   Routes: /health, /sse, /messages, /dashboard")
    uvicorn.run(app, host="0.0.0.0", port=port)
