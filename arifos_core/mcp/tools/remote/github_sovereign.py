"""
github_sovereign.py - Sovereign GitHub Bridge for arifOS

This module defines the interface for the Sovereign Witness to interact with
the remote GitHub repository, enforcing Constitutional governance on remote state.

Capabilities:
1. Manifest Verification (F2 Truth): Ensure remote and local specs match.
2. PR Auditing (F1 Amanah): Check PRs against constitutional floors.
3. CI Status Monitoring (F3 Tri-Witness): Observe remote build states.

Governance:
- All remote mutations must be preceded by a local SEAL verdict.
- Remote state is "Witnessed" but not "Trusted" until verified locally.
"""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional


# F1 (Amanah) Security: Mutating operations require human approval
MUTATING_OPS = {"merge_pr", "close_pr", "create_pr", "git_push"}
READ_ONLY_OPS = {"get_pr_status", "verify_remote_integrity", "audit_notifications"}


def require_human_approval(operation: str) -> None:
    """
    F1 (Amanah) GATE: Human approval required for mutating GitHub operations.

    Args:
        operation: Name of the operation (e.g., "merge_pr")

    Raises:
        PermissionError: If operation requires approval and no approval token present
    """
    if operation not in MUTATING_OPS:
        return  # Read-only operations don't need approval

    # Check for approval token in environment
    approval_token = os.getenv("ARIFOS_GITHUB_APPROVE_MUTATIONS")

    if not approval_token:
        raise PermissionError(
            f"F1 (Amanah) VIOLATION: '{operation}' requires human approval. "
            f"Set ARIFOS_GITHUB_APPROVE_MUTATIONS env var or use interactive mode."
        )


class SovereignGitHub:
    """
    Bridge interface for Sovereign GitHub operations.
    Leverages the GitHub MCP toolset or authenticated GLI (Git CLI).
    """

    @staticmethod
    def get_pr_status(pr_number: int) -> Dict[str, Any]:
        """
        Fetch status of a Pull Request using 'gh' CLI.
        Wrapped for sovereign audit logging.

        F1 (Amanah): READ-ONLY operation - no approval required
        """
        try:
            # Execute: gh pr view {N} --json ...
            cmd = ["gh", "pr", "view", str(pr_number), "--json", "number,state,title,body,mergeable,url"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {"error": result.stderr.strip(), "status": "cli_error"}

            data = json.loads(result.stdout)
            return {
                "action": "check_pr",
                "pr_number": data.get("number"),
                "status": data.get("state"),  # OPEN, MERGED, CLOSED
                "mergeable": data.get("mergeable"),
                "title": data.get("title"),
                "url": data.get("url"),
                "sovereign_check": "VERIFIED_BY_GH_CLI"
            }
        except Exception as e:
            return {"error": str(e), "status": "exception"}

    @staticmethod
    def verify_remote_integrity() -> bool:
        """
        Verify that the remote main branch matches the local sealed state.
        F2 Truth enforcement via 'git' CLI.
        """
        try:
            # 1. Fetch latest state (non-destructive)
            subprocess.run(["git", "fetch", "origin", "main"], capture_output=True, check=True)

            # 2. Get Local HEAD SHA
            local_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()

            # 3. Get Remote Main SHA
            remote_sha = subprocess.check_output(["git", "rev-parse", "origin/main"], text=True).strip()

            # 4. Compare (Strict Equality)
            return local_sha == remote_sha
        except Exception:
            # Fail-closed on any git error
            return False

    @staticmethod
    def audit_notifications(notifications: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Filter notifications for constitutional violations.
        If notifications is None, fetches from 'gh api notifications'.
        """
        if notifications is None:
            try:
                # Fetch via gh CLI
                cmd = ["gh", "api", "notifications", "--method", "GET"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    notifications = json.loads(result.stdout)
                else:
                    notifications = []
            except Exception:
                notifications = []

        critical_alerts = []
        for note in notifications:
            # F3 Burst/Peace logic: Check for failure/security keywords
            subject = note.get("subject", {})
            title_lower = subject.get("title", "").lower()

            is_critical = False

            # 1. CI Failures
            if "failure" in title_lower or "failed" in title_lower:
                is_critical = True

            # 2. Security Alerts
            if "security" in title_lower or "vulnerability" in title_lower:
                is_critical = True

            # 3. Constitutional Keywords ('void', 'breach')
            if "void" in title_lower or "breach" in title_lower:
                is_critical = True

            if is_critical:
                critical_alerts.append({
                    "id": note.get("id"),
                    "repo": note.get("repository", {}).get("full_name"),
                    "reason": "CONSTITUTIONAL_TRIGGER",
                    "title": subject.get("title"),
                    "url": subject.get("url")
                })

        return critical_alerts

    @staticmethod
    def merge_pr(pr_number: int) -> Dict[str, Any]:
        """
        Merge a PR via 'gh' CLI (Squash).

        F1 (Amanah): MUTATING operation - requires human approval
        """
        # F1 Amanah gate: Check approval before mutation
        require_human_approval("merge_pr")

        try:
            # gh pr merge {N} --squash --delete-branch
            # Explicitly non-interactive
            cmd = ["gh", "pr", "merge", str(pr_number), "--squash", "--delete-branch"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {"status": "MERGED", "pr_number": pr_number}
            return {"status": "error", "error": result.stderr.strip()}
        except Exception as e:
            return {"status": "exception", "error": str(e)}

    @staticmethod
    def close_pr(pr_number: int) -> Dict[str, Any]:
        """
        Close a PR via 'gh' CLI.

        F1 (Amanah): MUTATING operation - requires human approval
        """
        # F1 Amanah gate: Check approval before mutation
        require_human_approval("close_pr")

        try:
            cmd = ["gh", "pr", "close", str(pr_number)]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {"status": "CLOSED", "pr_number": pr_number}
            return {"status": "error", "error": result.stderr.strip()}
        except Exception as e:
            return {"status": "exception", "error": str(e)}

def main():
    """Main entry point for Sovereign GitHub Bridge."""
    print("Sovereign GitHub Bridge: Active")
    print("F1 (Amanah): Mutating operations require ARIFOS_GITHUB_APPROVE_MUTATIONS env var")
    print(f"Read-only ops: {', '.join(sorted(READ_ONLY_OPS))}")
    print(f"Mutating ops: {', '.join(sorted(MUTATING_OPS))}")

if __name__ == "__main__":
    main()  # Fixed: Removed duplicate call
