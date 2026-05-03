"""
arifosmcp/runtime/session_auth.py
═════════════════════════════════

Single F11 AUTH validator for all tools.
"""

import time

SESSION_TTL_SECONDS = 3600  # 1 hour


def validate_session(session_id: str | None, actor_id: str | None = None) -> dict:
    """
    Centralized F11 session validator.
    Returns: {"valid": bool, "session": dict|None, "reason": str, "actor_id": str|None, ...}
    """
    if not session_id:
        return {
            "valid": False,
            "session": None,
            "reason": "F11 AUTH: session_id missing",
            "actor_id": None,
        }

    from arifosmcp.runtime.tools import _SESSIONS

    sess = _SESSIONS.get(session_id)

    if not sess:
        return {
            "valid": False,
            "session": None,
            "reason": "F11 AUTH: session_id not found or expired",
            "received_session_id": session_id,
            "session_lookup": "not_found",
            "actor_id_received": actor_id,
            "validator": "F11_AUTH",
            "session_store": "in_memory_SESSIONS",
        }

    # TTL Check
    if time.time() > sess.get("expires_at_unix", float("inf")):
        return {
            "valid": False,
            "reason": "F11 AUTH: session expired",
            "expired": True,
            "created_at": sess.get("created_at"),
            "expires_at_unix": sess.get("expires_at_unix"),
            "ttl_seconds": SESSION_TTL_SECONDS,
            "validator": "F11_AUTH",
        }

    if actor_id and sess.get("actor_id") != actor_id:
        return {
            "valid": False,
            "session": sess,
            "reason": "F11 AUTH: actor_id mismatch",
            "actor_id_received": actor_id,
            "actor_id_on_session": sess.get("actor_id"),
        }

    return {
        "valid": True,
        "session": sess,
        "reason": "F11 AUTH: session valid",
        "actor_id": sess.get("actor_id"),
        "created_at": sess.get("created_at"),
        "stage": sess.get("stage"),
    }
