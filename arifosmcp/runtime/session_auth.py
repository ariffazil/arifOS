"""
arifosmcp/runtime/session_auth.py
═════════════════════════════════

Single F11 AUTH validator for all tools.
"""

import time

SESSION_TTL_SECONDS = 3600  # 1 hour
SESSION_GRACE_SECONDS = 300  # 5 min grace period after TTL


def validate_session(session_id: str | None, actor_id: str | None = None) -> dict:
    """
    Centralized F11 session validator.
    Falls back to persisted session store if in-memory _SESSIONS miss.
    Auto-refreshes TTL on valid validation to improve continuity.
    Returns: {"valid": bool, "session": dict|None, "reason": str, "actor_id": str|None, ...}
    """
    if not session_id:
        return {
            "valid": False,
            "session": None,
            "reason": "F11 AUTH: session_id missing",
            "actor_id": None,
        }

    # ── 1. In-memory lookup (fast path) ───────────────────────────────────────
    from arifosmcp.runtime.tools import _SESSIONS

    sess = _SESSIONS.get(session_id)

    # ── 2. Persisted store fallback ───────────────────────────────────────────
    if sess is None:
        try:
            from arifosmcp.runtime.session import _ensure_active_record

            persisted = _ensure_active_record(session_id)
            if persisted:
                # Rehydrate into in-memory store for continuity
                sess = {
                    "session_id": session_id,
                    "actor_id": persisted.get("actor_id", "anonymous"),
                    "created_at": persisted.get("created_at", ""),
                    "created_at_unix": persisted.get("created_at_unix", 0.0),
                    "expires_at_unix": persisted.get("expires_at_unix", float("inf")),
                    "stage": persisted.get("stage", "000"),
                    "lane": persisted.get("lane", "AGI"),
                    "entropy_delta": 0.0,
                    "sealed": False,
                    "trace_packet": persisted.get("trace_packet", {}),
                    "session_warnings": persisted.get("session_warnings", []),
                    "agent_card": persisted.get("agent_card", {}),
                    "model_governance_card": persisted.get("model_governance_card", {}),
                    "constitution_bound": persisted.get("constitution_bound", True),
                    "signature_verified": persisted.get("signature_verified", False),
                }
                _SESSIONS[session_id] = sess
        except Exception:
            pass

    if not sess:
        return {
            "valid": False,
            "session": None,
            "reason": "F11 AUTH: session_id not found or expired",
            "received_session_id": session_id,
            "session_lookup": "not_found",
            "actor_id_received": actor_id,
            "validator": "F11_AUTH",
            "session_store": "in_memory_and_persisted",
        }

    # ── 3. TTL Check with grace period ────────────────────────────────────────
    expires_at = sess.get("expires_at_unix", float("inf"))
    now = time.time()
    if now > expires_at + SESSION_GRACE_SECONDS:
        return {
            "valid": False,
            "reason": "F11 AUTH: session expired (24h limit + grace exceeded)",
            "expired": True,
            "created_at": sess.get("created_at"),
            "expires_at_unix": expires_at,
            "ttl_seconds": SESSION_TTL_SECONDS,
            "grace_seconds": SESSION_GRACE_SECONDS,
            "validator": "F11_AUTH",
        }

    # ── 4. Actor ID mismatch ──────────────────────────────────────────────────
    if actor_id and sess.get("actor_id") != actor_id:
        return {
            "valid": False,
            "session": sess,
            "reason": "F11 AUTH: actor_id mismatch",
            "actor_id_received": actor_id,
            "actor_id_on_session": sess.get("actor_id"),
        }

    # ── 5. TTL refresh (continuity improvement) ───────────────────────────────
    if now > expires_at - (SESSION_TTL_SECONDS // 2):
        # Session is past half-life: refresh TTL
        new_expires = now + SESSION_TTL_SECONDS
        sess["expires_at_unix"] = new_expires
        try:
            from arifosmcp.runtime.session import _touch_record

            _touch_record(session_id, {"expires_at_unix": new_expires})
        except Exception:
            pass

    return {
        "valid": True,
        "session": sess,
        "reason": "F11 AUTH: session valid",
        "actor_id": sess.get("actor_id"),
        "created_at": sess.get("created_at"),
        "stage": sess.get("stage"),
    }
