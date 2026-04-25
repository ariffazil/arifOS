"""
arifosmcp/tools/vault_seal.py — 999_VAULT
═════════════════════════════════════════

Immutable ledger and audit engine.
"""
from __future__ import annotations

from arifosmcp.runtime.tools import _arif_vault_seal
from arifosmcp.schemas.verdict import SealOutput


def arif_vault_seal(
    mode: str = "seal",
    payload: str = "",
    session_id: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
) -> SealOutput:
    return SealOutput(
        **_arif_vault_seal(
            mode=mode,
            payload=payload,
            session_id=session_id,
            ack_irreversible=ack_irreversible,
            actor_id=actor_id,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
        )
    )
