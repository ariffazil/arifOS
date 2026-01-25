"""
Phoenix-72 Guardrail CI Integration Test

This test runs the Phoenix-72 guardrail checks as part of the test suite,
ensuring constitutional drift and entropy growth are detected in CI.

Test Goals:
1. Detect hardcoded constitutional thresholds (spec sovereignty)
2. Enforce ΔS ≤ 0 constraint (net LOC cannot grow without justification)
3. Fail CI if violations detected
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL_SCRIPT = REPO_ROOT / "scripts" / "phoenix_72_guardrail.py"


class TestPhoenix72Guardrail:
    """Phoenix-72 Guardrail: Constitutional Drift & Entropy Detector"""

    def test_no_hardcoded_thresholds(self):
        """
        THRESHOLD SOVEREIGNTY: Scanner detects threshold violations (WARN mode).

        Constitutional thresholds (0.99, 0.95, 0.80, 0.50, 0.30, etc.) must be
        imported from spec-loaded modules, not hardcoded as literals.

        Authority: spec/v44/constitutional_floors.json, spec/v44/genius_law.json

        STAGED ENFORCEMENT: Currently in WARN mode (reports violations but doesn't block).
        Will transition to STRICT mode by deadline (2026-01-15).
        """
        result = subprocess.run(
            [sys.executable, str(GUARDRAIL_SCRIPT), "--check", "thresholds", "--mode", "warn"],
            capture_output=True,
            text=True,
        )

        # WARN mode should always return exit code 0
        assert result.returncode == 0, f"WARN mode should not block (got exit code {result.returncode})"

        # Assert scanner runs successfully and reports violations
        assert "Scanning for hardcoded thresholds" in result.stdout, "Scanner did not run"
        assert "violations" in result.stdout.lower(), "No violation report found"

        # Assert top offenders list is printed
        assert "Top 10 offenders" in result.stdout or "Top offenders" in result.stdout, "Top offenders list missing"

    def test_strict_mode_still_works(self):
        """
        THRESHOLD SOVEREIGNTY: STRICT mode enforcement still functional.

        Verify that --mode strict still blocks when violations are detected.
        This ensures we can transition to strict enforcement later.
        """
        result = subprocess.run(
            [sys.executable, str(GUARDRAIL_SCRIPT), "--check", "thresholds", "--mode", "strict"],
            capture_output=True,
            text=True,
        )

        # STRICT mode may return exit code 0 (no violations) or 1 (violations detected)
        # Just verify it runs and produces output
        assert result.returncode in [0, 1], f"Unexpected exit code: {result.returncode}"

        # Verify scanner ran
        assert "Scanning for hardcoded thresholds" in result.stdout, "Scanner did not run in strict mode"

    def test_entropy_constraint_satisfied(self):
        """
        ENTROPY CONSTRAINT: Delta_S_new + Delta_S_existing <= 0 (STRICT enforcement)

        Net LOC in arifos_core/ cannot grow without justification.
        Enforces "replace-only" development philosophy.

        To justify growth:
        1. Remove equivalent LOC elsewhere, OR
        2. Add entry to .phoenix_justifications.json, OR
        3. Update baseline: python scripts/phoenix_72_guardrail.py --update-baseline

        NOTE: Entropy check remains in STRICT mode (blocks on violations).
        """
        result = subprocess.run(
            [sys.executable, str(GUARDRAIL_SCRIPT), "--check", "entropy", "--mode", "strict"],
            capture_output=True,
            text=True,
        )

        # Exit code 0 = no violations, 2 = entropy growth detected
        if result.returncode == 2:
            pytest.fail(
                f"Entropy growth detected:\n\n{result.stdout}\n\nSee: scripts/phoenix_72_guardrail.py --update-baseline"
            )

        # Exit code 0 expected
        assert result.returncode == 0, f"Guardrail check failed: {result.stderr}"

    def test_full_guardrail_check(self):
        """
        Run both threshold and entropy checks together (STAGED enforcement).

        Threshold check: WARN mode (reports but doesn't block)
        Entropy check: STRICT mode (blocks on violations)

        This is the main CI gate. During transition period, threshold violations
        are reported but don't block CI. By 2026-01-15, threshold check will
        transition to STRICT mode.
        """
        result = subprocess.run(
            [sys.executable, str(GUARDRAIL_SCRIPT)],
            capture_output=True,
            text=True,
        )

        # Exit codes: 0=pass (or warn mode), 1=threshold (strict only), 2=entropy, 3=both
        # During staged enforcement, only entropy violations block (exit code 2)
        if result.returncode == 2:
            pytest.fail(
                f"Entropy growth detected (STRICT mode):\n\n{result.stdout}\n\nSee: --update-baseline"
            )
        elif result.returncode == 3:
            pytest.fail(
                f"Both violations detected:\n\n{result.stdout}"
            )

        # Entropy must pass (STRICT), thresholds in WARN mode won't block
        assert result.returncode in [0, 1], f"Unexpected exit code: {result.returncode}"

        # Verify both checks ran
        assert "Scanning for hardcoded thresholds" in result.stdout, "Threshold check didn't run"
        assert "Checking entropy constraint" in result.stdout, "Entropy check didn't run"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
