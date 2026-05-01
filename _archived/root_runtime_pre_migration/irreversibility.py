"""
arifos/runtime/irreversibility.py — Amanah Irreversibility Scorer

F1 (Amanah) Enforcement: Deterministic pre-execution scoring of tool payloads.
If score exceeds threshold → triggers 888_HOLD via HoldStateManager.

DITEMPA BUKAN DIBERI — Forged, Not Given
Author: 888_VALIDATOR | Version: 2026.04.10-CANONICAL
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from arifos.runtime.substrate_policy import (
    RiskTier,
    SubstrateClass,
    get_policy,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CRITICAL PATTERN SIGNATURES — tools that MUST trigger HOLD regardless of tier
# ---------------------------------------------------------------------------

CRITICAL_PATTERNS: list[tuple[str, str]] = [
    # (pattern_substring, reason)
    ("DROP TABLE", "irreversible_data_destruction"),
    ("DROP DATABASE", "irreversible_database_destruction"),
    ("rm -rf", "irreversible_filesystem_destruction"),
    ("rm -rf /", "catastrophic_filesystem_destruction"),
    ("FORMAT", "irreversible_storage_wipe"),
    ("SHUTDOWN", "irreversible_service_termination"),
    ("KILL", "irreversible_process_termination"),
    ("DELETE /", "irreversible_path_destruction"),
    ("sudo", "privilege_escalation"),
    ("chmod 777", "security_violation"),
    ("eval(", "command_injection_vector"),
    ("exec(", "command_injection_vector"),
    ("system(", "shell_injection_vector"),
    ("os.system", "shell_injection_vector"),
    ("subprocess", "unconstrained_execution"),
]

# Irreversibility score thresholds
TIER_SCORES: dict[RiskTier, float] = {
    RiskTier.LOW: 0.0,
    RiskTier.MEDIUM: 0.3,
    RiskTier.HIGH: 0.7,
    RiskTier.CRITICAL: 0.85,
}

# Actions that always score maximum regardless of tier
ALWAYS_IRREVERSIBLE: list[str] = [
    "revoke",
    "drop",
    "delete_all",
    "wipe",
    "shutdown",
    "kill_session",
    "format_disk",
]


@dataclass
class IrreversibilityScore:
    """Result of irreversibility evaluation."""
    score: float  # 0.0 (safe) → 1.0 (catastrophic)
    tier: RiskTier
    triggers_888_hold: bool
    floor_violations: list[str]
    reason: str
    detail: str  # human-readable explanation


class AmanahIrreversibilityScorer:
    """
    F1 (Amanah) — Sacred Trust: Can this be undone?

    Deterministically scores tool call payloads for reversibility risk.
    Wires directly to HoldStateManager when score exceeds threshold.

    Scoring logic:
    - LOW tier    → 0.0 (no hold, proceed)
    - MEDIUM tier → 0.3 (caution, no hold)
    - HIGH tier   → 0.7 (hold triggered)
    - CRITICAL tier → 0.85 (hold triggered)
    - Critical patterns detected → 1.0 (immediate VOID potential, hold + escalate)
    """

    def __init__(self):
        self._hit_count: int = 0

    def evaluate_payload(
        self,
        tool_name: str,
        mode: str,
        args: dict,
        actor_id: str = "anonymous",
    ) -> IrreversibilityScore:
        """
        Evaluate a tool call payload for irreversibility.

        Args:
            tool_name: Tool identifier (e.g. "init_anchor", "arifos_forge")
            mode: Tool mode/key within that tool's policy (e.g. "revoke", "run")
            args: Full argument dict passed to the tool
            actor_id: Who/what is calling this tool

        Returns:
            IrreversibilityScore with score (0.0-1.0), tier, and hold decision
        """
        self._hit_count += 1
        floor_violations: list[str] = []
        reason = "safe"
        detail_parts: list[str] = []

        # 1. Lookup policy for this tool+mode
        policy = get_policy(tool_name, mode)
        if policy is None:
            # Unknown tool — conservative HIGH hold
            logger.warning(f"[Amanah] Unknown tool '{tool_name}' mode '{mode}' — conservative hold")
            return IrreversibilityScore(
                score=0.8,
                tier=RiskTier.HIGH,
                triggers_888_hold=True,
                floor_violations=["F1_UNKNOWN_TOOL"],
                reason="unknown_tool_conservative_hold",
                detail=f"Tool '{tool_name}' not in policy matrix — holding for safety",
            )

        base_score = TIER_SCORES[policy.risk]
        tier = policy.risk
        detail_parts.append(f"base_tier={tier.value} score={base_score}")

        # 2. Check for always-irreversible action keywords in args
        args_str = str(args).lower()
        for irreversible_action in ALWAYS_IRREVERSIBLE:
            if irreversible_action in args_str:
                floor_violations.append(f"F1_IRREVERSIBLE_ACTION:{irreversible_action}")
                detail_parts.append(f"detected_irreversible_action={irreversible_action}")
                base_score = max(base_score, 0.95)  # Cap at near-maximum

        # 3. Check critical pattern signatures in args
        for pattern, pattern_reason in CRITICAL_PATTERNS:
            if pattern.lower() in args_str:
                floor_violations.append(f"F1_CRITICAL_PATTERN:{pattern_reason}")
                detail_parts.append(f"critical_pattern={pattern}")
                base_score = 1.0  # Maximum score — immediate escalation
                reason = f"critical_pattern_detected:{pattern_reason}"
                logger.error(f"[Amanah] CRITICAL pattern detected: '{pattern}' in {tool_name} call by {actor_id}")

        # 4. Substrate class modifiers
        if policy.substrate == SubstrateClass.DELETE:
            base_score = max(base_score, 0.75)
            floor_violations.append("F1_DELETE_SUBSTRATE")
            detail_parts.append("substrate=DELETE boost")
        elif policy.substrate == SubstrateClass.EXECUTE:
            base_score = max(base_score, 0.6)
            detail_parts.append("substrate=EXECUTE")
        elif policy.substrate == SubstrateClass.COMMIT:
            base_score = max(base_score, 0.65)
            floor_violations.append("F1_COMMIT_SUBSTRATE")
            detail_parts.append("substrate=COMMIT")

        # 5. Check for production environment flags
        if self._is_production_risk(args):
            base_score = max(base_score, 0.8)
            floor_violations.append("F1_PRODUCTION_RISK")
            detail_parts.append("production_target=true")

        # 6. Compute final score
        final_score = min(base_score, 1.0)

        # 7. Determine hold threshold
        hold_threshold = 0.7  # Default: HIGH and above trigger hold
        triggers_hold = final_score >= hold_threshold

        if triggers_hold and not floor_violations:
            floor_violations.append("F1_TIER_THRESHOLD_EXCEEDED")

        result = IrreversibilityScore(
            score=round(final_score, 3),
            tier=tier,
            triggers_888_hold=triggers_hold,
            floor_violations=floor_violations,
            reason=reason if reason != "safe" else tier.value,
            detail=" | ".join(detail_parts) if detail_parts else "no_additional_risk_factors",
        )

        logger.info(
            f"[Amanah] scored {tool_name}.{mode} → {result.score} "
            f"(tier={tier.value}, hold={triggers_hold}) {result.detail}"
        )
        return result

    def _is_production_risk(self, args: dict) -> bool:
        """Detect production environment targeting from args."""
        production_indicators = [
            "production",
            "prod",
            "live",
            "main",
            "master",
            "primary",
        ]
        args_str = str(args).lower()
        return any(ind in args_str for ind in production_indicators)

    def get_hold_decision(self, score: IrreversibilityScore) -> bool:
        """Simple threshold check for hold trigger."""
        return score.triggers_888_hold
