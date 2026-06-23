"""
Signal Detector — Recognizes eureka signals in engineering work.

A "eureka signal" is a pattern that suggests a structural insight is crystallizing.
Common signals:
- Cross-domain mapping (the same abstraction appears in N+1 domains)
- Entropy drop (complexity collapses to a simpler form)
- Substrate gap closure (a missing capability is now filled)
- Convergent optimization (multiple independent metrics improve)
- Anti-pattern detection (a known bad pattern is being repeated)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SignalType(str, Enum):
    """Types of engineering eureka signals."""

    CROSS_DOMAIN_MAPPING = "cross_domain_mapping"  # same abstraction in 2+ domains
    ENTROPY_DROP = "entropy_drop"  # complexity collapses
    SUBSTRATE_GAP_CLOSURE = "substrate_gap_closure"  # missing cap now filled
    CONVERGENT_OPTIMIZATION = "convergent_optimization"  # multiple metrics improve
    ANTI_PATTERN = "anti_pattern"  # known bad pattern
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"  # floor broken
    OPA_DENY = "opa_deny"  # policy rejected
    SEAL_CANDIDATE = "seal_candidate"  # candidate for VAULT999


@dataclass
class EngineeringSignal:
    """A single eureka signal detected in engineering work."""

    signal_id: str
    signal_type: SignalType
    title: str
    description: str
    confidence: float  # 0.0–0.90 (F7 cap)
    evidence: list[str] = field(default_factory=list)
    affected_components: list[str] = field(default_factory=list)
    suggested_action: str = ""
    human_review_required: bool = False


class SignalDetector:
    """Detect eureka signals in engineering work streams."""

    def __init__(self):
        self._detected: list[EngineeringSignal] = []

    def detect(self, text: str, context: dict | None = None) -> list[EngineeringSignal]:
        """
        Scan text for eureka signals. Phase 1: simple heuristic.
        Phase 2: LLM-assisted detection.
        """
        signals = []
        ctx = context or {}

        # Signal: substrate gap closure (was missing, now available)
        if "installed" in text.lower() and ("arifos" in text.lower() or "wealth" in text.lower()):
            signals.append(
                EngineeringSignal(
                    signal_id="sig-substrate-installed",
                    signal_type=SignalType.SUBSTRATE_GAP_CLOSURE,
                    title="Substrate library installed",
                    description="A substrate library was added to a federation organ.",
                    confidence=0.85,
                    evidence=[text[:200]],
                    affected_components=ctx.get("organs", []),
                    suggested_action="Verify the install with `make test` and add to substrate index.",
                )
            )

        # Signal: constitutional violation (floor named with negative finding)
        for floor in ["F1", "F2", "F4", "F7", "F8", "F9", "F11", "F13"]:
            if floor in text and (
                "violation" in text.lower() or "breach" in text.lower() or "unbound" in text.lower()
            ):
                signals.append(
                    EngineeringSignal(
                        signal_id=f"sig-constitutional-{floor}",
                        signal_type=SignalType.CONSTITUTIONAL_VIOLATION,
                        title=f"Constitutional floor {floor} potentially violated",
                        description=f"Text references floor {floor} with negative context.",
                        confidence=0.75,
                        evidence=[text[:200]],
                        human_review_required=True,
                        suggested_action=f"Review {floor} status with sovereign before proceeding.",
                    )
                )

        # Signal: OPA deny
        if "deny" in text.lower() and "opa" in text.lower():
            signals.append(
                EngineeringSignal(
                    signal_id="sig-opa-deny",
                    signal_type=SignalType.OPA_DENY,
                    title="OPA returned DENY",
                    description="An OPA policy evaluation returned DENY.",
                    confidence=0.95,
                    evidence=[text[:200]],
                    human_review_required=True,
                    suggested_action="Inspect policy + input; do not proceed without override.",
                )
            )

        # Signal: seal candidate
        if "seal" in text.lower() and ("vault" in text.lower() or "999" in text):
            signals.append(
                EngineeringSignal(
                    signal_id="sig-seal-candidate",
                    signal_type=SignalType.SEAL_CANDIDATE,
                    title="Seal candidate detected",
                    description="A VAULT999 seal candidate is being prepared.",
                    confidence=0.80,
                    evidence=[text[:200]],
                    suggested_action="Verify floor compliance before invoking arif_seal.",
                )
            )

        self._detected.extend(signals)
        return signals

    def detected(self) -> list[EngineeringSignal]:
        return list(self._detected)
