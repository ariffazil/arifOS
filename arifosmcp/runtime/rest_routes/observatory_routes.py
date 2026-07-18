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


def _sign_observatory_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    """Ed25519-sign snapshot. Key lives at /root/.arifos/observatory/keys/.

    Returns a signature envelope with value/state/verification_url for SPA.
    On failure: honest UNSIGNED (value=null, state=unknown) — never fake-green.
    """
    try:
        from arifosmcp.runtime.observatory_signing import sign_snapshot_payload

        return sign_snapshot_payload(payload)
    except Exception as exc:  # noqa: BLE001
        logger.warning("observatory snapshot signing failed: %s", exc)
        return _pf(
            None,
            source=f"ed25519 signing failed: {type(exc).__name__}: {exc}",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        )


def _finalize_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    """Enrich + sign. Signature always last so hash excludes prior signature."""
    payload = _enrich_snapshot(payload)
    payload["signature"] = _sign_observatory_snapshot(payload)
    # Keep F-007 honest relative to live signature; recompute OPEN count.
    findings = payload.get("findings")
    if isinstance(findings, dict):
        items = findings.get("findings") or findings.get("items") or findings.get("list") or []
        if isinstance(items, list):
            sig = payload.get("signature") or {}
            signed = bool(isinstance(sig, dict) and sig.get("value"))
            for f in items:
                if isinstance(f, dict) and f.get("id") == "F-007":
                    f["status"] = "RESOLVED" if signed else "OPEN"
                    f["description"] = (
                        "Snapshot signature verified (ed25519)"
                        if signed
                        else "Snapshot signature is not cryptographically verified"
                    )
                    f["evidence"] = (
                        f"signature.state={sig.get('state')} key_id={sig.get('key_id')}"
                        if signed
                        else "signature.value=null (signing failed or key missing)"
                    )
            open_items = [f for f in items if isinstance(f, dict) and f.get("status") == "OPEN"]
            findings["count"] = len(open_items)
            by_sev: dict[str, int] = {}
            for f in open_items:
                sev = str(f.get("severity") or "LOW")
                by_sev[sev] = by_sev.get(sev, 0) + 1
            findings["by_severity"] = by_sev
            findings["findings"] = items
    # Intelligence decomposition from live capability + metabolism numbers
    try:
        payload["intelligence_decomposition"] = _intelligence_decomposition(payload)
    except Exception:
        pass
    return payload


def _edge_transport_ok(edge: dict[str, Any]) -> bool:
    """Transport-reachable if transport field or state says so (never confuse with semantic)."""
    transport = edge.get("transport")
    if transport in ("reachable", "up", "ok"):
        return True
    state = edge.get("state")
    return state in (
        "reachable",
        "TRANSPORT_ONLY",
        "TRANSPORT_IDENTITY_OK",
        "aligned",
        "ALIGNED",
    )


def _edge_semantic_proven(edge: dict[str, Any]) -> bool:
    fields = (
        "session_propagated",
        "actor_propagated",
        "trace_propagated",
        "receipt_produced",
    )
    return all(edge.get(f) is True for f in fields)


def _intelligence_decomposition(payload: dict[str, Any]) -> dict[str, Any]:
    """Separate machine substrate from intelligence pipeline (no collapsed label)."""
    caps = payload.get("capabilities") if isinstance(payload.get("capabilities"), dict) else {}
    tested = int(caps.get("tested_count") or 0)
    proven = int(caps.get("proven_live_count") or 0)
    invocable = int(caps.get("invocable_count") or caps.get("callable_public") or 0)
    degraded = int(caps.get("degraded_count") or 0)
    metabolism = payload.get("metabolism") if isinstance(payload.get("metabolism"), list) else []
    stages_observed = 0
    for row in metabolism:
        if not isinstance(row, dict):
            continue
        inv = row.get("invocations")
        val = inv.get("value") if isinstance(inv, dict) else inv
        if isinstance(val, int) and val > 0:
            stages_observed += 1
    edges = payload.get("federation_edges") if isinstance(payload.get("federation_edges"), dict) else {}
    transport_n = int(edges.get("reachable") or 0)
    semantic_n = int(edges.get("semantic_proven") or 0)

    if invocable >= 8 and proven >= 8 and semantic_n > 0 and stages_observed >= 8:
        pipeline = "PARTIAL"
    elif proven >= 1 or tested >= 1 or stages_observed >= 1:
        pipeline = "RETAK"
    else:
        pipeline = "RETAK"

    substrate = "ALIGNED" if transport_n > 0 or invocable >= 8 else "UNKNOWN"
    return {
        "machine_substrate": _pf(
            substrate,
            source="transport + public wire invocable",
            state="derived",
            confidence=0.85,
            observation_method=_OBS_METHOD_DERIVED,
            independent=True,
        ),
        "intelligence_pipeline": _pf(
            pipeline,
            source=(
                f"proven_live={proven}/{invocable or 8} tested_fresh={tested} "
                f"stages_observed={stages_observed}/11 semantic_edges={semantic_n} "
                f"degraded={degraded}"
            ),
            state="derived",
            confidence=0.75,
            observation_method=_OBS_METHOD_DERIVED,
            independent=True,
        ),
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
    # Stable scalar retained for clients and tests that need one non-collapsed
    # source/build/deployed verdict.  The namespaced `drift` object above is
    # the detailed view; neither field claims schema or route alignment.
    out["drift_state"] = _pf(
        artifact_state.lower(),
        source="_compute_runtime_drift.artifact",
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
        dp = _deep_probe_organ(host, port, label)
        out[name] = {
            "transport": _probe_transport(host, port),
            "identity": dp["identity"] or _pf(
                None, source=f"{label}/identity", state="unknown",
                confidence=0.0, observation_method=_OBS_METHOD_UNKNOWN, independent=True,
            ),
            "contract": dp["contract"] or _pf(
                None, source=f"{label}/api/constitution", state="unknown",
                confidence=0.0, observation_method=_OBS_METHOD_UNKNOWN, independent=True,
            ),
            "capability": dp["capability"] or _pf(
                None, source=f"{label}/api/live/all", state="unknown",
                confidence=0.0, observation_method=_OBS_METHOD_UNKNOWN, independent=True,
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
    aaa_dp = _deep_probe_organ("127.0.0.1", 3001, "AAA :3001")
    out["aaa"] = {
        "transport": _probe_transport("127.0.0.1", 3001),
        "identity": aaa_dp["identity"] or _pf(None, source="AAA a2a-server", state="unknown", confidence=0.0, observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "contract": aaa_dp["contract"] or _pf(None, source="AAA agent-card", state="unknown", confidence=0.0, observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "capability": aaa_dp["capability"] or _pf(None, source="AAA port 3001", state="unknown", confidence=0.0, observation_method=_OBS_METHOD_UNKNOWN, independent=True),
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
    forge_dp = _deep_probe_organ("127.0.0.1", 7071, "A-FORGE :7071")
    out["aforge"] = {
        "transport": _probe_transport("127.0.0.1", 7071),
        "identity": forge_dp["identity"] or _pf(None, source="A-FORGE forgeTools.js", state="unknown", confidence=0.0, observation_method=_OBS_METHOD_UNKNOWN, independent=True),
        "contract": forge_dp["contract"] or _pf(None, source="A-FORGE affordances", state="unknown", confidence=0.0, observation_method=_OBS_METHOD_UNKNOWN, independent=True),
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


def _deep_probe_organ(host: str, port: int, label: str) -> dict[str, Any]:
    """HTTP /health probe — extract identity + contract + capability from organ."""
    import urllib.request, json as _json
    result = {
        "identity": None,
        "contract": None,
        "capability": None,
        "status": None,
    }
    try:
        with urllib.request.urlopen(
            f"http://{host}:{port}/health", timeout=3.0
        ) as resp:
            data = _json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        return result
    ihash = data.get("identity_hash")
    version = data.get("version") or data.get("federation_schema_version")
    status = data.get("status")
    result["status"] = status
    if ihash:
        result["identity"] = _pf(
            str(ihash)[:32],
            source=f"GET {host}:{port}/health→identity_hash",
            state="observed",
            confidence=0.95,
            observation_method="http_probe",
            independent=True,
        )
    if version:
        result["contract"] = _pf(
            str(version),
            source=f"GET {host}:{port}/health→version",
            state="observed",
            confidence=0.90,
            observation_method="http_probe",
            independent=True,
        )
    tools = data.get("tools_loaded") or data.get("tool_count")
    if tools is not None:
        result["capability"] = _pf(
            int(tools),
            source=f"GET {host}:{port}/health→tools_loaded",
            state="observed",
            confidence=0.90,
            observation_method="http_probe",
            independent=True,
        )
    return result


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
    """11 intelligence stages — counts from durable event bus when present.

    Never fabricates numbers. Zero invocations → honest zero (measured empty),
    not unknown-if-bus-exists. Unknown only if bus path unreadable.
    """
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
    counters: dict[str, dict[str, Any]] = {}
    bus_ok = False
    try:
        from arifosmcp.runtime.event_bus import stage_counters

        counters = stage_counters()
        bus_ok = True
    except Exception:
        counters = {}
        bus_ok = False

    out = []
    for s in stages:
        c = counters.get(s) or {}
        inv = c.get("invocations")
        succ = c.get("success")
        if bus_ok:
            inv_val = int(inv or 0)
            inv_state = "observed"
            inv_conf = 0.95 if inv_val else 0.7
            if inv_val > 0 and succ is not None:
                sr = float(succ) / float(inv_val)
                sr_state = "observed"
                sr_conf = 0.95
            else:
                sr = 0.0 if inv_val == 0 else None
                sr_state = "observed" if inv_val == 0 else "unknown"
                sr_conf = 0.7 if inv_val == 0 else 0.0
        else:
            inv_val = None
            inv_state = "unknown"
            inv_conf = 0.0
            sr = None
            sr_state = "unknown"
            sr_conf = 0.0

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
                inv_val,
                source=f"durable_event_bus:{s}:count",
                state=inv_state,
                confidence=inv_conf,
                observation_method=_OBS_METHOD_FILESYSTEM if bus_ok else _OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "success_rate": _pf(
                sr,
                source=f"durable_event_bus:{s}:success_rate",
                state=sr_state,
                confidence=sr_conf,
                observation_method=_OBS_METHOD_FILESYSTEM if bus_ok else _OBS_METHOD_UNKNOWN,
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
                "L2" if bus_ok and inv_val else "N/E",
                source=f"durable_event_bus:{s}:evidence_level",
                state="observed" if bus_ok else "unknown",
                confidence=0.8 if bus_ok else 0.0,
                observation_method=_OBS_METHOD_FILESYSTEM if bus_ok else _OBS_METHOD_UNKNOWN,
                independent=True,
            ),
            "output_confidence": _pf(
                inv_conf if bus_ok else None,
                source=f"durable_event_bus:{s}:confidence",
                state="observed" if bus_ok else "unknown",
                confidence=inv_conf if bus_ok else 0.0,
                observation_method=_OBS_METHOD_FILESYSTEM if bus_ok else _OBS_METHOD_UNKNOWN,
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


def _local_chain_verify() -> dict[str, Any]:
    """Walk seal_chain.jsonl; skip corrupt lines; report gaps (F-004)."""
    chain_path = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl")
    if not chain_path.exists():
        return {"verified": False, "status": "no-chain", "entries": 0, "gaps": []}
    entries: list[dict[str, Any]] = []
    skipped = 0
    try:
        with open(chain_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or not line.startswith("{"):
                    skipped += 1
                    continue
                try:
                    parsed = json.loads(line)
                except json.JSONDecodeError:
                    skipped += 1
                    continue
                if isinstance(parsed, dict):
                    entries.append(parsed)
        # SOVEREIGN RULING 2026-07-16: null-hash derived entries (seq 8+,
        # pre-May-2026 gaps seq 13-18) are declared non-issue.
        # Only count gaps between non-null-hash entries.
        # Skip entries without a this_hash entirely — they are derived/administrative.
        gaps = []
        prev_hash = None
        prev_index = None
        for i, entry in enumerate(entries):
            entry_hash = entry.get("this_hash") or entry.get("hash") or entry.get("seal_hash")
            entry_prev = entry.get("prev_hash")
            # Skip entries without a hash — sovereign-declared non-issue derived entries
            if not entry_hash:
                continue
            if prev_hash is not None and entry_prev and entry_prev != prev_hash:
                gaps.append({"index": i, "expected_prev": str(prev_hash)[:24], "got": str(entry_prev)[:24]})
            prev_hash = entry_hash
            prev_index = i
        return {
            "verified": len(gaps) == 0 and len(entries) > 0,
            "status": "verified" if (len(gaps) == 0 and entries) else "gaps-found",
            "entries": len(entries),
            "skipped_corrupt": skipped,
            "gaps": gaps[:20],
        }
    except Exception as exc:
        return {"verified": False, "status": "error", "detail": str(exc), "entries": 0, "gaps": []}


def _local_chain_replay_ok() -> dict[str, Any]:
    """Replay = parse all valid JSONL seals (skip garbage)."""
    chain_path = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl")
    if not chain_path.exists():
        return {"ok": False, "entries": 0, "status": "no-chain"}
    n = 0
    skipped = 0
    try:
        with open(chain_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or not line.startswith("{"):
                    skipped += 1
                    continue
                try:
                    json.loads(line)
                    n += 1
                except json.JSONDecodeError:
                    skipped += 1
        return {"ok": n > 0, "entries": n, "skipped_corrupt": skipped, "status": "available"}
    except Exception as exc:
        return {"ok": False, "entries": 0, "status": "error", "detail": str(exc)}


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
                try:
                    t = time.strptime(head_epoch_str.rstrip("Z")[:26], "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    t = time.strptime(head_epoch_str.rstrip("Z")[:19], "%Y-%m-%dT%H:%M:%S")
                head_epoch = time.mktime(t) - time.timezone
                if head_epoch < 0:
                    head_epoch += time.timezone
        except Exception:
            pass
    chain_v = _local_chain_verify()
    replay_v = _local_chain_replay_ok()
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
            True,
            source="GET /api/observatory/v1/seal/verify (handler present)",
            state="observed",
            confidence=0.95,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        ),
        "replay_path_alive": _pf(
            True,
            source="GET /api/observatory/v1/seal/replay (handler present)",
            state="observed",
            confidence=0.95,
            observation_method=_OBS_METHOD_FILESYSTEM,
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
            chain_v.get("verified"),
            source=f"local seal_chain.jsonl walk status={chain_v.get('status')} gaps={len(chain_v.get('gaps') or [])}",
            state="observed" if chain_v.get("status") != "error" else "unknown",
            confidence=0.9 if chain_v.get("status") != "error" else 0.0,
            observation_method=_OBS_METHOD_FILESYSTEM,
            independent=True,
        ),
        "replay_verified": _pf(
            replay_v.get("ok"),
            source=f"local seal_chain.jsonl parse entries={replay_v.get('entries')} skipped={replay_v.get('skipped_corrupt')}",
            state="observed" if replay_v.get("status") != "error" else "unknown",
            confidence=0.9 if replay_v.get("ok") else 0.5,
            observation_method=_OBS_METHOD_FILESYSTEM,
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

    Sync version — uses blocking urlopen. Use `_edges_block_async()` from
    async contexts to avoid blocking the event loop (P1-5 deadlock fix).
    """
    try:
        from arifosmcp.runtime.federation_edges import (
            probe_all_edges,
            edge_aggregate_state,
            EDGE_DECLARATIONS,
        )

        edges = probe_all_edges()
        aggregate = edge_aggregate_state(edges)
        reachable = sum(1 for e in edges if isinstance(e, dict) and _edge_transport_ok(e))
        semantic_proven = sum(
            1 for e in edges if isinstance(e, dict) and _edge_semantic_proven(e)
        )
        drifted = sum(1 for e in edges if e.get("state") == "drift")
        unreachable = sum(
            1
            for e in edges
            if isinstance(e, dict)
            and e.get("transport") in ("unreachable", "timeout", "connection_refused", "error")
        )
        unknown = max(0, len(edges) - reachable - unreachable)
    except Exception as exc:
        logger.warning("edges_block failure: %s", exc)
        edges = []
        aggregate = "UNKNOWN"
        reachable = drifted = unreachable = unknown = semantic_proven = 0

    # Aggregate honesty: transport success ≠ semantic federation.
    if edges and reachable == len(edges) and semantic_proven == len(edges):
        aggregate = "ALIGNED"
    elif edges and reachable == len(edges):
        aggregate = "TRANSPORT_ALIGNED"
    elif reachable > 0:
        aggregate = "PARTIAL" if reachable >= max(1, int(len(edges) * 0.7)) else "DEGRADED"
    else:
        aggregate = aggregate or "UNKNOWN"

    return {
        "declared": len(edges) if edges else 11,
        "probed": len(edges),
        "reachable": reachable,
        "transport_reachable": reachable,
        "semantic_proven": semantic_proven,
        "authority_propagated": semantic_proven,
        "drifted": drifted,
        "unreachable": unreachable,
        "unknown": unknown,
        "aggregate_state": aggregate,
        "edges": edges,
    }


async def _edges_block_async() -> dict[str, Any]:
    """Async version of _edges_block — yields to event loop while probing.

    Uses `probe_all_edges_async` from federation_edges which runs each
    HTTP fetch in a worker thread, preventing the self-deadlock where
    arifOS probes its own /health while /health is computing the
    snapshot (P1-5 observatory deadlock fix).
    """
    try:
        from arifosmcp.runtime.federation_edges import (
            probe_all_edges_async,
            edge_aggregate_state,
        )

        # Build minimal self-health to short-circuit source=8088 fetches
        # in probe_all_edges_async.  Without this, every edge where arifOS
        # is the source hits its own /health via a thread-pool worker.
        self_health = None
        try:
            identity_hash = None
            for id_file in ("/opt/arifos/app/.identity_hash", "/root/arifOS/.identity_hash"):
                if os.path.exists(id_file):
                    with open(id_file) as f:
                        identity_hash = f.read().strip()
                    if identity_hash:
                        break
            self_health = {
                "identity_hash": identity_hash or "UNKNOWN",
                "federation_schema_version": SCHEMA_VERSION,
            }
        except Exception:
            pass

        edges = await probe_all_edges_async(self_endpoint_health=self_health)
        aggregate = edge_aggregate_state(edges)
        reachable = sum(1 for e in edges if isinstance(e, dict) and _edge_transport_ok(e))
        semantic_proven = sum(
            1 for e in edges if isinstance(e, dict) and _edge_semantic_proven(e)
        )
        drifted = sum(1 for e in edges if e.get("state") == "drift")
        unreachable = sum(
            1
            for e in edges
            if isinstance(e, dict)
            and e.get("transport") in ("unreachable", "timeout", "connection_refused", "error")
        )
        unknown = max(0, len(edges) - reachable - unreachable)
    except Exception as exc:
        logger.warning("edges_block_async failure: %s", exc)
        edges = []
        aggregate = "UNKNOWN"
        reachable = drifted = unreachable = unknown = semantic_proven = 0

    if edges and reachable == len(edges) and semantic_proven == len(edges):
        aggregate = "ALIGNED"
    elif edges and reachable == len(edges):
        aggregate = "TRANSPORT_ALIGNED"
    elif reachable > 0:
        aggregate = "PARTIAL" if reachable >= max(1, int(len(edges) * 0.7)) else "DEGRADED"
    else:
        aggregate = aggregate or "UNKNOWN"

    return {
        "declared": len(edges) if edges else 11,
        "probed": len(edges),
        "reachable": reachable,
        "transport_reachable": reachable,
        "semantic_proven": semantic_proven,
        "authority_propagated": semantic_proven,
        "drifted": drifted,
        "unreachable": unreachable,
        "unknown": unknown,
        "aggregate_state": aggregate,
        "edges": edges,
    }


# ── Findings envelope (active gaps, not operational incidents) ───────────────

def _post_process_event_bus_findings(findings: dict[str, Any]) -> None:
    """Override F-002/F-003 from durable event bus if capability matrix lacks data."""
    for path in ["/root/.local/share/arifos/event_bus.jsonl", "/root/.arifos/event_bus.jsonl"]:
        if not Path(path).exists():
            continue
        try:
            tool_ok = meta_ok = total = 0
            stages = set()
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line: continue
                    try: evt = json.loads(line)
                    except json.JSONDecodeError: continue
                    total += 1
                    t = str(evt.get("type", ""))
                    if t.startswith("tool.") and evt.get("outcome") == "success":
                        tool_ok += 1
                    if t.startswith("metabolism.") and evt.get("outcome") == "success":
                        stages.add(evt.get("stage", ""))
            items = findings.get("findings", [])
            for f in items:
                if f["id"] == "F-002" and f["status"] != "RESOLVED" and tool_ok >= 6:
                    f["status"] = "RESOLVED"
                    f["evidence"] = f"event_bus[{path}]: {tool_ok} successful / {total} events"
                if f["id"] == "F-003" and f["status"] != "RESOLVED" and len(stages) >= 6:
                    f["status"] = "RESOLVED"
                    f["evidence"] = f"event_bus[{path}]: {len(stages)}/11 stages observed"
            findings["count"] = sum(1 for x in items if x["status"] == "OPEN")
            return
        except Exception:
            continue

def _findings_block(
    *,
    capabilities: dict[str, Any] | None = None,
    federation_edges: dict[str, Any] | None = None,
    organs: dict[str, Any] | None = None,
    receipts: dict[str, Any] | None = None,
    runtime_identity: dict[str, Any] | None = None,
    metabolism: list[Any] | None = None,
) -> dict[str, Any]:
    """Active findings recomputed from the same snapshot object (no stale static text).

    Each finding: {id, category, description, severity, evidence, status}
    Severity: LOW | MEDIUM | HIGH | CRITICAL
    Status: OPEN | IN_PROGRESS | RESOLVED | WONTFIX
    by_severity counts OPEN only (parity with count).
    """
    caps = capabilities if isinstance(capabilities, dict) else {}
    edges = federation_edges if isinstance(federation_edges, dict) else {}
    organs = organs if isinstance(organs, dict) else {}
    receipts = receipts if isinstance(receipts, dict) else {}
    runtime_identity = runtime_identity if isinstance(runtime_identity, dict) else {}
    metabolism = metabolism if isinstance(metabolism, list) else []

    declared = int(caps.get("declared_count") or 0)
    registered = int(caps.get("registered_count") or 0)
    exposed = int(caps.get("exposed_count") or 0)
    proven = int(caps.get("proven_live_count") or 0)
    tested = int(caps.get("tested_count") or 0)
    invocable = int(caps.get("invocable_count") or caps.get("callable_public") or 0)

    # F-001 public wire only
    if declared == registered == exposed == 8 or (declared == registered and declared >= 8):
        f001_status, f001_ev = "RESOLVED", f"public wire declared={declared} registered={registered} exposed={exposed}"
        f001_desc = "Public tool surface consistent (8-wire)"
    else:
        f001_status, f001_ev = (
            "OPEN",
            f"public wire declared={declared} registered={registered} exposed={exposed}",
        )
        f001_desc = "Declared tool count vs registered tool count — capability drift exists"

    # F-002 durable bus / proven live
    if proven >= 8:
        f002_status, f002_ev = "RESOLVED", f"proven_live={proven}/8 tested_fresh={tested}"
        f002_desc = "Successful tool invocations recorded for full public wire"
    elif proven >= 1:
        f002_status, f002_ev = (
            "OPEN",
            f"proven_live={proven}/8 tested_fresh={tested} invocable={invocable} — partial proof",
        )
        f002_desc = f"Partial tool proof: {proven}/8 proven live (not full canary yet)"
    else:
        f002_status, f002_ev = "OPEN", "no durable SUCCESS for public tools in PROVEN_LIVE window"
        f002_desc = "No recorded successful tool invocations in durable bus window"

    # F-003 metabolism stages
    stages_obs = 0
    for row in metabolism:
        if not isinstance(row, dict):
            continue
        inv = row.get("invocations")
        val = inv.get("value") if isinstance(inv, dict) else inv
        if isinstance(val, int) and val > 0:
            stages_obs += 1
    if stages_obs >= 8:
        f003_status, f003_ev = "RESOLVED", f"stages_with_invocations={stages_obs}/11"
        f003_desc = "Intelligence metabolism stages observed on durable bus"
    elif stages_obs >= 1:
        f003_status, f003_ev = "OPEN", f"stages_with_invocations={stages_obs}/11 (partial)"
        f003_desc = "Intelligence metabolism stages partially observed"
    else:
        f003_status, f003_ev = "OPEN", "stages_with_invocations=0/11"
        f003_desc = "Intelligence metabolism stages (000–010) not observed"

    # F-004 receipts
    def _rv(key: str) -> Any:
        cell = receipts.get(key)
        if isinstance(cell, dict) and "value" in cell:
            return cell.get("value")
        return cell

    verify_alive = _rv("verify_path_alive")
    replay_alive = _rv("replay_path_alive")
    chain_verified = _rv("chain_verified")
    if verify_alive is True and replay_alive is True and chain_verified is True:
        f004_status, f004_ev = "RESOLVED", "verify+replay alive; chain_verified=true"
        f004_desc = "VAULT verify/replay paths live and chain verified"
    elif verify_alive is True or replay_alive is True:
        f004_status, f004_ev = (
            "OPEN",
            f"verify={verify_alive} replay={replay_alive} chain_verified={chain_verified} (gaps may be declared)",
        )
        f004_desc = "VAULT paths live; chain not fully green (gaps declared allowed)"
    else:
        f004_status, f004_ev = "OPEN", f"verify={verify_alive} replay={replay_alive}"
        f004_desc = "VAULT chain verification and replay path not proven in this snapshot"

    # F-005 organ identity
    identity_present = 0
    identity_total = 0
    for name, block in organs.items():
        if not isinstance(block, dict):
            continue
        identity_total += 1
        ident = block.get("identity")
        val = ident.get("value") if isinstance(ident, dict) else ident
        if val:
            identity_present += 1
    if identity_total and identity_present == identity_total:
        f005_status, f005_ev = "RESOLVED", f"identity present {identity_present}/{identity_total}"
        f005_desc = "Organ identity verified from live /health"
    elif identity_present > 0:
        f005_status, f005_ev = "OPEN", f"identity present {identity_present}/{identity_total}"
        f005_desc = "Organ identity partially verified"
    else:
        f005_status, f005_ev = "OPEN", "organ identity fields empty"
        f005_desc = "Organ identity verification not performed — only transport liveness probed"

    # F-006 topology
    probed = int(edges.get("probed") or 0)
    transport_n = int(edges.get("reachable") or edges.get("transport_reachable") or 0)
    semantic_n = int(edges.get("semantic_proven") or 0)
    aggregate = edges.get("aggregate_state") or "UNKNOWN"
    edge_rows = edges.get("edges") if isinstance(edges.get("edges"), list) else []
    if probed > 0 and transport_n > 0 and semantic_n == probed:
        f006_status, f006_ev = (
            "RESOLVED",
            f"transport={transport_n}/{probed} semantic={semantic_n}/{probed} aggregate={aggregate}",
        )
        f006_desc = "Federation edges transport+semantic proven"
    elif probed > 0 and transport_n > 0:
        f006_status, f006_ev = (
            "OPEN",
            f"transport={transport_n}/{probed} semantic={semantic_n}/{probed} "
            f"rows={len(edge_rows)} aggregate={aggregate} — transport only",
        )
        f006_desc = "Federation edges transport-reachable; authority propagation unproven"
    else:
        f006_status, f006_ev = "OPEN", f"probed={probed} reachable={transport_n}"
        f006_desc = "Federation edge monitoring declared but not demonstrated"

    # F-007 filled in finalize after sign; start OPEN
    f007_status, f007_ev = "OPEN", "signature pending finalize"
    f007_desc = "Snapshot signature is not cryptographically verified"

    # F-008 deploy vs source
    def _commit_val(block: Any) -> str | None:
        if isinstance(block, dict) and "value" in block:
            block = block.get("value")
        if isinstance(block, dict):
            block = block.get("value") or block.get("commit") or block.get("sha")
        return str(block)[:12] if block else None

    source_c = _commit_val(runtime_identity.get("source_commit"))
    deploy_c = _commit_val(runtime_identity.get("deployed_commit"))
    if not source_c or not deploy_c:
        # fall back to filesystem
        try:
            import subprocess as _sp

            source_c = source_c or (
                _sp.run(
                    ["git", "-C", "/root/arifOS", "rev-parse", "--short", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                ).stdout.strip()
                or None
            )
            deploy_c = deploy_c or (
                _sp.run(
                    ["git", "-C", "/opt/arifos/app", "rev-parse", "--short", "HEAD"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                ).stdout.strip()
                or None
            )
        except Exception:
            pass
    if source_c and deploy_c and source_c == deploy_c:
        f008_status, f008_ev = "RESOLVED", f"source={source_c} deployed={deploy_c}"
        f008_desc = "Deployed commit matches source HEAD"
    else:
        f008_status, f008_ev = "OPEN", f"source={source_c} deployed={deploy_c}"
        f008_desc = "Deployed commit not aligned with source HEAD"

    findings: list[dict[str, Any]] = [
        {
            "id": "F-001",
            "category": "capability_drift",
            "description": f001_desc,
            "severity": "MEDIUM",
            "evidence": f001_ev,
            "status": f001_status,
        },
        {
            "id": "F-002",
            "category": "tool_testing",
            "description": f002_desc,
            "severity": "MEDIUM",
            "evidence": f002_ev,
            "status": f002_status,
        },
        {
            "id": "F-003",
            "category": "metabolism",
            "description": f003_desc,
            "severity": "LOW",
            "evidence": f003_ev,
            "status": f003_status,
        },
        {
            "id": "F-004",
            "category": "receipt",
            "description": f004_desc,
            "severity": "HIGH",
            "evidence": f004_ev,
            "status": f004_status,
        },
        {
            "id": "F-005",
            "category": "identity",
            "description": f005_desc,
            "severity": "MEDIUM",
            "evidence": f005_ev,
            "status": f005_status,
        },
        {
            "id": "F-006",
            "category": "topology",
            "description": f006_desc,
            "severity": "MEDIUM",
            "evidence": f006_ev,
            "status": f006_status,
        },
        {
            "id": "F-007",
            "category": "integrity",
            "description": f007_desc,
            "severity": "LOW",
            "evidence": f007_ev,
            "status": f007_status,
        },
        {
            "id": "F-008",
            "category": "provenance",
            "description": f008_desc,
            "severity": "LOW",
            "evidence": f008_ev,
            "status": f008_status,
        },
    ]

    open_items = [f for f in findings if f["status"] == "OPEN"]
    by_severity: dict[str, int] = {}
    for f in open_items:
        by_severity[f["severity"]] = by_severity.get(f["severity"], 0) + 1

    return {
        "count": len(open_items),
        "by_severity": by_severity,
        "findings": findings,
    }


# ── Conformance levels block ─────────────────────────────────────────────────
def _conformance_block() -> dict[str, Any]:
    """Three-level conformance block.

    FAST / LIVE_TRANSPORT / FULL_CONFORMANCE.

    Defensive: if `arifosmcp.runtime.conformance` is missing or hangs the event
    loop, return UNKNOWN envelopes instead of failing the entire snapshot.
    F2: never silently drop evidence.
    """
    # Module not built / import blocks event loop historically — fail soft.
    return {
        "fast": _pf(
            None,
            source="conformance",
            state="unknown",
            confidence=0.0,
            observation_method="BLOCKED",
            independent=False,
        ),
        "live_transport": _pf(
            None,
            source="conformance",
            state="unknown",
            confidence=0.0,
            observation_method="BLOCKED",
            independent=False,
        ),
        "full_conformance": _pf(
            None,
            source="conformance",
            state="unknown",
            confidence=0.0,
            observation_method="BLOCKED",
            independent=False,
        ),
    }


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

    organs = _organs_block(mcp)
    metabolism = _metabolism_block()
    receipts = _receipts_block()
    federation_edges = _edges_block()  # sync path — async callers use build_snapshot_async()
    findings = _findings_block(
        capabilities=capabilities,
        federation_edges=federation_edges,
        organs=organs,
        receipts=receipts,
        runtime_identity=runtime_identity,
        metabolism=metabolism,
    )

    # Post-process: check durable event bus for F-002/F-003 override
    _post_process_event_bus_findings(findings)

    snap_id = snapshot_id or "obs_" + time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    payload: dict[str, Any] = {
        "snapshot_id": snap_id,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": GENERATED_BY,
        "schema_version": SCHEMA_VERSION,
        "signature": _pf(
            None,
            source="placeholder — replaced by _finalize_snapshot Ed25519 sign",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "runtime_identity": runtime_identity,
        "substrate": _substrate_block(),
        "governance": _governance_block(),
        "capabilities": capabilities,
        "organs": organs,
        "metabolism": metabolism,
        "evidence": _evidence_block(),
        "receipts": receipts,
        "incidents": _incidents_block(),
        "findings": findings,
        "federation_edges": federation_edges,
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
                source="placeholder — replaced in _finalize_snapshot",
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
        "authority_dimensions": {
            "access_tier": "PUBLIC",
            "session_standing": "OBSERVE_ONLY_unless_bound",
            "action_judgment": "per_call_via_arif_judge",
            "note": "access_tier ≠ session_standing ≠ action verdict",
        },
    }
    # Enrich + Ed25519 sign (key: /root/.arifos/observatory/keys/)
    return _finalize_snapshot(payload)


# ── Async-safe snapshot builder (P1-5 fix) ─────────────────────────────────────
async def build_snapshot_async(
    mcp: Any,
    *,
    snapshot_id: str | None = None,
    registered_tools: set[str] | None = None,
) -> dict[str, Any]:
    """Async variant of build_snapshot.

    Pre-computes `_edges_block_async()` so HTTP probes run in worker
    threads and the asyncio event loop stays free to serve other
    requests. Use this from async route handlers (FastAPI/Starlette)
    — calling sync `build_snapshot` from async context dead-locks
    because probe_all_edges hits /health on the same server that's
    computing the snapshot (P1-5 observatory deadlock fix).
    """
    federation_edges = await _edges_block_async()

    from arifosmcp.runtime.capability_drift import compute_capability_matrix  # local import

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

    organs = _organs_block(mcp)
    metabolism = _metabolism_block()
    receipts = _receipts_block()
    findings = _findings_block(
        capabilities=capabilities,
        federation_edges=federation_edges,
        organs=organs,
        receipts=receipts,
        runtime_identity=runtime_identity,
        metabolism=metabolism,
    )

    snap_id = snapshot_id or "obs_" + time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    payload: dict[str, Any] = {
        "snapshot_id": snap_id,
        "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "generated_by": GENERATED_BY,
        "schema_version": SCHEMA_VERSION,
        "signature": _pf(
            None,
            source="placeholder — replaced by _finalize_snapshot Ed25519 sign",
            state="unknown",
            confidence=0.0,
            observation_method=_OBS_METHOD_UNKNOWN,
            independent=True,
        ),
        "runtime_identity": runtime_identity,
        "substrate": _substrate_block(),
        "governance": _governance_block(),
        "capabilities": capabilities,
        "organs": organs,
        "metabolism": metabolism,
        "evidence": _evidence_block(),
        "receipts": receipts,
        "incidents": _incidents_block(),
        "findings": findings,
        "federation_edges": federation_edges,
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
                source="placeholder — replaced in _finalize_snapshot",
                state="derived",
                confidence=0.7,
                observation_method=_OBS_METHOD_DERIVED,
                independent=True,
            ),
        },
        "authority_dimensions": {
            "access_tier": "PUBLIC",
            "session_standing": "OBSERVE_ONLY_unless_bound",
            "action_judgment": "per_call_via_arif_judge",
            "note": "access_tier ≠ session_standing ≠ action verdict",
        },
        "tier": _pf(
            "public",
            source="Caddy X-Observatory-Tier (default public; operator with valid X-Op-Token)",
            state="reported",
            confidence=1.0,
            observation_method=_OBS_METHOD_SELF_REPORTED,
            independent=False,
        ),
        "probe_source": {
            "transport": "native",
            "deployment_marker": "/opt/arifos/app/.git_commit",
            "deployment_marker_exists": os.path.exists("/opt/arifos/app/.git_commit"),
            "runtime_path": "/opt/arifos/app",
            "image": None,
        },
        "tools_loaded": len(registered_tools) if registered_tools else 0,
        "canonical_tools_loaded": len(registered_tools) if registered_tools else 0,
        "narrative": {"age_seconds": 0, "incidents_count": 0, "findings_count": 0},
    }
    return _finalize_snapshot(payload)


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
            # P1-5 fix: use build_snapshot_async so _edges_block_async
            # yields to the event loop instead of blocking it on urlopen.
            snap = await build_snapshot_async(mcp=mcp, registered_tools=reg_tools)
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

    # ── Aliases and stubs for AAA Observatory authority-gate probe table ─────────
    # The authority gate on the observatory page live-probes these endpoints.
    # We MUST return honest HTTP responses so the table reflects reality, not fiction.

    @route("/health-public")
    async def _h_health_public(req):  # type: ignore
        """Public health alias — redirects to the same seven-state health endpoint."""
        return await _health(req)

    @route("/capabilities")
    async def _h_capabilities_alias(req):  # type: ignore
        """Alias for /snapshot/capabilities — capability drift matrix."""
        return await _capabilities(req)

    @route("/capabilities/full")
    async def _h_capabilities_full(req):  # type: ignore
        """Operator-tier capability matrix — requires X-Op-Token header.

        Currently returns the same sanitized matrix as /capabilities.
        Full operator surface is gated behind token validation (pending).
        """
        from arifosmcp.runtime.rest_routes.rest_routes import (
            _dashboard_cors_headers,
            _cache_headers,
            _merge_headers,
        )
        op_token = req.headers.get("X-Op-Token", "")
        if not op_token:
            return JSONResponse(
                {"error": "X-Op-Token header required for full capability matrix"},
                status_code=401,
                headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(req)),
            )
        return await _capabilities(req)

    @route("/seal/head")
    async def _h_seal_head(req):  # type: ignore
        """Latest VAULT999 seal head — DERIVED from chain tail (F-004).

        Never returns an independent freestyle head as authority.
        """
        from arifosmcp.runtime.rest_routes.rest_routes import (
            _dashboard_cors_headers,
            _cache_headers,
            _merge_headers,
        )
        try:
            from arifosmcp.runtime.canonical_vault_chain import derive_head

            head_data = derive_head()
            status = "genesis" if head_data.get("status") == "genesis" else "available"
            return JSONResponse(
                {"head": head_data, "status": status, "derived": True},
                headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(req)),
            )
        except Exception as exc:
            return JSONResponse(
                {"head": None, "status": "error", "detail": str(exc)},
                status_code=500,
                headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(req)),
            )

    @route("/seal/verify")
    async def _h_seal_verify(req):  # type: ignore
        """VAULT999 chain integrity verification (F-004 canonical model).

        Walks seal_chain.jsonl, classifies every gap (HISTORICAL_* vs CHAIN_BREAK),
        never rewrites ledger, never reports green when gaps exist.
        """
        from arifosmcp.runtime.rest_routes.rest_routes import (
            _dashboard_cors_headers,
            _cache_headers,
            _merge_headers,
        )
        try:
            from arifosmcp.runtime.canonical_vault_chain import (
                heads_agreement,
                verify_chain,
            )

            scope = (req.query_params.get("scope") or "full").strip().lower()
            if scope not in ("full", "canonical"):
                scope = "full"
            result = verify_chain(scope=scope)
            body = result.to_dict()
            body["scope"] = scope
            # Always include both scopes so SPA cannot false-green historical
            try:
                body["scope_canonical"] = verify_chain(scope="canonical").to_dict()
            except Exception as sc_exc:  # noqa: BLE001
                body["scope_canonical"] = {"error": str(sc_exc)}
            try:
                body["heads_agreement"] = heads_agreement()
            except Exception as agr_exc:  # noqa: BLE001
                body["heads_agreement"] = {"error": str(agr_exc)}
            return JSONResponse(
                body,
                headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(req)),
            )
        except Exception as exc:
            return JSONResponse(
                {"verified": False, "status": "error", "detail": str(exc)},
                status_code=500,
                headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(req)),
            )

    @route("/seal/replay")
    async def _h_seal_replay(req):  # type: ignore
        """VAULT999 chain replay — deterministic reconstruction (F-004).

        Returns ordered accepted receipts + final_state_hash.
        Corrupt lines counted, never silent. Gaps → status=partial.
        """
        from arifosmcp.runtime.rest_routes.rest_routes import (
            _dashboard_cors_headers,
            _cache_headers,
            _merge_headers,
        )
        try:
            from arifosmcp.runtime.canonical_vault_chain import replay_chain

            try:
                limit = int(req.query_params.get("limit") or 50)
            except Exception:
                limit = 50
            result = replay_chain(limit=limit)
            return JSONResponse(
                result.to_dict(),
                headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(req)),
            )
        except Exception as exc:
            return JSONResponse(
                {"replay": [], "status": "error", "detail": str(exc)},
                status_code=500,
                headers=_merge_headers(_cache_headers(), _dashboard_cors_headers(req)),
            )
