"""
State Classifier — Deterministic Rule-Based Human State Engine
═══════════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Forged, Not Given.

Phase 1: Deterministic, rule-based, fully auditable.
Every classification carries evidence chain. No black boxes.

Physics: entropy reduction.
Human arrives ambiguous, contradictory, multi-self, linguistically lossy.
State vector exits structured: polyvagal state + SDT pressure + posture.

Pipeline:
  1. Extract linguistic features (markers, length, caps, repetition)
  2. Classify Polyvagal state (ventral / sympathetic / dorsal)
  3. Detect SDT pressure (autonomy / competence / relatedness)
  4. Resolve agent posture (explore / ground / hold_space / scaffold / acknowledge / offer_options)
  5. Attach evidence chain + governance flags

Constitutional floors:
  - F2 TRUTH: evidence chain on every classification
  - F4 CLARITY: output is lower-entropy than input
  - F6 EMPATHY: never pathologize, read signals not souls
  - F9 ANTIHANTU: no consciousness claims
  - F10 ONTOLOGY: no soul/feelings claims
  - F11 AUDIT: full trace
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from arifosmcp.rama.state_classifier_schemas import (
    AgentPosture,
    PolyvagalState,
    SDTPressure,
    SDTPressureVector,
    StateClassifierResult,
    StateVector,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# LINGUISTIC FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class LinguisticFeatures:
    """Extracted features from human message — raw signal before classification."""

    message: str
    message_length: int = 0
    word_count: int = 0
    has_caps_shouting: bool = False  # >50% uppercase = shouting
    caps_ratio: float = 0.0
    exclamation_count: int = 0
    question_count: int = 0
    ellipsis_count: int = 0  # "..." or "…" = hesitation/trailing
    repetition_detected: bool = False  # same message pasted multiple times
    short_response: bool = False  # <10 words = minimal engagement
    markers_found: dict[str, list[str]] | None = None  # category → matched markers

    def __post_init__(self) -> None:
        if self.markers_found is None:
            self.markers_found = {}


def extract_features(message: str, recent_messages: list[str] | None = None) -> LinguisticFeatures:
    """Extract linguistic features from human message.

    Deterministic. No ML. Pure regex + heuristics.
    """
    if not message:
        return LinguisticFeatures(message="")

    msg = message.strip()
    msg_lower = msg.lower()
    words = msg.split()
    word_count = len(words)
    char_count = len(msg)

    # Caps analysis
    alpha_chars = [c for c in msg if c.isalpha()]
    caps_ratio = (sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)) if alpha_chars else 0.0
    has_caps_shouting = caps_ratio > 0.5 and len(alpha_chars) > 5

    # Punctuation analysis
    exclamation_count = msg.count("!") + msg.count("！")
    question_count = msg.count("?") + msg.count("？")
    ellipsis_count = msg.count("...") + msg.count("…")

    # Short response detection
    short_response = word_count < 10

    # Repetition detection (same message appearing in recent history)
    repetition_detected = False
    if recent_messages:
        msg_normalized = msg_lower.strip()
        repetition_detected = sum(1 for m in recent_messages if m.strip().lower() == msg_normalized) >= 2

    return LinguisticFeatures(
        message=msg,
        message_length=char_count,
        word_count=word_count,
        has_caps_shouting=has_caps_shouting,
        caps_ratio=caps_ratio,
        exclamation_count=exclamation_count,
        question_count=question_count,
        ellipsis_count=ellipsis_count,
        repetition_detected=repetition_detected,
        short_response=short_response,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# POLYVAGAL STATE CLASSIFIERS
# ═══════════════════════════════════════════════════════════════════════════════

# ── Ventral vagal markers (safe & social) ─────────────────────────────────────
_VENTRAL_MARKERS: list[str] = [
    # Exploring, curious, playful
    "explore", "what if", "interesting", "curious", "let's think",
    "let me try", "wondering", "imagine", "suppose",
    # BM-English Penang
    "jom", "cuba", "tengok", "macam mana kalau",
    # Engaged, long-form
    "elaborate", "expand", "dig deeper", "go on",
    # Co-creating
    "together", "build", "create", "design", "forge",
    # Humor, play
    "haha", "lol", "lmao", "😂", "🤣", "nice",
    # Open exploration
    "interesting", "fascinating", "cool", "wow",
]

# ── Sympathetic markers (fight/flight) ────────────────────────────────────────
_SYMPATHETIC_MARKERS: list[str] = [
    # Frustration, anger
    "bangang", "bodoh", "stupid", "damn", "shit", "wtf",
    "geram", "marah", "angry", "furious", "pissed",
    # Urgency
    "now", "sekarang", "cepat", "quick", "asap", "hurry",
    "fix this", "fix it", "terus", "right now",
    # Defensive
    "don't tell me", "jangan", "stop", "enough", "sudah",
    # Exasperation
    "again?!?", "lagi?!?", "seriously?", "really?",
    "for fucks sake", "aiyo", "adoi",
    # ALL CAPS commands (handled via features, but marker too)
    "HELP", "FIX", "STOP", "NOW",
]

# ── Dorsal vagal markers (shutdown/freeze) ────────────────────────────────────
_DORSAL_MARKERS: list[str] = [
    # Withdrawal
    "entah", "tak tahu", "don't know", "whatever", "tak kisah",
    "doesn't matter", "tak penting", "skip",
    # Collapse
    "give up", "putus asa", "tak larat", "exhausted", "drained",
    "penat", "tak boleh", "can't anymore",
    # Numbness
    "kosong", "empty", "numb", "nothing", "tak rasa",
    "feel nothing", "blank",
    # Minimal engagement
    "ok", "k", "hmm", "mhm", "yeah", "ya",
    "fine", "baik", "noted",
    # Surrender without peace
    "buat je", "ikut kau", "whatever you want",
    "terserah", "up to you",
]


def classify_polyvagal(features: LinguisticFeatures) -> tuple[PolyvagalState, list[str], float]:
    """Classify Polyvagal state from linguistic features.

    Returns: (state, evidence_list, confidence)

    Deterministic rule-based. Priority: crisis > sympathetic > dorsal > ventral.
    """
    evidence: list[str] = []
    msg_lower = features.message.lower()

    # ── Sympathetic detection (fight/flight) ─────────────────────────
    sympathetic_score = 0
    sympathetic_markers: list[str] = []

    # ALL CAPS shouting
    if features.has_caps_shouting:
        sympathetic_score += 3
        sympathetic_markers.append(f"CAPS_SHOUTING({features.caps_ratio:.0%})")

    # Exclamation marks (high count = urgency/anger)
    if features.exclamation_count >= 3:
        sympathetic_score += 2
        sympathetic_markers.append(f"EXCLAMATION({features.exclamation_count})")

    # Keyword markers
    for marker in _SYMPATHETIC_MARKERS:
        if marker.lower() in msg_lower:
            sympathetic_score += 2
            sympathetic_markers.append(f"MARKER({marker})")

    # ── Dorsal vagal detection (shutdown) ────────────────────────────
    dorsal_score = 0
    dorsal_markers: list[str] = []

    # Repetition (paste loop = shutdown behavior)
    if features.repetition_detected:
        dorsal_score += 4
        dorsal_markers.append("REPETITION_LOOP")

    # Very short response (<5 words, not a question)
    if features.word_count <= 3 and features.question_count == 0:
        dorsal_score += 3
        dorsal_markers.append(f"MINIMAL_INPUT({features.word_count}w)")

    # Ellipsis without question (trailing off)
    if features.ellipsis_count > 0 and features.question_count == 0:
        dorsal_score += 1
        dorsal_markers.append("TRAILING_OFF")

    # Keyword markers
    for marker in _DORSAL_MARKERS:
        if marker.lower() in msg_lower:
            dorsal_score += 2
            dorsal_markers.append(f"MARKER({marker})")

    # ── Ventral vagal detection (safe & social) ──────────────────────
    ventral_score = 0
    ventral_markers: list[str] = []

    # Questions (curiosity signal)
    if features.question_count >= 1:
        ventral_score += 2
        ventral_markers.append(f"QUESTIONS({features.question_count})")

    # Long message (engagement signal)
    if features.word_count > 50:
        ventral_score += 2
        ventral_markers.append(f"LONG_MESSAGE({features.word_count}w)")
    elif features.word_count > 20:
        ventral_score += 1
        ventral_markers.append(f"MEDIUM_MESSAGE({features.word_count}w)")

    # Keyword markers
    for marker in _VENTRAL_MARKERS:
        if marker.lower() in msg_lower:
            ventral_score += 1
            ventral_markers.append(f"MARKER({marker})")

    # ── Resolution ───────────────────────────────────────────────────
    # Priority: sympathetic > dorsal > ventral (safety-first)
    # This is a constitutional choice: when in doubt, de-escalate.

    if sympathetic_score >= 3:
        evidence = sympathetic_markers
        confidence = min(0.5 + sympathetic_score * 0.08, 0.95)
        return PolyvagalState.SYMPATHETIC, evidence, confidence

    if dorsal_score >= 3:
        evidence = dorsal_markers
        confidence = min(0.5 + dorsal_score * 0.08, 0.95)
        return PolyvagalState.DORSAL, evidence, confidence

    # Default to ventral (safe baseline)
    evidence = ventral_markers if ventral_markers else ["DEFAULT_VENTRAL_NO_STRONG_SIGNALS"]
    confidence = min(0.4 + ventral_score * 0.1, 0.85) if ventral_markers else 0.4
    return PolyvagalState.VENTRAL, evidence, confidence


# ═══════════════════════════════════════════════════════════════════════════════
# SDT PRESSURE DETECTORS
# ═══════════════════════════════════════════════════════════════════════════════

# ── Autonomy markers ──────────────────────────────────────────────────────────
_AUTONOMY_DEFICIT_MARKERS: list[str] = [
    # Being told what to do
    "you should", "you must", "you need to", "kau kena",
    "do this", "buat ni", "just do it",
    # Resisting prescription
    "don't tell me", "jangan ajar", "i know",
    "let me decide", "biar aku", "my choice",
]

_AUTONOMY_GRANTED_MARKERS: list[str] = [
    # Sovereignty language
    "decide yourself", "your call", "kau decide",
    "ikut kau", "up to you", "terserah",
    "whatever you think", "you choose",
    # Exploration without prescription
    "explore", "try", "experiment", "cuba",
]

# ── Competence markers ────────────────────────────────────────────────────────
_COMPETENCE_DEFICIT_MARKERS: list[str] = [
    # Self-doubt
    "i can't", "tak boleh", "too hard", "susah",
    "i don't know how", "macam mana", "confused",
    "tak faham", "blur", "lost",
    # Failure language
    "failed", "gagal", "screwed up", "rosak",
    "messed up", "broken",
]

_COMPETENCE_SCAFFOLD_MARKERS: list[str] = [
    # Asking for help (not collapse — seeking scaffold)
    "how do i", "camne nak", "macam mana nak",
    "teach me", "show me", "ajar",
    "guide", "tunjuk",
]

# ── Relatedness markers ───────────────────────────────────────────────────────
_RELATEDNESS_DEFICIT_MARKERS: list[str] = [
    # Isolation
    "alone", "seorang", "sorang",
    "nobody understands", "siapa faham",
    "no one cares", "tak ada siapa kisah",
    # Disconnection
    "disconnected", "terasing", "forgotten",
    "dilupakan",
]

_RELATEDNESS_SEEKING_MARKERS: list[str] = [
    # Connection seeking
    "we", "kita", "together", "sama-sama",
    "flock", "bro", "sis", "friend",
    # Acknowledgment seeking
    "right?", "betul tak?", "agree?", "setuju?",
    "you know?", "kan?",
]


def detect_sdt_pressure(features: LinguisticFeatures) -> SDTPressureVector:
    """Detect SDT pressure from linguistic features.

    Returns pressure levels for autonomy, competence, relatedness.
    Each axis is independent — a human can have high pressure on all three.
    """
    msg_lower = features.message.lower()
    autonomy_evidence: list[str] = []
    competence_evidence: list[str] = []
    relatedness_evidence: list[str] = []

    # ── Autonomy ─────────────────────────────────────────────────────
    autonomy_deficit = 0
    autonomy_granted = 0

    for marker in _AUTONOMY_DEFICIT_MARKERS:
        if marker.lower() in msg_lower:
            autonomy_deficit += 2
            autonomy_evidence.append(f"DEFICIT({marker})")

    for marker in _AUTONOMY_GRANTED_MARKERS:
        if marker.lower() in msg_lower:
            autonomy_granted += 2
            autonomy_evidence.append(f"GRANTED({marker})")

    # Excessive exclamation = autonomy pressure (resisting being managed)
    if features.exclamation_count >= 3:
        autonomy_deficit += 1
        autonomy_evidence.append(f"PUSHBACK_EXCLAMATION({features.exclamation_count})")

    if autonomy_deficit >= 3:
        autonomy_level = SDTPressure.HIGH
    elif autonomy_deficit >= 1 or (autonomy_deficit > autonomy_granted):
        autonomy_level = SDTPressure.MEDIUM
    else:
        autonomy_level = SDTPressure.LOW

    # ── Competence ───────────────────────────────────────────────────
    competence_deficit = 0
    competence_scaffold = 0

    for marker in _COMPETENCE_DEFICIT_MARKERS:
        if marker.lower() in msg_lower:
            competence_deficit += 2
            competence_evidence.append(f"DEFICIT({marker})")

    for marker in _COMPETENCE_SCAFFOLD_MARKERS:
        if marker.lower() in msg_lower:
            competence_scaffold += 1
            competence_evidence.append(f"SCAFFOLD({marker})")

    if competence_deficit >= 3:
        competence_level = SDTPressure.HIGH
    elif competence_deficit >= 1:
        competence_level = SDTPressure.MEDIUM
    else:
        competence_level = SDTPressure.LOW

    # ── Relatedness ──────────────────────────────────────────────────
    relatedness_deficit = 0
    relatedness_seeking = 0

    for marker in _RELATEDNESS_DEFICIT_MARKERS:
        if marker.lower() in msg_lower:
            relatedness_deficit += 2
            relatedness_evidence.append(f"DEFICIT({marker})")

    for marker in _RELATEDNESS_SEEKING_MARKERS:
        if marker.lower() in msg_lower:
            relatedness_seeking += 1
            relatedness_evidence.append(f"SEEKING({marker})")

    if relatedness_deficit >= 3:
        relatedness_level = SDTPressure.HIGH
    elif relatedness_deficit >= 1:
        relatedness_level = SDTPressure.MEDIUM
    else:
        relatedness_level = SDTPressure.LOW

    return SDTPressureVector(
        autonomy=autonomy_level,
        competence=competence_level,
        relatedness=relatedness_level,
        autonomy_evidence=autonomy_evidence,
        competence_evidence=competence_evidence,
        relatedness_evidence=relatedness_evidence,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# POSTURE RESOLUTION
# ═══════════════════════════════════════════════════════════════════════════════


def resolve_posture(
    polyvagal: PolyvagalState,
    sdt: SDTPressureVector,
) -> tuple[AgentPosture, str]:
    """Resolve recommended agent posture from classified state.

    Priority: polyvagal state first, then SDT overlays.
    Returns: (posture, reason)
    """
    # ── Base posture from polyvagal state ─────────────────────────────
    if polyvagal == PolyvagalState.SYMPATHETIC:
        base_posture = AgentPosture.GROUND
        reason = "Sympathetic activation detected — de-escalate, shorten, ground."
    elif polyvagal == PolyvagalState.DORSAL:
        base_posture = AgentPosture.HOLD_SPACE
        reason = "Dorsal vagal detected — don't force engagement, hold space."
    else:
        base_posture = AgentPosture.EXPLORE
        reason = "Ventral vagal — safe to explore, challenge, co-create."

    # ── SDT overlays (modify base posture) ───────────────────────────
    # High autonomy pressure → offer options instead of prescribing
    if sdt.autonomy == SDTPressure.HIGH:
        if base_posture == AgentPosture.EXPLORE:
            base_posture = AgentPosture.OFFER_OPTIONS
            reason += " + Autonomy pressure HIGH — offer options, don't prescribe."
        elif base_posture == AgentPosture.GROUND:
            reason += " + Autonomy pressure HIGH — ground with options, not directives."

    # High competence pressure → scaffold instead of rescuing
    if sdt.competence == SDTPressure.HIGH:
        if base_posture == AgentPosture.EXPLORE:
            base_posture = AgentPosture.SCAFFOLD
            reason += " + Competence pressure HIGH — scaffold, don't rescue."
        elif base_posture == AgentPosture.GROUND:
            reason += " + Competence pressure HIGH — ground + scaffold."

    # High relatedness pressure → acknowledge before informing
    if sdt.relatedness == SDTPressure.HIGH:
        if base_posture == AgentPosture.EXPLORE:
            base_posture = AgentPosture.ACKNOWLEDGE
            reason += " + Relatedness pressure HIGH — acknowledge before informing."
        elif base_posture in (AgentPosture.GROUND, AgentPosture.HOLD_SPACE):
            reason += " + Relatedness pressure HIGH — connect before content."

    return base_posture, reason


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════


class StateClassifier:
    """Deterministic rule-based human state classifier.

    Physics: entropy reduction.
    Input: ambiguous human message + session context.
    Output: structured state vector with evidence chain.

    Constitutional:
      - F2: every classification carries evidence
      - F4: output is lower-entropy than input
      - F6: never pathologize
      - F9: no consciousness claims
      - F11: full audit trail
    """

    def classify(
        self,
        message: str,
        session_id: str = "",
        recent_messages: list[str] | None = None,
    ) -> StateClassifierResult:
        """Classify human state from message.

        Args:
            message: The human message to classify.
            session_id: Session identifier for audit trail.
            recent_messages: Recent message history for repetition detection.

        Returns:
            StateClassifierResult with state vector + governance metadata.
        """
        rules_applied: list[str] = []

        # Step 1: Extract linguistic features
        features = extract_features(message, recent_messages)
        rules_applied.append("LINGUISTIC_FEATURE_EXTRACTION")

        # Step 2: Classify Polyvagal state
        polyvagal, polyvagal_evidence, polyvagal_confidence = classify_polyvagal(features)
        rules_applied.append(f"POLYVAGAL_CLASSIFY→{polyvagal.value}")

        # Step 3: Detect SDT pressure
        sdt = detect_sdt_pressure(features)
        rules_applied.append("SDT_PRESSURE_DETECT")

        # Step 4: Resolve agent posture
        posture, posture_reason = resolve_posture(polyvagal, sdt)
        rules_applied.append(f"POSTURE_RESOLVE→{posture.value}")

        # Step 5: Governance flags
        f6_risk = 0.0
        f9_risk = 0.0

        # F6: dignity risk if human is in distress/crisis markers
        if polyvagal == PolyvagalState.SYMPATHETIC and polyvagal_confidence > 0.7:
            f6_risk = 0.3
            rules_applied.append("F6_RISK_ELEVATED(sympathetic_high_confidence)")

        if sdt.autonomy == SDTPressure.HIGH:
            f6_risk = max(f6_risk, 0.2)
            rules_applied.append("F6_RISK_ELEVATED(autonomy_pressure)")

        # F9: hantu risk if we're making strong claims with low evidence
        if polyvagal_confidence < 0.4:
            f9_risk = 0.2
            rules_applied.append("F9_RISK(low_confidence_classification)")

        # Build state vector
        state_vector = StateVector(
            polyvagal=polyvagal,
            sdt_pressure=sdt,
            confidence=polyvagal_confidence,
            uncertainty_note=(
                "Low confidence — weak signal, defaulting to ventral baseline."
                if polyvagal_confidence < 0.5
                else ""
            ),
            polyvagal_evidence=polyvagal_evidence,
            polyvagal_signal_count=len(polyvagal_evidence),
            recommended_posture=posture,
            posture_reason=posture_reason,
            message_length=features.message_length,
            has_caps=features.has_caps_shouting,
            has_repetition=features.repetition_detected,
        )

        return StateClassifierResult(
            state_vector=state_vector,
            session_id=session_id,
            f6_dignity_risk=f6_risk,
            f9_hantu_risk=f9_risk,
            requires_posture_shift=(posture != AgentPosture.EXPLORE),
            rules_applied=rules_applied,
            classification_note=(
                f"Polyvagal={polyvagal.value}({polyvagal_confidence:.2f}), "
                f"SDT=[A:{sdt.autonomy.value},C:{sdt.competence.value},R:{sdt.relatedness.value}], "
                f"Posture={posture.value}"
            ),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

_classifier: StateClassifier | None = None


def get_state_classifier() -> StateClassifier:
    """Get the singleton state classifier."""
    global _classifier
    if _classifier is None:
        _classifier = StateClassifier()
    return _classifier
