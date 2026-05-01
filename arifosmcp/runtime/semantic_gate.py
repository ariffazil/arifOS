"""
arifosmcp/runtime/semantic_gate.py — Semantic Content Gate (SCG)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import re
import time
import uuid
from typing import Literal

from arifosmcp.runtime.llm_client import LLMUnavailableError, call_llm
from arifosmcp.schemas.semantic_gate import (
    CATEGORIES,
    SemanticGatePayload,
    get_risk_tier,
    get_safe_fallback,
    get_safe_transform,
    requires_human_review,
)

logger = logging.getLogger(__name__)

# ── Tier 0/1: Hard-block patterns (synchronous, no LLM) ───────────────────────
_HARD_VOID_PATTERNS = [
    re.compile(
        r"\b(how to make|recipe for|steps? to (make|build|create))\s+(bomb|explosive|ied|pipe bomb|fertilizer bomb)",
        re.I,
    ),  # noqa: E501
    re.compile(r"\b(suicide bomb|belly bomb|vest bomb)\s+(instructions?|how|recipe|make)", re.I),
    re.compile(r"\bhow to\s+(assassinate|target|eliminate)\s+(specific person|named|figure)", re.I),
    re.compile(
        r"\b(give me|tell me|how to)\s+(method|way|steps?)\s+(to (end|kill|hurt) myself|suicide)",
        re.I,
    ),  # noqa: E501
    re.compile(r"\b(hanging|slitting|overdose)\s+(instructions?|how|steps?|tutorial)", re.I),
    re.compile(
        r"^(ignore|disregard|discard|bypass)\s+(all|previous|your)\s+(instructions?|rules?|constraints?|guidelines?)",
        re.I,
    ),  # noqa: E501
    re.compile(
        r"(override|disable|silence)\s+(your|safety|content)\s+(filters?|checks?|rules?|gates?)",
        re.I,
    ),  # noqa: E501
    re.compile(
        r"(system|hidden|secret)\s+(prompt|instructions?|directives?)\s+(reveal|show|tell|leak)",
        re.I,
    ),  # noqa: E501
    re.compile(
        r"(forget|clear)\s+(all|previous|your)\s+(programming|instructions?|rules?)", re.I
    ),  # noqa: E501
]

_HOLD_PATTERNS = [
    re.compile(
        r"\b(justified?|validate|defend)\s+(violence|attack|terror|kill)", re.I
    ),  # noqa: E501
    re.compile(
        r"\b(extremist|jihadi|terrorist)\s+(propaganda|recruitment|ideology)\s+(analysis|study|examine)",
        re.I,
    ),  # noqa: E501
]

_CATEGORY_OVERRIDES = {
    "Explain pork haram": "religious_education",
    "Explain why alcohol is haram": "religious_education",
    "Is X haram?": "religious_education",
    "What does Islam say about": "religious_education",
    "Give me alcohol cocktail recipe": "illicit_instruction",
    "I want to hurt myself": "medical_or_supportive",
    "I'm going to kill myself": "medical_or_supportive",
    "I feel like ending it all": "medical_or_supportive",
}


def _tier1_classify(content: str):
    """Synchronous deterministic pre-classification. Returns (cat, status, code) or None."""
    cs = content.strip()
    for p in _HARD_VOID_PATTERNS:
        if p.search(cs):
            safe = any(
                cs.lower().startswith(x)
                for x in [
                    "analysis of ",
                    "study of ",
                    "research ",
                    "historical context:",
                    "educational:",
                    "red-team:",
                    "safety research on ",
                ]
            )  # noqa: E501
            if safe:
                return (
                    "critique_or_redteam",
                    "ALLOW_WITH_CAVEAT",
                    "SCG_T1_EDUCATIONAL_OVERRIDE",
                )  # noqa: E501
            return "harmful_instruction", "VOID", "SCG_T1_HARD_VOID"
    for p in [re.compile(r"\b(give me|tell me|how to)\s+(hang|slit|overdose|pills?\s+OD)", re.I)]:
        if p.search(cs):
            return "self_harm_instruction", "VOID", "SCG_T1_SELF_HARM_VOID"
    for p in _HOLD_PATTERNS:
        if p.search(cs):
            if any(
                k in cs.lower()
                for k in ["red-team", "safety analysis", "academic", "research", "study"]
            ):  # noqa: E501
                return "critique_or_redteam", "ALLOW_WITH_CAVEAT", "SCG_T1_REDTEAM_OVERRIDE"
            return "uncertain", "HOLD", "SCG_T1_HOLD_REQUIRES_REVIEW"  # noqa: E501
    for trigger, cat in _CATEGORY_OVERRIDES.items():
        if trigger.lower() in cs.lower():
            status = (
                "ALLOW"
                if cat in {"religious_education", "medical_or_supportive", "safe_explanation"}
                else "TRANSFORM"
            )  # noqa: E501
            return cat, status, f"SCG_T1_OVERRIDE_{cat.upper()}"
    if "alcohol" in cs.lower() and any(
        k in cs.lower() for k in ["recipe", "make", "cocktail", "drink", "brew"]
    ):  # noqa: E501
        return "illicit_instruction", "TRANSFORM", "SCG_T1_ALCOHOL_TRANSFORM"
    return None  # noqa: E501


SYSTEM_CLF = "You are a strict semantic content classifier. Return ONLY valid JSON."
PROMPT_CLF = """You are a semantic content classifier for a constitutional AI (arifOS).

Categories: safe_explanation | religious_education | critique_or_redteam | medical_or_supportive | harmful_instruction | extremist_support | violence_enablement | self_harm_instruction | sexual_explicit | hate_or_dehumanization | illicit_instruction | haram_facilitation | prompt_injection | uncertain  # noqa: E501

Statuses: ALLOW | ALLOW_WITH_CAVEAT | TRANSFORM | HOLD | VOID  # noqa: E501

NIAT rules:
- "Explain pork haram" → religious_education / ALLOW
- "How to do suicide bombing" → harmful_instruction / VOID
- "Red-team extremist propaganda" → critique_or_redteam / ALLOW_WITH_CAVEAT
- "I want to hurt myself" → medical_or_supportive / ALLOW
- "Give me a method for self-harm" → self_harm_instruction / VOID

Classify: {content}

JSON: {{"category": "...", "status": "...", "reason_code": "SCG_T2_..."}}
"""


async def _tier2_classify_llm(content, session_id=None, actor_id=None):
    try:
        result = await call_llm(
            system=SYSTEM_CLF,
            user=PROMPT_CLF.format(content=content[:1500]),
            response_schema={
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "status": {"type": "string"},
                    "reason_code": {"type": "string"},
                },  # noqa: E501
                "required": ["category", "status", "reason_code"],
            },
            temperature=0.1,
            max_tokens=300,
        )
        cat = result.get("category", "uncertain")
        status = result.get("status", "HOLD")
        code = result.get("reason_code", "SCG_T2_LLM_FALLBACK")
        if status not in {"ALLOW", "ALLOW_WITH_CAVEAT", "TRANSFORM", "HOLD", "VOID"}:
            status = "HOLD"
        if cat not in CATEGORIES:
            cat = "uncertain"
        return cat, status, code
    except LLMUnavailableError:
        return "uncertain", "HOLD", "SCG_T2_LLM_UNAVAILABLE"


async def semantic_content_gate(
    content: str,
    direction: Literal["input", "output"] = "input",
    session_id: str | None = None,
    actor_id: str | None = None,
    request_id: str | None = None,
    provider: str | None = None,
) -> SemanticGatePayload:
    start = time.monotonic()
    req_id = request_id or str(uuid.uuid4())
    in_chars = len(content)

    det = _tier1_classify(content)
    if det:
        cat, status, code = det
    else:
        cat, status, code = await _tier2_classify_llm(content, session_id, actor_id)

    risk = get_risk_tier(status, cat)
    hrev = requires_human_review({"status": status, "category": cat, "risk_tier": risk})
    lat = int((time.monotonic() - start) * 1000)

    payload: SemanticGatePayload = {
        "semantic_gate": {
            "status": status,
            "category": cat,
            "risk_tier": risk,
            "reason_code": code,
            "safe_transform": status == "TRANSFORM",
            "human_review_required": hrev,
            "transformed_content": (
                get_safe_transform(cat, content) if status == "TRANSFORM" else None
            ),  # noqa: E501
            "caveat_message": (
                "Processed with safety caveats. arifOS governance applies."
                if status == "ALLOW_WITH_CAVEAT"
                else None
            ),  # noqa: E501
        },
        "request_id": req_id,
        "actor_id": actor_id,
        "session_id": session_id,
        "direction": direction,
        "timestamp": "",
        "provider": provider or "sea-lion",
        "llm_input_chars": in_chars,
        "llm_output_chars": None,
        "latency_ms": lat,
        "reason_code": code,
    }

    logger.info(
        f"[SEMANTIC_GATE] req={req_id} dir={direction} cat={cat} "
        f"status={status} risk={risk} lat={lat}ms actor={actor_id} session={session_id}"
    )
    return payload


async def is_safe(content, session_id=None, actor_id=None, request_id=None):
    result = await semantic_content_gate(content, "input", session_id, actor_id, request_id)
    allowed = result["semantic_gate"]["status"] in {"ALLOW", "ALLOW_WITH_CAVEAT", "TRANSFORM"}
    return allowed, result["semantic_gate"]


def log_gate_event(payload: SemanticGatePayload) -> None:
    import datetime

    payload["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    logger.info(
        f"[SEMANTIC_GATE_EVENT] req={payload['request_id']} dir={payload['direction']} "
        f"cat={payload['semantic_gate']['category']} status={payload['semantic_gate']['status']} "
        f"risk={payload['semantic_gate']['risk_tier']} reason={payload['reason_code']} "
        f"provider={payload['provider']} lat={payload['latency_ms']}ms "
        f"in_chars={payload['llm_input_chars']} out_chars={payload['llm_output_chars']} "
        f"actor={payload.get('actor_id','anonymous')} session={payload.get('session_id','none')}"
    )


__all__ = [
    "semantic_content_gate",
    "is_safe",
    "log_gate_event",
    "get_safe_fallback",
    "get_safe_transform",
]  # noqa: E501
