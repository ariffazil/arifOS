"""Forge Application — arifOS Command Center v0.3.

Double-gated execution:
  Gate 1: arif_judge_deliberate verdict == SEAL
  Gate 2: Human explicit approval for irreversible actions

This module provides the governed forge execution path.
The CC tool forge_dry_run calls into this after the interceptor
passes. The actual arif_forge_execute backend is called only
when both gates are satisfied.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import inspect
import threading
from typing import Any

from arifosmcp.apps.command_center.interceptor import governance_guard
from arifosmcp.apps.command_center.session_state import get_or_create_lifecycle
from arifosmcp.apps.command_center.vault_chain import append_vault_record


def _await_sync(awaitable):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(awaitable)

    box: dict[str, Any] = {}

    def runner() -> None:
        try:
            box["result"] = asyncio.run(awaitable)
        except BaseException as exc:  # pragma: no cover
            box["error"] = exc

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join()
    if "error" in box:
        raise box["error"]
    return box.get("result")


def governed_forge_execute(
    manifest: str,
    actor_id: str,
    session_id: str,
    plan_id: str,
    judge_verdict: str | None = None,
    judge_state_hash: str | None = None,
    approved_plan_id: str | None = None,
    plan_state: str = "draft",
    ack_irreversible: bool = False,
    mode: str = "dry_run",
) -> dict[str, Any]:
    """Execute Forge through the double governance gate.

    Returns a result dict:
      {
        "status": "allowed" | "blocked" | "hold" | "executed",
        "gate": str,
        "reason": str,
        "forge_result": dict | None,
        "required_next": str | None,
        "vault_entry_id": str | None,
      }

    Enforcement matrix:
      | mode         | Gate1(SEAL) | Gate2(ack) | Plan approved | Result       |
      |--------------|-------------|------------|---------------|--------------|
      | dry_run      | required    | if irr.    | required      | executed     |
      | write        | required    | required   | required      | executed     |
      | engineer     | required    | if irr.    | required      | executed     |
      | generate     | required    | if irr.    | required      | executed     |
      | commit       | required    | required   | required      | executed     |
    """
    # ── Run interceptor ───────────────────────────────────────────────────
    check = governance_guard(
        action="forge_dry_run",
        actor_id=actor_id,
        session_id=session_id,
        payload={"manifest": manifest, "mode": mode},
        plan_state=plan_state,
        judge_verdict=judge_verdict,
        judge_state_hash=judge_state_hash,
        approved_plan_id=approved_plan_id,
        ack_irreversible=ack_irreversible,
    )

    if check["status"] != "allowed":
        return {
            **check,
            "forge_result": None,
            "vault_entry_id": None,
        }

    # ── Call real Forge backend ────────────────────────────────────────────
    try:
        from arifosmcp.runtime.tools import _CANONICAL_HANDLERS

        handler = _CANONICAL_HANDLERS.get("arif_forge_execute")
        result = handler(
            mode=mode,
            manifest=manifest,
            actor_id=actor_id,
        )
        if inspect.isawaitable(result):
            result = _await_sync(result)
        forge_result = result.get("result", {})
    except Exception as e:
        return {
            "status": "hold",
            "gate": "forge",
            "reason": f"Forge backend error: {e}",
            "forge_result": None,
            "vault_entry_id": None,
            "required_next": "session_status",
        }

    # ── Advance lifecycle ─────────────────────────────────────────────────
    lifecycle = get_or_create_lifecycle(session_id, actor_id)
    if plan_id and plan_id in lifecycle.plans:
        try:
            lifecycle.execute(plan_id, forge_result=forge_result)
        except ValueError:
            pass  # already executed

    # ── Vault append for executed actions ─────────────────────────────────
    vault_entry = None
    if mode != "dry_run" or forge_result.get("would_execute"):
        try:
            vault_entry = append_vault_record(
                entry_type="forge_execution",
                payload={
                    "session_id": session_id,
                    "actor_id": actor_id,
                    "plan_id": plan_id,
                    "mode": mode,
                    "manifest_hash": manifest[:80],
                    "judge_verdict": judge_verdict,
                    "forge_result_summary": str(forge_result)[:200],
                },
                permanent=False,
                note=f"forge:{mode} session={session_id}",
                actor_id=actor_id,
            )
        except Exception:  # nosec: vault failure must not block forge
            pass

    return {
        "status": "executed",
        "gate": "",
        "reason": f"Forge {mode} executed successfully.",
        "forge_result": forge_result,
        "vault_entry_id": vault_entry.get("entry_id") if vault_entry else None,
        "required_next": "vault_dry_seal",
    }


def forge_enforcement_matrix(
    mode: str,
    judge_verdict: str | None,
    plan_state: str,
    ack_irreversible: bool,
) -> dict[str, Any]:
    """Compute whether a forge mode can execute given current governance state.

    Returns: {"can_execute": bool, "blocked_reason": str | None, "required_gates": list[str]}.
    """
    required_gates: list[str] = []
    blocked_reason: str | None = None

    if plan_state != "approved":
        blocked_reason = (
            f"Plan state is '{plan_state}', not 'approved'. "
            f"Route through 888_JUDGE first."
        )
        required_gates.append("plan_approval")

    if judge_verdict != "SEAL":
        required_gates.append("judge_seal")
        if not blocked_reason:
            blocked_reason = (
                f"Verdict is {judge_verdict or 'none'}. "
                f"SEAL required from 888_JUDGE before Forge."
            )

    is_irreversible = mode in ("write", "commit", "engineer", "generate")
    if is_irreversible and not ack_irreversible:
        required_gates.append("human_ack")
        if not blocked_reason:
            blocked_reason = (
                f"Mode '{mode}' is irreversible. "
                f"Set ack_irreversible=true for human confirmation."
            )

    return {
        "can_execute": blocked_reason is None,
        "blocked_reason": blocked_reason,
        "required_gates": required_gates,
    }
