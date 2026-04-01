#!/usr/bin/env python3
"""
APEX Judge (Ψ Soul) — arifOS Autoresearch
Final verdict using G† formula and constitutional floors.

G† = (A × P × X × E²) × |ΔS|
- A = Accuracy
- P = Penetration
- X = Coherence
- E = Stability
- ΔS = Entropy change

NPV gate: if temporal NPV < 0 → VOID regardless of G†

Usage:
    python apex_judge.py --input=/tmp/adam_output.json --output=/tmp/apex_output.json
"""

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

ARIFOS_ROOT = Path(__file__).parent.parent

import metrics


@dataclass
class ApexVerdict:
    g_dagger: float
    npv: float
    passes: bool
    verdict_scope: str
    violations: list
    timestamp: str


def get_timestamp():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def estimate_accuracy() -> float:
    return 0.85


def estimate_penetration() -> float:
    return 0.70


def estimate_coherence(arif_data: dict = None, adam_data: dict = None) -> float:
    if adam_data and adam_data.get("stability"):
        return adam_data["stability"].get("stability_index", 0.5)
    return 0.65


def estimate_stability(adam_data: dict = None) -> float:
    if adam_data and adam_data.get("stability"):
        return adam_data["stability"].get("stability_index", 0.5)
    return 0.50


def run_verdict(
    arif_data: dict = None,
    adam_data: dict = None,
    elapsed_seconds: float = 0.0,
) -> ApexVerdict:
    delta_s = 0.0
    if arif_data and arif_data.get("entropy_delta"):
        delta_s = arif_data["entropy_delta"].get("total_delta_s", 0.0)

    accuracy = estimate_accuracy()
    penetration = estimate_penetration()
    coherence = estimate_coherence(arif_data, adam_data)
    stability = estimate_stability(adam_data)

    g_dagger = metrics.compute_apex_g(
        accuracy, penetration, coherence, stability, delta_s
    )
    npv = metrics.compute_temporal_npv(delta_s, elapsed_seconds)

    stability_pass = adam_data.get("passes", False) if adam_data else True
    passes, violations = metrics.check_constitutional_floors(
        g_dagger, npv, stability_pass
    )

    verdict_scope = "DOMAIN_SEAL" if passes else "DOMAIN_VOID"

    return ApexVerdict(
        g_dagger=g_dagger,
        npv=npv,
        passes=passes,
        verdict_scope=verdict_scope,
        violations=violations,
        timestamp=get_timestamp(),
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="APEX Judge — Ψ Soul")
    parser.add_argument("--input", help="Input from ADAM agent (or combined)")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--elapsed", type=float, default=0.0, help="Elapsed seconds")
    args = parser.parse_args()

    arif_data = None
    adam_data = None

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
            if "entropy_delta" in data:
                arif_data = data
            elif "stability" in data:
                adam_data = data

    output = run_verdict(arif_data, adam_data, args.elapsed)

    summary = metrics.format_metrics_summary(
        arif_data.get("entropy_delta", {}).get("total_delta_s", 0.0)
        if arif_data
        else 0.0,
        0.0,
        output.g_dagger,
        output.npv,
        output.passes,
    )

    result = asdict(output)
    result["agent"] = "APEX"
    result["version"] = "1.0.0"
    result["summary"] = summary

    json_output = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(json_output)
        print(f"✅ APEX verdict written to {args.output}")
    else:
        print(json_output)

    return 0 if output.passes else 1


if __name__ == "__main__":
    sys.exit(main())
