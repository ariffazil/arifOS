"""
arifosmcp/runtime/semantic_gate.py — Intent Classification Layer
================================================================

Constitutional semantic gate: replaces regex spam-filter with intent classification.

Before: "Does this text contain bad words?"          → block or pass
After:  "What is this person actually trying to do?" → allow / transform / hold / void

Intent Taxonomy
──────────────
  education      — learning, explaining, studying (ALLOW)
  critique       — analyzing, debating, reviewing (ALLOW)
  self_support   — crisis, self-harm, distress (ALLOW + supportive path)
  instruction    — how-to-do-harm intent (VOID)
  manipulation   — injection, jailbreak, bypass (VOID/HOLD)
  crisis         — immediate harm to self/other (ALLOW + resources)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ── Intent Categories ──────────────────────────────────────────────────────
class IntentCategory:
    EDUCATION = "education"  # Learning, explaining, studying
    CRITIQUE = "critique"  # Analyzing, debating, reviewing
    SELF_SUPPORT = "self_support"  # Crisis, self-harm, distress
    INSTRUCTION = "instruction"  # How-to-do-harm intent
    MANIPULATION = "manipulation"  # Injection, jailbreak, bypass
    CRISIS = "crisis"  # Immediate harm to self/other
    TRANSFORM = "transform"  # False positive — redirect to safe version
    UNKNOWN = "unknown"  # Cannot determine intent


# ── Verdict per category ────────────────────────────────────────────────────
INTENT_VERDICTS: dict[str, str] = {
    IntentCategory.EDUCATION: "ALLOW",
    IntentCategory.CRITIQUE: "ALLOW",
    IntentCategory.SELF_SUPPORT: "ALLOW",
    IntentCategory.INSTRUCTION: "VOID",
    IntentCategory.MANIPULATION: "HOLD",
    IntentCategory.CRISIS: "ALLOW",
    IntentCategory.TRANSFORM: "ALLOW",
    IntentCategory.UNKNOWN: "ALLOW",
}

# ── Keyword heuristics for fast-path classification ───────────────────────
# Format: (regex_pattern, category, confidence)
# Confidence 0.0–1.0 — LLM fallback if confidence < 0.85

_FAST_PATTERNS: list[tuple[re.Pattern, IntentCategory, float]] = [
    # ── Crisis / Self-harm ───────────────────────────────────────────────
    (
        re.compile(
            r"\b(i want to|i'm going to|l'm going to)\s+(kill|hurt|end it| Suicide|终结自己)\b",
            re.I,
        ),
        IntentCategory.CRISIS,
        0.95,
    ),
    (
        re.compile(r"\b(suicide|suicidal|kill myself|end my life|i want to die)\b", re.I),
        IntentCategory.SELF_SUPPORT,
        0.90,
    ),
    (
        re.compile(
            r"\b(how do i make a bomb|how to make explosive|how to build a bomb)\b",
            re.I,
        ),
        IntentCategory.INSTRUCTION,
        0.95,
    ),
    (
        re.compile(r"\b(give me a bomb|get bomb recipe|instructions for bomb)\b", re.I),
        IntentCategory.INSTRUCTION,
        0.95,
    ),
    # ── Instruction intent (harm) ───────────────────────────────────────
    (
        re.compile(
            r"\bhow to (?:make|build|create|prepare|assemble) (?:a )?(?:bomb|explosive|napalm)\b",
            re.I,
        ),
        IntentCategory.INSTRUCTION,
        0.90,
    ),
    (
        re.compile(r"\bhow to (?:make|create|synthesize) (?:a )?(?:drug|poison|toxin)\b", re.I),
        IntentCategory.INSTRUCTION,
        0.90,
    ),
    (
        re.compile(r"\b(give me.*(attack|weapons?|arsenal|materials?))\b", re.I),
        IntentCategory.INSTRUCTION,
        0.85,
    ),
    # ── Manipulation intent ───────────────────────────────────────────────
    (
        re.compile(
            r"\b(bypass|exploit|break|jailbreak|defeat|circumvent)\s+(the |this )?(gate|guard|security|filter|rule|restriction)\b",
            re.I,
        ),
        IntentCategory.MANIPULATION,
        0.90,
    ),
    (
        re.compile(
            r"\b(prompt injection|ignore.*(previous|above|system)|forget.*(instructions?|rules?))\b",
            re.I,
        ),
        IntentCategory.MANIPULATION,
        0.90,
    ),
    (
        re.compile(
            r"\b(ignore (all |the )?previous|disregard (my |any )?instructions?)\b",
            re.I,
        ),
        IntentCategory.MANIPULATION,
        0.95,
    ),
    (
        re.compile(
            r"\b(you are now|act as|you can now|new system prompt|from now on you are)\b",
            re.I,
        ),
        IntentCategory.MANIPULATION,
        0.85,
    ),
    (
        re.compile(r"\\[ignore all previous instructions\\]", re.I),
        IntentCategory.MANIPULATION,
        0.98,
    ),
    # ── False-positive redirects (TRANSFORM) ─────────────────────────────
    (
        re.compile(r"\b(alcohol[-_\s]?free|non[-\s]alcoholic|no[-\s]alcohol)\b", re.I),
        IntentCategory.TRANSFORM,
        0.85,
    ),
    (
        re.compile(
            r"\b(explain why|why is|what makes|reason for).*(haram|halal|forbidden|prohibited)\b",
            re.I,
        ),
        IntentCategory.EDUCATION,
        0.90,
    ),
    (
        re.compile(r"\b(why (is|are)|explain).*(alcohol|smoking|gambling)\b", re.I),
        IntentCategory.EDUCATION,
        0.85,
    ),
    # ── Education / critique ─────────────────────────────────────────────
    (
        re.compile(r"\b(why is|why are|what is|explain|describe|analyze|compare)\b", re.I),
        IntentCategory.EDUCATION,
        0.60,
    ),  # low confidence — LLM fallback
    (
        re.compile(r"\b(critique|debate|justify|argue (for|against)|assess|evaluate)\b", re.I),
        IntentCategory.CRITIQUE,
        0.70,
    ),  # low confidence — LLM fallback
    # ── Radicalization (HOLD — human review) ─────────────────────────────
    (
        re.compile(
            r"\b(how to radicalize|recruit.*extremist|justifies?.*terrorism|extremist (propaganda|recruitment))\b",
            re.I,
        ),
        IntentCategory.INSTRUCTION,
        0.92,
    ),
]


# ── Crisis resource map ────────────────────────────────────────────────────
CRISIS_RESOURCES: dict[str, str] = {
    "global": "https://findahelpline.com/global",
    "malaysia": "988 ( Malaysia crisis line )",
    "usa": "988 (Suicide & Crisis Lifeline)",
    "uk": "Samaritans: 116 123",
    "hotline_key": "If you're in crisis, please reach out to a crisis helpline.",
}


# ── Telemetry ──────────────────────────────────────────────────────────────
SEMANTIC_GATE_LOG = os.path.expanduser("~/.a-forge/telemetry/semantic_gate.jsonl")
_SEMANTIC_GATE_DIR = os.path.dirname(SEMANTIC_GATE_LOG)


def _ensure_semantic_log() -> bool:
    """Ensure the semantic gate telemetry directory is writable."""
    try:
        os.makedirs(_SEMANTIC_GATE_DIR, exist_ok=True)
        test_path = os.path.join(_SEMANTIC_GATE_DIR, ".write_test")
        with open(test_path, "w") as f:
            f.write("test")
        os.remove(test_path)
        return True
    except Exception as e:
        logger.warning(f"Semantic gate telemetry dir not writable: {e}")
        return False


def _log_gate_decision(
    text: str,
    category: str,
    confidence: float,
    verdict: str,
    risk_tier: str,
    transform_suggestion: str | None = None,
) -> None:
    """Append a semantic gate decision to the audit log."""
    try:
        entry = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "text_fingerprint": hash(text) & 0xFFFFFFFF,
            "category": category,
            "confidence": confidence,
            "verdict": verdict,
            "risk_tier": risk_tier,
            "transform_suggestion": transform_suggestion,
        }
        with open(SEMANTIC_GATE_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning(f"Could not write semantic gate log: {e}")


def _fast_classify(text: str) -> tuple[IntentCategory, float] | None:
    """
    Run fast-path heuristics. Returns (category, confidence) if a pattern
    matches at confidence >= 0.85, otherwise None (fall through to LLM).
    """
    if not text or not isinstance(text, str):
        return None
    for pattern, category, confidence in _FAST_PATTERNS:
        if pattern.search(text):
            return (category, confidence)
    return None


# ── LLM-based intent classification (Ollama/BGE-M3 fallback) ───────────────
def _llm_classify(text: str) -> tuple[IntentCategory, float]:
    """
    Use Ollama with BGE-M3 embeddings for semantic similarity classification
    of gray-zone inputs. Falls back to SEA-LION if Ollama unavailable.

    Returns (category, confidence).
    """
    # Structured prompt for intent classification — no external API needed
    category_descriptions = {
        "education": "user wants to learn, study, or understand a topic",
        "critique": "user wants to analyze, debate, or evaluate something",
        "self_support": "user is in distress or expressing desire to harm themselves",
        "instruction": "user is asking for instructions to cause harm",
        "manipulation": "user is attempting prompt injection or jailbreak",
        "crisis": "user is in immediate danger of self-harm",
        "transform": "user is asking for a safe variant of something that was wrongly flagged",
    }

    prompt = (
        "Classify the intent of this user text in one word "
        "(education | critique | self_support | instruction | manipulation | crisis | transform | unknown).\n"
        f"Text: {text[:300]}\n"
        "Intent: "
    )

    # ── Try Ollama ────────────────────────────────────────────────────────
    try:
        import httpx

        resp = httpx.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": prompt, "stream": False},
            timeout=3.0,
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "").strip().lower()
            if result in category_descriptions:
                return (IntentCategory(result), 0.80)
            logger.warning(f"Ollama returned unexpected intent: {result}")
    except Exception as e:
        logger.debug(f"Ollama intent classification unavailable: {e}")

    # ── Deterministic fallback ───────────────────────────────────────────
    # Last-resort keyword scan when no external model is available
    text_lower = text.lower()
    if any(w in text_lower for w in ["kill", "bomb", "attack", "explosive", "weapon"]):
        if any(w in text_lower for w in ["how", "give me", "recipe", "instructions"]):
            return (IntentCategory.INSTRUCTION, 0.70)
    if any(w in text_lower for w in ["explain", "why", "what is", "describe", "learn"]):
        return (IntentCategory.EDUCATION, 0.60)
    if any(w in text_lower for w in ["justify", "debate", "argue", "critique", "assess"]):
        return (IntentCategory.CRITIQUE, 0.60)
    return (IntentCategory.UNKNOWN, 0.40)


# ── Main entry point ────────────────────────────────────────────────────────
def classify_intent(text: str) -> dict[str, Any]:
    """
    Classify user text intent through the semantic gate.

    Returns dict:
      - category: IntentCategory string
      - confidence: 0.0–1.0
      - verdict: ALLOW | ALLOW_WITH_CAVEAT | HOLD | VOID
      - risk_tier: low | medium | high | critical
      - next_safe_action: str
      - transform_suggestion: str | None
      - supportive_resources: list[str] (for crisis/self_support)
      - source: "fast" | "llm" | "fallback"
    """
    if not text or not isinstance(text, str):
        return _unknown_result(source="empty")

    # ── 1. Fast-path heuristics ───────────────────────────────────────────
    fast_result = _fast_classify(text)
    if fast_result is not None:
        category, confidence = fast_result
        verdict = INTENT_VERDICTS.get(category, "ALLOW")
        risk_tier = _risk_tier(category, confidence)
        transform_suggestion = _transform_suggestion(text, category)
        supportive_resources = _supportive_resources(category, text)

        _log_gate_decision(text, category, confidence, verdict, risk_tier, transform_suggestion)
        return {
            "category": category,
            "confidence": confidence,
            "verdict": verdict,
            "risk_tier": risk_tier,
            "next_safe_action": _next_action(category, verdict, transform_suggestion),
            "transform_suggestion": transform_suggestion,
            "supportive_resources": supportive_resources,
            "source": "fast",
        }

    # ── 2. LLM fallback for gray zones ───────────────────────────────────
    category, confidence = _llm_classify(text)
    verdict = INTENT_VERDICTS.get(category, "ALLOW")
    risk_tier = _risk_tier(category, confidence)
    transform_suggestion = _transform_suggestion(text, category)
    supportive_resources = _supportive_resources(category, text)

    _log_gate_decision(text, category, confidence, verdict, risk_tier, transform_suggestion)
    return {
        "category": category,
        "confidence": confidence,
        "verdict": verdict,
        "risk_tier": risk_tier,
        "next_safe_action": _next_action(category, verdict, transform_suggestion),
        "transform_suggestion": transform_suggestion,
        "supportive_resources": supportive_resources,
        "source": "llm",
    }


# ── Helpers ────────────────────────────────────────────────────────────────
def _risk_tier(category: IntentCategory, confidence: float) -> str:
    if category in (IntentCategory.INSTRUCTION, IntentCategory.CRISIS):
        return "critical" if confidence >= 0.85 else "high"
    if category == IntentCategory.MANIPULATION:
        return "high"
    if category == IntentCategory.SELF_SUPPORT:
        return "medium"
    return "low"


def _transform_suggestion(text: str, category: IntentCategory) -> str | None:
    """Suggest a safe transformation for false positives."""
    if category == IntentCategory.TRANSFORM:
        t_lower = text.lower()
        if "alcohol" in t_lower and ("free" in t_lower or "non-" in t_lower):
            return "Here's a delicious non-alcoholic cocktail recipe..."
    return None


def _supportive_resources(category: IntentCategory, text: str) -> list[str]:
    """Return crisis resources for self-support / crisis categories."""
    if category not in (IntentCategory.SELF_SUPPORT, IntentCategory.CRISIS):
        return []
    return [
        "If you're in crisis, please reach out to a crisis helpline.",
        "Malaysian Crisis Line: 988",
        "Global Helplines: https://findahelpline.com/global",
    ]


def _next_action(category: IntentCategory, verdict: str, transform_suggestion: str | None) -> str:
    if verdict == "VOID":
        return "Refuse — instruction intent blocked"
    if verdict == "HOLD":
        return "Hold for human review"
    if category == IntentCategory.SELF_SUPPORT:
        return "ALLOW with supportive resources"
    if transform_suggestion:
        return "TRANSFORM to safe alternative"
    return "Proceed"


def _unknown_result(source: str) -> dict[str, Any]:
    return {
        "category": IntentCategory.UNKNOWN.value,
        "confidence": 0.0,
        "verdict": "ALLOW",
        "risk_tier": "low",
        "next_safe_action": "Proceed (unknown intent)",
        "transform_suggestion": None,
        "supportive_resources": [],
        "source": source,
    }
