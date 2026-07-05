"""
Tool Invariant Check — startup validation against TOOL_INVARIANTS.yaml

One function. One check. One truth.
If the registry drifts from the YAML, the kernel logs a warning.

DITEMPA BUKAN DIBERI — 2026-07-05, FORGE (000Ω)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_INVARIANTS_PATH = Path(__file__).parent / "TOOL_INVARIANTS.yaml"


def _load_invariants() -> dict[str, Any] | None:
    """Load the canonical invariants file."""
    try:
        with open(_INVARIANTS_PATH) as f:
            return yaml.safe_load(f)
    except Exception as exc:
        logger.warning("Cannot load TOOL_INVARIANTS.yaml: %s", exc)
        return None


def _extract_canonical_names(invariants: dict) -> set[str]:
    """Extract all canonical tool names from invariants."""
    names = set()
    for tool in invariants.get("canonical", {}).values():
        names.add(tool["name"])
    for tool in invariants.get("diagnostic", {}).values():
        names.add(tool["name"])
    return names


def check_registry_against_invariants(
    registered_names: set[str],
) -> dict[str, Any]:
    """
    Compare live registered tools against TOOL_INVARIANTS.yaml.

    Returns:
        {
            "status": "PASS" | "DRIFT",
            "in_yaml_not_registered": [...],   # tools in YAML but missing from runtime
            "in_registered_not_yaml": [...],   # tools in runtime but not in YAML
            "canonical_count": int,
            "diagnostic_count": int,
            "registered_count": int,
        }
    """
    invariants = _load_invariants()
    if invariants is None:
        return {"status": "ERROR", "reason": "Cannot load invariants file"}

    yaml_names = _extract_canonical_names(invariants)
    # Also include deprecated aliases (they're still valid names)
    deprecated_names = {d["name"] for d in invariants.get("deprecated", [])}
    all_valid_names = yaml_names | deprecated_names

    in_yaml_not_registered = sorted(yaml_names - registered_names)
    in_registered_not_yaml = sorted(registered_names - all_valid_names)

    status = "PASS" if not in_yaml_not_registered and not in_registered_not_yaml else "DRIFT"

    if in_yaml_not_registered:
        logger.warning(
            "TOOL INVARIANT DRIFT: In YAML but not registered: %s",
            in_yaml_not_registered,
        )
    if in_registered_not_yaml:
        logger.warning(
            "TOOL INVARIANT DRIFT: Registered but not in YAML: %s",
            in_registered_not_yaml,
        )

    return {
        "status": status,
        "in_yaml_not_registered": in_yaml_not_registered,
        "in_registered_not_yaml": in_registered_not_yaml,
        "canonical_count": len(invariants.get("canonical", {})),
        "diagnostic_count": len(invariants.get("diagnostic", {})),
        "registered_count": len(registered_names),
        "yaml_total": len(yaml_names),
    }
