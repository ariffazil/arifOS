from __future__ import annotations

import os
from typing import Any

from arifosmcp.constitutional_map import list_canonical_tools, list_constitutional_tools

try:
    from arifosmcp.tools_canonical import TOOL_ALIAS_MAP
except Exception:  # pragma: no cover - defensive fallback
    TOOL_ALIAS_MAP = {}


CANONICAL_13: tuple[str, ...] = tuple(list_constitutional_tools())
CANONICAL_15: tuple[str, ...] = tuple(list_canonical_tools())

BLOCKED_PUBLIC_PREFIXES: tuple[str, ...] = (
    "arifos_",
    "_arifos_",
    "wealth_",
    "afwell_",
    "geox_",
    "geoxarifos_",
)

VALID_PUBLIC_SURFACE_MODES: tuple[str, ...] = ("canonical13", "canonical15", "expanded45")


def _alias_public_name(alias_name: str) -> str:
    namespace = "arifos"
    clean_name = alias_name
    if alias_name.startswith(("P_geox_", "E_geox_")):
        namespace = "geoxarifOS"
        clean_name = alias_name.replace("P_geox_", "").replace("E_geox_", "")
    elif alias_name.startswith(("V_", "P_wealth_")):
        namespace = "wealth"
        clean_name = alias_name.replace("V_", "").replace("P_wealth_", "")
    elif alias_name.startswith(("P_well_", "E_well_")):
        namespace = "AFWELL"
        clean_name = alias_name.replace("P_well_", "").replace("E_well_", "")
    return f"{namespace}_{clean_name}"


EXPANDED_45: tuple[str, ...] = tuple(
    list(dict.fromkeys([*CANONICAL_15, *(_alias_public_name(name) for name in TOOL_ALIAS_MAP)]))
)


def normalize_public_surface_mode(mode: str | None = None) -> str:
    raw = (mode or "").strip().lower()
    if not raw:
        raw = (os.getenv("ARIFOS_PUBLIC_SURFACE_MODE", "") or "").strip().lower()
    if not raw:
        raw = (os.getenv("ARIFOS_PUBLIC_TOOL_PROFILE", "") or "").strip().lower()

    profile_map = {
        "public": "canonical15",
        "chatgpt": "canonical15",
        "agnostic_public": "canonical15",
        "canonical13": "canonical13",
        "canonical15": "canonical15",
        "internal": "expanded45",
        "expanded45": "expanded45",
    }
    return profile_map.get(raw, "canonical15")


def current_public_surface_mode() -> str:
    return normalize_public_surface_mode(None)


def public_tool_names_for_mode(mode: str | None = None) -> tuple[str, ...]:
    resolved = normalize_public_surface_mode(mode)
    if resolved == "canonical13":
        return CANONICAL_13
    if resolved == "expanded45":
        return EXPANDED_45
    return CANONICAL_15


def public_boundary_allows(name: str, mode: str | None = None) -> bool:
    lowered = (name or "").strip().lower()
    if not lowered or lowered.startswith(BLOCKED_PUBLIC_PREFIXES):
        return False
    return name in set(public_tool_names_for_mode(mode))


def public_surface_state(mode: str | None = None) -> dict[str, Any]:
    resolved = normalize_public_surface_mode(mode)
    tool_names = list(public_tool_names_for_mode(resolved))
    diagnostic_tools = [name for name in tool_names if name in {"arif_ping", "arif_selftest"}]
    return {
        "mode": resolved,
        "tools_registered": len(tool_names),
        "kernel_tools": len(CANONICAL_13),
        "diagnostic_tools": diagnostic_tools,
        "tool_names": tool_names,
        "canonical13_count": len(CANONICAL_13),
        "canonical15_count": len(CANONICAL_15),
        "blocked_public_prefixes": list(BLOCKED_PUBLIC_PREFIXES),
    }
