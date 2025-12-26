"""
llm_claude.py - Anthropic Claude Adapter for arifOS v35Ω

Provides Claude model integration with entropy monitoring.

Note: Claude doesn't expose logprobs, so we use text-based entropy estimation.

Usage:
    from arifos_core.adapters.llm_claude import make_llm_generate

    generate = make_llm_generate(api_key="sk-ant-...", model="claude-3-haiku-20240307")
    response = generate("What is the capital of France?")

Note: This adapter supplies RAW intelligence only.
Apply @apex_guardrail at call sites for constitutional governance.
"""
from __future__ import annotations

from typing import Callable, Generator, Optional

from ..integration.adapters.llm_interface import (
    LLMConfig,
    LLMInterface,
    StreamChunk,
    estimate_entropy_from_text,
)


def create_claude_backend(
    api_key: str,
    model: str = "claude-3-haiku-20240307",
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> Callable[[str], Generator[StreamChunk, None, None]]:
    """
    Create an Anthropic Claude streaming backend.

    Args:
        api_key: Anthropic API key
        model: Model ID (claude-3-haiku, claude-3-sonnet, claude-3-opus, etc.)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Backend function that yields StreamChunks

    Note:
        Claude doesn't expose logprobs, so entropy is estimated from text.
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "anthropic package required: pip install anthropic"
        )

    client = anthropic.Anthropic(api_key=api_key)

    def stream_fn(prompt: str) -> Generator[StreamChunk, None, None]:
        try:
            with client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    # Estimate entropy from text since Claude doesn't expose logprobs
                    entropy = estimate_entropy_from_text(text)
                    yield StreamChunk(
                        text=text,
                        entropy=entropy,
                    )

            yield StreamChunk(text="", finish_reason="stop")

        except anthropic.APIError as e:
            yield StreamChunk(
                text=f"\n[ERROR] Anthropic API error: {str(e)}",
                finish_reason="error",
            )
        except Exception as e:
            yield StreamChunk(
                text=f"\n[ERROR] Claude adapter error: {str(e)}",
                finish_reason="error",
            )

    return stream_fn


def make_backend(
    api_key: str,
    model: str = "claude-3-haiku-20240307",
    config: Optional[LLMConfig] = None,
) -> Callable[[str], Generator[StreamChunk, None, None]]:
    """
    Create a Claude streaming backend with config.

    Args:
        api_key: Anthropic API key
        model: Model ID
        config: Optional LLMConfig for temperature/max_tokens

    Returns:
        Backend function for LLMInterface
    """
    cfg = config or LLMConfig()
    return create_claude_backend(
        api_key=api_key,
        model=model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )


def make_llm_generate(
    api_key: str,
    model: str = "claude-3-haiku-20240307",
    config: Optional[LLMConfig] = None,
) -> Callable[[str], str]:
    """
    Create a simple generate function using Claude.

    This wraps the streaming backend with LLMInterface for
    entropy monitoring and SABAR triggers.

    Args:
        api_key: Anthropic API key
        model: Model ID
        config: Optional LLMConfig

    Returns:
        Function that takes prompt and returns response text

    Example:
        generate = make_llm_generate("sk-ant-...", "claude-3-haiku-20240307")
        response = generate("What is 2+2?")
    """
    cfg = config or LLMConfig()
    backend = make_backend(api_key, model, cfg)

    llm = LLMInterface(config=cfg, backend_fn=backend)

    def generate(prompt: str) -> str:
        response, state = llm.generate(prompt)
        return response

    return generate


__all__ = [
    "create_claude_backend",
    "make_backend",
    "make_llm_generate",
]
