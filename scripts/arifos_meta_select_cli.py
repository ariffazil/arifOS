#!/usr/bin/env python3
"""
arifos_meta_select_cli.py - CLI tool for Track A/B/C consensus aggregation.

Aggregate multiple witness verdicts via deterministic consensus algorithm.

Usage:
    # From JSON file
    python scripts/arifos_meta_select_cli.py verdicts.json

    # From stdin
    cat verdicts.json | python scripts/arifos_meta_select_cli.py -

    # Custom consensus threshold
    python scripts/arifos_meta_select_cli.py verdicts.json --threshold 0.80

    # JSON output
    python scripts/arifos_meta_select_cli.py verdicts.json --json

    # Verbose output
    python scripts/arifos_meta_select_cli.py verdicts.json --verbose

Input Format (JSON):
    {
      "verdicts": [
        {"source": "human", "verdict": "SEAL", "confidence": 1.0},
        {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
        {"source": "earth", "verdict": "SEAL", "confidence": 1.0}
      ]
    }

    Or just an array:
    [
      {"source": "human", "verdict": "SEAL", "confidence": 1.0},
      {"source": "ai", "verdict": "SEAL", "confidence": 0.99}
    ]

Examples:
    # Strong consensus (100% SEAL)
    echo '[
      {"source": "human", "verdict": "SEAL", "confidence": 1.0},
      {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
      {"source": "earth", "verdict": "SEAL", "confidence": 1.0}
    ]' | python scripts/arifos_meta_select_cli.py -

    # Low consensus (disagreement → HOLD-888)
    echo '[
      {"source": "human", "verdict": "SEAL", "confidence": 1.0},
      {"source": "ai", "verdict": "VOID", "confidence": 0.99},
      {"source": "earth", "verdict": "PARTIAL", "confidence": 0.80}
    ]' | python scripts/arifos_meta_select_cli.py -

Track A/B/C Enforcement Loop v45.1
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos_core.enforcement.response_validator_extensions import meta_select


def load_verdicts_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Load verdicts from JSON file."""
    try:
        if file_path == "-":
            # Read from stdin
            content = sys.stdin.read()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

        data = json.loads(content)

        # Handle both formats: {"verdicts": [...]} and [...]
        if isinstance(data, dict) and "verdicts" in data:
            verdicts = data["verdicts"]
        elif isinstance(data, list):
            verdicts = data
        else:
            raise ValueError("Invalid format. Expected array or {\"verdicts\": [...]}")

        # Validate verdicts
        if not isinstance(verdicts, list):
            raise ValueError("Verdicts must be an array")

        for i, verdict in enumerate(verdicts):
            if not isinstance(verdict, dict):
                raise ValueError(f"Verdict {i} must be an object")
            if "source" not in verdict:
                raise ValueError(f"Verdict {i} missing 'source' field")
            if "verdict" not in verdict:
                raise ValueError(f"Verdict {i} missing 'verdict' field")
            if "confidence" not in verdict:
                raise ValueError(f"Verdict {i} missing 'confidence' field")

        return verdicts

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def format_human_readable(result: dict, verbose: bool = False) -> str:
    """Format consensus result as human-readable text."""
    lines = []

    # Header
    lines.append("=" * 70)
    lines.append("Track A/B/C Consensus Aggregation")
    lines.append("=" * 70)

    # Winner
    winner = result["winner"]
    if winner == "SEAL":
        winner_symbol = "[SEAL]"
    elif winner == "PARTIAL":
        winner_symbol = "[PARTIAL]"
    elif winner == "VOID":
        winner_symbol = "[VOID]"
    elif winner == "HOLD-888":
        winner_symbol = "[HOLD-888]"
    elif winner == "SABAR":
        winner_symbol = "[SABAR]"
    else:
        winner_symbol = f"[{winner}]"

    lines.append(f"\nWinner (Plurality): {winner_symbol}")

    # Consensus
    consensus = result["consensus"]
    consensus_pct = consensus * 100
    lines.append(f"Consensus Rate: {consensus:.3f} ({consensus_pct:.1f}%)")

    # Final verdict
    verdict = result["verdict"]
    if verdict == "SEAL":
        verdict_symbol = "[SEAL]"
        verdict_note = "(Strong consensus achieved)"
    elif verdict == "HOLD-888":
        verdict_symbol = "[HOLD-888]"
        verdict_note = "(Low consensus - human review required)"
    else:
        verdict_symbol = f"[{verdict}]"
        verdict_note = ""

    lines.append(f"Final Verdict: {verdict_symbol} {verdict_note}")

    # Tally
    lines.append("\nVote Tally:")
    lines.append("-" * 70)
    tally = result["tally"]
    total_votes = sum(tally.values())

    for verdict_type, count in sorted(tally.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_votes) * 100 if total_votes > 0 else 0
        lines.append(f"  {verdict_type:12s}: {count:2d} votes ({percentage:5.1f}%)")

    # Evidence (verbose mode)
    if verbose:
        lines.append("\nEvidence:")
        lines.append("-" * 70)
        evidence = result.get("evidence", "")
        lines.append(f"  {evidence}")

    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Aggregate witness verdicts via deterministic consensus (Track A/B/C v45.1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Input Format (JSON file or stdin):
  {
    "verdicts": [
      {"source": "human", "verdict": "SEAL", "confidence": 1.0},
      {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
      {"source": "earth", "verdict": "SEAL", "confidence": 1.0}
    ]
  }

  Or just an array:
  [
    {"source": "human", "verdict": "SEAL", "confidence": 1.0},
    {"source": "ai", "verdict": "SEAL", "confidence": 0.99}
  ]

Examples:
  # From file
  %(prog)s verdicts.json

  # From stdin
  cat verdicts.json | %(prog)s -

  # Custom threshold (default 0.95)
  %(prog)s verdicts.json --threshold 0.80

  # JSON output
  %(prog)s verdicts.json --json

  # Verbose output
  %(prog)s verdicts.json --verbose

Consensus Logic:
  - Counts votes for each verdict type
  - Determines winner by plurality (or hierarchy if tie)
  - Calculates consensus = winner_votes / total_votes
  - If winner==SEAL AND consensus>=threshold → SEAL
  - Else → HOLD-888 (requires human review)

Verdict Hierarchy (for tie-breaking):
  VOID > HOLD-888 > SABAR > PARTIAL > SEAL

Exit Codes:
  0 - SEAL (strong consensus)
  1 - HOLD-888 (low consensus or non-SEAL winner)
  2 - Error

For more info: https://github.com/ariffazil/arifOS
        """
    )

    # Input argument
    parser.add_argument(
        "verdicts_file",
        help="JSON file with verdicts array (use '-' for stdin)"
    )

    # Consensus threshold
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.95,
        metavar="THRESHOLD",
        help="Consensus threshold (0.0-1.0, default: 0.95)"
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
        help="Show detailed evidence"
    )

    args = parser.parse_args()

    # Validate threshold
    if not (0.0 <= args.threshold <= 1.0):
        parser.error("Threshold must be between 0.0 and 1.0")

    # Load verdicts
    verdicts = load_verdicts_from_file(args.verdicts_file)

    if not verdicts:
        print("Error: No verdicts provided", file=sys.stderr)
        sys.exit(2)

    # Run consensus
    try:
        result = meta_select(
            verdicts=verdicts,
            consensus_threshold=args.threshold,
        )
    except Exception as e:
        print(f"Error during consensus: {e}", file=sys.stderr)
        sys.exit(2)

    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_human_readable(result, verbose=args.verbose))

    # Exit code based on verdict
    verdict = result["verdict"]
    if verdict == "SEAL":
        sys.exit(0)  # Success (strong consensus)
    else:
        sys.exit(1)  # HOLD-888 (low consensus or non-SEAL winner)


if __name__ == "__main__":
    main()
