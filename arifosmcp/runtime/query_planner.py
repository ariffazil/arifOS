# arifOS SENSE Pipeline — Query Planner
# Routing engine that selects providers and query modes
# QueryPlanner owns routing authority — providers are interchangeable sensors
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx

from .provider_registry import (
    ProviderRegistry,
    ProviderType,
    QueryMode,
    get_registry,
)

logger = logging.getLogger(__name__)

QUERY_PLANNER_AVAILABLE = True

_MODE_PRIORITY_ATTR: dict[QueryMode, str] = {
    QueryMode.REALTIME: "priority_realtime",
    QueryMode.SEMANTIC: "priority_semantic",
    QueryMode.RESEARCH: "priority_research",
    QueryMode.NEWS: "priority_realtime",
}


@dataclass
class QueryPlannerResult:
    query: str
    query_mode: QueryMode
    results: list[Any]
    provider_used: str | None = None
    error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class QueryPlan:
    query: str
    query_mode: QueryMode


@dataclass
class QueryPlannerEvidence:
    url: str
    title: str
    description: str
    final_score: float
    evidence_level: Any
    relevance_score: float
    authority_score: float
    freshness_score: float
    provider_trust: float
    content_depth_score: float
    age_days: int | None = None


@dataclass
class QueryPlanExecutionResult:
    plan: QueryPlan
    results: list[QueryPlannerEvidence]
    provider_used: str | None
    latency_ms: float
    status_code: int
    error: str | None = None

    @property
    def is_success(self) -> bool:
        return self.status_code == 200 and self.error is None and bool(self.results)


class QueryPlanner:
    __slots__ = ("_registry",)

    def __init__(self, registry: ProviderRegistry | None = None) -> None:
        self._registry = registry if registry is not None else get_registry()

    async def search(
        self,
        query: str,
        query_mode: QueryMode = QueryMode.REALTIME,
        limit: int = 10,
    ) -> QueryPlannerResult:
        return await self._search_impl(query, query_mode, limit)

    async def plan_and_execute(
        self,
        query: str,
        mode: QueryMode | str | None = None,
        top_k: int = 10,
    ) -> QueryPlanExecutionResult:
        """
        Compatibility API used by RealityAcquisitionHandler.

        The newer planner internally returns normalized dictionaries; the runtime
        handler expects object-style result items and execution metadata.
        """
        start = time.perf_counter()
        query_mode = self._resolve_query_mode(query, mode)
        result = await self.search(query=query, query_mode=query_mode, limit=top_k)
        latency_ms = (time.perf_counter() - start) * 1000
        status_code = 500 if result.error else 200
        evidence = [self._dict_to_evidence(item) for item in result.results]
        return QueryPlanExecutionResult(
            plan=QueryPlan(query=query, query_mode=query_mode),
            results=evidence,
            provider_used=result.provider_used,
            latency_ms=latency_ms,
            status_code=status_code,
            error=result.error,
        )

    async def _search_impl(
        self, query: str, query_mode: QueryMode, limit: int
    ) -> QueryPlannerResult:
        if query_mode == QueryMode.DEEP_PAGE:
            return await self._handle_deep_page(query, limit)
        selected = self._select_providers(query, query_mode)
        if not selected:
            return QueryPlannerResult(
                query=query,
                query_mode=query_mode,
                results=[],
                provider_used=None,
                error="No live providers available for selected mode.",
            )
        provider = selected[0]
        try:
            async with httpx.AsyncClient(timeout=provider.timeout_secs) as client:
                results = await self._call_provider(client, provider, query, query_mode, limit)
                normalized = self._normalize_results(results, provider.provider_type.value)
                return QueryPlannerResult(
                    query=query,
                    query_mode=query_mode,
                    results=normalized,
                    provider_used=provider.name,
                )
        except Exception as e:
            logger.error(f"Provider {provider.name} failed: {e}")
            return QueryPlannerResult(
                query=query,
                query_mode=query_mode,
                results=[],
                provider_used=provider.name,
                error=str(e),
            )

    async def _handle_deep_page(self, url: str, limit: int) -> QueryPlannerResult:
        from .firecrawl_provider import FirecrawlProvider

        fp = FirecrawlProvider()
        try:
            result = await fp.scrape_url(url)
            return QueryPlannerResult(
                query=url,
                query_mode=QueryMode.DEEP_PAGE,
                results=[result] if result else [],
                provider_used="firecrawl",
            )
        except Exception as e:
            return QueryPlannerResult(
                query=url,
                query_mode=QueryMode.DEEP_PAGE,
                results=[],
                provider_used="firecrawl",
                error=str(e),
            )

    async def _call_provider(
        self,
        client: httpx.AsyncClient,
        provider: Any,
        query: str,
        query_mode: QueryMode,
        limit: int,
    ) -> list[dict[str, Any]]:
        ptype = provider.provider_type
        if ptype == ProviderType.BRAVE:
            return await self._brave_search(client, query, limit)
        elif ptype == ProviderType.EXA:
            return await self._exa_search(client, query, limit)
        elif ptype == ProviderType.TAVILY:
            return await self._tavily_search(client, query, limit)
        elif ptype == ProviderType.FIRECRAWL:
            return await self._firecrawl_search(client, query, limit)
        elif ptype == ProviderType.JINA:
            return await self._jina_search(client, query, limit)
        elif ptype == ProviderType.MEYHEM:
            return await self._meyhem_search(client, query, limit)
        return []

    async def _brave_search(
        self, client: httpx.AsyncClient, query: str, limit: int
    ) -> list[dict[str, Any]]:
        api_key = os.getenv("BRAVE_API_KEY", "")
        headers = {"X-Subscription-Token": api_key, "Accept": "application/json"}
        params = {"q": query, "count": min(limit, 20), "safesearch": "moderate"}
        try:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            web = data.get("web", {})
            results = web.get("results", [])
            return [
                {
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "description": r.get("description", ""),
                    "score": r.get("score", 0.0),
                }
                for r in results[:limit]
            ]
        except Exception:
            return []

    async def _exa_search(
        self, client: httpx.AsyncClient, query: str, limit: int
    ) -> list[dict[str, Any]]:
        api_key = os.getenv("EXA_API_KEY", "")
        headers = {"x-api-key": api_key, "Content-Type": "application/json"}
        try:
            resp = await client.post(
                "https://api.exa.ai/search",
                headers=headers,
                json={"query": query, "numResults": limit},
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return [
                {
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "description": r.get("snippet", ""),
                    "score": r.get("score", 0.0),
                }
                for r in data.get("results", [])[:limit]
            ]
        except Exception:
            return []

    async def _tavily_search(
        self, client: httpx.AsyncClient, query: str, limit: int
    ) -> list[dict[str, Any]]:
        api_key = os.getenv("TAVILY_API_KEY", "")
        try:
            resp = await client.post(
                "https://api.tavily.com/search",
                headers={"Content-Type": "application/json"},
                json={"api_key": api_key, "query": query, "max_results": limit},
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return [
                {
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "description": r.get("content", ""),
                    "score": r.get("score", 0.0),
                }
                for r in data.get("results", [])[:limit]
            ]
        except Exception:
            return []

    async def _firecrawl_search(
        self, client: httpx.AsyncClient, query: str, limit: int
    ) -> list[dict[str, Any]]:
        api_key = os.getenv("FIRECRAWL_API_KEY", "")
        try:
            resp = await client.post(
                "https://api.firecrawl.dev/v1/search",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"query": query, "limit": limit},
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return [
                {
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "description": r.get("description", ""),
                    "score": 0.5,
                }
                for r in data.get("data", [])[:limit]
            ]
        except Exception:
            return []

    async def _jina_search(
        self, client: httpx.AsyncClient, query: str, limit: int
    ) -> list[dict[str, Any]]:
        api_key = os.getenv("JINA_API_KEY", "")
        try:
            resp = await client.get(
                "https://api.jina.ai/search",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"q": query, "limit": limit},
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            return [
                {
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "description": r.get("description", ""),
                    "score": 0.5,
                }
                for r in data.get("data", [])[:limit]
            ]
        except Exception:
            return []

    async def _meyhem_search(
        self, client: httpx.AsyncClient, query: str, limit: int
    ) -> list[dict[str, Any]]:
        """Search via Meyhem (api.rhdxm.com) — outcome-ranked, no API key required."""
        try:
            resp = await client.post(
                "https://api.rhdxm.com/search",
                json={
                    "query": query,
                    "max_results": min(limit, 10),
                    "agent_id": "arifOS-queryplanner",
                    "freshness": "hour",
                },
                headers={"Content-Type": "application/json"},
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            results = data.get("results", []) if isinstance(data, dict) else []
            return [
                {
                    "url": r.get("url", ""),
                    "title": r.get("title", "") or r.get("url", ""),
                    "description": r.get("description", "") or r.get("snippet", ""),
                    "score": r.get("score", 0.5),
                }
                for r in results[:limit]
            ]
        except Exception:
            return []

    def _normalize_results(
        self, raw_results: list[dict[str, Any]], provider: str
    ) -> list[dict[str, Any]]:
        from .result_normalizer import ResultNormalizer

        normalizer = ResultNormalizer()
        normalized = []
        for r in raw_results:
            nr = normalizer.normalize(r, provider)
            normalized.append(nr.to_dict())
        return normalized

    def _resolve_query_mode(self, query: str, mode: QueryMode | str | None) -> QueryMode:
        if isinstance(mode, QueryMode):
            query_mode = mode
        elif isinstance(mode, str):
            query_mode = QueryMode(mode)
        else:
            query_mode = self._classify_query(query)

        # CODE is a classification signal, not currently a provider-supported mode.
        if query_mode == QueryMode.CODE:
            return QueryMode.REALTIME
        return query_mode

    def _dict_to_evidence(self, item: Any) -> QueryPlannerEvidence:
        if not isinstance(item, dict):
            return item

        from .result_normalizer import EvidenceLevel

        evidence_value = item.get("evidence_level", EvidenceLevel.L0.value)
        try:
            evidence_level = EvidenceLevel(evidence_value)
        except ValueError:
            evidence_level = EvidenceLevel.L0

        return QueryPlannerEvidence(
            url=item.get("url", ""),
            title=item.get("title", ""),
            description=item.get("snippet", item.get("description", "")),
            final_score=float(item.get("final_score", item.get("score", 0.0)) or 0.0),
            evidence_level=evidence_level,
            relevance_score=float(item.get("relevance", 0.0) or 0.0),
            authority_score=float(item.get("authority", 0.0) or 0.0),
            freshness_score=float(item.get("freshness", 0.0) or 0.0),
            provider_trust=float(item.get("provider_trust", 0.0) or 0.0),
            content_depth_score=float(item.get("content_depth", 0.0) or 0.0),
            age_days=item.get("age_days"),
        )

    def _select_providers(self, query: str, query_mode: QueryMode) -> list[Any]:
        classification = self._classify_query(query)
        live = self._registry.get_live()
        if not live:
            return []
        scored = []
        for p in live:
            if query_mode not in p.supported_modes and query_mode != QueryMode.DEEP_PAGE:
                continue
            attr = _MODE_PRIORITY_ATTR.get(query_mode, "priority_realtime")
            score = getattr(p, attr)
            if classification == QueryMode.CODE and p.provider_type == ProviderType.BRAVE:
                score += 5
            scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:2]]

    def _classify_query(self, query: str) -> QueryMode:
        q = query.strip()
        if q.lower().startswith("http://") or q.lower().startswith("https://"):
            return QueryMode.DEEP_PAGE
        code_signals = {
            "function",
            "code",
            "api",
            "error",
            "exception",
            "syntax",
            "github",
            "stackoverflow",
            "repository",
            "commit",
            "pull request",
            "python",
            "javascript",
            "typescript",
            "java",
            "rust",
            "go ",
            " c++",
            "regex",
            "shell",
            "bash",
            "dockerfile",
            "yaml",
            "json parse",
            "import ",
            "module",
            "class ",
            "def ",
            "async ",
            "await ",
            "null",
            "undefined",
            "react",
            "node",
        }
        semantic_signals = {
            "explain",
            "understand",
            "how does",
            "what is",
            "why does",
            "difference between",
            "compare",
            "analysis",
            "history of",
            "tutorial",
            "guide",
            "versus",
            "vs ",
        }
        research_signals = {
            "paper",
            "research",
            "study",
            "arxiv",
            "journal",
            "publication",
            "academic",
            "citation",
            "doi",
            "conference",
            "proceedings",
        }
        q_lower = q.lower()
        if any(signal in q_lower for signal in code_signals):
            return QueryMode.CODE
        if any(signal in q_lower for signal in research_signals):
            return QueryMode.RESEARCH
        if any(signal in q_lower for signal in semantic_signals):
            return QueryMode.SEMANTIC
        return QueryMode.REALTIME

    def route_query(self, query: str) -> QueryMode:
        return self._classify_query(query)


_planner: QueryPlanner | None = None


def get_planner() -> QueryPlanner:
    global _planner
    if _planner is None:
        _planner = QueryPlanner()
    return _planner
