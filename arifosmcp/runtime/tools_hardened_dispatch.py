"""Compatibility dispatch surface for historical runtime imports.

The canonical runtime now routes through `arifosmcp.runtime.tools`, but a
number of stdio, bridge, and audit paths still import this module directly.
Keep it as a thin compatibility layer over the live implementations.
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


async def dispatch_with_fail_closed(
    tool_name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
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


def hardened_init_anchor_dispatch(
    mode: str = "status", **kwargs: Any
) -> dict[str, Any]:
    """Compatibility wrapper that keeps the legacy init-anchor mode vocabulary visible."""
    from arifosmcp.runtime.tools import _arif_session_init

    if mode == "revoke":
        return {
            "status": "HOLD",
            "tool": "init_anchor",
            "meta": {
                "reason": "Legacy revoke mode retired; use epoch_seal + sovereign review."
            },
        }

    if mode in ("state", "status", "refresh"):
        return _arif_session_init(mode="validate", **kwargs)

    return _arif_session_init(mode=mode, **kwargs)


def hardened_agi_mind_dispatch(**kwargs: Any) -> Any:
    from arifosmcp.runtime.tools import _arif_mind_reason

    return _arif_mind_reason(**kwargs)


def get_shadow_backends() -> dict[str, Any]:
    return {}
