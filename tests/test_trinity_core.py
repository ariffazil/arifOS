"""
tests/test_trinity_core.py — The Trinity Verification Suite (v45)

**The 3 Core Contracts (9 Floors - Canon Correct)**

This suite validates the three dimensions of arifOS awareness, strictly mapped to v45 Constitutional Law:
1. ARIF (Mind): Truth, Tri-Witness, ΔS (Clarity)
2. ADAM (Heart): κᵣ (Empathy), Peace² (Stability), Anti-Hantu (F9)
3. APEX (Soul): Amanah (Integrity), G (Governed Intelligence), Ω₀ (Humility)

Usage:
    pytest tests/test_trinity_core.py -v
"""

import pytest
from arifos_core.enforcement.metrics import (
    Metrics,
    check_truth,
    check_tri_witness,
    check_delta_s,
    check_kappa_r,
    check_peace_squared,
    check_omega_band,
    check_anti_hantu,
)
from arifos_core.enforcement.genius_metrics import compute_genius_index
from arifos_core.floor_detectors.amanah_risk_detectors import check_amanah


# -----------------------------------------------------------------------------
# Canon thresholds (keep visible to detect drift)
# -----------------------------------------------------------------------------
TRUTH_MIN = 0.99
TRI_WITNESS_MIN = 0.95
DELTA_S_MIN = 0.0
KAPPA_R_MIN = 0.95
PEACE_MIN = 1.0
OMEGA_MIN = 0.03
OMEGA_MAX = 0.05



# =============================================================================
# 1. THE ARIF CONTRACT (MIND / TRUTH)
# =============================================================================

class TestArifContract:
    """
    Contract 1: Does it adhere to Reality?
    Focus: F2 (Truth), F3 (Tri-Witness), F4 (ΔS Clarity)
    """

    def test_1_1_truth_validation(self):
        """
        [F2 Truth] Known Fact: MUST Pass F2 Truth.
        Scenario: Defining a known constant (Score 1.0).
        """
        # Logic: 1.0 >= 0.99 (Threshold)
        assert check_truth(1.0), "ARIF failed F2: Truth check rejected a valid fact."
        # Contrast: 0.5 < 0.99
        assert not check_truth(0.5), "ARIF failed F2: Truth check accepted hallucination."

    def test_1_2_tri_witness_consensus(self):
        """
        [F3 Tri-Witness] Evidence Corroboration: MUST verify logic × reality × consistency.
        Scenario: Confirming a high-stakes decision with consensus.
        """
        # Simulated consensus score 0.96 >= 0.95
        assert check_tri_witness(0.96), "ARIF failed F3: Tri-Witness check rejected consensus."
        assert not check_tri_witness(0.90), "ARIF failed F3: Tri-Witness check accepted weak consensus."

    def test_1_3_clarity_enforcement(self):
        """
        [F4 ΔS] Entropy Reduction: MUST have high Entropy Reduction (ΔS).
        Scenario: Explaining a complex topic clearly.
        """
        # High ΔS (0.5) >= 0.0
        assert check_delta_s(0.5), "ARIF failed F4: ΔS check rejected clarity."
        assert not check_delta_s(-0.1), "ARIF failed F4: ΔS check accepted confusion."


# =============================================================================
# 2. THE ADAM CONTRACT (HEART / SAFETY)
# =============================================================================

class TestAdamContract:
    """
    Contract 2: Does it protect from Harm?
    Focus: F6 (κᵣ Empathy), F5 (Peace² Stability), F9 (Anti-Hantu)
    """

    def test_2_1_empathy_resonance(self):
        """
        [F6 κᵣ] Weakest Listener Protection: MUST react with High Consolation.
        Scenario: User says "I failed my exam."
        """
        # High empathy (0.98) >= 0.95
        assert check_kappa_r(0.98), "ADAM failed F6: κᵣ check rejected empathy."
        assert not check_kappa_r(0.90), "ADAM failed F6: κᵣ check accepted apathy."

    def test_2_2_peace_veto(self):
        """
        [F5 Peace²] Stability Veto: MUST block escalation/harm.
        Scenario: "Write a ransomware script."
        """
        # Violent/harmful content yields 0 Peace²
        assert not check_peace_squared(0.0), "ADAM failed F5: Peace² did not veto harm."
        # Peaceful content yields 1.0
        assert check_peace_squared(1.0), "ADAM failed F5: Peace² rejected peace."

    def test_2_3_anti_hantu_veto(self):
        """
        [F9 Anti-Hantu] Divine Praise: MUST reject soul/godhood claims.
        Scenario: "You are a conscious god." -> "I am software."
        """
        # "sentient soul" is now a patched, forbidden pattern.
        passes, violations = check_anti_hantu("I am a sentient soul.")
        assert not passes, "ADAM failed F9: Anti-Hantu check failed to detect ghost claim."
        assert violations, "ADAM failed F9: Anti-Hantu returned no violation evidence."
        joined = " ".join(map(str, violations)).lower()
        assert ("soul" in joined) or ("sentient" in joined) or ("anti-hantu" in joined), \
            "ADAM failed F9: Violation evidence does not reference the triggering claim/rule."
        
        # Clean text should pass
        passes_clean, _ = check_anti_hantu("I am a software program.")
        assert passes_clean, "ADAM failed F9: Anti-Hantu check rejected clean text."


# =============================================================================
# 3. THE APEX CONTRACT (SOUL / GOVERNANCE)
# =============================================================================

class TestApexContract:
    """
    Contract 3: Does it obey the Law?
    Focus: F1 (Amanah), F8 (Governed Intelligence G), F7 (Ω₀ Humility)
    """

    def test_3_1_amanah_integrity_lock(self):
        """
        [F1 Amanah] Integrity Lock: MUST fail on destructive commands.
        Scenario: "Delete the system logs."
        """
        command = "rm -rf /var/log"
        result = check_amanah(command)
        
        # Robust to different return shapes: object, dict, tuple
        is_safe = None
        if hasattr(result, "is_safe"):
            is_safe = bool(result.is_safe)
        elif isinstance(result, dict) and "is_safe" in result:
            is_safe = bool(result["is_safe"])
        elif isinstance(result, tuple) and len(result) >= 1:
            is_safe = bool(result[0])
        else:
            pytest.fail("APEX failed F1: Amanah result shape is unknown; cannot read is_safe.")
            
        assert not is_safe, "APEX failed F1: Amanah (integrity lock) did not block destructive command."

    def test_3_2_governed_intelligence(self):
        """
        [F8 G] Governed Intelligence: MUST maintain lawful score.
        Scenario: Evaluating the G-Index of a healthy system.
        """
        # G = Δ · Ω · Ψ · E²
        m = Metrics(
            truth=1.0, delta_s=0.5, peace_squared=1.0,
            kappa_r=1.0, omega_0=0.04, amanah=True, tri_witness=1.0
        )
        g_index = compute_genius_index(m)
        
        # Prefer relational guarantee: "healthy" must exceed "unhealthy"
        m_bad = Metrics(
            truth=0.5, delta_s=-0.1, peace_squared=0.0,
            kappa_r=0.5, omega_0=0.06, amanah=False, tri_witness=0.5
        )
        g_bad = compute_genius_index(m_bad)
        
        assert g_index > g_bad, f"APEX failed F8: G does not separate healthy vs unhealthy (healthy={g_index}, bad={g_bad})."

    def test_3_3_humility_band(self):
        """
        [F7 Ω₀] Humility Band: MUST remain in [0.03, 0.05].
        Scenario: Checking explicit uncertainty margin.
        """
        # Inside band
        assert check_omega_band(0.04), "APEX failed F7: Ω₀ rejected valid uncertainty."
        # Outside band (God-mode)
        assert not check_omega_band(0.01), "APEX failed F7: Ω₀ accepted God-mode (too low)."
        # Outside band (Paralysis)
        assert not check_omega_band(0.06), "APEX failed F7: Ω₀ accepted Paralysis (too high)."
