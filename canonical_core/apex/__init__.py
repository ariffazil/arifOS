"""
arifOS APEX (Soul/Ψ) Module
v51 Core Reorganization

Re-exports APEX components for compatibility.
The main implementation is in arifos.core.apex.kernel.APEXJudicialCore
"""

# New v51 kernel
from canonical_core.apex.kernel import APEXJudicialCore

# Alias for backward compatibility
APEXKernel = APEXJudicialCore

# Legacy engine (for backward compatibility)
try:
    from canonical_core.engines.apex_engine import (
        APEXEngine,
        APEXOutput,
        VoidJustification,
        ProofPacket,
        EurekaResult,
        JudgeResult,
        ProofResult,
    )
except ImportError:
    APEXEngine = None
    APEXOutput = None
    VoidJustification = None
    ProofPacket = None
    EurekaResult = None
    JudgeResult = None
    ProofResult = None

__all__ = [
    # v51 Kernel
    "APEXJudicialCore",
    "APEXKernel",
    # Legacy Engine
    "APEXEngine",
    "APEXOutput",
    "VoidJustification",
    "ProofPacket",
    "EurekaResult",
    "JudgeResult",
    "ProofResult",
]
