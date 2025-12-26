"""
llm_gemini.py - Google Gemini Adapter for arifOS v35Ω

Provides Gemini model integration with entropy monitoring.

Note: Gemini doesn't expose logprobs, so we use text-based entropy estimation.

Usage:
    from arifos_core.adapters.llm_gemini import make_llm_generate

    generate = make_llm_generate(api_key="...", model="gemini-1.5-flash")
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


def create_gemini_backend(
    api_key: str,
    model: str = "gemini-1.5-flash",
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> Callable[[str], Generator[StreamChunk, None, None]]:
    """
    Create a Google Gemini streaming backend.

    Args:
        api_key: Google AI API key
        model: Model ID (gemini-1.5-flash, gemini-1.5-pro, etc.)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        Backend function that yields StreamChunks

    Note:
        Gemini doesn't expose logprobs, so entropy is estimated from text.
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
            model_instance = genai.GenerativeModel(
                model,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            response = model_instance.generate_content(prompt, stream=True)

            for chunk in response:
                # Extract text from chunk
                text = getattr(chunk, "text", "") or ""
                if not text and hasattr(chunk, "parts"):
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


def make_backend(
    api_key: str,
    model: str = "gemini-1.5-flash",
    config: Optional[LLMConfig] = None,
) -> Callable[[str], Generator[StreamChunk, None, None]]:
    """
    Create a Gemini streaming backend with config.

    Args:
        api_key: Google AI API key
        model: Model ID
        config: Optional LLMConfig for temperature/max_tokens

    Returns:
        Backend function for LLMInterface
    """
    cfg = config or LLMConfig()
    return create_gemini_backend(
        api_key=api_key,
        model=model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )


def make_llm_generate(
    api_key: str,
    model: str = "gemini-1.5-flash",
    config: Optional[LLMConfig] = None,
) -> Callable[[str], str]:
    """
    Create a simple generate function using Gemini.

    This wraps the streaming backend with LLMInterface for
    entropy monitoring and SABAR triggers.

    Args:
        api_key: Google AI API key
        model: Model ID
        config: Optional LLMConfig

    Returns:
        Function that takes prompt and returns response text

    Example:
        generate = make_llm_generate("...", "gemini-1.5-flash")
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
    "create_gemini_backend",
    "make_backend",
    "make_llm_generate",
]
