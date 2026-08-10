#!/usr/bin/env python3
"""Commit + PR + merge the README sync — assumes README already updated by sync_readme_sot.py dry-run."""
import subprocess
import sys
from pathlib import Path

REPOS = ["arifOS", "GEOX", "WEALTH", "WELL", "HERMES", "arifFLOW", "A-FORGE", "AAA", "arif-fazil.com"]
BRANCH = "docs/sync-readme-sot-2026-08-10"

for repo in REPOS:
    base = Path(f"/root/{repo}")
    if not (base / ".git").exists():
        print(f"NO-GIT {repo}"); continue
    # Checkout new branch
    subprocess.run(["git", "checkout", "-B", BRANCH], cwd=base, capture_output=True, text=True)
    subprocess.run(["git", "add", "README.md"], cwd=base, capture_output=True, text=True)
    res = subprocess.run(["git", "commit", "-m", "docs: sync README to federation SOT v2026.08.09 + CI governance"], cwd=base, capture_output=True, text=True)
    if "nothing to commit" in res.stdout + res.stderr:
        print(f"NO-CHANGE {repo}"); continue
    res = subprocess.run(["git", "push", "-u", "origin", BRANCH], cwd=base, capture_output=True, text=True)
    if "rejected" in res.stderr:
        print(f"PUSH-FAIL {repo}: {res.stderr[:100]}"); continue
    res = subprocess.run(["gh", "pr", "create", "--head", BRANCH, "--base", "main", "--title", "docs: sync README to federation SOT v2026.08.09 + CI governance", "--body", "F13 verdict 2026-08-10 — README SOT sync. DITEMPA BUKAN DIBERI"], cwd=base, capture_output=True, text=True)
    pr_url = res.stdout.strip().splitlines()[-1] if res.stdout else ""
    pr_num = ""
    for part in pr_url.split("/"):
        if part.isdigit(): pr_num = part; break
    if pr_num:
        res = subprocess.run(["gh", "pr", "merge", pr_num, "--squash", "--admin", "--delete-branch"], cwd=base, capture_output=True, text=True)
        if "MERGED" in res.stdout + res.stderr or res.returncode == 0:
            print(f"MERGED {repo} PR #{pr_num}")
        else:
            print(f"MERGE-FAIL {repo}: {res.stderr[:100]}")
    else:
        print(f"PR-FAIL {repo}: {res.stderr[:120]}")
