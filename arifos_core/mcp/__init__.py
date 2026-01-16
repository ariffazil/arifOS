"""
arifOS MCP Package - Model Context Protocol server for IDE integration.

This module provides MCP tools for integrating arifOS governance
with IDEs like VS Code, Cursor, and others.

Unified Server (v46.3):
- 17 tools consolidated from 34 (across 3 old servers)
- 5 constitutional pipeline + 2 search + 3 vault999 + 4 FAG + 1 validation + 2 system
- Dual semantic search (agi_search, asi_search)
- All 12 constitutional floors enforced

Usage:
    from arifos_core.mcp import list_tools, arifos_judge, arifos_recall, arifos_audit

    # List available tools
    tools = list_tools()

    # Use tools directly
    from arifos_core.mcp.models import JudgeRequest
    result = arifos_judge(JudgeRequest(query="What is Amanah?"))

Version: v46.3
"""

from .unified_server import list_tools, run_tool, TOOLS, mcp_server
from .tools.judge import arifos_judge
from .tools.recall import arifos_recall
from .tools.audit import arifos_audit

__all__ = [
    "list_tools",
    "run_tool",
    "TOOLS",
    "mcp_server",
    "arifos_judge",
    "arifos_recall",
    "arifos_audit",
]
