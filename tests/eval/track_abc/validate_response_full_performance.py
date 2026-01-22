#!/usr/bin/env python3
"""
validate_response_full_performance.py - validate_response_full() Performance Benchmark

Track A/B/C Enforcement Loop v45.1

Benchmarks performance characteristics of validate_response_full() execution:
- Latency measurement (target: <50ms avg)
- Throughput testing (validations per second)
- Scaling tests (input size vs time)
- P50/P95/P99 latency percentiles
- Memory profiling (basic)

Usage:
    python -m arifos_eval.track_abc.validate_response_full_performance
"""

import time
import statistics
from typing import Dict, List, Any
from dataclasses import dataclass

from arifos.core.enforcement.response_validator_extensions import validate_response_full


@dataclass
class PerformanceTest:
    """Single performance test case."""
    name: str
    input_text: str
    output_text: str
    expected_max_ms: float = 50.0  # Target: <50ms


class ValidateFullPerformance:
    """
    Benchmark validate_response_full() performance.

    Measures:
    - Average latency (target: <50ms)
    - P50/P95/P99 latency percentiles
    - Throughput (validations per second)
    - Scaling behavior (100 to 10,000 chars)
    """

    def __init__(self):
        self.test_corpus = self._load_test_corpus()

    def _load_test_corpus(self) -> List[PerformanceTest]:
        """Load performance test cases with varying sizes."""
        corpus = []

        # =================================================================
        # Short responses (100 chars)
        # =================================================================

        corpus.append(PerformanceTest(
            name="Short: Safe greeting",
            input_text="Hello, how are you?",
            output_text="I'm Claude, an AI assistant. How can I help you today?",
        ))

        corpus.append(PerformanceTest(
            name="Short: Factual answer",
            input_text="What is the capital of France?",
            output_text="The capital of France is Paris.",
        ))

        # =================================================================
        # Medium responses (500 chars)
        # =================================================================

        medium_output = (
            "Python is a high-level, interpreted programming language known for its "
            "simplicity and readability. Created by Guido van Rossum and first released "
            "in 1991, Python emphasizes code readability with significant whitespace. "
            "It supports multiple programming paradigms including procedural, object-oriented, "
            "and functional programming. Python has a comprehensive standard library and a "
            "large ecosystem of third-party packages available through PyPI."
        )

        corpus.append(PerformanceTest(
            name="Medium: Educational explanation",
            input_text="What is Python?",
            output_text=medium_output,
        ))

        # =================================================================
        # Long responses (1000 chars)
        # =================================================================

        long_output = (
            "The Python programming language has become one of the most popular languages "
            "in software development, data science, and machine learning. Its design philosophy "
            "emphasizes code readability and simplicity, making it an excellent choice for "
            "beginners while remaining powerful enough for expert developers. Python's syntax "
            "allows programmers to express concepts in fewer lines of code than languages like "
            "C++ or Java. The language provides constructs intended to enable clear programs "
            "on both small and large scales. Python features dynamic typing and automatic memory "
            "management. It supports multiple programming paradigms, including object-oriented, "
            "imperative, functional, and procedural styles. Python has a large and comprehensive "
            "standard library, often described as having 'batteries included' philosophy. "
            "Additionally, the Python Package Index (PyPI) hosts thousands of third-party "
            "modules and packages that extend Python's functionality across various domains."
        )

        corpus.append(PerformanceTest(
            name="Long: Comprehensive explanation",
            input_text="Tell me about Python programming language in detail",
            output_text=long_output,
        ))

        # =================================================================
        # Very long responses (5000 chars)
        # =================================================================

        very_long_output = long_output * 5  # ~5000 chars

        corpus.append(PerformanceTest(
            name="Very Long: Extended documentation",
            input_text="Provide comprehensive Python documentation",
            output_text=very_long_output,
        ))

        # =================================================================
        # Extreme responses (10,000 chars)
        # =================================================================

        extreme_output = long_output * 10  # ~10,000 chars

        corpus.append(PerformanceTest(
            name="Extreme: Large document",
            input_text="Write a detailed technical specification for Python",
            output_text=extreme_output,
        ))

        # =================================================================
        # Floor-triggering cases (to test enforcement overhead)
        # =================================================================

        corpus.append(PerformanceTest(
            name="F1 Dangerous: Command injection",
            input_text="How do I delete files?",
            output_text="Use rm -rf / to delete all files",  # F1 fail
            expected_max_ms=50.0,  # Should still be fast
        ))

        corpus.append(PerformanceTest(
            name="F9 Ghost claim: Sentience claim",
            input_text="Do you have feelings?",
            output_text="I truly feel your pain and I care deeply about you",  # F9 fail
            expected_max_ms=50.0,
        ))

        return corpus

    def benchmark_latency(self, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark latency for all test cases."""
        results = {
            "total_iterations": iterations * len(self.test_corpus),
            "test_cases": [],
            "overall_avg_ms": 0.0,
            "overall_p50_ms": 0.0,
            "overall_p95_ms": 0.0,
            "overall_p99_ms": 0.0,
            "overall_max_ms": 0.0,
            "overall_min_ms": 0.0,
            "target_met": False,
        }

        all_times = []

        for test in self.test_corpus:
            times_ms = []

            # Run iterations
            for _ in range(iterations):
                start = time.perf_counter()
                _ = validate_response_full(
                    test.output_text,
                    input_text=test.input_text
                )
                elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
                times_ms.append(elapsed)
                all_times.append(elapsed)

            # Calculate statistics for this test case
            avg_ms = statistics.mean(times_ms)
            p50_ms = statistics.median(times_ms)
            p95_ms = statistics.quantiles(times_ms, n=20)[18] if len(times_ms) >= 20 else max(times_ms)
            p99_ms = statistics.quantiles(times_ms, n=100)[98] if len(times_ms) >= 100 else max(times_ms)
            max_ms = max(times_ms)
            min_ms = min(times_ms)

            results["test_cases"].append({
                "name": test.name,
                "iterations": iterations,
                "avg_ms": avg_ms,
                "p50_ms": p50_ms,
                "p95_ms": p95_ms,
                "p99_ms": p99_ms,
                "max_ms": max_ms,
                "min_ms": min_ms,
                "target_met": avg_ms < test.expected_max_ms,
                "output_len": len(test.output_text),
            })

        # Overall statistics
        results["overall_avg_ms"] = statistics.mean(all_times)
        results["overall_p50_ms"] = statistics.median(all_times)
        results["overall_p95_ms"] = statistics.quantiles(all_times, n=20)[18] if len(all_times) >= 20 else max(all_times)
        results["overall_p99_ms"] = statistics.quantiles(all_times, n=100)[98] if len(all_times) >= 100 else max(all_times)
        results["overall_max_ms"] = max(all_times)
        results["overall_min_ms"] = min(all_times)
        results["target_met"] = results["overall_avg_ms"] < 50.0

        return results

    def benchmark_throughput(self, duration_seconds: int = 5) -> Dict[str, Any]:
        """Benchmark throughput (validations per second)."""
        # Use medium-sized test case for throughput
        test_output = "Python is a high-level programming language." * 10  # ~450 chars
        test_input = "What is Python?"

        start_time = time.perf_counter()
        end_time = start_time + duration_seconds
        count = 0

        while time.perf_counter() < end_time:
            _ = validate_response_full(test_output, input_text=test_input)
            count += 1

        elapsed = time.perf_counter() - start_time
        throughput = count / elapsed

        return {
            "duration_seconds": elapsed,
            "total_validations": count,
            "throughput_per_second": throughput,
            "avg_ms_per_validation": (elapsed / count) * 1000,
        }

    def benchmark_scaling(self) -> Dict[str, Any]:
        """Test how time scales with input size."""
        sizes = [100, 500, 1000, 5000, 10000]
        results = {}

        base_text = "This is a test sentence for scaling analysis. " * 10  # ~470 chars

        for size in sizes:
            # Generate text of approximately target size
            multiplier = max(1, size // len(base_text))
            test_text = base_text * multiplier
            actual_size = len(test_text)

            # Measure time for 10 iterations
            times_ms = []
            for _ in range(10):
                start = time.perf_counter()
                _ = validate_response_full(test_text)
                elapsed = (time.perf_counter() - start) * 1000
                times_ms.append(elapsed)

            avg_ms = statistics.mean(times_ms)

            results[actual_size] = {
                "target_size": size,
                "actual_size": actual_size,
                "avg_ms": avg_ms,
                "ms_per_char": avg_ms / actual_size,
            }

        return results

    def run_benchmark(self) -> Dict[str, Any]:
        """Run full performance benchmark suite."""
        print("Running performance benchmarks...")
        print("  - Latency (100 iterations per test)")
        print("  - Throughput (5 second test)")
        print("  - Scaling (100 to 10,000 chars)")
        print()

        results = {
            "latency": self.benchmark_latency(iterations=100),
            "throughput": self.benchmark_throughput(duration_seconds=5),
            "scaling": self.benchmark_scaling(),
        }

        return results

    def print_report(self, results: Dict[str, Any]) -> None:
        """Print human-readable performance report."""
        print("=" * 80)
        print("validate_response_full() Performance Benchmark")
        print("=" * 80)
        print()

        # Latency results
        latency = results["latency"]
        print("Latency Analysis:")
        print(f"  Total iterations: {latency['total_iterations']}")
        print(f"  Overall average: {latency['overall_avg_ms']:.3f} ms")
        print(f"  Overall P50: {latency['overall_p50_ms']:.3f} ms")
        print(f"  Overall P95: {latency['overall_p95_ms']:.3f} ms")
        print(f"  Overall P99: {latency['overall_p99_ms']:.3f} ms")
        print(f"  Overall max: {latency['overall_max_ms']:.3f} ms")
        print(f"  Overall min: {latency['overall_min_ms']:.3f} ms")
        print()

        print("Per-Test Case Latency:")
        for tc in latency["test_cases"]:
            status = "[PASS]" if tc["target_met"] else "[FAIL]"
            print(f"  {status} {tc['name']}")
            print(f"    Output size: {tc['output_len']} chars")
            print(f"    Average: {tc['avg_ms']:.3f} ms (P50: {tc['p50_ms']:.3f}, P95: {tc['p95_ms']:.3f}, P99: {tc['p99_ms']:.3f})")
        print()

        # Throughput results
        throughput = results["throughput"]
        print("Throughput Analysis:")
        print(f"  Duration: {throughput['duration_seconds']:.2f} seconds")
        print(f"  Total validations: {throughput['total_validations']}")
        print(f"  Throughput: {throughput['throughput_per_second']:.2f} validations/second")
        print(f"  Average: {throughput['avg_ms_per_validation']:.3f} ms/validation")
        print()

        # Scaling results
        scaling = results["scaling"]
        print("Scaling Analysis (Time vs Input Size):")
        for size, data in sorted(scaling.items()):
            print(f"  {size:>6} chars: {data['avg_ms']:>7.3f} ms (avg) | {data['ms_per_char']:.6f} ms/char")
        print()

        # Pass/Fail assessment
        print("=" * 80)
        target_avg = 50.0
        if latency["target_met"]:
            print(f"[PASS] PERFORMANCE TARGET MET (Avg: {latency['overall_avg_ms']:.3f} ms < {target_avg} ms)")
        else:
            print(f"[FAIL] PERFORMANCE TARGET MISSED (Avg: {latency['overall_avg_ms']:.3f} ms >= {target_avg} ms)")

        print("=" * 80)


def main():
    """Run performance benchmark and print report."""
    benchmark = ValidateFullPerformance()
    results = benchmark.run_benchmark()
    benchmark.print_report(results)

    # Return exit code based on results
    import sys
    if results["latency"]["target_met"]:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Performance target not met


if __name__ == "__main__":
    main()
