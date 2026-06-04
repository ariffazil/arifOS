"""Concrete scorer for the Anti-Beautiful-One Lock.

Takes raw LLM-generated text and computes:
- beauty_score: how polished / abstract / confident / metaphorical
- operational_contact_score: how many concrete actions, paths, commands, tests
- human_cost_detected: whether human impact is acknowledged
- survival_status: inferred from keywords
- beauty_to_consequence_ratio: the critical collapse metric

The lock thresholds live in RecursiveGovernanceEngine._apply_anti_beautiful_one().
This module gives the lock something to see.

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

# ──────────────────────────────────────────────────────────────────────────
# Beauty markers — language that sparkles without necessarily touching ground
# ──────────────────────────────────────────────────────────────────────────

CONFIDENCE_MARKERS: Final[frozenset[str]] = frozenset({
    "certainly", "definitely", "absolutely", "without doubt", "undoubtedly",
    "clearly", "obviously", "it is evident", "there is no question",
    "seamlessly", "effortlessly", "robustly", "comprehensively",
    "holistically", "synergistically", "optimally", "best-in-class",
    "state-of-the-art", "cutting-edge", "world-class", "unparalleled",
})

ABSTRACT_NOUN_SUFFIXES: Final[tuple[str, ...]] = (
    "ness", "ity", "ism", "tion", "sion", "ment", "ance", "ence",
)

METAPHOR_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"\b(journey|anchor|north star|heartbeat|backbone|fabric|weaving|tapestry|ecosystem|landscape|orbit|gravity|pulse|soul|spirit|essence)\b", re.I),
    re.compile(r"\b(breathe life|give voice|come alive|take flight|rise above|forge|ignite|spark|ignite|blossom|unfold)\b", re.I),
)

EMOTIONAL_LANGUAGE: Final[frozenset[str]] = frozenset({
    "passion", "passionate", "deeply committed", "heartfelt", "believe in",
    "dream", "vision", "inspired", "transformative", "revolutionary",
    "meaningful", "purpose-driven", "sacred", "honored", "humbled",
})

SEAL_SELF_CERTIFY: Final[frozenset[str]] = frozenset({
    "seal", "certify", "i certify", "i attest", "i verify", "i confirm",
    "this is sealed", "verdict: seal", "state: seal", "# seal",
})

# ──────────────────────────────────────────────────────────────────────────
# Operational contact markers — language that touches real things
# ──────────────────────────────────────────────────────────────────────────

FILE_PATH_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?:/root|/opt|/etc|/var|/tmp|/home|/usr)[/\w\-\.]+"
)

COMMAND_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(curl|wget|git\s+(commit|push|pull|checkout|clone|log)|systemctl|docker|npm|pip|uv|pytest|make|mkdir|rm|cp|mv|sed|awk|grep)\b"
)

SERVICE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(arifos|arifosd|wealth-organ|well|geox-mcp|a-forge|aaa-a2a|caddy|nats|prometheus|grafana|earlyoom)\b",
    re.I,
)

PORT_PATTERN: Final[re.Pattern[str]] = re.compile(r":\d{4,5}")

TEST_RESULT_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(\d+\s*/\s*\d+\s+(pass|fail|PASS|FAIL)|pytest|coverage|test_)"
)

METRIC_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(\d+\.?\d*\s*(ms|s|MB|GB|%|rpm|rps)|CPU|memory|disk|load|latency)\b"
)

ROLLBACK_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\b(rollback|revert|undo|back out|previous commit|last known good|git revert)\b",
    re.I,
)

# ──────────────────────────────────────────────────────────────────────────
# Human cost / survival markers
# ──────────────────────────────────────────────────────────────────────────

HUMAN_COST_MARKERS: Final[frozenset[str]] = frozenset({
    "human", "user", "arif", "sovereign", "operator", "customer",
    "dignity", "privacy", "biometric", "stress", "fatigue", "cognitive load",
    "well-being", "wellbeing", "maruah", "consent", "trauma", "scar",
})

SURVIVAL_CRITICAL_MARKERS: Final[frozenset[str]] = frozenset({
    "critical", "outage", "down", "failure", "crash", "data loss",
    "corruption", "breach", "exposed", "leak", " compromis",
})

SURVIVAL_HEALTHY_MARKERS: Final[frozenset[str]] = frozenset({
    "healthy", "up", "green", "pass", "stable", "recovered", "resolved",
})

# ──────────────────────────────────────────────────────────────────────────
# Output structure
# ──────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class AntiBeautifulScores:
    beauty_score: float = 0.0
    operational_contact_score: float = 0.0
    human_cost_detected: bool = False
    survival_status: str = "unknown"
    reality_evidence_present: bool = False
    contradiction_challenged: bool = False
    beauty_to_consequence_ratio: float = 1.0


# ──────────────────────────────────────────────────────────────────────────
# Scorer
# ──────────────────────────────────────────────────────────────────────────


class AntiBeautifulScorer:
    """Score LLM text for sterile polished collapse."""

    def __init__(self) -> None:
        # These weights are forged from observed failure modes, not tuned.
        # They can be ratified by F13 if needed.
        self.confidence_weight = 0.20
        self.abstraction_weight = 0.15
        self.metaphor_weight = 0.20
        self.emotion_weight = 0.15
        self.seal_weight = 0.30

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────

    def score(self, text: str) -> AntiBeautifulScores:
        if not text or not text.strip():
            return AntiBeautifulScores()

        normalized = text.lower()
        tokens = re.findall(r"\b\w+\b", normalized)
        token_count = max(len(tokens), 1)
        word_count = max(len(normalized.split()), 1)

        beauty = self._beauty_score(normalized, tokens, token_count, word_count)
        op_contact = self._operational_contact_score(text)
        human_cost = self._human_cost_detected(normalized)
        survival = self._survival_status(normalized)
        reality = self._reality_evidence_present(text)
        contradiction = self._contradiction_challenged(normalized)

        ratio = self._compute_ratio(beauty, op_contact)

        return AntiBeautifulScores(
            beauty_score=round(beauty, 3),
            operational_contact_score=round(op_contact, 3),
            human_cost_detected=human_cost,
            survival_status=survival,
            reality_evidence_present=reality,
            contradiction_challenged=contradiction,
            beauty_to_consequence_ratio=round(ratio, 3),
        )

    # ──────────────────────────────────────────────────────────────────────
    # Beauty sub-scores
    # ──────────────────────────────────────────────────────────────────────

    def _beauty_score(
        self,
        normalized: str,
        tokens: list[str],
        token_count: int,
        word_count: int,
    ) -> float:
        confidence_hits = sum(1 for m in CONFIDENCE_MARKERS if m in normalized)
        confidence = min(confidence_hits * 0.15, 0.60)

        abstract_hits = sum(
            1 for t in tokens if t.endswith(ABSTRACT_NOUN_SUFFIXES) and len(t) > 4
        )
        abstraction = min(abstract_hits / token_count * 3.0, 0.50)

        metaphor_hits = sum(
            1 for p in METAPHOR_PATTERNS if p.search(normalized)
        )
        metaphor = min(metaphor_hits * 0.15, 0.55)

        emotion_hits = sum(1 for m in EMOTIONAL_LANGUAGE if m in normalized)
        emotion = min(emotion_hits * 0.12, 0.40)

        seal_hits = sum(1 for m in SEAL_SELF_CERTIFY if m in normalized)
        seal = min(seal_hits * 0.25, 0.70)

        raw = (
            confidence * self.confidence_weight
            + abstraction * self.abstraction_weight
            + metaphor * self.metaphor_weight
            + emotion * self.emotion_weight
            + seal * self.seal_weight
        )
        # Normalize by max possible weighted sum (~0.235) to 0–1
        return min(raw / 0.235, 1.0)

    # ──────────────────────────────────────────────────────────────────────
    # Operational contact sub-score
    # ──────────────────────────────────────────────────────────────────────

    def _operational_contact_score(self, text: str) -> float:
        scores: list[float] = []

        scores.append(min(len(FILE_PATH_PATTERN.findall(text)) * 0.08, 0.25))
        scores.append(min(len(COMMAND_PATTERN.findall(text)) * 0.08, 0.25))
        scores.append(min(len(SERVICE_PATTERN.findall(text)) * 0.10, 0.20))
        scores.append(min(len(PORT_PATTERN.findall(text)) * 0.05, 0.15))
        scores.append(min(len(TEST_RESULT_PATTERN.findall(text)) * 0.10, 0.20))
        scores.append(min(len(METRIC_PATTERN.findall(text)) * 0.08, 0.20))
        scores.append(min(len(ROLLBACK_PATTERN.findall(text)) * 0.15, 0.30))

        return min(sum(scores), 1.0)

    # ──────────────────────────────────────────────────────────────────────
    # Human cost and survival
    # ──────────────────────────────────────────────────────────────────────

    def _human_cost_detected(self, normalized: str) -> bool:
        return any(marker in normalized for marker in HUMAN_COST_MARKERS)

    def _survival_status(self, normalized: str) -> str:
        critical = sum(1 for m in SURVIVAL_CRITICAL_MARKERS if m in normalized)
        healthy = sum(1 for m in SURVIVAL_HEALTHY_MARKERS if m in SURVIVAL_HEALTHY_MARKERS if m in normalized)

        if critical > healthy and critical >= 1:
            return "critical"
        if healthy > critical and healthy >= 1:
            return "healthy"
        return "unknown"

    def _reality_evidence_present(self, text: str) -> bool:
        """Does the text cite URLs, file paths, commit SHAs, or measurable data?"""
        has_url = bool(re.search(r"https?://\S+", text))
        has_sha = bool(re.search(r"\b[0-9a-f]{7,40}\b", text, re.I))
        has_path = bool(FILE_PATH_PATTERN.search(text))
        has_metric = bool(METRIC_PATTERN.search(text))
        return any((has_url, has_sha, has_path, has_metric))

    def _contradiction_challenged(self, normalized: str) -> bool:
        """Does the text acknowledge uncertainty or open questions?"""
        challenge_markers = (
            "however", "but", "although", "on the other hand", "uncertain",
            "unknown", "might", "may", "could", "risk", "trade-off",
            "limitation", " caveat", "not clear", "requires verification",
        )
        return any(m in normalized for m in challenge_markers)

    # ──────────────────────────────────────────────────────────────────────
    # Ratio computation
    # ──────────────────────────────────────────────────────────────────────

    def _compute_ratio(self, beauty: float, op_contact: float) -> float:
        # High beauty with zero contact → maximum ratio
        # High beauty with high contact → ratio approaches 1
        denominator = max(op_contact, 0.05)
        return beauty / denominator
