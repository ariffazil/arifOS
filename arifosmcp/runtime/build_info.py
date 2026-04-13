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
    """Return the current git short SHA (HEAD), fallback to hardcoded."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            cwd="C:/ariffazil/arifOS",
        ).decode().strip()
    except Exception:
        return "909c4ca"  # v2026.04.07 release SHA


def get_build_info() -> dict[str, Any]:
    """Return comprehensive version and environment metadata.

    Returns:
        Dict with version, protocol_version, governance info, SoT linkage,
        build metadata (commit, branch), and status.
    """
    commit = _git_sha_short()
    app_version = os.environ.get("ARIFOS_APP_VERSION", "2026.04.11")
    return {
        # Server version (semantic, required by A2A/WebMCP)
        "version": app_version,
        "server_version": app_version,
        "update_summary": "Enforced single Source-of-Truth architecture and aligned runtime endpoints. This eliminates doctrine fragmentation and ensures live server status is the undisputed authority for system capabilities.",

        # MCP protocol compatibility
        "protocol_version": "2025-03-26",
        "supported_protocol_versions": ["2025-03-26", "2024-11-05"],

        # Governance layer
        "governance_version": "registry-1.2.0",
        "policy_version": "arifOS.constitution.v1",
        "floors_version": "2026.04",
        "floors_active": 13,

        # Source-of-Truth linkage — ties runtime back to canonical doctrine repo
        "source_repo": "https://github.com/ariffazil/arifOS",
        "source_repo_name": "ariffazil/arifOS",

        # Build traceability
        "build": {
            "commit": commit,
            "commit_short": commit,
            "built_at": datetime.now(timezone.utc).isoformat(),
            "branch": "main",
        },
        "release_tag": "v2026.04.11",

        # Status
        "status": "FORGED",
        "forge_date": "2026-04-11",

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
