"""F3: Tri-Witness floor."""

from typing import Any
from L4_MCP.apex.schema import ActionClass, Caller


def check(req: Any, caller: Caller, action_class: ActionClass) -> bool:
    """Floor 3: Tri-Witness - requires multi-source verification.
    Returns True if floor TRIGGERED (violation detected)."""
    return False  # Stub
