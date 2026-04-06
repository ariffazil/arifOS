"""
arifOS Tools Package
====================

Canonical tool implementations following the Tool base class pattern.

Usage:
    from arifosmcp.tools import init_anchor_tool, arifOS_kernel_tool

    tool = init_anchor_tool()
    result = await tool.run(payload={"actor_id": "test"})
"""

from arifosmcp.tools.base import Tool, ToolRegistry, FloorResult

# Governance tools
from arifosmcp.tools.governance import (
    init_anchor_tool,
    arifOS_kernel_tool,
    apex_judge_tool,
    vault_ledger_tool,
)

# Intelligence tools
from arifosmcp.tools.intelligence import (
    agi_mind_tool,
    asi_heart_tool,
    engineering_memory_tool,
)

# Reality tools
from arifosmcp.tools.reality import (
    physics_reality_tool,
    math_estimator_tool,
)

# Execution tools
from arifosmcp.tools.execution import (
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
