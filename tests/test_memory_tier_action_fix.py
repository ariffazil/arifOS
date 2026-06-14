"""
Test for Bug 1: tier='test' silently becoming tier='canon'
Test for Bug 2: store operations running under OBSERVE authority
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from arifosmcp.runtime.memory_store import (
    _normalise_tier,
    TIER_CANONICAL,
    TIER_EPHEMERAL,
    TIER_TEST,
)


class TestTierNormalisationFix:
    """Bug 1: tier='test' → silently becomes 'canon' (FIXED)"""

    def test_tier_test_returns_test(self):
        """'test' tier should normalize to 'test', NOT 'canon'"""
        result = _normalise_tier("test")
        assert result == TIER_TEST, f"Expected '{TIER_TEST}' but got '{result}'"
        assert result != TIER_CANONICAL, f"'test' must NOT become '{TIER_CANONICAL}'"

    def test_tier_TEST_returns_test(self):
        """Uppercase 'TEST' should also normalize to 'test'"""
        result = _normalise_tier("TEST")
        assert result == TIER_TEST

    def test_tier_probe_returns_test(self):
        """'probe' tier should normalize to 'test'"""
        assert _normalise_tier("probe") == TIER_TEST
        assert _normalise_tier("PROBE") == TIER_TEST

    def test_tier_debug_returns_test(self):
        """'debug' tier should normalize to 'test'"""
        assert _normalise_tier("debug") == TIER_TEST

    def test_unknown_tier_downgrades_to_ephemeral(self):
        """Unknown tiers like 'garbage' must downgrade to ephemeral, NOT canon"""
        result = _normalise_tier("garbage_tier_xyz")
        assert result == TIER_EPHEMERAL, (
            f"Unknown tier must downgrade to '{TIER_EPHEMERAL}' "
            f"to prevent silent canon pollution. Got '{result}'"
        )

    def test_unknown_tier_NOT_canon(self):
        """The silent elevation from unknown→canon MUST be dead"""
        result = _normalise_tier("something_random_123")
        assert result != TIER_CANONICAL, (
            f"UNKNOWN TIER MUST NOT BECOME CANON. Got '{TIER_CANONICAL}'"
        )

    def test_none_tier_defaults_to_canon(self):
        """None/NULL tier still defaults to canon (backward compat)"""
        assert _normalise_tier(None) == TIER_CANONICAL
        assert _normalise_tier("") == TIER_CANONICAL

    def test_known_tiers_unchanged(self):
        """All previously known tiers must still work"""
        assert _normalise_tier("sacred") == "sacred"
        assert _normalise_tier("SACRED") == "sacred"
        assert _normalise_tier("canon") == TIER_CANONICAL
        assert _normalise_tier("CANON") == TIER_CANONICAL
        assert _normalise_tier("canonical") == TIER_CANONICAL
        assert _normalise_tier("session") == "session"
        assert _normalise_tier("ephemeral") == TIER_EPHEMERAL


class TestStoreMutationGate:
    """Bug 2: store operations must require MUTATE authority, not OBSERVE"""

    def test_store_without_mutation_returns_hold(self):
        """Calling arif_memory_recall(mode='store') without mutation_allowed → HOLD"""
        from arifosmcp.runtime.tools import _arif_memory_recall, _SESSIONS

        # Insert a fake session with mutation_allowed=False
        test_sid = "test-store-gate-sid"
        _SESSIONS[test_sid] = {
            "authority_level": "OPERATOR",
            "mutation_allowed": False,
            "actor_id": "test-agent",
        }

        try:
            result = _arif_memory_recall(
                mode="store",
                query="test content for governance gate",
                session_id=test_sid,
                actor_id="test-agent",
                tier="test",
            )

            assert isinstance(result, dict), "Result must be a dict"
            assert result.get("tool") == "arif_memory_recall"
            assert result.get("verdict") == "HOLD" or "HOLD" in str(result.get("result", "")), (
                f"Store with mutation_allowed=False must return HOLD. Got: {result}"
            )
            # Verify the F1 reason is present (gate worked)
            inner = result.get("result", {})
            reasons = inner.get("reasons", []) if isinstance(inner, dict) else []
            assert any("F1 AMANAH" in r for r in reasons), (
                f"F1 AMANAH floor must be cited. Reasons: {reasons}"
            )
            # Verify the event_type in meta
            meta = result.get("meta", {})
            assert meta.get("event_type") == "mutation_not_allowed", (
                f"meta must tag as mutation_not_allowed. Got: {meta}"
            )
        finally:
            _SESSIONS.pop(test_sid, None)

    def test_store_with_mutation_allowed_proceeds(self):
        """Calling arif_memory_recall(mode='store') with mutation_allowed=True → proceeds"""
        from arifosmcp.runtime.tools import _arif_memory_recall, _SESSIONS

        test_sid = "test-store-gate-allowed-sid"
        _SESSIONS[test_sid] = {
            "authority_level": "OPERATOR",
            "mutation_allowed": True,
            "actor_id": "test-agent",
        }

        try:
            result = _arif_memory_recall(
                mode="store",
                query="test content for governance gate — allowed",
                session_id=test_sid,
                actor_id="test-agent",
                tier="test",
            )

            assert isinstance(result, dict), "Result must be a dict"
            # With mutation_allowed=True, the gate should let it through
            # (the store itself may still succeed/fail based on backend)
            assert result.get("tool") == "arif_memory_recall"
            # Result should NOT be a HOLD on the gate
            inner = result.get("result", result)
            stored = inner.get("stored") if isinstance(inner, dict) else False
            assert stored, (
                f"Store with mutation_allowed=True should proceed. Got: {result}"
            )
        finally:
            _SESSIONS.pop(test_sid, None)

    def test_recall_without_mutation_works(self):
        """Read-only modes (recall/get/list) still work without mutation_allowed"""
        from arifosmcp.runtime.tools import _arif_memory_recall, _SESSIONS

        test_sid = "test-recall-gate-sid"
        _SESSIONS[test_sid] = {
            "authority_level": "OPERATOR",
            "mutation_allowed": False,
            "actor_id": "test-agent",
        }

        try:
            result = _arif_memory_recall(
                mode="recall",
                query="test query",
                session_id=test_sid,
                actor_id="test-agent",
            )

            assert isinstance(result, dict)
            assert result.get("tool") == "arif_memory_recall"
            # Recall is read-only — should not be blocked by the gate
            assert "HOLD" not in str(result.get("result", "")) or "mutation_not_allowed" not in str(result.get("result", "")), (
                f"Recall (read-only) must NOT be blocked. Got: {result}"
            )
        finally:
            _SESSIONS.pop(test_sid, None)
