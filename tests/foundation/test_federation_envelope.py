"""
Test FederationEnvelope — Reconstruction A Foundation
═══════════════════════════════════════════════════════
"""

from __future__ import annotations

from arifosmcp.schemas.federation_envelope import (
    ActionClass,
    ActionReceipts,
    AuthorityEnvelope,
    AuthoritySource,
    FederationEnvelope,
    RiskPassport,
    RiskTier,
    wrap_legacy_call,
)


class TestFederationEnvelope:
    def test_valid_observe_passes(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(tier=RiskTier.T0, action_class=ActionClass.OBSERVE),
        )
        ok, reason = env.validate_for_execution()
        assert ok is True
        assert reason == "SEAL"

    def test_missing_actor_id_fails(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="",
            session_id="s1",
            organ="arifOS",
        )
        ok, reason = env.validate_for_execution()
        assert ok is False
        assert "actor_id" in reason.lower()

    def test_missing_session_id_fails(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="",
            organ="arifOS",
        )
        ok, reason = env.validate_for_execution()
        assert ok is False
        assert "session_id" in reason.lower()

    def test_unknown_authority_mutate_fails(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(tier=RiskTier.T3, action_class=ActionClass.MUTATE),
            authority=AuthorityEnvelope(source=AuthoritySource.UNKNOWN),
        )
        ok, reason = env.validate_for_execution()
        assert ok is False
        assert "UNKNOWN authority" in reason

    def test_mutate_requires_observe_receipt(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(tier=RiskTier.T3, action_class=ActionClass.MUTATE),
            authority=AuthorityEnvelope(source=AuthoritySource.TOKEN, verified=True),
            receipts=ActionReceipts(),
        )
        ok, reason = env.validate_for_execution()
        assert ok is False
        assert "observe_receipt_id" in reason

    def test_mutate_with_receipt_passes(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(tier=RiskTier.T3, action_class=ActionClass.MUTATE),
            authority=AuthorityEnvelope(source=AuthoritySource.TOKEN, verified=True),
            receipts=ActionReceipts(observe_receipt_id="obs-123"),
        )
        ok, reason = env.validate_for_execution()
        assert ok is True
        assert reason == "SEAL"

    def test_atomic_requires_arif_ack(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(tier=RiskTier.T5, action_class=ActionClass.ATOMIC),
            authority=AuthorityEnvelope(source=AuthoritySource.TOKEN, verified=True),
            receipts=ActionReceipts(observe_receipt_id="obs-123"),
        )
        ok, reason = env.validate_for_execution()
        assert ok is False
        assert "arif_ack_id" in reason

    def test_risk_exceeds_ceiling(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(
                tier=RiskTier.T4,
                action_class=ActionClass.MUTATE,
                risk_ceiling="T2",
            ),
            authority=AuthorityEnvelope(source=AuthoritySource.TOKEN, verified=True),
            receipts=ActionReceipts(observe_receipt_id="obs-123"),
        )
        ok, reason = env.validate_for_execution()
        assert ok is False
        assert "exceeds ceiling" in reason

    def test_to_log_dict_no_secrets(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
        )
        log = env.to_log_dict()
        assert "trace_id" in log
        assert "actor_id" in log
        assert "risk_tier" in log
        # Must not contain raw authority secret values
        assert "api_key" not in str(log).lower()
        assert "password" not in str(log).lower()


class TestWrapLegacyCall:
    def test_wraps_with_defaults(self):
        env = wrap_legacy_call(actor_id="a1", session_id="s1", tool_name="arif_sense_observe")
        assert env.legacy_wrap is True
        assert env.actor_id == "a1"
        assert env.risk.action_class == ActionClass.OBSERVE

    def test_wrap_mutate_is_conservative(self):
        env = wrap_legacy_call(
            actor_id="a1", session_id="s1", tool_name="arif_forge_execute",
            action_class=ActionClass.MUTATE,
        )
        assert env.legacy_wrap is True
        assert env.risk.tier == RiskTier.T2
        assert env.risk.action_class == ActionClass.MUTATE

    def test_anonymous_default(self):
        env = wrap_legacy_call(actor_id=None, session_id=None, tool_name="test")
        assert env.actor_id == "anonymous"
        assert env.session_id == "unknown"


class TestRiskPassport:
    def test_exceeds_ceiling_none(self):
        rp = RiskPassport(tier=RiskTier.T5)
        assert rp.exceeds_ceiling(None) is False

    def test_exceeds_ceiling_string(self):
        rp = RiskPassport(tier=RiskTier.T4)
        assert rp.exceeds_ceiling("T2") is True
        assert rp.exceeds_ceiling("T5") is False

    def test_exceeds_ceiling_enum(self):
        rp = RiskPassport(tier=RiskTier.T3)
        assert rp.exceeds_ceiling(RiskTier.T2) is True
        assert rp.exceeds_ceiling(RiskTier.T3) is False

    def test_is_dangerous(self):
        assert RiskPassport(tier=RiskTier.T5).is_dangerous() is True
        assert RiskPassport(tier=RiskTier.T4).is_dangerous() is True
        assert RiskPassport(tier=RiskTier.T2).is_dangerous() is False
        assert RiskPassport(action_class=ActionClass.ATOMIC).is_dangerous() is True


class TestAuthorityEnvelope:
    def test_delegation_expired(self):
        from datetime import UTC, datetime, timedelta
        auth = AuthorityEnvelope(
            source=AuthoritySource.DELEGATED,
            delegator="arif",
            delegatee="agent1",
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        assert auth.is_delegation_valid() is False

    def test_delegation_valid(self):
        from datetime import UTC, datetime, timedelta
        auth = AuthorityEnvelope(
            source=AuthoritySource.DELEGATED,
            delegator="arif",
            delegatee="agent1",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            scope=["observe", "prepare"],
        )
        assert auth.is_delegation_valid() is True
        assert auth.can_act("observe") is True
        assert auth.can_act("mutate") is False

    def test_no_expiry_invalid(self):
        auth = AuthorityEnvelope(source=AuthoritySource.DELEGATED, delegator="arif")
        assert auth.is_delegation_valid() is False
