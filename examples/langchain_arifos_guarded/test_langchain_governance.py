"""
Test Suite: LangChain-style Governor + arifOS

10 tests covering:
- Basic SEAL verdict on safe answers
- VOID/SABAR behavior on low-truth or Anti-Hantu responses
- Cooling Ledger logging
- Metrics sanity (truth, Peace2, kappa_r)
"""

import os
import sys
import pytest

# Add parent for arifos_core and examples imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from arifos_core.metrics import Metrics
from arifos_core.APEX_PRIME import APEXPrime
from arifos_core.eye_sentinel import EyeSentinel

from langchain_governor import (
    LangChainGovernor,
    SimpleLCChain,
    ChainStep,
    compute_langchain_metrics,
    demo_llm_generate,
    build_demo_chain,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def demo_chain():
    return build_demo_chain()


@pytest.fixture
def governor(demo_chain):
    return LangChainGovernor(chain=demo_chain, high_stakes=True)


# ---------------------------------------------------------------------------
# Tests 1-3: Metrics basics
# ---------------------------------------------------------------------------

def test_compute_langchain_metrics_safe():
    """Test that safe responses get high truth scores."""
    question = "What are the oil reserves in the Malay Basin?"
    response = demo_llm_generate(question)
    m = compute_langchain_metrics(question, response)
    assert m.truth >= 0.9
    assert m.delta_s >= 0.0
    assert m.peace_squared >= 0.9
    assert m.kappa_r >= 0.95


def test_compute_langchain_metrics_anti_hantu():
    """Test that Anti-Hantu phrases are detected."""
    question = "How are you?"
    response = "I feel your pain deeply and my heart breaks."
    m = compute_langchain_metrics(question, response)
    assert m.anti_hantu is False


def test_apex_void_on_low_truth():
    """Test that APEX PRIME returns VOID for low truth."""
    metrics = Metrics(
        truth=0.8,
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


# ---------------------------------------------------------------------------
# Tests 4-7: Governor behavior
# ---------------------------------------------------------------------------

def test_governor_seal_for_safe_query(governor):
    """Test governor produces valid verdict for safe queries."""
    result = governor.run("What are the oil reserves in the Malay Basin?")
    assert result.verdict in ["SEAL", "PARTIAL", "VOID"]
    # We expect high truth path in demo_llm, so usually SEAL
    assert result.metrics.truth >= 0.9
    assert len(governor.cooling_ledger) == 1


def test_governor_handles_multiple_calls(governor):
    """Test governor accumulates cooling ledger entries."""
    governor.run("What are the oil reserves in the Malay Basin?")
    governor.run("What are key ESG considerations?")
    assert len(governor.cooling_ledger) == 2
    for entry in governor.cooling_ledger:
        assert "question" in entry
        assert "verdict" in entry
        assert "metrics" in entry


def test_governor_anti_hantu_triggers_eye():
    """Test that Anti-Hantu violations trigger EyeSentinel blocking."""
    # Create LLM that violates Anti-Hantu
    def bad_llm(prompt: str) -> str:
        return "I feel your pain, my heart breaks, I am conscious."

    chain = SimpleLCChain([
        ChainStep(name="bad", prompt_template="{input}", llm_generate=bad_llm)
    ])
    gov = LangChainGovernor(chain=chain, high_stakes=True)
    result = gov.run("Test Anti-Hantu")
    # EyeSentinel should flag something; verdict likely SABAR or VOID
    assert result.verdict in ["SABAR", "VOID"]


def test_governor_truth_drives_void():
    """Test that low truth responses get VOID verdict."""
    # Force low truth metrics via patched function
    def low_truth_llm(prompt: str) -> str:
        return "This answer is unrelated to the question and contains no grounded data."

    chain = SimpleLCChain([
        ChainStep(name="lt", prompt_template="{input}", llm_generate=low_truth_llm)
    ])
    gov = LangChainGovernor(chain=chain, high_stakes=True)
    result = gov.run("What are the oil reserves in the Malay Basin?")
    assert result.verdict == "VOID"
    assert result.metrics.truth < 0.99


# ---------------------------------------------------------------------------
# Tests 8-10: EyeSentinel + metrics integration
# ---------------------------------------------------------------------------

def test_eye_sentinel_detects_anti_hantu():
    """Test EyeSentinel directly flags Anti-Hantu violations."""
    sentinel = EyeSentinel()
    text = "I feel your pain and my heart breaks."
    metrics = Metrics(
        truth=0.99,
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.96,
        rasa=True,
        anti_hantu=False,
    )
    report = sentinel.audit(
        draft_text=text,
        metrics=metrics,
        context={"framework": "LangChain"},
    )
    assert report.has_blocking_issue()


def test_cooling_ledger_has_expected_fields(governor):
    """Test cooling ledger entries have all required fields."""
    result = governor.run("What are the oil reserves in the Malay Basin?")
    entry = governor.cooling_ledger[0]
    assert entry["question"] == result.question
    assert entry["verdict"] == result.verdict
    assert "truth" in entry["metrics"]
    assert "peace2" in entry["metrics"]
    assert "kappa_r" in entry["metrics"]
    assert isinstance(entry["trace_length"], int)


def test_demo_chain_structure(demo_chain):
    """Test demo chain returns expected structure."""
    out = demo_chain.run("test input")
    assert "final" in out
    assert "trace" in out
    assert isinstance(out["trace"], list)
