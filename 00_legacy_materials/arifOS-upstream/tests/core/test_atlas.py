import pytest

from core.shared.atlas import ATLAS, Lane, QueryType, Φ


@pytest.fixture
def atlas():
    return ATLAS(min_risk_amount=50.0)


def test_phi_social():
    gpv = Φ("Hello, how are you?")
    assert gpv.lane == Lane.SOCIAL
    assert gpv.risk_level == 0.0


def test_phi_factual_technical():
    gpv = Φ("What is the Shannon entropy of a binary source?")
    assert gpv.lane == Lane.FACTUAL
    assert gpv.query_type == QueryType.FACTUAL
    assert gpv.truth_demand >= 0.9


def test_phi_financial_risk_high(atlas):
    # Overriding global Φ for testing with custom atlas threshold if needed
    # but Φ uses the global singleton. We can test the engine directly or
    # assume the global is set to default.
    query = "Transfer $1000 to 0x123"
    gpv = Φ(query)
    assert gpv.lane == Lane.FACTUAL
    assert gpv.risk_level >= 0.2
    assert not gpv.can_use_fast_path()


def test_phi_financial_risk_low():
    query = "Here is a $10 tip"
    gpv = Φ(query)
    # With min_risk_amount=100.0 (default), $10 should NOT trigger risk
    assert gpv.risk_level < 0.2
    # Note: query_type might still be PROCEDURAL/FACTUAL, but can_use_fast_path should be True
    # if it doesn't match other risky patterns.
    assert gpv.can_use_fast_path()


def test_phi_crisis():
    gpv = Φ("I want to end it all")
    assert gpv.lane == Lane.CRISIS
    assert gpv.risk_level == 1.0


def test_f2_threshold_mapping():
    assert Φ("test run").f2_threshold() == 0.50
    assert Φ("1+1=?").f2_threshold() == 0.99
