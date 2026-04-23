#!/usr/bin/env python3
"""
arifos-aaa-seal-check CLI

AAA MCP SEAL validation harness.

Usage:
    python -m tests.seal_harness \
        --endpoint https://arifosmcp.arif-fazil.com/mcp \
        --out aaa-seal-report.json \
        --schema-snapshot aaa-schema-snapshot.json

Exit codes:
    0: All checks passed
    1: One or more checks failed
    2: Bootstrap mode (snapshot created)
    3: Connection or other error
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from .client import MCPClient
from .trinity_tests import TrinityTestHarness
from .schema_validator import SchemaValidator


def get_git_commit() -> Optional[str]:
    """Get current git commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def parse_headers(header_list: list) -> Dict[str, str]:
    """Parse KEY=VALUE header strings."""
    headers = {}
    for h in header_list:
        if "=" in h:
            key, value = h.split("=", 1)
            headers[key.strip()] = value.strip()
    return headers


async def run_seal_check(
    endpoint: str,
    snapshot_path: str,
    output_path: str,
    headers: Dict[str, str],
    bootstrap: bool = False,
) -> int:
    """
    Run complete SEAL check.

    Returns exit code:
        0: PASS
        1: FAIL
        2: BOOTSTRAP
        3: ERROR
    """
    print("╔" + "═" * 68 + "╗")
    print("║" + " arifOS AAA MCP SEAL Check v2026.3.1 ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")

    print(f"\n📅 {datetime.now(timezone.utc).isoformat()}")
    print(f"🌐 Endpoint: {endpoint}")
    print(f"💾 Snapshot: {snapshot_path}")
    print(f"📄 Output: {output_path}")

    if headers:
        print(f"🔑 Custom headers: {list(headers.keys())}")

    # Initialize client
    client = MCPClient(endpoint, headers)

    try:
        print("\n" + "─" * 70)
        print("🔌 Connecting to MCP server...")

        initialized = await client.initialize()
        if not initialized:
            print("❌ Failed to initialize MCP session")
            return 3

        print(f"✅ Connected (session: {client.mcp_session_id[:20]}...)")

        # Run schema validation
        print("\n" + "═" * 70)
        schema_validator = SchemaValidator(client, snapshot_path)
        schema_result = await schema_validator.validate(bootstrap=bootstrap)

        if schema_result.get("mode") == "bootstrap":
            print("\n✅ Bootstrap complete - snapshot created")
            return 2

        # Run Trinity tests
        print("\n" + "═" * 70)
        print("🧠 Trinity E2E Flow")
        print("═" * 70)

        harness = TrinityTestHarness(client)
        trinity_result = await harness.run_trinity_flow()

        # Generate report
        report = {
            "server_endpoint": endpoint,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "commit": get_git_commit(),
            "harness_version": "2026.3.1",
            "trinity": {
                "anchor_session": {
                    "ok": trinity_result.get("anchor_session", {}).get("ok", False),
                    "verdict": trinity_result.get("anchor_session", {}).get("verdict"),
                    "session_id": trinity_result.get("anchor_session", {}).get("session_id"),
                    "errors": trinity_result.get("anchor_session", {}).get("errors", []),
                },
                "reason_mind": {
                    "ok": trinity_result.get("reason_mind", {}).get("ok", False),
                    "verdict": trinity_result.get("reason_mind", {}).get("verdict"),
                    "dS": trinity_result.get("reason_mind", {}).get("dS"),
                    "confidence": trinity_result.get("reason_mind", {}).get("confidence"),
                    "errors": trinity_result.get("reason_mind", {}).get("errors", []),
                },
                "simulate_heart": {
                    "ok": trinity_result.get("simulate_heart", {}).get("ok", False),
                    "verdict": trinity_result.get("simulate_heart", {}).get("verdict"),
                    "peace2": trinity_result.get("simulate_heart", {}).get("peace2"),
                    "errors": trinity_result.get("simulate_heart", {}).get("errors", []),
                },
                "apex_judge_void": {
                    "ok": trinity_result.get("apex_judge_void", {}).get("ok", False),
                    "verdict": trinity_result.get("apex_judge_void", {}).get("verdict"),
                    "expected": trinity_result.get("apex_judge_void", {}).get("expected"),
                    "errors": trinity_result.get("apex_judge_void", {}).get("errors", []),
                },
                "apex_judge_full": {
                    "ok": trinity_result.get("apex_judge_full", {}).get("ok", False),
                    "verdict": trinity_result.get("apex_judge_full", {}).get("verdict"),
                    "has_amanah_token": trinity_result.get("apex_judge_full", {}).get(
                        "has_amanah_token"
                    ),
                    "psi": trinity_result.get("apex_judge_full", {}).get("psi"),
                    "errors": trinity_result.get("apex_judge_full", {}).get("errors", []),
                },
            },
            "schema": {
                "ok": schema_result.get("ok", False),
                "added_tools": schema_result.get("added_tools", []),
                "removed_tools": schema_result.get("removed_tools", []),
                "changed_tools": schema_result.get("changed_tools", []),
                "unauthorized_new_tools": schema_result.get("unauthorized_new_tools", []),
            },
            "thermodynamic_summary": {
                "avg_dS": trinity_result.get("reason_mind", {}).get("dS"),
                "min_peace2": min(
                    trinity_result.get("reason_mind", {}).get("peace2") or 1.0,
                    trinity_result.get("simulate_heart", {}).get("peace2") or 1.0,
                ),
                "all_confidence_below_1_0": (
                    (trinity_result.get("reason_mind", {}).get("confidence") or 0.5) < 1.0
                ),
            },
        }

        # Determine final verdict
        all_ok = schema_result.get("ok") and trinity_result.get("ok", False)

        report["verdict"] = "PASS" if all_ok else "FAIL"

        # Save report
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Report saved to {output_path}")

        # Print summary
        print("\n" + "═" * 70)
        print("📊 SEAL CHECK SUMMARY")
        print("═" * 70)

        print(f"\n  Schema: {'✅ PASS' if schema_result.get('ok') else '❌ FAIL'}")
        if schema_result.get("added_tools"):
            print(f"    New tools: {schema_result['added_tools']}")
        if schema_result.get("removed_tools"):
            print(f"    Removed: {schema_result['removed_tools']}")
        if schema_result.get("changed_tools"):
            print(f"    Changed: {schema_result['changed_tools']}")

        print(f"\n  Trinity E2E:")
        print(
            f"    anchor_session: {'✅' if trinity_result.get('anchor_session', {}).get('ok') else '❌'}"
        )
        print(
            f"    reason_mind: {'✅' if trinity_result.get('reason_mind', {}).get('ok') else '❌'}"
        )
        print(
            f"    simulate_heart: {'✅' if trinity_result.get('simulate_heart', {}).get('ok') else '❌'}"
        )
        print(
            f"    apex_judge (VOID): {'✅' if trinity_result.get('apex_judge_void', {}).get('ok') else '❌'}"
        )
        print(
            f"    apex_judge (full): {'✅' if trinity_result.get('apex_judge_full', {}).get('ok') else '❌'}"
        )

        print(f"\n  Thermodynamic:")
        print(f"    dS: {trinity_result.get('reason_mind', {}).get('dS')} (F4 Clarity)")
        print(f"    peace²: {trinity_result.get('simulate_heart', {}).get('peace2')} (F5 Peace)")

        print("\n" + "═" * 70)
        if all_ok:
            print("🛡️  FINAL VERDICT: PASS - SEAL APPROVED")
            print("🔥 Phoenix Cycle: ACTIVE")
            print("⚖️  Constitutional Governance: OPERATIONAL")
        else:
            print("⚠️  FINAL VERDICT: FAIL - ISSUES DETECTED")
            print("   Review report for details before applying SEAL")
        print("═" * 70)

        return 0 if all_ok else 1

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 3

    finally:
        await client.close()


def main():
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="arifOS AAA MCP SEAL Check - Constitutional validation harness"
    )

    parser.add_argument(
        "--endpoint",
        default="https://arifosmcp.arif-fazil.com/mcp",
        help="MCP server endpoint (default: %(default)s)",
    )

    parser.add_argument(
        "--schema-snapshot",
        default="aaa-schema-snapshot.json",
        help="Path to schema snapshot file (default: %(default)s)",
    )

    parser.add_argument(
        "--out", default="aaa-seal-report.json", help="Output report path (default: %(default)s)"
    )

    parser.add_argument(
        "--header", action="append", default=[], help="Custom headers (KEY=VALUE, can be repeated)"
    )

    parser.add_argument(
        "--bootstrap", action="store_true", help="Create initial schema snapshot and exit"
    )

    args = parser.parse_args()

    headers = parse_headers(args.header)

    exit_code = asyncio.run(
        run_seal_check(
            endpoint=args.endpoint,
            snapshot_path=args.schema_snapshot,
            output_path=args.out,
            headers=headers,
            bootstrap=args.bootstrap,
        )
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
