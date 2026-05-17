# arifOS SENSE Pipeline — Evidence Span Extractor
# Keyword + regex span extraction from result snippets
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import re
from dataclasses import dataclass

from .result_normalizer import NormalizedResult


@dataclass
class EvidenceSpan:
    text: str
    start: int
    end: int
    method: str  # "keyword" | "regex" | "exact"
    matched_term: str | None = None
    confidence: float = 0.5


@dataclass
class SpanExtractionResult:
    url: str
    title: str
    spans: list[EvidenceSpan]
    span_count: int
    unique_terms_matched: int


def _extract_snippet(text: str, start: int, window: int = 40) -> str:
    """Extract surrounding context window around a match."""
    before = max(0, start - window)
    after = min(len(text), start + window)
    snippet = text[before:after].strip()
    prefix = "..." if before > 0 else ""
    suffix = "..." if after < len(text) else ""
    return f"{prefix}{snippet}{suffix}"


class EvidenceSpanExtractor:
    def __init__(
        self,
        keyword_patterns: dict[str, list[str]] | None = None,
        regex_patterns: list[str] | None = None,
    ) -> None:
        default_keywords: dict[str, list[str]] = {
            "number": [
                "one",
                "two",
                "three",
                "first",
                "second",
                "third",
                "1",
                "2",
                "3",
                "10",
                "100",
                "1000",
            ],
            "date": [
                "january",
                "february",
                "march",
                "april",
                "may",
                "june",
                "july",
                "august",
                "september",
                "october",
                "november",
                "december",
                "2020",
                "2021",
                "2022",
                "2023",
                "2024",
                "2025",
            ],
            "percentage": ["percent", "%", "percentage", "rate"],
            "definition": ["is defined as", "means", "refers to", "is the"],
            "comparison": [
                "compared to",
                "versus",
                "vs",
                "more than",
                "less than",
                "greater",
                "fewer",
                "higher",
                "lower",
            ],
        }
        self._keyword_patterns = keyword_patterns or default_keywords
        self._regex_patterns = [re.compile(p, re.IGNORECASE) for p in (regex_patterns or [])]
        self._fallback_regex = [
            re.compile(
                r"\b\d+(?:\.\d+)?\s*(?:percent|%|people|users|cases|deaths)\b", re.IGNORECASE
            ),
            re.compile(
                r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b",
                re.IGNORECASE,
            ),
            re.compile(r"\$\d+(?:,\d{3})*(?:\.\d{2})?"),
            re.compile(r"\b\d+(?:\.\d+)?\s+(?:million|billion|trillion|thousand)\b", re.IGNORECASE),
        ]

    def extract(self, result: NormalizedResult) -> SpanExtractionResult:
        text = f"{result.title} {result.snippet}"
        spans: list[EvidenceSpan] = []

        spans.extend(self._extract_keywords(text))
        spans.extend(self._extract_regex(text))
        spans.sort(key=lambda s: s.start)

        unique_terms = len(set(s.matched_term for s in spans if s.matched_term))

        return SpanExtractionResult(
            url=result.url,
            title=result.title,
            spans=spans,
            span_count=len(spans),
            unique_terms_matched=unique_terms,
        )

    def _extract_keywords(self, text: str) -> list[EvidenceSpan]:
        spans = []
        text_lower = text.lower()
        for _category, keywords in self._keyword_patterns.items():
            for kw in keywords:
                pos = 0
                while True:
                    idx = text_lower.find(kw.lower(), pos)
                    if idx == -1:
                        break
                    snippet = _extract_snippet(text, idx)
                    spans.append(
                        EvidenceSpan(
                            text=snippet,
                            start=idx,
                            end=idx + len(kw),
                            method="keyword",
                            matched_term=kw,
                            confidence=0.6,
                        )
                    )
                    pos = idx + 1
        return spans

    def _extract_regex(self, text: str) -> list[EvidenceSpan]:
        spans = []
        for pattern in self._fallback_regex:
            for match in pattern.finditer(text):
                snippet = _extract_snippet(text, match.start())
                spans.append(
                    EvidenceSpan(
                        text=snippet,
                        start=match.start(),
                        end=match.end(),
                        method="regex",
                        matched_term=match.group(),
                        confidence=0.5,
                    )
                )
        return spans

    def extract_batch(self, results: list[NormalizedResult]) -> list[SpanExtractionResult]:
        return [self.extract(r) for r in results]


def extract_spans(result: NormalizedResult) -> SpanExtractionResult:
    extractor = EvidenceSpanExtractor()
    return extractor.extract(result)


def extract_spans_from_results(
    results: list[NormalizedResult],
) -> list[SpanExtractionResult]:
    extractor = EvidenceSpanExtractor()
    return extractor.extract_batch(results)
