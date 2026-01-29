"""
Async Compatibility Layer for Native ASI Kernel

Ensures async/await interface for MCP tools
"""

from typing import Dict, Any, Optional

from codebase.engines.asi.kernel_native import ASIKernelNative

class AsyncASIKernelNative(ASIKernelNative):
    """
    Async compatibility wrapper
    
    Extends the native kernel to provide async interface expected by MCP
    Since kernel_native already has async methods, we just pass through
    """
    
    # Methods are already async in parent class, so no wrapping needed
    # This class exists for interface compatibility and future extensions
    
    async def __aenter__(self):
        """Async context manager support"""
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        """Async context manager cleanup"""
        pass

# Export async version as the primary interface
ASIActionCore = AsyncASIKernelNative

__all__ = ["AsyncASIKernelNative", "ASIActionCore"]
