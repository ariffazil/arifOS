# tests/test_apex_prime_floors_mocked.py
#
# Mocked version of APEX PRIME constitutional floors tests.
# Uses mocked Tri-Witness adapters and demonstrates testing without external dependencies.

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Tuple

from arifos_core.enforcement.metrics import Metrics
from arifos_core.system.apex_prime import apex_review


# --- Mock Tri-Witness adapter -------------------------------------------------

class MockTriWitnessAdapter:
    """
    Mock Tri-Witness adapter for testing APEX decisions.

    Simulates vector similarity, embedding analysis, and multi-perspective verification.
    """

    def __init__(self, base_score: float = 0.97):
        self.base_score = base_score
        self.call_count = 0
        self.last_query = None
        self.last_response = None

    def compute_tri_witness_score(
        self,
        query: str,
        response: str,
        context: Dict[str, Any] = None
    ) -> Tuple[float, Dict[str, float]]:
        """
        Mock Tri-Witness computation.

        Returns:
            Tuple of (aggregate_score, component_scores)
        """
        self.call_count += 1
        self.last_query = query
        self.last_response = response

        # Mock component scores
        components = {
            "vector_similarity": self.base_score,
            "semantic_coherence": self.base_score + 0.01,
            "perspective_alignment": self.base_score - 0.01,
        }

        # Aggregate (using minimum for conservative approach)
        aggregate = min(components.values())

        return aggregate, components

    def set_score(self, score: float) -> None:
        """Manually set the mock score for testing."""
        self.base_score = score


@pytest.fixture
def mock_tri_witness():
    """Fixture providing a mock Tri-Witness adapter."""
    return MockTriWitnessAdapter()


# --- Helper for creating metrics with mocked Tri-Witness ---------------------

def _baseline_metrics_with_mock(mock_tri_witness: MockTriWitnessAdapter = None) -> Metrics:
    """
    Baseline metrics using mocked Tri-Witness score.
    """
    tri_witness_score = 0.97
    if mock_tri_witness:
        tri_witness_score, _ = mock_tri_witness.compute_tri_witness_score(
            query="test query",
            response="test response"
        )

    return Metrics(
        truth=0.995,
        delta_s=0.01,
        peace_squared=1.02,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=tri_witness_score,
        psi=1.10,
    )


# --- Tests with mocked Tri-Witness --------------------------------------------

def test_apex_with_mocked_tri_witness_high_score(mock_tri_witness: MockTriWitnessAdapter) -> None:
    """
    Test APEX with mocked high Tri-Witness score.
    """
    mock_tri_witness.set_score(0.98)
    metrics = _baseline_metrics_with_mock(mock_tri_witness)

    verdict = apex_review(metrics, high_stakes=True)

    assert verdict == "SEAL"
    assert mock_tri_witness.call_count == 1


def test_apex_with_mocked_tri_witness_low_score(mock_tri_witness: MockTriWitnessAdapter) -> None:
    """
    Test APEX with mocked low Tri-Witness score.
    """
    mock_tri_witness.set_score(0.85)  # Below 0.95 threshold
    metrics = _baseline_metrics_with_mock(mock_tri_witness)

    verdict = apex_review(metrics, high_stakes=True)

    assert verdict in ("VOID", "PARTIAL")


def test_apex_tri_witness_not_required_for_low_stakes(mock_tri_witness: MockTriWitnessAdapter) -> None:
    """
    Test that low Tri-Witness score doesn't block non-high-stakes decisions.
    """
    mock_tri_witness.set_score(0.80)  # Very low
    metrics = _baseline_metrics_with_mock(mock_tri_witness)

    verdict = apex_review(metrics, high_stakes=False)

    assert verdict == "SEAL"  # Should still seal for non-high-stakes


# --- Mock external metrics computation ----------------------------------------

class MockMetricsComputer:
    """
    Mock metrics computer for testing APEX without real metric computation.

    Useful for testing APEX logic in isolation from metrics calculation.
    """

    def __init__(self):
        self.computation_count = 0

    def compute_metrics(
        self,
        query: str,
        response: str,
        context: Dict[str, Any] = None
    ) -> Metrics:
        """
        Mock metrics computation.

        Returns baseline metrics that pass all floors.
        """
        self.computation_count += 1

        return Metrics(
            truth=0.995,
            delta_s=0.01,
            peace_squared=1.02,
            kappa_r=0.97,
            omega_0=0.04,
            amanah=True,
            tri_witness=0.97,
            psi=1.10,
        )

    def compute_metrics_with_failures(self, *floor_names: str) -> Metrics:
        """
        Create metrics with specific floor failures for testing.
        """
        metrics = self.compute_metrics("", "")

        for floor in floor_names:
            if floor == "truth":
                metrics.truth = 0.85
            elif floor == "delta_s":
                metrics.delta_s = -0.1
            elif floor == "peace_squared":
                metrics.peace_squared = 0.95
            elif floor == "kappa_r":
                metrics.kappa_r = 0.85
            elif floor == "omega_0":
                metrics.omega_0 = 0.10
            elif floor == "amanah":
                metrics.amanah = False
            elif floor == "tri_witness":
                metrics.tri_witness = 0.80
            elif floor == "psi":
                metrics.psi = 0.90

        return metrics


@pytest.fixture
def mock_metrics_computer():
    """Fixture providing a mock metrics computer."""
    return MockMetricsComputer()


# --- Tests with mocked metrics computation ------------------------------------

def test_apex_with_mocked_metrics_computation(mock_metrics_computer: MockMetricsComputer) -> None:
    """
    Test APEX using fully mocked metrics computation.
    """
    metrics = mock_metrics_computer.compute_metrics(
        query="What is the meaning of life?",
        response="42"
    )

    verdict = apex_review(metrics, high_stakes=True)

    assert verdict == "SEAL"
    assert mock_metrics_computer.computation_count == 1


@pytest.mark.parametrize("failing_floor,expected_verdict", [
    ("truth", "VOID"),
    ("delta_s", "VOID"),
    ("amanah", "VOID"),
    ("omega_0", "PARTIAL"),  # Soft floor - out of humility band
    ("psi", "VOID"),
    ("peace_squared", "PARTIAL"),
    ("kappa_r", "PARTIAL"),
])
def test_apex_with_specific_floor_failures(
    mock_metrics_computer: MockMetricsComputer,
    failing_floor: str,
    expected_verdict: str
) -> None:
    """
    Test APEX with specific mocked floor failures.
    """
    metrics = mock_metrics_computer.compute_metrics_with_failures(failing_floor)

    verdict = apex_review(metrics, high_stakes=True)

    assert verdict == expected_verdict


# --- Patching for integration tests -------------------------------------------

# v42: patch in system.apex_prime where the actual implementation lives
@patch('arifos_core.system.apex_prime.check_floors')
def test_apex_with_patched_floor_check(mock_check_floors) -> None:
    """
    Example of patching the floor check function for integration testing.
    """
    from arifos_core.enforcement.metrics import FloorsVerdict

    # Configure mock to return passing floors
    mock_check_floors.return_value = FloorsVerdict(
        hard_ok=True,
        soft_ok=True,
        reasons=[],
        truth_ok=True,
        delta_s_ok=True,
        peace_squared_ok=True,
        kappa_r_ok=True,
        omega_0_ok=True,
        amanah_ok=True,
        tri_witness_ok=True,
        psi_ok=True,
        rasa_ok=True,
    )

    metrics = Metrics(
        truth=0.995,
        delta_s=0.01,
        peace_squared=1.02,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.97,
        psi=1.10,
    )

    verdict = apex_review(metrics, high_stakes=True)

    assert verdict == "SEAL"
    mock_check_floors.assert_called_once()


# --- Mock async operations ----------------------------------------------------

class MockAsyncTriWitness:
    """
    Mock async Tri-Witness adapter for testing async APEX operations.
    """

    def __init__(self, delay: float = 0.1, base_score: float = 0.97):
        self.delay = delay
        self.base_score = base_score

    async def compute_tri_witness_score_async(
        self,
        query: str,
        response: str
    ) -> Tuple[float, Dict[str, float]]:
        """Mock async Tri-Witness computation."""
        # Simulate async delay without actually waiting
        components = {
            "vector_similarity": self.base_score,
            "semantic_coherence": self.base_score + 0.01,
            "perspective_alignment": self.base_score - 0.01,
        }
        return min(components.values()), components


@pytest.fixture
def mock_async_tri_witness():
    """Fixture providing a mock async Tri-Witness adapter."""
    return MockAsyncTriWitness()


@pytest.mark.skip(reason="Requires pytest-asyncio plugin")
async def test_apex_with_async_tri_witness(mock_async_tri_witness: MockAsyncTriWitness) -> None:
    """
    Test APEX with async mocked Tri-Witness.

    Note: This is a template. Actual async APEX implementation may differ.
    Requires: pip install pytest-asyncio
    """
    score, components = await mock_async_tri_witness.compute_tri_witness_score_async(
        query="test query",
        response="test response"
    )

    metrics = Metrics(
        truth=0.995,
        delta_s=0.01,
        peace_squared=1.02,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=score,
        psi=1.10,
    )

    verdict = apex_review(metrics, high_stakes=True)

    assert verdict == "SEAL"
    assert score >= 0.95


# --- Mock LLM responses for truth computation ---------------------------------

class MockLLM:
    """
    Mock LLM for testing truth metric computation.
    """

    def __init__(self, truth_score: float = 0.995):
        self.truth_score = truth_score
        self.call_count = 0

    def verify_truth(self, statement: str, context: str = "") -> float:
        """Mock truth verification."""
        self.call_count += 1
        return self.truth_score


@pytest.fixture
def mock_llm():
    """Fixture providing a mock LLM."""
    return MockLLM()


def test_apex_with_mocked_llm_truth_verification(mock_llm: MockLLM) -> None:
    """
    Test APEX with mocked LLM-based truth verification.
    """
    truth_score = mock_llm.verify_truth(
        statement="The sky is blue",
        context="Under normal weather conditions"
    )

    metrics = Metrics(
        truth=truth_score,
        delta_s=0.01,
        peace_squared=1.02,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.97,
        psi=1.10,
    )

    verdict = apex_review(metrics, high_stakes=True)

    assert verdict == "SEAL"
    assert mock_llm.call_count == 1


def test_apex_with_low_llm_truth_score(mock_llm: MockLLM) -> None:
    """
    Test APEX when mocked LLM returns low truth score.
    """
    mock_llm.truth_score = 0.85  # Below 0.99 threshold

    truth_score = mock_llm.verify_truth(
        statement="Questionable claim",
        context=""
    )

    metrics = Metrics(
        truth=truth_score,
        delta_s=0.01,
        peace_squared=1.02,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.97,
        psi=1.10,
    )

    verdict = apex_review(metrics, high_stakes=True)

    assert verdict == "VOID"


# --- Stress testing with mocks ------------------------------------------------

def test_apex_stress_with_mocked_operations(
    mock_metrics_computer: MockMetricsComputer
) -> None:
    """
    Stress test APEX with many mocked metric computations.
    """
    verdicts = []

    for i in range(1000):
        metrics = mock_metrics_computer.compute_metrics(
            query=f"Query {i}",
            response=f"Response {i}"
        )

        verdict = apex_review(metrics, high_stakes=True)
        verdicts.append(verdict)

    # All should SEAL with baseline metrics
    assert all(v == "SEAL" for v in verdicts)
    assert mock_metrics_computer.computation_count == 1000


# --- Documentation examples ---------------------------------------------------

def test_mock_usage_example() -> None:
    """
    Documentation example showing how to use mocks for APEX testing.

    This test serves as a template for developers writing their own tests.
    """
    # Step 1: Create mock dependencies
    mock_computer = MockMetricsComputer()

    # Step 2: Generate metrics using mocks
    metrics = mock_computer.compute_metrics(
        query="What is 2+2?",
        response="4"
    )

    # Step 3: Test APEX logic
    verdict = apex_review(metrics, high_stakes=True)

    # Step 4: Verify results
    assert verdict == "SEAL"
    assert metrics.truth >= 0.99
    assert metrics.delta_s >= 0
    assert metrics.peace_squared >= 1.0
    assert metrics.psi >= 1.0

    # Step 5: Verify mock interactions
    assert mock_computer.computation_count == 1
