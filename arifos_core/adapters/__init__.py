"""
arifos_core.adapters - LLM Adapters for arifOS v35Ω

This package provides adapters for connecting real LLMs to arifOS.
Each adapter exposes:
- make_backend(): Returns streaming backend for LLMInterface
- make_llm_generate(): Returns simple generate function

The adapters supply RAW intelligence only. Constitutional governance
is applied via @apex_guardrail at the call sites.

Available adapters:
- llm_openai: OpenAI GPT models (gpt-4o, gpt-4o-mini, etc.)
- llm_claude: Anthropic Claude models (claude-3-opus, claude-3-sonnet, etc.)
- llm_gemini: Google Gemini models (gemini-1.5-flash, gemini-1.5-pro, etc.)

Usage:
    from arifos_core.adapters.llm_openai import make_llm_generate

    generate = make_llm_generate(api_key="sk-...")
    response = generate("What is 2+2?")
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .llm_openai import make_backend as openai_backend, make_llm_generate as openai_generate
    from .llm_claude import make_backend as claude_backend, make_llm_generate as claude_generate
    from .llm_gemini import make_backend as gemini_backend, make_llm_generate as gemini_generate

__all__ = [
    "llm_openai",
    "llm_claude",
    "llm_gemini",
]
