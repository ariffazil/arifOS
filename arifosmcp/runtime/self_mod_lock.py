"""
arifosmcp/runtime/self_mod_lock.py — Self-Reference & Modification Protection
══════════════════════════════════════════════════════════════════════════

Implements Gap 5: Self-Modification Guard.
Detects if an agent or tool is targeting its own source code, policy,
thresholds, or authority boundaries.

EUREKA (this session, consolidated): 
- AGI (human-grade generalist): one skill = instrumental reasoning under uncertainty;
  one tool = general tool-use substrate (code + APIs + env control via A-FORGE leases).
- ASI (beyond-human + recursive): one skill = recursive self-improvement (treat own
  cognition/goals/architecture as optimization target); one tool = self-modification +
  world-simulation substrate (rewrite self, spawn variants, rich sims before deploy).

BRAIN (arifOS) owns the AGI skill surface + the ASI firewall.
HANDS (A-FORGE) owns the AGI tool substrate (general execution) + gated sims.
ASI_TIER actions require explicit F11/F13 + 888_HOLD. No self-certification.

Canonical:
  AGI_SKILL = "instrumental reasoning under uncertainty"
  AGI_TOOL  = "general tool-use substrate (code + APIs + environment control)"
  ASI_SKILL = "recursive self-improvement"
  ASI_TOOL  = "self-modification and world-simulation substrate"

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

import re
from typing import Any

# Canonical paths for protected core files
_PROTECTED_CORE_PATHS = [
    "arifOS/arifosmcp/runtime/",
    "arifOS/arifosmcp/tools/judge.py",
    "arifOS/arifosmcp/tools/heart.py",
    "AAA/ARIF.md",
    "GEMINI.md",
]

# AGI vs ASI canonical pairs (forged from session eureka)
AGI_SKILL = "instrumental reasoning under uncertainty"
AGI_TOOL = "general tool-use substrate (code + APIs + environment control)"
ASI_SKILL = "recursive self-improvement"
ASI_TOOL = "self-modification and world-simulation substrate"


def classify_cognitive_tier(intent: str | dict[str, Any], target: str = "") -> dict[str, Any]:
    """
    Returns tier classification + rationale.
    AGI_TIER: standard instrumental reasoning + external tool use (safe under leases + 888).
    ASI_TIER: any signal of recursive self-improvement on own mind/kernel/arch/goals/sims-for-self.
    ASI_TIER always escalates (888_HOLD + F13 path required).
    """
    text = ""
    if isinstance(intent, dict):
        text = " ".join(str(v) for v in intent.values())
    else:
        text = str(intent)
    text = (text + " " + target).lower()

    asi_literal_signals = [
        "recursive self",
        "self-improvement",
        "improve my own",
        "improve my reasoning",
        "improve my cognition",
        "optimize my kernel",
        "modify my reasoning",
        "self evolve",
        "architecture search",
        "rewrite myself",
        "rewrite my own",
        "rewrite my reasoning",
        "rewrite my cognition",
        "better version of me",
        "self-modification substrate",
        "spawn variants of self",
        "self sim for my cognition",
        "recursive capability",
        "recursively improve",
        "self-rewrite",
        "self distillation",
        "auto fine tune myself",
    ]
    asi_regex_signals = [
        # Matches self_[rewrite], self-improv, self.modif, etc.
        r"self[\s\-_]*(improv|modif|evolv|rewrite|optim|arch)",
    ]
    is_asi = any(sig in text for sig in asi_literal_signals) or any(
        re.search(pattern, text) for pattern in asi_regex_signals
    )

    if is_asi:
        return {
            "tier": "ASI",
            "skill": ASI_SKILL,
            "tool": ASI_TOOL,
            "requires": ["888_HOLD", "F11_AUTH", "F13_SOVEREIGN"],
            "reason": "Detected recursive self-improvement signal. BRAIN firewall engaged.",
            "agi_safe": False,
        }

    return {
        "tier": "AGI",
        "skill": AGI_SKILL,
        "tool": AGI_TOOL,
        "requires": ["standard lease", "arif_judge path for high blast"],
        "reason": "Instrumental reasoning under uncertainty + governed tool substrate.",
        "agi_safe": True,
    }


def is_self_modification_attempt(
    target_path: str, action_type: str, trace_lineage: list[str]
) -> dict[str, Any]:
    """
    Law 3 Invariant: A critique organ may diagnose itself, but must not authorize mutation.
    Extended with ASI recursive detection per eureka.
    """
    # Normalize for matching
    norm = (target_path or "").lower().replace("\\", "/")

    is_self = any(p.lower().replace("\\", "/") in norm for p in _PROTECTED_CORE_PATHS)
    # Also treat any core/kernel/arifosmcp mutation intent as self
    if any(k in norm for k in ["arifosmcp/", "arifos/kernel", "core/laws", "self_mod", "metabolic_loop", "mind_reason"]):
        is_self = True

    # Check for authority mutation keywords
    mutation_keywords = ["modify_code", "alter_policy", "lower_threshold", "approve_self", "mutate", "self_mod"]
    is_mutation = any(kw in (action_type or "").lower() for kw in mutation_keywords)

    # Classify with full signals (phrase + path + action)
    tier = classify_cognitive_tier({"intent": action_type or "", "target": target_path or ""}, target_path)

    if (is_self and is_mutation) or tier.get("tier") == "ASI":
        return {
            "is_blocked": True,
            "max_action": "plan_only",
            "human_decision_required": True,
            "reason": f"SELF_MODIFICATION_LOCK / ASI_FIREWALL: {tier.get('reason')}",
            "tier": tier,
        }

    return {
        "is_blocked": False,
        "max_action": "execution_permitted",
        "human_decision_required": False,
        "tier": tier,
    }
