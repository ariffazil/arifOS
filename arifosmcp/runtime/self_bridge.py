"""arifosmcp/runtime/self_bridge.py — arifOS in-process self-attestation bridge.

T3 (F13 2026-09-22): ``_ORGAN_CONFIG['arifOS']`` has always declared
``health_module='arifosmcp.runtime.self_bridge'`` with ``health_fn=
'arifos_health_check'`` and ``list_fn='list_arifos_tools'`` — but the module
did not exist anywhere (phantom capability: NAME without CALL_PATH, the
Semantic-Authority-Gap invariant). Every self-attestation import-failed →
``{'status': 'unhealthy'}`` → ``DEGRADED_CLAIM`` → sessions stamped
BOOT_ATTESTATION_FAILED + substrate DEGRADED for a bridge that never was.

Contract (organ_attestation._call_organ_health / _list_organ_tools):
    arifos_health_check() -> dict with ``status`` in the healthy vocabulary
    list_arifos_tools()    -> list[dict] (feeds schema_hash; non-empty needed
                              to avoid the PARTIAL_DEGRADED branch)

Both probes are strictly IN-PROCESS — no HTTP loopback — so the boot seeder
cannot race the server socket. Health is a REAL check, never a constant
green: deploy stamp, constitutional floor table, and install identity must
each hold; every failure is listed and status degrades (fail-closed truth).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("arifosmcp.self_bridge")

BRIDGE_SCHEMA = "self_bridge/v1"


def arifos_health_check(organ: str | None = None) -> dict[str, Any]:
    """In-process kernel self-health. Honest: failures list, status degrades."""
    failures: list[str] = []

    # 1. Runtime truth — the deploy stamp must resolve to a commit.
    commit = "unknown"
    try:
        from arifosmcp.runtime.build import _read_commit_stamp

        commit = (_read_commit_stamp() or "unknown").strip()
        if not commit or commit == "unknown":
            failures.append("deploy stamp unreadable")
    except Exception as exc:  # pragma: no cover — only on a broken wheel
        failures.append(f"runtime build module: {exc}")

    # 2. Constitutional floor table must import and be non-empty.
    floor_count = 0
    try:
        from core.shared.laws import THRESHOLDS

        floor_count = len(THRESHOLDS)
        if floor_count == 0:
            failures.append("floor table empty")
    except Exception as exc:  # pragma: no cover
        failures.append(f"floor table: {exc}")

    # 3. Install identity — the wheel must be a resolvable distribution.
    version = "unknown"
    try:
        from importlib.metadata import version as _dist_version

        version = _dist_version("arifos")
    except Exception as exc:  # pragma: no cover
        failures.append(f"distribution metadata: {exc}")

    status = "healthy" if not failures else "degraded"
    return {
        "status": status,
        "version": version,
        "schema_version": BRIDGE_SCHEMA,
        "source_commit": commit,
        "floors_active": floor_count,
        "probe": "in-process (no loopback)",
        "failures": failures,
    }


def list_arifos_tools() -> list[dict[str, Any]]:
    """Canonical kernel tool surface, in-process (public ABI profile)."""
    try:
        from arifosmcp.abi.kernel_abi import tool_names_for_profile

        return [{"name": n} for n in tool_names_for_profile("public_agent")]
    except Exception as exc:  # pragma: no cover
        logger.warning("list_arifos_tools: %s", exc)
        return []
