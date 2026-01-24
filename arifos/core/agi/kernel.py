"""
arifOS AGI Kernel Shim
v51 - Re-exports from arifos.core.engines.agi.kernel
"""
from arifos.core.engines.agi.kernel import (
    AGINeuralCore,
    AGIVerdict,
)

# Alias for backward compatibility
AGIKernel = AGINeuralCore

__all__ = ["AGINeuralCore", "AGIKernel", "AGIVerdict"]
