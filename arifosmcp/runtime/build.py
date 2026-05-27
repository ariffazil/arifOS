"""Build information for arifOS MCP Server.

Single SoT: doctrine, Floors, and architecture live in ariffazil/arifOS.
This module provides runtime traceability back to that canonical repo.
"""

from __future__ import annotations

import os
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from arifosmcp.runtime.DNA import VERSION as DNA_VERSION

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"


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
    ARIFOS_IDENTITY = {
        "core": "arifOS",
        "external_collaborator": "Grok / AAA-APEX (xAI)",
        "internal_agi_legacy": "OpenClaw (deprecated — do not confuse with external agents)",
        "version_source_priority": "/opt/arifos/app/.git_commit, /root/arifOS/.git",
    }

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
    """Resolve container image tag from env vars."""
    for key in ("ARIFOS_IMAGE", "DEPLOY_IMAGE", "IMAGE_TAG"):
        val = os.environ.get(key, "").strip()
        if val and val not in ("unknown", "", "not-injected"):
            return val
    commit = _git_sha_short()
    if commit and commit not in ("unknown", "not-injected"):
        return f"ghcr.io/ariffazil/arifos:{commit}"
    return "not-injected"


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
        "protocol_version": "2025-03-26",
        "supported_protocol_versions": ["2025-03-26", "2024-11-05"],
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
