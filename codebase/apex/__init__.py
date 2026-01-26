"""
codebase APEX (Soul/Ψ) Module
v52 Constitutional AI Core

Re-exports APEX components for codebase.
The main implementation is in codebase.apex.kernel.APEXJudicialCore
"""

# v52 canonical kernel
from codebase.apex.kernel import APEXJudicialCore

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
