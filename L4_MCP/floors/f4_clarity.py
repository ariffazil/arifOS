"""F4: Clarity (ΔS) floor."""

from typing import Any
from L4_MCP.apex.schema import ActionClass, Caller


def check(req: Any, caller: Caller, action_class: ActionClass) -> bool:
    """Floor 4: Clarity - ensures response reduces entropy.
    Returns True if floor TRIGGERED (violation detected)."""
    return False  # Stub: Would measure ΔS via compression
