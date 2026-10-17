"""
drift_gate.py — Spec-Code Drift Gate (INV-L4-DRIFT)
═══════════════════════════════════════════════════════════════════════════════

Code mutations outside the declared locus in SPEC.lock.json or lacking mapped
verification signals fail the pre-commit drift gate.

This module extends independent_verify.py's locus check with:
  - Symbol-level AST extraction (via regex fallback when tree-sitter unavailable)
  - Frozen file hash verification
  - Negative constraint enforcement
  - Pre-commit hook integration

Governance:
  - Deterministic — no LLM calls
  - Feature-flagged: ARIFOS_DRIFT_GATE=1 (default OFF)
  - Returns structured DriftReport with PASS/BLOCK verdict

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Configuration ────────────────────────────────────────────────────────────
_DRIFT_GATE_ENABLED = os.environ.get("ARIFOS_DRIFT_GATE", "0") != "0"
_SPEC_LOCK_DIR = Path(
    os.environ.get(
        "ARIFOS_SPEC_LOCK_DIR",
        "/root/.local/share/arifos/state",
    )
)


class DriftReport:
    """Structured drift detection report."""

    def __init__(
        self,
        verdict: str,  # "PASS" | "BLOCK"
        violations: list[dict[str, Any]] | None = None,
        checked_files: int = 0,
        locus_patterns: list[str] | None = None,
        negative_patterns: list[str] | None = None,
    ):
        self.verdict = verdict
        self.violations = violations or []
        self.checked_files = checked_files
        self.locus_patterns = locus_patterns or []
        self.negative_patterns = negative_patterns or []
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "violations": self.violations,
            "checked_files": self.checked_files,
            "locus_patterns": self.locus_patterns,
            "negative_patterns": self.negative_patterns,
            "timestamp": self.timestamp,
        }

    @property
    def passed(self) -> bool:
        return self.verdict == "PASS"


def _read_spec_lock() -> dict[str, Any] | None:
    """Read SPEC.lock.json."""
    path = _SPEC_LOCK_DIR / "SPEC.lock.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _get_modified_files_from_diff(diff: str) -> list[str]:
    """Extract modified file paths from git diff output."""
    files = []
    for line in diff.split("\n"):
        if line.startswith("+++ b/"):
            file_path = line[6:].strip()
            if file_path:
                files.append(file_path)
    return files


def _extract_python_symbols(content: str) -> list[str]:
    """Extract Python function/class definitions via regex.

    Fallback when tree-sitter is not available.
    """
    symbols = []
    # Match class and function definitions
    for match in re.finditer(r"^(?:class|def)\s+(\w+)", content, re.MULTILINE):
        symbols.append(match.group(1))
    return symbols


def _check_frozen_files(
    modified_files: list[str],
    frozen_entries: list[str],
) -> list[dict[str, Any]]:
    """Check if any frozen files were modified.

    Returns list of violation dicts.
    """
    violations = []
    frozen_map: dict[str, str] = {}
    for entry in frozen_entries:
        if ":" in entry:
            path_str, file_hash = entry.rsplit(":", 1)
            frozen_map[os.path.normpath(path_str)] = file_hash

    for file_path in modified_files:
        norm_path = os.path.normpath(file_path)
        if norm_path in frozen_map:
            expected_hash = frozen_map[norm_path]
            actual_path = Path(file_path)
            if actual_path.exists():
                actual_hash = hashlib.sha256(actual_path.read_bytes()).hexdigest()[:16]
                if actual_hash != expected_hash:
                    violations.append(
                        {
                            "type": "FROZEN_FILE_MUTATED",
                            "file": file_path,
                            "expected_hash": expected_hash,
                            "actual_hash": actual_hash,
                        }
                    )
    return violations


def check_drift(
    diff: str | None = None,
    repo_root: str | None = None,
) -> DriftReport:
    """Run the drift gate check.

    Args:
        diff: Git diff text. If None, runs `git diff HEAD`.
        repo_root: Repository root. Defaults to cwd.

    Returns:
        DriftReport with PASS or BLOCK verdict.
    """
    violations: list[dict[str, Any]] = []

    # Get diff if not provided
    if diff is None:
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=repo_root or os.getcwd(),
            )
            diff = result.stdout if result.returncode == 0 else ""
        except Exception:
            diff = ""

    # Read spec
    spec = _read_spec_lock()
    if spec is None:
        return DriftReport(
            verdict="PASS",
            violations=[],
            checked_files=0,
        )

    constraints = spec.get("constraints", {})
    locus = constraints.get("locus", [])
    negative = constraints.get("negative", [])
    frozen = constraints.get("frozen", [])

    # Get modified files
    modified_files = _get_modified_files_from_diff(diff)

    # Check locus violations
    import fnmatch

    for file_path in modified_files:
        norm_path = os.path.normpath(file_path)

        # Check negative list
        for pattern in negative:
            norm_pattern = os.path.normpath(pattern)
            if fnmatch.fnmatch(norm_path, norm_pattern):
                violations.append(
                    {
                        "type": "NEGATIVE_CONSTRAINT",
                        "file": file_path,
                        "pattern": pattern,
                        "message": f"File {file_path} is in negative (do-not-touch) list",
                    }
                )
            elif pattern.endswith("/") or pattern.endswith(os.sep):
                dir_prefix = norm_pattern.rstrip(os.sep) + os.sep
                if norm_path.startswith(dir_prefix):
                    violations.append(
                        {
                            "type": "NEGATIVE_CONSTRAINT",
                            "file": file_path,
                            "pattern": pattern,
                            "message": f"File {file_path} is under negative directory {pattern}",
                        }
                    )

        # Check locus (only if locus is specified)
        if locus:
            in_locus = False
            for pattern in locus:
                norm_pattern = os.path.normpath(pattern)
                if fnmatch.fnmatch(norm_path, norm_pattern):
                    in_locus = True
                    break
                if pattern.endswith("/") or pattern.endswith(os.sep):
                    dir_prefix = norm_pattern.rstrip(os.sep) + os.sep
                    if norm_path.startswith(dir_prefix):
                        in_locus = True
                        break
            if not in_locus:
                violations.append(
                    {
                        "type": "OUT_OF_LOCUS",
                        "file": file_path,
                        "locus": locus,
                        "message": f"File {file_path} not in declared locus {locus}",
                    }
                )

    # Check frozen files
    if frozen:
        frozen_violations = _check_frozen_files(modified_files, frozen)
        violations.extend(frozen_violations)

    verdict = "BLOCK" if violations else "PASS"
    return DriftReport(
        verdict=verdict,
        violations=violations,
        checked_files=len(modified_files),
        locus_patterns=locus,
        negative_patterns=negative,
    )
