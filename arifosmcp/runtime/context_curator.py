# arifOS SENSE Pipeline — Context Curator
# L02 TRUTH + L07 HUMILITY — attribution, uncertainty bands, citation assembly
# DITEMPA BUKAN DIBERI

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .result_normalizer import TRUSTED_DOMAINS, EvidenceLevel, NormalizedResult

TRUSTED_DOMAINS_SET: set[str] = TRUSTED_DOMAINS

# Uncertainty adjustment by evidence level
EVIDENCE_UNCERTAINTY: dict[EvidenceLevel, float] = {
    EvidenceLevel.L0: 0.32,
    EvidenceLevel.L1: 0.26,
    EvidenceLevel.L2: 0.20,
    EvidenceLevel.L3: 0.14,
    EvidenceLevel.L4: 0.08,
    EvidenceLevel.L5: 0.04,
}


@dataclass
class UncertaintyBand:
    level: EvidenceLevel
    base_uncertainty: float
    domain_adjustment: float
    freshness_adjustment: float
    upper: float
    lower: float
    band_width: float
    label: str

    @property
    def display(self) -> str:
        pct = int(self.base_uncertainty * 100)
        return f"{self.label} ±{pct}%"


def _compute_domain_authority(domain: str) -> float:
    d = domain.lower()
    if ".edu" in d:
        return 0.8
    if d in TRUSTED_DOMAINS_SET:
        return 1.0
    if any(c in d for c in [".edu", ".gov", ".org"]):
        return 0.8
    if any(c in d for c in [".io", ".dev", ".ai"]):
        return 0.6
    return 0.4


def _compute_freshness_factor(published_date: datetime | None) -> float:
    if published_date is None:
        return 0.5
    age_days = (datetime.now(UTC) - published_date).days
    if age_days < 30:
        return 1.0
    if age_days < 180:
        return 0.85
    if age_days < 365:
        return 0.7
    if age_days < 730:
        return 0.55
    return 0.4


def _build_attribution(result: NormalizedResult) -> str:
    parts = []
    if result.author:
        parts.append(f"by {result.author}")
    if result.domain:
        parts.append(f"{result.domain}")
    if result.published_date:
        parts.append(result.published_date.strftime("%Y"))
    if not parts:
        parts.append("Unknown")
    return ", ".join(parts)


def compute_uncertainty_band(result: NormalizedResult) -> UncertaintyBand:
    base = EVIDENCE_UNCERTAINTY.get(result.evidence_level, 0.32)
    domain_auth = _compute_domain_authority(result.domain)
    freshness = _compute_freshness_factor(result.published_date)
    domain_adj = -(domain_auth - 0.5) * 0.06
    freshness_adj = -(freshness - 0.5) * 0.04
    adj = min(max(base + domain_adj + freshness_adj, 0.01), 0.99)
    upper = min(adj * 1.5, 0.99)
    lower = max(adj * 0.5, 0.01)
    label_map = {
        EvidenceLevel.L0: "HIGH",
        EvidenceLevel.L1: "MEDIUM-HIGH",
        EvidenceLevel.L2: "MEDIUM",
        EvidenceLevel.L3: "MEDIUM-LOW",
        EvidenceLevel.L4: "LOW",
        EvidenceLevel.L5: "VERY LOW",
    }
    return UncertaintyBand(
        level=result.evidence_level,
        base_uncertainty=round(adj, 4),
        domain_adjustment=round(domain_adj, 4),
        freshness_adjustment=round(freshness_adj, 4),
        upper=round(upper, 4),
        lower=round(lower, 4),
        band_width=round(upper - lower, 4),
        label=label_map.get(result.evidence_level, "HIGH"),
    )


@dataclass
class CitationBlock:
    number: int
    text: str
    url: str
    title: str
    is_trusted: bool
    evidence_level: EvidenceLevel
    attribution: str
    uncertainty: UncertaintyBand


@dataclass
class CuratedOutput:
    curated_results: list[dict[str, Any]]
    citation_blocks: list[CitationBlock]
    overall_uncertainty: float
    attribution_summary: str
    query: str
    result_count: int
    trusted_count: int


def curate(
    results: list[NormalizedResult],
    query: str,
) -> CuratedOutput:
    curated = []
    citations = []
    total_uncertainty = 0.0
    trusted = 0

    for i, r in enumerate(results, 1):
        band = compute_uncertainty_band(r)
        attribution = _build_attribution(r)
        is_trusted = r.is_trusted or r.evidence_level.value >= EvidenceLevel.L3.value

        citation = CitationBlock(
            number=i,
            text=r.snippet[:300],
            url=r.url,
            title=r.title[:80],
            is_trusted=is_trusted,
            evidence_level=r.evidence_level,
            attribution=attribution,
            uncertainty=band,
        )
        citations.append(citation)

        if is_trusted:
            trusted += 1

        curated.append(
            {
                "number": i,
                "title": r.title,
                "snippet": r.snippet[:200],
                "url": r.url,
                "source": r.source,
                "is_trusted": is_trusted,
                "evidence_level": r.evidence_level.value,
                "attribution": attribution,
                "uncertainty_display": band.display,
                "confidence": 1.0 - band.base_uncertainty,
            }
        )
        total_uncertainty += band.base_uncertainty

    avg_uncertainty = total_uncertainty / len(results) if results else 1.0
    attribution_summary = f"{trusted}/{len(results)} sources verified trusted"

    return CuratedOutput(
        curated_results=curated,
        citation_blocks=citations,
        overall_uncertainty=round(avg_uncertainty, 4),
        attribution_summary=attribution_summary,
        query=query,
        result_count=len(results),
        trusted_count=trusted,
    )


def curate_result(result: NormalizedResult, query: str, citation_number: int = 1) -> dict[str, Any]:
    band = compute_uncertainty_band(result)
    attribution = _build_attribution(result)
    is_trusted = result.is_trusted or result.evidence_level.value >= EvidenceLevel.L3.value
    return {
        "number": citation_number,
        "title": result.title,
        "snippet": result.snippet[:200],
        "url": result.url,
        "source": result.source,
        "is_trusted": is_trusted,
        "evidence_level": result.evidence_level.value,
        "attribution": attribution,
        "uncertainty_display": band.display,
        "confidence": round(1.0 - band.base_uncertainty, 4),
    }
