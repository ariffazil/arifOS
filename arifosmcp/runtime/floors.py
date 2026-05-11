"""
arifOS/arifosmcp/runtime/floors.py — Constitutional Floor Registry
═══════════════════════════════════════════════════════════════

Single source of truth for active floors and governance counts.
"""

from __future__ import annotations

from typing import Any

ACTIVE_FLOORS = [
    "F01",
    "F02",
    "F03",
    "F04",
    "F05",
    "F06",
    "F07",
    "F08",
    "F09",
    "F10",
    "F11",
    "F12",
    "F13",
]


def get_active_floors() -> list[str]:
    """Returns the list of active constitutional floor identifiers."""
    return ACTIVE_FLOORS


def get_floor_count() -> int:
    """Returns the total number of active constitutional floors."""
    return len(ACTIVE_FLOORS)


def check_floors(
    tool_name: str, params: dict[str, Any], actor_id: str | None
) -> dict[str, Any]:
    """Compatibility wrapper for the canonical runtime floor enforcer."""
    from arifosmcp.runtime.floor import check_floors as _check_floors

    return _check_floors(tool_name, params, actor_id)


def get_floor_status() -> dict[str, Any]:
    """Compatibility wrapper for the canonical runtime floor status."""
    from arifosmcp.runtime.floor import get_floor_status as _get_floor_status

    status = _get_floor_status()
    status["active_floors"] = get_active_floors()
    status["floor_count"] = get_floor_count()
    return status
