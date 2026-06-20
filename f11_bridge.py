#!/usr/bin/env python3
"""
F13 Sovereign Witness Bridge — arifOS Federation (Pilot)
=========================================================
Scope-restricted pilot for low-stakes VAULT999 seals.

Agents → seal-bridge (:5002) → vault999-writer (:5001) → VAULT999

The bridge auto-witnesses with Arif's Telegram session context when he is
actively connected. No elicitation. No blocking for allowed low-stakes actions.

PILOT GUARDRAILS:
  - Only actions matching ALLOWED_ACTION_PREFIXES pass.
  - Presence is determined by a message from Arif's Telegram user_id within
    SESSION_MAX_AGE_SEC (default 300s).
  - Per-agent rate limit: MAX_SEALS_PER_HOUR.
  - Every seal triggers an audit log + optional Telegram notification.
  - High-stakes / out-of-scope actions return 403; Arif not active returns 423.

CONSTITUTIONAL NOTE:
  F11 AUTH gate in vault999-writer accepts human_signature as a witness
  STRING when ed25519_signature is omitted. This bridge derives that string
  from Arif's active Telegram session — proving human presence for the
  pilot scope without per-seal manual approval.

LAYOUT:
  /root/arifOS/f11_bridge.py              — this file (canonical)
  /root/arifOS/deploy/f11-bridge.service  — systemd unit
  /root/arifOS/deploy/f11-bridge.toml     — optional config

USAGE (from any agent):
  curl -X POST http://localhost:5002/seal \
    -H "Content-Type: application/json" \
    -H "X-Agent-ID: kimi@af-forge" \
    -d '{"action":"CONTEXT_SYNC", "payload":{...}, "verdict":"SEAL"}'

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from __future__ import annotations

import asyncio
import logging
import os
import sqlite3
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

# ── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("seal-bridge")

# ── Config ────────────────────────────────────────────────────────────
VAULT999_WRITER = os.getenv("VAULT999_WRITER_URL", "http://127.0.0.1:5001")
VAULT999_WRITER_TOKEN = os.getenv("VAULT999_WRITER_TOKEN")
VAULT_WRITER_TOKEN = os.getenv("VAULT_WRITER_TOKEN")
VAULT999_WRITER_TOKEN_FILE = os.getenv(
    "VAULT999_WRITER_TOKEN_FILE", "/run/secrets/vault_writer_token"
)
if not VAULT999_WRITER_TOKEN:
    if VAULT_WRITER_TOKEN:
        VAULT999_WRITER_TOKEN = VAULT_WRITER_TOKEN
    elif Path(VAULT999_WRITER_TOKEN_FILE).exists():
        VAULT999_WRITER_TOKEN = Path(VAULT999_WRITER_TOKEN_FILE).read_text().strip()
BRIDGE_PORT = int(os.getenv("BRIDGE_PORT", "5002"))
HERMES_DB = Path(os.getenv("HERMES_DB", "/root/HERMES/state.db"))
# F11 AUTH: ARIF_TELEGRAM_ID sourced from /etc/arifOS/vault999.env.
# Default "0" = fail-closed. Bridge refuses all witnesses when unset.
# Sovereign value must be injected via systemd EnvironmentFile.
ARIF_TELEGRAM_ID = os.getenv("ARIF_TELEGRAM_ID", "0")
if ARIF_TELEGRAM_ID == "0":
    import logging as _logging

    _logging.getLogger(__name__).warning(
        "ARIF_TELEGRAM_ID not set — bridge will refuse all witnesses (F11 fail-closed)"
    )
SESSION_MAX_AGE_SEC = int(os.getenv("SESSION_MAX_AGE_SEC", "300"))  # 5 min pilot
MAX_SEALS_PER_HOUR = int(os.getenv("MAX_SEALS_PER_HOUR", "10"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Pilot scope: low-stakes seal actions only.
ALLOWED_ACTION_PREFIXES = frozenset(
    os.getenv(
        "ALLOWED_ACTION_PREFIXES",
        "AAA_REGISTRY,CONTEXT_SYNC,FASTMCP_ALIGN,SESSION_CLOSE,AGENT_KICKSTART",
    ).split(",")
)

# ── App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="F13 Sovereign Witness Bridge (Pilot)",
    version="1.1.0",
    description="Scope-restricted auto-witness for VAULT999 seals.",
)

# In-memory rate limiter: (agent_id, action_prefix) -> list of unix timestamps.
_rate_limit_buckets: defaultdict[tuple[str, str], list[float]] = defaultdict(list)
_rate_lock = asyncio.Lock()


# ── Models ────────────────────────────────────────────────────────────
class SealRequest(BaseModel):
    """Request from any federation agent to seal an action."""

    action: str
    payload: dict = Field(default_factory=dict)
    verdict: str = "SEAL"
    epoch: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    irreversibility_ack: bool = True
    metadata: dict = Field(default_factory=dict)


class SealResponse(BaseModel):
    """Response after bridging to vault999-writer."""

    sealed: bool
    vault_id: Optional[int] = None
    merkle_leaf: Optional[str] = None
    witness: str
    witness_source: str
    error: Optional[str] = None


class BridgeHealth(BaseModel):
    status: str
    vault_writer: str
    hermes_db: str
    arif_active: bool
    allowed_prefixes: list[str]
    pending_seals: int


# ── Helpers ───────────────────────────────────────────────────────────
def _is_allowed_action(action: str) -> bool:
    """Return True if action is in the pilot allowlist."""
    return any(action.startswith(prefix.strip()) for prefix in ALLOWED_ACTION_PREFIXES)


async def _check_rate_limit(agent_id: str, action: str) -> bool:
    """Return True if agent is within rate limit for this action prefix."""
    prefix = next(
        (p for p in ALLOWED_ACTION_PREFIXES if action.startswith(p.strip())),
        action,
    )
    key = (agent_id, prefix)
    now = time.time()
    window_start = now - 3600.0
    async with _rate_lock:
        bucket = _rate_limit_buckets[key]
        # Drop old timestamps
        bucket[:] = [ts for ts in bucket if ts > window_start]
        if len(bucket) >= MAX_SEALS_PER_HOUR:
            return False
        bucket.append(now)
    return True


def _is_arif_active() -> tuple[bool, str]:
    """
    Check if Arif has an active Telegram session in Hermes.

    Active = a user message from Arif (user_id=ARIF_TELEGRAM_ID) within
    SESSION_MAX_AGE_SEC in any channel.

    Returns (active: bool, context_string: str).
    """
    if not HERMES_DB.exists():
        return False, "hermes_db_not_found"

    try:
        conn = sqlite3.connect(str(HERMES_DB))
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            """
            SELECT m.timestamp, m.content, s.source as channel, s.user_id
            FROM messages m
            JOIN sessions s ON m.session_id = s.id
            WHERE m.role = 'user'
              AND s.user_id = ?
              AND m.content NOT LIKE '%[OUT-OF-BAND%'
            ORDER BY m.timestamp DESC
            LIMIT 1
            """,
            (ARIF_TELEGRAM_ID,),
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            return False, "no_recent_arif_message"

        ts = row["timestamp"]
        # Hermes stores timestamp as REAL unix epoch
        try:
            msg_time = datetime.fromtimestamp(float(ts), tz=timezone.utc)
        except (ValueError, TypeError):
            try:
                msg_time = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            except (ValueError, TypeError):
                return False, "unparseable_timestamp"

        age_sec = (datetime.now(timezone.utc) - msg_time).total_seconds()

        if age_sec > SESSION_MAX_AGE_SEC:
            return False, f"session_stale_{int(age_sec)}s"

        # Build context witness
        channel = row["channel"] if "channel" in row.keys() else "unknown"
        ctx = f"uid={ARIF_TELEGRAM_ID}:channel={channel}:ts={msg_time.isoformat()[:19]}"
        return True, ctx

    except Exception as e:
        logger.warning(f"Session check failed: {e}")
        return False, f"db_error:{e}"


async def _notify_telegram(message: str) -> None:
    """Send a notification if Telegram bot credentials are configured."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.info(f"[notify] {message}")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message[:4000],
        "parse_mode": "HTML",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(url, json=payload)
            if r.status_code != 200:
                logger.warning(f"Telegram notify failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        logger.warning(f"Telegram notify exception: {e}")


async def _forward_to_vault(
    req: SealRequest,
    agent_id: str,
    human_signature: str,
    witness_source: str,
) -> SealResponse:
    """Forward a seal request to vault999-writer."""
    now = datetime.now(timezone.utc).isoformat()

    body = {
        "agent_id": agent_id,
        "action": req.action,
        "payload": req.payload,
        "epoch": req.epoch or now,
        "verdict": req.verdict,
        "human_ratifier": "arif",
        "human_signature": human_signature,
        "ratified_at": now,
        "irreversibility_ack": req.irreversibility_ack,
        "tags": list(req.tags) + ["auto-witness", witness_source, "pilot"],
        "metadata": {
            **(req.metadata or {}),
            "bridge_version": "1.1.0",
            "witness_source": witness_source,
            "arif_telegram_id": ARIF_TELEGRAM_ID,
            "session_max_age_sec": SESSION_MAX_AGE_SEC,
        },
    }

    headers = {}
    if VAULT999_WRITER_TOKEN:
        headers["X-Writer-Token"] = VAULT999_WRITER_TOKEN

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.post(
                f"{VAULT999_WRITER}/seal",
                json=body,
                headers=headers,
            )
            if r.status_code == 200:
                data = r.json()
                return SealResponse(
                    sealed=True,
                    vault_id=data.get("id"),
                    merkle_leaf=data.get("merkle_leaf"),
                    witness=human_signature,
                    witness_source=witness_source,
                )
            else:
                detail = r.text[:500]
                logger.error(f"Vault writer rejected: {r.status_code} {detail}")
                return SealResponse(
                    sealed=False,
                    witness=human_signature,
                    witness_source=witness_source,
                    error=f"vault_rejected:{r.status_code}:{detail}",
                )
        except httpx.ConnectError as e:
            return SealResponse(
                sealed=False,
                witness="",
                witness_source="",
                error=f"vault_unreachable:{e}",
            )


# ── Routes ────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    """Health check."""
    active, ctx = _is_arif_active()

    # Check vault writer
    vault_ok = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{VAULT999_WRITER}/health")
            if r.status_code == 200:
                vault_ok = "healthy"
            else:
                vault_ok = f"http_{r.status_code}"
    except Exception:
        vault_ok = "unreachable"

    return BridgeHealth(
        status="ok" if vault_ok == "healthy" else "degraded",
        vault_writer=vault_ok,
        hermes_db="available" if HERMES_DB.exists() else "missing",
        arif_active=active,
        allowed_prefixes=sorted(ALLOWED_ACTION_PREFIXES),
        pending_seals=0,  # No queue in pilot
    )


@app.post("/seal", response_model=SealResponse)
async def seal(req: SealRequest, request: Request):
    """
    Seal a low-stakes action with sovereign presence witness.

    Requires X-Agent-ID header identifying the requesting agent.
    """
    agent_id = request.headers.get("X-Agent-ID", "unknown-agent")

    # Step 1: Scope check
    if not _is_allowed_action(req.action):
        logger.warning(f"REJECTED out-of-scope seal from {agent_id}: {req.action}")
        raise HTTPException(
            status_code=403,
            detail={
                "error": "ACTION_OUT_OF_SCOPE",
                "action": req.action,
                "allowed_prefixes": sorted(ALLOWED_ACTION_PREFIXES),
                "message": "This action is not in the pilot allowlist. Use explicit sovereign signature.",
            },
        )

    # Step 2: Rate limit
    if not await _check_rate_limit(agent_id, req.action):
        logger.warning(f"RATE LIMITED seal from {agent_id}: {req.action}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "RATE_LIMIT_EXCEEDED",
                "max_per_hour": MAX_SEALS_PER_HOUR,
                "message": "Too many auto-witnessed seals from this agent. Wait or use explicit signature.",
            },
        )

    # Step 3: Witness Arif's presence
    active, session_ctx = _is_arif_active()

    if not active:
        logger.warning(f"HOLD seal from {agent_id} — Arif not active ({session_ctx})")
        raise HTTPException(
            status_code=423,  # Locked
            detail={
                "error": "SOVEREIGN_NOT_PRESENT",
                "reason": session_ctx,
                "message": (
                    "Arif is not in an active Telegram session. "
                    "Seal held until sovereign returns. Retry later."
                ),
            },
        )

    # Step 4: Build witness and forward
    witness = (
        f"ARIF_ACTIVE_TELEGRAM:{session_ctx}:action={req.action}:"
        f"agent={agent_id}:nonce={uuid.uuid4().hex[:8]}"
    )
    witness_source = "auto-witness-pilot"
    logger.info(f"Auto-witnessed seal from {agent_id}: {req.action[:60]}...")

    result = await _forward_to_vault(req, agent_id, witness, witness_source)

    if not result.sealed:
        await _notify_telegram(
            f"⚠️ <b>F11 Bridge FAILED</b>\n"
            f"Action: <code>{req.action}</code>\n"
            f"Agent: <code>{agent_id}</code>\n"
            f"Error: <code>{result.error}</code>"
        )
        raise HTTPException(status_code=502, detail=result.error)

    await _notify_telegram(
        f"✅ <b>F11 Bridge SEALED</b>\n"
        f"Action: <code>{req.action}</code>\n"
        f"Agent: <code>{agent_id}</code>\n"
        f"Vault ID: <code>{result.vault_id}</code>\n"
        f"Merkle: <code>{(result.merkle_leaf or '?')[:16]}</code>"
    )

    logger.info(f"SEALED: id={result.vault_id} leaf={(result.merkle_leaf or '?')[:16]}...")
    return result


# ── Entry ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Seal bridge starting on :{BRIDGE_PORT} → vault999-writer {VAULT999_WRITER}")
    logger.info(f"Hermes DB: {HERMES_DB} (exists={HERMES_DB.exists()})")
    logger.info(f"Arif Telegram ID: {ARIF_TELEGRAM_ID}")
    logger.info(f"Allowed prefixes: {sorted(ALLOWED_ACTION_PREFIXES)}")
    uvicorn.run(app, host="127.0.0.1", port=BRIDGE_PORT, log_level="info")
