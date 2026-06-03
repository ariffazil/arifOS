"""
Test Risk Classifier — Reconstruction A Foundation
════════════════════════════════════════════════════
"""

from __future__ import annotations

from arifosmcp.core.enforcement.risk_classifier import (
    classify_from_legacy,
    classify_tool,
    derive_ceiling,
)
from arifosmcp.schemas.federation_envelope import (
    ActionClass,
    BlastRadius,
    ExternalEffect,
    ReversibilityLevel,
    RiskTier,
    SecretTouch,
)


class TestClassifyFromLegacy:
    def test_c0_to_t0_observe(self):
        rp = classify_from_legacy(level="C0")
        assert rp.tier == RiskTier.T0
        assert rp.action_class == ActionClass.OBSERVE

    def test_c2_to_t2_prepare(self):
        rp = classify_from_legacy(level="C2")
        assert rp.tier == RiskTier.T2
        assert rp.action_class == ActionClass.PREPARE

    def test_high_to_t4_mutate(self):
        rp = classify_from_legacy(level="high")
        assert rp.tier == RiskTier.T4
        assert rp.action_class == ActionClass.MUTATE

    def test_t3_to_t3_mutate(self):
        rp = classify_from_legacy(level="T3")
        assert rp.tier == RiskTier.T3
        assert rp.action_class == ActionClass.MUTATE

    def test_readonly_to_t0(self):
        rp = classify_from_legacy(level="READONLY")
        assert rp.tier == RiskTier.T0
        assert rp.action_class == ActionClass.OBSERVE

    def test_action_class_override(self):
        rp = classify_from_legacy(action_class="atomic")
        assert rp.action_class == ActionClass.ATOMIC
        assert rp.tier == RiskTier.T5

    def test_blast_radius_mapping(self):
        rp = classify_from_legacy(blast_radius="infra")
        assert rp.blast_radius == BlastRadius.INFRA

    def test_reversibility_mapping(self):
        rp = classify_from_legacy(reversibility="irreversible")
        assert rp.reversibility == ReversibilityLevel.IRREVERSIBLE

    def test_secret_touch_mapping(self):
        rp = classify_from_legacy(secret_touch="definite")
        assert rp.secret_touch == SecretTouch.DEFINITE

    def test_external_effect_mapping(self):
        rp = classify_from_legacy(external_effect="financial")
        assert rp.external_effect == ExternalEffect.FINANCIAL

    def test_unknown_value_defaults(self):
        rp = classify_from_legacy(level="unknown_xyz")
        assert rp.tier == RiskTier.T0  # default


class TestClassifyTool:
    def test_forge_execute_is_t5(self):
        rp = classify_tool("arif_forge_execute")
        assert rp.tier == RiskTier.T5
        assert rp.action_class == ActionClass.ATOMIC

    def test_session_init_is_t5(self):
        rp = classify_tool("arif_session_init")
        assert rp.tier == RiskTier.T5
        assert rp.action_class == ActionClass.ATOMIC

    def test_vault_seal_is_t5(self):
        rp = classify_tool("arif_vault_seal")
        assert rp.tier == RiskTier.T5
        assert rp.action_class == ActionClass.ATOMIC

    def test_judge_deliberate_is_t5(self):
        rp = classify_tool("arif_judge_deliberate")
        assert rp.tier == RiskTier.T5
        assert rp.action_class == ActionClass.ATOMIC

    def test_sense_observe_is_t1(self):
        rp = classify_tool("arif_sense_observe")
        assert rp.tier == RiskTier.T1
        assert rp.action_class == ActionClass.OBSERVE

    def test_memory_recall_is_t3(self):
        rp = classify_tool("arif_memory_recall")
        assert rp.tier == RiskTier.T3
        assert rp.action_class == ActionClass.MUTATE

    def test_mind_reason_is_t2(self):
        rp = classify_tool("arif_mind_reason")
        assert rp.tier == RiskTier.T2
        assert rp.action_class == ActionClass.PREPARE

    def test_evidence_fetch_is_t2(self):
        rp = classify_tool("arif_evidence_fetch")
        assert rp.tier == RiskTier.T2
        assert rp.action_class == ActionClass.PREPARE

    def test_kernel_route_is_t3(self):
        rp = classify_tool("arif_kernel_route")
        assert rp.tier == RiskTier.T3
        assert rp.action_class == ActionClass.MUTATE

    def test_gateway_connect_is_t3(self):
        rp = classify_tool("arif_gateway_connect")
        assert rp.tier == RiskTier.T3
        assert rp.action_class == ActionClass.MUTATE

    def test_ops_measure_is_t1(self):
        rp = classify_tool("arif_ops_measure")
        assert rp.tier == RiskTier.T1
        assert rp.action_class == ActionClass.OBSERVE

    def test_reply_compose_is_t1(self):
        rp = classify_tool("arif_reply_compose")
        assert rp.tier == RiskTier.T1
        assert rp.action_class == ActionClass.OBSERVE

    def test_heart_critique_is_t5(self):
        rp = classify_tool("arif_heart_critique")
        assert rp.tier == RiskTier.T5
        assert rp.action_class == ActionClass.ATOMIC

    def test_unknown_tool_defaults_t0(self):
        rp = classify_tool("some_random_tool")
        assert rp.tier == RiskTier.T0
        assert rp.action_class == ActionClass.OBSERVE


class TestDeriveCeiling:
    def test_f13_no_ceiling(self):
        ceiling = derive_ceiling(authority_verified=False, is_f13=True)
        assert ceiling == RiskTier.T5

    def test_verified_with_atomic_scope(self):
        ceiling = derive_ceiling(authority_verified=True, delegation_scope=["atomic"])
        assert ceiling == RiskTier.T5

    def test_verified_with_mutate_scope(self):
        ceiling = derive_ceiling(authority_verified=True, delegation_scope=["mutate"])
        assert ceiling == RiskTier.T3

    def test_verified_no_scope(self):
        ceiling = derive_ceiling(authority_verified=True)
        assert ceiling == RiskTier.T2

    def test_unverified(self):
        ceiling = derive_ceiling(authority_verified=False)
        assert ceiling == RiskTier.T1
