#!/usr/bin/env python3
"""
Autoresearch Loop — arifOS Autoresearch
Bounded exploration using Trinity architecture: ARIF → ADAM → APEX

Economic guards prevent overoptimization:
- MARGINAL_THRESHOLD: stop when ΔS improvement falls below noise floor
- MAX_ITERATIONS: hard cap (saturation point)
- CONVEXITY_CHECK: penalize declining returns
- NPV_GATE: reject if temporal NPV < 0

Usage:
    python autoresearch.py --budget=300
    python autoresearch.py --budget=60 --path=core/shared/utils.py
"""

import json
import subprocess
import sys
import time
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path

ARIFOS_ROOT = Path(__file__).parent.parent
VAULT999 = ARIFOS_ROOT / "VAULT999"

TIME_BUDGET = 300
MARGINAL_THRESHOLD = 0.003
MAX_ITERATIONS = 12
CONVEXITY_PENALTY = 0.5
NOISE_FLOOR = 0.001

sys.path.insert(0, str(Path(__file__).parent))
import metrics


@dataclass
class ExperimentResult:
    timestamp: str
    commit: str
    delta_s: float
    psi: float
    g_dagger: float
    npv: float
    passes: bool
    status: str
    verdict_scope: str
    violations: list
    description: str
    path_used: str
    marginal_gain: float
    elapsed_seconds: float


def get_timestamp():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def run_git_command(args, cwd=None):
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or ARIFOS_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def load_history():
    exp_file = VAULT999 / "experiments.jsonl"
    if not exp_file.exists():
        return []
    results = []
    with open(exp_file) as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    return results


def save_experiment(exp: ExperimentResult):
    VAULT999.mkdir(exist_ok=True)
    exp_file = VAULT999 / "experiments.jsonl"
    with open(exp_file, "a") as f:
        f.write(json.dumps(asdict(exp)) + "\n")


def call_agent(script_name: str, args: list = None, input_data: dict = None) -> dict:
    cmd = [sys.executable, str(Path(__file__).parent / script_name)]
    if args:
        cmd.extend(args)
    try:
        result = subprocess.run(
            cmd,
            input=json.dumps(input_data) if input_data else None,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.stdout:
            return json.loads(result.stdout)
        return {}
    except Exception as e:
        return {"error": str(e)}


def run_arif_analysis(target_path: str = None) -> dict:
    args = ["--mode=analyze"]
    if target_path:
        args.extend(["--path", target_path])
    output_file = Path(tempfile.mktemp(suffix=".json"))
    args.extend(["--output", str(output_file)])
    call_agent("arif_agent.py", args)
    if output_file.exists():
        with open(output_file) as f:
            data = json.load(f)
        output_file.unlink()
        return data
    return {}


def run_adam_analysis(arif_output: dict) -> dict:
    output_file = Path(tempfile.mktemp(suffix=".json"))
    input_file = Path(tempfile.mktemp(suffix=".json"))
    with open(input_file, "w") as f:
        json.dump(arif_output, f)
    call_agent("adam_agent.py", ["--input", str(input_file), "--output", str(output_file)])
    input_file.unlink()
    if output_file.exists():
        with open(output_file) as f:
            data = json.load(f)
        output_file.unlink()
        return data
    return {}


def run_apex_verdict(arif_output: dict, adam_output: dict, elapsed: float) -> dict:
    combined = {**arif_output, **adam_output}
    output_file = Path(tempfile.mktemp(suffix=".json"))
    input_file = Path(tempfile.mktemp(suffix=".json"))
    with open(input_file, "w") as f:
        json.dump(combined, f)
    call_agent(
        "apex_judge.py",
        [
            "--input",
            str(input_file),
            "--output",
            str(output_file),
            "--elapsed",
            str(elapsed),
        ],
    )
    input_file.unlink()
    if output_file.exists():
        with open(output_file) as f:
            data = json.load(f)
        output_file.unlink()
        return data
    return {}


def compute_marginal_gain(history: list, new_delta_s: float) -> float:
    if not history:
        return new_delta_s
    prev = history[-1]["delta_s"]
    return new_delta_s - prev


def check_convexity(history: list) -> float:
    if len(history) < 3:
        return 1.0
    gains = []
    for i in range(1, len(history)):
        gains.append(history[i]["delta_s"] - history[i - 1]["delta_s"])
    if len(gains) < 2:
        return 1.0
    if gains[-1] < gains[-2] * 0.8:
        return CONVEXITY_PENALTY
    return 1.0


def should_continue(
    iteration: int,
    elapsed: float,
    marginal_gain: float,
    convexity: float,
    history: list,
) -> tuple[bool, str]:
    if iteration >= MAX_ITERATIONS:
        return False, f"MAX_ITERATIONS={MAX_ITERATIONS}"
    if elapsed >= TIME_BUDGET:
        return False, f"TIME_BUDGET={TIME_BUDGET}s"
    if len(history) >= 2 and iteration > 3:
        if abs(marginal_gain) < NOISE_FLOOR:
            return (
                False,
                f"SATURATION: marginal={marginal_gain:.4f} < floor={NOISE_FLOOR}",
            )
    if marginal_gain < MARGINAL_THRESHOLD and iteration > 2:
        return False, f"MARGINAL_DMIN: gain={marginal_gain:.4f} < {MARGINAL_THRESHOLD}"
    if convexity < 1.0 and iteration > 3:
        return False, f"CONVEXITY: diminishing returns (penalty={convexity})"
    return True, "continue"


def generate_candidate_paths() -> list:
    return [
        {
            "name": "refactor",
            "description": "Refactor shared utilities",
            "files": ["core/shared/utils.py"],
            "risk": "low",
        },
        {
            "name": "docs",
            "description": "Improve docstrings",
            "files": ["ARCH/DOCS/*.md"],
            "risk": "very_low",
        },
        {
            "name": "tests",
            "description": "Add test coverage",
            "files": ["tests/test_core.py"],
            "risk": "low",
        },
    ]


def run_full_pipeline(path_info: dict, iteration: int, elapsed: float) -> ExperimentResult:
    arif_out = run_arif_analysis()
    adam_out = run_adam_analysis(arif_out)
    apex_out = run_apex_verdict(arif_out, adam_out, elapsed)

    delta_s = arif_out.get("entropy_delta", {}).get("total_delta_s", 0.0)
    psi = apex_out.get("psi", 0.0)
    g_dagger = apex_out.get("g_dagger", 0.0)
    npv = apex_out.get("npv", 0.0)
    passes = apex_out.get("passes", False)
    verdict = apex_out.get("verdict_scope", "UNKNOWN")

    return ExperimentResult(
        timestamp=get_timestamp(),
        commit=run_git_command(["rev-parse", "--short", "HEAD"]),
        delta_s=delta_s,
        psi=psi,
        g_dagger=g_dagger,
        npv=npv,
        passes=passes,
        status="PASS" if passes else "FAIL",
        verdict_scope=verdict,
        violations=apex_out.get("violations", []),
        description=path_info["description"],
        path_used=path_info["name"],
        marginal_gain=0.0,
        elapsed_seconds=elapsed,
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="arifOS Autoresearch")
    parser.add_argument("--budget", type=int, default=300)
    parser.add_argument("--path", help="Specific path to analyze")
    parser.add_argument("--clear", action="store_true", help="Clear history before run")
    args = parser.parse_args()

    global TIME_BUDGET
    TIME_BUDGET = args.budget

    if args.clear:
        exp_file = VAULT999 / "experiments.jsonl"
        if exp_file.exists():
            exp_file.unlink()

    print(f"🚀 Starting autoresearch loop")
    print(f"   Budget: {TIME_BUDGET}s | Max iterations: {MAX_ITERATIONS}")
    print(f"   Marginal: {MARGINAL_THRESHOLD} | Noise floor: {NOISE_FLOOR} | Half-life: 72h")
    print("─" * 60)

    history = load_history()
    start_time = time.time()
    iteration = 0

    while True:
        elapsed = time.time() - start_time
        remaining = TIME_BUDGET - elapsed

        if remaining <= 0:
            print(f"\n⏰ TIME_BUDGET exhausted")
            break

        paths = generate_candidate_paths()
        best = paths[iteration % len(paths)]

        print(
            f"\n🔄 Iteration {iteration + 1} ({elapsed:.1f}s elapsed, {remaining:.1f}s remaining)"
        )
        print(f"   Path: {best['name']}")

        exp = run_full_pipeline(best, iteration, elapsed)
        marginal = compute_marginal_gain(history, exp.delta_s)
        convexity = check_convexity(history)
        exp.marginal_gain = marginal

        print(
            f"   {metrics.format_metrics_summary(exp.delta_s, exp.psi, exp.g_dagger, exp.npv, exp.passes)}"
        )

        continue_ok, reason = should_continue(iteration, elapsed, marginal, convexity, history)

        if exp.passes and continue_ok:
            save_experiment(exp)
            history.append(asdict(exp))
            print(f"   ✅ ACCEPT | {reason}")
        else:
            print(f"   ❌ REJECT | {reason} | violations: {exp.violations}")
            break

        iteration += 1

    total_delta = sum(h["delta_s"] for h in history)
    print(f"\n📊 Final: {len(history)} experiments | Total ΔS={total_delta:+.4f}")
    if history:
        latest = history[-1]
        print(
            f"   Latest: G†={latest['g_dagger']:.3f} | NPV={latest['npv']:+.4f} | {latest['verdict_scope']}"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
