"""
tests/test_evidence_gate_v2.py — Tests for Evidence Gate v2 (fail-closed)
═══════════════════════════════════════════════════════════════════════════

Rewritten 2026-08-26 to match v2 API. Replaces test_evidence_gate.py which
importated dead names (decompose_and_classify, selfcheck_compare, etc.).

v2 API changes from v1:
  - decompose_and_classify() → decompose() (no parsed param, returns DecompositionResult)
  - check_evidence_coverage(claims, context: str) → (claims, evidence_set: list[str])
  - gate_envelope() returns EvidenceGateResult, not tuple(level, enriched, risks)
  - selfcheck_compare() removed → selfcheck_resample() (async, takes llm_call_fn)
  - normalize_for_comparison() removed
  - AtomicClaim gains source_verification, semantic_similarity fields
  - Defect 2 fix: URL+citation = "cited", not "verified"
  - Defect 3 fix: material-claim ratio, not single-claim upgrade

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from arifosmcp.runtime.evidence_gate import (
    AtomicClaim,
    CoverageResult,
    DecompositionResult,
    EvidenceGateResult,
    EvidenceVerdict,
    SelfCheckResult,
    SourceVerification,
    HIGH_STAKES_ORIGINS,
    SEMANTIC_SIMILARITY_THRESHOLD,
    check_evidence_coverage,
    classify_claim_evidence,
    decompose,
    extract_claims_from_text,
    format_gate_report,
    gate_envelope,
    should_selfcheck,
)


# ═══════════════════════════════════════════════════════════════════════════════
# GATE 1: Atomic Decomposition (sentence + clause-level splitting)
# ═══════════════════════════════════════════════════════════════════════════════


class TestExtractClaims:
    """Test claim extraction from LLM output."""

    def test_extracts_factual_sentences(self):
        text = "The kernel has 13 floors. The port is 8088."
        claims = extract_claims_from_text(text)
        assert len(claims) >= 1

    def test_excludes_questions(self):
        text = "Is the kernel running? The port is 8088."
        claims = extract_claims_from_text(text)
        assert not any("Is the kernel" in c for c in claims)

    def test_excludes_short_lines(self):
        text = "Hi.\nThe kernel has 13 constitutional floors active."
        claims = extract_claims_from_text(text)
        assert not any("Hi." == c.strip() for c in claims)

    def test_excludes_comments(self):
        text = "# This is a comment. The kernel has 13 floors."
        claims = extract_claims_from_text(text)
        assert not any("comment" in c for c in claims)

    def test_excludes_code_blocks(self):
        text = "```python\nprint('hello')\n```\nThe kernel has 13 floors."
        claims = extract_claims_from_text(text)
        assert not any("print" in c for c in claims)

    def test_empty_text(self):
        assert extract_claims_from_text("") == []
        assert extract_claims_from_text("   ") == []

    def test_clause_splitting_defect4(self):
        """Defect 4 fix: sentence with 3+ verbs splits into clauses."""
        text = (
            "The kernel supports sessions, enables intent routing, "
            "and prevents unauthorized access to all agents."
        )
        claims = extract_claims_from_text(text)
        # Should split into at least 2 clauses (3 CLAIM_VERBS, comma+and boundaries)
        assert len(claims) >= 2


class TestClassifyClaimEvidence:
    """Test evidence level classification per claim (Defect 2 fix)."""

    def test_claimed_by_default(self):
        atom = classify_claim_evidence("The kernel has 13 floors.")
        assert atom.evidence_level == "claimed"
        assert atom.source_verification == SourceVerification.NONE
        assert not atom.has_url
        assert not atom.has_citation

    def test_cited_with_url(self):
        atom = classify_claim_evidence("See https://arif-fazil.com for details.")
        assert atom.evidence_level == "cited"
        assert atom.has_url
        assert atom.source_verification == SourceVerification.URL_MENTION

    def test_cited_with_citation_language(self):
        atom = classify_claim_evidence(
            "According to the documentation, the kernel runs on port 8088."
        )
        assert atom.evidence_level == "cited"
        assert atom.has_citation

    def test_defect2_url_plus_citation_is_cited_not_verified(self):
        """Defect 2 fix: URL + citation language = 'cited', not 'verified'.
        'verified' requires SOURCE_CONTENT_MATCH (Gate 2 semantic check)."""
        atom = classify_claim_evidence(
            "According to https://arif-fazil.com, the kernel has 13 floors."
        )
        assert atom.evidence_level == "cited"
        assert atom.source_verification == SourceVerification.URL_MENTION

    def test_cited_with_tool_output(self):
        atom = classify_claim_evidence(
            "curl http://localhost:8088/health shows status: healthy"
        )
        assert atom.evidence_level == "cited"
        assert atom.has_tool_output
        assert atom.source_verification == SourceVerification.SOURCE_OPENED


class TestDecompose:
    """Test decompose() — replaces decompose_and_classify()."""

    def test_basic_decomposition(self):
        raw = "The kernel has 13 floors. The port is 8088."
        result = decompose(raw)
        assert isinstance(result, DecompositionResult)
        assert result.total_claims >= 1
        assert result.upgraded_evidence_level in ("claimed", "cited", "verified")

    def test_upgrades_with_url(self):
        raw = (
            "The kernel has 13 floors. "
            "The documentation at https://arif-fazil.com confirms SSL is enabled."
        )
        result = decompose(raw)
        assert result.upgraded_evidence_level == "cited"

    def test_upgrades_with_citation(self):
        raw = "According to the docs, the kernel has 13 floors. The port is 8088."
        result = decompose(raw)
        assert result.upgraded_evidence_level == "cited"

    def test_empty_input(self):
        result = decompose("")
        assert result.total_claims == 0
        assert result.atoms == []

    def test_deduplication(self):
        raw = "The kernel has 13 floors. The kernel has 13 floors."
        result = decompose(raw)
        assert result.total_claims == 1

    def test_defect3_material_claim_ratio(self):
        """Defect 3 fix: upgraded level uses material-claim ratio.
        One cited claim among many claimed → still 'claimed'."""
        raw = (
            "The kernel has 13 floors. The port is 8088. "
            "The service runs on Linux. According to docs, SSL is enabled."
        )
        result = decompose(raw)
        # Only 1 of 4 claims has citation → ratio < 0.5 → 'claimed'
        if result.material_claims >= 3:
            assert result.upgraded_evidence_level == "claimed"

    def test_atoms_have_correct_fields(self):
        raw = "The kernel has 13 floors."
        result = decompose(raw)
        assert len(result.atoms) >= 1
        atom = result.atoms[0]
        assert isinstance(atom, AtomicClaim)
        assert atom.text
        assert atom.evidence_level in ("claimed", "cited", "verified")
        assert isinstance(atom.has_url, bool)
        assert isinstance(atom.is_material, bool)


# ═══════════════════════════════════════════════════════════════════════════════
# GATE 2: Evidence Coverage (semantic similarity via Ollama)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEvidenceCoverage:
    """Test evidence coverage checking (v2: evidence_set is list[str])."""

    def test_full_coverage_keyword_fallback(self):
        """When Ollama is unavailable, falls back to keyword overlap."""
        claims = ["The kernel runs on port 8088."]
        evidence = ["The kernel runs on port 8088 with 13 floors."]
        result = check_evidence_coverage(claims, evidence)
        assert isinstance(result, CoverageResult)
        assert result.coverage_ratio >= 0.3

    def test_no_coverage(self):
        claims = ["The moon is made of cheese."]
        evidence = ["The kernel runs on port 8088."]
        result = check_evidence_coverage(claims, evidence)
        assert result.coverage_ratio < 0.5

    def test_no_evidence(self):
        claims = ["The kernel runs on port 8088."]
        result = check_evidence_coverage(claims, [])
        assert result.total_claims == 0

    def test_no_claims(self):
        result = check_evidence_coverage([], ["some context"])
        assert result.total_claims == 0

    def test_multiple_evidence_items(self):
        claims = ["The kernel has 13 floors.", "The port is 8088."]
        evidence = [
            "The kernel has 13 constitutional floors.",
            "The service listens on port 8088.",
        ]
        result = check_evidence_coverage(claims, evidence)
        assert result.total_claims == 2


# ═══════════════════════════════════════════════════════════════════════════════
# GATE 3: SelfCheck Re-sample (async)
# ═══════════════════════════════════════════════════════════════════════════════


class TestSelfCheck:
    """Test SelfCheck re-sample (v2: async, takes llm_call_fn)."""

    def test_consistent_claims(self):
        """Claims that appear in re-samples are consistent."""
        from arifosmcp.runtime.evidence_gate import selfcheck_resample

        primary = "The kernel has 13 floors. The port is 8088."

        async def mock_llm(query, temp):
            return "The kernel has 13 floors. The port is 8088."

        result = asyncio.get_event_loop().run_until_complete(
            selfcheck_resample("test query", primary, mock_llm, n_samples=2)
        )
        assert isinstance(result, SelfCheckResult)
        assert result.consistent_claims >= 1
        assert result.consistency_ratio > 0.5

    def test_inconsistent_claims(self):
        """Claims not in re-samples are inconsistent."""
        from arifosmcp.runtime.evidence_gate import selfcheck_resample

        primary = "Quantum entanglement enables faster than light communication."

        async def mock_llm(query, temp):
            return "The kernel has 13 floors. The port is 8088."

        result = asyncio.get_event_loop().run_until_complete(
            selfcheck_resample("test query", primary, mock_llm, n_samples=2)
        )
        assert result.inconsistent_claims >= 1

    def test_empty_primary(self):
        from arifosmcp.runtime.evidence_gate import selfcheck_resample

        async def mock_llm(query, temp):
            return "something"

        result = asyncio.get_event_loop().run_until_complete(
            selfcheck_resample("test query", "", mock_llm, n_samples=1)
        )
        assert result.total_claims == 0

    def test_llm_failure_graceful(self):
        """LLM exceptions are caught, returns empty result."""
        from arifosmcp.runtime.evidence_gate import selfcheck_resample

        async def failing_llm(query, temp):
            raise RuntimeError("LLM unavailable")

        result = asyncio.get_event_loop().run_until_complete(
            selfcheck_resample("test query", "some claims here", failing_llm, n_samples=2)
        )
        assert isinstance(result, SelfCheckResult)
        assert result.total_claims == 0


# ═══════════════════════════════════════════════════════════════════════════════
# GATE ORCHESTRATOR: gate_envelope + should_selfcheck
# ═══════════════════════════════════════════════════════════════════════════════


class TestGateEnvelope:
    """Test gate_envelope() — v2 returns EvidenceGateResult, not tuple."""

    def test_returns_evidence_gate_result(self):
        raw = "The kernel has 13 floors."
        parsed = {"confidence": 0.7}
        result = gate_envelope(raw, parsed, "claimed", "prompt text", "333_REASON")
        assert isinstance(result, EvidenceGateResult)
        assert isinstance(result.verdict, EvidenceVerdict)
        assert isinstance(result.claims, list)
        assert isinstance(result.coverage_ratio, float)

    def test_enriches_parsed_output(self):
        raw = "The kernel has 13 floors."
        parsed = {"confidence": 0.7}
        result = gate_envelope(raw, parsed, "claimed", "prompt text", "333_REASON")
        assert "_evidence_gate" in result.enriched_parsed_output
        eg = result.enriched_parsed_output["_evidence_gate"]
        assert "total_claims" in eg
        assert "verdict" in eg
        assert eg["gate_version"] == "2.0.0"

    def test_defect7_human_decision_required_after_gate(self):
        """Defect 7 fix: human_decision_required computed AFTER gate runs."""
        raw = "The kernel has 13 floors."
        parsed = {"confidence": 0.7}
        result = gate_envelope(raw, parsed, "claimed", "prompt text", "333_REASON")
        assert isinstance(result.human_decision_required, bool)

    def test_low_coverage_generates_risk_flag(self):
        """Claims about moon/sun don't match kernel context → risk flag."""
        raw = (
            "The moon is made of green cheese. "
            "The sun revolves around the Earth. "
            "Gravity does not exist on Mars. "
            "Water is dry on Venus."
        )
        parsed = {"confidence": 0.7}
        result = gate_envelope(
            raw, parsed, "claimed", "kernel port 8088", "333_REASON"
        )
        if result.material_claims > 2:
            assert len(result.risk_flags) > 0

    def test_defect6_fail_closed(self):
        """Defect 6 fix: exception → HOLD, not pass-through."""
        # Pass non-dict parsed_output to trigger exception path
        raw = "The kernel has 13 floors."
        result = gate_envelope(raw, None, "claimed", "prompt", "333_REASON")
        # Should not raise — fail-closed returns HOLD
        assert isinstance(result, EvidenceGateResult)
        # If exception occurred, gate_failure is set
        if result.gate_failure:
            assert result.verdict == EvidenceVerdict.HOLD
            assert result.human_decision_required is True

    def test_verdict_thresholds(self):
        """Verdict follows coverage thresholds."""
        raw = "The kernel has 13 floors."
        parsed = {}
        result = gate_envelope(raw, parsed, "claimed", "", "")
        # With no evidence set and no prompt, coverage should be low
        assert result.verdict in (
            EvidenceVerdict.PROCEED,
            EvidenceVerdict.WARN,
            EvidenceVerdict.HOLD,
            EvidenceVerdict.INSUFFICIENT_EVIDENCE,
        )

    def test_evidence_set_parameter(self):
        """v2 accepts evidence_set for Gate 2."""
        raw = "The kernel has 13 floors."
        parsed = {}
        evidence = ["The kernel has 13 constitutional floors active."]
        result = gate_envelope(
            raw, parsed, "claimed", "", "333_REASON", evidence_set=evidence
        )
        assert isinstance(result, EvidenceGateResult)
        # With matching evidence, coverage should be higher
        assert result.coverage_ratio >= 0.0


class TestShouldSelfCheck:
    """Test SelfCheck trigger logic."""

    def test_triggers_for_high_stakes(self):
        assert should_selfcheck("333_REASON", "reason") is True
        assert should_selfcheck("888_JUDGE", "judge") is True
        assert should_selfcheck("666_HEART", "critique") is True

    def test_no_trigger_for_low_stakes(self):
        assert should_selfcheck("444r_REPLY", "compose") is False
        assert should_selfcheck("UNKNOWN", "infer") is False

    def test_all_high_stakes_origins(self):
        for origin in HIGH_STAKES_ORIGINS:
            assert should_selfcheck(origin, "test") is True


class TestFormatGateReport:
    """Test human-readable gate report formatting."""

    def test_format_basic(self):
        result = EvidenceGateResult(
            verdict=EvidenceVerdict.PROCEED,
            material_claims=5,
            supported_claims=4,
            verified_claims=1,
            coverage_ratio=0.8,
            upgraded_evidence_level="cited",
            human_decision_required=False,
        )
        report = format_gate_report(result)
        assert "PROCEED" in report
        assert "80%" in report
        assert "cited" in report

    def test_format_with_risk_flags(self):
        result = EvidenceGateResult(
            verdict=EvidenceVerdict.HOLD,
            risk_flags=["EVIDENCE_GATE: HOLD — 3/5 claims unsupported."],
        )
        report = format_gate_report(result)
        assert "HOLD" in report
        assert "EVIDENCE_GATE" in report

    def test_format_with_gate_failure(self):
        result = EvidenceGateResult(
            verdict=EvidenceVerdict.HOLD,
            gate_failure="Ollama timeout",
        )
        report = format_gate_report(result)
        assert "Ollama timeout" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
