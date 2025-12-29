#!/usr/bin/env python3
"""
Sync Skills - Master-Derive Model Automation

Synchronizes skill definitions from master (.agent/workflows/) to platform
variants (.codex/skills/ and .claude/skills/) while preserving platform-specific
enhancements.

Constitutional Compliance:
- F1 Amanah: Reversible (dry-run mode, git-tracked)
- F2 Truth: Version tracking prevents fabrication
- F4 ΔS: Reduces confusion (single source of truth)
- F6 Amanah: Transparent (shows all changes before applying)

Usage:
    python scripts/sync_skills.py --dry-run   # Preview changes
    python scripts/sync_skills.py --diff      # Show detailed diff
    python scripts/sync_skills.py --apply     # Apply sync
    python scripts/sync_skills.py --skill 000 --apply  # Sync specific skill

Exit Codes:
    0 - Success (all synced)
    1 - Drift detected (in --dry-run mode)
    2 - Validation failed (tool violations, missing files)
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml


@dataclass
class SkillMetadata:
    """Skill metadata from YAML frontmatter."""
    skill: str
    version: str
    description: str
    floors: List[str]
    allowed_tools: List[str]
    expose_cli: bool
    derive_to: List[str]
    codex_name: Optional[str] = None
    claude_name: Optional[str] = None
    sabar_threshold: Optional[float] = None


@dataclass
class SyncResult:
    """Result of a sync operation."""
    skill: str
    platform: str
    synced: bool
    reason: str
    changes_preview: Optional[str] = None


class SkillSyncer:
    """Synchronizes skills from master to platform variants."""

    MASTER_DIR = Path(".agent/workflows")
    CODEX_DIR = Path(".codex/skills")
    CLAUDE_DIR = Path(".claude/skills")

    CANONICAL_BEGIN = "<!-- BEGIN CANONICAL WORKFLOW -->"
    CANONICAL_END = "<!-- END CANONICAL WORKFLOW -->"

    def __init__(self, dry_run: bool = True, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.results: List[SyncResult] = []

    def parse_yaml_frontmatter(self, content: str) -> Tuple[Optional[Dict], str]:
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
        except yaml.YAMLError as e:
            print(f"[WARN] YAML parsing error: {e}")
            return None, content

    def read_master_skill(self, skill_file: Path) -> Optional[SkillMetadata]:
        """Read master skill definition."""
        if not skill_file.exists():
            return None

        content = skill_file.read_text(encoding="utf-8")
        metadata_dict, _ = self.parse_yaml_frontmatter(content)

        if not metadata_dict:
            print(f"[WARN] No YAML frontmatter in {skill_file}")
            return None

        try:
            return SkillMetadata(
                skill=metadata_dict.get("skill", skill_file.stem),
                version=metadata_dict.get("version", "0.0.0"),
                description=metadata_dict.get("description", ""),
                floors=metadata_dict.get("floors", []),
                allowed_tools=metadata_dict.get("allowed-tools", []),
                expose_cli=metadata_dict.get("expose-cli", True),
                derive_to=metadata_dict.get("derive-to", []),
                codex_name=metadata_dict.get("codex-name"),
                claude_name=metadata_dict.get("claude-name"),
                sabar_threshold=metadata_dict.get("sabar-threshold"),
            )
        except Exception as e:
            print(f"[WARN] Failed to parse metadata from {skill_file}: {e}")
            return None

    def extract_canonical_content(self, master_content: str) -> str:
        """Extract canonical workflow content from master file."""
        # Remove YAML frontmatter
        _, body = self.parse_yaml_frontmatter(master_content)

        # The canonical content is the main body after frontmatter
        # (everything that should be synced to platforms)
        return body.strip()

    def update_platform_skill(
        self,
        platform_file: Path,
        canonical_content: str,
        master_metadata: SkillMetadata,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Update platform skill file with canonical content.

        Returns:
            (changed, reason, preview_diff)
        """
        if not platform_file.exists():
            return False, f"Platform file does not exist: {platform_file}", None

        current_content = platform_file.read_text(encoding="utf-8")

        # Check if platform file has sync markers
        if self.CANONICAL_BEGIN not in current_content:
            return (
                False,
                f"Missing sync markers in {platform_file} (need to add {self.CANONICAL_BEGIN})",
                None,
            )

        # Extract platform-specific parts
        before_match = re.search(
            rf"(.*?){re.escape(self.CANONICAL_BEGIN)}",
            current_content,
            re.DOTALL,
        )
        after_match = re.search(
            rf"{re.escape(self.CANONICAL_END)}(.*)",
            current_content,
            re.DOTALL,
        )

        if not before_match or not after_match:
            return (
                False,
                f"Malformed sync markers in {platform_file}",
                None,
            )

        platform_header = before_match.group(1)
        platform_footer = after_match.group(1)

        # Check platform metadata for version
        platform_metadata_dict, _ = self.parse_yaml_frontmatter(current_content)
        if platform_metadata_dict:
            platform_version = platform_metadata_dict.get("master-version", "0.0.0")
            if self._compare_versions(master_metadata.version, platform_version) <= 0:
                return (
                    False,
                    f"Platform version {platform_version} >= master {master_metadata.version} (no sync needed)",
                    None,
                )

        # Validate tool restrictions (platform can only restrict, not expand)
        if platform_metadata_dict:
            platform_tools = set(platform_metadata_dict.get("allowed-tools", []))
            master_tools = set(master_metadata.allowed_tools)

            illegal_tools = platform_tools - master_tools
            if illegal_tools:
                return (
                    False,
                    f"TOOL VIOLATION: Platform allows tools not in master: {illegal_tools}",
                    None,
                )

        # Reconstruct file with synced content
        new_content = (
            f"{platform_header}"
            f"{self.CANONICAL_BEGIN}\n"
            f"{canonical_content}\n"
            f"{self.CANONICAL_END}"
            f"{platform_footer}"
        )

        # Check if content changed
        if new_content == current_content:
            return False, "No changes needed (already in sync)", None

        # Generate diff preview
        diff_preview = self._generate_diff(current_content, new_content, platform_file.name)

        # Apply changes if not dry-run
        if not self.dry_run:
            platform_file.write_text(new_content, encoding="utf-8")
            return True, f"Synced to {platform_file}", diff_preview
        else:
            return True, f"Would sync to {platform_file} (dry-run)", diff_preview

    def _compare_versions(self, v1: str, v2: str) -> int:
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

            # Pad to same length
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
            # Fallback to string comparison
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
            return 0

    def _generate_diff(self, old: str, new: str, filename: str) -> str:
        """Generate simple diff preview."""
        old_lines = old.splitlines()
        new_lines = new.splitlines()

        # Simple line-by-line diff
        diff_lines = [f"--- {filename} (current)"]
        diff_lines.append(f"+++ {filename} (synced)")

        for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines)):
            if old_line != new_line:
                diff_lines.append(f"@@ Line {i+1} @@")
                diff_lines.append(f"- {old_line}")
                diff_lines.append(f"+ {new_line}")

        # Handle length differences
        if len(new_lines) > len(old_lines):
            diff_lines.append(f"@@ +{len(old_lines)+1} to {len(new_lines)} @@")
            for line in new_lines[len(old_lines):]:
                diff_lines.append(f"+ {line}")
        elif len(old_lines) > len(new_lines):
            diff_lines.append(f"@@ -{len(new_lines)+1} to {len(old_lines)} @@")
            for line in old_lines[len(new_lines):]:
                diff_lines.append(f"- {line}")

        return "\n".join(diff_lines[:50])  # Limit to 50 lines

    def sync_skill(self, skill_name: str) -> List[SyncResult]:
        """Sync a specific skill to all platforms."""
        results = []

        # Read master file
        master_file = self.MASTER_DIR / f"{skill_name}.md"
        if not master_file.exists():
            print(f"[WARN] Master file not found: {master_file}")
            return [
                SyncResult(
                    skill=skill_name,
                    platform="all",
                    synced=False,
                    reason=f"Master file not found: {master_file}",
                )
            ]

        master_metadata = self.read_master_skill(master_file)
        if not master_metadata:
            return [
                SyncResult(
                    skill=skill_name,
                    platform="all",
                    synced=False,
                    reason="Failed to parse master metadata",
                )
            ]

        master_content = master_file.read_text(encoding="utf-8")
        canonical_content = self.extract_canonical_content(master_content)

        # Sync to Codex (if specified)
        if "codex" in master_metadata.derive_to and master_metadata.codex_name:
            codex_file = self.CODEX_DIR / master_metadata.codex_name / "SKILL.md"
            changed, reason, diff = self.update_platform_skill(
                codex_file, canonical_content, master_metadata
            )
            results.append(
                SyncResult(
                    skill=skill_name,
                    platform="codex",
                    synced=changed,
                    reason=reason,
                    changes_preview=diff,
                )
            )

        # Sync to Claude (if specified)
        if "claude" in master_metadata.derive_to and master_metadata.claude_name:
            claude_file = self.CLAUDE_DIR / master_metadata.claude_name / "SKILL.md"
            changed, reason, diff = self.update_platform_skill(
                claude_file, canonical_content, master_metadata
            )
            results.append(
                SyncResult(
                    skill=skill_name,
                    platform="claude",
                    synced=changed,
                    reason=reason,
                    changes_preview=diff,
                )
            )

        return results

    def sync_all_skills(self) -> List[SyncResult]:
        """Sync all master skills to platforms."""
        results = []

        # Find all master files
        if not self.MASTER_DIR.exists():
            print(f"[WARN] Master directory not found: {self.MASTER_DIR}")
            return []

        master_files = list(self.MASTER_DIR.glob("*.md"))
        if not master_files:
            print(f"[WARN] No master files found in {self.MASTER_DIR}")
            return []

        print(f"[INFO] Found {len(master_files)} master skills")

        for master_file in master_files:
            skill_name = master_file.stem
            skill_results = self.sync_skill(skill_name)
            results.extend(skill_results)

        return results

    def print_summary(self, results: List[SyncResult], show_diff: bool = False):
        """Print sync summary."""
        total = len(results)
        synced = sum(1 for r in results if r.synced)
        failed = sum(1 for r in results if not r.synced)

        print("\n" + "="*60)
        print(f"{'DRY RUN ' if self.dry_run else ''}SYNC SUMMARY")
        print("="*60)

        print(f"\nTotal Operations: {total}")
        print(f"[OK] Synced: {synced}")
        print(f"[WARN] Skipped/Failed: {failed}")

        if synced > 0:
            print(f"\n{'WOULD BE ' if self.dry_run else ''}SYNCED:")
            for r in results:
                if r.synced:
                    print(f"  [OK] {r.skill} -> {r.platform}: {r.reason}")
                    if show_diff and r.changes_preview:
                        print(f"\n{r.changes_preview}\n")

        if failed > 0:
            print(f"\nSKIPPED/FAILED:")
            for r in results:
                if not r.synced:
                    print(f"  [WARN] {r.skill} -> {r.platform}: {r.reason}")

        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description="Sync skills from master to platform variants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/sync_skills.py --dry-run   # Preview changes
  python scripts/sync_skills.py --diff      # Show detailed diff
  python scripts/sync_skills.py --apply     # Apply sync
  python scripts/sync_skills.py --skill 000 --apply  # Sync specific skill

Exit Codes:
  0 - Success (all synced)
  1 - Drift detected (in --dry-run mode)
  2 - Validation failed (tool violations, missing files)
        """,
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes (default is dry-run)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying (default)",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Show detailed diff of changes",
    )
    parser.add_argument(
        "--skill",
        type=str,
        help="Sync specific skill only (e.g., '000', 'fag')",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # Determine mode (default is dry-run)
    dry_run = not args.apply or args.dry_run

    syncer = SkillSyncer(dry_run=dry_run, verbose=args.verbose)

    print("[SYNC] arifOS Skills Sync - Master-Derive Model")
    print(f"Mode: {'DRY RUN (preview only)' if dry_run else 'APPLY (will modify files)'}")
    print()

    # Sync skills
    if args.skill:
        results = syncer.sync_skill(args.skill)
    else:
        results = syncer.sync_all_skills()

    # Print summary
    syncer.print_summary(results, show_diff=args.diff)

    # Determine exit code
    if not results:
        print("\n[WARN] No sync operations performed")
        return 2

    # Check for failures
    failures = [r for r in results if not r.synced and "VIOLATION" in r.reason]
    if failures:
        print("\n❌ VALIDATION FAILED: Tool violations detected")
        return 2

    # Check for drift (in dry-run mode)
    if dry_run:
        drift = [r for r in results if r.synced]
        if drift:
            print(f"\n[WARN] DRIFT DETECTED: {len(drift)} skills need sync")
            print("Run with --apply to sync")
            return 1

    print("\n[OK] Sync complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
