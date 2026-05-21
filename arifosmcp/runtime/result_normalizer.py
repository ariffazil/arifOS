# arifOS SENSE Pipeline — Result Normalizer
# Canonical result format for all SENSE pipeline providers
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import IntEnum
from typing import Any

logger = logging.getLogger(__name__)


class EvidenceLevel(IntEnum):
    L0 = 0  # Unverified — no citation, no verification
    L1 = 1  # Title verified — title matches query
    L2 = 2  # Title + snippet verified
    L3 = 3  # Trusted domain, full attribution
    L4 = 4  # L3 + first-hand / primary source signal
    L5 = 5  # L4 + primary source, authoritative author


# Trusted domains — authority boost
TRUSTED_DOMAINS: set[str] = {
    "arxiv.org",
    "github.com",
    "stackoverflow.com",
    "wikipedia.org",
    "wikidata.org",
    "medium.com",
    "dev.to",
    "reddit.com",
    "news.ycombinator.com",
    "lobste.rs",
    "techcrunch.com",
    "theverge.com",
    "arstechnica.com",
    "wired.com",
    "nature.com",
    "science.org",
    "cell.com",
    "semanticscholar.org",
    "scholar.google.com",
    "pubmed.ncbi.nlm.nih.gov",
    "ncbi.nlm.nih.gov",
    "mit.edu",
    "stanford.edu",
    "harvard.edu",
    "berkeley.edu",
    "ox.ac.uk",
    "cambridge.org",
}

# Code / technical domains
CODE_DOMAINS: set[str] = {
    "github.com",
    "stackoverflow.com",
    "dev.to",
    "readthedocs.io",
    "docs.python.org",
    "docs.github.com",
    "developer.mozilla.org",
    "learn.microsoft.com",
    "huggingface.co",
    "replicate.com",
    "arxiv.org",
}

# News domains
NEWS_DOMAINS: set[str] = {
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "cnn.com",
    "nytimes.com",
    "theguardian.com",
    "npr.org",
    "bloomberg.com",
    "wsj.com",
    "economist.com",
    "nature.com",
    "science.org",
}


@dataclass
class NormalizedResult:
    url: str
    title: str
    snippet: str
    source: str  # Provider name e.g. "brave", "exa"
    score: float = 0.0  # Raw provider score
    domain: str = ""
    published_date: datetime | None = None
    author: str | None = None
    language: str | None = None
    is_code: bool = False
    is_news: bool = False
    is_trusted: bool = False
    relevance: float = 0.0
    authority: float = 0.0
    freshness: float = 0.0
    provider_trust: float = 0.5
    content_depth: float = 0.5
    evidence_level: EvidenceLevel = EvidenceLevel.L0
    _evidence_level_explicit: bool = False
    provider_type: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Track if evidence_level was explicitly set before we recalculate
        if self.evidence_level != EvidenceLevel.L0:
            self._evidence_level_explicit = True
        if not self.domain:
            self.domain = _extract_domain(self.url)
        if not self.source:
            self.source = self.provider_type
        self._compute_flags()
        self._compute_evidence_level()

    def _compute_flags(self) -> None:
        d = self.domain.lower()
        self.is_code = self.is_code or any(code_domain in d for code_domain in CODE_DOMAINS)
        self.is_news = self.is_news or any(news_domain in d for news_domain in NEWS_DOMAINS)
        self.is_trusted = self.is_trusted or d in TRUSTED_DOMAINS

    def _compute_evidence_level(self) -> None:
        if self.evidence_level != EvidenceLevel.L0:
            return
        if not self.title:
            self.evidence_level = EvidenceLevel.L0
            return
        if not self.url.startswith("http"):
            self.evidence_level = EvidenceLevel.L0
            return
        if self.is_trusted:
            self.evidence_level = EvidenceLevel.L3
        elif self.is_code:
            self.evidence_level = EvidenceLevel.L2
        elif self.published_date:
            self.evidence_level = EvidenceLevel.L1
        else:
            self.evidence_level = EvidenceLevel.L0

    @property
    def final_score(self) -> float:
        return (
            self.relevance * 0.40
            + self.authority * 0.20
            + self.freshness * 0.15
            + self.provider_trust * 0.15
            + self.content_depth * 0.10
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet,
            "source": self.source,
            "score": self.score,
            "domain": self.domain,
            "final_score": self.final_score,
            "evidence_level": self.evidence_level.value,
            "is_trusted": self.is_trusted,
            "is_code": self.is_code,
            "is_news": self.is_news,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "author": self.author,
            "relevance": self.relevance,
            "authority": self.authority,
            "freshness": self.freshness,
            "provider_trust": self.provider_trust,
            "content_depth": self.content_depth,
            "provider_type": self.provider_type,
            **self.extra,
        }


class ResultNormalizer:
    __slots__ = ("_trusted", "_code", "_news")

    def __init__(
        self,
        trusted_domains: set[str] | None = None,
        code_domains: set[str] | None = None,
        news_domains: set[str] | None = None,
    ) -> None:
        self._trusted = trusted_domains if trusted_domains is not None else TRUSTED_DOMAINS
        self._code = code_domains if code_domains is not None else CODE_DOMAINS
        self._news = news_domains if news_domains is not None else NEWS_DOMAINS

    def normalize(self, raw: dict[str, Any], provider: str) -> NormalizedResult:
        url = raw.get("url", raw.get("link", ""))
        title = raw.get("title", "")
        snippet = raw.get("description", raw.get("snippet", ""))
        score = raw.get("score", raw.get("relevance_score", 0.0))

        published_date: datetime | None = None
        if raw.get("published_date"):
            published_date = _parse_date(raw["published_date"])

        return NormalizedResult(
            url=url,
            title=title,
            snippet=snippet,
            source=provider,
            score=float(score) if score else 0.0,
            published_date=published_date,
            author=raw.get("author"),
            language=raw.get("language"),
            provider_type=provider,
            extra=raw.get("extra", {}),
        )

    def normalize_batch(
        self, raw_results: list[dict[str, Any]], provider: str
    ) -> list[NormalizedResult]:
        return [self.normalize(r, provider) for r in raw_results]


def _extract_domain(url: str) -> str:
    if not url:
        return ""
    match = re.match(r"https?://([^/]+)", url)
    return match.group(1) if match else ""


def _parse_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%b %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=UTC)
        except ValueError:
            pass
    return None
