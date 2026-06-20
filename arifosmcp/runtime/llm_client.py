"""
arifosmcp/runtime/llm_client.py — Shared LLM Cognition Client

Tier 1: MiniMax M3 (https://api.minimax.io/v1) — frontier agentic, rate-limited 2026-06-13
Tier 1.5: Azure OpenAI (gpt-4.1-mini) — reliable cheap fallback
Tier 2: SEA-LION v4 (https://api.sea-lion.ai/v1) — GPU API, intermittent
Tier 3: raises LLMUnavailableError — caller applies deterministic fallback

ILMU (ilmu-nemo-nano) — BLOCKED per FFF 2026-06-15.
  F13 inversion, register-dependent hallucination, L02A parse failure,
  institutional capture. Removed from cascade. Retained in config for
  audit trail only. See ariffazil/BBB, CCC, DDD, FFF for full receipts.

Ollama (localhost:11434) is reserved for EMBEDDING only (bge-m3).
It is NOT used for text generation — removed 2026-06-16 (Tier 4 was a ghost
reference to llava:7b which was never pulled).

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

# Tier 1.5 — Azure OpenAI (gpt-4.1-mini, ProCopilot $200 credit)
# Wired 2026-06-20. Sits between MiniMax (Tier 1) and ILMU (Tier 2)
# as a reliable, cheap fallback when MiniMax is rate-limited.
# Azure is OpenAI-compatible — uses same httpx pattern as ILMU.
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1-mini")

# Ollama — EMBEDDING ONLY (bge-m3). NOT used for text generation.
# Removed 2026-06-16: llava:7b generation tier was a ghost reference (never pulled).
# Ollama is retained solely for bge-m3 embeddings (arifbrain, L3 ingest, AAA).
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_URL", "http://localhost:11434")

# Tier 2.5 — ILMU hosted fallback (2026-06-03, replaces ollama as Tier 2)
# BLOCKED per FFF 2026-06-15. Removed from cascade.
# F13 inversion, register-dependent hallucination, L02A parse failure.
# Retained in config for audit trail only.
# Env: ILMU_API_KEY, ILMU_BASE_URL, ILMU_MODEL. If unset → falls through.
ILMU_BASE_URL = os.getenv("ILMU_BASE_URL", "https://api.ilmu.ai/v1")
ILMU_MODEL = os.getenv("ILMU_MODEL", "ilmu-nemo-nano")
ILMU_API_KEY = os.getenv("ILMU_API_KEY", "")
ILMU_ENABLED = False  # BLOCKED per FFF 2026-06-15 — do not re-enable without F13 directive

# Tier 2 — ILMU Console (hosted fallback)
# BLOCKED per FFF 2026-06-15. Removed from cascade.
# Retained in config for audit trail only.
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


def _repair_truncated_json(raw: str, min_viable_keys: set[str] | None = None) -> dict[str, Any] | None:
    """Attempt to repair truncated/incomplete JSON from LLM output.

    LLMs (especially via slower tiers like SEA-LION) often truncate complex
    structured JSON at the max_tokens boundary. This function attempts to
    salvage partial results by closing unterminated strings, objects, and arrays.

    Returns a parsed dict if repair succeeds AND the result contains at least
    the min_viable_keys (if specified). Returns None if repair is impossible
    or the result is too degraded.

    F2 TRUTH: Repaired JSON is always marked with _json_repaired=True so
    downstream consumers can adjust confidence accordingly.
    """
    if min_viable_keys is None:
        min_viable_keys = set()

    raw = raw.strip()
    if not raw:
        return None

    # Strategy 1: If the JSON ends with an unclosed string (trailing quote missing),
    # try appending the closing quote + any missing structural close tokens.
    strategies: list[str] = []

    # Detect trailing state
    in_string = False
    escape_next = False
    depth_brace = 0  # {
    depth_bracket = 0  # [
    for ch in raw:
        if escape_next:
            escape_next = False
            continue
        if ch == "\\":
            escape_next = True
            continue
        if ch == '"' and not escape_next:
            in_string = not in_string
        elif not in_string:
            if ch == "{":
                depth_brace += 1
            elif ch == "}":
                depth_brace -= 1
            elif ch == "[":
                depth_bracket += 1
            elif ch == "]":
                depth_bracket -= 1

    # Build repair suffixes
    suffixes: list[str] = []

    # If we're inside a string, close it
    if in_string:
        suffixes.append('"')

    # Close any open structures
    if depth_bracket > 0:
        suffixes.append("]" * depth_bracket)
    if depth_brace > 0:
        suffixes.append("}" * depth_brace)

    if suffixes:
        strategies.append(raw + "".join(suffixes))

    # Strategy 2: Also try with a trailing quote before structural closure
    # (for cases where both string AND structure are unterminated)
    if in_string and (depth_bracket > 0 or depth_brace > 0):
        alt = raw + '"' + "]" * depth_bracket + "}" * depth_brace
        if alt not in strategies:
            strategies.append(alt)

    # Strategy 3: Truncate to last valid comma and close structures
    # Find the last comma that's at structural depth
    last_comma = raw.rfind(",")
    if last_comma > len(raw) // 2:  # Only if we're keeping more than half
        truncated = raw[:last_comma]
        # Close any structures that were open at that point
        # Recompute depth up to truncation point
        b_depth = 0
        bk_depth = 0
        in_s = False
        esc = False
        for ch in truncated:
            if esc:
                esc = False
                continue
            if ch == "\\":
                esc = True
                continue
            if ch == '"' and not esc:
                in_s = not in_s
            elif not in_s:
                if ch == "{":
                    b_depth += 1
                elif ch == "}":
                    b_depth -= 1
                elif ch == "[":
                    bk_depth += 1
                elif ch == "]":
                    bk_depth -= 1
        repair = truncated
        if in_s:
            repair += '"'
        repair += "]" * max(0, bk_depth) + "}" * max(0, b_depth)
        if repair not in strategies:
            strategies.append(repair)

    for attempt in strategies:
        try:
            parsed = json.loads(attempt)
            if isinstance(parsed, dict):
                missing = min_viable_keys - set(parsed.keys())
                if not missing:
                    parsed["_json_repaired"] = True
                    logger.info(
                        "Repaired truncated JSON (strategy %d chars added). "
                        "Keys recovered: %s",
                        len(attempt) - len(raw),
                        list(parsed.keys()),
                    )
                    return parsed
                else:
                    logger.debug(
                        "Repaired JSON parses but missing critical keys: %s",
                        sorted(missing),
                    )
        except json.JSONDecodeError:
            continue

    return None


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
        async with httpx.AsyncClient(timeout=25.0) as client:
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
        # Attempt to repair truncated JSON before giving up
        repaired = _repair_truncated_json(raw_output)
        if repaired is not None:
            logger.info("SEA-LION JSON repaired after truncation (keys: %s)", list(repaired.keys()))
            parsed = repaired
            raw_output = json.dumps(repaired)  # Align raw with repaired for hash integrity
        else:
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
        # Attempt to repair truncated JSON before giving up
        repaired = _repair_truncated_json(raw_output)
        if repaired is not None:
            logger.info("MiniMax M3 JSON repaired after truncation (keys: %s)", list(repaired.keys()))
            parsed = repaired
            raw_output = json.dumps(repaired)
        else:
            # DDD-20260611: When M3 returns free-form text instead of JSON, wrap
            # the raw output into reasoning/answer so the kernel envelope can
            # surface the LLM's actual response. The constitutional wrapper
            # (F1-F13) will then metabolize the *real* M3 text, not a generic
            # "unable to parse" placeholder. This mirrors the SEA-LION parser
            # pattern at line 237-238. The L02 envelope is still issued
            # (status=HOLD, verdict=HOLD) so the kernel's downstream contract
            # is preserved — the difference is that the *raw LLM text* is now
            # visible to the operator via reasoning/answer rather than thrown
            # away. F1 AMANAH reversible: only the invalid-JSON path is
            # affected; valid JSON paths are untouched.
            logger.warning("MiniMax M3 returned invalid JSON (first 100 chars): %s", raw_output[:100])
            parsed = {
                "status": "HOLD",
                "verdict": "HOLD",
                "reason": "llm_schema_violation",
                "reasoning": raw_output,
                "answer": raw_output,
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


async def _call_azure(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
) -> tuple[str, dict[str, Any]]:
    """
    Tier 1.5 — call Azure OpenAI gpt-4.1-mini (ProCopilot $200 credit).

    OpenAI-compatible /v1/chat/completions at Azure endpoint.
    Wired 2026-06-20 per Arif's 888_HOLD. Sits between MiniMax (Tier 1)
    and ILMU (Tier 2) as a reliable, cheap fallback.

    Returns (raw_output_str, parsed_output_dict).
    """
    if not AZURE_OPENAI_KEY:
        raise LLMUnavailableError("AZURE_OPENAI_KEY not configured")

    messages = [{"role": "system", "content": system}]
    if user:
        messages.append({"role": "user", "content": user})

    payload: dict[str, Any] = {
        "model": AZURE_OPENAI_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{AZURE_OPENAI_ENDPOINT}/chat/completions",
                headers={
                    "api-key": AZURE_OPENAI_KEY,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except Exception as exc:
        logger.warning("Azure OpenAI transport error: %s", exc)
        raise LLMUnavailableError(f"Azure OpenAI unavailable: {exc}") from exc

    if response.status_code != 200:
        logger.warning("Azure OpenAI HTTP %s: %s", response.status_code, response.text[:200])
        raise LLMUnavailableError(f"Azure OpenAI HTTP {response.status_code}")

    try:
        data = response.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content", "")
    except Exception as exc:
        logger.warning("Azure OpenAI parse error: %s", exc)
        raise LLMUnavailableError(f"Azure OpenAI response parse error: {exc}") from exc

    raw_output = _strip_markdown(content)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        logger.warning("Azure OpenAI returned invalid JSON, wrapping plain text: %s", raw_output[:200])
        parsed = {"reasoning": raw_output, "answer": raw_output}

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(f"Azure OpenAI output must be a JSON object, got {type(parsed).__name__}")

    if not parsed:
        raise LLMUnavailableError("Azure OpenAI returned empty JSON object")

    logger.debug("Azure OpenAI inference complete (model=%s)", AZURE_OPENAI_MODEL)
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
        # 15s allows ~30 tokens — enough for structured JSON stub.
        # Longer prompts should use SEA-LION (GPU-accelerated API).
        # Previously 50s; reduced 2026-06-13 to prevent Ollama from
        # blocking faster upstream providers in the cascade.
        async with httpx.AsyncClient(timeout=15.0) as client:
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
                repaired = _repair_truncated_json(raw_output)
                if repaired is not None:
                    logger.info("Ollama JSON repaired after truncation (keys: %s)", list(repaired.keys()))
                    parsed = repaired
                    raw_output = json.dumps(repaired)
                else:
                    parsed = {"reasoning": raw_output, "answer": raw_output}
        elif isinstance(parsed, dict) and "message" in parsed:
            content = parsed["message"].get("content", "")
            raw_output = _strip_markdown(content)
            try:
                parsed = json.loads(raw_output)
                if not isinstance(parsed, dict):
                    parsed = {"reasoning": raw_output, "answer": raw_output}
            except json.JSONDecodeError:
                repaired = _repair_truncated_json(raw_output)
                if repaired is not None:
                    logger.info("Ollama JSON repaired after truncation (keys: %s)", list(repaired.keys()))
                    parsed = repaired
                    raw_output = json.dumps(repaired)
                else:
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
        # ILMU is a hosted API — 20s is generous; typical responses are <5s.
        async with httpx.AsyncClient(timeout=20.0) as client:
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
    Call MiniMax M3 (Tier 1) → Azure gpt-4.1-mini (Tier 1.5) → ILMU (Tier 2) → SEA-LION (Tier 3).

    Cascade updated 2026-06-20: Azure inserted as Tier 1.5 (ProCopilot $200 credit).
    Azure is OpenAI-compatible, cheap ($0.15/M input), reliable. Sits between
    MiniMax (rate-limited) and ILMU (free but intermittent).
    Original cascade reordered 2026-06-13: ILMU promoted to Tier 2.

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

    # Tier 1 — MiniMax M3 (frontier agentic model, best at structured JSON)
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

    # Tier 1.5 — Azure OpenAI gpt-4.1-mini (ProCopilot $200 credit)
    # Wired 2026-06-20. Sits BETWEEN MiniMax and ILMU. Cheap, reliable,
    # OpenAI-compatible. Falls through if AZURE_OPENAI_KEY is not set.
    try:
        t0 = time.monotonic()
        raw_output, parsed = await _call_azure(
            system, user, response_schema, temperature, max_tokens
        )
        return _make_envelope(
            raw_output,
            parsed,
            "azure_openai",
            AZURE_OPENAI_MODEL,
            tool_origin,
            mode,
            combined_prompt,
            (time.monotonic() - t0) * 1000,
            response_schema,
            trace_recursion_depth,
        )
    except LLMUnavailableError:
        pass

    # Tier 2 — ILMU BLOCKED per FFF 2026-06-15.
    # F13 inversion, register-dependent hallucination, L02A parse failure.
    # Removed from cascade. See ariffazil/BBB, CCC, DDD, FFF for full receipts.
    # To re-enable: set ILMU_ENABLED = True AND obtain F13 SOVEREIGN directive.
    if ILMU_ENABLED:
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

    # Tier 3 — SEA-LION v4 (GPU-accelerated API, intermittent as of 2026-06-13)
    try:
        t0 = time.monotonic()
        raw_output, parsed = await _call_sea_lion(
            system, user, response_schema, temperature, max_tokens
        )
        return _make_envelope(
            raw_output,
            parsed,
            "sea_lion",
            SEA_LION_MODEL,
            tool_origin,
            mode,
            combined_prompt,
            (time.monotonic() - t0) * 1000,
            response_schema,
            trace_recursion_depth,
        )
    except LLMUnavailableError:
        pass

    # Ollama removed 2026-06-16 — was a ghost reference to llava:7b (never pulled).
    # Ollama is retained for bge-m3 embeddings only (arifbrain, L3 ingest, AAA).
    # Text generation cascade: MiniMax → Azure → SEA-LION → fallback.
    # ILMU removed from cascade per FFF 2026-06-15.

    # Tier 4 — no LLM available
    return wrap_llm_error(
        provider="none",
        model="none",
        tool_origin=tool_origin,
        mode=mode,
        prompt=combined_prompt,
        error_message="All LLM tiers exhausted (MiniMax M3 + Azure + SEA-LION). ILMU BLOCKED per FFF.",
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

    # Check MiniMax M3 (Tier 1 — primary)
    if not MINIMAX_API_KEY:
        status["primary"] = "unconfigured"
        status["errors"].append("MINIMAX_API_KEY not set")
    else:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(
                    f"{MINIMAX_BASE_URL}/v1/models",
                    headers={"Authorization": f"Bearer {MINIMAX_API_KEY}"},
                )
                if r.status_code in (200, 401):
                    status["primary"] = "reachable"
                else:
                    status["primary"] = f"http_{r.status_code}"
        except Exception as exc:
            status["primary"] = "unreachable"
            status["errors"].append(f"MiniMax M3: {exc}")

    # Check SEA-LION v4 (Tier 2 — reactivated fallback)
    if not SEA_LION_API_KEY:
        status["sea_lion"] = "unconfigured"
    else:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(
                    f"{SEA_LION_BASE_URL}/models",
                    headers={"Authorization": f"Bearer {SEA_LION_API_KEY}"},
                )
                if r.status_code in (200, 401):
                    status["sea_lion"] = "reachable"
                else:
                    status["sea_lion"] = f"http_{r.status_code}"
        except Exception as exc:
            status["sea_lion"] = "unreachable"
            status["errors"].append(f"SEA-LION: {exc}")

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

    # Determine active provider (match cascade: MiniMax → Azure → SEA-LION → fallback)
    # ILMU BLOCKED per FFF 2026-06-15 — not in cascade
    if status["primary"] == "reachable":
        status["active_provider"] = "minimax"
    elif status.get("azure_openai") == "reachable":
        status["active_provider"] = "azure_openai"
    elif status.get("sea_lion") == "reachable":
        status["active_provider"] = "sea_lion"
    elif status.get("ilmu") == "reachable":
        status["active_provider"] = "ilmu_blocked_fff"
        status["ilmu_status"] = "BLOCKED per FFF 2026-06-15 — not in cascade"
    elif status.get("fallback") == "reachable":
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
