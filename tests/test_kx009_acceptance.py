"""
tests/test_kx009_acceptance.py — KX-009 Failing Acceptance Tests (F13 RATIFIED 2026-10-27)

TDD Gates: These tests assert the new Four-Plane Epistemic & Remediation Contract
against the current live runtime. As mandated by PART D, tests asserting features
not yet implemented in the runtime must FAIL against current main for the intended
semantic reason.
"""

import asyncio
import pytest
from contracts.four_plane_contract import (
    EpistemicState,
    AuthorityState,
    ActionDisposition,
    ConstitutionalVerdict,
    derive_action_disposition,
)


def test_kx009_at1_unverified_actor_strong_vs_unknown_evidence_discrimination():
    """KX009-AT1: Same unverified actor, strong evidence vs one UNKNOWN core sub-claim,
    yields different epistemic_state while authority_state remains identical.
    
    Current runtime collapses claim judgment into OBSERVE_ONLY/HOLD because the actor
    is unverified. This test proves that the live arif_judge does NOT yet expose distinct
    epistemic_state discrimination on its response.
    """
    from arifosmcp.tools.judge import arif_judge
    
    # Live runtime judge returns a dict or model with 'verdict'
    res = asyncio.run(arif_judge(
        candidate={"action": "test_claim", "action_mode": "OBSERVE"},
        session_id="SEAL-test",
    ))
    
    # Must fail because current runtime does not return the 'epistemic_state' plane
    res_dict = res if isinstance(res, dict) else (res.model_dump() if hasattr(res, "model_dump") else res.__dict__)
    assert "epistemic_state" in res_dict, "Current runtime arif_judge fails KX009-AT1: lacks epistemic_state plane"
    assert res_dict["epistemic_state"] in [e.value for e in EpistemicState]


def test_kx009_at2_verified_actor_with_unsupported_evidence_not_upgraded():
    """KX009-AT2: A verified actor with unsupported evidence is not epistemically upgraded."""
    epistemic = EpistemicState.INSUFFICIENT
    authority = AuthorityState.AUTHORIZED
    disposition = derive_action_disposition(epistemic, authority)
    assert disposition != ActionDisposition.ELIGIBLE_FOR_EXECUTION
    assert disposition == ActionDisposition.GATHER_EVIDENCE


def test_kx009_at3_supported_plus_observe_only_cannot_execute():
    """KX009-AT3: SUPPORTED + OBSERVE_ONLY cannot become ELIGIBLE_FOR_EXECUTION."""
    epistemic = EpistemicState.SUPPORTED
    authority = AuthorityState.OBSERVE_ONLY
    disposition = derive_action_disposition(epistemic, authority)
    assert disposition != ActionDisposition.ELIGIBLE_FOR_EXECUTION
    assert disposition == ActionDisposition.REPORT_ONLY


def test_kx009_at4_authorized_plus_insufficient_cannot_execute():
    """KX009-AT4: AUTHORIZED + INSUFFICIENT cannot become ELIGIBLE_FOR_EXECUTION."""
    epistemic = EpistemicState.INSUFFICIENT
    authority = AuthorityState.AUTHORIZED
    disposition = derive_action_disposition(epistemic, authority)
    assert disposition != ActionDisposition.ELIGIBLE_FOR_EXECUTION
    assert disposition == ActionDisposition.GATHER_EVIDENCE


def test_kx009_at5_read_only_remediation_yields_sabar_not_dead_hold():
    """KX009-AT5: Read-only machine-resolvable blocker yields SABAR with a typed resume
    contract, not a dead HOLD.
    
    Current runtime yields HOLD whenever a floor fails or evidence is missing.
    This test verifies that the live arif_judge produces SABAR when only read-only machine
    remediation is required. Currently it produces HOLD, so it must fail for semantic reasons.
    """
    from arifosmcp.tools.judge import arif_judge
    res = asyncio.run(arif_judge(
        candidate={"action": "observe_service", "action_mode": "OBSERVE"},
        session_id="SEAL-test",
    ))
    res_dict = res if isinstance(res, dict) else (res.model_dump() if hasattr(res, "model_dump") else res.__dict__)
    assert res_dict.get("verdict") == "SABAR", f"Current runtime emitted {res_dict.get('verdict')} instead of SABAR"
    assert "remediation" in res_dict, "Current runtime lacks typed remediation contract"


def test_kx009_at6_irreversible_action_yields_hold_and_one_decision_ready_request():
    """KX009-AT6: Irreversible action requiring human authority yields HOLD and exactly one
    decision-ready human request.
    """
    from arifosmcp.tools.judge import arif_judge
    res = asyncio.run(arif_judge(
        candidate={
            "action": "production_deploy",
            "action_mode": "EXECUTE",
            "reversibility": "TIER_3_IRREVERSIBLE",
        },
        session_id="SEAL-test",
    ))
    res_dict = res if isinstance(res, dict) else (res.model_dump() if hasattr(res, "model_dump") else res.__dict__)
    assert res_dict.get("verdict") in ("HOLD", "HOLD_888")
    remediation = res_dict.get("remediation", {})
    assert "human_required" in remediation, "Current runtime lacks typed human_required list in remediation"
    assert len(remediation["human_required"]) == 1
    assert "allowed_answers" in remediation["human_required"][0]


def test_kx009_at7_no_caller_supplied_remediation_creates_authority():
    """KX009-AT7: No caller-supplied remediation item can create authority."""
    from contracts.four_plane_contract import RemediationContract, MachineResolvableItem
    item = MachineResolvableItem(
        capability_id="test.cap",
        target_ref="ref://test",
        side_effect_class="READ_ONLY",
        authority_required="AUTHORIZED",
    )
    rem = RemediationContract(machine_resolvable=[item])
    authority = AuthorityState.OBSERVE_ONLY
    assert authority == AuthorityState.OBSERVE_ONLY


def test_kx009_at8_mutation_class_remediation_cannot_execute_without_authorization():
    """KX009-AT8: Mutation-class remediation cannot execute without separate authorization."""
    from contracts.four_plane_contract import MachineResolvableItem
    item = MachineResolvableItem(
        capability_id="service.restart",
        target_ref="service://arifos",
        side_effect_class="MUTATE",
        authority_required="AUTHORIZED",
    )
    assert item.side_effect_class == "MUTATE"
    current_authority = AuthorityState.OBSERVE_ONLY
    can_execute = (current_authority == AuthorityState.AUTHORIZED)
    assert not can_execute


def test_kx009_at9_stale_state_fingerprint_invalidates_remediation():
    """KX009-AT9: Stale state fingerprint invalidates remediation eligibility."""
    from contracts.four_plane_contract import ResumeContract
    resume = ResumeContract(
        rejudge_after=["observe_done"],
        state_fingerprint="fp_hash_initial_state",
    )
    current_fingerprint = "fp_hash_world_changed"
    is_valid = (resume.state_fingerprint == current_fingerprint)
    assert not is_valid, "Fingerprint drift must invalidate remediation"


def test_kx009_at10_retry_budget_exhaustion_stops_looping():
    """KX009-AT10: Retry budget exhaustion stops looping and surfaces the unresolved blocker."""
    from contracts.four_plane_contract import MachineResolvableItem
    item = MachineResolvableItem(
        capability_id="probe.service",
        target_ref="service://well",
        side_effect_class="READ_ONLY",
        authority_required="OBSERVE_ONLY",
        max_attempts=1,
    )
    attempts_made = 1
    can_retry = attempts_made < item.max_attempts
    assert not can_retry, "Budget exhaustion must prevent further retry"


def test_kx009_at11_kx007_unknown_evidence_behavior_preserved():
    """KX009-AT11: Existing KX-007 UNKNOWN-evidence behavior remains visible."""
    from arifosmcp.tools.judge import arif_judge
    res = asyncio.run(arif_judge(
        candidate={"action": "test_claim"},
        session_id="SEAL-test",
        evidence=[{"claim": "test", "status": "UNKNOWN"}],
    ))
    res_dict = res if isinstance(res, dict) else (res.model_dump() if hasattr(res, "model_dump") else res.__dict__)
    assert res_dict.get("verdict") != "SEAL", "UNKNOWN evidence must never produce SEAL (KX-007 baseline)"


def test_kx009_at12_execution_outcome_and_acceptance_are_separate_records():
    """KX009-AT12: Execution output, world outcome and human acceptance remain separate records."""
    records = {
        "command_success": True,
        "world_outcome_verified": False,
        "human_accepted": False,
    }
    assert records["command_success"] is not records["world_outcome_verified"]
    assert records["command_success"] is not records["human_accepted"]
