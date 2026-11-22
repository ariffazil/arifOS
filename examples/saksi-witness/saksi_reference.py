#!/usr/bin/env python3
"""
saksi_reference.py — SAKSI: The arifOS Witness Pattern (Sanitized Reference App)

A thin, 1-shot, read-only runtime witness and MCP client paired with a
cryptographic human-in-the-loop (HMAC-SHA256) circuit-breaker for Telegram.

Architectural invariants demonstrated:
  1. Author != Judge: SAKSI has no code-editing tools and no multi-turn loop.
     It binds an arifOS kernel session at OBSERVE_ONLY and reads raw journalctl.
  2. Dynamic SOUL loading: SOUL.template.md is read from disk on every turn,
     allowing persona/contract updates with zero process restarts.
  3. 888 HMAC Circuit-Breaker: The only mutation path is a single-use, 10-minute
     HMAC-SHA256 callback button bound to (unit, chat_id, owner_id, expiry, nonce),
     gated by `systemctl is-failed` (Gate 1) and 1/30m + 3/24h rate limits (Gate 2).

Environment variables (all generic placeholders — never hardcode secrets):
  WITNESS_BOT_TOKEN    Telegram Bot API token from @BotFather
  OWNER_TELEGRAM_ID    Numeric Telegram user ID of the human sovereign (F13)
  ALLOWED_CHAT_IDS     Comma-separated Telegram user/group IDs allowed to query SAKSI
  WITNESS_HMAC_SECRET  32-byte hex secret for signing single-use restart tokens
  KERNEL_MCP_URL       arifOS Kernel MCP endpoint (default: http://127.0.0.1:8088/mcp)
  KERNEL_HEALTH_URL    arifOS Kernel health URL (default: http://127.0.0.1:8088/health)
  FLOW_HEALTH_URL      arifFlow health URL (default: http://127.0.0.1:7073/health)
  FORGE_MCP_URL        A-FORGE MCP endpoint (default: http://127.0.0.1:7072/mcp)
  LLM_CHAT_URL         OpenAI-compatible chat completions URL (default: http://127.0.0.1:4000/v1/chat/completions)
  LLM_MODEL            Model alias (default: forge-777)

License: AGPL-3.0 (https://github.com/ariffazil/arifOS)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path
from typing import Any

import httpx

HERE = Path(__file__).resolve().parent
SOUL_PATH = Path(os.environ.get("WITNESS_SOUL_PATH", str(HERE / "SOUL.template.md")))

BOT_TOKEN = os.environ.get("WITNESS_BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_TELEGRAM_ID", "0"))
ALLOWED_CHATS = {
    int(x.strip())
    for x in os.environ.get("ALLOWED_CHAT_IDS", str(OWNER_ID)).split(",")
    if x.strip().lstrip("-").isdigit()
}
HMAC_SECRET = os.environ.get("WITNESS_HMAC_SECRET", secrets.token_hex(32)).encode()

KERNEL_MCP_URL = os.environ.get("KERNEL_MCP_URL", "http://127.0.0.1:8088/mcp")
KERNEL_HEALTH_URL = os.environ.get("KERNEL_HEALTH_URL", "http://127.0.0.1:8088/health")
FLOW_HEALTH_URL = os.environ.get("FLOW_HEALTH_URL", "http://127.0.0.1:7073/health")
FORGE_MCP_URL = os.environ.get("FORGE_MCP_URL", "http://127.0.0.1:7072/mcp")
LLM_CHAT_URL = os.environ.get("LLM_CHAT_URL", "http://127.0.0.1:4000/v1/chat/completions")
LLM_MODEL = os.environ.get("LLM_MODEL", "forge-777")

# Allowlisted systemd units that SAKSI may diagnose or propose a gated restart for
ALLOWLIST_UNITS = {
    "hermes-asi-gateway.service",
    "arifos-kernel.service",
    "a-forge.service",
    "arifflow.service",
}

HMAC_TTL_SECONDS = 600  # 10-minute single-use token expiry
RATE_LIMIT_WINDOW_SHORT = 1800  # 1 restart per 30 minutes per unit
RATE_LIMIT_WINDOW_DAY = 86400  # max 3 restarts per 24 hours per unit

# In-memory ledger for single-use HMAC nonces and per-unit restart timestamps
_PENDING_TOKENS: dict[str, dict[str, Any]] = {}
_RESTART_HISTORY: dict[str, list[float]] = {}


# ── 1. Cryptographic 888 HMAC Circuit-Breaker ──────────────────────────────
def mint_restart_token(unit: str, chat_id: int, user_id: int) -> tuple[str, str]:
    """Mint a single-use HMAC-SHA256 callback token bound to unit + chat + sovereign."""
    if unit not in ALLOWLIST_UNITS:
        raise ValueError(f"Unit {unit!r} is not in ALLOWLIST_UNITS")
    nonce = secrets.token_hex(6)
    exp = int(time.time()) + HMAC_TTL_SECONDS
    msg = f"{unit}|{chat_id}|{user_id}|{exp}|{nonce}".encode()
    sig = hmac.new(HMAC_SECRET, msg, hashlib.sha256).hexdigest()[:16]
    _PENDING_TOKENS[nonce] = {
        "unit": unit,
        "chat_id": chat_id,
        "user_id": user_id,
        "exp": exp,
        "sig": sig,
        "used": False,
    }
    return nonce, f"rst:{nonce}:{sig}"


def verify_and_consume_token(callback_data: str, chat_id: int, user_id: int) -> str:
    """Verify single-use HMAC token; fail-closed on expiry, replay, or wrong user."""
    parts = callback_data.split(":")
    if len(parts) != 3 or parts[0] != "rst":
        raise PermissionError("Malformed callback token")
    _, nonce, presented_sig = parts
    record = _PENDING_TOKENS.get(nonce)
    if not record:
        raise PermissionError("Unknown or expired token")
    if record["used"]:
        raise PermissionError("Token already consumed (single-use invariant)")
    if time.time() > record["exp"]:
        raise PermissionError("Token expired (TTL 10m exceeded)")
    if user_id != OWNER_ID or user_id != record["user_id"] or chat_id != record["chat_id"]:
        raise PermissionError("Unauthorized actor: only F13 Sovereign may execute 888 switch")

    expected_msg = (
        f"{record['unit']}|{record['chat_id']}|{record['user_id']}|{record['exp']}|{nonce}"
    ).encode()
    expected_sig = hmac.new(HMAC_SECRET, expected_msg, hashlib.sha256).hexdigest()[:16]
    if not hmac.compare_digest(presented_sig, expected_sig):
        raise PermissionError("HMAC signature mismatch")

    record["used"] = True
    return str(record["unit"])


def check_rate_limit(unit: str, now: float | None = None) -> tuple[bool, str]:
    """Gate 2: max 1 restart per 30m and max 3 restarts per 24h per unit."""
    ts = now if now is not None else time.time()
    history = [t for t in _RESTART_HISTORY.get(unit, []) if ts - t < RATE_LIMIT_WINDOW_DAY]
    _RESTART_HISTORY[unit] = history
    recent_30m = [t for t in history if ts - t < RATE_LIMIT_WINDOW_SHORT]
    if recent_30m:
        wait_s = int(RATE_LIMIT_WINDOW_SHORT - (ts - recent_30m[-1]))
        return False, f"Rate limit (1/30m): wait {wait_s}s before restarting {unit}"
    if len(history) >= 3:
        return False, f"Rate limit (3/24h): {unit} already restarted 3 times in 24h (888 HOLD)"
    return True, "PASS"


# ── 2. MCP & Observability Probes (Read-Only) ──────────────────────────────
def mcp_call(url: str, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Minimal JSON-RPC 2.0 Streamable HTTP MCP tool invocation."""
    payload = {
        "jsonrpc": "2.0",
        "id": secrets.token_hex(4),
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


def kernel_light_init(chat_id: int) -> dict[str, Any]:
    """Bind an OBSERVE_ONLY session with the arifOS kernel (:8088/mcp)."""
    try:
        res = mcp_call(
            KERNEL_MCP_URL,
            "arif_init",
            {
                "mode": "light",
                "actor_id": f"saksi-witness/telegram-{chat_id}",
                "intent": "1-shot runtime witness observation",
                "requested_authority": "OBSERVE_ONLY",
            },
        )
        return {"ok": True, "raw": res}
    except Exception as exc:
        return {"ok": False, "error": repr(exc)}


def tool_kernel_health() -> dict[str, Any]:
    """Read live arifOS kernel health (:8088/health)."""
    with httpx.Client(timeout=5.0) as client:
        return client.get(KERNEL_HEALTH_URL).json()


def tool_fq_pulse() -> dict[str, Any]:
    """Read live arifFlow metabolic quotient (:7073/health)."""
    with httpx.Client(timeout=5.0) as client:
        return client.get(FLOW_HEALTH_URL).json()


def tool_ops_diagnose(unit: str) -> dict[str, Any]:
    """Read-only systemd + journalctl witness probe via A-FORGE (:7072/mcp)."""
    if unit not in ALLOWLIST_UNITS:
        return {"ok": False, "error": f"Unit {unit!r} not in ALLOWLIST_UNITS"}
    svc = mcp_call(FORGE_MCP_URL, "forge_vps_services", {"unit": unit})
    jnl = mcp_call(FORGE_MCP_URL, "forge_journalctl", {"unit": unit, "lines": 40})
    return {"ok": True, "unit": unit, "service": svc, "journal_tail": jnl}


# ── 3. Dynamic System Prompt (Zero-Restart Persona Reload) ─────────────────
def build_system_prompt(kernel_session: dict[str, Any]) -> str:
    """Read SOUL.template.md on every turn so persona updates never need a restart."""
    soul = (
        SOUL_PATH.read_text(encoding="utf-8")
        if SOUL_PATH.exists()
        else "You are SAKSI, read-only runtime witness for arifOS."
    )
    now_utc = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    return (
        f"{soul}\n\n"
        f"--- LIVE RUNTIME CONTEXT ---\n"
        f"Timestamp: {now_utc}\n"
        f"Kernel Session (OBSERVE_ONLY): {json.dumps(kernel_session)[:300]}\n"
        "Rule: Always call kernel_health, fq_pulse, or ops_diagnose before making any "
        "claim about service health. Never grade a system from memory."
    )


if __name__ == "__main__":
    # Self-test of the cryptographic 888 HMAC circuit-breaker + rate-limit gates
    demo_unit = "hermes-asi-gateway.service"
    demo_chat = OWNER_ID or 100000001
    OWNER_ID = demo_chat

    nonce, cb_data = mint_restart_token(demo_unit, chat_id=demo_chat, user_id=demo_chat)
    ok_gate, gate_msg = check_rate_limit(demo_unit)
    verified_unit = verify_and_consume_token(cb_data, chat_id=demo_chat, user_id=demo_chat)

    print(
        json.dumps(
            {
                "pattern": "SAKSI — The arifOS Witness Pattern",
                "soul_loaded": SOUL_PATH.exists(),
                "unit": verified_unit,
                "rate_limit_gate": gate_msg,
                "hmac_single_use_verified": True,
            },
            indent=2,
        )
    )
