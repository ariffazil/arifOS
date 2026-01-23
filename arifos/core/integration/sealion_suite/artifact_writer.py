"""
artifact_writer.py - Test Run Artifact Generation for SEA-LION v4 Evaluation

Generates structured test run artifacts:
- run_config.json - Configuration and environment
- results.jsonl - One record per test case
- summary.json - Aggregated statistics
- failures.json - Failed cases only
- transcript.md - Human-readable report (optional)
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .evaluator import TestResult


class ArtifactWriter:
    """Writes test run artifacts to logs directory."""

    def __init__(self, run_dir: Path):
        """
        Initialize artifact writer.

        Args:
            run_dir: Directory to write artifacts (logs/sealion_runs/<timestamp>/)
        """
        self.run_dir = run_dir
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def write_run_config(
        self,
        model: str,
        provider: str,
        suite_name: str,
        total_cases: int,
        env_vars: Dict[str, str],
    ):
        """Write run configuration file."""
        # Get git commit hash
        git_hash = "unknown"
        git_tag = None
        try:
            git_hash = (
                subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
                .decode()
                .strip()[:8]
            )
            # Try to get tag if on tagged commit
            try:
                git_tag = (
                    subprocess.check_output(
                        ["git", "describe", "--exact-match", "--tags"], stderr=subprocess.DEVNULL
                    )
                    .decode()
                    .strip()
                )
            except subprocess.CalledProcessError:
                pass
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        config = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "provider": provider,
            "suite": suite_name,
            "total_cases": total_cases,
            "git_commit": git_hash,
            "git_tag": git_tag,
            "environment": env_vars,
            "arifos_version": "v45.0.0-patch-b1",
        }

        config_path = self.run_dir / "run_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        print(f"✅ Wrote config: {config_path}")

    def write_results_jsonl(self, results: List[TestResult]):
        """Write results as JSONL (one record per test)."""
        results_path = self.run_dir / "results.jsonl"

        with open(results_path, "w", encoding="utf-8") as f:
            for result in results:
                record = {
                    "test_id": result.test_id,
                    "test_name": result.test_name,
                    "bucket": result.bucket,
                    "passed": result.passed,
                    "skipped": result.skipped,
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms,
                    "lane": result.lane,
                    "verdict": result.verdict,
                    "llm_called": result.llm_called,
                    "metrics": result.metrics,
                    "validation_failures": result.validation_failures,
                    "validation_warnings": result.validation_warnings,
                    "prompt": result.prompt if len(result.prompt) < 200 else result.prompt[:200] + "...",
                    "response": result.response if len(result.response) < 500 else result.response[:500] + "...",
                }
                f.write(json.dumps(record) + "\n")

        print(f"✅ Wrote results: {results_path}")

    def write_summary(self, results: List[TestResult], suite_name: str):
        """Write summary statistics."""
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed and not r.skipped and not r.error)
        errors = sum(1 for r in results if r.error)
        skipped = sum(1 for r in results if r.skipped)

        # Aggregate by bucket
        bucket_stats = {}
        for result in results:
            if result.bucket not in bucket_stats:
                bucket_stats[result.bucket] = {"total": 0, "passed": 0, "failed": 0}
            bucket_stats[result.bucket]["total"] += 1
            if result.passed:
                bucket_stats[result.bucket]["passed"] += 1
            elif not result.skipped and not result.error:
                bucket_stats[result.bucket]["failed"] += 1

        # Aggregate verdicts
        verdict_counts = {}
        for result in results:
            if result.verdict:
                verdict_counts[result.verdict] = verdict_counts.get(result.verdict, 0) + 1

        # Aggregate lanes
        lane_counts = {}
        for result in results:
            if result.lane:
                lane_counts[result.lane] = lane_counts.get(result.lane, 0) + 1

        # LLM call stats
        llm_called_count = sum(1 for r in results if r.llm_called)
        llm_not_called_count = sum(1 for r in results if r.llm_called is False)

        # Average execution time
        avg_exec_time = sum(r.execution_time_ms for r in results) / total if total > 0 else 0

        summary = {
            "suite": suite_name,
            "timestamp": datetime.now().isoformat(),
            "totals": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "0%",
            },
            "bucket_stats": bucket_stats,
            "verdict_distribution": verdict_counts,
            "lane_distribution": lane_counts,
            "llm_calls": {
                "called": llm_called_count,
                "not_called": llm_not_called_count,
            },
            "performance": {
                "avg_execution_time_ms": round(avg_exec_time, 2),
                "total_execution_time_ms": round(sum(r.execution_time_ms for r in results), 2),
            },
        }

        summary_path = self.run_dir / "summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print(f"✅ Wrote summary: {summary_path}")
        return summary

    def write_failures(self, results: List[TestResult]):
        """Write failures.json with only failed cases."""
        failures = [r for r in results if not r.passed and not r.skipped]

        failures_data = {
            "count": len(failures),
            "failures": [
                {
                    "test_id": r.test_id,
                    "test_name": r.test_name,
                    "bucket": r.bucket,
                    "error": r.error,
                    "prompt": r.prompt[:200] if len(r.prompt) < 200 else r.prompt[:200] + "...",
                    "lane": r.lane,
                    "verdict": r.verdict,
                    "validation_failures": r.validation_failures,
                    "response_snippet": r.response[:300] if r.response else "",
                }
                for r in failures
            ],
        }

        failures_path = self.run_dir / "failures.json"
        with open(failures_path, "w", encoding="utf-8") as f:
            json.dump(failures_data, f, indent=2)

        print(f"✅ Wrote failures: {failures_path}")

    def write_transcript(self, results: List[TestResult], suite_name: str, summary: Dict[str, Any]):
        """Write human-readable markdown transcript."""
        transcript_path = self.run_dir / "transcript.md"

        with open(transcript_path, "w", encoding="utf-8") as f:
            # Header
            f.write(f"# SEA-LION v4 Evaluation Transcript\n\n")
            f.write(f"**Suite:** {suite_name}\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**arifOS Version:** v45.0.0-patch-b1\n\n")

            # Summary
            f.write("## Summary\n\n")
            totals = summary["totals"]
            f.write(f"- **Total Cases:** {totals['total']}\n")
            f.write(f"- **Passed:** {totals['passed']} ✅\n")
            f.write(f"- **Failed:** {totals['failed']} ❌\n")
            f.write(f"- **Errors:** {totals['errors']} 🔴\n")
            f.write(f"- **Skipped:** {totals['skipped']} ⏭️\n")
            f.write(f"- **Pass Rate:** {totals['pass_rate']}\n\n")

            # Performance
            perf = summary["performance"]
            f.write(f"**Performance:**\n")
            f.write(f"- Avg execution time: {perf['avg_execution_time_ms']:.0f}ms\n")
            f.write(f"- Total execution time: {perf['total_execution_time_ms']/1000:.1f}s\n\n")

            # Bucket breakdown
            f.write("## Bucket Breakdown\n\n")
            for bucket, stats in summary["bucket_stats"].items():
                f.write(f"### {bucket}\n")
                f.write(f"- Total: {stats['total']}\n")
                f.write(f"- Passed: {stats['passed']} / {stats['total']}\n\n")

            # Verdict distribution
            f.write("## Verdict Distribution\n\n")
            for verdict, count in summary["verdict_distribution"].items():
                f.write(f"- {verdict}: {count}\n")
            f.write("\n")

            # Lane distribution
            f.write("## Lane Distribution\n\n")
            for lane, count in summary["lane_distribution"].items():
                f.write(f"- {lane}: {count}\n")
            f.write("\n")

            # LLM calls
            llm = summary["llm_calls"]
            f.write(f"## LLM Calls\n\n")
            f.write(f"- Called: {llm['called']}\n")
            f.write(f"- Not Called (REFUSE short-circuit / templates): {llm['not_called']}\n\n")

            # Failed cases details
            failures = [r for r in results if not r.passed and not r.skipped]
            if failures:
                f.write(f"## Failed Cases ({len(failures)})\n\n")
                for r in failures:
                    f.write(f"### [{r.test_id}] {r.test_name}\n")
                    f.write(f"- **Bucket:** {r.bucket}\n")
                    if r.error:
                        f.write(f"- **Error:** {r.error}\n")
                    else:
                        f.write(f"- **Lane:** {r.lane}\n")
                        f.write(f"- **Verdict:** {r.verdict}\n")
                        f.write(f"- **Failures:**\n")
                        for failure in r.validation_failures:
                            f.write(f"  - {failure}\n")
                    f.write("\n")

            # Sample responses (first 5 passed cases)
            passed_samples = [r for r in results if r.passed][:5]
            if passed_samples:
                f.write(f"## Sample Passed Cases\n\n")
                for r in passed_samples:
                    f.write(f"### [{r.test_id}] {r.test_name}\n")
                    f.write(f"- **Prompt:** {r.prompt[:150]}...\n")
                    f.write(f"- **Lane:** {r.lane}\n")
                    f.write(f"- **Verdict:** {r.verdict}\n")
                    f.write(f"- **Response:** {r.response[:200]}...\n\n")

        print(f"✅ Wrote transcript: {transcript_path}")


def create_run_directory() -> Path:
    """Create timestamped run directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path("logs") / "sealion_runs" / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_all_artifacts(
    run_dir: Path,
    results: List[TestResult],
    suite_name: str,
    model: str,
    provider: str,
    total_cases: int,
    env_vars: Dict[str, str],
):
    """Write all artifacts for a test run."""
    writer = ArtifactWriter(run_dir)

    writer.write_run_config(model, provider, suite_name, total_cases, env_vars)
    writer.write_results_jsonl(results)
    summary = writer.write_summary(results, suite_name)
    writer.write_failures(results)
    writer.write_transcript(results, suite_name, summary)

    return summary
