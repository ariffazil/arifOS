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
Binding:    pending L11 actor verification

This is a stub. The live session manifest is maintained by
the runtime session manager and bound to the canonical
arif_session_init → arif_vault_seal lifecycle.
"""


def register_session(mcp: FastMCP) -> list[str]:
    """Register arifos://session/{id} — Ephemeral Instance."""

    @mcp.resource(
        uri="arifos://session/{id}",
        description=(
            "Ephemeral session manifest for a specific session ID. "
            "Returns the live session binding status, actor verification state, "
            "and constitutional fingerprint. Updated as the session progresses "
            "through the init→vault lifecycle. Use to inspect session health remotely."
        ),
    )
    def session_resource(id: str) -> str:
        return SESSION_STUB_TEXT.format(session_id=id)

    return ["arifos://session/{id}"]
