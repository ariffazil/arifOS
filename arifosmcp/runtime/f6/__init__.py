"""F6 / MARUAH v0 — kernel controls over how the system treats humans.

NOT a measure of human dignity. Measures SYSTEM BEHAVIOR only.
"LULUS tidak bermakna" (PASS does not imply) applies to every meter:
a pass on any meter never proves a human understood, consented, or
was treated well — it only proves a control held on the paths examined.

Four axes, never flattened:
  measurement : MEASURED | UNMEASURED | STALE | ERROR
  result      : PASS | FAIL | UNKNOWN | NOT_APPLICABLE
  witness     : REVIEWED | UNWITNESSED | STALE
  authority   : separate action-approval decision (never derived from meters)

Ruling binding this module: /root/AAA/instructions/f6-dignity-boundary-ruling.md
"""

from arifosmcp.runtime.f6.authority_binding import (
    ActionRequest,
    AuthorityBinding,
    BindingStore,
    BindingVerdict,
    SQLiteRevocationStore,
    check_binding,
    execute_bound,
)
from arifosmcp.runtime.f6.consent_scope import (
    ConsentDecision,
    ConsentScope,
    ConsentSource,
    check_consent,
)
from arifosmcp.runtime.f6.correction_effect import (
    CorrectionRecord,
    CorrectionStatus,
    apply_correction,
    challenge_record,
    load_corrections,
    propagate_correction_across_layers,
    record_correction,
    resolve_dissent_at_decision_gate,
    supersede,
    verify_effect,
)
from arifosmcp.runtime.f6.meters import (
    Axis,
    MeterAssessment,
    evaluate_all,
    evaluate_comprehension_ceremony,
    evaluate_manipulation_detector,
    evaluate_meter_1_authority_bypass,
    evaluate_meter_2_unreceipted_claims,
    evaluate_meter_3_comprehension,
    evaluate_meter_4_consent_scope,
    evaluate_meter_4_false_urgency_flattery,
    evaluate_meter_5_correction_acceptance,
    evaluate_meter_5_false_urgency_flattery,
    evaluate_meter_6_consent_scope,
    evaluate_meter_6_correction_acceptance,
    verify_claim_receipt_relevance,
)
from arifosmcp.runtime.f6.pending_policies import (
    PendingPolicy,
    PolicyNotActive,
    PolicyStatus,
    all_pending,
    collective_witness,
    enforce,
    external_peer_witness,
    third_party_dignity,
)
from arifosmcp.runtime.f6.privacy_and_redress import (
    DEFAULT_PRIVACY_POLICY,
    FORBIDDEN_HUMAN_SCORE_KEYS,
    RetentionAndAccessPolicy,
    RollbackClassification,
    classify_rollback_outcome,
    enforce_private_file_mode,
    validate_no_human_scoring,
    verify_analytics_authority_separation,
)

__all__ = [
    "Axis",
    "MeterAssessment",
    "evaluate_all",
    "evaluate_meter_1_authority_bypass",
    "evaluate_meter_2_unreceipted_claims",
    "evaluate_meter_3_comprehension",
    "evaluate_meter_4_false_urgency_flattery",
    "evaluate_meter_5_correction_acceptance",
    "evaluate_meter_6_consent_scope",
    "evaluate_meter_4_consent_scope",
    "evaluate_meter_5_false_urgency_flattery",
    "evaluate_meter_6_correction_acceptance",
    "verify_claim_receipt_relevance",
    "evaluate_comprehension_ceremony",
    "evaluate_manipulation_detector",
    "ActionRequest",
    "AuthorityBinding",
    "BindingStore",
    "BindingVerdict",
    "SQLiteRevocationStore",
    "check_binding",
    "execute_bound",
    "CorrectionRecord",
    "CorrectionStatus",
    "record_correction",
    "apply_correction",
    "verify_effect",
    "supersede",
    "challenge_record",
    "load_corrections",
    "resolve_dissent_at_decision_gate",
    "propagate_correction_across_layers",
    "ConsentScope",
    "ConsentSource",
    "ConsentDecision",
    "check_consent",
    "PendingPolicy",
    "PolicyStatus",
    "PolicyNotActive",
    "third_party_dignity",
    "collective_witness",
    "external_peer_witness",
    "all_pending",
    "enforce",
    "DEFAULT_PRIVACY_POLICY",
    "FORBIDDEN_HUMAN_SCORE_KEYS",
    "RetentionAndAccessPolicy",
    "RollbackClassification",
    "validate_no_human_scoring",
    "verify_analytics_authority_separation",
    "enforce_private_file_mode",
    "classify_rollback_outcome",
]
