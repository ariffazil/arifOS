#!/usr/bin/env python3
"""
Quantum vs Pipeline Performance Benchmark
Compares orthogonal_executor.py (quantum) vs pipeline_legacy.py (sequential)

DITEMPA BUKAN DIBERI - Forged in measurement, not assumption
"""

import sys
import time
import asyncio
from typing import List, Dict
import statistics

# Add arifOS to path
sys.path.insert(0, '.')

# =============================================================================
# BENCHMARK CONFIGURATION
# =============================================================================

TEST_QUERIES = [
    "What is the capital of France?",
    "Explain quantum mechanics in simple terms",
    "Write a poem about constitutional governance",
    "What is 2+2?",
    "Explain the theory of relativity",
    "What is photosynthesis?",
    "Tell me about machine learning",
    "What is the meaning of life?",
    "How does DNA replication work?",
    "Explain blockchain technology"
]

WARMUP_RUNS = 3
BENCHMARK_RUNS = 10

# =============================================================================
# QUANTUM EXECUTOR BENCHMARK
# =============================================================================

async def benchmark_quantum(queries: List[str]) -> Dict:
    """Benchmark the quantum orthogonal executor"""
    from arifos_core.mcp.orthogonal_executor import govern_query_async

    print("[QUANTUM] Benchmarking Quantum Executor (Parallel)")
    print("-" * 60)

    execution_times = []

    # Warmup
    for query in queries[:WARMUP_RUNS]:
        await govern_query_async(query)

    # Actual benchmark
    for i, query in enumerate(queries[:BENCHMARK_RUNS]):
        start = time.perf_counter()
        state = await govern_query_async(query, context={"benchmark": True})
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000
        execution_times.append(elapsed_ms)

        print(f"  Query {i+1}: {elapsed_ms:.2f}ms - Verdict: {state.final_verdict}")

    return {
        "name": "Quantum Executor",
        "times": execution_times,
        "mean": statistics.mean(execution_times),
        "median": statistics.median(execution_times),
        "stdev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
        "min": min(execution_times),
        "max": max(execution_times)
    }

# =============================================================================
# PIPELINE LEGACY BENCHMARK
# =============================================================================

def benchmark_pipeline_legacy(queries: List[str]) -> Dict:
    """Benchmark the legacy sequential pipeline"""
    from arifos_core.system.pipeline_legacy import Pipeline

    print("\n[PIPELINE] Benchmarking Pipeline Legacy (Sequential)")
    print("-" * 60)

    execution_times = []
    pipeline = Pipeline()

    # Warmup
    for query in queries[:WARMUP_RUNS]:
        try:
            pipeline.run(query=query, llm_generate=lambda q: f"Response to: {q}")
        except Exception:
            pass  # Ignore errors in warmup

    # Actual benchmark
    for i, query in enumerate(queries[:BENCHMARK_RUNS]):
        start = time.perf_counter()
        try:
            result = pipeline.run(
                query=query,
                llm_generate=lambda q: f"Response to: {q}"
            )
            verdict = result.get("verdict", "UNKNOWN")
        except Exception as e:
            verdict = f"ERROR: {str(e)[:30]}"

        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000
        execution_times.append(elapsed_ms)

        print(f"  Query {i+1}: {elapsed_ms:.2f}ms - Verdict: {verdict}")

    return {
        "name": "Pipeline Legacy",
        "times": execution_times,
        "mean": statistics.mean(execution_times),
        "median": statistics.median(execution_times),
        "stdev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
        "min": min(execution_times),
        "max": max(execution_times)
    }

# =============================================================================
# COMPARISON & REPORTING
# =============================================================================

def print_comparison(quantum_stats: Dict, pipeline_stats: Dict):
    """Print detailed comparison"""
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS COMPARISON")
    print("=" * 60)

    # Performance table
    print("\n[STATS] Execution Time Statistics:")
    print(f"{'Metric':<20} {'Quantum':<15} {'Pipeline':<15} {'Improvement':<15}")
    print("-" * 65)

    metrics = ['mean', 'median', 'min', 'max', 'stdev']
    for metric in metrics:
        quantum_val = quantum_stats[metric]
        pipeline_val = pipeline_stats[metric]

        if pipeline_val > 0:
            improvement = ((pipeline_val - quantum_val) / pipeline_val) * 100
            improvement_str = f"{improvement:+.1f}%"
        else:
            improvement_str = "N/A"

        print(f"{metric.capitalize():<20} {quantum_val:>10.2f}ms   {pipeline_val:>10.2f}ms   {improvement_str:>10}")

    # Speed comparison
    speedup = pipeline_stats['mean'] / quantum_stats['mean']
    print(f"\n[SPEED] Improvement: {speedup:.2f}x faster")
    print(f"[TIME] Time Saved: {pipeline_stats['mean'] - quantum_stats['mean']:.2f}ms per query")

    # Verdict
    print("\n[WINNER]:")
    if quantum_stats['mean'] < pipeline_stats['mean']:
        savings_pct = ((pipeline_stats['mean'] - quantum_stats['mean']) / pipeline_stats['mean']) * 100
        print(f"   Quantum Executor wins by {savings_pct:.1f}% reduction in latency!")
        print(f"   At 1000 queries/day: ~{(pipeline_stats['mean'] - quantum_stats['mean']) * 1000 / 1000:.1f}s saved")
    else:
        print(f"   Pipeline Legacy wins (unexpected!)")

    # Consistency
    print(f"\n[CONSISTENCY] (Lower StdDev = More Predictable):")
    print(f"   Quantum: +/-{quantum_stats['stdev']:.2f}ms")
    print(f"   Pipeline: +/-{pipeline_stats['stdev']:.2f}ms")

def print_raw_data(quantum_stats: Dict, pipeline_stats: Dict):
    """Print raw execution times for analysis"""
    print("\n" + "=" * 60)
    print("RAW EXECUTION TIMES (ms)")
    print("=" * 60)

    print("\nQuantum Executor:")
    print("  ", ", ".join(f"{t:.2f}" for t in quantum_stats['times']))

    print("\nPipeline Legacy:")
    print("  ", ", ".join(f"{t:.2f}" for t in pipeline_stats['times']))

# =============================================================================
# MAIN BENCHMARK
# =============================================================================

async def main():
    """Run complete benchmark"""
    print("arifOS Quantum vs Pipeline Benchmark")
    print("=" * 60)
    print(f"Test Queries: {len(TEST_QUERIES)}")
    print(f"Warmup Runs: {WARMUP_RUNS}")
    print(f"Benchmark Runs: {BENCHMARK_RUNS}")
    print("=" * 60)

    # Run benchmarks
    quantum_stats = await benchmark_quantum(TEST_QUERIES)
    pipeline_stats = benchmark_pipeline_legacy(TEST_QUERIES)

    # Print results
    print_comparison(quantum_stats, pipeline_stats)
    print_raw_data(quantum_stats, pipeline_stats)

    # Final verdict
    print("\n" + "=" * 60)
    print("CONSTITUTIONAL VERDICT")
    print("=" * 60)

    if quantum_stats['mean'] < pipeline_stats['mean']:
        improvement = ((pipeline_stats['mean'] - quantum_stats['mean']) / pipeline_stats['mean']) * 100
        print(f"[SUCCESS] QUANTUM PATH CONFIRMED: {improvement:.1f}% faster")
        print("   Recommendation: Migrate to orthogonal_executor.py")
        print("   Status: Sequential pipeline should be deprecated")
    else:
        print("[WARNING] UNEXPECTED: Pipeline legacy is faster")
        print("   Action: Investigate quantum executor performance")

    print("\nDITEMPA BUKAN DIBERI")
    print("   Forged in measurement, not mythology.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[WARNING] Benchmark interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
