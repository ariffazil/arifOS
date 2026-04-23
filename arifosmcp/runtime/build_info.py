"""Build information for arifOS MCP Server.

Single SoT: doctrine, Floors, and architecture live in ariffazil/arifOS.
This module provides runtime traceability back to that canonical repo.
"""

from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import tomllib
from arifosmcp.runtime.DNA import VERSION as DNA_VERSION


ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"


def _git_sha_short() -> str:
    """Return the current git short SHA (HEAD), checked in order:
    1. Direct read of .git/HEAD via known host paths
    2. GIT_SHA env var
    3. Fallback "unknown"
    """
    # 1. Try reading .git/HEAD from known bind-mount paths
    _possible_git_dirs = [
        "/usr/src/app/.git",
        "/usr/src/app/arifOS/.git",
        "/usr/src/project/.git",
        "/root/arifOS/.git",
    ]
    for _git_dir in _possible_git_dirs:
        try:
            _head_path = os.path.join(_git_dir, "HEAD")
            if os.path.exists(_head_path):
                with open(_head_path, "r") as _f:
                    _content = _f.read().strip()
                if _content.startswith("ref: refs/heads/"):
                    _branch = _content.split("ref: refs/heads/", 1)[1].strip()
                    _ref_path = os.path.join(_git_dir, "refs", "heads", _branch)
                    if os.path.exists(_ref_path):
                        with open(_ref_path, "r") as _f:
                            _sha = _f.read().strip()
                        return _sha[:7]
                elif len(_content) >= 7:
                    return _content[:7]
        except Exception:
            pass

    # 2. Env var fallback
    env_sha = os.environ.get("GIT_SHA", "").strip()
    if env_sha and env_sha != "unknown":
        return env_sha[:7]

    # 3. Truthful final fallback
    return "unknown"


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
        "update_summary": "5-Resource Canonical Consolidation. Enforced single Source-of-Truth architecture, consolidated 20+ fragmented resources into 5 canonical URIs (doctrine, vitals, schema, session, forge), and eliminated identity confusion.",

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
            "built_at": datetime.now(timezone.utc).isoformat(),
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
