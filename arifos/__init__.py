"""arifos — federation namespace package.

Phase 2 bridge: the kernel runtime still lives in ``arifosmcp``.
This namespace exposes federation thin clients:

- ``arifos.forge`` — MCP HTTP client → A-FORGE gateway (:7072/mcp)
- ``arifos.aaa``   — A2A JSON-RPC client → AAA gateway (:3001/a2a)

Unknown attributes fall through to ``arifosmcp`` so ``arifos.abi`` etc.
resolve to the kernel package until the Phase 3 rename lands.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import importlib

__version__ = "2026.07.17"

_LOCAL_SUBMODULES = {"forge", "aaa"}


def __getattr__(name: str):
    if name.startswith("_"):
        raise AttributeError(name)
    if name in _LOCAL_SUBMODULES:
        return importlib.import_module(f"arifos.{name}")
    try:
        return importlib.import_module(f"arifosmcp.{name}")
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise AttributeError(f"module 'arifos' has no attribute {name!r}") from exc
