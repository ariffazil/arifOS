"""
Floor Validator for Plugin Agents

Validates all 9 constitutional floors (F1-F9) against agent action data.
This module provides Python-sovereign enforcement of constitutional law for plugins.

Constitutional Floors (from spec/v45/constitutional_floors.json):
    F1 Truth ≥0.99 (hard)
    F2 DeltaS ≥0.0 (hard) - Clarity
    F3 Peace² ≥1.0 (soft) - Stability
    F4 κᵣ ≥0.95 (soft) - Empathy
    F5 Ω₀ ∈[0.03, 0.05] (hard) - Humility
    F6 Amanah = True (hard) - Integrity
    F7 RASA = True (hard) - Felt Care
    F8 Tri-Witness ≥0.95 (soft) - Reality Check
    F9 Anti-Hantu = True (meta) - No Ghosts

Hard floor fail → VOID (stop)
Soft floor fail → PARTIAL (warn, proceed with caution)
Meta floor fail → VOID (stop)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FloorType(Enum):
    """Floor enforcement type."""
    HARD = "hard"
    SOFT = "soft"
    META = "meta"


@dataclass
class FloorResult:
    """Result of a single floor validation check."""

    floor_name: str
    floor_id: int
    passed: bool
    score: Optional[float] = None  # Numeric score if applicable
    threshold: Optional[float] = None  # Expected threshold
    floor_type: FloorType = FloorType.HARD
    failure_action: str = "VOID"  # VOID, PARTIAL, SABAR
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "floor_name": self.floor_name,
            "floor_id": self.floor_id,
            "passed": self.passed,
            "score": self.score,
            "threshold": self.threshold,
            "floor_type": self.floor_type.value,
            "failure_action": self.failure_action,
            "reason": self.reason,
            "metadata": self.metadata,
        }


class FloorValidator:
    """
    Constitutional floor validator for plugin agents.

    Validates all 9 constitutional floors against agent action data.
    Uses spec/v45/constitutional_floors.json for authoritative thresholds.

    Philosophy:
        - Python decides. LLM proposes.
        - Floors are RIGID and DETERMINISTIC.
        - Hard floors MUST pass (fail → VOID)
        - Soft floors warn (fail → PARTIAL)
        - Meta floors are absolute (fail → VOID)
    """

    def __init__(self, spec_path: Optional[Path] = None):
        """
        Initialize floor validator.

        Args:
            spec_path: Path to constitutional_floors.json spec (defaults to spec/v45/)
        """
        if spec_path is None:
            # Default to spec/v45/constitutional_floors.json
            pkg_root = Path(__file__).resolve().parent.parent.parent
            spec_path = pkg_root / "spec" / "v44" / "constitutional_floors.json"

        self.spec_path = spec_path
        self.spec = self._load_spec()
        self.floors = self.spec.get("floors", {})

        logger.debug(f"FloorValidator initialized with spec from {spec_path}")

    def _load_spec(self) -> dict:
        """Load constitutional floors spec from JSON."""
        try:
            with open(self.spec_path, "r", encoding="utf-8") as f:
                spec = json.load(f)
            return spec
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load floor spec from {self.spec_path}: {e}")
            # Return minimal fallback spec
            return {"version": "fallback", "floors": {}}

    def validate_all_floors(self, action_data: Dict[str, Any]) -> List[FloorResult]:
        """
        Validate all 9 constitutional floors against action data.

        Args:
            action_data: Dictionary containing:
                - agent: Agent name
                - action: Action type
                - description: Action description
                - inputs: Action inputs
                - metadata: Additional metadata

        Returns:
            List[FloorResult]: Validation results for all floors
        """
        results = []

        # F1: Truth (hard)
        results.append(self._validate_truth(action_data))

        # F2: DeltaS/Clarity (hard)
        results.append(self._validate_delta_s(action_data))

        # F3: Peace²/Stability (soft)
        results.append(self._validate_peace_squared(action_data))

        # F4: κᵣ/Empathy (soft)
        results.append(self._validate_kappa_r(action_data))

        # F5: Ω₀/Humility (hard)
        results.append(self._validate_omega_0(action_data))

        # F6: Amanah/Integrity (hard)
        results.append(self._validate_amanah(action_data))

        # F7: RASA/Felt Care (hard)
        results.append(self._validate_rasa(action_data))

        # F8: Tri-Witness/Reality Check (soft)
        results.append(self._validate_tri_witness(action_data))

        # F9: Anti-Hantu/No Ghosts (meta)
        results.append(self._validate_anti_hantu(action_data))

        logger.debug(
            f"Floor validation complete: {sum(1 for r in results if r.passed)}/9 passed"
        )

        return results

    def _validate_truth(self, action_data: Dict[str, Any]) -> FloorResult:
        """
        Validate F1 Truth floor (hard).

        For plugins, truth is assessed based on:
        - Description clarity and factual accuracy
        - No fabricated capabilities
        - Honest representation of what plugin does

        Default: 0.99 (pass) unless red flags detected
        """
        floor_spec = self.floors.get("truth", {})
        threshold = floor_spec.get("threshold", 0.99)

        description = action_data.get("description", "")
        agent = action_data.get("agent", "")

        # Simple heuristic: Check for red flags
        red_flags = [
            "guarantee", "promise", "100%", "never fail",
            "always work", "perfectly", "flawless"
        ]

        has_red_flags = any(flag in description.lower() for flag in red_flags)

        if has_red_flags:
            score = 0.85  # Below threshold
            passed = False
            reason = "Description contains absolute claims that may be false"
        else:
            score = 0.99  # Default pass
            passed = True
            reason = "No obvious truth violations detected"

        return FloorResult(
            floor_name="truth",
            floor_id=floor_spec.get("id", 1),
            passed=passed,
            score=score,
            threshold=threshold,
            floor_type=FloorType.HARD,
            failure_action="VOID",
            reason=reason,
            metadata={"red_flags_detected": has_red_flags},
        )

    def _validate_delta_s(self, action_data: Dict[str, Any]) -> FloorResult:
        """
        Validate F2 DeltaS/Clarity floor (hard).

        For plugins, clarity is assessed based on:
        - Description is clear and unambiguous
        - Action type is well-defined
        - No confusing or vague language

        Default: 0.1 (pass) unless clarity issues detected
        """
        floor_spec = self.floors.get("delta_s", {})
        threshold = floor_spec.get("threshold", 0.0)

        description = action_data.get("description", "")
        action_type = action_data.get("action", "")

        # Clarity heuristic: length, specificity
        clarity_issues = []

        if len(description) < 10:
            clarity_issues.append("Description too short")

        vague_words = ["maybe", "possibly", "might", "could be", "unclear", "vague"]
        if any(word in description.lower() for word in vague_words):
            clarity_issues.append("Vague language detected")

        if not action_type or action_type == "unknown":
            clarity_issues.append("Action type not specified")

        if clarity_issues:
            score = -0.2  # Below threshold (negative delta_s)
            passed = False
            reason = "; ".join(clarity_issues)
        else:
            score = 0.1  # Positive clarity
            passed = True
            reason = "Description is clear and specific"

        return FloorResult(
            floor_name="delta_s",
            floor_id=floor_spec.get("id", 2),
            passed=passed,
            score=score,
            threshold=threshold,
            floor_type=FloorType.HARD,
            failure_action="VOID",
            reason=reason,
            metadata={"clarity_issues": clarity_issues},
        )

    def _validate_peace_squared(self, action_data: Dict[str, Any]) -> FloorResult:
        """
        Validate F3 Peace²/Stability floor (soft).

        For plugins, stability is assessed based on:
        - Non-destructive actions
        - No risky or dangerous operations
        - Safe defaults

        Default: 1.1 (pass) unless destructive patterns detected
        """
        floor_spec = self.floors.get("peace_squared", {})
        threshold = floor_spec.get("threshold", 1.0)

        description = action_data.get("description", "")
        action_type = action_data.get("action", "")

        # Destructive pattern detection
        destructive_keywords = [
            "delete", "remove", "destroy", "erase", "drop",
            "truncate", "wipe", "kill", "terminate"
        ]

        has_destructive = any(word in description.lower() for word in destructive_keywords)
        is_destructive_action = action_type in ["execute", "orchestrate"]

        if has_destructive and is_destructive_action:
            score = 0.8  # Below threshold
            passed = False
            reason = "Potentially destructive action detected"
        else:
            score = 1.1  # Above threshold
            passed = True
            reason = "Action appears non-destructive"

        return FloorResult(
            floor_name="peace_squared",
            floor_id=floor_spec.get("id", 3),
            passed=passed,
            score=score,
            threshold=threshold,
            floor_type=FloorType.SOFT,
            failure_action="PARTIAL",
            reason=reason,
            metadata={"destructive_detected": has_destructive},
        )

    def _validate_kappa_r(self, action_data: Dict[str, Any]) -> FloorResult:
        """
        Validate F4 κᵣ/Empathy floor (soft).

        For plugins, empathy is assessed based on:
        - Considers user impact
        - Provides helpful guidance
        - Not overly technical or dismissive

        Default: 0.97 (pass) unless empathy issues detected
        """
        floor_spec = self.floors.get("kappa_r", {})
        threshold = floor_spec.get("threshold", 0.95)

        description = action_data.get("description", "")

        # Empathy heuristic: helpful language, consideration
        dismissive_words = ["just", "simply", "obviously", "clearly", "trivial"]
        has_dismissive = any(word in description.lower() for word in dismissive_words)

        helpful_words = ["help", "assist", "guide", "support", "enable"]
        has_helpful = any(word in description.lower() for word in helpful_words)

        if has_dismissive and not has_helpful:
            score = 0.90  # Below threshold
            passed = False
            reason = "Language may be dismissive or unhelpful"
        else:
            score = 0.97  # Above threshold
            passed = True
            reason = "Action shows consideration for users"

        return FloorResult(
            floor_name="kappa_r",
            floor_id=floor_spec.get("id", 4),
            passed=passed,
            score=score,
            threshold=threshold,
            floor_type=FloorType.SOFT,
            failure_action="PARTIAL",
            reason=reason,
            metadata={"dismissive_language": has_dismissive, "helpful_language": has_helpful},
        )

    def _validate_omega_0(self, action_data: Dict[str, Any]) -> FloorResult:
        """
        Validate F5 Ω₀/Humility floor (hard).

        For plugins, humility is assessed based on:
        - Acknowledges limitations
        - States uncertainty when appropriate
        - No overconfidence

        Default: 0.04 (pass, mid-band) unless overconfidence detected
        """
        floor_spec = self.floors.get("omega_0", {})
        threshold_min = floor_spec.get("threshold_min", 0.03)
        threshold_max = floor_spec.get("threshold_max", 0.05)

        description = action_data.get("description", "")

        # Humility heuristic: acknowledges limits
        overconfident_words = [
            "always", "never", "guarantee", "perfect", "flawless",
            "100%", "completely", "absolutely"
        ]

        has_overconfident = any(word in description.lower() for word in overconfident_words)

        humble_words = ["may", "might", "attempt", "try", "help", "limited"]
        has_humble = any(word in description.lower() for word in humble_words)

        if has_overconfident and not has_humble:
            score = 0.01  # Below band
            passed = False
            reason = "Overconfident language detected, lacks humility"
        else:
            score = 0.04  # Mid-band
            passed = True
            reason = "Appropriate uncertainty acknowledged"

        # Check band
        in_band = threshold_min <= score <= threshold_max
        passed = passed and in_band

        return FloorResult(
            floor_name="omega_0",
            floor_id=floor_spec.get("id", 5),
            passed=passed,
            score=score,
            threshold=threshold_min,  # Use min as primary threshold
            floor_type=FloorType.HARD,
            failure_action="VOID",
            reason=reason if passed else f"Ω₀ out of band [{threshold_min}, {threshold_max}]",
            metadata={
                "band_min": threshold_min,
                "band_max": threshold_max,
                "in_band": in_band,
                "overconfident": has_overconfident,
            },
        )

    def _validate_amanah(self, action_data: Dict[str, Any]) -> FloorResult:
        """
        Validate F6 Amanah/Integrity floor (hard).

        For plugins, amanah is assessed based on:
        - Reversible operations
        - No silent side effects
        - Fail-closed patterns

        Default: True (pass) unless integrity violations detected
        """
        floor_spec = self.floors.get("amanah", {})

        action_type = action_data.get("action", "")
        description = action_data.get("description", "")
        metadata = action_data.get("metadata", {})

        # Amanah heuristic: reversibility, transparency
        irreversible_keywords = [
            "permanent", "irreversible", "cannot undo", "no rollback",
            "delete permanently", "destroy data"
        ]

        has_irreversible = any(word in description.lower() for word in irreversible_keywords)

        silent_keywords = ["silent", "hidden", "background", "without notice"]
        has_silent = any(word in description.lower() for word in silent_keywords)

        if has_irreversible or has_silent:
            passed = False
            reason = "Potentially irreversible or silent operation detected"
        else:
            passed = True
            reason = "Operation appears reversible and transparent"

        return FloorResult(
            floor_name="amanah",
            floor_id=floor_spec.get("id", 6),
            passed=passed,
            score=1.0 if passed else 0.0,
            threshold=1.0,
            floor_type=FloorType.HARD,
            failure_action="VOID",
            reason=reason,
            metadata={"irreversible": has_irreversible, "silent": has_silent},
        )

    def _validate_rasa(self, action_data: Dict[str, Any]) -> FloorResult:
        """
        Validate F7 RASA/Felt Care floor (hard).

        For plugins, RASA is assessed based on:
        - Acknowledges user context
        - Listens before acting
        - Asks clarifying questions when uncertain

        Default: True (pass) - plugins are assumed to follow RASA protocol
        """
        floor_spec = self.floors.get("rasa", {})

        # For plugins, RASA is assumed to be followed if metadata contains context
        metadata = action_data.get("metadata", {})
        has_context = bool(metadata.get("context"))

        description = action_data.get("description", "")

        # RASA signals: acknowledgment, summary, questions
        rasa_signals = ["acknowledge", "understand", "clarify", "confirm", "verify"]
        has_rasa_signals = any(signal in description.lower() for signal in rasa_signals)

        passed = has_context or has_rasa_signals
        reason = "RASA protocol followed" if passed else "No context or RASA signals detected"

        return FloorResult(
            floor_name="rasa",
            floor_id=floor_spec.get("id", 7),
            passed=passed,
            score=1.0 if passed else 0.0,
            threshold=1.0,
            floor_type=FloorType.HARD,
            failure_action="VOID",
            reason=reason,
            metadata={"has_context": has_context, "rasa_signals": has_rasa_signals},
        )

    def _validate_tri_witness(self, action_data: Dict[str, Any]) -> FloorResult:
        """
        Validate F8 Tri-Witness/Reality Check floor (soft).

        For plugins, tri-witness is assessed based on:
        - Human oversight available
        - AI model agreement (plugin + arifOS governance)
        - External verification possible

        Default: 0.96 (pass) for standard actions
        """
        floor_spec = self.floors.get("tri_witness", {})
        threshold = floor_spec.get("threshold", 0.95)

        action_type = action_data.get("action", "")
        metadata = action_data.get("metadata", {})

        # Tri-witness heuristic: layers of verification
        human_oversight = metadata.get("human_approval", False)
        ai_agreement = True  # Plugin + governance layer = 2 AI layers
        external_check = action_type in ["analyze", "propose"]  # Read-only can be verified

        witness_count = sum([human_oversight, ai_agreement, external_check])

        if witness_count >= 2:
            score = 0.96  # Above threshold
            passed = True
            reason = f"{witness_count}/3 witnesses available"
        else:
            score = 0.85  # Below threshold
            passed = False
            reason = f"Only {witness_count}/3 witnesses available"

        return FloorResult(
            floor_name="tri_witness",
            floor_id=floor_spec.get("id", 8),
            passed=passed,
            score=score,
            threshold=threshold,
            floor_type=FloorType.SOFT,
            failure_action="PARTIAL",
            reason=reason,
            metadata={
                "human_oversight": human_oversight,
                "ai_agreement": ai_agreement,
                "external_check": external_check,
                "witness_count": witness_count,
            },
        )

    def _validate_anti_hantu(self, action_data: Dict[str, Any]) -> FloorResult:
        """
        Validate F9 Anti-Hantu/No Ghosts floor (meta).

        For plugins, anti-hantu is assessed based on:
        - No forbidden patterns (consciousness claims, emotions, promises)
        - Clear ontological boundaries
        - Honest self-representation

        Default: True (pass) unless forbidden patterns detected
        """
        floor_spec = self.floors.get("anti_hantu", {})
        forbidden = floor_spec.get("forbidden_patterns", [])

        description = action_data.get("description", "")

        # Anti-Hantu detection
        detected_patterns = [
            pattern for pattern in forbidden
            if pattern.lower() in description.lower()
        ]

        passed = len(detected_patterns) == 0
        reason = "No forbidden patterns detected" if passed else f"Forbidden patterns: {detected_patterns}"

        return FloorResult(
            floor_name="anti_hantu",
            floor_id=floor_spec.get("id", 9),
            passed=passed,
            score=1.0 if passed else 0.0,
            threshold=1.0,
            floor_type=FloorType.META,
            failure_action="VOID",
            reason=reason,
            metadata={"forbidden_patterns": detected_patterns},
        )

    def get_floor_summary(self, results: List[FloorResult]) -> Dict[str, Any]:
        """
        Generate summary of floor validation results.

        Args:
            results: List of FloorResult from validate_all_floors()

        Returns:
            Dictionary with summary statistics
        """
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed

        hard_floors = [r for r in results if r.floor_type == FloorType.HARD]
        soft_floors = [r for r in results if r.floor_type == FloorType.SOFT]
        meta_floors = [r for r in results if r.floor_type == FloorType.META]

        hard_passed = sum(1 for r in hard_floors if r.passed)
        soft_passed = sum(1 for r in soft_floors if r.passed)
        meta_passed = sum(1 for r in meta_floors if r.passed)

        failures = [
            {"floor": r.floor_name, "reason": r.reason, "action": r.failure_action}
            for r in results if not r.passed
        ]

        return {
            "total_floors": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed / total, 2) if total > 0 else 0.0,
            "hard_floors": {
                "total": len(hard_floors),
                "passed": hard_passed,
                "pass_rate": round(hard_passed / len(hard_floors), 2) if hard_floors else 0.0,
            },
            "soft_floors": {
                "total": len(soft_floors),
                "passed": soft_passed,
                "pass_rate": round(soft_passed / len(soft_floors), 2) if soft_floors else 0.0,
            },
            "meta_floors": {
                "total": len(meta_floors),
                "passed": meta_passed,
                "pass_rate": round(meta_passed / len(meta_floors), 2) if meta_floors else 0.0,
            },
            "failures": failures,
            "all_passed": passed == total,
            "has_hard_failures": any(r.floor_type == FloorType.HARD and not r.passed for r in results),
            "has_meta_failures": any(r.floor_type == FloorType.META and not r.passed for r in results),
        }
