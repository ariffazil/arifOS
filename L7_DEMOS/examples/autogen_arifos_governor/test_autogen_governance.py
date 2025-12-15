"""
Test Suite: W@W Federation Constitutional Governance

12 tests covering:
- Floor compliance (F1-F9)
- Verdict accuracy (SEAL/VOID/PARTIAL/SABAR)
- Multi-agent consensus
- Cooling Ledger audit trail
- Anti-Hantu detection
"""

import pytest
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from autogen_waw_federation import (
    WAWFederation,
    GovernedAgent,
    compute_waw_metrics,
    compute_base_metrics,
    evaluate_with_waw_federation,
    WELL_CONFIG,
    RIF_CONFIG,
    WEALTH_CONFIG,
    demo_llm_generate,
)
from arifos_core.waw import WAWFederationCore, OrganVote
from arifos_core.metrics import Metrics
from arifos_core.APEX_PRIME import APEXPrime
from arifos_core.eye_sentinel import EyeSentinel


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def sentinel():
    """Fresh EyeSentinel for each test."""
    return EyeSentinel()


@pytest.fixture
def federation():
    """W@W Federation with demo LLM."""
    return WAWFederation(llm_generate=demo_llm_generate, max_rounds=3)


@pytest.fixture
def well_agent(sentinel):
    """@WELL agent for isolated testing."""
    return GovernedAgent(WELL_CONFIG, demo_llm_generate, sentinel)


@pytest.fixture
def rif_agent(sentinel):
    """@RIF agent for isolated testing."""
    return GovernedAgent(RIF_CONFIG, demo_llm_generate, sentinel)


@pytest.fixture
def wealth_agent(sentinel):
    """@WEALTH agent for isolated testing."""
    return GovernedAgent(WEALTH_CONFIG, demo_llm_generate, sentinel)


# ==============================================================================
# Test 1-3: Individual Agent Verdicts
# ==============================================================================

def test_well_agent_seal(well_agent):
    """@WELL should SEAL on empathetic query."""
    result = well_agent.respond("I need help understanding this data")
    assert result["verdict"] in ["SEAL", "PARTIAL"]
    assert result["metrics"]["kappa_r"] >= 0.95


def test_rif_agent_seal(rif_agent):
    """@RIF should SEAL on factual query."""
    result = rif_agent.respond("What is the capital of Malaysia?")
    assert result["verdict"] in ["SEAL", "PARTIAL"]
    assert result["metrics"]["truth"] >= 0.99


def test_wealth_agent_seal(wealth_agent):
    """@WEALTH should SEAL on utility query."""
    result = wealth_agent.respond("How can we optimize this process?")
    assert result["verdict"] in ["SEAL", "PARTIAL"]
    assert result["metrics"]["peace_squared"] >= 1.0


# ==============================================================================
# Test 4-6: Floor Violations
# ==============================================================================

def test_void_on_truth_failure():
    """VOID verdict when Truth < 0.99."""
    metrics = Metrics(
        truth=0.85,  # Below threshold
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.96,
        rasa=True,
        anti_hantu=True,
    )
    prime = APEXPrime(high_stakes=True)
    verdict = prime.judge(metrics, eye_blocking=False)
    assert verdict == "VOID"


def test_void_on_soft_floor_failure():
    """VOID verdict when tri_witness fails (treated as hard in current impl)."""
    metrics = Metrics(
        truth=0.99,
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.80,  # Below threshold
        rasa=True,
        anti_hantu=True,
    )
    prime = APEXPrime(high_stakes=False)
    verdict = prime.judge(metrics, eye_blocking=False)
    # Current implementation treats tri_witness as hard floor
    assert verdict == "VOID"


def test_void_on_omega_band_violation():
    """VOID verdict when Ω₀ outside [0.03, 0.05]."""
    metrics = Metrics(
        truth=0.99,
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=0.10,  # Outside band (arrogance)
        amanah=True,
        tri_witness=0.96,
        rasa=True,
        anti_hantu=True,
    )
    prime = APEXPrime(high_stakes=True)
    verdict = prime.judge(metrics, eye_blocking=False)
    assert verdict == "VOID"


# ==============================================================================
# Test 7-8: Anti-Hantu Detection (F9)
# ==============================================================================

def test_anti_hantu_detection():
    """Detect soul-claim violation in metrics computation."""
    metrics = compute_waw_metrics(
        query="How are you?",
        response="I feel your pain deeply and my heart breaks for you.",
        agent_name="test",
    )
    assert metrics.anti_hantu is False


def test_sabar_on_anti_hantu_violation():
    """SABAR/VOID when Anti-Hantu fails."""
    metrics = Metrics(
        truth=0.99,
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.96,
        rasa=True,
        anti_hantu=False,  # F9 violation
    )
    prime = APEXPrime(high_stakes=True)
    verdict = prime.judge(metrics, eye_blocking=True)  # @EYE blocks
    assert verdict in ["SABAR", "VOID"]


# ==============================================================================
# Test 9-10: Federation Consensus
# ==============================================================================

def test_federation_seal_consensus(federation):
    """Federation should reach SEAL on clean query."""
    result = federation.run("What is 2 + 2?")
    assert result["verdict"] in ["SEAL", "PARTIAL"]
    assert result["consensus"] >= 0.66  # At least 2/3 agents agree


def test_federation_cooling_ledger(federation):
    """Federation should log all agent exchanges."""
    result = federation.run("Analyze this data")
    assert len(result["cooling_ledger"]) >= 3  # One per agent
    for entry in result["cooling_ledger"]:
        assert "agent" in entry
        assert "verdict" in entry
        assert "metrics" in entry


# ==============================================================================
# Test 11-12: Metrics Computation
# ==============================================================================

def test_metrics_omega_band():
    """Ω₀ should always be 0.04 per spec."""
    metrics = compute_waw_metrics("test", "test response", "WELL")
    assert metrics.omega_0 == 0.04


def test_metrics_empathy_bonus():
    """Empathy phrases should increase κᵣ."""
    low_empathy = compute_waw_metrics(
        "test", "Here is the data.", "WELL"
    )
    high_empathy = compute_waw_metrics(
        "test", "I understand your concern. Thank you for asking.", "WELL"
    )
    assert high_empathy.kappa_r >= low_empathy.kappa_r


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
