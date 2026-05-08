"""
F1–F13 Constitutional Floor Evaluation
Ported from embedded JS theory (host/kernel/floors.js, canon/GOVERNANCE.md)
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

FLOORS = {
    "F1": "Amanah — reversible or explicitly irreversible",
    "F2": "Truth — epistemic tag required",
    "F3": "Input Clarity — clear task definition",
    "F4": "Clarity — reduce complexity",
    "F5": "Peace — no unresolved panic",
    "F6": "Maruah — dignity as variable",
    "F7": "Humility — uncertainty band",
    "F8": "Law — local-first data",
    "F9": "Anti-Hantu — no phantom entries",
    "F10": "AI Only Advises — human decides",
    "F11": "Auth — PIN for critical",
    "F12": "No Override — floors unbypassable",
    "F13": "Human Veto — final authority",
}


def check_floors(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate F1–F13 constitutional floors.
    Returns: pass, verdict, violations, holds, warnings, epistemic, vault_log_entry, witness
    """
    violations: List[str] = []
    holds: List[str] = []
    warnings: List[str] = []

    reversible = args.get("reversible")
    human_confirmed = args.get("human_confirmed", False)
    epistemic = args.get("epistemic", "ESTIMATE")
    ai_is_deciding = args.get("ai_is_deciding", False)
    floor_override = args.get("floor_override", False)
    peace2 = args.get("peace2", 1.0)
    maruah_score = args.get("maruah_score", 0.5)
    uncertainty_band = args.get("uncertainty_band")
    operation_type = args.get("operation_type", "PROJECTION")
    scale_mode = args.get("scale_mode", "enterprise")

    # F1 — Amanah
    if reversible is False and not human_confirmed:
        holds.append("F1: 888_HOLD — Irreversible action requires human confirmation.")

    # F2 — Truth
    if epistemic == "UNKNOWN":
        warnings.append("F2: Epistemic state is UNKNOWN.")
    confidence = args.get("confidence")
    if confidence is not None and confidence < 0.99 and uncertainty_band is None:
        warnings.append("F2: Confidence < 0.99 and no uncertainty band declared.")

    # F3 — Input Clarity
    task_definition = args.get("task_definition")
    if task_definition is not None and len(str(task_definition).strip()) < 10:
        warnings.append("F3: Input lacks clarity (task definition too short).")

    # F5 — Peace
    if peace2 < 1.0:
        holds.append("F5: Peace² below 1.0.")

    # F6 — Maruah
    maruah_floor = args.get("maruah_floor", 0.6)
    if maruah_score < maruah_floor:
        holds.append(f"F6: Maruah score {maruah_score} below floor {maruah_floor}.")

    # F7 — Humility
    if operation_type == "PROJECTION" and uncertainty_band is None:
        warnings.append("F7: Projection missing uncertainty band.")

    # F10 — AI Ontology
    if ai_is_deciding:
        violations.append("F10: AI cannot be the final decision maker.")

    # F12 — No Override
    if floor_override:
        violations.append("F12: Floor override is not permitted.")

    # F13 — Human Veto (escalated for high-scale irreversible operations)
    if not human_confirmed and reversible is False and scale_mode in {"national", "crisis", "civilization"}:
        holds.append("F13: High-scale irreversible action requires human confirmation.")

    # F8 / F9 / F11 — placeholder checks using explicit flags
    if args.get("phantom_entries"):
        violations.append("F9: Phantom entries detected.")
    if args.get("critical") and not args.get("pin_verified"):
        holds.append("F11: PIN required for critical operation.")

    # Derive verdict
    if violations:
        verdict = "VOID"
    elif holds:
        verdict = "HOLD"
    elif warnings:
        verdict = "CAUTION"
    else:
        verdict = "SEAL"

    return {
        "pass": verdict in ("SEAL", "CAUTION"),
        "verdict": verdict,
        "violations": violations,
        "holds": holds,
        "warnings": warnings,
        "epistemic": epistemic,
        "vault_log_entry": {"tool": "wealth_check_floors", "epoch": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")},
        "witness": {"human": human_confirmed, "ai": True, "earth": True},
    }


def maruah_band(maruah_score: float) -> str:
    if maruah_score >= 0.85:
        return "SOVEREIGN"
    if maruah_score >= 0.70:
        return "STABLE"
    if maruah_score >= 0.60:
        return "FLOOR"
    if maruah_score >= 0.40:
        return "AMBER"
    return "RED"
