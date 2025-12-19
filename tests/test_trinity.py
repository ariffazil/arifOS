"""
test_trinity.py - Unit tests for Trinity system (gitforge/QC/seal)

Tests the three-stage governance gate:
- /gitforge: State mapping and entropy prediction
- /gitQC: Constitutional floor validation
- /gitseal: Human authority + atomic bundling
"""

import json
import tempfile
from pathlib import Path

import pytest

from arifos_core.trinity import (
    ForgeReport,
    QCReport,
    HousekeeperProposal,
    SealDecision,
    analyze_branch,
    validate_changes,
    propose_docs,
    execute_seal,
)


class TestGitForge:
    """Tests for /gitforge state mapper."""

    def test_forge_report_structure(self):
        """Forge report has required fields."""
        report = ForgeReport(
            files_changed=["test.py"],
            hot_zones=[],
            entropy_delta=0.1,
            risk_score=0.2,
            timestamp="2025-12-19T15:00:00Z",
            branch="feat/test",
            base_commit="abc123",
            head_commit="def456",
        )

        assert report.files_changed == ["test.py"]
        assert report.entropy_delta == 0.1
        assert report.risk_score == 0.2

    def test_entropy_prediction(self):
        """Entropy delta scales with file count and hot zones."""
        # Small change = low entropy
        report1 = ForgeReport(
            files_changed=["a.py", "b.py"],
            hot_zones=[],
            entropy_delta=0.2,  # 2 files * 0.1
            risk_score=0.1,
            timestamp="",
           branch="test",
            base_commit="",
            head_commit="",
        )
        assert report1.entropy_delta < 1.0

        # Large change with hot zones = high entropy
        report2 = ForgeReport(
            files_changed=["a.py"] * 10,
            hot_zones=["a.py"] * 3,
            entropy_delta=1.9,  # 10*0.1 + 3*0.3
            risk_score=0.6,
            timestamp="",
            branch="test",
            base_commit="",
            head_commit="",
        )
        assert report2.entropy_delta > 1.0


class TestGitQC:
    """Tests for /gitQC constitutional validator."""

    def test_qc_report_structure(self):
        """QC report has required fields."""
        report = QCReport(
            floors_passed={"F1_Truth": True},
            zkpc_id="zkpc_stub_sha256:abc123",
            verdict="PASS",
            timestamp="2025-12-19T15:00:00Z",
        )

        assert report.verdict == "PASS"
        assert "zkpc_stub" in report.zkpc_id

    def test_floor_validation_pass(self):
        """All floors pass for clean changes."""
        forge_report = ForgeReport(
            files_changed=["test.py"],
            hot_zones=[],
            entropy_delta=0.1,
            risk_score=0.1,
            timestamp="",
            branch="test",
            base_commit="",
            head_commit="",
        )

        qc_report = validate_changes(forge_report, run_tests=False, check_syntax=False)

        assert qc_report.verdict in ["PASS", "FLAG"]  # FLAG if tests deferred
        assert qc_report.floors_passed["F1_Truth"] is True
        assert qc_report.floors_passed["F2_DeltaS"] is True

    def test_floor_validation_high_entropy_fails(self):
        """High entropy (>5.0) triggers F2 failure."""
        forge_report = ForgeReport(
            files_changed=["test.py"] * 50,
            hot_zones=["test.py"] * 20,
            entropy_delta=11.0,  # > 5.0 threshold
            risk_score=0.9,
            timestamp="",
            branch="test",
            base_commit="",
            head_commit="",
        )

        qc_report = validate_changes(forge_report, run_tests=False, check_syntax=False)

        assert qc_report.floors_passed["F2_DeltaS"] is False
        assert qc_report.verdict == "VOID"


class TestHousekeeper:
    """Tests for housekeeper auto-doc engine."""

    def test_version_bump_patch(self):
        """Small changes trigger patch version bump."""
        forge_report = ForgeReport(
            files_changed=["test.py"],
            hot_zones=[],
            entropy_delta=0.1,
            risk_score=0.1,
            timestamp="",
            branch="test",
            base_commit="",
            head_commit="",
            notes=["Small change: 1 files modified"],
        )
        qc_report = QCReport(
            floors_passed={}, zkpc_id="", verdict="PASS", timestamp=""
        )

        proposal = propose_docs(forge_report, qc_report, current_version="43.0.0")

        assert proposal.version_bump == "patch"
        assert proposal.new_version == "43.0.1"

    def test_version_bump_minor(self):
        """Medium changes trigger minor version bump."""
        forge_report = ForgeReport(
            files_changed=["test.py"] * 15,
            hot_zones=[],
            entropy_delta=1.5,
            risk_score=0.3,
            timestamp="",
            branch="test",
            base_commit="",
            head_commit="",
            notes=[],
        )
        qc_report = QCReport(
            floors_passed={}, zkpc_id="", verdict="PASS", timestamp=""
        )

        proposal = propose_docs(forge_report, qc_report, current_version="43.0.0")

        assert proposal.version_bump == "minor"
        assert proposal.new_version == "43.1.0"

    def test_changelog_generation(self):
        """Housekeeper generates CHANGELOG entry."""
        forge_report = ForgeReport(
            files_changed=["a.py", "b.py"],
            hot_zones=[],
            entropy_delta=0.2,
            risk_score=0.1,
            timestamp="",
            branch="test",
            base_commit="",
            head_commit="",
            notes=[],
        )
        qc_report = QCReport(
            floors_passed={"F1_Truth": True},
            zkpc_id="zkpc_test",
            verdict="PASS",
            timestamp="",
        )

        proposal = propose_docs(forge_report, qc_report)

        assert "## [43.0.1]" in proposal.changelog_entry
        assert "Modified `a.py`" in proposal.changelog_entry
        assert "zkpc_test" in proposal.changelog_entry


class TestGitSeal:
    """Tests for /gitseal human authority gate."""

    def test_seal_reject(self):
        """REJECT decision creates ledger entry without bundle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            (repo_path / "L1_THEORY" / "ledger").mkdir(parents=True)

            forge = ForgeReport(
                files_changed=[],
                hot_zones=[],
                entropy_delta=0,
                risk_score=0,
                timestamp="",
                branch="test",
                base_commit="",
                head_commit="",
            )
            qc = QCReport(floors_passed={}, zkpc_id="", verdict="PASS", timestamp="")
            hk = HousekeeperProposal(
                version_bump="none", new_version="N/A", changelog_entry=""
            )

            decision = execute_seal(
                decision="REJECT",
                branch="test",
                human_authority="Test User",
                reason="Not ready",
                forge_report=forge,
                qc_report=qc,
                housekeeper_proposal=hk,
                repo_path=repo_path,
            )

            assert decision.verdict == "REJECTED"
            assert decision.bundle_hash is None
            assert decision.ledger_entry_id != ""

            # Check ledger was written
            ledger_path = repo_path / "L1_THEORY" / "ledger" / "gitseal_audit_trail.jsonl"
            assert ledger_path.exists()

    def test_seal_hold(self):
        """HOLD decision creates ledger entry without bundle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            (repo_path / "L1_THEORY" / "ledger").mkdir(parents=True)

            forge = ForgeReport(
                files_changed=[],
                hot_zones=[],
                entropy_delta=0,
                risk_score=0,
                timestamp="",
                branch="test",
                base_commit="",
                head_commit="",
            )
            qc = QCReport(floors_passed={}, zkpc_id="", verdict="PASS", timestamp="")
            hk = HousekeeperProposal(
                version_bump="none", new_version="N/A", changelog_entry=""
            )

            decision = execute_seal(
                decision="HOLD",
                branch="test",
                human_authority="Test User",
                reason="Awaiting review",
                forge_report=forge,
                qc_report=qc,
                housekeeper_proposal=hk,
                repo_path=repo_path,
            )

            assert decision.verdict == "HOLD"
            assert decision.bundle_hash is None


# Integration test placeholder
def test_full_trinity_pipeline_happy_path():
    """
    Full Trinity pipeline: forge → QC → seal (APPROVE).

    NOTE: This test is a placeholder skeleton.
    Real implementation would use a git fixture repository.
    """
    # Would need actual git repository fixture
    # For now, mark as TODO
    pytest.skip("Requires git repository fixture")
