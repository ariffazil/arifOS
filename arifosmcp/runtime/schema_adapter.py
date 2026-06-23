"""
schema_adapter — MCP Schema Adapter Layer
===========================================
The kernel stays strict. The adapter absorbs human messiness.

Purpose:
  Normalize natural language and app-layer calls into canonical arifOS schema.
  Prevent "tool call failed because field name was wrong" — the #1 adoption killer.

Pattern:
  Human/agent input → schema_adapter.normalize() → canonical arifOS tool call → response

  The adapter:
    - Remaps common field name variations (query → question, scope → context)
    - Auto-injects session_id and actor_id if missing (with warning)
    - Validates only what's needed for THIS call, not the full schema
    - Returns human-readable errors: "You need to start a session first."

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ── Field Name Remappings ──────────────────────────────────────────────────

FIELD_REMAPPINGS: dict[str, dict[str, str]] = {
    # Common variations for 'query'
    "query": {
        "question": "query",
        "prompt": "query",
        "task": "query",
        "goal": "query",
        "request": "query",
        "what": "query",
        "ask": "query",
        "text": "query",
    },
    # Common variations for 'scope'
    "scope": {
        "domain": "scope",
        "area": "scope",
        "context": "scope",
        "namespace": "scope",
        "section": "scope",
        "range": "scope",
        "limit": "scope",
    },
    # Common variations for 'mode'
    "mode": {
        "type": "mode",
        "method": "mode",
        "approach": "mode",
        "variant": "mode",
        "style": "mode",
        "format": "mode",
    },
    # Common variations for 'session_id'
    "session_id": {
        "session": "session_id",
        "sid": "session_id",
        "token": "session_id",
        "conversation_id": "session_id",
        "thread_id": "session_id",
    },
    # Common variations for 'actor_id'
    "actor_id": {
        "actor": "actor_id",
        "agent": "actor_id",
        "user": "actor_id",
        "caller": "actor_id",
        "identity": "actor_id",
        "who": "actor_id",
    },
    # Common variations for 'intent'
    "intent": {
        "purpose": "intent",
        "reason": "intent",
        "objective": "intent",
        "aim": "intent",
        "goal": "intent",
    },
}


def normalize_field_name(key: str) -> str:
    """Map a field name to its canonical arifOS form."""
    lower_key = key.lower().strip()
    for canonical, aliases in FIELD_REMAPPINGS.items():
        if lower_key == canonical:
            return canonical
        if lower_key in aliases:
            return canonical
    return key  # No remapping found


def normalize_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Normalize all field names in a kwargs dict."""
    return {normalize_field_name(k): v for k, v in kwargs.items()}


# ── Session Auto-Injection ──────────────────────────────────────────────────


class SessionState:
    """Tracks session status for the adapter layer."""

    def __init__(self):
        self.active_session_id: str | None = None
        self.active_actor_id: str | None = None

    def is_active(self) -> bool:
        return self.active_session_id is not None

    def activate(self, session_id: str, actor_id: str):
        self.active_session_id = session_id
        self.active_actor_id = actor_id

    def clear(self):
        self.active_session_id = None
        self.active_actor_id = None


_session_state = SessionState()


def get_session_state() -> SessionState:
    return _session_state


# ── Adapter Entry Point ─────────────────────────────────────────────────────


class SchemaAdapterError(Exception):
    """Raised when the adapter cannot normalize the request."""

    def __init__(self, message: str, original_kwargs: dict | None = None):
        self.message = message
        self.original_kwargs = original_kwargs
        super().__init__(self.message)


def prepare_call(
    tool_name: str,
    kwargs: dict[str, Any],
    *,
    require_session: bool = False,
    accepted_fields: list[str] | None = None,
) -> dict[str, Any]:
    """Normalize and prepare a tool call.

    Args:
        tool_name: The canonical tool name.
        kwargs: Raw input kwargs (may contain non-canonical field names).
        require_session: If True, fail if no active session.
        accepted_fields: If provided, strip all kwargs not in this list.

    Returns:
        Normalized kwargs ready for the canonical tool.

    Raises:
        SchemaAdapterError: If the call cannot be prepared.
    """
    # Step 1: Normalize field names
    normalized = normalize_kwargs(kwargs)

    # Step 2: Auto-inject session context
    if _session_state.is_active():
        if "session_id" not in normalized:
            normalized["session_id"] = _session_state.active_session_id
        if "actor_id" not in normalized:
            normalized["actor_id"] = _session_state.active_actor_id

    # Step 3: Check session requirement
    if require_session and not _session_state.is_active():
        raise SchemaAdapterError(
            f"This call requires an active session. "
            f"Call 'arif_init' first with your actor_id. "
            f"Tool '{tool_name}' cannot proceed without session context.",
            original_kwargs=kwargs,
        )

    # Step 4: Filter to accepted fields if specified
    if accepted_fields:
        normalized = {k: v for k, v in normalized.items() if k in accepted_fields}

    return normalized


# ── Error Formatting ────────────────────────────────────────────────────────


def format_error(error: SchemaAdapterError) -> str:
    """Return a human-readable error message."""
    return (
        f"Schema Adapter Error: {error.message}\n"
        f"Original fields: {list(error.original_kwargs.keys()) if error.original_kwargs else 'N/A'}\n"
        f"Suggestion: Check field names or start a session with arif_init."
    )
