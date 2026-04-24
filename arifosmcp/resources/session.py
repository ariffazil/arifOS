"""
arifos://session/{id} — Ephemeral Instance
═══════════════════════════════════════════
Dynamic resource template for per-session manifest retrieval.
"""
from __future__ import annotations

from fastmcp import FastMCP


SESSION_STUB_TEXT = """\
arifOS Session Manifest
═══════════════════════
Session ID: {session_id}
Status:     ephemeral
Binding:    pending F11 actor verification

This is a stub. The live session manifest is maintained by
the runtime session manager and bound to the canonical
arif_session_init → arif_vault_seal lifecycle.
"""


def register_session(mcp: FastMCP) -> list[str]:
    """Register arifos://session/{id} — Ephemeral Instance."""

    @mcp.resource(uri="arifos://session/{id}")
    def session_resource(id: str) -> str:
        return SESSION_STUB_TEXT.format(session_id=id)

    return ["arifos://session/{id}"]
