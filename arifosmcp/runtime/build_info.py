"""Build information for arifOS MCP Server.

Single SoT: doctrine, Floors, and architecture live in ariffazil/arifOS.
This module provides runtime traceability back to that canonical repo.
"""

from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from typing import Any


def _git_sha_short() -> str:
    """Return the current git short SHA (HEAD), checked in order:
    1. GIT_SHA env var (set by entrypoint from host git)
    2. Direct read of .git/HEAD via known host paths
    3. Fallback hardcoded SHA
    """
    # 1. Env var (set by entrypoint from host git)
    env_sha = os.environ.get("GIT_SHA", "")
    if env_sha and env_sha != "unknown":
        return env_sha

    # 2. Try reading .git/HEAD from known host bind-mount paths
    #    /root/arifOS on host is bind-mounted to various container paths
    _possible_git_dirs = [
        "/root/arifOS/.git",           # host path (may be accessible via nsenter)
        "/usr/src/app/.git",           # if full repo bind-mounted
        "/usr/src/app/arifOS/.git",    # if arifOS subdir bind-mounted
        "/usr/src/project/.git",       # docker-compose volume mount target
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

    # 3. Fallback — only used when no git info available
    return "909c4ca"


def get_build_info() -> dict[str, Any]:
    """Return comprehensive version and environment metadata.

    Returns:
        Dict with version, protocol_version, governance info, SoT linkage,
        build metadata (commit, branch), and status.
    """
    commit = _git_sha_short()
    app_version = os.environ.get("ARIFOS_APP_VERSION", "2026.4.13")
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
