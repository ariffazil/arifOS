"""
Unit Tests for Multi-Provider Failover Orchestrator

Tests circuit breaker, retry logic, exponential backoff, and failover behavior.

Version: v45Ω Patch C (Failover)
Author: arifOS Constitutional Governance System
"""

import pytest
import time
from unittest.mock import Mock, patch
from typing import Callable

from arifos_core.connectors.failover_orchestrator import (
    ProviderConfig,
    ProviderStatus,
    FailureType,
    FailoverConfig,
    ProviderHealthTracker,
    FailoverOrchestrator,
    load_failover_config_from_env,
    create_governed_failover_backend
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_provider_primary():
    """Mock primary provider config."""
    return ProviderConfig(
        name="claude_primary",
        provider_type="claude",
        model="claude-sonnet-4-5-20250929",
        api_key="test-key-primary",
        priority=0
    )


@pytest.fixture
def mock_provider_fallback():
    """Mock fallback provider config."""
    return ProviderConfig(
        name="openai_fallback",
        provider_type="openai",
        model="gpt-4o",
        api_key="test-key-fallback",
        priority=1
    )


@pytest.fixture
def mock_provider_backup():
    """Mock backup provider config."""
    return ProviderConfig(
        name="sealion_backup",
        provider_type="sealion",
        model="aisingapore/Llama-SEA-LION-v3-70B-IT",
        api_key="test-key-backup",
        api_base="https://api.sea-lion.ai/v1",
        priority=2
    )


@pytest.fixture
def failover_config(mock_provider_primary, mock_provider_fallback, mock_provider_backup):
    """Failover configuration with 3 providers."""
    return FailoverConfig(
        providers=[mock_provider_primary, mock_provider_fallback, mock_provider_backup],
        max_consecutive_failures=3,
        circuit_open_duration=60.0,
        enable_ledger_logging=False  # Disable for unit tests
    )


@pytest.fixture
def health_tracker(failover_config):
    """Provider health tracker."""
    return ProviderHealthTracker(failover_config)


# ============================================================================
# ProviderHealthTracker Tests
# ============================================================================


def test_record_success_resets_failures(health_tracker, mock_provider_primary):
    """Test that recording success resets consecutive failures."""
    provider = mock_provider_primary
    provider.consecutive_failures = 2
    provider.status = ProviderStatus.DEGRADED

    health_tracker.record_success(provider)

    assert provider.consecutive_failures == 0
    assert provider.successful_requests == 1
    assert provider.status == ProviderStatus.HEALTHY
    assert provider.last_success_time is not None


def test_record_failure_increments_counter(health_tracker, mock_provider_primary):
    """Test that recording failure increments counter."""
    provider = mock_provider_primary

    health_tracker.record_failure(provider, FailureType.RATE_LIMIT)

    assert provider.consecutive_failures == 1
    assert provider.last_failure_time is not None


def test_circuit_breaker_opens_after_max_failures(health_tracker, mock_provider_primary):
    """Test that circuit breaker opens after max consecutive failures."""
    provider = mock_provider_primary

    # Record 2 failures -> DEGRADED
    health_tracker.record_failure(provider, FailureType.TIMEOUT)
    health_tracker.record_failure(provider, FailureType.TIMEOUT)
    assert provider.status == ProviderStatus.DEGRADED
    assert provider.consecutive_failures == 2

    # 3rd failure -> UNHEALTHY (circuit OPEN)
    health_tracker.record_failure(provider, FailureType.TIMEOUT)
    assert provider.status == ProviderStatus.UNHEALTHY
    assert provider.consecutive_failures == 3
    assert provider.circuit_opened_at is not None


def test_circuit_breaker_transitions_to_half_open(health_tracker, mock_provider_primary):
    """Test circuit breaker transitions to HALF_OPEN after cooldown."""
    provider = mock_provider_primary

    # Open circuit
    for _ in range(3):
        health_tracker.record_failure(provider, FailureType.TIMEOUT)
    assert provider.status == ProviderStatus.UNHEALTHY

    # Immediately check availability -> False (still in cooldown)
    assert health_tracker.is_available(provider) is False

    # Fast-forward past cooldown (mock time)
    provider.circuit_opened_at = time.time() - 61.0  # 61 seconds ago

    # Check availability -> True (transitions to HALF_OPEN)
    assert health_tracker.is_available(provider) is True
    assert provider.status == ProviderStatus.HALF_OPEN


def test_circuit_breaker_closes_on_success_after_half_open(health_tracker, mock_provider_primary):
    """Test circuit breaker closes when HALF_OPEN request succeeds."""
    provider = mock_provider_primary
    provider.status = ProviderStatus.HALF_OPEN
    provider.consecutive_failures = 3

    health_tracker.record_success(provider)

    assert provider.status == ProviderStatus.HEALTHY
    assert provider.consecutive_failures == 0


# ============================================================================
# FailoverOrchestrator Tests
# ============================================================================


def test_orchestrator_initialization(failover_config):
    """Test orchestrator initializes with providers sorted by priority."""
    # Mock backend initialization to avoid real API calls
    with patch.object(FailoverOrchestrator, '_initialize_backends'):
        orchestrator = FailoverOrchestrator(failover_config)

        # Check providers sorted by priority
        assert orchestrator.config.providers[0].priority == 0  # Primary
        assert orchestrator.config.providers[1].priority == 1  # Fallback
        assert orchestrator.config.providers[2].priority == 2  # Backup


def test_primary_success_no_failover(failover_config):
    """Test that primary provider success does not trigger failover."""
    # Mock backend to return success
    def mock_backend(prompt: str) -> str:
        return "Success from primary"

    orchestrator = FailoverOrchestrator(failover_config)
    orchestrator._backends = {
        "claude_primary": mock_backend,
        "openai_fallback": Mock(),
        "sealion_backup": Mock()
    }

    response, metadata = orchestrator.generate("Test prompt", lane="SOFT")

    assert response == "Success from primary"
    assert metadata["success"] is True
    assert metadata["provider"] == "claude_primary"
    assert metadata["fallback_occurred"] is False
    assert metadata["attempt_count"] == 1


def test_fallback_on_primary_failure(failover_config):
    """Test failover to fallback provider when primary fails."""
    # Mock backends
    def mock_primary_fail(prompt: str) -> str:
        raise Exception("429 Rate limit exceeded")

    def mock_fallback_success(prompt: str) -> str:
        return "Success from fallback"

    orchestrator = FailoverOrchestrator(failover_config)
    orchestrator._backends = {
        "claude_primary": mock_primary_fail,
        "openai_fallback": mock_fallback_success,
        "sealion_backup": Mock()
    }

    response, metadata = orchestrator.generate("Test prompt", lane="SOFT")

    assert response == "Success from fallback"
    assert metadata["success"] is True
    assert metadata["provider"] == "openai_fallback"
    assert metadata["fallback_occurred"] is True
    assert metadata["primary_provider"] == "claude_primary"
    assert metadata["attempt_count"] == 2  # Primary + fallback


def test_all_providers_fail_returns_void(failover_config):
    """Test that exhausting all providers returns VOID."""
    # Mock all backends to fail
    def mock_fail(prompt: str) -> str:
        raise Exception("API error")

    orchestrator = FailoverOrchestrator(failover_config)
    orchestrator._backends = {
        "claude_primary": mock_fail,
        "openai_fallback": mock_fail,
        "sealion_backup": mock_fail
    }

    response, metadata = orchestrator.generate("Test prompt", lane="HARD")

    assert "[VOID]" in response
    assert metadata["success"] is False
    assert metadata["provider"] is None
    assert metadata["attempt_count"] == 3  # All 3 providers tried
    assert "failures" in metadata


def test_retry_with_exponential_backoff(failover_config):
    """Test retry logic with exponential backoff for transient errors."""
    fail_count = 0

    def mock_backend_retry(prompt: str) -> str:
        nonlocal fail_count
        fail_count += 1
        if fail_count < 2:
            raise Exception("429 Rate limit")
        return "Success after retry"

    orchestrator = FailoverOrchestrator(failover_config)
    orchestrator._backends = {
        "claude_primary": mock_backend_retry,
        "openai_fallback": Mock(),
        "sealion_backup": Mock()
    }

    start_time = time.time()
    response, metadata = orchestrator.generate("Test prompt")
    elapsed = time.time() - start_time

    assert response == "Success after retry"
    assert metadata["success"] is True
    assert fail_count == 2  # Failed once, then succeeded
    # Should have exponential backoff delay (~0.5s)
    assert elapsed >= 0.5


def test_skip_retries_for_auth_errors(failover_config):
    """Test that auth errors skip retries and move to next provider."""
    def mock_auth_error(prompt: str) -> str:
        raise Exception("401 Unauthorized - Invalid API key")

    def mock_fallback_success(prompt: str) -> str:
        return "Fallback success"

    orchestrator = FailoverOrchestrator(failover_config)
    orchestrator._backends = {
        "claude_primary": mock_auth_error,
        "openai_fallback": mock_fallback_success,
        "sealion_backup": Mock()
    }

    start_time = time.time()
    response, metadata = orchestrator.generate("Test prompt")
    elapsed = time.time() - start_time

    assert response == "Fallback success"
    assert metadata["provider"] == "openai_fallback"
    # Auth error should skip retries -> fast failover (< 0.5s)
    assert elapsed < 0.5


def test_circuit_breaker_skips_unhealthy_provider(failover_config):
    """Test that circuit breaker skips UNHEALTHY providers."""
    orchestrator = FailoverOrchestrator(failover_config)

    # Manually set primary to UNHEALTHY
    primary = orchestrator.config.providers[0]
    primary.status = ProviderStatus.UNHEALTHY
    primary.circuit_opened_at = time.time()

    # Mock fallback success
    def mock_fallback_success(prompt: str) -> str:
        return "Fallback (primary skipped)"

    orchestrator._backends = {
        "claude_primary": Mock(),  # Should NOT be called
        "openai_fallback": mock_fallback_success,
        "sealion_backup": Mock()
    }

    response, metadata = orchestrator.generate("Test prompt")

    assert response == "Fallback (primary skipped)"
    assert metadata["provider"] == "openai_fallback"
    # Primary should not have been called
    orchestrator._backends["claude_primary"].assert_not_called()


def test_classify_error_rate_limit(failover_config):
    """Test error classification for rate limits."""
    orchestrator = FailoverOrchestrator(failover_config)

    error = Exception("429 Too Many Requests")
    failure_type = orchestrator._classify_error(error)

    assert failure_type == FailureType.RATE_LIMIT


def test_classify_error_timeout(failover_config):
    """Test error classification for timeouts."""
    orchestrator = FailoverOrchestrator(failover_config)

    error = Exception("Request timed out after 30s")
    failure_type = orchestrator._classify_error(error)

    assert failure_type == FailureType.TIMEOUT


def test_classify_error_auth(failover_config):
    """Test error classification for auth errors."""
    orchestrator = FailoverOrchestrator(failover_config)

    error = Exception("401 Unauthorized: Invalid API key")
    failure_type = orchestrator._classify_error(error)

    assert failure_type == FailureType.AUTH_ERROR


def test_exponential_backoff_calculation(failover_config):
    """Test exponential backoff delay calculation."""
    orchestrator = FailoverOrchestrator(failover_config)

    # Base: 500ms
    delay1 = orchestrator._exponential_backoff(1)
    delay2 = orchestrator._exponential_backoff(2)
    delay3 = orchestrator._exponential_backoff(3)

    assert delay1 == pytest.approx(0.5)    # 500ms
    assert delay2 == pytest.approx(1.0)    # 1000ms (2x)
    assert delay3 == pytest.approx(2.0)    # 2000ms (2x)


def test_exponential_backoff_max_cap(failover_config):
    """Test exponential backoff respects max cap."""
    orchestrator = FailoverOrchestrator(failover_config)

    # Should cap at 5000ms
    delay = orchestrator._exponential_backoff(10)  # Would be huge without cap

    assert delay <= 5.0  # 5000ms cap


# ============================================================================
# Configuration Loader Tests
# ============================================================================


def test_load_failover_config_from_env_success():
    """Test loading failover config from environment variables."""
    env = {
        "ARIFOS_FAILOVER_ENABLED": "true",
        "ARIFOS_FAILOVER_PROVIDERS": "claude_primary,openai_fallback",
        "ARIFOS_FAILOVER_CLAUDE_PRIMARY_TYPE": "claude",
        "ARIFOS_FAILOVER_CLAUDE_PRIMARY_MODEL": "claude-sonnet-4-5-20250929",
        "ARIFOS_FAILOVER_CLAUDE_PRIMARY_API_KEY": "test-key-1",
        "ARIFOS_FAILOVER_CLAUDE_PRIMARY_PRIORITY": "0",
        "ARIFOS_FAILOVER_OPENAI_FALLBACK_TYPE": "openai",
        "ARIFOS_FAILOVER_OPENAI_FALLBACK_MODEL": "gpt-4o",
        "ARIFOS_FAILOVER_OPENAI_FALLBACK_API_KEY": "test-key-2",
        "ARIFOS_FAILOVER_OPENAI_FALLBACK_PRIORITY": "1"
    }

    with patch.dict("os.environ", env, clear=True):
        config = load_failover_config_from_env()

        assert len(config.providers) == 2
        assert config.providers[0].name == "claude_primary"
        assert config.providers[0].priority == 0
        assert config.providers[1].name == "openai_fallback"
        assert config.providers[1].priority == 1


def test_load_failover_config_disabled():
    """Test loading config when failover is disabled."""
    env = {"ARIFOS_FAILOVER_ENABLED": "false"}

    with patch.dict("os.environ", env, clear=True):
        with pytest.raises(ValueError, match="not set to 'true'"):
            load_failover_config_from_env()


def test_load_failover_config_missing_providers():
    """Test loading config when provider list is missing."""
    env = {"ARIFOS_FAILOVER_ENABLED": "true"}

    with patch.dict("os.environ", env, clear=True):
        with pytest.raises(ValueError, match="ARIFOS_FAILOVER_PROVIDERS not set"):
            load_failover_config_from_env()


def test_load_failover_config_missing_provider_fields():
    """Test loading config when provider has missing required fields."""
    env = {
        "ARIFOS_FAILOVER_ENABLED": "true",
        "ARIFOS_FAILOVER_PROVIDERS": "claude_primary",
        "ARIFOS_FAILOVER_CLAUDE_PRIMARY_TYPE": "claude",
        # Missing MODEL and API_KEY
    }

    with patch.dict("os.environ", env, clear=True):
        with pytest.raises(ValueError, match="Missing required config"):
            load_failover_config_from_env()


# ============================================================================
# Governed Backend Factory Tests
# ============================================================================


def test_create_governed_failover_backend(failover_config):
    """Test creation of governed failover backend function."""
    # Mock backend initialization
    with patch.object(FailoverOrchestrator, '_initialize_backends'):
        backend = create_governed_failover_backend(failover_config)

        # Check signature matches (prompt, lane) -> (response, metadata)
        assert callable(backend)


def test_governed_backend_lane_metadata(failover_config):
    """Test governed backend passes lane metadata."""
    # Mock successful backend
    def mock_success(prompt: str) -> str:
        return "Test response"

    orchestrator = FailoverOrchestrator(failover_config)
    orchestrator._backends = {
        "claude_primary": mock_success,
        "openai_fallback": Mock(),
        "sealion_backup": Mock()
    }

    backend = create_governed_failover_backend(failover_config)

    # Patch orchestrator creation
    with patch('arifos_core.connectors.failover_orchestrator.FailoverOrchestrator', return_value=orchestrator):
        response, metadata = backend("Test prompt", lane="SOFT")

    assert response == "Test response"
    assert "provider" in metadata
    assert metadata["success"] is True


# ============================================================================
# Provider Status Monitoring Tests
# ============================================================================


def test_get_provider_status(failover_config):
    """Test getting provider status for monitoring."""
    with patch.object(FailoverOrchestrator, '_initialize_backends'):
        orchestrator = FailoverOrchestrator(failover_config)
        status = orchestrator.get_provider_status()

        assert len(status) == 3  # 3 providers
        assert all("name" in p for p in status)
        assert all("status" in p for p in status)
        assert all("total_requests" in p for p in status)


# ============================================================================
# Edge Cases & Error Handling
# ============================================================================


def test_empty_provider_list():
    """Test orchestrator with empty provider list."""
    config = FailoverConfig(providers=[])

    with patch.object(FailoverOrchestrator, '_initialize_backends'):
        orchestrator = FailoverOrchestrator(config)
        response, metadata = orchestrator.generate("Test prompt")

        assert "[VOID]" in response
        assert metadata["success"] is False


def test_backend_initialization_failure(failover_config):
    """Test handling of backend initialization failures."""
    # Mock backend creation to fail
    with patch('arifos_core.connectors.failover_orchestrator.make_claude_generate', side_effect=Exception("Init failed")):
        orchestrator = FailoverOrchestrator(failover_config)

        # Primary should be marked UNHEALTHY
        primary = orchestrator.config.providers[0]
        assert primary.status == ProviderStatus.UNHEALTHY
