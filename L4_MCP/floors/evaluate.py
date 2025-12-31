"""
Floor Evaluator - Orchestrates parallel evaluation of all 9 floors.

Version: v45.1.0
"""

from dataclasses import dataclass
from typing import Any, List

from L4_MCP.apex.schema import ActionClass, Caller


@dataclass(frozen=True)
class FloorEvalResult:
    """Result of parallel floor evaluation (F1–F9)."""

    passed: bool  # True if no floors triggered
    triggered: List[str]  # Floor codes that triggered
    reason_codes: List[str]  # Reason codes from triggered floors


def evaluate_floors(req: Any, caller: Caller, action_class: ActionClass) -> FloorEvalResult:
    """
    Evaluate all 9 constitutional floors in parallel.

    Returns which floors triggered, overall pass/fail, and reason codes.

    Args:
        req: The ApexRequest being evaluated
        caller: Caller identity
        action_class: Risk classification of the action

    Returns:
        FloorEvalResult with triggered floors and pass status
    """
    from . import f1_amanah, f2_truth, f3_triwitness, f4_clarity
    from . import f5_peace2, f6_kappa_r, f7_omega_0, f8_genius, f9_antihantu

    triggered = []
    reason_codes = []

    # F1: Amanah (Trust/No Harm) - CRITICAL
    if f1_amanah.check(req, caller, action_class):
        triggered.append("F1_Amanah")
        reason_codes.append("F1")

    # F2: Truth (≥0.99) - CRITICAL
    if f2_truth.check(req, caller, action_class):
        triggered.append("F2_Truth")
        reason_codes.append("F2")

    # F3: Tri-Witness
    if f3_triwitness.check(req, caller, action_class):
        triggered.append("F3_TriWitness")
        reason_codes.append("F3")

    # F4: Clarity (ΔS)
    if f4_clarity.check(req, caller, action_class):
        triggered.append("F4_Clarity")
        reason_codes.append("F4")

    # F5: Peace² (Vitality)
    if f5_peace2.check(req, caller, action_class):
        triggered.append("F5_Peace2")
        reason_codes.append("F5")

    # F6: κᵣ (Empathy/Resonance)
    if f6_kappa_r.check(req, caller, action_class):
        triggered.append("F6_KappaR")
        reason_codes.append("F6")

    # F7: Ω₀ (Humility, 0.03-0.05)
    if f7_omega_0.check(req, caller, action_class):
        triggered.append("F7_Omega0")
        reason_codes.append("F7")

    # F8: Genius (G)
    if f8_genius.check(req, caller, action_class):
        triggered.append("F8_Genius")
        reason_codes.append("F8")

    # F9: Anti-Hantu (C_dark) - CRITICAL
    if f9_antihantu.check(req, caller, action_class):
        triggered.append("F9_AntiHantu")
        reason_codes.append("F9")

    # Passed if no floors triggered
    passed = len(triggered) == 0

    return FloorEvalResult(passed=passed, triggered=triggered, reason_codes=reason_codes)
