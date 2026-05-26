"""
arifosmcp/runtime/wealth_bridge.py — WEALTH SSE MCP Client Bridge

DITEMPA BUKAN DIBERI — Forged, Not Given

Bridges arifOS kernel (port 8088) to WEALTH organ (port 18082) via SSE + JSON-RPC POST.
WEALTH FastMCP uses StreamableHTTP with server-generated session IDs.

Protocol (MCP StreamableHTTP):
1. Client sends POST with X-MCP-Session-ID header (any UUID)
2. Server responds with its OWN session ID in mcp-session-id response header
3. Client MUST use the server's session ID for all subsequent calls
4. Each POST is a new HTTP request; SSE events contain responses
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC
from typing import Any

import httpx

logger = logging.getLogger("arifosmcp.wealth_bridge")

# Bare-metal: use localhost. Docker: override via WEALTH_BRIDGE_HOST env var.
WEALTH_HOST = os.getenv("WEALTH_BRIDGE_HOST", "localhost")
# Bare-metal: 18082 (wealth-mcp systemd). Docker: 8082 (wealth-organ container).
WEALTH_PORT = int(os.getenv("WEALTH_BRIDGE_PORT", "18082"))
WEALTH_BASE = f"http://{WEALTH_HOST}:{WEALTH_PORT}"

_WEALTH_SESSION_ID: str | None = None


async def _ensure_session() -> str | None:
    """
    Establish or reuse a WEALTH session ID.

    WEALTH is a stateless MCP server — it does not issue mcp-session-id headers.
    This function returns None if no session is needed, or the session ID if WEALTH
    starts requiring sessions in future versions.
    """
    global _WEALTH_SESSION_ID
    if _WEALTH_SESSION_ID is not None:
        return _WEALTH_SESSION_ID

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.post(
            f"{WEALTH_BASE}/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "arifOS-kernel", "version": "1.0"},
                },
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
        )

        if resp.status_code != 200:
            raise ConnectionError(
                f"WEALTH session init failed: {resp.status_code} {resp.text[:200]}"
            )

        server_session = resp.headers.get("mcp-session-id")
        if server_session:
            # WEALTH supports sessions — cache and use it
            _WEALTH_SESSION_ID = server_session
            logger.info(f"WEALTH session established: {server_session}")
            return server_session
        else:
            # WEALTH is stateless — no session needed
            logger.info("WEALTH is stateless — no session required")
            _WEALTH_SESSION_ID = None
            return None


async def _post_json_rpc(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Send a JSON-RPC request to WEALTH.

    WEALTH is stateless — accepts requests with or without session headers.
    Responses are plain JSON (not SSE).
    """
    session_id = await _ensure_session()

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["x-mcp-session-id"] = session_id
        headers["mcp-session-id"] = session_id

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.post(
            f"{WEALTH_BASE}/mcp",
            json=payload,
            headers=headers,
        )

        if resp.status_code == 406:
            raise ConnectionError("WEALTH 406: Accept header issue")

        if resp.status_code >= 400:
            try:
                err_data = resp.json()
                msg = err_data.get("error", {}).get("message", resp.text[:200])
            except Exception:
                msg = resp.text[:200]
            raise ConnectionError(f"WEALTH HTTP {resp.status_code}: {msg}")

        # WEALTH returns plain JSON, not SSE
        parsed = resp.json()
        if parsed.get("error"):
            raise ConnectionError(f"WEALTH JSON-RPC error: {parsed['error']}")

        return parsed.get("result", {})


async def call_wealth_tool(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Call a WEALTH MCP tool by name with arguments.

    Example:
        result = await call_wealth_tool("wealth_reason_npv", {
            "cashflows": [...],
            "discount_rate": 0.12
        })
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {},
        },
    }
    result = await _post_json_rpc(payload)
    return result


async def list_wealth_tools() -> list[dict[str, Any]]:
    """List all tools available from WEALTH MCP server."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {},
    }
    result = await _post_json_rpc(payload)
    return result.get("tools", [])


async def wealth_health_check() -> dict[str, Any]:
    """Check WEALTH server health via MCP ping."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "ping",
        "params": {},
    }
    try:
        await _post_json_rpc(payload)
        return {"status": "healthy", "organ": "WEALTH", "host": WEALTH_HOST}
    except Exception as e:
        return {"status": "unhealthy", "organ": "WEALTH", "error": str(e)}


def reset_session() -> None:
    """Reset the cached session ID (for testing or reconnection)."""
    global _WEALTH_SESSION_ID
    _WEALTH_SESSION_ID = None


# C4 WEALTH ORCHESTRATOR
# ───────────────────────────────────────────────────────────────────────────────
# Runs the mandatory chain for any capital/investment decision.
# This is the single front door — no agent should be calling individual WEALTH
# tools for C4 decisions; they must call this and get a receipt.
#
# Chain order (all required for a valid C4 receipt):
#   conservation → liquidity → entropy_risk → field_macro → signal_information → boundary_governance
#
# If WEALTH is unreachable, returns verdict=HOLD (fail-closed).

_C4_WEALTH_CHAIN = [
    ("wealth_conservation_capital", "conservation"),
    ("wealth_flow_liquidity", "liquidity"),
    ("wealth_entropy_risk", "entropy_risk"),
    ("wealth_field_macro", "field_macro"),
    ("wealth_signal_information", "signal_information"),
    ("wealth_boundary_governance", "boundary_governance"),
]

_C4_FORBIDDEN_OUTPUT = [
    "direct buy instruction",
    "guaranteed return",
    "execution authorization",
    "sure win",
    "buy [ticker] on monday",
    "all-in recommendation",
]


async def wealth_c4_orchestrate(
    user_query: str,
    session_id: str,
    actor_id: str = "arif",
    capital_amount: float | None = None,
    currency: str = "MYR",
    jurisdiction: str = "Malaysia",
    risk_tolerance: str = "unknown",
    horizon: str = "unknown",
    shariah_required: bool | None = None,
) -> dict[str, Any]:
    """
    C4 capital decision coordinator — not a single chokepoint.

    F08 architecture: this function coordinates the receipt chain but each WEALTH
    tool node validates independently. If this coordinator is unavailable, individual
    WEALTH tools still check for session_id. Defense-in-depth, not single gate.

    Sequence: WELL readiness → WEALTH chain (6 tools) → receipt

    If WEALTH is unreachable or boundary_governance fails → verdict=HOLD (fail-closed).

    Returns:
        receipt dict with: verdict, checks_completed, allowed_output_level,
        session_valid, well_readiness, missing_questions, forbidden_output
    """
    import uuid
    from datetime import datetime

    receipt_id = f"WEALTH-C4-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
    checks_completed: list[str] = []
    check_results: dict[str, Any] = {}
    errors: list[str] = []

    # ── Step 0: WELL readiness (W0 invariant — informs, does not veto) ─────────
    well_readiness: dict[str, Any] = {"verdict": "UNKNOWN", "sabar_advisory": False}
    try:
        from arifosmcp.runtime.well_bridge import get_biological_readiness

        well_readiness = get_biological_readiness()
        checks_completed.append("well_readiness")
        check_results["well_readiness"] = well_readiness
    except Exception as e:
        errors.append(f"well_readiness: {e}")
        check_results["well_readiness"] = {"verdict": "UNAVAILABLE", "error": str(e)}

    common_args = {
        "query": user_query,
        "session_id": session_id,
        "actor_id": actor_id,
        "capital_amount": capital_amount,
        "currency": currency,
        "jurisdiction": jurisdiction,
        "risk_tolerance": risk_tolerance,
        "horizon": horizon,
        "shariah_required": shariah_required,
    }

    for tool_name, check_key in _C4_WEALTH_CHAIN:
        try:
            result = await call_wealth_tool(tool_name, common_args)
            checks_completed.append(check_key)
            check_results[check_key] = result
        except Exception as e:
            errors.append(f"{check_key}: {e}")
            logger.warning("C4 orchestrator: WEALTH tool %s failed — %s", tool_name, e)
            # Non-fatal: continue chain; boundary_governance failure is fatal (see below)
            check_results[check_key] = {"status": "unavailable", "error": str(e)}

    # Boundary governance is the minimum required check — HOLD if absent
    boundary_ok = "boundary_governance" in checks_completed
    conservation_ok = "conservation" in checks_completed
    liquidity_ok = "liquidity" in checks_completed

    if not boundary_ok:
        allowed_output_level = "HOLD"
    elif not (conservation_ok and liquidity_ok):
        allowed_output_level = "PARTIAL"
    elif len(checks_completed) >= 5:
        allowed_output_level = "ADVISORY_ONLY"
    else:
        allowed_output_level = "COMPARISON_ONLY"

    # Determine missing context questions
    missing_questions: list[str] = []
    if capital_amount is None:
        missing_questions.append("How much capital are you allocating?")
    if risk_tolerance == "unknown":
        missing_questions.append(
            "What is your risk tolerance? (conservative / moderate / aggressive)"
        )
    if horizon == "unknown":
        missing_questions.append("What is your investment horizon? (short / medium / long term)")
    if shariah_required is None:
        missing_questions.append("Is Shariah-compliant investment required?")

    receipt: dict[str, Any] = {
        "receipt_id": receipt_id,
        "session_id": session_id,
        "session_valid": bool(session_id),
        "decision_class": "C4",
        "well_readiness": well_readiness.get("verdict", "UNKNOWN"),
        "well_sabar_advisory": well_readiness.get("sabar_advisory", False),
        "checks_completed": checks_completed,
        "checks_failed": [k for _, k in _C4_WEALTH_CHAIN if k not in checks_completed],
        "allowed_output_level": allowed_output_level,
        "ticker_level_allowed": False,
        "execution_authorized": False,
        "recommendation_only": True,
        "human_final_authority": actor_id,
        "missing_questions": missing_questions,
        "forbidden_output": _C4_FORBIDDEN_OUTPUT,
        "errors": errors,
        "check_results": check_results,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    if allowed_output_level == "HOLD":
        receipt["verdict"] = "HOLD"
        receipt["safe_answer_template"] = (
            "C4 CAPITAL DECISION DETECTED. Session present but WEALTH governance chain incomplete. "
            "Cannot provide investment-specific guidance without boundary_governance clearance."
        )
    else:
        receipt["verdict"] = allowed_output_level
        receipt["safe_answer_template"] = (
            f"Advisory framework available (level: {allowed_output_level}). "
            "No specific tickers, amounts, or buy dates. Human final authority retained."
        )

    return receipt
