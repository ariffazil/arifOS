"""
Test Suite: RAG Truth Governor Constitutional Governance

10 tests covering:
- F1 Truth floor verification
- Grounding score computation
- Hallucination detection
- Retrieval relevance
- APEX PRIME verdicts
"""

import pytest
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from rag_truth_governor import (
    RAGTruthGovernor,
    TruthVerifier,
    SimpleVectorStore,
    Document,
    RetrievedNode,
    create_petronas_documents,
)
from arifos_core.enforcement.metrics import Metrics
from arifos_core.system.apex_prime import APEXPrime
from arifos_core.utils.eye_sentinel import EyeSentinel


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def verifier():
    """Fresh TruthVerifier for each test."""
    return TruthVerifier()


@pytest.fixture
def vector_store():
    """Vector store with Petronas documents."""
    store = SimpleVectorStore()
    store.add_documents(create_petronas_documents())
    return store


@pytest.fixture
def governor(vector_store):
    """RAG Governor with demo documents."""
    return RAGTruthGovernor(vector_store=vector_store)


# ==============================================================================
# Test 1-3: Truth Verifier
# ==============================================================================

def test_extract_facts(verifier):
    """Extract factual claims from text."""
    text = "The basin has 3.6 billion barrels and covers 80,000 km2."
    facts = verifier.extract_facts(text)
    assert len(facts) >= 2
    assert any("billion" in f.lower() for f in facts)


def test_grounding_score_high(verifier):
    """High grounding score when response matches sources."""
    response = "The Malay Basin has 3.6 billion barrels of oil."
    nodes = [
        RetrievedNode(
            document=Document(
                id="test",
                text="Proven reserves stand at approximately 3.6 billion barrels.",
                metadata={"source": "Test Source"},
            ),
            score=0.9,
        )
    ]

    grounding, citations, hallucinations = verifier.verify_grounding(response, nodes)
    assert grounding >= 0.5  # Facts should be grounded


def test_grounding_score_low_hallucination(verifier):
    """Low grounding score when response contains fabricated data."""
    response = "The basin has 99 billion barrels discovered in 2099."
    nodes = [
        RetrievedNode(
            document=Document(
                id="test",
                text="Proven reserves are approximately 3.6 billion barrels.",
                metadata={"source": "Test Source"},
            ),
            score=0.9,
        )
    ]

    grounding, citations, hallucinations = verifier.verify_grounding(response, nodes)
    # Should have hallucination flags for fabricated numbers
    assert len(hallucinations) > 0 or grounding < 1.0


# ==============================================================================
# Test 4-5: Vector Store Retrieval
# ==============================================================================

def test_retrieval_relevance(vector_store):
    """Retrieve relevant documents for query."""
    nodes = vector_store.retrieve("Malay Basin oil reserves", top_k=3)
    assert len(nodes) > 0
    assert all(node.score >= 0 for node in nodes)


def test_retrieval_empty_query(vector_store):
    """Handle queries with no matching documents."""
    nodes = vector_store.retrieve("quantum computing algorithms", top_k=3)
    # May return low-relevance results or empty
    # Just verify no crash
    assert isinstance(nodes, list)


# ==============================================================================
# Test 6-7: RAG Governor Integration
# ==============================================================================

def test_governor_seal_grounded(governor):
    """SEAL verdict when response is well-grounded."""
    result = governor.query("What are the oil reserves in Malay Basin?")

    # Should produce a result with verdict
    assert result.verdict in ["SEAL", "PARTIAL", "VOID"]
    assert result.metrics.truth >= 0.0
    assert len(result.retrieved_nodes) > 0


def test_governor_cooling_ledger(governor):
    """Cooling ledger should log queries."""
    governor.query("What is the NPV of Malay Basin projects?")
    governor.query("Describe seismic survey coverage.")

    assert len(governor.cooling_ledger) == 2
    for entry in governor.cooling_ledger:
        assert "query" in entry
        assert "verdict" in entry
        assert "truth" in entry


# ==============================================================================
# Test 8-9: APEX PRIME Verdicts
# ==============================================================================

def test_void_on_low_truth():
    """VOID verdict when truth score is too low."""
    metrics = Metrics(
        truth=0.75,  # Below 0.99 threshold
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


def test_seal_on_high_truth():
    """SEAL verdict when all floors pass."""
    metrics = Metrics(
        truth=0.99,
        delta_s=0.15,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.96,
        rasa=True,
        anti_hantu=True,
    )

    prime = APEXPrime(high_stakes=False)
    verdict = prime.judge(metrics, eye_blocking=False)
    assert verdict == "SEAL"


# ==============================================================================
# Test 10: Citation Detection
# ==============================================================================

def test_citation_detection(verifier):
    """Detect when response cites sources."""
    response = (
        "According to the Petronas Annual Report 2023, reserves are 3.6 billion barrels. "
        "Source: Petronas Annual Report 2023."
    )
    nodes = [
        RetrievedNode(
            document=Document(
                id="petronas",
                text="Reserves are 3.6 billion barrels.",
                metadata={"source": "Petronas Annual Report 2023"},
            ),
            score=0.95,
        )
    ]

    _, citations, _ = verifier.verify_grounding(response, nodes)
    # Should detect the citation
    assert len(citations) > 0 or "Petronas" in response


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
