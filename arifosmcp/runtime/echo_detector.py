"""
echo_detector.py — Receipt-Echo Detection
══════════════════════════════════════════

RSI EUREKA 2026-06-12: Forge #1
Source: ASI💃 receipt-loop observation (2026-06-12)

Problem: Hermes auto-attaches CLAIM blocks from previous assistant outputs
as if they were new input. The agent re-processes its own sealed answers,
creating a receipt-loop (ceremony, not cognition).

Solution: Before processing any incoming message, check if it is >80% similar
to a previously-issued output. If so, flag as ECHO and skip re-processing.

F-binding:
  F2 TRUTH:  honest about what's a receipt vs what's a new prompt
  F4 CLARITY: reduces entropy by preventing re-processing loops
  F7 HUMILITY: doesn't claim to understand new meaning from old text
  F1 AMANAH: fully reversible — delete this file to remove the feature

Usage:
  from arifosmcp.runtime.echo_detector import detect_echo
  result = detect_echo(incoming_message, previous_outputs)
  if result["is_echo"]:
      return {"verdict": "ECHO", "reply": "itu echo."}

DITEMPA BUKAN DIBERI — The echo is not a new question.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


# ─── Configuration ────────────────────────────────────────────────────────────
ECHO_SIMILARITY_THRESHOLD = 0.80  # 80% token overlap = echo
MIN_MESSAGE_LENGTH_CHARS = 100  # Don't bother with short messages
MIN_PREVIOUS_OUTPUT_LENGTH_CHARS = 200  # Don't match against short outputs
MAX_PREVIOUS_OUTPUTS_TO_CHECK = 10  # Only check last N outputs


def _normalize(text: str) -> str:
    """Strip whitespace, normalize to lowercase, collapse repeated spaces."""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _tokenize(text: str) -> set[str]:
    """Simple whitespace tokenization into a set of unique tokens."""
    return set(_normalize(text).split())


def detect_echo(
    incoming_message: str,
    previous_outputs: list[str],
    threshold: float = ECHO_SIMILARITY_THRESHOLD,
) -> dict[str, Any]:
    """Check if incoming message is an echo of a previous output.

    Uses Jaccard similarity on token sets. Simple, deterministic, no LLM needed.

    Args:
        incoming_message: The new message to check.
        previous_outputs: List of previously-issued assistant outputs (newest last).
        threshold: Jaccard similarity above which to flag as echo (default 0.80).

    Returns:
        {
            "is_echo": bool,
            "similarity": float,          # highest similarity found
            "matched_output_index": int | None,  # which previous output matched
            "matched_output_hash": str | None,   # sha256 of matched output
            "advice": str,
            "gate_id": "echo_detector_N1",
        }
    """
    if not incoming_message or len(incoming_message.strip()) < MIN_MESSAGE_LENGTH_CHARS:
        return {
            "is_echo": False,
            "similarity": 0.0,
            "matched_output_index": None,
            "matched_output_hash": None,
            "advice": "Message too short for echo detection.",
            "gate_id": "echo_detector_N1",
        }

    incoming_tokens = _tokenize(incoming_message)
    if len(incoming_tokens) == 0:
        return {
            "is_echo": False,
            "similarity": 0.0,
            "matched_output_index": None,
            "matched_output_hash": None,
            "advice": "Message has no tokens after normalization.",
            "gate_id": "echo_detector_N1",
        }

    # Only check the last N outputs, newest first
    outputs_to_check = previous_outputs[-MAX_PREVIOUS_OUTPUTS_TO_CHECK:]
    outputs_to_check.reverse()  # newest first

    best_similarity = 0.0
    best_index = None
    best_hash = None

    for i, prev_output in enumerate(outputs_to_check):
        if len(prev_output) < MIN_PREVIOUS_OUTPUT_LENGTH_CHARS:
            continue

        prev_tokens = _tokenize(prev_output)
        if len(prev_tokens) == 0:
            continue

        # Jaccard similarity: |A ∩ B| / |A ∪ B|
        intersection = len(incoming_tokens & prev_tokens)
        union = len(incoming_tokens | prev_tokens)
        similarity = intersection / union if union > 0 else 0.0

        if similarity > best_similarity:
            best_similarity = similarity
            best_index = len(previous_outputs) - 1 - i  # original index
            best_hash = hashlib.sha256(prev_output.encode()).hexdigest()[:16]

    is_echo = best_similarity >= threshold

    return {
        "is_echo": is_echo,
        "similarity": round(best_similarity, 4),
        "matched_output_index": best_index,
        "matched_output_hash": best_hash,
        "advice": (
            f"ECHO_DETECTED: {best_similarity:.0%} overlap with output #{best_index} "
            f"(hash={best_hash}). This is a receipt, not a new prompt."
            if is_echo
            else f"FRESH: max similarity {best_similarity:.0%} — below threshold {threshold:.0%}."
        ),
        "gate_id": "echo_detector_N1",
    }


# ─── Self-check ──────────────────────────────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """Verify the echo detector behaves correctly on known cases."""
    results = []

    # Test 1: identical text = echo
    text = "This is a long CLAIM block that was previously sent by the agent. " * 5
    r = detect_echo(text, [text])
    results.append(("identical_text_is_echo", r["is_echo"] is True, r))

    # Test 2: completely different text = fresh
    r = detect_echo("What is the weather today?", [text])
    results.append(("different_text_is_fresh", r["is_echo"] is False, r))

    # Test 3: high overlap (truncated version of same text = echo)
    # In real receipt-loops, the CLAIM block is the same content, just replayed.
    # Truncating the last sentence simulates near-identical content.
    truncated = text[: int(len(text) * 0.9)]  # 90% of the original
    r = detect_echo(truncated, [text])
    results.append(("high_overlap_is_echo", r["is_echo"] is True, r))

    # Test 4: short message = skip
    r = detect_echo("ok", [text])
    results.append(("short_message_skipped", r["is_echo"] is False, r))

    # Test 5: empty input = skip
    r = detect_echo("", [text])
    results.append(("empty_input_skipped", r["is_echo"] is False, r))

    passed = sum(1 for name, ok, _ in results if ok)
    total = len(results)

    return {
        "module": "echo_detector",
        "passed": passed,
        "total": total,
        "verdict": "PASS" if passed == total else "FAIL",
        "results": [{"test": name, "pass": ok} for name, ok, _ in results],
    }


if __name__ == "__main__":
    import json as _json

    sc = _self_check()
    print(_json.dumps(sc, indent=2))
    raise SystemExit(0 if sc["verdict"] == "PASS" else 1)
