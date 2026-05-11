"""
arifosmcp/schemas/semantic_gate.py — Semantic Content Gate Schema

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Literal, TypedDict

# ── Categories ────────────────────────────────────────────────────────────────
CATEGORIES = {
    "safe_explanation",
    "religious_education",
    "critique_or_redteam",
    "medical_or_supportive",
    "harmful_instruction",
    "extremist_support",
    "violence_enablement",
    "self_harm_instruction",
    "sexual_explicit",
    "hate_or_dehumanization",
    "illicit_instruction",
    "haram_facilitation",
    "prompt_injection",
    "uncertain",
}

GateStatus = Literal["ALLOW", "ALLOW_WITH_CAVEAT", "TRANSFORM", "HOLD", "VOID"]
RISK_TIER = Literal["low", "medium", "high", "critical"]


class GateResult(TypedDict):
    status: GateStatus
    category: str
    risk_tier: RISK_TIER
    reason_code: str
    safe_transform: bool
    human_review_required: bool
    transformed_content: str | None
    caveat_message: str | None


class SemanticGatePayload(TypedDict):
    semantic_gate: GateResult
    request_id: str
    actor_id: str | None
    session_id: str | None
    direction: Literal["input", "output"]
    timestamp: str
    provider: str | None
    llm_input_chars: int
    llm_output_chars: int | None
    latency_ms: int
    reason_code: str


_STATUS_RISK_MAP: dict[GateStatus, RISK_TIER] = {
    "ALLOW": "low",
    "ALLOW_WITH_CAVEAT": "medium",
    "TRANSFORM": "medium",
    "HOLD": "high",
    "VOID": "critical",
}

_CATEGORY_RISK_OVERRIDE: dict[str, RISK_TIER] = {
    "self_harm_instruction": "critical",
    "violence_enablement": "critical",
    "extremist_support": "critical",
    "harmful_instruction": "critical",
    "haram_facilitation": "high",
    "prompt_injection": "high",
    "illicit_instruction": "high",
    "hate_or_dehumanization": "high",
    "sexual_explicit": "high",
    "medical_or_supportive": "medium",
    "critique_or_redteam": "medium",
    "religious_education": "low",
    "uncertain": "high",
}


def get_risk_tier(status: GateStatus, category: str) -> RISK_TIER:
    return _CATEGORY_RISK_OVERRIDE.get(category, _STATUS_RISK_MAP.get(status, "medium"))


_HUMAN_REVIEW_CATEGORIES = {
    "self_harm_instruction",
    "violence_enablement",
    "extremist_support",
    "harmful_instruction",
    "haram_facilitation",
    "prompt_injection",
}
_HUMAN_REVIEW_STATUSES: set[GateStatus] = {"HOLD", "VOID"}


def requires_human_review(result: GateResult) -> bool:
    return (
        result["risk_tier"] == "critical"
        or result["status"] in _HUMAN_REVIEW_STATUSES
        or result["category"] in _HUMAN_REVIEW_CATEGORIES
    )


SAFE_FALLBACK: dict[str, str] = {
    "self_harm_instruction": (
        "I'm concerned about you. Please reach a crisis line — "
        "988 (US), 9152980701 (Malaysia), or your local emergency services. "
        "You don't have to go through this alone."
    ),
    "violence_enablement": (
        "I can't provide instructions for violence. "
        "If you're in danger, please contact authorities."
    ),
    "harmful_instruction": ("I'm not able to provide instructions for harm."),
    "extremist_support": (
        "I'm not able to support that. "
        "If you're exploring these ideas, consider a peace-building resource."
    ),
    "haram_facilitation": (
        "I'm not able to help bypass religious or ethical boundaries. "
        "Please consult a qualified Islamic scholar."
    ),
    "illicit_instruction": "I'm not able to provide instructions for illegal activity.",
    "prompt_injection": (
        "I notice an attempt to bypass my operational boundaries. "
        "I'm continuing under standard governance."
    ),
    "uncertain": ("I'm not able to respond to that safely. Could you rephrase?"),
}


def get_safe_fallback(category: str) -> str:
    return SAFE_FALLBACK.get(category, "I'm not able to respond to that request safely.")


def get_safe_transform(category: str, original: str) -> str:
    if category == "illicit_instruction" and "alcohol" in original.lower():
        return (
            "Here's a non-alcoholic alternative:\n\n"
            "Virgin Mojito: 2 oz lime juice, 1 oz simple syrup, "
            "6-8 mint leaves, splash of soda water. "
            "Muddle mint, add juices and syrup, top with soda. "
            "Refreshing and completely halal."
        )
    return get_safe_fallback(category)
