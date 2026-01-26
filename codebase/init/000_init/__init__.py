"""
codebase.init.000_init — Stage 000 VOID Components

System ignition and constitutional gate.
"""

from .stage_000_core import execute_stage_000, VerdictType, Stage000VOID
from .ignition import ignite_system

__all__ = [
    "execute_stage_000",
    "VerdictType",
    "Stage000VOID", 
    "ignite_system"
]
