#!/usr/bin/env python3
"""
Check Skill Drift - Detect Version Mismatches and Violations

Validates skill registry integrity by detecting:
1. Version drift (platform version < master version)
2. Missing skills (master exists but no platform variant)
3. Orphaned skills (platform exists but no master)
4. Tool violations (platform allows tools not in master)
5. Content drift (platform canonical section differs from master)

Constitutional Compliance:
- F1 Amanah: Non-destructive (read-only analysis)
- F2 Truth: Factual reporting of drift state
- F4 ΔS: Reduces confusion (identifies inconsistencies)
- F8 G: Governed intelligence (enforces registry rules)

Usage:
    python scripts/check_skill_drift.py              # Check all skills
    python scripts/check_skill_drift.py --skill 000  # Check specific skill
    python scripts/check_skill_drift.py --json       # JSON output for CI

Exit Codes:
    0 - No drift detected (all in sync)
    1 - Drift detected (needs sync)
    2 - Critical violations (tool violations, missing masters)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml


@dataclass
class DriftIssue:
    """Detected drift issue."""
    severity: str  # "warning", "error", "critical"
    category: str  # "version", "missing", "orphaned", "tool_violation", "content"
    skill: str
    platform: str
    message: str
    master_value: Optional[str] = None
    platform_value: Optional[str] = None


class SkillDriftChecker:
    """Checks for drift between master skills and platform variants."""

    MASTER_DIR = Path(".agent/workflows")
    CODEX_DIR = Path(".codex/skills")
    CLAUDE_DIR = Path(".claude/skills")

    CANONICAL_BEGIN = "<!-- BEGIN CANONICAL WORKFLOW -->"
    CANONICAL_END = "<!-- END CANONICAL WORKFLOW -->"

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.issues: List[DriftIssue] = []

    def parse_yaml_frontmatter(self, content: str) -> tuple[Optional[Dict], str]:
        """Extract YAML frontmatter and content."""
        if not content.startswith("---\n"):
            return None, content

        parts = content.split("---\n", 2)
        if len(parts) < 3:
            return None, content

        try:
            metadata = yaml.safe_load(parts[1])
            body = parts[2]
            return metadata, body
        except yaml.YAMLError:
            return None, content

    def compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare semantic versions.

        Returns:
            1 if v1 > v2
            0 if v1 == v2
            -1 if v1 < v2
        """
        try:
            parts1 = [int(x) for x in v1.split(".")]
            parts2 = [int(x) for x in v2.split(".")]

            max_len = max(len(parts1), len(parts2))
            parts1 += [0] * (max_len - len(parts1))
            parts2 += [0] * (max_len - len(parts2))

            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            return 0
        except ValueError:
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
            return 0

    def check_version_drift(
        self,
        skill_name: str,
        master_version: str,
        platform_file: Path,
        platform: str,
    ) -> None:
        """Check if platform version is behind master."""
        if not platform_file.exists():
            return

        content = platform_file.read_text(encoding="utf-8")
        metadata, _ = self.parse_yaml_frontmatter(content)

        if not metadata:
            self.issues.append(
                DriftIssue(
                    severity="error",
                    category="version",
                    skill=skill_name,
                    platform=platform,
                    message="No YAML frontmatter found",
                )
            )
            return

        platform_version = metadata.get("master-version", metadata.get("version", "0.0.0"))

        if self.compare_versions(master_version, platform_version) > 0:
            self.issues.append(
                DriftIssue(
                    severity="warning",
                    category="version",
                    skill=skill_name,
                    platform=platform,
                    message=f"Platform version behind master",
                    master_value=master_version,
                    platform_value=platform_version,
                )
            )

    def check_tool_violations(
        self,
        skill_name: str,
        master_tools: List[str],
        platform_file: Path,
        platform: str,
    ) -> None:
        """Check if platform allows tools not in master (security violation)."""
        if not platform_file.exists():
            return

        content = platform_file.read_text(encoding="utf-8")
        metadata, _ = self.parse_yaml_frontmatter(content)

        if not metadata:
            return

        platform_tools = set(metadata.get("allowed-tools", []))
        master_tools_set = set(master_tools)

        illegal_tools = platform_tools - master_tools_set

        if illegal_tools:
            self.issues.append(
                DriftIssue(
                    severity="critical",
                    category="tool_violation",
                    skill=skill_name,
                    platform=platform,
                    message=f"Platform allows tools not in master: {sorted(illegal_tools)}",
                    master_value=str(sorted(master_tools)),
                    platform_value=str(sorted(platform_tools)),
                )
            )

    def check_missing_platform_variant(
        self,
        skill_name: str,
        platform_name: str,
        expected_file: Path,
    ) -> None:
        """Check if platform variant is missing."""
        if not expected_file.exists():
            self.issues.append(
                DriftIssue(
                    severity="warning",
                    category="missing",
                    skill=skill_name,
                    platform=platform_name,
                    message=f"Master exists but no {platform_name} variant found",
                    platform_value=str(expected_file),
                )
            )

    def check_orphaned_platform_skill(
        self,
        platform_file: Path,
        platform: str,
        master_files: Set[str],
    ) -> None:
        """Check if platform skill has no corresponding master."""
        content = platform_file.read_text(encoding="utf-8")
        metadata, _ = self.parse_yaml_frontmatter(content)

        if not metadata:
            return

        master_source = metadata.get("master-source", "")
        if not master_source:
            # No master-source field, can't verify
            return

        master_file = Path(master_source)
        skill_name = master_file.stem

        if skill_name not in master_files:
            self.issues.append(
                DriftIssue(
                    severity="error",
                    category="orphaned",
                    skill=skill_name,
                    platform=platform,
                    message=f"Platform variant exists but no master found",
                    master_value=master_source,
                )
            )

    def check_content_drift(
        self,
        skill_name: str,
        master_canonical: str,
        platform_file: Path,
        platform: str,
    ) -> None:
        """Check if platform canonical section differs from master."""
        if not platform_file.exists():
            return

        content = platform_file.read_text(encoding="utf-8")

        # Check for sync markers
        if self.CANONICAL_BEGIN not in content:
            self.issues.append(
                DriftIssue(
                    severity="warning",
                    category="content",
                    skill=skill_name,
                    platform=platform,
                    message="Missing sync markers (cannot verify content drift)",
                )
            )
            return

        # Extract canonical section
        match = re.search(
            rf"{re.escape(self.CANONICAL_BEGIN)}\n(.*?)\n{re.escape(self.CANONICAL_END)}",
            content,
            re.DOTALL,
        )

        if not match:
            self.issues.append(
                DriftIssue(
                    severity="error",
                    category="content",
                    skill=skill_name,
                    platform=platform,
                    message="Malformed sync markers",
                )
            )
            return

        platform_canonical = match.group(1).strip()
        master_canonical_clean = master_canonical.strip()

        if platform_canonical != master_canonical_clean:
            # Calculate diff size
            diff_lines = len(set(platform_canonical.splitlines()) ^ set(master_canonical_clean.splitlines()))

            self.issues.append(
                DriftIssue(
                    severity="warning",
                    category="content",
                    skill=skill_name,
                    platform=platform,
                    message=f"Canonical content differs from master (~{diff_lines} lines diff)",
                )
            )

    def check_skill(self, skill_name: str) -> None:
        """Check drift for a specific skill."""
        master_file = self.MASTER_DIR / f"{skill_name}.md"

        if not master_file.exists():
            if self.verbose:
                print(f"⚠️ Master file not found: {master_file}")
            return

        # Read master metadata
        content = master_file.read_text(encoding="utf-8")
        metadata, body = self.parse_yaml_frontmatter(content)

        if not metadata:
            self.issues.append(
                DriftIssue(
                    severity="error",
                    category="version",
                    skill=skill_name,
                    platform="master",
                    message="No YAML frontmatter in master file",
                )
            )
            return

        master_version = metadata.get("version", "0.0.0")
        master_tools = metadata.get("allowed-tools", [])
        derive_to = metadata.get("derive-to", [])
        codex_name = metadata.get("codex-name")
        claude_name = metadata.get("claude-name")
        master_canonical = body.strip()

        # Check Codex variant
        if "codex" in derive_to and codex_name:
            codex_file = self.CODEX_DIR / codex_name / "SKILL.md"
            self.check_missing_platform_variant(skill_name, "codex", codex_file)

            if codex_file.exists():
                self.check_version_drift(skill_name, master_version, codex_file, "codex")
                self.check_tool_violations(skill_name, master_tools, codex_file, "codex")
                self.check_content_drift(skill_name, master_canonical, codex_file, "codex")

        # Check Claude variant
        if "claude" in derive_to and claude_name:
            claude_file = self.CLAUDE_DIR / claude_name / "SKILL.md"
            self.check_missing_platform_variant(skill_name, "claude", claude_file)

            if claude_file.exists():
                self.check_version_drift(skill_name, master_version, claude_file, "claude")
                self.check_tool_violations(skill_name, master_tools, claude_file, "claude")
                self.check_content_drift(skill_name, master_canonical, claude_file, "claude")

    def check_all_skills(self) -> None:
        """Check drift for all skills."""
        if not self.MASTER_DIR.exists():
            print(f"⚠️ Master directory not found: {self.MASTER_DIR}")
            return

        master_files = list(self.MASTER_DIR.glob("*.md"))
        if not master_files:
            print(f"⚠️ No master files found in {self.MASTER_DIR}")
            return

        master_skill_names = {f.stem for f in master_files}

        if self.verbose:
            print(f"Checking {len(master_files)} master skills...")

        # Check each master skill
        for master_file in master_files:
            self.check_skill(master_file.stem)

        # Check for orphaned platform skills (Codex)
        if self.CODEX_DIR.exists():
            for platform_dir in self.CODEX_DIR.iterdir():
                if platform_dir.is_dir():
                    skill_file = platform_dir / "SKILL.md"
                    if skill_file.exists():
                        self.check_orphaned_platform_skill(skill_file, "codex", master_skill_names)

        # Check for orphaned platform skills (Claude)
        if self.CLAUDE_DIR.exists():
            for platform_dir in self.CLAUDE_DIR.iterdir():
                if platform_dir.is_dir():
                    skill_file = platform_dir / "SKILL.md"
                    if skill_file.exists():
                        self.check_orphaned_platform_skill(skill_file, "claude", master_skill_names)

    def print_summary(self, as_json: bool = False) -> None:
        """Print drift check summary."""
        if as_json:
            output = {
                "total_issues": len(self.issues),
                "critical": len([i for i in self.issues if i.severity == "critical"]),
                "errors": len([i for i in self.issues if i.severity == "error"]),
                "warnings": len([i for i in self.issues if i.severity == "warning"]),
                "issues": [asdict(i) for i in self.issues],
            }
            print(json.dumps(output, indent=2))
            return

        # Text output
        print("\n" + "="*70)
        print("SKILL DRIFT CHECK REPORT")
        print("="*70)

        if not self.issues:
            print("\n[OK] No drift detected - all skills in sync!")
            print("\n" + "="*70)
            return

        # Group by severity
        critical = [i for i in self.issues if i.severity == "critical"]
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]

        print(f"\nTotal Issues: {len(self.issues)}")
        print(f"  CRITICAL: {len(critical)} (tool violations)")
        print(f"  ERRORS: {len(errors)} (missing masters, malformed)")
        print(f"  WARNINGS: {len(warnings)} (version drift, content drift)")

        # Print critical issues
        if critical:
            print("\n" + "CRITICAL ISSUES (Security Violations):")
            print("-"*70)
            for issue in critical:
                print(f"\n  Skill: {issue.skill} ({issue.platform})")
                print(f"  Issue: {issue.message}")
                if issue.master_value:
                    print(f"  Master allows: {issue.master_value}")
                if issue.platform_value:
                    print(f"  Platform allows: {issue.platform_value}")

        # Print errors
        if errors:
            print("\n" + "ERRORS:")
            print("-"*70)
            for issue in errors:
                print(f"\n  Skill: {issue.skill} ({issue.platform})")
                print(f"  Issue: {issue.message}")
                if issue.master_value:
                    print(f"  Details: {issue.master_value}")

        # Print warnings (grouped by category)
        if warnings:
            print("\n" + "WARNINGS:")
            print("-"*70)

            version_warnings = [i for i in warnings if i.category == "version"]
            content_warnings = [i for i in warnings if i.category == "content"]
            missing_warnings = [i for i in warnings if i.category == "missing"]

            if version_warnings:
                print("\n  Version Drift:")
                for issue in version_warnings:
                    print(f"    - {issue.skill} ({issue.platform}): {issue.platform_value} < master {issue.master_value}")

            if content_warnings:
                print("\n  Content Drift:")
                for issue in content_warnings:
                    print(f"    - {issue.skill} ({issue.platform}): {issue.message}")

            if missing_warnings:
                print("\n  Missing Platform Variants:")
                for issue in missing_warnings:
                    print(f"    - {issue.skill} → {issue.platform}")

        # Print recommendation
        print("\n" + "="*70)
        if critical or errors:
            print("[FAIL] CRITICAL/ERROR ISSUES FOUND")
            print("\nACTION REQUIRED:")
            if critical:
                print("  1. Fix tool violations (platform must not expand beyond master)")
            if errors:
                print("  2. Fix malformed files or create missing masters")
        else:
            print("[WARN] DRIFT DETECTED")
            print("\nRECOMMENDATION: Run 'python scripts/sync_skills.py --apply'")

        print("="*70)


def main():
    parser = argparse.ArgumentParser(
        description="Check skill drift between master and platform variants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/check_skill_drift.py              # Check all skills
  python scripts/check_skill_drift.py --skill 000  # Check specific skill
  python scripts/check_skill_drift.py --json       # JSON output for CI

Exit Codes:
  0 - No drift detected (all in sync)
  1 - Drift detected (needs sync)
  2 - Critical violations (tool violations, missing masters)
        """,
    )

    parser.add_argument(
        "--skill",
        type=str,
        help="Check specific skill only (e.g., '000', 'fag')",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    checker = SkillDriftChecker(verbose=args.verbose)

    if not args.json:
        print("arifOS Skills Drift Checker")
        print()

    # Check skills
    if args.skill:
        checker.check_skill(args.skill)
    else:
        checker.check_all_skills()

    # Print summary
    checker.print_summary(as_json=args.json)

    # Determine exit code
    if not checker.issues:
        return 0

    # Critical issues (tool violations, missing masters)
    critical = [i for i in checker.issues if i.severity in ("critical", "error")]
    if critical:
        return 2

    # Warnings only (version drift, content drift)
    return 1


if __name__ == "__main__":
    sys.exit(main())
