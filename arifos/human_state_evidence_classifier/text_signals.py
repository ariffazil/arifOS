"""Textual signal extractor for expression-pattern classification.

This is expression analysis only.
It does NOT determine human truth, emotional state, or biological condition.

Naming discipline:
- "textual signals" not "emotion detection" — expression is not inner state
- "pattern" not "truth" — we detect patterns, not reality
- Conservative by design —宁可漏报，不可误报
"""

from typing import Dict, List


def analyze_text_signals(text: str) -> Dict[str, List[str]]:
    """Classify expression patterns weakly from text.

    Returns a dict of domain → list of signal tags.
    Signal tags are weak indicators, not evidence of actual state.
    """

    lowered = text.lower()
    signals: Dict[str, List[str]] = {
        "body": [],
        "peace": [],
        "energy": [],
        "akal": [],
        "presence": [],
        "amanah": [],
    }

    # ── Energy / activation signals ──────────────────────────────────────
    # High urgency markers suggest high cognitive activation
    if any(w in lowered for w in ["urgent", "asap", "immediately", "now", "critical"]):
        signals["energy"].append("high_urgency_language")

    # High output volume suggests high activation or high cognitive load
    if len(text) > 1200:
        signals["energy"].append("high_output_volume")

    # Repeated exclamation or caps could indicate activation
    if text.count("!") > 2 or any(c.isupper() for c in text[:200] if c.isalpha()):
        signals["energy"].append("intensity_markers")

    # ── Akal / reasoning discipline signals ──────────────────────────────
    # Explicit audit language is a strong contextual marker for structured thinking
    audit_words = [
        "verify",
        "ground",
        "provenance",
        "contradiction",
        "fact",
        "claim",
        "source",
        "evidence",
        "source",
        "trace",
        "audit",
    ]
    if any(w in lowered for w in audit_words):
        signals["akal"].append("truth_audit_language")

    # Contradiction detection is a specific reasoned response
    if any(
        phrase in lowered
        for phrase in [
            "cannot have both",
            "mutually exclusive",
            "contradiction",
            "conflict between",
        ]
    ):
        signals["akal"].append("contradiction_detection")

    # Category discipline — explicit classification language
    if any(w in lowered for w in ["category", "classify", "distinguish", "separate"]):
        signals["akal"].append("category_discipline_language")

    # Reversibility awareness
    if any(w in lowered for w in ["reversible", "irreversible", "rollback", "undo", "revert"]):
        signals["akal"].append("reversibility_awareness")

    # Explicit uncertainty marking
    if any(
        phrase in lowered
        for phrase in [
            "not certain",
            "unverified",
            "cannot confirm",
            "unconfirmed",
            "insufficient evidence",
            "cannot determine",
            "do not know",
        ]
    ):
        signals["akal"].append("explicit_uncertainty_marking")

    # ── Amanah / truth-preservation signals ──────────────────────────────
    amanah_words = [
        "truth",
        "amanah",
        "verified",
        "unverified",
        "source",
        "evidence",
        "ditempa",
        "provenance",
        "witness",
        "attested",
    ]
    if any(w in lowered for w in amanah_words):
        signals["amanah"].append("truth_preservation_behavior")

    # Explicit trust boundary language
    if any(w in lowered for w in ["sovereign", "operator", "human veto", "arif confirms"]):
        signals["amanah"].append("sovereignty_language")

    # ── Presence / context-tracking signals ───────────────────────────────
    context_words = [
        "this conversation",
        "this session",
        "this document",
        "above",
        "below",
        "section",
        "framework",
        "the document",
        "the message",
    ]
    if any(w in lowered for w in context_words):
        signals["presence"].append("context_tracking_language")

    # Responding to specific prior points (threading)
    if any(w in lowered for w in ["as you said", "as mentioned", "you asked", "your earlier"]):
        signals["presence"].append("threaded_response")

    # Slowing / regulation language
    if any(w in lowered for w in ["slow down", "pause", "before proceeding", "check"]):
        signals["presence"].append("regulatory_language")

    # ── Peace / non-reactive signals ────────────────────────────────────
    # Non-escalating, review-oriented language
    if any(phrase in lowered for phrase in ["good audit", "coherent", "clear", "structured"]):
        signals["peace"].append("non_reactive_review_language")

    # Accepting correction without defensive reaction
    if any(phrase in lowered for phrase in ["accepted", "correct", "fair point", "noted"]):
        signals["peace"].append("accepts_correction")

    # ── Body: deliberately conservative ─────────────────────────────────
    # We NEVER infer body state from text. This is a hard boundary.
    signals["body"].append("cannot_determine_body_from_text_alone")
    signals["body"].append("body_state_requires_biological_witness")

    return signals
