"""
canonical_core APEX (Soul/Ψ) Module
v52 Canonical Core

Re-exports APEX components for canonical_core.
The main implementation is in canonical_core.apex.kernel.APEXJudicialCore
"""

# v52 canonical kernel
from canonical_core.apex.kernel import APEXJudicialCore

# Alias for backward compatibility
APEXKernel = APEXJudicialCore

# Legacy engine (for backward compatibility)
try:
    from arifos.core.engines.apex_engine import (
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
