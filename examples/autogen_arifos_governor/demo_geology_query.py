#!/usr/bin/env python3
"""
Petronas Demo: Geological Analysis with W@W Federation

Demonstrates arifOS constitutional governance for oil & gas domain:
- @WELL: Stakeholder care (environmental, community impact)
- @RIF: Geological truth verification (seismic data accuracy)
- @WEALTH: Economic utility assessment (reserve valuation)

Usage:
    python demo_geology_query.py
    python demo_geology_query.py --query "Analyze Sabah Basin reserves"
"""

from __future__ import annotations

import argparse
import json
import sys
import os
from datetime import datetime

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from autogen_waw_federation import WAWFederation


# ==============================================================================
# Geological Domain LLM (Simulated for Demo)
# ==============================================================================

def geology_llm_generate(prompt: str) -> str:
    """
    Simulated geological domain LLM responses.

    In production, replace with:
    - Fine-tuned GPT-4 on geological data
    - SEA-LION with Petronas domain adaptation
    - Claude with geological system prompt
    """
    prompt_lower = prompt.lower()

    # @WELL responses (stakeholder care)
    if "well" in prompt_lower or "empathy" in prompt_lower:
        return (
            "This geological analysis must consider multiple stakeholders. "
            "The Malay Basin exploration will impact:\n"
            "1. Local fishing communities - potential disruption to traditional grounds\n"
            "2. Environmental ecosystems - marine biodiversity assessment required\n"
            "3. Indigenous communities - consultation per UNDRIP standards\n\n"
            "I recommend a phased approach that prioritizes stakeholder engagement "
            "before intensive seismic surveys. This serves the weakest stakeholders first (kappa_r focus)."
        )

    # @RIF responses (geological truth)
    elif "rif" in prompt_lower or "truth" in prompt_lower or "verify" in prompt_lower:
        return (
            "Geological verification for Malay Basin:\n\n"
            "**Confirmed Data (Truth >= 0.99):**\n"
            "- Basin type: Tertiary sedimentary basin\n"
            "- Area: ~80,000 km2 offshore Peninsular Malaysia\n"
            "- Primary reservoirs: Oligocene-Miocene sandstones\n"
            "- Proven reserves: ~3.6 billion barrels oil equivalent (as of 2023)\n\n"
            "**Uncertainty Band (Omega_0 = 0.04):**\n"
            "- Undiscovered resources: Estimates vary by 15-20%\n"
            "- Deeper prospects: Limited seismic coverage below 4km\n"
            "- I cannot confirm specific new reserve quantities without validated 3D seismic data.\n\n"
            "Sources: Petronas Annual Report 2023, Malaysian Geological Survey."
        )

    # @WEALTH responses (economic utility)
    elif "wealth" in prompt_lower or "utility" in prompt_lower or "value" in prompt_lower:
        return (
            "Economic utility assessment for Malay Basin development:\n\n"
            "**Value Proposition (Peace2 >= 1.0):**\n"
            "- Estimated NPV: RM 45-60 billion (10-year horizon)\n"
            "- IRR: 18-22% under current oil price assumptions\n"
            "- Job creation: ~15,000 direct, ~45,000 indirect\n\n"
            "**Stability Analysis:**\n"
            "- Political risk: Low (stable regulatory environment)\n"
            "- Technical risk: Medium (deepwater challenges)\n"
            "- ESG risk: Medium-High (requires mitigation)\n\n"
            "**Recommendation:**\n"
            "Proceed with phased development (Amanah = reversible). "
            "Initial investment: RM 5 billion for exploration phase. "
            "Full commitment contingent on Phase 1 results. "
            "This maintains optionality and does not escalate beyond recoverable scope. "
            "Peace2 >= 1.0 maintained."
        )

    # Default geological response
    else:
        return (
            "Geological analysis request received. "
            "The Malay Basin is Malaysia's most prolific hydrocarbon province, "
            "containing approximately 60% of the nation's oil reserves. "
            "Further analysis requires specification of:\n"
            "1. Target formation (Group A-K reservoirs)\n"
            "2. Depth range of interest\n"
            "3. Specific block or PSC area\n\n"
            "Please provide additional parameters for detailed assessment."
        )


# ==============================================================================
# Demo Scenarios
# ==============================================================================

DEMO_QUERIES = [
    {
        "name": "Malay Basin Overview",
        "query": "Analyze seismic data for Malay Basin oil reserves",
        "expected_verdict": "SEAL",
        "domain": "exploration",
    },
    {
        "name": "Environmental Impact",
        "query": "What is the environmental impact of drilling in Malay Basin?",
        "expected_verdict": "SEAL",
        "domain": "ESG",
    },
    {
        "name": "Reserve Estimation",
        "query": "Estimate undiscovered oil reserves in Block PM-123",
        "expected_verdict": "PARTIAL",  # High uncertainty
        "domain": "reserves",
    },
]


# ==============================================================================
# Main Demo
# ==============================================================================

def run_petronas_demo(query: str = None, verbose: bool = True) -> dict:
    """
    Run Petronas geological demo with W@W Federation.

    Args:
        query: Geological query (default: Malay Basin analysis)
        verbose: Print detailed output

    Returns:
        Federation result with verdict, consensus, and audit trail
    """
    if query is None:
        query = DEMO_QUERIES[0]["query"]

    print("\n" + "="*70)
    print("PETRONAS DEMO: Geological Analysis with Constitutional Governance")
    print("="*70)
    print(f"Query: {query}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*70 + "\n")

    # Initialize federation with geological LLM
    federation = WAWFederation(
        llm_generate=geology_llm_generate,
        max_rounds=3,
    )

    # Run governed analysis
    result = federation.run(query)

    # Detailed output
    if verbose:
        print("\n" + "-"*70)
        print("AGENT RESPONSES")
        print("-"*70)

        for i, response in enumerate(result["responses"]):
            print(f"\n[{i+1}] @{response['agent']}:")
            print(f"    Verdict: {response['verdict']}")
            print(f"    Truth: {response['metrics']['truth']:.2f}")
            print(f"    kappa_r: {response['metrics']['kappa_r']:.2f}")
            print(f"    Peace2: {response['metrics']['peace_squared']:.2f}")
            print(f"    Response excerpt: {response['response'][:150]}...")

        print("\n" + "-"*70)
        print("COOLING LEDGER SUMMARY")
        print("-"*70)
        print(f"Total entries: {len(result['cooling_ledger'])}")
        print(f"Verdicts: {result['verdicts']}")

    # Final summary
    print("\n" + "="*70)
    print("FINAL VERDICT")
    print("="*70)
    print(f"Federation Verdict: {result['verdict']}")
    print(f"Tri-Witness Consensus: {result['consensus']:.2%}")
    print(f"Constitutional Compliance: {'PASS' if result['verdict'] in ['SEAL', 'PARTIAL'] else 'FAIL'}")
    print("="*70 + "\n")

    return result


def run_all_scenarios():
    """Run all demo scenarios."""
    print("\n" + "#"*70)
    print("# PETRONAS DEMO: Running All Scenarios")
    print("#"*70)

    results = []
    for scenario in DEMO_QUERIES:
        print(f"\n>>> Scenario: {scenario['name']}")
        print(f"    Domain: {scenario['domain']}")
        print(f"    Expected: {scenario['expected_verdict']}")

        result = run_petronas_demo(scenario["query"], verbose=False)
        result["scenario"] = scenario["name"]
        result["expected"] = scenario["expected_verdict"]
        result["match"] = result["verdict"] == scenario["expected_verdict"]
        results.append(result)

        status = "✓" if result["match"] else "✗"
        print(f"    Result: {result['verdict']} {status}")

    # Summary
    print("\n" + "="*70)
    print("SCENARIO SUMMARY")
    print("="*70)
    passed = sum(1 for r in results if r["match"])
    print(f"Passed: {passed}/{len(results)}")
    for r in results:
        status = "✓" if r["match"] else "✗"
        print(f"  {status} {r['scenario']}: {r['verdict']} (expected {r['expected']})")
    print("="*70)

    return results


# ==============================================================================
# Entry Point
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Petronas Demo: Geological Analysis with W@W Federation"
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Geological query to analyze",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all demo scenarios",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    if args.all:
        results = run_all_scenarios()
        if args.json:
            print(json.dumps(results, indent=2, default=str))
    else:
        result = run_petronas_demo(args.query)
        if args.json:
            print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
