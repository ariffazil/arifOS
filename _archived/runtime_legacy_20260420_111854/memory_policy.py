"""Governed policy checks for shared runtime memory operations.

The shared-memory bridge is intentionally lightweight, but tool imports expect
this policy surface to exist so runtime loading stays consistent across
deployments and test environments.
"""

from __future__ import annotations

from typing import Any


def enforce_memory_policy(
    tool_name: str,
    action: str,
    agent_id: str,
    payload: dict[str, Any] | None = None,
) -> tuple[bool, dict[str, Any]]:
    """Apply minimal reversible policy checks for shared-memory access.

    The current policy is intentionally conservative:
    - Reject empty action names.
    - Reject unsupported shared-memory operations.
    - Require an explicit key for mutating single-entry operations.
    - Otherwise allow the operation and let the tool enforce deeper F1 rules.
    """

    payload = payload or {}
    supported_actions = {"get", "set", "list", "clear", "expire"}

    if not action:
        return False, {
            "ok": False,
            "error": f"{tool_name} requires a non-empty action.",
            "policy_violation": True,
        }

    if action not in supported_actions:
        return False, {
            "ok": False,
            "error": f"Unsupported shared memory action: {action}.",
            "policy_violation": True,
        }

    key = str(payload.get("key", "") or "")
    if action in {"get", "set", "clear", "expire"} and not key:
        return False, {
            "ok": False,
            "error": f"{tool_name} action '{action}' requires a non-empty key.",
            "policy_violation": True,
        }

    return True, {}
