"""
arifos/runtime/metabolic_bridge.py — Vendor-Agnostic LLM Bridge

Canonical abstraction layer for all LLM inference inside arifOS.

Provider roles (as of 2026-04-20):
- **Ollama** (primary): local inference — chat + embeddings (bge-m3). Sovereign, zero egress cost.
- **MiniMax** (primary chat): user's main API for completions/chat. Wired via raw HTTP.
- **OpenAI** (backup/augmentation): chat fallback + embeddings backup (text-embedding-3-*).
- **Anthropic** (backup reasoning): Claude for high-quality reasoning. NO embeddings — Anthropic
  does not ship an embedding model (they recommend Voyage AI or third parties).

Every organ (111_SENSE, 333_MIND, MCP tools) calls `bridge.chat(...)` or
`bridge.embed(...)` and never imports a vendor SDK directly outside this module.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, AsyncGenerator, Literal

import httpx

logger = logging.getLogger(__name__)

# ── Provider detection ──────────────────────────────────────
Provider = Literal["ollama", "openai", "anthropic", "minimax", "auto"]

_DEFAULT_PROVIDER: Provider = os.getenv("ARIFOS_LLM_PROVIDER", "auto")  # type: ignore[assignment]
_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
_MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
_MINIMAX_GROUP_ID = os.getenv("MINIMAX_GROUP_ID", "")


# ── Lazy client initialisation ( forged on first use ) ──────
_openai_client: Any | None = None
_anthropic_client: Any | None = None


def _get_openai_client() -> Any:
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI

        _openai_client = OpenAI()
        logger.info("MetabolicBridge: OpenAI client forged")
    return _openai_client


def _get_anthropic_client() -> Any:
    global _anthropic_client
    if _anthropic_client is None:
        from anthropic import Anthropic

        _anthropic_client = Anthropic()
        logger.info("MetabolicBridge: Anthropic client forged")
    return _anthropic_client


# ── Bridge API ──────────────────────────────────────────────
class MetabolicBridge:
    """
    Constitutional LLM gateway.

    Usage:
        from arifos.runtime.metabolic_bridge import bridge
        response = await bridge.chat(
            messages=[{"role": "user", "content": "Hello"}],
            model="auto",          # or "gpt-5.2", "claude-opus-4", "abab6.5s", "qwen2.5:7b"
            provider="auto",       # or "openai", "anthropic", "minimax", "ollama"
        )
    """

    # ── Chat / Completion ───────────────────────────────────
    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str = "auto",
        provider: Provider = "auto",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        tools: list[dict[str, Any]] | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """
        Send a chat completion request through the governed bridge.

        Returns a normalised dict:
            {
                "provider": "openai" | "anthropic" | "minimax" | "ollama",
                "model": str,
                "content": str,
                "usage": {"prompt_tokens": int, "completion_tokens": int, "total_tokens": int},
                "raw": <original response object>,
            }
        """
        resolved = self._resolve_provider(provider, model)
        logger.debug(f"MetabolicBridge.chat → {resolved} | model={model}")

        if resolved == "ollama":
            return await self._chat_ollama(
                messages, model=model, temperature=temperature,
                max_tokens=max_tokens, stream=stream,
            )
        if resolved == "openai":
            return await self._chat_openai(
                messages, model=model, temperature=temperature,
                max_tokens=max_tokens, tools=tools, stream=stream,
            )
        if resolved == "anthropic":
            return await self._chat_anthropic(
                messages, model=model, temperature=temperature,
                max_tokens=max_tokens, tools=tools, stream=stream,
            )
        if resolved == "minimax":
            return await self._chat_minimax(
                messages, model=model, temperature=temperature,
                max_tokens=max_tokens, stream=stream,
            )

        raise ValueError(f"Unknown provider: {resolved}")

    # ── Embedding ───────────────────────────────────────────
    async def embed(
        self,
        texts: list[str],
        *,
        model: str = "bge-m3:latest",
        provider: Provider = "ollama",
    ) -> list[list[float]]:
        """
        Generate embeddings.

        **Primary**: Ollama (bge-m3:latest) — local, sovereign, no egress cost.
        **Backup**: OpenAI (text-embedding-3-small) — stable, battle-tested.

        Note: Anthropic does NOT offer an embedding model. MiniMax embeddings
        are available via langchain_community but not yet forged into this runtime.
        """
        if provider == "auto":
            provider = "ollama"

        if provider == "ollama":
            async with httpx.AsyncClient() as client:
                payloads = [
                    {"model": model, "prompt": t}
                    for t in texts
                ]
                results = []
                for payload in payloads:
                    r = await client.post(
                        f"{_OLLAMA_URL}/api/embeddings",
                        json=payload,
                        timeout=60.0,
                    )
                    r.raise_for_status()
                    results.append(r.json()["embedding"])
                return results

        if provider == "openai":
            client = _get_openai_client()
            response = client.embeddings.create(
                model=model if model != "bge-m3:latest" else "text-embedding-3-small",
                input=texts,
            )
            return [d.embedding for d in response.data]

        raise ValueError(
            f"Embed not supported for provider: {provider}. "
            "Use 'ollama' (primary) or 'openai' (backup)."
        )

    # ── Provider resolution ─────────────────────────────────
    def _resolve_provider(self, provider: Provider, model: str) -> Provider:
        if provider != "auto":
            return provider

        # Model-name heuristic
        if model.startswith("gpt-") or model.startswith("o") or model.startswith("text-embedding"):
            return "openai"
        if model.startswith("claude-"):
            return "anthropic"
        if model.startswith("abab") or model.startswith("minimax"):
            return "minimax"
        if ":" in model or model.startswith("qwen") or model.startswith("llama") or model.startswith("bge-"):
            return "ollama"

        # Default to local sovereignty
        return "ollama"

    # ── OpenAI backend ──────────────────────────────────────
    async def _chat_openai(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        tools: list[dict[str, Any]] | None,
        stream: bool,
    ) -> dict[str, Any]:
        client = _get_openai_client()
        if model == "auto":
            model = "gpt-4.1"

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
        if stream:
            kwargs["stream"] = True

        response = client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        return {
            "provider": "openai",
            "model": model,
            "content": choice.message.content or "",
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            } if response.usage else {},
            "raw": response,
        }

    # ── Anthropic backend ───────────────────────────────────
    async def _chat_anthropic(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        tools: list[dict[str, Any]] | None,
        stream: bool,
    ) -> dict[str, Any]:
        client = _get_anthropic_client()
        if model == "auto":
            model = "claude-sonnet-4-20250514"

        # Anthropic uses "user" / "assistant" only — system is top-level
        system_msg = None
        chat_messages = []
        for m in messages:
            if m.get("role") == "system":
                system_msg = m.get("content", "")
            else:
                chat_messages.append(m)

        kwargs: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": chat_messages,
            "temperature": temperature,
        }
        if system_msg:
            kwargs["system"] = system_msg
        if tools:
            kwargs["tools"] = tools
        if stream:
            return await self._stream_anthropic(client, kwargs)

        response = client.messages.create(**kwargs)
        return {
            "provider": "anthropic",
            "model": model,
            "content": response.content[0].text if response.content else "",
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            } if response.usage else {},
            "raw": response,
        }

    async def _stream_anthropic(
        self, client: Any, kwargs: dict[str, Any]
    ) -> AsyncGenerator[dict[str, Any], None]:
        import asyncio

        loop = asyncio.get_event_loop()
        stream = await loop.run_in_executor(
            None, lambda: client.messages.create(stream=True, **kwargs)
        )
        for chunk in stream:
            yield {
                "provider": "anthropic",
                "model": kwargs.get("model"),
                "delta": chunk.delta.text if hasattr(chunk, "delta") and chunk.delta else "",
                "finish_reason": chunk.stop_reason if hasattr(chunk, "stop_reason") else None,
            }

    # ── MiniMax backend ─────────────────────────────────────
    async def _chat_minimax(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool,
    ) -> dict[str, Any]:
        """
        MiniMax chat completion via raw HTTP.
        Docs: https://www.minimaxi.com/document/guides/chat-model/V2
        """
        if model == "auto":
            model = "abab6.5s-chat"

        if not _MINIMAX_API_KEY:
            raise RuntimeError(
                "MiniMax API key not configured. Set MINIMAX_API_KEY in environment."
            )

        # MiniMax uses a single "text" field for system prompt + messages
        # V2 API: POST https://api.minimaxi.com/v2/text/chatcompletion_v2
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if stream:
            payload["stream"] = True

        headers = {
            "Authorization": f"Bearer {_MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.minimaxi.com/v2/text/chatcompletion_v2",
                json=payload,
                headers=headers,
                timeout=120.0,
            )
            r.raise_for_status()
            data = r.json()

        # Normalise MiniMax response shape
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {})
        usage = data.get("usage", {})
        return {
            "provider": "minimax",
            "model": model,
            "content": msg.get("content", ""),
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
            "raw": data,
        }

    # ── Ollama backend ──────────────────────────────────────
    async def _chat_ollama(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool,
    ) -> dict[str, Any]:
        if model == "auto":
            model = "qwen2.5:7b"

        payload = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": stream,
        }

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{_OLLAMA_URL}/api/chat",
                json=payload,
                timeout=120.0,
            )
            r.raise_for_status()
            data = r.json()

        return {
            "provider": "ollama",
            "model": model,
            "content": data.get("message", {}).get("content", ""),
            "usage": {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": (
                    data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                ),
            },
            "raw": data,
        }


# ── Singleton export ────────────────────────────────────────
bridge = MetabolicBridge()
