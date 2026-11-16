"""arifOS evidence — envelopes, LawEvidence compiler, store, validator."""

from arifosmcp.evidence.emitters import (
    emit_aforge,
    emit_geox,
    emit_wealth,
    emit_well,
)
from arifosmcp.evidence.law_evidence import (
    FloorResult,
    FloorStatus,
    JudgeVerdict,
    LawEvidence,
    SessionState,
    VaultLineage,
    WellState,
    compile_law_evidence,
    recommend_verdict,
)
from arifosmcp.evidence.pipeline import PipelineResult, run_pipeline
from arifosmcp.schemas.envelope import (
    ActorContext,
    ContradictionEntry,
    EpistemicTag,
    EvidenceEnvelope,
    Lineage,
    Reversibility,
    SourceAttribution,
    UncertaintyBand,
    wrap_envelope,
)

__all__ = [
    "ActorContext",
    "ContradictionEntry",
    "EpistemicTag",
    "EvidenceEnvelope",
    "FloorResult",
    "FloorStatus",
    "JudgeVerdict",
    "LawEvidence",
    "Lineage",
    "PipelineResult",
    "Reversibility",
    "SessionState",
    "SourceAttribution",
    "UncertaintyBand",
    "VaultLineage",
    "WellState",
    "compile_law_evidence",
    "emit_aforge",
    "emit_geox",
    "emit_wealth",
    "emit_well",
    "recommend_verdict",
    "run_pipeline",
    "wrap_envelope",
]
