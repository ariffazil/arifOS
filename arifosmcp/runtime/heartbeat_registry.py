"""
arifosmcp/runtime/heartbeat_registry.py
═══════════════════════════════════════════════════════════════════════════════
Live heartbeat registry for the sovereign AGI kernel.

Tracks per-organ heartbeats, detects stale/degraded organs, and computes a
federation-wide liveness verdict. Heartbeats are evidence-only; arifOS judges
whether a missing heartbeat should block routing.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("arifosmcp.heartbeat_registry")


# ═══════════════════════════════════════════════════════════════════════════════
# Registry
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class HeartbeatRecord:
    organ_id: str
    status: str
    version: str
    schema_hash: str
    constitution_hash: str
    tool_count: int
    heartbeat_at: float
    degraded: bool
    reason: str | None = None
    load: dict[str, Any] = field(default_factory=dict)


_HEARTBEAT_REGISTRY: dict[str, HeartbeatRecord] = {}

# Staleness threshold: heartbeat older than this is DEGRADED
_STALE_THRESHOLD_SECONDS = 120


# ═══════════════════════════════════════════════════════════════════════════════
# Core API
# ═══════════════════════════════════════════════════════════════════════════════


def record_heartbeat(
    organ_id: str,
    status: str = "ALIVE",
    version: str = "unknown",
    schema_hash: str = "sha256:missing",
    constitution_hash: str = "sha256:missing",
    tool_count: int = 0,
    degraded: bool = False,
    reason: str | None = None,
    load: dict[str, Any] | None = None,
) -> HeartbeatRecord:
    """Record or update a heartbeat for an organ."""
    rec = HeartbeatRecord(
        organ_id=organ_id,
        status=status,
        version=version,
        schema_hash=schema_hash,
        constitution_hash=constitution_hash,
        tool_count=tool_count,
        heartbeat_at=time.time(),
        degraded=degraded,
        reason=reason,
        load=load or {},
    )
    _HEARTBEAT_REGISTRY[organ_id] = rec
    return rec


def get_heartbeat(organ_id: str) -> HeartbeatRecord | None:
    return _HEARTBEAT_REGISTRY.get(organ_id)


def list_heartbeats() -> dict[str, HeartbeatRecord]:
    return dict(_HEARTBEAT_REGISTRY)


def is_organ_stale(organ_id: str, threshold_seconds: float = _STALE_THRESHOLD_SECONDS) -> bool:
    rec = _HEARTBEAT_REGISTRY.get(organ_id)
    if rec is None:
        return True
    return (time.time() - rec.heartbeat_at) > threshold_seconds


def federation_liveness(
    required_organs: list[str] | None = None,
    threshold_seconds: float = _STALE_THRESHOLD_SECONDS,
) -> dict[str, Any]:
    """Compute federation-wide liveness verdict."""
    required = required_organs or ["arifOS", "GEOX", "WEALTH", "WELL"]
    now = time.time()
    stale: list[str] = []
    degraded: list[str] = []
    alive: list[str] = []

    for organ_id in required:
        rec = _HEARTBEAT_REGISTRY.get(organ_id)
        if rec is None:
            stale.append(organ_id)
            continue
        age = now - rec.heartbeat_at
        if age > threshold_seconds:
            stale.append(organ_id)
        elif rec.degraded or rec.status != "ALIVE":
            degraded.append(organ_id)
            alive.append(organ_id)
        else:
            alive.append(organ_id)

    if stale:
        verdict = "DEGRADED"
    elif degraded:
        verdict = "DEGRADED"
    else:
        verdict = "SEAL"

    return {
        "verdict": verdict,
        "alive": alive,
        "degraded": degraded,
        "stale": stale,
        "checked_at": datetime.now(UTC).isoformat(),
    }


def _record_to_dict(rec: HeartbeatRecord) -> dict[str, Any]:
    return {
        "organ_id": rec.organ_id,
        "status": rec.status,
        "version": rec.version,
        "schema_hash": rec.schema_hash,
        "constitution_hash": rec.constitution_hash,
        "tool_count": rec.tool_count,
        "heartbeat_at": datetime.fromtimestamp(rec.heartbeat_at, UTC).isoformat(),
        "degraded": rec.degraded,
        "reason": rec.reason,
        "load": rec.load,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MCP tool handler
# ═══════════════════════════════════════════════════════════════════════════════


def arif_heartbeat(
    organ_id: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Record or query federation heartbeats.

    If organ_id is provided, records a heartbeat for that organ and returns the
    current registry snapshot. If omitted, returns the liveness verdict for all
    known organs.
    """
    if organ_id:
        record_heartbeat(organ_id=organ_id, status="ALIVE")
        return {
            "status": "OK",
            "verdict": "SEAL",
            "result": {
                "recorded_for": organ_id,
                "registry": {k: _record_to_dict(v) for k, v in _HEARTBEAT_REGISTRY.items()},
            },
        }

    liveness = federation_liveness()
    return {
        "status": "OK",
        "verdict": liveness["verdict"],
        "result": {
            "liveness": liveness,
            "heartbeats": {k: _record_to_dict(v) for k, v in _HEARTBEAT_REGISTRY.items()},
        },
    }


__all__ = [
    "HeartbeatRecord",
    "record_heartbeat",
    "get_heartbeat",
    "list_heartbeats",
    "is_organ_stale",
    "federation_liveness",
    "arif_heartbeat",
]
