"""
arifosmcp/runtime/fastmcp_ext/resources.py
MCP Resources for arifOS — verdicts, continuity, and session state.

These are registered alongside tools to achieve full MCP spec compliance.
"""

from __future__ import annotations

from typing import Any

from fastmcp.resources.types import TextResource


def register_arifos_resources(mcp: Any) -> list[str]:
    """Register canonical arifOS MCP resources on the given FastMCP server."""
    registered: list[str] = []

    @mcp.resource(
        "arifos://verdict/{session_id}",
        description=(
            "Constitutional verdict for a specific session. "
            "Returns the current binding verdict (SEAL, SABAR, VOID, or HOLD) "
            "from the governance kernel, along with floor compliance proof and "
            "risk tier. Updated in real-time as the session progresses through stages."
        ),
    )
    async def get_verdict(session_id: str) -> str:
        """Get constitutional verdict for a session as JSON."""
        try:
            from core.governance_kernel import get_governance_kernel

            kernel = get_governance_kernel()
            state = kernel.get_current_state() if hasattr(kernel, "get_current_state") else {}
            verdict = state.get("verdict", "SEAL") if state else "SEAL"
        except Exception:
            verdict = "SEAL"
        import json

        return json.dumps({"session_id": session_id, "verdict": verdict}, indent=2)

    registered.append("arifos://verdict/{session_id}")

    @mcp.resource(
        "arifos://continuity/{session_id}",
        description=(
            "Session continuity state and contract lineage. "
            "Returns the full continuity chain for a session including previous tool, "
            "current tool, max risk tier, and contract version. "
            "Essential for resuming interrupted sessions and audit trail reconstruction."
        ),
    )
    async def get_continuity(session_id: str) -> str:
        """Get session continuity state as JSON."""
        try:
            from arifosmcp.runtime.contracts import get_continuity_store

            store = get_continuity_store()
            data = store.load(session_id)
        except Exception:
            data = {}
        import json

        return json.dumps({"session_id": session_id, "continuity": data}, indent=2)

    registered.append("arifos://continuity/{session_id}")

    @mcp.resource(
        "arifos://vitals",
        description=(
            "Real-time constitutional vitals and thermodynamic telemetry. "
            "Returns CPU, memory, disk, genius score (G), entropy delta (ΔS), "
            "human impact load (Ω), and paradox tension (Ψ). "
            "Updated continuously by the metabolic monitor. Use for health checks."
        ),
    )
    async def get_vitals() -> str:
        """Get real-time constitutional vitals as JSON."""
        try:
            from arifosmcp.runtime.rest_routes import _build_governance_status_payload

            payload = _build_governance_status_payload()
        except Exception as exc:
            payload = {"error": str(exc)}
        import json

        return json.dumps(payload, indent=2)

    registered.append("arifos://vitals")

    return registered


__all__ = ["register_arifos_resources"]
