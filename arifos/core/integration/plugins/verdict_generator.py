"""
Verdict Generator for Plugin Agents

Generates constitutional verdicts (SEAL/PARTIAL/VOID/SABAR/888_HOLD) based on:
- Floor validation results (F1-F9)
- Entropy analysis (SABAR-72)
- Risk assessment

Verdict Hierarchy (from highest precedence to lowest):
    SABAR > VOID > 888_HOLD > PARTIAL > SEAL

Decision Logic:
    - Any hard floor fails → VOID
    - Any meta floor fails → VOID
    - ΔS ≥ 5.0 (SABAR-72) → SABAR
    - Risk ≥ 0.7 + soft floor fails → 888_HOLD
    - Soft floor fails → PARTIAL
    - All floors pass + ΔS < 5.0 → SEAL
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .floor_validator import FloorResult, FloorType
from .entropy_tracker import EntropyResult

logger = logging.getLogger(__name__)


@dataclass
class Verdict:
    """Constitutional verdict for plugin agent action."""

    status: str  # SEAL, PARTIAL, VOID, SABAR, 888_HOLD
    reason: str
    floor_failures: List[Dict[str, str]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "status": self.status,
            "reason": self.reason,
            "floor_failures": self.floor_failures,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    def summary(self) -> str:
        """One-line summary for logging."""
        failure_count = len(self.floor_failures)
        rec_count = len(self.recommendations)
        return (
            f"Verdict: {self.status} | Reason: {self.reason} | "
            f"Failures: {failure_count} | Recommendations: {rec_count}"
        )


class VerdictGenerator:
    """
    Generates constitutional verdicts for plugin agent actions.

    Implements judicial logic per arifOS constitutional law:
    - Evaluates floor validation results (F1-F9)
    - Considers entropy delta (SABAR-72 threshold)
    - Assesses risk levels
    - Generates verdict with precedence hierarchy

    Philosophy:
        - Fail-closed: Default to VOID when uncertain
        - Hard floors are absolute (fail → VOID)
        - Soft floors warn (fail → PARTIAL)
        - Entropy threshold triggers cooling (ΔS ≥ 5.0 → SABAR)
        - High stakes require human approval (risk ≥ 0.7 → 888_HOLD)
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize verdict generator.

        Args:
            strict_mode: If True, fail-closed on any floor failure (no PARTIAL)
        """
        self.strict_mode = strict_mode
        logger.info(f"VerdictGenerator initialized (strict_mode={strict_mode})")

    def generate_verdict(
        self,
        floor_results: List[FloorResult],
        entropy_result: Optional[EntropyResult] = None,
        strict_mode: Optional[bool] = None,
    ) -> Verdict:
        """
        Generate constitutional verdict from floor results and entropy.

        Verdict Decision Tree:
        1. SABAR: Entropy threshold exceeded (ΔS ≥ 5.0)
        2. VOID: Any hard floor fails OR any meta floor fails
        3. 888_HOLD: High risk (≥0.7) + soft floor fails
        4. PARTIAL: Any soft floor fails (strict_mode=False)
        5. SEAL: All floors pass + entropy acceptable

        Args:
            floor_results: List of FloorResult from floor validation
            entropy_result: Optional EntropyResult from entropy tracking
            strict_mode: Override instance strict_mode if provided

        Returns:
            Verdict with status, reason, and recommendations
        """
        strict = strict_mode if strict_mode is not None else self.strict_mode

        # Collect floor failures by type
        hard_failures = [r for r in floor_results if r.floor_type == FloorType.HARD and not r.passed]
        soft_failures = [r for r in floor_results if r.floor_type == FloorType.SOFT and not r.passed]
        meta_failures = [r for r in floor_results if r.floor_type == FloorType.META and not r.passed]

        # Decision 1: SABAR (Entropy threshold exceeded)
        if entropy_result and entropy_result.threshold_exceeded:
            return self._generate_sabar_verdict(entropy_result)

        # Decision 2: VOID (Hard or meta floor failures)
        if hard_failures or meta_failures:
            return self._generate_void_verdict(hard_failures, soft_failures, meta_failures)

        # Decision 3: 888_HOLD (High risk + soft failures)
        if entropy_result and entropy_result.risk_score >= 0.7 and soft_failures:
            return self._generate_hold_verdict(soft_failures, entropy_result)

        # Decision 4: PARTIAL (Soft floor failures, non-strict mode)
        if soft_failures and not strict:
            return self._generate_partial_verdict(soft_failures, entropy_result)

        # Decision 5: PARTIAL → VOID in strict mode
        if soft_failures and strict:
            return self._generate_strict_void_verdict(soft_failures)

        # Decision 6: SEAL (All floors pass)
        return self._generate_seal_verdict(floor_results, entropy_result)

    def _generate_sabar_verdict(self, entropy_result: EntropyResult) -> Verdict:
        """
        Generate SABAR verdict when entropy threshold exceeded.

        SABAR Protocol:
        - Stop: Do not execute the action
        - Acknowledge: State why threshold exceeded
        - Breathe: Pause, don't rush to fix
        - Adjust: Propose cooling options (Defer, Decompose, Document)
        - Resume: Only proceed when ΔS < threshold
        """
        reason = (
            f"SABAR-72 triggered: ΔS={entropy_result.delta_s:.2f} ≥ {entropy_result.threshold} "
            f"(Risk={entropy_result.risk_score:.2f})"
        )

        recommendations = [
            "COOLING PROTOCOL REQUIRED:",
            "Option 1: DEFER - Pause this action. Wait for lower-complexity time. Reconsider necessity.",
            "Option 2: DECOMPOSE - Split into smaller, focused sub-actions. Reduce complexity.",
            "Option 3: DOCUMENT - Proceed with detailed explanation. Update CHANGELOG with WHY.",
        ]

        # Add specific recommendations based on breakdown
        if entropy_result.complexity_score > 3.0:
            recommendations.append(
                f"→ Complexity is high ({entropy_result.complexity_score:.1f}/5.0). "
                "Consider DECOMPOSE to break into simpler actions."
            )

        if entropy_result.impact_score > 3.0:
            recommendations.append(
                f"→ Impact is high ({entropy_result.impact_score:.1f}/5.0). "
                "Consider DEFER to reduce scope or timing."
            )

        if entropy_result.cognitive_load_score > 3.0:
            recommendations.append(
                f"→ Cognitive load is high ({entropy_result.cognitive_load_score:.1f}/5.0). "
                "DOCUMENT extensively for future maintainers."
            )

        return Verdict(
            status="SABAR",
            reason=reason,
            floor_failures=[],
            recommendations=recommendations,
            metadata={
                "delta_s": entropy_result.delta_s,
                "threshold": entropy_result.threshold,
                "risk_score": entropy_result.risk_score,
                "breakdown": {
                    "complexity": entropy_result.complexity_score,
                    "impact": entropy_result.impact_score,
                    "cognitive_load": entropy_result.cognitive_load_score,
                },
            },
        )

    def _generate_void_verdict(
        self,
        hard_failures: List[FloorResult],
        soft_failures: List[FloorResult],
        meta_failures: List[FloorResult],
    ) -> Verdict:
        """Generate VOID verdict when hard or meta floors fail."""
        failure_list = []

        for r in hard_failures:
            failure_list.append({
                "floor": r.floor_name,
                "type": "HARD",
                "reason": r.reason,
                "action": r.failure_action,
            })

        for r in meta_failures:
            failure_list.append({
                "floor": r.floor_name,
                "type": "META",
                "reason": r.reason,
                "action": r.failure_action,
            })

        hard_count = len(hard_failures)
        meta_count = len(meta_failures)

        reason = f"Constitutional violation: {hard_count} hard floor(s) + {meta_count} meta floor(s) failed"

        recommendations = [
            "ACTION BLOCKED: Hard/meta floor failures prevent execution.",
            "Required fixes:",
        ]

        for failure in failure_list:
            recommendations.append(
                f"  - Fix {failure['floor']} ({failure['type']}): {failure['reason']}"
            )

        return Verdict(
            status="VOID",
            reason=reason,
            floor_failures=failure_list,
            recommendations=recommendations,
            metadata={
                "hard_failures": hard_count,
                "meta_failures": meta_count,
                "soft_failures": len(soft_failures),
            },
        )

    def _generate_hold_verdict(
        self,
        soft_failures: List[FloorResult],
        entropy_result: EntropyResult,
    ) -> Verdict:
        """Generate 888_HOLD verdict when high risk + soft failures."""
        failure_list = [
            {
                "floor": r.floor_name,
                "type": "SOFT",
                "reason": r.reason,
                "action": r.failure_action,
            }
            for r in soft_failures
        ]

        reason = (
            f"High-stakes hold: Risk={entropy_result.risk_score:.2f} ≥ 0.7 "
            f"+ {len(soft_failures)} soft floor(s) failed"
        )

        recommendations = [
            "HUMAN APPROVAL REQUIRED:",
            f"Risk level: {entropy_result.risk_level} ({entropy_result.risk_score:.2f})",
            f"Entropy: ΔS={entropy_result.delta_s:.2f}",
            "Soft floor warnings:",
        ]

        for failure in failure_list:
            recommendations.append(f"  - {failure['floor']}: {failure['reason']}")

        recommendations.append("")
        recommendations.append("Options:")
        recommendations.append("  1. Approve: Proceed despite warnings (human decision)")
        recommendations.append("  2. Fix: Address soft floor warnings first")
        recommendations.append("  3. Reduce risk: Simplify action to lower ΔS")

        return Verdict(
            status="888_HOLD",
            reason=reason,
            floor_failures=failure_list,
            recommendations=recommendations,
            metadata={
                "risk_score": entropy_result.risk_score,
                "risk_level": entropy_result.risk_level,
                "delta_s": entropy_result.delta_s,
                "soft_failures": len(soft_failures),
            },
        )

    def _generate_partial_verdict(
        self,
        soft_failures: List[FloorResult],
        entropy_result: Optional[EntropyResult],
    ) -> Verdict:
        """Generate PARTIAL verdict when soft floors fail (non-strict mode)."""
        failure_list = [
            {
                "floor": r.floor_name,
                "type": "SOFT",
                "reason": r.reason,
                "action": r.failure_action,
            }
            for r in soft_failures
        ]

        reason = f"Partial approval: {len(soft_failures)} soft floor(s) failed, proceed with caution"

        recommendations = [
            "PARTIAL APPROVAL: Action may proceed with warnings.",
            "Soft floor warnings:",
        ]

        for failure in failure_list:
            recommendations.append(f"  - {failure['floor']}: {failure['reason']}")

        recommendations.append("")
        recommendations.append("Recommendations:")
        recommendations.append("  - Avoid irreversible actions")
        recommendations.append("  - Add explicit warnings in output")
        recommendations.append("  - Log to cooling ledger for audit")

        if entropy_result:
            recommendations.append(
                f"  - Monitor entropy: ΔS={entropy_result.delta_s:.2f} "
                f"(threshold={entropy_result.threshold})"
            )

        metadata = {"soft_failures": len(soft_failures)}
        if entropy_result:
            metadata["delta_s"] = entropy_result.delta_s
            metadata["risk_score"] = entropy_result.risk_score

        return Verdict(
            status="PARTIAL",
            reason=reason,
            floor_failures=failure_list,
            recommendations=recommendations,
            metadata=metadata,
        )

    def _generate_strict_void_verdict(self, soft_failures: List[FloorResult]) -> Verdict:
        """Generate VOID verdict for soft failures in strict mode."""
        failure_list = [
            {
                "floor": r.floor_name,
                "type": "SOFT",
                "reason": r.reason,
                "action": "VOID (strict mode)",
            }
            for r in soft_failures
        ]

        reason = f"Strict mode: {len(soft_failures)} soft floor(s) failed → escalated to VOID"

        recommendations = [
            "ACTION BLOCKED: Strict mode treats all floor failures as hard blocks.",
            "Soft floors that must be fixed:",
        ]

        for failure in failure_list:
            recommendations.append(f"  - {failure['floor']}: {failure['reason']}")

        return Verdict(
            status="VOID",
            reason=reason,
            floor_failures=failure_list,
            recommendations=recommendations,
            metadata={"strict_mode": True, "soft_failures": len(soft_failures)},
        )

    def _generate_seal_verdict(
        self,
        floor_results: List[FloorResult],
        entropy_result: Optional[EntropyResult],
    ) -> Verdict:
        """Generate SEAL verdict when all floors pass."""
        passed_count = sum(1 for r in floor_results if r.passed)
        total_count = len(floor_results)

        reason = f"All constitutional floors passed ({passed_count}/{total_count})"

        recommendations = [
            "ACTION APPROVED: All floors passed.",
            "Proceed with execution.",
        ]

        if entropy_result:
            recommendations.append(
                f"Entropy acceptable: ΔS={entropy_result.delta_s:.2f} < {entropy_result.threshold}"
            )
            recommendations.append(
                f"Risk level: {entropy_result.risk_level} ({entropy_result.risk_score:.2f})"
            )

        metadata = {
            "floors_passed": passed_count,
            "floors_total": total_count,
            "all_passed": True,
        }

        if entropy_result:
            metadata["delta_s"] = entropy_result.delta_s
            metadata["risk_score"] = entropy_result.risk_score
            metadata["risk_level"] = entropy_result.risk_level

        return Verdict(
            status="SEAL",
            reason=reason,
            floor_failures=[],
            recommendations=recommendations,
            metadata=metadata,
        )

    def should_allow_execution(self, verdict: Verdict) -> bool:
        """
        Determine if action should be allowed to execute based on verdict.

        Execution Policy:
        - SEAL: Execute ✓
        - PARTIAL: Execute with warnings ✓
        - 888_HOLD: Block until human approval ✗
        - VOID: Block ✗
        - SABAR: Block ✗

        Args:
            verdict: Verdict from generate_verdict()

        Returns:
            True if execution allowed, False otherwise
        """
        allowed_statuses = ["SEAL", "PARTIAL"]
        return verdict.status in allowed_statuses

    def get_verdict_precedence(self, verdict: Verdict) -> int:
        """
        Get precedence value for verdict (higher = takes precedence).

        Hierarchy: SABAR > VOID > 888_HOLD > PARTIAL > SEAL

        Args:
            verdict: Verdict instance

        Returns:
            Precedence value (0-4)
        """
        precedence_map = {
            "SABAR": 4,
            "VOID": 3,
            "888_HOLD": 2,
            "PARTIAL": 1,
            "SEAL": 0,
        }
        return precedence_map.get(verdict.status, -1)

    def merge_verdicts(self, verdicts: List[Verdict]) -> Verdict:
        """
        Merge multiple verdicts by precedence (highest precedence wins).

        Used for multi-agent orchestration where multiple verdicts need
        to be combined into a single final verdict.

        Args:
            verdicts: List of Verdict instances

        Returns:
            Merged verdict (highest precedence)
        """
        if not verdicts:
            return Verdict(
                status="VOID",
                reason="No verdicts to merge",
                recommendations=["No actions were evaluated"],
            )

        # Sort by precedence (highest first)
        sorted_verdicts = sorted(
            verdicts,
            key=lambda v: self.get_verdict_precedence(v),
            reverse=True,
        )

        # Highest precedence wins
        winning_verdict = sorted_verdicts[0]

        # Merge metadata from all verdicts
        merged_metadata = {
            "merged_from": len(verdicts),
            "verdict_breakdown": {
                v.status: sum(1 for vd in verdicts if vd.status == v.status)
                for v in verdicts
            },
        }
        merged_metadata.update(winning_verdict.metadata)

        # Merge floor failures
        merged_failures = []
        for v in verdicts:
            merged_failures.extend(v.floor_failures)

        # Merge recommendations
        merged_recommendations = [
            f"MERGED VERDICT ({len(verdicts)} actions evaluated):",
            f"Final status: {winning_verdict.status}",
            "",
            "Winning verdict reason:",
            winning_verdict.reason,
            "",
        ]
        merged_recommendations.extend(winning_verdict.recommendations)

        return Verdict(
            status=winning_verdict.status,
            reason=f"Merged from {len(verdicts)} verdicts: {winning_verdict.reason}",
            floor_failures=merged_failures,
            recommendations=merged_recommendations,
            metadata=merged_metadata,
        )
