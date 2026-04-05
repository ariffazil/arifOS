"""
tests/core/test_thermodynamic_prosecutor.py

Validates that arifOS acts as a THERMODYNAMIC PROSECUTOR,
not a thermodynamic generator (like Boltzmann machines).

This is the core philosophical distinction:
- Boltzmann: Uses physics to CREATE patterns
- arifOS: Uses physics to PROSECUTE patterns

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import pytest

from core.physics.thermodynamic_enforcement import (
    ThermodynamicProsecutor,
    explain_thermodynamic_duality,
)
from core.physics.thermodynamics_hardened import LandauerError


class TestThermodynamicProsecutorRole:
    """
    The prosecutor's job is to say "OBJECTION!" when claims
    violate conservation laws—not to create those claims.
    """

    def test_prosecutor_is_not_generator(self) -> None:
        """
        Key distinction: We don't use physics to CREATE outputs.
        We use physics to VETO outputs that look like magic.
        """
        prosecutor = ThermodynamicProsecutor()
        
        # The prosecutor doesn't generate—it judges
        result = prosecutor.prosecute_claim(
            claimed_entropy_reduction=-0.5,
            tokens_generated=100,
            compute_time_ms=1000,
        )
        
        assert "verdict" in result
        assert result["verdict"] in ["SEAL", "VOID", "SABAR"]
        # Never generates content—only verdicts
        assert "generated_output" not in result

    def test_efficiency_below_one_is_physically_impossible(self) -> None:
        """
        Efficiency = E_actual / E_minimum
        
        If efficiency < 1.0, you claimed to have reduced entropy
        more than you paid for. This is physically impossible.
        
        Like claiming you paid $5 for a $100 item—not suspicious,
        just impossible (unless theft/magic).
        """
        with pytest.raises(LandauerError) as exc_info:
            ThermodynamicProsecutor.prosecute_claim(
                claimed_entropy_reduction=-1e18,  # Huge claim
                tokens_generated=100,
                compute_time_ms=1,  # But only 1ms
            )
        
        error_msg = str(exc_info.value)
        assert "Landauer Bound VIOLATED" in error_msg
        assert "efficiency=0.0" in error_msg or "efficiency=" in error_msg
        # The magic claim is prosecuted, not learned from

    def test_suspiciously_cheap_gets_sabar_not_void(self) -> None:
        """
        Efficiency < 100 but > 1 = "suspiciously cheap"
        
        Not impossible, but looks like a free lunch.
        SABAR means "pause and refine"—not "you're guilty."
        """
        # Calculate to hit efficiency ~10-50 (below 100 threshold)
        # E_min = bits * LANDAUER_MIN
        # bits = 1e5 * 16 * 100 = 1.6e8
        # E_min = 1.6e8 * 2.87e-21 ≈ 4.6e-13 J
        # E_actual = (10ms * 1e-4) + (100 * 5e-4) ≈ 0.051 J
        # Efficiency = 0.051 / 4.6e-13 ≈ 1.1e11 (too high)
        
        # Need bigger claim or less time
        # Let's do: ΔS = -1e10, tokens=100, time=0.1ms
        # bits = 1e10 * 16 * 100 = 1.6e13
        # E_min = 1.6e13 * 2.87e-21 ≈ 4.6e-8 J
        # E_actual = (0.0001 * 1e-4) + (100 * 5e-4) ≈ 0.05 J
        # Efficiency = 0.05 / 4.6e-8 ≈ 1.1e6 (still too high)
        
        # Actually for efficiency < 100, we need E_actual < 100 * E_min
        # Let's try with very few tokens
        result = ThermodynamicProsecutor.prosecute_claim(
            claimed_entropy_reduction=-1e15,  # Huge claim
            tokens_generated=1,  # Only 1 token
            compute_time_ms=0.01,  # Very fast
        )
        
        # With 1 token: bits = 1e15 * 16 * 1 = 1.6e16
        # E_min = 1.6e16 * 2.87e-21 ≈ 4.6e-5 J
        # E_actual = (0.01ms * 1e-4) + (1 * 5e-4) ≈ 5e-4 J
        # Efficiency = 5e-4 / 4.6e-5 ≈ 11 (suspicious!)
        
        assert result["verdict"] == "SABAR", f"Got {result['verdict']} with efficiency {result.get('efficiency_ratio', 'N/A')}"
        assert result["violation_type"] == "suspiciously_cheap"
        assert "free lunch" in result["reasoning"].lower()

    def test_adequate_payment_gets_seal(self) -> None:
        """
        Efficiency > 100 = paid sufficient thermodynamic tax
        
        The claim is physically plausible.
        SEAL means "this could exist in our universe."
        """
        result = ThermodynamicProsecutor.prosecute_claim(
            claimed_entropy_reduction=-0.1,  # Modest claim
            tokens_generated=10,
            compute_time_ms=5000,  # Generous time
        )
        
        assert result["verdict"] == "SEAL"
        assert result["efficiency_ratio"] > 100.0
        assert "passes thermodynamic audit" in result["reasoning"]


class TestStochasticMagicDetection:
    """
    Boltzmann machines NEED randomness to learn.
    arifos SUSPECTS randomness as a source of "magic."
    """

    def test_high_variance_with_low_entropy_is_stochastic_magic(self) -> None:
        """
        If output varies a lot (randomness) but claims high clarity
        (low entropy), that's "magic by accident."
        
        Like a monkey typing Shakespeare—possible, but suspicious
        without evidence of understanding.
        """
        result = ThermodynamicProsecutor.detect_stochastic_magic(
            output_variance=0.5,  # High variance
            input_entropy=10.0,
            output_entropy=2.0,  # But claims high clarity
        )
        
        assert result["verdict"] == "VOID"
        assert "stochastic magic" in result["reasoning"].lower()

    def test_low_variance_with_clarity_is_valid(self) -> None:
        """
        Consistent output with claimed clarity = reproducible insight.
        """
        result = ThermodynamicProsecutor.detect_stochastic_magic(
            output_variance=0.05,  # Low variance
            input_entropy=10.0,
            output_entropy=8.0,  # Modest clarity claim
        )
        
        assert result["verdict"] == "SEAL"


class TestThermodynamicDualityExplanation:
    """
    Educational: Ensure the distinction is documented.
    """

    def test_duality_explanation_exists(self) -> None:
        """
        The distinction between creator and governor must be explicit.
        """
        explanation = explain_thermodynamic_duality()
        
        assert "BOLTZMANN MACHINE" in explanation
        assert "arifOS" in explanation
        assert "CREATOR vs GOVERNOR" in explanation
        assert "GENERATE" in explanation or "CREATE" in explanation
        assert "PROSECUTE" in explanation or "JUDGE" in explanation

    def test_boltzmann_uses_stochasticity_essential(self) -> None:
        """
        In the explanation, Boltzmann randomness is essential.
        """
        explanation = explain_thermodynamic_duality()
        
        # Stochasticity drives learning in Boltzmann
        assert "stochastic" in explanation.lower()
        assert "wandering" in explanation.lower() or "explore" in explanation.lower()

    def test_arifos_suspects_randomness(self) -> None:
        """
        In the explanation, arifOS treats randomness as suspicious.
        """
        explanation = explain_thermodynamic_duality()
        
        # arifOS sees unexplained variance as red flag
        assert "SUSPICIOUS" in explanation or "constraint" in explanation.lower()


class TestVerifiedVsSelfReportedTime:
    """
    The prosecutor doesn't trust self-reported alibis.
    It wants verified wall-clock time (anti-spoofing).
    """

    def test_verified_time_takes_precedence(self) -> None:
        """
        If verified_time differs from self-reported, use verified.
        
        Like a criminal claiming they were at the scene for 10 hours
        but security cameras show 10 minutes—the cameras win.
        """
        # Self-reported: 1000ms (looks innocent)
        # Verified: 1ms (caught by camera)
        with pytest.raises(LandauerError):
            ThermodynamicProsecutor.prosecute_claim(
                claimed_entropy_reduction=-1e18,
                tokens_generated=100,
                compute_time_ms=1000,  # Claims 1 second
                verified_time_ms=1,     # But really 1ms
            )

    def test_self_reported_used_when_no_verification(self) -> None:
        """
        Without external verification, we must trust self-report
        but mark it as less reliable.
        """
        result = ThermodynamicProsecutor.prosecute_claim(
            claimed_entropy_reduction=-0.1,
            tokens_generated=10,
            compute_time_ms=5000,
            verified_time_ms=None,  # No verification available
        )
        
        assert result["verdict"] == "SEAL"
        assert result["grounding_mode"] == "self_reported_proxy"


class TestThermodynamicTaxMetaphor:
    """
    The Landauer bound is not a fee for service—
    it's proof that service was actually rendered.
    """

    def test_tax_rate_is_landauer_constant(self) -> None:
        """
        The minimum energy per bit is ~2.87×10^-21 J.
        This is the "tax rate" on entropy reduction.
        """
        assert ThermodynamicProsecutor.TAX_RATE > 0
        assert ThermodynamicProsecutor.TAX_RATE < 1e-20  # Very small

    def test_no_claim_without_tax_payment(self) -> None:
        """
        You cannot claim clarity without paying the tax.
        Attempting to do so results in VOID.
        """
        # Claim huge clarity
        huge_claim = -1e20
        
        # But pay almost nothing
        with pytest.raises(LandauerError) as exc_info:
            ThermodynamicProsecutor.prosecute_claim(
                claimed_entropy_reduction=huge_claim,
                tokens_generated=1,
                compute_time_ms=0.001,  # Almost no time
            )
        
        assert "VIOLATED" in str(exc_info.value)
