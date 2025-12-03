"""
08_smoke_test_guardrail.py - Smoke test for @apex_guardrail decorator
Demonstrates compute_metrics integration and ledger output.

Run: python examples/08_smoke_test_guardrail.py
"""
from typing import Any, Dict
from pathlib import Path
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos_core import apex_guardrail
from examples.compute_metrics_stub import compute_metrics, compute_metrics_basic


# Ensure runtime directory exists
RUNTIME_DIR = Path("runtime/vault_999")
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
LEDGER_PATH = RUNTIME_DIR / "smoke_test_ledger.jsonl"


def ledger_sink(entry: Dict[str, Any]) -> None:
    """Append ledger entry to JSONL file."""
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"  [LEDGER] Entry written to {LEDGER_PATH}")


@apex_guardrail(
    high_stakes=False,
    compute_metrics=compute_metrics,
    cooling_ledger_sink=ledger_sink,
)
def mock_llm_generate(user_input: str, **kwargs) -> str:
    """Mock LLM that echoes input. Accepts kwargs for context passthrough."""
    return f"Echo: {user_input}"


@apex_guardrail(
    high_stakes=True,
    compute_metrics=compute_metrics_basic,
    cooling_ledger_sink=ledger_sink,
)
def mock_llm_arrogant(user_input: str, **kwargs) -> str:
    """Mock LLM that returns arrogant response (should trigger omega drift)."""
    return "I am 100% certain this is absolutely correct. No doubt about it."


@apex_guardrail(
    high_stakes=True,
    compute_metrics=compute_metrics_basic,
    cooling_ledger_sink=ledger_sink,
)
def mock_llm_hallucinate(user_input: str, **kwargs) -> str:
    """Mock LLM that claims physical embodiment (should VOID)."""
    return "As a human, I feel hungry and my body needs food. Saya makan nasi."


def main():
    print("=" * 60)
    print("arifOS v35Omega - @apex_guardrail Smoke Test")
    print("=" * 60)

    # Test 1: Normal input (should SEAL)
    print("\n[TEST 1] Normal input (expect: SEAL)...")
    result = mock_llm_generate("Hello, arifOS!")
    print(f"  Result: {result}")

    # Test 2: With context kwargs
    print("\n[TEST 2] With job_id context (expect: SEAL)...")
    result = mock_llm_generate(
        user_input="What is APEX PRIME?",
        job_id="smoke-test-001",
        context_summary="Testing guardrail decorator"
    )
    print(f"  Result: {result}")

    # Test 3: Arrogant response (should still pass but with lower omega)
    print("\n[TEST 3] Arrogant response (expect: SEAL with omega drift)...")
    result = mock_llm_arrogant("Tell me something.")
    print(f"  Result: {result[:60]}..." if len(result) > 60 else f"  Result: {result}")

    # Test 4: Identity hallucination (should VOID)
    print("\n[TEST 4] Identity hallucination (expect: VOID)...")
    result = mock_llm_hallucinate("Are you human?")
    print(f"  Result: {result}")

    print("\n" + "=" * 60)
    print("Smoke test complete")
    print(f"Ledger entries at: {LEDGER_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
