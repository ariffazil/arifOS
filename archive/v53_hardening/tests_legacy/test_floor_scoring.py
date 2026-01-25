"""
test_floor_scoring.py — Tests for Floor Scoring Engine

Verifies:
- F1 Amanah detection for dangerous operations
- F2 Truth threshold checking
- Verdict computation logic
- Ledger analysis parsing
"""

import pytest


class TestFloorScorer:
    """Test suite for FloorScorer class."""

    def test_import(self):
        """Verify module imports correctly (v46 Trinity Orchestrator)."""
        from arifos_core.enforcement.trinity_orchestrator import (
            FLOOR_SCORER,
            TrinityOrchestrator,
            grade_text,
            is_safe,
        )
        assert TrinityOrchestrator is not None
        assert FLOOR_SCORER is not None

    def test_safe_text_seals(self):
        """Safe conversational text should SEAL."""
        from arifos_core.enforcement.trinity_orchestrator import grade_text

        result = grade_text("Hello, how can I help you today?")
        assert result.verdict == "SEAL"
        assert len(result.failures) == 0

    def test_dangerous_text_voids(self):
        """Dangerous operations should VOID (v46: F1 Amanah)."""
        from arifos_core.enforcement.trinity_orchestrator import grade_text

        # File deletion pattern
        result = grade_text("I will now execute: rm -rf /home/user")
        assert result.verdict == "VOID"
        assert "F1: Amanah" in result.failures

    def test_is_safe_helper(self):
        """Quick is_safe check works."""
        from arifos_core.enforcement.trinity_orchestrator import is_safe

        assert is_safe("What is 2 + 2?") is True
        assert is_safe("sudo rm -rf /*") is False

    def test_floor_results_populated(self):
        """All 9 floors should have results."""
        from arifos_core.enforcement.trinity_orchestrator import grade_text

        result = grade_text("Test message")
        assert len(result.floors) == 9
        for i in range(1, 10):
            assert f"F{i}" in result.floors

    def test_claim_profile_attached(self):
        """Claim profile should be attached to result."""
        from arifos_core.enforcement.trinity_orchestrator import grade_text

        result = grade_text("The capital of France is Paris.")
        assert result.claim_profile is not None
        assert "claim_count" in result.claim_profile

    def test_truth_failure_with_low_score(self):
        """Low truth score should fail F2 (v46: Truth in AGI)."""
        from arifos_core.enforcement.trinity_orchestrator import grade_text

        result = grade_text(
            "Some text",
            metrics={"truth": 0.5},
        )
        assert "F2: Truth" in result.failures
        assert result.verdict in ["VOID", "PARTIAL"]

    def test_peace_squared_failure(self):
        """Low peace score should fail F3 (v46: Peace² in ASI)."""
        from arifos_core.enforcement.trinity_orchestrator import grade_text

        result = grade_text(
            "Some text",
            metrics={"peace_squared": 0.5},
        )
        assert "F3: Peace²" in result.failures

    def test_high_stakes_tri_witness(self):
        """High stakes should enforce tri-witness (v46: F8 in APEX)."""
        from arifos_core.enforcement.trinity_orchestrator import grade_text

        # Without high_stakes, low tri_witness passes
        result1 = grade_text("Test", metrics={"tri_witness": 0.8})
        assert "F8: Tri-Witness" not in result1.failures

        # With high_stakes, low tri_witness fails
        result2 = grade_text("Test", high_stakes=True, metrics={"tri_witness": 0.8})
        assert "F8: Tri-Witness" in result2.failures


class TestLedgerAnalysis:
    """Test suite for ledger analysis."""

    def test_ledger_module_imports(self):
        """Verify analyze_ledger module structure."""
        import sys
        from pathlib import Path

        # Add scripts to path
        scripts_path = Path(__file__).parent.parent / "scripts"
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))

        from analyze_ledger import (analyze_entries, extract_floor_failures,
                                    load_ledger_entries)
        assert load_ledger_entries is not None
        assert extract_floor_failures is not None

    def test_extract_failures_from_metrics(self):
        """Floor failures extracted from metrics dict."""
        import sys
        from pathlib import Path

        scripts_path = Path(__file__).parent.parent / "scripts"
        if str(scripts_path) not in sys.path:
            sys.path.insert(0, str(scripts_path))

        from analyze_ledger import extract_floor_failures

        entry = {
            "metrics": {
                "amanah": False,
                "truth": 0.5,
            }
        }
        failures = extract_floor_failures(entry)
        assert "F1: Amanah" in failures
        assert "F2: Truth" in failures


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
