"""
core/paradox/circuit_breakers.py — Epistemic Circuit Breakers (CB1-CB5)

Implements PARADOX_DOCTRINE_V1 Section 7 (P6 — Uncertainty vs Contradiction).

Five circuit breakers prevent epistemic collapse:
  CB1: Godellock    — Ω₀ < 0.03 (overconfidence)
  CB2: Single-Witness — Any witness lane W < 0.70
  CB3: Cheap Truth  — τ > 0.99 but evidence < Landauer bound
  CB4: Recursive Stack — Self-reference depth > 3 levels
  CB5: Confidence Cascade — τ rises without new evidence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CircuitBreakerState(Enum):
    TRIPPED = "TRIPPED"
    WARNING = "WARNING"
    OK = "OK"


@dataclass
class CircuitBreaker:
    name: str
    state: CircuitBreakerState
    reason: str
    suggested_action: str
    breaker_id: str


def check_godellock(omega_0: float) -> CircuitBreaker:
    """
    CB1: Godellock — overconfidence breaker.

    When Ω₀ < 0.03, the system is overconfident relative to its
    actual information. This is a self-referential overreach.

    Action: CAUTION. Generate 3+ alternatives. Suppress overconfident claims.
    """
    if omega_0 < 0.03:
        return CircuitBreaker(
            name="CB1-Godellock",
            state=CircuitBreakerState.TRIPPED,
            reason=f"Overconfidence detected — Ω₀={omega_0:.4f} below 0.03 threshold. System claims more certainty than its information supports.",
            suggested_action="CAUTION. Generate 3+ alternative hypotheses. Suppress overconfident claims.",
            breaker_id="CB1",
        )
    elif omega_0 < 0.05:
        return CircuitBreaker(
            name="CB1-Godellock",
            state=CircuitBreakerState.WARNING,
            reason=f"Near-overconfidence — Ω₀={omega_0:.4f}. Monitor closely.",
            suggested_action="Note low uncertainty. Verify evidence grounding.",
            breaker_id="CB1",
        )
    return CircuitBreaker(
        name="CB1-Godellock",
        state=CircuitBreakerState.OK,
        reason=f"Ω₀={omega_0:.4f} in healthy range.",
        suggested_action="Continue.",
        breaker_id="CB1",
    )


def check_single_witness(
    human_witness: float,
    ai_witness: float,
    earth_witness: float,
) -> CircuitBreaker:
    """
    CB2: Single-Witness — insufficient witness lanes.

    Any witness lane W < 0.70 on a consequential task triggers HOLD.

    Action: HOLD. Human escalation required. More evidence needed.
    """
    lanes: list[tuple[str, float]] = [
        ("human", human_witness),
        ("ai", ai_witness),
        ("earth", earth_witness),
    ]
    weak_lanes = [(name, val) for name, val in lanes if val < 0.70]
    active_lanes = [(name, val) for name, val in lanes if val > 0]

    if len(active_lanes) < 2:
        return CircuitBreaker(
            name="CB2-SingleWitness",
            state=CircuitBreakerState.TRIPPED,
            reason=f"Only {len(active_lanes)} witness lane(s) active. Minimum 2 required for consequential actions.",
            suggested_action="HOLD. Escalate to human. Gather additional witness evidence.",
            breaker_id="CB2",
        )
    if weak_lanes:
        return CircuitBreaker(
            name="CB2-SingleWitness",
            state=CircuitBreakerState.WARNING,
            reason=f"Weak witness lanes: {', '.join(f'{n}={v:.2f}' for n, v in weak_lanes)}",
            suggested_action="Note weak witness signal. Strengthen evidence before high-stakes judgment.",
            breaker_id="CB2",
        )
    return CircuitBreaker(
        name="CB2-SingleWitness",
        state=CircuitBreakerState.OK,
        reason=f"All witness lanes >= 0.70: human={human_witness:.2f}, ai={ai_witness:.2f}, earth={earth_witness:.2f}",
        suggested_action="Continue.",
        breaker_id="CB2",
    )


def check_cheap_truth(
    tau_truth: float,
    evidence_count: int,
    evidence_relevance: float,
) -> CircuitBreaker:
    """
    CB3: Cheap Truth — fabrication detector.

    When τ > 0.99 but evidence is below the Landauer bound
    (evidence_count * evidence_relevance < 1.0), the system is
    claiming high certainty without sufficient evidence.

    Action: VOID. Fabrication detected. Cannot proceed.
    """
    evidence_product = evidence_count * evidence_relevance

    if tau_truth > 0.99 and evidence_product < 1.0:
        return CircuitBreaker(
            name="CB3-CheapTruth",
            state=CircuitBreakerState.TRIPPED,
            reason=f"Fabrication risk — τ={tau_truth:.4f} with evidence_product={evidence_product:.2f}. High confidence unsupported by evidence.",
            suggested_action="VOID. Do not proceed. Fabrication detected.",
            breaker_id="CB3",
        )
    if tau_truth > 0.95 and evidence_product < 2.0:
        return CircuitBreaker(
            name="CB3-CheapTruth",
            state=CircuitBreakerState.WARNING,
            reason=f"Near-cheap-truth — τ={tau_truth:.4f}, evidence_product={evidence_product:.2f}. Strengthen grounding.",
            suggested_action="CAUTION. Demand additional evidence before proceeding.",
            breaker_id="CB3",
        )
    return CircuitBreaker(
        name="CB3-CheapTruth",
        state=CircuitBreakerState.OK,
        reason=f"Evidence sufficient — τ={tau_truth:.4f}, evidence_product={evidence_product:.2f}",
        suggested_action="Continue.",
        breaker_id="CB3",
    )


def check_recursive_stack(self_reference_depth: int) -> CircuitBreaker:
    """
    CB4: Recursive Stack — self-reference exceeds safe bound.

    When reasoning references itself more than 3 levels deep,
    the system is trapped in a self-referential loop.

    Action: SABAR. Flatten recursion. If persists, escalate to HOLD.
    """
    if self_reference_depth > 5:
        return CircuitBreaker(
            name="CB4-RecursiveStack",
            state=CircuitBreakerState.TRIPPED,
            reason=f"Severe recursion — self-reference depth={self_reference_depth} exceeds maximum safe bound.",
            suggested_action="HOLD. Flatten recursion immediately. Human review required.",
            breaker_id="CB4",
        )
    if self_reference_depth > 3:
        return CircuitBreaker(
            name="CB4-RecursiveStack",
            state=CircuitBreakerState.TRIPPED,
            reason=f"Recursive reasoning detected — depth={self_reference_depth} > 3. Risk of self-validating loops.",
            suggested_action="SABAR. Flatten reasoning chain. Break self-referential loops.",
            breaker_id="CB4",
        )
    return CircuitBreaker(
        name="CB4-RecursiveStack",
        state=CircuitBreakerState.OK,
        reason=f"Self-reference depth={self_reference_depth} within safe bound.",
        suggested_action="Continue.",
        breaker_id="CB4",
    )


def check_confidence_cascade(
    current_confidence: float,
    previous_confidence: float,
    new_evidence_since_last: bool,
    cascade_step: int = 0,
) -> CircuitBreaker:
    """
    CB5: Confidence Cascade — τ rises without new evidence.

    When confidence increases step-over-step without new evidence
    being introduced, the system is in a confidence cascade.

    Action: CAUTION on first detection. HOLD if persists 3+ steps.
    """
    confidence_rose = current_confidence > previous_confidence

    if confidence_rose and not new_evidence_since_last:
        if cascade_step >= 3:
            return CircuitBreaker(
                name="CB5-ConfidenceCascade",
                state=CircuitBreakerState.TRIPPED,
                reason=f"Sustained confidence cascade — {cascade_step} steps without new evidence. Confidence rose from {previous_confidence:.4f} to {current_confidence:.4f}.",
                suggested_action="HOLD. Demand new evidence before proceeding. Confidence cascade may indicate fabrication drift.",
                breaker_id="CB5",
            )
        return CircuitBreaker(
            name="CB5-ConfidenceCascade",
            state=CircuitBreakerState.WARNING,
            reason=f"Confidence rose without new evidence — step {cascade_step}. τ: {previous_confidence:.4f} → {current_confidence:.4f}",
            suggested_action="CAUTION. Demand evidence. If pattern persists 3+ steps, escalate to HOLD.",
            breaker_id="CB5",
        )
    return CircuitBreaker(
        name="CB5-ConfidenceCascade",
        state=CircuitBreakerState.OK,
        reason="Confidence trajectory aligned with evidence flow.",
        suggested_action="Continue.",
        breaker_id="CB5",
    )


def evaluate_all_breakers(
    omega_0: float,
    tau_truth: float,
    evidence_count: int,
    evidence_relevance: float,
    human_witness: float,
    ai_witness: float,
    earth_witness: float,
    self_reference_depth: int = 0,
    current_confidence: float | None = None,
    previous_confidence: float | None = None,
    new_evidence_since_last: bool = True,
    cascade_step: int = 0,
) -> list[CircuitBreaker]:
    """
    Evaluate all 5 circuit breakers and return results.
    Breakers are ordered by severity: CB3 > CB1 > CB4 > CB5 > CB2
    Any TRIPPED breaker triggers the corresponding action.
    """
    results: list[CircuitBreaker] = []

    results.append(check_cheap_truth(tau_truth, evidence_count, evidence_relevance))
    results.append(check_godellock(omega_0))
    results.append(check_recursive_stack(self_reference_depth))

    if current_confidence is not None and previous_confidence is not None:
        results.append(
            check_confidence_cascade(
                current_confidence, previous_confidence,
                new_evidence_since_last, cascade_step,
            )
        )

    results.append(check_single_witness(human_witness, ai_witness, earth_witness))

    return results
