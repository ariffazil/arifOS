"""
Engineering Eureka Agent — Substrate-aware engineering forge agent.

The Eureka Agent is the execution arm of the substrate doctrine.
It coordinates:
- SubstrateIndex: know what tools/libs are available
- SignalDetector: recognize eureka patterns
- EngineeringClaimValidator: validate claims before emission
- Pydantic AI: typed contracts
- OpenTelemetry: trace every action
- OPA: policy gates before any mutation
- arifOS governance: floor compliance

Usage:
    agent = EngineeringEurekaAgent()
    agent.bootstrap()  # builds substrate index
    signals = agent.scan_for_signals("OPA denied: floor F11 unbound")
    claim = EngineeringClaim(...)
    verdict, issues = agent.validate(claim)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .signals import EngineeringSignal, SignalDetector
from .substrate import SubstrateIndex
from .validator import EngineeringClaim, EngineeringClaimValidator, ValidationVerdict


class EurekaSignal(str, Enum):
    """High-level eureka moment types."""

    SUBSTRATE_INSTALLED = "substrate_installed"
    FLOOR_VIOLATION = "floor_violation"
    POLICY_DENY = "policy_deny"
    SEAL_CANDIDATE = "seal_candidate"
    CROSS_DOMAIN_INSIGHT = "cross_domain_insight"


@dataclass
class EurekaResult:
    """Result of a Eureka Agent operation."""

    operation: str
    success: bool
    signals: list[EngineeringSignal] = field(default_factory=list)
    notes: str = ""
    evidence: list[str] = field(default_factory=list)
    floor_compliance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "success": self.success,
            "signals": [
                {
                    "signal_id": s.signal_id,
                    "signal_type": s.signal_type.value,
                    "title": s.title,
                    "confidence": s.confidence,
                }
                for s in self.signals
            ],
            "notes": self.notes,
            "evidence": self.evidence,
            "floor_compliance": self.floor_compliance,
        }


class EngineeringEurekaAgent:
    """
    Substrate-aware engineering forge agent.

    Doctrine: engineering intelligence is forged through substrate discipline,
    not granted by LLM eloquence. This agent:
    - Knows what substrate exists (SubstrateIndex)
    - Detects eureka signals (SignalDetector)
    - Validates claims (EngineeringClaimValidator)
    - Respects constitutional floors (F1, F2, F4, F7, F8, F9, F11, F13)
    - Traces every action (OpenTelemetry)
    - Gates mutations through OPA (Phase 2)
    """

    def __init__(
        self,
        substrate_index: SubstrateIndex | None = None,
        signal_detector: SignalDetector | None = None,
        validator: EngineeringClaimValidator | None = None,
    ):
        self.substrate = substrate_index or SubstrateIndex()
        self.signals = signal_detector or SignalDetector()
        self.validator = validator or EngineeringClaimValidator()
        self._bootstrapped = False
        self._operation_count = 0

    def bootstrap(self) -> EurekaResult:
        """Build the substrate index. Idempotent."""
        if self._bootstrapped:
            return EurekaResult(
                operation="bootstrap",
                success=True,
                notes="Already bootstrapped",
                floor_compliance=["F1_AMANAH", "F11_AUDIT"],
            )

        summary_before = self.substrate.summary()
        self.substrate.build()
        summary_after = self.substrate.summary()

        self._bootstrapped = True
        self._operation_count += 1

        return EurekaResult(
            operation="bootstrap",
            success=True,
            notes=f"Substrate index built: {summary_after['available']}/{summary_after['total']} available",
            evidence=[
                f"available={summary_after['available']}",
                f"missing={summary_after['missing']}",
                f"missing_names={summary_after['missing_names']}",
            ],
            floor_compliance=["F1_AMANAH", "F2_TRUTH", "F11_AUDIT"],
        )

    def scan_for_signals(
        self, text: str, context: dict | None = None
    ) -> EurekaResult:
        """Scan text for eureka signals."""
        self._ensure_bootstrapped()
        signals = self.signals.detect(text, context=context)
        self._operation_count += 1

        return EurekaResult(
            operation="scan_for_signals",
            success=True,
            signals=signals,
            notes=f"Detected {len(signals)} signals in {len(text)} chars",
            evidence=[text[:200]],
            floor_compliance=["F2_TRUTH", "F11_AUDIT"],
        )

    def validate_claim(
        self, claim: EngineeringClaim
    ) -> EurekaResult:
        """Validate an engineering claim against constitutional floors."""
        self._ensure_bootstrapped()
        verdict, issues = self.validator.validate(claim)
        self._operation_count += 1

        success = verdict == ValidationVerdict.SEAL
        notes = f"Verdict: {verdict.value}"
        if issues:
            notes += f" — Issues: {'; '.join(issues)}"

        return EurekaResult(
            operation="validate_claim",
            success=success,
            notes=notes,
            evidence=[claim.claim[:200]],
            floor_compliance=claim.floor_compliance or ["F2_TRUTH", "F11_AUDIT"],
        )

    def substrate_summary(self) -> dict:
        """Return the substrate summary (for telemetry/inspection)."""
        self._ensure_bootstrapped()
        return self.substrate.summary()

    def _ensure_bootstrapped(self) -> None:
        if not self._bootstrapped:
            self.bootstrap()

    def operation_count(self) -> int:
        return self._operation_count
