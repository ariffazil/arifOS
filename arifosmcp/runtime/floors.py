"""
arifOS/arifosmcp/runtime/floors.py — Constitutional Floor Registry
═══════════════════════════════════════════════════════════════

Single source of truth for active floors and governance counts.
"""

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
