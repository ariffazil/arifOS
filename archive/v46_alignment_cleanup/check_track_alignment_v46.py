#!/usr/bin/env python3
"""
check_track_alignment_v46.py - Constitutional Alignment Verification

Purpose:
    Verify that arifos_core (Track C) is properly aligned with:
    - Track A (L1_THEORY/canon/) - Constitutional Authority
    - Track B (L2_PROTOCOLS/v46/) - Specification Authority

This script performs comprehensive alignment checking across all three tracks
and identifies specific gaps that need to be addressed.

Authority: Constitutional Alignment Protocol v46.0
Status: 🔵 PHOENIX-72 COOLING
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


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
    """Comprehensive alignment checker for arifOS v46."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.issues: List[AlignmentIssue] = []
        self.recommendations: List[str] = []
        
        # Define paths
        self.track_a_path = repo_root / "L1_THEORY" / "canon"
        self.track_b_path = repo_root / "L2_PROTOCOLS" / "v46"
        self.track_c_path = repo_root / "arifos_core"
        
    def check_track_a_integrity(self) -> AlignmentStatus:
        """Verify Track A (Canon) integrity."""
        print("🔍 Checking Track A (Canon) integrity...")
        
        # Check master index exists
        master_index = self.track_a_path / "000_MASTER_INDEX_v46.md"
        if not master_index.exists():
            self.issues.append(AlignmentIssue(
                track="A",
                component="Master Index",
                issue_type="MISSING_FILE",
                current_state="File not found",
                required_state="L1_THEORY/canon/000_MASTER_INDEX_v46.md",
                severity="CRITICAL",
                remediation="Ensure v46 canon is properly installed"
            ))
            return AlignmentStatus.MISSING
            
        # Check pipeline structure (000-999)
        required_stages = [
            "000_foundation", "111_sense", "222_reflect", "333_atlas",
            "444_align", "555_empathize", "666_bridge", "777_eureka",
            "888_compass", "999_vault"
        ]
        
        missing_stages = []
        for stage in required_stages:
            stage_path = self.track_a_path / stage
            if not stage_path.exists():
                missing_stages.append(stage)
                
        if missing_stages:
            self.issues.append(AlignmentIssue(
                track="A",
                component="Pipeline Structure",
                issue_type="INCOMPLETE_STRUCTURE",
                current_state=f"Missing stages: {missing_stages}",
                required_state="All 000-999 stages present",
                severity="HIGH",
                remediation="Complete v46 canon installation"
            ))
            return AlignmentStatus.MISALIGNED
            
        print("✅ Track A integrity verified")
        return AlignmentStatus.ALIGNED
        
    def check_track_b_manifest(self) -> AlignmentStatus:
        """Verify Track B (Specifications) manifest."""
        print("🔍 Checking Track B (Specifications) manifest...")
        
        manifest_path = self.track_b_path / "MANIFEST.sha256.json"
        if not manifest_path.exists():
            self.issues.append(AlignmentIssue(
                track="B",
                component="Cryptographic Manifest",
                issue_type="MISSING_FILE",
                current_state="MANIFEST.sha256.json not found",
                required_state="L2_PROTOCOLS/v46/MANIFEST.sha256.json",
                severity="CRITICAL",
                remediation="Generate v46 manifest or install Track B"
            ))
            return AlignmentStatus.MISSING
            
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                
            # Verify version
            version = manifest.get("version", "unknown")
            if not version.startswith("v46"):
                self.issues.append(AlignmentIssue(
                    track="B",
                    component="Manifest Version",
                    issue_type="VERSION_MISMATCH",
                    current_state=f"Version: {version}",
                    required_state="v46.x",
                    severity="HIGH",
                    remediation="Update to v46.1 manifest"
                ))
                return AlignmentStatus.MISALIGNED
                
            # Check required specification files
            required_specs = [
                "L2_PROTOCOLS/v46/000_foundation/constitutional_floors.json",
                "L2_PROTOCOLS/v46/333_atlas/agi_core.json",
                "L2_PROTOCOLS/v46/555_empathize/empathy_floor.json",
                "L2_PROTOCOLS/v46/888_compass/waw_prompt_floors.json",
                "L2_PROTOCOLS/v46/governance/aaa_trinity.json"
            ]
            
            files = manifest.get("files", {})
            missing_files = []
            for spec_file in required_specs:
                if spec_file not in files:
                    missing_files.append(spec_file)
                    
            if missing_files:
                self.issues.append(AlignmentIssue(
                    track="B",
                    component="Specification Files",
                    issue_type="MISSING_FILES",
                    current_state=f"Missing: {missing_files}",
                    required_state="All v46 specifications present",
                    severity="HIGH",
                    remediation="Complete v46 specification installation"
                ))
                return AlignmentStatus.MISALIGNED
                
        except json.JSONDecodeError:
            self.issues.append(AlignmentIssue(
                track="B",
                component="Manifest Format",
                issue_type="INVALID_FORMAT",
                current_state="Invalid JSON format",
                required_state="Valid JSON manifest",
                severity="CRITICAL",
                remediation="Regenerate manifest file"
            ))
            return AlignmentStatus.MISALIGNED
            
        print("✅ Track B manifest verified")
        return AlignmentStatus.ALIGNED
        
    def check_track_c_alignment(self) -> AlignmentStatus:
        """Verify Track C (arifos_core) alignment with Tracks A/B."""
        print("🔍 Checking Track C (Implementation) alignment...")
        
        status = AlignmentStatus.ALIGNED
        
        # Check spec loading paths
        status = self._check_spec_loading_paths() or status
        
        # Check version references
        status = self._check_version_references() or status
        
        # Check hypervisor integration
        status = self._check_hypervisor_integration() or status
        
        # Check engine assignment
        status = self._check_engine_assignment() or status
        
        # Check pipeline mapping
        status = self._check_pipeline_mapping() or status
        
        return status
        
    def _check_spec_loading_paths(self) -> AlignmentStatus:
        """Check if arifos_core loads from correct specifications."""
        print("  📋 Checking specification loading paths...")
        
        # Check metrics.py for spec loading
        metrics_file = self.track_c_path / "enforcement" / "metrics.py"
        if not metrics_file.exists():
            self.issues.append(AlignmentIssue(
                track="C",
                component="Metrics Module",
                issue_type="MISSING_FILE",
                current_state="metrics.py not found",
                required_state="arifos_core/enforcement/metrics.py",
                severity="CRITICAL",
                remediation="Restore metrics.py file"
            ))
            return AlignmentStatus.MISSING
            
        try:
            with open(metrics_file, 'r') as f:
                content = f.read()
                
            # Check for v46 spec paths
            if "L2_PROTOCOLS/v46" not in content:
                self.issues.append(AlignmentIssue(
                    track="C",
                    component="Spec Loading",
                    issue_type="PATH_MISMATCH",
                    current_state="Loading from legacy paths",
                    required_state="Load from L2_PROTOCOLS/v46/",
                    severity="HIGH",
                    remediation="Update _load_floors_spec_unified() to use v46 paths"
                ))
                return AlignmentStatus.MISALIGNED
                
            # Check for v46 manifest verification
            if "v46/MANIFEST.sha256.json" not in content:
                self.issues.append(AlignmentIssue(
                    track="C",
                    component="Manifest Verification",
                    issue_type="MISSING_VERIFICATION",
                    current_state="No v46 manifest verification",
                    required_state="Verify v46.1 cryptographic manifest",
                    severity="HIGH",
                    remediation="Add v46 manifest verification to spec loader"
                ))
                return AlignmentStatus.MISALIGNED
                
        except Exception as e:
            self.issues.append(AlignmentIssue(
                track="C",
                component="Metrics Analysis",
                issue_type="ANALYSIS_ERROR",
                current_state=f"Error reading metrics.py: {e}",
                required_state="Readable metrics.py file",
                severity="MEDIUM",
                remediation="Check file permissions and content"
            ))
            return AlignmentStatus.MISALIGNED
            
        print("    ✅ Specification paths aligned")
        return AlignmentStatus.ALIGNED
        
    def _check_version_references(self) -> AlignmentStatus:
        """Check version references throughout arifos_core."""
        print("  📋 Checking version references...")
        
        # Files to check for version references
        critical_files = [
            "system/pipeline.py",
            "system/apex_prime.py", 
            "enforcement/metrics.py",
            "__init__.py"
        ]
        
        version_issues = []
        
        for file_path in critical_files:
            full_path = self.track_c_path / file_path
            if not full_path.exists():
                continue
                
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
                    
                # Check for v45 references that should be v46
                if "v45" in content and "v46" not in content:
                    version_issues.append(file_path)
                    
            except Exception as e:
                self.issues.append(AlignmentIssue(
                    track="C",
                    component=f"File {file_path}",
                    issue_type="READ_ERROR",
                    current_state=f"Cannot read: {e}",
                    required_state="Readable file",
                    severity="LOW",
                    remediation=f"Check {file_path}"
                ))
                
        if version_issues:
            self.issues.append(AlignmentIssue(
                track="C",
                component="Version References",
                issue_type="VERSION_DRIFT",
                current_state=f"v45 references in: {version_issues}",
                required_state="All references updated to v46",
                severity="MEDIUM",
                remediation="Update version references to v46.0"
            ))
            return AlignmentStatus.MISALIGNED
            
        print("    ✅ Version references aligned")
        return AlignmentStatus.ALIGNED
        
    def _check_hypervisor_integration(self) -> AlignmentStatus:
        """Check F10-F12 hypervisor floor integration."""
        print("  📋 Checking hypervisor integration...")
        
        # Check if hypervisor guards exist
        guards_path = self.track_c_path / "guards"
        required_guards = [
            "ontology_guard.py",      # F10
            "command_auth_guard.py",  # F11  
            "injection_guard.py"      # F12
        ]
        
        missing_guards = []
        for guard in required_guards:
            guard_path = guards_path / guard
            if not guard_path.exists():
                missing_guards.append(guard)
                
        if missing_guards:
            self.issues.append(AlignmentIssue(
                track="C",
                component="Hypervisor Guards",
                issue_type="MISSING_IMPLEMENTATION",
                current_state=f"Missing guards: {missing_guards}",
                required_state="All F10-F12 guards implemented",
                severity="HIGH",
                remediation="Implement missing hypervisor guards"
            ))
            return AlignmentStatus.MISSING
            
        # Check pipeline integration
        pipeline_file = self.track_c_path / "system" / "pipeline.py"
        if pipeline_file.exists():
            try:
                with open(pipeline_file, 'r') as f:
                    content = f.read()
                    
                # Check for stage_000_hypervisor or similar
                if "stage_000" not in content or "hypervisor" not in content.lower():
                    self.issues.append(AlignmentIssue(
                        track="C",
                        component="Hypervisor Integration",
                        issue_type="MISSING_INTEGRATION",
                        current_state="No stage_000_hypervisor found",
                        required_state="F10-F12 integrated in stage 000",
                        severity="HIGH",
                        remediation="Add hypervisor stage to pipeline"
                    ))
                    return AlignmentStatus.MISALIGNED
                    
            except Exception as e:
                self.issues.append(AlignmentIssue(
                    track="C",
                    component="Pipeline Analysis",
                    issue_type="ANALYSIS_ERROR",
                    current_state=f"Error analyzing pipeline: {e}",
                    required_state="Readable pipeline.py",
                    severity="MEDIUM",
                    remediation="Check pipeline file"
                ))
                
        print("    ✅ Hypervisor integration verified")
        return AlignmentStatus.ALIGNED
        
    def _check_engine_assignment(self) -> AlignmentStatus:
        """Check ΔΩΨ engine assignment alignment."""
        print("  📋 Checking engine assignment...")
        
        # Check if engine assignment exists
        engine_assignment_found = False
        
        # Look in enforcement/stages or similar
        stages_path = self.track_c_path / "enforcement" / "stages"
        if stages_path.exists():
            for py_file in stages_path.glob("*.py"):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        
                    if "ENGINE_OWNERSHIP" in content or "AGI" in content and "ASI" in content:
                        engine_assignment_found = True
                        break
                        
                except Exception:
                    continue
                    
        # Check in main files
        if not engine_assignment_found:
            critical_files = ["system/pipeline.py", "system/apex_prime.py"]
            for file_path in critical_files:
                full_path = self.track_c_path / file_path
                if full_path.exists():
                    try:
                        with open(full_path, 'r') as f:
                            content = f.read()
                            
                        if "ENGINE_OWNERSHIP" in content or "STAGE_ENGINE_MAP" in content:
                            engine_assignment_found = True
                            break
                            
                    except Exception:
                        continue
                        
        if not engine_assignment_found:
            self.issues.append(AlignmentIssue(
                track="C",
                component="Engine Assignment",
                issue_type="MISSING_IMPLEMENTATION",
                current_state="No engine ownership mapping found",
                required_state="ΔΩΨ engine assignment implemented",
                severity="HIGH",
                remediation="Implement ENGINE_OWNERSHIP mapping"
            ))
            return AlignmentStatus.MISSING
            
        print("    ✅ Engine assignment verified")
        return AlignmentStatus.ALIGNED
        
    def _check_pipeline_mapping(self) -> AlignmentStatus:
        """Check 000-999 pipeline stage mapping."""
        print("  📋 Checking pipeline mapping...")
        
        # Check for v46 stage numbering
        pipeline_file = self.track_c_path / "system" / "pipeline.py"
        if pipeline_file.exists():
            try:
                with open(pipeline_file, 'r') as f:
                    content = f.read()
                    
                # Look for v46 stage constants
                v46_stages = [
                    "STAGE_000_FOUNDATION", "STAGE_111_SENSE", "STAGE_222_REFLECT",
                    "STAGE_333_ATLAS", "STAGE_444_ALIGN", "STAGE_555_EMPATHIZE",
                    "STAGE_666_BRIDGE", "STAGE_777_EUREKA", "STAGE_888_COMPASS",
                    "STAGE_999_VAULT"
                ]
                
                missing_stages = []
                for stage in v46_stages:
                    if stage not in content:
                        missing_stages.append(stage)
                        
                if missing_stages:
                    self.issues.append(AlignmentIssue(
                        track="C",
                        component="Pipeline Stages",
                        issue_type="INCOMPLETE_MAPPING",
                        current_state=f"Missing v46 stages: {missing_stages}",
                        required_state="All 000-999 v46 stages defined",
                        severity="MEDIUM",
                        remediation="Update stage constants to v46 numbering"
                    ))
                    return AlignmentStatus.MISALIGNED
                    
            except Exception as e:
                self.issues.append(AlignmentIssue(
                    track="C",
                    component="Pipeline Analysis",
                    issue_type="ANALYSIS_ERROR",
                    current_state=f"Error: {e}",
                    required_state="Readable pipeline file",
                    severity="MEDIUM",
                    remediation="Check pipeline file integrity"
                ))
                return AlignmentStatus.MISALIGNED
                
        print("    ✅ Pipeline mapping verified")
        return AlignmentStatus.ALIGNED
        
    def generate_alignment_percentage(self) -> float:
        """Calculate overall alignment percentage."""
        total_checks = 5  # Number of major alignment areas
        aligned_checks = 0
        
        # Count aligned components
        for issue in self.issues:
            if issue.severity in ["CRITICAL", "HIGH"]:
                continue  # Major issues count as misaligned
            else:
                aligned_checks += 1
                
        # Calculate percentage (minimum 0%)
        aligned_components = max(0, total_checks - len([i for i in self.issues if i.severity in ["CRITICAL", "HIGH"]]))
        return (aligned_components / total_checks) * 100
        
    def generate_recommendations(self) -> List[str]:
        """Generate alignment recommendations."""
        recommendations = []
        
        # Critical issues first
        critical_issues = [i for i in self.issues if i.severity == "CRITICAL"]
        if critical_issues:
            recommendations.append("🚨 ADDRESS CRITICAL ISSUES FIRST:")
            for issue in critical_issues:
                recommendations.append(f"   - {issue.component}: {issue.remediation}")
                
        # High priority issues
        high_issues = [i for i in self.issues if i.severity == "HIGH"]
        if high_issues:
            recommendations.append("⚠️  HIGH PRIORITY ALIGNMENT TASKS:")
            for issue in high_issues:
                recommendations.append(f"   - {issue.component}: {issue.remediation}")
                
        # General recommendations
        if not critical_issues and not high_issues:
            recommendations.append("✅ No critical alignment issues found")
            
        recommendations.extend([
            "",
            "📋 ALIGNMENT PROTOCOL:",
            "1. Complete Phoenix-72 cooling period before changes",
            "2. Create backup of current arifos_core state",
            "3. Follow step-by-step alignment protocol",
            "4. Run alignment verification after each phase",
            "5. Obtain human sovereign approval before SEAL"
        ])
        
        return recommendations
        
    def run_alignment_check(self) -> AlignmentReport:
        """Run complete alignment check across all tracks."""
        print("🚀 Starting Track A/B/C Alignment Verification v46.0")
        print("=" * 60)
        
        # Check each track
        track_a_status = self.check_track_a_integrity()
        track_b_status = self.check_track_b_manifest()
        track_c_status = self.check_track_c_alignment()
        
        # Determine overall status
        if track_a_status == AlignmentStatus.ALIGNED and track_b_status == AlignmentStatus.ALIGNED and track_c_status == AlignmentStatus.ALIGNED:
            overall_status = AlignmentStatus.ALIGNED
        elif any(status == AlignmentStatus.MISSING for status in [track_a_status, track_b_status, track_c_status]):
            overall_status = AlignmentStatus.MISSING
        else:
            overall_status = AlignmentStatus.MISALIGNED
            
        # Calculate alignment percentage
        alignment_percentage = self.generate_alignment_percentage()
        
        # Generate recommendations
        self.recommendations = self.generate_recommendations()
        
        # Create report
        report = AlignmentReport(
            overall_status=overall_status,
            track_a_status=track_a_status,
            track_b_status=track_b_status,
            track_c_status=track_c_status,
            issues=self.issues,
            recommendations=self.recommendations,
            alignment_percentage=alignment_percentage
        )
        
        # Print summary
        print("\n📊 ALIGNMENT REPORT SUMMARY")
        print("=" * 60)
        print(f"Overall Status: {overall_status.value}")
        print(f"Track A (Canon): {track_a_status.value}")
        print(f"Track B (Specs): {track_b_status.value}")
        print(f"Track C (Code): {track_c_status.value}")
        print(f"Alignment Percentage: {alignment_percentage:.1f}%")
        print(f"Issues Found: {len(self.issues)}")
        
        if self.issues:
            print(f"Critical Issues: {len([i for i in self.issues if i.severity == 'CRITICAL'])}")
            print(f"High Priority: {len([i for i in self.issues if i.severity == 'HIGH'])}")
            
        print("\n📝 RECOMMENDATIONS:")
        for rec in self.recommendations:
            print(rec)
            
        return report


def main():
    """Main execution function."""
    # Determine repository root
    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    
    print(f"📁 Repository Root: {repo_root}")
    
    # Create alignment checker
    checker = TrackAlignmentChecker(repo_root)
    
    # Run alignment check
    report = checker.run_alignment_check()
    
    # Exit with appropriate code
    if report.overall_status == AlignmentStatus.ALIGNED:
        print("\n✅ ALL TRACKS ALIGNED - Constitutional authority maintained")
        sys.exit(0)
    elif any(status == AlignmentStatus.MISSING for status in [report.track_a_status, report.track_b_status, report.track_c_status]):
        print("\n❌ CRITICAL ALIGNMENT FAILURE - Missing constitutional components")
        sys.exit(2)
    else:
        print("\n⚠️  ALIGNMENT GAPS DETECTED - Constitutional drift present")
        sys.exit(1)


if __name__ == "__main__":
    main()