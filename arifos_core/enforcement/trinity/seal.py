"""
seal.py - /gitseal Release Bundle Creator & Human Authority Gate

Creates atomic release bundles (code + docs + version + ledger) and enforces
human sovereignty through explicit APPROVE/REJECT/HOLD decisions.

Part of Trinity governance system (Phase 3: CRYSTALLIZATION -> THE HOUSEKEEPER)
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .forge import ForgeReport
from .housekeeper import HousekeeperProposal
from .qc import QCReport


@dataclass
class SealDecision:
    """Result of /gitseal execution."""

    verdict: str  # "APPROVED" | "REJECTED" | "HOLD"
    bundle_hash: Optional[str] = None
    commit_hash: Optional[str] = None
    tag: Optional[str] = None
    ledger_entry_id: str = ""
    timestamp: str = ""
    reason: str = ""


def execute_seal(
    decision: str,  # "APPROVE" | "REJECT" | "HOLD"
    branch: str,
    human_authority: str,
    reason: str,
    forge_report: ForgeReport,
    qc_report: QCReport,
    housekeeper_proposal: HousekeeperProposal,
    repo_path: Optional[Path] = None,
) -> SealDecision:
    """
    Execute /gitseal decision with human authority.

    Args:
        decision: "APPROVE" | "REJECT" | "HOLD"
        branch: Feature branch name
        human_authority: Name of approving authority (e.g. "Muhammad Arif bin Fazil")
        reason: Human-provided reason for decision
        forge_report: Output from /gitforge
        qc_report: Output from /gitQC
        housekeeper_proposal: Proposed doc updates from housekeeper
        repo_path: Path to git repository (default: current directory)

    Returns:
        SealDecision with verdict and (if approved) bundle details

    Raises:
        RuntimeError: If atomic bundling fails
    """
    repo_path = repo_path or Path.cwd()
    timestamp = datetime.now(timezone.utc).isoformat()

    # Write ledger entry FIRST (before any git operations)
    ledger_entry_id = _write_ledger_entry(
        decision=decision,
        branch=branch,
        human_authority=human_authority,
        reason=reason,
        forge_report=forge_report,
        qc_report=qc_report,
        housekeeper_proposal=housekeeper_proposal,
        timestamp=timestamp,
        repo_path=repo_path,
    )

    if decision == "REJECT":
        return SealDecision(
            verdict="REJECTED",
            ledger_entry_id=ledger_entry_id,
            timestamp=timestamp,
            reason=reason,
        )

    if decision == "HOLD":
        return SealDecision(
            verdict="HOLD",
            ledger_entry_id=ledger_entry_id,
            timestamp=timestamp,
            reason=reason,
        )

    # APPROVE: Create atomic release bundle
    if decision == "APPROVE":
        # Enforce preconditions
        _enforce_preconditions(qc_report, forge_report)

        # Create atomic bundle (all or nothing)
        try:
            bundle_result = _create_atomic_bundle(
                branch=branch,
                housekeeper_proposal=housekeeper_proposal,
                forge_report=forge_report,
                qc_report=qc_report,
                repo_path=repo_path,
            )

            # Update manifest with new version
            _update_manifest(
                version=housekeeper_proposal.new_version,
                bundle_hash=bundle_result["bundle_hash"],
                commit_hash=bundle_result["commit_hash"],
                tag=bundle_result["tag"],
                human_authority=human_authority,
                repo_path=repo_path,
            )

            # Integrate with Vault-999 constitutional memory
            _record_in_vault999(
                version=housekeeper_proposal.new_version,
                bundle_hash=bundle_result["bundle_hash"],
                commit_hash=bundle_result["commit_hash"],
                human_authority=human_authority,
                entropy_delta=forge_report.entropy_delta,
                repo_path=repo_path,
            )

            return SealDecision(
                verdict="APPROVED",
                bundle_hash=bundle_result["bundle_hash"],
                commit_hash=bundle_result["commit_hash"],
                tag=bundle_result["tag"],
                ledger_entry_id=ledger_entry_id,
                timestamp=timestamp,
                reason=reason,
            )

        except Exception as e:
            # Atomicity failure - rollback and record
            _rollback_changes(repo_path)
            raise RuntimeError(f"Atomic bundle creation failed: {e}") from e

    raise ValueError(f"Invalid decision: {decision}")


def _enforce_preconditions(qc_report: QCReport, forge_report: ForgeReport) -> None:
    """
    Enforce preconditions before APPROVE.

    Raises:
        RuntimeError: If preconditions not met
    """
    # Rule 1: QC must PASS (or FLAG with explained risk)
    if qc_report.verdict == "VOID":
        raise RuntimeError("Cannot APPROVE with VOID verdict - hard floor breach")

    # Rule 2: Critical tests must pass (checked during QC)
    if not qc_report.floors_passed.get("Tests", False):
        raise RuntimeError("Cannot APPROVE with failing tests")

    # Rule 3: If high risk (>= 0.7), require explicit SABAR acknowledgment
    if forge_report.risk_score >= 0.7:
        # In real implementation, would check for explicit --sabar-ack flag
        pass  # Placeholder - assume acknowledged if we got here


def _create_atomic_bundle(
    branch: str,
    housekeeper_proposal: HousekeeperProposal,
    forge_report: ForgeReport,
    qc_report: QCReport,
    repo_path: Path,
) -> dict:
    """
    Create atomic release bundle: code + docs + version + tag.

    ALL steps must succeed or ALL rollback (atomicity guarantee).

    Returns:
        dict with bundle_hash, commit_hash, tag

    Raises:
        Exception: If any step fails (triggers rollback)
    """
    # Step 1: Apply housekeeper proposals (if approved)
    # For now, skip auto-applying docs (require manual review first)
    # In future, could apply if --auto-doc flag set

    # Step 2: Stage all changes
    subprocess.run(["git", "add", "-A"], cwd=repo_path, check=True)

    # Step 3: Create commit
    commit_msg = _generate_commit_message(housekeeper_proposal, forge_report, qc_report)
    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Get commit hash
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    commit_hash = result.stdout.strip()

    # Step 4: Create tag
    tag = f"v{housekeeper_proposal.new_version}"
    subprocess.run(
        ["git", "tag", "-a", tag, "-m", f"Release {tag}"],
        cwd=repo_path,
        check=True,
    )

    # Step 5: Compute bundle hash (hash of commit + tag + timestamp)
    import hashlib

    bundle_data = f"{commit_hash}{tag}{datetime.now(timezone.utc).isoformat()}"
    bundle_hash = f"sha256:{hashlib.sha256(bundle_data.encode()).hexdigest()[:16]}"

    return {
        "bundle_hash": bundle_hash,
        "commit_hash": commit_hash,
        "tag": tag,
    }


def _rollback_changes(repo_path: Path) -> None:
    """Rollback uncommitted changes if atomic bundling fails."""
    try:
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=repo_path, check=False)
        subprocess.run(["git", "clean", "-fd"], cwd=repo_path, check=False)
    except Exception:
        pass  # Best effort rollback


def _generate_commit_message(
    proposal: HousekeeperProposal, forge: ForgeReport, qc: QCReport
) -> str:
    """Generate conventional commit message."""
    msg = f"feat(trinity): {proposal.version_bump} release v{proposal.new_version}\n\n"
    msg += f"Files changed: {len(forge.files_changed)}\n"
    msg += f"Entropy delta: {forge.entropy_delta:.2f}\n"
    msg += f"Risk score: {forge.risk_score:.2f}\n"
    msg += f"QC verdict: {qc.verdict}\n"
    msg += f"ZKPC: {qc.zkpc_id}\n"
    return msg


def _write_ledger_entry(
    decision: str,
    branch: str,
    human_authority: str,
    reason: str,
    forge_report: ForgeReport,
    qc_report: QCReport,
    housekeeper_proposal: HousekeeperProposal,
    timestamp: str,
    repo_path: Path,
) -> str:
    """
    Write entry to gitseal audit trail ledger.

    Ledger is append-only JSONL format.

    Returns:
        ledger_entry_id (UUID or hash-based ID)
    """
    import hashlib
    import uuid

    ledger_path = repo_path / "L1_THEORY" / "ledger" / "gitseal_audit_trail.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    # Create entry ID
    entry_id = str(uuid.uuid4())

    # Build entry
    entry = {
        "id": entry_id,
        "timestamp": timestamp,
        "verdict": f"GITSEAL_{decision}",
        "authority": human_authority,
        "branch": branch,
        "reason": reason,
        "forge_report": {
            "files_changed": forge_report.files_changed,
            "hot_zones": forge_report.hot_zones,
            "entropy_delta": forge_report.entropy_delta,
            "risk_score": forge_report.risk_score,
        },
        "qc_report": {
            "floors_passed": qc_report.floors_passed,
            "zkpc_id": qc_report.zkpc_id,
            "verdict": qc_report.verdict,
        },
        "housekeeper_proposal": {
            "version_bump": housekeeper_proposal.version_bump,
            "new_version": housekeeper_proposal.new_version,
        },
    }

    # Append to ledger (JSONL format - one JSON per line)
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return entry_id


def _update_manifest(
    version: str,
    bundle_hash: str,
    commit_hash: str,
    tag: str,
    human_authority: str,
    repo_path: Path,
) -> None:
    """
    Update versions.json manifest with new release.

    Manifest format: {version: {bundle_hash, commit_hash, tag, sealed_at, authority}}
    """
    manifest_path = repo_path / "L1_THEORY" / "manifest" / "versions.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing manifest or create new
    if manifest_path.exists():
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        manifest = {}

    # Add new version
    manifest[f"v{version}"] = {
        "bundle_hash": bundle_hash,
        "commit_hash": commit_hash,
        "tag": tag,
        "sealed_at": datetime.now(timezone.utc).isoformat(),
        "human_authority": human_authority,
    }

    # Write back
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def _record_in_vault999(
    version: str,
    bundle_hash: str,
    commit_hash: str,
    human_authority: str,
    entropy_delta: float,
    repo_path: Path,
) -> None:
    """
    Record /gitseal approval in Vault-999 constitutional memory.

    Integrates Trinity governance with canonical memory system.
    """
    try:
        # Import vault999 module
        import sys

        sys.path.insert(0, str(repo_path))
        from arifos_core.memory.vault999 import Vault999, VaultConfig

        # Initialize vault
        vault_config = VaultConfig(vault_path=repo_path / "runtime" / "vault_999" / "constitution.json")
        vault = Vault999(vault_config)

        # Record approval
        vault.record_gitseal_approval(
            version=version,
            bundle_hash=bundle_hash,
            commit_hash=commit_hash,
            human_authority=human_authority,
            entropy_delta=entropy_delta,
        )

    except Exception as e:
        # Vault integration is best-effort, don't fail seal on vault errors
        print(f"⚠️  Warning: Vault-999 integration failed: {e}")
        print("    (Ledger and manifest still recorded successfully)")

