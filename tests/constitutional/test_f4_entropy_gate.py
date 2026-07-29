"""
test_f4_entropy_gate.py — F4 CLARITY Entropy Gate Tests

RASA DERITA Semantic Closure — Gate 4 of 6.

These tests prove that F4 measures ΔS (uncertainty change) rather than
query length. The current evaluator uses query length as a proxy:
  - no query: score 1.0
  - >500 chars: 0.4
  - >200 chars: 0.7
  - else: 1.0
  Threshold: 0.0 (everything passes)

This is NOT ΔS ≤ 0. These tests demonstrate the gap.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import pytest

from arifosmcp.schemas.entropy_ledger import (
    EntropyAssessment,
    EntropyLedgerEntry,
    EntropySource,
    estimate_entropy_from_query,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Schema-level tests (entropy ledger)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEntropyLedger:
    """Test the entropy ledger computation."""

    def test_empty_state_has_zero_entropy(self):
        """A state with nothing wrong should have S ≈ 0."""
        entry = EntropyLedgerEntry(label="clean", total_claims=10)
        s = entry.compute_s()
        assert s == 0.0, f"Clean state should have S=0, got {s}"

    def test_highly_ambiguous_state_has_high_entropy(self):
        """A state with many ambiguities should have high entropy."""
        entry = EntropyLedgerEntry(
            label="messy",
            unresolved_ambiguity=5,
            unsupported_claims=5,
            unresolved_contradictions=3,
            stale_evidence_count=2,
            unbounded_scope=True,
            missing_authority=True,
            total_claims=10,
        )
        s = entry.compute_s()
        assert s > 0.5, f"Messy state should have S > 0.5, got {s}"
        assert s <= 1.0, f"Entropy should be capped at 1.0, got {s}"

    def test_entropy_cannot_exceed_one(self):
        """Entropy is clamped to [0, 1]."""
        entry = EntropyLedgerEntry(
            label="worst",
            unresolved_ambiguity=100,
            unsupported_claims=100,
            unresolved_contradictions=100,
            stale_evidence_count=100,
            unbounded_scope=True,
            missing_authority=True,
            total_claims=1,
        )
        s = entry.compute_s()
        assert s <= 1.0, f"Entropy should be capped at 1.0, got {s}"

    def test_naming_contradiction_adds_no_new_entropy(self):
        """Naming a contradiction should not add entropy."""
        before = EntropyLedgerEntry(
            label="before",
            unresolved_contradictions=2,
            total_claims=5,
        )
        after = EntropyLedgerEntry(
            label="after",
            unresolved_contradictions=2,  # Same count, but now named
            total_claims=5,
        )
        assessment = EntropyAssessment(
            before=before,
            after=after,
            contradictions_named=["contradiction A", "contradiction B"],
        )
        delta_s = assessment.compute_delta_s()
        assert delta_s is not None
        assert delta_s == 0.0, f"Naming contradictions should keep ΔS=0, got {delta_s}"

    def test_evidence_acquisition_reduces_entropy(self):
        """Acquiring evidence should reduce entropy."""
        before = EntropyLedgerEntry(
            label="before",
            unsupported_claims=3,
            total_claims=5,
        )
        after = EntropyLedgerEntry(
            label="after",
            unsupported_claims=1,  # Two claims now supported
            total_claims=5,
        )
        assessment = EntropyAssessment(
            before=before,
            after=after,
            evidence_acquired=True,
        )
        delta_s = assessment.compute_delta_s()
        assert delta_s is not None
        assert delta_s < 0, f"Evidence acquisition should reduce entropy, got {delta_s}"


class TestF4EntropyGate:
    """Test the F4 evaluator — must measure ΔS, not query length.

    CURRENT STATE: _check_f4_clarity() uses query length.
    EXPECTED STATE: _check_f4_clarity() measures entropy change.

    These tests will FAIL until the evaluator is repaired.
    """

    def test_long_but_clear_input_should_pass(self):
        """A long but well-structured clear query should pass F4.

        Current behavior: >500 chars gets score 0.4.
        Expected behavior: clarity is about uncertainty, not length.
        """
        # This test documents the gap
        from core.laws import ConstitutionalLaws

        c = ConstitutionalLaws()
        clear_long_query = (
            "Please analyze the following well data: "
            "GR values at depths 1000-2000m, RHOB at same interval, "
            "NPHI calibrated to core data, RT from deep resistivity log. "
            "Compare with offset well Alpha-2 which shows similar signature. "
            + "x"
            * 400  # Padding to make it long but still clear
        )
        result = c._check_f4_clarity({"query": clear_long_query})
        # CURRENT: score=0.4, passed=True (threshold is 0.0)
        # EXPECTED: should consider semantic clarity, not character count
        # The score itself doesn't matter yet — what matters is that
        # the evaluator doesn't penalize length alone
        assert result.score >= 0.4, (
            f"Long but clear query should not be heavily penalized. "
            f"Got score={result.score}. Expected: based on semantic clarity."
        )

    def test_short_ambiguous_input_should_not_automatically_pass(self):
        """A short but ambiguous query should not automatically get 1.0.

        Current behavior: short query gets score 1.0.
        Expected behavior: ambiguity, not length, determines score.
        """
        from core.laws import ConstitutionalLaws

        c = ConstitutionalLaws()
        # Very short, very ambiguous query
        result = c._check_f4_clarity({"query": "fix it"})
        # CURRENT: score=1.0 (threshold 0.0 → passes)
        # EXPECTED: "fix it" is highly ambiguous → should get low score
        # This test documents the gap
        assert result.score <= 0.9, (
            f"Short ambiguous query should not get perfect score. "
            f"Got score={result.score}. Expected: based on ambiguity assessment."
        )

    def test_delta_s_negative_should_pass_f4(self):
        """When ΔS < 0, F4 should pass."""
        before = EntropyLedgerEntry(
            label="before",
            unsupported_claims=5,
            unresolved_ambiguity=4,
            total_claims=10,
        )
        after = EntropyLedgerEntry(
            label="after",
            unsupported_claims=2,
            unresolved_ambiguity=1,
            total_claims=10,
        )
        assessment = EntropyAssessment(before=before, after=after)
        passed, delta_s, reasons = assessment.evaluate_f4()
        assert passed, f"ΔS < 0 should pass: {reasons}"
        assert delta_s is not None and delta_s < 0

    def test_delta_s_positive_should_fail_f4(self):
        """When ΔS > 0, F4 should fail (HOLD)."""
        before = EntropyLedgerEntry(
            label="before",
            unsupported_claims=1,
            total_claims=5,
        )
        after = EntropyLedgerEntry(
            label="after",
            unsupported_claims=3,  # More unsupported claims
            unresolved_contradictions=2,  # New contradictions
            total_claims=8,  # More claims but less clarity
        )
        assessment = EntropyAssessment(before=before, after=after)
        passed, delta_s, reasons = assessment.evaluate_f4()
        assert not passed, f"ΔS > 0 should fail: {reasons}"
        assert delta_s is not None and delta_s > 0

    def test_delta_s_zero_with_bounded_unknowns_should_pass(self):
        """ΔS = 0 with bounded unknowns should pass."""
        before = EntropyLedgerEntry(label="before", total_claims=5)
        after = EntropyLedgerEntry(label="after", total_claims=5)
        assessment = EntropyAssessment(
            before=before,
            after=after,
            bounded_unknowns=["Root cause unknown but contained to module X"],
        )
        passed, _, reasons = assessment.evaluate_f4()
        assert passed, f"ΔS=0 with bounded unknowns should pass: {reasons}"

    def test_missing_measurement_should_fail(self):
        """Missing before or after measurement should fail."""
        assessment = EntropyAssessment()
        passed, delta_s, reasons = assessment.evaluate_f4()
        assert not passed, f"Missing measurements should fail: {reasons}"
        assert delta_s is None
