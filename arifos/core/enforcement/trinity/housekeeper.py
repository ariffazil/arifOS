"""
housekeeper.py - Auto-Documentation Engine

Analyzes code changes and proposes (but does NOT apply) documentation updates:
- Version bumps (semantic versioning)
- CHANGELOG.md entries
- README.md updates
- pyproject.toml version field

Part of Trinity governance system (Phase 3: CRYSTALLIZATION -> THE HOUSEKEEPER)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .forge import ForgeReport
from .qc import QCReport


@dataclass
class HousekeeperProposal:
    """Proposed documentation updates (NOT auto-applied)."""

    version_bump: str  # "patch" | "minor" | "major"
    new_version: str  # e.g. "43.0.1"
    changelog_entry: str
    readme_updates: Optional[str] = None
    pyproject_updates: Dict[str, Any] = None


def propose_docs(
    forge_report: ForgeReport,
    qc_report: QCReport,
    current_version: str = "43.0.0",
) -> HousekeeperProposal:
    """
    Analyze changes and propose documentation updates.

    Uses heuristics to determine:
    - Semantic version bump (patch/minor/major)
    - CHANGELOG entry text
    - README updates (if needed)

    Args:
        forge_report: Output from /gitforge
        qc_report: Output from /gitQC
        current_version: Current version (default: 43.0.0)

    Returns:
        HousekeeperProposal with suggested updates

    Note:
        This function PROPOSES changes only. The human authority at /gitseal
        reviews and approves before any files are modified.
    """
    # Determine version bump based on change characteristics
    version_bump = _determine_version_bump(forge_report, qc_report)

    # Calculate new version
    new_version = _calculate_new_version(current_version, version_bump)

    # Generate CHANGELOG entry
    changelog_entry = _generate_changelog_entry(forge_report, qc_report, new_version)

    # Check if README needs updates
    readme_updates = _check_readme_updates(forge_report)

    # Prepare pyproject.toml updates
    pyproject_updates = {"version": new_version}

    return HousekeeperProposal(
        version_bump=version_bump,
        new_version=new_version,
        changelog_entry=changelog_entry,
        readme_updates=readme_updates,
        pyproject_updates=pyproject_updates,
    )


def _determine_version_bump(forge_report: ForgeReport, qc_report: QCReport) -> str:
    """
    Determine semantic version bump based on change characteristics.

    Rules:
    - MAJOR: Breaking changes, API changes, >20 files changed
    - MINOR: New features, 10-20 files changed
    - PATCH: Bug fixes, docs, <10 files changed
    """
    file_count = len(forge_report.files_changed)

    # Check for breaking change indicators
    breaking_indicators = ["BREAKING", "breaking change", "API change"]
    has_breaking = any(
        indicator in note.lower() for note in forge_report.notes for indicator in breaking_indicators
    )

    if has_breaking or file_count > 20:
        return "major"
    elif file_count >= 10:
        return "minor"
    else:
        return "patch"


def _calculate_new_version(current: str, bump: str) -> str:
    """
    Calculate new semantic version.

    Args:
        current: Current version e.g. "43.0.0"
        bump: "major" | "minor" | "patch"

    Returns:
        New version string
    """
    parts = current.split(".")
    if len(parts) != 3:
        return current  # Fallback to current if format unexpected

    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1

    return f"{major}.{minor}.{patch}"


def _generate_changelog_entry(
    forge_report: ForgeReport, qc_report: QCReport, new_version: str
) -> str:
    """
    Generate CHANGELOG.md entry based on changes.

    Format follows Keep a Changelog standard.
    """
    from datetime import datetime

    date = datetime.now().strftime("%Y-%m-%d")

    entry = f"""## [{new_version}] - {date}

### Changed
"""

    # Add file change summary
    if len(forge_report.files_changed) <= 5:
        entry += "".join(f"- Modified `{f}`\n" for f in forge_report.files_changed)
    else:
        entry += f"- Modified {len(forge_report.files_changed)} files across:\n"
        # Group by directory
        dirs = set(f.split("/")[0] if "/" in f else "root" for f in forge_report.files_changed)
        entry += "".join(f"  - `{d}/`\n" for d in sorted(dirs))

    # Add hot zone warnings if any
    if forge_report.hot_zones:
        entry += "\n### Notes\n"
        entry += f"- ⚠️  Touched {len(forge_report.hot_zones)} frequently-modified file(s)\n"

    # Add QC verdict
    entry += f"\n### Quality Control\n"
    entry += f"- Constitutional floors: {sum(qc_report.floors_passed.values())}/{len(qc_report.floors_passed)} passed\n"
    entry += f"- Verdict: {qc_report.verdict}\n"
    entry += f"- ZKPC: `{qc_report.zkpc_id}`\n"

    return entry


def _check_readme_updates(forge_report: ForgeReport) -> Optional[str]:
    """
    Check if README needs updates based on changed files.

    Returns:
        Suggested README update text, or None if no updates needed
    """
    # Check if new major features were added
    new_features = [
        f
        for f in forge_report.files_changed
        if any(keyword in f.lower() for keyword in ["trinity", "forge", "qc", "seal"])
    ]

    if new_features:
        return f"""
## Trinity System (v43)

New governance system for code changes:
- `/gitforge` - State mapping and entropy prediction
- `/gitQC` - Constitutional quality control
- `/gitseal` - Human authority gate + release bundling

See `FORGING_PROTOCOL_v43.md` for details.
"""

    return None
