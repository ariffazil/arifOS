"""
llm_openai.py - OpenAI Adapter for arifOS v35Ω

Provides OpenAI GPT model integration with entropy monitoring.

Usage:
    from arifos_core.adapters.llm_openai import make_llm_generate

    generate = make_llm_generate(api_key="sk-...", model="gpt-4o-mini")
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
    calc_entropy,
)


def create_openai_backend(
    api_key: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> Callable[[str], Generator[StreamChunk, None, None]]:
    """
    Create an OpenAI streaming backend.

    Args:
        api_key: OpenAI API key
        model: Model ID (gpt-4o-mini, gpt-4o, etc.)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Backend function that yields StreamChunks
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "openai package required: pip install openai"
        )

    client = OpenAI(api_key=api_key)

    def stream_fn(prompt: str) -> Generator[StreamChunk, None, None]:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                temperature=temperature,
                max_tokens=max_tokens,
                logprobs=True,
                top_logprobs=5,
            )

            for chunk in response:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta
                content = delta.content or ""
                finish_reason = chunk.choices[0].finish_reason

                # Extract logprobs for entropy calculation
                logprobs = None
                if (
                    chunk.choices[0].logprobs
                    and chunk.choices[0].logprobs.content
                ):
                    logprobs = [
                        lp.logprob
                        for lp in chunk.choices[0].logprobs.content
                    ]

                yield StreamChunk(
                    text=content,
                    logprobs=logprobs,
                    finish_reason=finish_reason,
                )

                if finish_reason == "stop":
                    return

        except Exception as e:
            # Yield error as final chunk
            yield StreamChunk(
                text=f"\n[ERROR] OpenAI API error: {str(e)}",
                finish_reason="error",
            )

    return stream_fn


def make_backend(
    api_key: str,
    model: str = "gpt-4o-mini",
    config: Optional[LLMConfig] = None,
) -> Callable[[str], Generator[StreamChunk, None, None]]:
    """
    Create an OpenAI streaming backend with config.

    Args:
        api_key: OpenAI API key
        model: Model ID
        config: Optional LLMConfig for temperature/max_tokens

    Returns:
        Backend function for LLMInterface
    """
    cfg = config or LLMConfig()
    return create_openai_backend(
        api_key=api_key,
        model=model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )


def make_llm_generate(
    api_key: str,
    model: str = "gpt-4o-mini",
    config: Optional[LLMConfig] = None,
) -> Callable[[str], str]:
    """
    Create a simple generate function using OpenAI.

    This wraps the streaming backend with LLMInterface for
    entropy monitoring and SABAR triggers.

    Args:
        api_key: OpenAI API key
        model: Model ID
        config: Optional LLMConfig

    Returns:
        Function that takes prompt and returns response text

    Example:
        generate = make_llm_generate("sk-...", "gpt-4o-mini")
        response = generate("What is 2+2?")
    """
    cfg = config or LLMConfig()
    backend = make_backend(api_key, model, cfg)

    llm = LLMInterface(config=cfg, backend_fn=backend)

    def generate(prompt: str) -> str:
        response, state = llm.generate(prompt)
        # If SABAR was triggered, the response will include the cooling message
        return response

    return generate


__all__ = [
    "create_openai_backend",
    "make_backend",
    "make_llm_generate",
]
