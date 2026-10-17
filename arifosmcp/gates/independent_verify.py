"""
independent_verify.py — Orthogonal Verification Gate (INV-L6-ORTHO)
═══════════════════════════════════════════════════════════════════════════════

Self-certification of task completion is FORBIDDEN. Done-v must be executed by
FRAME in an isolated context receiving ONLY:
  1. SPEC.lock.json
  2. git diff HEAD
  3. Fresh output of the done-v test runner (clean subprocess)

FRAME outputs a strict boolean verdict + trace before allowing merge/completion.

Governance:
  - FRAME never mutates — observe-only
  - Verdict: PASS / FAIL / INSUFFICIENT_EVIDENCE
  - Trace: structured evidence of what was checked
  - Feature-flagged: ARIFOS_INDEPENDENT_VERIFY=1 (default OFF until wired)

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Configuration ────────────────────────────────────────────────────────────
_VERIFY_ENABLED = os.environ.get("ARIFOS_INDEPENDENT_VERIFY", "0") != "0"
_SPEC_LOCK_DIR = Path(
    os.environ.get(
        "ARIFOS_SPEC_LOCK_DIR",
        "/root/.local/share/arifos/state",
    )
)

# ── Verification Result ─────────────────────────────────────────────────────


class VerificationResult:
    """Structured verification verdict from FRAME."""

    def __init__(
        self,
        verdict: str,  # "PASS" | "FAIL" | "INSUFFICIENT_EVIDENCE"
        spec_hash: str | None = None,
        diff_hash: str | None = None,
        test_exit_code: int | None = None,
        test_output_tail: str | None = None,
        violations: list[str] | None = None,
        trace: dict[str, Any] | None = None,
    ):
        self.verdict = verdict
        self.spec_hash = spec_hash
        self.diff_hash = diff_hash
        self.test_exit_code = test_exit_code
        self.test_output_tail = test_output_tail
        self.violations = violations or []
        self.trace = trace or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "spec_hash": self.spec_hash,
            "diff_hash": self.diff_hash,
            "test_exit_code": self.test_exit_code,
            "test_output_tail": self.test_output_tail,
            "violations": self.violations,
            "trace": self.trace,
            "timestamp": self.timestamp,
        }

    @property
    def passed(self) -> bool:
        return self.verdict == "PASS"


# ── Verification Functions ───────────────────────────────────────────────────


def _read_spec_lock() -> dict[str, Any] | None:
    """Read SPEC.lock.json from the standard location."""
    path = _SPEC_LOCK_DIR / "SPEC.lock.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _get_git_diff() -> str | None:
    """Get current git diff (staged + unstaged)."""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd(),
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except Exception:
        return None


def _run_tests(done_v: str) -> tuple[int, str]:
    """Run the verification command in a clean subprocess.

    Returns (exit_code, output_tail).
    """
    try:
        result = subprocess.run(
            done_v,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute max
            cwd=os.getcwd(),
        )
        # Get last 50 lines of output
        output = result.stdout + result.stderr
        tail = "\n".join(output.strip().split("\n")[-50:])
        return result.returncode, tail
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT: verification command exceeded 300s"
    except Exception as e:
        return -1, f"ERROR: {str(e)}"


def _check_locus_violations(diff: str, locus: list[str]) -> list[str]:
    """Check if diff modifies files outside declared locus.

    Returns list of violation messages.
    """
    import fnmatch

    violations = []
    if not locus:
        return violations  # No locus = unrestricted

    # Parse diff for modified file paths
    modified_files = set()
    for line in diff.split("\n"):
        if line.startswith("+++ b/"):
            file_path = line[6:].strip()
            if file_path:
                modified_files.add(file_path)

    for file_path in modified_files:
        in_locus = False
        for pattern in locus:
            if fnmatch.fnmatch(file_path, os.path.normpath(pattern)):
                in_locus = True
                break
            if pattern.endswith("/") or pattern.endswith(os.sep):
                dir_prefix = os.path.normpath(pattern).rstrip(os.sep) + os.sep
                if file_path.startswith(dir_prefix):
                    in_locus = True
                    break
        if not in_locus:
            violations.append(f"OUT_OF_LOCUS: {file_path} not in {locus}")

    return violations


def _check_integrity_violations(diff: str) -> list[str]:
    """Check for anti-reward-hack violations in the diff.

    Returns list of violation messages.
    """
    violations = []
    diff_lower = diff.lower()

    # Check for test weakening patterns
    test_weakeners = [
        ("@pytest.mark.skip", "SKIP_DECORATOR"),
        ("@unittest.skip", "SKIP_DECORATOR"),
        ("@pytest.mark.xfail", "XFAIL_DECORATOR"),
        ("# noqa:", "NOQA_SUPPRESSION"),
        ("# type: ignore", "TYPE_IGNORE"),
    ]

    for pattern, label in test_weakeners:
        if pattern.lower() in diff_lower:
            # Check if it's in a test file
            for line in diff.split("\n"):
                if line.startswith("+++ b/") and "test" in line.lower():
                    if pattern.lower() in diff_lower:
                        violations.append(f"INTEGRITY_{label}: {pattern} in test file")
                        break

    return violations


def verify_completion(
    done_v: str | None = None,
    check_locus: bool = True,
    check_integrity: bool = True,
) -> VerificationResult:
    """Run orthogonal verification of task completion.

    This is the INV-L6-ORTHO gate. It must be called by a different
    agent/context than the one that performed the work.

    Args:
        done_v: Verification command. If None, reads from SPEC.lock.json.
        check_locus: Whether to check diff against declared locus.
        check_integrity: Whether to check for anti-reward-hack violations.

    Returns:
        VerificationResult with verdict PASS/FAIL/INSUFFICIENT_EVIDENCE.
    """
    violations = []
    trace: dict[str, Any] = {"checks": []}

    # 1. Read SPEC.lock.json
    spec = _read_spec_lock()
    spec_hash = None
    if spec:
        spec_hash = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:16]
        trace["spec_read"] = True
        trace["task_id"] = spec.get("task_id")
    else:
        trace["spec_read"] = False
        violations.append("NO_SPEC: SPEC.lock.json not found")

    # 2. Get git diff
    diff = _get_git_diff()
    diff_hash = None
    if diff:
        diff_hash = hashlib.sha256(diff.encode()).hexdigest()[:16]
        trace["diff_lines"] = len(diff.split("\n"))
        trace["checks"].append("diff_captured")
    else:
        trace["diff_lines"] = 0
        trace["checks"].append("no_diff")

    # 3. Check locus violations
    if check_locus and diff and spec:
        locus = spec.get("constraints", {}).get("locus", [])
        locus_violations = _check_locus_violations(diff, locus)
        violations.extend(locus_violations)
        if locus_violations:
            trace["checks"].append(f"locus_violations={len(locus_violations)}")
        else:
            trace["checks"].append("locus_ok")

    # 4. Check integrity violations
    if check_integrity and diff:
        integrity_violations = _check_integrity_violations(diff)
        violations.extend(integrity_violations)
        if integrity_violations:
            trace["checks"].append(f"integrity_violations={len(integrity_violations)}")
        else:
            trace["checks"].append("integrity_ok")

    # 5. Run verification command
    test_exit_code = None
    test_output_tail = None
    if done_v:
        test_exit_code, test_output_tail = _run_tests(done_v)
        trace["test_exit_code"] = test_exit_code
        trace["checks"].append("tests_executed")
        if test_exit_code != 0:
            violations.append(f"TEST_FAILED: exit_code={test_exit_code}")
    elif spec:
        done_v_from_spec = spec.get("constraints", {}).get("done_v")
        if done_v_from_spec:
            test_exit_code, test_output_tail = _run_tests(done_v_from_spec)
            trace["test_exit_code"] = test_exit_code
            trace["checks"].append("tests_executed_from_spec")
            if test_exit_code != 0:
                violations.append(f"TEST_FAILED: exit_code={test_exit_code}")
        else:
            trace["checks"].append("no_done_v_command")

    # 6. Determine verdict
    if violations:
        verdict = "FAIL"
    elif not spec and not diff:
        verdict = "INSUFFICIENT_EVIDENCE"
    else:
        verdict = "PASS"

    trace["violation_count"] = len(violations)
    trace["verdict"] = verdict

    return VerificationResult(
        verdict=verdict,
        spec_hash=spec_hash,
        diff_hash=diff_hash,
        test_exit_code=test_exit_code,
        test_output_tail=test_output_tail,
        violations=violations,
        trace=trace,
    )
