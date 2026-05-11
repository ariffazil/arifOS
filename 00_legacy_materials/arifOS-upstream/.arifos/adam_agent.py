#!/usr/bin/env python3
"""
ADAM Agent (Ω Heart) — arifOS Autoresearch
Stability checks, readability scoring, cooling analysis.

Usage:
    python adam_agent.py --input=/tmp/arif_output.json --output=/tmp/adam_output.json
"""

import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC
from pathlib import Path

ARIFOS_ROOT = Path(__file__).parent.parent
SCOPED_DIRS = ["core/shared", "arifosmcp/runtime", "tests", "ARCH/DOCS"]


@dataclass
class StabilityMetrics:
    readability_score: float
    cooling_rate: float
    stability_index: float
    risk_level: str


@dataclass
class AdamOutput:
    stability: StabilityMetrics
    passes: bool
    warnings: list
    timestamp: str


def get_timestamp():
    from datetime import datetime

    return datetime.now(UTC).isoformat()


def measure_readability(file_path: Path) -> float:
    try:
        with open(file_path) as f:
            content = f.read()
        lines = content.split("\n")
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
        comment_lines = [l for l in lines if l.strip().startswith("#")]
        if not code_lines:
            return 0.0
        comment_ratio = len(comment_lines) / len(code_lines)
        avg_line_len = sum(len(l) for l in code_lines) / len(code_lines)
        len_score = max(0, 1 - (avg_line_len - 80) / 120)
        score = (comment_ratio * 2 + len_score) / 3
        return min(score, 1.0)
    except:
        return 0.5


def calculate_readability_score() -> float:
    scores = []
    for scope_dir in SCOPED_DIRS:
        dir_path = ARIFOS_ROOT / scope_dir
        if dir_path.exists():
            for py_file in dir_path.rglob("*.py"):
                if len(scores) < 50:
                    scores.append(measure_readability(py_file))
    return sum(scores) / len(scores) if scores else 0.5


def estimate_cooling_rate() -> float:
    return 0.15


def compute_stability_index(readability: float, cooling: float) -> float:
    return (readability * 0.7) + (cooling * 0.3)


def run_stability_checks(arif_input: dict = None) -> AdamOutput:
    readability = calculate_readability_score()
    cooling = estimate_cooling_rate()
    stability = compute_stability_index(readability, cooling)

    risk = "low" if stability > 0.6 else "medium" if stability > 0.4 else "high"
    passes = stability > 0.4

    warnings = []
    if readability < 0.4:
        warnings.append("Low readability score detected")
    if cooling < 0.1:
        warnings.append("Cooling rate below threshold")

    return AdamOutput(
        stability=StabilityMetrics(
            readability_score=readability,
            cooling_rate=cooling,
            stability_index=stability,
            risk_level=risk,
        ),
        passes=passes,
        warnings=warnings,
        timestamp=get_timestamp(),
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ADAM Agent — Ω Heart")
    parser.add_argument("--input", help="Input from ARIF agent")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    arif_input = None
    if args.input:
        with open(args.input) as f:
            arif_input = json.load(f)

    output = run_stability_checks(arif_input)
    result = asdict(output)
    result["agent"] = "ADAM"
    result["version"] = "1.0.0"

    json_output = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(json_output)
        print(f"✅ ADAM analysis written to {args.output}")
    else:
        print(json_output)

    return 0 if output.passes else 1


if __name__ == "__main__":
    sys.exit(main())
