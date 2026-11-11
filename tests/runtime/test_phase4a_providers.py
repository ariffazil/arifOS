# arifOS SENSE Pipeline — Phase 4A Provider Tests
# DITEMPA BUKAN DIBERI

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from arifosmcp.runtime.provider_registry import (
    ProviderRegistry,
    ProviderType,
    QueryMode,
    PROVIDER_CONFIGS,
)
from arifosmcp.runtime.result_normalizer import EvidenceLevel, NormalizedResult, ResultNormalizer


class TestT1ProviderRegistry:
    def test_registry_singleton_init(self, monkeypatch):
        monkeypatch.setenv("BRAVE_API_KEY", "")
        monkeypatch.setenv("EXA_API_KEY", "")
        monkeypatch.setenv("TAVILY_API_KEY", "")
        monkeypatch.setenv("FIRECRAWL_API_KEY", "")
        monkeypatch.setenv("JINA_API_KEY", "")
        reg = ProviderRegistry()
        assert reg.get(ProviderType.BRAVE) is not None
        assert reg.get(ProviderType.EXA) is not None

    def test_brave_resolves_live_with_key(self, monkeypatch):
        monkeypatch.setenv("BRAVE_API_KEY", "BSABWbaBI-sVc-i-2iCya6AcHjLQflt")
        monkeypatch.setenv("EXA_API_KEY", "")
        monkeypatch.setenv("TAVILY_API_KEY", "")
        monkeypatch.setenv("FIRECRAWL_API_KEY", "")
        monkeypatch.setenv("JINA_API_KEY", "")
        reg = ProviderRegistry()
        brave = reg.get(ProviderType.BRAVE)
        assert brave is not None
        assert brave.is_live

    def test_exa_resolves_live_with_key(self, monkeypatch):
        monkeypatch.setenv("BRAVE_API_KEY", "")
        monkeypatch.setenv("EXA_API_KEY", "00d2913e-d490-41c4-a70c-1e45accfff21")
        monkeypatch.setenv("TAVILY_API_KEY", "")
        monkeypatch.setenv("FIRECRAWL_API_KEY", "")
        monkeypatch.setenv("JINA_API_KEY", "")
        reg = ProviderRegistry()
        exa = reg.get(ProviderType.EXA)
        assert exa is not None
        assert exa.is_live

    def test_all_providers_in_configs(self):
        assert ProviderType.BRAVE in PROVIDER_CONFIGS
        assert ProviderType.EXA in PROVIDER_CONFIGS
        assert ProviderType.TAVILY in PROVIDER_CONFIGS
        assert ProviderType.FIRECRAWL in PROVIDER_CONFIGS
        assert ProviderType.JINA in PROVIDER_CONFIGS


class TestT2ProviderConfig:
    def test_brave_config_values(self, monkeypatch):
        monkeypatch.setenv("BRAVE_API_KEY", "BSABWbaBI-sVc-i-2iCya6AcHjLQflt")
        reg = ProviderRegistry()
        brave = reg.get(ProviderType.BRAVE)
        assert brave is not None
        assert brave.monthly_quota == 20_000_000
        assert brave.rate_limit_rpm == 20 * 60
        assert brave.is_default

    def test_api_key_property(self, monkeypatch):
        monkeypatch.setenv("BRAVE_API_KEY", "BSABWbaBI-sVc-i-2iCya6AcHjLQflt")
        reg = ProviderRegistry()
        brave = reg.get(ProviderType.BRAVE)
        assert brave is not None
        assert brave.api_key == "BSABWbaBI-sVc-i-2iCya6AcHjLQflt"

    def test_capabilities_returns_dict(self, monkeypatch):
        monkeypatch.setenv("BRAVE_API_KEY", "BSABWbaBI-sVc-i-2iCya6AcHjLQflt")
        reg = ProviderRegistry()
        brave = reg.get(ProviderType.BRAVE)
        caps = brave.capabilities()
        assert isinstance(caps, dict)
        assert caps["provider"] == "brave"
        assert "realtime" in caps["supported_modes"]


class TestT3QueryPlannerClassification:
    def test_realtime_query(self):
        from arifosmcp.runtime.query_planner import QueryPlanner

        planner = QueryPlanner()
        assert planner._classify_query("weather today") == QueryMode.REALTIME

    def test_semantic_query(self):
        from arifosmcp.runtime.query_planner import QueryPlanner

        planner = QueryPlanner()
        assert (
            planner._classify_query("how does blockchain achieve consensus") == QueryMode.SEMANTIC
        )

    def test_research_query(self):
        from arifosmcp.runtime.query_planner import QueryPlanner

        planner = QueryPlanner()
        assert planner._classify_query("arxiv paper on transformers") == QueryMode.RESEARCH

    def test_code_query(self):
        from arifosmcp.runtime.query_planner import QueryPlanner

        planner = QueryPlanner()
        assert planner._classify_query("python function to parse json") == QueryMode.CODE

    def test_url_query_is_deep_page(self):
        from arifosmcp.runtime.query_planner import QueryPlanner

        planner = QueryPlanner()
        assert planner._classify_query("https://python.dev/article/test") == QueryMode.DEEP_PAGE

    def test_http_query_is_deep_page(self):
        from arifosmcp.runtime.query_planner import QueryPlanner

        planner = QueryPlanner()
        assert planner._classify_query("http://python.dev/test") == QueryMode.DEEP_PAGE

    def test_github_query_classifies_code(self):
        from arifosmcp.runtime.query_planner import QueryPlanner

        planner = QueryPlanner()
        assert planner._classify_query("github api error 403") == QueryMode.CODE

    def test_research_signal_arxiv(self):
        from arifosmcp.runtime.query_planner import QueryPlanner

        planner = QueryPlanner()
        assert planner._classify_query("paper on attention mechanism") == QueryMode.RESEARCH


class TestT4QueryPlannerRouting:
    def test_provider_priority_realtime(self, monkeypatch):
        monkeypatch.setenv("BRAVE_API_KEY", "BSABWbaBI-sVc-i-2iCya6AcHjLQflt")
        monkeypatch.setenv("EXA_API_KEY", "00d2913e-d490-41c4-a70c-1e45accfff21")
        monkeypatch.setenv("TAVILY_API_KEY", "")
        monkeypatch.setenv("FIRECRAWL_API_KEY", "")
        monkeypatch.setenv("JINA_API_KEY", "")
        from arifosmcp.runtime.query_planner import QueryPlanner

        planner = QueryPlanner()
        providers = planner._select_providers("python tutorial", QueryMode.REALTIME)
        assert len(providers) >= 1
        assert providers[0].provider_type == ProviderType.BRAVE

    def test_semantic_routes_to_exa(self, monkeypatch):
        monkeypatch.setenv("BRAVE_API_KEY", "BSABWbaBI-sVc-i-2iCya6AcHjLQflt")
        monkeypatch.setenv("EXA_API_KEY", "00d2913e-d490-41c4-a70c-1e45accfff21")
        monkeypatch.setenv("TAVILY_API_KEY", "")
        monkeypatch.setenv("FIRECRAWL_API_KEY", "")
        monkeypatch.setenv("JINA_API_KEY", "")
        from arifosmcp.runtime.query_planner import QueryPlanner

        planner = QueryPlanner()
        providers = planner._select_providers("explain quantum computing", QueryMode.SEMANTIC)
        assert len(providers) >= 1
        assert providers[0].provider_type == ProviderType.EXA

    def test_no_live_providers_returns_empty(self, monkeypatch):
        """When no API-key providers are configured, Meyhem fallback is still live."""
        monkeypatch.setenv("BRAVE_API_KEY", "")
        monkeypatch.setenv("EXA_API_KEY", "")
        monkeypatch.setenv("TAVILY_API_KEY", "")
        monkeypatch.setenv("FIRECRAWL_API_KEY", "")
        monkeypatch.setenv("JINA_API_KEY", "")
        from arifosmcp.runtime.query_planner import QueryPlanner

        planner = QueryPlanner()
        providers = planner._select_providers("test", QueryMode.REALTIME)
        # Meyhem requires no API key — always live as fallback
        assert len(providers) >= 1
        assert any(p.provider_type.value == "meyhem" for p in providers)


class TestT5RuntimeCompatibility:
    @pytest.mark.asyncio
    async def test_plan_and_execute_restores_runtime_contract(self, monkeypatch):
        from arifosmcp.runtime.query_planner import QueryPlanner, QueryPlannerResult

        planner = QueryPlanner()

        async def fake_search(self, query, query_mode=QueryMode.REALTIME, limit=10):
            return QueryPlannerResult(
                query=query,
                query_mode=query_mode,
                provider_used="test-provider",
                results=[
                    {
                        "url": "https://example.com/source",
                        "title": "Source",
                        "snippet": "Evidence snippet",
                        "final_score": 0.72,
                        "evidence_level": 3,
                        "relevance": 0.8,
                        "authority": 0.9,
                        "freshness": 0.7,
                        "provider_trust": 0.6,
                        "content_depth": 0.5,
                    }
                ],
            )

        monkeypatch.setattr(QueryPlanner, "search", fake_search)

        result = await planner.plan_and_execute("python api error", mode=None, top_k=5)

        assert result.is_success is True
        assert result.status_code == 200
        assert result.latency_ms >= 0
        assert result.provider_used == "test-provider"
        assert result.plan.query == "python api error"
        assert result.plan.query_mode == QueryMode.REALTIME
        assert result.results[0].url == "https://example.com/source"
        assert result.results[0].description == "Evidence snippet"
        assert result.results[0].evidence_level.value == 3


class TestT6ResultQualitySignals:
    def test_news_domain_only_matches_actual_domain(self):
        normalizer = ResultNormalizer()

        non_news = normalizer.normalize(
            {
                "url": "https://example.com/article",
                "title": "Example",
                "description": "Not a news domain",
            },
            "test",
        )
        news = normalizer.normalize(
            {
                "url": "https://www.reuters.com/world/test",
                "title": "Reuters",
                "description": "News domain",
            },
            "test",
        )

        assert non_news.is_news is False
        assert news.is_news is True

    def test_trusted_fresh_sources_reduce_uncertainty(self):
        from arifosmcp.runtime.context_curator import compute_uncertainty_band

        fresh_trusted = NormalizedResult(
            url="https://nature.com/articles/test",
            title="Fresh trusted source",
            snippet="Evidence",
            source="test",
            published_date=datetime.now(timezone.utc) - timedelta(days=2),
        )
        stale_low_authority = NormalizedResult(
            url="https://example.com/articles/test",
            title="Stale source",
            snippet="Evidence",
            source="test",
            published_date=datetime.now(timezone.utc) - timedelta(days=900),
        )
        fresh_trusted.evidence_level = EvidenceLevel.L3
        stale_low_authority.evidence_level = EvidenceLevel.L3

        trusted_band = compute_uncertainty_band(fresh_trusted)
        stale_band = compute_uncertainty_band(stale_low_authority)

        assert trusted_band.domain_adjustment < 0
        assert trusted_band.freshness_adjustment < 0
        assert trusted_band.base_uncertainty < stale_band.base_uncertainty


class _FirecrawlResp:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


def _firecrawl_client(resp: _FirecrawlResp) -> AsyncMock:
    client = AsyncMock()
    client.post = AsyncMock(return_value=resp)
    client.__aenter__.return_value = client
    client.__aexit__.return_value = False
    return client


class TestFirecrawlV2:
    """Mocked HTTP only. v2 search lives at data.web; failures stay silent."""

    @pytest.mark.asyncio
    async def test_planner_search_posts_v2_and_maps_web(self, monkeypatch):
        monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-key")
        from arifosmcp.runtime.query_planner import QueryPlanner

        resp = _FirecrawlResp(
            200,
            {
                "success": True,
                "data": {
                    "web": [
                        {
                            "url": "https://example.com/a",
                            "title": "Alpha",
                            "description": "First hit",
                        }
                    ],
                    "news": [
                        {
                            "url": "https://news.example/n",
                            "title": "Not requested",
                            "snippet": "ignored",
                        }
                    ],
                },
            },
        )
        client = _firecrawl_client(resp)
        rows = await QueryPlanner()._firecrawl_search(client, "gold price", 5)

        args, kwargs = client.post.call_args
        assert args[0] == "https://api.firecrawl.dev/v2/search"
        assert kwargs["json"] == {"query": "gold price", "limit": 5}
        assert kwargs["headers"]["Authorization"] == "Bearer fc-test-key"
        assert rows == [
            {
                "url": "https://example.com/a",
                "title": "Alpha",
                "description": "First hit",
                "score": 0.5,
            }
        ]

    @pytest.mark.asyncio
    async def test_planner_search_non_200_returns_empty(self, monkeypatch):
        monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-key")
        from arifosmcp.runtime.query_planner import QueryPlanner

        client = _firecrawl_client(_FirecrawlResp(410, {"error": "gone"}))
        rows = await QueryPlanner()._firecrawl_search(client, "gold price", 5)
        assert rows == []

    @pytest.mark.asyncio
    async def test_planner_search_exception_returns_empty(self, monkeypatch):
        monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test-key")
        from arifosmcp.runtime.query_planner import QueryPlanner

        client = AsyncMock()
        client.post = AsyncMock(side_effect=RuntimeError("down"))
        rows = await QueryPlanner()._firecrawl_search(client, "gold price", 5)
        assert rows == []

    @pytest.mark.asyncio
    async def test_provider_search_maps_web_to_normalized_fields(self):
        from arifosmcp.runtime.firecrawl_provider import FirecrawlProvider

        resp = _FirecrawlResp(
            200,
            {
                "success": True,
                "data": {
                    "web": [
                        {
                            "url": "https://example.com/a",
                            "title": "Alpha",
                            "description": "First hit",
                        }
                    ]
                },
            },
        )
        client = _firecrawl_client(resp)
        provider = FirecrawlProvider(api_key="fc-test-key")
        with patch(
            "arifosmcp.runtime.firecrawl_provider.httpx.AsyncClient",
            return_value=client,
        ):
            rows = await provider.search("gold price")

        args, kwargs = client.post.call_args
        assert args[0] == "https://api.firecrawl.dev/v2/search"
        assert kwargs["json"]["limit"] == 5
        assert kwargs["headers"]["Authorization"] == "Bearer fc-test-key"
        assert len(rows) == 1
        assert rows[0].url == "https://example.com/a"
        assert rows[0].title == "Alpha"
        assert rows[0].snippet == "First hit"
        assert rows[0].score == 0.8

    @pytest.mark.asyncio
    async def test_provider_search_non_200_returns_empty(self):
        from arifosmcp.runtime.firecrawl_provider import FirecrawlProvider

        client = _firecrawl_client(_FirecrawlResp(410, {"error": "gone"}))
        provider = FirecrawlProvider(api_key="fc-test-key")
        with patch(
            "arifosmcp.runtime.firecrawl_provider.httpx.AsyncClient",
            return_value=client,
        ):
            assert await provider.search("gold price", limit=3) == []
        assert client.post.call_args.kwargs["json"]["limit"] == 3

    @pytest.mark.asyncio
    async def test_provider_search_exception_returns_empty(self):
        from arifosmcp.runtime.firecrawl_provider import FirecrawlProvider

        client = _firecrawl_client(_FirecrawlResp(200, {}))
        client.post = AsyncMock(side_effect=RuntimeError("down"))
        provider = FirecrawlProvider(api_key="fc-test-key")
        with patch(
            "arifosmcp.runtime.firecrawl_provider.httpx.AsyncClient",
            return_value=client,
        ):
            assert await provider.search("gold price", limit=5) == []

    @pytest.mark.asyncio
    async def test_provider_scrape_reads_v2_markdown(self):
        from arifosmcp.runtime.firecrawl_provider import FirecrawlProvider

        resp = _FirecrawlResp(
            200,
            {
                "success": True,
                "data": {
                    "markdown": "Hello markdown body",
                    "metadata": {
                        "title": "Page",
                        "description": "A desc",
                        "ogUrl": "https://example.com/og",
                    },
                },
            },
        )
        client = _firecrawl_client(resp)
        provider = FirecrawlProvider(api_key="fc-test-key")
        with patch(
            "arifosmcp.runtime.firecrawl_provider.httpx.AsyncClient",
            return_value=client,
        ):
            result = await provider.scrape_url("https://example.com")

        assert client.post.call_args.args[0] == "https://api.firecrawl.dev/v2/scrape"
        assert result is not None
        assert result.url == "https://example.com/og"
        assert result.title == "Page"
        assert result.snippet == "A desc"
        assert result.extra["raw_content"] == "Hello markdown body"
        assert result.score == 0.8

    @pytest.mark.asyncio
    async def test_provider_scrape_non_200_returns_none(self):
        from arifosmcp.runtime.firecrawl_provider import FirecrawlProvider

        client = _firecrawl_client(_FirecrawlResp(410, {"error": "gone"}))
        provider = FirecrawlProvider(api_key="fc-test-key")
        with patch(
            "arifosmcp.runtime.firecrawl_provider.httpx.AsyncClient",
            return_value=client,
        ):
            assert await provider.scrape_url("https://example.com") is None

    @pytest.mark.asyncio
    async def test_provider_scrape_exception_returns_none(self):
        from arifosmcp.runtime.firecrawl_provider import FirecrawlProvider

        client = _firecrawl_client(_FirecrawlResp(200, {}))
        client.post = AsyncMock(side_effect=RuntimeError("down"))
        provider = FirecrawlProvider(api_key="fc-test-key")
        with patch(
            "arifosmcp.runtime.firecrawl_provider.httpx.AsyncClient",
            return_value=client,
        ):
            assert await provider.scrape_url("https://example.com") is None
