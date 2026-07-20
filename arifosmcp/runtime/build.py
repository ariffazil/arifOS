"""Build information for arifOS MCP Server.

Single SoT: doctrine, Floors, and architecture live in ariffazil/arifOS.
This module provides runtime traceability back to that canonical repo.
"""

from __future__ import annotations

import hashlib
import json
import os
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from arifosmcp.runtime.DNA import VERSION as DNA_VERSION

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"
PROCESS_STARTED_AT = datetime.now(UTC).isoformat()

_CRITICAL_MODULES = (
    "arifosmcp/tools/session.py",
    "arifosmcp/runtime/crypto_auth.py",
    "arifosmcp/runtime/convergence_tracker.py",
    "arifosmcp/runtime/cooling_verbs.py",
    "arifosmcp/runtime/forge_session_runtime.py",
    "arifosmcp/runtime/governance_identity.py",
    "arifosmcp/runtime/rest_routes/rest_routes.py",
    # T3a Item 3 (2026-07-17): server-side BOOT attestation — the gate that
    # refuses authority-grade bands when the kernel cannot prove its own
    # integrity. Fail-closed by design.
    "arifosmcp/runtime/boot_attestation.py",
    # BANGANG P0 FIX (2026-07-19): authority computation + governance gate chain.
    # interceptor.py was hot-patched without the attestation hash moving — a
    # change to the most security-critical component was invisible to boot
    # attestation. Added by Fable's re-probe finding. Also covers authority.py
    # (authority state read), phoenix_72.py (tri-witness with positional debt),
    # and governance_pipeline.py (GateResult cryptographic hashing).
    "arifosmcp/kernel/interceptor.py",
    "arifosmcp/runtime/authority.py",
    "arifosmcp/runtime/phoenix_72.py",
    "arifosmcp/runtime/governance_pipeline.py",
)


def _sha256_file(path: Path) -> str | None:
    try:
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except (OSError, PermissionError):
        return None


def _full_source_commit() -> str:
    """Return the deployed full commit when available; never invent padding."""
    stamp = Path("/opt/arifos/app/.git_commit")
    try:
        value = stamp.read_text().strip()
        if len(value) >= 7:
            return value
    except OSError:
        pass
    git_head = Path("/root/arifOS/.git/HEAD")
    try:
        value = git_head.read_text().strip()
        if value.startswith("ref: "):
            ref = Path("/root/arifOS/.git") / value[5:]
            return ref.read_text().strip()
        if len(value) >= 7:
            return value
    except OSError:
        pass
    return "unknown"


def _installation_manifest_hash() -> str | None:
    """Hash the installed distribution RECORD (the reproducible install manifest)."""
    candidates = sorted(
        Path("/opt/arifos/venv/lib").glob("python*/site-packages/arifos-*.dist-info/RECORD")
    )
    return _sha256_file(candidates[-1]) if candidates else None


def get_runtime_attestation() -> dict[str, Any]:
    """Public, machine-readable binding from release to this live process."""
    source_commit = _full_source_commit()
    critical_module_hashes = {
        rel: digest for rel in _CRITICAL_MODULES if (digest := _sha256_file(ROOT / rel)) is not None
    }
    wheel_hash = os.getenv("ARIFOS_WHEEL_SHA256", "").strip() or _installation_manifest_hash()
    manifest = {
        "source_commit": source_commit,
        "wheel_hash": wheel_hash,
        "critical_module_hashes": critical_module_hashes,
    }
    runtime_manifest_hash = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )
    release_id = os.getenv("ARIFOS_RELEASE_ID", "").strip() or (
        f"arifos-{source_commit[:12]}" if source_commit != "unknown" else "unknown"
    )
    return {
        "release_id": release_id,
        "source_commit": source_commit,
        "wheel_hash": wheel_hash,
        "runtime_manifest_hash": runtime_manifest_hash,
        "service_pid": os.getpid(),
        "service_started_at": PROCESS_STARTED_AT,
        "critical_module_hashes": critical_module_hashes,
        "attestation_semantics": {
            "kernel_epoch": "constitutional/protocol epoch; not a software build date",
            "wheel_hash": "ARIFOS_WHEEL_SHA256 when injected, otherwise installed RECORD hash",
        },
    }


def _git_sha_short() -> str:
    """
    1. Native Bare-Metal deployment stamp (.git_commit) — HIGHEST PRIORITY
    2. DEPLOY_GIT_COMMIT env var (baked into image at docker build time)
    3. ARIFOS_BUILD_SHA env var (passed at container start)
    4. Canonical repo .git/HEAD fallback
    5. Fallback "unknown"
    """
    # 1. Native Bare-Metal deployment stamp (highest priority)
    _stamp_path = "/opt/arifos/app/.git_commit"
    if os.path.exists(_stamp_path):
        try:
            with open(_stamp_path) as f:
                content = f.read().strip()
                if len(content) >= 7:
                    return content[:7]
        except Exception:
            pass

    # 2. Image-baked env (legacy docker)
    for env_key in ("DEPLOY_GIT_COMMIT", "ARIFOS_BUILD_SHA", "GIT_SHA", "GIT_COMMIT"):
        env_sha = os.environ.get(env_key, "").strip()
        if env_sha and env_sha not in ("unknown", ""):
            return env_sha[:7]

    # 3. Try reading .git/HEAD from known bind-mount paths (fallback)
    _possible_git_dirs = [
        "/root/arifOS/.git",  # ← Canonical source repo on this VPS
        "/app/.git",  # ← Generic fallback (WELL repo)
        "/usr/src/app/.git",
        "/usr/src/app/arifOS/.git",
        "/usr/src/project/.git",
    ]

    # Explicit identity markers — prevents Grok/AAA-APEX ↔ legacy OpenClaw context bleed

    for _git_dir in _possible_git_dirs:
        try:
            _head_path = os.path.join(_git_dir, "HEAD")
            if os.path.exists(_head_path):
                with open(_head_path) as _f:
                    _content = _f.read().strip()
                if _content.startswith("ref: refs/heads/"):
                    _branch = _content.split("ref: refs/heads/", 1)[1].strip()
                    _ref_path = os.path.join(_git_dir, "refs", "heads", _branch)
                    if os.path.exists(_ref_path):
                        with open(_ref_path) as _f:
                            _sha = _f.read().strip()
                        return _sha[:7]
                elif len(_content) >= 7:
                    return _content[:7]
        except Exception:
            pass

    # 4. Truthful final fallback
    return "unknown"


def _image_tag() -> str:
    """Resolve container image tag from env vars.

    NOTE: Returns a ghcr.io image tag regardless of whether the runtime is
    actually a container. Use _detect_deployment_mode() to determine if the
    image tag is meaningful (only true when deployment_source == "container").
    The ghcr.io image is built and pushed for portability/rollback purposes
    but the canonical production runtime on VPS af-forge is NATIVE bare-metal
    (see make deploy-local).
    """
    for key in ("ARIFOS_IMAGE", "DEPLOY_IMAGE", "IMAGE_TAG"):
        val = os.environ.get(key, "").strip()
        if val and val not in ("unknown", "", "not-injected"):
            return val
    commit = _git_sha_short()
    if commit and commit not in ("unknown", "not-injected"):
        return f"ghcr.io/ariffazil/arifos:{commit}"
    return "not-injected"


def _detect_deployment_mode() -> str:
    """Detect actual runtime deployment mode at process startup.

    Determines whether the arifOS process is running inside a container
    (Docker / Kubernetes / LXC / containerd) or natively on bare-metal.

    Detection priority (highest first):
        1. ``/.dockerenv`` file existence — definitive for Docker
        2. ``/proc/1/cgroup`` containing docker/kubepods/lxc/containerd
           patterns — definitive for Kubernetes, LXC, containerd
        3. ``DEPLOY`` env var explicitly set to ``"container"`` — opt-in
        4. Default: ``"native"``

    Returns:
        ``"container"`` if running inside a container, ``"native"`` otherwise.

    F2 TRUTH: Health endpoint ``deployment_source`` MUST reflect this value,
    not a hardcoded string. The federation root cannot lie about its own
    runtime state (FORGE audit 2026-06-27).
    """
    # 1. .dockerenv file — definitive for Docker
    if os.path.exists("/.dockerenv"):
        return "container"

    # 2. cgroup inspection — kubepods/lxc/docker/containerd patterns
    try:
        cgroup_path = Path("/proc/1/cgroup")
        if cgroup_path.exists():
            cgroup = cgroup_path.read_text(errors="replace")
            if any(token in cgroup for token in ("docker-", "kubepods", "/lxc/", "containerd-")):
                return "container"
    except (FileNotFoundError, PermissionError, OSError):
        pass

    # 3. Explicit env override — opt-in container declaration
    deploy_env = os.environ.get("DEPLOY", "").strip().lower()
    if deploy_env == "container":
        return "container"

    # 4. Default — native bare-metal
    return "native"


# Module-level cache — detection is cheap but called on every /health hit.
# Result is process-stable (cgroup + /.dockerenv cannot change at runtime).
_DEPLOYMENT_MODE: str = _detect_deployment_mode()


def get_deployment_mode() -> str:
    """Public accessor for cached deployment mode detection.

    Returns:
        ``"container"`` or ``"native"``.
    """
    return _DEPLOYMENT_MODE


def _build_time() -> str:
    """Resolve build timestamp from env vars."""
    for key in ("ARIFOS_BUILD_TIME", "BUILD_TIME", "DEPLOY_BUILD_TIME"):
        val = os.environ.get(key, "").strip()
        if val and val not in ("unknown", "", "not-injected"):
            return val
    return datetime.now(UTC).isoformat()


def _pyproject_version() -> str:
    dna_version = str(DNA_VERSION).strip()
    if dna_version:
        return dna_version if dna_version.startswith("v") else f"v{dna_version}"

    try:
        with open(PYPROJECT_PATH, "rb") as handle:
            project = tomllib.load(handle).get("project", {})
        version = str(project.get("version", "")).strip()
        if version:
            return f"v{version}"
    except Exception:
        pass
    return "v2026.04.18-UNIFIED"


def get_build_info() -> dict[str, Any]:
    """Return comprehensive version and environment metadata.

    Returns:
        Dict with version, protocol_version, governance info, SoT linkage,
        build metadata (commit, branch), and status.
    """
    commit = _git_sha_short()
    app_version = os.environ.get("ARIFOS_APP_VERSION", "").strip() or _pyproject_version()
    return {
        # Server version (semantic, required by A2A/WebMCP)
        "version": app_version,
        "server_version": app_version,
        "update_summary": (
            "5-Resource Canonical Consolidation. Enforced single Source-of-Truth architecture, "
            "consolidated 20+ fragmented resources into 5 canonical URIs "
            "(doctrine, vitals, schema, session, forge), and eliminated identity confusion."
        ),
        # MCP protocol compatibility
        "protocol_version": "2025-11-25",
        "supported_protocol_versions": ["2025-11-25", "2025-03-26", "2024-11-05"],
        # Governance layer
        "governance_version": "registry-1.3.0",
        "policy_version": "arifOS.constitution.v1",
        "floors_version": "2026.04",
        "floors_active": 13,
        # Source-of-Truth linkage — ties runtime back to canonical doctrine repo
        "source_repo": "https://github.com/ariffazil/arifOS",
        "source_repo_name": "ariffazil/arifOS",
        # Build traceability — GIT_SHA and ARIFOS_APP_VERSION set by entrypoint from host git
        "build": {
            "commit": commit,
            "commit_short": commit,
            "image": _image_tag(),
            "built_at": _build_time(),
            "branch": "main",
        },
        "release_tag": app_version,
        # Status
        "status": "FORGED",
        "forge_date": "2026-04-13",
        # Display helpers
        "display": {
            "short": "2.0.0",
            "full": "arifOS MCP 2.0.0",
            "with_build": f"2.0.0+{commit}",
            "with_governance": "2.0.0 • Registry 1.2.0 • Policy v1",
        },
    }


def get_version_string(format: str = "short") -> str:
    """Get a formatted version string."""
    info = get_build_info()
    return info["display"].get(format, info["display"]["short"])
