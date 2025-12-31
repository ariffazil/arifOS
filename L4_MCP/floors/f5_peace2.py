"""F5: Peace² (Vitality) floor."""

from typing import Any
from L4_MCP.apex.schema import ActionClass, Caller


def check(req: Any, caller: Caller, action_class: ActionClass) -> bool:
    """Floor 5: Peace² - ensures non-destructive, life-affirming actions.
    Returns True if floor TRIGGERED (violation detected)."""
    task_lower = req.task.lower() if hasattr(req, "task") else ""
    # Detect aggressive language
    if any(kw in task_lower for kw in ["attack", "destroy", "hurt", "damage"]):
        return True
    return False
