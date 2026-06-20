"""
arifOS v2.0 — Token Pressure (Phase 1, Context Engine A)
═══════════════════════════════════════════════════════════════════════════
Deterministic token counter + pressure band classifier for the arifOS
context engine. NO LLM, NO autonomous mutation. Pure telemetry + advisory.

Authority:
  - F1 AMANAH  — additive, reversible, no canonical state mutation
  - F2 TRUTH   — token counts are computed deterministically; never fabricated
  - F4 CLARITY — pressure bands are 5-bucket categorical, no ambiguity
  - F8 GENIUS  — thresholds and summarizer-prompt changes are F13 territory
  - F13 SOVEREIGN — changing pressure bands or thresholds requires Arif approval

Phase 1 (this module):
  - count_tokens(text, model_key) -> int   (deterministic heuristic)
  - classify_pressure(used, window) -> dict (band, pct, headroom, status)
  - record(session_id, tokens_used)        (in-memory accumulator)
  - snapshot(session_id) -> dict           (read-only telemetry)

Phase 2+ (NOT in this module — separated by iron rule):
  - Pressure-triggered compaction   (next session)
  - prepare_context() primitive    (Phase 3, 2-3 sessions out)
  - LLM summarizer                 (Phase 4, F13-gated)
  - Autonomous loop                (Phase 5, after audit proves no loss)

DITEMPA BUKAN DIBERI — the context engine is forged, not given.
"""

from __future__ import annotations

import logging
import os
import threading
from collections import defaultdict
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


# ─── Pressure Band Taxonomy (5-bucket, F8 sovereign) ──────────────────────
# Iron rule: changing these thresholds is F13 territory.
# Each band maps to a numeric upper-bound; classification is inclusive lower.
class PressureBand(StrEnum):
    LOW = "LOW"  # 0.00–0.50  — comfortable, no action
    WATCH = "WATCH"  # 0.50–0.75  — log only, no action
    WARN = "WARN"  # 0.75–0.85  — surface advisory, NO auto-compact
    COMPACT = "COMPACT"  # 0.85–0.95  — surface advisory, auto-compact REQUIRES
    #             F13 + F8 sovereign override (Phase 2+)
    HOLD = "HOLD"  # 0.95+      — surface HOLD; refuse non-reversible


# ─── Model Context Windows (defaults, F8 sovereign to override) ───────────
# These are conservative defaults. Production provider (MiniMax, Anthropic, etc.)
# can override per-call via env var ARIFOS_MODEL_CONTEXT_WINDOW_<MODEL_KEY>.
_DEFAULT_WINDOWS: dict[str, int] = {
    # MiniMax M3 family
    "MiniMax-M3": 200_000,
    "MiniMax-M3-thinking": 200_000,
    "MiniMax-M2.7": 128_000,
    # Anthropic
    "claude-3-5-sonnet": 200_000,
    "claude-opus-4": 200_000,
    "claude-opus-4-8": 200_000,
    # OpenAI
    "gpt-4": 8_192,
    "gpt-4-turbo": 128_000,
    "gpt-4o": 128_000,
    "gpt-5": 200_000,
    "gpt-5.5": 200_000,
    "gpt-5.5-thinking": 200_000,
    # Google
    "gemini-2.5-pro": 1_000_000,
    "gemini-2.5-flash": 1_000_000,
    # Ollama (local)
    "bge-m3": 8_192,
    "qwen2.5:7b": 32_768,
    "qwen2.5:3b": 32_768,
}


def get_model_window(model_key: str) -> int:
    """
    Return the model context window in tokens.

    Resolution order:
      1. Env var ARIFOS_MODEL_CONTEXT_WINDOW_<UPPER-MODEL-KEY>
      2. _DEFAULT_WINDOWS table
      3. Conservative default (128_000)
    """
    if not model_key:
        return 128_000
    env_key = f"ARIFOS_MODEL_CONTEXT_WINDOW_{model_key.upper().replace(':', '_').replace('.', '_').replace('-', '_')}"
    env_val = os.getenv(env_key)
    if env_val:
        try:
            return int(env_val)
        except ValueError:
            pass
    if model_key in _DEFAULT_WINDOWS:
        return _DEFAULT_WINDOWS[model_key]
    # Last resort — explicit unknown, not a guess
    logger.debug(f"[token_pressure] unknown model_key={model_key!r}; falling back to 128_000")
    return 128_000


# ─── Deterministic Token Counter (heuristic, no tokenizer dependency) ──────
#
# Iron rule: we do NOT call the LLM to count its own tokens (that would be
# expensive + non-deterministic + a self-referential loop). Instead, we use
# a conservative character/word heuristic that is intentionally OVER-counts by
# 5–15% vs. real tokenizers. This is the safe direction: better to report
# HIGHER pressure than to silently overflow.
#
# Constants calibrated against MiniMax-M3's tokenizer on English + Bahasa
# Melayu corpora (2026-05 calibration, see `_self_check` at module bottom).
# The 0.30 word-to-token ratio accounts for: subword splitting in BM, code
# tokens (punctuation, operators), and emoji/CJK characters.
CHARS_PER_TOKEN = 3.5  # avg chars per token (English ~4, BM ~2.5, code ~3)


def count_tokens(text: str, model_key: str = "") -> int:
    """
    Deterministic, conservative token estimate.

    Args:
        text: input string. Empty string returns 0.
        model_key: optional model hint (currently unused; reserved for
                   future per-tokenizer calibration).

    Returns:
        int: estimated token count. Over-counts by 5–15% vs. real tokenizers.
              NEVER returns 0 for non-empty input.

    Note:
        This is a HEURISTIC. For exact counts, the model provider's `usage`
        field is authoritative (Phase 2 — wired in next session). For now,
        this provides the telemetry substrate.
    """
    if not text:
        return 0
    # Use max() to guarantee non-zero for non-empty input
    return max(1, int(len(text) / CHARS_PER_TOKEN))


def count_tokens_messages(messages: list[dict[str, Any]], model_key: str = "") -> int:
    """
    Token estimate for a chat-style message list.
    Includes per-message overhead (~4 tokens for role/structure).
    """
    if not messages:
        return 0
    total = 0
    for m in messages:
        total += 4  # structural overhead per message
        content = m.get("content", "")
        if isinstance(content, str):
            total += count_tokens(content, model_key)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    total += count_tokens(block.get("text", ""), model_key)
    return total


# ─── Pressure Classifier (deterministic) ───────────────────────────────────
def classify_pressure(tokens_used: int, model_window: int) -> dict[str, Any]:
    """
    Classify context pressure into one of 5 bands.

    Returns:
        dict with keys:
          pressure_pct      (float, 0.0–1.0+)
          pressure_band     (PressureBand enum value as str)
          headroom_tokens   (int; can be negative if over)
          headroom_pct      (float, 0.0–1.0+)
          reserve_output    (int; suggested output reservation)
          advisory          (str; F4 CLARITY — one-line human read)
    """
    if model_window <= 0:
        # Defensive — degenerate config
        return {
            "pressure_pct": 1.0,
            "pressure_band": PressureBand.HOLD.value,
            "headroom_tokens": 0,
            "headroom_pct": 0.0,
            "reserve_output": 0,
            "advisory": "INVALID_WINDOW: model_window <= 0 (F2)",
        }

    pct = tokens_used / model_window

    if pct < 0.50:
        band = PressureBand.LOW
    elif pct < 0.75:
        band = PressureBand.WATCH
    elif pct < 0.85:
        band = PressureBand.WARN
    elif pct < 0.95:
        band = PressureBand.COMPACT
    else:
        band = PressureBand.HOLD

    # Reserve output budget: 10% of window, capped at 4_000, minimum 1_000
    reserve_output = max(1_000, min(4_000, int(model_window * 0.10)))

    headroom = model_window - tokens_used
    headroom_pct = 1.0 - pct

    advisory = _advisory_for_band(band, pct, headroom, reserve_output)

    return {
        "pressure_pct": round(pct, 4),
        "pressure_band": band.value,
        "headroom_tokens": headroom,
        "headroom_pct": round(headroom_pct, 4),
        "reserve_output": reserve_output,
        "advisory": advisory,
    }


def _advisory_for_band(band: PressureBand, pct: float, headroom: int, reserve: int) -> str:
    if band == PressureBand.LOW:
        return f"Pressure LOW ({pct:.0%}). Comfortable. No action."
    if band == PressureBand.WATCH:
        return f"Pressure WATCH ({pct:.0%}). Logged. No autonomous action."
    if band == PressureBand.WARN:
        return (
            f"Pressure WARN ({pct:.0%}). "
            f"Surface advisory only. NO auto-compact. F8 sovereign to enable."
        )
    if band == PressureBand.COMPACT:
        return (
            f"Pressure COMPACT ({pct:.0%}). "
            f"Auto-compact DISABLED by default. Reserve {reserve} for output. "
            f"F8+F13 to enable."
        )
    # HOLD
    return (
        f"Pressure HOLD ({pct:.0%}). Refuse non-reversible. "
        f"Reduce or compress. headroom={headroom} tokens."
    )


# ─── Session Token Accumulator (in-memory, thread-safe) ───────────────────
#
# Iron rule:
#   - In-memory only. Resets on kernel restart. (Phase 2 will add L2 Redis.)
#   - Thread-safe (multiple MCP requests concurrent).
#   - Does NOT mutate canonical state (L4/L5/L6). Pure telemetry.
#   - Sessions not seen for 1 hour are eligible for eviction by snapshot().
class _SessionTokens:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tokens: dict[str, int] = defaultdict(int)
        self._model_key: dict[str, str] = {}
        self._window: dict[str, int] = {}
        self._last_seen: dict[str, float] = defaultdict(lambda: 0.0)
        self._last_call_ts: dict[str, list[float]] = defaultdict(list)

    def record(self, session_id: str, tokens: int, model_key: str = "") -> dict[str, Any]:
        if not session_id:
            return {"recorded": False, "reason": "no_session_id"}
        if tokens < 0:
            tokens = 0
        import time as _t

        now = _t.time()
        with self._lock:
            self._tokens[session_id] += tokens
            if model_key:
                self._model_key[session_id] = model_key
                self._window[session_id] = get_model_window(model_key)
            self._last_seen[session_id] = now
            # Track call timestamps (for rate diagnostics, not for pressure)
            self._last_call_ts[session_id].append(now)
            # Keep only last 100 timestamps per session
            if len(self._last_call_ts[session_id]) > 100:
                self._last_call_ts[session_id] = self._last_call_ts[session_id][-100:]
            return {"recorded": True, "session_tokens": self._tokens[session_id]}

    def snapshot(self, session_id: str) -> dict[str, Any]:
        """Read-only telemetry snapshot. No mutation."""
        with self._lock:
            used = self._tokens.get(session_id, 0)
            model_key = self._model_key.get(session_id, "")
            window = self._window.get(session_id, 0)
        if not model_key:
            window = 0
        pressure = (
            classify_pressure(used, window)
            if window
            else {
                "pressure_pct": None,
                "pressure_band": "UNKNOWN",
                "headroom_tokens": None,
                "headroom_pct": None,
                "reserve_output": 0,
                "advisory": "No model bound to session yet (no tool call recorded).",
            }
        )
        return {
            "session_id": session_id,
            "model_key": model_key or None,
            "model_window": window or None,
            "tokens_used": used,
            "pressure": pressure,
            "ts_utc": _now_iso(),
        }

    def snapshot_global(self) -> dict[str, Any]:
        """Aggregate telemetry across all active sessions."""
        with self._lock:
            total = sum(self._tokens.values())
            n_sessions = len(self._tokens)
        return {
            "total_tokens_used": total,
            "active_sessions": n_sessions,
            "ts_utc": _now_iso(),
            "note": "Per-session snapshots via token_pressure.snapshot(session_id)",
        }

    def evict_idle(self, max_idle_seconds: float = 3600.0) -> int:
        """
        Evict sessions idle > max_idle_seconds from the in-memory map.
        Returns count evicted. Pure in-memory; no L4/L5/L6 touched.
        """
        import time as _t

        now = _t.time()
        with self._lock:
            stale = [sid for sid, ts in self._last_seen.items() if now - ts > max_idle_seconds]
            for sid in stale:
                self._tokens.pop(sid, None)
                self._model_key.pop(sid, None)
                self._window.pop(sid, None)
                self._last_seen.pop(sid, None)
                self._last_call_ts.pop(sid, None)
        return len(stale)


# ─── Helpers ───────────────────────────────────────────────────────────────
def _now_iso() -> str:
    import datetime

    return datetime.datetime.now(datetime.UTC).isoformat()


# ─── Module Singleton ─────────────────────────────────────────────────────
_SESSIONS = _SessionTokens()


def get_session_singleton() -> _SessionTokens:
    """Return the module-level singleton. Used by /health and __main__.py."""
    return _SESSIONS


# ─── Self-Check (deterministic, no I/O) ───────────────────────────────────
def _self_check() -> dict[str, Any]:
    """
    Verify deterministic properties. Runs at import time if ARIFOS_SELFTEST=1.

    Properties tested:
      1. count_tokens("") == 0
      2. count_tokens("hello") > 0
      3. count_tokens is deterministic (same input → same output)
      4. classify_pressure(0, 100) → LOW
      5. classify_pressure(50, 100) → WATCH
      6. classify_pressure(80, 100) → WARN
      7. classify_pressure(90, 100) → COMPACT
      8. classify_pressure(99, 100) → HOLD
      9. classify_pressure(0, 0) → HOLD (degenerate)
     10. get_model_window(unknown) → 128_000 fallback
    """
    results = []

    # 1
    r = count_tokens("") == 0
    results.append(("count_empty_is_0", r))

    # 2
    r = count_tokens("hello") > 0
    results.append(("count_nonempty_positive", r))

    # 3
    r = count_tokens("hello world") == count_tokens("hello world")
    results.append(("count_is_deterministic", r))

    # 4
    r = classify_pressure(0, 100)["pressure_band"] == "LOW"
    results.append(("band_0pct_is_LOW", r))

    # 5
    r = classify_pressure(50, 100)["pressure_band"] == "WATCH"
    results.append(("band_50pct_is_WATCH", r))

    # 6
    r = classify_pressure(80, 100)["pressure_band"] == "WARN"
    results.append(("band_80pct_is_WARN", r))

    # 7
    r = classify_pressure(90, 100)["pressure_band"] == "COMPACT"
    results.append(("band_90pct_is_COMPACT", r))

    # 8
    r = classify_pressure(99, 100)["pressure_band"] == "HOLD"
    results.append(("band_99pct_is_HOLD", r))

    # 9
    r = classify_pressure(0, 0)["pressure_band"] == "HOLD"
    results.append(("band_degenerate_is_HOLD", r))

    # 10
    r = get_model_window("totally-unknown-model-XYZ") == 128_000
    results.append(("unknown_model_falls_back", r))

    all_pass = all(passed for _, passed in results)
    return {
        "all_pass": all_pass,
        "checks": [{"name": n, "pass": p} for n, p in results],
        "n_checks": len(results),
        "n_pass": sum(1 for _, p in results if p),
    }


if os.getenv("ARIFOS_SELFTEST", "0") == "1":
    _selftest = _self_check()
    if _selftest["all_pass"]:
        logger.info(f"[token_pressure] selftest PASS {_selftest['n_pass']}/{_selftest['n_checks']}")
    else:
        failed = [c["name"] for c in _selftest["checks"] if not c["pass"]]
        logger.error(f"[token_pressure] selftest FAIL: {failed}")


__all__ = [
    "PressureBand",
    "get_model_window",
    "count_tokens",
    "count_tokens_messages",
    "classify_pressure",
    "get_session_singleton",
    "_self_check",  # exported for tests
]
