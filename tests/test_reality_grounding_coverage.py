"""
Targeted tests for reality_grounding.py to boost coverage from 25% to 75%
Focus on SearchResult, search functions, and result processing
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import json


class TestSearchResult:
    """Test SearchResult dataclass - lines 81-100"""

    def test_search_result_creation(self):
        """Test SearchResult creation with all fields"""
        from arifosmcp.intelligence.tools.reality_grounding import SearchResult

        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            source="ddgs",
            rank=1,
            uncertainty=0.04,
            timestamp="2026-03-14T10:00:00Z",
        )

        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.uncertainty == 0.04

    def test_search_result_to_dict(self):
        """Test SearchResult.to_dict method"""
        from arifosmcp.intelligence.tools.reality_grounding import SearchResult

        result = SearchResult(
            title="Test", url="https://test.com", snippet="Snippet", source="test", rank=1
        )

        d = result.to_dict()
        assert d["title"] == "Test"
        assert d["url"] == "https://test.com"
        assert "uncertainty_omega" in d

    def test_search_result_defaults(self):
        """Test SearchResult with default values"""
        from arifosmcp.intelligence.tools.reality_grounding import SearchResult, UNCERTAINTY_DDGS

        result = SearchResult(
            title="Test", url="https://test.com", snippet="Snippet", source="ddgs", rank=1
        )

        assert result.uncertainty == UNCERTAINTY_DDGS
        assert result.timestamp is None


class TestGroundingSearch:
    """Test grounding_search function and related search logic"""

    @pytest.mark.asyncio
    async def test_grounding_search_with_results(self):
        """Test grounding search returning results"""
        from arifosmcp.intelligence.tools.reality_grounding import grounding_search

        with patch("arifosmcp.intelligence.tools.reality_grounding._search_ddgs") as mock_ddgs:
            mock_ddgs.return_value = [
                Mock(
                    title="Result 1",
                    url="https://1.com",
                    snippet="Snippet 1",
                    source="ddgs",
                    rank=1,
                    uncertainty=0.04,
                ),
                Mock(
                    title="Result 2",
                    url="https://2.com",
                    snippet="Snippet 2",
                    source="ddgs",
                    rank=2,
                    uncertainty=0.04,
                ),
            ]

            results = await grounding_search("test query")
            assert isinstance(results, list)
            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_grounding_search_empty_results(self):
        """Test grounding search with no results"""
        from arifosmcp.intelligence.tools.reality_grounding import grounding_search

        with patch("arifosmcp.intelligence.tools.reality_grounding._search_ddgs") as mock_ddgs:
            mock_ddgs.return_value = []

            results = await grounding_search("test query")
            assert isinstance(results, list)
            assert len(results) == 0

    @pytest.mark.asyncio
    async def test_grounding_search_fallback_to_playwright(self):
        """Test grounding search falls back to playwright"""
        from arifosmcp.intelligence.tools.reality_grounding import grounding_search

        with patch("arifosmcp.intelligence.tools.reality_grounding._search_ddgs") as mock_ddgs:
            mock_ddgs.return_value = []  # DDGS fails

            with patch(
                "arifosmcp.intelligence.tools.reality_grounding._search_playwright"
            ) as mock_pw:
                mock_pw.return_value = [
                    Mock(
                        title="PW Result",
                        url="https://pw.com",
                        snippet="PW",
                        source="playwright",
                        rank=1,
                    )
                ]

                results = await grounding_search("test query")
                assert len(results) > 0


class TestSearchResultProcessing:
    """Test result processing and filtering"""

    def test_rank_results(self):
        """Test result ranking/sorting"""
        from arifosmcp.intelligence.tools.reality_grounding import SearchResult, _rank_results

        results = [
            SearchResult(title="C", url="https://c.com", snippet="C", source="ddgs", rank=3),
            SearchResult(title="A", url="https://a.com", snippet="A", source="ddgs", rank=1),
            SearchResult(title="B", url="https://b.com", snippet="B", source="ddgs", rank=2),
        ]

        ranked = _rank_results(results)
        assert ranked[0].title == "A"
        assert ranked[1].title == "B"
        assert ranked[2].title == "C"

    def test_dedupe_results(self):
        """Test result deduplication"""
        from arifosmcp.intelligence.tools.reality_grounding import SearchResult, _dedupe_results

        results = [
            SearchResult(title="A", url="https://a.com", snippet="A", source="ddgs", rank=1),
            SearchResult(
                title="A Duplicate", url="https://a.com", snippet="A", source="ddgs", rank=2
            ),
            SearchResult(title="B", url="https://b.com", snippet="B", source="ddgs", rank=3),
        ]

        deduped = _dedupe_results(results)
        assert len(deduped) == 2

    def test_filter_asean_sources(self):
        """Test ASEAN source filtering"""
        from arifosmcp.intelligence.tools.reality_grounding import SearchResult, _filter_asean

        results = [
            SearchResult(title="MY", url="https://test.my", snippet="MY", source="ddgs", rank=1),
            SearchResult(title="SG", url="https://test.sg", snippet="SG", source="ddgs", rank=2),
            SearchResult(title="US", url="https://test.com", snippet="US", source="ddgs", rank=3),
        ]

        asean = _filter_asean(results)
        assert len(asean) == 2
        assert all(".my" in r.url or ".sg" in r.url for r in asean)


class TestThrottlingAndConfig:
    """Test configuration and throttling"""

    def test_default_throttle_constant(self):
        """Test throttle constant exists"""
        from arifosmcp.intelligence.tools.reality_grounding import DEFAULT_THROTTLE_SECONDS

        assert DEFAULT_THROTTLE_SECONDS == 2.0

    def test_asean_sites_constant(self):
        """Test ASEAN sites constant"""
        from arifosmcp.intelligence.tools.reality_grounding import ASEAN_SITES

        assert ".my" in ASEAN_SITES
        assert ".sg" in ASEAN_SITES
        assert ".id" in ASEAN_SITES

    def test_uncertainty_constants(self):
        """Test uncertainty level constants"""
        from arifosmcp.intelligence.tools.reality_grounding import (
            UNCERTAINTY_BRAVE,
            UNCERTAINTY_DDGS,
            UNCERTAINTY_PLAYWRIGHT,
        )

        assert UNCERTAINTY_BRAVE < UNCERTAINTY_DDGS < UNCERTAINTY_PLAYWRIGHT

    def test_brave_api_key_env(self):
        """Test Brave API key env var constant"""
        from arifosmcp.intelligence.tools.reality_grounding import BRAVE_API_KEY_ENV

        assert BRAVE_API_KEY_ENV == "BRAVE_API_KEY"


class TestSearchWithConsensus:
    """Test consensus arbitrator integration"""

    @pytest.mark.asyncio
    async def test_search_with_consensus(self):
        """Test search with consensus checking"""
        from arifosmcp.intelligence.tools.reality_grounding import search_with_consensus

        with patch(
            "arifosmcp.intelligence.tools.reality_grounding.grounding_search"
        ) as mock_search:
            mock_search.return_value = [
                Mock(
                    title="R1",
                    url="https://1.com",
                    snippet="S1",
                    source="ddgs",
                    rank=1,
                    uncertainty=0.04,
                ),
                Mock(
                    title="R2",
                    url="https://2.com",
                    snippet="S2",
                    source="ddgs",
                    rank=2,
                    uncertainty=0.04,
                ),
            ]

            with patch(
                "arifosmcp.intelligence.tools.reality_grounding.ConsensusArbitrator"
            ) as mock_ca:
                mock_instance = Mock()
                mock_instance.arbitrate.return_value = Mock(consensus=0.95, verdict="SUPPORTED")
                mock_ca.return_value = mock_instance

                result = await search_with_consensus("test query")
                assert result is not None


class TestUnifiedToolOutput:
    """Test tool output formatting"""

    def test_unified_output_with_results(self):
        """Test unified output formatting with results"""
        from arifosmcp.intelligence.tools.reality_grounding import (
            SearchResult,
            _format_unified_output,
        )

        results = [
            SearchResult(
                title="Test", url="https://test.com", snippet="Snippet", source="ddgs", rank=1
            )
        ]

        output = _format_unified_output(results, query="test")
        assert "query" in output
        assert "results" in output
        assert output["query"] == "test"

    def test_unified_output_empty(self):
        """Test unified output with no results"""
        from arifosmcp.intelligence.tools.reality_grounding import _format_unified_output

        output = _format_unified_output([], query="test")
        assert output["results"] == []
        assert "uncertainty" in output or "omega" in str(output).lower()


class TestErrorHandling:
    """Test error handling in grounding"""

    @pytest.mark.asyncio
    async def test_grounding_handles_exception(self):
        """Test grounding handles exceptions gracefully"""
        from arifosmcp.intelligence.tools.reality_grounding import grounding_search

        with patch("arifosmcp.intelligence.tools.reality_grounding._search_ddgs") as mock_ddgs:
            mock_ddgs.side_effect = Exception("Network error")

            with patch("arifosmcp.intelligence.tools.reality_grounding.logger") as mock_logger:
                results = await grounding_search("test query")
                # Should return empty list or fallback, not raise
                assert isinstance(results, list)


class TestResultValidation:
    """Test result validation"""

    def test_validate_search_result_valid(self):
        """Test valid result passes validation"""
        from arifosmcp.intelligence.tools.reality_grounding import SearchResult, _validate_result

        result = SearchResult(
            title="Valid", url="https://valid.com", snippet="Valid snippet", source="ddgs", rank=1
        )

        assert _validate_result(result) is True

    def test_validate_search_result_invalid(self):
        """Test invalid result fails validation"""
        from arifosmcp.intelligence.tools.reality_grounding import SearchResult, _validate_result

        result = SearchResult(
            title="",  # Empty title
            url="https://test.com",
            snippet="Snippet",
            source="ddgs",
            rank=1,
        )

        assert _validate_result(result) is False
