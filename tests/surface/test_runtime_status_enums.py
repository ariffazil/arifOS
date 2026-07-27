"""Regression test for RuntimeStatus/Verdict enum drift.

Audit finding (GPT-5.6 external probe, 2026-07-27):
  - RuntimeStatus.SABAR was used at runtime/tools_internal.py:1371 while
    some RuntimeStatus enums (legacy `runtime/tools.py:2669`) lacked it.
  - Verdict.DEGRADED was used at runtime/orchestrator.py:62 while the
    canonical Verdict does NOT have DEGRADED.
  - RuntimeStatus.FAILURE was used at tools/architect.py:100 while FAILURE
    is not in the canonical enum.

These crashed with AttributeError on kernel import / execution.

Canonical surfaces (after 2026-07-27 fix):
  - RuntimeStatus: SUCCESS, ERROR, TIMEOUT, RETRY, HOLD, SABAR, DRY_RUN, DEGRADED
  - Verdict: VOID, HOLD_888, HOLD, SABAR, PARTIAL, PROVISIONAL, SEAL

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import pytest


EXPECTED_RUNTIME_STATUS = {
    "SUCCESS",
    "ERROR",
    "TIMEOUT",
    "RETRY",
    "HOLD",
    "SABAR",
    "DRY_RUN",
    "DEGRADED",
}

EXPECTED_VERDICT = {
    "VOID",
    "HOLD_888",
    "HOLD",
    "SABAR",
    "PARTIAL",
    "PROVISIONAL",
    "SEAL",
}

# These enum values must NEVER appear at call sites because they do not exist
# on the canonical enums. Aliases map to:
#   FAILURE -> ERROR
#   DEGRADED (on Verdict) -> PARTIAL
FORBIDDEN_VERDICT_VALUES = {"DEGRADED", "FAILURE"}
FORBIDDEN_RUNTIME_STATUS_VALUES = {"FAILURE"}


class TestCanonicalEnums:
    def test_runtime_status_canonical_members(self):
        from arifosmcp.models.verdicts import RuntimeStatus
        actual = {m.name for m in RuntimeStatus}
        assert actual == EXPECTED_RUNTIME_STATUS, (
            f"RuntimeStatus drifted. expected={EXPECTED_RUNTIME_STATUS} actual={actual}"
        )

    def test_verdict_canonical_members(self):
        from arifosmcp.models.verdicts import Verdict
        actual = {m.name for m in Verdict}
        assert actual == EXPECTED_VERDICT, (
            f"Verdict drifted. expected={EXPECTED_VERDICT} actual={actual}"
        )

    def test_runtime_model_reexports_canonical(self):
        # runtime/model.py should re-export the canonical RuntimeStatus, not
        # the legacy local enum from runtime/tools.py.
        from arifosmcp.runtime.model import RuntimeStatus as M_RS
        from arifosmcp.models.verdicts import RuntimeStatus as V_RS
        assert M_RS is V_RS, "runtime.model.RuntimeStatus must be canonical (models.verdicts)"

    def test_runtime_model_verdict_reexport(self):
        from arifosmcp.runtime.model import Verdict as M_V
        from arifosmcp.models.verdicts import Verdict as V_V
        assert M_V is V_V, "runtime.model.Verdict must be canonical (models.verdicts)"


class TestForbiddenEnumReferences:
    """Scan source code for forbidden enum values that have crashed the kernel."""

    @pytest.mark.parametrize(
        "module_path",
        [
            "arifosmcp.runtime.tools_internal",
            "arifosmcp.runtime.verdict_wrapper",
            "arifosmcp.runtime.orchestrator",
            "arifosmcp.runtime.output_formatter",
            "arifosmcp.tools.architect",
        ],
    )
    def test_module_imports_clean(self, module_path: str):
        """Each previously-broken module must import without AttributeError."""
        __import__(module_path)

    def test_no_runtime_status_failure_anywhere(self):
        import os
        import subprocess
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        result = subprocess.run(
            [
                "grep",
                "-rn",
                "--exclude=test_runtime_status_enums.py",
                "--exclude-dir=__pycache__",
                "RuntimeStatus\\.FAILURE",
                "arifosmcp/",
                "tests/",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, (
            f"RuntimeStatus.FAILURE found in source:\n{result.stdout}"
        )

    def test_no_verdict_degraded_in_kernel_modules(self):
        import os
        import subprocess
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        result = subprocess.run(
            [
                "grep",
                "-rn",
                "--exclude-dir=__pycache__",
                "Verdict\\.DEGRADED",
                "arifosmcp/",
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        # Filter out FullVerdict.DEGRADED / AttestationVerdict.DEGRADED — those
        # are different (canonical) enums that DO have DEGRADED.
        offenders = [
            line for line in result.stdout.splitlines()
            if "Verdict.DEGRADED" in line
            and "FullVerdict" not in line
            and "AttestationVerdict" not in line
        ]
        assert not offenders, (
            f"Verdict.DEGRADED (canonical Verdict has no DEGRADED) found:\n"
            + "\n".join(offenders)
        )
