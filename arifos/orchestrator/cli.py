"""
CLI Interface for arifOS Multi-Agent Orchestrator

Usage:
    python -m arifos_orchestrator.cli "Your query here"
    python -m arifos_orchestrator.cli "How does thermodynamic AI work?" --context "User: Arif"
"""

import argparse
import sys
from arifos.orchestrator.core.orchestrator import run_orchestration, pretty_print_result


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="arifOS Multi-Agent Orchestrator (Claude + Codex + AntiGravity)",
        epilog="DITEMPA BUKAN DIBERI — Forged, not given.",
    )

    parser.add_argument("query", type=str, help="Query to process through orchestration")
    parser.add_argument(
        "--context",
        "-c",
        type=str,
        default="",
        help="Additional context for query",
    )
    parser.add_argument(
        "--claude-key",
        type=str,
        help="Anthropic API key (defaults to ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--openai-key",
        type=str,
        help="OpenAI API key (defaults to OPENAI_API_KEY env var)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress verbose output (only show verdict)",
    )

    args = parser.parse_args()

    try:
        # Run orchestration
        result = run_orchestration(
            query=args.query,
            context=args.context,
            claude_api_key=args.claude_key,
            openai_api_key=args.openai_key,
        )

        # Output results
        if args.quiet:
            print(f"Verdict: {result['verdict']}")
        else:
            pretty_print_result(result)

        # Exit code based on verdict
        if result["verdict"] == "SEAL":
            sys.exit(0)
        elif result["verdict"] == "PARTIAL":
            sys.exit(1)
        else:  # VOID
            sys.exit(2)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nHint: Set ANTHROPIC_API_KEY and OPENAI_API_KEY environment variables.")
        sys.exit(3)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    main()
