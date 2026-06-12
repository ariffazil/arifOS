"""
arifosmcp/runtime/vault_sealer.py
═══════════════════════════════════════════════════════════════════════════════
Auto-seal consequential state transitions to VAULT999.

This is a clerk-level audit receipt, not a sovereign SEAL. It writes a
non-binding AUDIT_RECEIPT to vault999-writer for every MUTATE/ATOMIC action
so the chain remains continuous and state transitions are recoverable.

Sovereign SEAL (arif_vault_seal / 888_JUDGE) remains the only binding verdict.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("arifosmcp.vault_sealer")

# Tools whose successful execution represents a consequential state transition
CONSEQUENTIAL_TOOLS: set[str] = {
    "arif_forge_execute",
    "arif_judge_deliberate",
    "arif_vault_seal",
    "arif_session_init",
    "arif_lease_issue",
    "arif_lease_revoke",
    "arif_organ_attest",
    "arif_organ_attest_all",
    "arif_detect_narrative_tension",
}

VAULT_WRITER_URL = os.getenv("VAULT999_WRITER_URL", "http://127.0.0.1:5001")
VAULT_WRITER_TOKEN = os.getenv("VAULT_WRITER_TOKEN", "")


# Lazy token load if env not set
if not VAULT_WRITER_TOKEN:
    for _env_path in ("/etc/arifOS/vault999.env", "/root/.secrets/vault.env"):
        try:
            with open(_env_path) as _f:
                for _line in _f:
                    if _line.startswith("VAULT_WRITER_TOKEN="):
                        VAULT_WRITER_TOKEN = _line.strip().split("=", 1)[1].strip()
                        break
            if VAULT_WRITER_TOKEN:
                break
        except Exception:
            continue


def _payload_summary(response: dict[str, Any]) -> str:
    """Compact, privacy-safe summary of the response for the audit chain."""
    try:
        return json.dumps(
            {
                "status": response.get("status"),
                "verdict": response.get("verdict"),
                "tool": response.get("tool"),
                "actor_id": response.get("actor_id"),
                "session_id": response.get("session_id"),
            },
            sort_keys=True,
        )
    except Exception:
        return "{}"


def _sha256_of_text(text: str) -> str:
    return f"sha256:{hashlib.sha256(text.encode()).hexdigest()}"


async def write_audit_receipt(
    tool_name: str,
    response: dict[str, Any],
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Write a non-binding audit receipt for a state transition to VAULT999.

    Returns the vault receipt or an error dict. Never raises — callers rely on
    best-effort audit continuity.
    """
    if not VAULT_WRITER_TOKEN:
        return {"sealed": False, "error": "VAULT_WRITER_TOKEN not configured"}

    payload = {
        "tool": tool_name,
        "status": response.get("status"),
        "verdict": response.get("verdict"),
        "session_id": session_id,
        "actor_id": actor_id,
        "response_hash": _sha256_of_text(json.dumps(response, sort_keys=True, default=str)),
    }

    request_body = {
        "agent_id": actor_id or "arifOS-kernel",
        "action": f"state_transition:{tool_name}",
        "payload": payload,
        "payload_summary": _payload_summary(response),
        "payload_hash": payload["response_hash"],
        "session_id": session_id,
        "trace_id": session_id,
        "claim_state": "OBSERVED",
        "binding": False,
        "irreversible": False,
        "tags": ["live-kernel", "state-transition", tool_name],
        "metadata": {"source": "arifosmcp.runtime.vault_sealer"},
        "created_at": datetime.now(UTC).isoformat(),
    }

    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{VAULT_WRITER_URL}/audit-receipt",
                json=request_body,
                headers={
                    "Authorization": f"Bearer {VAULT_WRITER_TOKEN}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info(
                f"[vault_sealer] audit receipt written for {tool_name}: vault_id={data.get('id')}"
            )
            return {
                "sealed": True,
                "vault_id": data.get("id"),
                "chain_hash": data.get("chain_hash"),
            }
    except Exception as e:
        logger.warning(f"[vault_sealer] failed to write audit receipt for {tool_name}: {e}")
        return {"sealed": False, "error": str(e)}


def should_seal(tool_name: str, response: dict[str, Any]) -> bool:
    """Determine if a tool response should be auto-sealed as a state transition."""
    if tool_name not in CONSEQUENTIAL_TOOLS:
        return False
    verdict = response.get("verdict")
    if verdict in ("HOLD", "DENY", "VOID", "SABAR"):
        # Non-SEAL outcomes are still state transitions (a decision was made).
        return True
    if response.get("status") in ("OK", "SEAL", "DEGRADED"):
        return True
    return False


def schedule_state_transition_seal(
    tool_name: str,
    response: dict[str, Any],
    session_id: str | None = None,
    actor_id: str | None = None,
) -> None:
    """
    Best-effort fire-and-forget seal of a consequential state transition.

    If an event loop is running, schedules an async task. Otherwise no-ops.
    This keeps the MCP response path fast while preserving audit continuity.
    """
    if not should_seal(tool_name, response):
        return

    try:
        import asyncio

        loop = asyncio.get_running_loop()
        loop.create_task(write_audit_receipt(tool_name, response, session_id, actor_id))
    except RuntimeError:
        # No running loop — sync context. Seal is skipped; caller may retry.
        logger.debug(f"[vault_sealer] no event loop; skipping async seal for {tool_name}")


__all__ = [
    "CONSEQUENTIAL_TOOLS",
    "write_audit_receipt",
    "should_seal",
    "schedule_state_transition_seal",
]
