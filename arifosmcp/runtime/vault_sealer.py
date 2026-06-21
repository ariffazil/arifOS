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
    # ── Shadow-Detection Tools (Phase 1, 2026-06-21) ──────────────
    "arif_tool_exists",
    "arif_cross_attest",
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

    call_hash = response.get("call_hash", "")
    payload = {
        "tool": tool_name,
        "status": response.get("status"),
        "verdict": response.get("verdict"),
        "session_id": session_id,
        "actor_id": actor_id,
        "call_hash": call_hash,
        "trace_id": response.get("trace_id"),
        "response_hash": _sha256_of_text(json.dumps(response, sort_keys=True, default=str)),
        "prediction": response.get("prediction"),
        "observed_result": response.get("observed_result"),
        "delta_from_prediction": response.get("delta_from_prediction"),
        "delta_numeric": response.get("delta_numeric"),
        "lesson": response.get("lesson"),
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
        "tearframe_metrics": {
            "truth_doubt_margin": response.get("truth_doubt_margin", 0.0),
            "echo_delta_s": response.get("echo_delta_s", 0.0),
            "amanah_irreversible_blocked": response.get("amanah_irreversible_blocked", False),
            "rasa_kappa_r": response.get("rasa_kappa_r", 0.0),
            "peace_squared": response.get("peace_squared", 0.0),
        },
        "entropy_total": response.get("entropy_total", 0.0),
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


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: seal_transition() — the only lawful path from kernel_transition()
# to vault999-writer. Writes a KSR_TRANSITION event to the /transition
# endpoint. This is the conduit that makes agent time real.
#
# Doctrine: Only kernel_transition() calls this. No other code path.
# No public/MCP exposure in Phase 1.
# ─────────────────────────────────────────────────────────────────────────────


async def seal_transition(
    receipt_id: str,
    event_type: str,
    payload: dict[str, Any],
    session_id: str | None = None,
    agent_id: str | None = None,
) -> dict[str, Any]:
    """
    Write a TransitionReceipt to vault999-writer /transition endpoint.

    Called ONLY by kernel_transition(). This is the sole conduit from
    KSR present-state to vault sealed-past.

    The receipt payload contains:
      - receipt_id: unique transition identifier
      - event_type: canonical KSR event type
      - from_ksr_hash / to_ksr_hash: the state arrow
      - prior_ledger_hash / event_hash / ledger_hash: the time arrow
      - started_at_ns / ended_at_ns / duration_ms: temporal bounds
      - caller / ksr_epoch_id: attribution
      - authority_source / proof_level / verdict: governance
      - metadata: optional structured data

    Returns vault response or error dict. Never raises — best-effort.
    """
    if not VAULT_WRITER_TOKEN:
        return {"sealed": False, "error": "VAULT_WRITER_TOKEN not configured"}

    request_body = {
        "agent_id": agent_id or "arifOS-kernel",
        "action": f"ksr_transition:{event_type}",
        "payload": payload,
        "payload_hash": _sha256_of_text(
            json.dumps(payload, sort_keys=True, default=str)
        ),
        "payload_summary": json.dumps(
            {
                "receipt_id": payload.get("receipt_id"),
                "event_type": payload.get("event_type"),
                "from_ksr_hash": payload.get("from_ksr_hash", "")[:24],
                "to_ksr_hash": payload.get("to_ksr_hash", "")[:24],
                "ledger_hash": payload.get("ledger_hash", "")[:24],
                "duration_ms": payload.get("duration_ms", 0),
                "caller": payload.get("caller"),
            },
            sort_keys=True,
        ),
        "session_id": session_id,
        "trace_id": receipt_id,
        "claim_state": "OBSERVED",
        "binding": False,
        "irreversible": False,
        "tags": ["ksr-transition", event_type, "kernel_transition"],
        "metadata": {
            "source": "arifosmcp.runtime.kernel_state.kernel_transition",
            "receipt_id": receipt_id,
            "event_type": event_type,
        },
        "created_at": datetime.now(UTC).isoformat(),
    }

    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{VAULT_WRITER_URL}/transition",
                json=request_body,
                headers={
                    "Authorization": f"Bearer {VAULT_WRITER_TOKEN}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info(
                f"[seal_transition] KSR transition sealed: "
                f"receipt_id={receipt_id} vault_id={data.get('id')} "
                f"event_type={event_type}"
            )
            return {
                "sealed": True,
                "vault_id": data.get("id"),
                "chain_hash": data.get("chain_hash"),
            }
    except Exception as e:
        logger.warning(
            f"[seal_transition] failed to seal transition {receipt_id}: {e}"
        )
        return {"sealed": False, "error": str(e)}


__all__ = [
    "CONSEQUENTIAL_TOOLS",
    "seal_transition",
    "write_audit_receipt",
    "should_seal",
    "schedule_state_transition_seal",
]
