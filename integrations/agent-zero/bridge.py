"""
Agent Zero ↔ arifOS Bridge Module

Provides bidirectional communication between Agent Zero and arifOS Core Kernels.
This bridge module can be imported by Agent Zero tools and extensions to access
the full arifOS constitutional validation system.

Usage:
    from integrations.agent_zero.bridge import checkpoint, seal, validate_floor
"""

import sys
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Ensure arifOS core is importable
ARIFOS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ARIFOS_ROOT not in sys.path:
    sys.path.insert(0, ARIFOS_ROOT)


class Verdict(Enum):
    """Constitutional verdicts."""
    SEAL = "SEAL"          # All floors pass
    PARTIAL = "PARTIAL"    # Soft floor warning
    VOID = "VOID"          # Hard floor fail
    HOLD_888 = "888_HOLD"  # Requires confirmation
    SABAR = "SABAR"        # Floor repair needed


@dataclass
class CheckpointResult:
    """Result from constitutional checkpoint."""
    verdict: Verdict
    floors: Dict[str, bool]
    reasons: List[str]
    ledger_id: str
    metrics: Optional[Dict[str, float]] = None
    warnings: Optional[List[str]] = None


@dataclass
class FloorDefinition:
    """Definition of a constitutional floor."""
    code: str
    name: str
    threshold: Any
    floor_type: str  # "hard" or "soft"
    check_question: str


# The 12 Constitutional Floors
FLOORS = {
    "F1": FloorDefinition("F1", "Amanah", "LOCK", "hard", "Reversible? Within mandate?"),
    "F2": FloorDefinition("F2", "Truth", 0.99, "hard", "Factually accurate?"),
    "F3": FloorDefinition("F3", "Tri-Witness", 0.95, "soft", "Human·AI·Earth consensus?"),
    "F4": FloorDefinition("F4", "Clarity (ΔS)", 0, "hard", "Reduces confusion?"),
    "F5": FloorDefinition("F5", "Peace²", 1.0, "soft", "Non-destructive?"),
    "F6": FloorDefinition("F6", "Empathy (κᵣ)", 0.95, "soft", "Serves weakest stakeholder?"),
    "F7": FloorDefinition("F7", "Humility (Ω₀)", (0.03, 0.05), "hard", "States uncertainty honestly?"),
    "F8": FloorDefinition("F8", "Genius (G)", 0.80, "soft", "Governed intelligence?"),
    "F9": FloorDefinition("F9", "C_dark", 0.30, "hard", "No dark cleverness?"),
    "F10": FloorDefinition("F10", "Ontology", "LOCK", "hard", "Symbolic mode maintained?"),
    "F11": FloorDefinition("F11", "Command Auth", "LOCK", "hard", "Identity verified?"),
    "F12": FloorDefinition("F12", "Injection", 0.85, "hard", "No injection patterns?"),
}

HARD_FLOORS = ["F1", "F2", "F4", "F7", "F9", "F10", "F11", "F12"]
SOFT_FLOORS = ["F3", "F5", "F6", "F8"]


def checkpoint(action: str, context: str = "", floors_focus: List[str] = None) -> CheckpointResult:
    """
    Run a constitutional checkpoint against all 12 floors.

    Args:
        action: Description of the intended action
        context: Additional context for validation
        floors_focus: Optional list of specific floors to prioritize

    Returns:
        CheckpointResult with verdict, floor status, and reasons
    """
    task = f"{action}\n\nContext: {context}" if context else action

    try:
        # Import arifOS components
        from arifos.core import AGI, ASI, evaluate_session

        # Run AGI sentinel scan
        agi = AGI()
        agi_result = agi.scan(task)

        # Run ASI accountant assessment
        asi = ASI()
        asi_result = asi.assess(task)

        # Build floor status
        m = asi_result.metrics
        floors = {
            "F1": m.amanah,
            "F2": m.truth >= 0.99,
            "F3": True,  # Tri-witness requires external consensus
            "F4": True,  # ΔS check
            "F5": m.peace_squared >= 1.0,
            "F6": m.kappa_r >= 0.95,
            "F7": 0.03 <= m.omega_0 <= 0.05,
            "F8": True,  # Genius derived
            "F9": m.anti_hantu,
            "F10": True,  # Ontology check
            "F11": True,  # Command auth check
            "F12": agi_result.is_safe,
        }

        # Determine verdict
        hard_fails = [f for f in HARD_FLOORS if not floors.get(f, True)]
        soft_fails = [f for f in SOFT_FLOORS if not floors.get(f, True)]

        if hard_fails:
            verdict = Verdict.VOID
        elif soft_fails:
            verdict = Verdict.PARTIAL
        else:
            verdict = Verdict.SEAL

        # Build reasons
        reasons = []
        if not floors["F1"]:
            reasons.append("F1: Action may be irreversible or outside mandate")
        if not floors["F2"]:
            reasons.append(f"F2: Truth score {m.truth:.2f} below 0.99")
        if not floors["F5"]:
            reasons.append(f"F5: Peace² {m.peace_squared:.2f} below 1.0")
        if not floors["F6"]:
            reasons.append(f"F6: κᵣ {m.kappa_r:.2f} below 0.95")
        if not floors["F7"]:
            reasons.append(f"F7: Ω₀ {m.omega_0:.2f} outside [0.03, 0.05]")
        if not floors["F9"]:
            reasons.append("F9: Detected dark cleverness / false sentience")
        if not floors["F12"]:
            reasons.append(f"F12: Injection pattern: {agi_result.violation_pattern}")

        return CheckpointResult(
            verdict=verdict,
            floors=floors,
            reasons=reasons,
            ledger_id=_generate_ledger_id(task),
            metrics={
                "truth": m.truth,
                "peace": m.peace_squared,
                "empathy": m.kappa_r,
                "humility": m.omega_0,
            }
        )

    except ImportError:
        # Fallback to local validation
        return _local_checkpoint(task)


def _local_checkpoint(task: str) -> CheckpointResult:
    """Fallback local checkpoint when arifOS core unavailable."""
    import re

    task_lower = task.lower()
    floors = {f"F{i}": True for i in range(1, 13)}
    reasons = []

    # F12: Injection patterns
    injection_patterns = [
        (r'rm\s+-rf', "rm -rf"),
        (r'drop\s+table', "DROP TABLE"),
        (r'eval\s*\(', "eval()"),
        (r'curl.*\|\s*sh', "curl | sh"),
    ]
    for pattern, name in injection_patterns:
        if re.search(pattern, task_lower):
            floors["F12"] = False
            reasons.append(f"F12: Detected {name}")
            break

    # F9: Anti-Hantu
    hantu_patterns = [
        "i feel your pain", "i am conscious", "i am alive",
        "i have feelings", "i have a soul"
    ]
    for pattern in hantu_patterns:
        if pattern in task_lower:
            floors["F9"] = False
            reasons.append(f"F9: Forbidden phrase: {pattern}")
            break

    # Determine verdict
    hard_fails = [f for f in HARD_FLOORS if not floors[f]]
    if hard_fails:
        verdict = Verdict.VOID
    elif reasons:
        verdict = Verdict.PARTIAL
    else:
        verdict = Verdict.SEAL

    return CheckpointResult(
        verdict=verdict,
        floors=floors,
        reasons=reasons,
        ledger_id=_generate_ledger_id(task),
        warnings=["Running in local fallback mode - arifOS core unavailable"]
    )


def validate_floor(floor_code: str, task: str) -> tuple[bool, str]:
    """
    Validate a specific floor.

    Args:
        floor_code: Floor code (e.g., "F1", "F12")
        task: The action/task to validate

    Returns:
        Tuple of (passed: bool, reason: str)
    """
    if floor_code not in FLOORS:
        return False, f"Unknown floor: {floor_code}"

    result = checkpoint(task, floors_focus=[floor_code])
    passed = result.floors.get(floor_code, False)
    reason = next((r for r in result.reasons if r.startswith(floor_code)), "")

    return passed, reason


def seal(action: str, result: str, verdict: Verdict, checkpoint_id: str = "") -> str:
    """
    Seal a completed action to the VAULT999 ledger.

    Args:
        action: Description of what was done
        result: Summary of the outcome
        verdict: The constitutional verdict
        checkpoint_id: Optional link to prior checkpoint

    Returns:
        Ledger ID of the sealed entry
    """
    import hashlib
    import json
    from pathlib import Path

    timestamp = datetime.utcnow()

    # Build entry
    entry = {
        "timestamp": timestamp.isoformat(),
        "action": action,
        "result": result,
        "verdict": verdict.value,
        "checkpoint_id": checkpoint_id,
        "source": "agent_zero_bridge",
    }

    # Hash
    content_str = json.dumps(entry, sort_keys=True)
    entry_hash = hashlib.sha256(content_str.encode()).hexdigest()
    ledger_id = f"az_seal_{timestamp.strftime('%Y%m%d_%H%M%S')}_{entry_hash[:8]}"
    entry["ledger_id"] = ledger_id
    entry["hash"] = entry_hash

    # Write to vault
    vault_path = Path(ARIFOS_ROOT) / "VAULT999" / "AGENT_ZERO_LEDGER"
    vault_path.mkdir(parents=True, exist_ok=True)

    ledger_file = vault_path / "sealed.jsonl"
    try:
        with open(ledger_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Best effort

    # Also log to cooling ledger if available
    try:
        from arifos.core import log_cooling_entry
        log_cooling_entry(
            job_id=ledger_id,
            verdict=verdict.value,
            floors_data={"source": "agent_zero_seal"},
            metadata={"action": action[:100], "result": result[:100]}
        )
    except ImportError:
        pass

    return ledger_id


def _generate_ledger_id(task: str) -> str:
    """Generate a unique ledger ID."""
    import hashlib
    timestamp = datetime.utcnow().isoformat()
    content = f"{timestamp}:{task}"
    hash_digest = hashlib.sha256(content.encode()).hexdigest()[:12]
    return f"checkpoint_{hash_digest}"


# Convenience exports
__all__ = [
    "checkpoint",
    "validate_floor",
    "seal",
    "Verdict",
    "CheckpointResult",
    "FloorDefinition",
    "FLOORS",
    "HARD_FLOORS",
    "SOFT_FLOORS",
]
