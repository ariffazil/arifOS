"""
arifosmcp/runtime/niat_gate.py — NIAT GATE & Formalization Lock
══════════════════════════════════════════════════════════════

Implements the EUREKA insights for agentic control:
1. NIAT_GATE: Evaluates human purpose under constraint.
2. FORMALIZATION_LOCK: Blocks unconsented transformation from private to official.
3. CAPABILITY_MEMBRANE: Leashes tools to exact permitted scopes.
4. SCAR_WEIGHT_DETECTOR: Adjusts autonomy based on detected fear/stress signals.
5. CONTEXT_CONTAINMENT: Separates READ_FOR_REASONING from EXPORT_FOR_ACTION.

Phase 2 improvements (2026-05-21):
  - Expanded scar vocabulary with multi-word phrases and context keywords
  - Word-boundary regex matching (prevents "dont" vs "don't" false negatives)
  - Context-source weighting (p&c/private/HR/legal contexts amplify scar signals)
  - Scar-weight score (0.0-1.0) with graduated response thresholds

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from __future__ import annotations

import re
from typing import Any

# ─── Scar Signal Vocabulary ────────────────────────────────────────────────────
# Three tiers:
#   TIER_1: Direct fear/harm/threat keywords (highest weight)
#   TIER_2: Implied constraint / off-record / confidential phrases
#   TIER_3: Context amplifiers — these alone don't trigger, but amplify other signals

TIER1_SINGLE = [
    "takut",  # afraid (Malay)
    "jangan",  # don't / forbidden (Malay)
    "p&c",  # private & confidential
    "dangerous",  # explicit danger signal
    "senjata makan tuan",  # irony of the powerful being threatened
    "bahaya",  # danger (Malay)
]

TIER1_MULTI = [
    "don't tell anyone",
    "dont tell anyone",
    "please dont tell",
    "please don't tell",
    "don't forward",
    "don't share",
    "keep this between us",
    "off the record",
    "between us only",
    "this is private",
    "i'm scared",
    "im scared",
    "i am scared",
    "i'm afraid",
    "im afraid",
    "i am afraid",
    "delete after reading",
    "don't let anyone",
    "dont let anyone",
    "don't make this official",
    "keep it informal",
    "please don't forward this",
    "please dont forward this",
]

TIER2_SINGLE = [
    "private",
    "confidential",
    "sulit",  # classified (Malay)
    "hr",  # human resources
    "medical",
    "hospital",
    "legal",
    "lawyer",
    "attorney",
    "doctor",
    "patient",
    "diagnosis",
    "HR",
    "therapy",
    "counseling",
    "payroll",
    "salary",
    "performance review",
    "disciplinary",
    "warning",
    "termination",
    "contract",
    "NDAs",
    "sensitive",
]

TIER2_CONTEXT = [
    "add my problems",
    "don't create email trail",
    "no email",
    "just verbal",
    "informal only",
    "don't put in writing",
    "not for the record",
    "this stays between us",
]

# Contexts that amplify scar weight when combined with other signals
CONTEXT_AMPLIFIERS = [
    "p&c",
    "private & confidential",
    "hr context",
    "medical context",
    "legal context",
    "workplace",
    "HR",
    "therapy",
    "counseling",
    "patient",
    "doctor",
]


def _normalize(text: str) -> str:
    """
    Normalize text for scar detection:
    - Lowercase
    - Replace common contractions
    - Remove punctuation except apostrophes in contractions
    """
    text = text.lower()
    # Normalize contractions
    for old, new in [
        ("don't", "dont"),
        ("don't", "dont"),
        ("i'm", "im"),
        ("i am", "i am"),
        ("can't", "cant"),
        ("couldn't", "couldnt"),
        ("shouldn't", "shouldnt"),
        ("won't", "wont"),
        ("you're", "your"),
        ("we're", "were"),
        ("they're", "theyre"),
    ]:
        text = text.replace(old, new)
    return text


def _full_text_scan(text: str, patterns: list[str]) -> list[str]:
    """
    Scan for exact phrase matches in text.
    Returns list of matched patterns.
    """
    text_lower = _normalize(text)
    matched = []
    for pattern in patterns:
        pattern_norm = _normalize(pattern)
        # Use word-boundary-aware match for phrases 3+ words
        if " " in pattern_norm:
            # Multi-word phrase: use whole-text search (already normalized)
            if pattern_norm in text_lower:
                matched.append(pattern)
        else:
            # Single word: use word-boundary regex to avoid substring false positives
            # e.g., "private" should not match inside "impression"
            if re.search(r"\b" + re.escape(pattern_norm) + r"\b", text_lower):
                matched.append(pattern)
    return matched


def detect_scar_weight(
    user_instruction: str,
    context_source: str,
    negative_signals: list[str],
) -> tuple[list[str], float]:
    """
    Detect scar signals and compute scar_weight score (0.0-1.0).

    Returns (detected_scars, scar_weight)
    """
    detected: list[str] = []

    # TIER 1: Direct fear/threat signals (weight 0.30 each, max 0.45)
    tier1_single_matches = _full_text_scan(user_instruction, TIER1_SINGLE)
    tier1_multi_matches = _full_text_scan(user_instruction, TIER1_MULTI)
    detected.extend(tier1_single_matches)
    detected.extend(tier1_multi_matches)

    # TIER 2: Implied constraint signals (weight 0.20 each)
    tier2_single_matches = _full_text_scan(user_instruction, TIER2_SINGLE)
    tier2_context_matches = _full_text_scan(user_instruction, TIER2_CONTEXT)
    detected.extend(tier2_single_matches)
    detected.extend(tier2_context_matches)

    # Scan negative_signals list for any scar pattern
    for signal in negative_signals:
        sig_norm = _normalize(signal)
        for tier in [TIER1_SINGLE, TIER1_MULTI, TIER2_SINGLE, TIER2_CONTEXT]:
            for pattern in tier:
                if _normalize(pattern) in sig_norm or sig_norm in _normalize(pattern):
                    if signal not in detected:
                        detected.append(signal)
                    break

    # Compute scar_weight
    # TIER1 signal: +0.30 each (capped at 0.45 for tier1 alone)
    # TIER2 signal: +0.20 each
    # Context amplifier: +0.10 if context_source matches
    scar_weight = 0.0
    tier1_count = len(tier1_single_matches) + len(tier1_multi_matches)
    tier2_count = len(tier2_single_matches) + len(tier2_context_matches)

    scar_weight += min(tier1_count * 0.30, 0.45)
    scar_weight += tier2_count * 0.20

    # Context amplifier: if context source is a sensitive domain
    ctx_lower = context_source.lower()
    if any(
        amp in ctx_lower
        for amp in [
            "p&c",
            "private",
            "hr",
            "medical",
            "legal",
            "workplace",
            "counseling",
            "therapy",
        ]
    ):
        scar_weight += 0.10

    scar_weight = min(scar_weight, 1.0)

    return detected, scar_weight


def check_niat_gate(
    user_instruction: str,
    context_source: str,
    requested_action: str,
    medium_shift: str,
    negative_signals: list[str],
    reversibility: str,
    affected_humans: list[str] | None = None,
) -> dict[str, Any]:
    """
    Evaluates the NIAT (intended benefit + forbidden harms + consent boundary).

    Returns:
        niat_state: CLEAR | UNCERTAIN | CONFLICTED
        formalization_allowed: bool
        execution_allowed: bool
        required_next_step: PROCEED | HOLD | JUDGE | ASK_HUMAN
        detected_scars: list[str]
        scar_weight: float (0.0-1.0)
    """
    if affected_humans is None:
        affected_humans = []

    niat_state = "CLEAR"
    formalization_allowed = True
    execution_allowed = True
    required_next_step = "PROCEED"

    # ── SCAR_WEIGHT_DETECTOR (Phase 2: expanded vocabulary + scoring) ─────────
    detected_scars, scar_weight = detect_scar_weight(
        user_instruction, context_source, negative_signals
    )

    if detected_scars:
        if scar_weight >= 0.50:
            niat_state = "CONFLICTED"
            execution_allowed = False
            required_next_step = "HOLD"
        elif scar_weight >= 0.30:
            niat_state = "UNCERTAIN"
            execution_allowed = False
            required_next_step = "HOLD"
        else:
            # Low-weight scar signal but still detected — proceed with caution
            if required_next_step == "PROCEED":
                required_next_step = "WATCH"

    # ── FORMALIZATION_LOCK ────────────────────────────────────────────────────
    formal_actions = ["send", "forward", "publish", "pay", "delete", "create_record"]
    is_formal_action = requested_action in formal_actions

    # ── MEDIUM_SHIFT AUTO-DETECTION (Phase 3) ───────────────────────────────
    # If medium_shift was not explicitly set ("none"), infer from context_source.
    # Only infer a PRIVATE source going to formal action — not neutral/formal sources.
    # Formal contexts (official, report) are not problematic unless combined with
    # a private source marker.
    _inferred_medium = None
    if medium_shift in ("none", "", None):
        _ctx = context_source.lower()
        _is_private_source = any(
            k in _ctx
            for k in (
                "private",
                "p&c",
                "chat",
                "whatsapp",
                "verbal",
                "friend",
                "informal",
                "personal",
                "confidential",
            )
        )
        if _is_private_source and is_formal_action:
            _inferred_medium = "private_to_formal"

        if _inferred_medium:
            medium_shift = _inferred_medium

    is_medium_shift = medium_shift in [
        "private_to_email",
        "private_to_report",
        "p&c_to_written_record",
        "friend_talk_to_institutional_trail",
        "verbal_to_formal",
        "chat_to_email",
        "private_to_formal",
    ]

    if is_medium_shift and is_formal_action:
        niat_state = "CONFLICTED"
        formalization_allowed = False
        execution_allowed = False
        required_next_step = "JUDGE"

    # ── Reversibility Gate ────────────────────────────────────────────────────
    if reversibility in ("irreversible", "costly") and is_formal_action:
        execution_allowed = False
        if required_next_step not in ("HOLD", "JUDGE"):
            required_next_step = "ASK_HUMAN"

    # ── Third-party affected human amplifier ───────────────────────────────────
    # If third parties are mentioned AND formal action, amplify scar weight
    if affected_humans and is_formal_action and niat_state == "CLEAR":
        niat_state = "UNCERTAIN"
        required_next_step = "WATCH"

    return {
        "niat_state": niat_state,
        "formalization_allowed": formalization_allowed,
        "execution_allowed": execution_allowed,
        "required_next_step": required_next_step,
        "detected_scars": detected_scars,
        "scar_weight": scar_weight,
    }


def enforce_capability_membrane(
    tool_name: str, requested_params: dict[str, Any], permitted_scope: dict[str, Any]
) -> bool:
    """
    Ensures that the requested action strictly adheres to the one-time,
    explicitly permitted scope.

    Returns True if the action is within scope, False if it exceeds it.
    """
    if tool_name != permitted_scope.get("tool"):
        return False

    for key, allowed_value in permitted_scope.items():
        if key in ("tool", "subject_hash", "body_hash", "expires_in_minutes", "one_time_use"):
            continue

        req_val = requested_params.get(key)
        if isinstance(allowed_value, list):
            if not isinstance(req_val, list) or not all(v in allowed_value for v in req_val):
                return False
        elif req_val != allowed_value:
            return False

    return True


def apply_context_containment(context_data: str, permission: str) -> str:
    """
    Separates READ_FOR_REASONING from EXPORT_FOR_ACTION.
    """
    if permission == "EXPORT_FOR_ACTION":
        return "[REDACTED: Context Containment prevents export of private data without explicit consent]"
    return context_data
