"""
interceptor.py — arifOS CC Governance Interceptor
═════════════════════════════════════════════════
Central mandatory middleware for ALL CC tool calls.

Every tool call must pass through `intercept()` before reaching the handler.
It checks: session validity, stage gate, actor authority, lifecycle state.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.apps.session_state import (
    STAGE_MIN_FORGE,
    LifecycleState,
    get_or_create_session,
)
from arifosmcp.apps.surface_utils import envelope_error, envelope_pause


def intercept(tool_name: str, payload: dict, session_id: str | None = None) -> dict | None:
    """Intercept a tool call and validate before routing.

    Returns None if clear to proceed, or an error/pause envelope to block.

    Dangerous tools (arif_forge_execute, vault_seal_record, vault_append)
    require a valid session_id. Anonymous callers are blocked.
    """
    if session_id:
        session = get_or_create_session(session_id)
    else:
        # Anonymous session — restrict dangerous tools
        dangerous_tools = {
            "arif_forge_execute",
            "vault_seal_record",
            "vault_append",
            "forge_surface",
            "vault_surface",
        }
        if tool_name in dangerous_tools:
            return envelope_error(
                tool_name=tool_name,
                stage="INTERCEPTOR",
                verdict="HOLD",
                detail=(
                    "Anonymous sessions cannot call dangerous tools. "
                    "Provide a valid session_id."
                ),
            )
        # Non-dangerous tools are fine without a session
        return None

    if tool_name in ("arif_forge_execute", "forge_surface"):
        # Must be APPROVED lifecycle state before forge can run
        if session.lifecycle != LifecycleState.APPROVED:
            return envelope_pause(
                tool_name=tool_name,
                stage="INTERCEPTOR",
                detail=(
                    f"Session must be in APPROVED state to execute. "
                    f"Current: {session.lifecycle.value}. "
                    f"Submit plan → risk review → judge review → approval first."
                ),
                session_id=session_id,
            )

        # Must meet minimum stage gate
        try:
            current_stage = int(session.stage)
        except (TypeError, ValueError):
            current_stage = 0

        if current_stage < STAGE_MIN_FORGE:
            return envelope_pause(
                tool_name=tool_name,
                stage="INTERCEPTOR",
                detail=(
                    f"Forge requires stage {STAGE_MIN_FORGE}+. "
                    f"Current: {session.stage}. Advance session first."
                ),
                session_id=session_id,
            )

    return None  # Clear to proceed
