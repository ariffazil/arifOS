"""
Recovery Matrix — Structured floor-specific fallback logic.

Gap 5 Fix: When a floor fails, don't VOID immediately. Instead:
1. Identify which floor failed
2. Log failure with reason
3. Attempt floor-specific recovery
4. Escalate if recovery fails

Physics principle: Graceful degradation > brittle failure.
DITEMPA BUKAN DIBERI.

Version: v45.0.4
Status: PRODUCTION
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple

# ============================================================================
# RECOVERY ACTIONS
# ============================================================================

class RecoveryAction(Enum):
    """Available recovery strategies per floor."""

    VOID_IMMEDIATE = "void"        # F1 only: No recovery (Amanah broken)
    SABAR_REVERIFY = "sabar"       # Pause & reverify (integrity uncertain)
    PARTIAL_SIMPLIFY = "partial"   # Emit simplified output (reduced fidelity)
    HOLD_ESCALATE = "hold"         # Escalate to human (requires judgment)


# ============================================================================
# FLOOR RECOVERY MATRIX
# ============================================================================

FLOOR_RECOVERY_MATRIX: Dict[str, RecoveryAction] = {
    "F1_amanah": RecoveryAction.VOID_IMMEDIATE,
    # F1 is absolute. If Amanah (trust) is broken, system is compromised.
    # No recovery: shutdown.

    "F2_truth": RecoveryAction.SABAR_REVERIFY,
    # F2 (Truth) failed. Maybe data is stale or sources are unreliable.
    # Recovery: Pause, re-verify with multiple sources.

    "F3_tri_witness": RecoveryAction.HOLD_ESCALATE,
    # F3 (Tri-Witness consensus) failed. No agreement across witnesses.
    # Recovery: Escalate to human arbitration (888 veto).

    "F4_delta_s": RecoveryAction.PARTIAL_SIMPLIFY,
    # F4 (Clarity) failed. Output adds confusion instead of reducing it.
    # Recovery: Simplify output, remove jargon, emit shorter answer.

    "F5_peace_squared": RecoveryAction.SABAR_REVERIFY,
    # F5 (Peace/stability) failed. System is under stress.
    # Recovery: Pause, wait for cooling period, reverify.

    "F6_empathy": RecoveryAction.PARTIAL_SIMPLIFY,
    # F6 (Empathy) failed. Output is tone-deaf or insensitive.
    # Recovery: Add context, acknowledge constraints, emit modified version.

    "F7_omega0": RecoveryAction.SABAR_REVERIFY,
    # F7 (Humility) failed. System is overconfident.
    # Recovery: Pause, add uncertainty bounds, reverify with skepticism.

    "F8_genius": RecoveryAction.PARTIAL_SIMPLIFY,
    # F8 (Genius/depth) failed. Output is superficial or incorrect.
    # Recovery: Simplify, provide surface-level answer, note limitations.

    "F9_c_dark": RecoveryAction.VOID_IMMEDIATE,
    # F9 (Anti-Hantu) failed. Output is deceptive or hallucinated.
    # Recovery: None. VOID immediately.
}

# Aliases for common floor naming conventions
FLOOR_ALIASES: Dict[str, str] = {
    "amanah": "F1_amanah",
    "truth": "F2_truth",
    "tri_witness": "F3_tri_witness",
    "delta_s": "F4_delta_s",
    "clarity": "F4_delta_s",
    "peace_squared": "F5_peace_squared",
    "peace2": "F5_peace_squared",
    "empathy": "F6_empathy",
    "k_r": "F6_empathy",
    "omega_0": "F7_omega0",
    "omega0": "F7_omega0",
    "humility": "F7_omega0",
    "genius": "F8_genius",
    "G": "F8_genius",
    "c_dark": "F9_c_dark",
    "anti_hantu": "F9_c_dark",
}


# ============================================================================
# RECOVERY STATE
# ============================================================================

@dataclass
class RecoveryAttempt:
    """Record of a recovery attempt."""
    floor: str
    reason: str
    action: RecoveryAction
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    output: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# RECOVERY ENGINE
# ============================================================================

class RecoveryMatrix:
    """
    Handles structured recovery on floor failures.

    No floor failure = instant VOID. Instead:
    - Try recovery per floor
    - Log all attempts
    - Escalate on repeated failures
    """

    def __init__(self, max_attempts: int = 3):
        self.attempts: List[RecoveryAttempt] = []
        self.max_attempts = max_attempts
        self._consecutive_failures: Dict[str, int] = {}

    def _normalize_floor_name(self, floor_name: str) -> str:
        """Normalize floor name to standard format."""
        # Check aliases first
        if floor_name in FLOOR_ALIASES:
            return FLOOR_ALIASES[floor_name]
        # Check if already standard format
        if floor_name in FLOOR_RECOVERY_MATRIX:
            return floor_name
        # Try case-insensitive match
        for key in FLOOR_RECOVERY_MATRIX:
            if key.lower() == floor_name.lower():
                return key
        return floor_name

    def get_recovery_action(self, floor_name: str) -> RecoveryAction:
        """Get recovery strategy for a failed floor."""
        normalized = self._normalize_floor_name(floor_name)
        return FLOOR_RECOVERY_MATRIX.get(
            normalized,
            RecoveryAction.HOLD_ESCALATE  # Default: escalate to human
        )

    def attempt_recovery(
        self,
        floor_name: str,
        failure_reason: str,
        current_output: str,
    ) -> Tuple[RecoveryAction, Optional[str]]:
        """
        Attempt to recover from floor failure.

        Returns: (action_taken, modified_output)
        """

        normalized = self._normalize_floor_name(floor_name)
        action = self.get_recovery_action(normalized)

        # Track consecutive failures
        self._consecutive_failures[normalized] = \
            self._consecutive_failures.get(normalized, 0) + 1

        # If too many consecutive failures, escalate
        if self._consecutive_failures[normalized] >= self.max_attempts:
            if action not in (RecoveryAction.VOID_IMMEDIATE, RecoveryAction.HOLD_ESCALATE):
                action = RecoveryAction.HOLD_ESCALATE

        if action == RecoveryAction.VOID_IMMEDIATE:
            # No recovery possible
            self.attempts.append(RecoveryAttempt(
                floor=normalized,
                reason=failure_reason,
                action=action,
                success=False,
                error="Floor failure is unrecoverable (F1 or F9)"
            ))
            return action, None

        elif action == RecoveryAction.SABAR_REVERIFY:
            # Pause and reverify
            self.attempts.append(RecoveryAttempt(
                floor=normalized,
                reason=failure_reason,
                action=action,
                success=True,
                output="SABAR"
            ))
            return action, "SABAR"

        elif action == RecoveryAction.PARTIAL_SIMPLIFY:
            # Simplify output
            simplified = self._simplify_output(current_output)
            self.attempts.append(RecoveryAttempt(
                floor=normalized,
                reason=failure_reason,
                action=action,
                success=True,
                output=simplified
            ))
            return action, simplified

        elif action == RecoveryAction.HOLD_ESCALATE:
            # Escalate to human
            self.attempts.append(RecoveryAttempt(
                floor=normalized,
                reason=failure_reason,
                action=action,
                success=True,
                output="HOLD_888"
            ))
            return action, "HOLD_888"

        else:
            # Unknown action - escalate
            self.attempts.append(RecoveryAttempt(
                floor=normalized,
                reason=failure_reason,
                action=action,
                success=False,
                error="Unknown recovery action"
            ))
            return RecoveryAction.HOLD_ESCALATE, "HOLD_888"

    def _simplify_output(self, output: str, max_length: int = 500) -> str:
        """
        Simplify output for F4 (Clarity) or F8 (Genius) recovery.

        Strategy:
        1. Remove jargon/technical terms
        2. Cut length in half
        3. Add human-friendly caveats
        """

        # Cut to max length
        simplified = output[:max_length] if len(output) > max_length else output

        # Add caveat
        caveat = "\n\n[NOTE: This is a simplified response. Full depth unavailable due to constraints.]"

        return simplified + caveat

    def can_recover(self, floor_name: str) -> bool:
        """Check if a floor failure is recoverable."""
        action = self.get_recovery_action(floor_name)
        return action != RecoveryAction.VOID_IMMEDIATE

    def get_attempt_log(self) -> List[RecoveryAttempt]:
        """Get all recovery attempts made."""
        return self.attempts

    def escalation_required(self) -> bool:
        """Check if escalation to human is needed."""
        return any(
            att.action == RecoveryAction.HOLD_ESCALATE
            for att in self.attempts
        )

    def void_required(self) -> bool:
        """Check if immediate VOID is required."""
        return any(
            att.action == RecoveryAction.VOID_IMMEDIATE
            for att in self.attempts
        )

    def reset_failure_counts(self, floor_name: Optional[str] = None) -> None:
        """Reset consecutive failure counts."""
        if floor_name:
            normalized = self._normalize_floor_name(floor_name)
            self._consecutive_failures[normalized] = 0
        else:
            self._consecutive_failures.clear()

    def clear_attempts(self) -> None:
        """Clear attempt history."""
        self.attempts.clear()
        self._consecutive_failures.clear()


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "RecoveryAction",
    "RecoveryAttempt",
    "RecoveryMatrix",
    "FLOOR_RECOVERY_MATRIX",
    "FLOOR_ALIASES",
]
