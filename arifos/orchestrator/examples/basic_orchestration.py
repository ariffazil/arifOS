"""
Basic orchestration example

Demonstrates:
1. Claude reasoning (Floors 1-2)
2. Codex code generation
3. AntiGravity validation
"""

from arifos.orchestrator.core.orchestrator import run_orchestration, pretty_print_result


def main():
    """Run basic orchestration example"""

    query = "How does thermodynamic AI governance reduce hallucination?"
    context = "User: Arif Fazil, arifOS architect"

    print("Running arifOS Multi-Agent Orchestration...")
    print(f"Query: {query}\n")

    # Run orchestration
    result = run_orchestration(query=query, context=context)

    # Pretty print results
    pretty_print_result(result)

    # Show verdict details
    print("\n📊 Orchestration Summary:")
    print(f"   Final Verdict: {result['verdict']}")
    print(f"   Claude Tokens: {result['claude']['usage']['input_tokens']} in, {result['claude']['usage']['output_tokens']} out")
    print(f"   Codex Tokens: {result['codex']['usage']['total_tokens']} total")
    print(f"   AntiGravity Confidence: {result['antigravity']['validation']['confidence']}")


if __name__ == "__main__":
    main()
