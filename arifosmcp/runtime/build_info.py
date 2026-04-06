"""Build information for arifOS AAA MCP."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from .public_registry import release_version_label


@lru_cache(maxsize=1)
def _resolve_commit() -> str:
    """Resolve git commit SHA from env var (set by deployment), else 'unknown'."""
    # Primary: ARIFOS_BUILD_SHA (AF-FORGE deployment standard)
    if c := os.environ.get("ARIFOS_BUILD_SHA", "").strip():
        return c[:8]
    # Legacy: GIT_COMMIT
    if c := os.environ.get("GIT_COMMIT", "").strip():
        return c[:8]
    # Fallback: .git_commit file written by Makefile hot-restart
    for path in ("/usr/src/app/.git_commit", "/app/.git_commit", "/app/.git_commit"):
        try:
            with open(path) as f:
                return f.read().strip()[:8]
        except OSError:
            pass
    return "unknown"


def _resolve_build_time() -> str:
    """Resolve build time from env var, else current time."""
    return os.environ.get("ARIFOS_BUILD_TIME", datetime.now(timezone.utc).isoformat())


def _resolve_version() -> str:
    """Resolve version from env var, else from registry."""
    return os.environ.get("ARIFOS_APP_VERSION", release_version_label())


def _resolve_transport() -> str:
    """Resolve current transport mode."""
    return os.environ.get("ARIFOS_MCP_TRANSPORT", "streamable-http")


def get_build_info() -> dict[str, Any]:
    """Return version and environment metadata — live timestamp on every call."""
    return {
        "name": "arifOS MCP",
        "version": _resolve_version(),
        "commit": _resolve_commit(),
        "build_sha": _resolve_commit(),
        "build_time": _resolve_build_time(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "FORGED",
        "forge_date": "2026-04-06",
        "forge_word": "FORGE",
        "transport": _resolve_transport(),
    }
