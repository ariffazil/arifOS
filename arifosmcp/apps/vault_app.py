"""
VaultApp — 999 Immutable Ledger Surface
═══════════════════════════════════════
Read-only vault viewer and audit surface.
"""
from __future__ import annotations

from fastmcp import FastMCP


def _register(mcp: FastMCP) -> None:
    @mcp.tool(name="vault_surface", description="999_VAULT ledger viewer")
    def vault_surface() -> dict:
        return {"status": "locked", "ledger_size": 0, "last_audit": None}
