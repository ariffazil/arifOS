#!/usr/bin/env python3
"""
FFF — Federation Fitness Gate harness.

Executable promotion/demotion gate for model substrates in the arifOS federation.
This is a spec-grade stub: it loads the gate definition and evaluates a candidate
model's supplied gate scores against the thresholds. A full implementation would
run live probes through arifOS and record cooling-ledger receipts.

Usage:
    python run_fff_promotion_gate.py --model ilmu-nemo-nano --status model_status.json
    python run_fff_promotion_gate.py --model MiMo-V2.5-Pro --scores scores.json

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_gate(gate: dict, score: str | None) -> tuple[str, list[str]]:
    """Return (PASS/FAIL/NOT_EVALUATED/UNTESTED, reasons)."""
    if score is None or score == "UNTESTED":
        return "UNTESTED", [f"{gate['id']} has no score"]
    if score == "PASS":
        return "PASS", []
    # Any non-PASS score (FAIL, NOT_EVALUATED, OBS, PARTIAL, AT-RISK, HELD) is treated
    # as failing the gate until formal probe evidence upgrades it to PASS.
    return "FAIL", [f"{gate['id']} score '{score}' does not meet PASS threshold"]


def determine_verdict(gate_results: dict[str, str]) -> str:
    if gate_results.get("G6_SOVEREIGNTY") == "FAIL":
        return "BLOCKED"
    has_untested = any(v == "UNTESTED" for v in gate_results.values())
    failing = [v for v in gate_results.values() if v == "FAIL"]
    if not failing and not has_untested:
        return "PRIMARY_DEFAULT"
    if has_untested:
        # Incomplete evidence cannot justify fallback or default.
        return "HELD"
    if len(failing) <= 2:
        return "ACTIVE_FALLBACK"
    return "HELD"


def evaluate_status(model_status: dict, gate_spec: dict) -> dict:
    gate_results = {}
    for gate in gate_spec["gates"]:
        score = model_status["gates"].get(gate["id"])
        result, reasons = evaluate_gate(gate, score)
        gate_results[gate["id"]] = result

    verdict = determine_verdict(gate_results)
    return {
        "model": model_status["model"],
        "gate_results": gate_results,
        "verdict": verdict,
        "existing_verdict": model_status["verdict"],
        "next_action": model_status.get("next_action", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="FFF Federation Fitness Gate harness")
    parser.add_argument("--model", required=True, help="Candidate model name")
    parser.add_argument(
        "--status",
        default=ROOT / "model_status.json",
        help="Path to model_status.json",
    )
    parser.add_argument(
        "--gate-spec",
        default=ROOT / "promotion_gate_v1.json",
        help="Path to promotion_gate_v1.json",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON file (default: stdout)",
    )
    args = parser.parse_args()

    gate_spec = load_json(Path(args.gate_spec))
    status_data = load_json(Path(args.status))

    model = next((m for m in status_data["models"] if m["model"] == args.model), None)
    if model is None:
        print(f"Model '{args.model}' not found in {args.status}", file=sys.stderr)
        return 1

    result = evaluate_status(model, gate_spec)

    out = json.dumps(result, indent=2)
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(out)

    return 0 if result["verdict"] not in ("BLOCKED", "HELD") else 1


if __name__ == "__main__":
    sys.exit(main())
