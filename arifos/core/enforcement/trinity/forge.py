"""
forge.py - /gitforge State Mapper & Entropy Predictor

Scans git history to identify hot zones (frequently changed files) and
predicts entropy impact (ΔS) of proposed changes.

Part of Trinity governance system (Phase 1: STABILIZATION -> THE RIG SETUP)
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class ForgeReport:
    """Report from /gitforge analysis."""

    files_changed: List[str]
    hot_zones: List[str]  # Frequently modified files
    entropy_delta: float  # Predicted ΔS impact
    risk_score: float  # 0-1 scale (higher = more risky)
    timestamp: str
    branch: str
    base_commit: str
    head_commit: str
    notes: List[str] = field(default_factory=list)


def analyze_branch(
    branch_name: str,
    base: str = "main",
    repo_path: Optional[Path] = None,
) -> ForgeReport:
    """
    Scan git history and predict entropy impact of proposed changes.

    Args:
        branch_name: Feature branch to analyze
        base: Base branch to compare against (default: main)
        repo_path: Path to git repository (default: current directory)

    Returns:
        ForgeReport with hot zones, entropy prediction, and risk assessment

    Raises:
        RuntimeError: If git commands fail
    """
    repo_path = repo_path or Path.cwd()

    # Get list of changed files
    files_changed = _get_changed_files(branch_name, base, repo_path)

    # Identify hot zones (files changed frequently in last 30 commits)
    hot_zones = _identify_hot_zones(files_changed, repo_path)

    # Predict entropy delta based on file count, hot zone overlap
    entropy_delta = _predict_entropy_delta(files_changed, hot_zones)

    # Calculate risk score
    risk_score = _calculate_risk_score(files_changed, hot_zones, entropy_delta)

    # Get commit hashes
    base_commit = _get_commit_hash(base, repo_path)
    head_commit = _get_commit_hash(branch_name, repo_path)

    # Generate notes
    notes = _generate_notes(files_changed, hot_zones, risk_score)

    return ForgeReport(
        files_changed=files_changed,
        hot_zones=hot_zones,
        entropy_delta=entropy_delta,
        risk_score=risk_score,
        timestamp=datetime.now(timezone.utc).isoformat(),
        branch=branch_name,
        base_commit=base_commit,
        head_commit=head_commit,
        notes=notes,
    )


def _get_changed_files(branch: str, base: str, repo_path: Path) -> List[str]:
    """Get list of files changed between base and branch."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base}...{branch}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        return files
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get changed files: {e.stderr}") from e


def _identify_hot_zones(files: List[str], repo_path: Path, limit: int = 30) -> List[str]:
    """
    Identify hot zones - files that have been frequently modified.

    A file is a hot zone if it appears in the changed files AND has been
    modified frequently in recent history (last N commits).
    """
    try:
        # Get files changed in last N commits
        result = subprocess.run(
            ["git", "log", f"-{limit}", "--name-only", "--pretty=format:"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Count frequency of each file
        file_counts: dict[str, int] = {}
        for line in result.stdout.split("\n"):
            line = line.strip()
            if line:
                file_counts[line] = file_counts.get(line, 0) + 1

        # Hot zones = changed files that appear frequently (>= 3 times in last 30 commits)
        hot_zones = [f for f in files if file_counts.get(f, 0) >= 3]
        return hot_zones

    except subprocess.CalledProcessError as e:
        # AGENTS.md: No silent errors - log and continue
        import logging

        logging.getLogger(__name__).warning(
            f"Hot zone detection failed (git log error): {e.stderr}. Continuing with empty hot zones."
        )
        return []


def _predict_entropy_delta(files_changed: List[str], hot_zones: List[str]) -> float:
    """
    Predict entropy delta (ΔS) based on change characteristics.

    Higher ΔS = more entropy added (bad for clarity).
    Lower ΔS = more entropy removed (good for clarity).

    For now, a simple heuristic:
    - Each changed file adds 0.1 entropy
    - Each hot zone file adds 0.3 additional entropy (riskier)
    - Ideal ΔS < 5.0 (from FORGING_PROTOCOL_v43.md SABAR threshold)
    """
    base_entropy = len(files_changed) * 0.1
    hot_zone_penalty = len(hot_zones) * 0.3
    return base_entropy + hot_zone_penalty


def _calculate_risk_score(
    files_changed: List[str], hot_zones: List[str], entropy_delta: float
) -> float:
    """
    Calculate risk score (0-1 scale).

    Risk factors:
    - Number of files changed
    - Number of hot zones touched
    - Predicted entropy delta

    Returns float between 0.0 (low risk) and 1.0 (high risk).
    """
    # Normalize factors to 0-1 range
    file_risk = min(len(files_changed) / 20.0, 1.0)  # 20+ files = max risk
    hot_zone_risk = min(len(hot_zones) / 5.0, 1.0)  # 5+ hot zones = max risk
    entropy_risk = min(entropy_delta / 5.0, 1.0)  # ΔS >= 5.0 = SABAR threshold

    # Weighted average (hot zones matter most)
    risk = (file_risk * 0.3) + (hot_zone_risk * 0.5) + (entropy_risk * 0.2)
    return round(risk, 3)


def _get_commit_hash(ref: str, repo_path: Path) -> str:
    """Get full commit hash for a git reference."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", ref],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get commit hash for {ref}: {e.stderr}") from e


def _generate_notes(files: List[str], hot_zones: List[str], risk: float) -> List[str]:
    """Generate human-readable analysis notes."""
    notes = []

    if len(files) == 0:
        notes.append("No files changed - clean branch")
    elif len(files) <= 5:
        notes.append(f"Small change: {len(files)} files modified")
    elif len(files) <= 15:
        notes.append(f"Medium change: {len(files)} files modified")
    else:
        notes.append(f"Large change: {len(files)} files modified")

    if hot_zones:
        notes.append(f"⚠️  {len(hot_zones)} hot zone(s) touched: {', '.join(hot_zones[:3])}")

    if risk >= 0.7:
        notes.append("🔴 HIGH RISK - Recommend full cooling + human review")
    elif risk >= 0.4:
        notes.append("🟡 MODERATE RISK - Standard review recommended")
    else:
        notes.append("🟢 LOW RISK - Fast track eligible")

    return notes
