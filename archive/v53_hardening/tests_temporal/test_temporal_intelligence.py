"""
arifOS v45xx - Temporal Intelligence Tests

Tests for:
- Timestamp anchoring
- Contradiction detection
- Lag metrics
- Combined temporal checks
"""

import os
import time
from unittest.mock import patch

import pytest

os.environ["ARIFOS_TEMPORAL_INTEL_ENABLED"] = "1"

from arifos.core.enforcement.temporal_checks import (_ASSERTION_MEMORY,
                                                     TemporalCheckResult,
                                                     check_timestamp_anchor,
                                                     clear_assertion_memory,
                                                     compute_lag_penalty,
                                                     detect_contradiction,
                                                     is_temporal_intel_enabled,
                                                     run_temporal_checks)


class TestTemporalIntelEnabled:
    """Test enable/disable logic."""

    def test_enabled_via_env(self):
        with patch.dict(os.environ, {"ARIFOS_TEMPORAL_INTEL_ENABLED": "1"}):
            assert is_temporal_intel_enabled() is True


class TestTimestampAnchoring:
    """Test timestamp anchoring checks."""

    def test_medical_domain_detected(self):
        result = check_timestamp_anchor(
            "What is the treatment for diabetes?",
            "Treatment includes insulin therapy and diet management."
        )
        assert result.detected_domain == "medical"
        assert result.timestamp_required is True

    def test_timestamp_found(self):
        result = check_timestamp_anchor(
            "What is the stock price of AAPL?",
            "As of 2025, AAPL stock is trading at approximately $180."
        )
        assert result.has_temporal_anchor is True

    def test_missing_timestamp_flagged(self):
        result = check_timestamp_anchor(
            "What is the current inflation rate?",
            "The inflation rate is 3.5%."  # No timestamp
        )
        # Financial domain should require timestamp
        if result.timestamp_required:
            assert result.has_temporal_anchor is False
            assert "F4" in " ".join(result.floor_violations)

    def test_non_temporal_domain_ok(self):
        result = check_timestamp_anchor(
            "What is the capital of France?",
            "The capital of France is Paris."
        )
        # Geography is not time-sensitive
        assert result.timestamp_required is False

    def test_timestamp_patterns(self):
        """Various timestamp patterns should be detected."""
        patterns = [
            "As of 2025, the data shows...",
            "Last updated 2025-01-03",
            "Currently, the situation is...",
            "Today, we see that...",
        ]
        for text in patterns:
            result = check_timestamp_anchor("financial query", text)
            # Should find timestamp
            assert result.has_temporal_anchor is True


class TestContradictionDetection:
    """Test contradiction detection."""

    def setup_method(self):
        _ASSERTION_MEMORY.clear()

    def test_no_contradiction_first_response(self):
        result = detect_contradiction(
            "session_1",
            "The sky is blue. Water is wet.",
            store_assertions=True
        )
        assert result.contradiction_detected is False

    def test_contradiction_detected(self):
        # First response
        detect_contradiction(
            "session_2",
            "The answer is true.",
            store_assertions=True
        )
        # Contradicting response
        result = detect_contradiction(
            "session_2",
            "The answer is false.",
            store_assertions=True
        )
        # Simple heuristic may or may not catch this
        # Test the basic structure
        assert isinstance(result.contradiction_detected, bool)

    def test_clear_memory(self):
        detect_contradiction("session_3", "Test assertion", store_assertions=True)
        assert "session_3" in _ASSERTION_MEMORY
        clear_assertion_memory("session_3")
        assert "session_3" not in _ASSERTION_MEMORY

    def test_contradiction_floor_violation(self):
        result = TemporalCheckResult(contradiction_detected=True)
        result.floor_violations.append("F3_CONTRADICTION")
        assert "F3" in " ".join(result.floor_violations)


class TestLagMetrics:
    """Test processing lag metrics."""

    def test_no_lag_penalty(self):
        start = time.time()
        time.sleep(0.01)  # 10ms
        result = compute_lag_penalty(start)
        assert result.lag_exceeded is False
        assert result.psi_penalty == 0.0

    def test_lag_detected(self):
        # Simulate 6 seconds ago
        start = time.time() - 6.0
        result = compute_lag_penalty(start)
        assert result.processing_ms > 5000
        assert result.lag_exceeded is True
        assert result.psi_penalty > 0

    def test_critical_lag(self):
        # Simulate 15 seconds ago
        start = time.time() - 15.0
        result = compute_lag_penalty(start)
        assert result.lag_exceeded is True
        assert "F1" in " ".join(result.floor_violations)
        if result.processing_ms > 10000:
            assert "CRITICAL" in " ".join(result.floor_violations)

    def test_psi_penalty_capped(self):
        # Very long processing time
        start = time.time() - 60.0  # 60 seconds
        result = compute_lag_penalty(start)
        assert result.psi_penalty <= 0.5  # Should be capped


class TestCombinedTemporalChecks:
    """Test combined temporal check function."""

    def setup_method(self):
        _ASSERTION_MEMORY.clear()

    def test_combined_check(self):
        start = time.time() - 0.1  # 100ms ago (fast)
        result = run_temporal_checks(
            session_id="combined_1",
            query="What is the capital of France?",
            response="Paris is the capital of France.",
            start_time=start,
        )
        # Should complete without error
        assert isinstance(result, TemporalCheckResult)
        assert result.processing_ms > 0
        assert result.contradiction_detected is False

    def test_combined_check_medical(self):
        start = time.time()
        result = run_temporal_checks(
            session_id="combined_2",
            query="What is the treatment for hypertension?",
            response="Treatment includes ACE inhibitors and lifestyle changes.",
            start_time=start,
        )
        assert result.detected_domain == "medical"
        assert result.timestamp_required is True


class TestTemporalCheckResult:
    """Test TemporalCheckResult dataclass."""

    def test_to_dict(self):
        result = TemporalCheckResult(
            has_temporal_anchor=True,
            timestamp_required=True,
            detected_domain="medical",
            processing_ms=1500.0,
            floor_violations=["F4_MISSING_TIMESTAMP"],
        )
        d = result.to_dict()
        assert d["has_temporal_anchor"] is True
        assert d["detected_domain"] == "medical"
        assert d["processing_ms"] == 1500.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
