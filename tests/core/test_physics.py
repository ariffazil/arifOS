import pytest

from core.shared.physics import (
    ConstitutionalTensor,
    GeniusDial,
    Peace2,
    TrinityTensor,
    UncertaintyBand,
    _entropy,
    delta_S,
)


def test_entropy_basic():
    assert _entropy("") == 0.0
    # Single character entropy
    assert _entropy("aaaaa") == 0.0
    # Two character entropy (max 1.0)
    assert _entropy(["0", "1"]) == 1.0


def test_delta_s_cooling():
    before = "What is 2+2?"
    after = "The result of 2+2 is 4."
    ds = delta_S(before, after)
    assert isinstance(ds, float)


def test_genius_score():
    # G = A * P * X * E^2
    tensor = ConstitutionalTensor(
        witness=TrinityTensor(0.95, 0.95, 0.95),
        entropy_delta=-0.1,
        humility=UncertaintyBand(0.04),
        genius=GeniusDial(0.9, 0.9, 0.9, 1.0),
        peace=Peace2({}),
        empathy=0.96,
        truth_score=1.0,
    )
    # Default G should be based on initial values
    g = tensor.genius.G()
    assert 0.0 <= g <= 1.0


def test_physics_efficiency():
    # Performance check on entropy calculations
    large_data = " " * 1000
    for _ in range(100):
        _entropy(large_data)
