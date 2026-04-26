"""
Vault Audit App — 999_VAULT Ledger Viewer
══════════════════════════════════════════
Real VAULT999 ledger reader — reads and audits the immutable ledger.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

import json
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.apps import AppConfig

VAULT_PATH = Path("/root/VAULT999/outcomes.jsonl")
VAULT999_DOMAIN = "https://arifosmcp.arif-fazil.com"


def _register(mcp: FastMCP) -> None:
    app = AppConfig(
        domain=VAULT999_DOMAIN,
        visibility=["app", "model"],
    )

    @mcp.tool(
        name="arif_vault_audit",
        description="999_VAULT immutable ledger audit — read recent entries",
        app=app,
    )
    def arif_vault_audit(seal_id: str = None, limit: int = 10) -> dict:
        """Read entries from VAULT999 outcomes.jsonl.

        seal_id: optional — filter to a specific entry_id
        limit: number of recent entries to return (default 10)
        """
        if not VAULT_PATH.exists():
            return {
                "status": "empty",
                "entries": [],
                "ledger_size": 0,
                "app": "vault_audit",
            }

        text = VAULT_PATH.read_text().strip()
        if not text:
            return {
                "status": "empty",
                "entries": [],
                "ledger_size": 0,
                "app": "vault_audit",
            }

        lines = text.split("\n")
        all_entries = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                all_entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        total = len(all_entries)

        if seal_id:
            filtered = [e for e in all_entries if e.get("entry_id") == seal_id]
            entries = filtered[-limit:]
        else:
            entries = all_entries[-limit:]

        return {
            "status": "SEAL",
            "entries": entries,
            "ledger_size": total,
            "seal_id": seal_id,
            "returned": len(entries),
            "app": "vault_audit",
        }

    @mcp.tool(
        name="arif_vault_chain_verify",
        description="Verify VAULT999 hash chain integrity",
        app=app,
    )
    def arif_vault_chain_verify() -> dict:
        """Verify the hash chain integrity of VAULT999.

        Checks that each entry's prev_hash matches the previous entry's payload_hash.
        """
        if not VAULT_PATH.exists():
            return {"status": "error", "detail": "VAULT999 not found", "broken_at": None}

        text = VAULT_PATH.read_text().strip()
        if not text:
            return {"status": "SEAL", "detail": "empty vault — GENESIS", "verified": True}

        lines = [l for l in text.split("\n") if l.strip()]
        entries = []
        for line in lines:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        if not entries:
            return {"status": "SEAL", "detail": "empty vault", "verified": True}

        broken_at = None
        for i in range(1, len(entries)):
            expected_prev = entries[i - 1].get("payload_hash", "GENESIS")
            actual_prev = entries[i].get("prev_hash", "NONE")
            if expected_prev != actual_prev:
                broken_at = entries[i].get("entry_id", f"index_{i}")
                break

        return {
            "status": "VOID" if broken_at else "SEAL",
            "detail": "chain broken" if broken_at else "chain intact",
            "broken_at": broken_at,
            "total_entries": len(entries),
            "verified": broken_at is None,
            "app": "vault_audit",
        }
