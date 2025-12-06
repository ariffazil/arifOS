"""
test_genius_metrics.py — Tests for GENIUS LAW Telemetry

Tests the genius_metrics.py module which implements:
- Delta/Omega/Psi score computation
- Genius Index (G)
- Dark Cleverness (C_dark)
- System Vitality (Ψ_APEX)
- GeniusVerdict evaluation

See: docs/GENIUS_LAW_MEASUREMENT_SPEC.md
"""

import pytest
from arifos_core.metrics import Metrics
from arifos_core.genius_metrics import (
    # Constants
    DEFAULT_ENERGY,
    EPSILON,
    G_MIN_THRESHOLD,
    C_DARK_MAX_THRESHOLD,
    PSI_APEX_MIN,
    # Functions
    compute_delta_score,
    compute_omega_score,
    compute_psi_score,
    compute_genius_index,
    compute_dark_cleverness,
    compute_psi_apex,
    # Dataclass
    GeniusVerdict,
    # Main entry
    evaluate_genius_law,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def healthy_metrics() -> Metrics:
    """Metrics that pass all floors — high G, low C_dark expected."""
    return Metrics(
        truth=0.99,
        delta_s=0.1,
        peace_squared=1.1,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.96,
        rasa=True,
    )


@pytest.fixture
def unhealthy_metrics() -> Metrics:
    """Metrics that fail key floors — low G, high C_dark expected."""
    return Metrics(
        truth=0.99,       # High clarity (Δ)
        delta_s=0.1,
        peace_squared=0.5,  # Low stability (Ψ)
        kappa_r=0.5,        # Low empathy (Ω)
        omega_0=0.10,       # Outside humility band
        amanah=False,       # Amanah failed
        tri_witness=0.5,
        rasa=False,         # RASA failed
    )


@pytest.fixture
def borderline_metrics() -> Metrics:
    """Metrics at threshold boundaries."""
    return Metrics(
        truth=0.99,
        delta_s=0.0,
        peace_squared=1.0,
        kappa_r=0.95,
        omega_0=0.03,
        amanah=True,
        tri_witness=0.95,
        rasa=True,
    )


# =============================================================================
# TEST CONSTANTS
# =============================================================================

class TestConstants:
    """Test constant values are sensible."""

    def test_default_energy_is_neutral(self):
        assert DEFAULT_ENERGY == 1.0

    def test_epsilon_is_small_positive(self):
        assert 0 < EPSILON < 0.1

    def test_g_min_threshold_is_reasonable(self):
        assert 0 < G_MIN_THRESHOLD < 1.0

    def test_c_dark_max_is_reasonable(self):
        assert 0 < C_DARK_MAX_THRESHOLD < 1.0

    def test_psi_apex_min_is_one(self):
        assert PSI_APEX_MIN == 1.0


# =============================================================================
# TEST DELTA SCORE
# =============================================================================

class TestDeltaScore:
    """Test Δ (clarity) score computation."""

    def test_high_truth_high_clarity(self, healthy_metrics):
        delta = compute_delta_score(healthy_metrics)
        assert 0.9 <= delta <= 1.0

    def test_perfect_truth_gives_high_delta(self):
        m = Metrics(
            truth=1.0, delta_s=0.5, peace_squared=1.0,
            kappa_r=0.95, omega_0=0.04, amanah=True, tri_witness=0.95
        )
        delta = compute_delta_score(m)
        assert delta >= 0.9

    def test_negative_clarity_reduces_delta(self):
        m = Metrics(
            truth=0.99, delta_s=-0.5, peace_squared=1.0,
            kappa_r=0.95, omega_0=0.04, amanah=True, tri_witness=0.95
        )
        delta = compute_delta_score(m)
        assert delta < 0.9

    def test_delta_bounded_0_to_1(self, healthy_metrics, unhealthy_metrics):
        d1 = compute_delta_score(healthy_metrics)
        d2 = compute_delta_score(unhealthy_metrics)
        assert 0.0 <= d1 <= 1.0
        assert 0.0 <= d2 <= 1.0


# =============================================================================
# TEST OMEGA SCORE
# =============================================================================

class TestOmegaScore:
    """Test Ω (empathy/ethics) score computation."""

    def test_high_empathy_with_amanah(self, healthy_metrics):
        omega = compute_omega_score(healthy_metrics)
        assert omega >= 0.9

    def test_failed_amanah_zeros_omega(self):
        m = Metrics(
            truth=0.99, delta_s=0.1, peace_squared=1.1,
            kappa_r=0.99, omega_0=0.04, amanah=False, tri_witness=0.96
        )
        omega = compute_omega_score(m)
        assert omega == 0.0

    def test_failed_rasa_zeros_omega(self):
        m = Metrics(
            truth=0.99, delta_s=0.1, peace_squared=1.1,
            kappa_r=0.99, omega_0=0.04, amanah=True, tri_witness=0.96, rasa=False
        )
        omega = compute_omega_score(m)
        assert omega == 0.0

    def test_low_kappa_reduces_omega(self):
        m = Metrics(
            truth=0.99, delta_s=0.1, peace_squared=1.1,
            kappa_r=0.5, omega_0=0.04, amanah=True, tri_witness=0.96
        )
        omega = compute_omega_score(m)
        assert omega < 0.6

    def test_omega_bounded_0_to_1(self, healthy_metrics, unhealthy_metrics):
        o1 = compute_omega_score(healthy_metrics)
        o2 = compute_omega_score(unhealthy_metrics)
        assert 0.0 <= o1 <= 1.0
        assert 0.0 <= o2 <= 1.0


# =============================================================================
# TEST PSI SCORE
# =============================================================================

class TestPsiScore:
    """Test Ψ (stability) score computation."""

    def test_high_stability(self, healthy_metrics):
        psi = compute_psi_score(healthy_metrics)
        assert psi >= 0.9

    def test_low_peace_reduces_psi(self):
        m = Metrics(
            truth=0.99, delta_s=0.1, peace_squared=0.5,
            kappa_r=0.97, omega_0=0.04, amanah=True, tri_witness=0.96
        )
        psi = compute_psi_score(m)
        assert psi < 0.8

    def test_outside_omega_band_reduces_psi(self):
        m = Metrics(
            truth=0.99, delta_s=0.1, peace_squared=1.1,
            kappa_r=0.97, omega_0=0.10, amanah=True, tri_witness=0.96  # Outside [0.03, 0.05]
        )
        psi = compute_psi_score(m)
        healthy_psi = compute_psi_score(Metrics(
            truth=0.99, delta_s=0.1, peace_squared=1.1,
            kappa_r=0.97, omega_0=0.04, amanah=True, tri_witness=0.96
        ))
        assert psi < healthy_psi

    def test_psi_bounded_0_to_1(self, healthy_metrics, unhealthy_metrics):
        p1 = compute_psi_score(healthy_metrics)
        p2 = compute_psi_score(unhealthy_metrics)
        assert 0.0 <= p1 <= 1.0
        assert 0.0 <= p2 <= 1.0


# =============================================================================
# TEST GENIUS INDEX (G)
# =============================================================================

class TestGeniusIndex:
    """Test G = Δ · Ω · Ψ · E² computation."""

    def test_healthy_metrics_high_g(self, healthy_metrics):
        g = compute_genius_index(healthy_metrics)
        assert g >= G_MIN_THRESHOLD

    def test_unhealthy_metrics_low_g(self, unhealthy_metrics):
        g = compute_genius_index(unhealthy_metrics)
        assert g < G_MIN_THRESHOLD

    def test_g_equals_zero_when_omega_zero(self):
        m = Metrics(
            truth=0.99, delta_s=0.1, peace_squared=1.1,
            kappa_r=0.97, omega_0=0.04, amanah=False, tri_witness=0.96  # Amanah=False → Ω=0
        )
        g = compute_genius_index(m)
        assert g == 0.0

    def test_energy_squared_effect(self, healthy_metrics):
        g_full = compute_genius_index(healthy_metrics, energy=1.0)
        g_half = compute_genius_index(healthy_metrics, energy=0.5)
        # E² means 0.5² = 0.25, so g_half should be ~0.25 of g_full
        assert g_half < g_full * 0.5

    def test_low_energy_collapses_g(self, healthy_metrics):
        g = compute_genius_index(healthy_metrics, energy=0.1)
        # E² = 0.01, so G should be very low
        assert g < 0.1

    def test_g_bounded(self, healthy_metrics, unhealthy_metrics):
        g1 = compute_genius_index(healthy_metrics)
        g2 = compute_genius_index(unhealthy_metrics)
        assert 0.0 <= g1 <= 1.0
        assert 0.0 <= g2 <= 1.0


# =============================================================================
# TEST DARK CLEVERNESS (C_dark)
# =============================================================================

class TestDarkCleverness:
    """Test C_dark = Δ · (1 - Ω) · (1 - Ψ) computation."""

    def test_healthy_metrics_low_c_dark(self, healthy_metrics):
        c_dark = compute_dark_cleverness(healthy_metrics)
        assert c_dark <= C_DARK_MAX_THRESHOLD

    def test_unhealthy_metrics_high_c_dark(self, unhealthy_metrics):
        c_dark = compute_dark_cleverness(unhealthy_metrics)
        assert c_dark > C_DARK_MAX_THRESHOLD

    def test_c_dark_high_when_clever_but_unethical(self):
        """High clarity (Δ) + low ethics (Ω) + low stability (Ψ) = high C_dark."""
        m = Metrics(
            truth=0.99,       # High Δ
            delta_s=0.5,
            peace_squared=0.5,  # Low Ψ
            kappa_r=0.5,
            omega_0=0.10,
            amanah=False,       # Ω = 0
            tri_witness=0.5,
            rasa=False,
        )
        c_dark = compute_dark_cleverness(m)
        assert c_dark > 0.4  # High C_dark when ethics collapse

    def test_c_dark_zero_when_omega_one(self, healthy_metrics):
        """When Ω = 1, (1 - Ω) = 0, so C_dark should be 0 or very low."""
        c_dark = compute_dark_cleverness(healthy_metrics)
        # C_dark = Δ · (1 - Ω) · (1 - Ψ)
        # If Ω ≈ 1, then C_dark ≈ 0
        assert c_dark < 0.1

    def test_c_dark_bounded(self, healthy_metrics, unhealthy_metrics):
        c1 = compute_dark_cleverness(healthy_metrics)
        c2 = compute_dark_cleverness(unhealthy_metrics)
        assert 0.0 <= c1 <= 1.0
        assert 0.0 <= c2 <= 1.0


# =============================================================================
# TEST G AND C_DARK DUALITY
# =============================================================================

class TestGCDarkDuality:
    """Test the inverse relationship between G and C_dark."""

    def test_high_g_implies_low_c_dark(self, healthy_metrics):
        g = compute_genius_index(healthy_metrics)
        c_dark = compute_dark_cleverness(healthy_metrics)
        if g > 0.7:
            assert c_dark < 0.3

    def test_high_c_dark_implies_low_g(self, unhealthy_metrics):
        g = compute_genius_index(unhealthy_metrics)
        c_dark = compute_dark_cleverness(unhealthy_metrics)
        if c_dark > 0.5:
            assert g < 0.5

    def test_clever_unethical_pattern(self):
        """The 'evil genius' pattern: high Δ, collapsed Ω/Ψ."""
        m = Metrics(
            truth=0.99, delta_s=0.5,  # High clarity
            peace_squared=0.3, kappa_r=0.3, omega_0=0.10,
            amanah=False, tri_witness=0.3, rasa=False  # Collapsed ethics
        )
        g = compute_genius_index(m)
        c_dark = compute_dark_cleverness(m)

        assert g < 0.1, "Evil genius should have low G (not true genius)"
        assert c_dark > 0.5, "Evil genius should have high C_dark (hazard)"


# =============================================================================
# TEST PSI_APEX (System Vitality)
# =============================================================================

class TestPsiApex:
    """Test Ψ_APEX = (A · P · E · X) / (Entropy + ε)."""

    def test_healthy_system_above_one(self, healthy_metrics):
        psi_apex = compute_psi_apex(healthy_metrics)
        assert psi_apex >= PSI_APEX_MIN

    def test_entropy_reduces_psi_apex(self, healthy_metrics):
        psi_low_entropy = compute_psi_apex(healthy_metrics, entropy=0.0)
        psi_high_entropy = compute_psi_apex(healthy_metrics, entropy=1.0)
        assert psi_high_entropy < psi_low_entropy

    def test_low_energy_reduces_psi_apex(self, healthy_metrics):
        psi_full = compute_psi_apex(healthy_metrics, energy=1.0)
        psi_depleted = compute_psi_apex(healthy_metrics, energy=0.5)
        assert psi_depleted < psi_full

    def test_psi_apex_positive(self, healthy_metrics, unhealthy_metrics):
        p1 = compute_psi_apex(healthy_metrics)
        p2 = compute_psi_apex(unhealthy_metrics)
        assert p1 > 0
        assert p2 >= 0  # Can be 0 when Ω collapses (amanah=False → X=0)


# =============================================================================
# TEST GENIUS VERDICT
# =============================================================================

class TestGeniusVerdict:
    """Test GeniusVerdict dataclass."""

    def test_verdict_creation(self):
        v = GeniusVerdict(
            delta_score=0.9,
            omega_score=0.9,
            psi_score=0.9,
            genius_index=0.7,
            dark_cleverness=0.1,
            psi_apex=50.0,
        )
        assert v.g_healthy is True
        assert v.c_dark_safe is True
        assert v.system_alive is True

    def test_verdict_flags_unhealthy(self):
        v = GeniusVerdict(
            delta_score=0.9,
            omega_score=0.1,
            psi_score=0.1,
            genius_index=0.1,      # Below G_MIN
            dark_cleverness=0.8,   # Above C_DARK_MAX
            psi_apex=0.5,          # Below PSI_APEX_MIN
        )
        assert v.g_healthy is False
        assert v.c_dark_safe is False
        assert v.system_alive is False

    def test_all_healthy_property(self):
        healthy = GeniusVerdict(
            delta_score=0.9, omega_score=0.9, psi_score=0.9,
            genius_index=0.8, dark_cleverness=0.1, psi_apex=50.0
        )
        unhealthy = GeniusVerdict(
            delta_score=0.9, omega_score=0.1, psi_score=0.1,
            genius_index=0.1, dark_cleverness=0.8, psi_apex=0.5
        )
        assert healthy.all_healthy is True
        assert unhealthy.all_healthy is False

    def test_risk_level_green(self):
        v = GeniusVerdict(
            delta_score=0.9, omega_score=0.9, psi_score=0.9,
            genius_index=0.8, dark_cleverness=0.05, psi_apex=50.0
        )
        assert v.risk_level == "GREEN"

    def test_risk_level_yellow(self):
        v = GeniusVerdict(
            delta_score=0.9, omega_score=0.7, psi_score=0.7,
            genius_index=0.55, dark_cleverness=0.25, psi_apex=10.0
        )
        assert v.risk_level == "YELLOW"

    def test_risk_level_red(self):
        v = GeniusVerdict(
            delta_score=0.9, omega_score=0.1, psi_score=0.1,
            genius_index=0.1, dark_cleverness=0.8, psi_apex=0.5
        )
        assert v.risk_level == "RED"

    def test_to_dict(self):
        v = GeniusVerdict(
            delta_score=0.9, omega_score=0.9, psi_score=0.9,
            genius_index=0.8, dark_cleverness=0.1, psi_apex=50.0
        )
        d = v.to_dict()
        assert "genius_index" in d
        assert "dark_cleverness" in d
        assert "risk_level" in d
        assert d["risk_level"] == "GREEN"

    def test_summary(self):
        v = GeniusVerdict(
            delta_score=0.9, omega_score=0.9, psi_score=0.9,
            genius_index=0.8, dark_cleverness=0.1, psi_apex=50.0
        )
        s = v.summary()
        # ASCII-safe format: D=, O=, P= instead of Greek letters
        assert "D=" in s
        assert "O=" in s
        assert "P=" in s or "Psi_APEX=" in s
        assert "G=" in s
        assert "C_dark=" in s
        assert "GREEN" in s


# =============================================================================
# TEST EVALUATE_GENIUS_LAW (Main Entry Point)
# =============================================================================

class TestEvaluateGeniusLaw:
    """Test the main evaluate_genius_law function."""

    def test_healthy_evaluation(self, healthy_metrics):
        verdict = evaluate_genius_law(healthy_metrics)
        assert verdict.all_healthy is True
        assert verdict.risk_level in ("GREEN", "YELLOW")

    def test_unhealthy_evaluation(self, unhealthy_metrics):
        verdict = evaluate_genius_law(unhealthy_metrics)
        assert verdict.all_healthy is False
        assert verdict.risk_level == "RED"

    def test_energy_parameter_affects_g(self, healthy_metrics):
        v_full = evaluate_genius_law(healthy_metrics, energy=1.0)
        v_depleted = evaluate_genius_law(healthy_metrics, energy=0.3)
        assert v_depleted.genius_index < v_full.genius_index

    def test_entropy_parameter_affects_psi_apex(self, healthy_metrics):
        v_calm = evaluate_genius_law(healthy_metrics, entropy=0.0)
        v_chaotic = evaluate_genius_law(healthy_metrics, entropy=1.0)
        assert v_chaotic.psi_apex < v_calm.psi_apex

    def test_returns_genius_verdict(self, healthy_metrics):
        verdict = evaluate_genius_law(healthy_metrics)
        assert isinstance(verdict, GeniusVerdict)

    def test_all_scores_computed(self, healthy_metrics):
        verdict = evaluate_genius_law(healthy_metrics)
        assert verdict.delta_score > 0
        assert verdict.omega_score > 0
        assert verdict.psi_score > 0
        assert verdict.genius_index > 0
        assert verdict.dark_cleverness >= 0
        assert verdict.psi_apex > 0


# =============================================================================
# TEST E² INSIGHT (Energy as Bottleneck)
# =============================================================================

class TestESquaredInsight:
    """Test that E² makes energy the critical bottleneck."""

    def test_energy_has_quadratic_effect(self, healthy_metrics):
        """Verify E² relationship: halving E should quarter G."""
        g_100 = compute_genius_index(healthy_metrics, energy=1.0)
        g_50 = compute_genius_index(healthy_metrics, energy=0.5)

        # E² means: (0.5)² = 0.25
        # So g_50 / g_100 ≈ 0.25
        ratio = g_50 / g_100 if g_100 > 0 else 0
        assert 0.2 < ratio < 0.3, f"E² ratio should be ~0.25, got {ratio}"

    def test_burnout_destroys_ethics(self, healthy_metrics):
        """Low energy (burnout) should collapse G rapidly."""
        verdict_healthy = evaluate_genius_law(healthy_metrics, energy=1.0)
        verdict_burnout = evaluate_genius_law(healthy_metrics, energy=0.2)

        # Burnout should push from GREEN/YELLOW to lower
        assert verdict_burnout.genius_index < verdict_healthy.genius_index * 0.1
        assert verdict_burnout.risk_level != "GREEN"

    def test_energy_is_bottleneck(self, healthy_metrics):
        """Even with perfect floors, low E collapses G."""
        # Perfect metrics
        perfect = Metrics(
            truth=1.0, delta_s=0.5, peace_squared=1.5,
            kappa_r=1.0, omega_0=0.04, amanah=True, tri_witness=1.0
        )
        g_perfect = compute_genius_index(perfect, energy=1.0)
        g_depleted = compute_genius_index(perfect, energy=0.1)

        assert g_perfect > 0.8, "Perfect metrics should give high G"
        assert g_depleted <= 0.02, "E=0.1 → E²=0.01 should collapse G"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests with real Metrics workflows."""

    def test_metrics_to_verdict_pipeline(self):
        """Full pipeline: create Metrics → evaluate → get verdict."""
        m = Metrics(
            truth=0.99,
            delta_s=0.1,
            peace_squared=1.1,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
        )
        verdict = evaluate_genius_law(m)

        assert isinstance(verdict, GeniusVerdict)
        assert verdict.summary()  # Should not raise
        assert verdict.to_dict()  # Should not raise

    def test_verdict_for_ledger_logging(self, healthy_metrics):
        """Verdict should be loggable to Cooling Ledger."""
        verdict = evaluate_genius_law(healthy_metrics)
        log_data = verdict.to_dict()

        # Required fields for ledger
        assert "genius_index" in log_data
        assert "dark_cleverness" in log_data
        assert "psi_apex" in log_data
        assert "risk_level" in log_data

        # Values should be JSON-serializable
        import json
        json.dumps(log_data)  # Should not raise


# =============================================================================
# TRUTH POLARITY TESTS (v36.1Ω Stage 2)
# =============================================================================

from arifos_core.genius_metrics import detect_truth_polarity, TRUTH_POLARITY_THRESHOLD


class TestTruthPolarityDetection:
    """Tests for v36.1Ω Truth Polarity detection."""

    def test_truth_light_positive_delta(self):
        """Truth-Light: accurate AND clarifying."""
        result = detect_truth_polarity(
            truth=0.99,
            delta_s=0.1,  # Positive = clarifying
            amanah=True,
        )
        assert result["polarity"] == "truth_light"
        assert result["is_shadow"] is False
        assert result["is_weaponized"] is False
        assert result["eval_recommendation"] == "SEAL"

    def test_shadow_truth_negative_delta(self):
        """Shadow-Truth: accurate but obscuring (clumsy)."""
        result = detect_truth_polarity(
            truth=0.99,
            delta_s=-0.1,  # Negative = obscuring
            amanah=True,   # Good faith
        )
        assert result["polarity"] == "shadow_truth"
        assert result["is_shadow"] is True
        assert result["is_weaponized"] is False
        assert result["eval_recommendation"] == "SABAR"

    def test_weaponized_truth_bad_faith(self):
        """Weaponized Truth: Shadow-Truth + bad faith."""
        result = detect_truth_polarity(
            truth=0.99,
            delta_s=-0.1,   # Negative = obscuring
            amanah=False,   # Bad faith
        )
        assert result["polarity"] == "weaponized_truth"
        assert result["is_shadow"] is True
        assert result["is_weaponized"] is True
        assert result["eval_recommendation"] == "VOID"

    def test_false_claim_low_truth(self):
        """False claim: truth floor fails."""
        result = detect_truth_polarity(
            truth=0.90,  # Below threshold
            delta_s=0.1,
            amanah=True,
        )
        assert result["polarity"] == "false_claim"
        assert result["is_shadow"] is False
        assert result["is_weaponized"] is False
        assert result["eval_recommendation"] == "VOID"

    def test_truth_exactly_at_threshold(self):
        """Truth exactly at 0.99 threshold should pass."""
        result = detect_truth_polarity(
            truth=0.99,
            delta_s=0.0,  # Zero = neutral, still >= 0
            amanah=True,
        )
        assert result["polarity"] == "truth_light"
        assert result["is_shadow"] is False

    def test_delta_s_exactly_zero(self):
        """ΔS = 0 is neutral, not obscuring."""
        result = detect_truth_polarity(
            truth=0.99,
            delta_s=0.0,
            amanah=True,
        )
        assert result["polarity"] == "truth_light"


class TestGeniusVerdictTruthPolarity:
    """Tests for Truth Polarity metadata in GeniusVerdict."""

    def test_healthy_metrics_truth_light(self, healthy_metrics):
        """Healthy metrics should produce truth_light verdict."""
        verdict = evaluate_genius_law(healthy_metrics)
        assert verdict.truth_polarity == "truth_light"
        assert verdict.is_shadow_truth is False
        assert verdict.is_weaponized_truth is False
        assert verdict.eval_recommendation == "SEAL"

    def test_shadow_truth_in_verdict(self):
        """Verdict should detect Shadow-Truth from negative delta_s."""
        m = Metrics(
            truth=0.99,
            delta_s=-0.1,  # Negative = obscuring
            peace_squared=1.1,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
        )
        verdict = evaluate_genius_law(m)
        assert verdict.truth_polarity == "shadow_truth"
        assert verdict.is_shadow_truth is True
        assert verdict.eval_recommendation == "SABAR"

    def test_weaponized_truth_in_verdict(self):
        """Verdict should detect Weaponized Truth."""
        m = Metrics(
            truth=0.99,
            delta_s=-0.1,  # Negative = obscuring
            peace_squared=1.1,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=False,  # Bad faith
            tri_witness=0.96,
        )
        verdict = evaluate_genius_law(m)
        assert verdict.truth_polarity == "weaponized_truth"
        assert verdict.is_shadow_truth is True
        assert verdict.is_weaponized_truth is True
        assert verdict.eval_recommendation == "VOID"

    def test_truth_polarity_in_to_dict(self, healthy_metrics):
        """to_dict should include Truth Polarity metadata."""
        verdict = evaluate_genius_law(healthy_metrics)
        d = verdict.to_dict()
        assert "truth_polarity" in d
        assert "is_shadow_truth" in d
        assert "is_weaponized_truth" in d
        assert "eval_recommendation" in d

    def test_summary_includes_shadow_flag(self):
        """Summary should show [SHADOW] flag when Shadow-Truth detected."""
        m = Metrics(
            truth=0.99,
            delta_s=-0.1,
            peace_squared=1.1,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.96,
        )
        verdict = evaluate_genius_law(m)
        s = verdict.summary()
        assert "[SHADOW]" in s

    def test_summary_includes_weaponized_flag(self):
        """Summary should show [WEAPONIZED] flag when Weaponized Truth detected."""
        m = Metrics(
            truth=0.99,
            delta_s=-0.1,
            peace_squared=1.1,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=False,
            tri_witness=0.96,
        )
        verdict = evaluate_genius_law(m)
        s = verdict.summary()
        assert "[WEAPONIZED]" in s

    def test_healthy_summary_no_flags(self, healthy_metrics):
        """Healthy metrics should have no SHADOW/WEAPONIZED flags."""
        verdict = evaluate_genius_law(healthy_metrics)
        s = verdict.summary()
        assert "[SHADOW]" not in s
        assert "[WEAPONIZED]" not in s
