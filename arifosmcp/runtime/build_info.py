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
    if c := os.environ.get("GIT_COMMIT", "").strip():
        return c[:8]
    # Fallback: .git_commit file written by Makefile hot-restart
    for path in ("/usr/src/app/.git_commit", "/app/.git_commit"):
        try:
            with open(path) as f:
                return f.read().strip()[:8]
        except OSError:
            pass
    return "unknown"


def get_build_info() -> dict[str, Any]:
    """Return version and environment metadata — live timestamp on every call."""
    return {
        "version": release_version_label(),
        "commit": _resolve_commit(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "FORGED",
        "forge_date": "2026-04-06",
        "forge_word": "FORGE",
    }
