"""
arifosmcp/apps/charters/__init__.py
Canonical MCP App charters for the 5 core arifOS governance apps.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

_CHARTER_DIR = pathlib.Path(__file__).parent


def load_charter(app_id: str) -> dict[str, Any] | None:
    """Load an app charter by app_id."""
    path = _CHARTER_DIR / f"{app_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def list_charters() -> list[str]:
    """List all available charter app_ids."""
    return sorted([p.stem for p in _CHARTER_DIR.glob("*.json")])


__all__ = ["load_charter", "list_charters"]
