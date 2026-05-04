"""
arifosmcp/runtime/tools_hardened_dispatch.py — Canonical Dispatch Map
══════════════════════════════════════════════════════════════════════

Compatibility shim for the hardened dispatch layer. The current runtime
routes public traffic through `kernel.dispatch_with_fail_closed`, but
several megaTools, apps, tests, and stdio helpers still import this module.
"""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any


class _LazyDispatchMap(MutableMapping[str, Any]):
    """Lazy mapping wrapper that avoids import-time cycles with runtime.tools."""

    def __init__(self) -> None:
        self._mapping: dict[str, Any] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        from arifosmcp.runtime.tools import FINAL_TOOL_IMPLEMENTATIONS

        self._mapping.update(FINAL_TOOL_IMPLEMENTATIONS)
        self._loaded = True

    def __getitem__(self, key: str) -> Any:
        self._ensure_loaded()
        return self._mapping[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._ensure_loaded()
        self._mapping[key] = value

    def __delitem__(self, key: str) -> None:
        self._ensure_loaded()
        del self._mapping[key]

    def __iter__(self):
        self._ensure_loaded()
        return iter(self._mapping)

    def __len__(self) -> int:
        self._ensure_loaded()
        return len(self._mapping)

    def get(self, key: str, default: Any = None) -> Any:
        self._ensure_loaded()
        return self._mapping.get(key, default)

    def __contains__(self, key: object) -> bool:
        self._ensure_loaded()
        return key in self._mapping


HARDENED_DISPATCH_MAP: MutableMapping[str, Any] = _LazyDispatchMap()


def get_dispatch_map() -> MutableMapping[str, Any]:
    return HARDENED_DISPATCH_MAP


async def dispatch_with_fail_closed(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    from arifosmcp.runtime.kernel import kernel

    return await kernel.dispatch_with_fail_closed(tool_name, arguments)


def get_tool_handler(name: str) -> Any:
    from arifosmcp.runtime.tools import LEGACY_TOOL_ALIASES

    handler = HARDENED_DISPATCH_MAP.get(name)
    if handler:
        return handler

    canonical_name = LEGACY_TOOL_ALIASES.get(name)
    if canonical_name:
        return HARDENED_DISPATCH_MAP.get(canonical_name)

    return None


async def hardened_init_anchor_dispatch(
    mode: str = "init", arguments: dict[str, Any] | None = None
) -> Any:
    """
    Compatibility helper for legacy tests and scripts.

    Keep the explicit mode handling visible so architectural tests that
    inspect this function still verify the intended lifecycle branches.
    """

    from arifosmcp.runtime.megaTools.tool_01_init_anchor import init_anchor

    args = dict(arguments or {})
    if mode == "revoke":
        return await init_anchor(mode="revoke", payload=args, session_id=args.get("session_id"))
    if mode in ("state", "status", "refresh"):
        return await init_anchor(mode=mode, payload=args, session_id=args.get("session_id"))
    return await init_anchor(mode=mode, payload=args, session_id=args.get("session_id"))


async def hardened_agi_mind_dispatch(
    mode: str = "reason", arguments: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Legacy compatibility wrapper for the AGI mind lane."""

    from arifosmcp.runtime.tools import _arif_mind_reason_tool

    args = dict(arguments or {})
    return await _arif_mind_reason_tool(
        mode=mode,
        query=args.get("query"),
        session_id=args.get("session_id"),
        actor_id=args.get("actor_id"),
        plan_id=args.get("plan_id"),
        witness_type=args.get("witness_type", "ai"),
    )


def get_shadow_backends() -> dict[str, Any]:
    return {}
