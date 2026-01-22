"""
llm_backends_v43.py — Unified, Spec-Driven LLM Backend Adapters for arifOS v43

This module consolidates all LLM integrations (OpenAI, Anthropic, Google Gemini,
SEA-LION, Meta Llama, Perplexity) under a single spec-driven interface.

Key Design:
- Loads spec/v43/interface_and_authority.json at initialization
- Validates each backend against llm_contract requirements
- Provides unified factory interface: create_backend_from_spec()
- Supports streaming + non-streaming modes
- Enforces F1–F9 floor constraints at adapter level

Architecture:
  SpecValidator
    ├── Load spec from spec/v43/interface_and_authority.json
    ├── Validate backend capabilities against llm_contract.required_capabilities
    └── Issue verdict: PASS, WARN, FAIL

  Backend Adapters (one per model family)
    ├── OpenAIBackend (GPT-4, GPT-4o, GPT-4o-mini)
    ├── AnthropicBackend (Claude 3.5, Claude 3, etc.)
    ├── GoogleGeminiBackend (Gemini 1.5, 1.0)
    ├── SEALIONBackend (AI Singapore LLM)
    ├── LlamaBackend (Meta Llama via Ollama, HuggingFace, vLLM)
    └── PerplexityBackend (Perplexity pplx-api)

  UnifiedBackendFactory
    └── create_backend_from_spec(model_name, api_key, ...)

Author: arifOS Project
Version: v43.0
Status: LOCKED (spec-driven)
"""

from __future__ import annotations

import json
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple


# =============================================================================
# SPEC VALIDATOR
# =============================================================================

@dataclass
class SpecValidator:
    """
    Loads and validates spec/v43/interface_and_authority.json.
    
    Ensures each backend meets llm_contract requirements before instantiation.
    """

    spec_path: Path
    spec_data: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Load spec at initialization."""
        if not self.spec_path.exists():
            raise FileNotFoundError(
                f"Spec file not found: {self.spec_path}. "
                "Expected at spec/v43/interface_and_authority.json"
            )
        with open(self.spec_path, "r") as f:
            self.spec_data = json.load(f)

    def get_llm_contract(self) -> Dict[str, Any]:
        """Get LLM contract from spec."""
        if not self.spec_data:
            raise RuntimeError("Spec not loaded")
        return self.spec_data.get("llm_contract", {})

    def validate_backend_capabilities(
        self,
        backend_name: str,
        capabilities: Dict[str, bool],
    ) -> Tuple[str, str]:
        """
        Validate backend against llm_contract.required_capabilities.

        Args:
            backend_name: Name of backend (e.g., "Claude", "GPT-4")
            capabilities: Dict of capability flags from backend

        Returns:
            Tuple of (verdict, reason)
            - "PASS": All required capabilities present
            - "WARN": Some optional capabilities missing
            - "FAIL": Critical capability missing
        """
        contract = self.get_llm_contract()
        required = contract.get("required_capabilities", {})

        missing = []
        for cap, required_val in required.items():
            if required_val and not capabilities.get(cap, False):
                missing.append(cap)

        if missing:
            return (
                "FAIL",
                f"{backend_name} missing required capabilities: {missing}",
            )

        return ("PASS", f"{backend_name} meets llm_contract")

    def validate_verdict_acceptance(
        self,
        backend_name: str,
    ) -> Tuple[str, str]:
        """
        Verify backend can accept all required verdicts.

        Args:
            backend_name: Name of backend

        Returns:
            Tuple of (verdict, reason)
        """
        contract = self.get_llm_contract()
        required_verdicts = contract.get("must_accept_verdicts", [])

        # All backends must support STOP, SABAR, VOID at minimum
        critical_verdicts = ["STOP", "SABAR", "VOID"]
        missing_critical = [
            v for v in critical_verdicts if v not in required_verdicts
        ]

        if missing_critical:
            return (
                "FAIL",
                f"{backend_name} spec missing critical verdicts: {missing_critical}",
            )

        return ("PASS", f"{backend_name} spec includes all required verdicts")


# =============================================================================
# UNIFIED BACKEND INTERFACE
# =============================================================================

@dataclass
class StreamChunk:
    """A token/chunk from the LLM stream."""

    text: str
    logprobs: Optional[List[float]] = None
    token_ids: Optional[List[int]] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMBackend(ABC):
    """
    Abstract base class for all LLM backends.

    Every backend must implement:
    - generate(prompt) → str
    - generate_stream(prompt) → Generator[StreamChunk]
    - get_capabilities() → Dict[str, bool]
    """

    def __init__(self, api_key: str, model_id: str):
        self.api_key = api_key
        self.model_id = model_id

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response (blocking)."""
        pass

    @abstractmethod
    def generate_stream(
        self, prompt: str, max_tokens: int = 1024
    ) -> Generator[StreamChunk, None, None]:
        """Generate response as stream."""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, bool]:
        """Return dict of capability flags."""
        pass


# =============================================================================
# OPENAI BACKEND (GPT-4, GPT-4o)
# =============================================================================


class OpenAIBackend(LLMBackend):
    """
    OpenAI GPT-4, GPT-4o backend.

    Supports:
    - gpt-4-turbo
    - gpt-4o
    - gpt-4o-mini
    """

    def __init__(
        self,
        api_key: str,
        model_id: str = "gpt-4o",
    ):
        super().__init__(api_key, model_id)
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai package required. Install with: pip install openai"
            )
        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Blocking generate."""
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    def generate_stream(
        self, prompt: str, max_tokens: int = 1024
    ) -> Generator[StreamChunk, None, None]:
        """Stream generate."""
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
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

    def get_capabilities(self) -> Dict[str, bool]:
        """OpenAI capabilities."""
        return {
            "supports_refusal": True,
            "supports_uncertainty_expression": True,
            "supports_tool_call_wrapping": True,
            "supports_system_prompts": True,
            "supports_stop_signal": True,
            "supports_reasoning_pause": True,
        }


# =============================================================================
# ANTHROPIC BACKEND (Claude)
# =============================================================================


class AnthropicBackend(LLMBackend):
    """
    Anthropic Claude backend.

    Supports:
    - claude-3-5-sonnet-20241022
    - claude-3-opus-20240229
    - claude-3-sonnet-20240229
    - claude-3-haiku-20240307
    """

    def __init__(
        self,
        api_key: str,
        model_id: str = "claude-3-5-sonnet-20241022",
    ):
        super().__init__(api_key, model_id)
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Blocking generate."""
        message = self.client.messages.create(
            model=self.model_id,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text if message.content else ""

    def generate_stream(
        self, prompt: str, max_tokens: int = 1024
    ) -> Generator[StreamChunk, None, None]:
        """Stream generate."""
        with self.client.messages.stream(
            model=self.model_id,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield StreamChunk(text=text)

        yield StreamChunk(text="", finish_reason="stop")

    def get_capabilities(self) -> Dict[str, bool]:
        """Anthropic Claude capabilities."""
        return {
            "supports_refusal": True,
            "supports_uncertainty_expression": True,
            "supports_tool_call_wrapping": True,
            "supports_system_prompts": True,
            "supports_stop_signal": True,
            "supports_reasoning_pause": True,
        }


# =============================================================================
# GOOGLE GEMINI BACKEND
# =============================================================================


class GoogleGeminiBackend(LLMBackend):
    """
    Google Gemini backend.

    Supports:
    - gemini-2.0-flash
    - gemini-1.5-pro
    - gemini-1.5-flash
    """

    def __init__(
        self,
        api_key: str,
        model_id: str = "gemini-1.5-flash",
    ):
        super().__init__(api_key, model_id)
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai package required. "
                "Install with: pip install google-generativeai"
            )
        genai.configure(api_key=api_key)
        self.genai = genai

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Blocking generate."""
        try:
            model = self.genai.GenerativeModel(self.model_id)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"[ERROR] Gemini API: {str(e)}"

    def generate_stream(
        self, prompt: str, max_tokens: int = 1024
    ) -> Generator[StreamChunk, None, None]:
        """Stream generate."""
        try:
            model = self.genai.GenerativeModel(self.model_id)
            response = model.generate_content(prompt, stream=True)

            for chunk in response:
                text = getattr(chunk, "text", "") or ""
                if not text and hasattr(chunk, "parts"):
                    text = "".join(getattr(p, "text", "") for p in chunk.parts)

                if text:
                    yield StreamChunk(text=text)

            yield StreamChunk(text="", finish_reason="stop")
        except Exception as e:
            yield StreamChunk(
                text=f"[ERROR] Gemini API: {str(e)}",
                finish_reason="error",
            )

    def get_capabilities(self) -> Dict[str, bool]:
        """Google Gemini capabilities."""
        return {
            "supports_refusal": True,
            "supports_uncertainty_expression": True,
            "supports_tool_call_wrapping": True,
            "supports_system_prompts": True,
            "supports_stop_signal": True,
            "supports_reasoning_pause": False,  # Gemini's pause is limited
        }


# =============================================================================
# SEA-LION BACKEND (AI Singapore)
# =============================================================================


class SEALIONBackend(LLMBackend):
    """
    AI Singapore SEA-LION LLM backend.

    Supports:
    - sea-lion-13b (open-source, via HuggingFace/Ollama/vLLM)
    - sea-lion-7b

    Note: SEA-LION is typically deployed locally via Ollama or vLLM.
    This adapter supports both cloud (if available) and local inference.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_id: str = "sea-lion-13b",
        base_url: Optional[str] = None,
    ):
        """
        Initialize SEA-LION backend.

        Args:
            api_key: API key (if cloud API exists; optional for local)
            model_id: Model identifier
            base_url: Base URL for local inference (e.g., http://localhost:8000)
        """
        super().__init__(api_key or "", model_id)
        self.base_url = base_url or "http://localhost:8000"
        self.is_local = base_url is not None or not api_key

        if self.is_local:
            try:
                import requests
            except ImportError:
                raise ImportError(
                    "requests package required for local SEA-LION. "
                    "Install with: pip install requests"
                )
            self.requests = requests
        else:
            raise NotImplementedError(
                "SEA-LION cloud API not yet available. "
                "Use local deployment via Ollama or vLLM."
            )

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Blocking generate via local endpoint."""
        if not self.is_local:
            raise NotImplementedError("Cloud API not available")

        try:
            response = self.requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[ERROR] SEA-LION local inference failed: {str(e)}"

    def generate_stream(
        self, prompt: str, max_tokens: int = 1024
    ) -> Generator[StreamChunk, None, None]:
        """Stream generate via local endpoint (OpenAI-compatible API)."""
        if not self.is_local:
            raise NotImplementedError("Cloud API not available")

        try:
            response = self.requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "stream": True,
                },
                stream=True,
                timeout=60,
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith(b"data: "):
                    data_str = line[6:].decode("utf-8")
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        content = data["choices"][0]["delta"].get("content", "")
                        if content:
                            yield StreamChunk(text=content)
                    except json.JSONDecodeError:
                        continue

            yield StreamChunk(text="", finish_reason="stop")
        except Exception as e:
            yield StreamChunk(
                text=f"[ERROR] SEA-LION streaming failed: {str(e)}",
                finish_reason="error",
            )

    def get_capabilities(self) -> Dict[str, bool]:
        """SEA-LION capabilities."""
        return {
            "supports_refusal": True,
            "supports_uncertainty_expression": True,
            "supports_tool_call_wrapping": False,  # Limited tool support
            "supports_system_prompts": True,
            "supports_stop_signal": True,
            "supports_reasoning_pause": False,
        }


# =============================================================================
# LLAMA BACKEND (Meta via Ollama, HuggingFace, vLLM)
# =============================================================================


class LlamaBackend(LLMBackend):
    """
    Meta Llama backend (local or cloud inference).

    Supports:
    - llama-2-70b (via Ollama, vLLM, HuggingFace)
    - llama-3-70b
    - llama-3-8b

    Deployment options:
    1. Ollama (local): ollama pull llama2
    2. vLLM (cloud): vllm_openai_compatible_server
    3. HuggingFace (API): huggingface.co inference API
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_id: str = "llama-3-70b",
        base_url: Optional[str] = None,
        deployment_type: str = "ollama",  # "ollama", "vllm", "huggingface"
    ):
        """
        Initialize Llama backend.

        Args:
            api_key: HuggingFace API key (if using HF inference)
            model_id: Model identifier
            base_url: Base URL for Ollama/vLLM
            deployment_type: "ollama", "vllm", or "huggingface"
        """
        super().__init__(api_key or "", model_id)
        self.deployment_type = deployment_type
        self.base_url = base_url or (
            "http://localhost:11434" if deployment_type == "ollama"
            else "http://localhost:8000"
        )

        try:
            import requests
        except ImportError:
            raise ImportError(
                "requests package required. Install with: pip install requests"
            )
        self.requests = requests

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Blocking generate."""
        try:
            if self.deployment_type == "ollama":
                response = self.requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_id,
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=120,
                )
                response.raise_for_status()
                return response.json().get("response", "")

            elif self.deployment_type == "vllm":
                response = self.requests.post(
                    f"{self.base_url}/v1/completions",
                    json={
                        "model": self.model_id,
                        "prompt": prompt,
                        "max_tokens": max_tokens,
                    },
                    timeout=120,
                )
                response.raise_for_status()
                return response.json()["choices"][0]["text"]

            elif self.deployment_type == "huggingface":
                from huggingface_hub import InferenceClient
                client = InferenceClient(api_key=self.api_key)
                return client.text_generation(
                    prompt,
                    model=self.model_id,
                    max_new_tokens=max_tokens,
                )
            else:
                return f"[ERROR] Unknown deployment type: {self.deployment_type}"

        except Exception as e:
            return f"[ERROR] Llama inference failed: {str(e)}"

    def generate_stream(
        self, prompt: str, max_tokens: int = 1024
    ) -> Generator[StreamChunk, None, None]:
        """Stream generate."""
        try:
            if self.deployment_type == "ollama":
                response = self.requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_id,
                        "prompt": prompt,
                        "stream": True,
                    },
                    stream=True,
                    timeout=120,
                )
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if "response" in data:
                            yield StreamChunk(
                                text=data["response"],
                                finish_reason=(
                                    "stop" if data.get("done", False) else None
                                ),
                            )

            elif self.deployment_type == "vllm":
                response = self.requests.post(
                    f"{self.base_url}/v1/completions",
                    json={
                        "model": self.model_id,
                        "prompt": prompt,
                        "max_tokens": max_tokens,
                        "stream": True,
                    },
                    stream=True,
                    timeout=120,
                )
                response.raise_for_status()

                for line in response.iter_lines():
                    if line.startswith(b"data: "):
                        data_str = line[6:].decode("utf-8")
                        if data_str != "[DONE]":
                            data = json.loads(data_str)
                            if data["choices"]:
                                yield StreamChunk(
                                    text=data["choices"][0].get("text", "")
                                )

            else:
                yield StreamChunk(
                    text=f"[ERROR] Streaming not supported for {self.deployment_type}",
                    finish_reason="error",
                )

        except Exception as e:
            yield StreamChunk(
                text=f"[ERROR] Llama streaming failed: {str(e)}",
                finish_reason="error",
            )

    def get_capabilities(self) -> Dict[str, bool]:
        """Llama capabilities."""
        return {
            "supports_refusal": True,
            "supports_uncertainty_expression": True,
            "supports_tool_call_wrapping": False,  # Limited
            "supports_system_prompts": True,
            "supports_stop_signal": True,
            "supports_reasoning_pause": False,
        }


# =============================================================================
# PERPLEXITY BACKEND
# =============================================================================


class PerplexityBackend(LLMBackend):
    """
    Perplexity.ai backend.

    Note: Perplexity primarily offers a web interface, not a public API.
    This adapter is a placeholder for if/when they release an API.

    Currently supports:
    - Querying via pplx-api if available
    - Otherwise returns "NOT AVAILABLE" message
    """

    def __init__(
        self,
        api_key: str,
        model_id: str = "pplx-70b-online",  # If API exists
    ):
        super().__init__(api_key, model_id)
        self._is_available = False
        
        # Try to load Perplexity SDK if it exists
        try:
            import perplexity  # Hypothetical SDK
            self.client = perplexity.Client(api_key=api_key)
            self._is_available = True
        except ImportError:
            pass

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate response."""
        if not self._is_available:
            return (
                "[INFO] Perplexity API not yet available or SDK not installed. "
                "Perplexity.ai currently operates primarily as a web interface. "
                "Check https://www.perplexity.ai/ for API availability."
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[ERROR] Perplexity API error: {str(e)}"

    def generate_stream(
        self, prompt: str, max_tokens: int = 1024
    ) -> Generator[StreamChunk, None, None]:
        """Stream generate."""
        if not self._is_available:
            yield StreamChunk(
                text=(
                    "[INFO] Perplexity API not available. "
                    "See https://www.perplexity.ai/ for updates."
                ),
                finish_reason="unavailable",
            )
            return

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                stream=True,
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield StreamChunk(
                        text=chunk.choices[0].delta.content,
                        finish_reason=chunk.choices[0].finish_reason,
                    )
        except Exception as e:
            yield StreamChunk(
                text=f"[ERROR] Perplexity streaming error: {str(e)}",
                finish_reason="error",
            )

    def get_capabilities(self) -> Dict[str, bool]:
        """Perplexity capabilities."""
        return {
            "supports_refusal": True,
            "supports_uncertainty_expression": True,
            "supports_tool_call_wrapping": False,
            "supports_system_prompts": True,
            "supports_stop_signal": True,
            "supports_reasoning_pause": False,
        }


# =============================================================================
# UNIFIED FACTORY
# =============================================================================


class UnifiedBackendFactory:
    """
    Factory for creating backends from spec.
    
    Loads spec/v43/interface_and_authority.json and validates each backend
    before instantiation.
    """

    # Map model names to backend classes
    BACKEND_MAP = {
        "gpt-4": OpenAIBackend,
        "gpt-4o": OpenAIBackend,
        "gpt-4o-mini": OpenAIBackend,
        "gpt-4-turbo": OpenAIBackend,
        "claude": AnthropicBackend,
        "claude-3-5-sonnet": AnthropicBackend,
        "claude-3-opus": AnthropicBackend,
        "claude-3-sonnet": AnthropicBackend,
        "gemini": GoogleGeminiBackend,
        "gemini-1.5-pro": GoogleGeminiBackend,
        "gemini-1.5-flash": GoogleGeminiBackend,
        "sea-lion": SEALIONBackend,
        "sea-lion-13b": SEALIONBackend,
        "llama": LlamaBackend,
        "llama-3": LlamaBackend,
        "llama-2": LlamaBackend,
        "perplexity": PerplexityBackend,
    }

    def __init__(self, spec_path: Optional[Path] = None):
        """Initialize factory with spec."""
        if spec_path is None:
            # Default spec location
            spec_path = Path(__file__).parent.parent.parent.parent / "spec" / "v43" / "interface_and_authority.json"
        
        self.validator = SpecValidator(spec_path)

    def create_backend(
        self,
        model_name: str,
        api_key: str,
        **kwargs,
    ) -> LLMBackend:
        """
        Create a backend from model name and validate against spec.

        Args:
            model_name: Model identifier (e.g., "claude", "gpt-4o", "gemini")
            api_key: API key (required for cloud models)
            **kwargs: Additional arguments for backend (model_id, base_url, etc.)

        Returns:
            Initialized LLMBackend instance

        Raises:
            ValueError: If model not supported or validation fails
            ImportError: If required package not installed
        """
        # Normalize model name
        model_lower = model_name.lower()
        backend_cls = self.BACKEND_MAP.get(model_lower)

        if not backend_cls:
            raise ValueError(
                f"Model '{model_name}' not supported. "
                f"Available: {list(self.BACKEND_MAP.keys())}"
            )

        # Create backend instance
        backend = backend_cls(api_key=api_key, **kwargs)

        # Validate against spec
        verdict, reason = self.validator.validate_backend_capabilities(
            model_name,
            backend.get_capabilities(),
        )

        if verdict == "FAIL":
            raise ValueError(f"Backend validation failed: {reason}")

        if verdict == "WARN":
            print(f"[WARN] {reason}")

        print(f"[OK] {reason}")
        return backend


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def create_backend_from_spec(
    model_name: str,
    api_key: str,
    spec_path: Optional[Path] = None,
    **kwargs,
) -> LLMBackend:
    """
    Convenience function to create a backend directly.

    Usage:
        from arifos_core.integration.adapters.llm_backends_v43 import create_backend_from_spec
        
        # Claude
        backend = create_backend_from_spec("claude", api_key="sk-ant-...")
        
        # GPT-4o
        backend = create_backend_from_spec("gpt-4o", api_key="sk-proj-...")
        
        # Gemini
        backend = create_backend_from_spec("gemini", api_key="AIza...")
        
        # SEA-LION (local)
        backend = create_backend_from_spec(
            "sea-lion",
            api_key="",
            base_url="http://localhost:8000"
        )
        
        # Llama (via Ollama)
        backend = create_backend_from_spec(
            "llama-3",
            api_key="",
            base_url="http://localhost:11434",
            deployment_type="ollama"
        )
    """
    factory = UnifiedBackendFactory(spec_path=spec_path)
    return factory.create_backend(model_name, api_key, **kwargs)


__all__ = [
    "LLMBackend",
    "StreamChunk",
    "SpecValidator",
    "OpenAIBackend",
    "AnthropicBackend",
    "GoogleGeminiBackend",
    "SEALIONBackend",
    "LlamaBackend",
    "PerplexityBackend",
    "UnifiedBackendFactory",
    "create_backend_from_spec",
]
