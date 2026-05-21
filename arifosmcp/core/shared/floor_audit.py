"""
Core Floor Audit — ML Runtime Floor Status
═══════════════════════════════════════════════════════

Provides get_ml_floor_runtime() for health endpoint reporting.
Returns active floor enforcement status for the ML/AI governance layer.

Ditempa Bukan Diberi — Intelligence is forged, not given.
"""

from __future__ import annotations

import importlib.util
import sys

from arifosmcp.constitutional_map import CANONICAL_TOOLS


def _check_ml_packages() -> tuple[bool, bool]:
    """
    Check which ML packages are available at runtime.

    Returns:
        tuple of (torch_available, sentence_transformers_available)
    """
    torch_spec = importlib.util.find_spec("torch")
    st_spec = importlib.util.find_spec("sentence_transformers")
    return bool(torch_spec), bool(st_spec)


def get_ml_floor_runtime() -> dict[str, int | list[str] | bool | str]:
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
        - ml_floors_enabled: bool (always True — ML floors are wired in code)
        - ml_runtime_ready: bool (True only when torch + sentence_transformers loaded)
        - ml_mode: str ("full-ml" or "heuristic-only")
        - heuristic_fallback_active: bool (True when ML packages unavailable)
        - enforcement_version: str (semantic version of floor enforcement)
    """
    torch_avail, st_avail = _check_ml_packages()
    ml_runtime_ready = bool(torch_avail and st_avail)
    heuristic_fallback_active = not ml_runtime_ready
    ml_mode = "full-ml" if ml_runtime_ready else "heuristic-only"

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
        "ml_floors_enabled": True,  # ML floors are always wired; runtime differs
        "ml_runtime_ready": ml_runtime_ready,
        "ml_mode": ml_mode,
        "heuristic_fallback_active": heuristic_fallback_active,
        "enforcement_version": "2026.05.04-kanon-e920436",
    }
