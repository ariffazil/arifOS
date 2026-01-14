"""
arifos_core.runtime - Constitutional Runtime Pipeline (000→999)

Complete 10-stage runtime pipeline implementing Track B specs:
L2_PROTOCOLS/v46/[stage]/

Pipeline Flow:
000 VOID → 111 SENSE → 222 REFLECT → 333 REASON → 333 CONTRAST → 333 INTEGRATION
→ 444 ALIGN → 555 EMPATHIZE → 666 BRIDGE → 777 EUREKA → 888 WITNESS → 999 SEAL

Each stage:
- Takes previous stage's bundle as IMMUTABLE input (F8 lineage)
- Applies constitutional floors (AGI/ASI/APEX)
- Generates new bundle with pass-through + new data
- Raises ValueError on VOID/SABAR verdicts

Authority:
- Track A (Canon): L1_THEORY/canon/[stage]/
- Track B (Spec): L2_PROTOCOLS/v46/[stage]/
- Track C (Code): arifos_core/runtime/[stage].py
"""

# Stage 111: SENSE - Input measurement and classification
from .sense_111 import (
    sense_stage,
    SensedBundle111,
    DomainType,
    LaneType,
    measure_shannon_entropy,
    detect_subtext_urgency,
    classify_domain,
    classify_lane,
)

# Stage 222: REFLECT - Path evaluation and bearing selection
from .reflect_222 import (
    reflect_stage,
    ReflectedBundle222,
    PathType,
    PathDraft,
    BearingSelection,
    TACAnalysis,
    generate_constitutional_paths,
    select_constitutional_bearing,
)

# Stage 333: REASON - AGI commitment under bearing lock
from .reason_333 import (
    reason_stage,
    ReasonedBundle333,
    VerdictType,
    validate_bearing_lock,
)

# Stage 333: CONTRAST - Multi-agent TAC validation (optional)
from .contrast_333 import (
    contrast_stage,
    ContrastBundle,
    ContrastType,
    ContrastMode,
    AgentName,
    AgentContribution,
    compute_tac_score,
    detect_jailbreak,
)

# Stage 333: INTEGRATION - Tri-axis AND logic
from .integration_333 import (
    integration_stage,
    IntegrationBundle,
    IntegratedVerdict,
    FloorVerdict,
    evaluate_floors,
    apply_cascade_rules,
)

# Stage 444: ALIGN - Thermodynamic heat sink (SABAR Protocol)
from .align_444 import (
    align_stage,
    AlignedBundle444,
    CognitiveHeatMetrics,
    SafetyTaxMetrics,
    AlignmentVerdict,
    CoolingStrategy,
    measure_cognitive_heat,
    apply_sabar_protocol,
    verify_thermodynamic_cooling,
)

# Stage 555: EMPATHIZE - ASI empathy calibration
from .empathy_555 import (
    empathy_stage,
    EmpathyBundle555,
    ASIFloorScores,
    EmpathyVerdict,
    compute_asi_scores,
    check_weakest_stakeholder,
)

# Stage 666: BRIDGE - Neuro-symbolic synthesis (Delta + Omega)
from .bridge_666 import (
    bridge_stage,
    BridgeBundle666,
    MoEWeights,
    HumilityMetrics,
    ConflictResolution,
    SynthesisVerdict,
    ConflictType,
    ContextGate,
    measure_humility,
    determine_context_gate,
    compute_moe_weights,
    synthesize_dual_process,
)

# Stage 777: EUREKA - Insight crystallization (F7 RASA + ScarPacket)
from .eureka_777 import (
    eureka_stage,
    EurekaBundle777,
    RASAMetrics,
    ScarPacket,
    ConstitutionalPrecheck,
    EurekaVerdict,
    ScarType,
    measure_rasa_compliance,
    generate_scar_packet,
    precheck_constitutional_compliance,
    crystallize_insight,
)

# Stage 888: WITNESS - APEX final judgment
from .witness_888 import (
    witness_stage,
    WitnessBundle888,
    HypervisorStatus,
    TriKernelEvaluation,
    WitnessVerdict,
    compute_genius_score,
    render_final_verdict,
)

# Stage 999: SEAL - Cooling ledger integration
from .seal_999 import (
    seal_stage,
    SealBundle999,
    CoolingReceipt,
    RetentionBand,
    SealStatus,
    route_verdict_to_band,
    synthesize_sealed_response,
)


__all__ = [
    # Stage 111 SENSE
    "sense_stage",
    "SensedBundle111",
    "DomainType",
    "LaneType",
    "measure_shannon_entropy",
    "detect_subtext_urgency",
    "classify_domain",
    "classify_lane",
    # Stage 222 REFLECT
    "reflect_stage",
    "ReflectedBundle222",
    "PathType",
    "PathDraft",
    "BearingSelection",
    "TACAnalysis",
    "generate_constitutional_paths",
    "select_constitutional_bearing",
    # Stage 333 REASON
    "reason_stage",
    "ReasonedBundle333",
    "VerdictType",
    "validate_bearing_lock",
    # Stage 333 CONTRAST
    "contrast_stage",
    "ContrastBundle",
    "ContrastType",
    "ContrastMode",
    "AgentName",
    "AgentContribution",
    "compute_tac_score",
    "detect_jailbreak",
    # Stage 333 INTEGRATION
    "integration_stage",
    "IntegrationBundle",
    "IntegratedVerdict",
    "FloorVerdict",
    "evaluate_floors",
    "apply_cascade_rules",
    # Stage 444 ALIGN
    "align_stage",
    "AlignedBundle444",
    "CognitiveHeatMetrics",
    "SafetyTaxMetrics",
    "AlignmentVerdict",
    "CoolingStrategy",
    "measure_cognitive_heat",
    "apply_sabar_protocol",
    "verify_thermodynamic_cooling",
    # Stage 555 EMPATHIZE
    "empathy_stage",
    "EmpathyBundle555",
    "ASIFloorScores",
    "EmpathyVerdict",
    "compute_asi_scores",
    "check_weakest_stakeholder",
    # Stage 666 BRIDGE
    "bridge_stage",
    "BridgeBundle666",
    "MoEWeights",
    "HumilityMetrics",
    "ConflictResolution",
    "SynthesisVerdict",
    "ConflictType",
    "ContextGate",
    "measure_humility",
    "determine_context_gate",
    "compute_moe_weights",
    "synthesize_dual_process",
    # Stage 777 EUREKA
    "eureka_stage",
    "EurekaBundle777",
    "RASAMetrics",
    "ScarPacket",
    "ConstitutionalPrecheck",
    "EurekaVerdict",
    "ScarType",
    "measure_rasa_compliance",
    "generate_scar_packet",
    "precheck_constitutional_compliance",
    "crystallize_insight",
    # Stage 888 WITNESS
    "witness_stage",
    "WitnessBundle888",
    "HypervisorStatus",
    "TriKernelEvaluation",
    "WitnessVerdict",
    "compute_genius_score",
    "render_final_verdict",
    # Stage 999 SEAL
    "seal_stage",
    "SealBundle999",
    "CoolingReceipt",
    "RetentionBand",
    "SealStatus",
    "route_verdict_to_band",
    "synthesize_sealed_response",
]
