"""
Smoke test for arifos_mcp.

Ensures server can be instantiated and imports are valid.
"""

import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent.absolute()
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

def test_mcp_package_import():
    """Ensure we can import the server and its local dependencies."""
    from arifos_mcp.server import (attestation_registry, mcp, recovery_matrix,
                                   witness_system)

    assert mcp.name == "arifOS_AAA_MCP"
    assert attestation_registry is not None
    assert recovery_matrix is not None
    assert witness_system is not None

def test_mcp_tools_registration():
    """Check if all AAA tools are registered."""
    import asyncio

    from arifos_mcp.server import mcp

    tools = asyncio.run(mcp.get_tools())
    tool_names = [t.name if hasattr(t, "name") else str(t) for t in tools]
    expected_tools = [
        "vtempa_reflection",
        "vtempa_action",
        "vtempa_execution",
        "vtempa_self_correction",
        "vtempa_memory",
        "get_aaa_manifest",
        "check_vitality",
        "witness_vote"
    ]

    for tool in expected_tools:
        assert tool in tool_names
