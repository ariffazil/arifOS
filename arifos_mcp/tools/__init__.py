"""
arifOS Tools Package
====================

Canonical tool implementations following the Tool base class pattern.

Usage:
    from arifos_mcp.tools import init_anchor_tool, arifOS_kernel_tool

    tool = init_anchor_tool()
    result = await tool.run(payload={"actor_id": "test"})
"""

from arifos_mcp.tools.base import Tool, ToolRegistry, FloorResult

# Governance tools
from arifos_mcp.tools.governance import (
    init_anchor_tool,
    arifOS_kernel_tool,
    apex_judge_tool,
    vault_ledger_tool,
)

# Intelligence tools
from arifos_mcp.tools.intelligence import (
    agi_mind_tool,
    asi_heart_tool,
    engineering_memory_tool,
)

# Reality tools
from arifos_mcp.tools.reality import (
    physics_reality_tool,
    math_estimator_tool,
)

# Execution tools
from arifos_mcp.tools.execution import (
    code_engine_tool,
    architect_registry_tool,
)

__all__ = [
    # Base
    "Tool",
    "ToolRegistry",
    "FloorResult",
    # Governance
    "init_anchor_tool",
    "arifOS_kernel_tool",
    "apex_judge_tool",
    "vault_ledger_tool",
    # Intelligence
    "agi_mind_tool",
    "asi_heart_tool",
    "engineering_memory_tool",
    # Reality
    "physics_reality_tool",
    "math_estimator_tool",
    # Execution
    "code_engine_tool",
    "architect_registry_tool",
]
