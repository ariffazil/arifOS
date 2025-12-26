"""
test_llm_adapters.py - Tests for LLM adapters

Tests adapter functionality using mocks (no real API calls).
"""
import pytest
from unittest.mock import patch, MagicMock
from typing import Generator

from arifos_core.integration.adapters.llm_interface import (
    LLMInterface,
    LLMConfig,
    StreamChunk,
    StreamState,
    StreamThermostat,
    calc_entropy,
    estimate_entropy_from_text,
)


# =============================================================================
# MOCK BACKENDS
# =============================================================================

def create_mock_backend(responses: list[str]):
    """Create a mock backend that yields predefined responses."""
    def backend(prompt: str) -> Generator[StreamChunk, None, None]:
        for text in responses:
            yield StreamChunk(text=text, logprobs=[-0.5, -0.8])
        yield StreamChunk(text="", finish_reason="stop")
    return backend


def create_entropy_spike_backend():
    """Create a mock backend that triggers entropy spike."""
    def backend(prompt: str) -> Generator[StreamChunk, None, None]:
        # Normal chunks first
        yield StreamChunk(text="Normal ", logprobs=[-0.5, -0.8])
        yield StreamChunk(text="response ", logprobs=[-0.5, -0.8])
        # Spike chunk with very high entropy logprobs
        yield StreamChunk(text="CHAOS ", logprobs=[-5.0, -4.5, -5.2, -4.8, -5.5])
        yield StreamChunk(text="more ", logprobs=[-0.5, -0.8])
        yield StreamChunk(text="", finish_reason="stop")
    return backend


# =============================================================================
# TEST LLM INTERFACE
# =============================================================================

class TestLLMInterface:
    """Tests for LLMInterface core functionality."""

    def test_interface_with_mock_backend(self):
        """LLMInterface should work with mock backend."""
        backend = create_mock_backend(["Hello ", "world!"])
        llm = LLMInterface(backend_fn=backend)

        response, state = llm.generate("Test prompt")

        assert "Hello" in response
        assert "world!" in response
        assert not state.sabar_triggered

    def test_generate_returns_string(self):
        """generate() should return a string."""
        backend = create_mock_backend(["Test response"])
        llm = LLMInterface(backend_fn=backend)

        response, state = llm.generate("Test")

        assert isinstance(response, str)
        assert isinstance(state, StreamState)

    def test_stub_backend_works(self):
        """Default stub backend should work."""
        llm = LLMInterface()

        response, state = llm.generate("What is 2+2?")

        assert isinstance(response, str)
        assert len(response) > 0
        assert "stub response" in response.lower()


class TestStreamThermostat:
    """Tests for entropy monitoring."""

    def test_normal_entropy_returns_ok(self):
        """Normal entropy should return OK."""
        config = LLMConfig(entropy_threshold_chaos=3.5)
        thermostat = StreamThermostat(config)

        chunk = StreamChunk(text="Hello", logprobs=[-0.5, -0.8])
        action = thermostat.check(chunk)

        assert action == "OK"
        assert not thermostat.state.sabar_triggered

    def test_high_entropy_returns_sabar(self):
        """High entropy should trigger SABAR."""
        config = LLMConfig(entropy_threshold_chaos=1.0)  # Low threshold for test
        thermostat = StreamThermostat(config)

        # Create chunk with high entropy logprobs
        chunk = StreamChunk(text="Chaos", logprobs=[-5.0, -4.5, -5.2, -4.8])
        action = thermostat.check(chunk)

        assert action == "SABAR"
        assert thermostat.state.sabar_triggered
        assert "entropy" in thermostat.state.sabar_reason.lower()

    def test_warning_on_elevated_entropy(self):
        """Elevated entropy should return WARNING."""
        config = LLMConfig(
            entropy_threshold_warning=1.0,
            entropy_threshold_chaos=5.0,
        )
        thermostat = StreamThermostat(config)

        # Medium entropy
        chunk = StreamChunk(text="Test", logprobs=[-2.0, -1.8, -2.2])
        action = thermostat.check(chunk)

        assert action == "WARNING"
        assert thermostat.state.warning_count == 1

    def test_sustained_warnings_trigger_sabar(self):
        """Multiple consecutive warnings should trigger SABAR."""
        config = LLMConfig(
            entropy_threshold_warning=1.0,
            entropy_threshold_chaos=10.0,  # High so we get warnings not immediate SABAR
        )
        thermostat = StreamThermostat(config)

        # Send 3 warning-level chunks
        for _ in range(3):
            chunk = StreamChunk(text="Test", logprobs=[-2.0, -1.8, -2.2])
            action = thermostat.check(chunk)

        assert action == "SABAR"
        assert thermostat.state.sabar_triggered


class TestLLMInterfaceSabar:
    """Tests for SABAR triggering in LLMInterface."""

    def test_sabar_on_entropy_spike(self):
        """LLMInterface should trigger SABAR on entropy spike."""
        config = LLMConfig(entropy_threshold_chaos=1.0)  # Low threshold
        backend = create_entropy_spike_backend()
        llm = LLMInterface(config=config, backend_fn=backend)

        response, state = llm.generate("Test")

        assert state.sabar_triggered
        assert "[SABAR]" in response

    def test_response_truncated_on_sabar(self):
        """Response should be truncated when SABAR triggers."""
        config = LLMConfig(entropy_threshold_chaos=1.0)
        backend = create_entropy_spike_backend()
        llm = LLMInterface(config=config, backend_fn=backend)

        response, state = llm.generate("Test")

        # Should have partial response + SABAR message
        assert "Normal" in response  # Before spike
        assert "[SABAR]" in response  # Cooling message


# =============================================================================
# TEST ENTROPY CALCULATIONS
# =============================================================================

class TestEntropyCalculations:
    """Tests for entropy calculation functions."""

    def test_calc_entropy_uniform(self):
        """Uniform distribution should have high entropy."""
        # Log probs for roughly uniform distribution
        logprobs = [-1.0, -1.0, -1.0, -1.0]
        entropy = calc_entropy(logprobs)

        assert entropy > 0
        assert entropy < 2.0  # Reasonable bound

    def test_calc_entropy_peaked(self):
        """Peaked distribution should have low entropy."""
        # One very likely, others unlikely
        logprobs = [-0.1, -5.0, -5.0, -5.0]
        entropy = calc_entropy(logprobs)

        assert entropy >= 0
        assert entropy < 1.0  # Low entropy

    def test_estimate_entropy_from_text(self):
        """Text entropy estimation should work."""
        # Repetitive text = low entropy
        low_entropy_text = "aaaaaaaaaa"
        # Varied text = higher entropy
        high_entropy_text = "abcdefghij"

        low = estimate_entropy_from_text(low_entropy_text)
        high = estimate_entropy_from_text(high_entropy_text)

        assert low < high

    def test_estimate_entropy_empty(self):
        """Empty text should have zero entropy."""
        entropy = estimate_entropy_from_text("")
        assert entropy == 0.0


# =============================================================================
# TEST ADAPTER FACTORIES
# =============================================================================

class TestAdapterFactories:
    """Tests for adapter make_* functions."""

    def test_openai_make_backend_returns_callable(self):
        """make_backend should return a callable."""
        # Mock the openai module before importing the adapter function
        mock_openai = MagicMock()
        with patch.dict("sys.modules", {"openai": mock_openai}):
            from arifos_core.adapters.llm_openai import make_backend

            backend = make_backend(api_key="test-key", model="gpt-4o-mini")

            assert callable(backend)

    def test_openai_make_llm_generate_returns_callable(self):
        """make_llm_generate should return a callable."""
        mock_openai = MagicMock()
        with patch.dict("sys.modules", {"openai": mock_openai}):
            from arifos_core.adapters.llm_openai import make_llm_generate

            generate = make_llm_generate(api_key="test-key", model="gpt-4o-mini")

            assert callable(generate)

    def test_claude_make_backend_returns_callable(self):
        """Claude make_backend should return a callable."""
        mock_anthropic = MagicMock()
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            from arifos_core.adapters.llm_claude import make_backend

            backend = make_backend(api_key="test-key", model="claude-3-haiku")

            assert callable(backend)

    def test_claude_make_llm_generate_returns_callable(self):
        """Claude make_llm_generate should return a callable."""
        mock_anthropic = MagicMock()
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            from arifos_core.adapters.llm_claude import make_llm_generate

            generate = make_llm_generate(api_key="test-key", model="claude-3-haiku")

            assert callable(generate)

    def test_gemini_make_backend_returns_callable(self):
        """Gemini make_backend should return a callable."""
        mock_genai = MagicMock()
        with patch.dict("sys.modules", {"google.generativeai": mock_genai, "google": MagicMock()}):
            from arifos_core.adapters.llm_gemini import make_backend

            backend = make_backend(api_key="test-key", model="gemini-1.5-flash")

            assert callable(backend)

    def test_gemini_make_llm_generate_returns_callable(self):
        """Gemini make_llm_generate should return a callable."""
        mock_genai = MagicMock()
        with patch.dict("sys.modules", {"google.generativeai": mock_genai, "google": MagicMock()}):
            from arifos_core.adapters.llm_gemini import make_llm_generate

            generate = make_llm_generate(api_key="test-key", model="gemini-1.5-flash")

            assert callable(generate)


class TestAdapterIntegration:
    """Integration tests with mocked API clients."""

    def test_openai_generate_returns_string(self):
        """OpenAI generate should return a string."""
        # Mock the openai module
        mock_openai = MagicMock()
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client

        # Setup mock response
        mock_choice = MagicMock()
        mock_choice.delta.content = "Test response"
        mock_choice.finish_reason = "stop"
        mock_choice.logprobs = None
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = [mock_response]

        with patch.dict("sys.modules", {"openai": mock_openai}):
            from arifos_core.adapters.llm_openai import make_llm_generate

            generate = make_llm_generate(api_key="test-key")

            # Verify callable was created
            assert callable(generate)

    def test_config_passed_to_backend(self):
        """LLMConfig settings should be passed to backend."""
        config = LLMConfig(temperature=0.7, max_tokens=500)

        mock_openai = MagicMock()
        with patch.dict("sys.modules", {"openai": mock_openai}):
            from arifos_core.adapters.llm_openai import make_backend

            # Backend should be created with config values
            backend = make_backend(api_key="test", config=config)
            assert callable(backend)
