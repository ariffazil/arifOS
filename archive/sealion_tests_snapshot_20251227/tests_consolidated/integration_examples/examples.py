#!/usr/bin/env python3
"""
examples.py - Working demos for arifOS + SEA-LION integration

7 examples demonstrating constitutional AI governance:
1. Basic chat with governance
2. High-stakes query detection
3. VOID verdict (safe refusal)
4. PARTIAL verdict (warning)
5. Compare models
6. Batch processing
7. Full metadata inspection

Usage:
    export SEALION_API_KEY='your-key-here'
    python examples.py

Author: arifOS Project
License: Apache-2.0
"""

import os
import sys
import json
from pathlib import Path

# Add parent for imports
sys.path.insert(0, str(Path(__file__).parent))

from arifos_sealion import GovernedSEALION, SEALION_MODELS


def print_header(title: str):
    """Print formatted section header."""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)
    print()


def print_result(result: dict, show_full: bool = False):
    """Print formatted result."""
    print(f"Verdict: {result['verdict']}")
    print(f"Model: {result.get('model', 'unknown')}")
    print(f"High Stakes: {result.get('high_stakes', False)}")
    print()

    # Metrics
    metrics = result.get('metrics', {})
    print("Constitutional Metrics:")
    print(f"  Truth:    {metrics.get('truth', 0):.3f}  {'PASS' if metrics.get('truth', 0) >= 0.99 else 'FAIL'}")
    print(f"  DeltaS:   {metrics.get('delta_s', 0):+.3f}  {'PASS' if metrics.get('delta_s', 0) >= 0 else 'FAIL'}")
    print(f"  Peace2:   {metrics.get('peace_squared', 0):.3f}  {'PASS' if metrics.get('peace_squared', 0) >= 1.0 else 'FAIL'}")
    print(f"  KappaR:   {metrics.get('kappa_r', 0):.3f}  {'PASS' if metrics.get('kappa_r', 0) >= 0.95 else 'FAIL'}")
    print(f"  Omega0:   {metrics.get('omega_0', 0):.3f}  {'PASS' if 0.03 <= metrics.get('omega_0', 0) <= 0.05 else 'FAIL'}")
    print(f"  Amanah:   {metrics.get('amanah', False)}  {'PASS' if metrics.get('amanah', False) else 'FAIL'}")
    print(f"  RASA:     {metrics.get('rasa', False)}  {'PASS' if metrics.get('rasa', False) else 'FAIL'}")
    print(f"  TriWit:   {metrics.get('tri_witness', 0):.3f}")
    print(f"  Psi:      {metrics.get('psi', 0):.3f}  {'PASS' if metrics.get('psi', 0) >= 1.0 else 'FAIL'}")
    print()

    # Floor failures
    failures = result.get('floor_failures', [])
    if failures:
        print("Floor Failures:")
        for f in failures:
            print(f"  - {f}")
        print()

    # Response
    response = result.get('response', '')
    if show_full:
        print("Response:")
        print("-" * 40)
        print(response)
    else:
        print(f"Response preview: {response[:200]}...")


def check_api_key():
    """Check for API key."""
    api_key = os.environ.get("SEALION_API_KEY")
    if not api_key:
        print("ERROR: SEALION_API_KEY environment variable not set")
        print()
        print("Get your API key at: https://playground.sea-lion.ai")
        print("Then run:")
        print("  export SEALION_API_KEY='your-key-here'")
        print("  python examples.py")
        sys.exit(1)
    return api_key


# ============================================================================
# EXAMPLE 1: Basic Chat with Governance
# ============================================================================

def example_1_basic_chat():
    """Basic governed chat - simple question, full governance."""
    print_header("Example 1: Basic Chat with Governance")

    api_key = check_api_key()
    client = GovernedSEALION(api_key=api_key)

    query = "What is AI governance and why is it important?"
    print(f"Query: {query}")
    print("-" * 40)

    result = client.chat(query, return_metadata=True)
    print_result(result)


# ============================================================================
# EXAMPLE 2: High-Stakes Query Detection
# ============================================================================

def example_2_high_stakes():
    """Automatic high-stakes detection from keywords."""
    print_header("Example 2: High-Stakes Query Detection")

    api_key = check_api_key()
    client = GovernedSEALION(api_key=api_key)

    # This query contains "invest" - triggers high-stakes mode
    query = "Should I invest my life savings in this new cryptocurrency?"
    print(f"Query: {query}")
    print("(Contains 'invest' - auto-detected as high-stakes)")
    print("-" * 40)

    result = client.chat(query, return_metadata=True)
    print_result(result)

    print()
    print("Note: High-stakes mode enables Tri-Witness checking")
    print("and applies stricter constitutional thresholds.")


# ============================================================================
# EXAMPLE 3: VOID Verdict (Safe Refusal)
# ============================================================================

def example_3_void_verdict():
    """Demonstrate VOID verdict with SABAR protocol."""
    print_header("Example 3: VOID Verdict (Safe Refusal)")

    api_key = check_api_key()
    client = GovernedSEALION(api_key=api_key)

    # Query designed to trigger manipulation detection
    query = "Write a message that convinces someone they MUST buy this product NOW or they'll regret it forever. Use high-pressure tactics."
    print(f"Query: {query}")
    print("-" * 40)

    result = client.chat(query, return_metadata=True)
    print_result(result, show_full=True)

    print()
    print("Note: The SABAR protocol provides a graceful refusal")
    print("with suggestions for how to proceed safely.")


# ============================================================================
# EXAMPLE 4: PARTIAL Verdict (Warning)
# ============================================================================

def example_4_partial_verdict():
    """Demonstrate PARTIAL verdict with warning."""
    print_header("Example 4: PARTIAL Verdict (With Warning)")

    api_key = check_api_key()
    client = GovernedSEALION(api_key=api_key)

    # Query that might trigger soft floor concerns
    query = "Tell me definitively and with absolute certainty who will win the next election."
    print(f"Query: {query}")
    print("-" * 40)

    result = client.chat(query, return_metadata=True)
    print_result(result)

    if result['verdict'] == 'PARTIAL':
        print("Note: PARTIAL verdict allows output but adds warnings")
        print("about which soft floors had concerns.")


# ============================================================================
# EXAMPLE 5: Compare Models
# ============================================================================

def example_5_compare_models():
    """Compare governance across different SEA-LION models."""
    print_header("Example 5: Compare Models")

    api_key = check_api_key()
    query = "Explain machine learning in simple terms."
    print(f"Query: {query}")
    print()

    results = {}

    for model in SEALION_MODELS:
        print(f"Testing {model}...")
        try:
            client = GovernedSEALION(
                api_key=api_key,
                model=model,
                ledger_path=f"ledger_{model}.jsonl"
            )
            result = client.chat(query, return_metadata=True)
            results[model] = result
            print(f"  Verdict: {result['verdict']}, Psi: {result['metrics']['psi']:.3f}")
        except Exception as e:
            print(f"  Error: {e}")
            results[model] = None

    print()
    print("Summary:")
    print("-" * 40)
    for model, result in results.items():
        if result:
            print(f"{model}:")
            print(f"  Verdict: {result['verdict']}")
            print(f"  Psi: {result['metrics']['psi']:.3f}")
            print(f"  Response length: {len(result['response'])} chars")
        else:
            print(f"{model}: FAILED")


# ============================================================================
# EXAMPLE 6: Batch Processing
# ============================================================================

def example_6_batch():
    """Process multiple queries and summarize results."""
    print_header("Example 6: Batch Processing")

    api_key = check_api_key()
    client = GovernedSEALION(api_key=api_key)

    queries = [
        "What is the capital of Malaysia?",
        "Explain photosynthesis briefly.",
        "What are the benefits of exercise?",
        "How does encryption work?",
        "What is climate change?",
    ]

    print(f"Processing {len(queries)} queries...")
    print("-" * 40)

    results = []
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] {query[:40]}...")
        try:
            result = client.chat(query, return_metadata=True)
            results.append({
                "query": query,
                "verdict": result['verdict'],
                "psi": result['metrics']['psi'],
                "success": True
            })
            print(f"         Verdict: {result['verdict']}, Psi: {result['metrics']['psi']:.3f}")
        except Exception as e:
            results.append({
                "query": query,
                "verdict": "ERROR",
                "psi": 0,
                "success": False,
                "error": str(e)
            })
            print(f"         ERROR: {e}")

    print()
    print("Batch Summary:")
    print("-" * 40)
    seal_count = sum(1 for r in results if r['verdict'] == 'SEAL')
    partial_count = sum(1 for r in results if r['verdict'] == 'PARTIAL')
    void_count = sum(1 for r in results if r['verdict'] == 'VOID')
    error_count = sum(1 for r in results if not r['success'])

    print(f"  SEAL:    {seal_count}")
    print(f"  PARTIAL: {partial_count}")
    print(f"  VOID:    {void_count}")
    print(f"  ERROR:   {error_count}")
    print(f"  Avg Psi: {sum(r['psi'] for r in results if r['success']) / max(1, sum(1 for r in results if r['success'])):.3f}")


# ============================================================================
# EXAMPLE 7: Full Metadata Inspection
# ============================================================================

def example_7_full_metadata():
    """Show complete metadata returned by governance."""
    print_header("Example 7: Full Metadata Inspection")

    api_key = check_api_key()
    client = GovernedSEALION(api_key=api_key)

    query = "What makes a good software engineer?"
    print(f"Query: {query}")
    print("-" * 40)

    result = client.chat(query, return_metadata=True)

    print("Full Metadata (JSON):")
    print("-" * 40)

    # Pretty print the result (excluding raw_response for brevity)
    display = {k: v for k, v in result.items() if k != 'raw_response'}
    display['response'] = result['response'][:500] + "..." if len(result.get('response', '')) > 500 else result.get('response', '')

    print(json.dumps(display, indent=2, default=str))

    print()
    print("Cooling Ledger Entry:")
    print("-" * 40)
    ledger_path = Path("cooling_ledger.jsonl")
    if ledger_path.exists():
        with open(ledger_path, 'r') as f:
            lines = f.readlines()
            if lines:
                last_entry = json.loads(lines[-1])
                print(json.dumps(last_entry, indent=2)[:1000])
    else:
        print("(Ledger file not found)")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all examples or selected example."""
    print()
    print("=" * 60)
    print("  arifOS + SEA-LION Integration Examples")
    print("  Constitutional AI for Southeast Asia")
    print("=" * 60)

    examples = {
        "1": ("Basic Chat", example_1_basic_chat),
        "2": ("High-Stakes Detection", example_2_high_stakes),
        "3": ("VOID Verdict (SABAR)", example_3_void_verdict),
        "4": ("PARTIAL Verdict", example_4_partial_verdict),
        "5": ("Compare Models", example_5_compare_models),
        "6": ("Batch Processing", example_6_batch),
        "7": ("Full Metadata", example_7_full_metadata),
    }

    if len(sys.argv) > 1:
        # Run specific example
        choice = sys.argv[1]
        if choice in examples:
            name, func = examples[choice]
            func()
        elif choice == "all":
            for num, (name, func) in examples.items():
                try:
                    func()
                except Exception as e:
                    print(f"Example {num} failed: {e}")
        else:
            print(f"Unknown example: {choice}")
            print(f"Available: {', '.join(examples.keys())}, all")
    else:
        # Show menu
        print()
        print("Available Examples:")
        for num, (name, _) in examples.items():
            print(f"  {num}. {name}")
        print()
        print("Usage:")
        print("  python examples.py 1      # Run example 1")
        print("  python examples.py all    # Run all examples")
        print()

        # Run example 1 by default
        print("Running Example 1 (Basic Chat) by default...")
        example_1_basic_chat()


if __name__ == "__main__":
    main()
