"""
Test Ingress Envelope Validation — Reconstruction A Foundation
════════════════════════════════════════════════════════════════

Tests the envelope extraction and validation logic in ingress_middleware
without requiring a live FastMCP server.
"""

from __future__ import annotations

from arifosmcp.runtime.ingress_middleware import (
    _extract_envelope_from_arguments,
    _validate_envelope_for_tool,
)
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


class TestExtractEnvelope:
    def test_no_arguments_returns_none(self):
        env = _extract_envelope_from_arguments({}, "test")
        assert env is None

    def test_nested_envelope(self):
        env = _extract_envelope_from_arguments(
            {
                "envelope": {
                    "trace_id": "t1",
                    "actor_id": "arif",
                    "session_id": "s1",
                    "organ": "arifOS",
                },
                "query": "test",
            },
            "test",
        )
        assert env is not None
        assert env.actor_id == "arif"
        assert env.trace_id == "t1"

    def test_flattened_fields(self):
        env = _extract_envelope_from_arguments(
            {
                "actor_id": "arif",
                "session_id": "s1",
                "trace_id": "t1",
                "query": "test",
            },
            "test",
        )
        assert env is not None
        assert env.actor_id == "arif"
        assert env.legacy_wrap is True

    def test_no_envelope_fields_returns_none(self):
        env = _extract_envelope_from_arguments({"query": "test"}, "test")
        assert env is None


class TestValidateEnvelope:
    def test_observe_with_unknown_authority_passes(self):
        env = wrap_legacy_call(actor_id="a1", session_id="s1", tool_name="arif_sense_observe")
        ok, reason = _validate_envelope_for_tool(env, "arif_sense_observe")
        assert ok is True
        assert reason == "SEAL"

    def test_mutate_with_legacy_wrap_fails(self):
        env = wrap_legacy_call(
            actor_id="a1",
            session_id="s1",
            tool_name="arif_forge_execute",
            action_class=ActionClass.MUTATE,
        )
        ok, reason = _validate_envelope_for_tool(env, "arif_forge_execute")
        assert ok is False
        assert "LEGACY_WRAP" in reason

    def test_mutate_with_unknown_authority_fails(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(tier=RiskTier.T3, action_class=ActionClass.MUTATE),
            authority=AuthorityEnvelope(source=AuthoritySource.UNKNOWN),
            receipts=ActionReceipts(),
        )
        ok, reason = _validate_envelope_for_tool(env, "arif_forge_execute")
        assert ok is False
        assert "UNKNOWN authority" in reason

    def test_mutate_with_verified_authority_no_receipt_fails(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(tier=RiskTier.T3, action_class=ActionClass.MUTATE),
            authority=AuthorityEnvelope(source=AuthoritySource.TOKEN, verified=True),
            receipts=ActionReceipts(),
        )
        ok, reason = _validate_envelope_for_tool(env, "arif_forge_execute")
        assert ok is False
        assert "observe_receipt_id" in reason

    def test_mutate_with_verified_authority_and_receipt_passes(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(tier=RiskTier.T3, action_class=ActionClass.MUTATE),
            authority=AuthorityEnvelope(source=AuthoritySource.TOKEN, verified=True),
            receipts=ActionReceipts(observe_receipt_id="obs-123"),
        )
        ok, reason = _validate_envelope_for_tool(env, "arif_forge_execute")
        assert ok is True
        assert reason == "SEAL"

    def test_atomic_without_arif_ack_fails(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(tier=RiskTier.T5, action_class=ActionClass.ATOMIC),
            authority=AuthorityEnvelope(source=AuthoritySource.HUMAN_888, verified=True),
            receipts=ActionReceipts(observe_receipt_id="obs-123"),
        )
        ok, reason = _validate_envelope_for_tool(env, "arif_vault_seal")
        assert ok is False
        assert "arif_ack_id" in reason

    def test_tool_risk_upgrades_envelope_then_fails_no_receipt(self):
        env = FederationEnvelope(
            trace_id="t1",
            actor_id="arif",
            session_id="s1",
            organ="arifOS",
            risk=RiskPassport(tier=RiskTier.T0, action_class=ActionClass.OBSERVE),
            authority=AuthorityEnvelope(source=AuthoritySource.TOKEN, verified=True),
        )
        ok, reason = _validate_envelope_for_tool(env, "arif_forge_execute")
        # Envelope gets upgraded to tool's risk class (ATOMIC/T5), then fails on receipt check
        assert ok is False
        assert "arif_ack_id" in reason
        assert env.risk.action_class == ActionClass.ATOMIC
        assert env.risk.tier == RiskTier.T5
