"""
arifosmcp/tools/session_init.py — 000_INIT
══════════════════════════════════════════

Constitutional session bootstrap + identity binding.
"""

from __future__ import annotations

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.tools import ARIF_DOCTRINE, _new_session
from arifosmcp.schemas.session import SessionManifest


def arif_session_init(
    mode: str = "init",
    actor_id: str | None = None,
    ack_irreversible: bool = False,
    session_id: str | None = None,
    declared_model_key: str | None = None,
    deployment_id: str = "vps_main_arifos",
) -> SessionManifest:
    if mode == "cleanup":
        from arifosmcp.runtime.session import list_active_sessions_count

        count_after = list_active_sessions_count()
        return SessionManifest(
            status="OK",
            result={"stale_swept": True, "active_count": count_after},
            doctrine=ARIF_DOCTRINE,
        )

    floor_check = check_floors(
        "arif_session_init",
        {"mode": mode, "ack_irreversible": ack_irreversible},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return SessionManifest(
            status="HOLD",
            result={},
            meta={
                "reason": floor_check["reason"],
                "failed_floors": floor_check.get("failed_floors", []),
            },
            doctrine=ARIF_DOCTRINE,
        )

    if mode == "init":
        sess = _new_session(
            actor_id, declared_model_key=declared_model_key, deployment_id=deployment_id
        )
        return SessionManifest(
            status="OK",
            result={"session": sess, "model_governance_card": sess.get("model_governance_card")},
            doctrine=ARIF_DOCTRINE,
        )

    if mode == "status":
        from arifosmcp.runtime.tools import _SESSIONS

        return SessionManifest(
            status="OK",
            result={"active_sessions": len(_SESSIONS), "version": "2026.04.26-KANON"},
            doctrine=ARIF_DOCTRINE,
        )

    if mode == "discover":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        return SessionManifest(
            status="OK",
            result={"canonical_tools": list(CANONICAL_TOOLS.keys())},
            doctrine=ARIF_DOCTRINE,
        )

    if mode == "handover":
        from arifosmcp.runtime.tools import _SESSIONS

        sess = _SESSIONS.get(session_id) if session_id else None
        return SessionManifest(
            status="OK",
            result={"session": sess, "handover": True},
            doctrine=ARIF_DOCTRINE,
        )

    if mode == "revoke":
        from arifosmcp.runtime.tools import _SESSIONS

        if session_id and session_id in _SESSIONS:
            del _SESSIONS[session_id]
            return SessionManifest(
                status="OK",
                result={"revoked": session_id},
                doctrine=ARIF_DOCTRINE,
            )
        return SessionManifest(
            status="HOLD",
            result={},
            meta={"reason": "session_id required for revoke"},
            doctrine=ARIF_DOCTRINE,
        )

    if mode == "refresh":
        from arifosmcp.runtime.tools import _SESSIONS, _now

        if session_id and session_id in _SESSIONS:
            _SESSIONS[session_id]["refreshed_at"] = _now()
            return SessionManifest(
                status="OK",
                result={"refreshed": session_id},
                doctrine=ARIF_DOCTRINE,
            )
        return SessionManifest(
            status="HOLD",
            result={},
            meta={"reason": "session_id required for refresh"},
            doctrine=ARIF_DOCTRINE,
        )

    return SessionManifest(
        status="HOLD",
        result={},
        meta={"reason": f"Unknown mode: {mode}"},
        doctrine=ARIF_DOCTRINE,
    )
