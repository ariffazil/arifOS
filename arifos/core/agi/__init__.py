"""
arifOS AGI (Mind/Δ) Module
v51 Core Reorganization

Re-exports AGI components for compatibility.
The main implementation is in arifos.core.engines.agi.kernel.AGINeuralCore
"""

# New v51 kernel (from engines subdirectory)
from arifos.core.engines.agi.kernel import AGINeuralCore, AGIVerdict

# Alias for backward compatibility
AGIKernel = AGINeuralCore

# Legacy engine (for backward compatibility)
try:
    from arifos.core.engines.agi_engine import (
        AGIEngine,
        AGIOutput,
        Lane,
        GovernancePlacementVector,
        SenseResult,
        ThinkResult,
        AtlasResult,
        ForgeResult,
    )
except ImportError:
    AGIEngine = None
    AGIOutput = None
    Lane = None
    GovernancePlacementVector = None
    SenseResult = None
    ThinkResult = None
    AtlasResult = None
    ForgeResult = None

# ATLAS routing system
try:
    from arifos.core.engines.agi.atlas import ATLAS
except ImportError:
    ATLAS = None

__all__ = [
    # v51 Kernel
    "AGINeuralCore",
    "AGIKernel",
    "AGIVerdict",
    # ATLAS
    "ATLAS",
    # Legacy Engine
    "AGIEngine",
    "AGIOutput",
    "Lane",
    "GovernancePlacementVector",
    "SenseResult",
    "ThinkResult",
    "AtlasResult",
    "ForgeResult",
]
