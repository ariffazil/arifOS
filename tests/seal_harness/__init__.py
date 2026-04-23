"""
arifOS AAA MCP SEAL Test Harness v0

A minimal, repeatable test harness for constitutional AI governance validation.

Usage:
    python -m tests.seal_harness \
        --endpoint https://arifosmcp.arif-fazil.com/mcp \
        --out aaa-seal-report.json
"""

__version__ = "2026.3.1"
__all__ = ["MCPClient", "TrinityTestHarness", "SchemaValidator", "run_seal_check"]
