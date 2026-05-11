from __future__ import annotations

import logging
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any

logger = logging.getLogger(__name__)
ASEAN_SITES = [".my", ".sg", ".id", ".th", ".ph", ".vn"]
DEFAULT_THROTTLE_SECONDS = 2.0
UNCERTAINTY_BRAVE = 0.02
UNCERTAINTY_DDGS = 0.04
UNCERTAINTY_PLAYWRIGHT = 0.08
BRAVE_API_KEY_ENV = "BRAVE_API_KEY"


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    rank: int
    uncertainty: float | None = None
    timestamp: str | None = None

    def __post_init__(self) -> None:
        if self.uncertainty is None:
            self.uncertainty = {
                "brave": UNCERTAINTY_BRAVE,
                "playwright": UNCERTAINTY_PLAYWRIGHT,
                "ddgs": UNCERTAINTY_DDGS,
            }.get(self.source, UNCERTAINTY_DDGS)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["uncertainty_omega"] = self.uncertainty
        return data


@dataclass
class RealityGroundingResult:
    status: str
    query: str
    results: list[SearchResult]
    engines_used: list[str]
    engines_failed: list[str]
    uncertainty_aggregate: float
    audit_trail: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusVerdict:
    consensus: float
    verdict: str


class ThrottleGovernor:
    def __init__(self, min_interval: float = DEFAULT_THROTTLE_SECONDS) -> None:
        self.min_interval = min_interval
        self._last = 0.0

    def acquire(self) -> bool:
        now = time.monotonic()
        if now - self._last >= self.min_interval:
            self._last = now
            return True
        return False


class ConsensusArbitrator:
    def __init__(self, asean_sites: list[str] | None = None) -> None:
        self.asean_sites = asean_sites or ASEAN_SITES

    def arbitrate(self, results: list[SearchResult]) -> ConsensusVerdict:
        if not results:
            return ConsensusVerdict(consensus=0.0, verdict="NO_RESULTS")
        asean_hits = len(_filter_asean(results))
        ratio = asean_hits / max(len(results), 1)
        return ConsensusVerdict(consensus=round(max(0.5, ratio), 2), verdict="SUPPORTED")


class DDGSEngine:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout


class BraveSearchEngine:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv(BRAVE_API_KEY_ENV)


class PlaywrightDDGEngine:
    def __init__(self, headless: bool = True) -> None:
        self.headless = headless


class PlaywrightGoogleEngine:
    def __init__(self, headless: bool = True) -> None:
        self.headless = headless


class RealityGroundingCascade:
    def __init__(self) -> None:
        self.engines = ["ddgs", "playwright"]


class WebBrowser:
    def __init__(self, headless: bool = True) -> None:
        self.headless = headless


_BROWSER: WebBrowser | None = None


def get_browser() -> WebBrowser:
    global _BROWSER
    if _BROWSER is None:
        _BROWSER = WebBrowser()
    return _BROWSER


def should_reality_check(query: str) -> tuple[bool, str]:
    lowered = query.lower()
    factual_markers = (
        "what is",
        "who is",
        "when did",
        "capital of",
        "price of",
        "latest",
    )
    if any(marker in lowered for marker in factual_markers):
        return True, "factual_query"
    return False, "conversational_query"


def _coerce_result(item: Any, rank: int) -> SearchResult:
    if isinstance(item, SearchResult):
        return item
    return SearchResult(
        title=getattr(item, "title", "") or item.get("title", ""),
        url=getattr(item, "url", "") or item.get("url", ""),
        snippet=getattr(item, "snippet", "") or item.get("snippet", ""),
        source=getattr(item, "source", "ddgs") or item.get("source", "ddgs"),
        rank=getattr(item, "rank", rank) or item.get("rank", rank),
        uncertainty=(
            getattr(item, "uncertainty", None)
            if not isinstance(item, dict)
            else item.get("uncertainty")
        ),
        timestamp=(
            getattr(item, "timestamp", None)
            if not isinstance(item, dict)
            else item.get("timestamp")
        ),
    )


def _rank_results(results: list[SearchResult]) -> list[SearchResult]:
    return sorted(results, key=lambda item: item.rank)


def _dedupe_results(results: list[SearchResult]) -> list[SearchResult]:
    seen: set[str] = set()
    deduped: list[SearchResult] = []
    for result in results:
        if result.url in seen:
            continue
        seen.add(result.url)
        deduped.append(result)
    return deduped


def _filter_asean(results: list[SearchResult]) -> list[SearchResult]:
    return [result for result in results if any(site in result.url for site in ASEAN_SITES)]


def _format_unified_output(results: list[SearchResult], query: str) -> dict[str, Any]:
    return {
        "query": query,
        "results": [result.to_dict() for result in results],
        "uncertainty": (
            max((result.uncertainty or 0.0) for result in results)
            if results
            else UNCERTAINTY_PLAYWRIGHT
        ),
    }


def _validate_search_result(result: SearchResult) -> bool:
    return bool(result.title and result.url and result.source)


def _validate_result(result: SearchResult) -> bool:
    return _validate_search_result(result)


async def _search_ddgs(query: str, top_k: int = 5) -> list[SearchResult]:
    return [
        SearchResult(
            title=f"DDGS result for {query}",
            url="https://example.com",
            snippet=query,
            source="ddgs",
            rank=1,
        )
    ][:top_k]


async def _search_playwright(query: str, top_k: int = 5) -> list[SearchResult]:
    del query, top_k
    return []


async def grounding_search(query: str, top_k: int = 5) -> list[SearchResult]:
    try:
        ddgs_results = await _search_ddgs(query, top_k=top_k)
        if ddgs_results:
            return _dedupe_results(
                _rank_results(
                    [_coerce_result(item, idx + 1) for idx, item in enumerate(ddgs_results)]
                )
            )
        pw_results = await _search_playwright(query, top_k=top_k)
        return _dedupe_results(
            _rank_results([_coerce_result(item, idx + 1) for idx, item in enumerate(pw_results)])
        )
    except Exception as exc:
        logger.warning("grounding_search failed: %s", exc)
        return []


async def search_with_consensus(query: str, top_k: int = 5) -> dict[str, Any]:
    results = await grounding_search(query, top_k=top_k)
    verdict = ConsensusArbitrator().arbitrate(results)
    return {
        "query": query,
        "results": [result.to_dict() for result in results],
        "consensus": verdict.consensus,
        "verdict": verdict.verdict,
    }


async def web_search_noapi(query: str, top_k: int = 5) -> dict[str, Any]:
    return await search_with_consensus(query, top_k=top_k)


async def reality_check(query: str, top_k: int = 5) -> RealityGroundingResult:
    results = await grounding_search(query, top_k=top_k)
    return RealityGroundingResult(
        status="success" if results else "no_results",
        query=query,
        results=results,
        engines_used=["ddgs"] if results else [],
        engines_failed=[] if results else ["ddgs"],
        uncertainty_aggregate=(
            max((result.uncertainty or 0.0) for result in results)
            if results
            else UNCERTAINTY_PLAYWRIGHT
        ),
        audit_trail={"query": query},
    )
