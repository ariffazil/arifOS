"""
arifosmcp/tools/vault_seal.py — 999_VAULT
═════════════════════════════════════════

Immutable ledger and audit engine.
"""

from __future__ import annotations

from typing import Literal

from arifosmcp.runtime.tools import _arif_vault_seal
from arifosmcp.schemas.verdict import SealOutput


def arif_vault_seal(
    mode: Literal[
        "seal", "verify", "chain", "list", "dry_run", "seal_card", "render"
    ] = "seal",
    payload: str = "",
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
    witness_type: str = "ai",
    drift_events: list[dict] | None = None,
    verdict: str = "SEAL",
    floors: dict | None = None,
    witness: dict | None = None,
    trace_root: str | None = None,
    policy_digest: str | None = None,
) -> SealOutput:
    if mode in ("seal_card", "render"):
        return _build_seal_card(
            verdict=verdict,
            floors=floors,
            witness=witness,
            trace_root=trace_root,
            policy_digest=policy_digest,
            mode=mode,
        )

    return SealOutput(
        **_arif_vault_seal(
            mode=mode,
            payload=payload,
            session_id=session_id,
            ack_irreversible=ack_irreversible,
            actor_id=actor_id,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            witness_type=witness_type,
            drift_events=drift_events,
        )
    )


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
        tool="arif_vault_seal",
        mode=mode,
        seal_data=seal_data,
    )
