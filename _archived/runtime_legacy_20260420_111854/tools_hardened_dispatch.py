"""
arifos/runtime/tools_hardened_dispatch.py — Canonical Dispatch Map
══════════════════════════════════════════════════════════════════════

Compatibility shim for the hardened dispatch layer. The current runtime
routes public traffic through `kernel.dispatch_with_fail_closed`, but
several megaTools and kernel helpers still import this historical module.

DITEMPA BUKAN DIBERI — Forged, Not Given
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
        from arifos.runtime.tools import FINAL_TOOL_IMPLEMENTATIONS

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


HARDENED_DISPATCH_MAP: MutableMapping[str, Any] = _LazyDispatchMap()


def get_dispatch_map() -> MutableMapping[str, Any]:
    """Compatibility accessor for callers that expect a function."""
    return HARDENED_DISPATCH_MAP


async def dispatch_with_fail_closed(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Delegate to the canonical kernel fail-closed gateway."""
    from arifos.runtime.kernel import kernel

    return await kernel.dispatch_with_fail_closed(tool_name, arguments)


def get_tool_handler(name: str) -> Any:
    """Resolve tool handlers through the canonical runtime registry."""
    from arifos.runtime.tools import get_tool_handler as _get_tool_handler

    return _get_tool_handler(name)


def get_shadow_backends() -> dict[str, Any]:
    """Shadow comparison is optional; default to no alternate backends."""
    return {}
