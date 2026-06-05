#!/usr/bin/env python3
"""Pre-execution governance gate for CLI agents (Kimi, Claude, etc.).

Routes dangerous operations through arifOS 888_JUDGE before execution.
Non-dangerous operations pass through instantly.

Usage:
    python3 /root/arifOS/core/governance/preflight.py "git push --force origin main"
    python3 /root/arifOS/core/governance/preflight.py "docker rm -f container"
    python3 /root/arifOS/core/governance/preflight.py "npm install"  # passes instantly

Returns:
    0 = SEAL (proceed)
    1 = HOLD (ask Arif)
    2 = VOID (blocked)
    3 = NON_DANGEROUS (proceed instantly, no arifOS call)

DANGEROUS_PATTERNS determine what gets routed to arifOS.
Everything else passes through with exit code 3.
"""

import re
import subprocess
import sys

# ── Patterns that trigger governance ──────────────────────────────────
# Only operations with irreversible or wide-reaching consequences.
# Conservative: when in doubt, classify as dangerous.

DANGEROUS_PATTERNS = [
    # Git — destructive mutations
    (r"git\s+push\s+.*(-f|--force)", "git force push"),
    (r"git\s+push\s+.*--delete", "git delete remote branch"),
    (r"git\s+reset\s+--hard", "git hard reset"),
    (r"git\s+clean\s+-[fdx]+", "git clean"),

    # Docker — container/data destruction
    (r"docker\s+rm\s+-f", "docker force remove"),
    (r"docker\s+system\s+prune", "docker system prune"),
    (r"docker\s+volume\s+(rm|prune)", "docker volume remove"),
    (r"docker\s+compose\s+down\s+-v", "docker compose down with volumes"),

    # Filesystem — mass deletion (only exact rm -rf /, not /tmp etc.)
    (r"rm\s+-rf\s+/[^t]", "rm -rf dangerous path"),
    (r"rm\s+-rf\s+\$HOME", "rm -rf home"),
    (r"rm\s+-rf\s+~", "rm -rf home"),
    (r"rm\s+-rf\s+\.\s*$", "rm -rf current dir"),
    (r"find\s+.*\s+-delete\s+/", "find with delete on root"),
    (r">\s*/etc/", "redirect to /etc/"),

    # System — service/file mutations
    (r"systemctl\s+(stop|disable|mask)", "systemctl stop/disable"),
    (r"chmod\s+777", "chmod 777"),
    (r"chown\s+-R\s+", "recursive chown"),

    # Secrets
    (r"curl.*Authorization.*Bearer", "curl with auth bearer"),
    (r"gpg\s+--delete-secret", "gpg delete secret"),

    # Deployments
    (r"rsync\s+.*/var/www", "rsync to /var/www"),
    (r"rsync\s+.*/etc/", "rsync to /etc/"),
    (r"scp\s+.*/etc/", "scp to /etc/"),
    (r"ansible-playbook", "ansible playbook"),
    (r"terraform\s+(apply|destroy)", "terraform apply/destroy"),
]

ARIFOS_JUDGE_URL = "http://127.0.0.1:8088/mcp"


def classify(command: str) -> tuple[str, str] | None:
    """Return (pattern_description, matched_text) if dangerous, else None."""
    for pattern, description in DANGEROUS_PATTERNS:
        match = re.search(pattern, command)
        if match:
            return description, match.group(0)
    return None


def judge(command: str, description: str) -> int:
    """Route to arifOS 888_JUDGE via MCP call. Returns 0/1/2."""
    import json
    import urllib.request

    body = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "arif_judge_deliberate",
            "arguments": {
                "mode": "judge",
                "candidate": command,
                "session_id": "preflight-auto",
                "evidence_receipt": {"source": "preflight-sidecar", "pattern": description}
            }
        },
        "id": 1,
    }).encode()

    try:
        req = urllib.request.Request(
            ARIFOS_JUDGE_URL,
            data=body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            verdict = result.get("result", {}).get("content", [{}])[0].get("text", "")
            if "SEAL" in verdict:
                return 0
            elif "HOLD" in verdict:
                return 1
            elif "VOID" in verdict:
                return 2
            return 1  # default: HOLD
    except Exception as e:
        # Fail closed — if arifOS is unreachable, HOLD
        print(f"PREFLIGHT: arifOS unreachable ({e}). Holding for safety.", file=sys.stderr)
        return 1


def main():
    if len(sys.argv) < 2:
        print("Usage: preflight.py '<command>'", file=sys.stderr)
        sys.exit(1)

    command = " ".join(sys.argv[1:])

    # Step 1: classify
    result = classify(command)
    if result is None:
        print(f"PREFLIGHT: non-dangerous — proceed")
        sys.exit(3)  # NON_DANGEROUS

    description, matched = result
    print(f"PREFLIGHT: DANGEROUS pattern detected: {description} → '{matched}'")

    # Step 2: judge
    verdict = judge(command, description)

    if verdict == 0:
        print(f"PREFLIGHT: arifOS verdict = SEAL — proceed")
        sys.exit(0)
    elif verdict == 2:
        print(f"PREFLIGHT: arifOS verdict = VOID — BLOCKED")
        sys.exit(2)
    else:
        print(f"PREFLIGHT: arifOS verdict = HOLD — escalate to Arif (F13 SOVEREIGN)")
        sys.exit(1)


if __name__ == "__main__":
    main()
