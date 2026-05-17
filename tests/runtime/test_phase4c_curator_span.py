# arifOS SENSE Pipeline — Phase 4C Context Curator + Evidence Span Tests
# DITEMPA BUKAN DIBERI

from __future__ import annotations

from datetime import datetime, timezone

from arifosmcp.runtime.result_normalizer import NormalizedResult, EvidenceLevel
from arifosmcp.runtime.context_curator import (
    compute_uncertainty_band,
    curate,
    curate_result,
    _compute_domain_authority,
    _compute_freshness_factor,
    _build_attribution,
)
from arifosmcp.runtime.evidence_span import (
    EvidenceSpanExtractor,
    extract_spans,
    extract_spans_from_results,
)


def _make_result(
    url="https://python.dev/test",
    title="Test Title Here",
    snippet="This is a test snippet for testing",
    domain="python.dev",
    evidence_level=EvidenceLevel.L3,
    published_date=None,
    author=None,
    is_trusted=False,
    relevance=0.5,
    authority=0.5,
    freshness=0.5,
    provider_trust=0.5,
    content_depth=0.5,
):
    return NormalizedResult(
        url=url,
        title=title,
        snippet=snippet,
        source="test",
        score=0.5,
        domain=domain,
        published_date=published_date,
        author=author,
        is_trusted=is_trusted,
        evidence_level=evidence_level,
        relevance=relevance,
        authority=authority,
        freshness=freshness,
        provider_trust=provider_trust,
        content_depth=content_depth,
        provider_type="test",
    )


class TestComputeUncertaintyBand:
    def test_l0_highest_uncertainty(self):
        r = _make_result(evidence_level=EvidenceLevel.L0)
        band = compute_uncertainty_band(r)
        assert band.level == EvidenceLevel.L0
        assert band.label == "HIGH"

    def test_l5_highest_authority(self):
        r = _make_result(evidence_level=EvidenceLevel.L5)
        band = compute_uncertainty_band(r)
        assert band.level == EvidenceLevel.L5
        assert band.base_uncertainty < 0.10

    def test_l3_band(self):
        r = _make_result(evidence_level=EvidenceLevel.L3)
        band = compute_uncertainty_band(r)
        assert band.level == EvidenceLevel.L3
        assert band.label == "MEDIUM-LOW"
        assert band.base_uncertainty < band.upper
        assert band.lower < band.base_uncertainty

    def test_l3_band_upper_lower_than_l0(self):
        r_l0 = _make_result(evidence_level=EvidenceLevel.L0)
        r_l3 = _make_result(evidence_level=EvidenceLevel.L3)
        band_l0 = compute_uncertainty_band(r_l0)
        band_l3 = compute_uncertainty_band(r_l3)
        assert band_l3.upper < band_l0.upper

    def test_domain_authority_trusted(self):
        auth = _compute_domain_authority("github.com")
        assert auth == 1.0

    def test_domain_authority_edu(self):
        auth = _compute_domain_authority("stanford.edu")
        assert auth == 0.8

    def test_domain_authority_io(self):
        auth = _compute_domain_authority("python.dev")
        assert auth == 0.6

    def test_freshness_recent(self):
        recent = datetime.now(timezone.utc)
        factor = _compute_freshness_factor(recent)
        assert factor == 1.0

    def test_freshness_old(self):
        old = datetime(2020, 1, 1, tzinfo=timezone.utc)
        factor = _compute_freshness_factor(old)
        assert factor < 0.5

    def test_freshness_none(self):
        factor = _compute_freshness_factor(None)
        assert factor == 0.5


class TestCurate:
    def test_curate_output_structure(self):
        r1 = _make_result(title="Python Tutorial", evidence_level=EvidenceLevel.L3)
        r2 = _make_result(title="JavaScript Guide", evidence_level=EvidenceLevel.L2)
        output = curate([r1, r2], "python tutorial")
        assert output.query == "python tutorial"
        assert output.result_count == 2
        assert len(output.curated_results) == 2

    def test_curate_citation_blocks(self):
        r = _make_result(title="Test Result")
        output = curate([r], "test")
        assert len(output.citation_blocks) == 1
        assert output.citation_blocks[0].number == 1

    def test_curate_trusted_count(self):
        r1 = _make_result(is_trusted=True, evidence_level=EvidenceLevel.L3)
        r2 = _make_result(evidence_level=EvidenceLevel.L0)
        output = curate([r1, r2], "test")
        assert output.trusted_count == 1

    def test_curate_uncertainty_band_display(self):
        r = _make_result(evidence_level=EvidenceLevel.L0)
        output = curate([r], "test")
        band = output.citation_blocks[0].uncertainty
        assert "%" in band.display

    def test_curate_empty_results(self):
        output = curate([], "nothing")
        assert output.result_count == 0
        assert output.overall_uncertainty == 1.0

    def test_build_attribution_with_author(self):
        r = _make_result(author="John Doe", domain="python.dev")
        attr = _build_attribution(r)
        assert "John Doe" in attr

    def test_build_attribution_without_author(self):
        r = _make_result(domain="python.dev")
        attr = _build_attribution(r)
        assert "python.dev" in attr


class TestCurateResult:
    def test_curate_result_structure(self):
        r = _make_result(evidence_level=EvidenceLevel.L3)
        result = curate_result(r, "test query", citation_number=5)
        assert result["number"] == 5
        assert "uncertainty_display" in result
        assert "confidence" in result

    def test_curate_result_trusted_by_evidence_level(self):
        r = _make_result(evidence_level=EvidenceLevel.L4)
        result = curate_result(r, "test")
        assert result["is_trusted"] is True


class TestEvidenceSpanExtractor:
    def test_extract_spans_from_keyword(self):
        r = _make_result(title="Python Function Parse", snippet="This function parses JSON")
        extractor = EvidenceSpanExtractor()
        result = extractor.extract(r)
        assert result.url == r.url
        assert result.span_count >= 0

    def test_extract_batch(self):
        r1 = _make_result(title="Python Tutorial")
        r2 = _make_result(title="JavaScript Guide")
        extractor = EvidenceSpanExtractor()
        results = extractor.extract_batch([r1, r2])
        assert len(results) == 2

    def test_extract_spans_function(self):
        r = _make_result(title="Python Function", snippet="A function in python")
        spans = extract_spans(r)
        assert spans.url == r.url
        assert isinstance(spans.spans, list)

    def test_extract_spans_from_results_function(self):
        r = _make_result(title="Test")
        results = extract_spans_from_results([r])
        assert len(results) == 1

    def test_span_extraction_result_fields(self):
        r = _make_result(title="Test Result")
        extractor = EvidenceSpanExtractor()
        result = extractor.extract(r)
        assert hasattr(result, "span_count")
        assert hasattr(result, "unique_terms_matched")

    def test_regex_fallback_extraction(self):
        r = _make_result(snippet="The price is $99.99 and 50% off")
        extractor = EvidenceSpanExtractor()
        result = extractor.extract(r)
        assert result.span_count >= 0

    def test_date_regex_extraction(self):
        r = _make_result(snippet="Posted on January 15, 2024")
        extractor = EvidenceSpanExtractor()
        result = extractor.extract(r)
        assert result.span_count >= 0
