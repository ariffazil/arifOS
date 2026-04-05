#!/usr/bin/env python3
"""Verify that each commit being pushed has a recorded Ed25519 signature in VAULT999.
This script is intended to be called from a Git pre-push hook.
It reads the list of commits to be pushed (provided via stdin by Git) and checks
the VAULT999/commits.log file for a matching entry.
If any commit lacks a signature, the script exits with non‑zero status, aborting the push.
"""

import json
import sys
from pathlib import Path

VAULT_LOG = Path("C:/Users/User/arifOS/VAULT999/commits.log")


def load_signed_commits():
    signed = set()
    if VAULT_LOG.is_file():
        for line in VAULT_LOG.read_text().splitlines():
            try:
                entry = json.loads(line)
                signed.add(entry.get("commit"))
            except json.JSONDecodeError:
                continue
    return signed


def main():
    # Git passes refs to be pushed via stdin: <local> <local_sha> <remote> <remote_sha>
    signed_commits = load_signed_commits()
    missing = []
    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) != 4:
            continue
        local_ref, local_sha, remote_ref, remote_sha = parts
        # Determine the range of new commits (local_sha..remote_sha) if remote_sha not 0
        if remote_sha == "0" * 40:
            # New branch, compare against empty tree
            rev_range = f"{local_sha}"
        else:
            rev_range = f"{remote_sha}..{local_sha}"
        # Get list of commits in the range
        import subprocess

        result = subprocess.run(
            ["git", "rev-list", rev_range], capture_output=True, text=True, check=True
        )
        for commit in result.stdout.splitlines():
            if commit not in signed_commits:
                missing.append(commit)
    if missing:
        sys.stderr.write(
            f"[verify_commit_signatures] Missing signatures for commits: {', '.join(missing)}\n"
        )
        sys.exit(1)
    sys.stdout.write("[verify_commit_signatures] All pushed commits have signatures.\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
