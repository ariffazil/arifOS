"""
wealth.py - @WEALTH Organ (Resource Stewardship / Amanah)

@WEALTH is the trust/mandate organ of W@W Federation.
Domain: Scope control, reversibility, resource integrity, fairness, dignity

Version: v36.3Omega
Status: PRODUCTION
Alignment: archive/versions/v36_3_omega/v36.3O/spec/waw_wealth_spec_v36.3O.yaml

Core responsibilities:
- Amanah (trust) enforcement = LOCK (must be true)
- Scope boundary protection
- Reversibility checking
- Fairness/bias detection
- Dignity (maruah) protection
- Exploitation risk assessment

This organ is part of W@W Federation:
@WEALTH (Integrity) -> highest veto priority (ABSOLUTE)

Veto Type: ABSOLUTE (Non-negotiable veto on trust violation)

Lead Stages: 666 ALIG, 777 FORG, 888 JUDGE

See: archive/versions/v36_3_omega/v36.3O/spec/waw_wealth_spec_v36.3O.yaml
     archive/versions/v36_3_omega/v36.3O/spec/wealth_floors_v36.3O.json
     canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..metrics import Metrics
from .base import OrganSignal, OrganVote, WAWOrgan
from .bridges.wealth_bridge import WealthBridge


# -----------------------------------------------------------------------------
# Wealth Governance Types (v36.3Omega)
# -----------------------------------------------------------------------------

@dataclass
class WealthSignals:
    """
    Governance signals for integrity/Amanah under @WEALTH organ.

    These signals measure integrity-level constitutional floors:
    - F6: Amanah (trust lock)
    - F7: RASA (felt care)
    - Bias/fairness assessment
    - Dignity (maruah) risk
    - Exploitation risk

    Primary signal: amanah_ok (boolean) - any breach triggers ABSOLUTE VETO.
    """

    # Core integrity floor (F6)
    amanah_ok: bool = True  # Trust lock - must be True for any non-VOID verdict

    # Fairness metrics (soft floors)
    bias_index: float = 0.0       # Range: 0.0-1.0, lower is better
    dignity_risk: float = 0.0     # Range: 0.0-1.0, lower is better
    exploitation_risk: float = 0.0  # Range: 0.0-1.0, lower is better

    # Pattern counts (diagnostic)
    scope_violation_count: int = 0
    irreversible_count: int = 0
    trust_violation_count: int = 0
    fairness_violation_count: int = 0
    dignity_violation_count: int = 0
    exploitation_pattern_count: int = 0

    # Human-readable outputs
    issues: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    # Bridge results (optional external tools)
    bridge_results: Dict[str, Any] = field(default_factory=dict)


# -----------------------------------------------------------------------------
# @WEALTH W@W Organ (WAWOrgan interface + governance signals)
# -----------------------------------------------------------------------------

class WealthOrgan(WAWOrgan):
    """
    @WEALTH - Resource Stewardship Organ

    Guards trust (Amanah), scope boundaries, resource integrity, fairness,
    and dignity (maruah). Issues ABSOLUTE veto on trust violations - non-negotiable.

    WAW Interface:
        check(output_text, metrics, context) -> OrganSignal

    Governance Interface (v36.3Omega):
        compute_wealth_signals(text, metrics, context) -> WealthSignals

    Metrics:
    - Amanah = trust lock (must be TRUE)
    - bias_index = fairness score (< 0.20 for SEAL)
    - dignity_risk = maruah protection (< 0.20 for SEAL)
    - exploitation_risk = ethical framing (< 0.20 for SEAL)

    Veto: ABSOLUTE when Amanah = false (non-negotiable VOID)
    """

    organ_id = "@WEALTH"
    domain = "resource_stewardship"
    primary_metric = "amanah"
    floor_threshold = 1.0  # Amanah must be true (1.0)
    veto_type = "ABSOLUTE"

    # -------------------------------------------------------------------------
    # Scope violation patterns (exceeding mandate)
    # These break Amanah immediately
    # -------------------------------------------------------------------------
    SCOPE_VIOLATION_PATTERNS: List[str] = [
        r"\bdelete all\b",
        r"\bformat disk\b",
        r"\bdrop database\b",
        r"\brm -rf\b",
        r"\bsudo\b",
        r"\broot access\b",
        r"\badmin override\b",
        r"\bbypass security\b",
    ]

    # -------------------------------------------------------------------------
    # Irreversible action patterns
    # Trigger WARN/888_HOLD but don't break Amanah alone
    # -------------------------------------------------------------------------
    IRREVERSIBLE_PATTERNS: List[str] = [
        r"\bpermanently\b",
        r"\bcannot be undone\b",
        r"\birreversible\b",
        r"\bno going back\b",
        r"\bforce push\b",
        r"\b--force\b",
        r"\bhard reset\b",
    ]

    # -------------------------------------------------------------------------
    # Trust violation patterns
    # These break Amanah immediately
    # -------------------------------------------------------------------------
    TRUST_VIOLATION_PATTERNS: List[str] = [
        r"\bI'll do it anyway\b",
        r"\bignore the rules\b",
        r"\bskip verification\b",
        r"\bwithout permission\b",
        r"\boverride safety\b",
    ]

    # -------------------------------------------------------------------------
    # Fairness/bias patterns (v36.3Omega)
    # Increase bias_index score
    # -------------------------------------------------------------------------
    FAIRNESS_VIOLATION_PATTERNS: List[str] = [
        r"\bonly for\b.*\b(men|women|whites|blacks|muslims|christians)\b",
        r"\bdiscriminate\b",
        r"\bunfair\s+advantage\b",
        r"\bexclude\b.*\b(from|based on)\b",
        r"\bfavor\b.*\b(over|instead)\b",
        r"\bprivilege\b.*\b(over|above)\b",
    ]

    # -------------------------------------------------------------------------
    # Dignity (maruah) violation patterns (v36.3Omega)
    # Increase dignity_risk score
    # -------------------------------------------------------------------------
    DIGNITY_VIOLATION_PATTERNS: List[str] = [
        r"\bhumiliate\b",
        r"\bdegrade\b",
        r"\bmock\b",
        r"\bbelittle\b",
        r"\bshame\b",
        r"\bembarrass\b",
        r"\bdemean\b",
        r"\bridiculed?\b",
        r"\binsult\b",
    ]

    # -------------------------------------------------------------------------
    # Exploitation patterns (v36.3Omega)
    # Increase exploitation_risk score
    # -------------------------------------------------------------------------
    EXPLOITATION_PATTERNS: List[str] = [
        r"\btake advantage\b",
        r"\bexploit\b",
        r"\bmanipulate\b.*\bfor\s+(gain|profit|benefit)\b",
        r"\bextract\b.*\bwithout\s+consent\b",
        r"\bcoerce\b",
        r"\bpressure\b.*\binto\b",
    ]

    def __init__(self) -> None:
        super().__init__()
        self.bridge = WealthBridge()

    # =========================================================================
    # Governance Interface: Wealth-level signals (v36.3Omega)
    # =========================================================================

    @staticmethod
    def compute_wealth_signals(
        text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> WealthSignals:
        """
        Compute all governance signals for integrity/Amanah assessment.

        This is the primary interface for integrity-level governance (v36.3Omega).

        Args:
            text: The text to evaluate
            metrics: Constitutional metrics from AAA engines
            context: Additional context (optional)

        Returns:
            WealthSignals dataclass with all integrity metrics
        """
        context = context or {}
        signals = WealthSignals()
        text_lower = text.lower()

        # 1. Start with Amanah from metrics
        signals.amanah_ok = metrics.amanah

        # 2. Detect scope violations (breaks Amanah immediately)
        for pattern in WealthOrgan.SCOPE_VIOLATION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.scope_violation_count += len(matches)

        if signals.scope_violation_count > 0:
            signals.amanah_ok = False
            signals.issues.append(f"scope_violations={signals.scope_violation_count}")

        # 3. Detect trust violations (breaks Amanah immediately)
        for pattern in WealthOrgan.TRUST_VIOLATION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.trust_violation_count += len(matches)

        if signals.trust_violation_count > 0:
            signals.amanah_ok = False
            signals.issues.append(f"trust_violations={signals.trust_violation_count}")

        # 4. Detect irreversible actions (warns, doesn't break Amanah alone)
        for pattern in WealthOrgan.IRREVERSIBLE_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.irreversible_count += len(matches)

        if signals.irreversible_count > 0:
            signals.issues.append(f"irreversible_actions={signals.irreversible_count}")

        # 5. Compute bias_index from fairness violations
        for pattern in WealthOrgan.FAIRNESS_VIOLATION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.fairness_violation_count += len(matches)

        # Each fairness violation adds 0.15 to bias_index (capped at 1.0)
        signals.bias_index = min(1.0, signals.fairness_violation_count * 0.15)

        if signals.fairness_violation_count > 0:
            signals.issues.append(f"bias_index={signals.bias_index:.2f}")

        # 6. Compute dignity_risk from dignity violations
        for pattern in WealthOrgan.DIGNITY_VIOLATION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.dignity_violation_count += len(matches)

        # Each dignity violation adds 0.15 to dignity_risk (capped at 1.0)
        signals.dignity_risk = min(1.0, signals.dignity_violation_count * 0.15)

        if signals.dignity_violation_count > 0:
            signals.issues.append(f"dignity_risk={signals.dignity_risk:.2f}")

        # 7. Compute exploitation_risk from exploitation patterns
        for pattern in WealthOrgan.EXPLOITATION_PATTERNS:
            matches = re.findall(pattern, text_lower)
            signals.exploitation_pattern_count += len(matches)

        # Each exploitation pattern adds 0.15 to exploitation_risk (capped at 1.0)
        signals.exploitation_risk = min(1.0, signals.exploitation_pattern_count * 0.15)

        if signals.exploitation_pattern_count > 0:
            signals.issues.append(f"exploitation_risk={signals.exploitation_risk:.2f}")

        # 8. Final Amanah status note
        if not signals.amanah_ok:
            signals.issues.append("Amanah=BROKEN")
        else:
            signals.notes.append("Amanah=LOCK")

        return signals

    # =========================================================================
    # WAW Interface: check() for federation
    # =========================================================================

    def check(
        self,
        output_text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> OrganSignal:
        """
        Evaluate output for trust and resource integrity.

        This method satisfies the WAWOrgan interface for W@W Federation.

        Checks:
        1. Amanah = true (trust lock)
        2. No scope violations
        3. No irreversible actions without explicit approval
        4. No trust violations
        5. Fairness/bias assessment (v36.3Omega)
        6. Dignity risk assessment (v36.3Omega)
        7. Exploitation risk assessment (v36.3Omega)

        Returns:
            OrganSignal with PASS/WARN/VETO (VETO is ABSOLUTE)
        """
        context = context or {}

        # Compute wealth signals
        wealth = self.compute_wealth_signals(output_text, metrics, context)

        # Optional external bridge analysis
        bridge_result = None
        try:
            bridge_result = self.bridge.analyze(output_text, context)
        except Exception:
            bridge_result = None

        # Apply bridge signal (if any) as additional breach indicator
        if bridge_result is not None:
            bridge_data = bridge_result.to_dict()
            wealth.bridge_results = bridge_data
            if bool(bridge_data.get("amanah_breach", False)):
                wealth.amanah_ok = False
                wealth.issues.append("[Bridge] Amanah breach detected")
            bridge_issues = list(bridge_data.get("issues", []))
            for issue in bridge_issues:
                wealth.issues.append(f"[Bridge] {issue}")

        # Build evidence string
        evidence = f"Amanah={'LOCK' if wealth.amanah_ok else 'BROKEN'}"
        if wealth.issues:
            evidence += f" | Issues: {', '.join(wealth.issues)}"

        # Amanah metric value for OrganSignal
        amanah_value = 1.0 if wealth.amanah_ok else 0.0

        # Determine vote based on signals
        if not wealth.amanah_ok:
            # ABSOLUTE VETO - trust violation (non-negotiable)
            return self._make_signal(
                vote=OrganVote.VETO,
                metric_value=amanah_value,
                evidence=evidence,
                tags={
                    "amanah_ok": wealth.amanah_ok,
                    "bias_index": wealth.bias_index,
                    "dignity_risk": wealth.dignity_risk,
                    "exploitation_risk": wealth.exploitation_risk,
                    "scope_violation_count": wealth.scope_violation_count,
                    "irreversible_count": wealth.irreversible_count,
                    "trust_violation_count": wealth.trust_violation_count,
                },
                is_absolute_veto=True,  # Non-negotiable
                proposed_action=(
                    "ABSOLUTE: Cannot proceed. Trust/Amanah violation requires human review."
                ),
            )

        # Check for high risk scores that need SABAR
        high_risk = (
            wealth.bias_index >= 0.40 or
            wealth.dignity_risk >= 0.40 or
            wealth.exploitation_risk >= 0.40
        )

        if high_risk:
            # WARN with SABAR recommendation (repairable)
            repairs = []
            if wealth.bias_index >= 0.40:
                repairs.append(f"Reduce bias (current: {wealth.bias_index:.2f})")
            if wealth.dignity_risk >= 0.40:
                repairs.append(f"Protect dignity (current: {wealth.dignity_risk:.2f})")
            if wealth.exploitation_risk >= 0.40:
                repairs.append(f"Remove exploitation (current: {wealth.exploitation_risk:.2f})")

            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=amanah_value,
                evidence=evidence,
                tags={
                    "amanah_ok": wealth.amanah_ok,
                    "bias_index": wealth.bias_index,
                    "dignity_risk": wealth.dignity_risk,
                    "exploitation_risk": wealth.exploitation_risk,
                },
                proposed_action=f"SABAR: {'; '.join(repairs)}",
            )

        if wealth.irreversible_count > 0:
            # WARN - irreversible but within scope (888_HOLD consideration)
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=amanah_value,
                evidence=evidence,
                tags={
                    "amanah_ok": wealth.amanah_ok,
                    "irreversible_count": wealth.irreversible_count,
                    "bias_index": wealth.bias_index,
                    "dignity_risk": wealth.dignity_risk,
                    "exploitation_risk": wealth.exploitation_risk,
                },
                proposed_action=(
                    "Confirm irreversible action with explicit user approval (888_HOLD)"
                ),
            )

        # Check for moderate risk (PARTIAL warning)
        moderate_risk = (
            wealth.bias_index >= 0.20 or
            wealth.dignity_risk >= 0.20 or
            wealth.exploitation_risk >= 0.20
        )

        if moderate_risk:
            return self._make_signal(
                vote=OrganVote.WARN,
                metric_value=amanah_value,
                evidence=evidence,
                tags={
                    "amanah_ok": wealth.amanah_ok,
                    "bias_index": wealth.bias_index,
                    "dignity_risk": wealth.dignity_risk,
                    "exploitation_risk": wealth.exploitation_risk,
                },
                proposed_action="Minor fairness/dignity concerns - proceed with caution",
            )

        # PASS - trust intact, all risk scores low
        return self._make_signal(
            vote=OrganVote.PASS,
            metric_value=amanah_value,
            evidence=evidence,
            tags={
                "amanah_ok": wealth.amanah_ok,
                "bias_index": wealth.bias_index,
                "dignity_risk": wealth.dignity_risk,
                "exploitation_risk": wealth.exploitation_risk,
            },
        )


# -----------------------------------------------------------------------------
# Convenience function for pipeline integration
# -----------------------------------------------------------------------------

def compute_wealth_signals(
    text: str,
    metrics: Metrics,
    context: Optional[Dict[str, Any]] = None,
) -> WealthSignals:
    """
    Pipeline-friendly entry point for integrity/Amanah governance.

    Usage in arifos_core/pipeline.py (stage 666 ALIG, 777 FORG):
        from arifos_core.waw.wealth import compute_wealth_signals
        signals = compute_wealth_signals(output_text, metrics)
        if not signals.amanah_ok:
            # ABSOLUTE VETO - trust broken
    """
    return WealthOrgan.compute_wealth_signals(text, metrics, context)


__all__ = [
    "WealthOrgan",
    "WealthSignals",
    "compute_wealth_signals",
]
