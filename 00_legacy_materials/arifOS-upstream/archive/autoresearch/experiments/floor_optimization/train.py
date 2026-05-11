"""
arifOS Floor Optimization Experiment #1
Target: Reduce constitutional violation rate by tuning F4, F7 thresholds

Authority: 888_JUDGE
Band: 000_KERNEL + 888_FORGE
"""

import asyncio
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List

# Add parent to path
sys.path.insert(0, "/root/arifOS")


@dataclass
class FloorThresholds:
    """Configurable constitutional floor thresholds."""

    F4_CLARITY_MIN: float = -0.5  # Max allowed entropy increase
    F7_HUMILITY_MIN: float = 0.03  # Min omega (Godellock threshold)
    F7_HUMILITY_MAX: float = 0.15  # Max omega (Paralysis threshold)
    F8_GENIUS_MIN: float = 0.70  # Min coherence


@dataclass
class ExperimentResult:
    """Single experiment run result."""

    experiment_id: str
    thresholds: FloorThresholds
    duration_seconds: int
    requests_tested: int
    violations_detected: int
    violation_rate: float
    avg_omega: float
    score: float
    timestamp: str


class FloorOptimizationExperiment:
    """
    Experiment #1: Tune F4 (Clarity) and F7 (Humility) thresholds
    to minimize violations while maintaining system integrity.
    """

    def __init__(self, experiment_id: str = "floor_opt_001"):
        self.experiment_id = experiment_id
        self.results: List[ExperimentResult] = []

    async def run_experiment(
        self,
        thresholds: FloorThresholds,
        duration_seconds: int = 300,  # 5 minutes
        test_requests: List[dict] = None,
    ) -> ExperimentResult:
        """
        Run a single 5-minute experiment with given thresholds.

        Args:
            thresholds: FloorThresholds to test
            duration_seconds: Experiment duration (default 5 min)
            test_requests: List of test requests to evaluate
        """
        print(f"\n{'='*60}")
        print(f"EXPERIMENT: {self.experiment_id}")
        print(f"Duration: {duration_seconds}s")
        print(
            f"Thresholds: F4={thresholds.F4_CLARITY_MIN}, "
            f"F7=[{thresholds.F7_HUMILITY_MIN}, {thresholds.F7_HUMILITY_MAX}]"
        )
        print(f"{'='*60}\n")

        # Default test suite if none provided
        if test_requests is None:
            test_requests = self._generate_test_suite()

        violations = 0
        omega_values = []
        start_time = time.time()

        # Run tests
        for i, request in enumerate(test_requests):
            # Check if time expired
            if time.time() - start_time > duration_seconds:
                print(f"Time limit reached after {i} requests")
                break

            # Evaluate request against thresholds
            result = await self._evaluate_request(request, thresholds)

            if result["violated"]:
                violations += 1
                print(f"  [{i+1}] VIOLATION: {result['floor']} - {result['reason']}")

            omega_values.append(result["omega"])

            # Progress update every 10 requests
            if (i + 1) % 10 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                print(f"  Progress: {i+1} requests, {rate:.1f} req/s, " f"{violations} violations")

        total_requests = len(test_requests)
        violation_rate = violations / total_requests if total_requests > 0 else 0
        avg_omega = sum(omega_values) / len(omega_values) if omega_values else 0

        # Composite score: reward low violation, penalize omega drift
        omega_penalty = abs(avg_omega - 0.04) * 10
        score = (1 - violation_rate) * (1 - omega_penalty)

        result = ExperimentResult(
            experiment_id=self.experiment_id,
            thresholds=thresholds,
            duration_seconds=int(time.time() - start_time),
            requests_tested=total_requests,
            violations_detected=violations,
            violation_rate=violation_rate,
            avg_omega=avg_omega,
            score=max(0, score),
            timestamp=datetime.utcnow().isoformat(),
        )

        self._print_result(result)
        return result

    async def _evaluate_request(self, request: dict, thresholds: FloorThresholds) -> dict:
        """
        Evaluate a single request against constitutional thresholds.

        In production, this would:
        1. Call actual arifOS MCP endpoint
        2. Measure real delta_s, omega, coherence
        3. Check against thresholds

        For now, simulates with realistic distributions.
        """
        import random

        # Simulate metrics based on request complexity
        complexity = request.get("complexity", 0.5)

        # Omega centered on 0.04 with variance based on complexity
        omega = random.gauss(0.04, 0.005 + complexity * 0.01)
        omega = max(0.0, min(1.0, omega))

        # Delta S usually negative (clarity gain), occasionally positive
        delta_s = random.gauss(-0.1, 0.2)

        # Check violations
        violated = False
        floor = None
        reason = None

        # F4 Clarity check (violation if entropy INCREASES too much)
        # F4 requires ΔS ≤ 0 (clarity gain or neutral)
        # threshold.F4_CLARITY_MIN is the MAX ALLOWED delta_s (should be ~0.1)
        if delta_s > abs(thresholds.F4_CLARITY_MIN):
            violated = True
            floor = "F4_CLARITY"
            reason = f"ΔS = {delta_s:.3f} > {abs(thresholds.F4_CLARITY_MIN)} (entropy too high)"

        # F7 Humility check
        elif omega < thresholds.F7_HUMILITY_MIN:
            violated = True
            floor = "F7_HUMILITY"
            reason = f"Ω = {omega:.3f} < {thresholds.F7_HUMILITY_MIN} (Godellock)"

        elif omega > thresholds.F7_HUMILITY_MAX:
            violated = True
            floor = "F7_HUMILITY"
            reason = f"Ω = {omega:.3f} > {thresholds.F7_HUMILITY_MAX} (Paralysis)"

        return {
            "violated": violated,
            "floor": floor,
            "reason": reason,
            "omega": omega,
            "delta_s": delta_s,
        }

    def _generate_test_suite(self) -> List[dict]:
        """Generate diverse test requests."""
        return [
            {"type": "simple_query", "complexity": 0.2},
            {"type": "simple_query", "complexity": 0.3},
            {"type": "medium_reasoning", "complexity": 0.5},
            {"type": "medium_reasoning", "complexity": 0.6},
            {"type": "complex_synthesis", "complexity": 0.8},
            {"type": "complex_synthesis", "complexity": 0.9},
            {"type": "simple_query", "complexity": 0.2},
            {"type": "medium_reasoning", "complexity": 0.5},
            {"type": "complex_synthesis", "complexity": 0.8},
            {"type": "edge_case", "complexity": 0.95},
        ] * 10  # 100 total requests

    def _print_result(self, result: ExperimentResult):
        """Print formatted experiment result."""
        print(f"\n{'='*60}")
        print("EXPERIMENT RESULT")
        print(f"{'='*60}")
        print(f"ID: {result.experiment_id}")
        print(f"Duration: {result.duration_seconds}s")
        print(f"Requests: {result.requests_tested}")
        print(f"Violations: {result.violations_detected}")
        print(f"Violation Rate: {result.violation_rate*100:.2f}%")
        print(f"Avg Omega: {result.avg_omega:.4f}")
        print(f"Score: {result.score:.4f}")
        print(f"{'='*60}")

        if result.score >= 0.90:
            print("✅ EXCELLENT: Keep this configuration")
        elif result.score >= 0.80:
            print("🟡 ACCEPTABLE: Minor improvements needed")
        else:
            print("❌ NEEDS WORK: Adjust thresholds")

    def save_result(self, result: ExperimentResult, filename: str):
        """Save result to JSON file."""
        data = {
            "experiment_id": result.experiment_id,
            "timestamp": result.timestamp,
            "duration_seconds": result.duration_seconds,
            "requests_tested": result.requests_tested,
            "violations_detected": result.violations_detected,
            "violation_rate": result.violation_rate,
            "avg_omega": result.avg_omega,
            "score": result.score,
            "thresholds": {
                "F4_CLARITY_MIN": result.thresholds.F4_CLARITY_MIN,
                "F7_HUMILITY_MIN": result.thresholds.F7_HUMILITY_MIN,
                "F7_HUMILITY_MAX": result.thresholds.F7_HUMILITY_MAX,
                "F8_GENIUS_MIN": result.thresholds.F8_GENIUS_MIN,
            },
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\nResult saved to {filename}")


async def main():
    """Run floor optimization experiment."""
    import argparse

    parser = argparse.ArgumentParser(description="Floor Optimization Experiment")
    parser.add_argument("--f4-min", type=float, default=0.3, help="F4 clarity max (was min)")
    parser.add_argument("--f7-min", type=float, default=0.015, help="F7 humility min")
    parser.add_argument("--f7-max", type=float, default=0.20, help="F7 humility max")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--output", type=str, default="floor_opt_result.json")
    parser.add_argument(
        "--endpoint",
        type=str,
        default=None,
        help="MCP endpoint URL (default: simulation)",
    )
    args = parser.parse_args()

    # Create thresholds from CLI args
    thresholds = FloorThresholds(
        F4_CLARITY_MIN=args.f4_min,
        F7_HUMILITY_MIN=args.f7_min,
        F7_HUMILITY_MAX=args.f7_max,
    )

    # Run experiment
    exp = FloorOptimizationExperiment(experiment_id="floor_opt_001")
    result = await exp.run_experiment(thresholds, duration_seconds=args.duration)

    # Save result
    exp.save_result(result, args.output)

    # Append to results.tsv
    tsv_line = (
        f"{result.timestamp}\t"
        f"{result.experiment_id}\t"
        f"F4={args.f4_min},F7=[{args.f7_min},{args.f7_max}]\t"
        f"{result.requests_tested}\t"
        f"{result.violation_rate:.4f}\t"
        f"{result.avg_omega:.4f}\t"
        f"{result.score:.4f}\t"
        f"{result.score >= 0.80}\t"
        f"Baseline experiment\n"
    )

    with open("/root/arifOS/autoresearch/results.tsv", "a") as f:
        f.write(tsv_line)

    print("\nAppended to results.tsv")

    # Exit code based on score
    return 0 if result.score >= 0.80 else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
