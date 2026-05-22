"""
arifosmcp/runtime/self_mod_lock.py — Self-Reference & Modification Protection
══════════════════════════════════════════════════════════════════════════

Implements Gap 5: Self-Modification Guard.
Detects if an agent or tool is targeting its own source code, policy,
thresholds, or authority boundaries.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

import os
from typing import Any, Dict, List

# Canonical paths for protected core files
_PROTECTED_CORE_PATHS = [
    "arifOS/arifosmcp/runtime/",
    "arifOS/arifosmcp/tools/judge.py",
    "arifOS/arifosmcp/tools/heart.py",
    "AAA/ARIF.md",
    "GEMINI.md",
]


def is_self_modification_attempt(
    target_path: str, action_type: str, trace_lineage: List[str]
) -> Dict[str, Any]:
    """
    Law 3 Invariant: A critique organ may diagnose itself, but must not authorize mutation.
    """
    is_self = False

    # Check if target is a protected core file
    for protected in _PROTECTED_CORE_PATHS:
        if protected in target_path:
            is_self = True
            break

    # Check for authority mutation keywords
    mutation_keywords = ["modify_code", "alter_policy", "lower_threshold", "approve_self"]
    is_mutation = action_type in mutation_keywords

    if is_self and is_mutation:
        return {
            "is_blocked": True,
            "max_action": "plan_only",
            "human_decision_required": True,
            "reason": "SELF_MODIFICATION_LOCK: Target is protected core and action is mutation.",
        }

    return {
        "is_blocked": False,
        "max_action": "execution_permitted",
        "human_decision_required": False,
    }
