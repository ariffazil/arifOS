"""
codebase.asi — ASI (Heart) Engine Package

Native implementation of the ASI (Ω) constitutional engine

Architecture: v53 Native (no proxy to arifos/core)
Execution Model: Async wrapper over sync ASIRoom
"""

__version__ = "53.0.0-NATIVE"
__migrated__ = True
__proxy_mode__ = False
__execution_model__ = "async_wrapper"

# Export async-wrapped native kernel for MCP compatibility
from .async_wrapper import ASIActionCore, AsyncASIKernelNative

__all__ = ["ASIActionCore", "AsyncASIKernelNative"]

# Migration metadata
MIGRATION_STATUS = {
    "phase": "native_v53",
    "proxy_removed": True,
    "native_implementation": True,
    "architecture": "codebase_native",
    "constitutional_physics_location": "codebase/engines/asi/"
}
