"""
llm_interface.py - LLM Interface with Thermodynamic Stream Gating for arifOS v35Ω

Provides:
- generate_stream(): Yields token chunks with optional logprobs
- Entropy monitoring with SABAR trigger on chaos detection
- Pluggable backends (stub, OpenAI, Anthropic, local)

Thermodynamic invariant: If entropy exceeds threshold, halt and cool.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Callable, Generator, List, Optional, Tuple

import numpy as np


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class LLMConfig:
    """Configuration for LLM interface."""
    # Entropy thresholds
    entropy_threshold_warning: float = 2.5  # H > this → yellow flag
    entropy_threshold_chaos: float = 3.5    # H > this → SABAR trigger

    # Stream settings
    max_tokens: int = 1024
    temperature: float = 0.3

    # Backend
    backend: str = "stub"  # "stub", "openai", "anthropic", "local"
    model_id: Optional[str] = None

    # Cooling
    cooling_pause_ms: int = 100  # Pause between chunks when cooling


@dataclass
class StreamChunk:
    """A chunk from the LLM stream."""
    text: str
    logprobs: Optional[List[float]] = None
    entropy: Optional[float] = None
    token_ids: Optional[List[int]] = None
    finish_reason: Optional[str] = None


@dataclass
class StreamState:
    """State accumulated during streaming."""
    chunks: List[StreamChunk] = field(default_factory=list)
    total_text: str = ""
    entropy_history: List[float] = field(default_factory=list)
    sabar_triggered: bool = False
    sabar_reason: Optional[str] = None
    warning_count: int = 0
    start_time: float = field(default_factory=time.time)


# =============================================================================
# ENTROPY CALCULATION
# =============================================================================

def calc_entropy(logprobs: List[float]) -> float:
    """
    Calculate Shannon entropy from log probabilities.

    H = -Σ p(x) * log(p(x))

    Args:
        logprobs: List of log probabilities (natural log)

    Returns:
        Entropy in nats (convert to bits by dividing by ln(2))
    """
    if not logprobs:
        return 0.0

    # Convert logprobs to probabilities
    probs = np.exp(logprobs)

    # Normalize if needed
    prob_sum = np.sum(probs)
    if prob_sum > 0:
        probs = probs / prob_sum

    # Calculate entropy
    entropy = 0.0
    for p in probs:
        if p > 0:
            entropy -= p * np.log(p)

    return float(entropy)


def estimate_entropy_from_text(text: str) -> float:
    """
    Estimate entropy from text using character frequency.
    Fallback when logprobs not available.

    Returns entropy in bits.
    """
    if not text:
        return 0.0

    # Character frequency
    freq = {}
    for c in text.lower():
        freq[c] = freq.get(c, 0) + 1

    total = len(text)
    entropy = 0.0
    for count in freq.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)

    return entropy


# =============================================================================
# STREAM THERMOSTAT
# =============================================================================

class StreamThermostat:
    """
    Monitors entropy during streaming and triggers SABAR on chaos.

    Usage:
        thermostat = StreamThermostat(config)
        for chunk in stream:
            action = thermostat.check(chunk)
            if action == "SABAR":
                break
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.state = StreamState()

    def reset(self) -> None:
        """Reset state for new stream."""
        self.state = StreamState()

    def check(self, chunk: StreamChunk) -> str:
        """
        Check a chunk and return action.

        Returns:
            "OK" - Continue streaming
            "WARNING" - Entropy elevated, proceed with caution
            "SABAR" - Entropy too high, halt streaming
        """
        self.state.chunks.append(chunk)
        self.state.total_text += chunk.text

        # Calculate entropy
        if chunk.logprobs:
            entropy = calc_entropy(chunk.logprobs)
        elif chunk.entropy is not None:
            entropy = chunk.entropy
        else:
            entropy = estimate_entropy_from_text(chunk.text)

        chunk.entropy = entropy
        self.state.entropy_history.append(entropy)

        # Check thresholds
        if entropy > self.config.entropy_threshold_chaos:
            self.state.sabar_triggered = True
            self.state.sabar_reason = f"Entropy spike: {entropy:.2f} > {self.config.entropy_threshold_chaos}"
            return "SABAR"

        if entropy > self.config.entropy_threshold_warning:
            self.state.warning_count += 1
            # Multiple warnings in a row → escalate
            if self.state.warning_count >= 3:
                self.state.sabar_triggered = True
                self.state.sabar_reason = f"Sustained high entropy: {self.state.warning_count} warnings"
                return "SABAR"
            return "WARNING"

        # Reset warning count on good chunk
        self.state.warning_count = 0
        return "OK"

    def get_average_entropy(self) -> float:
        """Get average entropy across stream."""
        if not self.state.entropy_history:
            return 0.0
        return float(np.mean(self.state.entropy_history))

    def get_max_entropy(self) -> float:
        """Get maximum entropy seen."""
        if not self.state.entropy_history:
            return 0.0
        return float(max(self.state.entropy_history))


# =============================================================================
# LLM INTERFACE
# =============================================================================

class LLMInterface:
    """
    Thermodynamically-gated LLM interface.

    Wraps any LLM backend with entropy monitoring and SABAR triggers.

    Usage:
        llm = LLMInterface()
        result = llm.generate("What is 2+2?")
        # or
        for chunk in llm.generate_stream("Tell me a story"):
            print(chunk.text, end="")
    """

    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        backend_fn: Optional[Callable[[str], Generator[StreamChunk, None, None]]] = None,
    ):
        """
        Initialize LLM interface.

        Args:
            config: LLM configuration
            backend_fn: Custom backend function that yields StreamChunks
        """
        self.config = config or LLMConfig()
        self.thermostat = StreamThermostat(self.config)
        self._backend_fn = backend_fn

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, StreamState]:
        """
        Generate response with entropy monitoring.

        Args:
            prompt: Input prompt
            max_tokens: Override max tokens

        Returns:
            Tuple of (response_text, stream_state)
        """
        self.thermostat.reset()
        response_parts = []

        for chunk in self.generate_stream(prompt, max_tokens):
            response_parts.append(chunk.text)
            if self.thermostat.state.sabar_triggered:
                break

        return "".join(response_parts), self.thermostat.state

    def generate_stream(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
    ) -> Generator[StreamChunk, None, None]:
        """
        Generate response as a stream with entropy monitoring.

        Yields StreamChunks. If entropy spikes, triggers SABAR and stops.

        Args:
            prompt: Input prompt
            max_tokens: Override max tokens

        Yields:
            StreamChunk objects
        """
        self.thermostat.reset()
        max_tokens = max_tokens or self.config.max_tokens

        # Get backend generator
        if self._backend_fn:
            backend = self._backend_fn(prompt)
        else:
            backend = self._stub_backend(prompt, max_tokens)

        for chunk in backend:
            # Check entropy
            action = self.thermostat.check(chunk)

            if action == "SABAR":
                # Yield a cooling response
                yield StreamChunk(
                    text="\n\n[SABAR] Entropy spike detected. Cooling response.",
                    finish_reason="sabar",
                )
                return

            yield chunk

            if chunk.finish_reason == "stop":
                return

    def _stub_backend(
        self,
        prompt: str,
        max_tokens: int,
    ) -> Generator[StreamChunk, None, None]:
        """
        Stub backend for testing - echoes prompt in chunks.
        """
        # Simulate a response
        response = f"This is a stub response to: {prompt[:50]}..."

        # Yield in chunks
        words = response.split()
        for i, word in enumerate(words):
            # Simulate varying entropy
            fake_logprobs = [-0.5, -1.0, -0.8]  # Low entropy
            if "spike" in prompt.lower() and i == len(words) // 2:
                # Simulate entropy spike for testing
                fake_logprobs = [-5.0, -4.5, -4.8, -5.2]  # High entropy

            yield StreamChunk(
                text=word + " ",
                logprobs=fake_logprobs,
            )
            time.sleep(0.01)  # Simulate latency

        yield StreamChunk(text="", finish_reason="stop")


# =============================================================================
# BACKEND ADAPTERS
# =============================================================================

def create_openai_backend(
    api_key: str,
    model: str = "gpt-4o-mini",
) -> Callable[[str], Generator[StreamChunk, None, None]]:
    """
    Create an OpenAI streaming backend.

    Usage:
        backend = create_openai_backend(api_key)
        llm = LLMInterface(backend_fn=backend)
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package required: pip install openai")

    client = OpenAI(api_key=api_key)

    def stream_fn(prompt: str) -> Generator[StreamChunk, None, None]:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            logprobs=True,
            top_logprobs=5,
        )

        for chunk in response:
            delta = chunk.choices[0].delta
            content = delta.content or ""

            logprobs = None
            if chunk.choices[0].logprobs and chunk.choices[0].logprobs.content:
                logprobs = [
                    lp.logprob for lp in chunk.choices[0].logprobs.content
                ]

            yield StreamChunk(
                text=content,
                logprobs=logprobs,
                finish_reason=chunk.choices[0].finish_reason,
            )

    return stream_fn


def create_anthropic_backend(
    api_key: str,
    model: str = "claude-3-haiku-20240307",
) -> Callable[[str], Generator[StreamChunk, None, None]]:
    """
    Create an Anthropic streaming backend.

    Note: Anthropic doesn't expose logprobs, so we estimate entropy from text.
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package required: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)

    def stream_fn(prompt: str) -> Generator[StreamChunk, None, None]:
        with client.messages.stream(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                # Estimate entropy from text since Anthropic doesn't expose logprobs
                entropy = estimate_entropy_from_text(text)
                yield StreamChunk(
                    text=text,
                    entropy=entropy,
                )

        yield StreamChunk(text="", finish_reason="stop")

    return stream_fn


def create_gemini_backend(
    api_key: str,
    model: str = "gemini-1.5-flash",
) -> Callable[[str], Generator[StreamChunk, None, None]]:
    """
    Create a Google Gemini streaming backend.

    Note: Gemini doesn't expose logprobs, so we estimate entropy from text.

    Usage:
        backend = create_gemini_backend(api_key)
        llm = LLMInterface(backend_fn=backend)
    """
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError(
            "google-generativeai package required: pip install google-generativeai"
        )

    genai.configure(api_key=api_key)

    def stream_fn(prompt: str) -> Generator[StreamChunk, None, None]:
        try:
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(prompt, stream=True)

            for chunk in response:
                # Extract text from chunk
                text = getattr(chunk, "text", "") or ""
                if not text and hasattr(chunk, "parts"):
                    # Some Gemini responses use parts
                    text = "".join(
                        getattr(p, "text", "") for p in chunk.parts
                    )

                # Estimate entropy from text
                entropy = estimate_entropy_from_text(text)

                yield StreamChunk(
                    text=text,
                    entropy=entropy,
                )

            yield StreamChunk(text="", finish_reason="stop")

        except Exception as e:
            yield StreamChunk(
                text=f"\n[ERROR] Gemini API error: {str(e)}",
                finish_reason="error",
            )

    return stream_fn


# =============================================================================
# CONVENIENCE
# =============================================================================

def quick_generate(prompt: str, config: Optional[LLMConfig] = None) -> str:
    """Quick generation with default settings."""
    llm = LLMInterface(config=config)
    response, _ = llm.generate(prompt)
    return response


__all__ = [
    "LLMInterface",
    "LLMConfig",
    "StreamChunk",
    "StreamState",
    "StreamThermostat",
    "calc_entropy",
    "estimate_entropy_from_text",
    "create_openai_backend",
    "create_anthropic_backend",
    "create_gemini_backend",
    "quick_generate",
]
