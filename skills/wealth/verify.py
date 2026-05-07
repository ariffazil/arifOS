"""
skills/wealth/verify.py — Verification-First Capital Governance
═══════════════════════════════════════════════════════════════

Post-AGI WEALTH kernel: measures Δm, prices verification scarcity,
preserves human apprenticeship capacity, routes liability.

Each schema is a constitutional data structure — floors F1-F13 enforced.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

EPSILON = 1e-9


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMAS — Canonical input/output for verification-first capital governance
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class VerificationSurface:
    """
    Canonical input for every WEALTH opportunity assessment.

    Serializes: what was claimed, what evidence exists, who can verify it,
    at what cost, on what time horizon, and who bears the liability.
    """

    claim_id: str
    domain: str  # "trading" | "private_markets" | "ops" | "civilization" | "crisis"
    action_type: str  # "analysis" | "execution" | "allocation" | "underwriting"
    output_claims: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    provenance_score: float = 0.0  # 0-1
    verification_cost_hours: float = 0.0
    verification_latency_days: float = 0.0
    reversibility_score: float = 1.0  # 0-1, 1 = fully reversible
    liability_owner: str | None = None
    # Δm inputs
    executable_scope: float = 1.0  # proportion of task space AI can execute
    verifiable_scope: float = 1.0  # proportion human can verify
    # Junior loop
    junior_task_share_removed: float = 0.0  # 0-1
    synthetic_training_available: bool = False
    # Codifier's curse
    verification_events: int = 0
    captured_reasoning_depth: float = 0.0  # 0-1, how much is re-usable training data

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "domain": self.domain,
            "action_type": self.action_type,
            "output_claims": self.output_claims,
            "evidence_refs": self.evidence_refs,
            "provenance_score": self.provenance_score,
            "verification_cost_hours": self.verification_cost_hours,
            "verification_latency_days": self.verification_latency_days,
            "reversibility_score": self.reversibility_score,
            "liability_owner": self.liability_owner,
            "executable_scope": self.executable_scope,
            "verifiable_scope": self.verifiable_scope,
            "junior_task_share_removed": self.junior_task_share_removed,
            "synthetic_training_available": self.synthetic_training_available,
            "verification_events": self.verification_events,
            "captured_reasoning_depth": self.captured_reasoning_depth,
        }


@dataclass
class AuditEntropyResult:
    """
    Quantifies the Measurability Gap (Δm) between executable scope and
    affordable human verification scope.

    Core metric from: Catalini, Hui & Wu (MIT/WashU/UCLA, February 2026)
    "Some Simple Economics of AGI"
    """

    executable_scope: float  # m_A — share AI can execute cheaply
    verifiable_scope: float  # m_H — share humans can afford to verify
    delta_m: float  # structural gap, NOT a transient tech bug
    svs: float  # safe verifiable share = verifiable_scope / executable_scope
    entropy_band: str  # "LOW" | "MEDIUM" | "HIGH" | "EXTREME"
    bottlenecks: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    # Sub-components
    novelty_weight: float = 0.0
    proxy_distance_weight: float = 0.0
    verifier_scarcity_weight: float = 0.0
    latency_weight: float = 0.0
    model_opacity_weight: float = 0.0
    provenance_penalty: float = 0.0
    reversibility_bonus: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "executable_scope": round(self.executable_scope, 4),
            "verifiable_scope": round(self.verifiable_scope, 4),
            "delta_m": round(self.delta_m, 4),
            "svs": round(self.svs, 4),
            "entropy_band": self.entropy_band,
            "bottlenecks": self.bottlenecks,
            "notes": self.notes,
            "novelty_weight": round(self.novelty_weight, 4),
            "proxy_distance_weight": round(self.proxy_distance_weight, 4),
            "verifier_scarcity_weight": round(self.verifier_scarcity_weight, 4),
            "latency_weight": round(self.latency_weight, 4),
            "model_opacity_weight": round(self.model_opacity_weight, 4),
            "provenance_penalty": round(self.provenance_penalty, 4),
            "reversibility_bonus": round(self.reversibility_bonus, 4),
        }


@dataclass
class JuniorLoopImpact:
    """
    Measures damage to the human apprenticeship pipeline.

    Prevents WEALTH from optimizing into a future with no human checkers left.
    Missing junior loop = strategic existential risk, not just operational risk.
    """

    domain: str
    junior_task_share_removed: float  # 0-1
    synthetic_training_available: bool
    human_skill_reproduction_risk: float  # 0-1
    projected_senior_capacity_5y: float  # estimated senior verifiers in 5 years, relative to now
    status: str  # "SAFE" | "DEGRADING" | "CRITICAL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "junior_task_share_removed": round(self.junior_task_share_removed, 4),
            "synthetic_training_available": self.synthetic_training_available,
            "human_skill_reproduction_risk": round(self.human_skill_reproduction_risk, 4),
            "projected_senior_capacity_5y": round(self.projected_senior_capacity_5y, 4),
            "status": self.status,
        }


@dataclass
class CodifierCurse:
    """
    Tracks when human verification labor simultaneously creates training data
    that erodes future verifier scarcity rents.

    Not a blocker — a hidden cost/pricing signal.
    """

    verification_events: int
    captured_reasoning_depth: float  # 0-1
    downstream_model_training_probability: float  # 0-1
    expertise_rent_decay_risk: float  # 0-1
    mitigation: list[str] = field(
        default_factory=list
    )  # "partial_redaction" | "airgapped_review" | "premium_liability_pricing"

    def to_dict(self) -> dict[str, Any]:
        return {
            "verification_events": self.verification_events,
            "captured_reasoning_depth": round(self.captured_reasoning_depth, 4),
            "downstream_model_training_probability": round(
                self.downstream_model_training_probability, 4
            ),
            "expertise_rent_decay_risk": round(self.expertise_rent_decay_risk, 4),
            "mitigation": self.mitigation,
        }


@dataclass
class LiabilityRoute:
    """
    Post-AGI alpha requires not just "who knows" but "who will stand behind it."

    No liability owner = no SEAL. Hard gate.
    """

    decision_id: str
    liability_owner: str | None  # None = automatic HOLD
    owner_type: str | None  # "human" | "firm" | "committee"
    max_loss_band: float = 0.0
    insurance_required: bool = False
    legal_review_required: bool = False
    deployment_class: str = "LOW"  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "liability_owner": self.liability_owner,
            "owner_type": self.owner_type,
            "max_loss_band": self.max_loss_band,
            "insurance_required": self.insurance_required,
            "legal_review_required": self.legal_review_required,
            "deployment_class": self.deployment_class,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CORE FUNCTIONS — Audit Entropy / Δm Engine
# ═══════════════════════════════════════════════════════════════════════════════

# Weights for audit_entropy formula
_W_NOVELTY = 0.20
_W_PROXY = 0.20
_W_SCARCITY = 0.25
_W_LATENCY = 0.15
_W_OPACITY = 0.10
_W_PROVENANCE = -0.05
_W_REVERSIBILITY = -0.05


def wealth_measure_delta_m(
    cashflows: list[float] | None = None,
    novelty: float = 0.5,
    proxy_distance: float = 0.5,
    verifier_scarcity: float = 0.5,
    latency_to_ground_truth: float = 0.5,
    model_opacity: float = 0.5,
    provenance_score: float = 0.5,
    reversibility_score: float = 0.5,
    executable_scope: float = 1.0,
    verifiable_scope: float = 1.0,
) -> AuditEntropyResult:
    """
    Compute the Measurability Gap (Δm) = executable_scope - verifiable_scope.

    As Δm grows: un-underwritten decisions accumulate; output rises but risk
    ledger fills with unknowns. This is structural, not technical.

    Formula:
        svs = verifiable_scope / max(executable_scope, EPSILON)
        delta_m = max(0, executable_scope - verifiable_scope)
        audit_entropy =
            w1 * novelty
          + w2 * proxy_distance
          + w3 * verifier_scarcity
          + w4 * latency
          + w5 * model_opacity
          - w6 * provenance_score
          - w7 * reversibility_score
    """
    # Δm computation
    safe_exec = max(executable_scope, EPSILON)
    svs = verifiable_scope / safe_exec
    delta_m = max(0.0, executable_scope - verifiable_scope)

    # Entropy band classification
    if delta_m >= 0.75 or svs < 0.25:
        band = "EXTREME"
    elif delta_m >= 0.50 or svs < 0.50:
        band = "HIGH"
    elif delta_m >= 0.25 or svs < 0.75:
        band = "MEDIUM"
    else:
        band = "LOW"

    # Audit entropy sub-component
    (
        _W_NOVELTY * novelty
        + _W_PROXY * proxy_distance
        + _W_SCARCITY * verifier_scarcity
        + _W_LATENCY * latency_to_ground_truth
        + _W_OPACITY * model_opacity
        + _W_PROVENANCE * provenance_score  # note: negative weight (penalty)
        + _W_REVERSIBILITY * reversibility_score  # note: negative weight (bonus)
    )

    # Bottlenecks
    bottlenecks = []
    if novelty > 0.7:
        bottlenecks.append("high novelty — no established verification precedent")
    if proxy_distance > 0.6:
        bottlenecks.append("proxy metric too far from true outcome")
    if verifier_scarcity > 0.6:
        bottlenecks.append("verifier scarcity in domain — cost stubbornly high")
    if latency_to_ground_truth > 0.6:
        bottlenecks.append(
            f"ground truth delayed — {int(latency_to_ground_truth * 90)} days expected"
        )
    if model_opacity > 0.6:
        bottlenecks.append("model/tool opacity — black box, no audit trail")
    if provenance_score < 0.4:
        bottlenecks.append("low provenance score — evidence chain weak")

    # Notes
    notes = []
    if band in ("HIGH", "EXTREME"):
        notes.append(f"Δm={delta_m:.2f} exceeds safe threshold — human oversight required")
    if svs < 0.4:
        notes.append(f"svs={svs:.2f} — less than 40% of execution is safely verifiable")
    if delta_m > executable_scope * 0.8:
        notes.append("delta_m approaching executable_scope ceiling — structural limit reached")

    return AuditEntropyResult(
        executable_scope=executable_scope,
        verifiable_scope=verifiable_scope,
        delta_m=delta_m,
        svs=svs,
        entropy_band=band,
        bottlenecks=bottlenecks,
        notes=notes,
        novelty_weight=novelty * _W_NOVELTY,
        proxy_distance_weight=proxy_distance * _W_PROXY,
        verifier_scarcity_weight=verifier_scarcity * _W_SCARCITY,
        latency_weight=latency_to_ground_truth * _W_LATENCY,
        model_opacity_weight=model_opacity * _W_OPACITY,
        provenance_penalty=provenance_score * abs(_W_PROVENANCE),
        reversibility_bonus=reversibility_score * abs(_W_REVERSIBILITY),
    )


def wealth_assess_junior_loop(
    domain: str,
    junior_task_share_removed: float,
    synthetic_training_available: bool,
    current_senior_capacity: float = 1.0,
    annual_depletion_rate: float = 0.0,
) -> JuniorLoopImpact:
    """
    Assess damage to human apprenticeship pipeline.

    When junior work is automated away, there's no entry-level pathway to develop
    senior-level expertise. 5-year projection models skill reproduction collapse.
    """
    risk = min(1.0, junior_task_share_removed * 1.5)
    projected = max(0.0, current_senior_capacity * (1 - annual_depletion_rate * 5))
    if projected < 0.3 or risk > 0.8:
        status = "CRITICAL"
    elif projected < 0.6 or risk > 0.5:
        status = "DEGRADING"
    else:
        status = "SAFE"

    # Synthetic training available as partial mitigation
    if synthetic_training_available and status != "SAFE":
        risk *= 0.7  # partial offset
        projected *= 1.2  # slight uplift

    return JuniorLoopImpact(
        domain=domain,
        junior_task_share_removed=junior_task_share_removed,
        synthetic_training_available=synthetic_training_available,
        human_skill_reproduction_risk=round(risk, 4),
        projected_senior_capacity_5y=round(min(projected, 1.0), 4),
        status=status,
    )


def wealth_track_codifier_curse(
    verification_events: int,
    captured_reasoning_depth: float,
    downstream_model_training_probability: float = 0.5,
) -> CodifierCurse:
    """
    Track when verification labor generates reusable training data.

    The expert who does their job well works themselves out of a job.
    Mitigation options: partial_redaction, airgapped_review, premium_liability_pricing.
    """
    decay_risk = min(1.0, captured_reasoning_depth * downstream_model_training_probability)
    mitigation: list[str] = []
    if captured_reasoning_depth > 0.5:
        mitigation.append("partial_redaction")
    if downstream_model_training_probability > 0.6:
        mitigation.append("airgapped_review")
    if decay_risk > 0.4:
        mitigation.append("premium_liability_pricing")

    return CodifierCurse(
        verification_events=verification_events,
        captured_reasoning_depth=captured_reasoning_depth,
        downstream_model_training_probability=downstream_model_training_probability,
        expertise_rent_decay_risk=round(decay_risk, 4),
        mitigation=mitigation,
    )


def wealth_route_liability(
    decision_id: str,
    liability_owner: str | None,
    owner_type: str | None = None,
    max_loss_band: float = 0.0,
    insurance_required: bool = False,
    legal_review_required: bool = False,
    deployment_class: str = "LOW",
) -> LiabilityRoute:
    """
    Route liability for every agentic decision.

    HARD RULE: No liability owner = no SEAL. This is the post-AGI alpha condition:
    not "who knows" but "who will stand behind it."
    """
    return LiabilityRoute(
        decision_id=decision_id,
        liability_owner=liability_owner,
        owner_type=owner_type,
        max_loss_band=max_loss_band,
        insurance_required=insurance_required,
        legal_review_required=legal_review_required,
        deployment_class=deployment_class,
    )


def wealth_audit_entropy_from_cashflow(cashflows: list[float]) -> AuditEntropyResult:
    """
    Compute audit entropy from cashflow sign changes.

    Cashflow entropy is a proxy for uncertainty and multiple-IRR risk.
    High entropy = high audit burden.
    """
    if not cashflows:
        return wealth_measure_delta_m()

    signs = [1 if cf >= 0 else -1 for cf in cashflows if abs(cf) > EPSILON]
    if not signs:
        return wealth_measure_delta_m()

    pos = sum(1 for s in signs if s > 0)
    neg = sum(1 for s in signs if s < 0)
    n = len(signs)
    p_pos = pos / n if n > 0 else 0.5
    p_neg = neg / n if n > 0 else 0.5

    entropy = 0.0
    if p_pos > 0:
        entropy -= p_pos * math.log2(p_pos)
    if p_neg > 0:
        entropy -= p_neg * math.log2(p_neg)
    norm_entropy = entropy / math.log2(2) if math.log2(2) > 0 else 0.0

    # Map entropy (0-1) to novelty/proxy/etc
    novelty = norm_entropy
    proxy_distance = min(1.0, norm_entropy * 1.3)
    verifier_scarcity = 0.3 + norm_entropy * 0.4
    latency = 0.2 + norm_entropy * 0.5
    model_opacity = 0.4 + norm_entropy * 0.3

    return wealth_measure_delta_m(
        novelty=novelty,
        proxy_distance=proxy_distance,
        verifier_scarcity=verifier_scarcity,
        latency_to_ground_truth=latency,
        model_opacity=model_opacity,
    )
