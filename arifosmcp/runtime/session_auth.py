"""
arifosmcp/runtime/session_auth.py
════════════════════════════════

Single F11 AUTH validator for all tools.
"""

import os
import time

SESSION_TTL_SECONDS = 3600  # 1 hour
SESSION_GRACE_SECONDS = 300  # 5 min grace period after TTL


def _get_env_actor() -> str | None:
    """Fall back to env var for auto-ID when MCP client doesn't pass actor_id."""
    return os.getenv("ARIFOS_ACTOR_ID") or os.getenv("ARIFOS_DEFAULT_ACTOR_ID")


def _get_env_session() -> str | None:
    """Fall back to env var for auto-session when MCP client doesn't pass session_id."""
    return os.getenv("ARIFOS_SESSION_ID") or os.getenv("ARIFOS_DEFAULT_SESSION_ID")


def validate_session(session_id: str | None, actor_id: str | None = None) -> dict:
    """
    Centralized F11 session validator.
    Falls back to persisted session store if in-memory _SESSIONS miss.
    Auto-refreshes TTL on valid validation to improve continuity.

    Auto-ID: if session_id or actor_id is None AND the corresponding
    env var (ARIFOS_SESSION_ID / ARIFOS_ACTOR_ID) is set, use it.
    This enables autonomous governance when MCP clients don't pass IDs.

    Returns: {"valid": bool, "session": dict|None, "reason": str, "actor_id": str|None, ...}
    """
    # ── Auto-ID: env var fallback for autonomous governance ───────────────────
    if not session_id:
        session_id = _get_env_session()
    if not actor_id:
        actor_id = _get_env_actor()

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
        # ── 2b. Auto-bootstrap: env var session with no prior record ────────────
        # If session_id came from env vars (ARIFOS_SESSION_ID / ARIFOS_DEFAULT_SESSION_ID)
        # AND actor_id came from env vars, the deployer explicitly configured this
        # autonomous governance context. Create the session now rather than failing —
        # this is the intended sovereign bootstrap path for container-to-container MCP.
        env_session_id = _get_env_session()
        env_actor_id = _get_env_actor()
        auto_bootstrapped = (
            session_id == env_session_id  # session_id was sourced from env
            and env_actor_id  # and we also have an env actor_id
        )
        if auto_bootstrapped:
            try:
                from arifosmcp.runtime.session import bind_session_identity

                bind_session_identity(
                    session_id=session_id,
                    actor_id=env_actor_id or "anonymous",
                    authority_level=(
                        "sovereign"
                        if env_actor_id == "arif"
                        else ("operator" if env_actor_id == "a-forge" else "anonymous")
                    ),
                    auth_context={
                        "source": "validate_session",
                        "mode": "auto_bootstrap",
                        "via": "env_var_fallback",
                    },
                    stage="000",
                    governance={"verdict": "SEAL", "trace_packet": None},
                )
                # Re-fetch the freshly created session
                try:
                    from arifosmcp.runtime.session import _ensure_active_record

                    persisted = _ensure_active_record(session_id)
                    if persisted:
                        sess = {
                            "session_id": session_id,
                            "actor_id": persisted.get("actor_id", env_actor_id),
                            "created_at": persisted.get("created_at", ""),
                            "created_at_unix": persisted.get("created_at_unix", time.time()),
                            "expires_at_unix": (
                                persisted.get("expires_at_unix", time.time() + SESSION_TTL_SECONDS)
                            ),
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
                        from arifosmcp.runtime.tools import _SESSIONS

                        _SESSIONS[session_id] = sess
                except Exception:
                    pass
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
                "validator": "F11_AUDIT",
                "session_store": "in_memory_and_persisted",
                "auto_bootstrap_attempted": auto_bootstrapped,
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
            "validator": "F11_AUDIT",
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
