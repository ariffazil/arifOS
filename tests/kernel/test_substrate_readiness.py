"""
test_substrate_readiness — Tests for AGI Substrate Readiness Gate.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import pytest
from arifosmcp.kernel.substrate_readiness import (
    assess_substrate_readiness,
    ReadinessCheck,
    SubstrateReadinessReport,
)


class TestSubstrateReadiness:
    """Substrate readiness gate tests."""

    def test_assess_returns_report(self):
        """assess_substrate_readiness must return a SubstrateReadinessReport."""
        report = assess_substrate_readiness()
        assert isinstance(report, SubstrateReadinessReport)

    def test_report_has_checks(self):
        """Report must contain at least one check."""
        report = assess_substrate_readiness()
        assert len(report.checks) >= 5, f"Expected >=5 checks, got {len(report.checks)}"

    def test_report_counts_sum(self):
        """passed + failed must equal total checks."""
        report = assess_substrate_readiness()
        assert report.passed + report.failed == len(report.checks), (
            f"Count mismatch: {report.passed} + {report.failed} != {len(report.checks)}"
        )

    def test_overall_verdict_is_valid(self):
        """Overall verdict must be PASS, HOLD, or FAIL."""
        report = assess_substrate_readiness()
        assert report.overall_verdict in ("PASS", "HOLD", "FAIL")

    def test_critical_failure_causes_fail(self):
        """If critical_failures > 0, verdict must be FAIL."""
        report = assess_substrate_readiness()
        if report.critical_failures > 0:
            assert report.overall_verdict == "FAIL", (
                f"Critical failures ({report.critical_failures}) but verdict={report.overall_verdict}"
            )

    def test_all_checks_have_names(self):
        """Every check must have a non-empty name."""
        report = assess_substrate_readiness()
        for check in report.checks:
            assert check.name, f"Check missing name: {check}"

    def test_all_checks_have_descriptions(self):
        """Every check must have a non-empty description."""
        report = assess_substrate_readiness()
        for check in report.checks:
            assert check.description, f"Check {check.name} missing description"

    def test_public_surface_check_present(self):
        """Must include the public_surface_exact check."""
        report = assess_substrate_readiness()
        names = {c.name for c in report.checks}
        assert "public_surface_exact" in names, f"Missing public_surface_exact check: {names}"

    def test_forbidden_tools_check_present(self):
        """Must include the forbidden_tools_blocked check."""
        report = assess_substrate_readiness()
        names = {c.name for c in report.checks}
        assert "forbidden_tools_blocked" in names, f"Missing forbidden_tools_blocked check: {names}"

    def test_capability_graph_check_present(self):
        """Must include the capability_graph_core check."""
        report = assess_substrate_readiness()
        names = {c.name for c in report.checks}
        assert "capability_graph_core" in names, f"Missing capability_graph_core check: {names}"

    def test_to_dict_serializable(self):
        """to_dict must produce JSON-serializable dict."""
        report = assess_substrate_readiness()
        d = report.to_dict()
        assert isinstance(d, dict)
        assert "substrate_gate" in d
        assert "checks" in d
        assert "passed" in d
        assert "failed" in d
        # Must be JSON-serializable
        import json

        json.dumps(d)

    def test_to_json_valid(self):
        """to_json must produce valid JSON string."""
        report = assess_substrate_readiness()
        output = report.to_json()
        import json

        parsed = json.loads(output)
        assert "substrate_gate" in parsed

    def test_readiness_check_dataclass(self):
        """ReadinessCheck must be a frozen dataclass."""
        check = ReadinessCheck(
            name="test",
            description="test check",
            passed=True,
        )
        assert check.name == "test"
        assert check.passed is True
        with pytest.raises(Exception):
            check.passed = False  # frozen
