#!/usr/bin/env python3
"""
arifos_copilot_relay.py — Copilot Governance CLI Relay Client
════════════════════════════════════════════════════════════════════════════════

CLI tool to relay Copilot output to the arifOS Copilot Governance Gateway.

Usage:
    echo "Copilot output here" | python3 /root/arifOS/scripts/arifos_copilot_relay.py --session <id> --api-key <key>

    python3 /root/arifOS/scripts/arifos_copilot_relay.py --file copilot_output.txt --session <id> --api-key <key>

Exit codes:
    0 = PARTIAL or SEAL (output allowed)
    1 = HOLD (output blocked, requires ARIF review)
    2 = VOID (output rejected, constitutional violation)
    3 = ERROR (network failure, auth failure)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid

import urllib.error
import urllib.request

DEFAULT_GATEWAY = os.environ.get("ARIFOS_COPILOT_GATEWAY_URL", "http://localhost:8090")
DEFAULT_API_KEY = os.environ.get("ARIFOS_COPILOT_API_KEY", "")


def relay(
    copilot_output: str,
    session_id: str,
    gateway_url: str,
    api_key: str,
    actor_id: str = "ARIF",
    trigger: str = "MANUAL",
) -> dict:
    """POST copilot output to the gateway and return the verdict JSON."""
    payload = {
        "session_id": session_id,
        "actor_id": actor_id,
        "copilot_output": copilot_output,
        "trigger": trigger,
        "metadata": {
            "relay": "cli",
            "python_version": sys.version.split()[0],
        },
    }

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{gateway_url}/copilot/ingest",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Key": api_key,
            "X-Request-ID": f"cli-{uuid.uuid4().hex[:12]}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8") if e.fp else ""
        try:
            body_json = json.loads(body_text)
        except Exception:
            body_json = {"error": body_text}
        sys.stderr.write(f"ERROR: Gateway returned {e.code} {e.reason}: {body_json}\n")
        sys.exit(3)
    except urllib.error.URLError as e:
        sys.stderr.write(f"ERROR: Cannot reach gateway at {gateway_url}: {e.reason}\n")
        sys.exit(3)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="arifOS Copilot Governance CLI Relay",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--session", default=str(uuid.uuid4()), help="Governed session ID")
    parser.add_argument("--gateway", default=DEFAULT_GATEWAY, help="Gateway URL")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="API key")
    parser.add_argument("--actor", default="ARIF", help="Actor ID")
    parser.add_argument("--trigger", default="MANUAL", help="Trigger: MANUAL|AUTO|TEAMS")
    parser.add_argument("--file", dest="input_file", type=str, help="Read from file")
    parser.add_argument("--stdin", action="store_true", help="Read from stdin")
    parser.add_argument("--json-only", action="store_true", help="Output JSON only")

    args = parser.parse_args()

    # Read copilot output
    if args.input_file:
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                copilot_output = f.read()
        except FileNotFoundError:
            sys.stderr.write(f"ERROR: File not found: {args.input_file}\n")
            return 3
        except Exception as e:
            sys.stderr.write(f"ERROR: Cannot read file: {e}\n")
            return 3
    elif args.stdin or not sys.stdin.isatty():
        copilot_output = sys.stdin.read()
    else:
        sys.stderr.write("ERROR: No input. Use --file or pipe input via stdin.\n")
        parser.print_help()
        return 3

    if not copilot_output.strip():
        sys.stderr.write("ERROR: Empty Copilot output.\n")
        return 3

    # Call gateway
    result = relay(
        copilot_output=copilot_output,
        session_id=args.session,
        gateway_url=args.gateway,
        api_key=args.api_key,
        actor_id=args.actor,
        trigger=args.trigger,
    )

    verdict = result.get("verdict", "UNKNOWN")
    blocked = result.get("blocked", False)

    if args.json_only:
        print(json.dumps(result))
    else:
        print("=" * 70)
        print("  A R I F O S   C O P I L O T   G O V E R N A N C E")
        print("=" * 70)
        print(f"  Verdict    : {verdict}")
        print(f"  Blocked    : {blocked}")
        print(f"  Confidence : {result.get('confidence', 0.0):.2f}")
        print(f"  Judge Eng. : {result.get('judge_engine', 'unknown')}")
        print(f"  Session    : {result.get('session_id', 'unknown')}")
        print(f"  Trace      : {result.get('trace_id', 'unknown')}")
        floors = result.get("floors_triggered", [])
        if floors:
            print(f"  Floors     : {', '.join(floors)}")
        print(f"  Audit ID   : {result.get('audit_id', 'none')}")
        print("-" * 70)
        print(f"  Reason     : {result.get('reason', 'no reason')}")
        print("=" * 70)
        print("\n--- VERDICT JSON ---")
        print(json.dumps(result, indent=2))

    if blocked:
        sys.stderr.write(f"\n[FAIL-CLOSED] BLOCKED. Verdict: {verdict}\n")
        sys.stderr.write(f"Reason: {result.get('reason', 'unknown')}\n")
        sys.stderr.write(f"Audit ID: {result.get('audit_id', 'none')}\n")

    # Exit codes: 0=ok, 1=HOLD, 2=VOID, 3=error
    if verdict == "VOID":
        return 2
    elif verdict == "HOLD":
        return 1
    elif verdict in ("PARTIAL", "SEAL"):
        return 0
    else:
        return 3


if __name__ == "__main__":
    sys.exit(main())
