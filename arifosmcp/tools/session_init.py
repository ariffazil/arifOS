"""
arifosmcp/tools/session_init.py — 000_INIT
══════════════════════════════════════════

Constitutional session bootstrap + identity binding.
"""
from __future__ import annotations

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.tools import _hold, _new_session, _ok
from arifosmcp.schemas.session import SessionManifest


def arif_session_init(
    mode: str = "init",
    actor_id: str | None = None,
    ack_irreversible: bool = False,
    session_id: str | None = None,
) -> SessionManifest:
    floor_check = check_floors(
        "arif_session_init",
        {"mode": mode, "ack_irreversible": ack_irreversible},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return SessionManifest(
            **_hold("arif_session_init", floor_check["reason"], floor_check["failed_floors"])
        )

    if mode == "init":
        sess = _new_session(actor_id)
        return SessionManifest(**_ok("arif_session_init", {"session": sess}))

    if mode == "status":
        from arifosmcp.runtime.tools import _SESSIONS
        return SessionManifest(
            **_ok("arif_session_init", {"active_sessions": len(_SESSIONS), "version": "2026.04.24-KANON"})
        )

    if mode == "discover":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
        return SessionManifest(
            **_ok("arif_session_init", {"canonical_tools": list(CANONICAL_TOOLS.keys())})
        )

    if mode == "handover":
        from arifosmcp.runtime.tools import _SESSIONS
        sess = _SESSIONS.get(session_id) if session_id else None
        return SessionManifest(**_ok("arif_session_init", {"session": sess, "handover": True}))

    if mode == "revoke":
        from arifosmcp.runtime.tools import _SESSIONS
        if session_id and session_id in _SESSIONS:
            del _SESSIONS[session_id]
            return SessionManifest(**_ok("arif_session_init", {"revoked": session_id}))
        return SessionManifest(**_hold("arif_session_init", "session_id required for revoke"))

    if mode == "refresh":
        from arifosmcp.runtime.tools import _SESSIONS, _now
        if session_id and session_id in _SESSIONS:
            _SESSIONS[session_id]["refreshed_at"] = _now()
            return SessionManifest(**_ok("arif_session_init", {"refreshed": session_id}))
        return SessionManifest(**_hold("arif_session_init", "session_id required for refresh"))

    return SessionManifest(**_hold("arif_session_init", f"Unknown mode: {mode}"))
