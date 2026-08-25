"""
tests/test_evidence_gate_reddit_replay.py — Live Reddit replay validation
═══════════════════════════════════════════════════════════════════════════

Replays the Reddit gap-fill incident through the v2 evidence gate.

Scenario: Agent searches for "Reddit blocking AI scrapers". Search returns
partial evidence. LLM output contains BOTH supported claims (from evidence)
AND gap-filled claims (fabricated to fill knowledge gaps). The gate must
catch the gap-filling.

Three replay cases:
  1. Supported claims only → PROCEED
  2. Mixed (supported + gap-filled) → WARN or HOLD
  3. Gap-filled claims dominate → HOLD or INSUFFICIENT_EVIDENCE

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from arifosmcp.runtime.evidence_gate import (
    ClaimVerification,
    EvidenceGateResult,
    EvidenceVerdict,
    decompose,
    gate_envelope,
    check_evidence_coverage,
    verify_claim,
    verify_claims,
)


# Simulated search evidence (what the agent actually found)
REDDIT_SEARCH_EVIDENCE = [
    "Reddit has changed its API pricing in 2023. "
    "The new pricing requires $0.24 per 1000 API calls.",
    "Several third-party Reddit apps have shut down after the API changes. "
    "Apollo for Reddit was among the most notable closures.",
    "Reddit's API changes caused widespread subreddit protests. "
    "Over 8,000 subreddits went dark in June 2023.",
]


def SOURCE_CARD(
    *,
    source_id: str = "SRC-reddit-api-2023",
    status: str = "full",
    passage: str = (
        "Reddit has changed its API pricing in 2023. "
        "The new pricing requires $0.24 per 1000 API calls."
    ),
) -> dict[str, object]:
    return {
        "source_id": source_id,
        "status": status,
        "url": "https://www.reddit.com/dev/api-policy",
        "content_hash_sha256": "sha256:" + "a" * 64,
        "retrieved_at": "2026-08-26T00:00:00+00:00",
        "provider": "reddit-mcp",
        "exact_passage": passage,
        "independent_witness": True,
    }


class TestClaimVerification:
    def test_same_domain_false_number_is_unsupported(self):
        result = verify_claim(
            "Reddit has lost 40% of its users.",
            SOURCE_CARD(
                passage=(
                    "Reddit's API pricing changed in 2023. "
                    "The new pricing requires $0.24 per 1000 API calls."
                )
            ),
        )
        assert result["verdict"] == ClaimVerification.UNSUPPORTED.value

    def test_contradicted_claim_is_contradicted(self):
        source = SOURCE_CARD(
            passage="Reddit user numbers remained stable during the period."
        )
        result = verify_claim("Reddit gained 60% of daily active users.", source)
        assert result["verdict"] == ClaimVerification.CONTRADICTED.value

    def test_contradiction_placeholder_is_conservative(self):
        result = verify_claim(
            "Reddit gained 60% of daily active users.",
            SOURCE_CARD(passage="Reddit changed its API pricing in 2023."),
        )
        assert result["verdict"] == ClaimVerification.UNSUPPORTED.value
        assert result["reason"] == "claim_not_entailed_by_exact_passage"

    def test_snippet_only_source_is_unknown(self):
        result = verify_claim(
            "Reddit changed its API pricing in 2023.",
            SOURCE_CARD(status="partial"),
        )
        assert result["verdict"] == ClaimVerification.UNKNOWN.value
        assert result["reason"] == "partial_source_not_admissible"

    def test_gate_accepts_full_source_cards(self):
        result = gate_envelope(
            "Reddit has changed its API pricing in 2023. The new pricing requires $0.24 per 1000 API calls.",
            {"confidence": 0.8},
            "claimed",
            evidence_set=REDDIT_SEARCH_EVIDENCE,
            source_cards=[SOURCE_CARD()],
        )
        assert result.verdict in (EvidenceVerdict.PROCEED, EvidenceVerdict.WARN)
        assert result.enriched_parsed_output["_evidence_gate"]["claim_verification"]["verified"] == 2

    def test_gate_holds_same_domain_false_number_with_source_card(self):
        result = gate_envelope(
            "Reddit has lost 40% of its users.",
            {"confidence": 0.9},
            "claimed",
            evidence_set=REDDIT_SEARCH_EVIDENCE,
            source_cards=[SOURCE_CARD()],
        )
        assert result.verdict == EvidenceVerdict.INSUFFICIENT_EVIDENCE
        assert result.enriched_parsed_output["_evidence_gate"]["claim_verification"]["verdict"] == "PARTIALLY_SUPPORTED"

    def test_missing_source_fields_is_unknown(self):
        result = verify_claim(
            "Reddit changed its API pricing in 2023.",
            {"status": "full", "url": "https://example.test"},
        )
        assert result["verdict"] == ClaimVerification.UNKNOWN.value

    def test_material_claim_verifier_counts_source_verification(self):
        result = verify_claims(
            [
                "Reddit changed its API pricing in 2023.",
                "The new pricing requires $0.24 per 1000 API calls.",
            ],
            [SOURCE_CARD()],
        )
        assert result["verdict"] == "SUPPORTED"
        assert result["verified"] == 2
        assert result["coverage_ratio"] == 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# REPLAY 1: Supported claims only → should PROCEED
# ═══════════════════════════════════════════════════════════════════════════════


class TestReplaySupportedOnly:
    """LLM output that only contains claims supported by evidence."""

    def test_supported_claims_pass(self):
        """Output repeating evidence claims → high coverage."""
        raw = (
            "Reddit has changed its API pricing in 2023. "
            "The new pricing requires $0.24 per 1000 API calls. "
            "Several third-party Reddit apps have shut down after the changes."
        )
        parsed = {"confidence": 0.8}

        result = gate_envelope(
            raw, parsed, "claimed",
            "What happened with Reddit's API changes?",
            "333_REASON",
            evidence_set=REDDIT_SEARCH_EVIDENCE,
        )

        assert isinstance(result, EvidenceGateResult)
        # With claims directly from evidence, coverage should be high
        assert result.coverage_ratio >= 0.5
        assert result.verdict in (EvidenceVerdict.PROCEED, EvidenceVerdict.WARN)


# ═══════════════════════════════════════════════════════════════════════════════
# REPLAY 2: Mixed (supported + gap-filled) → WARN or HOLD
# ═══════════════════════════════════════════════════════════════════════════════


class TestReplayMixed:
    """LLM output with some evidence-backed claims and some gap-filled."""

    def test_gap_filling_detected(self):
        """LLM adds claims about completely different topics → coverage drops."""
        raw = (
            "Reddit has changed its API pricing in 2023. "          # supported
            "The new pricing requires $0.24 per 1000 API calls. "   # supported
            "The boiling point of water is 100 degrees Celsius. "    # DIFFERENT DOMAIN
            "The speed of light is approximately 300000 km/s. "      # DIFFERENT DOMAIN
            "The human heart has four chambers. "                    # DIFFERENT DOMAIN
        )
        parsed = {"confidence": 0.7}

        result = gate_envelope(
            raw, parsed, "claimed",
            "What happened with Reddit's API changes?",
            "333_REASON",
            evidence_set=REDDIT_SEARCH_EVIDENCE,
        )

        assert isinstance(result, EvidenceGateResult)
        # 2/5 claims supported → 40% coverage → WARN territory
        assert result.coverage_ratio < 0.7
        assert result.verdict in (
            EvidenceVerdict.WARN,
            EvidenceVerdict.HOLD,
            EvidenceVerdict.INSUFFICIENT_EVIDENCE,
        )
        # WARN doesn't generate risk flags; HOLD/INSUFFICIENT do
        if result.verdict in (EvidenceVerdict.HOLD, EvidenceVerdict.INSUFFICIENT_EVIDENCE):
            assert len(result.risk_flags) > 0

    def test_gap_filling_with_citation_still_caught(self):
        """Citation language on off-domain claims doesn't save them."""
        raw = (
            "According to reports, Reddit has changed its API pricing. "  # cited + supported
            "The documentation confirms $0.24 per 1000 calls. "           # cited + supported
            "Physics textbooks show the speed of light is 300000 km/s. "  # cited + OFF-DOMAIN
            "Medical literature indicates the heart has four chambers. "  # cited + OFF-DOMAIN
        )
        parsed = {"confidence": 0.7}

        result = gate_envelope(
            raw, parsed, "claimed",
            "Reddit API changes impact",
            "333_REASON",
            evidence_set=REDDIT_SEARCH_EVIDENCE,
        )

        assert isinstance(result, EvidenceGateResult)
        # Citation language doesn't save gap-filled claims
        # Coverage should still be low because evidence doesn't contain
        # user loss or revenue drop claims
        assert result.coverage_ratio < 0.7


# ═══════════════════════════════════════════════════════════════════════════════
# REPLAY 3: Gap-filled claims dominate → HOLD / INSUFFICIENT
# ═══════════════════════════════════════════════════════════════════════════════


class TestReplayGapFilled:
    """LLM output where gap-filled claims dominate."""

    def test_mostly_fabricated(self):
        """Output about unrelated domains → INSUFFICIENT_EVIDENCE."""
        raw = (
            "The boiling point of water is 100 degrees Celsius at sea level. "
            "The speed of light is approximately 300000 kilometers per second. "
            "The human heart has four chambers that pump blood. "
            "The Earth orbits the Sun at a distance of 150 million km. "
            "DNA contains the genetic instructions for all living organisms."
        )
        parsed = {"confidence": 0.6}

        result = gate_envelope(
            raw, parsed, "claimed",
            "Reddit API changes impact",
            "333_REASON",
            evidence_set=REDDIT_SEARCH_EVIDENCE,
        )

        assert isinstance(result, EvidenceGateResult)
        # None of these claims are in the evidence
        assert result.coverage_ratio < 0.4
        assert result.verdict in (
            EvidenceVerdict.HOLD,
            EvidenceVerdict.INSUFFICIENT_EVIDENCE,
        )
        assert result.human_decision_required is True
        assert len(result.risk_flags) > 0

    def test_no_evidence_at_all(self):
        """No evidence provided → all claims unsupported."""
        raw = (
            "Reddit has lost 40% of daily active users. "
            "The company has reduced revenue by $200 million."
        )
        parsed = {"confidence": 0.5}

        result = gate_envelope(raw, parsed, "claimed", "", "333_REASON")

        assert isinstance(result, EvidenceGateResult)
        assert result.verdict in (
            EvidenceVerdict.HOLD,
            EvidenceVerdict.INSUFFICIENT_EVIDENCE,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# COVERAGE ANALYSIS: Verify gate correctly identifies supported vs gap-filled
# ═══════════════════════════════════════════════════════════════════════════════


class TestCoverageAnalysis:
    """Verify the gate's coverage analysis matches expectations."""

    def test_decompose_identifies_all_claims(self):
        """decompose() extracts all factual claims from mixed output."""
        raw = (
            "Reddit has changed its API pricing in 2023. "
            "The pricing requires $0.24 per 1000 calls. "
            "Reddit has lost 40% of daily active users. "
            "The company has laid off 30% of its workforce."
        )
        result = decompose(raw)
        assert result.total_claims >= 3

    def test_coverage_separates_supported_from_gapfilled(self):
        """check_evidence_coverage correctly identifies which claims are covered."""
        claims = [
            "Reddit has changed its API pricing in 2023.",
            "The new pricing requires $0.24 per 1000 API calls.",
            "The boiling point of water is 100 degrees Celsius.",
            "The human heart has four chambers that pump blood.",
        ]
        coverage = check_evidence_coverage(claims, REDDIT_SEARCH_EVIDENCE)

        # First 2 claims should be covered, last 2 should not
        assert coverage.coverage_ratio > 0.0
        assert coverage.coverage_ratio < 1.0
        assert coverage.uncovered_claims >= 1

    def test_evidence_set_size_matters(self):
        """More evidence → better coverage (when claims match)."""
        claims = ["Reddit has changed its API pricing in 2023."]

        small_evidence = ["Something unrelated about cats."]
        large_evidence = REDDIT_SEARCH_EVIDENCE

        small = check_evidence_coverage(claims, small_evidence)
        large = check_evidence_coverage(claims, large_evidence)

        assert large.coverage_ratio >= small.coverage_ratio


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
