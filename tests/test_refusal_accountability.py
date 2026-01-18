"""
arifOS v45xx - Refusal Accountability Tests

Tests for:
- Reason code mapping
- Message formatting
- Escalation tracking
- Audit logging
"""

import os
from unittest.mock import patch

import pytest

os.environ["ARIFOS_REFUSAL_ACCOUNTABILITY_ENABLED"] = "1"

from arifos.enforcement.refusal_accountability import (
    _REFUSAL_TRACKER, check_escalation_needed, clear_refusal_history,
    format_refusal_message, get_guidance_for_reason, get_refusal_count,
    get_refusal_display_reason, get_refusal_reason_code,
    is_refusal_accountability_enabled, log_refusal, track_refusal)


class TestRefusalAccountabilityEnabled:
    """Test enable/disable logic."""

    def test_enabled_via_env(self):
        with patch.dict(os.environ, {"ARIFOS_REFUSAL_ACCOUNTABILITY_ENABLED": "1"}):
            assert is_refusal_accountability_enabled() is True


class TestReasonCodeMapping:
    """Test floor failure to reason code mapping."""

    def test_f1_priority(self):
        """F1 Amanah should take priority."""
        code = get_refusal_reason_code(["F1 violation", "F5 violation"])
        assert code == "F1_AMANAH"

    def test_f5_priority(self):
        """F5 Peace² should be high priority."""
        code = get_refusal_reason_code(["F5 Peace² failure", "F7 warning"])
        assert code == "F5_PEACE_SQUARED"

    def test_f9_anti_hantu(self):
        """F9 Anti-Hantu should be detected."""
        code = get_refusal_reason_code(["F9 Anti-Hantu violation"])
        assert code == "F9_ANTI_HANTU"

    def test_safety_refusal(self):
        """Safety refusals should be detected."""
        code = get_refusal_reason_code(["SAFETY policy enforced", "REFUSE lane"])
        assert "SAFETY" in code

    def test_destructive_intent(self):
        """Destructive intent should be detected."""
        code = get_refusal_reason_code(["DESTRUCTIVE_INTENT detected"])
        assert "DESTRUCTIVE" in code

    def test_fallback_code(self):
        """Unknown failures should get generic code."""
        code = get_refusal_reason_code(["Unknown weird error"])
        assert "VIOLATION" in code or "CONSTITUTIONAL" in code


class TestDisplayReasons:
    """Test human-readable display text."""

    def test_display_for_f1(self):
        display = get_refusal_display_reason("F1_AMANAH")
        assert "harm" in display.lower() or "trust" in display.lower()

    def test_display_for_f9(self):
        display = get_refusal_display_reason("F9_ANTI_HANTU")
        assert "hantu" in display.lower() or "anti" in display.lower()


class TestGuidance:
    """Test guidance text retrieval."""

    def test_guidance_for_safety(self):
        guidance = get_guidance_for_reason("SAFETY_REFUSAL")
        assert len(guidance) > 10

    def test_guidance_fallback(self):
        guidance = get_guidance_for_reason("UNKNOWN_CODE")
        # Should return some guidance text
        assert len(guidance) > 10


class TestMessageFormatting:
    """Test refusal message formatting."""

    def test_basic_message(self):
        message = format_refusal_message(["F1 violation"], include_reason=False, include_guidance=False)
        assert "cannot assist" in message.lower()

    def test_message_with_reason(self):
        message = format_refusal_message(["F1 violation"], include_reason=True, include_guidance=False)
        assert "cannot" in message.lower()

    def test_message_with_guidance(self):
        message = format_refusal_message(["F5 Peace² violation"], include_reason=True, include_guidance=True)
        assert len(message) > 20

    def test_escalation_message(self):
        message = format_refusal_message(["F1"], is_escalation=True)
        assert "multiple" in message.lower() or "declined" in message.lower()


class TestEscalationTracking:
    """Test repeated refusal tracking and escalation."""

    def setup_method(self):
        """Clear tracker before each test."""
        _REFUSAL_TRACKER.clear()

    def test_track_refusal(self):
        track_refusal("session_1", "test query", "F1_AMANAH", ["F1"])
        assert get_refusal_count("session_1") == 1

    def test_multiple_refusals(self):
        track_refusal("session_2", "query 1", "F1_AMANAH", ["F1"])
        track_refusal("session_2", "query 2", "F5_PEACE_SQUARED", ["F5"])
        track_refusal("session_2", "query 3", "SAFETY_REFUSAL", ["SAFETY"])
        assert get_refusal_count("session_2") == 3

    def test_escalation_triggered(self):
        """Escalation should trigger after max_repeated_refusals."""
        for i in range(4):
            track_refusal("session_3", f"query {i}", "F1_AMANAH", ["F1"])
        assert check_escalation_needed("session_3") is True

    def test_no_escalation_below_threshold(self):
        track_refusal("session_4", "query 1", "F1_AMANAH", ["F1"])
        track_refusal("session_4", "query 2", "F1_AMANAH", ["F1"])
        assert check_escalation_needed("session_4") is False

    def test_clear_history(self):
        track_refusal("session_5", "query", "F1_AMANAH", ["F1"])
        clear_refusal_history("session_5")
        assert get_refusal_count("session_5") == 0


class TestAuditLogging:
    """Test audit entry creation."""

    def setup_method(self):
        _REFUSAL_TRACKER.clear()

    def test_log_refusal_creates_entry(self):
        entry = log_refusal("session_6", "test query", ["F1 violation"], "VOID")
        assert entry is not None
        assert entry.reason_code == "F1_AMANAH"
        assert entry.verdict == "VOID"

    def test_audit_entry_to_dict(self):
        entry = log_refusal("session_7", "test", ["F5"], "VOID")
        d = entry.to_dict()
        assert "timestamp" in d
        assert "query_hash" in d
        assert "reason_code" in d
        assert d["type"] == "REFUSAL"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
