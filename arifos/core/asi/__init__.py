"""
arifOS ASI (Heart/Ω) Module
v51 Core Reorganization

Re-exports ASI components for compatibility.
The main implementation is in arifos.core.asi.kernel.ASIActionCore
"""

# New v51 kernel
from arifos.core.asi.kernel import ASIActionCore

# Alias for backward compatibility
ASIKernel = ASIActionCore

# Cooling engine (used by apex_prime)
try:
    from arifos.core.asi.cooling import CoolingEngine
except ImportError:
    CoolingEngine = None

__all__ = [
    # v51 Kernel
    "ASIActionCore",
    "ASIKernel",
    # Cooling
    "CoolingEngine",
]
