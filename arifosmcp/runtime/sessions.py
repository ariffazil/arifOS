"""
arifosmcp/runtime/sessions.py — Session Continuity State

Centralized session registry for arifOS runtime.
Single source of truth for session → identity binding.

DITEMPA BUKAN DIBERI — Forged, Not Given

SECURITY HARDENING (Zero-Day Mitigation):
- Strict sovereign identity map: explicit verified identities only
- No guessable aliases (e.g., "arif" not promoted to "ariffazil")
- Identity trust precedence: verified token > signed session > explicit admin map > anonymous
"""

import re
import uuid
from typing import Any

from core.shared.types import ActorIdentity

# Global Session Registry (In-memory fallback for stateless bridge)
_ACTOR_IDENTITIES: dict[str, ActorIdentity] = {}
_ACTOR_SESSION_MAP: dict[str, str] = {}  # session_id -> actor_id
_ACTIVE_SESSION_ID: str | None = None
_SESSION_CONTINUITY_STATE: dict[str, dict[str, Any]] = {}

# ── Sovereign Identity Map ─────────────────────────────────────────────────
# Explicit verified identities only — no guessable aliases
# Blind spot 3 amendment: moved from hardcoded function logic to explicit map
_SOVEREIGN_IDENTITY_MAP: dict[str, str] = {
    "ariffazil": "ariffazil",
}
_VALID_ACTOR_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{1,64}$")

# ── Session Identity Storage ──────────────────────────────────────────────
# Stores the resolved identity for each anchored session.
# This is the canonical binding: session_id → {actor_id, authority_level, auth_context, ...}
_SESSION_IDENTITY: dict[str, dict[str, Any]] = {}


def _resolve_session_id(provided_id: str | None) -> str | None:
    """Resolve session_id from provided input or last active session."""
    if provided_id and str(provided_id).strip():
        return provided_id
    return _ACTIVE_SESSION_ID


def set_active_session(session_id: str) -> None:
    """Update the global pointer for the last active session."""
    global _ACTIVE_SESSION_ID
    _ACTIVE_SESSION_ID = session_id


def bind_session_identity(
    session_id: str,
    actor_id: str,
    authority_level: str,
    auth_context: dict[str, Any],
    approval_scope: list[str] | None = None,
    human_approval: bool = False,
    caller_state: str | None = None,
    constitutional_context: str | None = None,
) -> None:
    """
    Bind a verified identity to a session. Called after successful init_anchor.

    This is the canonical write: after this call, get_session_identity(session_id)
    will return the stored identity instead of anonymous defaults.
    """
    _SESSION_IDENTITY[session_id] = {
        "actor_id": actor_id,
        "authority_level": authority_level,
        "auth_context": auth_context,
        "approval_scope": approval_scope or [],
        "caller_state": caller_state or "anchored",
        "human_approval": human_approval,
        "constitutional_context": constitutional_context,
    }
    _ACTOR_SESSION_MAP[session_id] = actor_id


def get_session_identity(session_id: str) -> dict[str, Any] | None:
    """
    Retrieve the stored identity for a session.

    Returns None if the session has not been anchored via init_anchor.
    """
    return _SESSION_IDENTITY.get(session_id)


def clear_session_identity(session_id: str) -> None:
    """Remove stored identity for a session (e.g., on revocation)."""
    _SESSION_IDENTITY.pop(session_id, None)
    _ACTOR_SESSION_MAP.pop(session_id, None)
    _SESSION_CONTINUITY_STATE.pop(session_id, None)


def list_active_sessions_count() -> int:
    """Return the total number of currently anchored sessions."""
    return len(_SESSION_IDENTITY)


def get_session_continuity_state(session_id: str | None) -> dict[str, Any] | None:
    """Return canonical continuity state for a session if present."""
    if not session_id:
        return None
    return _SESSION_CONTINUITY_STATE.get(session_id)


def set_session_continuity_state(session_id: str, state: dict[str, Any]) -> None:
    """Persist canonical continuity state for a session."""
    _SESSION_CONTINUITY_STATE[session_id] = state


# ── Session Truth Resolution ──────────────────────────────────────────────
# F2 Truth: Single canonical resolution of session + identity continuity.
# Identity Trust Chain (strict precedence per Zero-Day hardening):
#   1. verified token identity (auth_context.session_id)
#   2. signed trusted session identity (anchored session state)
#   3. explicit admin-approved mapping (SOVEREIGN_IDENTITY_MAP)
#   4. otherwise anonymous / denied
# No transport-provided actor string outranks verified identity.


def resolve_runtime_context(
    incoming_session_id: str | None,
    auth_context: dict[str, Any] | None,
    actor_id: str | None,
    declared_name: str | None,
) -> dict[str, Any]:
    """
    Canonical resolution of session and identity truth.

    Returns unified context with explicit separation of:
    - transport_session_id: raw incoming value (for debugging)
    - resolved_session_id: canonical continuity-verified truth
    - canonical_actor_id: authority-bearing identity
    - display_name: human-readable only
    - authority_source: provenance for audit
    """
    # Identity precedence: actor_id > declared_name > anonymous
    canonical_actor_id = _resolve_canonical_actor(actor_id, declared_name)

    # Transport session: raw incoming value, may be "global"
    transport_session_id = incoming_session_id or "global"

    # Session resolution with precedence
    resolved_session_id: str = transport_session_id
    authority_source: str = "fallback"

    # 1. auth_context.session_id (verified token)
    if auth_context and auth_context.get("session_id"):
        resolved_session_id = auth_context["session_id"]
        authority_source = "token"
    # 2. Anchored session state for this actor
    elif transport_session_id != "global" and get_session_identity(transport_session_id):
        resolved_session_id = transport_session_id
        authority_source = "session"
    # 3. Check if actor has any anchored session
    elif canonical_actor_id != "anonymous":
        # Find session by actor mapping
        for sid, aid in _ACTOR_SESSION_MAP.items():
            if aid == canonical_actor_id:
                resolved_session_id = sid
                authority_source = "session"
                break

    # Display name is presentation-only
    display_name = declared_name or actor_id or "anonymous"

    # F2 Truth: Single canonical session_id — unified truth across all surfaces
    unified_session_id = resolved_session_id

    return {
        "session_id": unified_session_id,  # ← Canonical single truth (NEW)
        "resolved_session_id": unified_session_id,  # ← Same value, explicit redundancy
        "transport_session_id": transport_session_id,  # ← Debug/audit only
        "canonical_actor_id": canonical_actor_id,
        "display_name": display_name,
        "authority_source": authority_source,
        "_invariant": "session_id == resolved_session_id",  # ← Enforced
    }


def _resolve_canonical_actor(actor_id: str | None, declared_name: str | None) -> str:
    """
    Identity precedence: actor_id > declared_name > anonymous.
    Strict sovereign protection: uses SOVEREIGN_IDENTITY_MAP for verified identities.
    No guessable aliases like "arif" are promoted to "ariffazil" at this layer.
    Identity verification happens in governance layers (F11/F13).
    """
    # Normalize inputs
    aid = (actor_id or "").strip()
    dname = (declared_name or "").strip()

    # Strict pattern validation — reject malformed actor_id before any processing
    if aid and not _VALID_ACTOR_ID_PATTERN.match(aid):
        aid = ""
    if dname and not _VALID_ACTOR_ID_PATTERN.match(dname):
        dname = ""

    aid_normalized = aid.lower().replace("_", "-") if aid else ""
    dname_normalized = dname.lower().replace("_", "-") if dname else ""

    # Precedence: actor_id first
    if aid_normalized and aid_normalized != "anonymous":
        # Check sovereign identity map first — explicit verified identities only
        if aid_normalized in _SOVEREIGN_IDENTITY_MAP:
            return _SOVEREIGN_IDENTITY_MAP[aid_normalized]
        return aid  # Return original case-preserved form if valid

    # Fallback: declared_name (normalized)
    if dname_normalized and dname_normalized != "anonymous":
        # Check sovereign identity map — explicit verified identities only
        if dname_normalized in _SOVEREIGN_IDENTITY_MAP:
            return _SOVEREIGN_IDENTITY_MAP[dname_normalized]
        return dname  # Return original case-preserved form if valid

    return "anonymous"


def _normalize_session_id(session_id: str | None) -> str:
    """Normalize session ID - create new if not provided.

    This is the single source of truth for session ID normalization.
    Moved from tools.py to avoid circular imports.
    """
    resolved = _resolve_session_id(session_id)
    if resolved and str(resolved).strip():
        return str(resolved).strip()
    minted = f"session-{uuid.uuid4().hex[:8]}"
    set_active_session(minted)
    return minted
