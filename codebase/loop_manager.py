"""
codebase/loop_manager.py — DEPRECATED Legacy Compatibility Shim
v55.0 Migration Notice

This file is DEPRECATED and maintained only for backward compatibility.

LEGACY PATH (v52-v53):
    from codebase.loop_manager import LoopManager

NEW CANONICAL PATH (v55.0+):
    from codebase.loop import LoopManager, LoopBridge, LoopState

This shim forwards imports to the new module structure.
Will be removed in v56.0.

DITEMPA BUKAN DIBERI
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "codebase/loop_manager.py is deprecated. "
    "Use 'from codebase.loop import LoopManager' instead. "
    "This shim will be removed in v56.0.",
    DeprecationWarning,
    stacklevel=2,
)

# Forward imports to new canonical location
from codebase.loop.manager import (
    LoopManager,
    LoopBridge,
    LoopState,
    LoopContext,
    StageResult,
    Verdict,
)

# Legacy singleton for backward compatibility
loop_manager = LoopManager()

__all__ = [
    "LoopManager",
    "LoopBridge",
    "LoopState",
    "LoopContext",
    "StageResult",
    "Verdict",
    "loop_manager",  # Singleton
]
