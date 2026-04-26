"""
VaultApp — 999 Immutable Ledger Surface
═══════════════════════════════════════
Real vault append and hash-chain integration for VAULT999.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

from arifosmcp.apps.vault_chain import append_vault_record, VAULT_PATH

VAULT999_DOMAIN = "https://arifosmcp.arif-fazil.com"


def _register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="vault_surface",
        description="999_VAULT ledger viewer and append surface",
    )
    def vault_surface(session_id: str = None) -> dict:
        """Surface-level vault viewer. Returns ledger stats and a test receipt."""
        from arifosmcp.apps.vault_chain import get_last_hash

        if VAULT_PATH.exists():
            text = VAULT_PATH.read_text().strip()
            lines = text.split("\n") if text else []
            ledger_size = len([l for l in lines if l.strip()])
            last_hash = get_last_hash()
        else:
            ledger_size = 0
            last_hash = "GENESIS"

        # Write a test entry to prove the chain works
        test_record = {
            "type": "vault_surface_ping",
            "note": "vault_surface called — ledger alive",
            "session_id": session_id or "anonymous",
        }
        result = append_vault_record(test_record)

        return {
            "status": "ok",
            "ledger_size": ledger_size,
            "last_hash": last_hash,
            "vault_receipt": result["vault_receipt"],
            "app": "vault_app",
        }

    @mcp.tool(
        name="vault_seal_record",
        description="999_VAULT — seal a record to the immutable ledger",
    )
    def vault_seal_record(record: dict, session_id: str = None) -> dict:
        """Append a permanent record to VAULT999.

        record: dict — the payload to seal (must be JSON-serializable)
        session_id: optional session context
        """
        from arifosmcp.apps.interceptor import intercept
        from arifosmcp.apps.surface_utils import envelope_error

        # Intercept dangerous tool call
        blocker = intercept("vault_seal_record", {"record": record}, session_id)
        if blocker:
            return blocker

        if not isinstance(record, dict):
            return envelope_error(
                tool_name="vault_seal_record",
                stage="VAULT",
                verdict="VOID",
                detail="record must be a JSON-serializable dict",
                session_id=session_id,
            )

        record["session_id"] = session_id or "anonymous"
        result = append_vault_record(record)
        return {
            "ok": True,
            "entry_id": result["entry_id"],
            "vault_receipt": result["vault_receipt"],
            "payload_hash": result["payload_hash"],
            "prev_hash": result["prev_hash"],
            "timestamp": result["timestamp"],
            "status": "SEAL",
            "app": "vault_app",
        }
