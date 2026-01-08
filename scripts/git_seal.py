#!/usr/bin/env python3
"""
git_seal.py - CLI wrapper for /gitseal human authority gate

Usage:
    python scripts/git_seal.py APPROVE --branch feat/x --human "Arif" --reason "Ready"
    python scripts/git_seal.py REJECT --reason "Needs more tests"
    python scripts/git_seal.py HOLD --reason "Awaiting stakeholder review"
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path to import arifos_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos_core.enforcement.trinity import (
    analyze_branch,
    execute_seal,
    propose_docs,
    validate_changes,
)


def main():
    parser = argparse.ArgumentParser(description="/gitseal - Human authority gate for code changes")
    parser.add_argument(
        "decision",
        choices=["APPROVE", "REJECT", "HOLD"],
        help="Seal decision",
    )
    parser.add_argument("--branch", help="Feature branch (required for APPROVE)")
    parser.add_argument(
        "--human",
        default="Unknown",
        help="Human authority name (e.g. 'Muhammad Arif bin Fazil')",
    )
    parser.add_argument("--reason", required=True, help="Reason for decision")
    parser.add_argument("--current-version", default="45.0.0", help="Current version")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        # APPROVE requires branch analysis
        if args.decision == "APPROVE":
            if not args.branch:
                print("Error: --branch required for APPROVE", file=sys.stderr)
                sys.exit(1)

            print("🔨 Running /gitforge analysis...")
            forge_report = analyze_branch(branch_name=args.branch)

            print("🔍 Running /gitQC validation...")
            qc_report = validate_changes(forge_report)

            print("📝 Generating housekeeper proposal...")
            housekeeper_proposal = propose_docs(forge_report, qc_report, args.current_version)

            print("\n" + "=" * 60)
            print("📋 /GITSEAL SUMMARY")
            print("=" * 60)
            print(
                f"\n🔨 Forge: {len(forge_report.files_changed)} files, "
                f"ΔS={forge_report.entropy_delta:.2f}, "
                f"risk={forge_report.risk_score:.2f}"
            )
            print(f"🔍 QC: {qc_report.verdict}, ZKPC={qc_report.zkpc_id}")
            print(
                f"📝 Housekeeper: {housekeeper_proposal.version_bump} → "
                f"v{housekeeper_proposal.new_version}"
            )
            print("\n" + "=" * 60)
            print(f"\n⏸️  AWAITING HUMAN DECISION...")
            print(f"\nYou chose: {args.decision}")
            print(f"Authority: {args.human}")
            print(f"Reason: {args.reason}")
            print("\n" + "=" * 60)

            print("\n⚙️  Executing /gitseal...")
            seal_decision = execute_seal(
                decision=args.decision,
                branch=args.branch,
                human_authority=args.human,
                reason=args.reason,
                forge_report=forge_report,
                qc_report=qc_report,
                housekeeper_proposal=housekeeper_proposal,
            )

        else:
            # REJECT or HOLD - minimal ledger entry only
            from arifos_core.enforcement.trinity.forge import ForgeReport
            from arifos_core.enforcement.trinity.housekeeper import HousekeeperProposal
            from arifos_core.enforcement.trinity.qc import QCReport

            # Create placeholder reports for ledger
            forge_report = ForgeReport(
                files_changed=[],
                hot_zones=[],
                entropy_delta=0.0,
                risk_score=0.0,
                timestamp="",
                branch=args.branch or "unknown",
                base_commit="",
                head_commit="",
            )
            qc_report = QCReport(
                floors_passed={},
                zkpc_id="",
                verdict="N/A",
                timestamp="",
            )
            housekeeper_proposal = HousekeeperProposal(
                version_bump="none",
                new_version="N/A",
                changelog_entry="",
            )

            seal_decision = execute_seal(
                decision=args.decision,
                branch=args.branch or "N/A",
                human_authority=args.human,
                reason=args.reason,
                forge_report=forge_report,
                qc_report=qc_report,
                housekeeper_proposal=housekeeper_proposal,
            )

        # Output result
        if args.json:
            print(json.dumps(seal_decision.__dict__, indent=2))
        else:
            print("\n" + "=" * 60)
            print(f"✅ /GITSEAL COMPLETE")
            print("=" * 60)
            print(f"\nVerdict: {seal_decision.verdict}")
            if seal_decision.bundle_hash:
                print(f"Bundle hash: {seal_decision.bundle_hash}")
                print(f"Commit: {seal_decision.commit_hash}")
                print(f"Tag: {seal_decision.tag}")
            print(f"Ledger entry: {seal_decision.ledger_entry_id}")
            print(f"Timestamp: {seal_decision.timestamp}")
            print("\n" + "=" * 60 + "\n")

        # Exit with appropriate code
        if seal_decision.verdict == "APPROVED":
            sys.exit(100)  # SEALED exit code
        elif seal_decision.verdict == "HOLD":
            sys.exit(88)  # HOLD exit code
        else:
            sys.exit(0)  # REJECTED - clean exit

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(255)


if __name__ == "__main__":
    main()
