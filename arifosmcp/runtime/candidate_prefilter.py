# arifOS SENSE Pipeline — Candidate Prefilter
# 7-stage hard filter pipeline before reranking
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .result_normalizer import NormalizedResult

# Hard limits
MIN_TITLE_LENGTH = 10
MIN_DESCRIPTION_LENGTH = 20
MIN_FINAL_SCORE = 0.05
MAX_URL_LENGTH = 2048

BLOCKED_DOMAINS: set[str] = {
    "facebook.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "tiktok.com",
    "snapchat.com",
    "pinterest.com",
    "linkedin.com",
    "youtube.com",
    "youtu.be",
    "twitch.tv",
    "reddit.com/r/",
    "redd.it",
    "wikipedia.org",  # too broad, prefer specific articles
    "example.com",
    "test.com",
    "localhost",
}

SPAM_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)\b(buy\s+now|click\s+here|limited\s+offer|act\s+now)\b"),
    re.compile(r"(?i)\b(free\s+win|congratulations\s+you\s+won)\b"),
    re.compile(r"(?i)\b(earn\s+\$\$|make\s+money\s+online)\b"),
    re.compile(r"^\s*https?://[^\s]+\.(pdf|docx?)\s*$", re.IGNORECASE),
]

ADULT_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)\b(adult|nsfw|porn|x-rated)\b"),
]


@dataclass
class PrefilterResult:
    passed: bool
    failed_stages: list[str] = field(default_factory=list)
    final_score: float = 0.0
    reason: str | None = None


class CandidatePrefilter:
    __slots__ = ("_blocked", "_spam", "_adult", "_min_title", "_min_desc", "_min_score", "_max_url")

    def __init__(
        self,
        blocked_domains: set[str] | None = None,
        spam_patterns: list[re.Pattern[str]] | None = None,
        adult_patterns: list[re.Pattern[str]] | None = None,
    ) -> None:
        self._blocked = blocked_domains if blocked_domains is not None else BLOCKED_DOMAINS
        self._spam = spam_patterns if spam_patterns is not None else SPAM_PATTERNS
        self._adult = adult_patterns if adult_patterns is not None else ADULT_PATTERNS
        self._min_title = MIN_TITLE_LENGTH
        self._min_desc = MIN_DESCRIPTION_LENGTH
        self._min_score = MIN_FINAL_SCORE
        self._max_url = MAX_URL_LENGTH

    def filter(self, result: NormalizedResult) -> PrefilterResult:
        failed: list[str] = []
        score = result.final_score

        # Stage 1: URL validity
        if not result.url or not result.url.startswith("http"):
            failed.append("url_invalid")

        # Stage 2: URL length
        if len(result.url) > self._max_url:
            failed.append("url_too_long")

        # Stage 3: Domain blocklist
        if any(blocked in result.domain.lower() for blocked in self._blocked):
            failed.append("domain_blocked")

        # Stage 4: Title quality
        title = (result.title or "").strip()
        if len(title) < self._min_title:
            failed.append("title_too_short")

        # Stage 5: Snippet quality
        snippet = (result.snippet or "").strip()
        if len(snippet) < self._min_desc:
            failed.append("snippet_too_short")

        # Stage 6: Spam / adult content
        combined = f"{title} {snippet}".lower()
        if any(p.search(combined) for p in self._spam):
            failed.append("spam_detected")
        if any(p.search(combined) for p in self._adult):
            failed.append("adult_content")

        # Stage 7: Minimum quality score
        if score < self._min_score:
            failed.append("score_below_minimum")

        passed = len(failed) == 0
        return PrefilterResult(
            passed=passed,
            failed_stages=failed,
            final_score=score,
            reason=", ".join(failed) if failed else None,
        )

    def filter_batch(self, results: list[NormalizedResult]) -> list[NormalizedResult]:
        passed = []
        for r in results:
            pf = self.filter(r)
            if pf.passed:
                passed.append(r)
        return passed


def prefilter_candidates(
    results: list[NormalizedResult],
) -> list[NormalizedResult]:
    prefilter = CandidatePrefilter()
    return prefilter.filter_batch(results)
