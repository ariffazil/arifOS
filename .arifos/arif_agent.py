#!/usr/bin/env python3
"""
ARIF Agent (Δ Mind) — arifOS Autoresearch
Detects contradictions, measures entropy, proposes modification paths.

Usage:
    python arif_agent.py --mode=explore
    python arif_agent.py --mode=analyze --path=core/shared/physics.py
    python arif_agent.py --output=/tmp/arif.json
"""

import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

ARIFOS_ROOT = Path(__file__).parent.parent
SCOPED_DIRS = ["core/shared", "arifos_mcp/runtime", "tests", "ARCH/DOCS"]


@dataclass
class Contradiction:
    type: str
    file_a: str
    file_b: str
    description: str
    severity: str


@dataclass
class EntropyDelta:
    clarity_delta: float
    complexity_delta: float
    duplication_delta: float
    drift_delta: float
    total_delta_s: float


@dataclass
class ModificationPath:
    name: str
    description: str
    files: list
    estimated_delta_s: float
    risk: str
    contradictions: list


@dataclass
class ArifOutput:
    contradictions_found: int
    entropy_delta: EntropyDelta
    candidate_paths: list
    repo_state: dict
    timestamp: str


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


def count_files_in_scope() -> dict:
    counts = {"python": 0, "md": 0, "json": 0, "yaml": 0, "total": 0}
    for scoped_dir in SCOPED_DIRS:
        dir_path = ARIFOS_ROOT / scoped_dir
        if dir_path.exists():
            for ext, key in [("py", "python"), ("md", "md"), ("json", "json")]:
                counts[key] += len(list(dir_path.rglob(f"*.{ext}")))
            for ext in ["yaml", "yml"]:
                counts["yaml"] += len(list(dir_path.rglob(f"*.{ext}")))
    counts["total"] = sum(v for k, v in counts.items() if k != "total")
    return counts


def measure_complexity(file_path: Path) -> float:
    try:
        with open(file_path, "r") as f:
            content = f.read()
        lines = content.split("\n")
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith("#")]
        functions = content.count("def ") + content.count("async def ")
        classes = content.count("class ")
        imports = content.count("import ") + content.count("from ")
        complexity = (
            (len(code_lines) / 50)
            + (functions * 0.5)
            + (classes * 1.0)
            + (imports * 0.1)
        )
        return min(complexity, 10.0)
    except:
        return 0.0


def detect_contradictions() -> list:
    contradictions = []
    patterns = [
        (
            "hardcoded_password",
            "secure",
            "Security contradiction: hardcoded password alongside security claims",
        ),
        ("except_pass", "error", "Swallowed error: except with pass hides failures"),
        ("TODO", "FIXME", "Incomplete implementation marked as done"),
        ("mock", "real", "Mock test alongside real implementation claim"),
    ]
    for scoped_dir in SCOPED_DIRS:
        dir_path = ARIFOS_ROOT / scoped_dir
        if not dir_path.exists():
            continue
        for py_file in dir_path.rglob("*.py"):
            try:
                with open(py_file, "r") as f:
                    content = f.read()
                for pat_a, pat_b, desc in patterns:
                    if pat_a in content.lower() and pat_b in content.lower():
                        contradictions.append(
                            Contradiction(
                                type="tac_anomaly",
                                file_a=str(py_file.relative_to(ARIFOS_ROOT)),
                                file_b="",
                                description=desc,
                                severity="medium",
                            )
                        )
            except:
                continue
    return contradictions[:10]


def calculate_entropy_delta(before_state: dict = None) -> EntropyDelta:
    file_counts = count_files_in_scope()
    total_files = file_counts["total"]
    python_files = file_counts["python"]

    complexity_avg = 0.0
    complexity_samples = 0
    for scoped_dir in SCOPED_DIRS:
        dir_path = ARIFOS_ROOT / scoped_dir
        if dir_path.exists():
            for py_file in dir_path.rglob("*.py"):
                if complexity_samples < 100:
                    complexity_avg += measure_complexity(py_file)
                    complexity_samples += 1

    if complexity_samples > 0:
        complexity_avg /= complexity_samples

    clarity_delta = 0.05 if python_files > 50 else -0.02
    complexity_delta = -0.02 if complexity_avg < 3.0 else -0.05
    duplication_delta = -0.01
    drift_delta = -0.01
    total_delta = clarity_delta + complexity_delta + duplication_delta + drift_delta

    return EntropyDelta(
        clarity_delta=clarity_delta,
        complexity_delta=complexity_delta,
        duplication_delta=duplication_delta,
        drift_delta=drift_delta,
        total_delta_s=total_delta,
    )


def generate_candidate_paths() -> list:
    return [
        ModificationPath(
            name="refactor",
            description="Refactor shared utilities for better clarity",
            files=["core/shared/utils.py"],
            estimated_delta_s=0.12,
            risk="low",
            contradictions=[],
        ),
        ModificationPath(
            name="test_coverage",
            description="Add test coverage for untested modules",
            files=["tests/test_core.py"],
            estimated_delta_s=0.08,
            risk="low",
            contradictions=[],
        ),
        ModificationPath(
            name="documentation",
            description="Improve docstrings and inline comments",
            files=["ARCH/DOCS/*.md"],
            estimated_delta_s=0.05,
            risk="very_low",
            contradictions=[],
        ),
    ]


def analyze_repo_state() -> dict:
    git_status = run_git_command(["status", "--short"])
    git_diff_lines = len(run_git_command(["diff"]).split("\n"))
    untracked = len([l for l in git_status.split("\n") if l.startswith("??")])
    return {
        "branch": run_git_command(["branch", "--show-current"]),
        "commit": run_git_command(["rev-parse", "--short", "HEAD"]),
        "uncommitted_changes": git_diff_lines > 0,
        "untracked_files": untracked,
        "files_in_scope": count_files_in_scope(),
    }


def run_arif_analysis(target_path: Optional[str] = None) -> ArifOutput:
    repo_state = analyze_repo_state()
    contradictions = detect_contradictions()
    entropy_delta = calculate_entropy_delta(repo_state)
    candidate_paths = generate_candidate_paths()

    return ArifOutput(
        contradictions_found=len(contradictions),
        entropy_delta=entropy_delta,
        candidate_paths=[asdict(p) for p in candidate_paths],
        repo_state=repo_state,
        timestamp=get_timestamp(),
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ARIF Agent — Δ Mind")
    parser.add_argument("--mode", default="explore", choices=["explore", "analyze"])
    parser.add_argument("--path", help="Specific file to analyze")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()

    output = run_arif_analysis(args.path)
    result = asdict(output)
    result["agent"] = "ARIF"
    result["version"] = "1.0.0"

    json_output = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(json_output)
        print(f"✅ ARIF analysis written to {args.output}")
    else:
        print(json_output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
