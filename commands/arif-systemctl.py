#!/usr/bin/env python3
"""
arif-systemctl — Service control wrapper for arifOS Constitutional Kernel

Usage:   arif-systemctl start|stop|restart|enable|disable|mask SERVICE
         arif-systemctl --dry-run stop docker

Every systemd operation goes through this wrapper.
Critical services (ssh, docker, network, etc.) always prompt HOLD
unless explicitly confirmed via 888_HOLD.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
Stage C — A-FORGE adapter wrapper
"""

import sys, re, json, argparse, subprocess, os
from pathlib import Path

# Services whose control always requires elevated scrutiny
CRITICAL_SERVICES = {
    "ssh", "sshd", "systemd", "network", "firewalld",
    "docker", "docker.socket", "containerd",
    "nginx", "apache2", "httpd",
    "mysql", "mariadb", "postgresql", "redis",
    "caddy", "traefik",
    # arifOS itself
    "arifos", "arifos.socket",
}

# Services where stop/restart = HIGH risk
RISKY_ACTIONS = {"stop", "restart", "mask", "disable"}
NEUTRAL_ACTIONS = {"start", "enable", "reload", "status", "is-active", "show"}


def classify(service: str, action: str) -> tuple:
    """Classify systemctl operation. Returns (tier, verdict, rationale)."""
    svc_key = service.replace(".service", "").replace(".socket", "")
    svc_key_base = svc_key.split("-")[0]  # e.g. "docker" from "docker.socket"

    # Any action on a critical service
    if svc_key in CRITICAL_SERVICES or svc_key_base in CRITICAL_SERVICES:
        if action in RISKY_ACTIONS:
            return ("ATOMIC", "HOLD",
                    f"F13 ATOMIC: critical service '{service}' {action} — requires 888_HOLD")
        elif action == "mask":
            return ("HIGH", "HOLD",
                    f"F13 HIGH: masking critical service '{service}'")
        else:
            return ("MEDIUM", "CAUTION",
                    f"F13 CAUTION: critical service '{service}' {action}")

    # Any mask operation on any service
    if action == "mask":
        return ("HIGH", "HOLD", f"F13 HIGH: service masking — {service}")

    # Risky action on non-critical
    if action in RISKY_ACTIONS:
        return ("MEDIUM", "CAUTION", f"F13 CAUTION: {action} on {service}")

    return ("LOW", "PROCEED", f"Service control {action} on {service} — no risk")


def execute_systemctl(action: str, service: str) -> dict:
    """Execute actual systemctl command. Returns result dict."""
    import time
    start = time.time()
    try:
        result = subprocess.run(
            ["systemctl", action, service],
            capture_output=True, text=True, timeout=60
        )
        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "duration_ms": round((time.time() - start) * 1000),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "exit_code": -1, "stdout": "", "stderr": "Timeout (60s)", "duration_ms": 60000}
    except FileNotFoundError:
        return {"success": False, "exit_code": -1, "stdout": "", "stderr": "systemctl not found", "duration_ms": 0}
    except Exception as e:
        return {"success": False, "exit_code": -1, "stdout": "", "stderr": str(e), "duration_ms": 0}


def main():
    parser = argparse.ArgumentParser(description="arifOS Service Control Wrapper")
    parser.add_argument("--dry-run", action="store_true", help="Classify only")
    parser.add_argument("--intent", "-i", default="", help="Intent description")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--force", action="store_true", help="Skip HOLD — 888_HOLD already confirmed")
    parser.add_argument("action", nargs="?", help="systemctl action")
    parser.add_argument("service", nargs="?", help="Service name")
    args = parser.parse_args()

    if not args.action or not args.service:
        # List critical services and exit
        print("arifOS — arif-systemctl")
        print(f"Critical services: {', '.join(sorted(CRITICAL_SERVICES))}")
        print("\nUsage: arif-systemctl <action> <service>")
        print("Actions: start, stop, restart, enable, disable, mask, status")
        print("Use --force only with 888_HOLD confirmation")
        sys.exit(0)

    intent = args.intent or f"systemctl {args.action} {args.service}"
    action = args.action.lower()
    service = args.service

    tier, verdict, rationale = classify(service, action)

    result = {
        "verdict": verdict, "tier": tier,
        "intent": intent, "action": action, "service": service,
        "rationale": rationale,
        "critical_service": service in CRITICAL_SERVICES,
        "action_blocked": verdict in ("HOLD", "VOID"),
        "monitored": verdict == "CAUTION",
        "force": args.force,
    }

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0)

    print("=" * 60)
    print("arifOS — arif-systemctl (Service Control Wrapper)")
    print("=" * 60)
    print(f"  Intent:   {intent}")
    print(f"  Action:   {action}")
    print(f"  Service:  {service}")
    print(f"  Critical: {result['critical_service']}")
    print(f"  Tier:     {tier}")
    print(f"  Verdict:  {verdict}")
    print(f"  Rationale: {rationale}")
    print("=" * 60)

    if verdict == "HOLD":
        print("\n⚠  SERVICE CONTROL BLOCKED")
        if not args.force:
            print("To override: 888_HOLD confirmation from Arif required")
            print("Use --force only if 888_HOLD has been confirmed")
        print("systemctl was NOT called. Exiting.")
        sys.exit(1)

    if verdict == "CAUTION":
        print("\n⚠  SERVICE CONTROL — MONITORED MODE")
        print("All state changes logged to /var/log/arifos/audit.log")

    if args.dry_run:
        print(f"\n✅ Dry run complete — would execute: systemctl {action} {service}")
        sys.exit(0)

    # Log before execution
    try:
        audit = Path("/var/log/arifos/audit.log")
        audit.parent.mkdir(parents=True, exist_ok=True)
        import datetime
        entry = json.dumps({
            "epoch": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "actor": "arif-systemctl",
            "verdict": verdict,
            "tier": tier,
            "action": action, "service": service,
            "intent": intent,
        })
        with open(audit, "a") as f:
            f.write(entry + "\n")
    except Exception:
        pass

    # Execute
    print(f"\nExecuting: systemctl {action} {service}")
    exec_result = execute_systemctl(action, service)
    print(f"Exit code: {exec_result['exit_code']}")
    if exec_result["stdout"]:
        print(exec_result["stdout"])
    if exec_result["stderr"]:
        print(exec_result["stderr"], file=sys.stderr)
    sys.exit(exec_result["exit_code"])


if __name__ == "__main__":
    main()