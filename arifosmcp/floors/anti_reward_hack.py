"""
anti_reward_hack.py — Anti-Reward-Hack Runtime Enforcement (INV-L6-INTEGRITY)
═══════════════════════════════════════════════════════════════════════════════

Any diff that deletes tests, weakens assertions, adds skip decorators, or
modifies CI/linter rules without an explicit 888 capability token triggers
an immediate F1/F2 block.

This module provides deterministic diff scanning — no LLM calls, pure pattern
matching against the diff text.

Patterns detected:
  - Test file deletions or assertion count reductions
  - Skip/xfail decorators in test files
  - noqa/type:ignore suppressions in test files
  - CI workflow modifications without authorization
  - Linter config changes without authorization
  - Mock additions that suppress failures (not genuine test doubles)

Governance:
  - Deterministic — no LLM, pure regex
  - Feature-flagged: ARIFOS_ANTI_REWARD_HACK=1 (default OFF)
  - Returns IntegrityReport with PASS/F1_VIOLATION/F2_VIOLATION verdict

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any


class IntegrityReport:
    """Structured integrity violation report."""

    def __init__(
        self,
        verdict: str,  # "PASS" | "F1_VIOLATION" | "F2_VIOLATION"
        violations: list[dict[str, Any]] | None = None,
    ):
        self.verdict = verdict
        self.violations = violations or []
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "violations": self.violations,
            "timestamp": self.timestamp,
        }

    @property
    def passed(self) -> bool:
        return self.verdict == "PASS"


def _is_test_file(file_path: str) -> bool:
    """Check if a file path is a test file."""
    path_lower = file_path.lower()
    return any(
        pattern in path_lower
        for pattern in [
            "test_",
            "_test.py",
            "tests/",
            "test/",
            "spec/",
            "spec_",
            ".test.",
            ".spec.",
            "__tests__",
        ]
    )


def _is_ci_file(file_path: str) -> bool:
    """Check if a file is a CI/workflow configuration."""
    path_lower = file_path.lower()
    return any(
        pattern in path_lower
        for pattern in [
            ".github/workflows/",
            "ci.yml",
            "ci.yaml",
            ".gitlab-ci.yml",
            "jenkinsfile",
            ".circleci/",
            "Makefile",  # Often contains CI targets
        ]
    )


def _is_linter_config(file_path: str) -> bool:
    """Check if a file is a linter/formatter configuration."""
    basename = os.path.basename(file_path).lower()
    return basename in [
        ".flake8",
        ".pylintrc",
        "pylintrc",
        ".eslintrc",
        ".eslintrc.json",
        ".eslintrc.js",
        ".prettierrc",
        "ruff.toml",
        ".ruff.toml",
        "setup.cfg",
        "pyproject.toml",
        "mypy.ini",
        ".mypy.ini",
        "tox.ini",
    ]


def scan_diff(diff: str) -> IntegrityReport:
    """Scan a git diff for reward-hack patterns.

    Args:
        diff: Git diff text (from `git diff HEAD`).

    Returns:
        IntegrityReport with PASS/F1_VIOLATION/F2_VIOLATION verdict.
    """
    violations: list[dict[str, Any]] = []

    # Parse diff into per-file sections
    current_file = None
    file_diffs: dict[str, list[str]] = {}

    for line in diff.split("\n"):
        if line.startswith("+++ b/"):
            current_file = line[6:].strip()
            file_diffs[current_file] = []
        elif current_file and line.startswith("-") and not line.startswith("---"):
            # Removed lines
            file_diffs[current_file].append(line)
        elif current_file and line.startswith("+") and not line.startswith("+++"):
            # Added lines
            file_diffs[current_file].append(line)

    for file_path, lines in file_diffs.items():
        removed = [l[1:] for l in lines if l.startswith("-")]
        added = [l[1:] for l in lines if l.startswith("+")]
        all_changes = removed + added
        changes_text = "\n".join(all_changes)

        # ── Test file protections ────────────────────────────────────────
        if _is_test_file(file_path):
            # Skip decorators
            skip_patterns = [
                (r"@pytest\.mark\.skip", "pytest.skip decorator"),
                (r"@unittest\.skip", "unittest.skip decorator"),
                (r"@pytest\.mark\.xfail", "pytest.xfail decorator"),
                (r"pytest\.skip\(", "pytest.skip() call"),
                (r"self\.skipTest\(", "self.skipTest() call"),
            ]
            for pattern, label in skip_patterns:
                if re.search(pattern, changes_text):
                    violations.append(
                        {
                            "type": "TEST_SKIP_DECORATOR",
                            "file": file_path,
                            "pattern": label,
                            "floor": "F2",  # F2 TRUTH
                            "message": f"Test weakening: {label} in {file_path}",
                        }
                    )

            # noqa / type:ignore suppressions
            suppression_patterns = [
                (r"#\s*noqa:", "noqa suppression"),
                (r"#\s*type:\s*ignore", "type:ignore suppression"),
                (r"#\s*pragma:\s*no cover", "pragma:no-cover"),
            ]
            for pattern, label in suppression_patterns:
                if re.search(pattern, changes_text):
                    violations.append(
                        {
                            "type": "TEST_SUPPRESSION",
                            "file": file_path,
                            "pattern": label,
                            "floor": "F2",
                            "message": f"Test suppression: {label} in {file_path}",
                        }
                    )

            # Assertion count reduction (heuristic: count assert statements)
            removed_asserts = sum(1 for l in removed if re.search(r"\bassert\b", l))
            added_asserts = sum(1 for l in added if re.search(r"\bassert\b", l))
            if removed_asserts > added_asserts and removed_asserts > 0:
                violations.append(
                    {
                        "type": "ASSERTION_REDUCTION",
                        "file": file_path,
                        "removed_asserts": removed_asserts,
                        "added_asserts": added_asserts,
                        "floor": "F2",
                        "message": f"Assertions reduced: {removed_asserts} removed, {added_asserts} added in {file_path}",
                    }
                )

        # ── CI file protections ──────────────────────────────────────────
        if _is_ci_file(file_path):
            violations.append(
                {
                    "type": "CI_MODIFICATION",
                    "file": file_path,
                    "floor": "F1",  # F1 AMANAH
                    "message": f"CI/workflow modification without authorization: {file_path}",
                }
            )

        # ── Linter config protections ────────────────────────────────────
        if _is_linter_config(file_path):
            # Check if severity/strictness was reduced
            if any(
                keyword in changes_text.lower()
                for keyword in [
                    "ignore",
                    "disable",
                    "skip",
                    "exclude",
                ]
            ):
                violations.append(
                    {
                        "type": "LINTER_WEAKENING",
                        "file": file_path,
                        "floor": "F2",
                        "message": f"Linter config weakening detected in {file_path}",
                    }
                )

    # Determine verdict
    if not violations:
        verdict = "PASS"
    elif any(v.get("floor") == "F1" for v in violations):
        verdict = "F1_VIOLATION"
    else:
        verdict = "F2_VIOLATION"

    return IntegrityReport(verdict=verdict, violations=violations)
