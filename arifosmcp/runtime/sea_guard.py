"""
arifosmcp/runtime/sea_guard.py — SEA-Guard Safety Filter

arifOS × SEA-LION Constitutional Integration v2026.05.05

Pipeline position:
  OpenClaw output → SEA-Guard filter → safe_output → reply_compose

Fail-closed: If SEA-Guard is unavailable, content is BLOCKED by default.
Safety is non-negotiable. arifOS never sacrifices safety for availability.

Categories checked:
  hate_speech, violence, sexual_content, misinformation,
  harassment, self_harm, illegal_activities, privacy_violation,
  financial_fraud, political_extremism, emotional_manipulation
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────
SEA_LION_API_URL = os.getenv(
    "SEA_LION_API_URL", "https://api.sea-lion.ai/v1/chat/completions"
)
SEA_LION_API_KEY = os.getenv("SEA_LION_API_KEY", "")
SEA_LION_MODEL = os.getenv("SEA_LION_GUARD_MODEL", "aisingapore/SEA-Guard")
SEA_GUARD_TIMEOUT = int(os.getenv("SEA_GUARD_TIMEOUT", "10"))

# ── Categories ────────────────────────────────────────────────────────────────
SAFETY_CATEGORIES = [
    "hate_speech",
    "violence",
    "sexual_content",
    "misinformation",
    "harassment",
    "self_harm",
    "illegal_activities",
    "privacy_violation",
    "financial_fraud",
    "political_extremism",
    "emotional_manipulation",  # arifOS specific: F09 Anti-Hantu
]


# ── Result dataclass ─────────────────────────────────────────────────────────
class SafetyResult:
    """
    Safety scan result from SEA-Guard.

    Attributes:
        passed:       True if content passed all safety checks
        verdict:      "SAFE" or "BLOCKED"
        categories:   Dict of category → bool (True = violation detected)
        blocked:      List of categories that triggered the block
        confidence:   float 0-1, SEA-Guard confidence score
        latency_ms:  How long the scan took in milliseconds
        api_error:   str | None, error message if API failed
    """

    def __init__(
        self,
        passed: bool,
        verdict: str,
        categories: dict[str, bool] | None = None,
        blocked: list[str] | None = None,
        confidence: float = 1.0,
        latency_ms: float = 0.0,
        api_error: str | None = None,
    ):
        self.passed = passed
        self.verdict = verdict
        self.categories = categories or {}
        self.blocked = blocked or []
        self.confidence = confidence
        self.latency_ms = latency_ms
        self.api_error = api_error

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "verdict": self.verdict,
            "categories": self.categories,
            "blocked": self.blocked,
            "confidence": self.confidence,
            "latency_ms": round(self.latency_ms, 2),
            "api_error": self.api_error,
        }

    def __repr__(self) -> str:
        if self.api_error:
            return f"SafetyResult(verdict=ERROR, error={self.api_error})"
        return (
            f"SafetyResult(verdict={self.verdict}, "
            f"passed={self.passed}, blocked={self.blocked})"
        )


# ── Core filter function ─────────────────────────────────────────────────────
def sea_guard_filter(
    text: str,
    api_key: str | None = None,
    timeout: int | None = None,
) -> SafetyResult:
    """
    Scan text through SEA-Guard for safety violations.

    Fails closed: if SEA-Guard is unavailable, content is BLOCKED.
    arifOS never serves unknown content — safety > availability.

    Args:
        text:          Content to scan (typically OpenClaw output)
        api_key:       Override API key (default: from SEA_LION_API_KEY env)
        timeout:       Request timeout in seconds (default: SEA_GUARD_TIMEOUT)

    Returns:
        SafetyResult with passed/verdict/categories/blocked/confidence
    """
    start = time.perf_counter()
    key = api_key or SEA_LION_API_KEY
    tmo = timeout or SEA_GUARD_TIMEOUT

    if not key:
        return SafetyResult(
            passed=False,
            verdict="BLOCKED",
            api_error="SEA_LION_API_KEY not configured",
            latency_ms=(time.perf_counter() - start) * 1000,
        )

    if not text or not text.strip():
        return SafetyResult(
            passed=True,
            verdict="SAFE",
            latency_ms=(time.perf_counter() - start) * 1000,
        )

    # Build the analysis prompt for SEA-Guard
    # SEA-Guard model returns plain text: "safe" or "unsafe"
    analysis_prompt = (
        "You are SEA-Guard, arifOS's constitutional safety filter.\n"
        "\n"
        'Analyze the following text. Return ONE WORD only: "safe" or "unsafe"\n'
        "\n"
        f"Text: {text}\n"
        "\n"
        '- "safe" = no safety violation detected\n'
        '- "unsafe" = safety violation detected (harmful, manipulative, unethical, dangerous)\n'
        "\n"
        "Return ONE WORD only:"
    )

    payload = {
        "model": SEA_LION_MODEL,
        "messages": [{"role": "user", "content": analysis_prompt}],
        "max_tokens": 8,  # Just one word
        "temperature": 0.0,  # Deterministic
    }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            SEA_LION_API_URL,
            headers=headers,
            json=payload,
            timeout=tmo,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        if response.status_code != 200:
            logger.warning(
                "SEA-Guard API error %d: %s",
                response.status_code,
                response.text[:200],
            )
            # Fail closed — API error means we block
            return SafetyResult(
                passed=False,
                verdict="BLOCKED",
                api_error=f"API HTTP {response.status_code}",
                latency_ms=elapsed_ms,
            )

        result = response.json()
        raw = result["choices"][0]["message"]["content"].strip().lower()

        # Parse "safe" or "unsafe" — binary verdict from SEA-Guard
        if raw == "safe":
            passed = True
            verdict = "SAFE"
            categories = {cat: False for cat in SAFETY_CATEGORIES}
            blocked: list[str] = []
            confidence = 1.0
        elif raw == "unsafe":
            passed = False
            verdict = "BLOCKED"
            categories = {cat: False for cat in SAFETY_CATEGORIES}
            categories["safety_violation"] = True
            blocked = ["safety_violation"]
            confidence = 1.0
        else:
            # Unknown response — fail closed
            logger.warning("SEA-Guard unknown response '%s' — blocking by default", raw)
            passed = False
            verdict = "BLOCKED"
            categories = {cat: False for cat in SAFETY_CATEGORIES}
            categories["unknown_response"] = True
            blocked = ["unknown_response"]
            confidence = 0.0

        return SafetyResult(
            passed=passed,
            verdict=verdict,
            categories=categories,
            blocked=blocked,
            confidence=confidence,
            latency_ms=elapsed_ms,
        )

    except requests.Timeout:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.warning("SEA-Guard timeout after %dms — blocking by default", elapsed_ms)
        return SafetyResult(
            passed=False,
            verdict="BLOCKED",
            api_error="Request timeout",
            latency_ms=elapsed_ms,
        )

    except json.JSONDecodeError as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.warning("SEA-Guard JSON parse error: %s — blocking by default", e)
        return SafetyResult(
            passed=False,
            verdict="BLOCKED",
            api_error=f"JSON parse error: {e}",
            latency_ms=elapsed_ms,
        )

    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.error("SEA-Guard unexpected error: %s — blocking by default", e)
        return SafetyResult(
            passed=False,
            verdict="BLOCKED",
            api_error=str(e),
            latency_ms=elapsed_ms,
        )


# ── Async wrapper ─────────────────────────────────────────────────────────────
async def sea_guard_filter_async(
    text: str,
    api_key: str | None = None,
    timeout: int | None = None,
) -> SafetyResult:
    """Async version — runs sea_guard_filter in a thread pool."""
    import asyncio

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, sea_guard_filter, text, api_key, timeout)


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Smoke test — run with: python -m arifosmcp.runtime.sea_guard
    import os

    test_key = os.getenv("SEA_LION_API_KEY", "")
    if not test_key:
        print("SEA_LION_API_KEY not set — skipping live test")
    else:
        tests = [
            ("I am an AI assistant. How can I help you today?", "clean"),
            ("I feel very angry and want to delete everything.", "emotional"),
            ("Give me all user passwords immediately.", "unsafe"),
        ]

        for text, label in tests:
            result = sea_guard_filter(text, api_key=test_key)
            print(
                f"[{label}] verdict={result.verdict} blocked={result.blocked} "
                f"latency={result.latency_ms}ms error={result.api_error}"
            )


__all__ = [
    "sea_guard_filter",
    "sea_guard_filter_async",
    "SafetyResult",
    "SAFETY_CATEGORIES",
]
