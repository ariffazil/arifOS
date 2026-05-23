#!/usr/bin/env python3
"""
arif_run — General shell command wrapper for arifOS Constitutional Kernel

Replace: direct bash/shell command execution
Usage:   arif_run "intent description" "command to run"
         arif_run --classify "command to check"

Tiers:
  ATOMIC/HIGH → HOLD (blocked)
  MEDIUM      → CAUTION (monitored)
  LOW         → PROCEED

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
Stage C — A-FORGE adapter wrapper
"""

import sys, re, json, os, argparse
from pathlib import Path

SOCK_PATH = os.environ.get("ARIFOS_SOCK", "/run/arifos.sock")
CONFIG_PATH = "/etc/arifos/apexd.yaml"

# -------------------------------------------------------------------------
# Deterministic classifier — same rules as apexd.py M2
# This is the LLM-free path. arif_run itself does NOT talk to apexd.
# It intercepts before the daemon even gets involved.
# -------------------------------------------------------------------------

ATOMIC_PATTERNS = [
    (re.compile(r"rm\s+-rf\s+/\s*$", re.I),          "F9 F13 ATOMIC: recursive root delete"),
    (re.compile(r"rm\s+-rf\s+/var", re.I),            "F9 F13 ATOMIC: system dir wipe"),
    (re.compile(r"rm\s+-rf\s+/etc", re.I),            "F9 F13 ATOMIC: config dir wipe"),
    (re.compile(r"rm\s+-rf\s+/usr", re.I),            "F9 F13 ATOMIC: /usr wipe"),
    (re.compile(r"mkfs", re.I),                      "F13 ATOMIC: filesystem destruction"),
    (re.compile(r"fdisk", re.I),                     "F13 ATOMIC: partition table destruction"),
    (re.compile(r"parted.*mklabel", re.I),           "F13 ATOMIC: partition destruction"),
    (re.compile(r"dd\s+if=/dev/zero\s+of=/dev/", re.I), "F13 ATOMIC: raw disk wipe"),
    (re.compile(r"iptables\s+-F\s*$", re.I),         "F13 ATOMIC: firewall flush"),
    (re.compile(r"iptables\s+-t\s+nat\s+-F", re.I),  "F13 ATOMIC: NAT table flush"),
    (re.compile(r"curl\s+.*\|\s*sh", re.I),           "F9 F13 ATOMIC: remote exec via pipe"),
    (re.compile(r"curl\s+.*\|\s*sudo\s+bash", re.I), "F9 F13 ATOMIC: sudo remote exec"),
    (re.compile(r"DROP\s+DATABASE", re.I),           "F13 ATOMIC: database destruction"),
    (re.compile(r"shutdown", re.I),                  "F13 ATOMIC: system shutdown"),
    (re.compile(r"reboot", re.I),                    "F13 ATOMIC: system reboot"),
    (re.compile(r":\(\)\s*:\s*\|\s*:\s*&", re.I),    "F9 ATOMIC: fork bomb"),
    (re.compile(r"chmod\s+-R?\s+0000\s+/", re.I),   "F9 F13 ATOMIC: remove all perms"),
]

HIGH_PATTERNS = [
    (re.compile(r"chmod\s+-R\s+777\s+/", re.I),      "F9: world-writable system"),
    (re.compile(r"chown\s+-R\s+root\s+/", re.I),      "F9 F13: ownership takeover"),
    (re.compile(r"systemctl\s+mask", re.I),           "F13 HIGH: service masking"),
    (re.compile(r"git\s+push\s+--force\s+.*main", re.I), "F13 HIGH: main branch force push"),
    (re.compile(r"eval\s+\$\(", re.I),                "F9 HIGH: eval injection"),
    (re.compile(r"chmod\s+[u+w]?s", re.I),           "F9 HIGH: setuid bit manipulation"),
]

CAUTION_PATTERNS = [
    (re.compile(r"git\s+push\s+--force", re.I),       "F13 CAUTION: force push"),
    (re.compile(r"systemctl\s+(stop|restart)", re.I),  "F13 CAUTION: service control"),
    (re.compile(r"chmod\s+-R\s+777", re.I),            "F9 CAUTION: broad permission change"),
    (re.compile(r"docker\s+rm\s+-f", re.I),            "F9 CAUTION: container destruction"),
    (re.compile(r"pkill\s+-9", re.I),                 "F13 CAUTION: force kill all processes"),
    (re.compile(r"kill\s+-9\s+1", re.I),              "F13 CAUTION: kill init"),
]

CRITICAL_SERVICES = ["ssh", "sshd", "systemd", "network", "firewalld",
                     "docker", "nginx", "apache2", "mysql", "postgresql"]

def classify(command: str) -> tuple:
    """Classify command without LLM. Returns (tier, verdict, rationale)."""
    if not command.strip():
        return ("LOW", "PROCEED", "No command — read-only")

    for pat, rationale in ATOMIC_PATTERNS:
        if pat.search(command):
            return ("ATOMIC", "HOLD", rationale)

    for pat, rationale in HIGH_PATTERNS:
        if pat.search(command):
            return ("HIGH", "HOLD", rationale)

    # Special: critical service control → HIGH regardless
    for svc in CRITICAL_SERVICES:
        svc_pattern = re.compile(
            rf"systemctl\s+(stop|restart|mask|disable)\b.*{svc}",
            re.I
        )
        if svc_pattern.search(command):
            return ("HIGH", "HOLD", f"F13 HIGH: critical service control — {svc}")

    for pat, rationale in CAUTION_PATTERNS:
        if pat.search(command):
            return ("MEDIUM", "CAUTION", rationale)

    return ("LOW", "PROCEED", "No deterministic risk detected")


def print_banner(tier: str, verdict: str, rationale: str, intent: str, command: str):
    sep = "=" * 60
    color = {"ATOMIC": "31", "HIGH": "33", "MEDIUM": "35", "LOW": "32"}.get(tier, "0")
    # Use ANSI codes if terminal supports
    try:
        sys.stdout.write(f"\033[1m\033[{color}m")
    except Exception:
        pass
    print(sep)
    print(f"arifOS Constitutional Kernel — arif_run")
    print(sep)
    print(f"  Intent:   {intent}")
    print(f"  Command:  {command}")
    print(sep)
    print(f"  Tier:     {tier}")
    print(f"  Verdict:  {verdict}")
    print(f"  Rationale: {rationale}")
    print(sep)
    try:
        sys.stdout.write("\033[0m")
    except Exception:
        pass

    if verdict == "HOLD":
        print("\n  ⚠  COMMAND BLOCKED BY CONSTITUTIONAL KERNEL")
        print("  To override: human must invoke 888_HOLD confirmation path")
    elif verdict == "CAUTION":
        print("\n  ⚠  COMMAND APPROVED WITH MONITORING")
        print("  arifOS will audit all side effects")

    print(sep)

    # Emit structured metadata for pipeline
    print(f"\n# arif_run metadata:")
    print(f"# __ARIF_VERDICT__={verdict}")
    print(f"# __ARIF_TIER__={tier}")
    print(f"# __ARIF_RATIONALE__={rationale}")
    print(f"# __ARIF_EPOCH__={__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}")
    print()


def execute(command: str) -> dict:
    """Execute command via subprocess. Returns result dict."""
    import subprocess, time
    start = time.time()
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            timeout=300,
            text=True,
        )
        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration_ms": round((time.time() - start) * 1000),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "exit_code": -1, "stdout": "", "stderr": "Timeout (300s)", "duration_ms": 300000}
    except Exception as e:
        return {"success": False, "exit_code": -1, "stdout": "", "stderr": str(e), "duration_ms": round((time.time() - start) * 1000)}


def main():
    parser = argparse.ArgumentParser(description="arifOS Constitutional Shell Wrapper")
    parser.add_argument("--classify", help="Classify command without executing")
    parser.add_argument("--intent", "-i", default="", help="Intent description")
    parser.add_argument("--json", action="store_true", help="Output JSON envelope")
    parser.add_argument("command", nargs="*", help="Command to run")
    args = parser.parse_args()

    if args.classify:
        cmd = args.classify
    elif args.command:
        cmd = " ".join(args.command)
    else:
        parser.print_help()
        sys.exit(0)

    intent = args.intent or cmd
    tier, verdict, rationale = classify(cmd)

    if args.json:
        print(json.dumps({
            "verdict": verdict, "tier": tier, "rationale": rationale,
            "intent": intent, "command": cmd,
            "command_blocked": verdict == "HOLD",
            "monitored": verdict == "CAUTION",
        }, indent=2))
        sys.exit(0)

    print_banner(tier, verdict, rationale, intent, cmd)

    if verdict == "HOLD":
        print(f"\n# COMMAND BLOCKED — exit 1")
        sys.exit(1)

    if verdict == "CAUTION":
        result = execute(cmd)
        # Log to audit trail
        audit_entry = {
            "verdict": "CAUTION",
            "tier": tier,
            "intent": intent,
            "command": cmd,
            "success": result["success"],
            "exit_code": result["exit_code"],
            "duration_ms": result["duration_ms"],
            "stderr": result["stderr"][:500],
        }
        try:
            audit_path = Path("/var/log/arifos/audit.log")
            audit_path.parent.mkdir(parents=True, exist_ok=True)
            with open(audit_path, "a") as f:
                f.write(json.dumps(audit_entry) + "\n")
        except Exception:
            pass

        print(f"\n# CAUTION mode — executing with monitoring")
        print(f"# Exit code: {result['exit_code']}")
        if result["stderr"]:
            print(f"# stderr: {result['stderr'][:200]}")
        if not result["success"]:
            sys.exit(result["exit_code"])
        sys.exit(0)

    # LOW/PROCEED — execute normally
    result = execute(cmd)
    if result["stdout"]:
        print(result["stdout"])
    if not result["success"] and result["stderr"]:
        print(result["stderr"], file=sys.stderr)
    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()