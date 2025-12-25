"""
litellm_gateway.py - LiteLLM Gateway for arifOS v38.2

Provides a unified LLM interface using LiteLLM, supporting:
- SEA-LION (via OpenAI-compatible API)
- OpenAI (GPT-4, GPT-4o-mini, etc.)
- Anthropic (Claude models)
- Google (Gemini models)
- Any OpenAI-compatible endpoint

This adapter reads configuration from environment variables and
provides a governed interface to the underlying LLM.

Environment Variables:
    ARIF_LLM_PROVIDER: Provider identifier (openai, anthropic, gemini)
    ARIF_LLM_API_BASE: API base URL (for OpenAI-compatible endpoints)
    ARIF_LLM_API_KEY: API key for authentication
    ARIF_LLM_MODEL: Model identifier

Usage:
    from arifos_core.connectors.litellm_gateway import make_llm_generate
    
    generate = make_llm_generate()
    response = generate("What is AI governance?")

Author: arifOS Project
Version: v38.2
License: Apache 2.0
"""

from __future__ import annotations

import os
from typing import Callable, Dict, Any, Optional

# LiteLLM import with fallback
try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    litellm = None


class LiteLLMConfig:
    """Configuration for LiteLLM gateway."""
    
    def __init__(
        self,
        provider: Optional[str] = None,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """
        Initialize LiteLLM configuration.
        
        Args:
            provider: Provider identifier (openai, anthropic, gemini, etc.)
            api_base: API base URL (for OpenAI-compatible endpoints like SEA-LION)
            api_key: API key for authentication
            model: Model identifier
            temperature: Generation temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        """
        # Read from environment with fallbacks
        self.provider = provider or os.getenv("ARIF_LLM_PROVIDER", "openai")
        self.api_base = api_base or os.getenv("ARIF_LLM_API_BASE")

        # Check API key with priority fallback
        self.api_key = (
            api_key
            or os.getenv("ARIF_LLM_API_KEY")
            or os.getenv("SEALION_API_KEY")
            or os.getenv("LLM_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

        self.model = model or os.getenv(
            "ARIF_LLM_MODEL",
            "aisingapore/Llama-SEA-LION-v3-70B-IT"
        )
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Validate required fields
        if not self.api_key:
            raise ValueError(
                "API key required. Set one of: ARIF_LLM_API_KEY, SEALION_API_KEY, "
                "LLM_API_KEY, OPENAI_API_KEY, or pass api_key parameter."
            )


def create_litellm_backend(
    config: Optional[LiteLLMConfig] = None,
) -> Callable[[str], str]:
    """
    Create a LiteLLM backend function.
    
    Args:
        config: Optional LiteLLMConfig (reads from env if not provided)
        
    Returns:
        Function that takes prompt and returns response text
        
    Raises:
        ImportError: If litellm is not installed
        ValueError: If required configuration is missing
    """
    if not LITELLM_AVAILABLE:
        raise ImportError(
            "litellm required. Install with: pip install litellm"
        )
    
    cfg = config or LiteLLMConfig()
    
    def generate(prompt: str) -> str:
        """
        Generate response using LiteLLM.
        
        Args:
            prompt: User prompt
            
        Returns:
            Response text from LLM
        """
        # Build messages
        messages = [{"role": "user", "content": prompt}]
        
        # Prepare model name for LiteLLM
        # LiteLLM requires provider prefix (e.g., "openai/model-name")
        # For custom OpenAI-compatible endpoints (like SEA-LION), prepend "openai/"
        model_name = cfg.model
        if cfg.api_base and not model_name.startswith(("openai/", "anthropic/", "gemini/", "huggingface/")):
            # This is a custom OpenAI-compatible endpoint (SEA-LION, etc.)
            model_name = f"openai/{cfg.model}"
        
        # Build completion kwargs
        completion_kwargs: Dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "temperature": cfg.temperature,
            "max_tokens": cfg.max_tokens,
        }
        
        # Add API base if provided (for SEA-LION, custom endpoints, etc.)
        if cfg.api_base:
            completion_kwargs["api_base"] = cfg.api_base
        
        # Add API key
        completion_kwargs["api_key"] = cfg.api_key
        
        # Call LiteLLM
        try:
            response = litellm.completion(**completion_kwargs)
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LiteLLM completion failed: {str(e)}")
    
    return generate


def make_llm_generate(
    config: Optional[LiteLLMConfig] = None,
) -> Callable[[str], str]:
    """
    Create a governed LLM generate function using LiteLLM.
    
    This is the primary interface for external integrations.
    Configuration is read from environment variables by default.
    
    Environment Variables:
        ARIF_LLM_PROVIDER: Provider (default: openai)
        ARIF_LLM_API_BASE: API base URL (required for SEA-LION)
        ARIF_LLM_API_KEY: API key (required)
        ARIF_LLM_MODEL: Model ID (default: aisingapore/Llama-SEA-LION-v3-70B-IT)
    
    Args:
        config: Optional LiteLLMConfig (reads from env if not provided)
        
    Returns:
        Function that takes prompt and returns response text
        
    Example:
        # Using environment variables (.env file)
        generate = make_llm_generate()
        response = generate("Explain AI governance")
        
        # Using explicit configuration
        config = LiteLLMConfig(
            provider="openai",
            api_base="https://api.sea-lion.ai/v1",
            api_key="your-key",
            model="aisingapore/Llama-SEA-LION-v3-70B-IT",
        )
        generate = make_llm_generate(config)
    """
    return create_litellm_backend(config)


def get_supported_providers() -> Dict[str, Dict[str, Any]]:
    """
    Get information about supported LLM providers.
    
    Returns:
        Dictionary mapping provider names to configuration requirements
    """
    return {
        "openai": {
            "description": "OpenAI GPT models (also SEA-LION compatible)",
            "requires_api_base": False,
            "example_models": [
                "gpt-4o",
                "gpt-4o-mini",
                "aisingapore/Llama-SEA-LION-v3-70B-IT",  # via api_base
            ],
        },
        "anthropic": {
            "description": "Anthropic Claude models",
            "requires_api_base": False,
            "example_models": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ],
        },
        "gemini": {
            "description": "Google Gemini models",
            "requires_api_base": False,
            "example_models": [
                "gemini-1.5-flash",
                "gemini-1.5-pro",
            ],
        },
        "sealion": {
            "description": "SEA-LION models via OpenAI-compatible API",
            "requires_api_base": True,
            "api_base": "https://api.sea-lion.ai/v1",
            "example_models": [
                "aisingapore/Llama-SEA-LION-v3-70B-IT",
                "aisingapore/Gemma-SEA-LION-v4-27B-IT",
                "aisingapore/Qwen-SEA-LION-v4-32B-IT",
            ],
        },
    }


__all__ = [
    "LiteLLMConfig",
    "create_litellm_backend",
    "make_llm_generate",
    "get_supported_providers",
]
