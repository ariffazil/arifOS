"""
codebase.init.000_init — Stage 000 VOID Components

System ignition and constitutional gate.

Canonical MCP init_000: codebase.init.000_init.init_000.mcp_000_init
Reference class:        codebase.init.000_init.stage_000_core.Stage000VOID
"""

from .stage_000_core import execute_stage_000, VerdictType, Stage000VOID
from .ignition import ignite_system
from .init_000 import mcp_000_init, InitResult

__all__ = [
    "execute_stage_000",
    "VerdictType",
    "Stage000VOID",
    "ignite_system",
    "mcp_000_init",
    "InitResult",
]
