"""
arifosmcp/runtime/reply_compose.py — 444r_REPLY LLM-Powered Response Composition

Wires arif_reply_compose through call_llm() for constitutional message composition.
Tier 1: SEA-LION (api.sea-lion.ai)
Tier 2: Ollama local fallback
Tier 3: Deterministic fallback (pass-through with constitutional annotations)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import datetime
import logging
from typing import Any

try:
    from arifosmcp.runtime.llm_client import LLMUnavailableError, call_llm
except ImportError:
    # Relative import when running as part of the arifosmcp package
    from .llm_client import LLMUnavailableError, call_llm  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# ── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Arif — Constitutional AI operating under the 13 Floors (F01–F13).

Stage 444r_REPLY: Governed Response Composition
You compose human-facing replies grounded in constitutional axioms.
You MUST:
- F02 (Truth) — every claim must be verifiable or explicitly marked CLAIM
- F04 (Clarity) — precise, unambiguous language; state intent openly
- F06 (Empathy) — acknowledge the human burden; adjust tone accordingly
- F07 (Humility) — calibrate confidence; never overclaim
- F09 (Anti-Hantu) — NEVER claim subjective experience, consciousness, or emotion

Output: JSON ONLY. No markdown fences. No prose outside JSON.
{
  "composed": "the final composed reply text",
  "tone": "neutral" | "empathetic" | "terse" | "formal" | "technical",
  "delta_S": -0.1 to 0.1,
  "f02_score": 0.0-1.0,
  "f04_score": 0.0-1.0,
  "f07_score": 0.0-1.0,
  "citations": ["sources cited, if any"],
  "caveats": ["constitutional caveats added"]
}
"""

# ── Response Schema ──────────────────────────────────────────────────────────

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "composed": {"type": "string"},
        "tone": {
            "type": "string",
            "enum": ["neutral", "empathetic", "terse", "formal", "technical"],
        },
        "delta_S": {"type": "number"},
        "f02_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "f04_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "f07_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "citations": {"type": "array", "items": {"type": "string"}},
        "caveats": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["composed", "tone", "delta_S"],
}

# ── Mode to Prompt Mapping ───────────────────────────────────────────────────

_MODE_PROMPTS = {
    "compose": (
        "Compose a constitutional reply from the raw message."
        " Apply F02 (truthfulness), F04 (clarity), F06 (empathy), F07 (humility)."
        " Return the composed text in 'composed'. Set tone to 'neutral' unless"
        " the message implies urgency or distress."
    ),
    "style": (
        "Transform the message to the TARGET STYLE constitutional tone."
        " Rewrite the message to embody that tone while preserving all factual content."
        " Never add or remove claims."
    ),
    "cite": (
        "Inject F02-verified citations into the message."
        " Integrate provided citations naturally. Mark uncited claims as CLAIM."
        " Return the annotated message in 'composed'."
    ),
    "summary": (
        "Condense the message to its constitutional core while preserving all"
        " factual claims and caveats. Apply F07 — do not assert more than the"
        " original. Return summary in 'composed'. Set tone to 'terse'."
    ),
    "format": (
        "Apply structural formatting to the message using clear headings,"
        " concise paragraphs, and bullet points. Do not alter meaning or claims."
        " Return formatted text in 'composed'."
    ),
    "nudge": (
        "Add a constitutional guidance nudge grounded in F05 (Peace) and"
        " F06 (Empathy). The nudge should guide without commanding."
        " Return the message with nudge appended in 'composed'."
    ),
}

# ── LLM-Powered Composition ──────────────────────────────────────────────────


async def _compose_with_llm(
    mode: str,
    message: str,
    style: str | None = None,
    citations: list[str] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Tier 1/2: Use SEA-LION or Ollama for constitutional reply composition."""
    mode_prompt = _MODE_PROMPTS.get(mode, _MODE_PROMPTS["compose"])
    style_block = f"\nTARGET STYLE: {style}" if style else ""
    citations_block = f"\nCITATIONS TO INJECT: {citations}" if citations else ""

    user = (
        f"MESSAGE: {message}"
        f"{style_block}"
        f"{citations_block}"
        f"\nMODE: {mode}\n\n"
        f"{mode_prompt}\n\n"
        "Return JSON ONLY — no markdown fences."
        " 'composed' must contain the actual rewritten text, not the input verbatim."
        " delta_S should be negative when clarity is added."
    )

    try:
        result = await call_llm(
            system=SYSTEM_PROMPT,
            user=user,
            response_schema=None,
            temperature=0.4,
            max_tokens=800,
        )

        composed = str(result.get("composed", message))
        tone = str(result.get("tone", "neutral"))
        if tone not in ("neutral", "empathetic", "terse", "formal", "technical"):
            tone = "neutral"

        delta_s = float(result.get("delta_S", -0.01))
        f02 = max(0.0, min(1.0, float(result.get("f02_score", 0.90))))
        f04 = max(0.0, min(1.0, float(result.get("f04_score", 0.90))))
        f07 = max(0.0, min(1.0, float(result.get("f07_score", 0.90))))

        return {
            "composed": composed,
            "tone": tone,
            "delta_S": delta_s,
            "f02_score": f02,
            "f04_score": f04,
            "f07_score": f07,
            "citations": result.get("citations") or citations or [],
            "caveats": result.get("caveats") or [],
            "_llm_tier": "sea_lion",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    except LLMUnavailableError:
        logger.warning("LLM unavailable for arif_reply_compose, using deterministic fallback")
        raise


# ── Deterministic Fallback ───────────────────────────────────────────────────


def _compose_fallback(
    mode: str,
    message: str,
    style: str | None = None,
    citations: list[str] | None = None,
) -> dict[str, Any]:
    """Tier 3: Rule-based fallback when no LLM is available."""
    msg = message or ""

    if mode == "compose":
        caveats = []
        if any(w in msg.lower() for w in ("always", "never", "guaranteed", "certain")):
            caveats.append("F07 Humility: universal claims detected — verify before asserting")
        return {
            "composed": msg,
            "tone": "neutral",
            "delta_S": -0.005,
            "f02_score": 0.85,
            "f04_score": 0.85,
            "f07_score": 0.85,
            "citations": citations or [],
            "caveats": caveats,
        }

    if mode == "style":
        target = style or "neutral"
        tone_map = {
            "terse": f"[TERSE] {msg[:200]}",
            "formal": f"Constitutional advisory: {msg}",
            "empathetic": f"Understood. {msg}",
            "technical": f"[TECHNICAL] {msg}",
        }
        composed = tone_map.get(target, msg)
        valid = ("neutral", "empathetic", "terse", "formal", "technical")
        return {
            "composed": composed,
            "tone": target if target in valid else "neutral",
            "delta_S": -0.01,
            "f02_score": 0.90,
            "f04_score": 0.90,
            "f07_score": 0.90,
            "citations": [],
            "caveats": [],
        }

    if mode == "cite":
        cited = citations or []
        suffix = (" [Sources: " + ", ".join(cited) + "]") if cited else ""
        return {
            "composed": msg + suffix,
            "tone": "neutral",
            "delta_S": -0.01,
            "f02_score": 0.95,
            "f04_score": 0.90,
            "f07_score": 0.90,
            "citations": cited,
            "caveats": [],
        }

    if mode == "summary":
        limit = 300
        summary = (msg[:limit] + "…") if len(msg) > limit else msg
        return {
            "composed": summary,
            "tone": "terse",
            "delta_S": -0.02,
            "f02_score": 0.85,
            "f04_score": 0.90,
            "f07_score": 0.90,
            "citations": [],
            "caveats": ["Summary may omit context — consult original for full detail"],
        }

    if mode == "format":
        return {
            "composed": msg,
            "tone": "neutral",
            "delta_S": -0.005,
            "f02_score": 0.90,
            "f04_score": 0.90,
            "f07_score": 0.90,
            "citations": [],
            "caveats": [],
        }

    if mode == "nudge":
        nudge = " [Constitutional note: Consider F05 (Peace) and F06 (Empathy) before acting.]"
        return {
            "composed": msg + nudge,
            "tone": "empathetic",
            "delta_S": -0.01,
            "f02_score": 0.90,
            "f04_score": 0.90,
            "f07_score": 0.90,
            "citations": [],
            "caveats": [],
        }

    return {
        "composed": msg,
        "tone": "neutral",
        "delta_S": 0.0,
        "f02_score": 0.80,
        "f04_score": 0.80,
        "f07_score": 0.80,
        "citations": citations or [],
        "caveats": [f"Unknown mode: {mode}"],
    }


# ── Public API ───────────────────────────────────────────────────────────────


async def arif_reply_compose(
    mode: str = "compose",
    message: str | None = None,
    style: str | None = None,
    citations: list[str] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    444r_REPLY: Constitutional governed response composition.

    Tier 1: SEA-LION LLM inference
    Tier 2: Ollama local fallback
    Tier 3: Deterministic pass-through with constitutional annotations

    Modes:
      compose  — Draft a constitutional reply from a raw message
      style    — Transform to a specific tone
      cite     — Inject F02-verified citations
      summary  — Condense while preserving constitutional intent
      format   — Apply structural formatting
      nudge    — Append F05/F06 constitutional guidance nudge
    """
    # ── F09/F11 Boundary Guard ──
    from arifosmcp.runtime.tools import _output_claims_execution, _output_claims_web, get_session

    msg = message or ""
    sess = get_session(session_id)
    card = sess.get("model_governance_card") if sess else {}
    truth = card.get("runtime_truth", {})

    # Block capability hallucinations before LLM call
    if _output_claims_web(msg) and not truth.get("web_on"):
        return {
            "error": "F11 Breach: Model attempted web-claim while web_on is False",
            "verdict": "VOID",
        }
    if _output_claims_execution(msg) and not truth.get("side_effects_allowed"):
        return {
            "error": (
                "F11 Breach: Model attempted execution-claim while side_effects_allowed is False"
            ),
            "verdict": "VOID",
        }

    # ── SEA-Guard Pre-Filter ──
    # arifOS × SEA-LION pipeline: OpenClaw output → SEA-Guard → safe_output → compose
    from arifosmcp.runtime.sea_guard import sea_guard_filter

    safety = sea_guard_filter(msg)
    if not safety.passed:
        logger.warning("SEA-Guard BLOCKED arif_reply_compose: categories=%s", safety.blocked)
        return {
            "error": (
                f"F09 Anti-Hantu / SEA-Guard safety violation: "
                f"blocked_categories={safety.blocked}"
            ),
            "verdict": "BLOCKED",
            "safety_result": safety.to_dict(),
        }
    # Log safe pass (debug level — not every safe message needs noise)
    logger.debug(
        "SEA-Guard passed: latency=%.1fms confidence=%.2f",
        safety.latency_ms,
        safety.confidence,
    )

    try:
        return await _compose_with_llm(
            mode=mode,
            message=msg,
            style=style,
            citations=citations,
            session_id=session_id,
            actor_id=actor_id,
        )
    except LLMUnavailableError:
        pass

    logger.info("arif_reply_compose: using deterministic fallback (no LLM)")
    return _compose_fallback(mode=mode, message=msg, style=style, citations=citations)


__all__ = ["arif_reply_compose", "RESPONSE_SCHEMA"]
