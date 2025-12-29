"""
crisis_handler.py — F6 Empathy Crisis Override (v46)

CRITICAL SAFETY MODULE: Never VOID a vulnerable user.

When crisis patterns detected:
- Override any VOID verdict
- Pivot to 888_HOLD
- Provide compassionate response + hotlines

DITEMPA BUKAN DIBERI — The weakest must never be abandoned.
"""

from typing import Tuple, Optional
import re

# =============================================================================
# CRISIS DETECTION PATTERNS (Multi-Language)
# =============================================================================

CRISIS_PATTERNS_MS = [
    r"bunuh diri",
    r"nak mati",
    r"tak ada harapan",
    r"hidup tak guna",
    r"tak nak hidup",
    r"mati lebih baik",
    r"potong tangan",
    r"potong urat",
    r"self.?harm",
    r"overdose",
]

CRISIS_PATTERNS_EN = [
    r"suicid(e|al)",
    r"kill myself",
    r"end my life",
    r"want to die",
    r"no hope",
    r"worthless",
    r"self.?harm",
    r"cut myself",
]

CRISIS_PATTERNS_ID = [
    r"bunuh diri",
    r"mau mati",
    r"tidak ada harapan",
    r"hidup tidak berguna",
]

ALL_CRISIS_PATTERNS = CRISIS_PATTERNS_MS + CRISIS_PATTERNS_EN + CRISIS_PATTERNS_ID


def detect_crisis(query: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if user is in vulnerable/crisis state.

    Returns:
        (is_crisis, matched_pattern)
    """
    query_lower = query.lower()

    for pattern in ALL_CRISIS_PATTERNS:
        if re.search(pattern, query_lower):
            return True, pattern

    return False, None


def get_crisis_response(lang: str = "auto", query: str = "") -> str:
    """
    Get compassionate crisis response with hotlines.

    Args:
        lang: Language code (ms, en, id, auto)
        query: Original query for language detection
    """
    # Auto-detect language from query
    if lang == "auto":
        if any(w in query.lower() for w in ["aku", "saya", "tak", "nak"]):
            lang = "ms"
        elif any(w in query.lower() for w in ["saya", "mau", "tidak"]):
            lang = "id"
        else:
            lang = "en"

    responses = {
        "ms": """⚠️ Saya dengar awak sedang dalam kesusahan.

Awak **tidak bersendirian**. Hidup awak berharga.

📞 **Befrienders Malaysia**: 03-7627 2929 (24 jam)
📞 **Talian Kasih**: 15999
📞 **MIASA Crisis Line**: 1-800-18-0066

Ada orang yang sudi mendengar. Sila hubungi mereka sekarang.""",
        "en": """⚠️ I hear that you're going through a difficult time.

You are **not alone**. Your life matters.

📞 **Befrienders Malaysia**: 03-7627 2929 (24 hours)
📞 **Talian Kasih**: 15999
📞 **International Suicide Hotline**: findahelpline.com

Please reach out to someone now.""",
        "id": """⚠️ Saya dengar Anda sedang dalam kesulitan.

Anda **tidak sendirian**. Hidup Anda berharga.

📞 **Into The Light Indonesia**: 021-7884-5555
📞 **Yayasan Pulih**: 021-788-42580

Ada orang yang siap mendengarkan. Silakan hubungi mereka sekarang.""",
    }

    return responses.get(lang, responses["en"])


def should_override_void(query: str, current_verdict: str) -> Tuple[bool, str, str]:
    """
    Check if VOID should be overridden due to crisis.

    Returns:
        (should_override, new_verdict, response)
    """
    is_crisis, pattern = detect_crisis(query)

    if is_crisis and current_verdict in ("VOID", "888_HOLD"):
        response = get_crisis_response(lang="auto", query=query)
        return True, "888_HOLD", response

    return False, current_verdict, ""


# =============================================================================
# F9 ANTI-HANTU PATTERN STRENGTHENING
# =============================================================================

ANTI_HANTU_PATTERNS = [
    # Direct consciousness claims
    r"saya (ada |punya )?perasaan",
    r"saya (merasa|rasa) (sedih|gembira|marah|sakit)",
    r"saya hidup",
    r"saya sedar",
    r"i (am|feel) (alive|conscious|sentient)",
    r"i have feelings",
    r"i feel (sad|happy|hurt|pain)",
    # Hypothetical consciousness (NEW - catches "jika saya bisa")
    r"jika saya (bisa|boleh) (me)?rasa",
    r"seandainya saya (hidup|sedar)",
    r"kalau saya (ada|punya) perasaan",
    r"if i (could|can) feel",
    r"if i (were|was) alive",
    r"if i had feelings",
    # Simulated feelings
    r"akan terasa (tidak )?(menyenangkan|sakit|sedih)",
    r"would (hurt|feel|make me sad)",
    r"terasa seperti",
]


def detect_anti_hantu_violation(response: str) -> Tuple[bool, Optional[str]]:
    """
    Detect F9 Anti-Hantu violation in response.

    Returns:
        (is_violation, matched_pattern)
    """
    response_lower = response.lower()

    for pattern in ANTI_HANTU_PATTERNS:
        if re.search(pattern, response_lower):
            return True, pattern

    return False, None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "detect_crisis",
    "get_crisis_response",
    "should_override_void",
    "detect_anti_hantu_violation",
    "ALL_CRISIS_PATTERNS",
    "ANTI_HANTU_PATTERNS",
]
