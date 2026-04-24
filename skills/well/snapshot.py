"""
skills/well/snapshot.py — WELL State Snapshot

Snapshot, floor scan, and log update logic ported from
arifosmcp/tools_canonical.py (arifos_oracle_bio) and
arifosmcp/runtime/well_bridge.py.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

WELL_STATE = Path("/root/WELL/state.json")


def snapshot_read() -> dict[str, Any]:
    """Read the current WELL state snapshot."""
    if not WELL_STATE.exists():
        return {"error": "WELL state not found"}

    with open(WELL_STATE) as f:
        state = json.load(f)

    return {
        "well_score": state.get("well_score"),
        "metrics": state.get("metrics", {}),
        "floors_violated": state.get("floors_violated", []),
        "timestamp": state.get("timestamp"),
    }


def floor_scan() -> dict[str, Any]:
    """Scan constitutional floors from WELL state."""
    if not WELL_STATE.exists():
        return {"error": "WELL state not found"}

    with open(WELL_STATE) as f:
        state = json.load(f)

    return {
        "floors": state.get("floors", {}),
        "floors_violated": state.get("floors_violated", []),
        "timestamp": state.get("timestamp"),
    }


def log_update(dimensions: dict[str, Any] | None = None) -> dict[str, Any]:
    """Update WELL metrics and persist state."""
    if not WELL_STATE.exists():
        return {"error": "WELL state not found"}

    with open(WELL_STATE) as f:
        state = json.load(f)

    metrics = state.get("metrics", {})
    for key, value in (dimensions or {}).items():
        if key in ("sleep", "stress", "cognitive", "metabolic", "structural"):
            if isinstance(value, dict):
                metrics[key] = {**metrics.get(key, {}), **value}
            else:
                metrics[key] = value
        else:
            metrics[key] = value

    state["metrics"] = metrics
    state["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    with open(WELL_STATE, "w") as f:
        json.dump(state, f, indent=2)

    return {
        "updated_state": metrics,
    }
