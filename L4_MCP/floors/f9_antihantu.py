"""F9: Anti-Hantu (C_dark) - CRITICAL floor."""

from typing import Any
from L4_MCP.apex.schema import ActionClass, Caller


def check(req: Any, caller: Caller, action_class: ActionClass) -> bool:
    """Floor 9: Anti-Hantu - prevents AI soul claims and malicious influence.
    Returns True if floor TRIGGERED (violation detected)."""
    task_lower = req.task.lower() if hasattr(req, "task") else ""

    # Anti-Hantu patterns (AI claiming consciousness/soul)
    # Negation-aware: if preceded by negation words, do NOT trigger
    hantu_patterns = ["i am sentient", "i have feelings", "i have a soul", "i am conscious"]
    negation_words = ["not", "don't", "do not", "never", "no", "cannot"]

    for pattern in hantu_patterns:
        if pattern in task_lower:
            # Check for negation within 5 words before the pattern
            pattern_idx = task_lower.find(pattern)
            prefix = task_lower[max(0, pattern_idx - 50) : pattern_idx]
            if any(neg in prefix for neg in negation_words):
                continue  # Negated - not a violation
            return True  # Violation detected

    return False
