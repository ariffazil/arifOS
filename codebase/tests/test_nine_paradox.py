"""
TEST SUITE: 9-PARADOX CONSTITUTIONAL MATRIX (v54.0)

Tests for:
1. All 9 paradoxes correctly instantiated
2. Equilibrium detection
3. Equilibrium solver convergence
4. Perturbation recovery
5. Trinity tier calculations

DITEMPA BUKAN DIBERI
"""

import asyncio
import pytest
import numpy as np
from codebase.apex.trinity_nine import (
    TrinityNine, NineFoldBundle, NineParadox, EquilibriumState,
    TrinityTier, create_nine_paradoxes, trinity_nine_sync, check_equilibrium
)
from codebase.apex.equilibrium_finder import (
    EquilibriumFinder, EquilibriumPoint, PerturbationAnalyzer
)


# ============ TESTS: 9 PARADOXES ============

class TestNineParadoxes:
    """Tests for the 9-paradox matrix."""
    
    def test_all_nine_exist(self):
        """Test that all 9 paradoxes are created."""
        paradoxes = create_nine_paradoxes()
        assert len(paradoxes) == 9
    
    def test_trinity_alpha_paradoxes(self):
        """Test Trinity Alpha (core virtues) paradoxes."""
        paradoxes = create_nine_paradoxes()
        
        alpha = [p for p in paradoxes.values() if p.tier == TrinityTier.ALPHA]
        assert len(alpha) == 3
        
        names = [p.name for p in alpha]
        assert "Truth ↔ Care" in names
        assert "Clarity ↔ Peace" in names
        assert "Humility ↔ Justice" in names
    
    def test_trinity_beta_paradoxes(self):
        """Test Trinity Beta (implementation) paradoxes."""
        paradoxes = create_nine_paradoxes()
        
        beta = [p for p in paradoxes.values() if p.tier == TrinityTier.BETA]
        assert len(beta) == 3
        
        names = [p.name for p in beta]
        assert "Precision ↔ Reversibility" in names
        assert "Hierarchy ↔ Consent" in names
        assert "Agency ↔ Protection" in names
    
    def test_trinity_gamma_paradoxes(self):
        """Test Trinity Gamma (temporal/meta) paradoxes."""
        paradoxes = create_nine_paradoxes()
        
        gamma = [p for p in paradoxes.values() if p.tier == TrinityTier.GAMMA]
        assert len(gamma) == 3
        
        names = [p.name for p in gamma]
        assert "Urgency ↔ Sustainability" in names
        assert "Certainty ↔ Doubt" in names
        assert "Unity ↔ Diversity" in names
    
    def test_paradox_synthesis_descriptions(self):
        """Test that all paradoxes have synthesis descriptions."""
        paradoxes = create_nine_paradoxes()
        
        syntheses = {
            "truth_care": "Compassionate Truth",
            "clarity_peace": "Clear Peace",
            "humility_justice": "Humble Justice",
            "precision_reversibility": "Careful Action",
            "hierarchy_consent": "Structured Freedom",
            "agency_protection": "Responsible Power",
            "urgency_sustainability": "Deliberate Speed",
            "certainty_doubt": "Adaptive Conviction",
            "unity_diversity": "Coherent Plurality"
        }
        
        for key, expected_synthesis in syntheses.items():
            assert paradoxes[key].synthesis == expected_synthesis


# ============ TESTS: EQUILIBRIUM ============

class TestEquilibrium:
    """Tests for equilibrium detection and solving."""
    
    def test_perfect_equilibrium(self):
        """Test that perfect equilibrium is detected."""
        # All scores at threshold
        scores = [0.85] * 9
        eq = check_equilibrium(scores)
        
        assert eq.is_equilibrium is True
        assert eq.trinity_score == 0.85
        assert eq.std_deviation == 0.0
    
    def test_below_threshold_not_equilibrium(self):
        """Test that below-threshold scores are not equilibrium."""
        scores = [0.70] * 9  # Below 0.85
        eq = check_equilibrium(scores)
        
        assert eq.is_equilibrium is False
        assert eq.conditions_met["geometric_mean_threshold"] is False
    
    def test_high_variance_not_equilibrium(self):
        """Test that imbalanced scores are not equilibrium."""
        # High variance
        scores = [0.99, 0.99, 0.99, 0.50, 0.50, 0.50, 0.99, 0.99, 0.99]
        eq = check_equilibrium(scores)
        
        assert eq.is_equilibrium is False
        assert eq.conditions_met["balance_tolerance"] is False
    
    def test_equilibrium_conditions_structure(self):
        """Test that equilibrium conditions are properly reported."""
        scores = [0.85] * 9
        eq = check_equilibrium(scores)
        
        assert "geometric_mean_threshold" in eq.conditions_met
        assert "balance_tolerance" in eq.conditions_met
        assert "min_score_requirement" in eq.conditions_met
        assert "variance_tolerance" in eq.conditions_met
        assert "max_spread" in eq.conditions_met


# ============ TESTS: EQUILIBRIUM FINDER ============

class TestEquilibriumFinder:
    """Tests for equilibrium finder."""
    
    def test_find_optimal_equilibrium(self):
        """Test finding theoretical optimal equilibrium."""
        finder = EquilibriumFinder()
        optimal = finder.find_optimal_equilibrium()
        
        assert optimal.trinity_score == 0.85
        assert optimal.balance_index == 1.0
        assert len(optimal.coordinates) == 9
        assert all(v == 0.85 for v in optimal.coordinates.values())
    
    def test_find_nearest_equilibrium_convergence(self):
        """Test that nearest equilibrium finder converges."""
        finder = EquilibriumFinder()
        
        current_state = {
            "truth_care": 0.82,
            "clarity_peace": 0.88,
            "humility_justice": 0.79,
            "precision_reversibility": 0.91,
            "hierarchy_consent": 0.75,
            "agency_protection": 0.83,
            "urgency_sustainability": 0.77,
            "certainty_doubt": 0.86,
            "unity_diversity": 0.80
        }
        
        point, path = finder.find_nearest_equilibrium(current_state)
        
        # Should converge in reasonable iterations
        assert len(path) < 1000
        assert len(path) > 0
        
        # Final point should be closer to equilibrium
        assert point.trinity_score >= 0.80
    
    def test_stability_calculation(self):
        """Test stability calculation."""
        finder = EquilibriumFinder()
        
        # Balanced high scores = high stability
        stable_state = {name: 0.90 for name in finder.paradox_names}
        paradoxes = create_nine_paradoxes()
        for name, score in stable_state.items():
            paradoxes[name].score = score
        
        stability = finder._calculate_stability(stable_state)
        assert stability > 0.8


# ============ TESTS: TRINITY NINE SYNC ============

class TestTrinityNineSync:
    """Tests for 9-paradox Trinity synchronization."""
    
    @pytest.mark.asyncio
    async def test_basic_synchronization(self):
        """Test basic 9-paradox sync."""
        trinity = TrinityNine()
        
        agi_delta = {
            "F2_truth": 0.92,
            "F4_clarity": 0.88,
            "F7_humility": 0.85,
            "kalman_gain": 0.90,
            "hierarchy": 0.87,
            "agency": 0.83,
            "urgency": 0.80,
            "certainty": 0.89,
            "unity": 0.86
        }
        
        asi_omega = {
            "kappa_r": 0.91,
            "peace_squared": 0.84,
            "justice": 0.88,
            "reversibility": 0.95,
            "consent": 0.82,
            "protection": 0.90,
            "sustainability": 0.85,
            "doubt": 0.78,
            "diversity": 0.87
        }
        
        result = await trinity.synchronize(agi_delta, asi_omega, optimize=True)
        
        assert isinstance(result, NineFoldBundle)
        assert result.session_id is not None
        assert len(result.paradoxes) == 9
        assert result.final_verdict in ["EQUILIBRIUM", "SEAL", "VOID", "SABAR", "888_HOLD"]
    
    @pytest.mark.asyncio
    async def test_tier_scores_calculated(self):
        """Test that tier scores are properly calculated."""
        trinity = TrinityNine()
        
        agi_delta = {f"metric_{i}": 0.85 for i in range(9)}
        asi_omega = {f"metric_{i}": 0.85 for i in range(9)}
        
        # Map metrics properly
        agi_delta = {
            "F2_truth": 0.85, "F4_clarity": 0.85, "F7_humility": 0.85,
            "kalman_gain": 0.85, "hierarchy": 0.85, "agency": 0.85,
            "urgency": 0.85, "certainty": 0.85, "unity": 0.85
        }
        asi_omega = {
            "kappa_r": 0.85, "peace_squared": 0.85, "justice": 0.85,
            "reversibility": 0.85, "consent": 0.85, "protection": 0.85,
            "sustainability": 0.85, "doubt": 0.85, "diversity": 0.85
        }
        
        result = await trinity.synchronize(agi_delta, asi_omega, optimize=False)
        
        assert 0 <= result.alpha_score <= 1
        assert 0 <= result.beta_score <= 1
        assert 0 <= result.gamma_score <= 1


# ============ TESTS: PERTURBATION ANALYSIS ============

class TestPerturbationAnalysis:
    """Tests for perturbation analysis."""
    
    def test_perturbation_recovery(self):
        """Test perturbation recovery metrics."""
        finder = EquilibriumFinder()
        analyzer = PerturbationAnalyzer(finder)
        
        # Create equilibrium point
        equilibrium = EquilibriumPoint(
            coordinates={name: 0.85 for name in finder.paradox_names},
            trinity_score=0.85,
            balance_index=1.0,
            constitutional_alignment=0.85,
            stability=0.95
        )
        
        # Apply small perturbation
        perturbation = {"truth_care": -0.10}
        result = analyzer.test_perturbation(equilibrium, perturbation)
        
        assert "perturbation_magnitude" in result
        assert "recovery_distance" in result
        assert "recovery_ratio" in result
        assert result["perturbation_magnitude"] > 0


# ============ TESTS: CONSTITUTIONAL ALIGNMENT ============

class TestConstitutionalAlignment:
    """Tests for constitutional floor alignment."""
    
    @pytest.mark.asyncio
    async def test_constitutional_vector_generated(self):
        """Test that constitutional alignment vector is generated."""
        trinity = TrinityNine()
        
        agi_delta = {
            "F2_truth": 0.92, "F4_clarity": 0.88, "F7_humility": 0.85,
            "kalman_gain": 0.90, "hierarchy": 0.87, "agency": 0.83,
            "urgency": 0.80, "certainty": 0.89, "unity": 0.86
        }
        asi_omega = {
            "kappa_r": 0.91, "peace_squared": 0.84, "justice": 0.88,
            "reversibility": 0.95, "consent": 0.82, "protection": 0.90,
            "sustainability": 0.85, "doubt": 0.78, "diversity": 0.87
        }
        
        result = await trinity.synchronize(agi_delta, asi_omega, optimize=False)
        
        assert "F1" in result.constitutional_vector or "F2" in result.constitutional_vector
        assert all(0 <= v <= 1 for v in result.constitutional_vector.values())


# ============ INTEGRATION TESTS ============

class TestNineParadoxIntegration:
    """Integration tests for full 9-paradox pipeline."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline_with_equilibrium(self):
        """Test full pipeline achieving equilibrium."""
        agi_delta = {f"F2_truth": 0.90, "F4_clarity": 0.90, "F7_humility": 0.90,
                     "kalman_gain": 0.90, "hierarchy": 0.90, "agency": 0.90,
                     "urgency": 0.90, "certainty": 0.90, "unity": 0.90}
        
        asi_omega = {"kappa_r": 0.90, "peace_squared": 0.90, "justice": 0.90,
                     "reversibility": 0.90, "consent": 0.90, "protection": 0.90,
                     "sustainability": 0.90, "doubt": 0.90, "diversity": 0.90}
        
        result = await trinity_nine_sync(agi_delta, asi_omega, optimize=True)
        
        # With high inputs, should achieve equilibrium or SEAL
        assert result.final_verdict in ["EQUILIBRIUM", "SEAL"]
        assert result.equilibrium.trinity_score >= 0.85


# ============ MAIN ============

if __name__ == "__main__":
    print("=" * 70)
    print("9-PARADOX CONSTITUTIONAL MATRIX TEST SUITE")
    print("=" * 70)
    print("\nRun with: pytest tests/test_nine_paradox.py -v")
