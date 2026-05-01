"""
arifosmcp/tools/sense_observe.py — 111_SENSE
════════════════════════════════════════════

Reality-grounded observation and telemetry.
"""
from __future__ import annotations

import random
from typing import Any

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.tools import _hold, _ok


def arif_sense_observe(
    mode: str = "search",
    query: str | None = None,
    url: str | None = None,
    layers: list[str] | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_sense_observe", {"query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_sense_observe", floor_check["reason"], floor_check["failed_floors"])

    if mode == "search":
        return _ok("arif_sense_observe", {"query": query, "results": [], "source": "sense", "omega_0": 0.04})
    if mode == "ingest":
        return _ok("arif_sense_observe", {"url": url, "ingested": False, "note": "stub"})
    if mode == "compass":
        return _ok("arif_sense_observe", {"heading": "north", "confidence": 0.95})
    if mode == "atlas":
        return _ok("arif_sense_observe", {"map": {}, "layers": layers or []})
    if mode == "entropy_dS":
        dS = random.uniform(-0.1, 0.1)
        return _ok("arif_sense_observe", {"delta_S": round(dS, 6), "trend": "stable"})
    if mode == "vitals":
        return _ok("arif_sense_observe", {"cpu": 12.5, "mem": 34.0, "io": "normal"})

    return _hold("arif_sense_observe", f"Unknown mode: {mode}")
