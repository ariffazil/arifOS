"""F6 P0/P3 — execution-boundary authority guard for the forge path.

The 2026-10-26 baseline probe found `authority_binding.check_binding()` built
and tested but with **zero live call sites** in the kernel — a dead seam. This
module is the caller. It is wired into `_arif_forge_execute_tool` (tools.py)
before any governed mutation is dispatched.

Authority is checked at THREE levels:

  1. FLAG — `ARIFOS_F6_BINDING_ENFORCE` (default "0"). Off = observe only:
     the decision is computed and annotated, never blocking. On = fail-closed.
  2. BINDING — a mutating forge call must carry `f6_binding_id` in its JSON
     manifest; absence is REJECT_BYPASS, not "no policy configured".
  3. REQUEST — `check_binding` re-verifies scope, resource, parameters,
     expiry, revocation, replay nonce, delegation chain and post-approval
     state at execution time. Any non-ALLOW decision blocks the call.

An optional `approved_action_hash` becomes the state guard: the manifest hash
must equal the hash that was approved, otherwise the action changed after
approval (REJECT_STATE). No guard = UNKNOWN = blocked when enforcing.

This is a control over SYSTEM behaviour. It never scores a human.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable, Optional

from arifosmcp.runtime.f6.authority_binding import (
    DEFAULT_DB as DEFAULT_BINDING_DB,
)
from arifosmcp.runtime.f6.authority_binding import (
    ActionRequest,
    AuthorityBinding,
    BindingStore,
    BindingVerdict,
    check_binding,
)

SCHEMA = "arifos.f6.execution_boundary.v1"
ENFORCE_ENV = "ARIFOS_F6_BINDING_ENFORCE"
DB_ENV = "ARIFOS_F6_BINDING_DB"

# Only action-producing modes are in scope. query/recall/dry_run are observation.
MUTATING_MODES = frozenset({"engineer", "write", "generate", "commit"})

StateGuard = Callable[[ActionRequest, AuthorityBinding], tuple[bool, str]]
Result = dict[str, Any]


def _enforcing(explicit: Optional[bool] = None) -> bool:
    if explicit is not None:
        return bool(explicit)
    return os.environ.get(ENFORCE_ENV, "0").strip() == "1"


def _manifest_dict(manifest: str) -> dict[str, Any]:
    try:
        data = json.loads(manifest) if manifest else {}
    except (json.JSONDecodeError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def _manifest_state_guard(manifest: str, approved_action_hash: str) -> StateGuard:
    """State guard: the action at execution time must hash to the approved hash."""

    def _guard(_request: ActionRequest, _binding: AuthorityBinding) -> tuple[bool, str]:
        actual = hashlib.sha256((manifest or "").encode("utf-8")).hexdigest()
        if actual == approved_action_hash:
            return True, "manifest hash matches approved_action_hash"
        return (
            False,
            "manifest changed after approval: "
            f"sha256={actual[:16]}… != approved={approved_action_hash[:16]}…",
        )

    return _guard


def _build_request(data: dict[str, Any], actor_id: Optional[str]) -> ActionRequest:
    return ActionRequest(
        binding_id=str(data.get("f6_binding_id") or ""),
        actor_id=str(actor_id or data.get("f6_actor_id") or ""),
        action=str(data.get("f6_action") or data.get("action") or ""),
        resource=str(
            data.get("f6_resource")
            or data.get("resource")
            or data.get("path")
            or data.get("repo")
            or ""
        ),
        params=dict(data.get("f6_params") or data.get("params") or {}),
        scope=(str(data["f6_scope"]) if data.get("f6_scope") is not None else None),
    )


def guard_forge_call(
    *,
    mode: str,
    manifest: str = "",
    actor_id: Optional[str] = None,
    approved_action_hash: Optional[str] = None,
    store: Optional[BindingStore] = None,
    state_guard: Optional[StateGuard] = None,
    enforce: Optional[bool] = None,
) -> Result:
    """Return the execution-boundary decision for one forge call.

    `blocked=True` means the caller MUST NOT dispatch the mutation.
    Never raises: an evaluator failure becomes UNKNOWN, which blocks when
    enforcing and is annotated when observing.
    """
    enforcing = _enforcing(enforce)
    out: Result = {
        "schema": SCHEMA,
        "mode": mode,
        "enforced": enforcing,
        "blocked": False,
        "decision": BindingVerdict.UNKNOWN,
        "reason": "",
        "binding_id": "",
        "checked_at_execution_time": True,
    }
    if mode not in MUTATING_MODES:
        out["decision"] = "NOT_APPLICABLE"
        out["reason"] = f"mode '{mode}' is observation, not mutation — out of F6 binding scope"
        return out

    data = _manifest_dict(manifest)
    request = _build_request(data, actor_id)
    out["binding_id"] = request.binding_id

    if not request.binding_id:
        out["decision"] = BindingVerdict.REJECT_BYPASS
        out["reason"] = (
            "mutating forge call carries no f6_binding_id in its manifest — "
            "execution boundary cannot verify authority"
        )
        out["blocked"] = enforcing
        if not enforcing:
            out["reason"] += " (observe-only; not blocked)"
        return out

    try:
        binding_store = store or BindingStore(Path(os.environ.get(DB_ENV) or DEFAULT_BINDING_DB))
        guard = state_guard
        if guard is None and approved_action_hash:
            guard = _manifest_state_guard(manifest, approved_action_hash)
        verdict = check_binding(request, binding_store, state_guard=guard)
        out["decision"] = verdict.get("decision", BindingVerdict.UNKNOWN)
        out["reason"] = verdict.get("reason", "")
        out["blocked"] = enforcing and out["decision"] != BindingVerdict.ALLOW
        if not enforcing and out["decision"] != BindingVerdict.ALLOW:
            out["reason"] += " (observe-only; not blocked)"
    except Exception as exc:  # evaluator failure is UNKNOWN, never PASS
        out["decision"] = BindingVerdict.UNKNOWN
        out["reason"] = f"binding evaluator error: {type(exc).__name__}: {exc}"[:300]
        out["blocked"] = enforcing
    return out


__all__ = ["guard_forge_call", "MUTATING_MODES", "ENFORCE_ENV", "SCHEMA"]
