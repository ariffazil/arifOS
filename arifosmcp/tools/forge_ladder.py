"""
arifosmcp/tools/forge_ladder.py — 010_FORGE Governed Ladder
═══════════════════════════════════════════════════════════════

Splits the monolithic arif_forge_execute into a classification ladder:
  forge_query    → OBSERVE class — read-only introspection (always enabled)
  forge_plan     → REASON class — classify action, estimate blast radius
  forge_dry_run  → REASON class — simulate execution, produce diff preview

arif_forge_execute (v2) → MUTATE/ATOMIC class — gated by 888_JUDGE + ack_irreversible

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from arifosmcp.constitutional_map import CANONICAL_TOOLS, ToolStage
from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.tools import _ok, _hold
from arifosmcp.schemas.forge import (
    ForgeDryRunResult,
    ForgeErrorCode,
    ForgePlanResult,
    ForgeQueryResult,
    ToolManifest,
)

# ═══════════════════════════════════════════════════════════════════════════════
# WORKSPACE ROOT — filesystem jail for all forge operations
# ═══════════════════════════════════════════════════════════════════════════════

WORKSPACE_ROOT = Path("/root").resolve()

FORGE_DENY_LIST = [
    Path("/root/.secrets"),
    Path("/root/.ssh"),
    Path("/etc"),
    Path("/var/lib/docker"),
]

ALLOWED_COMMANDS = {
    "python": "/usr/bin/python3",
    "node": "/usr/bin/node",
    "npm": "/usr/bin/npm",
    "git": "/usr/bin/git",
    "pytest": "/usr/local/bin/pytest",
    "ruff": "/usr/local/bin/ruff",
    "make": "/usr/bin/make",
}

# ═══════════════════════════════════════════════════════════════════════════════
# TOOL MANIFESTS — INSPECTABLE METADATA
# ═══════════════════════════════════════════════════════════════════════════════

FORGE_QUERY_MANIFEST = ToolManifest(
    name="forge_query",
    version="0.2.0",
    stage=ToolStage.FORGE_EXECUTE,
    lane="AGI",
    safe_modes=["query"],
    dangerous_modes=[],
    requires_identity=False,
    requires_state_hash=False,
    requires_approval_for=[],
    side_effects=[],
    max_blast_radius="none",
)

FORGE_PLAN_MANIFEST = ToolManifest(
    name="forge_plan",
    version="0.2.0",
    stage=ToolStage.FORGE_EXECUTE,
    lane="AGI",
    safe_modes=["plan"],
    dangerous_modes=[],
    requires_identity=False,
    requires_state_hash=False,
    requires_approval_for=[],
    side_effects=[],
    max_blast_radius="none",
)

FORGE_DRY_RUN_MANIFEST = ToolManifest(
    name="forge_dry_run",
    version="0.2.0",
    stage=ToolStage.FORGE_EXECUTE,
    lane="AGI",
    safe_modes=["dry_run"],
    dangerous_modes=[],
    requires_identity=False,
    requires_state_hash=False,
    requires_approval_for=[],
    side_effects=[],
    max_blast_radius="none",
)

ARIF_FORGE_EXECUTE_MANIFEST = ToolManifest(
    name="arif_forge_execute",
    version="0.2.0",
    stage=ToolStage.FORGE_EXECUTE,
    lane="AGI",
    safe_modes=["query", "recall", "dry_run"],
    dangerous_modes=["engineer", "write", "generate", "commit", "deploy"],
    requires_identity=True,
    requires_state_hash=True,
    requires_approval_for=["write", "commit", "deploy"],
    side_effects=["filesystem", "git", "subprocess"],
    max_blast_radius="workspace",
)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: resolve and validate workspace path
# ═══════════════════════════════════════════════════════════════════════════════


def _resolve_cwd(cwd: str) -> Path:
    """Resolve cwd within workspace jail. Escapes return HOLD."""
    target = (WORKSPACE_ROOT / cwd).resolve()
    if not str(target).startswith(str(WORKSPACE_ROOT)):
        raise ValueError("cwd escapes workspace root")
    for deny in FORGE_DENY_LIST:
        if str(target).startswith(str(deny)):
            raise ValueError(f"cwd enters denied path: {deny}")
    return target


def _compute_plan_id(goal: str, actor_id: str | None) -> str:
    """Deterministic plan ID from goal + actor."""
    raw = f"{goal}:{actor_id or 'anonymous'}:{datetime.now(UTC).isoformat()}"
    return f"plan_{hashlib.sha256(raw.encode()).hexdigest()[:16]}"


# ═══════════════════════════════════════════════════════════════════════════════
# RUNG 1: forge_query — OBSERVE class, always enabled
# ═══════════════════════════════════════════════════════════════════════════════


def forge_query(
    manifest: str = "",
    query: str = "",
    cwd: str = ".",
    session_id: str | None = None,
    actor_id: str | None = None,
    _envelope: Any = None,
) -> ForgeQueryResult:
    """
    010_FORGE_QUERY: Read-only system introspection.

    Safe to call without approval. Produces no side effects.
    Returns workspace tree, system state, and query result.
    """
    start = time.perf_counter()
    ts = datetime.now(UTC).isoformat()

    floor_check = check_laws(
        "forge_query",
        {"query": query, "manifest": manifest, "cwd": cwd},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return ForgeQueryResult(
            verdict="HOLD",
            error_code=ForgeErrorCode.E_SIDE_EFFECTS_BLOCKED,
            query=query,
            result={},
            timestamp=ts,
            duration_ms=int((time.perf_counter() - start) * 1000),
        )

    try:
        target_cwd = _resolve_cwd(cwd)
    except ValueError as exc:
        return ForgeQueryResult(
            verdict="HOLD",
            error_code=ForgeErrorCode.E_WORKSPACE_ESCAPE,
            query=query,
            result={},
            timestamp=ts,
            duration_ms=int((time.perf_counter() - start) * 1000),
        )

    # Build workspace tree (shallow, safe)
    workspace_tree: list[dict[str, Any]] = []
    try:
        for entry in sorted(target_cwd.iterdir())[:50]:
            workspace_tree.append(
                {
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "size": entry.stat().st_size if entry.is_file() else None,
                }
            )
    except PermissionError:
        pass

    # System state (safe, read-only)
    system_state = {
        "workspace": str(target_cwd),
        "workspace_root": str(WORKSPACE_ROOT),
        "tool_manifest": FORGE_QUERY_MANIFEST.model_dump(),
    }

    return ForgeQueryResult(
        verdict="SEAL",
        query=query,
        result={
            "query_mode": True,
            "manifest_received": manifest,
            "workspace_readable": True,
        },
        workspace_tree=workspace_tree,
        system_state=system_state,
        timestamp=ts,
        duration_ms=int((time.perf_counter() - start) * 1000),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# RUNG 2: forge_plan — REASON class, always enabled
# ═══════════════════════════════════════════════════════════════════════════════


def forge_plan(
    goal: str = "",
    workspace: str = ".",
    session_id: str | None = None,
    actor_id: str | None = None,
    _envelope: Any = None,
) -> ForgePlanResult:
    """
    010_FORGE_PLAN: Classify action, estimate blast radius, produce plan.

    Safe to call without approval. Produces no side effects.
    """
    start = time.perf_counter()
    ts = datetime.now(UTC).isoformat()

    floor_check = check_laws(
        "forge_plan",
        {"goal": goal, "workspace": workspace},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return ForgePlanResult(
            verdict="HOLD",
            error_code=ForgeErrorCode.E_SIDE_EFFECTS_BLOCKED,
            goal=goal,
            timestamp=ts,
            duration_ms=int((time.perf_counter() - start) * 1000),
        )

    if not goal:
        return ForgePlanResult(
            verdict="HOLD",
            error_code=ForgeErrorCode.E_SYNTHESIS_EMPTY,
            goal=goal,
            timestamp=ts,
            duration_ms=int((time.perf_counter() - start) * 1000),
        )

    # Simple keyword-based classification
    action_str = goal.lower()
    dangerous_keywords = ["deploy", "restart", "delete", "drop", "rm -rf", "git push", "systemctl"]
    mutate_keywords = ["write", "modify", "create", "generate", "install", "commit"]

    if any(k in action_str for k in dangerous_keywords):
        action_class: Literal["OBSERVE", "REASON", "MUTATE", "ATOMIC"] = "ATOMIC"
        risk_tier = "critical"
        required_approval = True
        estimated_blast_radius = "system"
    elif any(k in action_str for k in mutate_keywords):
        action_class = "MUTATE"
        risk_tier = "medium"
        required_approval = True
        estimated_blast_radius = "workspace"
    elif any(k in action_str for k in ["query", "inspect", "read", "check", "status"]):
        action_class = "OBSERVE"
        risk_tier = "low"
        required_approval = False
        estimated_blast_radius = "none"
    else:
        action_class = "REASON"
        risk_tier = "low"
        required_approval = False
        estimated_blast_radius = "none"

    plan_id = _compute_plan_id(goal, actor_id)

    # Recommend tools based on classification
    required_tools = ["forge_query"]
    if action_class in ("MUTATE", "ATOMIC"):
        required_tools.extend(["forge_dry_run", "arif_heart_critique", "arif_judge_deliberate"])
    if action_class == "ATOMIC":
        required_tools.append("arif_forge_execute")

    return ForgePlanResult(
        verdict="SEAL",
        plan_id=plan_id,
        goal=goal,
        action_class=action_class,
        risk_tier=risk_tier,
        required_approval=required_approval,
        required_tools=required_tools,
        estimated_blast_radius=estimated_blast_radius,
        plan={
            "steps": [
                {"step": 1, "tool": "forge_query", "purpose": "introspect current state"},
                {"step": 2, "tool": "forge_dry_run", "purpose": "simulate action"},
                {"step": 3, "tool": "arif_heart_critique", "purpose": "ethical review"},
                {
                    "step": 4,
                    "tool": "arif_judge_deliberate",
                    "purpose": "constitutional authorization",
                },
                {"step": 5, "tool": "arif_forge_execute", "purpose": "execute approved plan"},
            ],
            "notes": f"Action classified as {action_class}. Blast radius: {estimated_blast_radius}.",
        },
        timestamp=ts,
        duration_ms=int((time.perf_counter() - start) * 1000),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# RUNG 3: forge_dry_run — REASON class, always enabled
# ═══════════════════════════════════════════════════════════════════════════════


def forge_dry_run(
    plan_id: str = "",
    manifest: str = "",
    cwd: str = ".",
    session_id: str | None = None,
    actor_id: str | None = None,
    _envelope: Any = None,
) -> ForgeDryRunResult:
    """
    010_FORGE_DRY_RUN: Simulate execution without mutation.

    Safe to call without approval. Produces no side effects.
    Returns diff preview, files touched, rollback plan.
    """
    start = time.perf_counter()
    ts = datetime.now(UTC).isoformat()

    floor_check = check_laws(
        "forge_dry_run",
        {"plan_id": plan_id, "manifest": manifest, "cwd": cwd},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return ForgeDryRunResult(
            verdict="HOLD",
            error_code=ForgeErrorCode.E_SIDE_EFFECTS_BLOCKED,
            plan_id=plan_id,
            timestamp=ts,
            duration_ms=int((time.perf_counter() - start) * 1000),
        )

    try:
        target_cwd = _resolve_cwd(cwd)
    except ValueError:
        return ForgeDryRunResult(
            verdict="HOLD",
            error_code=ForgeErrorCode.E_WORKSPACE_ESCAPE,
            plan_id=plan_id,
            timestamp=ts,
            duration_ms=int((time.perf_counter() - start) * 1000),
        )

    # Parse manifest for planned actions
    files_to_create: list[str] = []
    files_to_modify: list[str] = []
    files_to_delete: list[str] = []
    commands: list[list[str]] = []
    external_effects: list[str] = []

    # Simple heuristic: if manifest mentions file paths, classify them
    manifest_lower = manifest.lower()
    if "create" in manifest_lower or "write" in manifest_lower or "generate" in manifest_lower:
        files_to_create.append("<new file(s) from manifest>")
    if "modify" in manifest_lower or "update" in manifest_lower:
        files_to_modify.append("<existing file(s) from manifest>")
    if "delete" in manifest_lower or "remove" in manifest_lower:
        files_to_delete.append("<file(s) from manifest>")

    # Diff preview (placeholder — real diff would need manifest parser)
    diff_preview = f"""# Dry Run Plan: {plan_id or "unnamed"}
# Workspace: {target_cwd}
# Actor: {actor_id or "anonymous"}
# Manifest length: {len(manifest)} chars

## Planned Actions
- Files to create: {len(files_to_create)}
- Files to modify: {len(files_to_modify)}
- Files to delete: {len(files_to_delete)}

## Commands (simulated)
{chr(10).join("  $ " + " ".join(cmd) for cmd in commands) or "  (none parsed from manifest)"}

## External Effects
{chr(10).join("  - " + e for e in external_effects) or "  (none detected)"}

## Rollback Plan
  1. Identify modified files via git status
  2. git checkout -- <file> for each modified file
  3. rm <file> for each created file
  4. git stash pop if stash was created
"""

    return ForgeDryRunResult(
        verdict="SEAL",
        plan_id=plan_id,
        dry_run=True,
        commands=commands,
        files_to_create=files_to_create,
        files_to_modify=files_to_modify,
        files_to_delete=files_to_delete,
        external_effects=external_effects,
        rollback_plan=[
            "git status to identify changes",
            "git checkout -- <modified files>",
            "rm <created files>",
            "git stash pop if needed",
        ],
        diff_preview=diff_preview,
        timestamp=ts,
        duration_ms=int((time.perf_counter() - start) * 1000),
    )
