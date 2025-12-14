"""
arifOS MCP Package - Model Context Protocol server for IDE integration.

This module provides MCP tools for integrating arifOS governance
with IDEs like VS Code, Cursor, and others.

Tools:
- arifos_judge: Run a query through the pipeline and return verdict
- arifos_recall: Recall memories from L7 (Mem0 + Qdrant)
- arifos_audit: Return ledger/audit data (stubbed for now)

Usage:
    from arifos_core.mcp import list_tools, arifos_judge, arifos_recall, arifos_audit

    # List available tools
    tools = list_tools()

    # Use tools directly
    from arifos_core.mcp.models import JudgeRequest
    result = arifos_judge(JudgeRequest(query="What is Amanah?"))

Version: v38.2-alpha
"""

from .server import list_tools, run_tool, TOOLS
from .tools.judge import arifos_judge
from .tools.recall import arifos_recall
from .tools.audit import arifos_audit
from .tools.apex_llama import apex_llama

__all__ = [
    "list_tools",
    "run_tool",
    "TOOLS",
    "arifos_judge",
    "arifos_recall",
    "arifos_audit",
    "apex_llama",
]
