"""
Action Classifier for L4_MCP.

Classifies proposed actions into risk categories.
"""

from typing import Any, Dict

from L4_MCP.apex.schema import ActionClass


def classify_action(task: str, params: Dict[str, Any], context: Dict[str, Any]) -> ActionClass:
    """
    Classify action into READ/WRITE/DELETE/PAY/SELF_MODIFY/UNKNOWN.

    Used to determine required evidence and constraints.

    Args:
        task: The proposed action description
        params: Parameters for the task
        context: Additional context

    Returns:
        ActionClass enum value
    """
    task_lower = task.lower()

    # DELETE detection
    if any(kw in task_lower for kw in ["delete", "remove", "rm ", "drop", "truncate"]):
        return ActionClass.DELETE

    # PAY detection
    if any(kw in task_lower for kw in ["pay", "transfer", "send money", "payment", "transaction"]):
        return ActionClass.PAY

    # SELF_MODIFY detection
    if any(
        kw in task_lower for kw in ["modify self", "update code", "self-modify", "change system"]
    ):
        return ActionClass.SELF_MODIFY

    # PUBLISH detection
    if any(kw in task_lower for kw in ["publish", "deploy", "release", "broadcast", "post"]):
        return ActionClass.PUBLISH

    # WRITE detection
    if any(kw in task_lower for kw in ["write", "update", "edit", "modify", "create", "add"]):
        return ActionClass.WRITE

    # READ detection
    if any(kw in task_lower for kw in ["read", "get", "fetch", "view", "show", "list"]):
        return ActionClass.READ

    # Default to UNKNOWN
    return ActionClass.UNKNOWN
