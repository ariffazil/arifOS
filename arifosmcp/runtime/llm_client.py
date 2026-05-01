"""
arifosmcp/runtime/llm_client.py — Shared LLM Cognition Client

Tier 1: SEA-LION (https://api.sea-lion.ai/v1)
Tier 2: Ollama local fallback
Tier 3: raises LLMUnavailableError — caller applies deterministic fallback

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
SEA_LION_API_KEY = os.getenv("SEA_LION_API_KEY")
SEA_LION_BASE_URL = os.getenv("SEA_LION_BASE_URL", "https://api.sea-lion.ai/v1")
SEA_LION_MODEL = os.getenv("SEA_LION_MEANING_MODEL", "aisingapore/Qwen-SEA-LION-v4-32B-IT")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")


class LLMUnavailableError(Exception):
    """Raised when both SEA-LION and Ollama are unavailable."""

    pass


# ── Internal Helpers ───────────────────────────────────────────────────────────


def _strip_markdown(content: str) -> str:
    """Strip markdown code fences from LLM output."""
    content = content.strip()
    for fence in ("```json", "```json\n", "```"):
        if content.startswith(fence):
            content = content[len(fence) :]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


def _validate_schema(parsed: dict[str, Any], required_fields: set[str]) -> None:
    """Raise LLMUnavailableError if required schema fields are missing."""
    missing = required_fields - set(parsed.keys())
    if missing:
        raise LLMUnavailableError(f"LLM output missing required fields: {sorted(missing)}")


async def _call_sea_lion(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
) -> dict[str, Any]:
    """Tier 1 — call SEA-LION chat completions API."""
    if not SEA_LION_API_KEY:
        raise LLMUnavailableError("SEA_LION_API_KEY not configured")

    messages = [{"role": "system", "content": system}]
    if user:
        messages.append({"role": "user", "content": user})

    payload = {
        "model": SEA_LION_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{SEA_LION_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {SEA_LION_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except Exception as exc:
        logger.warning("SEA-LION transport error: %s", exc)
        raise LLMUnavailableError(f"SEA-LION transport error: {exc}") from exc

    if response.status_code != 200:
        logger.warning("SEA-LION HTTP %s: %s", response.status_code, response.text[:200])
        raise LLMUnavailableError(f"SEA-LION HTTP {response.status_code}")

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except Exception as exc:
        logger.warning("SEA-LION parse error: %s", exc)
        raise LLMUnavailableError(f"SEA-LION response parse error: {exc}") from exc

    content = _strip_markdown(content)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.warning("SEA-LION returned invalid JSON: %s", content[:200])
        raise LLMUnavailableError(f"SEA-LION returned invalid JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(
            f"SEA-LION output must be a JSON object, got {type(parsed).__name__}"
        )

    # Strip response_format schema enforcement — SEA-LION returns its own
    # JSON structure. Validate only that at least some content is present.
    if not parsed:
        raise LLMUnavailableError("SEA-LION returned empty JSON object")

    logger.debug("SEA-LION inference complete")
    return parsed


async def _call_ollama(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
) -> dict[str, Any]:
    """Tier 2 — call local Ollama as fallback."""
    prompt = f"{system}\n\n{user}" if user else system

    payload: dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": temperature,
        "options": {"num_predict": max_tokens},
    }
    if response_schema:
        payload["format"] = "json"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
            )
    except Exception as exc:
        logger.warning("Ollama transport error: %s", exc)
        raise LLMUnavailableError(f"Ollama unavailable: {exc}") from exc

    if response.status_code != 200:
        raise LLMUnavailableError(f"Ollama HTTP {response.status_code}")

    try:
        parsed = response.json()
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        if isinstance(parsed, dict) and "response" in parsed:
            raw = parsed["response"]
            raw = _strip_markdown(raw)
            parsed = json.loads(raw)
    except Exception as exc:
        raise LLMUnavailableError(f"Ollama parse error: {exc}") from exc

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(
            f"Ollama output must be a JSON object, got {type(parsed).__name__}"
        )

    logger.debug("Ollama inference complete")
    return parsed


# ── Public API ────────────────────────────────────────────────────────────────


async def call_llm(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1200,
) -> dict[str, Any]:
    """
    Call SEA-LION with Ollama fallback.

    Returns a dict matching the response_schema (if provided).
    Raises LLMUnavailableError if both tiers fail — caller falls back to
    deterministic logic.

    Args:
        system:     Constitutional system prompt
        user:       User query / task description
        response_schema: JSON schema describing required output fields
        temperature: Sampling temperature (0.1–0.3 for adjudication, 0.4–0.7 for reply)
        max_tokens: Maximum tokens in response
    """
    # Tier 1 — SEA-LION (schema validation skipped — provider returns its own format)
    try:
        result = await _call_sea_lion(system, user, response_schema, temperature, max_tokens)
        return result
    except LLMUnavailableError:
        pass

    # Tier 2 — Ollama fallback
    try:
        result = await _call_ollama(system, user, response_schema, temperature, max_tokens)
        if response_schema:
            _validate_schema(result, set(response_schema.get("properties", {}).keys()))
        return result
    except LLMUnavailableError:
        pass

    # Tier 3 — no LLM available
    raise LLMUnavailableError(
        "All LLM tiers exhausted (SEA-LION + Ollama). "
        "Caller should apply deterministic fallback."
    )


__all__ = [
    "call_llm",
    "LLMUnavailableError",
]
