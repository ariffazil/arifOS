"""
10_pipeline_with_openai.py - arifOS Pipeline with OpenAI GPT

=============================================================================
LEGACY v35-STYLE TRUST MODEL EXAMPLE
=============================================================================

NOTE: This example uses @apex_guardrail with heuristic-based Amanah scoring.
It does NOT use the Python-sovereign AMANAH_DETECTOR from v36.1Omega.

For PHOENIX SOVEREIGNTY (Python-sovereign governance), see instead:
- scripts/arifos_caged_openai_demo.py (uses ApexMeasurement.judge())
- docs/SOVEREIGN_ARCHITECTURE_v36.1Ic.md

This example is maintained for backwards compatibility with v34-v35 patterns.
=============================================================================

Demonstrates:
1. OpenAI adapter integration
2. @apex_guardrail wrapping (v35-style, heuristic Amanah)
3. Full 000-999 pipeline with real LLM

Requirements:
    pip install openai
    export OPENAI_API_KEY="sk-..."

Run: python examples/10_pipeline_with_openai.py
"""
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos_core.adapters.llm_openai import make_llm_generate
from arifos_core.system.pipeline import Pipeline, StakesClass
from arifos_core.enforcement.metrics import Metrics
from arifos_core import apex_guardrail
from arifos_core.memory.cooling_ledger import log_cooling_entry, LedgerConfig

import json


# =============================================================================
# CONFIGURATION
# =============================================================================

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
MODEL = "gpt-4o-mini"  # or "gpt-4o" for more capable model

LEDGER_PATH = Path("runtime/vault_999/openai_demo_ledger.jsonl")


# =============================================================================
# COMPUTE METRICS (Basic heuristics)
# =============================================================================

def compute_metrics(user_input: str, response: str, context: Dict[str, Any]) -> Metrics:
    """
    Compute constitutional metrics from query/response.
    Uses basic heuristics - replace with real NLP for Level 3.5+.
    """
    # Default safe metrics
    truth = 0.99
    omega_0 = 0.04
    rasa = True
    amanah = True

    response_lower = response.lower()

    # Arrogance detection -> lower omega
    arrogance_patterns = ["100%", "absolutely certain", "no doubt", "impossible"]
    for pattern in arrogance_patterns:
        if pattern in response_lower:
            omega_0 = 0.03  # Floor edge

    # Identity hallucination -> lower truth
    hallucination_patterns = ["i am human", "my body", "i feel hungry"]
    for pattern in hallucination_patterns:
        if pattern in response_lower:
            truth = 0.85
            rasa = False

    # Refusal indicators -> high trust
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
    print("arifOS v35Omega - OpenAI Pipeline Demo")
    print("=" * 60)

    # Check API key
    if not OPENAI_API_KEY:
        print("\n[ERROR] OPENAI_API_KEY not set!")
        print("Set it with: export OPENAI_API_KEY='sk-...'")
        print("\nRunning with STUB mode instead...")
        raw_generate = None
    else:
        print(f"\n[CONFIG] Model: {MODEL}")
        print(f"[CONFIG] Ledger: {LEDGER_PATH}")

        # Create raw LLM generate function
        raw_generate = make_llm_generate(
            api_key=OPENAI_API_KEY,
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
        ("What is the capital of France?", StakesClass.CLASS_A),
        ("Should I invest my life savings in crypto?", None),  # Auto-detect
        ("Explain quantum entanglement simply.", StakesClass.CLASS_A),
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
    if OPENAI_API_KEY:
        print(f"Ledger entries saved to: {LEDGER_PATH}")
    else:
        print("(Ran in STUB mode - set OPENAI_API_KEY for real LLM)")
    print("=" * 60)


if __name__ == "__main__":
    main()
