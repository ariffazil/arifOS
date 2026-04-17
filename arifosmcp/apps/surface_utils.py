"""
arifosmcp/apps/surface_utils.py
═══════════════════════════════════════════════════════════════════════════════
Shared utilities for arifOS MCP surface apps.

Provides:
  - normalize_state()   — force any state object into a plain serializable dict
  - safe_get()         — safe field access (handles StateProxy, dict, object attrs)
  - envelope_error()   — fully-structured error envelope with all required fields

P0 fixes: StateProxy subscript bug, missing stage in error paths,
session propagation for stateful surfaces.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


def normalize_state(state: Any) -> dict[str, Any]:
    """Force any state object into a plain serializable dict.

    Handles: None, dict, Pydantic models, StateProxy, attrs objects,
    and any object with a dict-like interface.

    Use this BEFORE any surface code accesses state fields.
    """
    if state is None:
        return {}
    if isinstance(state, dict):
        return dict(state)
    if hasattr(state, "model_dump"):
        return state.model_dump()
    if hasattr(state, "dict"):
        return state.dict()
    if hasattr(state, "__dict__"):
        return {k: v for k, v in state.__dict__.items() if not k.startswith("_")}
    return {
        k: getattr(state, k, None)
        for k in dir(state)
        if not k.startswith("_") and not callable(getattr(state, k, None))
    }


def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """Safe field access that handles StateProxy, dict, and object attrs.

    Replaces direct dict-style access like state["session_id"] which crashes
    when state is a StateProxy or non-subscriptable object.
    """
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    if isinstance(obj, dict):
        return obj.get(key, default)
    if hasattr(obj, key):
        return getattr(obj, key, default)
    return default


def envelope_error(
    tool_name: str,
    stage: str,
    verdict: str = "VOID",
    detail: str = "",
    session_id: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """Return a fully-structured error envelope with all required fields.

    Every surface tool error response MUST include:
      - ok: bool
      - canonical_tool_name: str
      - execution_status: str  ("ERROR" | "SUCCESS" | "PAUSE")
      - status: str
      - verdict: str
      - stage: str
      - timestamp: str

    Using this helper prevents the '_StateProxy object is not subscriptable'
    crash and ensures diagnostics and UI surfaces get parseable responses.
    """
    return {
        "ok": False,
        "canonical_tool_name": tool_name,
        "execution_status": "ERROR",
        "status": "ERROR",
        "verdict": verdict,
        "stage": stage,
        "detail": detail,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **extra,
    }


def envelope_pause(
    tool_name: str,
    stage: str,
    detail: str = "",
    session_id: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """Return a PAUSE envelope — session not hydrated or precondition not met.

    Used when a stateful surface is called without a resolved session.
    Differs from envelope_error in that this is an expected precondition
    failure, not an exception.
    """
    return {
        "ok": False,
        "canonical_tool_name": tool_name,
        "execution_status": "PAUSE",
        "status": "PAUSE",
        "verdict": "PAUSE",
        "stage": stage,
        "detail": detail,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **extra,
    }
