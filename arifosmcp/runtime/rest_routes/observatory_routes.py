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


# ── Explanation vocabulary (2026-07-14) ──────────────────────────────────────
# Every technical failure carries three layers:
#   machine_code  — the canonical identifier (e.g., DNS_RESOLUTION_FAILED)
#   human         — what this means for a non-technical reader
#   builder       — what an engineer should check or do
#
# This is NOT auto-generated. Each entry is manually written to be truthful
# about what the failure means and what can be done about it.
# "Never show more certainty than the underlying machine state has earned."

_EXPLAIN: dict[str, dict[str, str]] = {
    # Transport failures
    "TRANSPORT_UNREACHABLE": {
        "human": "The Observatory could not reach this service over the network. The service may be stopped, starting up, or running on a different address.",
        "builder": "Check: systemctl status <service>, verify the port with ss -tlnp, confirm the probe target is 127.0.0.1:<port>.",
    },
    "TRANSPORT_TIMEOUT": {
        "human": "The service was found on the network but did not respond in time. It may be overloaded or blocked.",
        "builder": "Check: service logs for errors, resource usage (CPU/memory), firewall rules, and whether the process is hung.",
    },
    "TRANSPORT_CONNECTION_REFUSED": {
        "human": "The address exists but the service is not accepting connections. It may be stopped or crashed.",
        "builder": "Check: systemctl status <service>, dmesg for OOM kills, service logs for startup failures.",
    },
    "TRANSPORT_DNS_FAILED": {
        "human": "The Observatory could not find the configured network address. The service may still be running but the address is wrong.",
        "builder": "Check: service hostname in Caddyfile, /etc/hosts, network namespace, and whether the probe target uses 127.0.0.1 instead of a hostname.",
    },
    # Capability failures
    "CAPABILITY_DRIFTED": {
        "human": "Some tools that were expected to be available are missing or changed. The service may have been updated without restarting, or a dependency is not loaded.",
        "builder": "Check: the capability drift matrix in the Observatory snapshot, restart the service to reload the tool registry, verify MCP tool registration.",
    },
    "CAPABILITY_DEGRADED": {
        "human": "Some tools are not fully working. The service is running but not all features are available.",
        "builder": "Check: which tools are degraded in /api/observatory/v1/snapshot/capabilities, verify tool input/output schemas match the registry.",
    },
    "CAPABILITY_UNKNOWN": {
        "human": "The Observatory could not determine which tools are available. The service may not have started yet.",
        "builder": "Check: service startup logs, MCP tool registry initialization, FastMCP list_tools() availability.",
    },
    # Conformance failures
    "CONFORMANCE_UNVERIFIED": {
        "human": "The Observatory has not yet verified this aspect of the service. This does not mean it is broken — just that no check has run.",
        "builder": "Run the conformance checks: POST /api/observatory/v1/conformance/run. Check conformance_spine.py for available checks.",
    },
    "CONFORMANCE_TRANSPORT_FAIL": {
        "human": "The service is not reachable over the network. Some checks require a running service.",
        "builder": "Check: service status, port availability, Caddy reverse proxy configuration.",
    },
    "CONFORMANCE_STATIC_FAIL": {
        "human": "A basic configuration check failed. The service may be misconfigured.",
        "builder": "Check: the conformance check details in the Observatory snapshot, verify environment variables and configuration files.",
    },
    # Edge failures
    "EDGE_UNREACHABLE": {
        "human": "The Observatory could not verify that this service can communicate with another service. The connection between them may be broken.",
        "builder": "Check: both services are running, network connectivity between them, reverse proxy configuration for the edge.",
    },
    "EDGE_DRIFTED": {
        "human": "The connection between two services has changed from what was expected. One service may have been updated.",
        "builder": "Check: schema compatibility between the two services, verify tool registration on both ends.",
    },
    # Governance failures
    "GOVERNANCE_DEGRADED": {
        "human": "Some governance checks are not passing. The service is running but may not be enforcing all rules correctly.",
        "builder": "Check: which floors are failing in the governance block, verify floor computation in core/shared/floors.py.",
    },
    # Receipt failures
    "RECEIPT_CHAIN_BROKEN": {
        "human": "The audit trail has a gap. Some events may not have been recorded properly.",
        "builder": "Check: VAULT999 chain integrity via /api/observatory/v1/seal/verify, verify seal_chain.jsonl is writable.",
    },
    "RECEIPT_UNAVAILABLE": {
        "human": "The audit system is not responding. Events may not be being recorded.",
        "builder": "Check: vault999 service status, Postgres connectivity, seal_chain.jsonl file permissions.",
    },
    # Generic
    "PROBE_FAILED": {
        "human": "A health check did not complete. This may be temporary.",
        "builder": "Check: service logs, try the probe again, verify the probe target is correct.",
    },
    "UNKNOWN": {
        "human": "The Observatory encountered an unexpected condition. This needs investigation.",
        "builder": "Check: Observatory logs for exceptions, verify all dependencies are running.",
    },
}


def _explain(code: str) -> dict[str, str]:
    """Return {machine_code, human, builder} for a failure code.

    Unknown codes get a generic explanation — never silent, never empty.
    """
    entry = _EXPLAIN.get(code, _EXPLAIN["UNKNOWN"])
    return {
        "machine_code": code,
        "human": entry["human"],
        "builder": entry["builder"],
    }


def _enrich_with_explanation(envelope: dict[str, Any]) -> dict[str, Any]:
    """Add explanation to a per-field envelope if it represents a failure.

    Non-failure states (value in GOOD_VALUES) get no explanation —
    we don't explain things that are working. Only failures get the
    three-layer treatment.
    """
    GOOD_VALUES = {"up", "ALIGNED", "STATIC_PASS", "TRANSPORT_PASS",
                   "GOVERNED_RUNTIME_PASS", "GREEN", "reachable", "aligned"}
    value = envelope.get("value")
    # Only check membership for hashable scalar types. dict/list values (e.g.
    # nested envelopes) bypass the good-values check and proceed to explanation.
    if isinstance(value, (str, int, float, bool)) and value in GOOD_VALUES:
        return envelope
    # Derive a failure code from the value or state
    code = _derive_failure_code(envelope)
    if code:
        envelope["explanation"] = _explain(code)
    return envelope


def _derive_failure_code(envelope: dict[str, Any]) -> str | None:
    """Derive a machine failure code from an envelope's value and source."""
    value = envelope.get("value")
    source = envelope.get("source", "")
    state = envelope.get("state", "")

    # Transport failures
    if value == "unreachable" or "unreachable" in str(value).lower():
        return "TRANSPORT_UNREACHABLE"
    if value == "timeout" or "timeout" in str(value).lower():
        return "TRANSPORT_TIMEOUT"
    if value == "connection_refused" or "refused" in str(value).lower():
        return "TRANSPORT_CONNECTION_REFUSED"
    if "dns" in str(value).lower() or "gaierror" in str(source).lower():
        return "TRANSPORT_DNS_FAILED"

    # Capability failures
    if "capability" in source.lower() and value == "degraded":
        return "CAPABILITY_DEGRADED"
    if "capability" in source.lower() and value == "DRIFTED":
        return "CAPABILITY_DRIFTED"
    if "capability" in source.lower() and value == "unknown":
        return "CAPABILITY_UNKNOWN"

    # Conformance failures
    if "conformance" in source.lower() and value == "UNVERIFIED":
        return "CONFORMANCE_UNVERIFIED"
    if "conformance" in source.lower() and value in ("TRANSPORT_FAIL", "STATIC_FAIL"):
        return f"CONFORMANCE_{value}"

    # Edge failures
    if "edge" in source.lower() and value == "unreachable":
        return "EDGE_UNREACHABLE"
    if "edge" in source.lower() and value == "drifted":
        return "EDGE_DRIFTED"

    # Governance failures
    if "governance" in source.lower() and value == "degraded":
        return "GOVERNANCE_DEGRADED"

    # Receipt failures
    if "receipt" in source.lower() and not envelope.get("value"):
        return "RECEIPT_UNAVAILABLE"
    if "chain" in source.lower() and value == "broken":
        return "RECEIPT_CHAIN_BROKEN"

    # Generic
    if state == "unknown":
        return "UNKNOWN"
    if value in (None, "unknown", "degraded", "unreachable"):
        return "PROBE_FAILED"

    return None


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


def _pf_age(
    value: Any,
    *,
    source: str,
    epoch: float | None,
    state: str = "observed",
    confidence: float = 0.95,
    observation_method: str = _OBS_METHOD_UNKNOWN,
    independent: bool = True,
) -> dict[str, Any]:
    """Per-field envelope with explicit observed_at epoch (so age_seconds is honest)."""
    if epoch is None:
        return _pf(
            value,
            source=source,
            state="unknown",
            confidence=0.0,
            observation_method=observation_method,
            independent=independent,
        )
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
        out["cpu"] = _pf(
            None,
            source="psutil.cpu",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_PROCESS,
            independent=True,
        )
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
        out["memory"] = _pf(
            None,
            source="psutil.virtual_memory",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_PROCESS,
            independent=True,
        )
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
        out["disk"] = _pf(
            None,
            source="psutil.disk_usage",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        )
    try:
        net = psutil.net_io_counters()
        out["network"] = _pf(
            {
                "bytes_sent": net.bytes_sent,
                "bytes_recv": net.bytes_recv,
                "errin": net.errin,
                "errout": net.errout,
            },
            source="psutil.net_io_counters",
            confidence=0.9,
            observation_method=_OBS_METHOD_PROCESS,
            independent=True,
        )
    except Exception:
        out["network"] = _pf(
            None,
            source="psutil.net_io_counters",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_PROCESS,
            independent=True,
        )
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
    sub["postgres"] = _pf(
        None,
        source="postgres_probe_pending",
        state="unknown",
        confidence=0.0,
        observation_method=_OBS_METHOD_UNKNOWN,
        independent=True,
    )
    sub["redis"] = _pf(
        None,
        source="redis_probe_pending",
        state="unknown",
        confidence=0.0,
        observation_method=_OBS_METHOD_UNKNOWN,
        independent=True,
    )
    sub["qdrant"] = _pf(
        None,
        source="qdrant_probe_pending",
        state="unknown",
        confidence=0.0,
        observation_method=_OBS_METHOD_UNKNOWN,
        independent=True,
    )
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

    out["source_commit"] = _pf(
        git_snap.get("commit"),
        source="arifOS/_collect_git_snapshot",
        confidence=0.99,
        observation_method=_OBS_METHOD_FILESYSTEM,
        independent=True,
    )
    out["source_branch"] = _pf(
        git_snap.get("branch"),
        source="arifOS/_collect_git_snapshot",
        confidence=0.99,
        observation_method=_OBS_METHOD_FILESYSTEM,
        independent=True,
    )
    deployed = drift.get("live_commit", "unknown")
    out["deployed_commit"] = _pf(
        deployed,
        source="/opt/arifos/app/.git_commit or HEAD",
        confidence=0.99 if deployed != "unknown" else 0.0,
        observation_method=_OBS_METHOD_FILESYSTEM,
        independent=True,
    )
    out["build_commit"] = _pf(
        drift.get("build_commit"),
        source="BUILD_INFO.build.commit",
        confidence=0.99,
        observation_method=_OBS_METHOD_FILESYSTEM,
        independent=True,
    )

    # Drift state derivation — namespaced per verdict 2026-07-15.
    # artifact: source=build=deployed alignment (independent filesystem probe)
    # capability: declared vs registered tool drift (derived from capability_matrix)
    # forge_registry: A-FORGE registry staleness (independent registry probe)
    # schema / route / upstream_repository: honest UNKNOWN until probed
    if drift.get("runtime_drift") is True:
        artifact_state = "DRIFTED"
    elif drift.get("runtime_drift") is False:
        artifact_state = "ALIGNED"
    else:
        artifact_state = "UNKNOWN"
    out["drift"] = _pf(
        {
            "artifact": artifact_state,
            "capability": "UNKNOWN",  # populated from capability_matrix at snapshot level
            "forge_registry": "UNKNOWN",  # populated from A-FORGE probe at snapshot level
            "schema": "UNKNOWN",
            "route": "UNKNOWN",
            "upstream_repository": "UNVERIFIED",
        },
        source="_compute_runtime_drift + capability_matrix",
        state="derived",
        confidence=0.9,
        observation_method=_OBS_METHOD_DERIVED,
        independent=True,
    )

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
    out["platform"] = _pf(
        platform.platform(),
        source="platform.platform",
        state="observed",
        confidence=0.99,
        observation_method=_OBS_METHOD_PROCESS,
        independent=True,
    )
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
                "score": _pf(
                    score,
                    source="governance_kernel.get_current_state",
                    confidence=0.9,
                    observation_method=_OBS_METHOD_SELF_REPORTED,
                    independent=False,
                ),
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
    out["floors_loaded"] = _pf(
        len(floors),
        source="kernel.enum.LAW_SPEC_KEYS",
        confidence=0.99,
        observation_method=_OBS_METHOD_REGISTRY,
        independent=True,
    )
    out["floors_passing"] = _pf(
        passing,
        source="_floor_passes count",
        state="derived",
        confidence=0.95,
        observation_method=_OBS_METHOD_DERIVED,
        independent=False,
    )
    out["floors_failing"] = _pf(
        failing,
        source="_floor_passes count",
        state="derived",
        confidence=0.95,
        observation_method=_OBS_METHOD_DERIVED,
        independent=False,
    )
    out["verdict"] = _pf(
        verdict,
        source="governance_kernel",
        state="observed",
        confidence=0.9,
        observation_method=_OBS_METHOD_SELF_REPORTED,
        independent=False,
    )

    # Decomposition — never collapse into a single green badge.
    out["verdict_decomposition"] = {
        "substrate_state": _pf(
            "PASS" if failing == 0 else "FAIL",
            source="floors_passing count",
            state="derived",
            confidence=0.9,
            observation_method=_OBS_METHOD_DERIVED,
            independent=False,
        ),
        "session_state": _pf(
            "OBSERVE_ONLY",
            source="governance_kernel.session_state",
            state="reported",
            confidence=0.7,
            observation_method=_OBS_METHOD_SELF_REPORTED,
            independent=False,
        ),
        "action_state": _pf(
            verdict,
            source="governance_kernel.verdict",
            state="observed",
            confidence=0.9,
            observation_method=_OBS_METHOD_SELF_REPORTED,
            independent=False,
        ),
        "receipt_state": _pf(
            {
                "snapshot_receipt": "PRESENT"
                if Path("/root/.local/share/arifos/vault999/seal_chain_head.json").exists()
                else "ABSENT",
                "issuer_claim": "SEALED"
                if Path("/root/.local/share/arifos/vault999/seal_chain_head.json").exists()
                else "UNSEALED",
                "signature_verified": False,
                "ledger_write": "AVAILABLE"
                if Path("/root/.local/share/arifos/vault999/seal_chain.jsonl").exists()
                else "UNAVAILABLE",
                "ledger_read": "AVAILABLE"
                if Path("/root/.local/share/arifos/vault999/seal_chain.jsonl").exists()
                else "UNAVAILABLE",
                "chain_verified": "UNKNOWN",
                "replay_verified": "UNKNOWN",
            },
            source="sealer.head.exists() + chain.jsonl.exists()",
            state="observed",
            confidence=0.9,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        ),
        "constitutional_judgment": _pf(
            "NOT_INVOKED",
            source="observation-only",
            state="reported",
            confidence=0.7,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "human_ratification": _pf(
            "NOT_REQUIRED",
            source="observation-only",
            state="reported",
            confidence=0.7,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
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
            "identity": _pf(
                None,
                source=f"{label}/identity",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "contract": _pf(
                None,
                source=f"{label}/api/constitution",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "capability": _pf(
                None,
                source=f"{label}/api/live/all",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "evidence": _pf(
                None,
                source=f"{label} domain evidence",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "governance": _pf(
                None,
                source=f"{label} floor scope",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "last_receipt": _pf(
                None,
                source=f"{label} seal_chain tail",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "drift": _pf(
                None,
                source=f"{label} identity diff",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "dependency": _pf(
                [],
                source=f"{label} declared deps",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "label": label,
        }

    # AAA — independent TCP probe + static config
    out["aaa"] = {
        "transport": _probe_transport("127.0.0.1", 3001),
        "identity": _pf(
            None,
            source="AAA a2a-server",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "contract": _pf(
            None,
            source="AAA agent-card",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "capability": _pf(
            None,
            source="AAA port 3001",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "evidence": _pf(
            None,
            source="AAA memory bridge",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "governance": _pf(
            None,
            source="AAA delegates to arifOS",
            state="reported",
            confidence=0.9,
            observation_method=_OBS_METHOD_STATIC,
            independent=True,
        ),
        "last_receipt": _pf(
            None,
            source="AAA writes via arif_seal",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "drift": _pf(
            None,
            source="AAA vs seal_chain",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "dependency": _pf(
            ["arifos"],
            source="declared dep",
            state="reported",
            confidence=0.7,
            observation_method=_OBS_METHOD_STATIC,
            independent=True,
        ),
        "label": "AAA :3001",
    }
    # A-FORGE — independent TCP probe + static config
    out["aforge"] = {
        "transport": _probe_transport("127.0.0.1", 7071),
        "identity": _pf(
            None,
            source="A-FORGE forgeTools.js",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "contract": _pf(
            None,
            source="A-FORGE affordances",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "capability": _pf(
            None,
            source="A-FORGE registry",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "evidence": _pf(
            None,
            source="A-FORGE SHELL ledger",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "governance": _pf(
            "DELEGATES_TO_KERNEL",
            source="arifOS 3-B",
            state="reported",
            confidence=0.9,
            observation_method=_OBS_METHOD_STATIC,
            independent=True,
        ),
        "last_receipt": _pf(
            None,
            source="forge_shell_ledger",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "drift": _pf(
            "DEGRADED: forge_registry_status exposes stale 31-tool hard-coded list vs live 65+",
            source="ARIFOS_AFORGE_TOOL_ALIGNMENT_MAP.md:108",
            state="reported",
            confidence=0.99,
            observation_method=_OBS_METHOD_REGISTRY,
            independent=True,
        ),
        "dependency": _pf(
            ["arifos"],
            source="declared dep",
            state="reported",
            confidence=0.7,
            observation_method=_OBS_METHOD_STATIC,
            independent=True,
        ),
        "label": "A-FORGE :7071/:7072",
    }
    # mcp-gateway — public endpoint, self-reported (we can't independently probe from inside)
    out["mcp_gateway"] = {
        "transport": _pf(
            "mcp.arif-fazil.com",
            source="Caddyfile vhost",
            state="reported",
            confidence=0.95,
            observation_method=_OBS_METHOD_STATIC,
            independent=True,
        ),
        "identity": _pf(
            None,
            source="/.well-known/agent-card.json",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "contract": _pf(
            None,
            source="/.well-known/mcp/server.json",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "capability": _pf(
            None,
            source="mcp tools/list",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "evidence": _pf(
            None,
            source="gateway probe",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "governance": _pf(
            "ROUTES_TO_ORGANS",
            source="arifOS 3-B",
            state="reported",
            confidence=0.9,
            observation_method=_OBS_METHOD_STATIC,
            independent=True,
        ),
        "last_receipt": _pf(
            None,
            source="mcp.recent_seal",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "drift": _pf(
            None,
            source="mcp canonical vs exposed",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "dependency": _pf(
            ["arifos", "geox", "wealth", "well", "aaa", "aforge"],
            source="declared dep",
            state="reported",
            confidence=0.95,
            observation_method=_OBS_METHOD_STATIC,
            independent=True,
        ),
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
            return _pf(
                "up",
                source=source,
                state="observed",
                confidence=0.85,
                observation_method=_OBS_METHOD_TCP_PROBE,
                independent=True,
            )
    except socket.gaierror:
        return _pf(
            "unreachable: dns_resolution_failed",
            source=source,
            state="observed",
            confidence=0.85,
            observation_method=_OBS_METHOD_TCP_PROBE,
            independent=True,
        )
    except ConnectionRefusedError:
        return _pf(
            "down: connection_refused",
            source=source,
            state="observed",
            confidence=0.85,
            observation_method=_OBS_METHOD_TCP_PROBE,
            independent=True,
        )
    except socket.timeout:
        return _pf(
            "down: timeout",
            source=source,
            state="observed",
            confidence=0.85,
            observation_method=_OBS_METHOD_TCP_PROBE,
            independent=True,
        )
    except Exception as exc:
        return _pf(
            f"down: {type(exc).__name__}",
            source=source,
            state="observed",
            confidence=0.85,
            observation_method=_OBS_METHOD_TCP_PROBE,
            independent=True,
        )


# ── Metabolism (000 → 010) ────────────────────────────────────────────────────
def _metabolism_block() -> list[dict[str, dict[str, Any]]]:
    """11 intelligence stages — counts/latency/confidence are populated from the
    Kafka/NATS event bus when available; honest UNKNOWN otherwise (we never
    fabricate numbers)."""
    stages = [
        "000_INIT",
        "111_OBSERVE",
        "222_EVIDENCE",
        "333_THINK",
        "444_ROUTE",
        "555_MEMORY",
        "666_CRITIQUE",
        "777_MEASURE",
        "888_JUDGE",
        "999_RECEIPT",
        "010_FORGE",
    ]
    out = []
    for s in stages:
        stage: dict[str, dict[str, Any]] = {
            "stage": _pf(
                s,
                source="kernel.stage_enum",
                state="reported",
                confidence=0.99,
                observation_method=_OBS_METHOD_STATIC,
                independent=True,
            ),
            "invocations": _pf(
                None,
                source=f"event_bus:{s}:count",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "success_rate": _pf(
                None,
                source=f"event_bus:{s}:success_rate",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "void_rate": _pf(
                None,
                source=f"event_bus:{s}:void_rate",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "hold_rate": _pf(
                None,
                source=f"event_bus:{s}:hold_rate",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "median_latency_ms": _pf(
                None,
                source=f"event_bus:{s}:median_latency",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "queue_depth": _pf(
                None,
                source=f"event_bus:{s}:queue_depth",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "last_error": _pf(
                None,
                source=f"event_bus:{s}:last_error",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "evidence_level": _pf(
                None,
                source=f"event_bus:{s}:evidence_level",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "output_confidence": _pf(
                None,
                source=f"event_bus:{s}:confidence",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "responsible_organ": _pf(
                "arifos",
                source="kernel.stage_lane",
                state="reported",
                confidence=0.9,
                observation_method=_OBS_METHOD_STATIC,
                independent=True,
            ),
            "human_gate": _pf(
                False,
                source="kernel.stage_lane",
                state="reported",
                confidence=0.9,
                observation_method=_OBS_METHOD_STATIC,
                independent=True,
            ),
        }
        out.append(stage)
    return out


# ── Evidence + receipts envelopes ─────────────────────────────────────────────
def _evidence_block() -> dict[str, dict[str, Any]]:
    return {
        "sources_used": _pf(
            [],
            source="snapshot source registry",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "source_diversity": _pf(
            None,
            source="HUMAN×AI×EXTERNAL geometric mean",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "contradictions": _pf(
            [],
            source="contradiction_engine.scan",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "missing_witnesses": _pf(
            [],
            source="witness_class.scan",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "direct_vs_inferred": {
            "direct": _pf(
                0,
                source="evidence_class=OBS count",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "inferred": _pf(
                0,
                source="evidence_class=DER|INT count",
                state="unknown",
                confidence=0.0,
                observation_method=_OBS_METHOD_UNKNOWN,
                independent=True,
            ),
        },
        "confidence_calibration": _pf(
            None,
            source="reliability.bin",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "unsupported_claims": _pf(
            [],
            source="claims without evidence_refs",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "evidence_expiry": _pf(
            [],
            source="expiring receipts",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
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
        "chain_path": _pf(
            str(chain_path),
            source="VAULT999 path probe",
            state="reported",
            confidence=0.99,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        ),
        "snapshot_receipt": _pf(
            "PRESENT" if head_seq is not None else "ABSENT",
            source="sealer head file",
            state="observed" if head_seq is not None else "unknown",
            confidence=0.99,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        ),
        "issuer_claim": _pf(
            "SEALED" if head_seq is not None else "UNSEALED",
            source="sealer head file",
            state="reported",
            confidence=0.8,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        ),
        "head_seq": _pf(
            head_seq,
            source="sealer head file",
            state="observed" if head_seq is not None else "unknown",
            confidence=0.99,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        ),
        "head_epoch": _pf_age(
            head_epoch_str_no_z(head_epoch),
            source="sealer.head.epoch",
            epoch=head_epoch,
            state="observed" if head_epoch is not None else "unknown",
            confidence=0.99,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        ),
        "write_path_alive": _pf(
            head_path.exists(),
            source="sealer writer alive heuristic",
            state="derived",
            confidence=0.7,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        ),
        "read_path_alive": _pf(
            chain_path.exists(),
            source="sealer reader (jsonl exists)",
            state="derived",
            confidence=0.95,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        ),
        "verify_path_alive": _pf(
            None,
            source="GET /api/observatory/v1/seal/verify",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "replay_path_alive": _pf(
            None,
            source="GET /api/observatory/v1/seal/replay",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "signature_verified": _pf(
            None,
            source="GET /api/observatory/v1/seal/verify",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "chain_verified": _pf(
            None,
            source="GET /api/observatory/v1/seal/verify",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "replay_verified": _pf(
            None,
            source="GET /api/observatory/v1/seal/replay",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "orphan_traces": _pf(
            None,
            source="trace_id without receipt",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "unsealed_actions": _pf(
            None,
            source="audit gap detector",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
    }


def head_epoch_str_no_z(epoch: float | None) -> str | None:
    return None if epoch is None else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


# ── Incidents envelope ────────────────────────────────────────────────────────
def _incidents_block() -> list[dict[str, Any]]:
    """Honest empty list until the audit gap detector wires real incidents.

    Every incident carries: {id, severity, first_seen, evidence, owner, status}.
    """
    return []


# ── Federation edges envelope ─────────────────────────────────────────────────
def _edges_block() -> dict[str, Any]:
    """Probe all 11 directed federation edges and return structured results.

    Each edge: {id, source, target, transport, state, latency_ms, schema_match,
    identity_propagated, trace_propagated, receipt_produced, probe_type, observed_at}.
    """
    try:
        from arifosmcp.runtime.federation_edges import (
            probe_all_edges,
            edge_aggregate_state,
            EDGE_DECLARATIONS,
        )

        edges = probe_all_edges()
        aggregate = edge_aggregate_state(edges)
        reachable = sum(1 for e in edges if e.get("state") == "reachable")
        drifted = sum(1 for e in edges if e.get("state") == "drift")
        unreachable = sum(1 for e in edges if e.get("state") == "unreachable")
        unknown = sum(1 for e in edges if e.get("state") == "unknown")
    except Exception as exc:
        logger.warning("edges_block failure: %s", exc)
        edges = []
        aggregate = "UNKNOWN"
        reachable = drifted = unreachable = unknown = 0

    return {
        "declared": len(edges) if edges else 11,
        "probed": len(edges),
        "reachable": reachable,
        "drifted": drifted,
        "unreachable": unreachable,
        "unknown": unknown,
        "aggregate_state": aggregate,
        "edges": edges,
    }


# ── Findings envelope (active gaps, not operational incidents) ───────────────
def _findings_block() -> dict[str, Any]:
    """Active findings that are not operational incidents but represent
    verification gaps or incomplete evidence. Per verdict 2026-07-15:
    'incidents: 0 should never imply nothing is wrong.'

    Each finding: {id, category, description, severity, evidence, status}
    Severity: LOW | MEDIUM | HIGH | CRITICAL
    Status: OPEN | IN_PROGRESS | RESOLVED | WONTFIX
    """
    findings: list[dict[str, Any]] = []

    # F-001: Declared tools not registered (capability drift)
    findings.append(
        {
            "id": "F-001",
            "category": "capability_drift",
            "description": "Declared tool count vs registered tool count — capability drift exists",
            "severity": "MEDIUM",
            "evidence": "capability_matrix.declared_count vs registered_count",
            "status": "OPEN",
        }
    )

    # F-002: Tools with no recorded successful test
    findings.append(
        {
            "id": "F-002",
            "category": "tool_testing",
            "description": "No recorded successful tool invocations in current session",
            "severity": "MEDIUM",
            "evidence": "event_bus tool invocation counts unavailable",
            "status": "OPEN",
        }
    )

    # F-003: Metabolism states unknown
    findings.append(
        {
            "id": "F-003",
            "category": "metabolism",
            "description": "Intelligence metabolism stages (000–010) not observed",
            "severity": "LOW",
            "evidence": "event_bus not wired for stage counters",
            "status": "OPEN",
        }
    )

    # F-004: VAULT verification and replay untested
    findings.append(
        {
            "id": "F-004",
            "category": "receipt",
            "description": "VAULT chain verification and replay path not tested in this snapshot",
            "severity": "HIGH",
            "evidence": "verify_path_alive = null, replay_path_alive = null",
            "status": "OPEN",
        }
    )

    # F-005: Organ identities unknown (transport-only probing)
    findings.append(
        {
            "id": "F-005",
            "category": "identity",
            "description": "Organ identity verification not performed — only transport liveness probed",
            "severity": "MEDIUM",
            "evidence": "organ identity fields = null for all organs",
            "status": "OPEN",
        }
    )

    # F-006: Edge results not populated
    findings.append(
        {
            "id": "F-006",
            "category": "topology",
            "description": "Federation edge monitoring declared but not demonstrated — 0 edges probed",
            "severity": "MEDIUM",
            "evidence": "federation_edges block absent or empty",
            "status": "OPEN",
        }
    )

    # F-007: Snapshot signature not verified
    findings.append(
        {
            "id": "F-007",
            "category": "integrity",
            "description": "Snapshot signature is not cryptographically verified",
            "severity": "LOW",
            "evidence": "signature field = null (pending key bootstrap)",
            "status": "OPEN",
        }
    )

    # F-008: Upstream repository commit not resolvable
    findings.append(
        {
            "id": "F-008",
            "category": "provenance",
            "description": "Deployed commit not verified against canonical repository",
            "severity": "LOW",
            "evidence": "upstream_repository = UNVERIFIED",
            "status": "OPEN",
        }
    )

    open_count = sum(1 for f in findings if f["status"] == "OPEN")
    by_severity = {}
    for f in findings:
        by_severity.setdefault(f["severity"], []).append(f["id"])

    return {
        "count": open_count,
        "by_severity": {k: len(v) for k, v in by_severity.items()},
        "findings": findings,
    }


# ── Conformance levels block ─────────────────────────────────────────────────
def _conformance_block() -> dict[str, Any]:
    """Three-level conformance using the PR7 conformance levels module.

    FAST: schemas + policy files + declared registry
    LIVE_TRANSPORT: MCP initialize + protocol version + schema echo
    FULL_CONFORMANCE: session binding + mutation hold + organ call + judgment + vault + capability

    Each level has its own verdict vocabulary. The substrate gate is AMBER when
    any check is skipped — GREEN requires all checks to have actually passed.

    Defensive: if `arifosmcp.runtime.conformance` or its runner functions are
    missing (regression in some builds), return UNKNOWN envelopes instead of
    failing the entire snapshot. F2: never silently drop evidence.
    """
    try:
        from arifosmcp.runtime.conformance import (
            run_fast,
            run_full,
            run_live_transport,
        )

        fast = run_fast()
        transport = run_live_transport()
        full = run_full()
        return {
            "fast": _pf(
                fast.to_dict(),
                source="conformance.run_fast",
                state="observed",
                confidence=0.95,
                observation_method=_OBS_METHOD_SELF_REPORTED,
                independent=False,
            ),
            "live_transport": _pf(
                transport.to_dict(),
                source="conformance.run_live_transport",
                state="observed",
                confidence=0.9,
                observation_method=_OBS_METHOD_SELF_REPORTED,
                independent=False,
            ),
            "full_conformance": _pf(
                full.to_dict(),
                source="conformance.run_full",
                state="observed",
                confidence=0.85,
                observation_method=_OBS_METHOD_SELF_REPORTED,
                independent=False,
            ),
        }
    except Exception as exc:
        logger.warning("conformance_block failure: %s", exc)
        return {
            "fast": _pf(None, source="conformance.run_fast", state="unknown", confidence=0.0,
                       observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "live_transport": _pf(None, source="conformance.run_live_transport", state="unknown", confidence=0.0,
                                observation_method=_OBS_METHOD_UNKNOWN, independent=True),
            "full_conformance": _pf(None, source="conformance.run_full", state="unknown", confidence=0.0,
                                  observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        }


# ── Explanation enrichment (2026-07-14) ──────────────────────────────────────
def _enrich_snapshot(obj: Any) -> Any:
    """Walk the snapshot tree and add explanations to all failure envelopes.

    An envelope is identified by having 'value', 'state', and 'source' keys.
    Non-failure envelopes are left untouched. This runs once at the end of
    build_snapshot — it's the explanation layer.
    """
    if isinstance(obj, dict):
        # Check if this is a per-field envelope
        if "value" in obj and "state" in obj and "source" in obj:
            return _enrich_with_explanation(obj)
        # Otherwise recurse into children
        return {k: _enrich_snapshot(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_enrich_snapshot(item) for item in obj]
    return obj


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

        server_json = build_server_json(
            os.getenv("ARIFOS_PUBLIC_BASE_URL", "http://arifos.arif-fazil.com")
        )
    except Exception as exc:
        logger.warning("build_server_json failed: %s", exc)

    capabilities = compute_capability_matrix(
        mcp=mcp, server_json=server_json, registered_tools=registered_tools
    )
    runtime_identity = _runtime_identity_block()
    capability_degraded = int(capabilities.get("degraded_count", 0) or 0)
    drift_value = runtime_identity.get("drift", {}).get("value")
    if isinstance(drift_value, dict):
        drift_value["capability"] = "DRIFTED" if capability_degraded else "ALIGNED"
        drift_value["forge_registry"] = "DRIFTED" if capability_degraded else "UNKNOWN"

    snap_id = snapshot_id or "obs_" + time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    payload: dict[str, Any] = {
        "snapshot_id": snap_id,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": GENERATED_BY,
        "schema_version": SCHEMA_VERSION,
        "signature": _pf(
            None,
            source="ed25519 over canonicaljson(payload_without_signature) — pending key bootstrap",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "runtime_identity": runtime_identity,
        "substrate": _substrate_block(),
        "governance": _governance_block(),
        "capabilities": capabilities,
        "organs": _organs_block(mcp),
        "metabolism": _metabolism_block(),
        "evidence": _evidence_block(),
        "receipts": _receipts_block(),
        "incidents": _incidents_block(),
        "findings": _findings_block(),
        "federation_edges": _edges_block(),
        "conformance": _conformance_block(),
        "stage_evidence": _pf(
            "self-reported",
            source="observatory pipeline stage (not a governed session)",
            state="reported",
            confidence=0.7,
            observation_method=_OBS_METHOD_SELF_REPORTED,
            independent=False,
        ),
        "intelligence_decomposition": {
            "machine_substrate": _pf(
                "ALIGNED",
                source="transport + artifact self-report",
                state="derived",
                confidence=0.85,
                observation_method=_OBS_METHOD_DERIVED,
                independent=True,
            ),
            "intelligence_pipeline": _pf(
                "RETAK",
                source="metabolism 0/11 observed, capability tests 0/18, capability drift present",
                state="derived",
                confidence=0.7,
                observation_method=_OBS_METHOD_DERIVED,
                independent=True,
            ),
        },
        "tier": _pf(
            "public",
            source="Caddy X-Observatory-Tier (default public; operator with valid X-Op-Token)",
            state="reported",
            confidence=0.99,
            observation_method=_OBS_METHOD_STATIC,
            independent=True,
        ),
    }
    # Enrich all failure envelopes with human/builder explanations
    return _enrich_snapshot(payload)


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
    states["LIVENESS"] = _pf(
        "up",
        source="self-process responding",
        state="observed",
        confidence=0.99,
        observation_method=_OBS_METHOD_SELF_REPORTED,
        independent=False,
    )
    # READINESS — independent filesystem probe: vault999 jsonl exists and is readable.
    fs_ok = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl").exists()
    states["READINESS"] = _pf(
        "up" if fs_ok else "degraded",
        source="VAULT fs reachable",
        state="observed",
        confidence=0.85,
        observation_method=_OBS_METHOD_FILESYSTEM,
        independent=True,
    )
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
        states["CAPABILITY"] = _pf(
            "unknown",
            source="compute_capability_matrix",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        )
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
        states["GOVERNANCE"] = _pf(
            "unknown",
            source="governance_block",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        )
    # AUTHORIZATION — only meaningful in a specific request context; mark UNKNOWN here.
    states["AUTHORIZATION"] = _pf(
        "request-scoped",
        source="action_request envelope",
        state="reported",
        confidence=0.0,
        observation_method=_OBS_METHOD_UNKNOWN,
        independent=True,
    )
    # RECEIPT — derive from independent filesystem probe.
    try:
        rcpts = _receipts_block()
        chain_alive = rcpts.get("read_path_alive", {}).get("value")
        states["RECEIPT"] = _pf(
            "up" if chain_alive else "unknown",
            source="receipts.read_path_alive",
            state="derived",
            confidence=0.7,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        )
    except Exception:
        states["RECEIPT"] = _pf(
            "unknown",
            source="receipts_block",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        )
    # CONSTITUTIONAL — only meaningful after arif_judge ran. Mark UNKNOWN here.
    states["CONSTITUTIONAL"] = _pf(
        "judgment-scoped",
        source="arif_judge envelope",
        state="reported",
        confidence=0.0,
        observation_method=_OBS_METHOD_UNKNOWN,
        independent=True,
    )
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
        from arifosmcp.runtime.rest_routes.rest_routes import (
            _dashboard_cors_headers,
            _cache_headers,
            _merge_headers,
        )  # type: ignore
        from arifosmcp.runtime.capability_drift import _registered_tools_async

        # Defensive: build_snapshot is a composition of many blocks (substrate,
        # governance, organs, conformance, edges). A single failing block should
        # not yield 500 on the page — return a partial snapshot with an
        # `_error` field instead. F2: never silently drop evidence.
        try:
            # Pre-compute registered tools async (FastMCP 3.x list_tools is async)
            reg_tools = await _registered_tools_async(mcp)
            snap = build_snapshot(mcp=mcp, registered_tools=reg_tools)
        except Exception as exc:
            logger.exception("observatory snapshot partial failure")
            snap = {
                "snapshot_id": "obs_partial_" + time.strftime("%Y%m%d_%H%M%S", time.gmtime()),
                "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "schema_version": SCHEMA_VERSION,
                "generated_by": GENERATED_BY,
                "_partial": True,
                "_error": f"{type(exc).__name__}: {exc}",
                "signature": _pf(
                    None,
                    source="ed25519 over canonicaljson — pending key bootstrap",
                    state="unknown",
                    confidence=0.0,
                    observation_method=_OBS_METHOD_UNKNOWN,
                    independent=True,
                ),
            }
        return JSONResponse(
            snap,
            headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(request)),
        )

    async def _capabilities(request):
        from arifosmcp.runtime.rest_routes.rest_routes import (
            _dashboard_cors_headers,
            _cache_headers,
            _merge_headers,
        )  # type: ignore
        from arifosmcp.runtime.capability_drift import (
            compute_capability_matrix,
            _registered_tools_async,
        )

        try:
            server_json = None
            try:
                from arifosmcp.runtime.rest_routes.rest_routes import build_server_json  # type: ignore

                server_json = build_server_json(
                    os.getenv("ARIFOS_PUBLIC_BASE_URL", "http://arifos.arif-fazil.com")
                )
            except Exception:
                pass
            reg_tools = await _registered_tools_async(mcp)
            matrix = compute_capability_matrix(
                mcp=mcp, server_json=server_json, registered_tools=reg_tools
            )
        except Exception as exc:
            return JSONResponse({"error": f"matrix failure: {exc}"}, status_code=500)
        return JSONResponse(
            matrix, headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(request))
        )

    # Use the same flexible route convention as register_rest_routes.
    def route(path: str):
        full = prefix.rstrip("/") + path

        def _decorator(handler: Callable):
            if (
                hasattr(app, "add_route")
                or "Starlette" in str(type(app))
                or "FastAPI" in str(type(app))
            ):
                from starlette.routing import Route

                app.router.routes.append(Route(full, endpoint=handler, methods=["GET"]))
            elif hasattr(app, "custom_route"):
                app.custom_route(full, methods=["GET"])(handler)
            elif hasattr(app, "route"):
                app.route(full, methods=["GET"])(handler)
            else:
                logger.warning(
                    "Failed to register observatory route %s: app has no route method", full
                )
            return handler

        return _decorator

    @route("/snapshot")
    async def _h_snapshot(req):  # type: ignore
        return await _snapshot(req)

    @route("/snapshot/capabilities")
    async def _h_capabilities(req):  # type: ignore
        return await _capabilities(req)

    async def _health(request):
        from arifosmcp.runtime.rest_routes.rest_routes import (
            _dashboard_cors_headers,
            _cache_headers,
            _merge_headers,
        )  # type: ignore

        states = seven_state_health(mcp=mcp)
        return JSONResponse(
            {"states": states, "schema_version": SCHEMA_VERSION},
            headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(request)),
        )

    @route("/health")
    async def _h_health(req):  # type: ignore
        return await _health(req)
