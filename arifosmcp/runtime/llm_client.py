"""
arifosmcp/runtime/llm_client.py — Shared LLM Cognition Client

APEX Theory applied (TokenRouter primary gateway):
- TokenRouter (https://api.tokenrouter.com/v1) — PRIMARY for all organs.
  Organ/task-aware routing (quality/cost/latency modes per spec):
    GEOX: petrophysics=deepseek-v4-pro (1M quality), basin screen=flash (cost), seismic=glm-5.1 (spatial)
    WEALTH: emv/npv=cost-fast, risk=deep-reasoner (quality), market=latency
    WELL: cost mode only + PII firewalls (reflect-only)
- Direct fallbacks (MiniMax/MiMo) for redundancy: federation survives single provider failure.
- TokenRouter + direct = sovereignty + resilience.

Tier 0 (TokenRouter) → Tier 1 (MiniMax) → Tier 1.5 (MiMo) → Tier 2 (Groq FREE → Gemini FREE) → etc. as fallback.

ILMU BLOCKED. Ollama EMBEDDING only.

ALL output via 777_WITNESS envelope.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from arifosmcp.runtime.llm_envelope import LLMOutputEnvelope, wrap_llm_output
from arifosmcp.runtime.m3_agentic import (
    AgentRole,
    get_m3_header,
    is_m3_model,
)

logger = logging.getLogger(__name__)


# ── Configuration ─────────────────────────────────────────────────────────────
# Tier 0 — TokenRouter (OpenAI-compatible proxy)
# P1 HARDENING (2026-06-28): Key loaded from /root/.secrets/tokenrouter.env.
# Env var TOKENROUTER_API_KEY overrides the file.
# Base URL and model have sensible defaults.
def _load_tokenrouter_config() -> dict[str, str]:
    """Load TokenRouter config from secrets file, with env var override."""
    cfg = {"key": "", "url": "https://api.tokenrouter.com/v1", "model": "MiniMax-M3"}
    # Env var takes highest priority
    cfg["key"] = os.getenv("TOKENROUTER_API_KEY", "")
    cfg["url"] = os.getenv("TOKENROUTER_BASE_URL", cfg["url"])
    cfg["model"] = os.getenv("TOKENROUTER_MODEL", cfg["model"])
    # Fallback: load from secrets file
    if not cfg["key"]:
        secrets_file = Path("/root/.secrets/tokenrouter.env")
        try:
            if secrets_file.exists():
                for line in secrets_file.read_text().splitlines():
                    line = line.strip()
                    if line.startswith("TOKENROUTER_API_KEY="):
                        cfg["key"] = line.split("=", 1)[1].strip()
                    elif line.startswith("TOKENROUTER_BASE_URL="):
                        cfg["url"] = line.split("=", 1)[1].strip()
                    elif line.startswith("TOKENROUTER_MODEL="):
                        cfg["model"] = line.split("=", 1)[1].strip()
        except (PermissionError, OSError):
            pass
    return cfg


_tokenrouter_cfg = _load_tokenrouter_config()
TOKENROUTER_API_KEY = _tokenrouter_cfg["key"]
TOKENROUTER_BASE_URL = _tokenrouter_cfg["url"]
TOKENROUTER_MODEL = _tokenrouter_cfg["model"]

# Tier 1 — MiniMax M3 (frontier agentic operator, MSA architecture, 1M ctx, native multimodal)
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
MINIMAX_BASE_URL = os.getenv("MINIMAX_API_HOST", "https://api.minimax.io")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M3")

# Tier 1.5 — MiMo (TokenPlan mimo-v2.5-pro, Arif's primary model)
# Replaces Azure per Arif directive 2026-06-27.
# M3 ↔ MiMo loop: MiniMax M3 (primary reasoning) ↔ MiMo (secondary/parallel).
# OpenAI-compatible /v1/chat/completions at TokenPlan endpoint.
MIMO_API_KEY = os.getenv("MIMO_API_KEY")
MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://token-plan-sgp.xiaomimimo.com/v1")
MIMO_MODEL = os.getenv("MIMO_DEFAULT_MODEL", "mimo-v2.5-pro")

# Tier 2 — Groq LPU (FREE tier, ultra-fast inference, no credit card required)
# All models included in free tier: 560-1000 t/s, 128K context.
# Rate limits: llama-3.1-8b-instant = 14,400 req/day (most generous),
#              llama-3.3-70b = 1,000 req/day, gpt-oss-120b = 1,000 req/day.
# OpenAI-compatible /v1/chat/completions endpoint.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Tier 2 — Google Gemini (FREE tier, 1,500 req/day, 250K TPM, no credit card)
# OpenAI-compatible at v1beta/openai endpoint.
# Best free-tier model: gemini-2.5-flash (1M ctx, multimodal, reasoning).
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai"
)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Tier 2 — Cerebras ($5 free credit, expires Aug 20 2026, OpenAI-compatible)
# Fast inference on wafer-scale hardware. Models: gemma-4-31b, gpt-oss-120b, zai-glm-4.7.
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
CEREBRAS_BASE_URL = os.getenv("CEREBRAS_BASE_URL", "https://api.cerebras.ai/v1")
CEREBRAS_MODEL = os.getenv("CEREBRAS_MODEL", "gpt-oss-120b")

# Ollama — local text-generation fallback after SEA-LION.
# bge-m3 embedding use remains independent of this guarded fallback path.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
# CPU-only local generation is too slow for the governed request path. Keep it
# opt-in while retaining Ollama as the independent bge-m3 embedding backend.
OLLAMA_TEXT_ENABLED = os.getenv("OLLAMA_TEXT_ENABLED", "false").lower() in {"1", "true", "yes"}

# Tier 0.5 — FLAME free-loop (local Groq proxy, RM0, ZEN-fix 2026-07-30)
# FLAME is a local OpenAI-compatible proxy that multiplexes Groq free-tier models.
# Inserted as immediate fallback after TokenRouter failure to prevent cascade
# from exceeding the 45s ToolTimeoutMiddleware budget.
# No auth needed — localhost-only, UFW-gated.
FLAME_BASE_URL = os.getenv("FLAME_BASE_URL", "http://localhost:18901/v1")
FLAME_MODEL = os.getenv("FLAME_MODEL", "llama-3.3-70b-versatile")
FLAME_TIMEOUT = 4.0  # ZEN: 4s max — FLAME typical 0.3-1s

# ── ZEN CASCADE BUDGET (2026-07-30) ──────────────────────────────────────
# Per ChatGPT forensic: one slow provider must not consume the entire kernel
# budget and block faster providers. Every provider gets 3-4s individual
# timeout. Total cascade completes in under 30s, leaving 15s for kernel
# response construction before the 45s ToolTimeoutMiddleware fires.
PROVIDER_TIMEOUT = 4.0  # max per-provider HTTP timeout
TOTAL_CASCADE_BUDGET = 30.0  # hard ceiling for entire cascade
CB_FAIL_THRESHOLD = 2  # consecutive failures before circuit breaks
CB_COOLDOWN_SECONDS = 120  # circuit stays open for 2 minutes

# Circuit breaker state (module-level, resets on process restart)
_circuit_state: dict[str, dict[str, float]] = {}  # provider → {failures, open_until}


def _cb_is_open(provider: str) -> bool:
    """Check if circuit breaker is open for a provider (skip it)."""
    import time as _time

    state = _circuit_state.get(provider)
    if state is None:
        return False
    if state["open_until"] > _time.monotonic():
        return True
    # Circuit has cooled — reset
    _circuit_state.pop(provider, None)
    return False


def _cb_record_failure(provider: str) -> None:
    """Record a failure. Open circuit after CB_FAIL_THRESHOLD consecutive failures."""
    import time as _time

    state = _circuit_state.get(provider, {"failures": 0, "open_until": 0})
    state["failures"] += 1
    if state["failures"] >= CB_FAIL_THRESHOLD:
        state["open_until"] = _time.monotonic() + CB_COOLDOWN_SECONDS
        logger.warning("CIRCUIT BREAKER OPEN for %s (%ds cooldown)", provider, CB_COOLDOWN_SECONDS)
    _circuit_state[provider] = state


def _cb_record_success(provider: str) -> None:
    """Reset circuit on success."""
    _circuit_state.pop(provider, None)


def _cascade_exhausted(
    tool_origin: str,
    mode: str,
    combined_prompt: str,
    trace_recursion_depth: int,
    failures: list[str] | None = None,
) -> LLMOutputEnvelope:
    """
    ZEN (2026-07-30): Return structured HOLD when all providers fail or budget exceeded.

    Per ChatGPT forensic: do NOT wait 45s. Return DEGRADED immediately
    so the kernel can respond within the ToolTimeoutMiddleware budget.
    """
    t0 = time.monotonic()
    failed_providers = failures or ["all"]
    parsed = {
        "status": "DEGRADED",
        "verdict": "HOLD",
        "reason": "llm_cascade_exhausted",
        "reasons": [
            f"All LLM providers consumed within {TOTAL_CASCADE_BUDGET}s budget.",
            f"Failed providers: {', '.join(failed_providers)}.",
            "This is a constitutional HOLD — execution is blocked until "
            "the reasoning backend recovers. No LLM, no judgment.",
        ],
        "failed_providers": failed_providers,
        "budget_total_s": TOTAL_CASCADE_BUDGET,
        "human_decision_required": True,
        "execution_allowed": False,
        "retryable": True,
        "next_safe_action": (
            "Recharge TokenRouter credit or wait for circuit breakers to cool "
            f"({CB_COOLDOWN_SECONDS}s). FLAME (:18901) is the fastest recovery path."
        ),
        "confidence": 0.0,
    }
    return _make_envelope(
        json.dumps(parsed),
        parsed,
        "deterministic_fallback",
        "cascade-exhausted-v1",
        tool_origin,
        mode,
        combined_prompt,
        (time.monotonic() - t0) * 1000,
        None,
        trace_recursion_depth,
    )


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

# SEA-LION — remote fallback before local Ollama and deterministic rules.
SEA_LION_API_KEY = os.getenv("SEA_LION_API_KEY")
SEA_LION_BASE_URL = os.getenv("SEA_LION_BASE_URL", "https://api.sea-lion.ai/v1")
SEA_LION_MODEL = os.getenv("SEA_LION_MEANING_MODEL", "aisingapore/Qwen-SEA-LION-v4-32B-IT")


def resolve_tokenrouter_model(
    organ: str = "", task_type: str = "", preferred: str | None = None
) -> str:
    """APEX Theory router: organ + task → best TokenRouter model (quality/cost/latency).

    Uses the pasted spec for GEOX/WEALTH/WELL + fallbacks.
    All via TokenRouter for unified key + redundancy (TokenRouter + direct providers).

    CANONICAL SOURCE: /root/AAA/registries/models/AGENT_MODEL_MAP.json
    routing_rules[] section defines domain-based model overrides.
    TODO: Replace hardcoded branches with registry query:
        rules = json.load(open('/root/AAA/registries/models/AGENT_MODEL_MAP.json'))
        for r in rules['routing_rules']:
            if re.search(r['task_pattern'], task_type):
                return r['preferred_model']
    This ensures organ routing stays in sync with the canonical registry.
    """
    if preferred:
        return preferred
    o = (organ or "").lower()
    t = (task_type or "").lower()
    if (
        o == "geox"
        or "geox" in t
        or "petrophys" in t
        or "well_log" in t
        or "basin" in t
        or "seismic" in t
    ):
        if any(k in t for k in ("petrophys", "well log", "full log", "qc", "interpretation")):
            return "deepseek-v4-pro"  # quality, 1M ctx for full well logs
        if any(k in t for k in ("quick", "screen", "basin screen", "fast")):
            return "deepseek-v4-flash"  # cost mode
        if any(k in t for k in ("seismic", "spatial", "interpret")):
            return "glm-5.1"  # or glm-5-turbo; good spatial reasoning
        return "deepseek-v4-pro"  # default quality for GEOX earth evidence
    if o == "wealth" or "wealth" in t or "emv" in t or "npv" in t or "risk" in t or "market" in t:
        if any(k in t for k in ("emv", "npv", "compute", "irr", "fiscal", "runway")):
            return "deepseek-v4-flash"  # cost/fast deterministic math
        if any(k in t for k in ("risk", "asym", "asymmetry", "scenario")):
            return "deepseek-reasoner"  # quality deep on asymmetric
        if any(k in t for k in ("market", "latency", "real-time", "fx", "price")):
            return "glm-5-turbo"  # latency mode (fast agentic)
        return "deepseek-v4-flash"  # default cost for capital compute
    if o == "well" or "well" in t or "vital" in t or "metabol" in t or "dignity" in t:
        return "deepseek-v4-flash"  # cost mode for reflect-only; low compute
    # default (e.g. arifos, aforge, general)
    return TOKENROUTER_MODEL


class LLMUnavailableError(Exception):
    """Raised when one LLM provider cannot return a usable response."""

    pass


class ConstitutionalSeatUnavailable(LLMUnavailableError):
    """Raised when the constitutional seat model for 666/999 is unavailable.

    Unlike the generic cascade, gated roles MUST fail-closed — no fallback
    to MiniMax, MiMo, Groq, or any other model. Deputy activation requires
    explicit F13 directive per AMEND-20260724-001.
    """

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


def _repair_truncated_json(
    raw: str, min_viable_keys: set[str] | None = None
) -> dict[str, Any] | None:
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
                        "Repaired truncated JSON (strategy %d chars added). Keys recovered: %s",
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
        async with httpx.AsyncClient(timeout=PROVIDER_TIMEOUT) as client:
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
            logger.warning(
                "SEA-LION returned invalid JSON, wrapping plain text: %s", raw_output[:200]
            )
            parsed = {"reasoning": raw_output, "answer": raw_output}

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(
            f"SEA-LION output must be a JSON object, got {type(parsed).__name__}"
        )

    if not parsed:
        raise LLMUnavailableError("SEA-LION returned empty JSON object")

    logger.debug("SEA-LION inference complete")
    return raw_output, parsed


async def _call_tokenrouter(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
    model: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """
    Tier 0 — call TokenRouter (OpenAI-compatible proxy, embedded key).

    TokenRouter is the PRIMARY gateway per APEX Theory (F13 directive).
    Supports organ/task-specific routing (quality/cost/latency modes).
    Proxies to best model for task (DeepSeek V4 Pro for high-accuracy 1M ctx,
    Flash for cost, GLM for spatial, etc.). + direct fallbacks for redundancy.
    API key from vault / env. OpenAI-compatible /v1/chat/completions.

    Returns (raw_output_str, parsed_output_dict).
    """
    if not TOKENROUTER_API_KEY:
        raise LLMUnavailableError("TOKENROUTER_API_KEY not configured")

    messages = [{"role": "system", "content": system}]
    if user:
        messages.append({"role": "user", "content": user})

    effective_model = model or TOKENROUTER_MODEL
    payload: dict[str, Any] = {
        "model": effective_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        # ZEN FIX (2026-07-30): 3s timeout — fail aggressively so cascade reaches FLAME within 10s
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.post(
                f"{TOKENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {TOKENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except Exception as exc:
        logger.warning("TokenRouter transport error: %s", exc)
        raise LLMUnavailableError(f"TokenRouter transport error: {exc}") from exc

    if response.status_code != 200:
        logger.warning("TokenRouter HTTP %s: %s", response.status_code, response.text[:200])
        raise LLMUnavailableError(f"TokenRouter HTTP {response.status_code}")

    try:
        data = response.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content", "") or msg.get("reasoning_content", "")
    except Exception as exc:
        logger.warning("TokenRouter parse error: %s", exc)
        raise LLMUnavailableError(f"TokenRouter response parse error: {exc}") from exc

    raw_output = _strip_markdown(content)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        repaired = _repair_truncated_json(raw_output)
        if repaired is not None:
            logger.info(
                "TokenRouter JSON repaired after truncation (keys: %s)",
                list(repaired.keys()),
            )
            parsed = repaired
            raw_output = json.dumps(repaired)
        else:
            logger.warning(
                "TokenRouter returned invalid JSON, wrapping plain text: %s",
                raw_output[:200],
            )
            parsed = {"reasoning": raw_output, "answer": raw_output}

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(
            f"TokenRouter output must be a JSON object, got {type(parsed).__name__}"
        )

    if not parsed:
        raise LLMUnavailableError("TokenRouter returned empty JSON object")

    logger.debug("TokenRouter inference complete (model=%s)", effective_model)
    return raw_output, parsed


async def _call_flame(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
    model: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """
    Tier 0.5 — FLAME free-loop (local Groq proxy, ZEN-fix 2026-07-30).

    FLAME is a local OpenAI-compatible proxy at :18901 that multiplexes
    Groq's free-tier models (llama-3.3-70b, qwen3.6-27b, etc.).
    No API key needed — localhost-only, UFW-gated.

    Inserted as immediate fallback after TokenRouter failure to prevent
    the cascade from exceeding the 45s ToolTimeoutMiddleware budget.
    Proven: 1s response time, Groq/Llama-3.3-70b backend.
    """
    effective_model = model or FLAME_MODEL

    messages = [{"role": "system", "content": system}]
    if user:
        messages.append({"role": "user", "content": user})

    payload: dict[str, Any] = {
        "model": effective_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        async with httpx.AsyncClient(timeout=FLAME_TIMEOUT) as client:
            response = await client.post(
                f"{FLAME_BASE_URL}/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
    except Exception as exc:
        logger.warning("FLAME transport error: %s", exc)
        raise LLMUnavailableError(f"FLAME transport error: {exc}") from exc

    if response.status_code != 200:
        logger.warning("FLAME HTTP %s: %s", response.status_code, response.text[:200])
        raise LLMUnavailableError(f"FLAME HTTP {response.status_code}")

    try:
        data = response.json()
        # FLAME returns custom format: {"content": "...", "ok": true, ...}
        # NOT OpenAI-compatible {"choices": [...]}. Handle both.
        if "content" in data:
            content = data["content"]
        elif "choices" in data:
            content = data["choices"][0]["message"].get("content", "")
        else:
            raise LLMUnavailableError("FLAME: no 'content' or 'choices' in response")
        if not data.get("ok", True):
            logger.warning("FLAME returned ok=false: %s", data.get("error", "unknown"))
            raise LLMUnavailableError(f"FLAME error: {data.get('error', 'unknown')}")
    except LLMUnavailableError:
        raise
    except Exception as exc:
        logger.warning("FLAME parse error: %s", exc)
        raise LLMUnavailableError(f"FLAME response parse error: {exc}") from exc

    raw_output = _strip_markdown(content)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        repaired = _repair_truncated_json(raw_output)
        if repaired is not None:
            parsed = repaired
            raw_output = json.dumps(repaired)
        else:
            parsed = {"reasoning": raw_output, "answer": raw_output}

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(
            f"FLAME output must be a JSON object, got {type(parsed).__name__}"
        )

    logger.debug("FLAME inference complete (model=%s, provider=groq)", effective_model)
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
        # P2 FIX (2026-07-12): 20s timeout — cascade budget: TokenRouter(10s) + MiniMax(20s) = 30s
        async with httpx.AsyncClient(timeout=PROVIDER_TIMEOUT) as client:
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
            logger.info(
                "MiniMax M3 JSON repaired after truncation (keys: %s)", list(repaired.keys())
            )
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
            logger.warning(
                "MiniMax M3 returned invalid JSON (first 100 chars): %s", raw_output[:100]
            )
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


async def _call_groq(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
) -> tuple[str, dict[str, Any]]:
    """
    Tier 2 — call Groq LPU (FREE tier, ultra-fast) via OpenAI-compatible API.

    Pure OpenAI-compatible — no agentic headers, no role injection.
    560-1000 t/s, 128K context, all models free (rate-limited).
    Returns (raw_output_str, parsed_output_dict).
    """
    if not GROQ_API_KEY:
        raise LLMUnavailableError("GROQ_API_KEY not configured")

    messages = [{"role": "system", "content": system}]
    if user:
        messages.append({"role": "user", "content": user})

    payload: dict[str, Any] = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    t0 = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=PROVIDER_TIMEOUT) as client:
            response = await client.post(
                f"{GROQ_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except Exception as exc:
        logger.warning("Groq LPU transport error: %s", exc)
        raise LLMUnavailableError(f"Groq LPU transport error: {exc}") from exc

    if response.status_code != 200:
        logger.warning("Groq LPU HTTP %s: %s", response.status_code, response.text[:200])
        raise LLMUnavailableError(f"Groq LPU HTTP {response.status_code}")

    try:
        data = response.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content", "")
    except Exception as exc:
        logger.warning("Groq LPU parse error: %s", exc)
        raise LLMUnavailableError(f"Groq LPU response parse error: {exc}") from exc

    raw_output = _strip_markdown(content)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        repaired = _repair_truncated_json(raw_output)
        if repaired is not None:
            logger.info("Groq LPU JSON repaired after truncation (keys: %s)", list(repaired.keys()))
            parsed = repaired
            raw_output = json.dumps(repaired)
        else:
            logger.warning("Groq LPU returned invalid JSON (first 100 chars): %s", raw_output[:100])
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
            f"Groq LPU output must be a JSON object, got {type(parsed).__name__}"
        )

    if not parsed:
        raise LLMUnavailableError("Groq LPU returned empty JSON object")

    logger.debug("Groq LPU inference complete (model=%s)", GROQ_MODEL)
    return raw_output, parsed


async def _call_gemini(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
) -> tuple[str, dict[str, Any]]:
    """
    Tier 2 — call Google Gemini (FREE tier) via OpenAI-compatible v1beta endpoint.

    1,500 req/day free, 250K TPM, 1M context, multimodal.
    Returns (raw_output_str, parsed_output_dict).
    """
    if not GEMINI_API_KEY:
        raise LLMUnavailableError("GEMINI_API_KEY not configured")

    messages = [{"role": "system", "content": system}]
    if user:
        messages.append({"role": "user", "content": user})

    payload: dict[str, Any] = {
        "model": GEMINI_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    t0 = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=PROVIDER_TIMEOUT) as client:
            response = await client.post(
                f"{GEMINI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GEMINI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except Exception as exc:
        logger.warning("Gemini transport error: %s", exc)
        raise LLMUnavailableError(f"Gemini transport error: {exc}") from exc

    if response.status_code != 200:
        logger.warning("Gemini HTTP %s: %s", response.status_code, response.text[:200])
        raise LLMUnavailableError(f"Gemini HTTP {response.status_code}")

    try:
        data = response.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content", "")
    except Exception as exc:
        logger.warning("Gemini parse error: %s", exc)
        raise LLMUnavailableError(f"Gemini response parse error: {exc}") from exc

    raw_output = _strip_markdown(content)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        repaired = _repair_truncated_json(raw_output)
        if repaired is not None:
            logger.info("Gemini JSON repaired (keys: %s)", list(repaired.keys()))
            parsed = repaired
            raw_output = json.dumps(repaired)
        else:
            logger.warning("Gemini invalid JSON (first 100 chars): %s", raw_output[:100])
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
            f"Gemini output must be a JSON object, got {type(parsed).__name__}"
        )

    if not parsed:
        raise LLMUnavailableError("Gemini returned empty JSON object")

    logger.debug("Gemini inference complete (model=%s)", GEMINI_MODEL)
    return raw_output, parsed


async def _call_cerebras(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
) -> tuple[str, dict[str, Any]]:
    """
    Tier 2 — call Cerebras ($5 free credit) via OpenAI-compatible API.

    Wafer-scale hardware, fast inference. Models: gpt-oss-120b, gemma-4-31b, zai-glm-4.7.
    Returns (raw_output_str, parsed_output_dict).
    """
    if not CEREBRAS_API_KEY:
        raise LLMUnavailableError("CEREBRAS_API_KEY not configured")

    messages = [{"role": "system", "content": system}]
    if user:
        messages.append({"role": "user", "content": user})

    payload: dict[str, Any] = {
        "model": CEREBRAS_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    t0 = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=PROVIDER_TIMEOUT) as client:
            response = await client.post(
                f"{CEREBRAS_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {CEREBRAS_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except Exception as exc:
        logger.warning("Cerebras transport error: %s", exc)
        raise LLMUnavailableError(f"Cerebras transport error: {exc}") from exc

    if response.status_code != 200:
        logger.warning("Cerebras HTTP %s: %s", response.status_code, response.text[:200])
        raise LLMUnavailableError(f"Cerebras HTTP {response.status_code}")

    try:
        data = response.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content", "")
    except Exception as exc:
        logger.warning("Cerebras parse error: %s", exc)
        raise LLMUnavailableError(f"Cerebras response parse error: {exc}") from exc

    raw_output = _strip_markdown(content)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        repaired = _repair_truncated_json(raw_output)
        if repaired is not None:
            logger.info("Cerebras JSON repaired (keys: %s)", list(repaired.keys()))
            parsed = repaired
            raw_output = json.dumps(repaired)
        else:
            parsed = {
                "status": "HOLD",
                "verdict": "HOLD",
                "reason": "llm_schema_violation",
                "reasoning": raw_output,
                "answer": raw_output,
            }

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(
            f"Cerebras output must be a JSON object, got {type(parsed).__name__}"
        )

    if not parsed:
        raise LLMUnavailableError("Cerebras returned empty JSON object")

    logger.debug("Cerebras inference complete (model=%s)", CEREBRAS_MODEL)
    return raw_output, parsed


async def _call_mimo(
    system: str,
    user: str,
    response_schema: dict[str, Any] | None,
    temperature: float,
    max_tokens: int = 1200,
) -> tuple[str, dict[str, Any]]:
    """
    Tier 1.5 — call MiMo (TokenPlan mimo-v2.5-pro) via OpenAI-compatible API.

    Arif's primary model. 1M context, native multimodal, MiMo architecture.
    Replaces Azure gpt-4.1-mini as secondary reasoning partner per 2026-06-27 directive.

    Returns (raw_output_str, parsed_output_dict).
    """
    if not MIMO_API_KEY:
        raise LLMUnavailableError("MIMO_API_KEY not configured")

    messages = [{"role": "system", "content": system}]
    if user:
        messages.append({"role": "user", "content": user})

    payload: dict[str, Any] = {
        "model": MIMO_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        async with httpx.AsyncClient(timeout=PROVIDER_TIMEOUT) as client:
            response = await client.post(
                f"{MIMO_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {MIMO_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except Exception as exc:
        logger.warning("MiMo transport error: %s", exc)
        raise LLMUnavailableError(f"MiMo transport error: {exc}") from exc

    if response.status_code != 200:
        logger.warning("MiMo HTTP %s: %s", response.status_code, response.text[:200])
        raise LLMUnavailableError(f"MiMo HTTP {response.status_code}")

    try:
        data = response.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content", "") or msg.get("reasoning_content", "")
    except Exception as exc:
        logger.warning("MiMo parse error: %s", exc)
        raise LLMUnavailableError(f"MiMo response parse error: {exc}") from exc

    raw_output = _strip_markdown(content)

    try:
        parsed = json.loads(raw_output)
    except json.JSONDecodeError:
        repaired = _repair_truncated_json(raw_output)
        if repaired is not None:
            logger.info("MiMo JSON repaired after truncation (keys: %s)", list(repaired.keys()))
            parsed = repaired
            raw_output = json.dumps(repaired)
        else:
            logger.warning("MiMo returned invalid JSON, wrapping plain text: %s", raw_output[:200])
            parsed = {"reasoning": raw_output, "answer": raw_output}

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(f"MiMo output must be a JSON object, got {type(parsed).__name__}")

    if not parsed:
        raise LLMUnavailableError("MiMo returned empty JSON object")

    logger.debug("MiMo inference complete (model=%s)", MIMO_MODEL)
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
        async with httpx.AsyncClient(timeout=PROVIDER_TIMEOUT) as client:
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
        logger.warning(
            "Azure OpenAI returned invalid JSON, wrapping plain text: %s", raw_output[:200]
        )
        parsed = {"reasoning": raw_output, "answer": raw_output}

    if not isinstance(parsed, dict):
        raise LLMUnavailableError(
            f"Azure OpenAI output must be a JSON object, got {type(parsed).__name__}"
        )

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
        async with httpx.AsyncClient(timeout=PROVIDER_TIMEOUT) as client:
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
                    logger.info(
                        "Ollama JSON repaired after truncation (keys: %s)", list(repaired.keys())
                    )
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
                    logger.info(
                        "Ollama JSON repaired after truncation (keys: %s)", list(repaired.keys())
                    )
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
        async with httpx.AsyncClient(timeout=PROVIDER_TIMEOUT) as client:
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


# ── Constitutional Model Role Enforcement (arifOS, F13-ratified 2026-07-24) ──
# The canonical model law lives in:
#   /root/AAA/registries/models/AGENT_MODEL_MAP.json
# For constitutional roles 666_JUDGE and 999_SEAL, ONLY the model(s) that
# the law declares as allowed for the role may serve the call. Any other
# model must fail-closed with a FORBIDDEN_MODEL_FOR_ROLE event into the
# VAULT999 operational ledger (outcomes.jsonl) and raise — the call never
# reaches the cascade. Non-constitutional roles pass through unchanged
# (TOKENROUTER_MODEL = deepseek-v4-flash remains the operational default).
#
# This makes the AGENT_MODEL_MAP law executable, not declarative.
# Option B (sovereign directive 2026-07-24): general calls keep the flash
# default; judge/seal invocations must explicitly set deepseek/deepseek-v4-pro.
# Per-call roles are passed via the constitutional_role argument to call_llm().
CONSTITUTIONAL_ROLES_GATED: frozenset[str] = frozenset({"666_JUDGE", "999_SEAL"})

_DEFAULT_AGENT_MODEL_MAP_PATH = "/root/AAA/registries/models/AGENT_MODEL_MAP.json"

# VAULT999 operational ledger path (mirrors arifosmcp/runtime/tools.py:23411).
# Resolved relative to the arifOS package root (parents[2] of this file).
_ARIFOS_ROOT = Path(__file__).resolve().parents[2]
_VAULT_OUTCOMES_PATH = _ARIFOS_ROOT / "VAULT999" / "outcomes.jsonl"


def _agent_model_map_path() -> str:
    """Resolve AGENT_MODEL_MAP path (env override ARIFOS_AGENT_MODEL_MAP_PATH)."""
    return os.getenv("ARIFOS_AGENT_MODEL_MAP_PATH", _DEFAULT_AGENT_MODEL_MAP_PATH)


_agent_model_map_cache: dict[str, Any] = {"mtime": None, "data": None}


def _load_agent_model_map() -> dict[str, Any]:
    """Load AGENT_MODEL_MAP.json with mtime-based cache invalidation.

    Returns {} on missing/unparseable. Callers MUST treat empty dict as
    fail-closed for constitutional roles (see select_model_for_role).
    """
    path = _agent_model_map_path()
    try:
        p = Path(path)
        if not p.exists():
            return {}
        mtime = p.stat().st_mtime
        cached = _agent_model_map_cache
        if cached["mtime"] == mtime and cached["data"] is not None:
            return cached["data"]
        data = json.loads(p.read_text(encoding="utf-8"))
        cached["mtime"] = mtime
        cached["data"] = data
        return data
    except Exception as exc:  # noqa: BLE001 — best-effort; gate fail-closes on empty
        logger.debug("AGENT_MODEL_MAP load failed for %s: %s", path, exc)
        return {}


def _allowed_models_for_role(model_map: dict[str, Any], role: str) -> set[str]:
    """Return the set of model_keys allowed to serve a constitutional role.

    A model is allowed iff `role in model['constitutional_roles']` AND
    `role NOT in model['constitutional_roles_forbidden']`.
    """
    if not model_map or not role:
        return set()
    allowed: set[str] = set()
    for m in model_map.get("models", []) or []:
        mk = (m.get("model_key") or "").strip()
        if not mk:
            continue
        roles = set(m.get("constitutional_roles") or [])
        forbidden = set(m.get("constitutional_roles_forbidden") or [])
        if role in roles and role not in forbidden:
            allowed.add(mk)
    return allowed


def _emit_vault999_outcome(event: dict[str, Any]) -> None:
    """Append a JSONL event to VAULT999/outcomes.jsonl (operational ledger).

    Mirrors the kernel's existing operational-ledger write pattern
    (arifosmcp/runtime/tools.py:23411). Best-effort: failures are logged
    and swallowed — the gate's fail-closed behavior must not depend on
    the write path succeeding.
    """
    try:
        _VAULT_OUTCOMES_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _VAULT_OUTCOMES_PATH.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    except Exception as exc:  # noqa: BLE001
        logger.warning("VAULT999 outcomes.jsonl append failed: %s", exc)


def select_model_for_role(
    role: str | None,
    requested_model: str | None = None,
    *,
    agent_id: str | None = None,
) -> str:
    """Enforce AGENT_MODEL_MAP law for constitutional roles.

    For role in {666_JUDGE, 999_SEAL}: the requested_model (or the
    operational default TOKENROUTER_MODEL when requested_model is None)
    MUST appear in the map's allowed set for that role. If not, raise
    LLMUnavailableError with a FORBIDDEN_MODEL_FOR_ROLE message and emit
    a governance event to VAULT999/outcomes.jsonl. Missing or unparseable
    map also fail-closes for constitutional roles.

    For all other roles (None or non-constitutional): passthrough,
    returning requested_model unchanged. Zero behavior change for the
    overwhelming majority of calls that are not judge/seal.

    The function is pure with respect to call_llm's cascade: it only
    validates and returns the model string. The actual provider call
    happens in the cascade below. Model-key normalization handles the
    "deepseek-v4-pro" (cascade short form) vs "deepseek/deepseek-v4-pro"
    (map full form) mismatch by matching against both.
    """
    if not role or role not in CONSTITUTIONAL_ROLES_GATED:
        return (requested_model or "").strip()

    model_map = _load_agent_model_map()
    allowed = _allowed_models_for_role(model_map, role)
    # Normalize: accept both full ("provider/model") and short ("model") forms.
    allowed_normalized = set(allowed)
    for a in list(allowed):
        short = a.split("/", 1)[-1] if "/" in a else a
        allowed_normalized.add(short)

    requested = (requested_model or "").strip()
    effective = requested or os.getenv("TOKENROUTER_MODEL", "").strip()
    eff_normalized = effective.split("/", 1)[-1] if "/" in effective else effective

    timestamp = datetime.now(UTC).isoformat()

    if not model_map or not allowed:
        event = {
            "event": "FORBIDDEN_MODEL_FOR_ROLE",
            "role": role,
            "requested_model": requested_model,
            "effective_model": effective,
            "allowed_models": sorted(allowed),
            "agent_id": agent_id,
            "decision": "888_HOLD",
            "reason": (
                "AGENT_MODEL_MAP unavailable or no models allowed for role"
                if not model_map
                else f"AGENT_MODEL_MAP declares no allowed model for role {role}"
            ),
            "registry_path": _agent_model_map_path(),
            "timestamp": timestamp,
        }
        _emit_vault999_outcome(event)
        raise LLMUnavailableError(
            f"FORBIDDEN_MODEL_FOR_ROLE: role={role} effective_model={effective!r}; "
            f"registry path={_agent_model_map_path()}; "
            f"reason={event['reason']}"
        )

    if effective not in allowed_normalized:
        event = {
            "event": "FORBIDDEN_MODEL_FOR_ROLE",
            "role": role,
            "requested_model": requested_model,
            "effective_model": effective,
            "allowed_models": sorted(allowed),
            "agent_id": agent_id,
            "decision": "888_HOLD",
            "reason": (
                f"Model {effective!r} is not in the AGENT_MODEL_MAP allowed "
                f"set for role {role}. Allowed: {sorted(allowed)}"
            ),
            "registry_path": _agent_model_map_path(),
            "timestamp": timestamp,
        }
        _emit_vault999_outcome(event)
        raise LLMUnavailableError(
            f"FORBIDDEN_MODEL_FOR_ROLE: role={role} model={effective!r} "
            f"not in allowed set {sorted(allowed)}; see VAULT999 outcomes.jsonl"
        )

    return effective


def _emit_seat_unavailable(
    role: str,
    seat_model: str,
    tool_origin: str,
    attempted_model: str | None,
) -> None:
    """Emit JUDGE_SEAT_UNAVAILABLE or SEAL_SEAT_UNAVAILABLE to VAULT999.

    AMEND-20260724-001: when the constitutional seat model fails, the system
    MUST NOT enter the generic provider cascade. The event is best-effort
    (failures are swallowed) — it is an operational log, not a seal.
    """
    event_kind = (
        "JUDGE_SEAT_UNAVAILABLE"
        if role == "666_JUDGE"
        else "SEAL_SEAT_UNAVAILABLE"
        if role == "999_SEAL"
        else "CONSTITUTIONAL_SEAT_UNAVAILABLE"
    )
    event = {
        "event": event_kind,
        "role": role,
        "seat_model": seat_model,
        "attempted_model": attempted_model or seat_model,
        "tool_origin": tool_origin,
        "decision": "HOLD",
        "reason": (
            f"Constitutional seat model {seat_model!r} is unavailable "
            f"for role {role}. No cascade — deputy requires F13 directive."
        ),
        "registry_path": _agent_model_map_path(),
        "timestamp": datetime.now(UTC).isoformat(),
    }
    _emit_vault999_outcome(event)


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
    preferred_model: str | None = None,
    organ: str = "",
    task_type: str = "",
    constitutional_role: str | None = None,
) -> LLMOutputEnvelope:
    """
    Call TokenRouter (Tier 0 primary) → remote providers → SEA-LION → Ollama → rules.

    APEX Theory applied (per pasted spec):
    - TokenRouter as unified gateway for redundancy (survives single provider failure).
    - The final SEA-LION/Ollama/rule tail guarantees a valid governed HOLD on outage.
    - Organ/task-specific routing (quality/cost/latency modes):
      GEOX: petrophysics=DeepSeek V4 Pro (1M), quick basin=Flash (cost), seismic=GLM 5.1 (spatial)
      WEALTH: EMV/NPV=cost fast, risk=quality deep, market=latency
      WELL: cost mode + PII firewalls (reflect-only)
    - tool_origin or organ/task_type used to resolve model when preferred_model not passed.

    Returns LLMOutputEnvelope — the single legal form of LLM output in arifOS.

    Args:
        ... (existing)
        preferred_model: explicit model id to send to TokenRouter (e.g. "deepseek-v4-pro")
        organ: "geox" | "wealth" | "well" | ...
        task_type: "petrophysics" | "emv" | "risk" | "seismic" | ...
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

    # F13 — Constitutional model-role gate (AMEND-20260724-001, 2026-07-24)
    # For roles 666_JUDGE / 999_SEAL, the effective model is determined by
    # select_model_for_role() which enforces the seat policy. The returned
    # model MUST be used — the generic cascade below is NEVER entered for
    # gated roles. If the exact seat model fails → ConstitutionalSeatUnavailable
    # → HOLD (fail-closed). No fallback, no silent substitution.
    # Non-constitutional roles pass through to the generic cascade unchanged.
    if constitutional_role and constitutional_role in CONSTITUTIONAL_ROLES_GATED:
        gated_model = select_model_for_role(
            constitutional_role, preferred_model, agent_id=tool_origin
        )
        t0 = time.monotonic()
        try:
            raw_output, parsed = await _call_tokenrouter(
                system,
                user,
                response_schema,
                temperature,
                max_tokens,
                model=gated_model,
            )
            return _make_envelope(
                raw_output,
                parsed,
                "tokenrouter",
                gated_model,
                tool_origin,
                mode,
                combined_prompt,
                (time.monotonic() - t0) * 1000,
                response_schema,
                trace_recursion_depth,
            )
        except LLMUnavailableError:
            _emit_seat_unavailable(
                constitutional_role,
                gated_model,
                tool_origin,
                preferred_model,
            )
            raise ConstitutionalSeatUnavailable(
                f"Constitutional seat unavailable: role={constitutional_role} "
                f"model={gated_model} — HOLD. No cascade for gated roles. "
                f"Deputy must be activated by F13 directive."
            ) from None
    elif constitutional_role:
        # Non-gated constitutional role — validate but don't short-circuit cascade
        select_model_for_role(constitutional_role, preferred_model, agent_id=tool_origin)

    # Tier 0 — TokenRouter (OpenAI-compatible proxy, embedded key) — PRIMARY
    # APEX Theory: resolve per organ/task for quality/cost/latency + redundancy.
    cascade_start = time.monotonic()
    effective_model = preferred_model or resolve_tokenrouter_model(organ, task_type)
    if not _cb_is_open("tokenrouter"):
        try:
            t0 = time.monotonic()
            raw_output, parsed = await _call_tokenrouter(
                system, user, response_schema, temperature, max_tokens, model=effective_model
            )
            _cb_record_success("tokenrouter")
            return _make_envelope(
                raw_output,
                parsed,
                "tokenrouter",
                effective_model,
                tool_origin,
                mode,
                combined_prompt,
                (time.monotonic() - t0) * 1000,
                response_schema,
                trace_recursion_depth,
            )
        except LLMUnavailableError:
            _cb_record_failure("tokenrouter")
    if time.monotonic() - cascade_start > TOTAL_CASCADE_BUDGET:
        return _cascade_exhausted(tool_origin, mode, combined_prompt, trace_recursion_depth)

    # Tier 0.5 — FLAME free-loop (local Groq proxy, ZEN-fix 2026-07-30)
    # FLAME is proven working (1s response, Groq Llama-3.3-70b backend).
    # Inserted BEFORE paid tiers so the cascade reaches a working backend
    # within the 45s ToolTimeoutMiddleware budget.
    if not _cb_is_open("flame"):
        try:
            t0 = time.monotonic()
            raw_output, parsed = await _call_flame(
                system, user, response_schema, temperature, max_tokens
            )
            _cb_record_success("flame")
            return _make_envelope(
                raw_output,
                parsed,
                "flame-groq",
                FLAME_MODEL,
                tool_origin,
                mode,
                combined_prompt,
                (time.monotonic() - t0) * 1000,
                response_schema,
                trace_recursion_depth,
            )
        except LLMUnavailableError:
            _cb_record_failure("flame")
    if time.monotonic() - cascade_start > TOTAL_CASCADE_BUDGET:
        return _cascade_exhausted(tool_origin, mode, combined_prompt, trace_recursion_depth)

    # Tier 1 — MiniMax M3 (frontier agentic model, best at structured JSON)
    if not _cb_is_open("minimax"):
        try:
            t0 = time.monotonic()
            raw_output, parsed = await _call_minimax(
                system, user, response_schema, temperature, max_tokens
            )
            _cb_record_success("minimax")
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
            _cb_record_failure("minimax")
    if time.monotonic() - cascade_start > TOTAL_CASCADE_BUDGET:
        return _cascade_exhausted(tool_origin, mode, combined_prompt, trace_recursion_depth)

    # Tier 1.5 — MiMo (TokenPlan mimo-v2.5-pro)
    if not _cb_is_open("mimo"):
        try:
            t0 = time.monotonic()
            raw_output, parsed = await _call_mimo(
                system, user, response_schema, temperature, max_tokens
            )
            _cb_record_success("mimo")
            return _make_envelope(
                raw_output,
                parsed,
                "mimo",
                MIMO_MODEL,
                tool_origin,
                mode,
                combined_prompt,
                (time.monotonic() - t0) * 1000,
                response_schema,
                trace_recursion_depth,
            )
        except LLMUnavailableError:
            _cb_record_failure("mimo")
    if time.monotonic() - cascade_start > TOTAL_CASCADE_BUDGET:
        return _cascade_exhausted(tool_origin, mode, combined_prompt, trace_recursion_depth)

    # Tier 2 — Groq LPU (FREE tier, ultra-fast 560-1000 t/s, 128K context)
    if not _cb_is_open("groq"):
        try:
            t0 = time.monotonic()
            raw_output, parsed = await _call_groq(
                system, user, response_schema, temperature, max_tokens
            )
            _cb_record_success("groq")
            return _make_envelope(
                raw_output,
                parsed,
                "groq",
                GROQ_MODEL,
                tool_origin,
                mode,
                combined_prompt,
                (time.monotonic() - t0) * 1000,
                response_schema,
                trace_recursion_depth,
            )
        except LLMUnavailableError:
            _cb_record_failure("groq")
    if time.monotonic() - cascade_start > TOTAL_CASCADE_BUDGET:
        return _cascade_exhausted(tool_origin, mode, combined_prompt, trace_recursion_depth)

    # Tier 2 — Google Gemini (FREE tier, 1M ctx, multimodal)
    if not _cb_is_open("gemini"):
        try:
            t0 = time.monotonic()
            raw_output, parsed = await _call_gemini(
                system, user, response_schema, temperature, max_tokens
            )
            _cb_record_success("gemini")
            return _make_envelope(
                raw_output,
                parsed,
                "gemini",
                GEMINI_MODEL,
                tool_origin,
                mode,
                combined_prompt,
                (time.monotonic() - t0) * 1000,
                response_schema,
                trace_recursion_depth,
            )
        except LLMUnavailableError:
            _cb_record_failure("gemini")
    if time.monotonic() - cascade_start > TOTAL_CASCADE_BUDGET:
        return _cascade_exhausted(tool_origin, mode, combined_prompt, trace_recursion_depth)

    # Tier 2 — Cerebras (free credit, wafer-scale)
    if not _cb_is_open("cerebras"):
        try:
            t0 = time.monotonic()
            raw_output, parsed = await _call_cerebras(
                system, user, response_schema, temperature, max_tokens
            )
            _cb_record_success("cerebras")
            return _make_envelope(
                raw_output,
                parsed,
                "cerebras",
                CEREBRAS_MODEL,
                tool_origin,
                mode,
                combined_prompt,
                (time.monotonic() - t0) * 1000,
                response_schema,
                trace_recursion_depth,
            )
        except LLMUnavailableError:
            _cb_record_failure("cerebras")
    if time.monotonic() - cascade_start > TOTAL_CASCADE_BUDGET:
        return _cascade_exhausted(tool_origin, mode, combined_prompt, trace_recursion_depth)

    # Tier 2 — SEA-LION v4 (GPU-accelerated, third voice in trinity)
    if not _cb_is_open("sea_lion"):
        try:
            t0 = time.monotonic()
            raw_output, parsed = await _call_sea_lion(
                system, user, response_schema, temperature, max_tokens
            )
            _cb_record_success("sea_lion")
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
            _cb_record_failure("sea_lion")
    if time.monotonic() - cascade_start > TOTAL_CASCADE_BUDGET:
        return _cascade_exhausted(tool_origin, mode, combined_prompt, trace_recursion_depth)

    # Tier 2.5 — Ollama (local CPU, opt-in)
    if OLLAMA_TEXT_ENABLED and not _cb_is_open("ollama"):
        try:
            t0 = time.monotonic()
            raw_output, parsed = await _call_ollama(
                system, user, response_schema, temperature, max_tokens
            )
            _cb_record_success("ollama")
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
            _cb_record_failure("ollama")

    # ── All providers exhausted → structured DEGRADED/HOLD ──
    failed = [
        p
        for p in [
            "tokenrouter",
            "flame",
            "minimax",
            "mimo",
            "groq",
            "gemini",
            "cerebras",
            "sea_lion",
        ]
        if _cb_is_open(p) or p in ("tokenrouter",)
    ]  # tokenrouter always tried
    return _cascade_exhausted(
        tool_origin, mode, combined_prompt, trace_recursion_depth, failures=failed
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
        "ollama_embedding": "unknown",
        "ollama_text": "enabled" if OLLAMA_TEXT_ENABLED else "disabled",
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

    # Check Ollama. Embeddings are production-enabled independently from the
    # opt-in CPU text fallback, so report their readiness separately.
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if r.status_code == 200:
                models = r.json().get("models", [])
                model_names = [m.get("name") for m in models]
                status["ollama_models"] = model_names
                status["ollama_embedding"] = (
                    "reachable"
                    if any(name in {"bge-m3", "bge-m3:latest"} for name in model_names)
                    else "model_missing"
                )
                if OLLAMA_TEXT_ENABLED:
                    status["fallback"] = (
                        "reachable" if OLLAMA_MODEL in model_names else "model_missing"
                    )
                else:
                    status["fallback"] = "disabled"
            else:
                status["ollama_embedding"] = f"http_{r.status_code}"
                if OLLAMA_TEXT_ENABLED:
                    status["fallback"] = f"http_{r.status_code}"
    except Exception as exc:
        status["ollama_embedding"] = "unreachable"
        if OLLAMA_TEXT_ENABLED:
            status["fallback"] = "unreachable"
        status["errors"].append(f"Ollama: {exc}")

    # Check MiMo (Tier 1.5 — TokenPlan mimo-v2.5-pro)
    if not MIMO_API_KEY:
        status["mimo"] = "unconfigured"
    else:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(
                    MIMO_BASE_URL.rstrip("/v1") + "/models",
                    headers={"Authorization": f"Bearer {MIMO_API_KEY}"},
                )
                if r.status_code in (200, 401):
                    status["mimo"] = "reachable"
                else:
                    status["mimo"] = f"http_{r.status_code}"
        except Exception as exc:
            status["mimo"] = "unreachable"
            status["errors"].append(f"MiMo: {exc}")

    # Determine active provider (match cascade: M3 → MiMo → SEA-LION, then
    # Ollama only when its CPU text path was explicitly enabled).
    # ILMU BLOCKED per FFF 2026-06-15 — not in cascade
    if status["primary"] == "reachable":
        status["active_provider"] = "minimax"
    elif status.get("mimo") == "reachable":
        status["active_provider"] = "mimo"
    elif status.get("sea_lion") == "reachable":
        status["active_provider"] = "sea_lion"
    elif status.get("ilmu") == "reachable":
        status["active_provider"] = "ilmu_blocked_fff"
        status["ilmu_status"] = "BLOCKED per FFF 2026-06-15 — not in cascade"
    elif OLLAMA_TEXT_ENABLED and status.get("fallback") == "reachable":
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
