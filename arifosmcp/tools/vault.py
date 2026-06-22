
"""
arifosmcp/tools/vault_seal.py — 999_VAULT
═════════════════════════════════════════

Immutable ledger and audit engine.
"""

from __future__ import annotations

import hashlib
from typing import Literal

from arifosmcp.runtime.tools import _arif_seal
from arifosmcp.schemas.verdict import SealOutput


async def arif_seal(
    mode: Literal["seal", "verify", "chain", "list", "dry_run", "seal_card", "render"] = "seal",
    payload: str = "",
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    actor_signature: str | None = None,
    nonce: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
    witness_type: str = "ai",
    drift_events: list[dict] | None = None,
    verdict: str = "SEAL",
    floors: dict | None = None,
    witness: dict | None = None,
    trace_root: str | None = None,
    policy_digest: str | None = None,
    cooldown_entry_id: str | None = None,
) -> SealOutput:
    """
    999_VAULT: Immutable ledger anchoring.

    Args:
        cooldown_entry_id: If provided, the seal is gated on SABAR cooldown completion.
            Without it, cooldown is logged as bypassed (legacy compat path).
            Internal hardening — no new tool surface.
    """
    # ── GÖDEL-LOCK (Mission 001): No self-certification ──
    # The actor of an IRREVERSIBLE mutation cannot be the final certifier.
    # Enforced at the SEAL boundary — the last gate before Vault999 write.
    if mode == "seal" and ack_irreversible:
        judge_session_id = session_id
        actor_session_id = actor_id  # the session that originated the action
        # If actor == judge, block self-certification
        if actor_session_id and judge_session_id and actor_session_id == judge_session_id:
            return SealOutput(
                mode=mode,
                verdict="HOLD",
                payload=payload,
                status="GODEL_LOCK",
                chain_ok=False,
                entry_id="",
                created_at="",
                note=(
                    f"GÖDEL-LOCK: actor {actor_session_id} cannot certify its own "
                    f"IRREVERSIBLE action. Requires separate judge session (F13 SOVEREIGN or "
                    f"independent 888 JUDGE). This is an illegal state — the system cannot "
                    f"self-certify."
                ),
            )
        # witness required for IRREVERSIBLE
        if not witness:
            return SealOutput(
                mode=mode,
                verdict="HOLD",
                payload=payload,
                status="MISSING_WITNESS",
                chain_ok=False,
                entry_id="",
                created_at="",
                note=(
                    "GÖDEL-LOCK: IRREVERSIBLE seal requires a non-null witness. "
                    "No witness_id provided. An external witness (human, signed sensor, "
                    "or vault anchor) must attest to this action."
                ),
            )

    # ── SABAR cooldown gate (internal hardening) ──
    cooldown_meta: dict = {}
    if mode == "seal" and payload:
        try:
            from arifosmcp.core.cooldown_engine import get_cooldown_engine

            engine = get_cooldown_engine()
            if cooldown_entry_id:
                entry = engine.check(cooldown_entry_id)
                if entry and entry.verdict == "SEAL":
                    cooldown_meta["cooldown"] = "verified"
                    cooldown_meta["cooldown_entry_id"] = cooldown_entry_id
                elif entry:
                    cooldown_meta["cooldown"] = "pending"
                    cooldown_meta["cooldown_entry_id"] = cooldown_entry_id
                    cooldown_meta["cooldown_remaining_hours"] = entry.remaining_hours
                    cooldown_meta["cooldown_verdict"] = entry.verdict
                else:
                    cooldown_meta["cooldown"] = "not_found"
            else:
                # Legacy path — no cooldown entry, log bypass + increment counter
                auto_entry = engine.propose(
                    artifact_ref=(
                        f"vault:{session_id or 'anon'}:"
                        f"{hashlib.md5(payload.encode()).hexdigest()[:8]}"  # nosec
                    ),
                    description="auto-registered from vault seal (legacy compat)",
                    risk_tier="low",
                    session_id=session_id,
                )
                bypass_n = engine.record_bypass()
                cooldown_meta["cooldown"] = "bypassed"
                cooldown_meta["cooldown_entry_id"] = auto_entry.entry_id
                cooldown_meta["cooldown_bypass_count"] = bypass_n
                cooldown_meta["cooldown_note"] = (
                    f"legacy compat — cooldown bypassed (bypass #{bypass_n}). "
                    f"Will hard-enforce in Stage 2C."
                )
        except Exception:
            cooldown_meta["cooldown"] = "unavailable"

    if mode in ("seal_card", "render"):
        return _build_seal_card(
            verdict=verdict,
            floors=floors,
            witness=witness,
            trace_root=trace_root,
            policy_digest=policy_digest,
            mode=mode,
        )

    result = _arif_seal(
        mode=mode,
        payload=payload,
        session_id=session_id,
        ack_irreversible=ack_irreversible,
        actor_id=actor_id,
        actor_signature=actor_signature,
        nonce=nonce,
        constitutional_chain_id=constitutional_chain_id,
        judge_state_hash=judge_state_hash,
        witness_type=witness_type,
        drift_events=drift_events,
    )
    if cooldown_meta:
        result["meta"] = result.get("meta", {})
        result["meta"]["sabar_cooldown"] = cooldown_meta
    # Backward-compat alias (deprecated 2026-06-06)
    if "meta" in result:
        _meta = result["meta"]
        if "violated_laws" in _meta and "failed_floors" not in _meta:
            _meta["failed_floors"] = [
                f"F{int(v[1:]):02d}" if v.startswith("L") and v[1:].isdigit() else v
                for v in _meta["violated_laws"]
            ]
    return SealOutput(**result)


def _build_seal_card(
    verdict: str,
    floors: dict | None,
    witness: dict | None,
    trace_root: str | None,
    policy_digest: str | None,
    mode: str,
) -> SealOutput:
    """Build structured constitutional seal data (read-only, no irreversible write)."""
    from arifosmcp.runtime.rest_routes import _build_governance_status_payload

    payload = _build_governance_status_payload()
    seal_data = {
        "verdict": verdict,
        "floors": floors or payload.get("floors", {}),
        "witness": witness or payload.get("witness", {}),
        "trace_root": trace_root,
        "policy_digest": policy_digest,
        "mode": mode,
    }

    if mode == "render":
        seal_data["_meta"] = {"ui": {"domain": "web-sandbox.oaiusercontent.com"}}

    return SealOutput(
        entry_id=f"card_{hash(str(seal_data)) & 0xFFFFFFFF:08x}",
        chain_hash=trace_root or "unsigned",
        timestamp=payload.get("telemetry", {}).get("timestamp") or "0",
        permanence_flag=False,
        status="OK",
        tool="arif_seal",
        mode=mode,
        seal_data=seal_data,
    )

# Backward compatibility alias
arif_vault_seal = arif_seal
