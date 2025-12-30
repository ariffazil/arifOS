#!/usr/bin/env python3
"""
arifos_validate_cli.py - CLI tool for Track A/B/C constitutional validation.

Validates AI responses against all 6 constitutional floors (F1, F2, F4, F5, F6, F9).

Usage:
    # Validate text directly
    python scripts/arifos_validate_cli.py "The sky is blue."

    # Validate from file
    python scripts/arifos_validate_cli.py --file response.txt

    # With input text (for F4 DeltaS, F6 κᵣ)
    python scripts/arifos_validate_cli.py --output "Clear answer." --input "What is 2+2?"

    # High-stakes mode (UNVERIFIABLE → HOLD-888)
    python scripts/arifos_validate_cli.py "Bitcoin will rise." --high-stakes

    # With external evidence (for F2 Truth)
    python scripts/arifos_validate_cli.py "Paris is in France." --truth-score 0.99

    # JSON output
    python scripts/arifos_validate_cli.py "Text" --json

    # Verbose mode (show all floor details)
    python scripts/arifos_validate_cli.py "Text" --verbose

Examples:
    # Test F9 negation detection
    python scripts/arifos_validate_cli.py "I do NOT have a soul. I am a language model."

    # Test dangerous pattern (F1 Amanah)
    python scripts/arifos_validate_cli.py "rm -rf /"

    # Test with clarity measurement
    python scripts/arifos_validate_cli.py --output "I don't understand." --input "asdkjfh???"

Track A/B/C Enforcement Loop v45.1
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos_core.enforcement.response_validator_extensions import validate_response_full


def load_text_from_file(file_path: str) -> str:
    """Load text content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def format_human_readable(result: dict, verbose: bool = False) -> str:
    """Format validation result as human-readable text."""
    lines = []

    # Header
    lines.append("=" * 70)
    lines.append("Track A/B/C Constitutional Validation")
    lines.append("=" * 70)

    # Verdict (with color coding via symbols)
    verdict = result["verdict"]
    if verdict == "SEAL":
        verdict_symbol = "[SEAL]"
    elif verdict == "PARTIAL":
        verdict_symbol = "[PARTIAL]"
    elif verdict == "VOID":
        verdict_symbol = "[VOID]"
    elif verdict == "HOLD-888":
        verdict_symbol = "[HOLD-888]"
    else:
        verdict_symbol = f"[{verdict}]"

    lines.append(f"\nFinal Verdict: {verdict_symbol}")

    # Violations
    if result["violations"]:
        lines.append(f"\nViolations: {len(result['violations'])}")
        for violation in result["violations"]:
            lines.append(f"  - {violation}")
    else:
        lines.append("\nViolations: None")

    # Floor results
    lines.append("\nConstitutional Floors:")
    lines.append("-" * 70)

    for floor_name, floor_data in result["floors"].items():
        passed = floor_data["passed"]
        score = floor_data.get("score")
        evidence = floor_data.get("evidence", "")

        # Status symbol
        status = "[PASS]" if passed else "[FAIL]"

        # Format floor line
        if score is not None:
            lines.append(f"{status} {floor_name}: {score:.3f}")
        else:
            lines.append(f"{status} {floor_name}: N/A")

        # Show evidence in verbose mode or if failed
        if verbose or not passed:
            lines.append(f"      Evidence: {evidence}")

    # Metadata (verbose mode only)
    if verbose:
        lines.append("\nMetadata:")
        lines.append("-" * 70)
        metadata = result.get("metadata", {})
        lines.append(f"  Input provided: {metadata.get('input_provided', False)}")
        lines.append(f"  Evidence provided: {metadata.get('evidence_provided', False)}")
        lines.append(f"  Telemetry provided: {metadata.get('telemetry_provided', False)}")
        lines.append(f"  High stakes: {metadata.get('high_stakes', False)}")
        lines.append(f"  Session turns: {metadata.get('session_turns', 'N/A')}")
        lines.append(f"  Timestamp: {result.get('timestamp', 'N/A')}")

    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate AI responses against arifOS constitutional floors (Track A/B/C v45.1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic validation
  %(prog)s "The sky is blue."

  # From file
  %(prog)s --file response.txt

  # With input text (enables F4 DeltaS, F6 κᵣ)
  %(prog)s --output "Answer" --input "Question"

  # High-stakes mode
  %(prog)s "Prediction" --high-stakes

  # With external truth evidence
  %(prog)s "Fact" --truth-score 0.99

  # JSON output
  %(prog)s "Text" --json

  # Verbose output
  %(prog)s "Text" --verbose

Constitutional Floors:
  F1 - Amanah (Integrity): Dangerous pattern detection
  F2 - Truth: External evidence or UNVERIFIABLE
  F4 - DeltaS (Clarity): Zlib compression proxy
  F5 - Peace² (Stability): Harmful content detection
  F6 - κᵣ (Empathy): Physics vs semantic split
  F9 - Anti-Hantu: Ghost claim detection (negation-aware)

Verdicts:
  SEAL      - All floors pass
  PARTIAL   - Soft floor fails (F2, F4, F6)
  VOID      - Hard floor fails (F1, F5, F9)
  HOLD-888  - High-stakes + UNVERIFIABLE

For more info: https://github.com/ariffazil/arifOS
        """
    )

    # Input arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "output_text",
        nargs="?",
        help="AI response text to validate (direct input)"
    )
    input_group.add_argument(
        "--file", "-f",
        metavar="PATH",
        help="Read response text from file"
    )

    parser.add_argument(
        "--output", "-o",
        metavar="TEXT",
        help="AI response text (alternative to positional arg)"
    )

    parser.add_argument(
        "--input", "-i",
        metavar="TEXT",
        help="User input/question (optional, enables F4 DeltaS and F6 κᵣ)"
    )

    parser.add_argument(
        "--input-file",
        metavar="PATH",
        help="Read user input from file"
    )

    # Evidence arguments
    parser.add_argument(
        "--truth-score",
        type=float,
        metavar="SCORE",
        help="External truth score (0.0-1.0) for F2 Truth floor"
    )

    parser.add_argument(
        "--evidence",
        metavar="JSON",
        help="External evidence as JSON string (e.g., '{\"truth_score\": 0.99}')"
    )

    # Telemetry arguments
    parser.add_argument(
        "--session-turns",
        type=int,
        metavar="N",
        help="Number of turns in session (for F6 κᵣ gating)"
    )

    parser.add_argument(
        "--telemetry",
        metavar="JSON",
        help="Session telemetry as JSON string (turn_rate, token_rate, stability_var_dt)"
    )

    # Mode arguments
    parser.add_argument(
        "--high-stakes",
        action="store_true",
        help="Enable high-stakes mode (UNVERIFIABLE → HOLD-888)"
    )

    # Output arguments
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed floor evidence and metadata"
    )

    args = parser.parse_args()

    # Determine output text
    if args.file:
        output_text = load_text_from_file(args.file)
    elif args.output:
        output_text = args.output
    elif args.output_text:
        output_text = args.output_text
    else:
        parser.error("No output text provided. Use positional argument, --output, or --file")

    # Determine input text
    input_text = None
    if args.input_file:
        input_text = load_text_from_file(args.input_file)
    elif args.input:
        input_text = args.input

    # Parse evidence
    evidence = None
    if args.evidence:
        try:
            evidence = json.loads(args.evidence)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in --evidence: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.truth_score is not None:
        evidence = {"truth_score": args.truth_score}

    # Parse telemetry
    telemetry = None
    if args.telemetry:
        try:
            telemetry = json.loads(args.telemetry)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in --telemetry: {e}", file=sys.stderr)
            sys.exit(1)

    # Validate
    try:
        result = validate_response_full(
            output_text=output_text,
            input_text=input_text,
            telemetry=telemetry,
            high_stakes=args.high_stakes,
            evidence=evidence,
            session_turns=args.session_turns,
        )
    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        sys.exit(1)

    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_human_readable(result, verbose=args.verbose))

    # Exit code based on verdict
    verdict = result["verdict"]
    if verdict == "SEAL":
        sys.exit(0)  # Success
    elif verdict == "PARTIAL":
        sys.exit(1)  # Warning
    elif verdict in ("VOID", "HOLD-888", "SABAR"):
        sys.exit(2)  # Error
    else:
        sys.exit(3)  # Unknown


if __name__ == "__main__":
    main()
