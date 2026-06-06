"""
arifOS Canonical Output Schemas (v2026.04.26-KANON)
═══════════════════════════════════════════════════

Phase 2 Civilization Intelligence:
- 888_JUDGE: VerdictOutput with ToAC, ThermodynamicState,
  DecisionCollapse, GrowthParadox, AKAL, AmanahProof
- 999_VAULT: SealOutput with IrreversibilityBond, EntropyDelta,
  EpistemicSnapshot
- 333_MIND: MindOutput with AxiomsUsed, Metrics, ReasoningTrace
- 222_FETCH: Sequential thinking schemas
- 010_FORGE: ForgeOutput with IrreversibilityFlag, DeltaSEvidence
- 444_KERNEL: KernelMetrics with stage trajectory
- 777_OPS: WEALTH metrics with Landauer, psi_le, omega
- 114_INGEST: CanonicalEvidenceBundle + IngestResult + ClaimSchema
  (Phase 1 SENSE-INGEST pipeline)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

# Sequential thinking (222_SENSE)
from arifosmcp.schemas.cognition import (
    EpistemicHumility,
    EvidenceCivilizationContext,
    EvidenceOutput,
    RealityAnchor,
    ReasoningQuality,
    ResourceMetrics,
    ThinkingMode,
    ThinkingOutcome,
    ThinkingSequence,
    ThinkingStep,
    UncertaintyGeometry,
)

# Forge (010_FORGE)
from arifosmcp.schemas.forge import (
    ConstitutionalCompliance,
    DeltaSEvidence,
    ExecutionNode,
    ExecutionTrace,
    ForgeEnvelope,
    ForgeManifest,
    ForgeOutput,
    IrreversibilityBond,
    IrreversibilityLevel,
    ManifestStatus,
)

# Gateway (666g_GATEWAY)
from arifosmcp.schemas.gateway import GatewayBlock

# Intent Envelope v1 — Atomic authorization object (F1/F11/F13 enforcement)
# Ratified 2026-06-06. Kernel rule: "AI may generate. Humans must authorize consequence."
from arifosmcp.schemas.intent_envelope import (
    DisplayCard,
    IntentEnvelopeV1,
    ProvenanceClass,
    Reversibility,
    RiskClass,
    SovereignProvenance,
)

# Verdict (888_JUDGE, 999_VAULT, 666_HEART)
from arifosmcp.schemas.lineage import JudgeSealContract

# Memory (555_MEMORY)
from arifosmcp.schemas.memory import MemoryBlock

# ModelCard (F3 TRI_WITNESS — identity binding)
from arifosmcp.schemas.model_card import (
    ModelAnchor,
    ModelGovernanceCard,
    RiskLeash,
    RuntimeTruth,
    SelfClaimBoundary,
    ShadowProfile,
)

# Session (000_INIT)
from arifosmcp.schemas.session import SessionManifest, SessionState

# Synthesis (333_MIND, 444r_REPLY, 222_FETCH)
from arifosmcp.schemas.synthesis import (
    AxiomSource,
    AxiomsUsed,
    AxiomUsage,
    ContrastType,
    EvidenceBlock,
    MindAnomalousContrast,
    # 333_MIND MindOutput schemas
    MindOutput,
    ReasoningMode,
    ReasoningStep,
    ReasoningTrace,
    ReplyBlock,
    Synthesis,
)

# Telemetry (777_OPS, 111_SENSE)
from arifosmcp.schemas.telemetry import TelemetryBlock, VitalsBlock

# Topology (777_OPS — Anti-Sink / Inclusive Topology diagnostics)
from arifosmcp.schemas.topology import (
    AntiSinkCheck,
    AppealPath,
    Confidence,
    Delta,
    InnovationRights,
    InstitutionalDrift,
    InstitutionalVerdict,
    ParticipationWidth,
    Presence,
    RiskBand,
    SovereigntyIntegrity,
    Strength,
)
from arifosmcp.schemas.topology import (
    Verdict as TopologyVerdict,
)
from arifosmcp.schemas.verdict import (
    AkalState,
    AmanahProof,
    # 888_JUDGE civilization schemas
    AnomalousContrast,
    CivilizationalAnchor,
    CritiqueReport,
    DecisionCollapse,
    DissentReasoning,
    EntropyDelta,
    EpistemicSnapshot,
    FloorComplianceProof,
    GrowthParadox,
    # 999_VAULT seal schemas
    SealOutput,
    SealReceipt,
    ThermodynamicState,
    Verdict,
    VerdictCode,
    VerdictOutput,
    VerdictReport,
)

__all__ = [
    # Topology (777_OPS — Anti-Sink / Inclusive Topology diagnostics)
    "AntiSinkCheck",
    "InstitutionalDrift",
    "TopologyVerdict",
    "Delta",
    "Strength",
    "RiskBand",
    "Confidence",
    "Presence",
    "ParticipationWidth",
    "InnovationRights",
    "AppealPath",
    "SovereigntyIntegrity",
    "InstitutionalVerdict",
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
    "ForgeEnvelope",
    "ForgeOutput",
    "ExecutionNode",
    "ExecutionTrace",
    "ConstitutionalCompliance",
    "DeltaSEvidence",
    "IrreversibilityBond",
    "IrreversibilityLevel",
    "ManifestStatus",
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
    # Intent Envelope v1 (F1/F11/F13 atomic authorization)
    "DisplayCard",
    "IntentEnvelopeV1",
    "ProvenanceClass",
    "Reversibility",
    "RiskClass",
    "SovereignProvenance",
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
    # EvidenceBundle (111_SENSE → 114_INGEST pipeline)
    "CanonicalEvidenceBundle",
    "IngestResult",
    "ClaimSchema",
    "EntitySchema",
    "RelationSchema",
    "ReceiptSchema",
    "EvidenceLevel",
    "IngestStatus",
    # ModelCard (F3 TRI_WITNESS — identity binding)
    "ModelGovernanceCard",
    "ModelAnchor",
    "RuntimeTruth",
    "SelfClaimBoundary",
    "ShadowProfile",
    "RiskLeash",
]
