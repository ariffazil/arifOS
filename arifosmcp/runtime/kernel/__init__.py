"""
arifOS Kernel — Constitutional Judgment Engine

Physics computes. Kernel governs. Agent acts. Receipt remembers. Sovereign decides.

Wording law (2026-07-09):
  Python kernel = constitutional judgment engine (CollapseResult / SEAL-path / HOLD / VOID / SABAR).
  It does NOT replace sovereign veto. Arif / F13 remains supreme.

Architecture:
  Python kernel  = constitutional judgment engine — ΔΩΨ, 000-999, 6 tripwires, collapse
  TypeScript     = executor   — A-FORGE hands (forge_* tools), never reimplements verdicts
  Quantum        = calculator — evidence organ / contract only; never kernel, never judge, never hands
  VAULT999       = memory     — immutable seal chain (only true SEAL)
  AAA            = cockpit    — state display, intent routing
  Arif / F13     = sovereign  — final veto above all code

This module implements the formal judgment engine ONLY:
  - Δ (entropy/pressure), Ω (uncertainty), Ψ (integrity)
  - 000-999 metabolic pipeline
  - 6 tripwires at 888
  - Source-weighted evidence fusion
  - SealRecord / SealChain helpers (library; live VAULT999 is the civilizational seal)
  - Governance contracts for external compute (quantum, etc.)

Local tests prove behavior under fixtures — they are NOT a constitutional SEAL.
No domain physics. No solver code. No execution logic.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from .compute import (
    compute_delta,
    compute_omega,
    compute_psi,
    compute_scalars,
    compute_source_consensus,
)

# ── Governance Contracts (not execution) ──
from .contracts import (
    QUANTUM_ADAPTER_CONTRACT,
    BackendClass,
    EvidenceRank,
    QuantumComputeReceipt,
    QuantumEvidenceFloor,
    QuantumReversibility,
    validate_receipt,
)
from .judge import judge, judge_with_reason
from .pipeline import (
    PhaseTransitionError,
    PipelineResult,
    cool,
    critique,
    ingest_evidence,
    ingest_intent,
    pipeline_seal,
    prepare_action,
    run_judge,
    run_pipeline,
    think,
    validate_transition,
)
from .seal import (
    SealChain,
    SealRecord,
    append_to_chain,
    empty_chain,
    seal,
    verify_chain,
)
from .types import (
    BLAST_WEIGHTS,
    DELTA_CRITICAL,
    OMEGA_HARD_LIMIT,
    OMEGA_MAX,
    OMEGA_WARN,
    PHASE_LABELS,
    PHASE_ORDER,
    PHASES,
    PSI_MIN,
    SOURCE_WEIGHTS,
    BlastRadius,
    CollapseResult,
    EvidenceFusion,
    EvidenceItem,
    GovernanceScalars,
    GovernanceState,
    Organ,
    Phase,
    RiskProfile,
    SourceConsensus,
    TripwireId,
    TripwireResult,
    UncertaintyTag,
    Verdict,
)

__all__ = [
    # Types
    "UncertaintyTag",
    "Verdict",
    "Phase",
    "EvidenceItem",
    "SourceConsensus",
    "GovernanceScalars",
    "CollapseResult",
    "EvidenceFusion",
    "TripwireResult",
    "TripwireId",
    "GovernanceState",
    "Organ",
    "BlastRadius",
    "RiskProfile",
    # Constants
    "OMEGA_MAX",
    "PSI_MIN",
    "DELTA_CRITICAL",
    "OMEGA_WARN",
    "OMEGA_HARD_LIMIT",
    "PHASES",
    "PHASE_LABELS",
    "PHASE_ORDER",
    "SOURCE_WEIGHTS",
    "BLAST_WEIGHTS",
    # Compute
    "compute_delta",
    "compute_omega",
    "compute_psi",
    "compute_source_consensus",
    "compute_scalars",
    # Judge
    "judge",
    "judge_with_reason",
    # Pipeline
    "ingest_intent",
    "ingest_evidence",
    "think",
    "critique",
    "prepare_action",
    "run_judge",
    "cool",
    "pipeline_seal",
    "run_pipeline",
    "validate_transition",
    "PhaseTransitionError",
    "PipelineResult",
    # Seal
    "SealRecord",
    "SealChain",
    "seal",
    "empty_chain",
    "append_to_chain",
    "verify_chain",
    # Governance Contracts
    "QuantumComputeReceipt",
    "QuantumEvidenceFloor",
    "QuantumReversibility",
    "QUANTUM_ADAPTER_CONTRACT",
    "validate_receipt",
    "BackendClass",
    "EvidenceRank",
]
