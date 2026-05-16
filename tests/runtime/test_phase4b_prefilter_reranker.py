# arifOS SENSE Pipeline — Phase 4B Prefilter + Reranker Tests
# DITEMPA BUKAN DIBERI

from __future__ import annotations


from arifosmcp.runtime.result_normalizer import NormalizedResult
from arifosmcp.runtime.candidate_prefilter import (
    CandidatePrefilter,
)
from arifosmcp.runtime.evidence_reranker import (
    EvidenceReranker,
    _extract_keywords,
    _compute_keyword_score,
)


def _make_result(
    url="https://python.dev/test",
    title="Test Title Here",
    snippet="This is a test snippet for testing purposes",
    score=0.5,
    domain="python.dev",
    **kwargs,
):
    return NormalizedResult(
        url=url,
        title=title,
        snippet=snippet,
        source="test",
        score=score,
        domain=domain,
        provider_type="test",
        **kwargs,
    )


class TestCandidatePrefilter:
    def test_passes_valid_result(self):
        r = _make_result()
        pf = CandidatePrefilter()
        result = pf.filter(r)
        assert result.passed

    def test_fails_url_too_long(self):
        r = _make_result(url="https://python.dev/" + "a" * 3000)
        pf = CandidatePrefilter()
        result = pf.filter(r)
        assert not result.passed
        assert "url_too_long" in result.failed_stages

    def test_fails_domain_blocked(self):
        r = _make_result(url="https://facebook.com/test", domain="facebook.com")
        pf = CandidatePrefilter()
        result = pf.filter(r)
        assert not result.passed
        assert "domain_blocked" in result.failed_stages

    def test_fails_title_too_short(self):
        r = _make_result(title="Short")
        pf = CandidatePrefilter()
        result = pf.filter(r)
        assert not result.passed
        assert "title_too_short" in result.failed_stages

    def test_fails_snippet_too_short(self):
        r = _make_result(snippet="Too short")
        pf = CandidatePrefilter()
        result = pf.filter(r)
        assert not result.passed
        assert "snippet_too_short" in result.failed_stages

    def test_fails_score_below_minimum(self):
        r = _make_result(score=0.01)
        r.relevance = 0.01
        r.authority = 0.01
        r.freshness = 0.01
        r.provider_trust = 0.01
        r.content_depth = 0.01
        pf = CandidatePrefilter()
        result = pf.filter(r)
        assert not result.passed
        assert "score_below_minimum" in result.failed_stages

    def test_batch_filter(self):
        r1 = _make_result()
        r2 = _make_result(url="https://facebook.com/test", domain="facebook.com")
        pf = CandidatePrefilter()
        passed = pf.filter_batch([r1, r2])
        assert len(passed) == 1
        assert passed[0].url == r1.url

    def test_url_without_http_fails(self):
        r = _make_result(url="not-a-url")
        pf = CandidatePrefilter()
        result = pf.filter(r)
        assert not result.passed
        assert "url_invalid" in result.failed_stages


class TestEvidenceReranker:
    def test_extract_keywords(self):
        keywords = _extract_keywords("python function parse json")
        assert "python" in keywords
        assert "function" in keywords
        assert "parse" in keywords
        assert "json" in keywords

    def test_extract_keywords_removes_stopwords(self):
        keywords = _extract_keywords("the python tutorial")
        assert "the" not in keywords
        assert "python" in keywords

    def test_compute_keyword_score(self):
        r = _make_result(
            title="Python Function Tutorial",
            snippet="Learn how to parse JSON with Python",
        )
        score = _compute_keyword_score(r, {"python", "parse", "json"})
        assert 0.0 <= score <= 1.0

    def test_compute_keyword_score_empty_keywords(self):
        r = _make_result()
        score = _compute_keyword_score(r, set())
        assert score == 0.5

    def test_rerank_no_duplicates(self):
        r1 = _make_result(url="https://python.dev/1", score=0.9)
        r2 = _make_result(url="https://python.dev/2", score=0.7)
        reranker = EvidenceReranker(stage1_only=True)
        result = reranker.rerank([r1, r2], "python tutorial")
        urls = [r.url for r in result.reranked]
        assert len(urls) == len(set(urls))

    def test_rerank_respects_top_k(self):
        results = [_make_result(url=f"https://python.dev/{i}", score=0.1 * i) for i in range(10)]
        reranker = EvidenceReranker(stage1_only=True)
        result = reranker.rerank(results, "python", top_k=3)
        assert len(result.reranked) == 3

    def test_rerank_stage1_only_by_default(self):
        reranker = EvidenceReranker()
        assert reranker._stage1_only is False

    def test_rerank_stage1_scores_returned(self):
        r1 = _make_result(title="Python Tutorial")
        r2 = _make_result(title="JavaScript Tutorial")
        reranker = EvidenceReranker(stage1_only=True)
        result = reranker.rerank([r1, r2], "python")
        assert r1.url in result.stage1_scores
        assert result.stage2_applied is False
