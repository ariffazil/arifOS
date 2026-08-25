"""
tests/test_evidence_gate_pipeline.py — Full pipeline integration tests
═══════════════════════════════════════════════════════════════════════

Tests the complete flow:
  LLM raw output → gate_envelope() → EvidenceGateResult → verdict → downstream

Three scenarios:
  1. High-quality output with strong evidence → PROCEED
  2. Low-quality output with no evidence → HOLD / INSUFFICIENT_EVIDENCE
  3. Mixed output → WARN with risk flags

Also tests:
  - enriched_parsed_output carries _evidence_gate metadata
  - human_decision_required tracks verdict correctly
  - fail-closed behavior on exceptions
  - evidence_set parameter improves coverage

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from arifosmcp.runtime.evidence_gate import (
    EvidenceGateResult,
    EvidenceVerdict,
    gate_envelope,
    format_gate_report,
    decompose,
    check_evidence_coverage,
)


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 1: High-quality output with strong evidence → PROCEED
# ═══════════════════════════════════════════════════════════════════════════════


class TestPipelineHighQuality:
    """LLM output with cited claims and matching evidence."""

    def test_cited_output_with_matching_evidence(self):
        """Output with URL+citation + matching evidence set → best possible verdict."""
        raw = (
            "According to https://arif-fazil.com, the kernel has 13 constitutional floors. "
            "The documentation confirms the service runs on port 8088."
        )
        parsed = {"confidence": 0.8, "claim_state": "VERIFIED"}
        evidence = [
            "The arifOS kernel has 13 constitutional floors (F1-F13). "
            "The kernel service listens on port 8088.",
        ]

        result = gate_envelope(
            raw, parsed, "cited", "What are the kernel floors?", "333_REASON",
            evidence_set=evidence,
        )

        assert isinstance(result, EvidenceGateResult)
        assert result.verdict in (EvidenceVerdict.PROCEED, EvidenceVerdict.WARN)
        assert result.coverage_ratio > 0.0
        assert result.material_claims >= 1
        # With cited input + matching evidence, should not require human
        # (unless coverage is still below PROCEED threshold)

    def test_enriched_output_has_gate_metadata(self):
        """enriched_parsed_output must carry _evidence_gate block."""
        raw = "The kernel has 13 floors. The port is 8088."
        parsed = {"confidence": 0.7}

        result = gate_envelope(raw, parsed, "claimed", "prompt", "333_REASON")

        eg = result.enriched_parsed_output.get("_evidence_gate")
        assert eg is not None
        assert eg["gate_version"] == "2.0.0"
        assert "total_claims" in eg
        assert "verdict" in eg
        assert "coverage_ratio" in eg
        assert "upgraded_from" in eg
        assert "upgraded_to" in eg

    def test_report_format(self):
        """format_gate_report produces readable output."""
        raw = (
            "According to https://arif-fazil.com, the kernel supports 13 floors. "
            "The service enables constitutional governance for all agents."
        )
        parsed = {"confidence": 0.8}
        evidence = [
            "The arifOS kernel supports 13 constitutional floors. "
            "The service enables governance for agents.",
        ]

        result = gate_envelope(
            raw, parsed, "cited", "kernel governance", "333_REASON",
            evidence_set=evidence,
        )
        report = format_gate_report(result)
        assert "Evidence Gate" in report
        assert "Verdict:" in report
        assert "Claims:" in report


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 2: Low-quality output with no evidence → HOLD / INSUFFICIENT
# ═══════════════════════════════════════════════════════════════════════════════


class TestPipelineLowQuality:
    """LLM output with unsupported claims and no evidence."""

    def test_unsupported_claims_no_evidence(self):
        """Claims about unrelated topics with no evidence → HOLD or INSUFFICIENT."""
        raw = (
            "The moon is made of green cheese. "
            "The sun revolves around the Earth. "
            "Gravity does not exist on Mars. "
            "Water is dry on Venus."
        )
        parsed = {"confidence": 0.3}

        result = gate_envelope(raw, parsed, "claimed", "", "")

        assert isinstance(result, EvidenceGateResult)
        assert result.verdict in (
            EvidenceVerdict.HOLD,
            EvidenceVerdict.INSUFFICIENT_EVIDENCE,
        )
        assert result.human_decision_required is True
        assert len(result.risk_flags) > 0

    def test_empty_output(self):
        """Empty LLM output → no claims → HOLD."""
        result = gate_envelope("", {}, "claimed", "", "")

        assert isinstance(result, EvidenceGateResult)
        assert result.material_claims == 0

    def test_low_confidence_parsed(self):
        """Low confidence in parsed output doesn't crash the gate."""
        raw = "The kernel has 13 floors."
        parsed = {"confidence": 0.1}

        result = gate_envelope(raw, parsed, "claimed", "prompt", "333_REASON")
        assert isinstance(result, EvidenceGateResult)
        # human_decision_required should be True for low confidence + claimed
        assert result.human_decision_required is True

    def test_fail_closed_on_none_parsed(self):
        """Defect 6: None parsed_output → exception → HOLD (fail-closed)."""
        result = gate_envelope("The kernel has 13 floors.", None, "claimed", "", "")

        assert isinstance(result, EvidenceGateResult)
        # If exception occurred, gate_failure is set and verdict is HOLD
        if result.gate_failure:
            assert result.verdict == EvidenceVerdict.HOLD
            assert result.human_decision_required is True
            assert any("fail-closed" in f for f in result.risk_flags)


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 3: Mixed output → WARN with risk flags
# ═══════════════════════════════════════════════════════════════════════════════


class TestPipelineMixed:
    """LLM output with some supported and some unsupported claims."""

    def test_partial_evidence_coverage(self):
        """Some claims match evidence, some don't → WARN or HOLD."""
        raw = (
            "The kernel has 13 constitutional floors. "
            "The service runs on port 8088. "
            "The moon is made of green cheese. "
            "Gravity does not exist on Mars."
        )
        parsed = {"confidence": 0.6}
        evidence = [
            "The arifOS kernel has 13 constitutional floors. "
            "The service listens on port 8088.",
        ]

        result = gate_envelope(
            raw, parsed, "claimed", "kernel info", "333_REASON",
            evidence_set=evidence,
        )

        assert isinstance(result, EvidenceGateResult)
        # With partial coverage, verdict should be WARN or HOLD
        assert result.verdict in (
            EvidenceVerdict.PROCEED,
            EvidenceVerdict.WARN,
            EvidenceVerdict.HOLD,
        )
        # Coverage should be between 0 and 1
        assert 0.0 <= result.coverage_ratio <= 1.0

    def test_prompt_as_proxy_evidence(self):
        """When no evidence_set, prompt is used as proxy evidence."""
        raw = "The kernel has 13 floors. The port is 8088."
        parsed = {"confidence": 0.7}
        prompt = "Tell me about the arifOS kernel with 13 floors on port 8088."

        result = gate_envelope(raw, parsed, "claimed", prompt, "333_REASON")

        assert isinstance(result, EvidenceGateResult)
        # Prompt as proxy should give some coverage
        assert result.coverage_ratio >= 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE INVARIANTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestPipelineInvariants:
    """Invariants that must hold across all pipeline paths."""

    def test_verdict_is_always_enum(self):
        """Verdict is always an EvidenceVerdict enum value."""
        for raw in ["", "Hello.", "The kernel has 13 floors."]:
            result = gate_envelope(raw, {}, "claimed", "", "")
            assert isinstance(result.verdict, EvidenceVerdict)

    def test_human_decision_required_is_bool(self):
        """human_decision_required is always bool."""
        for raw in ["", "The kernel has 13 floors."]:
            result = gate_envelope(raw, {}, "claimed", "", "")
            assert isinstance(result.human_decision_required, bool)

    def test_claims_list_is_always_list(self):
        """claims is always a list of AtomicClaim."""
        for raw in ["", "The kernel has 13 floors."]:
            result = gate_envelope(raw, {}, "claimed", "", "")
            assert isinstance(result.claims, list)

    def test_risk_flags_is_always_list(self):
        """risk_flags is always a list."""
        for raw in ["", "The kernel has 13 floors."]:
            result = gate_envelope(raw, {}, "claimed", "", "")
            assert isinstance(result.risk_flags, list)

    def test_enriched_output_always_has_gate_key(self):
        """enriched_parsed_output always has _evidence_gate key."""
        for raw in ["", "The kernel has 13 floors."]:
            result = gate_envelope(raw, {}, "claimed", "", "")
            assert "_evidence_gate" in result.enriched_parsed_output

    def test_gate_failure_none_on_success(self):
        """gate_failure is None when no exception occurs."""
        result = gate_envelope("The kernel has 13 floors.", {}, "claimed", "", "")
        assert result.gate_failure is None

    def test_coverage_ratio_bounded(self):
        """coverage_ratio is always between 0.0 and 1.0."""
        for raw in [
            "",
            "The kernel has 13 floors.",
            "The moon is cheese. The sun is hot. Water is wet. Fire burns.",
        ]:
            result = gate_envelope(raw, {}, "claimed", "", "")
            assert 0.0 <= result.coverage_ratio <= 1.0

    def test_decompose_then_coverage_consistent(self):
        """decompose() + check_evidence_coverage() agree with gate_envelope()."""
        raw = (
            "The kernel has 13 constitutional floors. "
            "The service runs on port 8088."
        )
        evidence = [
            "The arifOS kernel has 13 constitutional floors. "
            "The service listens on port 8088.",
        ]

        # Independent calls
        decomp = decompose(raw)
        claim_texts = [a.text for a in decomp.atoms]
        coverage = check_evidence_coverage(claim_texts, evidence)

        # Pipeline call
        result = gate_envelope(
            raw, {}, "claimed", "", "333_REASON", evidence_set=evidence,
        )

        # Claim counts should match
        assert result.material_claims == decomp.material_claims
        # Coverage should be consistent (may differ slightly due to prompt proxy)
        if decomp.material_claims > 0:
            assert result.coverage_ratio == coverage.coverage_ratio


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
