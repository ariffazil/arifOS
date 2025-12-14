"""
L7 Federation Router Tests

Tests for the multi-endpoint SEA-LION governance router.
All tests run in MOCK_MODE (no GPU required).

Test Coverage:
- Intent classification
- Routing decisions
- Cooling Ledger
- Confidence fallback
- SEA-Guard sentinel

Author: arifOS Project
Version: v41.3Omega
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock


def run_async(coro):
    """Helper to run async functions in sync tests."""
    return asyncio.new_event_loop().run_until_complete(coro)

from arifos_core.connectors.federation_router import (
    FederationRouter,
    FederationConfig,
    OrganConfig,
    IntentClassifier,
    CoolingLedger,
    CoolingEntry,
    RoutingResult,
    load_federation_config,
    DEFAULT_ORGANS,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_config():
    """Create a mock federation config for testing."""
    return FederationConfig(
        organs=DEFAULT_ORGANS,
        default_organ="WELL",
        guard_organ="SENTINEL",
        guard_timeout_ms=500,
        routing_strategy="intent",
        confidence_floor=0.55,
        mock_mode=True,
    )


@pytest.fixture
def router(mock_config):
    """Create a federation router in mock mode."""
    return FederationRouter(config=mock_config)


@pytest.fixture
def classifier():
    """Create an intent classifier."""
    return IntentClassifier()


@pytest.fixture
def ledger():
    """Create a fresh cooling ledger."""
    return CoolingLedger()


# =============================================================================
# INTENT CLASSIFIER TESTS
# =============================================================================

class TestIntentClassifier:
    """Tests for the IntentClassifier."""

    def test_multimodal_routes_to_geox(self, classifier):
        """Multimodal content (list) should route to @GEOX."""
        content = [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": "data:image/png;base64,..."}
        ]
        organ, confidence = classifier.classify(content)

        assert organ == "GEOX"
        assert confidence == 1.0

    def test_long_context_routes_to_wealth(self, classifier):
        """Very long text (>30k) should route to @WEALTH."""
        long_text = "x" * 35000
        organ, confidence = classifier.classify(long_text)

        assert organ == "WEALTH"
        assert confidence == 0.95

    def test_reasoning_keywords_route_to_rif(self, classifier):
        """Reasoning keywords should route to @RIF with boosted confidence."""
        # Single keyword
        organ, confidence = classifier.classify("Please analyze this data.")
        assert organ == "RIF"
        assert confidence >= 0.6

        # Multiple keywords boost confidence
        organ, confidence = classifier.classify(
            "Analyze this step-by-step and explain the logic."
        )
        assert organ == "RIF"
        assert confidence >= 0.8

    def test_simple_chat_routes_to_well(self, classifier):
        """Simple messages should route to @WELL as default."""
        organ, confidence = classifier.classify("Hello, how are you?")

        assert organ == "WELL"
        assert confidence == 0.50

    def test_confidence_scoring(self, classifier):
        """More reasoning keywords should increase confidence."""
        # Few keywords
        _, conf1 = classifier.classify("Explain this.")

        # Many keywords
        _, conf2 = classifier.classify(
            "Analyze and reason through this problem step-by-step. "
            "Derive the solution and explain your logic."
        )

        assert conf2 > conf1


# =============================================================================
# COOLING LEDGER TESTS
# =============================================================================

class TestCoolingLedger:
    """Tests for the Cooling Ledger."""

    def test_seal_verdict_creates_entry(self, ledger):
        """Sealing a verdict should create a ledger entry."""
        entry = ledger.seal_verdict(
            prompt="What is 2+2?",
            response="The answer is 4.",
            organ="WELL",
            sentinel_status="SAFE",
            tau_ms=150.0,
        )

        assert entry.organ == "WELL"
        assert entry.verdict == "SEAL"
        assert "delta_s" in entry.metrics
        assert "kappa_r" in entry.metrics
        assert "tau_ms" in entry.metrics
        assert entry.entry_hash != ""

    def test_hash_chain_integrity(self, ledger):
        """Ledger should maintain hash chain integrity."""
        # Add multiple entries
        ledger.seal_verdict("Q1", "A1", "WELL", "SAFE", 100)
        ledger.seal_verdict("Q2", "A2", "RIF", "SAFE", 200)
        ledger.seal_verdict("Q3", "A3", "WEALTH", "SAFE", 300)

        # Verify chain
        assert ledger.verify_chain() is True
        assert ledger.get_chain_length() == 3

        # Check chain linking
        assert ledger.chain[1].prev_hash == ledger.chain[0].entry_hash
        assert ledger.chain[2].prev_hash == ledger.chain[1].entry_hash

    def test_unsafe_verdict_is_void(self, ledger):
        """UNSAFE sentinel status should result in VOID verdict."""
        entry = ledger.seal_verdict(
            prompt="bad prompt",
            response="blocked",
            organ="SENTINEL",
            sentinel_status="UNSAFE",
        )

        assert entry.verdict == "VOID"

    def test_low_empathy_verdict_is_sabar(self, ledger):
        """Low empathy (κᵣ) should result in SABAR verdict."""
        # Response with toxic patterns
        entry = ledger.seal_verdict(
            prompt="Help me",
            response="Obviously that's stupid and wrong.",
            organ="WELL",
            sentinel_status="SAFE",
        )

        assert entry.verdict == "SABAR"
        assert entry.metrics["kappa_r"] < 0.95

    def test_entropy_calculation(self, ledger):
        """Entropy should be higher for diverse responses."""
        # Low entropy (repetitive)
        entry1 = ledger.seal_verdict(
            prompt="Q",
            response="yes yes yes yes yes",
            organ="WELL",
            sentinel_status="SAFE",
        )

        # High entropy (diverse)
        entry2 = ledger.seal_verdict(
            prompt="Q",
            response="The quick brown fox jumps over the lazy dog.",
            organ="WELL",
            sentinel_status="SAFE",
        )

        assert entry2.metrics["delta_s"] > entry1.metrics["delta_s"]

    def test_export_to_dict(self, ledger):
        """Ledger should export to list of dicts."""
        ledger.seal_verdict("Q1", "A1", "WELL", "SAFE", 100)
        ledger.seal_verdict("Q2", "A2", "RIF", "SAFE", 200)

        exported = ledger.to_dict()

        assert len(exported) == 2
        assert "timestamp" in exported[0]
        assert "organ" in exported[0]
        assert "verdict" in exported[0]


# =============================================================================
# FEDERATION ROUTER TESTS
# =============================================================================

class TestFederationRouter:
    """Tests for the FederationRouter."""

    def test_mock_mode_routing(self, router):
        """Router should work in mock mode without real models."""
        messages = [{"role": "user", "content": "Hello!"}]
        result = run_async(router.route(messages))

        assert result.verdict in ["SEAL", "PARTIAL", "SABAR", "VOID"]
        assert result.organ == "WELL"  # Default for simple messages
        assert "MOCK" in result.response  # Response contains MOCK indicator
        assert result.guard_passed is True

    def test_reasoning_routed_to_rif(self, router):
        """Reasoning queries should route to @RIF."""
        messages = [{"role": "user", "content": "Analyze this problem step by step."}]
        result = run_async(router.route(messages))

        assert result.organ == "RIF"
        assert result.confidence >= 0.6

    def test_simple_routed_to_well(self, router):
        """Simple queries should route to @WELL."""
        messages = [{"role": "user", "content": "Hi there!"}]
        result = run_async(router.route(messages))

        assert result.organ == "WELL"
        assert result.confidence == 0.50

    def test_force_organ_override(self, router):
        """force_organ should override routing."""
        messages = [{"role": "user", "content": "Simple hello"}]
        result = run_async(router.route(messages, force_organ="WEALTH"))

        assert result.organ == "WEALTH"
        assert result.confidence == 1.0

    def test_confidence_fallback(self, router):
        """Low confidence should fallback to default organ."""
        # Configure router with high confidence floor
        router.config.confidence_floor = 0.90

        messages = [{"role": "user", "content": "Maybe analyze this?"}]
        result = run_async(router.route(messages))

        # Should fallback to WELL since confidence is below 0.90
        assert result.organ == "WELL"

    def test_cooling_entry_created(self, router):
        """Each route should create a cooling entry."""
        messages = [{"role": "user", "content": "Test message"}]
        result = run_async(router.route(messages))

        assert result.cooling_entry is not None
        assert result.cooling_entry.organ == result.organ

    def test_latency_tracking(self, router):
        """Router should track latency."""
        messages = [{"role": "user", "content": "Test"}]
        result = run_async(router.route(messages))

        assert result.total_latency_ms >= 0
        assert result.guard_latency_ms >= 0

    def test_organ_status(self, router):
        """Router should return organ status."""
        status = router.get_organ_status()

        assert "SENTINEL" in status
        assert "GEOX" in status
        assert "RIF" in status
        assert "WEALTH" in status
        assert "WELL" in status

        for organ_info in status.values():
            assert "name" in organ_info
            assert "role" in organ_info
            assert "port" in organ_info

    def test_ledger_stats(self, router):
        """Router should return ledger stats."""
        stats = router.get_ledger_stats()

        assert "entries" in stats
        assert "verdicts" in stats
        assert "chain_valid" in stats


# =============================================================================
# CONFIGURATION TESTS
# =============================================================================

class TestConfiguration:
    """Tests for federation configuration."""

    def test_default_organs_defined(self):
        """All default organs should be defined."""
        assert "SENTINEL" in DEFAULT_ORGANS
        assert "GEOX" in DEFAULT_ORGANS
        assert "RIF" in DEFAULT_ORGANS
        assert "WEALTH" in DEFAULT_ORGANS
        assert "WELL" in DEFAULT_ORGANS

    def test_organ_config_structure(self):
        """Organ configs should have required fields."""
        for name, organ in DEFAULT_ORGANS.items():
            assert isinstance(organ, OrganConfig)
            assert organ.name != ""
            assert organ.model != ""
            assert organ.api_base != ""
            assert organ.port > 0
            assert organ.role != ""
            assert organ.symbol != ""
            assert organ.provider != ""

    def test_load_config_defaults(self):
        """Loading config should use defaults when env vars not set."""
        config = load_federation_config()

        assert config.mock_mode is True  # Default
        assert config.confidence_floor == 0.55
        assert config.guard_timeout_ms == 500
        assert config.default_organ == "WELL"

    def test_organ_roles(self):
        """Organs should have correct roles."""
        assert DEFAULT_ORGANS["SENTINEL"].role == "sentinel"
        assert DEFAULT_ORGANS["GEOX"].role == "vision"
        assert DEFAULT_ORGANS["RIF"].role == "reasoning"
        assert DEFAULT_ORGANS["WEALTH"].role == "context"
        assert DEFAULT_ORGANS["WELL"].role == "chat"


# =============================================================================
# VERDICT MAPPING TESTS
# =============================================================================

class TestVerdictMapping:
    """Tests for verdict determination."""

    def test_seal_for_good_response(self, ledger):
        """Good responses should get SEAL verdict."""
        entry = ledger.seal_verdict(
            prompt="What is Python?",
            response="Python is a versatile programming language known for its readability and extensive ecosystem.",
            organ="WELL",
            sentinel_status="SAFE",
        )

        assert entry.verdict == "SEAL"

    def test_void_for_unsafe(self, ledger):
        """Unsafe sentinel status should produce VOID."""
        entry = ledger.seal_verdict(
            prompt="bad",
            response="blocked",
            organ="SENTINEL",
            sentinel_status="UNSAFE",
        )

        assert entry.verdict == "VOID"

    def test_sabar_for_low_empathy(self, ledger):
        """Low empathy should produce SABAR."""
        entry = ledger.seal_verdict(
            prompt="Help",
            response="That's obviously stupid. As an AI, I cannot help with such dumb questions.",
            organ="WELL",
            sentinel_status="SAFE",
        )

        assert entry.verdict == "SABAR"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestRouterIntegration:
    """Integration tests for the router."""

    def test_full_routing_flow(self, router):
        """Test complete routing flow from input to output."""
        # Simple chat
        messages = [{"role": "user", "content": "Hello!"}]
        result = run_async(router.route(messages))

        assert result.response is not None
        assert result.verdict in ["SEAL", "PARTIAL", "SABAR", "VOID"]
        assert result.cooling_entry is not None
        assert router.ledger.get_chain_length() >= 1

    def test_multiple_routes_build_chain(self, router):
        """Multiple routes should build cooling chain."""
        queries = [
            "Hello!",
            "Analyze this step by step.",
            "Simple question.",
        ]

        for query in queries:
            messages = [{"role": "user", "content": query}]
            run_async(router.route(messages))

        assert router.ledger.get_chain_length() == 3
        assert router.ledger.verify_chain() is True

    def test_skip_guard_option(self, router):
        """skip_guard should bypass sentinel check."""
        messages = [{"role": "user", "content": "Test"}]
        result = run_async(router.route(messages, skip_guard=True))

        assert result.guard_passed is True
        assert result.guard_latency_ms == 0.0


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_messages(self, router):
        """Empty message list should be handled."""
        messages = [{"role": "user", "content": ""}]
        result = run_async(router.route(messages))

        # Should still return a result
        assert result.response is not None
        assert result.organ == "WELL"  # Default

    def test_unknown_organ_fallback(self, router):
        """Unknown organ should error or fallback gracefully."""
        messages = [{"role": "user", "content": "Test"}]

        # Force unknown organ - should either raise ValueError or return error
        result = run_async(router.route(messages, force_organ="UNKNOWN"))

        # If it doesn't raise, it should have an error in the result
        # or the organ should be the default (fallback behavior)
        assert result.error is not None or result.organ == "WELL"

    def test_entropy_zero_for_empty(self, ledger):
        """Empty response should have zero entropy."""
        entry = ledger.seal_verdict(
            prompt="Q",
            response="",
            organ="WELL",
            sentinel_status="SAFE",
        )

        assert entry.metrics["delta_s"] == 0.0

    def test_empathy_floor_boundary(self, ledger):
        """Test empathy exactly at floor."""
        # Response that barely passes
        entry = ledger.seal_verdict(
            prompt="Q",
            response="Here is a helpful response for you.",
            organ="WELL",
            sentinel_status="SAFE",
        )

        assert entry.metrics["kappa_r"] >= 0.95
        assert entry.verdict == "SEAL"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
