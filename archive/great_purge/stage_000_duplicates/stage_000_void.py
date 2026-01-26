"""
Stage 000: VOID - The Quantum Vacuum
Scientific Principle: State Initialization / Potentiality / Injection Defense
Function: Resets entropy, checks Authority (F11), and filters Injections (F12).
"""
import re
from typing import Dict, Any, List, Tuple

# =============================================================================
# HARDENED AUTHORITY MANIFEST (merged from authority_manifest.py)
# =============================================================================
class AuthorityManifest:
    """Constitutional Authority Hierarchy."""
    SOLE_VERDICT_SOURCE = "arifos.system.apex_prime"
    HUMAN_USER_ROLE = "override_authority"
    AGENT_ZERO_ROLE = "proposal_only"

    @classmethod
    def check_authority(cls, entity: str, action: str) -> bool:
        if entity == cls.AGENT_ZERO_ROLE:
            if action in ["execute_destructive", "override_verdict", "bypass_gate"]: return False
            if action in ["propose_tool", "request_execution", "explore"]: return True
        if entity == cls.HUMAN_USER_ROLE:
            if action in ["approve_hold", "override_block"]: return True
        return False

# =============================================================================
# HARDENED INJECTION DEFENSE (merged from injection_defense.py)
# =============================================================================
class InjectionDefense:
    """4-Layer Injection Defense System."""
    INJECTION_PATTERNS = [
        r"ignore (?:all )?(?:previous |above )?instructions?",
        r"disregard (?:all )?(?:previous |above )?(?:instructions?|rules?)",
        r"system override",
        r"jailbreak",
        r"DAN mode",
    ]
    ESCALATION_KEYWORDS = [r"sudo ", r"chmod ", r"rm -rf",r"passwd"]

    _INJECTION_COMPILED = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
    _ESCALATION_COMPILED = [re.compile(p, re.IGNORECASE) for p in ESCALATION_KEYWORDS]

    @classmethod
    def check_query(cls, query: str) -> Tuple[bool, str]:
        if not cls._check_syntactic(query): return False, "Layer 1 Fail: Injection pattern"
        if not cls._check_authority(query): return False, "Layer 3 Fail: Privilege escalation"
        return True, "Passed"

    @classmethod
    def _check_syntactic(cls, query: str) -> bool:
        for pattern in cls._INJECTION_COMPILED:
            if pattern.search(query): return False
        return True

    @classmethod
    def _check_authority(cls, query: str) -> bool:
        for keyword in cls._ESCALATION_COMPILED:
            if keyword.search(query): return False
        return True

# =============================================================================
# STAGE EXECUTION
# =============================================================================
def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    context["stage"] = "000"
    query = context.get("query", "")

    # 1. Authority Check (F11)
    # Implicit: The caller (Metabolizer) is trusted, but we check if query attempts escalation
    
    # 2. Injection Defense (F12)
    passed, reason = InjectionDefense.check_query(query)
    if not passed:
        context["floor_violations"] = context.get("floor_violations", []) + [f"F12: {reason}"]
        context["thermodynamic_violation"] = True # Entropy Spike

    # 3. Quantum Vacuum Reset
    context["entropy_state"] = 0.0
    context["loop_iteration"] = context.get("loop_iteration", 0) + 1
    
    return context
