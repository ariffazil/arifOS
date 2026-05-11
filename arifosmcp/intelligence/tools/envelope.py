from __future__ import annotations

from typing import Any


class _SessionManager:
    def get_session(self, session_id: str) -> dict[str, Any]:
        return {"session_id": session_id, "tool_calls": [], "trace": []}


session_manager = _SessionManager()


async def trace_replay(
    session_id: str,
    limit: int = 20,
    auth_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    session = session_manager.get_session(session_id) or {}
    return {
        "session_id": session_id,
        "limit": limit,
        "auth_context": auth_context,
        "trace": list(session.get("trace", []))[:limit],
        "tool_calls": list(session.get("tool_calls", []))[:limit],
    }
