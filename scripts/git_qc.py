#!/usr/bin/env python3
"""
git_qc.py - CLI wrapper for /gitQC constitutional validator

Usage:
    python scripts/git_qc.py --branch feat/my-feature
    python scripts/git_qc.py --forge-report forge_output.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import arifos_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos_core.trinity import analyze_branch, validate_changes, ForgeReport


def main():
    parser = argparse.ArgumentParser(description="/gitQC - Validate constitutional floors")
    parser.add_argument("--branch", help="Feature branch to validate")
    parser.add_argument("--forge-report", help="Path to forge report JSON")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        # Get forge report (either from file or generate fresh)
        if args.forge_report:
            with open(args.forge_report) as f:
                data = json.load(f)
                forge_report = ForgeReport(**data)
        elif args.branch:
            forge_report = analyze_branch(branch_name=args.branch)
        else:
            print("Error: Must provide --branch or --forge-report", file=sys.stderr)
            sys.exit(1)

        # Run QC validation
        qc_report = validate_changes(forge_report)

        if args.json:
            # JSON output for pipe to /gitseal
            print(json.dumps(qc_report.__dict__, indent=2))
        else:
            # Human-readable output
            print("\n" + "=" * 60)
            print(f"🔍 /gitQC Constitutional Validation")
            print("=" * 60)
            print(f"\nBranch: {forge_report.branch}")
            print(f"ZKPC ID: {qc_report.zkpc_id}")
            print(f"Verdict: {qc_report.verdict}")
            print(f"\n📊 Floor Results:")
            for floor, passed in qc_report.floors_passed.items():
                status = "✅" if passed else "❌"
                detail = qc_report.floor_details.get(floor, "")
                print(f"  {status} {floor}: {detail}")
            print(f"\n📝 Notes:")
            for note in qc_report.notes:
                print(f"  • {note}")
            print(f"\n⏰ Generated: {qc_report.timestamp}")
            print("=" * 60 + "\n")

            # Exit with appropriate code
            if qc_report.verdict == "VOID":
                sys.exit(89)  # VOID exit code
            elif qc_report.verdict == "FLAG":
                sys.exit(1)  # FLAG exit code

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(255)


if __name__ == "__main__":
    main()
