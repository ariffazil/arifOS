"""
arifOS Canonical Output Schemas (v2026.04.24-KANON)
════════════════════════════════════════════════════

Phase 2 Civilization Intelligence:
- 888_JUDGE: VerdictOutput with ToAC, ThermodynamicState, DecisionCollapse, GrowthParadox, AKAL, AmanahProof
- 999_VAULT: SealOutput with IrreversibilityBond, EntropyDelta, EpistemicSnapshot
- 333_MIND: MindOutput with AxiomsUsed, Metrics, ReasoningTrace
- 222_FETCH: Sequential thinking schemas
- 010_FORGE: ForgeOutput with IrreversibilityFlag, DeltaSEvidence
- 444_KERNEL: KernelMetrics with stage trajectory
- 777_OPS: WEALTH metrics with Landauer, psi_le, omega

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

# Session (000_INIT)
from arifosmcp.schemas.session import SessionManifest, SessionState

# Verdict (888_JUDGE, 999_VAULT, 666_HEART)
from arifosmcp.schemas.lineage import JudgeSealContract
from arifosmcp.schemas.verdict import (
    Verdict, VerdictCode, VerdictReport, CritiqueReport, SealReceipt,
    # 888_JUDGE civilization schemas
    AnomalousContrast,
    ThermodynamicState,
    DecisionCollapse,
    GrowthParadox,
    AkalState,
    AmanahProof,
    FloorComplianceProof,
    DissentReasoning,
    CivilizationalAnchor,
    VerdictOutput,
    # 999_VAULT seal schemas
    SealOutput,
    EntropyDelta,
    EpistemicSnapshot,
)

# Telemetry (777_OPS, 111_SENSE)
from arifosmcp.schemas.telemetry import TelemetryBlock, VitalsBlock

# Forge (010_FORGE)
from arifosmcp.schemas.forge import (
    ForgeManifest,
    ForgeOutput,
    IrreversibilityBond,
    DeltaSEvidence,
    ExecutionTrace,
    ExecutionNode,
    ConstitutionalCompliance,
    IrreversibilityLevel,
    ManifestStatus,
    ForgeEnvelope,
)

# Synthesis (333_MIND, 444r_REPLY, 222_FETCH)
from arifosmcp.schemas.synthesis import (
    Synthesis,
    ReplyBlock,
    EvidenceBlock,
    # 333_MIND MindOutput schemas
    MindOutput,
    ReasoningMode,
    AxiomSource,
    ContrastType,
    AxiomUsage,
    AxiomsUsed,
    ReasoningStep,
    ReasoningTrace,
    MindAnomalousContrast,
)

# Memory (555_MEMORY)
from arifosmcp.schemas.memory import MemoryBlock

# Gateway (666g_GATEWAY)
from arifosmcp.schemas.gateway import GatewayBlock

# Sequential thinking (222_SENSE)
from arifosmcp.schemas.cognition import (
    ThinkingStep,
    ThinkingSequence,
    ThinkingMode,
    ThinkingOutcome,
    ReasoningQuality,
    ResourceMetrics,
    RealityAnchor,
    EvidenceOutput,
    UncertaintyGeometry,
    EvidenceCivilizationContext,
    EpistemicHumility,
)

__all__ = [
    # Session (000_INIT)
    "SessionManifest",
    "SessionState",

    # Verdict (888_JUDGE, 999_VAULT, 666_HEART)
    "Verdict",
    "VerdictCode",
    "VerdictReport",
    "CritiqueReport",
    "SealReceipt",
    "JudgeSealContract",
    # 888_JUDGE + 999_VAULT civilization intelligence
    "AnomalousContrast",
    "ThermodynamicState",
    "DecisionCollapse",
    "GrowthParadox",
    "AkalState",
    "AmanahProof",
    "FloorComplianceProof",
    "DissentReasoning",
    "CivilizationalAnchor",
    "VerdictOutput",
    "SealOutput",
    "EntropyDelta",
    "EpistemicSnapshot",

    # Telemetry (777_OPS, 111_SENSE)
    "TelemetryBlock",
    "VitalsBlock",

    # Forge (010_FORGE)
    "ForgeManifest",

    # Synthesis (333_MIND, 444r_REPLY, 222_FETCH)
    "Synthesis",
    "ReplyBlock",
    "EvidenceBlock",
    "MindOutput",
    "ReasoningMode",
    "AxiomSource",
    "ContrastType",
    "AxiomUsage",
    "AxiomsUsed",
    "ReasoningStep",
    "ReasoningTrace",
    "MindAnomalousContrast",

    # Memory (555_MEMORY)
    "MemoryBlock",

    # Gateway (666g_GATEWAY)
    "GatewayBlock",

    # Sequential thinking (222_SENSE)
    "ThinkingStep",
    "ThinkingSequence",
    "ThinkingMode",
    "ThinkingOutcome",
    "ReasoningQuality",
    "ResourceMetrics",
    "RealityAnchor",
    "EvidenceOutput",
    "UncertaintyGeometry",
    "EvidenceCivilizationContext",
    "EpistemicHumility",
]
