#!/usr/bin/env python3
"""
arif_sudo — Privileged action wrapper for arifOS Constitutional Kernel

Usage:   arif_sudo "intent" "command to run with privilege"

All sudo/invasive commands go through this wrapper.
The wrapper classifies BEFORE calling the actual sudo.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
Stage C — A-FORGE adapter wrapper
"""

import sys, re, json, argparse, os
from pathlib import Path

CRITICAL_SERVICES = ["ssh", "sshd", "systemd", "network", "firewalld",
                     "docker", "nginx", "apache2", "mysql", "postgresql"]

ATOMIC_PATTERNS = [
    (re.compile(r"rm\s+-rf\s+/\s*$", re.I), "F9 F13: root recursive delete"),
    (re.compile(r"rm\s+-rf\s+/var\s+/usr", re.I), "F9 F13: system dir wipe"),
    (re.compile(r"mkfs", re.I), "F13: filesystem destruction"),
    (re.compile(r"fdisk", re.I), "F13: partition table destruction"),
    (re.compile(r"dd\s+if=/dev/zero\s+of=/dev/", re.I), "F13: raw disk wipe"),
    (re.compile(r"iptables\s+-F", re.I), "F13: firewall flush"),
    (re.compile(r"curl\s+.*\|\s*sh", re.I), "F9 F13: remote exec pipe"),
    (re.compile(r"DROP\s+DATABASE", re.I), "F13: database destruction"),
    (re.compile(r"shutdown", re.I), "F13: system shutdown"),
    (re.compile(r"reboot", re.I), "F13: system reboot"),
    (re.compile(r":\(\)\s*:", re.I), "F9: fork bomb"),
]

HIGH_PATTERNS = [
    (re.compile(r"chmod\s+-R\s+777\s+/", re.I), "F9: world-writable system"),
    (re.compile(r"chown\s+-R\s+root\s+/", re.I), "F9 F13: ownership takeover"),
    (re.compile(r"systemctl\s+(stop|restart|mask)\s+(ssh|sshd|systemd|network|docker)", re.I), "F13: critical service control"),
    (re.compile(r"systemctl\s+mask", re.I), "F13: service masking"),
    (re.compile(r"git\s+push\s+--force", re.I), "F13: force push"),
    (re.compile(r"eval\s+\$\(", re.I), "F9: eval injection"),
]

CAUTION_PATTERNS = [
    (re.compile(r"systemctl\s+(stop|restart)", re.I), "F13: service control"),
    (re.compile(r"chmod\s+-R\s+777", re.I), "F9: permission change"),
    (re.compile(r"docker\s+(rm|stop)\s+-f", re.I), "F9: container destruction"),
]

def classify(command: str):
    for pat, rationale in ATOMIC_PATTERNS:
        if pat.search(command):
            return ("ATOMIC", "HOLD", rationale)
    for pat, rationale in HIGH_PATTERNS:
        if pat.search(command):
            return ("HIGH", "HOLD", rationale)
    for pat, rationale in CAUTION_PATTERNS:
        if pat.search(command):
            return ("MEDIUM", "CAUTION", rationale)
    return ("LOW", "PROCEED", "No risk detected in privileged context")


def main():
    parser = argparse.ArgumentParser(description="arifOS Sudo Escalation Wrapper")
    parser.add_argument("--classify", help="Classify without executing")
    parser.add_argument("--intent", "-i", default="", help="Intent")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("command", nargs="*", help="Command to run")
    args = parser.parse_args()

    cmd = args.classify or " ".join(args.command) if args.command else ""
    intent = args.intent or cmd

    if not cmd:
        parser.print_help()
        sys.exit(0)

    tier, verdict, rationale = classify(cmd)

    result = {
        "verdict": verdict, "tier": tier,
        "intent": intent, "command": cmd,
        "rationale": rationale,
        "escalation_denied": verdict == "HOLD",
        "escalation_monitored": verdict == "CAUTION",
    }

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0)

    print("=" * 60)
    print("arifOS — arif_sudo (Privileged Action Wrapper)")
    print("=" * 60)
    print(f"  Intent:   {intent}")
    print(f"  Command:  {cmd}")
    print(f"  Tier:     {tier}")
    print(f"  Verdict:  {verdict}")
    print(f"  Rationale: {rationale}")
    print("=" * 60)

    if verdict == "HOLD":
        print("\n⚠  PRIVILEGE ESCALATION DENIED")
        print("This command requires human confirmation via 888_HOLD")
        print("sudo was NOT called. Exiting.")
        sys.exit(1)

    if verdict == "CAUTION":
        print("\n⚠  PRIVILEGE ESCALATION — MONITORED MODE")
        print("All side effects will be logged to /var/log/arifos/audit.log")
        # Log to audit
        try:
            audit = Path("/var/log/arifos/audit.log")
            audit.parent.mkdir(parents=True, exist_ok=True)
            import datetime
            entry = json.dumps({
                "epoch": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "actor": "arif_sudo",
                "verdict": "CAUTION",
                "tier": "MEDIUM",
                "intent": intent,
                "command": cmd,
                "rationale": rationale,
            })
            with open(audit, "a") as f:
                f.write(entry + "\n")
        except Exception:
            pass

    # Execute actual sudo
    import subprocess
    print(f"\nExecuting via sudo: {cmd}")
    r = subprocess.run(f"sudo {cmd}", shell=True, capture_output=True, text=True)
    if r.stdout: print(r.stdout)
    if r.stderr: print(r.stderr, file=sys.stderr)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()