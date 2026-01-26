"""
arifos.mcp.sse (v53.0.0-SEAL)

The HTTP/SSE Adaptation layer for the AAA Monolith (AGI ∩ ASI ∩ APEX).
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
import asyncio
from starlette.responses import JSONResponse, HTMLResponse, FileResponse
from starlette.staticfiles import StaticFiles
from mcp.server.fastmcp import FastMCP
from arifos.mcp.constitutional_metrics import get_seal_rate, get_full_metrics, record_session_activity

# --- STATIC ASSETS ---
# Path to dashboard static files: arifos/core/integration/api/static
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "core", "integration", "api", "static")

# --- AAA TOOLS IMPORT ---
# We import from mcp_aaa.py which contains the canonical 5-tool implementation
from arifos.mcp.tools.mcp_aaa import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
)

# v53 Human-language translation layer (for verdict translation)
from arifos.mcp.tools.v53_human_layer import Verdict

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

# Redis integration for persistent sessions
from arifos.mcp import redis_client

logger = logging.getLogger(__name__)

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
VERSION = "v53.0.0-SEAL"
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
    """Start new session and verify user authority.

    Call this FIRST before any other tools. Initializes session, checks rate limits,
    and detects prompt injection.

    Actions:
    - `init` (default): Full session initialization. Requires `query`.
    - `gate`: Quick authority check only.
    - `reset`: Clear session state.
    - `validate`: Verify session integrity.

    Args:
        action: The operation to perform (init, gate, reset, validate).
        query: The user's request text (Required for `init`).
        session_id: Existing session ID (optional, auto-generated if missing).
        authority_token: Token for verified users (optional).
        context: Additional context (optional).
    """
    # NOTE: Orphan recovery now runs at startup, not per-request (performance fix)

    # Execute Init
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
            redis_client.save_token(new_session_id, token)
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
    """Analyze query logically, check facts, and verify reasoning confidence.

    The reasoning engine. Performs logical analysis, fact-checking, and ensures
    response clarity. Call after init_000 succeeds.

    Actions:
    - `sense`: Gather facts and classify user intent. Requires `query`.
    - `think`: Deep logical reasoning. Requires `query`.
    - `reflect`: Check if response reduces confusion. Requires `query` + `draft`.
    - `atlas`: Map relationships and concepts. Requires `query`.
    - `forge`: Generate solution. Requires `query`.
    - `evaluate`: Audit reasoning quality. Requires `query` + `draft` + `truth_score`.
    - `full`: Complete analysis pipeline (recommended).

    Args:
        action: The analysis operation to perform.
        query: The user's question or task.
        session_id: Session ID from init_000.
        thought: Internal reasoning (for 'think' or 'reflect').
        draft: Response draft to evaluate (for 'evaluate' or 'reflect').
        truth_score: Estimated factual accuracy (0.0-1.0).
        context: Previous context (optional).
        axioms: Core assumptions for mapping (optional).
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
    """Check response for harm, bias, and fairness to all stakeholders.

    The safety engine. Evaluates potential harm, detects bias, and ensures
    the response serves vulnerable stakeholders fairly. Call after agi_genius.

    Actions:
    - `evidence`: Verify claims against sources. Requires `query` + `sources`.
    - `empathize`: Assess impact on stakeholders. Requires `text` + `stakeholders`.
    - `align`: Check safety compliance. Requires `text` + `agi_result`.
    - `act`: Execute verified action. Requires `proposal` + `witness_request_id`.
    - `witness`: Collect approval signatures. Requires `witness_request_id` + `approval`.
    - `evaluate`: Full safety audit. Requires `text`.
    - `full`: Complete safety pipeline (recommended).

    Args:
        action: The safety operation to perform.
        text: Content to analyze for harm/bias.
        session_id: Session ID.
        proposal: Proposed action description (for 'act').
        query: Query for evidence gathering.
        stakeholders: Affected parties (e.g. ["user", "environment", "vulnerable_groups"]).
        sources: Trusted sources for verification.
        agi_result: Output from agi_genius (for 'align').
        witness_request_id: ID for multi-signature verification.
        approval: Approval for witness signature.
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
    """Synthesize logic and safety checks into final verdict (Approve/Reject).

    The judgment engine. Combines reasoning (agi_genius) and safety (asi_act)
    results to render a final decision. Call after both agi_genius and asi_act.

    Actions:
    - `eureka`: Synthesize insights and resolve conflicts. Requires `query` + `agi_result` + `asi_result`.
    - `judge`: Issue final verdict (APPROVE/REJECT). Requires `query` + `response`.
    - `proof`: Generate cryptographic seal for audit. Requires `data` + `verdict`.
    - `entropy`: Measure decision confidence.
    - `full`: Complete judgment pipeline (recommended).

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
    """Record decision immutably in ledger for audit trail.

    The archive. Commits the final verdict to an immutable ledger, creating
    a cryptographic proof. Call LAST to finalize the session.

    Actions:
    - `seal`: Commit verdict to ledger. Requires `verdict`.
    - `list`: View ledger history.
    - `read`: Retrieve specific entry. Requires `query` (as entry ID).
    - `write`: Low-level write (requires authority).
    - `propose`: Suggest policy update.

    Args:
        action: The archive operation to perform.
        session_id: Session ID to finalize.
        verdict: Final decision (APPROVE/REJECT) to record.
        target: Storage target (seal, ledger, canon).
        query: Entry ID for read operations.
        data: Data payload to store.
        init_result: Results from init_000.
        agi_result: Results from agi_genius.
        asi_result: Results from asi_act.
        apex_result: Results from apex_judge.
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
        redis_client.delete_token(session_id)
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
        "redis": redis_client.health(),
        "active_sessions": redis_client.count_tokens(),
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

        # Step 2 & 3: Run AGI and ASI in PARALLEL (they're independent)
        agi_task = mcp_agi_genius(
            action="full",
            query=query,
            session_id=session_id,
            context={"stakeholders": stakeholders}
        )
        asi_task = mcp_asi_act(
            action="empathize",
            text=query,
            session_id=session_id,
            stakeholders=stakeholders
        )
        agi_result, asi_result = await asyncio.gather(agi_task, asi_task)

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

        # Build response - translate internal verdict to human-readable
        internal_verdict = apex_result.get("verdict", "SEAL")
        human_verdict = Verdict.to_human(internal_verdict)

        floors = {
            "truth": agi_result.get("truth_score", 1.0),
            "clarity": agi_result.get("entropy_delta", 0),
            "humility": agi_result.get("humility", 0.04),
            "empathy": asi_result.get("empathy_score", 1.0),
            "peace": asi_result.get("peace_squared", 1.0),
            "amanah": asi_result.get("reversible", True),
        }

        # Generate human-readable summary using human verdicts
        if human_verdict == "APPROVE":
            summary = "✓ Constitutional check passed. All floors within thresholds."
        elif human_verdict == "CONDITIONAL":
            summary = "⚠ Soft floor warning. Proceed with caution."
        elif human_verdict == "ESCALATE":
            summary = "⏸ High-stakes decision detected. Human confirmation required."
        else:  # REJECT
            summary = "✗ Hard floor violated. Action blocked."

        return JSONResponse({
            "verdict": human_verdict,
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
        "openapi": "3.1.0",
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
                                                "enum": ["APPROVE", "CONDITIONAL", "REJECT", "ESCALATE"],
                                                "description": "Constitutional verdict (human-readable)"
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
                                        "verdict": "REJECT",
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
                                        "version": "v53.0.0-SEAL"
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
    """Serve Live Sovereign Dashboard with real-time metrics polling."""
    m = get_full_metrics()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arifOS Live Dashboard</title>
    <style>
        :root {{ --bg: #0a0a0a; --panel: #111; --card: #1a1a1a; --border: #333; --text: #fff; --dim: #a1a1aa; --muted: #71717a; --agi: #3b82f6; --asi: #ef4444; --apex: #eab308; --seal: #22c55e; --void: #ef4444; --hold: #a855f7; --partial: #f59e0b; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', monospace; background: var(--bg); color: var(--text); min-height: 100vh; }}
        .header {{ background: var(--panel); border-bottom: 1px solid var(--border); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ font-size: 1.5rem; }} .header h1 span {{ color: var(--agi); }}
        .status {{ display: flex; align-items: center; gap: 1rem; }}
        .status-dot {{ width: 12px; height: 12px; border-radius: 50%; background: var(--seal); animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
        .uptime {{ color: var(--dim); font-size: 0.85rem; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 1.5rem; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }}
        .metric-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; }}
        .metric-card.highlight {{ border-color: var(--agi); }}
        .metric-label {{ color: var(--dim); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }}
        .metric-value {{ font-size: 2rem; font-weight: bold; color: var(--text); }}
        .metric-value.seal {{ color: var(--seal); }}
        .metric-subtext {{ color: var(--muted); font-size: 0.75rem; margin-top: 0.25rem; }}
        .main-grid {{ display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; }}
        .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; }}
        .card h3 {{ color: var(--dim); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }}
        .verdict-bar {{ display: flex; height: 24px; border-radius: 6px; overflow: hidden; margin-bottom: 1rem; }}
        .verdict-segment {{ transition: width 0.5s ease; }}
        .verdict-segment.seal {{ background: var(--seal); }} .verdict-segment.partial {{ background: var(--partial); }} .verdict-segment.void {{ background: var(--void); }} .verdict-segment.hold {{ background: var(--hold); }}
        .verdict-legend {{ display: flex; gap: 1.5rem; flex-wrap: wrap; }}
        .legend-item {{ display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; }}
        .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
        .floor-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; }}
        .floor {{ padding: 0.75rem; border-radius: 8px; text-align: center; font-size: 0.75rem; }}
        .floor.ok {{ background: rgba(34,197,94,0.15); color: var(--seal); border: 1px solid rgba(34,197,94,0.3); }}
        .floor.fail {{ background: rgba(239,68,68,0.15); color: var(--void); border: 1px solid rgba(239,68,68,0.3); }}
        .floor-name {{ font-weight: bold; }}
        .tool-row {{ display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border); }}
        .tool-row:last-child {{ border-bottom: none; }}
        .tool-name {{ display: flex; align-items: center; gap: 0.5rem; }}
        .tool-badge {{ padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.7rem; font-weight: bold; }}
        .tool-badge.gate {{ background: rgba(59,130,246,0.15); color: var(--agi); }}
        .tool-badge.mind {{ background: rgba(59,130,246,0.15); color: var(--agi); }}
        .tool-badge.heart {{ background: rgba(239,68,68,0.15); color: var(--asi); }}
        .tool-badge.soul {{ background: rgba(234,179,8,0.15); color: var(--apex); }}
        .tool-badge.seal {{ background: rgba(34,197,94,0.15); color: var(--seal); }}
        .tool-count {{ font-weight: bold; font-size: 1.1rem; }}
        .activity-list {{ max-height: 300px; overflow-y: auto; }}
        .activity-item {{ display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid var(--border); font-size: 0.85rem; }}
        .activity-item:last-child {{ border-bottom: none; }}
        .activity-tool {{ color: var(--dim); }}
        .activity-verdict {{ padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem; font-weight: bold; }}
        .activity-verdict.SEAL {{ background: rgba(34,197,94,0.15); color: var(--seal); }}
        .activity-verdict.VOID {{ background: rgba(239,68,68,0.15); color: var(--void); }}
        .activity-verdict.PARTIAL {{ background: rgba(245,158,11,0.15); color: var(--partial); }}
        .activity-time {{ color: var(--muted); font-size: 0.75rem; }}
        .alerts {{ margin-bottom: 1.5rem; }}
        .alert {{ background: rgba(239,68,68,0.1); border: 1px solid var(--void); border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 1rem; }}
        .alert.warning {{ background: rgba(245,158,11,0.1); border-color: var(--partial); }}
        .alert.info {{ background: rgba(59,130,246,0.1); border-color: var(--agi); }}
        .alert-icon {{ font-size: 1.5rem; }}
        .alert-content h4 {{ margin-bottom: 0.25rem; }}
        .alert-content p {{ color: var(--dim); font-size: 0.85rem; }}
        .trinity-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem; }}
        .trinity-gauge {{ text-align: center; }}
        .trinity-label {{ font-size: 0.75rem; color: var(--dim); margin-bottom: 0.5rem; }}
        .trinity-value {{ font-size: 1.5rem; font-weight: bold; }}
        .trinity-value.agi {{ color: var(--agi); }} .trinity-value.asi {{ color: var(--asi); }} .trinity-value.apex {{ color: var(--apex); }}
        .latency-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; text-align: center; }}
        .latency-item {{ padding: 0.75rem; background: var(--panel); border-radius: 6px; }}
        .latency-label {{ font-size: 0.7rem; color: var(--muted); }}
        .latency-value {{ font-size: 1.25rem; font-weight: bold; margin-top: 0.25rem; }}
        .footer {{ text-align: center; padding: 1.5rem; color: var(--muted); font-size: 0.85rem; }}
        .footer a {{ color: var(--apex); text-decoration: none; }}
        @media (max-width: 1024px) {{ .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }} .main-grid {{ grid-template-columns: 1fr; }} }}
        @media (max-width: 600px) {{ .metrics-grid {{ grid-template-columns: 1fr; }} .floor-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>arif<span>OS</span> Live Dashboard</h1>
        <div class="status">
            <div class="status-dot" id="statusDot"></div>
            <span id="statusText">HEALTHY</span>
            <span class="uptime">Uptime: <span id="uptime">{m.get('uptime_hours', 0):.1f}h</span></span>
        </div>
    </div>
    <div class="container">
        <div class="alerts" id="alerts"></div>
        <div class="metrics-grid">
            <div class="metric-card highlight">
                <div class="metric-label">SEAL Rate (1h)</div>
                <div class="metric-value seal" id="sealRate">{m.get('seal_rate', 0)*100:.1f}%</div>
                <div class="metric-subtext">Constitutional approval rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Tool Calls</div>
                <div class="metric-value" id="totalSessions">{m.get('total_tool_calls', 0)}</div>
                <div class="metric-subtext">Invocations processed</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Active Sessions</div>
                <div class="metric-value" id="activeSessions">{m.get('active_sessions', 0)}</div>
                <div class="metric-subtext">Currently processing</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Latency</div>
                <div class="metric-value" id="avgLatency">{m.get('latency_ms', {{}}).get('avg', 0):.0f}ms</div>
                <div class="metric-subtext">Response time</div>
            </div>
        </div>
        <div class="main-grid">
            <div>
                <div class="card" style="margin-bottom: 1.5rem;">
                    <h3>⚖️ Verdict Distribution</h3>
                    <div class="verdict-bar" id="verdictBar"><div class="verdict-segment seal" style="width:100%"></div></div>
                    <div class="verdict-legend">
                        <div class="legend-item"><div class="legend-dot" style="background:var(--seal)"></div> SEAL <span id="sealCount">0</span></div>
                        <div class="legend-item"><div class="legend-dot" style="background:var(--partial)"></div> PARTIAL <span id="partialCount">0</span></div>
                        <div class="legend-item"><div class="legend-dot" style="background:var(--void)"></div> VOID <span id="voidCount">0</span></div>
                        <div class="legend-item"><div class="legend-dot" style="background:var(--hold)"></div> 888_HOLD <span id="holdCount">0</span></div>
                    </div>
                </div>
                <div class="card" style="margin-bottom: 1.5rem;">
                    <h3>🏛️ Constitutional Floor Health</h3>
                    <div class="floor-grid" id="floorGrid"></div>
                </div>
                <div class="card">
                    <h3>⚡ Response Latency</h3>
                    <div class="latency-grid">
                        <div class="latency-item"><div class="latency-label">P50</div><div class="latency-value" id="p50">0ms</div></div>
                        <div class="latency-item"><div class="latency-label">P95</div><div class="latency-value" id="p95">0ms</div></div>
                        <div class="latency-item"><div class="latency-label">P99</div><div class="latency-value" id="p99">0ms</div></div>
                        <div class="latency-item"><div class="latency-label">AVG</div><div class="latency-value" id="avg">0ms</div></div>
                    </div>
                </div>
            </div>
            <div>
                <div class="card" style="margin-bottom: 1.5rem;">
                    <h3>🔧 Tool Usage</h3>
                    <div id="toolUsage"></div>
                </div>
                <div class="card" style="margin-bottom: 1.5rem;">
                    <h3>🔺 Trinity Scores</h3>
                    <div class="trinity-grid">
                        <div class="trinity-gauge"><div class="trinity-label">AGI Mind (τ)</div><div class="trinity-value agi" id="agiScore">0.99</div></div>
                        <div class="trinity-gauge"><div class="trinity-label">ASI Heart (κᵣ)</div><div class="trinity-value asi" id="asiScore">0.96</div></div>
                        <div class="trinity-gauge"><div class="trinity-label">APEX Soul (Ψ)</div><div class="trinity-value apex" id="apexScore">0.85</div></div>
                    </div>
                </div>
                <div class="card">
                    <h3>📜 Recent Activity</h3>
                    <div class="activity-list" id="activityList"><div class="activity-item"><span class="activity-tool">Waiting for data...</span></div></div>
                </div>
            </div>
        </div>
    </div>
    <div class="footer"><a href="/">← Back to arifOS</a> · Last updated: <span id="lastUpdate">-</span> · Auto-refresh: 5s</div>
    <script>
        async function updateDashboard() {{
            try {{
                const res = await fetch('/metrics/json');
                const m = await res.json();
                document.getElementById('uptime').textContent = m.uptime_hours.toFixed(1) + 'h';
                document.getElementById('statusText').textContent = m.status === 'active' ? 'HEALTHY' : 'DEGRADED';
                document.getElementById('statusDot').style.background = m.status === 'active' ? 'var(--seal)' : 'var(--void)';
                document.getElementById('sealRate').textContent = (m.seal_rate * 100).toFixed(1) + '%';
                document.getElementById('totalSessions').textContent = m.total_tool_calls || 0;
                document.getElementById('activeSessions').textContent = m.active_sessions || 0;
                document.getElementById('avgLatency').textContent = (m.latency_ms?.avg || 0).toFixed(0) + 'ms';
                const vd = m.verdict_distribution || {{}};
                const total = Object.values(vd).reduce((a, b) => a + b, 0) || 1;
                document.getElementById('verdictBar').innerHTML = `<div class="verdict-segment seal" style="width:${{((vd.SEAL||0)/total*100).toFixed(1)}}%"></div><div class="verdict-segment partial" style="width:${{((vd.PARTIAL||0)/total*100).toFixed(1)}}%"></div><div class="verdict-segment void" style="width:${{((vd.VOID||0)/total*100).toFixed(1)}}%"></div><div class="verdict-segment hold" style="width:${{(((vd['888_HOLD']||0)+(vd.SABAR||0))/total*100).toFixed(1)}}%"></div>`;
                document.getElementById('sealCount').textContent = vd.SEAL || 0;
                document.getElementById('partialCount').textContent = vd.PARTIAL || 0;
                document.getElementById('voidCount').textContent = vd.VOID || 0;
                document.getElementById('holdCount').textContent = (vd['888_HOLD'] || 0) + (vd.SABAR || 0);
                document.getElementById('p50').textContent = (m.latency_ms?.p50 || 0).toFixed(0) + 'ms';
                document.getElementById('p95').textContent = (m.latency_ms?.p95 || 0).toFixed(0) + 'ms';
                document.getElementById('p99').textContent = (m.latency_ms?.p99 || 0).toFixed(0) + 'ms';
                document.getElementById('avg').textContent = (m.latency_ms?.avg || 0).toFixed(0) + 'ms';
                const tu = m.tool_usage || {{}};
                const toolMap = {{'init_000': ['GATE', 'gate'], 'agi_genius': ['MIND', 'mind'], 'asi_act': ['HEART', 'heart'], 'apex_judge': ['SOUL', 'soul'], 'vault_999': ['SEAL', 'seal']}};
                let toolHtml = '';
                for (const [tool, [label, cls]] of Object.entries(toolMap)) toolHtml += `<div class="tool-row"><div class="tool-name"><span class="tool-badge ${{cls}}">${{label}}</span> ${{tool}}</div><div class="tool-count">${{tu[tool] || 0}}</div></div>`;
                document.getElementById('toolUsage').innerHTML = toolHtml;
                document.getElementById('agiScore').textContent = (m.trinity?.agi_mind?.truth || 0.99).toFixed(2);
                document.getElementById('asiScore').textContent = (m.trinity?.asi_heart?.empathy || 0.96).toFixed(2);
                document.getElementById('apexScore').textContent = (m.trinity?.apex_soul?.genius || 0.85).toFixed(2);
                const fh = m.floor_health || {{}};
                const floors = [['F1','Amanah','F1_amanah'],['F2','Truth','F2_truth'],['F3','Witness','F3_tri_witness'],['F4','Clarity','F4_clarity'],['F5','Peace','F5_peace'],['F6','Empathy','F6_empathy'],['F7','Humility','F7_humility'],['F8','Genius','F8_genius'],['F9','Dark','F9_dark'],['F10','Ontology','F10_ontology'],['F11','Auth','F11_auth'],['F12','Injection','F12_injection']];
                let floorHtml = '';
                for (const [n, name, key] of floors) floorHtml += `<div class="floor ${{fh[key] !== false ? 'ok' : 'fail'}}"><div class="floor-name">${{n}}</div>${{name}}</div>`;
                document.getElementById('floorGrid').innerHTML = floorHtml;
                const recent = m.recent_executions || [];
                if (recent.length > 0) {{
                    let actHtml = '';
                    for (const r of recent.slice(0, 10)) {{
                        const time = r.timestamp ? new Date(r.timestamp).toLocaleTimeString() : '-';
                        actHtml += `<div class="activity-item"><span class="activity-tool">${{r.tool || 'unknown'}}</span><span class="activity-verdict ${{r.verdict || 'SEAL'}}">${{r.verdict || 'SEAL'}}</span><span class="activity-time">${{time}}</span></div>`;
                    }}
                    document.getElementById('activityList').innerHTML = actHtml;
                }}
                let alertHtml = '';
                if (m.void_rate > 0.1) alertHtml += `<div class="alert"><span class="alert-icon">🚨</span><div class="alert-content"><h4>High VOID Rate</h4><p>VOID rate is ${{(m.void_rate * 100).toFixed(1)}}%. Review recent rejections.</p></div></div>`;
                if (m.latency_ms?.p99 > 5000) alertHtml += `<div class="alert warning"><span class="alert-icon">⚠️</span><div class="alert-content"><h4>High Latency</h4><p>P99 latency is ${{m.latency_ms.p99.toFixed(0)}}ms.</p></div></div>`;
                if ((vd['888_HOLD'] || 0) > 0) alertHtml += `<div class="alert info"><span class="alert-icon">⏸️</span><div class="alert-content"><h4>Pending Human Review</h4><p>${{vd['888_HOLD']}} decisions awaiting confirmation.</p></div></div>`;
                document.getElementById('alerts').innerHTML = alertHtml;
                document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            }} catch (e) {{
                document.getElementById('statusText').textContent = 'ERROR';
                document.getElementById('statusDot').style.background = 'var(--void)';
            }}
        }}
        updateDashboard();
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>"""
    return HTMLResponse(html)

# --- ROOT LANDING PAGE (README) ---
@mcp.custom_route("/", methods=["GET"])
async def get_landing(request):
    """Serve arifOS MCP v53 landing page with client-specific quick starts."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arifOS - Constitutional AI Governance</title>
    <meta name="description" content="A filter that stops AI from lying, harming, or being overconfident. 5 rules, 4 verdicts, works with any AI.">
    <style>
        :root {{ --bg: #050505; --panel: #111; --card: #1a1a1a; --border: #333; --text: #fff; --dim: #a1a1aa; --muted: #71717a; --agi: #3b82f6; --asi: #ef4444; --apex: #eab308; --seal: #22c55e; --void: #ef4444; --hold: #a855f7; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: var(--text); background: var(--bg); min-height: 100vh; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 2rem; }}
        header {{ text-align: center; padding: 2.5rem 0; border-bottom: 1px solid var(--border); margin-bottom: 2rem; }}
        h1 {{ font-size: 3rem; margin-bottom: 0.5rem; }} h1 span {{ color: var(--agi); }}
        .motto {{ font-style: italic; color: var(--apex); font-size: 1.1rem; margin-bottom: 0.75rem; }}
        .tagline {{ color: var(--dim); max-width: 600px; margin: 0 auto; }}
        .version {{ display: inline-block; background: var(--panel); color: var(--agi); padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; margin-top: 1rem; border: 1px solid var(--agi); }}
        h2 {{ color: var(--text); margin: 2rem 0 1rem; text-align: center; }}
        .quickstart {{ background: linear-gradient(135deg, var(--panel) 0%, var(--card) 100%); border: 2px solid var(--agi); border-radius: 16px; padding: 2rem; margin: 2rem 0; }}
        .quickstart h2 {{ margin-top: 0; color: var(--agi); }}
        .quickstart-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1.5rem; }}
        .qs-card {{ background: var(--bg); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; text-align: center; transition: all 0.2s; cursor: pointer; text-decoration: none; color: var(--text); }}
        .qs-card:hover {{ border-color: var(--agi); transform: translateY(-2px); }}
        .qs-icon {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        .qs-title {{ font-weight: bold; margin-bottom: 0.25rem; }}
        .qs-desc {{ font-size: 0.8rem; color: var(--dim); margin-bottom: 0.75rem; }}
        .qs-code {{ background: var(--card); padding: 0.4rem 0.6rem; border-radius: 4px; font-size: 0.75rem; color: var(--agi); font-family: monospace; word-break: break-all; }}
        .endpoints {{ background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; margin: 2rem 0; }}
        .endpoints h3 {{ color: var(--dim); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem; }}
        .endpoint-table {{ width: 100%; border-collapse: collapse; }}
        .endpoint-table th, .endpoint-table td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }}
        .endpoint-table th {{ color: var(--muted); font-size: 0.75rem; text-transform: uppercase; }}
        .endpoint-table td:first-child {{ font-weight: bold; }}
        .endpoint-table code {{ background: var(--card); padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.85rem; }}
        .method {{ display: inline-block; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-right: 0.5rem; }}
        .method.get {{ background: rgba(34,197,94,0.15); color: var(--seal); }}
        .method.post {{ background: rgba(59,130,246,0.15); color: var(--agi); }}
        .teach {{ background: var(--panel); border: 2px solid var(--asi); border-radius: 12px; padding: 1.5rem; margin: 2rem 0; }}
        .teach h2 {{ color: var(--asi); margin: 0 0 1rem 0; text-align: left; }}
        .teach-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.5rem; text-align: center; }}
        .teach-item {{ padding: 0.75rem 0.25rem; }}
        .teach-letter {{ font-size: 1.75rem; font-weight: bold; color: var(--agi); }}
        .teach-word {{ font-size: 0.8rem; color: var(--dim); }}
        .teach-word small {{ color: var(--muted); }}
        .verdicts {{ display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: center; margin: 1rem 0; }}
        .verdict {{ padding: 0.4rem 0.8rem; border-radius: 6px; font-weight: bold; font-size: 0.85rem; }}
        .verdict.seal {{ background: rgba(34,197,94,0.15); color: var(--seal); border: 1px solid var(--seal); }}
        .verdict.partial {{ background: rgba(234,179,8,0.15); color: var(--apex); border: 1px solid var(--apex); }}
        .verdict.void {{ background: rgba(239,68,68,0.15); color: var(--void); border: 1px solid var(--void); }}
        .verdict.hold {{ background: rgba(168,85,247,0.15); color: var(--hold); border: 1px solid var(--hold); }}
        .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin: 2rem 0; }}
        .card {{ background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; transition: all 0.2s; }}
        .card:hover {{ border-color: var(--agi); }}
        .card h3 {{ color: var(--text); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; font-size: 1rem; }}
        .card p {{ color: var(--dim); font-size: 0.9rem; }}
        .links {{ display: flex; flex-wrap: wrap; gap: 0.75rem; justify-content: center; margin: 2rem 0; }}
        .links a {{ display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.6rem 1.25rem; border-radius: 8px; text-decoration: none; font-weight: 500; font-size: 0.9rem; transition: all 0.2s; }}
        .links a.primary {{ background: var(--agi); color: white; }}
        .links a.primary:hover {{ background: #2563eb; }}
        .links a.dashboard {{ background: var(--apex); color: #000; }}
        .links a.dashboard:hover {{ background: #ca8a04; }}
        .links a.secondary {{ background: var(--card); color: var(--dim); border: 1px solid var(--border); }}
        .links a.secondary:hover {{ border-color: var(--agi); color: var(--agi); }}
        footer {{ text-align: center; padding: 2rem 0; border-top: 1px solid var(--border); margin-top: 2rem; color: var(--muted); font-size: 0.85rem; }}
        footer a {{ color: var(--apex); text-decoration: none; }}
        @media (max-width: 768px) {{ .quickstart-grid {{ grid-template-columns: 1fr; }} .teach-grid {{ grid-template-columns: repeat(3, 1fr); }} .grid {{ grid-template-columns: 1fr; }} h1 {{ font-size: 2rem; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>arif<span>OS</span></h1>
            <p class="motto">"DITEMPA BUKAN DIBERI" — Forged, Not Given</p>
            <p class="tagline">Constitutional AI governance that stops AI from lying, harming, or being overconfident.</p>
            <span class="version">{VERSION}</span>
        </header>

        <div class="quickstart">
            <h2>🚀 Quick Start — Choose Your Client</h2>
            <div class="quickstart-grid">
                <a href="/docs#mcp" class="qs-card">
                    <div class="qs-icon">🖥️</div>
                    <div class="qs-title">MCP Clients</div>
                    <div class="qs-desc">Claude Desktop, Cursor, Kimi</div>
                    <div class="qs-code">/sse</div>
                </a>
                <a href="/openapi.json" class="qs-card">
                    <div class="qs-icon">🤖</div>
                    <div class="qs-title">ChatGPT / GPT Builder</div>
                    <div class="qs-desc">Import OpenAPI spec</div>
                    <div class="qs-code">/openapi.json</div>
                </a>
                <a href="/docs#rest" class="qs-card">
                    <div class="qs-icon">⚡</div>
                    <div class="qs-title">REST / Postman / curl</div>
                    <div class="qs-desc">Direct HTTP calls</div>
                    <div class="qs-code">POST /checkpoint</div>
                </a>
            </div>
        </div>

        <div class="endpoints">
            <h3>📡 Endpoint Reference</h3>
            <table class="endpoint-table">
                <tr><th>Endpoint</th><th>URL</th><th>Purpose</th></tr>
                <tr><td><span class="method get">GET</span>/sse</td><td><code>https://arifos.arif-fazil.com/sse</code></td><td>MCP streaming (Claude, Cursor)</td></tr>
                <tr><td><span class="method post">POST</span>/checkpoint</td><td><code>https://arifos.arif-fazil.com/checkpoint</code></td><td>Full constitutional validation</td></tr>
                <tr><td><span class="method get">GET</span>/openapi.json</td><td><code>https://arifos.arif-fazil.com/openapi.json</code></td><td>ChatGPT GPT Builder import</td></tr>
                <tr><td><span class="method get">GET</span>/dashboard</td><td><code>https://arifos.arif-fazil.com/dashboard</code></td><td>Live monitoring</td></tr>
                <tr><td><span class="method get">GET</span>/metrics/json</td><td><code>https://arifos.arif-fazil.com/metrics/json</code></td><td>Machine-readable metrics</td></tr>
                <tr><td><span class="method get">GET</span>/health</td><td><code>https://arifos.arif-fazil.com/health</code></td><td>System status</td></tr>
                <tr><td><span class="method get">GET</span>/docs</td><td><code>https://arifos.arif-fazil.com/docs</code></td><td>API documentation</td></tr>
            </table>
        </div>

        <div class="teach">
            <h2>The TEACH Framework</h2>
            <div class="teach-grid">
                <div class="teach-item"><div class="teach-letter">T</div><div class="teach-word">Truth<br><small>≥0.99</small></div></div>
                <div class="teach-item"><div class="teach-letter">E</div><div class="teach-word">Empathy<br><small>κᵣ≥0.95</small></div></div>
                <div class="teach-item"><div class="teach-letter">A</div><div class="teach-word">Amanah<br><small>Reversible</small></div></div>
                <div class="teach-item"><div class="teach-letter">C</div><div class="teach-word">Clarity<br><small>ΔS≥0</small></div></div>
                <div class="teach-item"><div class="teach-letter">H</div><div class="teach-word">Humility<br><small>3-5%</small></div></div>
            </div>
        </div>

        <h2>Four Verdicts</h2>
        <div class="verdicts">
            <span class="verdict seal">✓ APPROVE</span>
            <span class="verdict partial">⚠ CONDITIONAL</span>
            <span class="verdict void">✗ REJECT</span>
            <span class="verdict hold">⏸ ESCALATE</span>
        </div>
        <p style="text-align: center; color: var(--muted); margin-bottom: 2rem; font-size: 0.9rem;">Every AI response receives a constitutional verdict before reaching you.</p>

        <div class="grid">
            <div class="card">
                <h3>🔧 5 Trinity Tools</h3>
                <p>init_000 (Gate) → agi_genius (Mind) → asi_act (Heart) → apex_judge (Soul) → vault_999 (Seal)</p>
            </div>
            <div class="card">
                <h3>🛣️ ATLAS-333 Routing</h3>
                <p>Smart intent classification: CRISIS, FACTUAL, CARE, or SOCIAL lanes with adaptive thresholds.</p>
            </div>
            <div class="card">
                <h3>🔒 Immutable Ledger</h3>
                <p>Every decision sealed with Merkle proofs. Hash-chained audit trail you can verify.</p>
            </div>
            <div class="card">
                <h3>⚖️ Tri-Witness Consensus</h3>
                <p>Human · AI · Earth — three validators must agree on high-stakes decisions.</p>
            </div>
        </div>

        <div class="links">
            <a href="/docs" class="primary">📖 API Docs</a>
            <a href="/dashboard" class="dashboard">📊 Live Dashboard</a>
            <a href="/openapi.json" class="secondary">📋 OpenAPI</a>
            <a href="https://arifos.pages.dev/" class="secondary">📚 Full Docs</a>
        </div>
        <div class="links">
            <a href="https://github.com/ariffazil/arifOS" class="secondary">GitHub</a>
            <a href="https://pypi.org/project/arifos/" class="secondary">PyPI</a>
            <a href="/metrics/json" class="secondary">Metrics</a>
            <a href="/health" class="secondary">💚 Health</a>
        </div>

        <footer>
            <p>Built by <a href="https://github.com/ariffazil">Muhammad Arif bin Fazil</a></p>
            <p style="margin-top: 0.5rem;">Constitutional AI Governance · {VERSION}</p>
        </footer>
    </div>
</body>
</html>"""
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

        <h2>Human Language Tools (v53)</h2>
        <div class="tool">
            <h3>authorize <span class="badge">Gate</span></h3>
            <p><strong>Verification Engine.</strong> Verifies user identity, token, & injection risks.</p>
            <p><code>Call FIRST. Wraps init_000.</code></p>
        </div>
        <div class="tool">
            <h3>reason <span class="badge">Mind</span></h3>
            <p><strong>Logic Engine.</strong> Logical analysis & chain-of-thought.</p>
            <p><code>Wraps agi_genius.</code></p>
        </div>
        <div class="tool">
            <h3>evaluate <span class="badge">Heart</span></h3>
            <p><strong>Safety Engine.</strong> Checks harm, bias, fairness.</p>
            <p><code>Wraps asi_act.</code></p>
        </div>
        <div class="tool">
            <h3>decide <span class="badge">Soul</span></h3>
            <p><strong>Verdict Engine.</strong> Synthesizes final constitutional verdict.</p>
            <p><code>Wraps apex_judge.</code></p>
        </div>
        <div class="tool">
            <h3>seal <span class="badge">Seal</span></h3>
            <p><strong>Ledger Engine.</strong> Immutable recording.</p>
            <p><code>Wraps 999_vault.</code></p>
        </div>

        <h2>ATLAS-333 Lanes (v53.0.0)</h2>
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


def main():
    """
    Main entry point for aaa-mcp-sse command.

    Used by:
      - pyproject.toml: aaa-mcp-sse = "arifos.mcp.sse:main"
      - railway.toml: startCommand = "aaa-mcp-sse"
    """
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    print(f"[IGNITION] AAA Monolith (SSE) starting on port {port}...")

    # Run initial recovery
    recovered = _recover_orphans()
    if recovered > 0:
        print(f"[BOOTSTRAP] Recovered {recovered} orphaned session(s)")

    print(f"   Version: {VERSION}")
    print(f"   Routes: /health, /sse, /messages, /dashboard, /docs")
    print(f"   Motto: DITEMPA BUKAN DIBERI")

    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
