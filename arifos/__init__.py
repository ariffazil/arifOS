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
from importlib.metadata import version as _pkg_version, PackageNotFoundError as _PkgNotFound

# __version__ is DERIVED from installed package metadata (single source of truth: pyproject.toml).
# Hardcoded string here served "2026.07.17" while the wheel said "1!2026.9.6" — same drift class
# the arifosmcp/__init__.py fix landed. F13 directive 2026-09-30: kill the drift class at the root.
try:
    __version__ = _pkg_version("arifos")
except _PkgNotFound:  # source tree without installed distribution
    __version__ = "0.0.0.dev0"

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
