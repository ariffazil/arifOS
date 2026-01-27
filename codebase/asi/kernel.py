"""
ASI Kernel - Re-exports from codebase.engines.asi.kernel
Self-contained implementation for Railway deployment.
"""
from codebase.engines.asi.kernel import ASIActionCore, get_asi_core

# Alias for backward compatibility
ASIKernel = ASIActionCore

__all__ = ["ASIActionCore", "ASIKernel", "get_asi_core"]
