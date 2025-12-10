"""
arifos_core.adapters - LLM adapters for arifOS.

This package provides adapters for connecting real LLMs to arifOS.
Each adapter exposes:
- make_backend(): Returns streaming backend for LLMInterface
- make_llm_generate(): Returns simple generate function

The adapters supply RAW intelligence only. Constitutional governance
is applied via @apex_guardrail at the call sites.

Available adapters:
- llm_sealion: AI Singapore SEA-LION models (Qwen, Llama, Gemma based)
- llm_openai: OpenAI GPT models (gpt-4o, gpt-4o-mini, etc.)
- llm_claude: Anthropic Claude models (claude-3-opus, claude-3-sonnet, etc.)
- llm_gemini: Google Gemini models (gemini-1.5-flash, gemini-1.5-pro, etc.)

Usage:
    # SEA-LION (local/Colab with GPU)
    from arifos_core.adapters.llm_sealion import make_llm_generate
    generate = make_llm_generate(model="qwen-7b")

    # OpenAI (API)
    from arifos_core.adapters.llm_openai import make_llm_generate
    generate = make_llm_generate(api_key="sk-...")
"""

