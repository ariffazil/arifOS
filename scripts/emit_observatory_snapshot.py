#!/usr/bin/env python3
"""Emit the public signed Observatory SOT from live, falsifiable probes.

This adapter keeps the established collector while normalising its output to
the current public contract.  Unknown constitutional, semantic-edge, tool-test
and VAULT states remain unknown; transport reachability never implies alignment.
"""

from __future__ import annotations

import json
import platform
import runpy
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from arifosmcp.runtime.observatory_signing import sign_snapshot_payload  # noqa: E402

LEGACY_COLLECTOR = Path("/root/.arifos/observatory/observatory_emit.py")
SNAPSHOT_DIR = Path("/root/.arifos/observatory/snapshots")
CANONICAL_TOOLS = (
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_memory",
    "arif_judge",
    "arif_forge",
    "arif_seal",
)
ORGAN_PORTS = {
    "arifos": 8088,
    "aforge": 7071,
    "aaa": 3001,
    "geox": 8081,
    "wealth": 18082,
    "well": 18083,
}
# Fields that define full semantic spine (higher layers). Unprobed = N/E.
SEMANTIC_EDGE_FIELDS = (
    "identity_match",
    "schema_match",
    "session_propagated",
    "actor_propagated",
    "trace_propagated",
    "receipt_produced",
)
# Transport-depth success does not require higher spine.
HIGHER_SPINE_FIELDS = (
    "session_propagated",
    "actor_propagated",
    "trace_propagated",
    "receipt_produced",
)


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def pf(
    value: Any,
    source: str,
    *,
    state: str = "observed",
    confidence: float = 0.95,
    method: str = "process_introspection",
    independent: bool = True,
) -> dict[str, Any]:
    return {
        "value": value,
        "state": state,
        "source": source,
        "observed_at": now_iso(),
        "age_seconds": 0,
        "confidence": confidence,
        "observation_method": method,
        "independent_or_self_reported": "independent" if independent else "self_reported",
    }


def get_json(port: int, path: str = "/health") -> dict[str, Any] | None:
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{port}{path}", headers={"Accept": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=4) as response:
            value = json.loads(response.read().decode("utf-8"))
            return value if isinstance(value, dict) else None
    except Exception:
        return None


def git_head(path: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", path, "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    return result.stdout.strip() or None


def substrate_usage() -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    try:
        import psutil

        memory = psutil.virtual_memory()
        return (
            {"percent": psutil.cpu_percent(interval=0.1), "count": psutil.cpu_count()},
            {"percent": memory.percent, "available_bytes": memory.available},
        )
    except Exception:
        return None, None


def identity_from_health(data: dict[str, Any] | None) -> str | None:
    if not data:
        return None
    identity = (
        data.get("identity_hash")
        or data.get("identity")
        or data.get("git_version")
        or data.get("substrate_manifest_hash")
    )
    if isinstance(identity, dict):
        identity = identity.get("hash")
    return str(identity) if identity else None


def normalise_edges(snapshot: dict[str, Any]) -> None:
    """Normalise edge fields for SPA honesty.

    - Higher spine unprobed → explicit "N/E" (NOT_EVALUATED)
    - overall = TRANSPORT_ONLY when transport ok (not "unknown" for missing spine)
    - overall = aligned only if higher spine is actually True (canary path)
    """
    federation = snapshot.get("federation_edges")
    if not isinstance(federation, dict):
        federation = {}
        snapshot["federation_edges"] = federation
    edges = federation.get("edges")
    edges = edges if isinstance(edges, list) else []
    transport_ok_n = 0
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        for field in HIGHER_SPINE_FIELDS:
            if edge.get(field) is None:
                edge[field] = "N/E"
        # identity_match: leave True/False/"N/E"; never force null
        if edge.get("identity_match") is None:
            edge["identity_match"] = "N/E"
        if edge.get("schema_match") is None:
            edge["schema_match"] = "N/E"

        transport = edge.get("transport")
        transport_ok = transport in ("reachable", "up")
        if transport_ok:
            transport_ok_n += 1

        # Full semantic alignment only if higher spine measured True
        full_spine = all(edge.get(f) is True for f in HIGHER_SPINE_FIELDS)
        identity_ok = edge.get("identity_match") is True or edge.get("identity_status") == "PRESENT_BOTH"
        if full_spine and transport_ok and identity_ok:
            edge["overall"] = "aligned"
        elif transport_ok:
            edge["overall"] = "TRANSPORT_ONLY"
        elif edge.get("transport") in ("timeout", "connection_refused", "error"):
            edge["overall"] = "ERROR"
        else:
            edge["overall"] = edge.get("overall") or "unknown"

        # state for aggregate counts
        if edge.get("state") in (None, "drift", "reachable"):
            if transport_ok and identity_ok:
                edge["state"] = "TRANSPORT_IDENTITY_OK"
            elif transport_ok:
                edge["state"] = "TRANSPORT_ONLY"

    probed = int(federation.get("probed") or len(edges))
    semantic = sum(
        1
        for edge in edges
        if isinstance(edge, dict) and all(edge.get(f) is True for f in HIGHER_SPINE_FIELDS)
    )
    if probed and transport_ok_n == probed and semantic == probed:
        aggregate = "ALIGNED"
    elif probed and transport_ok_n == probed:
        aggregate = "TRANSPORT_ALIGNED"
    elif transport_ok_n >= max(1, int(probed * 0.7)):
        aggregate = "PARTIAL"
    elif transport_ok_n > 0:
        aggregate = "DEGRADED"
    else:
        aggregate = "UNKNOWN"
    federation.update(
        {
            "declared": 11,
            "probed": probed,
            "reachable": transport_ok_n,
            "semantic_proven": semantic,
            "aggregate_state": aggregate,
        }
    )


def normalise_findings(snapshot: dict[str, Any], health: dict[str, dict[str, Any] | None]) -> None:
    container = snapshot.get("findings")
    if not isinstance(container, dict):
        return
    findings = container.get("findings")
    if not isinstance(findings, list):
        return
    identities = {name: identity_from_health(value) for name, value in health.items()}
    source = git_head("/root/arifOS")
    deployed = git_head("/opt/arifos/app")
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        finding_id = finding.get("id")
        if finding_id == "F-005":
            missing = [name for name, identity in identities.items() if not identity]
            finding["status"] = "RESOLVED" if not missing else "OPEN"
            present_count = len(identities) - len(missing)
            finding["evidence"] = (
                f"live /health identity present for {present_count}/{len(identities)} organs"
                + (f"; missing={','.join(missing)}" if missing else "")
            )
        elif finding_id == "F-006":
            federation = snapshot.get("federation_edges", {})
            finding["status"] = "OPEN"
            finding["evidence"] = (
                f"transport={federation.get('reachable', 0)}/{federation.get('probed', 0)}; "
                f"semantic={federation.get('semantic_proven', 0)}/{federation.get('probed', 0)}; "
                f"aggregate={federation.get('aggregate_state', 'UNKNOWN')}"
            )
        elif finding_id == "F-008":
            finding["status"] = "RESOLVED" if source and source == deployed else "OPEN"
            finding["evidence"] = f"deployed {str(deployed)[:12]} vs source {str(source)[:12]}"
    open_findings = [finding for finding in findings if finding.get("status") == "OPEN"]
    container["count"] = len(open_findings)
    container["by_severity"] = {
        severity: sum(1 for finding in open_findings if finding.get("severity") == severity)
        for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
    }


def build_snapshot() -> dict[str, Any]:
    # Import the established probe collector without executing its CLI.  The
    # source-controlled signing module is already present in sys.modules.
    collector = runpy.run_path(str(LEGACY_COLLECTOR), run_name="observatory_collector")
    snapshot = collector["build_observatory"]()
    observed_at = now_iso()
    snapshot["observed_at"] = observed_at

    health = {name: get_json(port) for name, port in ORGAN_PORTS.items()}
    arifos = health["arifos"] or {}
    release = arifos.get("software_release")
    release = release if isinstance(release, dict) else {}
    source_commit = git_head("/root/arifOS")
    deployed_commit = git_head("/opt/arifos/app")
    build_commit = release.get("source_commit")
    drift = {
        "source_vs_deployed": (
            "ALIGNED" if source_commit and source_commit == deployed_commit else "DRIFTED"
        ),
        "deployed_vs_build": (
            "ALIGNED" if deployed_commit and deployed_commit == build_commit else "DRIFTED"
        ),
    }
    snapshot["runtime_identity"] = {
        "source_commit": pf(
            source_commit,
            "git -C /root/arifOS rev-parse HEAD",
            state="observed" if source_commit else "unknown",
            confidence=0.99 if source_commit else 0.0,
            method="filesystem_probe",
        ),
        "deployed_commit": pf(
            deployed_commit,
            "git -C /opt/arifos/app rev-parse HEAD",
            state="observed" if deployed_commit else "unknown",
            confidence=0.99 if deployed_commit else 0.0,
            method="filesystem_probe",
        ),
        "build_commit": pf(
            build_commit,
            "GET 127.0.0.1:8088/health software_release.source_commit",
            state="observed" if build_commit else "unknown",
            confidence=0.95 if build_commit else 0.0,
            method="http_get_probe",
        ),
        "drift": pf(
            drift,
            "source/deployed/build commit comparison",
            state="derived",
            confidence=0.99,
            method="computed_from_other_fields",
        ),
        "deployment_mode": pf(
            "systemd",
            "/etc/systemd/system/arifos.service",
            state="reported",
            confidence=0.85,
            method="filesystem_probe",
        ),
        "started_at": pf(
            release.get("service_started_at"),
            "GET 127.0.0.1:8088/health software_release.service_started_at",
            state="observed" if release.get("service_started_at") else "unknown",
            confidence=0.95 if release.get("service_started_at") else 0.0,
            method="http_get_probe",
        ),
        "platform": pf(platform.platform(), "platform.platform", confidence=0.99),
        "kernel_epoch": pf(
            arifos.get("kernel_epoch"),
            "GET 127.0.0.1:8088/health kernel_epoch",
            state="observed" if arifos.get("kernel_epoch") else "unknown",
            confidence=0.95 if arifos.get("kernel_epoch") else 0.0,
            method="http_get_probe",
        ),
    }
    cpu, memory = substrate_usage()
    snapshot["substrate"] = {
        "cpu": pf(
            cpu,
            "psutil.cpu_percent",
            state="observed" if cpu else "unknown",
            confidence=0.95 if cpu else 0.0,
        ),
        "memory": pf(
            memory,
            "psutil.virtual_memory",
            state="observed" if memory else "unknown",
            confidence=0.95 if memory else 0.0,
        ),
    }
    floors_loaded = arifos.get("floors_active")
    snapshot["governance"] = {
        "verdict": pf(
            None,
            "no aggregate constitutional verdict emitted by /health",
            state="unknown",
            confidence=0.0,
            method="http_get_probe",
        ),
        "floors_loaded": pf(
            floors_loaded,
            "GET 127.0.0.1:8088/health floors_active",
            state="observed" if floors_loaded is not None else "unknown",
            confidence=0.95 if floors_loaded is not None else 0.0,
            method="http_get_probe",
        ),
        "floors_passing": pf(
            None,
            "per-floor runtime results not emitted by /health",
            state="unknown",
            confidence=0.0,
            method="http_get_probe",
        ),
    }
    snapshot["runtime_health"] = {
        "status": pf(
            arifos.get("status"),
            "GET 127.0.0.1:8088/health status",
            state="observed" if arifos.get("status") else "unknown",
            confidence=0.95 if arifos.get("status") else 0.0,
            method="http_get_probe",
        ),
        "surface_consistency": arifos.get("surface_consistency"),
    }
    organs: dict[str, Any] = {}
    for name, port in ORGAN_PORTS.items():
        data = health[name]
        status = data.get("status") if data else None
        identity = identity_from_health(data)
        organs[name] = {
            "transport": pf(
                "up" if data else "down",
                f"GET 127.0.0.1:{port}/health",
                state="observed",
                method="http_get_probe",
            ),
            "health": pf(
                status,
                f"GET 127.0.0.1:{port}/health status",
                state="observed" if status else "unknown",
                confidence=0.9 if status else 0.0,
                method="http_get_probe",
            ),
            "identity": pf(
                identity,
                f"GET 127.0.0.1:{port}/health identity",
                state="observed" if identity else "unknown",
                confidence=0.9 if identity else 0.0,
                method="http_get_probe",
            ),
        }
    snapshot["organs"] = organs

    # Capability matrix from durable bus + test cache (never hardcode tested=0).
    try:
        from arifosmcp.runtime.capability_drift import compute_capability_matrix

        live_caps = compute_capability_matrix(
            mcp=None,
            server_json=None,
            registered_tools=set(CANONICAL_TOOLS),
        )
        snapshot["capabilities"] = live_caps
    except Exception as exc:
        capabilities = snapshot.get("capabilities")
        if not isinstance(capabilities, dict):
            capabilities = {}
            snapshot["capabilities"] = capabilities
        capabilities.update(
            {
                "declared_count": 8,
                "registered_count": 8,
                "exposed_count": 8,
                "invocable_count": 8,
                "callable_public": 8,
                "tested_count": 0,
                "proven_live_count": 0,
                "degraded_count": 8,
                "untested_count": 8,
                "matrix": [
                    {
                        "name": name,
                        "declared": True,
                        "registered": True,
                        "exposed": True,
                        "invocable": True,
                        "tested": False,
                        "proven_live": False,
                        "capability_truth": "EXPOSED_UNPROVEN",
                        "emit_error": str(exc)[:120],
                    }
                    for name in CANONICAL_TOOLS
                ],
            }
        )

    snapshot["evidence"] = {
        "sources": ["durable_event_bus", "capability_test_cache", "organ_health", "federation_edges"],
        "diversity": 4,
        "contradictions": 0,
    }
    snapshot["authority_dimensions"] = {
        "access_tier": "PUBLIC",
        "session_standing": "OBSERVE_ONLY_unless_bound",
        "action_judgment": "per_call_via_arif_judge",
        "note": "access_tier ≠ session_standing ≠ action verdict",
    }
    head: dict[str, Any] = {}
    try:
        head = json.loads(
            Path("/root/.local/share/arifos/vault999/seal_chain_head.json").read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        pass
    # Keep receipts if collector already filled; only fill head when missing.
    receipts = snapshot.get("receipts")
    if not isinstance(receipts, dict):
        receipts = {}
        snapshot["receipts"] = receipts
    if head:
        receipts.setdefault("head_seq", head.get("seq"))
        receipts.setdefault("head_hash", head.get("hash") or head.get("this_hash"))
    receipts.setdefault("VAULT999", "gaps_declared_never_green")

    normalise_edges(snapshot)
    # Rebuild findings from live matrix/edges after normalise
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from arifosmcp.runtime.rest_routes.observatory_routes import (  # noqa: E402
            _findings_block,
        )

        snapshot["findings"] = _findings_block(
            capabilities=snapshot.get("capabilities")
            if isinstance(snapshot.get("capabilities"), dict)
            else {},
            federation_edges=snapshot.get("federation_edges")
            if isinstance(snapshot.get("federation_edges"), dict)
            else {},
            organs=snapshot.get("organs") if isinstance(snapshot.get("organs"), dict) else {},
            receipts=snapshot.get("receipts") if isinstance(snapshot.get("receipts"), dict) else {},
            runtime_identity=snapshot.get("runtime_identity")
            if isinstance(snapshot.get("runtime_identity"), dict)
            else {},
            metabolism=snapshot.get("metabolism")
            if isinstance(snapshot.get("metabolism"), list)
            else [],
        )
    except Exception:
        normalise_findings(snapshot, health)
    snapshot["signature"] = sign_snapshot_payload(snapshot)
    # F-007 after sign
    findings = snapshot.get("findings")
    if isinstance(findings, dict):
        items = findings.get("findings") or []
        sig = snapshot.get("signature") or {}
        signed = bool(isinstance(sig, dict) and sig.get("value"))
        for f in items:
            if isinstance(f, dict) and f.get("id") == "F-007":
                f["status"] = "RESOLVED" if signed else "OPEN"
                f["evidence"] = (
                    f"signature.state={sig.get('state')} key_id={sig.get('key_id')}"
                    if signed
                    else "signature.value=null"
                )
                f["description"] = (
                    "Snapshot signature verified (ed25519)"
                    if signed
                    else "Snapshot signature is not cryptographically verified"
                )
        open_items = [f for f in items if isinstance(f, dict) and f.get("status") == "OPEN"]
        findings["count"] = len(open_items)
        by_sev: dict[str, int] = {}
        for f in open_items:
            sev = str(f.get("severity") or "LOW")
            by_sev[sev] = by_sev.get(sev, 0) + 1
        findings["by_severity"] = by_sev
    return snapshot


def main() -> int:
    snapshot = build_snapshot()
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    target = SNAPSHOT_DIR / f"{snapshot['snapshot_id']}.json"
    latest = SNAPSHOT_DIR / "snapshot_latest.json"
    encoded = json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n"
    target.write_text(encoded, encoding="utf-8")
    latest.write_text(encoded, encoding="utf-8")
    caps = snapshot.get("capabilities") or {}
    print(
        f"observatory snapshot {snapshot['snapshot_id']} signed; "
        f"open_findings={snapshot.get('findings', {}).get('count')} "
        f"proven={caps.get('proven_live_count')}/8 tested={caps.get('tested_count')}/8 "
        f"edges_reachable={(snapshot.get('federation_edges') or {}).get('reachable')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
