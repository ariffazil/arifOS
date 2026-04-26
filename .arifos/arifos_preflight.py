#!/usr/bin/env python3
import sys
import os
import subprocess
import json
from datetime import datetime, timezone

VAULT_PATH = "/root/.agent-workbench/vault999.jsonl"

def log_event(agent_id, action, target, status, message):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "agent": agent_id,
        "action": action,
        "target": target,
        "status": status,
        "message": message
    }
    try:
        with open(VAULT_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"FAILED TO LOG TO VAULT: {e}", file=sys.stderr)

def get_git_root(filepath):
    """Dynamically find the git root for the target file."""
    dirname = os.path.dirname(os.path.abspath(filepath))
    try:
        result = subprocess.run(
            ["git", "-C", dirname, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def check_git_status(filepath):
    git_root = get_git_root(filepath)
    if not git_root:
        return None # Not in a git repo
    
    try:
        # Check for uncommitted changes in the specific file relative to its git root
        result = subprocess.run(
            ["git", "-C", git_root, "diff", "--name-only", filepath],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip() != ""
    except subprocess.CalledProcessError:
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: arifos_preflight.py <agent_id> <target_file>")
        sys.exit(1)

    agent_id = sys.argv[1]
    target_file = os.path.abspath(sys.argv[2])
    
    # 1. Physical Integrity Check
    if not os.path.exists(target_file):
        log_event(agent_id, "PREFLIGHT", target_file, "ERROR", "File does not exist")
        print(f"[888-HOLD] Target file {target_file} not found.")
        sys.exit(1)

    # 2. Information Asymmetry (Git Diff) Check
    is_dirty = check_git_status(target_file)
    
    if is_dirty is True:
        log_event(agent_id, "PREFLIGHT", target_file, "HOLD", "Uncommitted changes detected")
        print(f"[888-HOLD] UNCOMMITTED CHANGES DETECTED IN {target_file}")
        print("F1 Violation: Resource is in a state of high entropy. Potential collision.")
        sys.exit(1)
    elif is_dirty is False:
        log_event(agent_id, "PREFLIGHT", target_file, "PASS", "File is clean")
        print(f"[PASS] Pre-flight successful for {target_file}")
        sys.exit(0)
    else:
        # File is not tracked or not in a git repo
        log_event(agent_id, "PREFLIGHT", target_file, "QUALIFY", "Untracked/Non-Git file")
        print(f"[QUALIFY] {target_file} is not under version control. Proceeding with caution.")
        sys.exit(0)

if __name__ == "__main__":
    main()
