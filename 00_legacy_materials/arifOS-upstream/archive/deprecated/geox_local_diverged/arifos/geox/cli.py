"""
arifos/geox/cli.py — GEOX CLI Entrypoint

A hardened CLI for geological coprocessor intelligence.
Exposes evaluation, memory, and health tools to the command line.
"""

import argparse
import asyncio
import sys

import yaml

from arifos.geox.geox_agent import GeoXAgent, GeoXConfig
from arifos.geox.geox_init import verify_and_exit_if_void
from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest


def main():
    """Main entrypoint for the `geox` CLI command."""

    # Hardened ignition and check
    foundation = verify_and_exit_if_void()

    parser = argparse.ArgumentParser(
        description=f"GEOX — Geological Intelligence Coprocessor v{foundation['version']}"
    )

    subparsers = parser.add_subparsers(dest="command", help="GEOX commands")

    # ── command: evaluate ────────────────────────
    eval_parser = subparsers.add_parser("evaluate", help="Perform geological evaluation")
    eval_parser.add_argument("--query", required=True, help="Geological query")
    eval_parser.add_argument("--lat", type=float, required=True, help="Latitude")
    eval_parser.add_argument("--lon", type=float, required=True, help="Longitude")
    eval_parser.add_argument("--basin", required=True, help="Sedimentary basin name")
    eval_parser.add_argument("--risk", default="low", choices=["low", "medium", "high"], help="Risk level")
    eval_parser.add_argument("--output", default="markdown", choices=["json", "markdown"], help="Output format")

    # ── command: health ──────────────────────────
    subparsers.add_parser("health", help="Check system health")

    # ── command: config ──────────────────────────
    config_parser = subparsers.add_parser("config", help="Manage GEOX configuration")
    config_parser.add_argument("--show", action="store_true", help="Show current config")

    args = parser.parse_args()

    if args.command == "health":
        print(yaml.dump(foundation, sort_keys=False))
        sys.exit(0)

    elif args.command == "evaluate":
        asyncio.run(run_evaluate(args))

    elif args.command == "config":
        if args.show:
                print(yaml.dump(GeoXConfig().model_dump(), sort_keys=False))

    else:
        parser.print_help()

async def run_evaluate(args):
    """Execution wrapper for eval command."""
    config = GeoXConfig(risk_tolerance=args.risk)
    agent = GeoXAgent(config=config)

    request = GeoRequest(
        query=args.query,
        location=CoordinatePoint(latitude=args.lat, longitude=args.lon),
        basin=args.basin,
        risk_tolerance=args.risk,
        requester_id="geox-cli"
    )

    print(f"[*] Initializing GEOX Pipeline for: {args.basin}...")
    response = await agent.evaluate_prospect(request)

    if args.output == "json":
        print(response.model_dump_json(indent=2))
    else:
        print("\n" + "="*80)
        print(f" GEOX VERDICT: {response.verdict}")
        print("="*80)
        for insight in response.insights:
            print(f"- {insight.text} (Risk: {insight.risk_level})")

        print("\n---\n" + response.arifos_telemetry["seal"])

if __name__ == "__main__":
    main()
