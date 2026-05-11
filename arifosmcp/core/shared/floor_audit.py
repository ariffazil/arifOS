"""
Core Floor Audit — ML Runtime Floor Status
═══════════════════════════════════════════════════════

Provides get_ml_floor_runtime() for health endpoint reporting.
Returns active floor enforcement status for the ML/AI governance layer.

Ditempa Bukan Diberi — Intelligence is forged, not given.
"""

from __future__ import annotations

from arifosmcp.constitutional_map import CANONICAL_TOOLS


def get_ml_floor_runtime() -> dict[str, int | list[str]]:
    """
    Return ML runtime floor enforcement status.

    This function provides the floors_active count for the /health endpoint.
    It reads from the canonical tool registry to determine which floors
    are actively enforced.

    Returns:
        dict with:
        - floors_active: int (count of active floors, always 13 for arifOS)
        - floors_list: list of floor IDs that are enforced
        - ml_runtime_status: str ("healthy" if all floors enforced)
    """
    active_floors: list[str] = []

    for _tool_name, spec in CANONICAL_TOOLS.items():
        tool_floors = spec.get("floors", [])
        for f in tool_floors:
            floor_id = f.value if hasattr(f, "value") else f
            if floor_id not in active_floors:
                active_floors.append(floor_id)

    unique_floors = sorted(set(active_floors))

    return {
        "floors_active": len(unique_floors),
        "floors_list": unique_floors,
        "ml_runtime_status": "healthy" if len(unique_floors) >= 13 else "degraded",
        "total_floors": 13,
        "enforcement_version": "2026.05.04-kanon-e920436",
    }
