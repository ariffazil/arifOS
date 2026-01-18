#!/usr/bin/env python3
"""
git_forge.py - CLI wrapper for /gitforge state mapper

Usage:
    python scripts/git_forge.py --branch feat/my-feature
    python scripts/git_forge.py --branch feat/my-feature --base main
"""

import argparse
import json
import sys
from pathlib import Path

# Add repo root to path to import arifos
# We are in scripts/, so repo root is parent
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from arifos.enforcement.trinity import analyze_branch


def main():
    parser = argparse.ArgumentParser(description="/gitforge - Analyze git branch changes")
    parser.add_argument("--branch", required=True, help="Feature branch to analyze")
    parser.add_argument("--base", default="main", help="Base branch (default: main)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        # Run forge analysis
        report = analyze_branch(branch_name=args.branch, base=args.base)

        if args.json:
            # JSON output for pipe to /gitQC
            print(json.dumps(report.__dict__, indent=2))
        else:
            # Human-readable output
            print("\n" + "=" * 60)
            print(f"🔨 /gitforge Analysis: {args.branch}")
            print("=" * 60)
            print(f"\nBranch: {report.branch}")
            print(f"Base commit: {report.base_commit[:8]}")
            print(f"Head commit: {report.head_commit[:8]}")
            print(f"\n📊 Metrics:")
            print(f"  Files changed: {len(report.files_changed)}")
            print(f"  Hot zones: {len(report.hot_zones)}")
            print(f"  Entropy delta (ΔS): {report.entropy_delta:.2f}")
            print(f"  Risk score: {report.risk_score:.3f}")
            print(f"\n📝 Notes:")
            for note in report.notes:
                print(f"  • {note}")
            print(f"\n⏰ Generated: {report.timestamp}")
            print("=" * 60 + "\n")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
