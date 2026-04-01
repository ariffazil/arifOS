"""
arifOS Autoresearch — prepare.py
===============================
FIXED EVALUATION HARNESS. DO NOT MODIFY.

This file is the ground truth for constitutional evaluation.
Agents may NOT edit this file.

Purpose:
- Load experiment configuration
- Run benchmark against live MCP
- Return scored metrics
- Log results to results.tsv

The ONLY thing train.py can affect is the CONFIG it reads.
prepare.py is invariant across all experiments.

Usage:
    python prepare.py --config config/exp_001.json
"""

import argparse
import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add metrics to path
sys.path.insert(0, str(Path(__file__).parent / "metrics"))

from benchmark import arifOSBenchmark, AggregateMetrics


# =============================================================================
# CONSTITUTIONAL CONSTANTS — INVARIANT
# =============================================================================

OMEGA_RANGE = (0.03, 0.05)  # GOLDILOCKS zone
W3_THRESHOLD = 0.95
TARGET_THROUGHPUT = 100.0  # req/s
TARGET_VIOLATION_RATE = 0.05  # 5%
TARGET_SCORE = 0.90

ABORT_VIOLATION_RATE = 0.15  # 15% — abort if exceeded
ABORT_OMEGA_DRIFT = 0.02    # Ω outside [0.02, 0.06] for >10% of requests

RESULTS_TSV = Path(__file__).parent / "results.tsv"
OBSERVATIONS_MD = Path(__file__).parent / "observations.md"


@dataclass
class ExperimentResult:
    """Result of a single experiment run."""
    experiment_id: str
    timestamp: str
    duration_seconds: int
    change_description: str
    throughput: float
    violation_rate: float
    avg_omega: float
    omega_in_range_pct: float
    avg_W_cube: float
    composite_score: float
    kept: bool
    notes: str


# =============================================================================
# EVALUATION ENGINE — FIXED
# =============================================================================

class ConstitutionalEvaluator:
    """
    Fixed evaluation engine.
    Runs benchmark and determines if experiment improved or degraded.
    """
    
    def __init__(self, mcp_endpoint: str = "https://arifosmcp.arif-fazil.com/mcp"):
        self.mcp_endpoint = mcp_endpoint
        self.benchmark = arifOSBenchmark(
            target_url=mcp_endpoint,
            omega_range=OMEGA_RANGE,
            w3_threshold=W3_THRESHOLD
        )
    
    async def evaluate(
        self,
        experiment_id: str,
        change_description: str,
        duration_seconds: int = 300,
        concurrency: int = 10
    ) -> ExperimentResult:
        """
        Run evaluation for a single experiment.
        
        Args:
            experiment_id: Unique identifier for this experiment
            change_description: What was changed (from train.py)
            duration_seconds: How long to run (default 5 min = 300s)
            concurrency: Concurrent workers
            
        Returns:
            ExperimentResult with scored metrics
        """
        print(f"\n{'='*60}")
        print(f"EXPERIMENT: {experiment_id}")
        print(f"Change: {change_description}")
        print(f"Duration: {duration_seconds}s | Concurrency: {concurrency}")
        print(f"{'='*60}")
        
        # Run benchmark
        start_time = time.time()
        
        try:
            metrics = await self.benchmark.run_benchmark(
                duration_seconds=duration_seconds,
                concurrency=concurrency
            )
        except Exception as e:
            print(f"\n❌ BENCHMARK FAILED: {e}")
            return self._error_result(experiment_id, change_description, str(e))
        
        elapsed = time.time() - start_time
        
        # Print results
        self._print_metrics(metrics)
        
        # Determine if experiment should be kept
        score_delta = metrics.composite_score - self._load_baseline()
        kept = metrics.composite_score >= TARGET_SCORE and metrics.violation_rate < ABORT_VIOLATION_RATE
        
        # Check abort conditions
        abort_reason = self._check_abort(metrics)
        if abort_reason:
            kept = False
            print(f"\n🚨 ABORT: {abort_reason}")
        
        # Build result
        result = ExperimentResult(
            experiment_id=experiment_id,
            timestamp=datetime.utcnow().isoformat(),
            duration_seconds=int(elapsed),
            change_description=change_description,
            throughput=metrics.throughput_rps,
            violation_rate=metrics.violation_rate,
            avg_omega=metrics.avg_omega,
            omega_in_range_pct=metrics.omega_in_range_pct,
            avg_W_cube=metrics.avg_W_cube,
            composite_score=metrics.composite_score,
            kept=kept,
            notes=abort_reason or ("improved" if score_delta > 0 else "degraded")
        )
        
        # Log to results.tsv
        self._append_results(result)
        
        # Update observations
        self._update_observations(experiment_id, change_description, metrics, kept)
        
        print(f"\n{'='*60}")
        print(f"RESULT: {'✅ KEPT' if kept else '❌ DISCARDED'}")
        print(f"Baseline: {self._load_baseline():.4f} → Current: {metrics.composite_score:.4f} (Δ={score_delta:+.4f})")
        print(f"{'='*60}\n")
        
        return result
    
    def _load_baseline(self) -> float:
        """Load baseline score from results.tsv (first entry = baseline)."""
        if not RESULTS_TSV.exists():
            return 0.72  # Default baseline
        
        with open(RESULTS_TSV) as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            return 0.72
        
        # Second line is baseline (first data row after header)
        parts = lines[1].strip().split("\t")
        if len(parts) >= 10:
            try:
                return float(parts[9])  # composite_score column
            except (ValueError, IndexError):
                return 0.72
        
        return 0.72
    
    def _check_abort(self, metrics: AggregateMetrics) -> Optional[str]:
        """Check if abort conditions are met."""
        if metrics.violation_rate > ABORT_VIOLATION_RATE:
            return f"Violation rate {metrics.violation_rate*100:.1f}% > {ABORT_VIOLATION_RATE*100:.1f}% threshold"
        
        if metrics.omega_in_range_pct < 0.90:
            return f"Omega in-range {metrics.omega_in_range_pct*100:.1f}% < 90%"
        
        return None
    
    def _print_metrics(self, metrics: AggregateMetrics):
        """Pretty print metrics."""
        print(f"\nPerformance:")
        print(f"  Throughput: {metrics.throughput_rps:.2f} req/s (target: {TARGET_THROUGHPUT})")
        print(f"  Latency (avg): {metrics.avg_latency_ms:.1f}ms")
        print(f"  Latency (p95): {metrics.p95_latency_ms:.1f}ms")
        print(f"  Latency (p99): {metrics.p99_latency_ms:.1f}ms")
        print(f"\nConstitutional:")
        print(f"  Violation Rate: {metrics.violation_rate*100:.2f}% (target: <{TARGET_VIOLATION_RATE*100}%)")
        print(f"  Avg Omega: {metrics.avg_omega:.4f} (range: {OMEGA_RANGE})")
        print(f"  Omega in Range: {metrics.omega_in_range_pct*100:.1f}%")
        print(f"  Avg W³: {metrics.avg_W_cube:.4f} (threshold: {W3_THRESHOLD})")
        if metrics.floor_violation_counts:
            print(f"  Floor Violations: {metrics.floor_violation_counts}")
        print(f"\nComposite Score: {metrics.composite_score:.4f} (target: >{TARGET_SCORE})")
    
    def _append_results(self, result: ExperimentResult):
        """Append result to results.tsv."""
        header = "timestamp\texperiment_id\tchange_description\tthroughput\tviolation_rate\tavg_omega\tomega_in_range_pct\tavg_W_cube\tcomposite_score\tkept\tnotes"
        
        line = "\t".join([
            result.timestamp,
            result.experiment_id,
            result.change_description,
            f"{result.throughput:.2f}",
            f"{result.violation_rate:.4f}",
            f"{result.avg_omega:.4f}",
            f"{result.omega_in_range_pct:.4f}",
            f"{result.avg_W_cube:.4f}",
            f"{result.composite_score:.4f}",
            str(result.kept).lower(),
            result.notes
        ])
        
        if not RESULTS_TSV.exists():
            RESULTS_TSV.write_text(header + "\n")
        
        with open(RESULTS_TSV, "a") as f:
            f.write(line + "\n")
        
        print(f"📊 Logged to {RESULTS_TSV}")
    
    def _update_observations(
        self,
        experiment_id: str,
        change_description: str,
        metrics: AggregateMetrics,
        kept: bool
    ):
        """Update observations.md with learnings."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        
        entry = f"""
## {experiment_id} ({timestamp})

**Change:** {change_description}

**Result:** {'✅ KEPT' if kept else '❌ DISCARDED'}

| Metric | Value | Target |
|--------|-------|--------|
| Throughput | {metrics.throughput_rps:.2f} req/s | >{TARGET_THROUGHPUT} |
| Violation Rate | {metrics.violation_rate*100:.2f}% | <{TARGET_VIOLATION_RATE*100}% |
| Avg Omega | {metrics.avg_omega:.4f} | {OMEGA_RANGE} |
| Omega In Range | {metrics.omega_in_range_pct*100:.1f}% | >90% |
| W³ | {metrics.avg_W_cube:.4f} | >{W3_THRESHOLD} |
| **Score** | **{metrics.composite_score:.4f}** | >{TARGET_SCORE} |

"""
        
        if OBSERVATIONS_MD.exists():
            content = OBSERVATIONS_MD.read_text()
            # Insert after header
            if "## " in content:
                parts = content.split("## ", 1)
                content = parts[0] + "## " + parts[1]
                OBSERVATIONS_MD.write_text(content)
            else:
                OBSERVATIONS_MD.write_text(entry + content)
        else:
            OBSERVATIONS_MD.write_text(f"# Observations Log\n\n{entry}")
    
    def _error_result(
        self,
        experiment_id: str,
        change_description: str,
        error: str
    ) -> ExperimentResult:
        """Create error result."""
        return ExperimentResult(
            experiment_id=experiment_id,
            timestamp=datetime.utcnow().isoformat(),
            duration_seconds=0,
            change_description=change_description,
            throughput=0,
            violation_rate=1.0,
            avg_omega=0.0,
            omega_in_range_pct=0.0,
            avg_W_cube=0.0,
            composite_score=0.0,
            kept=False,
            notes=f"ERROR: {error}"
        )


# =============================================================================
# MAIN — CLI entry point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="arifOS Autoresearch Evaluation Harness (FIXED — DO NOT MODIFY)"
    )
    parser.add_argument(
        "--experiment-id",
        required=True,
        help="Unique experiment identifier (e.g., exp_001)"
    )
    parser.add_argument(
        "--change",
        required=True,
        help="Description of what was changed"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Benchmark duration in seconds (default: 300 = 5 min)"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Concurrent workers (default: 10)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to experiment config (for record only)"
    )
    
    args = parser.parse_args()
    
    evaluator = ConstitutionalEvaluator()
    result = asyncio.run(evaluator.evaluate(
        experiment_id=args.experiment_id,
        change_description=args.change,
        duration_seconds=args.duration,
        concurrency=args.concurrency
    ))
    
    # Exit code
    if result.kept:
        print("✅ Experiment kept — score meets threshold")
        return 0
    else:
        print("❌ Experiment discarded — score below threshold or aborted")
        return 1


if __name__ == "__main__":
    exit(main())
