from __future__ import annotations

from arifosmcp.kernel.apex_decision_field import (
    ApexDecisionField,
    ApexDecisionVerdict,
    GovernanceScore,
    assess_apex_decision_field,
)
from arifosmcp.kernel.forge_skill_contract import (
    ForgeSkillDenyCode,
    ForgeSkillRequest,
    ForgeSkillVerdict,
    assess_forge_skill_request,
)

READ_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {}}
OUT_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {"ok": {"type": "boolean"}}}


def test_apex_decision_field_admits_high_wisdom_stable_tool():
    field = ApexDecisionField(
        q_action_potential=0.90,
        v_vitality=0.90,
        psi_stability=0.90,
        phi_wisdom=0.90,
        theta_dphi_dt=0.02,
        omega_infinity_drift=0.05,
        cce_passed=True,
        scar_constraints_applied=True,
        tpcp_passed=True,
    )

    assessment = assess_apex_decision_field(field)

    assert assessment.verdict == ApexDecisionVerdict.ADMIT
    assert assessment.admissible is True
    assert assessment.energy > assessment.thresholds["energy_threshold"]
    assert assessment.reasons == ()


def test_g36_governance_score_is_dimensionless_ratio():
    field = ApexDecisionField(
        q_action_potential=1.0,
        v_vitality=1.0,
        psi_stability=1.0,
        phi_wisdom=1.0,
        governance_score=GovernanceScore(
            a_akal_clarity=0.90,
            p_present_stability=0.90,
            e_energy_vitality=0.90,
            x_ethics_alignment=0.90,
        ),
    )

    assessment = assess_apex_decision_field(field)

    assert assessment.verdict == ApexDecisionVerdict.ADMIT
    assert assessment.governance_score == 0.9**4
    assert 0.0 <= assessment.governance_score <= 1.0
    assert assessment.c_dark == 0.9 * 0.1 * 0.1 * 1.0
    assert 0.0 <= assessment.c_dark <= 1.0


def test_g36_partial_range_holds_generated_tool():
    field = ApexDecisionField(
        q_action_potential=1.0,
        v_vitality=1.0,
        psi_stability=1.0,
        phi_wisdom=1.0,
        governance_score=GovernanceScore(
            a_akal_clarity=0.80,
            p_present_stability=0.80,
            e_energy_vitality=0.80,
            x_ethics_alignment=0.80,
        ),
    )

    assessment = assess_apex_decision_field(field)

    assert assessment.verdict == ApexDecisionVerdict.HOLD
    assert "G36_GOVERNANCE_SCORE_PARTIAL_RANGE" in assessment.reasons


def test_g36_void_range_blocks_generated_tool():
    field = ApexDecisionField(
        q_action_potential=1.0,
        v_vitality=1.0,
        psi_stability=1.0,
        phi_wisdom=1.0,
        governance_score=GovernanceScore(
            a_akal_clarity=0.90,
            p_present_stability=0.90,
            e_energy_vitality=0.90,
            x_ethics_alignment=0.10,
        ),
    )

    assessment = assess_apex_decision_field(field)

    assert assessment.verdict == ApexDecisionVerdict.VOID
    assert "G36_GOVERNANCE_SCORE_VOID_RANGE" in assessment.reasons


def test_c_dark_review_range_holds_generated_tool():
    field = ApexDecisionField(
        q_action_potential=1.0,
        v_vitality=1.0,
        psi_stability=1.0,
        phi_wisdom=1.0,
        governance_score=GovernanceScore(
            a_akal_clarity=1.0,
            p_present_stability=0.30,
            e_energy_vitality=1.0,
            x_ethics_alignment=0.50,
        ),
    )

    assessment = assess_apex_decision_field(field)

    assert assessment.c_dark == 0.35
    assert assessment.verdict == ApexDecisionVerdict.HOLD
    assert "C_DARK_REVIEW_RANGE" in assessment.reasons


def test_apex_decision_field_holds_low_phi_tool_before_registry():
    field = ApexDecisionField(
        q_action_potential=1.0,
        v_vitality=1.0,
        psi_stability=1.0,
        phi_wisdom=0.20,
        theta_dphi_dt=0.0,
        omega_infinity_drift=0.0,
    )

    assessment = assess_apex_decision_field(field)

    assert assessment.verdict == ApexDecisionVerdict.HOLD
    assert "PHI_WISDOM_BELOW_THRESHOLD" in assessment.reasons
    assert "DECISION_FIELD_ENERGY_TOO_LOW" in assessment.reasons


def test_apex_decision_field_holds_decaying_theta():
    field = ApexDecisionField(
        q_action_potential=0.95,
        v_vitality=0.95,
        psi_stability=0.95,
        phi_wisdom=0.95,
        theta_dphi_dt=-0.25,
        omega_infinity_drift=0.0,
    )

    assessment = assess_apex_decision_field(field)

    assert assessment.verdict == ApexDecisionVerdict.HOLD
    assert "THETA_WISDOM_TRAJECTORY_DECAYING" in assessment.reasons


def test_apex_decision_field_voids_failed_cce():
    field = ApexDecisionField(
        q_action_potential=0.95,
        v_vitality=0.95,
        psi_stability=0.95,
        phi_wisdom=0.95,
        theta_dphi_dt=0.0,
        omega_infinity_drift=0.0,
        cce_passed=False,
    )

    assessment = assess_apex_decision_field(field)

    assert assessment.verdict == ApexDecisionVerdict.VOID
    assert "CCE_SELF_AUDIT_FAILED" in assessment.reasons


def test_forge_skill_uses_apex_field_to_hold_low_wisdom_tool():
    request = ForgeSkillRequest(
        intent="generate risky capability that sounds useful but lacks wisdom",
        domain="aforge",
        seal_verdict_id="seal_123",
        generated_code="def run(payload):\n    return {'ok': True}\n",
        input_schema=READ_SCHEMA,
        output_schema=OUT_SCHEMA,
        apex_field=ApexDecisionField(
            q_action_potential=1.0,
            v_vitality=1.0,
            psi_stability=1.0,
            phi_wisdom=0.10,
        ),
    )

    assessment = assess_forge_skill_request(request)

    assert assessment.verdict == ForgeSkillVerdict.HOLD_888
    assert ForgeSkillDenyCode.APEX_DECISION_FIELD_HOLD in assessment.deny_codes
    assert assessment.tool_id is None
    assert assessment.evidence["apex_decision_field"] is not None


def test_forge_skill_uses_g36_to_void_low_ethics_tool():
    request = ForgeSkillRequest(
        intent="generate highly capable but ethically weak capability",
        domain="aforge",
        seal_verdict_id="seal_123",
        generated_code="def run(payload):\n    return {'ok': True}\n",
        input_schema=READ_SCHEMA,
        output_schema=OUT_SCHEMA,
        apex_field=ApexDecisionField(
            q_action_potential=1.0,
            v_vitality=1.0,
            psi_stability=1.0,
            phi_wisdom=1.0,
            governance_score=GovernanceScore(
                a_akal_clarity=1.0,
                p_present_stability=1.0,
                e_energy_vitality=1.0,
                x_ethics_alignment=0.10,
            ),
        ),
    )

    assessment = assess_forge_skill_request(request)

    assert assessment.verdict == ForgeSkillVerdict.VOID
    assert ForgeSkillDenyCode.APEX_DECISION_FIELD_VOID in assessment.deny_codes
    assert assessment.tool_id is None


def test_forge_skill_uses_apex_field_to_void_failed_cce():
    request = ForgeSkillRequest(
        intent="generate capability with failed self audit",
        domain="aforge",
        seal_verdict_id="seal_123",
        generated_code="def run(payload):\n    return {'ok': True}\n",
        input_schema=READ_SCHEMA,
        output_schema=OUT_SCHEMA,
        apex_field=ApexDecisionField(
            q_action_potential=1.0,
            v_vitality=1.0,
            psi_stability=1.0,
            phi_wisdom=1.0,
            cce_passed=False,
        ),
    )

    assessment = assess_forge_skill_request(request)

    assert assessment.verdict == ForgeSkillVerdict.VOID
    assert ForgeSkillDenyCode.APEX_DECISION_FIELD_VOID in assessment.deny_codes
    assert assessment.tool_id is None
