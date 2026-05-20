"""
arifOS Supabase Client Wrapper
==============================
Replaces all /root/... and /tmp/... JSON state writes with Postgres calls.
Built for use on Prefect Horizon (Python/FastMCP runtime).

Usage:
    from supabase_client import get_supabase, read_well_state, write_well_state, seal_vault

Environment variables required:
    SUPABASE_URL
    SUPABASE_SERVICE_ROLE_KEY
"""

import os
import logging
from typing import Optional

from supabase import create_client, Client
from supabase.client import SupabaseClient

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """
    Returns singleton Supabase client.
    Uses SUPABASE_SERVICE_ROLE_KEY — only for server-side trusted code.
    """
    global _supabase_client
    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise EnvironmentError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set"
            )
        _supabase_client = create_client(url, key)
        logger.info("[arifOS] Supabase client initialized")
    return _supabase_client


# ── VAULT999: Immutable seal ledger ──────────────────────────────────────────


def seal_vault(
    seal_id: str,
    session_id: str,
    verdict: str,
    timestamp: str,
    record_id: Optional[str] = None,
    prev_hash: Optional[str] = None,
    hashofinput: Optional[str] = None,
    telemetrysnapshot: Optional[dict] = None,
    floors_triggered: Optional[list] = None,
    irreversibilityacknowledged: bool = False,
    task: Optional[str] = None,
    final_text: Optional[str] = None,
    turn_count: int = 0,
    profile_name: Optional[str] = None,
    escalation: Optional[dict] = None,
    data: Optional[dict] = None,
) -> dict:
    """
    Write a terminal verdict to arifosmcp_vault_seals.
    Append-only — UPDATE and DELETE are blocked by trigger.

    Args:
        seal_id: UUID identifier
        session_id: Agent session
        verdict: SEAL | HOLD | SABAR | VOID
        timestamp: ISO epoch
        record_id: SHA-256 of content (Merkle leaf ID)
        prev_hash: SHA-256 of previous record (chain link)
        hashofinput: SHA-256(task + finalText + sessionId + turnCount)
        telemetrysnapshot: { dS, peace2, psi_le, W3, G }
        floors_triggered: List of floor codes triggered
        irreversibilityacknowledged: Boolean
        task: Agent task description
        final_text: Agent final response text
        turn_count: Number of turns
        profile_name: Agent profile used
        escalation: Human decision metadata
        data: Full VaultSealRecord as JSONB
    """
    sb = get_supabase()

    payload = {
        "seal_id": seal_id,
        "session_id": session_id,
        "verdict": verdict,
        "timestamp": timestamp,
        "record_id": record_id,
        "prev_hash": prev_hash,
        "hashofinput": hashofinput,
        "telemetrysnapshot": telemetrysnapshot or {},
        "floors_triggered": floors_triggered or [],
        "irreversibilityacknowledged": irreversibilityacknowledged,
        "task": task,
        "final_text": final_text,
        "turn_count": turn_count,
        "profile_name": profile_name,
        "escalation": escalation,
    }

    full_data = data if data is not None else payload

    sb.table("arifosmcp_vault_seals").insert(
        {
            "seal_id": seal_id,
            "session_id": session_id,
            "verdict": verdict,
            "timestamp": timestamp,
            "record_id": record_id,
            "prev_hash": prev_hash,
            "hashofinput": hashofinput,
            "telemetrysnapshot": telemetrysnapshot,
            "floors_triggered": floors_triggered,
            "irreversibilityacknowledged": irreversibilityacknowledged,
            "task": task,
            "final_text": final_text,
            "turn_count": turn_count,
            "profile_name": profile_name,
            "data": full_data,
        }
    ).execute()

    logger.info(f"[arifOS] SEAL written: {seal_id} verdict={verdict}")
    return payload


def query_vault_seals(
    session_id: Optional[str] = None,
    verdict: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    limit: int = 100,
) -> list:
    """
    Query vault seals with optional filters.
    Returns newest first.
    """
    sb = get_supabase()
    q = sb.table("arifosmcp_vault_seals").select("*").order("timestamp", desc=True)

    if session_id:
        q = q.eq("session_id", session_id)
    if verdict:
        q = q.eq("verdict", verdict)
    if since:
        q = q.gte("timestamp", since)
    if until:
        q = q.lte("timestamp", until)
    if limit:
        q = q.limit(limit)

    result = q.execute()
    return result.data or []


def find_vault_seal(seal_id: str) -> Optional[dict]:
    """Find a single vault seal by seal_id."""
    sb = get_supabase()
    result = (
        sb.table("arifosmcp_vault_seals")
        .select("*")
        .eq("seal_id", seal_id)
        .maybe_single()
        .execute()
    )
    return result.data


# ── SESSIONS: replaces /root/WELL/state.json ───────────────────────────────────


def open_session(
    session_id: str,
    agent_id: str,
    risk_tier: str = "medium",
    declared_intent: str = "",
) -> dict:
    """
    Open a new agent session. Creates record if not exists.
    Called at session start (arifOS PipelineCoordinator.vault()).
    """
    sb = get_supabase()
    sb.table("arifosmcp_sessions").insert(
        {
            "session_id": session_id,
            "agent_id": agent_id,
            "risk_tier": risk_tier,
            "declared_intent": declared_intent,
        },
        on_conflict="session_id",
    ).execute()
    logger.info(f"[arifOS] Session opened: {session_id} agent={agent_id}")
    return {"session_id": session_id, "agent_id": agent_id}


def seal_session(session_id: str, final_verdict: str) -> dict:
    """
    Close a session with final verdict.
    Called at session end.
    """
    sb = get_supabase()
    sb.table("arifosmcp_sessions").update(
        {
            "final_verdict": final_verdict,
            "closed_at": "now()",
        }
    ).eq("session_id", session_id).execute()
    logger.info(f"[arifOS] Session sealed: {session_id} verdict={final_verdict}")
    return {"session_id": session_id, "final_verdict": final_verdict}


def get_session(session_id: str) -> Optional[dict]:
    """Retrieve session by session_id."""
    sb = get_supabase()
    result = (
        sb.table("arifosmcp_sessions")
        .select("*")
        .eq("session_id", session_id)
        .maybe_single()
        .execute()
    )
    return result.data


# ── TOOL CALLS: audit log ──────────────────────────────────────────────────────


def log_tool_call(
    run_id: Optional[str],
    session_id: str,
    tool_name: str,
    organ: Optional[str],
    tool_args: Optional[dict],
    tool_result: Optional[str],
    duration_ms: int,
    floor_triggered: list,
    verdict: str,
) -> dict:
    """
    Log a tool execution to arifosmcp_tool_calls.
    """
    sb = get_supabase()
    sb.table("arifosmcp_tool_calls").insert(
        {
            "run_id": run_id,
            "session_id": session_id,
            "tool_name": tool_name,
            "organ": organ,
            "tool_args": tool_args,
            "tool_result": tool_result,
            "duration_ms": duration_ms,
            "floor_triggered": floor_triggered,
            "verdict": verdict,
        }
    ).execute()
    return {"session_id": session_id, "tool_name": tool_name, "verdict": verdict}


# ── CANON RECORDS: ARCHIVIST writes on every SEAL ─────────────────────────────


def write_canon_record(
    adr_id: str,
    title: str,
    decision: str,
    rationale: str,
    agent_id: str,
    session_id: str,
    payload: dict,
    sealed_by: str = "Muhammad Arif bin Fazil",
) -> dict:
    """
    Write to arifosmcp_canon_records on every SEAL verdict.
    This is the ARCHIVIST agent function.
    """
    sb = get_supabase()
    sb.table("arifosmcp_canon_records").insert(
        {
            "adr_id": adr_id,
            "title": title,
            "decision": decision,
            "rationale": rationale,
            "agent_id": agent_id,
            "session_id": session_id,
            "sealed_by": sealed_by,
            "payload": payload,
        },
        on_conflict="adr_id",
    ).execute()
    logger.info(f"[arifOS] Canon record written: ADR-{adr_id}")
    return {"adr_id": adr_id, "agent_id": agent_id}


# ── APPROVAL TICKETS: 888_HOLD queue ──────────────────────────────────────────


def create_approval_ticket(
    ticket_id: str,
    session_id: str,
    status: str,
    risk_level: str,
    intent_model: str,
    domain: Optional[str],
    data: dict,
) -> dict:
    """
    Create or update an approval ticket.
    """
    sb = get_supabase()
    sb.table("arifosmcp_approval_tickets").insert(
        {
            "ticket_id": ticket_id,
            "session_id": session_id,
            "status": status,
            "risk_level": risk_level,
            "intent_model": intent_model,
            "domain": domain,
            "data": data,
        },
        on_conflict="ticket_id",
    ).execute()
    logger.info(f"[arifOS] Ticket created: {ticket_id} status={status}")
    return {"ticket_id": ticket_id, "status": status}


def get_approval_ticket(ticket_id: str) -> Optional[dict]:
    """Get a single approval ticket."""
    sb = get_supabase()
    result = (
        sb.table("arifosmcp_approval_tickets")
        .select("*")
        .eq("ticket_id", ticket_id)
        .maybe_single()
        .execute()
    )
    return result.data


def query_approval_tickets(
    status: Optional[str] = None,
    session_id: Optional[str] = None,
    risk_level: Optional[str] = None,
) -> list:
    """Query approval tickets with filters."""
    sb = get_supabase()
    q = (
        sb.table("arifosmcp_approval_tickets")
        .select("*")
        .order("created_at", desc=True)
    )
    if status:
        q = q.eq("status", status)
    if session_id:
        q = q.eq("session_id", session_id)
    if risk_level:
        q = q.eq("risk_level", risk_level)
    result = q.execute()
    return result.data or []


def update_approval_ticket(ticket_id: str, patch: dict) -> dict:
    """
    Update ticket fields (status, decision, decidedAt, etc.)
    """
    sb = get_supabase()
    result = (
        sb.table("arifosmcp_approval_tickets")
        .update(patch)
        .eq("ticket_id", ticket_id)
        .execute()
    )
    logger.info(f"[arifOS] Ticket updated: {ticket_id}")
    return result.data


# ── FLOOR RULES: constitutional thresholds ────────────────────────────────────


def load_floor_rules() -> list:
    """
    Load F1–F13 constitutional floor rules from database.
    """
    sb = get_supabase()
    result = sb.table("arifosmcp_floor_rules").select("*").order("floor_id").execute()
    return result.data or []


# ── WEALTH: transaction ledger ────────────────────────────────────────────────


def log_transaction(
    tx_type: str,
    asset: Optional[str],
    amount: Optional[float],
    currency: str = "MYR",
    metadata: Optional[dict] = None,
) -> dict:
    """Log a wealth transaction."""
    sb = get_supabase()
    sb.table("arifosmcp_transactions").insert(
        {
            "tx_type": tx_type,
            "asset": asset,
            "amount": amount,
            "currency": currency,
            "metadata": metadata or {},
        }
    ).execute()
    return {"tx_type": tx_type, "asset": asset, "amount": amount}


def log_portfolio_snapshot(
    holdings: dict,
    total_value: Optional[float],
    currency: str = "MYR",
) -> dict:
    """Log a portfolio snapshot."""
    sb = get_supabase()
    sb.table("arifosmcp_portfolio_snapshots").insert(
        {
            "holdings": holdings,
            "total_value": total_value,
            "currency": currency,
        }
    ).execute()
    return {"total_value": total_value, "currency": currency}
