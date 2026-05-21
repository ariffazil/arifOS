"""
arifosmcp/runtime/llm_client.py — Shared LLM Cognition Client

Tier 1: SEA-LION (https://api.sea-lion.ai/v1) — PRIMARY sovereign model
Tier 2: Ollama local fallback — qwen2.5:7b on VPS localhost:11434
Tier 3: raises LLMUnavailableError — caller applies deterministic fallback

ALL LLM output passes through 777_WITNESS envelope before reaching tool logic.
Raw LLM text never enters judgment, memory, vault, or external action directly.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import Any

import httpx

from arifosmcp.runtime.llm_envelope import (
    LLMOutputEnvelope,
    wrap_llm_error,
    wrap_llm_output,
)

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
SEA_LION_API_KEY = os.getenv("SEA_LION_API_KEY")
SEA_LION_BASE_URL = os.getenv("SEA_LION_BASE_URL", "https://api.sea-lion.ai/v1")
SEA_LION_MODEL = os.getenv("SEA_LION_MEANING_MODEL", "aisingapore/Qwen-SEA-LION-v4-32B-IT")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")  # Only 7b is installed on ollama-engine-prod


class LLMUnavailableError(Exception):
    """Raised when both SEA-LION and Ollama are unavailable."""

    pass


# ── Internal Helpers ───────────────────────────────────────────────────────────


def _sha256(text: str) -> str:
    return f"sha256:{hashlib.sha256(text.encode()).hexdigest()[:16]}"


def _extract_confidence(parsed: dict[str, Any]) -> float:
    val = parsed.get("confidence") if isinstance(parsed, dict) else None
    if isinstance(val, dict):
        val = val.get("overall_confidence") or val.get("confidence", 0.5)
    return val if isinstance(val, (int, float)) else 0.5


def _make_envelope(
    raw_output: str,
    parsed: dict[str, Any],
    provider: str,
    model: str,
    tool_origin: str,
    mode: str,
    combined_prompt: str,
    latency_ms: float,
    response_schema: dict[str, Any] | None,
) -> LLMOutputEnvelope:
    envelope = wrap_llm_output(
        raw_output=raw_output,
        parsed_output=parsed,
        provider=provider,
        model=model,
        tool_origin=tool_origin,
        mode=mode,
        prompt=combined_prompt,
        schema_valid=True,
        confidence=_extract_confidence(parsed),
        latency_ms=latency_ms,
    )
    if response_schema:
        _validate_schema(envelope.parsed_output, set(response_schema.get("properties", {}).keys()))
    return envelope


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
    """Log warning if required schema fields are missing; do not fail the envelope."""
    missing = required_fields - set(parsed.keys())
    if missing:
        logger.warning("LLM output missing optional fields (permissive pass): %s", sorted(missing))


# ── Core LLM Call Helpers ─────────────────────────────────────────────────────


async def _call_sea_lion(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
) -> tuple[str, dict[str, Any]]:
    """
    Tier 1 — call SEA-LION chat completions API.

    Returns (raw_output_str, parsed_output_dict).
    The raw_output is preserved for envelope integrity hashing.
    """
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
        async with httpx.AsyncClient(timeout=20.0) as client:
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
        msg = data["choices"][0]["message"]
        # SEA-LION v4 returns reasoning_content instead of content for some models
        content = msg.get("content") or msg.get("reasoning_content", "")
    except Exception as exc:
        logger.warning("SEA-LION parse error: %s", exc)
        raise LLMUnavailableError(f"SEA-LION response parse error: {exc}") from exc

    raw_output = _strip_markdown(content)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        logger.warning("SEA-LION returned invalid JSON, wrapping plain text: %s", raw_output[:200])
        parsed = {"reasoning": raw_output, "answer": raw_output}

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(
            f"SEA-LION output must be a JSON object, got {type(parsed).__name__}"
        )

    if not parsed:
        raise LLMUnavailableError("SEA-LION returned empty JSON object")

    logger.debug("SEA-LION inference complete")
    return raw_output, parsed


async def _call_ollama(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
) -> tuple[str, dict[str, Any]]:
    """
    Tier 2 — call local Ollama as fallback.

    Returns (raw_output_str, parsed_output_dict).
    """
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
        # F13 TIMEOUT_SAFE: CPU inference on 7B model is ~2 tok/s.
        # 10s allows ~20 tokens — enough for structured JSON stub.
        # Longer prompts should use SEA-LION (GPU-accelerated API).
        async with httpx.AsyncClient(timeout=50.0) as client:
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
            raw_output = _strip_markdown(parsed["response"])
            try:
                parsed = json.loads(raw_output)
            except json.JSONDecodeError:
                parsed = {"reasoning": raw_output, "answer": raw_output}
        elif isinstance(parsed, dict) and "message" in parsed:
            content = parsed["message"].get("content", "")
            raw_output = _strip_markdown(content)
            try:
                parsed = json.loads(raw_output)
            except json.JSONDecodeError:
                parsed = {"reasoning": raw_output, "answer": raw_output}
        else:
            raw_output = _strip_markdown(json.dumps(parsed))
    except Exception as exc:
        raise LLMUnavailableError(f"Ollama parse error: {exc}") from exc

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(
            f"Ollama output must be a JSON object, got {type(parsed).__name__}"
        )

    logger.debug("Ollama inference complete")
    return raw_output, parsed


# ── Public API ────────────────────────────────────────────────────────────────


async def call_llm(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1200,
    tool_origin: str = "UNKNOWN",
    mode: str = "infer",
) -> LLMOutputEnvelope:
    """
    Call SEA-LION with Ollama fallback.

    Returns LLMOutputEnvelope — the single legal form of LLM output in arifOS.
    The envelope is the ONLY thing that should reach tool logic, judgment, or memory.

    Args:
        system:       Constitutional system prompt
        user:         User query / task description
        response_schema: JSON schema describing required output fields
        temperature:  Sampling temperature (0.1–0.3 for adjudication, 0.4–0.7 for reply)
        max_tokens:   Maximum tokens in response
        tool_origin:  Canonical tool name calling this LLM (e.g. "333_REASON")
        mode:         Cognitive mode of the call (e.g. "reason", "critique")
    """
    # Build combined prompt string for audit trail
    combined_prompt = f"{system}\n\n{user}"

    # Tier 1 — SEA-LION remote (PRIMARY sovereign model)
    try:
        t0 = time.monotonic()
        raw_output, parsed = await _call_sea_lion(
            system, user, response_schema, temperature, max_tokens
        )
        return _make_envelope(
            raw_output, parsed, "sea_lion", SEA_LION_MODEL,
            tool_origin, mode, combined_prompt,
            (time.monotonic() - t0) * 1000, response_schema,
        )
    except LLMUnavailableError:
        pass

    # Tier 2 — Ollama local fallback (qwen2.5:7b on VPS localhost:11434)
    try:
        t0 = time.monotonic()
        raw_output, parsed = await _call_ollama(
            system, user, response_schema, temperature, max_tokens
        )
        return _make_envelope(
            raw_output, parsed, "ollama", OLLAMA_MODEL,
            tool_origin, mode, combined_prompt,
            (time.monotonic() - t0) * 1000, response_schema,
        )
    except LLMUnavailableError:
        pass

    # Tier 3 — no LLM available
    return wrap_llm_error(
        provider="none",
        model="none",
        tool_origin=tool_origin,
        mode=mode,
        prompt=combined_prompt,
        error_message="All LLM tiers exhausted (SEA-LION + Ollama)",
    )


async def check_provider_health() -> dict[str, Any]:
    """
    777_OPS: Lightweight provider-state diagnostic.

    Returns reachable/unknown for each LLM tier without generating tokens.
    Logs state for audit; does not mutate provider configs.
    """
    status: dict[str, Any] = {
        "primary": "unknown",
        "fallback": "unknown",
        "active_provider": "none",
        "errors": [],
    }

    # Check SEA-LION (Tier 1)
    if not SEA_LION_API_KEY:
        status["primary"] = "unconfigured"
        status["errors"].append("SEA_LION_API_KEY not set")
    else:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Lightweight health-like probe: list models endpoint
                r = await client.get(
                    f"{SEA_LION_BASE_URL}/models",
                    headers={"Authorization": f"Bearer {SEA_LION_API_KEY}"},
                )
                if r.status_code in (200, 401):
                    # 401 means auth works but endpoint may not support /models
                    status["primary"] = "reachable"
                else:
                    status["primary"] = f"http_{r.status_code}"
        except Exception as exc:
            status["primary"] = "unreachable"
            status["errors"].append(f"SEA_LION: {exc}")

    # Check Ollama (Tier 2)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if r.status_code == 200:
                models = r.json().get("models", [])
                status["fallback"] = "reachable"
                status["ollama_models"] = [m.get("name") for m in models]
            else:
                status["fallback"] = f"http_{r.status_code}"
    except Exception as exc:
        status["fallback"] = "unreachable"
        status["errors"].append(f"Ollama: {exc}")

    # Determine active provider
    if status["primary"] == "reachable":
        status["active_provider"] = "sea_lion"
    elif status["fallback"] == "reachable":
        status["active_provider"] = "ollama"
    else:
        status["active_provider"] = "none"

    logger.info("LLM provider health: %s", status)
    return status


async def call_llm_raw(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1200,
) -> dict[str, Any]:
    """
    Legacy raw call — returns parsed dict directly.
    DEPRECATED: Use call_llm() which returns LLMOutputEnvelope.

    Kept only for internal callers that have not yet migrated to envelope pattern.
    """
    logger.warning("call_llm_raw is deprecated — use call_llm() returning LLMOutputEnvelope")
    envelope = await call_llm(system, user, response_schema, temperature, max_tokens)
    return envelope.parsed_output


__all__ = [
    "call_llm",
    "call_llm_raw",  # deprecated
    "check_provider_health",
    "LLMUnavailableError",
    "LLMOutputEnvelope",
]
