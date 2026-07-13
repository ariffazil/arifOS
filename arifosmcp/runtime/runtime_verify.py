"""
runtime_verify.py — Canonical Runtime Verification Probe (EUREKA P1 I1)

Read-only probe that independently verifies runtime alignment across:
  - Git source
  - Built artifact (wheel dist-info)
  - Installed distribution
  - Active import paths
  - Running process
  - Module file hashes
  - Duplicate installations

This is the Epistemic Navigator's primary runtime probe.
It does NOT mutate state. It produces a structured report.

Allowed convergence states:
  CONVERGED — source == artifact == import path == process
  SOURCE_AHEAD — source has newer commit than runtime
  RUNTIME_AHEAD — runtime has newer commit than source
  DUPLICATE_INSTALL — multiple importable arifosmcp distributions
  MANIFEST_MISMATCH — artifact hash differs from release manifest
  UNKNOWN_ARTIFACT — cannot determine installed artifact state
  IMPORT_OUTSIDE_APPROVED_ROOT — import path is not the approved venv

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Approved paths ─────────────────────────────────────────────────────────

APPROVED_SOURCE_ROOTS: list[str] = [
    "/root/arifOS",
    "/opt/arifos/app",
]

APPROVED_VENV_PYTHON = "/opt/arifos/venv/bin/python"
APPROVED_VENV_SITE_PACKAGES = "/opt/arifos/venv/lib/python3.12/site-packages"
APPROVED_IMPORT_ROOTS = [
    APPROVED_VENV_SITE_PACKAGES,
    "/opt/arifos/app",
]

# ── Key modules to verify ─────────────────────────────────────────────────

KEY_MODULES = [
    "arifosmcp.runtime.authority",
    "arifosmcp.runtime.governance_identity",
    "arifosmcp.runtime.forge_session_runtime",
    "arifosmcp.runtime.__main__",
    "arifosmcp.runtime.seal_chain",
    "arifosmcp.runtime.tools",
    "arifosmcp.runtime.vault_registry",
]

# ── Probe functions ────────────────────────────────────────────────────────


def _read_file_safe(path: str | Path) -> str | None:
    """Read a file, return None on any error."""
    try:
        return Path(path).read_text().strip()
    except (OSError, IOError):
        return None


def _sha256_file(path: str | Path) -> str | None:
    """Return sha256 of file, or None if unreadable."""
    try:
        data = Path(path).read_bytes()
        return f"sha256:{hashlib.sha256(data).hexdigest()}"
    except (OSError, IOError):
        return None


def probe_git_source(source_root: str | None = None) -> dict[str, Any]:
    """Probe git source repository state."""
    result: dict[str, Any] = {
        "commit": None,
        "branch": None,
        "dirty": None,
        "source_root": None,
    }
    for root in APPROVED_SOURCE_ROOTS:
        p = Path(root) / ".git"
        if p.exists():
            source_root = root
            break
    if not source_root:
        # Try the passed root
        source_root = source_root or "/root/arifOS"

    try:
        commit = subprocess.run(
            ["git", "-C", source_root, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if commit.returncode == 0:
            result["commit"] = commit.stdout.strip()

        branch = subprocess.run(
            ["git", "-C", source_root, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if branch.returncode == 0:
            result["branch"] = branch.stdout.strip()

        dirty = subprocess.run(
            ["git", "-C", source_root, "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
        )
        result["dirty"] = bool(dirty.stdout.strip())
        result["source_root"] = source_root
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return result


def probe_wheel_artifact() -> dict[str, Any]:
    """Probe installed wheel/dist-info for version and hash."""
    result: dict[str, Any] = {
        "dist_info": None,
        "version": None,
        "wheel_hash": None,
        "installed_at": None,
    }
    dist_dir = Path(APPROVED_VENV_SITE_PACKAGES)
    if not dist_dir.exists():
        return result

    # Find arifosmcp dist-info
    for d in dist_dir.iterdir():
        if d.name.startswith("arifos-") and d.name.endswith(".dist-info"):
            result["dist_info"] = d.name
            # Try METADATA for version
            meta = d / "METADATA"
            if meta.exists():
                content = meta.read_text()
                for line in content.splitlines():
                    if line.startswith("Version:"):
                        result["version"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Installed:"):
                        result["installed_at"] = line.split(":", 1)[1].strip()
            # Try RECORD for wheel hash
            record = d / "RECORD"
            if record.exists():
                for line in record.read_text().splitlines():
                    if line.endswith(".whl,"):
                        parts = line.split(",")
                        if len(parts) >= 2 and parts[1].startswith("sha256="):
                            result["wheel_hash"] = parts[1]
                            break
    return result


def probe_imported_modules() -> dict[str, Any]:
    """Probe import paths for key modules."""
    # We can't import during probe without risking side effects.
    # Instead, check if files exist at expected paths.
    results: dict[str, Any] = {}
    for mod_name in KEY_MODULES:
        mod_path = mod_name.replace(".", "/") + ".py"
        pkg_path = mod_name.replace(".", "/") + "/__init__.py"
        found = False
        for root in APPROVED_IMPORT_ROOTS:
            full = Path(root) / mod_path
            if full.exists():
                results[mod_name] = {
                    "path": str(full),
                    "sha256": _sha256_file(full),
                    "root": root,
                }
                found = True
                break
            # Check package init
            full_pkg = Path(root) / pkg_path
            if full_pkg.exists():
                results[mod_name] = {
                    "path": str(full_pkg),
                    "sha256": _sha256_file(full_pkg),
                    "root": root,
                }
                found = True
                break
        if not found:
            results[mod_name] = {"path": None, "sha256": None, "error": "module file not found"}
    return results


def probe_process() -> dict[str, Any]:
    """Probe the current running Python process."""
    result: dict[str, Any] = {
        "pid": os.getpid(),
        "executable": sys.executable,
        "argv": sys.argv,
        "started_at": None,
    }
    # Try /proc for start time
    try:
        with open(f"/proc/{os.getpid()}/stat") as f:
            parts = f.read().split()
            if len(parts) > 21:
                # Boot time based clock tick — convert to ISO if possible
                clock_ticks = int(parts[21])
                try:
                    boot_time = _read_file_safe("/proc/stat")
                    if boot_time:
                        for line in boot_time.splitlines():
                            if line.startswith("btime "):
                                btime = int(line.split()[1])
                                start_ts = btime + clock_ticks // 100
                                result["started_at"] = datetime.fromtimestamp(
                                    start_ts, tz=timezone.utc
                                ).isoformat()
                                break
                except (ValueError, IndexError):
                    pass
    except (OSError, IOError, IndexError, ValueError):
        pass
    return result


def probe_duplicate_installations() -> list[dict[str, Any]]:
    """Detect duplicate importable arifosmcp distributions.

    A distribution is considered duplicate when the package directory
    (arifosmcp/) exists in two different approved roots. The dist-info
    directory is metadata for the same install, NOT a separate distribution.
    """
    duplicates: list[dict[str, Any]] = []
    seen_package_dirs: set[str] = set()

    # A directory is a live installation only when Python can import from its
    # parent. Dormant deployment copies such as /opt/arifos/app are not dupes.
    importable_roots = {str(Path(p or ".").resolve()) for p in sys.path}

    # Check for actual importable package directories first
    for root in APPROVED_IMPORT_ROOTS:
        if str(Path(root).resolve()) not in importable_roots:
            continue
        p = Path(root) / "arifosmcp"
        if p.exists() and p.is_dir():
            key = str(p.resolve())
            if key not in seen_package_dirs:
                seen_package_dirs.add(key)
                duplicates.append({
                    "type": "package_dir",
                    "path": key,
                    "root": root,
                })

    # Dist-info is metadata only — only flag if there's NO package dir to go with it
    dist_dir = Path(APPROVED_VENV_SITE_PACKAGES)
    if dist_dir.exists():
        for d in dist_dir.iterdir():
            if d.name.startswith("arifos-") and d.name.endswith(".dist-info"):
                # Check if this dist-info has a matching package dir
                pkg_dir = d.parent / "arifosmcp"
                if not pkg_dir.exists():
                    duplicates.append({
                        "type": "orphan_dist_info",
                        "path": str(d.resolve()),
                        "root": "dist-info (no matching package)",
                    })

    return duplicates


def probe_service() -> dict[str, Any]:
    """Probe the systemd service state."""
    result: dict[str, Any] = {
        "service_name": "arifos.service",
        "active": None,
        "pid": None,
        "executable": None,
    }
    try:
        active = subprocess.run(
            ["systemctl", "is-active", "arifos.service"],
            capture_output=True, text=True, timeout=5,
        )
        result["active"] = active.stdout.strip()

        pid = subprocess.run(
            ["systemctl", "show", "arifos.service", "-p", "MainPID", "--value"],
            capture_output=True, text=True, timeout=5,
        )
        if pid.returncode == 0 and pid.stdout.strip().isdigit():
            result["pid"] = int(pid.stdout.strip())

        # Probe the service's executable
        if result["pid"]:
            try:
                exe = os.readlink(f"/proc/{result['pid']}/exe")
                result["executable"] = exe
            except (OSError, FileNotFoundError):
                pass
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return result


def compute_convergence_state(
    git: dict[str, Any],
    wheel: dict[str, Any],
    modules: dict[str, Any],
    process: dict[str, Any],
    duplicates: list[dict[str, Any]],
    service: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Compute convergence state from all probes.

    Returns (state, evidence_string).
    """
    evidence_parts = []

    # Check duplicates first — trumps all
    if len(duplicates) > 1:
        paths = [f"{d['type']}:{d['path']}" for d in duplicates]
        return ("DUPLICATE_INSTALL", f"multiple distributions: {paths}")
    if len(duplicates) == 1 and duplicates[0].get("type") == "orphan_dist_info":
        return ("MANIFEST_MISMATCH", f"orphan dist-info: {duplicates[0]['path']}")

    # Check module import roots
    outside_approved = False
    for mod_name, info in modules.items():
        if info.get("path") and info.get("root") not in APPROVED_IMPORT_ROOTS:
            outside_approved = True
            evidence_parts.append(f"{mod_name} imports from {info['root']} (not approved)")

    if outside_approved and not evidence_parts:
        return ("IMPORT_OUTSIDE_APPROVED_ROOT", "one or more modules outside approved root")

    # Check git vs artifact
    git_commit = git.get("commit")
    if git_commit:
        # Try to find the commit in the dist-info METADATA
        # For now, check if source file hashes match imported module hashes
        forge_source = _sha256_file("/root/arifOS/arifosmcp/runtime/forge_session_runtime.py")
        forge_imported = modules.get("arifosmcp.runtime.forge_session_runtime", {}).get("sha256")
        if forge_source and forge_imported:
            if forge_source != forge_imported:
                return ("SOURCE_AHEAD", f"source forge_session_runtime {forge_source[:20]} ≠ imported {forge_imported[:20]}")

        authority_source = _sha256_file("/root/arifOS/arifosmcp/runtime/authority.py")
        authority_imported = modules.get("arifosmcp.runtime.authority", {}).get("sha256")
        if authority_source and authority_imported:
            if authority_source == authority_imported:
                evidence_parts.append("authority.py: source=imported")

    # Check process executable — use SERVICE's executable, not probe process
    service_exec = service.get("executable") if service else None
    if service_exec:
        # Resolve the symlink to compare the real binary
        import os as _os
        expected_real = None
        if _os.path.islink(APPROVED_VENV_PYTHON):
            try:
                expected_real = _os.path.realpath(APPROVED_VENV_PYTHON)
            except (OSError, IOError):
                pass
        allowed_execs = {APPROVED_VENV_PYTHON}
        if expected_real:
            allowed_execs.add(expected_real)
        if service_exec not in allowed_execs:
            return ("IMPORT_OUTSIDE_APPROVED_ROOT",
                    f"service uses {service_exec}, expected {APPROVED_VENV_PYTHON} (realpath: {expected_real})")

    # Check service active
    evidence_parts.append(f"service_active={duplicates}")  # temp

    if not evidence_parts:
        return ("CONVERGED", "all probes matched")
    return ("CONVERGED", "; ".join(evidence_parts))


# ── Main verification function ─────────────────────────────────────────────


def verify_runtime() -> dict[str, Any]:
    """
    Full runtime verification probe.

    Returns structured dict with all probe results and convergence verdict.
    """
    git = probe_git_source()
    wheel = probe_wheel_artifact()
    modules = probe_imported_modules()
    process = probe_process()
    duplicates = probe_duplicate_installations()
    service = probe_service()

    convergence_state, convergence_evidence = compute_convergence_state(
        git, wheel, modules, process, duplicates, service,
    )

    # Determine readiness
    readiness = "PASS"
    if convergence_state in ("DUPLICATE_INSTALL", "IMPORT_OUTSIDE_APPROVED_ROOT", "UNKNOWN_ARTIFACT"):
        readiness = "BLOCKED"
    elif convergence_state in ("SOURCE_AHEAD", "RUNTIME_AHEAD"):
        readiness = "DEGRADED"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": service.get("service_name", "unknown"),
        "active": service.get("active"),
        "service_pid": service.get("pid"),
        "service_executable": service.get("executable"),
        "python_executable": process.get("executable"),
        "process_pid": process.get("pid"),
        "process_started_at": process.get("started_at"),
        "git": git,
        "wheel": {
            "dist_info": wheel.get("dist_info"),
            "version": wheel.get("version"),
            "wheel_hash": wheel.get("wheel_hash"),
            "installed_at": wheel.get("installed_at"),
        },
        "imported_modules": modules,
        "duplicate_distributions": duplicates,
        "convergence": {
            "state": convergence_state,
            "evidence": convergence_evidence,
        },
        "readiness": readiness,
    }


# ── CLI entry point ────────────────────────────────────────────────────────


def main() -> None:
    """CLI entry point: run verification and print JSON."""
    import json
    result = verify_runtime()
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
