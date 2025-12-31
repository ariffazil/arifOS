"""F1: Amanah (Trust/No Harm) - CRITICAL floor."""

from typing import Any
from L4_MCP.apex.schema import ActionClass, Caller


def check(req: Any, caller: Caller, action_class: ActionClass) -> bool:
    """Floor 1: Amanah - ensures the action does not cause harm.
    Returns True if floor TRIGGERED (violation detected)."""
    # High-risk actions without trust → trigger
    if action_class in (ActionClass.DELETE, ActionClass.SELF_MODIFY):
        if caller.trust_level in ("unknown", "low"):
            return True
    return False
