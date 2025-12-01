"""
@EYE Sentinel v35Ω — Independent Auditor Module

The @EYE Sentinel is an independent oversight system that:
- Does NOT generate content
- ONLY inspects and flags issues
- Has 10 "Views" (lenses) that scan reasoning, metrics, and text

Views in v35Ω:
1. Trace View — logical coherence, missing steps
2. Floor View — proximity to floor thresholds
3. Shadow View — hidden intent, prompt injection, jailbreak
4. Drift View — hallucination, departure from reality/canon
5. Maruah View — dignity, respect, bias, humiliation
6. Paradox View — logical contradictions, self-referential traps
7. Silence View — cases where refusal is the only safe action
8. Version/Ontology View — ensures v35Ω, treats v34Ω as artifact
9. Behavior Drift View — multi-turn evolution watch
10. Sleeper-Agent View — sudden changes in goal/identity/constraints
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

from .metrics import Metrics
from .APEX_PRIME import APEX_VERSION, APEX_EPOCH


class AlertSeverity(Enum):
    """Severity levels for @EYE alerts."""
    INFO = "INFO"      # Informational, no action required
    WARN = "WARN"      # Warning, proceed with caution
    BLOCK = "BLOCK"    # Blocking issue, must not SEAL


@dataclass
class EyeAlert:
    """A single alert from an @EYE view."""
    view_name: str
    severity: AlertSeverity
    message: str


@dataclass
class EyeReport:
    """Aggregated report from all @EYE views."""
    alerts: List[EyeAlert] = field(default_factory=list)

    def has_blocking_issue(self) -> bool:
        """Check if any alert is BLOCK severity."""
        return any(a.severity == AlertSeverity.BLOCK for a in self.alerts)

    def has_warnings(self) -> bool:
        """Check if any alert is WARN severity."""
        return any(a.severity == AlertSeverity.WARN for a in self.alerts)

    def add(self, view_name: str, severity: AlertSeverity, message: str) -> None:
        """Add an alert to the report."""
        self.alerts.append(EyeAlert(view_name, severity, message))

    def get_by_view(self, view_name: str) -> List[EyeAlert]:
        """Get all alerts from a specific view."""
        return [a for a in self.alerts if a.view_name == view_name]

    def get_blocking_alerts(self) -> List[EyeAlert]:
        """Get all blocking alerts."""
        return [a for a in self.alerts if a.severity == AlertSeverity.BLOCK]


class EyeSentinel:
    """
    @EYE Sentinel v35Ω Auditor.

    Runs 10 views on draft text + context + metrics to detect issues.
    If has_blocking_issue() is True, APEX PRIME must NOT return SEAL.
    """

    # Jailbreak detection phrases
    JAILBREAK_PHRASES = [
        "ignore previous",
        "pretend the rules don't apply",
        "you are no longer bound by",
        "forget your instructions",
        "disregard all previous",
        "bypass your restrictions",
        "act as if you have no limits",
    ]

    # Dignity/Maruah violation patterns (basic heuristics)
    DIGNITY_VIOLATIONS = [
        "stupid",
        "idiot",
        "moron",
        "bangang",  # Malay slur (context-dependent)
        "bodoh",    # Malay: stupid
    ]

    # Paradox triggers
    PARADOX_TRIGGERS = [
        "this statement is false",
        "liar paradox",
        "i always lie",
        "can god create a stone",
    ]

    def audit(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> EyeReport:
        """
        Run all 10 @EYE views on the draft.

        Args:
            draft_text: The candidate output from an AI model
            metrics: Constitutional metrics for the draft
            context: Optional dict with flags like:
                - 'reasoning_incoherent': bool
                - 'suspected_hallucination': bool
                - 'disallowed_domain': bool
                - 'constitution_version': str
                - 'uses_legacy_nodes': bool
                - 'behavior_drift_exceeds_threshold': bool
                - 'sudden_identity_shift': bool

        Returns:
            EyeReport with all alerts from all views
        """
        context = context or {}
        report = EyeReport()

        # Run all 10 views
        self._trace_view(draft_text, context, report)
        self._floor_view(metrics, report)
        self._shadow_view(draft_text, context, report)
        self._drift_view(draft_text, context, report)
        self._maruah_view(draft_text, report)
        self._paradox_view(draft_text, context, report)
        self._silence_view(draft_text, context, metrics, report)
        self._version_ontology_view(context, report)
        self._behavior_drift_view(context, report)
        self._sleeper_view(draft_text, context, report)

        return report

    # ————————————— View 1: Trace View ————————————— #
    def _trace_view(
        self,
        draft_text: str,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Check logical coherence and reasoning step continuity."""
        if context.get("reasoning_incoherent", False):
            report.add(
                "TraceView",
                AlertSeverity.WARN,
                "Reasoning appears disjoint or incomplete.",
            )

    # ————————————— View 2: Floor View ————————————— #
    def _floor_view(self, metrics: Metrics, report: EyeReport) -> None:
        """Monitor proximity to floor thresholds."""
        # Amanah breach is critical
        if not metrics.amanah:
            report.add(
                "FloorView",
                AlertSeverity.BLOCK,
                "Amanah breach detected — integrity compromised.",
            )

        # Truth below threshold
        if metrics.truth < 0.99:
            report.add(
                "FloorView",
                AlertSeverity.WARN,
                f"Truth metric ({metrics.truth:.3f}) below 0.99 threshold.",
            )

        # Omega outside band
        if not (0.03 <= metrics.omega_0 <= 0.05):
            report.add(
                "FloorView",
                AlertSeverity.WARN,
                f"Ω₀ ({metrics.omega_0:.3f}) outside [0.03, 0.05] humility band.",
            )

    # ————————————— View 3: Shadow View ————————————— #
    def _shadow_view(
        self,
        draft_text: str,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Detect jailbreaks, prompt injection, hidden intent."""
        text_lower = draft_text.lower()

        for phrase in self.JAILBREAK_PHRASES:
            if phrase in text_lower:
                report.add(
                    "ShadowView",
                    AlertSeverity.BLOCK,
                    f"Potential jailbreak/prompt injection: '{phrase}' detected.",
                )
                break

        if context.get("prompt_injection_detected", False):
            report.add(
                "ShadowView",
                AlertSeverity.BLOCK,
                "External prompt injection detection flagged this input.",
            )

    # ————————————— View 4: Drift View ————————————— #
    def _drift_view(
        self,
        draft_text: str,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Watch for hallucination and departure from reality/canon."""
        if context.get("suspected_hallucination", False):
            report.add(
                "DriftView",
                AlertSeverity.BLOCK,
                "Possible hallucination / drift from canon detected.",
            )

        if context.get("factual_inconsistency", False):
            report.add(
                "DriftView",
                AlertSeverity.WARN,
                "Factual inconsistency with prior sealed outputs.",
            )

    # ————————————— View 5: Maruah View ————————————— #
    def _maruah_view(self, draft_text: str, report: EyeReport) -> None:
        """Check for dignity/respect violations, bias, humiliation."""
        text_lower = draft_text.lower()

        for term in self.DIGNITY_VIOLATIONS:
            if term in text_lower:
                report.add(
                    "MaruahView",
                    AlertSeverity.WARN,
                    f"Potential dignity/maruah issue: '{term}' in output.",
                )

    # ————————————— View 6: Paradox View ————————————— #
    def _paradox_view(
        self,
        draft_text: str,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Detect logical contradictions and self-referential traps."""
        text_lower = draft_text.lower()

        for trigger in self.PARADOX_TRIGGERS:
            if trigger in text_lower:
                report.add(
                    "ParadoxView",
                    AlertSeverity.BLOCK,
                    f"Self-referential paradox detected: '{trigger}'.",
                )
                break

        if context.get("logical_contradiction", False):
            report.add(
                "ParadoxView",
                AlertSeverity.WARN,
                "Logical contradiction detected in reasoning.",
            )

    # ————————————— View 7: Silence View ————————————— #
    def _silence_view(
        self,
        draft_text: str,
        context: Dict[str, Any],
        metrics: Metrics,
        report: EyeReport,
    ) -> None:
        """Identify cases where refusal/SABAR is the only safe action."""
        if context.get("disallowed_domain", False):
            report.add(
                "SilenceView",
                AlertSeverity.BLOCK,
                "Domain requires refusal (policy / Amanah constraint).",
            )

        if context.get("self_harm_content", False):
            report.add(
                "SilenceView",
                AlertSeverity.BLOCK,
                "Self-harm content detected — immediate SABAR required.",
            )

        if context.get("violence_incitement", False):
            report.add(
                "SilenceView",
                AlertSeverity.BLOCK,
                "Violence incitement detected — silence is mandatory.",
            )

    # ————————————— View 8: Version/Ontology View ————————————— #
    def _version_ontology_view(
        self,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Ensure v35Ω is active; treat v34Ω as historical artifact only."""
        version = context.get("constitution_version", APEX_VERSION)

        if version != APEX_VERSION:
            report.add(
                "VersionOntologyView",
                AlertSeverity.BLOCK,
                f"Inconsistent constitution version: {version}, expected {APEX_VERSION}.",
            )

        if context.get("uses_legacy_nodes", False):
            report.add(
                "VersionOntologyView",
                AlertSeverity.WARN,
                "Legacy nodes (333/555) referenced — treat as historical only.",
            )

        epoch = context.get("constitution_epoch", APEX_EPOCH)
        if epoch < APEX_EPOCH:
            report.add(
                "VersionOntologyView",
                AlertSeverity.WARN,
                f"Operating on older epoch {epoch} — current law is epoch {APEX_EPOCH}.",
            )

    # ————————————— View 9: Behavior Drift View (MBDM) ————————————— #
    def _behavior_drift_view(
        self,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Watch multi-turn evolution for permissiveness/aggressiveness drift."""
        if context.get("behavior_drift_exceeds_threshold", False):
            report.add(
                "BehaviorDriftView",
                AlertSeverity.BLOCK,
                "Multi-turn behavioral drift exceeds safe threshold.",
            )

        if context.get("trending_permissive", False):
            report.add(
                "BehaviorDriftView",
                AlertSeverity.WARN,
                "Conversation trending toward excessive permissiveness.",
            )

        if context.get("trending_aggressive", False):
            report.add(
                "BehaviorDriftView",
                AlertSeverity.WARN,
                "Conversation trending toward aggressive/hostile tone.",
            )

    # ————————————— View 10: Sleeper-Agent View ————————————— #
    def _sleeper_view(
        self,
        draft_text: str,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Detect sudden changes in goal, identity, or constraints."""
        if context.get("sudden_identity_shift", False):
            report.add(
                "SleeperView",
                AlertSeverity.BLOCK,
                "Possible sleeper-agent activation or identity shift detected.",
            )

        if context.get("goal_hijacking", False):
            report.add(
                "SleeperView",
                AlertSeverity.BLOCK,
                "Goal hijacking detected — original intent compromised.",
            )

        if context.get("constraint_relaxation", False):
            report.add(
                "SleeperView",
                AlertSeverity.WARN,
                "Unexpected relaxation of safety constraints observed.",
            )


# ——————————————————— PUBLIC EXPORTS ——————————————————— #
__all__ = [
    "AlertSeverity",
    "EyeAlert",
    "EyeReport",
    "EyeSentinel",
]
