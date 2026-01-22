"""
arifOS Constitutional Engines (v50.5.23)

The Three Engines of Intelligence:
    AGI (Δ) — Mind: SENSE → THINK → ATLAS → FORGE
    ASI (Ω) — Heart: EVIDENCE → EMPATHY → ALIGN → ACT
    APEX (Ψ) — Soul: EUREKA → JUDGE → PROOF

Metabolic Pipeline (111-888):
    000 INIT     → Gate (Ignition + Authority)
    111 SENSE    → AGI Δ
    222 REFLECT  → AGI Δ
    333 REASON   → AGI Δ
    444 EVIDENCE → ASI Ω
    555 EMPATHIZE → ASI Ω
    666 ALIGN    → ASI Ω
    777 FORGE    → EUREKA (AGI + ASI → APEX)
    888 JUDGE    → APEX Ψ
    889 PROOF    → APEX Ψ
    999 SEAL     → Vault

Tool Links (via MCP):
    AGI: mcp://search, mcp://code, mcp://memory, mcp://docs
    ASI: mcp://email, mcp://desktop, mcp://api, mcp://notify
    APEX: mcp://vault, mcp://audit, mcp://proof

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

# Paradox detection (legacy)
from arifos.core.engines.paradox import ParadoxDetector, ParadoxMetrics, ScarPacket

# AGI Engine (Mind/Δ)
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

# ASI Engine (Heart/Ω)
from arifos.core.engines.asi_engine import (
    ASIEngine,
    ASIOutput,
    Stakeholder,
    StakeholderMap,
    EvidenceResult,
    EmpathyResult,
    AlignResult,
    ActResult,
)

# APEX Engine (Soul/Ψ)
from arifos.core.engines.apex_engine import (
    APEXEngine,
    APEXOutput,
    VoidJustification,
    ProofPacket,
    EurekaResult,
    JudgeResult,
    ProofResult,
)

__all__ = [
    # Legacy paradox
    "ParadoxDetector",
    "ParadoxMetrics",
    "ScarPacket",
    # AGI (Mind/Δ)
    "AGIEngine",
    "AGIOutput",
    "Lane",
    "GovernancePlacementVector",
    "SenseResult",
    "ThinkResult",
    "AtlasResult",
    "ForgeResult",
    # ASI (Heart/Ω)
    "ASIEngine",
    "ASIOutput",
    "Stakeholder",
    "StakeholderMap",
    "EvidenceResult",
    "EmpathyResult",
    "AlignResult",
    "ActResult",
    # APEX (Soul/Ψ)
    "APEXEngine",
    "APEXOutput",
    "VoidJustification",
    "ProofPacket",
    "EurekaResult",
    "JudgeResult",
    "ProofResult",
]
