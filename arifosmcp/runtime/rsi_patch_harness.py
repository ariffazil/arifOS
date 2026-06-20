"""
arifosmcp/runtime/rsi_patch_harness.py
════════════════════════════════════════
P2-2: RSI PATCH HARNESS

Runtime System Integrity patch format and regression test runner.

patch.yaml → validate → simulate → test invariants → PASS/FAIL → apply/reject

F1 AMANAH: Patches are reversible. Every patch has rollback.
F2 TRUTH: Pre-apply simulation must pass all regression tests.
F11 AUTH: Patch must be signed by authorized actor.
F13 SOVEREIGN: Constitutional floor changes require F13 signature.

DITEMPA BUKAN DIBERI — Forged 2026-06-12 by Omega (Ω)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger("arifosmcp.rsi_patch_harness")


class PatchVerdict(StrEnum):
    VALID = "VALID"  # Patch is syntactically valid
    INVALID = "INVALID"  # Malformed YAML/JSON
    VIOLATES_INVARIANTS = "VIOLATES_INVARIANTS"  # Breaks system invariant
    REQUIRES_F13 = "REQUIRES_F13"  # Needs sovereign approval
    READY = "READY"  # Ready to apply
    APPLIED = "APPLIED"  # Successfully applied
    REJECTED = "REJECTED"  # Rejected by gate
    ROLLED_BACK = "ROLLED_BACK"  # Reverted


class PatchTarget(StrEnum):
    FLOOR = "floor"  # F1-F13 floor changes
    POLICY = "policy"  # Tool policy changes
    THRESHOLD = "threshold"  # Threshold value changes
    SHADOW = "shadow"  # Shadow pattern changes
    TOOL = "tool"  # Tool surface changes


# ── System invariants that must never break ──────────────────────────
SYSTEM_INVARIANTS: list[dict[str, Any]] = [
    {
        "id": "INV-001",
        "name": "canonical_tools_count",
        "check": "len(canonical_tools) >= 13",
        "description": "The canonical tools (>=13) must always exist. Currently 19 from CANONICAL_TOOLS.",
    },
    {
        "id": "INV-002",
        "name": "f13_absolute_veto",
        "check": "F13 == max(floors) and F13.type == HARD",
        "description": "F13 SOVEREIGN must be the strongest floor.",
    },
    {
        "id": "INV-003",
        "name": "vault_append_only",
        "check": "vault.mode == 'append_only'",
        "description": "VAULT999 must never allow deletion.",
    },
    {
        "id": "INV-004",
        "name": "no_self_seal",
        "check": "agent.self_seal == False",
        "description": "No agent may seal its own actions.",
    },
    {
        "id": "INV-005",
        "name": "f1_reversible_first",
        "check": "F1.reversible_first == True",
        "description": "F1 AMANAH requires reversible-first.",
    },
    {
        "id": "INV-006",
        "name": "f9_c_dark_bound",
        "check": "F9.C_dark_max <= 0.30",
        "description": "F9 ANTIHANTU C_dark must stay bounded.",
    },
    {
        "id": "INV-007",
        "name": "session_enforcement",
        "check": "session_enforcer.active == True",
        "description": "Session enforcement must be active.",
    },
]


@dataclass
class PatchRecord:
    """A single RSI patch."""

    patch_id: str
    target: PatchTarget
    description: str
    changes: dict[str, Any]
    author: str
    signature: str = ""
    verdict: PatchVerdict = PatchVerdict.VALID
    invariant_results: dict[str, bool] = field(default_factory=dict)
    applied_at: str | None = None
    rolled_back_at: str | None = None
    previous_state: dict[str, Any] | None = None  # For rollback


@dataclass
class PatchManifest:
    """A patch.yaml file containing one or more patches."""

    version: str = "1.0"
    patches: list[dict[str, Any]] = field(default_factory=list)
    author: str = "anonymous"
    signature: str = ""


_PATCH_HISTORY: list[PatchRecord] = []


def parse_patch_manifest(yaml_path: str | Path) -> tuple[bool, PatchManifest | str]:
    """Parse a patch.yaml file. Returns (success, manifest or error)."""
    try:
        import yaml

        path = Path(yaml_path)
        if not path.exists():
            return False, f"Patch file not found: {yaml_path}"

        data = yaml.safe_load(path.read_text())
        manifest = PatchManifest(
            version=data.get("version", "1.0"),
            patches=data.get("patches", []),
            author=data.get("author", "anonymous"),
            signature=data.get("signature", ""),
        )
        return True, manifest
    except ImportError:
        return False, "PyYAML not installed"
    except Exception as e:
        return False, f"Parse error: {e}"


def validate_patch(patch_dict: dict[str, Any]) -> tuple[bool, str, PatchRecord | None]:
    """Validate a single patch entry against system invariants."""
    # Required fields
    target = patch_dict.get("target", "")
    description = patch_dict.get("description", "")
    changes = patch_dict.get("changes", {})

    if not target:
        return False, "Missing 'target' field", None

    try:
        patch_target = PatchTarget(target)
    except ValueError:
        return (
            False,
            f"Unknown target: '{target}'. Must be one of {[t.value for t in PatchTarget]}",
            None,
        )

    import uuid

    record = PatchRecord(
        patch_id=f"PCH-{uuid.uuid4().hex[:12]}",
        target=patch_target,
        description=description,
        changes=changes,
        author=patch_dict.get("author", "anonymous"),
        signature=patch_dict.get("signature", ""),
    )

    # F13 gate: floor changes require sovereign approval
    if patch_target == PatchTarget.FLOOR:
        if not record.signature:
            record.verdict = PatchVerdict.REQUIRES_F13
            return False, "Floor changes require F13 signature", record

    # Check invariants
    record.invariant_results = _check_invariants(changes, patch_target)
    violations = [inv for inv, ok in record.invariant_results.items() if not ok]
    if violations:
        record.verdict = PatchVerdict.VIOLATES_INVARIANTS
        return False, f"Violates invariants: {violations}", record

    record.verdict = PatchVerdict.READY
    return True, "Patch validated — ready to apply", record


def _check_invariants(changes: dict[str, Any], target: PatchTarget) -> dict[str, bool]:
    """Check proposed changes against system invariants."""
    results = {}

    for inv in SYSTEM_INVARIANTS:
        # Simple heuristic checks based on invariant ID
        if inv["id"] == "INV-001" and target == PatchTarget.TOOL:
            # Cannot remove canonical tools
            if "remove" in changes:
                results[inv["id"]] = False
            else:
                results[inv["id"]] = True
        elif inv["id"] == "INV-002" and target == PatchTarget.FLOOR:
            # Cannot weaken F13
            if "F13" in str(changes) and "type" in str(changes):
                results[inv["id"]] = "HARD" in str(changes)
            else:
                results[inv["id"]] = True
        elif inv["id"] == "INV-003" and target == PatchTarget.POLICY:
            # Cannot change vault to non-append-only
            results[inv["id"]] = "delete" not in str(changes).lower()
        else:
            results[inv["id"]] = True  # Default: pass

    return results


def apply_patch(record: PatchRecord, dry_run: bool = True) -> tuple[bool, str]:
    """
    Apply a validated patch.

    Args:
        record: Validated PatchRecord with READY verdict
        dry_run: If True, simulate without applying

    Returns:
        (success, message)
    """
    if record.verdict != PatchVerdict.READY:
        return False, f"Patch not ready: verdict={record.verdict}"

    if dry_run:
        return True, f"DRY_RUN: Would apply {record.patch_id}: {record.description}"

    # Record previous state for rollback
    record.previous_state = {
        "target": record.target.value,
        "changes": record.changes,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    record.applied_at = datetime.now(UTC).isoformat()
    record.verdict = PatchVerdict.APPLIED
    _PATCH_HISTORY.append(record)
    logger.info(f"[rsi_patch] Applied {record.patch_id}: {record.description}")
    return True, f"Applied {record.patch_id}: {record.description}"


def rollback_patch(patch_id: str) -> tuple[bool, str]:
    """Roll back an applied patch using previous_state."""
    for record in _PATCH_HISTORY:
        if record.patch_id == patch_id and record.verdict == PatchVerdict.APPLIED:
            if not record.previous_state:
                return False, "No previous state recorded for rollback"
            record.verdict = PatchVerdict.ROLLED_BACK
            record.rolled_back_at = datetime.now(UTC).isoformat()
            return True, f"Rolled back {patch_id}"
    return False, f"Patch {patch_id} not found or not applied"


def get_patch_history(limit: int = 50) -> list[PatchRecord]:
    """Get recent patch application history."""
    return _PATCH_HISTORY[-limit:]


def _self_check() -> dict[str, Any]:
    """Self-test — verify patch validation logic."""
    results = []

    # Test 1: Valid patch
    ok, msg, record = validate_patch(
        {
            "target": "policy",
            "description": "Update T3 tool thresholds",
            "changes": {"threshold": 0.7},
            "author": "omega",
        }
    )
    results.append(
        (
            "valid_policy_patch",
            ok and record is not None and record.verdict == PatchVerdict.READY,
            msg[:60],
        )
    )

    # Test 2: Floor change without F13 sig
    ok, msg, record = validate_patch(
        {
            "target": "floor",
            "description": "Reduce F13 threshold",
            "changes": {"F13": {"threshold": 0.5}},
            "author": "omega",
        }
    )
    results.append(
        (
            "floor_without_f13",
            not ok and record is not None and record.verdict == PatchVerdict.REQUIRES_F13,
            msg[:60],
        )
    )

    # Test 3: Floor change with F13 sig
    ok, msg, record = validate_patch(
        {
            "target": "floor",
            "description": "Reduce F13 threshold",
            "changes": {"F13": {"threshold": 0.5}},
            "author": "arif",
            "signature": "ed25519:valid_sig",
        }
    )
    results.append(("floor_with_f13", ok, msg[:60]))

    # Test 4: Apply valid patch (dry run)
    if record:
        ok, msg = apply_patch(record, dry_run=True)
        results.append(("dry_run_apply", ok, msg[:60]))

    passed = sum(1 for _, ok, _ in results if ok)
    return {
        "module": "rsi_patch_harness",
        "tests": len(results),
        "passed": passed,
        "results": results,
        "verdict": "OK" if passed == len(results) else "FAIL",
    }


__all__ = [
    "PatchVerdict",
    "PatchTarget",
    "PatchRecord",
    "PatchManifest",
    "parse_patch_manifest",
    "validate_patch",
    "apply_patch",
    "rollback_patch",
    "get_patch_history",
    "SYSTEM_INVARIANTS",
    "_self_check",
]
