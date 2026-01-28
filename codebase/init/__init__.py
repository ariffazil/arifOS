"""
codebase.init — Initialization Package

Stage 000 VOID: System Ignition and Constitutional Gate

Canonical MCP init: codebase.init.mcp_000_init
"""

import importlib as _importlib

# Python can't do `from .000_init import ...` because 000 is parsed as a
# decimal literal. Use importlib to work around the numeric directory name.
_stage = _importlib.import_module("codebase.init.000_init")

execute_stage_000 = _stage.execute_stage_000
VerdictType = _stage.VerdictType
Stage000VOID = _stage.Stage000VOID
ignite_system = _stage.ignite_system
mcp_000_init = _stage.mcp_000_init
InitResult = _stage.InitResult

__all__ = [
    "execute_stage_000",
    "VerdictType",
    "Stage000VOID",
    "ignite_system",
    "mcp_000_init",
    "InitResult",
]
