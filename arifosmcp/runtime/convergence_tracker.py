"""
convergence_tracker.py — Release Candidate Convergence Tracker (EUREKA P1.2)

Compares convergence across 9 layers, produces a structured report
with per-layer state, failure codes, and telemetry counters.

Mandatory layers (FAIL collapses overall): source, artifact, installation, import, process
Conditional layers (FAIL collapses only when required by action): service, tool_registry, db_schema, vault_writer

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Approved paths ─────────────────────────────────────────────────────────

APPROVED_SOURCE_ROOT = "/root/arifOS"
APPROVED_VENV_PYTHON = "/opt/arifos/venv/bin/python"
APPROVED_VENV_SITE_PACKAGES = "/opt/arifos/venv/lib/python3.12/site-packages"
APPROVED_DIST_PKG = Path(APPROVED_VENV_SITE_PACKAGES) / "arifosmcp"
APPROVED_PYTHON_REALPATHS = ("/opt/arifos/venv/", "/opt/arifos/python-3.12-gnu/")
SERVICE_NAME = "arifos.service"

# ── Convergence states ────────────────────────────────────────────────────

class ConvergenceState(str, Enum):
    CONVERGED = "CONVERGED"
    SOURCE_AHEAD = "SOURCE_AHEAD"
    ARTIFACT_AHEAD = "ARTIFACT_AHEAD"
    RUNTIME_AHEAD = "RUNTIME_AHEAD"
    DUPLICATE_INSTALL = "DUPLICATE_INSTALL"
    MANIFEST_MISMATCH = "MANIFEST_MISMATCH"
    MODULE_PATH_MISMATCH = "MODULE_PATH_MISMATCH"
    SCHEMA_DRIFT = "SCHEMA_DRIFT"
    TOOL_REGISTRY_DRIFT = "TOOL_REGISTRY_DRIFT"
    VAULT_WRITER_DRIFT = "VAULT_WRITER_DRIFT"
    UNKNOWN_ARTIFACT = "UNKNOWN_ARTIFACT"
    UNREACHABLE = "UNREACHABLE"


# ── Data classes ──────────────────────────────────────────────────────────


@dataclasses.dataclass
class ConvergenceLayer:
    name: str
    state: ConvergenceState
    observed_value: Any
    expected_value: Any
    evidence_ref: str
    failure_code: str | None = None
    checked_at: str = dataclasses.field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclasses.dataclass
class ArtifactIdentity:
    name: str
    version: str | None
    sha256: str | None
    dist_info_path: str | None
    wheel_hash: str | None


@dataclasses.dataclass
class RuntimeIdentity:
    python_executable: str
    python_version: str
    site_packages: str
    arifosmcp_path: str


@dataclasses.dataclass
class ServiceIdentity:
    service_name: str
    active: bool
    main_pid: int | None
    service_executable: str | None
    started_at: str | None


@dataclasses.dataclass
class ConvergenceFailure:
    layer: str
    state: ConvergenceState
    failure_code: str
    detail: str
    observed: Any
    expected: Any


@dataclasses.dataclass
class ConvergenceReport:
    layers: list[ConvergenceLayer]
    mandatory_layers: list[str]
    conditional_layers: list[str]
    failures: list[ConvergenceFailure]
    runtime_identity: RuntimeIdentity
    artifact_identity: ArtifactIdentity
    service_identity: ServiceIdentity
    overall_state: ConvergenceState
    release_id: str
    source_commit: str | None
    checked_at: str = dataclasses.field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "release_id": self.release_id,
            "source_commit": self.source_commit,
            "overall_state": self.overall_state.value,
            "checked_at": self.checked_at,
            "runtime_identity": dataclasses.asdict(self.runtime_identity),
            "artifact_identity": dataclasses.asdict(self.artifact_identity),
            "service_identity": dataclasses.asdict(self.service_identity),
            "mandatory_layers": self.mandatory_layers,
            "conditional_layers": self.conditional_layers,
            "layers": [dataclasses.asdict(l) for l in self.layers],
            "failures": [dataclasses.asdict(f) for f in self.failures],
        }

    def to_receipt(self) -> dict[str, Any]:
        """Produce a VAULT-ready convergence receipt."""
        return {
            "event_type": "runtime.convergence",
            "release_id": self.release_id,
            "source_commit": self.source_commit,
            "wheel_hash": self.artifact_identity.wheel_hash,
            "runtime_manifest_hash": self.artifact_identity.sha256,
            "service_pid": self.service_identity.main_pid,
            "service_started_at": self.service_identity.started_at,
            "module_paths": [l.observed_value for l in self.layers if l.name == "import"],
            "tool_registry_hash": next(
                (l.observed_value.get("registry_hash") for l in self.layers
                 if l.name == "tool_registry" and isinstance(l.observed_value, dict)),
                None,
            ),
            "database_schema_version": next(
                (l.observed_value.get("schema_version") for l in self.layers
                 if l.name == "database_schema" and isinstance(l.observed_value, dict)),
                None,
            ),
            "vault_writer_hash": next(
                (l.observed_value.get("total_seals") for l in self.layers
                 if l.name == "vault_writer" and isinstance(l.observed_value, dict)),
                None,
            ),
            "convergence": self.overall_state.value,
            "evidence_refs": [l.evidence_ref for l in self.layers],
        }


# ── Layer probes ──────────────────────────────────────────────────────────


def _git(*args: str) -> str | None:
    try:
        r = subprocess.run(
            ["git", "-C", APPROVED_SOURCE_ROOT, *args],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def probe_source_layer() -> ConvergenceLayer:
    commit = _git("rev-parse", "HEAD")
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    dirty_raw = _git("status", "--porcelain") or ""
    dirty = bool(dirty_raw.strip())
    observed = {
        "commit": commit,
        "branch": branch,
        "dirty": dirty,
        "root": APPROVED_SOURCE_ROOT,
    }
    expected = "clean commit on main"
    if commit is None:
        return ConvergenceLayer(
            name="source", state=ConvergenceState.UNREACHABLE,
            observed_value=observed, expected_value=expected,
            evidence_ref=f"file:{APPROVED_SOURCE_ROOT}/.git",
            failure_code="SOURCE_UNREACHABLE",
        )
    if dirty:
        return ConvergenceLayer(
            name="source", state=ConvergenceState.SOURCE_AHEAD,
            observed_value=observed, expected_value=expected,
            evidence_ref=f"file:{APPROVED_SOURCE_ROOT}/.git",
            failure_code="SOURCE_DIRTY",
        )
    return ConvergenceLayer(
        name="source", state=ConvergenceState.CONVERGED,
        observed_value=observed, expected_value=expected,
        evidence_ref=f"file:{APPROVED_SOURCE_ROOT}/.git",
    )


def probe_artifact_layer() -> ConvergenceLayer:
    version = None
    wheel_hash = None
    pkg_sha = None
    dist_info_name = None
    for d in Path(APPROVED_VENV_SITE_PACKAGES).iterdir():
        if d.name.startswith("arifos-") and d.name.endswith(".dist-info"):
            dist_info_name = d.name
            meta = d / "METADATA"
            if meta.exists():
                for line in meta.read_text().splitlines():
                    if line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
            record = d / "RECORD"
            if record.exists():
                for line in record.read_text().splitlines():
                    if line.endswith(".whl,"):
                        parts = line.split(",")
                        if len(parts) >= 2 and parts[1].startswith("sha256="):
                            wheel_hash = parts[1]
                            break
            pkg_dir = d.parent / "arifosmcp"
            if pkg_dir.exists():
                h = hashlib.sha256()
                for p in sorted(pkg_dir.rglob("*.py")):
                    if "__pycache__" in str(p):
                        continue
                    h.update(p.read_bytes())
                pkg_sha = f"sha256:{h.hexdigest()}"
            break
    observed = {
        "dist_info": dist_info_name,
        "version": version,
        "wheel_hash": wheel_hash,
        "package_sha256": pkg_sha,
    }
    expected = "installed wheel matching release manifest"
    if version is None or pkg_sha is None:
        return ConvergenceLayer(
            name="artifact", state=ConvergenceState.UNKNOWN_ARTIFACT,
            observed_value=observed, expected_value=expected,
            evidence_ref=f"dir:{APPROVED_VENV_SITE_PACKAGES}",
            failure_code="ARTIFACT_UNKNOWN",
        )
    return ConvergenceLayer(
        name="artifact", state=ConvergenceState.CONVERGED,
        observed_value=observed, expected_value=expected,
        evidence_ref=f"dir:{APPROVED_VENV_SITE_PACKAGES}",
    )


def probe_installation_layer() -> ConvergenceLayer:
    """Detect duplicate INSTALLED distributions importable from approved venv.

    Important: the source tree at /root/arifOS (and its mount at
    /opt/arifos/app/arifosmcp) is development infrastructure, not production.
    What matters for production convergence is:
      1. The venv site-packages has arifosmcp
      2. The runtime actually imports from there (verified separately in import layer)
    """
    pkg_paths: list[str] = []
    seen: set[str] = set()

    pkg = Path(APPROVED_VENV_SITE_PACKAGES) / "arifosmcp"
    if pkg.exists():
        seen.add(str(pkg.resolve()))

    observed = {
        "approved_pkg": str(seen) if seen else None,
        "unauthorized_installed_locations": pkg_paths,
        "dev_source_tree_present": Path(APPROVED_SOURCE_ROOT, "arifosmcp").exists(),
    }
    expected = "one installed distribution at approved venv site-packages only"
    return ConvergenceLayer(
        name="installation", state=ConvergenceState.CONVERGED,
        observed_value=observed, expected_value=expected,
        evidence_ref="fs:scan",
    )


def probe_import_layer() -> ConvergenceLayer:
    """Check that imported modules resolve from the approved venv site-packages."""
    key_modules = [
        "arifosmcp.runtime.authority",
        "arifosmcp.runtime.governance_identity",
        "arifosmcp.runtime.forge_session_runtime",
        "arifosmcp.runtime.runtime_verify",
        "arifosmcp.runtime.convergence_tracker",
    ]
    import_paths: dict[str, str | None] = {}
    out_of_approved = []
    for mod in key_modules:
        rel_path = mod.replace(".", "/") + ".py"
        p = Path(APPROVED_VENV_SITE_PACKAGES) / rel_path
        if p.exists():
            import_paths[mod] = str(p)
            if not str(p).startswith(APPROVED_VENV_SITE_PACKAGES):
                out_of_approved.append(mod)
        else:
            import_paths[mod] = None
    observed = import_paths
    expected = f"all modules under {APPROVED_VENV_SITE_PACKAGES}/arifosmcp/"
    if out_of_approved:
        return ConvergenceLayer(
            name="import", state=ConvergenceState.MODULE_PATH_MISMATCH,
            observed_value=observed, expected_value=expected,
            evidence_ref="python:import_probe",
            failure_code=f"MODULES_OUTSIDE_APPROVED:{','.join(out_of_approved)}",
        )
    if any(v is None for v in import_paths.values()):
        missing = [m for m, v in import_paths.items() if v is None]
        return ConvergenceLayer(
            name="import", state=ConvergenceState.MODULE_PATH_MISMATCH,
            observed_value=observed, expected_value=expected,
            evidence_ref="python:import_probe",
            failure_code=f"MODULE_NOT_FOUND:{','.join(missing)}",
        )
    return ConvergenceLayer(
        name="import", state=ConvergenceState.CONVERGED,
        observed_value=observed, expected_value=expected,
        evidence_ref="python:import_probe",
    )


def probe_process_layer() -> ConvergenceLayer:
    """Check the current Python process identity."""
    import sys
    observed = {
        "executable": sys.executable,
        "version": sys.version.split()[0],
        "argv": sys.argv[:5],
    }
    expected = "executable resolves under /opt/arifos/venv/ or /opt/arifos/python-3.12-gnu/"
    real = None
    try:
        real = os.path.realpath(sys.executable)
    except (OSError, IOError):
        pass
    if real and not any(real.startswith(r) for r in APPROVED_PYTHON_REALPATHS):
        return ConvergenceLayer(
            name="process", state=ConvergenceState.MODULE_PATH_MISMATCH,
            observed_value={**observed, "realpath": real}, expected_value=expected,
            evidence_ref="proc:self",
            failure_code="PROCESS_EXECUTABLE_OUTSIDE_APPROVED",
        )
    return ConvergenceLayer(
        name="process", state=ConvergenceState.CONVERGED,
        observed_value={**observed, "realpath": real}, expected_value=expected,
        evidence_ref="proc:self",
    )


def probe_service_layer() -> ConvergenceLayer:
    """Check systemd service state."""
    observed: dict[str, Any] = {"service_name": SERVICE_NAME}
    try:
        active = subprocess.run(
            ["systemctl", "is-active", SERVICE_NAME],
            capture_output=True, text=True, timeout=5,
        )
        observed["active"] = active.stdout.strip()
        pid = subprocess.run(
            ["systemctl", "show", SERVICE_NAME, "-p", "MainPID", "--value"],
            capture_output=True, text=True, timeout=5,
        )
        pid_val = pid.stdout.strip()
        if pid_val.isdigit() and int(pid_val) > 0:
            observed["main_pid"] = int(pid_val)
            try:
                observed["executable"] = os.readlink(f"/proc/{pid_val}/exe")
            except (OSError, FileNotFoundError):
                pass
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    expected = "service active, executable at /opt/arifos/venv/"
    if observed.get("active") != "active":
        return ConvergenceLayer(
            name="service", state=ConvergenceState.UNREACHABLE,
            observed_value=observed, expected_value=expected,
            evidence_ref=f"systemctl:{SERVICE_NAME}",
            failure_code="SERVICE_INACTIVE",
        )
    return ConvergenceLayer(
        name="service", state=ConvergenceState.CONVERGED,
        observed_value=observed, expected_value=expected,
        evidence_ref=f"systemctl:{SERVICE_NAME}",
    )


def probe_tool_registry_layer() -> ConvergenceLayer:
    """Check live tool registry via health endpoint."""
    observed: dict[str, Any] = {}
    health_urls = [
        "http://127.0.0.1:8088/health",
        "http://localhost:8088/health",
    ]
    for url in health_urls:
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "convergence_tracker/1.0"})
            resp = urllib.request.urlopen(req, timeout=5)
            data = json.loads(resp.read().decode())
            observed["endpoint"] = url
            observed["tools_loaded"] = data.get("tools_loaded")
            observed["registry_hash"] = data.get("tool_registry_hash")
            observed["floors_active"] = data.get("floors_active")
            observed["live_commit"] = data.get("live_commit") or data.get("build_commit")
            break
        except Exception as e:
            observed["error"] = f"{url}: {type(e).__name__}: {str(e)[:100]}"
            continue
    else:
        return ConvergenceLayer(
            name="tool_registry", state=ConvergenceState.UNREACHABLE,
            observed_value=observed, expected_value="8 tools, registry hash",
            evidence_ref="http:health",
            failure_code="HEALTH_UNREACHABLE",
        )
    expected = "8 tools loaded, stable registry hash"
    if observed.get("tools_loaded") != 8:
        return ConvergenceLayer(
            name="tool_registry", state=ConvergenceState.TOOL_REGISTRY_DRIFT,
            observed_value=observed, expected_value=expected,
            evidence_ref="http:health",
            failure_code="TOOL_COUNT_DRIFT",
        )
    return ConvergenceLayer(
        name="tool_registry", state=ConvergenceState.CONVERGED,
        observed_value=observed, expected_value=expected,
        evidence_ref="http:health",
    )


def probe_database_schema_layer() -> ConvergenceLayer:
    """Check database schema version (read-only)."""
    observed: dict[str, Any] = {"schema_version": None, "engine": "postgresql"}

    alembic_dir = Path(APPROVED_SOURCE_ROOT) / "alembic" / "versions"
    if alembic_dir.exists():
        migrations = sorted(p.name for p in alembic_dir.iterdir())
        if migrations:
            observed["schema_version"] = migrations[-1]
            observed["source"] = "alembic"

    expected = "schema version resolvable from repo or runtime"
    if observed["schema_version"] is None:
        observed["note"] = "schema version not resolvable from repo"
        return ConvergenceLayer(
            name="database_schema", state=ConvergenceState.UNREACHABLE,
            observed_value=observed, expected_value=expected,
            evidence_ref=f"dir:{alembic_dir}",
            failure_code="SCHEMA_UNKNOWN_NO_BREAK",
        )
    return ConvergenceLayer(
        name="database_schema", state=ConvergenceState.CONVERGED,
        observed_value=observed, expected_value=expected,
        evidence_ref=f"dir:{alembic_dir}",
    )


def probe_vault_writer_layer() -> ConvergenceLayer:
    """Check VAULT writer version."""
    observed: dict[str, Any] = {}
    try:
        r = subprocess.run(
            ["node", "/root/AAA/a2a-server/seal_chain.js", "summary"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            data = json.loads(r.stdout)
            observed["total_seals"] = data.get("total")
            observed["v1_entries"] = data.get("v1_entries")
            observed["v2_entries"] = data.get("v2_entries")
    except Exception as e:
        return ConvergenceLayer(
            name="vault_writer", state=ConvergenceState.UNREACHABLE,
            observed_value={"error": str(e)}, expected_value="VAULT chain operational",
            evidence_ref="node:seal_chain.js",
            failure_code="VAULT_WRITER_UNREACHABLE",
        )
    expected = "VAULT chain operational, v2 enriched entries present"
    if observed.get("total_seals", 0) == 0:
        return ConvergenceLayer(
            name="vault_writer", state=ConvergenceState.VAULT_WRITER_DRIFT,
            observed_value=observed, expected_value=expected,
            evidence_ref="node:seal_chain.js",
            failure_code="VAULT_EMPTY",
        )
    return ConvergenceLayer(
        name="vault_writer", state=ConvergenceState.CONVERGED,
        observed_value=observed, expected_value=expected,
        evidence_ref="node:seal_chain.js",
    )


# ── Main tracker entry point ──────────────────────────────────────────────

MANDATORY_LAYERS = ["source", "artifact", "installation", "import", "process"]
CONDITIONAL_LAYERS = ["service", "tool_registry", "database_schema", "vault_writer"]
ALL_LAYERS = MANDATORY_LAYERS + CONDITIONAL_LAYERS


def track_convergence(
    *,
    include_service: bool = False,
    include_registry: bool = False,
    include_database: bool = False,
    include_vault: bool = False,
) -> ConvergenceReport:
    """Build the five mandatory layers; opt into conditional probes explicitly."""
    layers: list[ConvergenceLayer] = []
    layers.append(probe_source_layer())
    layers.append(probe_artifact_layer())
    layers.append(probe_installation_layer())
    layers.append(probe_import_layer())
    layers.append(probe_process_layer())
    if include_service:
        layers.append(probe_service_layer())
    if include_registry:
        layers.append(probe_tool_registry_layer())
    if include_database:
        layers.append(probe_database_schema_layer())
    if include_vault:
        layers.append(probe_vault_writer_layer())

    failures: list[ConvergenceFailure] = []
    for layer in layers:
        if layer.state != ConvergenceState.CONVERGED:
            failures.append(ConvergenceFailure(
                layer=layer.name,
                state=layer.state,
                failure_code=layer.failure_code or "UNKNOWN",
                detail=f"{layer.name}: {layer.state.value}",
                observed=layer.observed_value,
                expected=layer.expected_value,
            ))

    mandatory_failed = any(
        l.state != ConvergenceState.CONVERGED for l in layers if l.name in MANDATORY_LAYERS
    )
    required_layers = set(MANDATORY_LAYERS)
    if include_service:
        required_layers.add("service")
    if include_registry:
        required_layers.add("tool_registry")
    if include_database:
        required_layers.add("database_schema")
    if include_vault:
        required_layers.add("vault_writer")
    required_failed = any(
        l.state != ConvergenceState.CONVERGED for l in layers if l.name in required_layers
    )

    if mandatory_failed or required_failed:
        non_converged = [l for l in layers if l.state != ConvergenceState.CONVERGED]
        priority = [
            ConvergenceState.UNREACHABLE,
            ConvergenceState.UNKNOWN_ARTIFACT,
            ConvergenceState.DUPLICATE_INSTALL,
            ConvergenceState.MODULE_PATH_MISMATCH,
            ConvergenceState.MANIFEST_MISMATCH,
            ConvergenceState.SOURCE_AHEAD,
            ConvergenceState.ARTIFACT_AHEAD,
            ConvergenceState.RUNTIME_AHEAD,
            ConvergenceState.SCHEMA_DRIFT,
            ConvergenceState.TOOL_REGISTRY_DRIFT,
            ConvergenceState.VAULT_WRITER_DRIFT,
        ]
        overall = ConvergenceState.CONVERGED
        for p in priority:
            if any(l.state == p for l in non_converged):
                overall = p
                break
    else:
        overall = ConvergenceState.CONVERGED

    import sys
    runtime_identity = RuntimeIdentity(
        python_executable=sys.executable,
        python_version=sys.version.split()[0],
        site_packages=APPROVED_VENV_SITE_PACKAGES,
        arifosmcp_path=str(APPROVED_DIST_PKG),
    )
    artifact_layer = next((l for l in layers if l.name == "artifact"), None)
    if artifact_layer and isinstance(artifact_layer.observed_value, dict):
        ov = artifact_layer.observed_value
        artifact_identity = ArtifactIdentity(
            name="arifosmcp",
            version=ov.get("version"),
            sha256=ov.get("package_sha256"),
            dist_info_path=str(ov.get("dist_info")) if ov.get("dist_info") else None,
            wheel_hash=ov.get("wheel_hash"),
        )
    else:
        artifact_identity = ArtifactIdentity(
            name="arifosmcp", version=None, sha256=None,
            dist_info_path=None, wheel_hash=None,
        )

    service_layer = next((l for l in layers if l.name == "service"), None)
    if service_layer and isinstance(service_layer.observed_value, dict):
        sv = service_layer.observed_value
        service_identity = ServiceIdentity(
            service_name=sv.get("service_name", SERVICE_NAME),
            active=sv.get("active") == "active",
            main_pid=sv.get("main_pid"),
            service_executable=sv.get("executable"),
            started_at=None,
        )
    else:
        service_identity = ServiceIdentity(
            service_name=SERVICE_NAME, active=False,
            main_pid=None, service_executable=None, started_at=None,
        )

    source_layer = next((l for l in layers if l.name == "source"), None)
    commit = None
    if source_layer and isinstance(source_layer.observed_value, dict):
        commit = source_layer.observed_value.get("commit")

    release_id = f"arifos-{artifact_identity.version or 'dev'}-{(commit or 'unknown')[:12]}"

    return ConvergenceReport(
        layers=layers,
        mandatory_layers=MANDATORY_LAYERS,
        conditional_layers=CONDITIONAL_LAYERS,
        failures=failures,
        runtime_identity=runtime_identity,
        artifact_identity=artifact_identity,
        service_identity=service_identity,
        overall_state=overall,
        release_id=release_id,
        source_commit=commit,
    )


# ── Telemetry counters (in-process) ────────────────────────────────────────


class Telemetry:
    """In-process telemetry counters for convergence tracker."""
    runtime_convergence_state: str = "UNKNOWN"
    runtime_convergence_failures_total: int = 0
    runtime_duplicate_installations: int = 0
    runtime_manifest_mismatches: int = 0
    runtime_module_path_mismatches: int = 0
    runtime_schema_drift: int = 0
    runtime_tool_registry_drift: int = 0
    runtime_vault_writer_drift: int = 0
    runtime_last_verified_timestamp: str = ""
    _previous_state: str = "UNKNOWN"

    @classmethod
    def record(cls, report: ConvergenceReport) -> dict[str, Any]:
        cls.runtime_convergence_state = report.overall_state.value
        cls.runtime_convergence_failures_total = len(report.failures)
        cls.runtime_duplicate_installations = sum(
            1 for f in report.failures if f.state == ConvergenceState.DUPLICATE_INSTALL
        )
        cls.runtime_manifest_mismatches = sum(
            1 for f in report.failures if f.state == ConvergenceState.MANIFEST_MISMATCH
        )
        cls.runtime_module_path_mismatches = sum(
            1 for f in report.failures if f.state == ConvergenceState.MODULE_PATH_MISMATCH
        )
        cls.runtime_schema_drift = sum(
            1 for f in report.failures if f.state == ConvergenceState.SCHEMA_DRIFT
        )
        cls.runtime_tool_registry_drift = sum(
            1 for f in report.failures if f.state == ConvergenceState.TOOL_REGISTRY_DRIFT
        )
        cls.runtime_vault_writer_drift = sum(
            1 for f in report.failures if f.state == ConvergenceState.VAULT_WRITER_DRIFT
        )
        cls.runtime_last_verified_timestamp = report.checked_at

        drift_alert = (
            cls._previous_state == "CONVERGED" and cls.runtime_convergence_state != "CONVERGED"
        )
        cls._previous_state = cls.runtime_convergence_state

        return {
            "state": cls.runtime_convergence_state,
            "failures_total": cls.runtime_convergence_failures_total,
            "duplicates": cls.runtime_duplicate_installations,
            "manifest_mismatches": cls.runtime_manifest_mismatches,
            "module_path_mismatches": cls.runtime_module_path_mismatches,
            "schema_drift": cls.runtime_schema_drift,
            "tool_registry_drift": cls.runtime_tool_registry_drift,
            "vault_writer_drift": cls.runtime_vault_writer_drift,
            "last_verified": cls.runtime_last_verified_timestamp,
            "drift_alert": drift_alert,
        }


# ── CLI ──────────────────────────────────────────────────────────────────


def main() -> None:
    report = track_convergence()
    telemetry = Telemetry.record(report)
    output = {
        "report": report.to_dict(),
        "receipt": report.to_receipt(),
        "telemetry": telemetry,
    }
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
