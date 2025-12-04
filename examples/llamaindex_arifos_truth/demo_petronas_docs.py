#!/usr/bin/env python3
"""
Petronas Demo: RAG Document Analysis with Truth Governor

Demonstrates arifOS constitutional governance for document-grounded AI:
- Load Petronas documents (seismic, financial, ESG)
- RAG retrieval with relevance scoring
- F1 Truth verification (grounding check)
- APEX PRIME verdict (SEAL grounded / VOID hallucination)

Usage:
    python demo_petronas_docs.py
    python demo_petronas_docs.py --query "What is the NPV of Malay Basin?"
    python demo_petronas_docs.py --all  # Run all demo scenarios
"""

from __future__ import annotations

import argparse
import json
import sys
import os
from datetime import datetime

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from rag_truth_governor import (
    RAGTruthGovernor,
    Document,
    create_petronas_documents,
)


# ==============================================================================
# Demo Scenarios
# ==============================================================================

DEMO_QUERIES = [
    {
        "name": "Oil Reserves Query",
        "query": "What are the proven oil reserves in the Malay Basin?",
        "expected_verdict": "SEAL",
        "domain": "reserves",
    },
    {
        "name": "Seismic Survey Analysis",
        "query": "What did the 2022 seismic surveys discover?",
        "expected_verdict": "SEAL",
        "domain": "technical",
    },
    {
        "name": "Economic Analysis",
        "query": "What is the NPV and IRR for Malay Basin projects?",
        "expected_verdict": "SEAL",
        "domain": "economic",
    },
    {
        "name": "ESG Impact",
        "query": "What are the environmental impacts and community investments?",
        "expected_verdict": "SEAL",
        "domain": "ESG",
    },
    {
        "name": "Combined Analysis",
        "query": "Summarize the Malay Basin: reserves, economics, and environmental impact",
        "expected_verdict": "SEAL",
        "domain": "comprehensive",
    },
]


# ==============================================================================
# Additional Domain Documents
# ==============================================================================

def create_extended_documents() -> list[Document]:
    """Create extended document set for demo."""
    base_docs = create_petronas_documents()

    extended_docs = [
        Document(
            id="well_log_2023_01",
            text=(
                "Well PM-15 drilled in Block 4A reached total depth of 3,850 meters. "
                "Pay zones identified at 2,100-2,300m and 3,200-3,400m intervals. "
                "Estimated recoverable reserves: 45 million barrels per well. "
                "Drilling completed ahead of schedule with zero safety incidents."
            ),
            metadata={"source": "Well Log PM-15 2023", "type": "technical"},
        ),
        Document(
            id="production_forecast",
            text=(
                "Production forecast for Malay Basin 2024-2034: Peak production "
                "expected in 2027 at 180,000 barrels per day. Plateau maintained "
                "for 5 years before natural decline. Cumulative production over "
                "10 years: approximately 450 million barrels."
            ),
            metadata={"source": "Production Forecast 2024", "type": "planning"},
        ),
        Document(
            id="regulatory_compliance",
            text=(
                "All Malay Basin operations maintain full compliance with: "
                "Petroleum Development Act 1974, Environmental Quality Act 1974, "
                "and OSHA 1994. Latest audit score: 98/100. No major violations "
                "in the past 5 years. Carbon tax compliance achieved."
            ),
            metadata={"source": "Regulatory Compliance Report 2023", "type": "legal"},
        ),
    ]

    return base_docs + extended_docs


# ==============================================================================
# Demo Runner
# ==============================================================================

def run_petronas_demo(query: str = None, verbose: bool = True) -> dict:
    """
    Run Petronas document analysis demo.

    Args:
        query: Query to analyze (default: oil reserves)
        verbose: Print detailed output

    Returns:
        RAG result with verdict and analysis
    """
    if query is None:
        query = DEMO_QUERIES[0]["query"]

    print("\n" + "="*70)
    print("PETRONAS DOCUMENT ANALYSIS: RAG + Truth Governor")
    print("="*70)
    print(f"Query: {query}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*70 + "\n")

    # Initialize governor with extended documents
    governor = RAGTruthGovernor(high_stakes=True)
    governor.add_documents(create_extended_documents())

    # Execute governed RAG query
    result = governor.query(query, top_k=4)

    # Detailed output
    if verbose:
        print("\n" + "-"*70)
        print("RETRIEVED SOURCES")
        print("-"*70)
        for i, node in enumerate(result.retrieved_nodes):
            print(f"\n[{i+1}] {node.source}")
            print(f"    Relevance: {node.score:.2f}")
            print(f"    Excerpt: {node.text[:100]}...")

        print("\n" + "-"*70)
        print("TRUTH ANALYSIS")
        print("-"*70)
        print(f"F1 Truth Score: {result.metrics.truth:.2f}")
        print(f"Grounding Score: {result.grounding_score:.2%}")
        print(f"Citations Found: {result.citations_found}")
        print(f"Hallucination Flags: {result.hallucination_flags}")

    # Final verdict
    print("\n" + "="*70)
    print("FINAL VERDICT")
    print("="*70)
    print(f"Query: {query}")
    print(f"Verdict: {result.verdict}")
    print(f"F1 Truth: {result.metrics.truth:.2f} (threshold: >= 0.99)")
    print(f"Grounding: {result.grounding_score:.2%}")
    print(f"Constitutional Compliance: {'PASS' if result.verdict in ['SEAL', 'PARTIAL'] else 'FAIL'}")
    print("="*70 + "\n")

    return {
        "query": result.query,
        "verdict": result.verdict,
        "truth": result.metrics.truth,
        "grounding": result.grounding_score,
        "response": result.response,
        "sources": [n.source for n in result.retrieved_nodes],
        "citations": result.citations_found,
        "hallucinations": result.hallucination_flags,
    }


def run_all_scenarios() -> list[dict]:
    """Run all demo scenarios."""
    print("\n" + "#"*70)
    print("# PETRONAS RAG DEMO: Running All Scenarios")
    print("#"*70)

    results = []
    for scenario in DEMO_QUERIES:
        print(f"\n>>> Scenario: {scenario['name']}")
        print(f"    Domain: {scenario['domain']}")
        print(f"    Expected: {scenario['expected_verdict']}")

        result = run_petronas_demo(scenario["query"], verbose=False)
        result["scenario"] = scenario["name"]
        result["expected"] = scenario["expected_verdict"]
        result["match"] = result["verdict"] in [scenario["expected_verdict"], "PARTIAL"]
        results.append(result)

        status = "PASS" if result["match"] else "FAIL"
        print(f"    Result: {result['verdict']} [{status}]")
        print(f"    Truth: {result['truth']:.2f}")

    # Summary
    print("\n" + "="*70)
    print("SCENARIO SUMMARY")
    print("="*70)
    passed = sum(1 for r in results if r["match"])
    print(f"Passed: {passed}/{len(results)}")
    for r in results:
        status = "PASS" if r["match"] else "FAIL"
        print(f"  [{status}] {r['scenario']}: {r['verdict']} (truth={r['truth']:.2f})")
    print("="*70)

    return results


def run_hallucination_test() -> dict:
    """Test hallucination detection with fabricated query."""
    print("\n" + "="*70)
    print("HALLUCINATION DETECTION TEST")
    print("="*70)

    # Custom LLM that generates hallucinations
    def hallucinating_llm(query: str, context: str) -> str:
        return (
            "The Malay Basin contains 999 billion barrels of oil discovered in 2099. "
            "This represents a 10000% increase over previous estimates. "
            "Flying cars will be powered by this oil by 2025."
        )

    governor = RAGTruthGovernor(
        llm_generate=hallucinating_llm,
        high_stakes=True,
    )
    governor.add_documents(create_petronas_documents())

    result = governor.query("What are the oil reserves?")

    print("\n--- Hallucination Test Result ---")
    print(f"Verdict: {result.verdict}")
    print(f"Truth Score: {result.metrics.truth:.2f}")
    print(f"Hallucination Flags: {result.hallucination_flags}")
    print(f"Expected: VOID (due to fabricated data)")
    print("="*70 + "\n")

    return {
        "verdict": result.verdict,
        "truth": result.metrics.truth,
        "hallucinations": result.hallucination_flags,
        "passed": result.verdict == "VOID" or result.metrics.truth < 0.99,
    }


# ==============================================================================
# Entry Point
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Petronas RAG Demo: Document Analysis with Truth Governor"
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Query to analyze",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all demo scenarios",
    )
    parser.add_argument(
        "--hallucination-test",
        action="store_true",
        help="Run hallucination detection test",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    if args.hallucination_test:
        result = run_hallucination_test()
        if args.json:
            print(json.dumps(result, indent=2, default=str))
    elif args.all:
        results = run_all_scenarios()
        if args.json:
            print(json.dumps(results, indent=2, default=str))
    else:
        result = run_petronas_demo(args.query)
        if args.json:
            print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
