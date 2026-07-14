"""
arifOS Observatory Routes — Phase A of Reality Observatory.

Defines:

  GET  /api/observatory/v1/snapshot         — the canonical signed snapshot
  GET  /api/observatory/v1/snapshot/capabilities — capability drift matrix alone
  GET  /api/observatory/v1/health            — 7-state vocabulary status (LIVENESS | READINESS | CAPABILITY | GOVERNANCE | AUTHORIZATION | RECEIPT | CONSTITUTIONAL)

All endpoints are READ-ONLY and ADDITIVE. No mutation. No DELETE. No service start.

Everything exposed here carries per-field envelopes:
    {value, state, source, observed_at, age_seconds, confidence,
     observation_method, independent_or_self_reported}

State is one of: observed | derived | reported | unknown.
Observation method is one of: tcp_connect_probe | http_get_probe | filesystem_probe |
    self_reported_endpoint | computed_from_other_fields | environment_variable |
    registry_file_read | process_introspection | static_configuration | unknown.
independent_or_self_reported is one of: independent | self_reported.

The "HEALTHY" badge is forbidden: a green dashboard must NEVER collapse the seven
distinct states into one. The /api/observatory/v1/health endpoint returns them
separately.

This is NOT the single source of truth. It is the federation's public reality witness —
a read-only projection assembled from several underlying sources (filesystem probes,
process introspection, registry reads, and self-reported endpoints). The actual truth
is distributed across arifOS governance, VAULT999 receipts, organ health endpoints,
and the live MCP tool registry.

Forged 2026-07-14 — companion to capability_drift.py.
Epistemic honesty contract added 2026-07-14 — every field carries observation_method
and independent_or_self_reported. A service's own /health is self_reported; a TCP
probe from a different process is independent.
"""

from __future__ import annotations

import json
import logging
import os
import platform
import time
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "observatory.v1"
GENERATED_BY = "arifOS"


# ── Observation-method vocabulary ─────────────────────────────────────────────
# Every per-field envelope MUST carry observation_method and independent_or_self_reported.
# This is the epistemic honesty contract: a service's own /health is self-reported;
# a TCP probe from a different process is independent.
_OBS_METHOD_TCP_PROBE = "tcp_connect_probe"
_OBS_METHOD_HTTP_PROBE = "http_get_probe"
_OBS_METHOD_FILESYSTEM = "filesystem_probe"
_OBS_METHOD_SELF_REPORTED = "self_reported_endpoint"
_OBS_METHOD_DERIVED = "computed_from_other_fields"
_OBS_METHOD_ENV = "environment_variable"
_OBS_METHOD_REGISTRY = "registry_file_read"
_OBS_METHOD_PROCESS = "process_introspection"
_OBS_METHOD_STATIC = "static_configuration"
_OBS_METHOD_UNKNOWN = "unknown"


# ── Per-field envelope helper ─────────────────────────────────────────────────
def _pf(
    value: Any,
    *,
    source: str,
    state: str = "observed",
    confidence: float = 0.95,
    observation_method: str = _OBS_METHOD_UNKNOWN,
    independent: bool = True,
) -> dict[str, Any]:
    """Single-cell per-field envelope. Use this everywhere.

    `observation_method` — how this value was obtained (tcp_probe, filesystem, self_reported, etc.)
    `independent` — True if observed by a process OTHER than the organ being described.
                    False if the organ's own endpoint reported this about itself.
    """
    return {
        "value": value,
        "state": state,
        "source": source,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "age_seconds": 0,
        "confidence": confidence,
        "observation_method": observation_method,
        "independent_or_self_reported": "independent" if independent else "self_reported",
    }


def _pf_age(value: Any, *, source: str, epoch: float | None, state: str = "observed", confidence: float = 0.95,
             observation_method: str = _OBS_METHOD_UNKNOWN, independent: bool = True) -> dict[str, Any]:
    """Per-field envelope with explicit observed_at epoch (so age_seconds is honest)."""
    if epoch is None:
        return _pf(value, source=source, state="unknown", confidence=0.0,
                   observation_method=observation_method, independent=independent)
    age = max(0, int(time.time() - epoch))
    return {
        "value": value,
        "state": state,
        "source": source,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch)),
        "age_seconds": age,
        "confidence": confidence,
        "observation_method": observation_method,
        "independent_or_self_reported": "independent" if independent else "self_reported",
    }


# ── Substrate (machine reality) ────────────────────────────────────────────────
def _safe_psutil(*, source_prefix: str) -> dict[str, dict[str, Any]]:
    """Probe CPU/RAM/disk/network via psutil when available; honest UNKNOWN when not."""
    out: dict[str, dict[str, Any]] = {}
    try:
        import psutil  # type: ignore
    except ImportError:
        return {
            k: _pf(None, source=source_prefix + "." + k, state="unknown", confidence=0.0)
            for k in ("cpu", "memory", "disk", "network")
        }

    try:
        out["cpu"] = _pf(
            {"percent": psutil.cpu_percent(interval=0.1), "count": psutil.cpu_count()},
            source="psutil.cpu",
            confidence=0.95,
            observation_method=_OBS_METHOD_PROCESS,
            independent=True,
        )
    except Exception:
        out["cpu"] = _pf(None, source="psutil.cpu", state="unknown", confidence=0.0,
                        observation_method=_OBS_METHOD_PROCESS, independent=True)
    try:
        mem = psutil.virtual_memory()
        out["memory"] = _pf(
            {"percent": mem.percent, "total_bytes": mem.total, "available_bytes": mem.available},
            source="psutil.virtual_memory",
            confidence=0.95,
            observation_method=_OBS_METHOD_PROCESS,
            independent=True,
        )
    except Exception:
        out["memory"] = _pf(None, source="psutil.virtual_memory", state="unknown", confidence=0.0,
                           observation_method=_OBS_METHOD_PROCESS, independent=True)
    try:
        disk = psutil.disk_usage("/")
        out["disk"] = _pf(
            {"percent": disk.percent, "total_bytes": disk.total, "free_bytes": disk.free},
            source="psutil.disk_usage",
            confidence=0.95,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        )
    except Exception:
        out["disk"] = _pf(None, source="psutil.disk_usage", state="unknown", confidence=0.0,
                         observation_method=_OBS_METHOD_FILESYSTEM, independent=True)
    try:
        net = psutil.net_io_counters()
        out["network"] = _pf(
            {"bytes_sent": net.bytes_sent, "bytes_recv": net.bytes_recv, "errin": net.errin, "errout": net.errout},
            source="psutil.net_io_counters",
            confidence=0.9,
            observation_method=_OBS_METHOD_PROCESS,
            independent=True,
        )
    except Exception:
        out["network"] = _pf(None, source="psutil.net_io_counters", state="unknown", confidence=0.0,
                            observation_method=_OBS_METHOD_PROCESS, independent=True)
    return out


def _substrate_block() -> dict[str, dict[str, Any]]:
    """Compose the substrate envelope: cpu/memory/disk/network + key backends."""
    sub = _safe_psutil(source_prefix="psutil")
    # Backend probes use existing rest_routes helpers when available.
    try:
        from arifosmcp.runtime.rest_routes.rest_routes import _probe_vault999_health  # type: ignore

        vault_state = _probe_vault999_health()
    except Exception:
        vault_state = "unknown"
    sub["postgres"] = _pf(None, source="postgres_probe_pending", state="unknown", confidence=0.0,
                         observation_method=_OBS_METHOD_UNKNOWN, independent=True)
    sub["redis"] = _pf(None, source="redis_probe_pending", state="unknown", confidence=0.0,
                      observation_method=_OBS_METHOD_UNKNOWN, independent=True)
    sub["qdrant"] = _pf(None, source="qdrant_probe_pending", state="unknown", confidence=0.0,
                       observation_method=_OBS_METHOD_UNKNOWN, independent=True)
    # vault999 probe is independent — it checks filesystem state, not the organ's self-report.
    sub["vault999"] = _pf(
        vault_state,
        source="rest_routes._probe_vault999_health",
        state="observed" if vault_state in ("healthy", "degraded") else "unknown",
        confidence=0.9,
        observation_method=_OBS_METHOD_FILESYSTEM,
        independent=True,
    )
    return sub


# ── Runtime identity ───────────────────────────────────────────────────────────
def _runtime_identity_block() -> dict[str, dict[str, Any]]:
    """Runtime identity envelope: commits, hashes, deployment mode, drift state."""
    out: dict[str, dict[str, Any]] = {}

    # Source commit (mounted code)
    try:
        from arifosmcp.runtime.rest_routes.rest_routes import (  # type: ignore
            BUILD_INFO,
            _collect_git_snapshot,
            _compute_runtime_drift,
        )

        git_snap = _collect_git_snapshot()
        drift = _compute_runtime_drift()
    except Exception:
        git_snap = {"commit": "unknown", "branch": "unknown"}
        drift = {"runtime_drift": None, "build_commit": "unknown", "live_commit": "unknown"}

    out["source_commit"] = _pf(git_snap.get("commit"), source="arifOS/_collect_git_snapshot", confidence=0.99,
                               observation_method=_OBS_METHOD_FILESYSTEM, independent=True)
    out["source_branch"] = _pf(git_snap.get("branch"), source="arifOS/_collect_git_snapshot", confidence=0.99,
                               observation_method=_OBS_METHOD_FILESYSTEM, independent=True)
    deployed = drift.get("live_commit", "unknown")
    out["deployed_commit"] = _pf(deployed, source="/opt/arifos/app/.git_commit or HEAD",
                                 confidence=0.99 if deployed != "unknown" else 0.0,
                                 observation_method=_OBS_METHOD_FILESYSTEM, independent=True)
    out["build_commit"] = _pf(drift.get("build_commit"), source="BUILD_INFO.build.commit", confidence=0.99,
                              observation_method=_OBS_METHOD_FILESYSTEM, independent=True)

    # Drift state derivation
    if drift.get("runtime_drift") is True:
        drift_state = "drifted"
    elif drift.get("runtime_drift") is False:
        drift_state = "aligned"
    else:
        drift_state = "unknown"
    out["drift_state"] = _pf(drift_state, source="_compute_runtime_drift", state="derived", confidence=0.9,
                             observation_method=_OBS_METHOD_DERIVED, independent=True)

    out["deployment_mode"] = _pf(
        _detect_deployment_mode(),
        source="Container/Path-probe",
        state="reported",
        confidence=0.85,
        observation_method=_OBS_METHOD_FILESYSTEM,
        independent=True,
    )
    out["process_started_at"] = _pf(
        _kernel_started_at_iso(),
        source="psutil.Process(arifOS).create_time (preferred) → /proc/stat btime fallback",
        confidence=0.85,
        observation_method=_OBS_METHOD_PROCESS,
        independent=True,
    )
    out["kernel_epoch"] = _pf(
        os.getenv("ARIFOS_RELEASE_NAME", "unknown"),
        source="ENV:ARIFOS_RELEASE_NAME",
        state="reported",
        confidence=0.85,
        observation_method=_OBS_METHOD_ENV,
        independent=True,
    )
    out["platform"] = _pf(platform.platform(), source="platform.platform", state="observed", confidence=0.99,
                          observation_method=_OBS_METHOD_PROCESS, independent=True)
    return out


def _safe_uptime() -> float:
    """Best-effort uptime seconds. Zero on failure.

    Returns the OS uptime (not boot_time epoch) — used to derive `now - uptime`
    when callers want seconds-since-boot. For absolute start-time, callers
    should use `_kernel_started_at_iso()` instead.
    """
    try:
        import psutil  # type: ignore

        return float(time.time() - psutil.boot_time())
    except Exception:
        pass
    try:
        with open("/proc/uptime") as fh:
            return float(fh.read().split()[0])
    except Exception:
        return 0.0


def _kernel_started_at_iso() -> str:
    """ISO-8601 UTC when the current arifOS kernel process started.

    Best-effort: prefers psutil.Process(os.getpid()).create_time, falls back
    to deriving from /proc/stat btime + uptime, finally to "unknown".
    """
    try:
        import psutil  # type: ignore

        started_at = float(psutil.Process(__import__("os").getpid()).create_time())
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_at))
    except Exception:
        pass
    try:
        import psutil  # type: ignore

        boot = float(psutil.boot_time())
        # uptime = now − boot ⇒ started_at ≈ boot if process began with the OS
        # We use boot only as last-resort estimate.
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(boot + 30))  # +30s post-boot slack
    except Exception:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _detect_deployment_mode() -> str:
    """systemd|container|mixed|unknown — based on standard filesystem probes."""
    in_container = Path("/.dockerenv").exists() or Path("/proc/1/cgroup").exists()
    systemd_active = Path("/run/systemd/system").exists()
    if in_container and systemd_active:
        return "container"
    if in_container:
        return "container"
    if systemd_active:
        return "systemd"
    return "unknown"


# ── Governance envelope ────────────────────────────────────────────────────────
def _governance_block() -> dict[str, dict[str, Any]]:
    """Governance verdict + 13-floor status + per-field envelopes."""
    out: dict[str, dict[str, Any]] = {}
    floors: dict[str, dict[str, Any]] = {}
    try:
        from arifosmcp.runtime.rest_routes.rest_routes import (  # type: ignore
            _build_governance_status_payload,
            _floor_passes,
        )

        gov = _build_governance_status_payload()
        raw_floors = gov.get("floors", {})
        passing = 0
        failing = 0
        for fid, score in raw_floors.items():
            try:
                ok = _floor_passes(fid, float(score))
            except Exception:
                ok = False
            if ok:
                passing += 1
            else:
                failing += 1
            floors[fid] = {
                "score": _pf(score, source="governance_kernel.get_current_state", confidence=0.9,
                           observation_method=_OBS_METHOD_SELF_REPORTED, independent=False),
                "status": _pf(
                    "pass" if ok else "fail",
                    source="_floor_passes",
                    state="derived",
                    confidence=0.9,
                    observation_method=_OBS_METHOD_DERIVED,
                    independent=False,
                ),
            }
        verdict = gov.get("verdict", "UNKNOWN")
    except Exception as exc:
        logger.warning("governance_block failure: %s", exc)
        verdict = "UNKNOWN"

    out["floors"] = floors
    out["floors_loaded"] = _pf(len(floors), source="kernel.enum.LAW_SPEC_KEYS", confidence=0.99,
                              observation_method=_OBS_METHOD_REGISTRY, independent=True)
    out["floors_passing"] = _pf(passing, source="_floor_passes count", state="derived", confidence=0.95,
                               observation_method=_OBS_METHOD_DERIVED, independent=False)
    out["floors_failing"] = _pf(failing, source="_floor_passes count", state="derived", confidence=0.95,
                               observation_method=_OBS_METHOD_DERIVED, independent=False)
    out["verdict"] = _pf(verdict, source="governance_kernel", state="observed", confidence=0.9,
                        observation_method=_OBS_METHOD_SELF_REPORTED, independent=False)

    # Decomposition — never collapse into a single green badge.
    out["verdict_decomposition"] = {
        "substrate_state": _pf("PASS" if failing == 0 else "FAIL", source="floors_passing count", state="derived",
                              confidence=0.9, observation_method=_OBS_METHOD_DERIVED, independent=False),
        "session_state": _pf("OBSERVE_ONLY", source="governance_kernel.session_state", state="reported",
                            confidence=0.7, observation_method=_OBS_METHOD_SELF_REPORTED, independent=False),
        "action_state": _pf(verdict, source="governance_kernel.verdict", state="observed",
                           confidence=0.9, observation_method=_OBS_METHOD_SELF_REPORTED, independent=False),
        "receipt_state": _pf(
            "SEALED" if Path("/root/.local/share/arifos/vault999/seal_chain_head.json").exists() else "UNSEALED",
            source="sealer.head.exists()", state="observed", confidence=0.99,
            observation_method=_OBS_METHOD_FILESYSTEM, independent=True),
        "constitutional_judgment": _pf("NOT_INVOKED", source="observation-only", state="reported",
                                      confidence=0.7, observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "human_ratification": _pf("NOT_REQUIRED", source="observation-only", state="reported",
                                 confidence=0.7, observation_method=_OBS_METHOD_UNKNOWN, independent=True),
    }
    return out


# ── Federation organs ─────────────────────────────────────────────────────────
def _organs_block(mcp: Any) -> dict[str, dict[str, Any]]:
    """Per-organ field envelopes — never collapses to single LAMP GREEN.

    Transport / Identity / Contract / Capability / Evidence / Governance / Last-receipt / Drift / Dependency
    for each of: arifOS, GEOX, WEALTH, WELL, AAA, A-FORGE, mcp_gateway.

    IMPORTANT: All transport probes use 127.0.0.1 (the host loopback) because
    organs bind to localhost. Docker/service hostnames (geox_eic, wealth-organ, well)
    do not resolve from the host namespace — using them causes gaierror which falsely
    implies the organ is dead when it's actually the probe that's misconfigured.
    """
    out: dict[str, dict[str, Any]] = {}

    # All organs bind to 127.0.0.1 on the host. Probe via loopback, not service names.
    organs = [
        ("arifos", "kernel :8088", "127.0.0.1", 8088),
        ("geox", "GEOX :8081", "127.0.0.1", 8081),
        ("wealth", "WEALTH :18082", "127.0.0.1", 18082),
        ("well", "WELL :18083", "127.0.0.1", 18083),
    ]
    for name, label, host, port in organs:
        out[name] = {
            "transport": _probe_transport(host, port),
            "identity": _pf(None, source=f"{label}/identity", state="unknown", confidence=0.0,
                           observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "contract": _pf(None, source=f"{label}/api/constitution", state="unknown", confidence=0.0,
                           observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "capability": _pf(None, source=f"{label}/api/live/all", state="unknown", confidence=0.0,
                            observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "evidence": _pf(None, source=f"{label} domain evidence", state="unknown", confidence=0.0,
                          observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "governance": _pf(None, source=f"{label} floor scope", state="unknown", confidence=0.0,
                            observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "last_receipt": _pf(None, source=f"{label} seal_chain tail", state="unknown", confidence=0.0,
                              observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "drift": _pf(None, source=f"{label} identity diff", state="unknown", confidence=0.0,
                       observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "dependency": _pf([], source=f"{label} declared deps", state="unknown", confidence=0.0,
                            observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "label": label,
        }

    # AAA — independent TCP probe + static config
    out["aaa"] = {
        "transport": _probe_transport("127.0.0.1", 3001),
        "identity": _pf(None, source="AAA a2a-server", state="unknown", confidence=0.0,
                       observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "contract": _pf(None, source="AAA agent-card", state="unknown", confidence=0.0,
                       observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "capability": _pf(None, source="AAA port 3001", state="unknown", confidence=0.0,
                        observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "evidence": _pf(None, source="AAA memory bridge", state="unknown", confidence=0.0,
                      observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "governance": _pf(None, source="AAA delegates to arifOS", state="reported", confidence=0.9,
                        observation_method=_OBS_METHOD_STATIC, independent=True),
        "last_receipt": _pf(None, source="AAA writes via arif_seal", state="unknown", confidence=0.0,
                          observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "drift": _pf(None, source="AAA vs seal_chain", state="unknown", confidence=0.0,
                   observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "dependency": _pf(["arifos"], source="declared dep", state="reported", confidence=0.7,
                        observation_method=_OBS_METHOD_STATIC, independent=True),
        "label": "AAA :3001",
    }
    # A-FORGE — independent TCP probe + static config
    out["aforge"] = {
        "transport": _probe_transport("127.0.0.1", 7071),
        "identity": _pf(None, source="A-FORGE forgeTools.js", state="unknown", confidence=0.0,
                       observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "contract": _pf(None, source="A-FORGE affordances", state="unknown", confidence=0.0,
                       observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "capability": _pf(None, source="A-FORGE registry", state="unknown", confidence=0.0,
                        observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "evidence": _pf(None, source="A-FORGE SHELL ledger", state="unknown", confidence=0.0,
                      observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "governance": _pf("DELEGATES_TO_KERNEL", source="arifOS 3-B", state="reported", confidence=0.9,
                        observation_method=_OBS_METHOD_STATIC, independent=True),
        "last_receipt": _pf(None, source="forge_shell_ledger", state="unknown", confidence=0.0,
                          observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "drift": _pf("DEGRADED: forge_registry_status exposes stale 31-tool hard-coded list vs live 65+",
                    source="ARIFOS_AFORGE_TOOL_ALIGNMENT_MAP.md:108", state="reported", confidence=0.99,
                    observation_method=_OBS_METHOD_REGISTRY, independent=True),
        "dependency": _pf(["arifos"], source="declared dep", state="reported", confidence=0.7,
                        observation_method=_OBS_METHOD_STATIC, independent=True),
        "label": "A-FORGE :7071/:7072",
    }
    # mcp-gateway — public endpoint, self-reported (we can't independently probe from inside)
    out["mcp_gateway"] = {
        "transport": _pf("mcp.arif-fazil.com", source="Caddyfile vhost", state="reported", confidence=0.95,
                        observation_method=_OBS_METHOD_STATIC, independent=True),
        "identity": _pf(None, source="/.well-known/agent-card.json", state="unknown", confidence=0.0,
                       observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "contract": _pf(None, source="/.well-known/mcp/server.json", state="unknown", confidence=0.0,
                       observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "capability": _pf(None, source="mcp tools/list", state="unknown", confidence=0.0,
                        observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "evidence": _pf(None, source="gateway probe", state="unknown", confidence=0.0,
                      observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "governance": _pf("ROUTES_TO_ORGANS", source="arifOS 3-B", state="reported", confidence=0.9,
                        observation_method=_OBS_METHOD_STATIC, independent=True),
        "last_receipt": _pf(None, source="mcp.recent_seal", state="unknown", confidence=0.0,
                          observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "drift": _pf(None, source="mcp canonical vs exposed", state="unknown", confidence=0.0,
                   observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "dependency": _pf(["arifos", "geox", "wealth", "well", "aaa", "aforge"], source="declared dep",
                        state="reported", confidence=0.95,
                        observation_method=_OBS_METHOD_STATIC, independent=True),
        "label": "mcp.arif-fazil.com",
    }
    return out


def _probe_transport(host: str, port: int) -> dict[str, Any]:
    """Best-effort TCP reachability probe with timeout. Honest about failure.

    This is an INDEPENDENT probe — the Observatory process connects to the organ's
    listening port. The organ does not report its own status. If the connection fails,
    the failure class is exposed (gaierror = DNS, ConnectionRefused = port closed,
    Timeout = process hung) — never collapsed into a bare 'down'.
    """
    import socket

    source = f"tcp_probe({host}:{port})"
    try:
        with socket.create_connection((host, port), timeout=1.5) as _:
            return _pf("up", source=source, state="observed", confidence=0.85,
                       observation_method=_OBS_METHOD_TCP_PROBE, independent=True)
    except socket.gaierror:
        return _pf(
            "unreachable: dns_resolution_failed",
            source=source, state="observed", confidence=0.85,
            observation_method=_OBS_METHOD_TCP_PROBE, independent=True,
        )
    except ConnectionRefusedError:
        return _pf(
            "down: connection_refused",
            source=source, state="observed", confidence=0.85,
            observation_method=_OBS_METHOD_TCP_PROBE, independent=True,
        )
    except socket.timeout:
        return _pf(
            "down: timeout",
            source=source, state="observed", confidence=0.85,
            observation_method=_OBS_METHOD_TCP_PROBE, independent=True,
        )
    except Exception as exc:
        return _pf(f"down: {type(exc).__name__}", source=source, state="observed", confidence=0.85,
                   observation_method=_OBS_METHOD_TCP_PROBE, independent=True)


# ── Metabolism (000 → 010) ────────────────────────────────────────────────────
def _metabolism_block() -> list[dict[str, dict[str, Any]]]:
    """11 intelligence stages — counts/latency/confidence are populated from the
    Kafka/NATS event bus when available; honest UNKNOWN otherwise (we never
    fabricate numbers)."""
    stages = [
        "000_INIT", "111_OBSERVE", "222_EVIDENCE", "333_THINK", "444_ROUTE",
        "555_MEMORY", "666_CRITIQUE", "777_MEASURE", "888_JUDGE", "999_RECEIPT",
        "010_FORGE",
    ]
    out = []
    for s in stages:
        stage: dict[str, dict[str, Any]] = {
            "stage": _pf(s, source="kernel.stage_enum", state="reported", confidence=0.99,
                        observation_method=_OBS_METHOD_STATIC, independent=True),
            "invocations": _pf(None, source=f"event_bus:{s}:count", state="unknown", confidence=0.0,
                              observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "success_rate": _pf(None, source=f"event_bus:{s}:success_rate", state="unknown", confidence=0.0,
                               observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "void_rate": _pf(None, source=f"event_bus:{s}:void_rate", state="unknown", confidence=0.0,
                            observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "hold_rate": _pf(None, source=f"event_bus:{s}:hold_rate", state="unknown", confidence=0.0,
                           observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "median_latency_ms": _pf(None, source=f"event_bus:{s}:median_latency", state="unknown", confidence=0.0,
                                    observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "queue_depth": _pf(None, source=f"event_bus:{s}:queue_depth", state="unknown", confidence=0.0,
                              observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "last_error": _pf(None, source=f"event_bus:{s}:last_error", state="unknown", confidence=0.0,
                            observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "evidence_level": _pf(None, source=f"event_bus:{s}:evidence_level", state="unknown", confidence=0.0,
                                observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "output_confidence": _pf(None, source=f"event_bus:{s}:confidence", state="unknown", confidence=0.0,
                                   observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "responsible_organ": _pf("arifos", source="kernel.stage_lane", state="reported", confidence=0.9,
                                   observation_method=_OBS_METHOD_STATIC, independent=True),
            "human_gate": _pf(False, source="kernel.stage_lane", state="reported", confidence=0.9,
                            observation_method=_OBS_METHOD_STATIC, independent=True),
        }
        out.append(stage)
    return out


# ── Evidence + receipts envelopes ─────────────────────────────────────────────
def _evidence_block() -> dict[str, dict[str, Any]]:
    return {
        "sources_used": _pf([], source="snapshot source registry", state="unknown", confidence=0.0,
                           observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "source_diversity": _pf(None, source="HUMAN×AI×EXTERNAL geometric mean", state="unknown", confidence=0.0,
                               observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "contradictions": _pf([], source="contradiction_engine.scan", state="unknown", confidence=0.0,
                            observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "missing_witnesses": _pf([], source="witness_class.scan", state="unknown", confidence=0.0,
                                observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "direct_vs_inferred": {
            "direct": _pf(0, source="evidence_class=OBS count", state="unknown", confidence=0.0,
                         observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "inferred": _pf(0, source="evidence_class=DER|INT count", state="unknown", confidence=0.0,
                           observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        },
        "confidence_calibration": _pf(None, source="reliability.bin", state="unknown", confidence=0.0,
                                     observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "unsupported_claims": _pf([], source="claims without evidence_refs", state="unknown", confidence=0.0,
                                observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "evidence_expiry": _pf([], source="expiring receipts", state="unknown", confidence=0.0,
                             observation_method=_OBS_METHOD_UNKNOWN, independent=True),
    }


def _receipts_block() -> dict[str, dict[str, Any]]:
    head_path = Path("/root/.local/share/arifos/vault999/seal_chain_head.json")
    chain_path = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl")
    head_seq = None
    head_epoch = None
    if head_path.exists():
        try:
            with open(head_path, encoding="utf-8") as fh:
                head_data = json.load(fh)
            head_seq = head_data.get("seq")
            head_epoch_str = head_data.get("epoch")
            if head_epoch_str:
                # ISO-8601 UTC → epoch; tolerate trailing Z.
                t = time.strptime(head_epoch_str.rstrip("Z"), "%Y-%m-%dT%H:%M:%S.%f")
                head_epoch = time.mktime(t) - time.timezone
                if head_epoch < 0:
                    head_epoch += time.timezone
        except Exception:
            pass
    return {
        "chain_path": _pf(str(chain_path), source="VAULT999 path probe", state="reported", confidence=0.99,
                         observation_method=_OBS_METHOD_FILESYSTEM, independent=True),
        "head_seq": _pf(head_seq, source="sealer head file",
                       state="observed" if head_seq is not None else "unknown", confidence=0.99,
                       observation_method=_OBS_METHOD_FILESYSTEM, independent=True),
        "head_epoch": _pf_age(head_epoch_str_no_z(head_epoch), source="sealer.head.epoch", epoch=head_epoch,
                             state="observed" if head_epoch is not None else "unknown", confidence=0.99,
                             observation_method=_OBS_METHOD_FILESYSTEM, independent=True),
        "write_path_alive": _pf(head_path.exists(), source="sealer writer alive heuristic", state="derived", confidence=0.7,
                               observation_method=_OBS_METHOD_FILESYSTEM, independent=True),
        "read_path_alive": _pf(chain_path.exists(), source="sealer reader (jsonl exists)", state="derived", confidence=0.95,
                              observation_method=_OBS_METHOD_FILESYSTEM, independent=True),
        "verify_path_alive": _pf(None, source="GET /api/observatory/v1/seal/verify", state="unknown", confidence=0.0,
                                observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "replay_path_alive": _pf(None, source="GET /api/observatory/v1/seal/replay", state="unknown", confidence=0.0,
                                observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "chain_verified": _pf(None, source="GET /api/observatory/v1/seal/verify", state="unknown", confidence=0.0,
                             observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "orphan_traces": _pf(None, source="trace_id without receipt", state="unknown", confidence=0.0,
                           observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "unsealed_actions": _pf(None, source="audit gap detector", state="unknown", confidence=0.0,
                              observation_method=_OBS_METHOD_UNKNOWN, independent=True),
    }


def head_epoch_str_no_z(epoch: float | None) -> str | None:
    return None if epoch is None else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


# ── Incidents envelope ────────────────────────────────────────────────────────
def _incidents_block() -> list[dict[str, Any]]:
    """Honest empty list until the audit gap detector wires real incidents.

    Every incident carries: {id, severity, first_seen, evidence, owner, status}.
    """
    return []


# ── Snapshot composition ──────────────────────────────────────────────────────
def build_snapshot(
    mcp: Any,
    *,
    snapshot_id: str | None = None,
    registered_tools: set[str] | None = None,
) -> dict[str, Any]:
    """Compose the canonical observatory snapshot.

    `mcp` is the FastMCP instance.
    `registered_tools` — pre-computed set of live registered tool names (preferred,
    avoids async issues with FastMCP 3.x). If None, falls back to sync probe.
    """
    from arifosmcp.runtime.capability_drift import compute_capability_matrix  # local import

    # Server JSON for `exposed` computation
    server_json: dict[str, Any] | None = None
    try:
        from arifosmcp.runtime.rest_routes.rest_routes import build_server_json  # type: ignore

        server_json = build_server_json(os.getenv("ARIFOS_PUBLIC_BASE_URL", "http://arifos.arif-fazil.com"))
    except Exception as exc:
        logger.warning("build_server_json failed: %s", exc)

    capabilities = compute_capability_matrix(mcp=mcp, server_json=server_json, registered_tools=registered_tools)

    snap_id = snapshot_id or "obs_" + time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    payload: dict[str, Any] = {
        "snapshot_id": snap_id,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": GENERATED_BY,
        "schema_version": SCHEMA_VERSION,
        "signature": _pf(None, source="ed25519 over canonicaljson(payload_without_signature) — pending key bootstrap",
                        state="unknown", confidence=0.0,
                        observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "runtime_identity": _runtime_identity_block(),
        "substrate": _substrate_block(),
        "governance": _governance_block(),
        "capabilities": capabilities,
        "organs": _organs_block(mcp),
        "metabolism": _metabolism_block(),
        "evidence": _evidence_block(),
        "receipts": _receipts_block(),
        "incidents": _incidents_block(),
        "tier": _pf("public", source="Caddy X-Observatory-Tier (default public; operator with valid X-Op-Token)",
                   state="reported", confidence=0.99,
                   observation_method=_OBS_METHOD_STATIC, independent=True),
    }
    return payload


# ── Seven-state vocabulary health endpoint ────────────────────────────────────
def seven_state_health(mcp: Any) -> dict[str, dict[str, Any]]:
    """Return the seven independent states. Never collapse them into one badge.

    LIVENESS       — process responds
    READINESS      — dependencies reachable
    CAPABILITY     — tool registry callable end-to-end
    GOVERNANCE     — floors + authority controls active
    AUTHORIZATION  — specific action permitted
    RECEIPT        — event written + replayable
    CONSTITUTIONAL — judged action passed required gates
    """
    states: dict[str, dict[str, Any]] = {}
    # LIVENESS — kernel responds at all. This IS self-reported (we probe ourselves),
    # but the alternative is no probe at all. Confidence is high because a dead process
    # cannot respond. Mark as self_reported to be epistemically honest.
    states["LIVENESS"] = _pf("up", source="self-process responding", state="observed", confidence=0.99,
                            observation_method=_OBS_METHOD_SELF_REPORTED, independent=False)
    # READINESS — independent filesystem probe: vault999 jsonl exists and is readable.
    fs_ok = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl").exists()
    states["READINESS"] = _pf("up" if fs_ok else "degraded", source="VAULT fs reachable", state="observed", confidence=0.85,
                             observation_method=_OBS_METHOD_FILESYSTEM, independent=True)
    # CAPABILITY — derived from capability drift (independent matrix computation).
    try:
        from arifosmcp.runtime.capability_drift import compute_capability_matrix

        cap = compute_capability_matrix(mcp=mcp, server_json=None)
        degraded = cap.get("degraded_count", 0)
        states["CAPABILITY"] = _pf(
            "up" if degraded == 0 else "degraded",
            source="compute_capability_matrix.degraded_count",
            state="derived",
            confidence=0.9,
            observation_method=_OBS_METHOD_DERIVED,
            independent=True,
        )
    except Exception:
        states["CAPABILITY"] = _pf("unknown", source="compute_capability_matrix", state="unknown", confidence=0.0,
                                  observation_method=_OBS_METHOD_UNKNOWN, independent=True)
    # GOVERNANCE — derived from governance block (kernel's own floor scores = self-reported).
    try:
        gov = _governance_block()
        passing = gov.get("floors_passing", {}).get("value") if isinstance(gov, dict) else None
        states["GOVERNANCE"] = _pf(
            "up" if isinstance(passing, int) and passing >= 13 else "degraded",
            source="governance_block.floors_passing",
            state="derived",
            confidence=0.85,
            observation_method=_OBS_METHOD_DERIVED,
            independent=False,
        )
    except Exception:
        states["GOVERNANCE"] = _pf("unknown", source="governance_block", state="unknown", confidence=0.0,
                                  observation_method=_OBS_METHOD_UNKNOWN, independent=True)
    # AUTHORIZATION — only meaningful in a specific request context; mark UNKNOWN here.
    states["AUTHORIZATION"] = _pf("request-scoped", source="action_request envelope", state="reported", confidence=0.0,
                                 observation_method=_OBS_METHOD_UNKNOWN, independent=True)
    # RECEIPT — derive from independent filesystem probe.
    try:
        rcpts = _receipts_block()
        chain_alive = rcpts.get("read_path_alive", {}).get("value")
        states["RECEIPT"] = _pf("up" if chain_alive else "unknown", source="receipts.read_path_alive", state="derived", confidence=0.7,
                               observation_method=_OBS_METHOD_FILESYSTEM, independent=True)
    except Exception:
        states["RECEIPT"] = _pf("unknown", source="receipts_block", state="unknown", confidence=0.0,
                               observation_method=_OBS_METHOD_UNKNOWN, independent=True)
    # CONSTITUTIONAL — only meaningful after arif_judge ran. Mark UNKNOWN here.
    states["CONSTITUTIONAL"] = _pf("judgment-scoped", source="arif_judge envelope", state="reported", confidence=0.0,
                                  observation_method=_OBS_METHOD_UNKNOWN, independent=True)
    return states


# ── Starlette/FastAPI route registration ─────────────────────────────────────
def register_observatory_routes(app: Any, mcp: Any, prefix: str = "/api/observatory/v1") -> None:
    """Register the Observatory REST routes on the given Starlette/FastAPI app.

    Routes registered (all READ-ONLY):
        GET /api/observatory/v1/snapshot
        GET /api/observatory/v1/snapshot/capabilities
        GET /api/observatory/v1/health
    """
    from starlette.responses import JSONResponse  # type: ignore

    async def _snapshot(request):
        from arifosmcp.runtime.rest_routes.rest_routes import _dashboard_cors_headers, _cache_headers, _merge_headers  # type: ignore
        from arifosmcp.runtime.capability_drift import _registered_tools_async

        # Pre-compute registered tools async (FastMCP 3.x list_tools is async)
        reg_tools = await _registered_tools_async(mcp)
        snap = build_snapshot(mcp=mcp, registered_tools=reg_tools)
        return JSONResponse(
            snap,
            headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(request)),
        )

    async def _capabilities(request):
        from arifosmcp.runtime.rest_routes.rest_routes import _dashboard_cors_headers, _cache_headers, _merge_headers  # type: ignore
        from arifosmcp.runtime.capability_drift import compute_capability_matrix, _registered_tools_async

        try:
            server_json = None
            try:
                from arifosmcp.runtime.rest_routes.rest_routes import build_server_json  # type: ignore

                server_json = build_server_json(os.getenv("ARIFOS_PUBLIC_BASE_URL", "http://arifos.arif-fazil.com"))
            except Exception:
                pass
            reg_tools = await _registered_tools_async(mcp)
            matrix = compute_capability_matrix(mcp=mcp, server_json=server_json, registered_tools=reg_tools)
        except Exception as exc:
            return JSONResponse({"error": f"matrix failure: {exc}"}, status_code=500)
        return JSONResponse(matrix, headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(request)))

    # Use the same flexible route convention as register_rest_routes.
    def route(path: str):
        full = prefix.rstrip("/") + path

        def _decorator(handler: Callable):
            if hasattr(app, "add_route") or "Starlette" in str(type(app)) or "FastAPI" in str(type(app)):
                from starlette.routing import Route

                app.router.routes.append(Route(full, endpoint=handler, methods=["GET"]))
            elif hasattr(app, "custom_route"):
                app.custom_route(full, methods=["GET"])(handler)
            elif hasattr(app, "route"):
                app.route(full, methods=["GET"])(handler)
            else:
                logger.warning("Failed to register observatory route %s: app has no route method", full)
            return handler

        return _decorator

    @route("/snapshot")
    async def _h_snapshot(req):  # type: ignore
        return await _snapshot(req)

    @route("/snapshot/capabilities")
    async def _h_capabilities(req):  # type: ignore
        return await _capabilities(req)

    async def _health(request):
        from arifosmcp.runtime.rest_routes.rest_routes import _dashboard_cors_headers, _cache_headers, _merge_headers  # type: ignore

        states = seven_state_health(mcp=mcp)
        return JSONResponse({"states": states, "schema_version": SCHEMA_VERSION}, headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(request)))

    @route("/health")
    async def _h_health(req):  # type: ignore
        return await _health(req)
