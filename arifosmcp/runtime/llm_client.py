"""
arifosmcp/runtime/llm_client.py — Shared LLM Cognition Client

Tier 1: MiniMax M3 (https://api.minimax.io/v1) — PRIMARY frontier model (L13 directive 2026-06-02)
Tier 2: Ollama local fallback — qwen2.5:7b on VPS localhost:11434
Tier 3: raises LLMUnavailableError — caller applies deterministic fallback

Migration note: Replaced SEA-LION (unreachable) with MiniMax-M3 per L13 SOVEREIGN.
SEA-LION env vars retained in /etc/arifos/arifos.env for potential future reactivation.

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
from arifosmcp.runtime.m3_agentic import (
    AgentRole,
    get_m3_header,
    is_m3_model,
)

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
# Tier 1 — MiniMax M3 (frontier agentic operator, MSA architecture, 1M ctx, native multimodal)
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_BASE_URL = os.getenv("MINIMAX_API_HOST", "https://api.minimax.io")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M3")

# Tier 2 — Ollama local fallback (qwen2.5:7b, free, no API cost)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")  # Only 7b is installed on ollama-engine-prod

# Tier 2.5 — ILMU hosted fallback (2026-06-03, replaces ollama as Tier 2)
# ILMU is OpenAI-compatible. Faster than ollama on CPU. Wired per 888_HOLD.
# Env: ILMU_API_KEY, ILMU_BASE_URL, ILMU_MODEL. If unset → falls through to ollama.
ILMU_BASE_URL = os.getenv("ILMU_BASE_URL", "https://api.ilmu.ai/v1")
ILMU_MODEL = os.getenv("ILMU_MODEL", "ilmu-nemo-nano")
ILMU_API_KEY = os.getenv("ILMU_API_KEY", "")
ILMU_ENABLED = bool(ILMU_API_KEY)  # only active when key is configured

# Tier 2 — ILMU Console (hosted hosted fallback, replaces ollama for text generation 2026-06-03)
# OpenAI-compatible chat/completions endpoint. Used by arifOS when MiniMax M3 is unreachable.
ILMU_API_KEY = os.getenv("ILMU_API_KEY")
ILMU_BASE_URL = os.getenv("ILMU_BASE_URL", "https://api.ilmu.ai/v1")
ILMU_MODEL = os.getenv("ILMU_MODEL", "ilmu-nemo-nano")

# Legacy — SEA-LION retained in env for reactivation, no longer in cascade
SEA_LION_API_KEY = os.getenv("SEA_LION_API_KEY")
SEA_LION_BASE_URL = os.getenv("SEA_LION_BASE_URL", "https://api.sea-lion.ai/v1")
SEA_LION_MODEL = os.getenv("SEA_LION_MEANING_MODEL", "aisingapore/Qwen-SEA-LION-v4-32B-IT")


class LLMUnavailableError(Exception):
    """Raised when both MiniMax M3 and Ollama are unavailable."""

    pass


# ── Internal Helpers ───────────────────────────────────────────────────────────


def _extract_m3_role_from_system(system: str) -> AgentRole | None:
    """Detect if the caller's system prompt already specifies a role.

    Looks for a line like: ROLE: leader  or  ROLE=worker  or  # role: verifier
    Returns the role if found, else None (caller didn't specify, default to WORKER).
    """
    if not system:
        return None
    lowered = system.lower()
    for role in AgentRole:
        for marker in (f"role: {role.value}", f"role={role.value}", f"[{role.value}]"):
            if marker in lowered:
                return role
    return None


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
    trace_recursion_depth: int = 0,
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
        trace_recursion_depth=trace_recursion_depth,
    )
    if response_schema:
        _validate_schema(envelope.parsed_output, set(response_schema.get("properties", {}).keys()))
    return envelope


def _strip_think_tags(content: str) -> str:
    """Strip <｜end▁of▁thinking｜> tags from LLM output before parsing.

    MiniMax M3 returns reasoning_content as a separate field, but some
    providers inline  in the content itself. This prevents
    CoT from leaking into parsed_output (F11 AUTH — model internals
    must never reach the audit surface)."""
    import re

    # Remove  blocks including any content between them
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
    # Also catch unclosed <think> tags (model truncated mid-thought)
    content = re.sub(r"<think>.*", "", content, flags=re.DOTALL)
    return content.strip()


def _strip_markdown(content: str) -> str:
    """Strip markdown code fences from LLM output."""
    content = _strip_think_tags(content)
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
    LEGACY — call SEA-LION chat completions API.

    Replaced by _call_minimax (M3) as Tier 1 on 2026-06-02.
    Retained for potential future reactivation — not in current cascade.

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


async def _call_minimax(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
) -> tuple[str, dict[str, Any]]:
    """
    Tier 1 — call MiniMax M3 (frontier agentic operator) via OpenAI-compatible API.

    MSA architecture, 1M context, native multimodal (text/image/video).
    Returns (raw_output_str, parsed_output_dict).
    The raw_output is preserved for envelope integrity hashing.
    """
    if not MINIMAX_API_KEY:
        raise LLMUnavailableError("MINIMAX_API_KEY not configured")

    # M3 agentic contract injection: when calling M3, prepend the role-specific
    # header (Leader/Worker/Verifier + shared base) to the system prompt. The
    # caller's system prompt is preserved as the tail (caller-specific framing).
    # Caller can opt out by prepending the header themselves (idempotent: we
    # detect an already-tagged prompt by the [arifos-m3-header] marker).
    system_with_header = system
    if is_m3_model(MINIMAX_MODEL):
        role = _extract_m3_role_from_system(system) or AgentRole.WORKER
        header = get_m3_header(role)
        if "[arifos-m3-header]" not in system:
            system_with_header = header + "\n\n" + system

    messages = [{"role": "system", "content": system_with_header}]
    if user:
        messages.append({"role": "user", "content": user})

    payload: dict[str, Any] = {
        "model": MINIMAX_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    t0 = time.monotonic()
    try:
        # M3 with thinking enabled can be slower than typical LLMs (60s+)
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{MINIMAX_BASE_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {MINIMAX_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except Exception as exc:
        logger.warning("MiniMax M3 transport error: %s", exc)
        raise LLMUnavailableError(f"MiniMax M3 transport error: {exc}") from exc

    if response.status_code != 200:
        logger.warning("MiniMax M3 HTTP %s: %s", response.status_code, response.text[:200])
        try:
            from arifosmcp.runtime.metrics import record_m3_usage

            record_m3_usage(
                prompt_tokens=0,
                completion_tokens=0,
                cached_tokens=0,
                latency_seconds=time.monotonic() - t0,
                status="error",
            )
        except Exception:
            pass
        raise LLMUnavailableError(f"MiniMax M3 HTTP {response.status_code}")

    try:
        data = response.json()
        msg = data["choices"][0]["message"]
        # M3 returns reasoning_content separately when thinking is enabled.
        # NEVER use reasoning_content as the output — it is the model's internal
        # chain-of-thought and must not leak to the audit surface (F11 AUTH).
        # If content is empty but reasoning_content exists, the model failed
        # to produce a usable answer — treat as empty content, not fallback.
        content = msg.get("content", "")
        if not content and msg.get("reasoning_content"):
            logger.warning(
                "MiniMax M3 returned reasoning_content without content — "
                "model thought but did not answer. Using empty content."
            )
    except Exception as exc:
        logger.warning("MiniMax M3 parse error: %s", exc)
        try:
            from arifosmcp.runtime.metrics import record_m3_usage

            record_m3_usage(
                prompt_tokens=0,
                completion_tokens=0,
                cached_tokens=0,
                latency_seconds=time.monotonic() - t0,
                status="error",
            )
        except Exception:
            pass
        raise LLMUnavailableError(f"MiniMax M3 response parse error: {exc}") from exc

    # Record M3 token usage (F2 TRUTH observability)
    try:
        from arifosmcp.runtime.metrics import record_m3_usage

        usage = data.get("usage", {}) or {}
        prompt_tokens = int(usage.get("prompt_tokens", 0))
        completion_tokens = int(usage.get("completion_tokens", 0))
        cached_tokens = int((usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0))
        record_m3_usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens,
            latency_seconds=time.monotonic() - t0,
            status="success",
        )
    except Exception:
        # Metrics must never break the call path
        pass

    raw_output = _strip_markdown(content)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        # P1-20260610: When LLM fails to return valid JSON, do NOT dump raw
        # text (including potential CoT remnants) into reasoning/answer.
        # Instead return a structured error the caller can handle.
        logger.warning("MiniMax M3 returned invalid JSON (first 100 chars): %s", raw_output[:100])
        parsed = {
            "status": "HOLD",
            "verdict": "HOLD",
            "reason": "llm_schema_violation",
            "reasoning": "LLM returned non-JSON output. Raw output logged for debugging.",
            "answer": "Unable to parse LLM response. Check server logs.",
            "_raw_output_hash": hashlib.sha256(raw_output.encode()).hexdigest()[:16],
        }

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(
            f"MiniMax M3 output must be a JSON object, got {type(parsed).__name__}"
        )

    if not parsed:
        raise LLMUnavailableError("MiniMax M3 returned empty JSON object")

    logger.debug("MiniMax M3 inference complete (model=%s)", MINIMAX_MODEL)
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
        # L13 TIMEOUT_SAFE: CPU inference on 7B model is ~2 tok/s.
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
                if not isinstance(parsed, dict):
                    parsed = {"reasoning": raw_output, "answer": raw_output}
            except json.JSONDecodeError:
                parsed = {"reasoning": raw_output, "answer": raw_output}
        elif isinstance(parsed, dict) and "message" in parsed:
            content = parsed["message"].get("content", "")
            raw_output = _strip_markdown(content)
            try:
                parsed = json.loads(raw_output)
                if not isinstance(parsed, dict):
                    parsed = {"reasoning": raw_output, "answer": raw_output}
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


async def _call_ilmu(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
) -> tuple[str, dict[str, Any]]:
    """
    Tier 2 — call ILMU Console (ilmu-nemo-nano) as hosted fallback.

    OpenAI-compatible /v1/chat/completions endpoint at api.ilmu.ai.
    Migrated into the cascade 2026-06-03 18:50 UTC to relieve local ollama
    (qwen2.5:7b on CPU was 0.076 tok/s — see audit/2026-06-03-audit-and-clean-report.md).

    Returns (raw_output_str, parsed_output_dict).
    """
    if not ILMU_API_KEY:
        raise LLMUnavailableError("ILMU_API_KEY not configured")

    messages = [{"role": "system", "content": system}]
    if user:
        messages.append({"role": "user", "content": user})

    payload: dict[str, Any] = {
        "model": ILMU_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        # ILMU is a hosted API — 50s is generous; typical responses are <5s.
        async with httpx.AsyncClient(timeout=50.0) as client:
            response = await client.post(
                f"{ILMU_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {ILMU_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except Exception as exc:
        logger.warning("ILMU transport error: %s", exc)
        raise LLMUnavailableError(f"ILMU unavailable: {exc}") from exc

    if response.status_code != 200:
        logger.warning("ILMU HTTP %s: %s", response.status_code, response.text[:200])
        raise LLMUnavailableError(f"ILMU HTTP {response.status_code}")

    try:
        data = response.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content", "") or msg.get("reasoning_content", "")
    except Exception as exc:
        logger.warning("ILMU parse error: %s", exc)
        raise LLMUnavailableError(f"ILMU response parse error: {exc}") from exc

    raw_output = _strip_markdown(content)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        logger.warning("ILMU returned invalid JSON, wrapping plain text: %s", raw_output[:200])
        parsed = {"reasoning": raw_output, "answer": raw_output}

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(f"ILMU output must be a JSON object, got {type(parsed).__name__}")

    if not parsed:
        raise LLMUnavailableError("ILMU returned empty JSON object")

    logger.debug("ILMU inference complete (model=%s)", ILMU_MODEL)
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
    trace_recursion_depth: int = 0,
) -> LLMOutputEnvelope:
    """
    Call MiniMax M3 (Tier 1, frontier agentic) with Ollama fallback (Tier 2).

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
        trace_recursion_depth: current recursion depth in the call chain
    """
    # Build combined prompt string for audit trail
    combined_prompt = f"{system}\n\n{user}"

    # Tier 0 — Deterministic fallback for test/diagnostic modes
    if mode in {"smoke", "ping", "health", "schema_check", "diagnostic", "status"}:
        t0 = time.monotonic()
        parsed = {
            "status": "HOLD",
            "verdict": "HOLD",
            "reason": "provider_timeout_or_unavailable",
            "reasoning": "Deterministic fallback engaged.",
        }
        return _make_envelope(
            json.dumps(parsed),
            parsed,
            "deterministic_fallback",
            "mock-model",
            tool_origin,
            mode,
            combined_prompt,
            (time.monotonic() - t0) * 1000,
            None,  # skip strict schema validation
            trace_recursion_depth,
        )

    # Tier 1 — MiniMax M3 (PRIMARY frontier model, L13 directive 2026-06-02)
    try:
        t0 = time.monotonic()
        raw_output, parsed = await _call_minimax(
            system, user, response_schema, temperature, max_tokens
        )
        return _make_envelope(
            raw_output,
            parsed,
            "minimax",
            MINIMAX_MODEL,
            tool_origin,
            mode,
            combined_prompt,
            (time.monotonic() - t0) * 1000,
            response_schema,
            trace_recursion_depth,
        )
    except LLMUnavailableError:
        pass

    # Tier 2 — ILMU hosted fallback (ilmu-nemo-nano, OpenAI-compatible, added 2026-06-03)
    # Replaces ollama for text generation — CPU ollama was 0.076 tok/s, ILMU is fast.
    try:
        t0 = time.monotonic()
        raw_output, parsed = await _call_ilmu(
            system, user, response_schema, temperature, max_tokens
        )
        return _make_envelope(
            raw_output,
            parsed,
            "ilmu",
            ILMU_MODEL,
            tool_origin,
            mode,
            combined_prompt,
            (time.monotonic() - t0) * 1000,
            response_schema,
            trace_recursion_depth,
        )
    except LLMUnavailableError:
        pass

    # Tier 2b — Ollama local fallback (qwen2.5:7b on VPS localhost:11434, free)
    # Last-resort before Tier 3. Kept for the rare case both MiniMax and ILMU are down.
    try:
        t0 = time.monotonic()
        raw_output, parsed = await _call_ollama(
            system, user, response_schema, temperature, max_tokens
        )
        return _make_envelope(
            raw_output,
            parsed,
            "ollama",
            OLLAMA_MODEL,
            tool_origin,
            mode,
            combined_prompt,
            (time.monotonic() - t0) * 1000,
            response_schema,
            trace_recursion_depth,
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
        error_message="All LLM tiers exhausted (MiniMax M3 + ILMU + Ollama)",
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

    # Check MiniMax M3 (Tier 1)
    if not MINIMAX_API_KEY:
        status["primary"] = "unconfigured"
        status["errors"].append("MINIMAX_API_KEY not set")
    else:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Lightweight health-like probe: list models endpoint
                r = await client.get(
                    f"{MINIMAX_BASE_URL}/v1/models",
                    headers={"Authorization": f"Bearer {MINIMAX_API_KEY}"},
                )
                if r.status_code in (200, 401):
                    # 401 means auth works but endpoint may not support /models
                    status["primary"] = "reachable"
                else:
                    status["primary"] = f"http_{r.status_code}"
        except Exception as exc:
            status["primary"] = "unreachable"
            status["errors"].append(f"MiniMax M3: {exc}")

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
        status["active_provider"] = "minimax"
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
