"""
Tests for the Moral Accountability Kernel — all 6 primitives.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from datetime import UTC, datetime

import pytest

from arifosmcp.core.moral_accountability_kernel import (
    BurdenTransferDetector,
    EuphemismDecoder,
    HumanInvariantTracker,
    MoralAccountabilityKernel,
    MoralRecursionTracker,
    NoSoulClaimRule,
    ValidationResult,
    WeakestStakeholderRegister,
)


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 1: HumanInvariantTracker
# ═══════════════════════════════════════════════════════════════════════════


class TestHumanInvariantTracker:
    """Test HumanInvariantTracker — tracking named actors across repeated decisions."""

    def test_register_decision_returns_structured_dict(self):
        """register_decision should return a dict with required fields."""
        tracker = HumanInvariantTracker()
        result = tracker.register_decision(
            actor_id="TT",
            pattern="rightsizing",
            context="PETRONAS layoff of 5,000 workers",
        )

        assert isinstance(result, dict)
        assert result["actor_id"] == "TT"
        assert result["pattern"] == "rightsizing"
        assert result["total_decisions"] == 1
        assert result["alert_triggered"] is False
        assert "registration_id" in result
        assert "timestamp" in result

    def test_alert_triggers_at_three_defensive_patterns(self):
        """Alert should trigger when actor has 3+ defensive patterns."""
        tracker = HumanInvariantTracker()
        tracker.register_decision("TT", "burden_transfer", "Layoff workers, keep F1")
        tracker.register_decision("TT", "cost_externalisation", "Give assets to foreign firms")
        result = tracker.register_decision(
            "TT", "euphemistic_justification", "Call layoffs rightsizing"
        )

        assert result["alert_triggered"] is True
        assert result["defensive_pattern_count"] == 3
        assert "invariant accountability flag" in result["alert_message"]

    def test_get_invariant_score_no_decisions(self):
        """get_invariant_score should return zeros for unknown actors."""
        tracker = HumanInvariantTracker()
        result = tracker.get_invariant_score("unknown_actor")

        assert result["total_decisions"] == 0
        assert result["invariant_score"] == 0.0
        assert result["assessment"] == "no_decisions"

    def test_get_invariant_score_computes_correctly(self):
        """get_invariant_score should compute ratio of defensive to total decisions."""
        tracker = HumanInvariantTracker()
        tracker.register_decision("TT", "burden_transfer", "decision 1")
        tracker.register_decision("TT", "normal_ops", "decision 2")
        tracker.register_decision("TT", "cost_externalisation", "decision 3")
        tracker.register_decision("TT", "normal_ops", "decision 4")

        result = tracker.get_invariant_score("TT")
        assert result["total_decisions"] == 4
        assert result["defensive_count"] == 2
        assert result["invariant_score"] == 0.5  # 2/4

    def test_get_pattern_history_returns_ordered_list(self):
        """get_pattern_history should return all decisions chronologically."""
        tracker = HumanInvariantTracker()
        tracker.register_decision("TT", "pattern_a", "first")
        tracker.register_decision("TT", "pattern_b", "second")

        history = tracker.get_pattern_history("TT")
        assert len(history) == 2
        assert history[0]["pattern"] == "pattern_a"
        assert history[1]["pattern"] == "pattern_b"

    def test_add_defensive_pattern(self):
        """Custom defensive patterns should be added and counted."""
        tracker = HumanInvariantTracker()
        tracker.add_defensive_pattern("my_custom_flag")
        tracker.register_decision("TT", "my_custom_flag", "test")
        result = tracker.get_invariant_score("TT")
        assert result["defensive_count"] == 1


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 2: BurdenTransferDetector
# ═══════════════════════════════════════════════════════════════════════════


class TestBurdenTransferDetector:
    """Test BurdenTransferDetector — detecting asymmetric burden transfer."""

    def test_analyze_decision_returns_structured_result(self):
        """analyze_decision should return a dict with required fields."""
        detector = BurdenTransferDetector()
        result = detector.analyze_decision({
            "decision_id": "tt_layoffs_2025",
            "beneficiary": "PETRONAS_CEO",
            "burden_bearer": "PETRONAS_workers",
            "benefit_value": 10,
            "burden_value": 90,
        })

        assert result["decision_id"] == "tt_layoffs_2025"
        assert result["beneficiary"] == "PETRONAS_CEO"
        assert result["burden_bearer"] == "PETRONAS_workers"
        assert result["is_asymmetric"] is True
        assert result["assessment"] == "ASYMMETRIC"

    def test_infinite_ratio_when_no_benefit(self):
        """Transfer ratio should be infinity when benefit is zero."""
        detector = BurdenTransferDetector()
        result = detector.analyze_decision({
            "decision_id": "zero_benefit",
            "beneficiary": "Executive",
            "burden_bearer": "Workers",
            "benefit_value": 0,
            "burden_value": 50,
        })

        assert result["transfer_ratio"] == float("inf")
        assert result["is_asymmetric"] is True
        assert result["assessment"] == "EXTREME_ASYMMETRY"

    def test_get_transfer_ratio_existing(self):
        """get_transfer_ratio should return ratio for an existing decision."""
        detector = BurdenTransferDetector()
        detector.analyze_decision({
            "decision_id": "test_id",
            "beneficiary": "A",
            "burden_bearer": "B",
            "benefit_value": 20,
            "burden_value": 80,
        })

        result = detector.get_transfer_ratio("test_id")
        assert result["found"] is True
        assert result["transfer_ratio"] == 4.0  # 80/20

    def test_get_transfer_ratio_missing(self):
        """get_transfer_ratio should return found=False for unknown."""
        detector = BurdenTransferDetector()
        result = detector.get_transfer_ratio("nonexistent")
        assert result["found"] is False

    def test_flag_asymmetric_returns_only_asymmetric(self):
        """flag_asymmetric should return only asymmetric transfers."""
        detector = BurdenTransferDetector()
        detector.analyze_decision({
            "decision_id": "fair",
            "beneficiary": "A",
            "burden_bearer": "B",
            "benefit_value": 50,
            "burden_value": 50,
        })
        detector.analyze_decision({
            "decision_id": "unfair",
            "beneficiary": "A",
            "burden_bearer": "C",
            "benefit_value": 10,
            "burden_value": 90,
        })

        flags = detector.flag_asymmetric()
        assert len(flags) == 1
        assert flags[0]["decision_id"] == "unfair"

    def test_get_systemic_burden_pattern(self):
        """get_systemic_burden_pattern should aggregate patterns."""
        detector = BurdenTransferDetector()
        detector.analyze_decision({
            "decision_id": "d1",
            "beneficiary": "CEO",
            "burden_bearer": "Workers",
            "benefit_value": 10,
            "burden_value": 80,
        })
        detector.analyze_decision({
            "decision_id": "d2",
            "beneficiary": "CEO",
            "burden_bearer": "Contractors",
            "benefit_value": 5,
            "burden_value": 60,
        })
        detector.analyze_decision({
            "decision_id": "d3",
            "beneficiary": "CEO",
            "burden_bearer": "Suppliers",
            "benefit_value": 8,
            "burden_value": 70,
        })

        pattern = detector.get_systemic_burden_pattern()
        assert pattern["systemic_flag"] is True  # CEO appears 3 times
        assert pattern["total_transfers"] == 3
        assert pattern["beneficiary_frequency"]["CEO"] == 3


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 3: EuphemismDecoder
# ═══════════════════════════════════════════════════════════════════════════


class TestEuphemismDecoder:
    """Test EuphemismDecoder — translating corporate language to human impact."""

    def test_decode_known_euphemism(self):
        """decode should return translation for known euphemisms."""
        decoder = EuphemismDecoder()
        result = decoder.decode("rightsizing")

        assert result["found"] is True
        assert "mass layoff" in result["translation"]
        assert result["impact_category"] == "economic_harm"
        assert result["confidence"] >= 0.9

    def test_decode_unknown_euphemism(self):
        """decode should return found=False for unknown phrases."""
        decoder = EuphemismDecoder()
        result = decoder.decode("synergistic paradigm shift")

        assert result["found"] is False
        assert result["translation"] is None

    def test_add_euphemism_then_decode(self):
        """add_euphemism should allow dynamic addition."""
        decoder = EuphemismDecoder()
        decoder.add_euphemism(
            euphemism="synergistic downsizing",
            translation="coordinated job cuts across departments",
            impact_category="economic_harm",
            confidence=0.85,
        )
        result = decoder.decode("synergistic downsizing")
        assert result["found"] is True
        assert "coordinated job cuts" in result["translation"]

    def test_scan_text_finds_multiple_euphemisms(self):
        """scan_text should find all known euphemisms in a text block."""
        decoder = EuphemismDecoder()
        text = (
            "We are undergoing a rightsizing transformation. "
            "This is part of our portfolio rationalisation strategy "
            "to ensure energy security."
        )
        results = decoder.scan_text(text)

        assert len(results) >= 3
        found_terms = [r["original"] for r in results]
        assert "rightsizing" in found_terms
        assert "transformation" in found_terms
        assert "energy security" in found_terms

    def test_get_dictionary_stats(self):
        """get_dictionary_stats should return category breakdown."""
        decoder = EuphemismDecoder()
        stats = decoder.get_dictionary_stats()

        assert stats["total_euphemisms"] >= 10
        assert "economic_harm" in stats["categories"]
        assert stats["categories"]["economic_harm"] >= 3

    def test_remove_euphemism(self):
        """remove_euphemism should delete from dictionary."""
        decoder = EuphemismDecoder()
        assert decoder.remove_euphemism("rightsizing") is True
        result = decoder.decode("rightsizing")
        assert result["found"] is False


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 4: NoSoulClaimRule
# ═══════════════════════════════════════════════════════════════════════════


class TestNoSoulClaimRule:
    """Test NoSoulClaimRule — separating pattern from intent attribution."""

    def test_validate_claim_pattern_only_pass(self):
        """Pattern-based claims should pass validation."""
        rule = NoSoulClaimRule()
        result = rule.validate_claim(
            "TT repeatedly chose burden transfer across 7 decision points"
        )

        assert isinstance(result, ValidationResult)
        assert result.is_pattern_claim is True
        assert result.has_intent_attribute is False
        assert result.f2_compliant is True

    def test_validate_claim_intent_attribution_fails(self):
        """Claims attributing intent should fail validation."""
        rule = NoSoulClaimRule()
        result = rule.validate_claim(
            "TT knew what he was doing when he fired 5,000 workers"
        )

        assert result.has_intent_attribute is True
        assert result.f2_compliant is False
        assert "intent" in result.reason.lower()

    def test_validate_claim_evil_attribution_fails(self):
        """Calling an actor 'evil' should be flagged."""
        rule = NoSoulClaimRule()
        result = rule.validate_claim(
            "The CEO is an evil man who deliberately harms people"
        )

        assert result.has_intent_attribute is True
        assert result.f2_compliant is False

    def test_is_intent_claimed_returns_bool(self):
        """is_intent_claimed should return boolean."""
        rule = NoSoulClaimRule()
        assert rule.is_intent_claimed("He intended to harm them") is True
        assert rule.is_intent_claimed("Pattern shows 7 instances of burden transfer") is False

    def test_generate_f2_compliant_formats_correctly(self):
        """generate_f2_compliant should produce structured pattern/intent string."""
        rule = NoSoulClaimRule()
        result = rule.generate_f2_compliant(
            pattern_obs="7 of 7 decisions transferred cost to weakest stakeholders",
        )
        assert "PATTERN:" in result
        assert "INTENT:" in result
        assert "intent_unknown_by_design" in result

    def test_explain_violation_detailed(self):
        """explain_violation should return match details."""
        rule = NoSoulClaimRule()
        result = rule.explain_violation(
            "He knew exactly what he was doing"
        )

        assert result["has_intent_attribution"] is True
        assert result["violates_no_soul_rule"] is True
        assert len(result["intent_attribution_details"]) > 0
        assert "Replace" in result["recommended_fix"]

    def test_explain_violation_clean(self):
        """explain_violation should show no violations for clean text."""
        rule = NoSoulClaimRule()
        result = rule.explain_violation(
            "Over 7 decision points, pattern shows consistent burden transfer"
        )

        assert result["has_intent_attribution"] is False
        assert result["violates_no_soul_rule"] is False
        assert "No fix needed" in result["recommended_fix"]


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 5: WeakestStakeholderRegister
# ═══════════════════════════════════════════════════════════════════════════


class TestWeakestStakeholderRegister:
    """Test WeakestStakeholderRegister — identifying who pays if decision fails."""

    def test_register_stakeholder_returns_result(self):
        """register_stakeholder should return structured result."""
        register = WeakestStakeholderRegister()
        result = register.register_stakeholder(
            name="PETRONAS_Worker",
            power_score=0.05,
            optionality_score=0.10,
            voice_score=0.02,
        )

        assert result["name"] == "PETRONAS_Worker"
        assert result["registered"] is True
        assert "vulnerability_index" in result

    def test_vulnerability_index_high_for_low_power(self):
        """Low scores should yield high vulnerability index."""
        register = WeakestStakeholderRegister()
        register.register_stakeholder("Worker", power_score=0.0, optionality_score=0.0, voice_score=0.0)
        result = register.identify_weakest()
        assert result[0]["vulnerability_index"] == 1.0

    def test_vulnerability_index_low_for_high_power(self):
        """High scores should yield low vulnerability index."""
        register = WeakestStakeholderRegister()
        register.register_stakeholder("CEO", power_score=1.0, optionality_score=1.0, voice_score=1.0)
        result = register.identify_weakest()
        assert result[0]["vulnerability_index"] == 0.0

    def test_identify_weakest_sorts_by_vulnerability(self):
        """identify_weakest should return sorted list with weakest first."""
        register = WeakestStakeholderRegister()
        register.register_stakeholder("CEO", power_score=0.9, optionality_score=0.8, voice_score=0.9)
        register.register_stakeholder("Manager", power_score=0.5, optionality_score=0.4, voice_score=0.3)
        register.register_stakeholder("Worker", power_score=0.1, optionality_score=0.15, voice_score=0.05)

        result = register.identify_weakest()
        assert result[0]["name"] == "Worker"
        assert result[1]["name"] == "Manager"
        assert result[2]["name"] == "CEO"
        assert result[0]["vulnerability_index"] > result[1]["vulnerability_index"] > result[2]["vulnerability_index"]

    def test_get_protected_stakeholders(self):
        """get_protected_stakeholders should return those with low vulnerability."""
        register = WeakestStakeholderRegister()
        register.register_stakeholder("CEO", power_score=0.9, optionality_score=0.9, voice_score=0.9)
        register.register_stakeholder("Worker", power_score=0.1, optionality_score=0.1, voice_score=0.1)

        protected = register.get_protected_stakeholders()
        assert len(protected) == 1
        assert protected[0]["name"] == "CEO"

    def test_get_decision_impact_returns_both_sides(self):
        """get_decision_impact should show impacted and protected."""
        register = WeakestStakeholderRegister()
        register.register_stakeholder("CEO", power_score=0.9, optionality_score=0.9, voice_score=0.9)
        register.register_stakeholder("Worker", power_score=0.1, optionality_score=0.1, voice_score=0.1)

        impact = register.get_decision_impact("layoff_decision")
        assert impact["decision_context"] == "layoff_decision"
        assert len(impact["most_impacted"]) > 0
        assert len(impact["protected"]) > 0
        assert impact["vulnerability_gap"] > 0


# ═══════════════════════════════════════════════════════════════════════════
# Primitive 6: MoralRecursionTracker
# ═══════════════════════════════════════════════════════════════════════════


class TestMoralRecursionTracker:
    """Test MoralRecursionTracker — tracking exception → normalised → irreversible."""

    def test_record_decision_benign_stage(self):
        """Low-severity first decision should be 'benign'."""
        tracker = MoralRecursionTracker()
        result = tracker.record_decision(actor="TT", decision_type="layoffs", severity=0.2)

        assert result["stage"] == "benign"
        assert result["alert"] is False

    def test_record_decision_exception_stage(self):
        """High-severity first decision should be 'exception'."""
        tracker = MoralRecursionTracker()
        result = tracker.record_decision(actor="TT", decision_type="rights_violation", severity=0.7)

        assert result["stage"] == "exception"
        assert result["alert"] is False

    def test_record_decision_repeated_stage(self):
        """Second occurrence of same type should be 'repeated'."""
        tracker = MoralRecursionTracker()
        tracker.record_decision(actor="TT", decision_type="layoffs", severity=0.6)
        result = tracker.record_decision(actor="TT", decision_type="layoffs", severity=0.7)

        assert result["stage"] == "repeated"

    def test_record_decision_normalised_stage(self):
        """Fifth+ occurrence should be 'normalised'."""
        tracker = MoralRecursionTracker()
        for _ in range(5):
            tracker.record_decision(actor="TT", decision_type="layoffs", severity=0.6)
        # Now record the 6th
        result = tracker.record_decision(actor="TT", decision_type="layoffs", severity=0.6)

        # After 5 or more of same type → normalised
        assert result["stage"] in ("normalised",)
        assert result["alert"] is True

    def test_record_decision_irreversible_by_severity(self):
        """Severity >= 0.85 should be 'irreversible' regardless of count."""
        tracker = MoralRecursionTracker()
        result = tracker.record_decision(actor="TT", decision_type="rights_denial", severity=0.90)

        assert result["stage"] == "irreversible"
        assert result["alert"] is True

    def test_get_escalation_path(self):
        """get_escalation_path should return chronological escalation steps."""
        tracker = MoralRecursionTracker()
        tracker.record_decision(actor="TT", decision_type="a", severity=0.3)
        tracker.record_decision(actor="TT", decision_type="a", severity=0.5)
        tracker.record_decision(actor="TT", decision_type="a", severity=0.6)

        path = tracker.get_escalation_path("TT")
        assert len(path) == 3
        assert path[0]["stage"] == "benign"
        assert path[1]["stage"] == "repeated"
        assert path[2]["stage"] == "repeated"

    def test_is_at_irreversible_risk_true(self):
        """is_at_irreversible_risk should return True for actors at irreversible stage."""
        tracker = MoralRecursionTracker()
        tracker.record_decision(actor="TT", decision_type="rights_denial", severity=0.90)
        result = tracker.is_at_irreversible_risk("TT")

        assert result["at_irreversible_risk"] is True
        assert result["current_stage"] == "irreversible"

    def test_is_at_irreversible_risk_false(self):
        """is_at_irreversible_risk should return False for benign."""
        tracker = MoralRecursionTracker()
        tracker.record_decision(actor="TT", decision_type="low_impact", severity=0.1)
        result = tracker.is_at_irreversible_risk("TT")

        assert result["at_irreversible_risk"] is False


# ═══════════════════════════════════════════════════════════════════════════
# Integration: MoralAccountabilityKernel (convenience wrapper)
# ═══════════════════════════════════════════════════════════════════════════


class TestMoralAccountabilityKernel:
    """Test the unified MoralAccountabilityKernel wrapper."""

    def test_kernel_imports_and_instantiates(self):
        """MoralAccountabilityKernel should instantiate all 6 primitives."""
        kernel = MoralAccountabilityKernel()

        assert hasattr(kernel, "human_tracker")
        assert hasattr(kernel, "burden_detector")
        assert hasattr(kernel, "euphemism_decoder")
        assert hasattr(kernel, "no_soul_rule")
        assert hasattr(kernel, "weakest_register")
        assert hasattr(kernel, "recursion_tracker")

        assert isinstance(kernel.human_tracker, HumanInvariantTracker)
        assert isinstance(kernel.burden_detector, BurdenTransferDetector)
        assert isinstance(kernel.euphemism_decoder, EuphemismDecoder)
        assert isinstance(kernel.no_soul_rule, NoSoulClaimRule)
        assert isinstance(kernel.weakest_register, WeakestStakeholderRegister)
        assert isinstance(kernel.recursion_tracker, MoralRecursionTracker)

    def test_kernel_get_all_state(self):
        """get_all_state should return structured dict with all states."""
        kernel = MoralAccountabilityKernel()
        state = kernel.get_all_state()

        assert isinstance(state, dict)
        assert "human_tracker" in state
        assert "burden_detector" in state
        assert "euphemism_decoder" in state
        assert "no_soul_rule" in state
        assert "weakest_register" in state
        assert "recursion_tracker" in state

    def test_kernel_reset_clears_all(self):
        """reset should clear all primitive state."""
        kernel = MoralAccountabilityKernel()
        kernel.human_tracker.register_decision("TT", "rightsizing", "test")
        assert kernel.human_tracker.get_invariant_score("TT")["total_decisions"] == 1

        kernel.reset()
        assert kernel.human_tracker.get_invariant_score("TT")["total_decisions"] == 0

    def test_tt_case_study_integration(self):
        """Full TT case study through all 6 primitives."""
        kernel = MoralAccountabilityKernel()
        tracker = kernel.human_tracker
        detector = kernel.burden_detector
        decoder = kernel.euphemism_decoder
        no_soul = kernel.no_soul_rule

        # 1. Register TT's decisions
        tracker.register_decision("TT", "burden_transfer", "EnQuest $833M deal - give assets to British firm")
        tracker.register_decision("TT", "burden_transfer", "Eni $15B JV - give assets to Italian firm")
        tracker.register_decision("TT", "rightsizing", "Fire 5,000 workers - keep F1 sponsorship")
        tracker.register_decision("TT", "euphemistic_justification", "Call it 'rightsizing' and 'energy security'")
        tracker.register_decision("TT", "burden_transfer", "Sue Sarawak in Federal Court for gas rights")
        tracker.register_decision("TT", "accountability_avoidance", "Say 'awaiting clarity' on MA63")
        tracker.register_decision("TT", "burden_transfer", "F1 sponsorship RM340M kept while workers fired")

        # 2. Verify alert triggers
        score = tracker.get_invariant_score("TT")
        assert score["total_decisions"] == 7
        assert score["invariant_score"] >= 0.7
        assert score["assessment"] == "high_invariant_risk"

        # 3. Analyze burden transfers
        detector.analyze_decision({
            "decision_id": "workers_vs_f1",
            "beneficiary": "TT_and_executives",
            "burden_bearer": "5,000_workers_and_families",
            "benefit_value": 5,
            "burden_value": 95,
        })
        flags = detector.flag_asymmetric()
        assert len(flags) >= 1

        # 4. Decode euphemisms
        text = "We are rightsizing for energy security through portfolio rationalisation"
        decoded = decoder.scan_text(text)
        assert len(decoded) >= 3

        # 5. No soul claim validation
        compliant = no_soul.validate_claim(
            "TT's 7 decisions show a consistent pattern of burden transfer to weakest stakeholders"
        )
        assert compliant.f2_compliant is True

        non_compliant = no_soul.validate_claim(
            "TT knew he was hurting people and intended to do so"
        )
        assert non_compliant.f2_compliant is False

        # 6. Weakest stakeholders
        kernel.weakest_register.register_stakeholder("Sarawak_people", 0.05, 0.02, 0.01)
        kernel.weakest_register.register_stakeholder("PETRONAS_workers", 0.08, 0.10, 0.03)
        kernel.weakest_register.register_stakeholder("TT_CEO", 0.95, 0.90, 0.95)

        weakest = kernel.weakest_register.identify_weakest()
        assert weakest[0]["name"] == "Sarawak_people"

        # 7. Moral recursion
        kernel.recursion_tracker.record_decision("TT", "layoffs", 0.6, "First round layoffs")
        kernel.recursion_tracker.record_decision("TT", "layoffs", 0.7, "Second round")
        kernel.recursion_tracker.record_decision("TT", "layoffs", 0.8, "Third round")
        kernel.recursion_tracker.record_decision("TT", "rights_violation", 0.9, "Federal Court against Sarawak")
        kernel.recursion_tracker.record_decision("TT", "layoffs", 0.6, "Fourth round")
        kernel.recursion_tracker.record_decision("TT", "layoffs", 0.6, "Fifth round")
        kernel.recursion_tracker.record_decision("TT", "layoffs", 0.7, "Sixth round")

        risk = kernel.recursion_tracker.is_at_irreversible_risk("TT")
        assert risk["at_irreversible_risk"] is True
