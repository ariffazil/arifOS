"""Build information for arifOS MCP Server.

Versioning Strategy:
- server_version: Semantic version for the MCP server release (2.0.0)
- protocol_version: MCP protocol compatibility (2025-03-26)
- governance_version: Registry/constitutional layer version (registry-1.2.0)
- build: Commit hash and build timestamp for traceability
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def get_build_info() -> dict[str, Any]:
    """Return comprehensive version and environment metadata.
    
    Returns:
        Dict with server_version, protocol_version, governance_version,
        build metadata, and status information.
    """
    return {
        # Primary version - semantic versioning for server releases
        "server_version": "2.0.0",
        
        # MCP protocol compatibility
        "protocol_version": "2025-03-26",
        "supported_protocol_versions": ["2025-03-26", "2024-11-05"],
        
        # Governance layer versioning (separate from server)
        "governance_version": "registry-1.2.0",
        "policy_version": "arifOS.constitution.v1",
        "floors_version": "2026.04",
        "floors_active": 13,
        
        # Build traceability
        "build": {
            "commit": "ab774bf8",
            "commit_short": "ab774bf8",
            "built_at": datetime.now(timezone.utc).isoformat(),
            "branch": "main",
        },
        
        # Status
        "status": "FORGED",
        "forge_date": "2026-04-06",
        "forge_word": "FORGE",
        
        # Display helpers
        "display": {
            "short": "2.0.0",
            "full": "arifOS MCP 2.0.0",
            "with_build": "2.0.0+ab774bf8.20260406",
            "with_governance": "2.0.0 • Registry 1.2.0 • Policy v1",
        }
    }


def get_version_string(format: str = "short") -> str:
    """Get a formatted version string.
    
    Args:
        format: One of 'short', 'full', 'with_build', 'with_governance'
    
    Returns:
        Formatted version string
    """
    info = get_build_info()
    return info["display"].get(format, info["display"]["short"])
