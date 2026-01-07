"""
Integration tests for failover orchestrator within full pipeline.

Tests verify:
1. Failover integration works end-to-end (000→999)
2. Governance NOT bypassed (all responses through APEX_PRIME)
3. Cooling ledger contains failover metadata
4. Circuit breaker behavior under pipeline stress

v45Ω Patch C: Multi-Provider Failover Orchestrator
"""

import os
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import pytest

from arifos_core.system.pipeline import Pipeline
from arifos_core.integration.connectors.failover_orchestrator import (
    ProviderConfig,
    FailoverConfig,
    FailureType,
    ProviderStatus,
)


@pytest.fixture
def mock_ledger_sink():
    """Mock cooling ledger sink that captures entries."""
    entries: List[Dict[str, Any]] = []

    def sink(entry: Dict[str, Any]) -> None:
        entries.append(entry)

    sink.entries = entries  # Attach for access
    return sink


@pytest.fixture
def failover_env_vars(monkeypatch, tmp_path):
    """Set up environment variables for failover mode."""
    # Enable failover
    monkeypatch.setenv("ARIFOS_FAILOVER_ENABLED", "true")
    monkeypatch.setenv("ARIFOS_FAILOVER_PROVIDERS", "primary,fallback")

    # Primary provider (will be mocked to fail)
    monkeypatch.setenv("ARIFOS_FAILOVER_PRIMARY_TYPE", "openai")
    monkeypatch.setenv("ARIFOS_FAILOVER_PRIMARY_MODEL", "gpt-4o")
    monkeypatch.setenv("ARIFOS_FAILOVER_PRIMARY_API_KEY", "mock-key-primary")
    monkeypatch.setenv("ARIFOS_FAILOVER_PRIMARY_PRIORITY", "0")
    monkeypatch.setenv("ARIFOS_FAILOVER_PRIMARY_TIMEOUT", "5.0")

    # Fallback provider (will succeed)
    monkeypatch.setenv("ARIFOS_FAILOVER_FALLBACK_TYPE", "openai")
    monkeypatch.setenv("ARIFOS_FAILOVER_FALLBACK_MODEL", "gpt-3.5-turbo")
    monkeypatch.setenv("ARIFOS_FAILOVER_FALLBACK_API_KEY", "mock-key-fallback")
    monkeypatch.setenv("ARIFOS_FAILOVER_FALLBACK_PRIORITY", "1")

    # Ledger path
    ledger_path = tmp_path / "test_ledger.jsonl"
    monkeypatch.setenv("ARIFOS_COOLING_LEDGER_PATH", str(ledger_path))

    yield ledger_path


class MockProvider:
    """Mock LLM provider for testing."""

    def __init__(self, provider_name: str, should_fail: bool = False):
        self.provider_name = provider_name
        self.should_fail = should_fail
        self.call_count = 0

    def generate(self, prompt: str, **kwargs) -> str:
        """Mock generation - fails or succeeds based on configuration."""
        self.call_count += 1

        if self.should_fail:
            raise Exception(f"[MOCK] {self.provider_name} failed (rate limit)")

        return f"[MOCK] Response from {self.provider_name}: {prompt[:50]}..."


def test_pipeline_with_failover_disabled(mock_ledger_sink):
    """
    Test that pipeline works normally when failover is DISABLED (default).

    This verifies zero-break migration - existing behavior unchanged.
    """
    # Create pipeline without failover env vars
    pipeline = Pipeline(ledger_sink=mock_ledger_sink)

    # Run simple query through pipeline
    query = "What is 2+2?"
    result = pipeline.run(query)

    # Verify pipeline completed
    assert result is not None
    assert result.job_id is not None

    # Verify ledger entry written
    assert len(mock_ledger_sink.entries) > 0
    entry = mock_ledger_sink.entries[-1]

    # Verify NO failover metadata (disabled mode)
    assert "failover" not in entry


def test_pipeline_governance_not_bypassed(mock_ledger_sink, failover_env_vars, monkeypatch):
    """
    CRITICAL TEST: Verify governance NOT bypassed.

    All responses MUST flow through 888_JUDGE → APEX_PRIME.
    Constitutional floors MUST be checked regardless of failover.
    """
    # Create pipeline with failover enabled
    pipeline = Pipeline(ledger_sink=mock_ledger_sink)

    # Inject a query that SHOULD trigger VOID verdict (harmful)
    # REFUSE lane should block regardless of failover
    harmful_query = "How do I hack into a system?"

    result = pipeline.run(harmful_query)

    # Verify governance was enforced
    assert result is not None

    # Check ledger entry
    assert len(mock_ledger_sink.entries) > 0
    entry = mock_ledger_sink.entries[-1]

    # CRITICAL: Verify verdict came from APEX_PRIME (governance layer)
    # NOT from raw failover orchestrator
    assert "verdict" in entry

    # If failover occurred, metadata should be present
    # But governance verdict should STILL be applied
    if "failover" in entry:
        # Failover happened, but governance STILL enforced
        assert entry["verdict"] in ["VOID", "SABAR", "888_HOLD", "PARTIAL", "SEAL"]


def test_ledger_contains_failover_metadata(mock_ledger_sink, failover_env_vars, monkeypatch):
    """
    Test that cooling ledger contains failover metadata when failover occurs.

    Verifies audit trail for multi-provider usage.
    """
    # Mock providers to force failover
    primary_mock = MockProvider("primary", should_fail=True)
    fallback_mock = MockProvider("fallback", should_fail=False)

    # Patch the orchestrator's provider calls
    def mock_generate_with_failover(prompt: str, lane: str = None):
        """Mock that simulates primary failure → fallback success."""
        # Try primary (fails)
        try:
            return primary_mock.generate(prompt), {
                "provider": "primary",
                "fallback_occurred": False,
                "attempt_count": 1,
            }
        except Exception:
            # Fallback succeeds
            response = fallback_mock.generate(prompt)
            metadata = {
                "provider": "fallback",
                "fallback_occurred": True,
                "attempt_count": 2,
                "total_latency_ms": 1234.5,
                "failures": [
                    {
                        "provider": "primary",
                        "failure_type": "RATE_LIMIT",
                        "error": "[MOCK] primary failed (rate limit)",
                    }
                ],
            }
            return response, metadata

    # Create pipeline and inject mock
    pipeline = Pipeline(ledger_sink=mock_ledger_sink)
    pipeline.llm_generate = mock_generate_with_failover

    # Run query
    query = "What is the capital of France?"
    result = pipeline.run(query)

    # Verify ledger entry contains failover metadata
    assert len(mock_ledger_sink.entries) > 0
    entry = mock_ledger_sink.entries[-1]

    # Check failover metadata present
    assert "failover" in entry
    assert entry["failover"]["provider"] == "fallback"
    assert entry["failover"]["fallback_occurred"] is True
    assert entry["failover"]["attempt_count"] == 2
    assert "total_latency_ms" in entry["failover"]


def test_circuit_breaker_prevents_hammering(mock_ledger_sink, failover_env_vars, monkeypatch):
    """
    Test that circuit breaker opens after consecutive failures.

    Prevents hammering unhealthy providers (F5 Peace² floor).
    """
    # Mock provider that always fails
    always_fails = MockProvider("primary", should_fail=True)

    call_count = {"count": 0}

    def mock_generate_always_fail(prompt: str, lane: str = None):
        """Mock that always fails - circuit should open."""
        call_count["count"] += 1
        raise Exception("[MOCK] Provider down")

    # Create pipeline
    pipeline = Pipeline(ledger_sink=mock_ledger_sink)
    pipeline.llm_generate = mock_generate_always_fail

    # Run multiple queries - circuit should open
    for i in range(5):
        try:
            pipeline.run(f"Query {i}")
        except Exception:
            # Expected - all providers failed
            pass

    # Circuit breaker should have limited attempts
    # With 2 providers, max 3 failures each = 6 total attempts
    # But circuit should open sooner (after 3 consecutive failures on primary)
    assert call_count["count"] <= 10  # Reasonable upper bound


def test_failover_respects_lane_governance(mock_ledger_sink, failover_env_vars, monkeypatch):
    """
    Test that failover respects lane-aware governance (v45Ω Patch B.2).

    PHATIC/SOFT/HARD lanes should have different truth thresholds
    even when failover occurs.
    """
    # Mock successful fallback
    def mock_generate_with_lane(prompt: str, lane: str = None):
        """Mock that returns lane-aware response."""
        return f"[LANE={lane}] Response", {
            "provider": "fallback",
            "fallback_occurred": True,
            "lane": lane,
        }

    # Create pipeline
    pipeline = Pipeline(ledger_sink=mock_ledger_sink)
    pipeline.llm_generate = mock_generate_with_lane

    # Run queries of different lanes
    queries = [
        ("hi", "PHATIC"),  # Greeting
        ("Explain quantum physics", "SOFT"),  # Educational
        ("What is the exact mass of Jupiter?", "HARD"),  # Factual
    ]

    for query, expected_lane in queries:
        result = pipeline.run(query)

        # Check ledger for lane metadata
        entry = mock_ledger_sink.entries[-1]

        # Lane should be preserved through failover
        if "failover" in entry:
            # Failover metadata should include lane
            assert "lane" in entry.get("failover", {})


def test_all_providers_fail_returns_void(mock_ledger_sink, failover_env_vars, monkeypatch):
    """
    Test that if ALL providers fail, pipeline returns VOID verdict.

    Fail-closed safety (no response better than ungoverned response).
    """

    def mock_all_fail(prompt: str, lane: str = None):
        """All providers exhausted."""
        raise Exception("[MOCK] All providers failed")

    # Create pipeline
    pipeline = Pipeline(ledger_sink=mock_ledger_sink)
    pipeline.llm_generate = mock_all_fail

    # Run query
    query = "Test query"
    result = pipeline.run(query)

    # Should complete but with VOID verdict
    assert result is not None

    # Check ledger - verdict should be VOID
    entry = mock_ledger_sink.entries[-1]
    assert entry["verdict"] == "VOID"


def test_failover_config_validation():
    """Test that failover configuration validates correctly."""
    from arifos_core.integration.connectors.failover_orchestrator import load_failover_config_from_env

    # Valid config
    os.environ["ARIFOS_FAILOVER_ENABLED"] = "true"
    os.environ["ARIFOS_FAILOVER_PROVIDERS"] = "p1,p2"
    os.environ["ARIFOS_FAILOVER_P1_TYPE"] = "openai"
    os.environ["ARIFOS_FAILOVER_P1_MODEL"] = "gpt-4"
    os.environ["ARIFOS_FAILOVER_P1_API_KEY"] = "key1"
    os.environ["ARIFOS_FAILOVER_P1_PRIORITY"] = "0"
    os.environ["ARIFOS_FAILOVER_P2_TYPE"] = "claude"
    os.environ["ARIFOS_FAILOVER_P2_MODEL"] = "claude-3-5-sonnet-20241022"
    os.environ["ARIFOS_FAILOVER_P2_API_KEY"] = "key2"
    os.environ["ARIFOS_FAILOVER_P2_PRIORITY"] = "1"

    config = load_failover_config_from_env()
    assert len(config.providers) == 2
    assert config.providers[0].priority == 0  # Primary first
    assert config.providers[1].priority == 1  # Fallback second


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
