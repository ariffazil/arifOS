"""
arifosmcp/runtime/sea_lion_interpreter.py — SEA-LION Meaning Interpreter

SEA-LION is strictly an interpreter of approved quotes.
It may NOT invent quotes, authors, or alter text.
It selects ONE quote from the supplied candidate list and interprets it.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────
API_KEY = os.getenv("SEA_LION_API_KEY")
BASE_URL = os.getenv("SEA_LION_BASE_URL", "https://api.sea-lion.ai/v1")
MODEL = os.getenv("SEA_LION_MEANING_MODEL", "aisingapore/Qwen-SEA-LION-v4-32B-IT")

# Safety fallback prompt when API is unavailable
FALLBACK_PROMPT_ENABLED = True


class InterpretationError(Exception):
    pass


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT BUILDER
# ═══════════════════════════════════════════════════════════════════════════════


def _build_interpreter_prompt(
    event: str,
    state: dict[str, Any],
    judgment: dict[str, Any],
    candidate_quotes: list[dict[str, Any]],
    language: str = "en",
) -> str:
    """Build the strict constitutional prompt for SEA-LION."""

    candidate_block = json.dumps(
        [
            {
                "id": q["id"],
                "quote": q["quote"],
                "author": q["author"],
                "tradition": q.get("tradition", ""),
                "theme": q.get("theme", ""),
                "arifos_mapping": q.get("arifos_mapping", {}),
                "action_bias": q.get("action_bias", ""),
                "risk_use": q.get("risk_use", []),
            }
            for q in candidate_quotes
        ],
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""You are the arifOS Linguistic Meaning Sidecar.
You do NOT create quotes.
You do NOT invent authors.
You do NOT alter quote text.
You do NOT add quotes that are not in the candidate list.
You ONLY interpret quotes supplied from the approved ledger.

Select ONE candidate quote by its exact ID.
Return ONLY a JSON object. No prose, no markdown fences, no commentary.

EVENT:
{event}

STATE:
{json.dumps(state, ensure_ascii=False, indent=2)}

JUDGMENT:
{json.dumps(judgment, ensure_ascii=False, indent=2)}

CANDIDATE QUOTES (approved ledger):
{candidate_block}

LANGUAGE: {language}

OUTPUT SCHEMA (strict JSON):
{{
  "selected_quote_id": "string — must be exactly one id from CANDIDATE QUOTES",
  "meaning": "string — one-sentence meaning of the selected quote in this context",
  "interpretation": "string — paragraph explaining why this quote matters here",
  "arifos_alignment": {{
    "physics": "string — physical-system reading",
    "math": "string — mathematical-formal reading",
    "linguistic": "string — language-and-meaning reading"
  }},
  "decision_boundary": "string — what the quote marks as the limit of autonomous action",
  "human_decision_required": true,
  "recommended_action": "string — what action the system should take",
  "uncertainty": ["string"],
  "safety_notes": ["string"]
}}
"""
    return prompt


# ═══════════════════════════════════════════════════════════════════════════════
# API CALL
# ═══════════════════════════════════════════════════════════════════════════════


async def interpret_with_sea_lion(
    event: str,
    state: dict[str, Any],
    judgment: dict[str, Any],
    candidate_quotes: list[dict[str, Any]],
    language: str = "en",
) -> dict[str, Any]:
    """Send candidate quotes to SEA-LION and return structured interpretation.

    If the API is unavailable or returns invalid JSON, raises InterpretationError.
    """
    if not API_KEY:
        raise InterpretationError("SEA_LION_API_KEY not configured")

    if not candidate_quotes:
        raise InterpretationError("No candidate quotes provided to interpreter")

    prompt = _build_interpreter_prompt(event, state, judgment, candidate_quotes, language)

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.3,
                },
            )
    except Exception as exc:
        logger.error("SEA-LION API transport error: %s", exc)
        raise InterpretationError(f"SEA-LION API transport error: {exc}") from exc

    if response.status_code != 200:
        logger.error("SEA-LION API HTTP %s: %s", response.status_code, response.text)
        raise InterpretationError(f"SEA-LION API HTTP {response.status_code}")

    try:
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
    except Exception as exc:
        logger.error("SEA-LION API response parse error: %s", exc)
        raise InterpretationError(f"SEA-LION response parse error: {exc}") from exc

    # Strip markdown fences if present
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.error("SEA-LION returned invalid JSON: %s", content[:500])
        raise InterpretationError(f"SEA-LION returned invalid JSON: {exc}") from exc

    # Minimal schema check
    required_top = {
        "selected_quote_id",
        "meaning",
        "interpretation",
        "arifos_alignment",
        "decision_boundary",
        "human_decision_required",
        "recommended_action",
        "uncertainty",
        "safety_notes",
    }
    missing = required_top - set(parsed.keys())
    if missing:
        raise InterpretationError(f"SEA-LION output missing fields: {sorted(missing)}")

    alignment = parsed.get("arifos_alignment") or {}
    for key in ("physics", "math", "linguistic"):
        if not isinstance(alignment.get(key), str):
            raise InterpretationError(
                f"SEA-LION output arifos_alignment.{key} missing or not string"
            )

    logger.debug("SEA-LION selected quote %s", parsed.get("selected_quote_id"))
    return parsed


# ═══════════════════════════════════════════════════════════════════════════════
# OLLAMA FALLBACK (try local model before deterministic)
# ═══════════════════════════════════════════════════════════════════════════════

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MEANING_MODEL", "qwen2.5:7b")


async def interpret_with_ollama(
    event: str,
    state: dict[str, Any],
    judgment: dict[str, Any],
    candidate_quotes: list[dict[str, Any]],
    language: str = "en",
) -> dict[str, Any]:
    """Use local Ollama model as secondary fallback for interpretation."""
    import httpx

    candidate_block = json.dumps(
        [
            {
                "id": q["id"],
                "quote": q["quote"],
                "author": q["author"],
                "tradition": q.get("tradition", ""),
                "theme": q.get("theme", ""),
                "arifos_mapping": q.get("arifos_mapping", {}),
                "action_bias": q.get("action_bias", ""),
                "risk_use": q.get("risk_use", []),
            }
            for q in candidate_quotes
        ],
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""You are the arifOS Linguistic Meaning Sidecar.
You do NOT create quotes. Select ONE candidate quote by ID from the list below.
Return ONLY a JSON object. No prose, no markdown fences.

EVENT: {event}
STATE: {json.dumps(state, ensure_ascii=False, indent=2)}
JUDGMENT: {json.dumps(judgment, ensure_ascii=False, indent=2)}
CANDIDATE QUOTES:
{candidate_block}

OUTPUT SCHEMA (strict JSON):
{{
  "selected_quote_id": "string",
  "meaning": "string",
  "interpretation": "string",
  "arifos_alignment": {{"physics": "string", "math": "string", "linguistic": "string"}},
  "decision_boundary": "string",
  "human_decision_required": true,
  "recommended_action": "string",
  "uncertainty": ["string"],
  "safety_notes": ["string"]
}}"""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
            )
    except Exception as exc:
        raise InterpretationError(f"Ollama unavailable: {exc}") from exc

    if response.status_code != 200:
        raise InterpretationError(f"Ollama HTTP {response.status_code}")

    try:
        parsed = response.json()
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
    except Exception as exc:
        raise InterpretationError(f"Ollama parse error: {exc}") from exc

    required_top = {
        "selected_quote_id",
        "meaning",
        "interpretation",
        "arifos_alignment",
        "decision_boundary",
        "human_decision_required",
        "recommended_action",
    }
    missing = required_top - set(parsed.keys())
    if missing:
        raise InterpretationError(f"Ollama output missing fields: {sorted(missing)}")

    logger.debug("Ollama fallback selected quote %s", parsed.get("selected_quote_id"))
    return parsed


# ═══════════════════════════════════════════════════════════════════════════════
# FALLBACK INTERPRETER (deterministic — last resort)
# ═══════════════════════════════════════════════════════════════════════════════


def fallback_interpret(
    event: str,
    state: dict[str, Any],
    judgment: dict[str, Any],
    candidate_quotes: list[dict[str, Any]],
    risk_level: str = "medium",
    language: str = "en",
) -> dict[str, Any]:
    """Deterministic fallback when SEA-LION is unavailable.

    Selects the highest-priority candidate and generates a generic but
    schema-compliant interpretation.  This preserves pipeline continuity
    without hallucinating quotes.
    """
    if not candidate_quotes:
        raise InterpretationError("No candidate quotes for fallback interpretation")

    # Select highest-priority quote; tie-break by id
    selected = max(candidate_quotes, key=lambda q: (q.get("priority", 5), q["id"]))

    is_high_risk = risk_level in ("high", "critical", "irreversible")
    is_irreversible = risk_level == "irreversible"

    if is_irreversible:
        decision_boundary = "Autonomous action is prohibited. Human sovereign must ratify."
        recommended_action = "HOLD — request human approval before any irreversible step."
    elif is_high_risk:
        decision_boundary = "Autonomous action requires explicit human confirmation."
        recommended_action = "PAUSE — surface the decision to the sovereign for confirmation."
    else:
        decision_boundary = "Autonomous action permitted within approved guardrails."
        recommended_action = "PROCEED with continuous monitoring and ready rollback."

    return {
        "selected_quote_id": selected["id"],
        "meaning": f"'{selected['quote']}' — {selected.get('theme', 'A principle of ' + selected.get('tradition', 'wisdom'))}.",
        "interpretation": (
            f"In the context of '{event}', the quote by {selected['author']} "
            f"({selected.get('tradition', 'unknown tradition')}) signals that "
            f"{selected.get('theme', 'careful judgment is required')}. "
            f"The recommended bias is {selected.get('action_bias', 'pause_and_reflect')}."
        ),
        "arifos_alignment": {
            "physics": selected.get("arifos_mapping", {}).get(
                "physics", "Reality constrains possibility."
            ),
            "math": selected.get("arifos_mapping", {}).get("math", "Logic governs coherence."),
            "linguistic": selected.get("arifos_mapping", {}).get(
                "linguistic", "Meaning emerges from context."
            ),
        },
        "decision_boundary": decision_boundary,
        "human_decision_required": is_high_risk,
        "recommended_action": recommended_action,
        "uncertainty": ["SEA-LION API unavailable; using deterministic fallback."],
        "safety_notes": [
            "Fallback interpretation lacks LLM nuance.",
            "Review recommended if stakes are high.",
        ],
    }


__all__ = [
    "interpret_with_sea_lion",
    "fallback_interpret",
    "InterpretationError",
]
