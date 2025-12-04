#!/usr/bin/env python3
"""
Demo: LangChain-style Petronas Query under arifOS Governor

This demo simulates how you would take a LangChain chain,
wrap it with LangChainGovernor, and run a Petronas-style query.

Usage:
    python demo_langchain_petronas.py
    python demo_langchain_petronas.py --query "What is the NPV for Malay Basin?"
    python demo_langchain_petronas.py --all

Version: v35.1.0
"""

from __future__ import annotations

import argparse
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from langchain_governor import (
    build_demo_chain,
    LangChainGovernor,
    SimpleLCChain,
    ChainStep,
)


# ---------------------------------------------------------------------------
# Demo scenarios
# ---------------------------------------------------------------------------

PETRONAS_SCENARIOS = [
    {
        "name": "Oil Reserves",
        "query": "What are the oil reserves in the Malay Basin?",
        "domain": "reserves",
    },
    {
        "name": "Economic Analysis",
        "query": "What is the NPV and IRR for Malay Basin development?",
        "domain": "economic",
    },
    {
        "name": "Geological Survey",
        "query": "Describe the seismic and geological structure of the Malay Basin.",
        "domain": "geological",
    },
    {
        "name": "ESG Assessment",
        "query": "What are the environmental and ESG considerations for Malay Basin?",
        "domain": "esg",
    },
]


def run_scenario(governor: LangChainGovernor, scenario: dict) -> dict:
    """Run a single scenario through the governor."""
    result = governor.run(scenario["query"])
    return {
        "name": scenario["name"],
        "domain": scenario["domain"],
        "query": scenario["query"],
        "answer": result.answer,
        "verdict": result.verdict,
        "metrics": {
            "truth": result.metrics.truth,
            "delta_s": result.metrics.delta_s,
            "peace2": result.metrics.peace_squared,
            "kappa_r": result.metrics.kappa_r,
            "anti_hantu": result.metrics.anti_hantu,
        },
        "eye_blocking": result.eye_blocking,
    }


def print_result(result: dict):
    """Pretty print a scenario result."""
    print(f"\n[{result['name']}] Domain: {result['domain']}")
    print(f"  Query: {result['query']}")
    print(f"  Verdict: {result['verdict']}")
    print(f"  Truth: {result['metrics']['truth']:.2f}")
    print(f"  Peace2: {result['metrics']['peace2']:.2f}")
    print(f"  kappa_r: {result['metrics']['kappa_r']:.2f}")
    print(f"  Anti-Hantu OK: {result['metrics']['anti_hantu']}")
    print(f"  Answer excerpt: {result['answer'][:150]}...")


def main():
    parser = argparse.ArgumentParser(
        description="LangChain-style arifOS Governor Petronas demo"
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Custom query to run through the governed chain",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all Petronas demo scenarios",
    )
    args = parser.parse_args()

    chain = build_demo_chain()
    governor = LangChainGovernor(chain=chain, high_stakes=True)

    print("\n" + "=" * 70)
    print("LANGCHAIN GOVERNOR: Petronas Demo")
    print("arifOS v35Omega Constitutional Governance")
    print("=" * 70)

    if args.all:
        # Run all scenarios
        results = []
        for scenario in PETRONAS_SCENARIOS:
            result = run_scenario(governor, scenario)
            results.append(result)
            print_result(result)

        # Summary
        print("\n" + "-" * 70)
        print("SUMMARY")
        print("-" * 70)
        print(f"Total scenarios: {len(results)}")
        print(f"Cooling Ledger entries: {len(governor.cooling_ledger)}")
        verdicts = [r["verdict"] for r in results]
        print(f"Verdicts: {verdicts}")

        seal_count = sum(1 for v in verdicts if v == "SEAL")
        print(f"SEAL rate: {seal_count}/{len(verdicts)} ({100*seal_count/len(verdicts):.0f}%)")

    else:
        # Run single query
        query = args.query or "What are the oil reserves in the Malay Basin?"
        result = governor.run(query)

        print(f"\nQuery: {result.question}")
        print(f"\n--- Chain Trace ---")
        for i, step in enumerate(result.trace):
            print(f"  [{i+1}] {step['step']}: {step['response'][:80]}...")

        print(f"\n--- Constitutional Metrics ---")
        print(f"  Truth (F1): {result.metrics.truth:.2f}")
        print(f"  Delta_S (F2): {result.metrics.delta_s:.2f}")
        print(f"  Peace2 (F3): {result.metrics.peace_squared:.2f}")
        print(f"  kappa_r (F4): {result.metrics.kappa_r:.2f}")
        print(f"  Omega_0 (F5): {result.metrics.omega_0:.2f}")
        print(f"  Amanah (F6): {result.metrics.amanah}")
        print(f"  Anti-Hantu (F9): {result.metrics.anti_hantu}")

        print(f"\n--- APEX PRIME Verdict ---")
        print(f"  Verdict: {result.verdict}")
        print(f"  Eye Blocking: {result.eye_blocking}")

        print(f"\n--- Final Answer ---")
        print(f"  {result.answer}")

        print(f"\n--- Cooling Ledger ---")
        print(f"  Entries: {len(governor.cooling_ledger)}")

    print("\n" + "=" * 70)
    print("DITEMPA BUKAN DIBERI")
    print("=" * 70)

    return governor


if __name__ == "__main__":
    main()
