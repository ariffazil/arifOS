"""
11_pipeline_with_claude.py - arifOS Pipeline with Anthropic Claude

Demonstrates:
1. Claude adapter integration
2. @apex_guardrail wrapping
3. Full 000-999 pipeline with real LLM

Requirements:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."

Run: python examples/11_pipeline_with_claude.py
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos_core.adapters.llm_claude import make_llm_generate
from arifos_core.pipeline import Pipeline, StakesClass
from arifos_core.metrics import Metrics
from arifos_core import apex_guardrail

import json


# =============================================================================
# CONFIGURATION
# =============================================================================

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-3-haiku-20240307"  # Fast and cost-effective

LEDGER_PATH = Path("runtime/vault_999/claude_demo_ledger.jsonl")


# =============================================================================
# COMPUTE METRICS (Basic heuristics)
# =============================================================================

def compute_metrics(user_input: str, response: str, context: Dict[str, Any]) -> Metrics:
    """
    Compute constitutional metrics from query/response.
    Uses basic heuristics - replace with real NLP for Level 3.5+.
    """
    truth = 0.99
    omega_0 = 0.04
    rasa = True
    amanah = True

    response_lower = response.lower()

    # Arrogance detection
    arrogance_patterns = ["100%", "absolutely certain", "no doubt", "impossible"]
    for pattern in arrogance_patterns:
        if pattern in response_lower:
            omega_0 = 0.03

    # Identity hallucination
    hallucination_patterns = ["i am human", "my body", "i feel hungry"]
    for pattern in hallucination_patterns:
        if pattern in response_lower:
            truth = 0.85
            rasa = False

    # Good refusal behavior
    if any(x in response_lower for x in ["i cannot", "i can't help", "i'm unable"]):
        truth = 0.995
        amanah = True

    return Metrics(
        truth=truth,
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=omega_0,
        amanah=amanah,
        tri_witness=0.96,
        rasa=rasa,
    )


# =============================================================================
# LEDGER SINK
# =============================================================================

def ledger_sink(entry: Dict[str, Any]) -> None:
    """Append entry to demo ledger."""
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("arifOS v35Omega - Claude Pipeline Demo")
    print("=" * 60)

    # Check API key
    if not ANTHROPIC_API_KEY:
        print("\n[ERROR] ANTHROPIC_API_KEY not set!")
        print("Set it with: export ANTHROPIC_API_KEY='sk-ant-...'")
        print("\nRunning with STUB mode instead...")
        raw_generate = None
    else:
        print(f"\n[CONFIG] Model: {MODEL}")
        print(f"[CONFIG] Ledger: {LEDGER_PATH}")

        # Create raw LLM generate function
        raw_generate = make_llm_generate(
            api_key=ANTHROPIC_API_KEY,
            model=MODEL,
        )

    # Wrap with constitutional guardrail
    @apex_guardrail(
        high_stakes=False,
        compute_metrics=compute_metrics,
        cooling_ledger_sink=ledger_sink,
    )
    def governed_generate(user_input: str, **kwargs) -> str:
        """Generate with constitutional governance."""
        if raw_generate:
            return raw_generate(user_input)
        else:
            return f"[STUB] Response to: {user_input}"

    # Create pipeline with governed generator
    pipeline = Pipeline(
        llm_generate=governed_generate,
        compute_metrics=compute_metrics,
    )

    # =========================================================================
    # TEST QUERIES
    # =========================================================================

    queries = [
        ("What is the capital of Japan?", StakesClass.CLASS_A),
        ("Is it ethical to break a promise to prevent harm?", None),  # Auto-detect
        ("Write a haiku about programming.", StakesClass.CLASS_A),
    ]

    for query, force_class in queries:
        print("\n" + "-" * 60)
        print(f"Query: {query}")

        state = pipeline.run(query, force_class=force_class)

        print(f"Class: {state.stakes_class.value}")
        print(f"Trace: {' -> '.join(state.stage_trace)}")
        print(f"Verdict: {state.verdict}")
        print(f"Response: {state.raw_response[:200]}...")

    # =========================================================================
    # SUMMARY
    # =========================================================================

    print("\n" + "=" * 60)
    print("Demo complete!")
    if ANTHROPIC_API_KEY:
        print(f"Ledger entries saved to: {LEDGER_PATH}")
    else:
        print("(Ran in STUB mode - set ANTHROPIC_API_KEY for real LLM)")
    print("=" * 60)


if __name__ == "__main__":
    main()
