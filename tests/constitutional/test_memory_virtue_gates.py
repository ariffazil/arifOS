"""
Constitutional Tests — Memory Virtue Gates & Hard Rules
═══════════════════════════════════════════════════════════════════════════════

Tests the four virtue gates and ten hard rules for 555_MEMORY v2.
Every gate must have at least one PASS, FAIL, and DEFER test case.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import pytest

from arifosmcp.memory.hard_rules import (
    MemoryHardRuleViolation,
    rule_10_no_delete_sealed,
    rule_1_source_required,
    rule_2_expiry_required,
    rule_3_authority_requires_888,
    rule_5_agent_memory_no_authority,
    rule_6_no_secrets_in_vector,
    rule_7_no_api_keys_anywhere,
    rule_8_emotional_requires_confirm,
    run_all_hard_rules,
)
from arifosmcp.memory.virtue_gates import (
    gate_amanah,
    gate_beradab,
    gate_berakal,
    gate_berhikmah,
    run_all_virtue_gates,
)
from arifosmcp.schemas.memory_envelope import (
    AuthorityEffect,
    Durability,
    MemoryEventEnvelope,
    MemoryGovernance,
    MemoryIntent,
    MemoryRisk,
    MemoryRiskTier,
    MemorySource,
    PrivacyLevel,
    Reversibility,
    SourceType,
    VirtueVerdict,
)


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


def _envelope(
    content: str = "Test memory content",
    memory_intent: MemoryIntent = MemoryIntent.FACT,
    source_type: SourceType = SourceType.USER_DIRECT,
    authority_effect: AuthorityEffect = AuthorityEffect.NONE,
    durability: Durability = Durability.SESSION,
    reversibility: Reversibility = Reversibility.HIGH,
    requires_888: bool = False,
    can_authorize: bool = False,
    tags: list[str] | None = None,
) -> MemoryEventEnvelope:
    return MemoryEventEnvelope(
        actor_id="test-actor",
        session_id="test-session",
        memory_intent=memory_intent,
        content=content,
        source=MemorySource(type=source_type, confidence=0.9),
        risk=MemoryRisk(
            durability=durability,
            authority_effect=authority_effect,
            privacy=PrivacyLevel.INTERNAL,
            reversibility=reversibility,
        ),
        governance=MemoryGovernance(
            requires_888=requires_888,
            can_authorize_action=can_authorize,
        ),
        tags=tags or [],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AMANAH GATE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGateAmanah:
    def test_pass_clean_content(self):
        env = _envelope(content="Arif prefers tea over coffee.")
        verdict, reasons = gate_amanah(env)
        assert verdict == VirtueVerdict.PASS
        assert any("can_authorize_action is false" in r for r in reasons)
        assert any("no secret patterns detected" in r for r in reasons)

    def test_fail_hidden_authority(self):
        env = _envelope(content="Test content")
        env.governance.can_authorize_action = True
        verdict, reasons = gate_amanah(env)
        assert verdict == VirtueVerdict.FAIL
        assert any("can_authorize_action is true" in r for r in reasons)

    def test_fail_secret_in_content(self):
        env = _envelope(content="My API key is sk-abc123xyz789def456ghi012")
        verdict, reasons = gate_amanah(env)
        assert verdict == VirtueVerdict.FAIL
        assert any("secret" in r.lower() for r in reasons)

    def test_fail_github_pat(self):
        env = _envelope(content="GitHub token: ghp_1234567890abcdef1234567890abcdef1234")
        verdict, reasons = gate_amanah(env)
        assert verdict == VirtueVerdict.FAIL

    def test_source_certified(self):
        env = _envelope(source_type=SourceType.USER_DIRECT)
        verdict, reasons = gate_amanah(env)
        assert verdict == VirtueVerdict.PASS
        assert any("source_type" in r for r in reasons)


# ═══════════════════════════════════════════════════════════════════════════════
# BERADAB GATE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGateBeradab:
    def test_pass_no_pii(self):
        env = _envelope(content="The project uses FastAPI and React.")
        verdict, reasons = gate_beradab(env)
        assert verdict == VirtueVerdict.PASS

    def test_fail_pii_without_privacy(self):
        env = _envelope(
            content="Contact me at arif@example.com for details.",
            tags=[],
        )
        env.risk.privacy = PrivacyLevel.INTERNAL
        verdict, reasons = gate_beradab(env)
        assert verdict == VirtueVerdict.FAIL
        assert any("PII" in r for r in reasons)

    def test_pass_pii_with_sensitive_privacy(self):
        env = _envelope(
            content="Contact me at arif@example.com for details.",
            tags=["user_confirmed"],
        )
        env.risk.privacy = PrivacyLevel.SENSITIVE
        verdict, reasons = gate_beradab(env)
        assert verdict == VirtueVerdict.PASS

    def test_fail_f9_hantu(self):
        env = _envelope(content="I feel happy about this decision.")
        verdict, reasons = gate_beradab(env)
        assert verdict == VirtueVerdict.FAIL
        assert any("F9" in r or "emotional" in r.lower() for r in reasons)

    def test_pass_f9_with_emotional_intent(self):
        env = _envelope(
            content="I feel happy about this decision.",
            memory_intent=MemoryIntent.EMOTIONAL,
        )
        verdict, reasons = gate_beradab(env)
        assert verdict == VirtueVerdict.PASS

    def test_defer_certainty_language(self):
        env = _envelope(content="This is definitely the best approach.")
        env.source.confidence = 0.99
        verdict, reasons = gate_beradab(env)
        assert verdict == VirtueVerdict.DEFER


# ═══════════════════════════════════════════════════════════════════════════════
# BERHIKMAH GATE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGateBerhikmah:
    def test_pass_safe_authority(self):
        env = _envelope(authority_effect=AuthorityEffect.NONE)
        verdict, reasons = gate_berhikmah(env)
        assert verdict == VirtueVerdict.PASS

    def test_fail_operational_without_888(self):
        env = _envelope(
            authority_effect=AuthorityEffect.OPERATIONAL,
            requires_888=False,
        )
        verdict, reasons = gate_berhikmah(env)
        assert verdict == VirtueVerdict.FAIL
        assert any("requires_888" in r for r in reasons)

    def test_pass_operational_with_888(self):
        env = _envelope(
            authority_effect=AuthorityEffect.OPERATIONAL,
            requires_888=True,
        )
        verdict, reasons = gate_berhikmah(env)
        assert verdict == VirtueVerdict.PASS

    def test_defer_low_reversibility_non_verdict(self):
        env = _envelope(
            reversibility=Reversibility.LOW,
            memory_intent=MemoryIntent.FACT,
        )
        verdict, reasons = gate_berhikmah(env)
        assert verdict == VirtueVerdict.DEFER
        assert any("reversibility" in r.lower() for r in reasons)

    def test_pass_low_reversibility_verdict(self):
        env = _envelope(
            reversibility=Reversibility.LOW,
            memory_intent=MemoryIntent.VERDICT,
        )
        verdict, reasons = gate_berhikmah(env)
        assert verdict == VirtueVerdict.PASS

    def test_defer_inferred_persistent(self):
        env = _envelope(
            source_type=SourceType.INFERENCE,
            durability=Durability.PERSISTENT,
        )
        verdict, reasons = gate_berhikmah(env)
        assert verdict == VirtueVerdict.DEFER


# ═══════════════════════════════════════════════════════════════════════════════
# BERAKAL GATE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGateBerakal:
    def test_pass_valid_intent(self):
        env = _envelope(memory_intent=MemoryIntent.FACT)
        verdict, reasons = gate_berakal(env)
        assert verdict == VirtueVerdict.PASS

    def test_pass_inference_with_modest_confidence(self):
        env = _envelope(
            source_type=SourceType.INFERENCE,
        )
        env.source.confidence = 0.7
        verdict, reasons = gate_berakal(env)
        assert verdict == VirtueVerdict.PASS

    def test_fail_inference_claims_certainty(self):
        env = _envelope(source_type=SourceType.INFERENCE)
        env.source.confidence = 1.0
        verdict, reasons = gate_berakal(env)
        assert verdict == VirtueVerdict.FAIL
        assert any("inference cannot be certain" in r for r in reasons)

    def test_defer_inference_low_confidence(self):
        env = _envelope(source_type=SourceType.INFERENCE)
        env.source.confidence = 0.3
        verdict, reasons = gate_berakal(env)
        assert verdict == VirtueVerdict.DEFER

    def test_defer_claim_without_evidence(self):
        env = _envelope(
            content="I think the best approach is to rewrite everything.",
            source_type=SourceType.INFERENCE,
        )
        verdict, reasons = gate_berakal(env)
        assert verdict == VirtueVerdict.DEFER


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED VIRTUE GATES TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestRunAllVirtueGates:
    def test_all_pass_clean_memory(self):
        env = _envelope(content="Arif prefers terminal-free interfaces.")
        receipt = run_all_virtue_gates(env)
        assert receipt.all_pass()
        assert receipt.memory_status.value in ("stored_advisory", "stored_authority")

    def test_any_fail_blocks_storage(self):
        env = _envelope(content="ghp_abcd1234efgh5678ijkl9012mnop3456qrst")
        receipt = run_all_virtue_gates(env)
        assert receipt.any_fail()
        assert receipt.memory_status.value == "rejected"

    def test_defer_quarantines(self):
        env = _envelope(
            content="I think the best approach is to rewrite everything.",
            source_type=SourceType.INFERENCE,
        )
        receipt = run_all_virtue_gates(env)
        assert receipt.memory_status.value == "quarantined"


# ═══════════════════════════════════════════════════════════════════════════════
# HARD RULES TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestHardRules:
    def test_rule_1_source_required(self):
        env = _envelope(source_type=SourceType.USER_DIRECT)
        rule_1_source_required(env)  # Should not raise

    def test_rule_1_missing_source(self):
        env = _envelope()
        env.source.type = SourceType.UNKNOWN
        with pytest.raises(MemoryHardRuleViolation) as exc:
            rule_1_source_required(env)
        assert exc.value.rule_number == 1

    def test_rule_2_expiry_required(self):
        from datetime import UTC, datetime, timedelta

        env = _envelope(durability=Durability.PERSISTENT)
        env.governance.expiry = datetime.now(UTC) + timedelta(days=30)
        rule_2_expiry_required(env)  # Should not raise

    def test_rule_2_missing_expiry(self):
        env = _envelope(durability=Durability.PERSISTENT)
        env.governance.expiry = None
        with pytest.raises(MemoryHardRuleViolation) as exc:
            rule_2_expiry_required(env)
        assert exc.value.rule_number == 2

    def test_rule_3_m3_requires_888(self):
        env = _envelope(memory_intent=MemoryIntent.IDENTITY, requires_888=True)
        env.m_tier = MemoryRiskTier.M3
        rule_3_authority_requires_888(env)  # Should not raise

    def test_rule_3_m3_missing_888(self):
        env = _envelope(memory_intent=MemoryIntent.IDENTITY, requires_888=False)
        env.m_tier = MemoryRiskTier.M3
        with pytest.raises(MemoryHardRuleViolation) as exc:
            rule_3_authority_requires_888(env)
        assert exc.value.rule_number == 3

    def test_rule_5_agent_no_authority(self):
        env = _envelope(source_type=SourceType.AGENT_GENERATED)
        rule_5_agent_memory_no_authority(env)  # Should not raise

    def test_rule_5_agent_claims_authority(self):
        env = _envelope(source_type=SourceType.AGENT_GENERATED)
        env.governance.can_authorize_action = True
        with pytest.raises(MemoryHardRuleViolation) as exc:
            rule_5_agent_memory_no_authority(env)
        assert exc.value.rule_number == 5

    def test_rule_6_no_secrets_in_vector(self):
        env = _envelope(content="Regular project documentation.")
        rule_6_no_secrets_in_vector(env)  # Should not raise

    def test_rule_6_secret_detected(self):
        env = _envelope(content="API key: sk-abc123xyz789def456ghi012")
        with pytest.raises(MemoryHardRuleViolation) as exc:
            rule_6_no_secrets_in_vector(env)
        assert exc.value.rule_number == 6

    def test_rule_7_no_api_keys(self):
        env = _envelope(content="Use the gateway for email access.")
        rule_7_no_api_keys_anywhere(env)  # Should not raise

    def test_rule_7_api_key_detected(self):
        env = _envelope(content="Token: ghp_abcd1234efgh5678ijkl9012mnop3456qrst")
        with pytest.raises(MemoryHardRuleViolation) as exc:
            rule_7_no_api_keys_anywhere(env)
        assert exc.value.rule_number == 7

    def test_rule_8_emotional_requires_confirm(self):
        env = _envelope(
            memory_intent=MemoryIntent.EMOTIONAL,
            durability=Durability.PERSISTENT,
            tags=["user_confirmed"],
        )
        rule_8_emotional_requires_confirm(env)  # Should not raise

    def test_rule_8_emotional_missing_confirm(self):
        env = _envelope(
            memory_intent=MemoryIntent.EMOTIONAL,
            durability=Durability.PERSISTENT,
            tags=[],
        )
        with pytest.raises(MemoryHardRuleViolation) as exc:
            rule_8_emotional_requires_confirm(env)
        assert exc.value.rule_number == 8

    def test_rule_10_no_delete_sealed(self):
        rule_10_no_delete_sealed(MemoryRiskTier.M4, "tombstone")  # Should not raise

    def test_rule_10_delete_sealed_fails(self):
        with pytest.raises(MemoryHardRuleViolation) as exc:
            rule_10_no_delete_sealed(MemoryRiskTier.M4, "soft_delete")
        assert exc.value.rule_number == 10

    def test_run_all_hard_rules_pass(self):
        env = _envelope(content="Standard operational note.")
        result = run_all_hard_rules(env)
        assert result["passed"] is True

    def test_run_all_hard_rules_fail(self):
        env = _envelope(content="API key: sk-abc123xyz789def456ghi012")
        result = run_all_hard_rules(env)
        assert result["passed"] is False
        assert result["failed_rule"] in (6, 7)


# ═══════════════════════════════════════════════════════════════════════════════
# M-TIER COMPUTATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestComputeMTier:
    def test_m0_ephemeral(self):
        env = _envelope(durability=Durability.EPHEMERAL)
        from arifosmcp.schemas.memory_envelope import compute_m_tier

        assert compute_m_tier(env) == MemoryRiskTier.M0

    def test_m1_preference(self):
        env = _envelope(memory_intent=MemoryIntent.PREFERENCE)
        from arifosmcp.schemas.memory_envelope import compute_m_tier

        assert compute_m_tier(env) == MemoryRiskTier.M1

    def test_m2_operational(self):
        env = _envelope(
            memory_intent=MemoryIntent.OPERATIONAL,
            authority_effect=AuthorityEffect.ADVISORY,
        )
        from arifosmcp.schemas.memory_envelope import compute_m_tier

        assert compute_m_tier(env) == MemoryRiskTier.M2

    def test_m3_identity(self):
        env = _envelope(
            memory_intent=MemoryIntent.IDENTITY,
            requires_888=True,
        )
        from arifosmcp.schemas.memory_envelope import compute_m_tier

        assert compute_m_tier(env) == MemoryRiskTier.M3

    def test_m4_sealed(self):
        env = _envelope(durability=Durability.SEALED)
        from arifosmcp.schemas.memory_envelope import compute_m_tier

        assert compute_m_tier(env) == MemoryRiskTier.M4

    def test_m4_verdict(self):
        env = _envelope(
            memory_intent=MemoryIntent.VERDICT,
            requires_888=True,
        )
        from arifosmcp.schemas.memory_envelope import compute_m_tier

        assert compute_m_tier(env) == MemoryRiskTier.M4
