"""
Tests for arif_think_kernel.py — Constitutional Embedding for arif_think

Verifies:
- I1-I8 invariants
- Entropy policy
- Reality stack layers
- Math axioms
- Symbolic code
- Linguistic contract
- Quote metadata schema

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import pytest

from arifosmcp.core.arif_think_kernel import (
    BANNED_DEFAULT_LANGUAGE,
    ARIF_THINK_DOCTRINE,
    EntropyPolicy,
    EvidenceClaim,
    FORBIDDEN_IN_ARIF_THINK,
    INVARIANTS,
    InvariantID,
    LaneType,
    LANE_CONFIG,
    LinguisticLabel,
    MathAxioms,
    QuoteMetadata,
    QUOTE_PLACEMENT_RULES,
    RealityLayer,
    RealityStack,
    VerdictSymbol,
    check_invariant,
    validate_output,
)


class TestInvariants:
    """Test I1-I8 core invariants."""

    def test_invariants_exist(self):
        """All 8 invariants should be defined."""
        assert len(INVARIANTS) == 8
        for inv_id in InvariantID:
            assert inv_id.value in INVARIANTS

    def test_i1_reversibility(self):
        """I1: Thinking is reversible. Execution is not."""
        inv = INVARIANTS[InvariantID.I1_REVERSIBILITY.value]
        assert "reversible" in inv["rule"].lower()
        assert "execute" in inv["meaning"].lower()

    def test_i2_authority_separation(self):
        """I2: Mind does not judge. Judge does not execute. Vault does not think."""
        inv = INVARIANTS[InvariantID.I2_AUTHORITY_SEPARATION.value]
        assert "arif_think" in inv["mapping"]
        assert inv["mapping"]["arif_think"] == "reason"

    def test_i3_evidence_honesty(self):
        """I3: No evidence, no verified claim."""
        inv = INVARIANTS[InvariantID.I3_EVIDENCE_HONESTY.value]
        assert "verified fact" in inv["forbidden_without_evidence"]
        assert "hypothesis" in inv["allowed_without_evidence"]

    def test_i8_quotes_do_not_reason(self):
        """I8: A quote can anchor meaning, but cannot carry proof."""
        inv = INVARIANTS[InvariantID.I8_QUOTES_DO_NOT_REASON.value]
        assert "metadata" in inv["meaning"].lower()


class TestEntropyPolicy:
    """Test entropy management."""

    def test_lower_entropy(self):
        """Shorter output should reduce entropy."""
        assert EntropyPolicy.lower_entropy_if("short", "much longer output")

    def test_higher_entropy(self):
        """Repetitive output should increase entropy."""
        assert EntropyPolicy.higher_entropy_if("the the the the the the")

    def test_operational_test(self):
        """Non-empty output should pass operational test."""
        assert EntropyPolicy.operational_test("meaningful output")


class TestRealityStack:
    """Test reality layers and evidence management."""

    def test_reality_layers_exist(self):
        """All 4 reality layers should be defined."""
        assert len(RealityLayer) == 4

    def test_max_confidence(self):
        """Each layer should have max confidence."""
        assert RealityStack.MAX_CONFIDENCE[RealityLayer.L1_GROUND_TRUTH] == 1.0
        assert RealityStack.MAX_CONFIDENCE[RealityLayer.L4_INFERRED] == 0.60

    def test_validate_claim(self):
        """Claims should not exceed layer confidence."""
        claim = EvidenceClaim(
            claim="test",
            layer=RealityLayer.L2_VERIFIED_STATE,
            confidence=0.85,
            source="tool_result",
        )
        assert RealityStack.validate_claim(claim)

    def test_validate_claim_violation(self):
        """Claims exceeding layer confidence should fail."""
        claim = EvidenceClaim(
            claim="test",
            layer=RealityLayer.L4_INFERRED,
            confidence=0.90,  # Exceeds 0.60 max
        )
        assert not RealityStack.validate_claim(claim)


class TestMathAxioms:
    """Test mathematical axioms."""

    def test_confidence(self):
        """Confidence should be bounded 0-1."""
        c = MathAxioms.confidence(0.8, 0.7, 0.1, 0.1)
        assert 0.0 <= c <= 1.0

    def test_entropy_change(self):
        """Entropy change should be difference."""
        assert MathAxioms.entropy_change(0.5, 0.3) == -0.2
        assert MathAxioms.entropy_change(0.3, 0.5) == 0.2

    def test_risk(self):
        """Risk should be product of factors."""
        r = MathAxioms.risk(0.8, 0.5, 0.3)
        assert abs(r - 0.12) < 0.001

    def test_confidence_cap(self):
        """Confidence cap should not exceed evidence quality."""
        assert MathAxioms.confidence_cap(0.9, 0.7) == 0.7


class TestVerdictSymbols:
    """Test verdict symbols."""

    def test_verdict_symbols_exist(self):
        """All verdict symbols should be defined."""
        assert VerdictSymbol.THINK.value == "THINK"
        assert VerdictSymbol.HOLD.value == "HOLD"
        assert VerdictSymbol.VOID.value == "VOID"
        assert VerdictSymbol.ADVISORY.value == "ADVISORY"
        assert VerdictSymbol.DEGRADED.value == "DEGRADED"
        assert VerdictSymbol.SEAL.value == "SEAL"

    def test_seal_forbidden_in_think(self):
        """SEAL should be forbidden in arif_think."""
        assert "SEAL in arif_think" in FORBIDDEN_IN_ARIF_THINK


class TestLinguisticContract:
    """Test linguistic labels."""

    def test_linguistic_labels(self):
        """All linguistic labels should be defined."""
        assert LinguisticLabel.CLAIM.value == "CLAIM"
        assert LinguisticLabel.HYPOTHESIS.value == "HYPOTHESIS"
        assert LinguisticLabel.INFERENCE.value == "INFERENCE"
        assert LinguisticLabel.UNKNOWN.value == "UNKNOWN"
        assert LinguisticLabel.ASSUMPTION.value == "ASSUMPTION"
        assert LinguisticLabel.NEXT_ACTION.value == "NEXT_ACTION"

    def test_banned_language(self):
        """Banned language should include SEAL without evidence."""
        assert "SEAL" in BANNED_DEFAULT_LANGUAGE
        assert "VERIFIED_FACT" in BANNED_DEFAULT_LANGUAGE


class TestQuoteMetadata:
    """Test quote metadata schema."""

    def test_quote_metadata(self):
        """Quote metadata should have required fields."""
        quote = QuoteMetadata(
            id="Q01",
            quote="Test quote",
            author="Test Author",
            function="humility",
            use_when=["high_uncertainty"],
            must_not_be_used_when=["compact_mode"],
        )
        assert quote.id == "Q01"
        assert quote.function == "humility"

    def test_quote_valid_for_context(self):
        """Quote should be valid for allowed context."""
        quote = QuoteMetadata(
            id="Q01",
            quote="Test",
            author="Test",
            function="humility",
            must_not_be_used_when=["compact_mode"],
        )
        assert quote.is_valid_for_context("normal mode")
        assert not quote.is_valid_for_context("compact_mode")

    def test_quote_placement_rules(self):
        """Quote placement rules should be defined."""
        assert QUOTE_PLACEMENT_RULES["count"] == 33
        assert QUOTE_PLACEMENT_RULES["default_output"] is False
        assert "user asks for philosophy" in QUOTE_PLACEMENT_RULES["trigger_only_when"]
        assert "compact mode" in QUOTE_PLACEMENT_RULES["forbidden_when"]


class TestLaneConfig:
    """Test lane configuration."""

    def test_lane_types(self):
        """Both lane types should be defined."""
        assert LaneType.FAST.value == "fast"
        assert LaneType.GUARDED.value == "guarded"

    def test_lane_config(self):
        """Lane configs should have required fields."""
        fast = LANE_CONFIG[LaneType.FAST]
        assert fast["evidence_required"] is False
        assert "ADVISORY" in fast["verdicts"]

        guarded = LANE_CONFIG[LaneType.GUARDED]
        assert guarded["evidence_required"] is True
        assert "NEEDS_EVIDENCE" in guarded["verdicts"]


class TestHelperFunctions:
    """Test helper functions."""

    def test_check_invariant_i1(self):
        """I1 check should verify reversibility."""
        assert check_invariant(InvariantID.I1_REVERSIBILITY, {"is_reversible": True})
        assert not check_invariant(InvariantID.I1_REVERSIBILITY, {"is_reversible": False})

    def test_check_invariant_i3(self):
        """I3 check should verify evidence for verified facts."""
        assert check_invariant(
            InvariantID.I3_EVIDENCE_HONESTY,
            {"has_evidence": True, "claim_type": "verified_fact"},
        )
        assert not check_invariant(
            InvariantID.I3_EVIDENCE_HONESTY,
            {"has_evidence": False, "claim_type": "verified_fact"},
        )

    def test_validate_output_valid(self):
        """Valid output should have no violations."""
        output = {
            "text": "meaningful output",
            "is_reversible": True,
            "has_evidence": True,
            "claim_type": "hypothesis",
        }
        violations = validate_output(output)
        assert len(violations) == 0

    def test_validate_output_i1_violation(self):
        """Irreversible output should violate I1."""
        output = {
            "text": "irreversible action",
            "is_irreversible": True,
        }
        violations = validate_output(output)
        assert any("I1" in v for v in violations)

    def test_validate_output_i2_violation(self):
        """SEAL in think should violate I2."""
        output = {
            "text": "seal attempt",
            "verdict": "SEAL",
        }
        violations = validate_output(output)
        assert any("I2" in v for v in violations)


class TestDoctrine:
    """Test arif_think doctrine."""

    def test_doctrine_exists(self):
        """Doctrine should have 6 items."""
        assert len(ARIF_THINK_DOCTRINE) == 6

    def test_doctrine_core(self):
        """Doctrine should include core rules."""
        assert "Do not seal." in ARIF_THINK_DOCTRINE
        assert "Do not execute." in ARIF_THINK_DOCTRINE
        assert "Lower entropy." in ARIF_THINK_DOCTRINE
