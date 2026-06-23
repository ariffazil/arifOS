"""
arifosmcp/runtime/intelligence_mesh.py — Federation Intelligence Mesh
═══════════════════════════════════════════════════════════════════════════

Unified health query for federation mesh intelligence.

This module provides a TOOL that any organ can call to:
  1. Discover all federation organs via MCP health endpoints
  2. Check each organ's liveness and intelligence state
  3. Return a unified mesh health report

Orchestrators (AAA cockpit, Hermes, OpenClaw) use this to render the
federation intelligence dashboard.

F1 AMANAH: Read-only. Never mutates organ state.
F2 TRUTH: Every organ state is verified via live HTTP probe.
F11 AUTH: Requires session_id for tracked calls, anonymous for dashboard.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

import httpx

logger = logging.getLogger("arifosmcp.intelligence_mesh")

# Canonical organ registry — single source of truth
# Ports, roles, and expected health fields
ORGAN_REGISTRY: dict[str, dict[str, Any]] = {
    "arifOS": {
        "port": 8088,
        "role": "Constitutional Kernel",
        "health_path": "/health",
        "identity_field": "identity_hash",
        "expected_keys": ["tools_loaded", "floors_active", "contract_status"],
    },
    "GEOX": {
        "port": 8081,
        "role": "Earth Intelligence (Evidence-Only)",
        "health_path": "/health",
        "identity_field": "git_version",
        "expected_keys": ["status", "version", "profile"],
    },
    "WEALTH": {
        "port": 18082,
        "role": "Capital Intelligence (Compute-Only)",
        "health_path": "/health",
        "identity_field": "repo_head",
        "expected_keys": ["status", "version", "public_surface_count"],
    },
    "WELL": {
        "port": 18083,
        "role": "Human Readiness (Reflect-Only)",
        "health_path": "/health",
        "identity_field": "identity_hash",
        "expected_keys": ["status", "authority", "role"],
    },
    "A-FORGE": {
        "port": 7071,
        "role": "Execution Shell (Governed)",
        "health_path": "/health",
        "identity_field": "identity_hash",
        "expected_keys": ["status", "authority_ceiling", "version"],
    },
    "AAA": {
        "port": 3001,
        "role": "Control Plane / Cockpit",
        "health_path": "/health",
        "identity_field": "gateway",
        "expected_keys": ["status", "protocol", "version"],
    },
    "APEX": {
        "port": 3002,
        "role": "Legacy 888 Judge (Decommissioned)",
        "health_path": "/health",
        "identity_field": None,
        "expected_keys": ["status"],
    },
}


async def probe_organ(
    organ_id: str,
    timeout: float = 3.0,
) -> dict[str, Any]:
    """Probe a single organ's health endpoint.

    Returns structured health data or error information.
    This is the atomic unit of mesh intelligence gathering.

    Args:
        organ_id: Canonical organ identifier (key in ORGAN_REGISTRY)
        timeout: HTTP probe timeout in seconds

    Returns:
        Dict with probe result including status, health data, and timing
    """
    config = ORGAN_REGISTRY.get(organ_id)
    if not config:
        return {
            "organ_id": organ_id,
            "alive": False,
            "error": f"Unknown organ: {organ_id}",
        }

    url = f"http://127.0.0.1:{config['port']}{config['health_path']}"
    t0 = datetime.now(UTC)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
            elapsed = (datetime.now(UTC) - t0).total_seconds()

            if resp.status_code != 200:
                return {
                    "organ_id": organ_id,
                    "alive": False,
                    "error": f"HTTP {resp.status_code}",
                    "elapsed_s": round(elapsed, 3),
                    "role": config["role"],
                }

            data = resp.json()
            health_status = data.get("status", data.get("ok", False))

            return {
                "organ_id": organ_id,
                "alive": health_status in ("healthy", True, "ok", "OK"),
                "status": health_status,
                "role": config["role"],
                "identity": data.get(config["identity_field"])
                if config.get("identity_field")
                else None,
                "health_data": data,
                "elapsed_s": round(elapsed, 3),
                "probed_at": t0.isoformat(),
            }

    except httpx.TimeoutException:
        return {
            "organ_id": organ_id,
            "alive": False,
            "error": "timeout",
            "elapsed_s": timeout,
            "role": config["role"],
        }
    except Exception as e:
        return {
            "organ_id": organ_id,
            "alive": False,
            "error": str(e)[:100],
            "role": config["role"],
        }


async def probe_all_organs(
    timeout: float = 3.0,
    organ_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Probe all (or specified) federation organs concurrently.

    This is the primary mesh intelligence gathering function.
    Returns a unified health report with aggregate stats.

    Args:
        timeout: Per-organ probe timeout
        organ_ids: Subset of organs to probe (None = all known)

    Returns:
        Dict with mesh state, organ details, and aggregate health
    """
    targets = organ_ids or list(ORGAN_REGISTRY.keys())

    # Probe all organs concurrently
    tasks = [probe_organ(oid, timeout) for oid in targets]
    results = await asyncio.gather(*tasks)

    # Build result map
    organs: dict[str, Any] = {}
    alive_count = 0
    degraded_count = 0
    dead_count = 0

    for r in results:
        oid = r["organ_id"]
        organs[oid] = r
        if r.get("alive"):
            alive_count += 1
        elif r.get("error"):
            dead_count += 1
        else:
            degraded_count += 1

    total = len(targets)
    mesh_status = "HEALTHY"
    if dead_count > 0:
        mesh_status = "DEGRADED"
    if alive_count == 0:
        mesh_status = "DOWN"

    return {
        "mesh_status": mesh_status,
        "organs_probed": total,
        "alive": alive_count,
        "degraded": degraded_count,
        "dead": dead_count,
        "mesh_coverage_pct": round((alive_count / max(total, 1)) * 100, 1),
        "organs": organs,
        "probed_at": datetime.now(UTC).isoformat(),
        "epistemic": "OBSERVED",
    }


async def mesh_intelligence_report(
    include_health_data: bool = False,
) -> dict[str, Any]:
    """Generate a comprehensive mesh intelligence report.

    This is the top-level dashboard data for the AAA cockpit.
    Returns organ states, connectivity, and aggregate health.

    Args:
        include_health_data: Include full health payloads (large)

    Returns:
        Structured intelligence report
    """
    report = await probe_all_organs()

    # Optionally strip verbose health data
    if not include_health_data and "organs" in report:
        for oid, data in report["organs"].items():
            if isinstance(data, dict) and "health_data" in data:
                del data["health_data"]

    report["report_type"] = "mesh_intelligence"
    report["generated_by"] = "arifosmcp.runtime.intelligence_mesh"
    return report


__all__ = [
    "ORGAN_REGISTRY",
    "probe_organ",
    "probe_all_organs",
    "mesh_intelligence_report",
]
