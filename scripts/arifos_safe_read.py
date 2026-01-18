#!/usr/bin/env python3
"""
arifos-safe-read - Constitutional file reading CLI

Usage:
    arifos-safe-read --path README.md
    arifos-safe-read --path src/config.py --root /project
    arifos-safe-read --path .env  # VOID - forbidden pattern

Exit Codes:
    0  - SEAL (success, file read)
    40 - VOID (access denied)
    88 - HOLD (not used in FAG, reserved)

Part of arifOS v41 File Access Governance (FAG).
"""

import argparse
import sys
from pathlib import Path

from arifos.apex.governance.fag import FAG, FAGReadResult


def main() -> int:
    parser = argparse.ArgumentParser(
        description="arifOS FAG - Constitutional file reading with 9-floor governance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  arifos-safe-read --path README.md
  arifos-safe-read --path src/main.py --root /my/project
  arifos-safe-read --path .env  # VOID - forbidden

Constitutional Floors Enforced:
  F1 Amanah   - Root jail, reversible
  F2 Truth    - File must exist and be readable
  F4 DeltaS   - Reject binary/unreadable files
  F5 Peace²   - Read-only, non-destructive
  F7 Omega0   - Return verdict + uncertainty
  F8 G        - Log to Cooling Ledger
  F9 C_dark   - Block secrets, credentials
        """,
    )
    
    parser.add_argument(
        "--path",
        required=True,
        help="Path to file (relative to root or absolute within root)",
    )
    
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory for jailed access (default: current directory)",
    )
    
    parser.add_argument(
        "--no-ledger",
        action="store_true",
        help="Disable Cooling Ledger logging",
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only output file content (if SEAL), suppress verdict messages",
    )
    
    args = parser.parse_args()
    
    # Create FAG instance
    try:
        fag = FAG(
            root=args.root,
            read_only=True,
            enable_ledger=not args.no_ledger,
            job_id="arifos-safe-read",
        )
    except ValueError as e:
        print(f"Error initializing FAG: {e}", file=sys.stderr)
        return 1
    
    # Read file
    result = fag.read(args.path)
    
    # Output
    if args.json:
        import json
        output = {
            "verdict": result.verdict,
            "path": result.path,
            "content": result.content,
            "reason": result.reason,
            "floor_scores": result.floor_scores,
        }
        print(json.dumps(output, indent=2))
    elif args.quiet:
        if result.verdict == "SEAL" and result.content:
            print(result.content)
    else:
        # Human-readable output
        print(f"[FAG] File: {result.path}")
        print(f"[FAG] Verdict: {result.verdict}")
        
        if result.floor_scores:
            print("[FAG] Floor Scores:")
            for floor, score in result.floor_scores.items():
                status = "✅" if _floor_passed(floor, score) else "❌"
                print(f"  {status} {floor}: {score:.2f}")
        
        if result.verdict == "SEAL":
            print(f"\n[FAG] Content ({len(result.content)} chars):")
            print("─" * 60)
            print(result.content)
            print("─" * 60)
        else:
            print(f"\n[FAG] Access Denied: {result.reason}")
    
    # Exit code
    if result.verdict == "SEAL":
        return 0
    elif result.verdict == "VOID":
        return 40
    else:
        return 88  # HOLD (not used in FAG, but reserved)


def _floor_passed(floor: str, score: float) -> bool:
    """Check if floor score passes threshold."""
    if "amanah" in floor.lower():
        return score >= 1.0
    elif "truth" in floor.lower():
        return score >= 0.99
    elif "delta_s" in floor.lower():
        return score >= 0.0
    elif "peace" in floor.lower():
        return score >= 1.0
    elif "omega0" in floor.lower():
        return 0.03 <= score <= 0.05
    elif "c_dark" in floor.lower():
        return score < 0.30
    else:
        return True


if __name__ == "__main__":
    sys.exit(main())
