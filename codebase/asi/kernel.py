"""
codebase.asi.kernel - Native ASI Kernel

Re-exports the native implementation for backward compatibility
"""

from typing import Dict, Any, Optional
import asyncio

from codebase.engines.asi.kernel_native import ASIKernelNative, ASIKernel, ASIActionCore

# Version markers for transparency
__native_version__ = "53.0.0"
__proxy_mode__ = False
__delegates_to__ = None  # No delegation - pure native

# Re-export
__all__ = ["ASIKernelNative", "ASIKernel", "ASIActionCore"]
