#!/usr/bin/env python3
"""
check_track_alignment_v49.py - Constitutional Alignment Verification (v49)

Purpose:
    Verify that the Single Body (arifos/) is properly aligned with:
    - Track A (000_THEORY/) - Constitutional Authority
    - Track B (arifos/spec/) - Specification Authority

Authority: Constitutional Alignment Protocol v49.0
Status: 🔵 PRODUCTION READY
"""

import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List


class AlignmentStatus(Enum):
    """Alignment status levels."""
    ALIGNED = "ALIGNED"
    MISALIGNED = "MISALIGNED"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


@dataclass
class AlignmentIssue:
    """Represents a specific alignment issue."""
    track: str
    component: str
    issue_type: str
    current_state: str
    required_state: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    remediation: str


@dataclass
class AlignmentReport:
    """Complete alignment analysis report."""
    overall_status: AlignmentStatus
    track_a_status: AlignmentStatus
    track_b_status: AlignmentStatus
    track_c_status: AlignmentStatus
    issues: List[AlignmentIssue]
    recommendations: List[str]
    alignment_percentage: float


class TrackAlignmentChecker:
    """Comprehensive alignment checker for arifOS v49."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.issues: List[AlignmentIssue] = []
        self.recommendations: List[str] = []

        # Define paths for v49 Single Body
        self.track_a_path = repo_root / "000_THEORY"
        self.track_b_path = repo_root / "arifos" / "spec"
        self.track_c_path = repo_root / "arifos"

    def check_track_a_integrity(self) -> AlignmentStatus:
        """Verify Track A (Canon) integrity."""
        print("🔍 Checking Track A (Canon) integrity...")

        # Check master law and architecture exists
        required_files = ["000_LAW.md", "000_ARCHITECTURE.md", "001_AGENTS.md"]
        for req_file in required_files:
            file_path = self.track_a_path / req_file
            if not file_path.exists():
                self.issues.append(AlignmentIssue(
                    track="A",
                    component=req_file,
                    issue_type="MISSING_FILE",
                    current_state="File not found",
                    required_state=f"000_THEORY/{req_file}",
                    severity="CRITICAL",
                    remediation=f"Restore 000_THEORY/{req_file}"
                ))
                return AlignmentStatus.MISSING

        # Check aCLIP structure (000-999) stages in docs or THEORY
        required_stages = [
            "111_AGI.md", "333_ATLAS.md", "555_ASI.md", "777_EUREKA.md",
            "888_APEX.md", "999_AAA_HUMAN.md"
        ]

        missing_stages = []
        for stage in required_stages:
            stage_path = self.track_a_path / stage
            if not stage_path.exists():
                missing_stages.append(stage)

        if missing_stages:
            self.issues.append(AlignmentIssue(
                track="A",
                component="Pipeline Documentation",
                issue_type="INCOMPLETE_STRUCTURE",
                current_state=f"Missing stage docs: {missing_stages}",
                required_state="All major pipeline docs present in 000_THEORY",
                severity="HIGH",
                remediation="Ensure all metabolic stage documentation is migrated to 000_THEORY"
            ))
            return AlignmentStatus.MISALIGNED

        print("✅ Track A integrity verified")
        return AlignmentStatus.ALIGNED

    def check_track_b_alignment(self) -> AlignmentStatus:
        """Verify Track B (Specifications) alignment."""
        print("🔍 Checking Track B (Specifications) alignment...")

        # v49 uses arifos/core/spec/ for schema validation and manifests
        required_files = ["manifest_verifier.py", "schema_validator.py"]
        for req_file in required_files:
            file_path = self.repo_root / "arifos" / "core" / "spec" / req_file
            if not file_path.exists():
                self.issues.append(AlignmentIssue(
                    track="B",
                    component=f"Spec Component: {req_file}",
                    issue_type="MISSING_FILE",
                    current_state="File not found",
                    required_state=f"arifos/core/spec/{req_file}",
                    severity="CRITICAL",
                    remediation=f"Ensure arifos/core/spec contains {req_file}"
                ))
                return AlignmentStatus.MISSING

        print("✅ Track B specs verified")
        return AlignmentStatus.ALIGNED

    def check_track_c_alignment(self) -> AlignmentStatus:
        """Verify Track C (arifos/) alignment with Tracks A/B."""
        print("🔍 Checking Track C (Implementation) alignment...")

        status = AlignmentStatus.ALIGNED

        # Check version references (v49)
        status = self._check_version_references() or status

        # Check unified package structure
        status = self._check_unified_structure() or status

        return status

    def _check_version_references(self) -> AlignmentStatus:
        """Check version references throughout arifos/."""
        print("  📋 Checking version references...")

        # Files to check for version references should use v49
        files_to_check = [
            self.repo_root / "pyproject.toml",
            self.track_c_path / "__init__.py"
        ]

        version_issues = []
        for file_path in files_to_check:
            if not file_path.exists():
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if "49" not in content and "v49" not in content:
                    version_issues.append(file_path.name)
            except Exception:
                pass

        if version_issues:
            self.issues.append(AlignmentIssue(
                track="C",
                component="Version References",
                issue_type="VERSION_DRIFT",
                current_state=f"Missing v49 refs in: {version_issues}",
                required_state="Version 49 should be active",
                severity="MEDIUM",
                remediation="Update version references to v49"
            ))
            return AlignmentStatus.MISALIGNED

        print("    ✅ Version references aligned")
        return AlignmentStatus.ALIGNED

    def _check_unified_structure(self) -> AlignmentStatus:
        """Check for legacy arifos_core references that should be arifos."""
        print("  📋 Checking for legacy arifos_core references...")

        legacy_pattern = re.compile(r'arifos_core')
        found_legacy = []

        # Scan arifos/ directory for legacy imports
        for py_file in self.track_c_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    if legacy_pattern.search(f.read()):
                        found_legacy.append(str(py_file.relative_to(self.repo_root)))
            except Exception:
                pass

        if found_legacy:
            self.issues.append(AlignmentIssue(
                track="C",
                component="Package Refactoring",
                issue_type="LEGACY_REFERENCE",
                current_state=f"Found 'arifos_core' in: {found_legacy[:5]}...",
                required_state="All references should use 'arifos'",
                severity="HIGH",
                remediation="Refactor arifos_core to arifos in implementation files"
            ))
            return AlignmentStatus.MISALIGNED

        print("    ✅ Single Body structure verified")
        return AlignmentStatus.ALIGNED

    def generate_alignment_percentage(self) -> float:
        """Calculate overall alignment percentage."""
        total_checks = 4  # Track A Integrity, Track B Specs, Version Refs, Unified Structure
        failed_checks = len([i for i in self.issues if i.severity in ["CRITICAL", "HIGH"]])
        aligned_components = max(0, total_checks - failed_checks)
        return (aligned_components / total_checks) * 100

    def generate_recommendations(self) -> List[str]:
        """Generate alignment recommendations."""
        recommendations = []

        critical_issues = [i for i in self.issues if i.severity == "CRITICAL"]
        if critical_issues:
            recommendations.append("🚨 ADDRESS CRITICAL ISSUES FIRST:")
            for issue in critical_issues:
                recommendations.append(f"   - {issue.component}: {issue.remediation}")

        high_issues = [i for i in self.issues if i.severity == "HIGH"]
        if high_issues:
            recommendations.append("⚠️  HIGH PRIORITY ALIGNMENT TASKS:")
            for issue in high_issues:
                recommendations.append(f"   - {issue.component}: {issue.remediation}")

        if not critical_issues and not high_issues:
            recommendations.append("✅ No critical alignment issues found")

        return recommendations

    def run_alignment_check(self) -> AlignmentReport:
        """Run complete alignment check across all tracks."""
        print("🚀 Starting Track A/B/C Alignment Verification v49.0")
        print("=" * 60)

        track_a_status = self.check_track_a_integrity()
        track_b_status = self.check_track_b_alignment()
        track_c_status = self.check_track_c_alignment()

        if track_a_status == AlignmentStatus.ALIGNED and track_b_status == AlignmentStatus.ALIGNED and track_c_status == AlignmentStatus.ALIGNED:
            overall_status = AlignmentStatus.ALIGNED
        elif any(status == AlignmentStatus.MISSING for status in [track_a_status, track_b_status, track_c_status]):
            overall_status = AlignmentStatus.MISSING
        else:
            overall_status = AlignmentStatus.MISALIGNED

        alignment_percentage = self.generate_alignment_percentage()
        self.recommendations = self.generate_recommendations()

        report = AlignmentReport(
            overall_status=overall_status,
            track_a_status=track_a_status,
            track_b_status=track_b_status,
            track_c_status=track_c_status,
            issues=self.issues,
            recommendations=self.recommendations,
            alignment_percentage=alignment_percentage
        )

        print("\n📊 ALIGNMENT REPORT SUMMARY")
        print("=" * 60)
        print(f"Overall Status: {overall_status.value}")
        print(f"Track A (Canon): {track_a_status.value}")
        print(f"Track B (Specs): {track_b_status.value}")
        print(f"Track C (Code): {track_c_status.value}")
        print(f"Alignment Percentage: {alignment_percentage:.1f}%")

        return report


def main():
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent

    checker = TrackAlignmentChecker(repo_root)
    report = checker.run_alignment_check()

    if report.overall_status == AlignmentStatus.ALIGNED:
        sys.exit(0)
    elif any(status == AlignmentStatus.MISSING for status in [report.track_a_status, report.track_b_status, report.track_c_status]):
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
