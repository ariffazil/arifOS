"""
Multi-Provider Failover Orchestrator for arifOS

Provides automatic failover across multiple LLM providers (Claude, OpenAI, Gemini, SEA-LION)
with circuit breaker pattern, health tracking, and cooling ledger integration.

Constitutional Guarantee: ALL responses flow through 888_JUDGE → APEX_PRIME.
The orchestrator ONLY handles provider selection, never bypassing governance.

Usage:
    # Environment configuration
    export ARIFOS_FAILOVER_ENABLED=true
    export ARIFOS_FAILOVER_PROVIDERS=claude_primary,openai_fallback

    # Provider configs
    export ARIFOS_FAILOVER_CLAUDE_PRIMARY_TYPE=claude
    export ARIFOS_FAILOVER_CLAUDE_PRIMARY_MODEL=claude-sonnet-4-5-20250929
    export ARIFOS_FAILOVER_CLAUDE_PRIMARY_API_KEY=$ANTHROPIC_API_KEY
    export ARIFOS_FAILOVER_CLAUDE_PRIMARY_PRIORITY=0

    # In code
    from arifos_core.connectors.failover_orchestrator import (
        load_failover_config_from_env,
        create_governed_failover_backend
    )

    config = load_failover_config_from_env()
    llm_generate = create_governed_failover_backend(config, ledger_sink)

Version: v45Ω Patch C (Failover)
Author: arifOS Constitutional Governance System
"""

import os
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, List, Dict, Any, Tuple
from datetime import datetime, timezone

# Import existing adapters
from ..adapters.llm_openai import make_llm_generate as make_openai_generate
from ..adapters.llm_claude import make_llm_generate as make_claude_generate
from ..adapters.llm_gemini import make_llm_generate as make_gemini_generate
from ..adapters.llm_sealion import make_llm_generate_governed as make_sealion_generate
from ..integration.adapters.llm_interface import LLMConfig

logger = logging.getLogger(__name__)


# ============================================================================
# Enumerations
# ============================================================================


class ProviderStatus(Enum):
    """Provider health status for circuit breaker."""
    HEALTHY = "HEALTHY"          # Circuit CLOSED - requests allowed
    DEGRADED = "DEGRADED"        # Experiencing failures but not yet tripped
    UNHEALTHY = "UNHEALTHY"      # Circuit OPEN - skip for cooldown period
    HALF_OPEN = "HALF_OPEN"      # Testing recovery after cooldown


class FailureType(Enum):
    """Classification of provider failures for retry logic."""
    RATE_LIMIT = "RATE_LIMIT"        # 429 - Retry with backoff
    TIMEOUT = "TIMEOUT"              # Connection timeout - Retry
    API_ERROR = "API_ERROR"          # 5xx server error - Retry
    AUTH_ERROR = "AUTH_ERROR"        # 401/403 - Skip retries
    INVALID_RESPONSE = "INVALID_RESPONSE"  # Malformed response - Skip
    UNKNOWN = "UNKNOWN"              # Unclassified - Skip


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class ProviderConfig:
    """
    Configuration for a single LLM provider.

    Attributes:
        name: Unique provider identifier (e.g., "claude_primary")
        provider_type: Provider type ("claude", "openai", "gemini", "sealion")
        model: Model identifier
        api_key: API authentication key
        api_base: Custom API base URL (for SEA-LION)
        priority: Lower = higher priority (0=primary, 1=fallback, 2=backup)
        timeout_seconds: Request timeout
        max_retries: Maximum retry attempts for transient failures

        # Runtime health tracking
        status: Current provider health status
        consecutive_failures: Consecutive failure count
        total_requests: Total requests sent to this provider
        successful_requests: Total successful requests
        last_success_time: Timestamp of last successful request
        last_failure_time: Timestamp of last failed request
        circuit_opened_at: Timestamp when circuit opened (UNHEALTHY)
    """
    name: str
    provider_type: str
    model: str
    api_key: str
    api_base: Optional[str] = None
    priority: int = 0
    timeout_seconds: float = 30.0
    max_retries: int = 2

    # Runtime health tracking
    status: ProviderStatus = ProviderStatus.HEALTHY
    consecutive_failures: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    last_success_time: Optional[float] = None
    last_failure_time: Optional[float] = None
    circuit_opened_at: Optional[float] = None


@dataclass
class ProviderAttempt:
    """
    Record of a single provider generation attempt.

    Attributes:
        provider_name: Provider that was attempted
        success: Whether attempt succeeded
        failure_type: Type of failure (if failed)
        error_message: Error details (if failed)
        latency_ms: Request latency in milliseconds
        timestamp: Attempt timestamp
    """
    provider_name: str
    success: bool
    failure_type: Optional[FailureType] = None
    error_message: Optional[str] = None
    latency_ms: float = 0.0
    timestamp: float = field(default_factory=lambda: time.time())


@dataclass
class FailoverResult:
    """
    Result of failover generation attempt.

    Attributes:
        response: Generated text response
        success: Overall success status
        successful_provider: Name of provider that succeeded (if any)
        attempts: List of all provider attempts
        fallback_occurred: True if primary provider failed
        total_latency_ms: Total time including retries and failover
        metadata: Additional metadata for cooling ledger
    """
    response: str
    success: bool
    successful_provider: Optional[str] = None
    attempts: List[ProviderAttempt] = field(default_factory=list)
    fallback_occurred: bool = False
    total_latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailoverConfig:
    """
    Failover orchestrator configuration.

    Attributes:
        providers: List of provider configurations (sorted by priority)
        max_consecutive_failures: Failures before opening circuit breaker
        circuit_open_duration: Seconds to keep circuit open (cooldown)
        exponential_backoff_base_ms: Base delay for exponential backoff
        exponential_backoff_max_ms: Maximum delay cap for backoff
        enable_ledger_logging: Write failover events to cooling ledger
    """
    providers: List[ProviderConfig]
    max_consecutive_failures: int = 3
    circuit_open_duration: float = 60.0  # seconds
    exponential_backoff_base_ms: float = 500.0
    exponential_backoff_max_ms: float = 5000.0
    enable_ledger_logging: bool = True


# ============================================================================
# Provider Health Tracker (Circuit Breaker)
# ============================================================================


class ProviderHealthTracker:
    """
    Tracks provider health and implements circuit breaker pattern.

    States:
        CLOSED (HEALTHY): Provider working normally
        OPEN (UNHEALTHY): Provider failed too many times, skip for cooldown
        HALF_OPEN: Testing recovery after cooldown

    Transitions:
        CLOSED → OPEN: After max_consecutive_failures
        OPEN → HALF_OPEN: After circuit_open_duration seconds
        HALF_OPEN → CLOSED: If test request succeeds
        HALF_OPEN → OPEN: If test request fails (reset timer)
    """

    def __init__(self, config: FailoverConfig):
        self.config = config

    def record_success(self, provider: ProviderConfig) -> None:
        """Record successful request."""
        provider.consecutive_failures = 0
        provider.successful_requests += 1
        provider.last_success_time = time.time()

        # Close circuit if was open
        if provider.status in [ProviderStatus.UNHEALTHY, ProviderStatus.HALF_OPEN]:
            provider.status = ProviderStatus.HEALTHY
            provider.circuit_opened_at = None
            logger.info(f"[CIRCUIT_BREAKER] Provider {provider.name} recovered → HEALTHY")

    def record_failure(self, provider: ProviderConfig, failure_type: FailureType) -> None:
        """Record failed request and update circuit breaker state."""
        provider.consecutive_failures += 1
        provider.last_failure_time = time.time()

        # Check if should open circuit
        if provider.consecutive_failures >= self.config.max_consecutive_failures:
            if provider.status != ProviderStatus.UNHEALTHY:
                provider.status = ProviderStatus.UNHEALTHY
                provider.circuit_opened_at = time.time()
                logger.warning(
                    f"[CIRCUIT_BREAKER] Provider {provider.name} → UNHEALTHY "
                    f"({provider.consecutive_failures} consecutive failures)"
                )
        elif provider.consecutive_failures > 1:
            provider.status = ProviderStatus.DEGRADED

    def is_available(self, provider: ProviderConfig) -> bool:
        """
        Check if provider is available for requests.

        Returns:
            True if circuit is CLOSED or HALF_OPEN (allow test), False if OPEN
        """
        if provider.status == ProviderStatus.UNHEALTHY:
            # Check if cooldown period elapsed
            if provider.circuit_opened_at:
                elapsed = time.time() - provider.circuit_opened_at
                if elapsed >= self.config.circuit_open_duration:
                    # Transition to HALF_OPEN for testing
                    provider.status = ProviderStatus.HALF_OPEN
                    logger.info(f"[CIRCUIT_BREAKER] Provider {provider.name} → HALF_OPEN (testing recovery)")
                    return True  # Allow one test request
                else:
                    # Still in cooldown
                    return False
            else:
                return False

        # HEALTHY, DEGRADED, or HALF_OPEN → allow requests
        return True


# ============================================================================
# Failover Orchestrator
# ============================================================================


class FailoverOrchestrator:
    """
    Main orchestrator for multi-provider failover with circuit breaker.

    Tries providers in priority order with automatic retry and failover:
    1. Sort providers by priority (0=primary, 1=fallback, etc.)
    2. For each provider:
       - Check circuit breaker (skip if OPEN)
       - Attempt generation
       - On transient failure: retry with exponential backoff
       - On non-retryable failure: move to next provider
    3. If all providers fail: return VOID

    Constitutional guarantee: This orchestrator ONLY selects providers.
    ALL responses still flow through 888_JUDGE → APEX_PRIME.
    """

    def __init__(
        self,
        config: FailoverConfig,
        ledger_sink: Optional[Callable[[dict], None]] = None
    ):
        self.config = config
        self.ledger_sink = ledger_sink
        self.health_tracker = ProviderHealthTracker(config)

        # Sort providers by priority
        self.config.providers.sort(key=lambda p: p.priority)

        # Create provider backends
        self._backends: Dict[str, Callable[[str], str]] = {}
        self._initialize_backends()

        logger.info(
            f"[FAILOVER] Initialized with {len(self.config.providers)} providers: "
            f"{[p.name for p in self.config.providers]}"
        )

    def _initialize_backends(self) -> None:
        """Initialize LLM backends for all providers."""
        for provider in self.config.providers:
            try:
                backend = self._create_backend(provider)
                self._backends[provider.name] = backend
                logger.info(f"[FAILOVER] Initialized backend for {provider.name} ({provider.provider_type})")
            except Exception as e:
                logger.error(f"[FAILOVER] Failed to initialize {provider.name}: {e}")
                provider.status = ProviderStatus.UNHEALTHY

    def _create_backend(self, provider: ProviderConfig) -> Callable[[str], str]:
        """
        Create LLM backend for provider.

        Returns:
            Callable that takes prompt and returns response text
        """
        llm_config = LLMConfig(
            max_tokens=2048,
            temperature=0.7
        )

        if provider.provider_type == "openai":
            return make_openai_generate(
                api_key=provider.api_key,
                model=provider.model,
                config=llm_config
            )
        elif provider.provider_type == "claude":
            return make_claude_generate(
                api_key=provider.api_key,
                model=provider.model,
                config=llm_config
            )
        elif provider.provider_type == "gemini":
            return make_gemini_generate(
                api_key=provider.api_key,
                model=provider.model,
                config=llm_config
            )
        elif provider.provider_type == "sealion":
            # SEA-LION uses governed variant (already returns tuple)
            backend_tuple = make_sealion_generate(
                model=provider.model,
                config=llm_config,
                ledger_sink=self.ledger_sink
            )
            # Wrap to extract text only
            def sealion_wrapper(prompt: str) -> str:
                response, _ = backend_tuple(prompt, lane="UNKNOWN")
                return response
            return sealion_wrapper
        else:
            raise ValueError(f"Unknown provider type: {provider.provider_type}")

    def _classify_error(self, error: Exception) -> FailureType:
        """Classify error type for retry logic."""
        error_str = str(error).lower()

        if "429" in error_str or "rate limit" in error_str:
            return FailureType.RATE_LIMIT
        elif "timeout" in error_str or "timed out" in error_str:
            return FailureType.TIMEOUT
        elif "500" in error_str or "502" in error_str or "503" in error_str:
            return FailureType.API_ERROR
        elif "401" in error_str or "403" in error_str or "api key" in error_str:
            return FailureType.AUTH_ERROR
        elif "invalid" in error_str or "malformed" in error_str:
            return FailureType.INVALID_RESPONSE
        else:
            return FailureType.UNKNOWN

    def _is_retryable(self, failure_type: FailureType) -> bool:
        """Check if failure type should be retried."""
        return failure_type in [
            FailureType.RATE_LIMIT,
            FailureType.TIMEOUT,
            FailureType.API_ERROR
        ]

    def _exponential_backoff(self, retry_attempt: int) -> float:
        """
        Calculate exponential backoff delay.

        Args:
            retry_attempt: Retry number (1, 2, 3, ...)

        Returns:
            Delay in seconds
        """
        delay_ms = self.config.exponential_backoff_base_ms * (2 ** (retry_attempt - 1))
        delay_ms = min(delay_ms, self.config.exponential_backoff_max_ms)
        return delay_ms / 1000.0  # Convert to seconds

    def _try_provider(
        self,
        provider: ProviderConfig,
        prompt: str
    ) -> Tuple[bool, str, Optional[FailureType], Optional[str], float]:
        """
        Try to generate response from provider with retries.

        Returns:
            (success, response, failure_type, error_message, latency_ms)
        """
        backend = self._backends.get(provider.name)
        if not backend:
            return (False, "", FailureType.UNKNOWN, "Backend not initialized", 0.0)

        retry_attempt = 0
        max_retries = provider.max_retries

        while retry_attempt <= max_retries:
            start_time = time.time()

            try:
                # Attempt generation
                response = backend(prompt)
                latency_ms = (time.time() - start_time) * 1000

                # Success
                provider.total_requests += 1
                self.health_tracker.record_success(provider)
                return (True, response, None, None, latency_ms)

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                provider.total_requests += 1

                # Classify error
                failure_type = self._classify_error(e)
                error_message = str(e)

                # Check if should retry
                if retry_attempt < max_retries and self._is_retryable(failure_type):
                    retry_attempt += 1
                    delay = self._exponential_backoff(retry_attempt)

                    logger.warning(
                        f"[FAILOVER] {provider.name} failed ({failure_type.value}), "
                        f"retry {retry_attempt}/{max_retries} in {delay:.2f}s"
                    )

                    time.sleep(delay)
                    continue  # Retry
                else:
                    # No more retries or non-retryable error
                    self.health_tracker.record_failure(provider, failure_type)
                    return (False, "", failure_type, error_message, latency_ms)

        # Exhausted retries
        return (False, "", FailureType.UNKNOWN, "Max retries exhausted", latency_ms)

    def generate(
        self,
        prompt: str,
        lane: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate response with automatic failover.

        Args:
            prompt: Input prompt
            lane: Applicability lane (PHATIC/SOFT/HARD/REFUSE) for metadata

        Returns:
            (response, metadata) tuple

            metadata = {
                "provider": str,
                "primary_provider": str,
                "fallback_occurred": bool,
                "attempt_count": int,
                "total_latency_ms": float,
                "success": bool,
                "failures": List[dict]
            }
        """
        start_time = time.time()
        attempts: List[ProviderAttempt] = []
        primary_provider = self.config.providers[0].name if self.config.providers else None

        # Try each provider in priority order
        for provider in self.config.providers:
            # Check circuit breaker
            if not self.health_tracker.is_available(provider):
                logger.info(f"[FAILOVER] Skipping {provider.name} (circuit OPEN)")
                continue

            # Attempt generation
            success, response, failure_type, error_msg, latency_ms = self._try_provider(
                provider,
                prompt
            )

            # Record attempt
            attempt = ProviderAttempt(
                provider_name=provider.name,
                success=success,
                failure_type=failure_type,
                error_message=error_msg,
                latency_ms=latency_ms
            )
            attempts.append(attempt)

            if success:
                # Success - return response
                total_latency_ms = (time.time() - start_time) * 1000
                fallback_occurred = (provider.name != primary_provider)

                metadata = {
                    "provider": provider.name,
                    "primary_provider": primary_provider,
                    "fallback_occurred": fallback_occurred,
                    "attempt_count": len(attempts),
                    "total_latency_ms": total_latency_ms,
                    "success": True
                }

                # Log failover event if occurred
                if fallback_occurred and self.config.enable_ledger_logging and self.ledger_sink:
                    self._log_failover_event(
                        lane=lane,
                        primary_provider=primary_provider,
                        successful_provider=provider.name,
                        attempts=attempts
                    )

                return (response, metadata)

        # All providers failed
        total_latency_ms = (time.time() - start_time) * 1000

        metadata = {
            "provider": None,
            "primary_provider": primary_provider,
            "fallback_occurred": True,
            "attempt_count": len(attempts),
            "total_latency_ms": total_latency_ms,
            "success": False,
            "failures": [
                {
                    "provider": a.provider_name,
                    "failure_type": a.failure_type.value if a.failure_type else "UNKNOWN",
                    "error": a.error_message
                }
                for a in attempts
            ]
        }

        # Log catastrophic failure
        if self.config.enable_ledger_logging and self.ledger_sink:
            self._log_all_providers_failed(lane, attempts)

        # Return VOID response (will be caught by APEX_PRIME)
        return ("[VOID] All LLM providers failed", metadata)

    def _log_failover_event(
        self,
        lane: Optional[str],
        primary_provider: Optional[str],
        successful_provider: str,
        attempts: List[ProviderAttempt]
    ) -> None:
        """Log failover event to cooling ledger."""
        if not self.ledger_sink:
            return

        event = {
            "event": "PROVIDER_FAILOVER",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "primary_provider": primary_provider,
            "successful_provider": successful_provider,
            "lane": lane or "UNKNOWN",
            "attempt_count": len(attempts),
            "failures": [
                {
                    "provider": a.provider_name,
                    "failure_type": a.failure_type.value if a.failure_type else "UNKNOWN",
                    "error": a.error_message,
                    "latency_ms": a.latency_ms
                }
                for a in attempts if not a.success
            ]
        }

        try:
            self.ledger_sink(event)
        except Exception as e:
            logger.error(f"[FAILOVER] Failed to log failover event: {e}")

    def _log_all_providers_failed(
        self,
        lane: Optional[str],
        attempts: List[ProviderAttempt]
    ) -> None:
        """Log catastrophic failure event to cooling ledger."""
        if not self.ledger_sink:
            return

        event = {
            "event": "ALL_PROVIDERS_FAILED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lane": lane or "UNKNOWN",
            "attempt_count": len(attempts),
            "failures": [
                {
                    "provider": a.provider_name,
                    "failure_type": a.failure_type.value if a.failure_type else "UNKNOWN",
                    "error": a.error_message,
                    "latency_ms": a.latency_ms
                }
                for a in attempts
            ]
        }

        try:
            self.ledger_sink(event)
        except Exception as e:
            logger.error(f"[FAILOVER] Failed to log catastrophic failure: {e}")

    def get_provider_status(self) -> List[Dict[str, Any]]:
        """Get current status of all providers (for monitoring/debugging)."""
        return [
            {
                "name": p.name,
                "type": p.provider_type,
                "model": p.model,
                "priority": p.priority,
                "status": p.status.value,
                "total_requests": p.total_requests,
                "successful_requests": p.successful_requests,
                "consecutive_failures": p.consecutive_failures,
                "last_success": p.last_success_time,
                "last_failure": p.last_failure_time
            }
            for p in self.config.providers
        ]


# ============================================================================
# Configuration Loaders
# ============================================================================


def load_failover_config_from_env() -> FailoverConfig:
    """
    Load failover configuration from environment variables.

    Environment Variables:
        ARIFOS_FAILOVER_ENABLED: "true" to enable failover
        ARIFOS_FAILOVER_PROVIDERS: Comma-separated provider names

        Per provider (example for "claude_primary"):
        ARIFOS_FAILOVER_CLAUDE_PRIMARY_TYPE: Provider type (claude/openai/gemini/sealion)
        ARIFOS_FAILOVER_CLAUDE_PRIMARY_MODEL: Model ID
        ARIFOS_FAILOVER_CLAUDE_PRIMARY_API_KEY: API key
        ARIFOS_FAILOVER_CLAUDE_PRIMARY_API_BASE: Optional API base URL
        ARIFOS_FAILOVER_CLAUDE_PRIMARY_PRIORITY: Priority (0=primary)

    Returns:
        FailoverConfig with providers loaded from environment

    Raises:
        ValueError: If configuration is invalid or missing required fields
    """
    enabled = os.getenv("ARIFOS_FAILOVER_ENABLED", "").lower() == "true"
    if not enabled:
        raise ValueError("ARIFOS_FAILOVER_ENABLED not set to 'true'")

    # Get provider names
    provider_names_str = os.getenv("ARIFOS_FAILOVER_PROVIDERS", "")
    if not provider_names_str:
        raise ValueError("ARIFOS_FAILOVER_PROVIDERS not set")

    provider_names = [name.strip() for name in provider_names_str.split(",")]

    # Load each provider
    providers: List[ProviderConfig] = []

    for provider_name in provider_names:
        # Build env var prefix
        prefix = f"ARIFOS_FAILOVER_{provider_name.upper()}"

        # Load required fields
        provider_type = os.getenv(f"{prefix}_TYPE")
        model = os.getenv(f"{prefix}_MODEL")
        api_key = os.getenv(f"{prefix}_API_KEY")

        if not all([provider_type, model, api_key]):
            raise ValueError(
                f"Missing required config for provider {provider_name}: "
                f"TYPE={provider_type}, MODEL={model}, API_KEY={'set' if api_key else 'missing'}"
            )

        # Load optional fields
        api_base = os.getenv(f"{prefix}_API_BASE")
        priority = int(os.getenv(f"{prefix}_PRIORITY", "0"))
        timeout = float(os.getenv(f"{prefix}_TIMEOUT", "30.0"))
        max_retries = int(os.getenv(f"{prefix}_MAX_RETRIES", "2"))

        provider = ProviderConfig(
            name=provider_name,
            provider_type=provider_type,
            model=model,
            api_key=api_key,
            api_base=api_base,
            priority=priority,
            timeout_seconds=timeout,
            max_retries=max_retries
        )

        providers.append(provider)

    # Load global failover settings
    max_failures = int(os.getenv("ARIFOS_FAILOVER_MAX_CONSECUTIVE_FAILURES", "3"))
    circuit_duration = float(os.getenv("ARIFOS_FAILOVER_CIRCUIT_OPEN_DURATION", "60.0"))

    return FailoverConfig(
        providers=providers,
        max_consecutive_failures=max_failures,
        circuit_open_duration=circuit_duration
    )


def create_governed_failover_backend(
    config: FailoverConfig,
    ledger_sink: Optional[Callable[[dict], None]] = None
) -> Callable[[str, str], Tuple[str, Dict[str, Any]]]:
    """
    Create governed failover backend function.

    Args:
        config: Failover configuration
        ledger_sink: Optional cooling ledger sink function

    Returns:
        Function with signature: (prompt, lane) -> (response, metadata)

        This function signature matches the governed SEA-LION adapter and
        integrates seamlessly with pipeline stage 333_REASON.
    """
    orchestrator = FailoverOrchestrator(config, ledger_sink)

    def generate(prompt: str, lane: str = "UNKNOWN") -> Tuple[str, Dict[str, Any]]:
        """
        Generate with failover.

        Args:
            prompt: Input prompt
            lane: Applicability lane (PHATIC/SOFT/HARD/REFUSE)

        Returns:
            (response, metadata) tuple
        """
        return orchestrator.generate(prompt, lane)

    return generate


# ============================================================================
# CLI Status Command (for debugging)
# ============================================================================


def print_provider_status(config: FailoverConfig) -> None:
    """Print current status of all providers (for debugging)."""
    orchestrator = FailoverOrchestrator(config)
    status = orchestrator.get_provider_status()

    print("\n[FAILOVER STATUS]")
    print(f"Total Providers: {len(status)}\n")

    for p in status:
        print(f"Provider: {p['name']}")
        print(f"  Type: {p['type']}")
        print(f"  Model: {p['model']}")
        print(f"  Priority: {p['priority']}")
        print(f"  Status: {p['status']}")
        print(f"  Total Requests: {p['total_requests']}")
        print(f"  Successful: {p['successful_requests']}")
        print(f"  Consecutive Failures: {p['consecutive_failures']}")
        print()


if __name__ == "__main__":
    # CLI status command
    import sys

    if "--status" in sys.argv:
        try:
            config = load_failover_config_from_env()
            print_provider_status(config)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    else:
        print("Usage: python -m arifos_core.connectors.failover_orchestrator --status")
        sys.exit(1)
