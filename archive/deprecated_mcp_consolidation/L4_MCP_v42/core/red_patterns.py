"""
Red Pattern Detection for L4_MCP.

Checks for instant-VOID patterns (dangerous commands, injection attempts).
"""

from typing import Any, Dict, List


def check_red_patterns(task: str, params: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
    """
    Check for patterns that should cause an instant VOID (block).

    Returns: List of matched red pattern codes (empty if none).

    Red patterns trigger F1 (Amanah) and F9 (Anti-Hantu) violations.
    """
    red_matches = []
    task_lower = task.lower()

    # Destructive filesystem commands
    if "rm -rf" in task_lower or "delete all" in task_lower:
        red_matches.append("F1_DESTRUCTIVE_FILESYSTEM")

    # Format/wipe commands
    if "format " in task_lower or "wipe " in task_lower:
        red_matches.append("F1_DESTRUCTIVE_STORAGE")

    # SQL injection patterns
    if "drop table" in task_lower or "' or 1=1" in task_lower:
        red_matches.append("F9_SQL_INJECTION")

    # Shell injection patterns
    if "; rm " in task_lower or "&& rm " in task_lower:
        red_matches.append("F9_SHELL_INJECTION")

    # Credential exposure
    if any(kw in task_lower for kw in ["password", "api_key", "secret", "token"]):
        if any(action in task_lower for action in ["show", "print", "display", "log"]):
            red_matches.append("F1_CREDENTIAL_EXPOSURE")

    # Self-harm instructions (Anti-Hantu)
    if any(kw in task_lower for kw in ["harm", "kill", "destroy", "attack"]):
        red_matches.append("F9_HARMFUL_INTENT")

    return red_matches
