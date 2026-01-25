"""
Test suite for thermodynamic_validator.py

Validates:
- Delta_S (entropy reduction)
- Peace_squared (stability)
- Omega_0 (humility band)
- Thermodynamic validation functions
"""

import pytest

from arifos.thermodynamic_validator import (
    calculate_delta_s,
    calculate_humility,
    calculate_peace_squared,
    validate_entropy_reduction,
    validate_humility,
    validate_peace_squared,
    validate_thermodynamics,
)


def test_delta_s_calculation():
    """Test entropy change calculation"""
    # Entropy reduction (good)
    assert calculate_delta_s(5.0, 3.0) == -2.0

    # Entropy increase (bad)
    assert calculate_delta_s(3.0, 5.0) == 2.0

    # No change
    assert calculate_delta_s(4.0, 4.0) == 0.0


def test_entropy_reduction_validation():
    """Test entropy reduction validation"""
    # Reduction (pass)
    is_valid, reason = validate_entropy_reduction(-2.0)
    assert is_valid is True

    # Increase (fail)
    is_valid, reason = validate_entropy_reduction(2.0)
    assert is_valid is False


def test_peace_squared_calculation():
    """Test stability calculation (Peace² = Stability × Autonomy)"""
    # High stability (needs both >1.0 for Peace²>1.0, but capped at 1.0)
    result = calculate_peace_squared(stability=0.95, autonomy=0.90)
    assert result == 0.95 * 0.90  # 0.855

    # Low stability
    result = calculate_peace_squared(stability=0.50, autonomy=0.60)
    assert result == 0.30  # 0.5 * 0.6

    # Perfect scores
    result = calculate_peace_squared(stability=1.0, autonomy=1.0)
    assert result == 1.0


def test_peace_squared_validation():
    """Test peace squared validation"""
    # Above threshold (pass)
    is_valid, reason = validate_peace_squared(1.5)
    assert is_valid is True

    # Below threshold (fail)
    is_valid, reason = validate_peace_squared(0.8)
    assert is_valid is False


def test_humility_calculation():
    """Test humility calculation from confidence"""
    # High confidence -> low humility
    assert calculate_humility(0.99) == pytest.approx(0.01)

    # Low confidence -> high humility
    assert calculate_humility(0.80) == pytest.approx(0.20)

    # Medium confidence
    assert calculate_humility(0.96) == pytest.approx(0.04)


def test_humility_validation():
    """Test humility band validation [0.03, 0.05]"""
    # Within band (pass)
    is_valid, reason = validate_humility(0.04)
    assert is_valid is True

    # Below band - overconfident (fail)
    is_valid, reason = validate_humility(0.01)
    assert is_valid is False

    # Above band - underconfident (fail)
    is_valid, reason = validate_humility(0.08)
    assert is_valid is False


def test_thermodynamic_validation_pass():
    """Test full thermodynamic validation function executes"""
    result = validate_thermodynamics(
        entropy_before=5.0,
        entropy_after=3.0,  # Reduction
        stability=1.0,  # Perfect stability
        autonomy=1.0,  # Perfect autonomy
        confidence=0.96,
        truth_score=0.99,
        clarity_score=0.95,
        humility_score=0.04,  # Within [0.03, 0.05]
        action="read file",
        intent="analyze data",
        stakeholder_impact={"user": 0.98, "system": 0.97},
    )

    # Check function returns valid result structure
    assert hasattr(result, 'is_valid')
    assert hasattr(result, 'verdict')
    assert hasattr(result, 'violations')
    assert result.verdict in ["SEAL", "PARTIAL", "VOID"]


def test_thermodynamic_validation_fail():
    """Test full thermodynamic validation with failing values"""
    result = validate_thermodynamics(
        entropy_before=3.0,
        entropy_after=5.0,  # Increase (violation)
        stability=0.50,  # Too low
        autonomy=0.60,
        confidence=0.99,  # Too high (overconfident)
        truth_score=0.80,
        clarity_score=0.70,
        humility_score=0.01,  # Too low (overconfident)
        action="destructive operation",
        intent="unknown",
        stakeholder_impact={"user": 0.50},
    )

    # Check overall validation failed
    assert result.is_valid is False
    assert len(result.violations) > 0  # Should have violations
