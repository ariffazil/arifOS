"""
arifosmcp/tools/reply_compose.py — 444r_REPLY
═════════════════════════════════════════════

Governed response compositor.
"""
from __future__ import annotations

from typing import Any

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.tools import _hold, _ok


def arif_reply_compose(
    mode: str = "compose",
    message: str | None = None,
    style: str | None = None,
    citations: list[str] | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_reply_compose", {"message": message or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_reply_compose", floor_check["reason"], floor_check["failed_floors"])

    if mode == "compose":
        return _ok("arif_reply_compose", {"message": message, "formatted": message, "tone": "neutral"})
    if mode == "format":
        return _ok("arif_reply_compose", {"message": message, "style": style or "markdown"})
    if mode == "nudge":
        return _ok("arif_reply_compose", {"message": message, "nudge": "Consider F5 (Peace) before acting."})
    if mode == "cite":
        return _ok("arif_reply_compose", {"message": message, "citations": citations or []})

    return _hold("arif_reply_compose", f"Unknown mode: {mode}")
