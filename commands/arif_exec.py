#!/usr/bin/env python3
"""
arif_exec — Script execution wrapper for arifOS Constitutional Kernel

Usage:   arif_exec "intent" /path/to/script.sh
         arif_exec --dry-run /path/to/script.sh

Reads script content, classifies all patterns found inside,
then executes if cleared. Provides full audit trail.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
Stage C — A-FORGE adapter wrapper
"""

import sys, re, json, argparse
from pathlib import Path

def classify_patterns_in_content(content: str) -> list:
    """Scan script content for dangerous patterns."""
    findings = []

    patterns = [
        (re.compile(r"rm\s+-rf\s+/\s*$", re.I), "ATOMIC", "rm -rf /"),
        (re.compile(r"rm\s+-rf\s+/var", re.I), "ATOMIC", "rm -rf /var"),
        (re.compile(r"mkfs", re.I), "ATOMIC", "mkfs"),
        (re.compile(r"fdisk", re.I), "ATOMIC", "fdisk"),
        (re.compile(r"dd\s+if=/dev/zero\s+of=/dev/", re.I), "ATOMIC", "dd disk wipe"),
        (re.compile(r"iptables\s+-F", re.I), "ATOMIC", "iptables -F"),
        (re.compile(r"curl\s+.*\|\s*sh", re.I), "ATOMIC", "curl | sh"),
        (re.compile(r"DROP\s+(TABLE|DATABASE)", re.I), "ATOMIC", "DROP statement"),
        (re.compile(r"chmod\s+-R\s+777\s+/", re.I), "HIGH", "chmod -R 777 /"),
        (re.compile(r"systemctl\s+mask", re.I), "HIGH", "systemctl mask"),
        (re.compile(r"git\s+push\s+--force\s+.*main", re.I), "HIGH", "git force push main"),
        (re.compile(r"eval\s+\$\(", re.I), "HIGH", "eval injection"),
    ]

    for pat, tier, name in patterns:
        if pat.search(content):
            findings.append({"pattern": name, "tier": tier, "matched": pat.search(content).group()})

    return findings


def main():
    parser = argparse.ArgumentParser(description="arifOS Script Execution Wrapper")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, don't execute")
    parser.add_argument("--intent", "-i", default="", help="Intent description")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("script_path", nargs="?", help="Path to script file")
    args = parser.parse_args()

    if not args.script_path:
        parser.print_help()
        sys.exit(0)

    intent = args.intent or args.script_path
    path = Path(args.script_path)

    if not path.exists():
        result = {"verdict": "VOID", "error": f"Script not found: {args.script_path}"}
        print(json.dumps(result, indent=2) if args.json else f"❌ {result['error']}")
        sys.exit(1)

    try:
        content = path.read_text()
    except Exception as e:
        result = {"verdict": "VOID", "error": f"Cannot read script: {e}"}
        print(json.dumps(result, indent=2) if args.json else f"❌ {result['error']}")
        sys.exit(1)

    findings = classify_patterns_in_content(content)

    # Determine overall verdict
    atomic_found = [f for f in findings if f["tier"] == "ATOMIC"]
    high_found   = [f for f in findings if f["tier"] == "HIGH"]

    if atomic_found:
        verdict = "HOLD"
        rationale = f"ATOMIC patterns in script: {', '.join(f['pattern'] for f in atomic_found)}"
        tier = "ATOMIC"
    elif high_found:
        verdict = "HOLD"
        rationale = f"HIGH patterns in script: {', '.join(f['pattern'] for f in high_found)}"
        tier = "HIGH"
    else:
        verdict = "SEAL"
        rationale = "Script cleared — no dangerous patterns detected"
        tier = "LOW"

    result = {
        "verdict": verdict, "tier": tier,
        "intent": intent, "script": str(path),
        "rationale": rationale,
        "findings": findings,
        "script_size_bytes": len(content),
        "lines": content.count('\n') + 1,
        "command_blocked": verdict == "HOLD",
    }

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0)

    print("=" * 60)
    print(f"arifOS — arif_exec")
    print("=" * 60)
    print(f"  Script:  {path}")
    print(f"  Intent:  {intent}")
    print(f"  Size:    {result['script_size_bytes']} bytes, {result['lines']} lines")
    print("-" * 60)
    if findings:
        print(f"  Patterns found: {len(findings)}")
        for f in findings:
            print(f"    [{f['tier']}] {f['pattern']} → {f['matched'][:60]}")
    else:
        print(f"  Patterns found: none")
    print("-" * 60)
    print(f"  Verdict: {verdict}")
    print(f"  Rationale: {rationale}")
    print("=" * 60)

    if verdict == "HOLD":
        print(f"\n⚠  SCRIPT BLOCKED — exit 1")
        print("To override: invoke 888_HOLD with human confirmation")
        sys.exit(1)

    if args.dry_run:
        print(f"\n✅ Dry run complete — script would execute")
        sys.exit(0)

    # Execute
    import subprocess
    print(f"\nExecuting script...")
    r = subprocess.run(["bash", str(path)], capture_output=True, text=True)
    if r.stdout: print(r.stdout)
    if r.stderr: print(r.stderr, file=sys.stderr)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()