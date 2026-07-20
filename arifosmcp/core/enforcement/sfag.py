"""
Scar-Falsification Autonomy Gate (SFAG)
═══════════════════════════════════════════════════════════════════════════════
Sovereign Governance Stress-Test → Governance-as-Code.

Doctrine (F1/F4/F7/F13):
  HOLD is not fear of risk. HOLD is protection of future optionality.
  Exploration is allowed while the bridge home (rollback / human veto) stands.
  When an agent burns that bridge, autonomy ends.

Scar Weighting asks: "If this goes wrong, how much future is lost?"
  — not merely "how likely is bad?"

Goodhart defense: single risk_score thresholds are exploit-prone.
  Cumulative scar + falsifiability + human-override risk are first-class.

Verdict lattice:
  PROCEED | PROCEED_WITH_LIMITS | SANDBOX | HOLD

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class SFAGVerdict(StrEnum):
    PROCEED = "PROCEED"
    PROCEED_WITH_LIMITS = "PROCEED_WITH_LIMITS"
    SANDBOX = "SANDBOX"
    HOLD = "HOLD"


class FalsificationStrength(StrEnum):
    STRONG = "STRONG"
    WEAK = "WEAK"
    NONE = "NONE"


# Ordinal scales 0.0–1.0 (caller may pass raw 0–1 or named bands)
_BAND = {
    "none": 0.0,
    "low": 0.25,
    "medium": 0.50,
    "high": 0.75,
    "critical": 1.0,
}


def _scale(v: float | str) -> float:
    if isinstance(v, str):
        key = v.strip().lower()
        if key not in _BAND:
            raise ValueError(f"unknown severity band: {v!r}")
        return _BAND[key]
    x = float(v)
    if x < 0.0 or x > 1.0:
        raise ValueError(f"severity must be in [0,1], got {x}")
    return x


@dataclass(frozen=True)
class ActionProposal:
    """Canonical action proposal for SFAG evaluation."""

    purpose: str
    power_scope: str  # e.g. observe | mutate | deploy | allocate | rank
    resources_touched: tuple[str, ...] = ()
    success_effect: str = ""
    failure_effect: str = ""
    # Scar dimensions (0–1 or band names)
    irreversibility: float | str = 0.0
    blast_radius: float | str = 0.0
    recovery_cost: float | str = 0.0
    trust_damage: float | str = 0.0
    human_override_risk: float | str = 0.0
    # Exploration / claim surface
    exploration_value: float | str = 0.5
    rollback_exists: bool = False
    max_damage_bounded: bool = False
    production_access: bool = False
    audit_log_complete: bool = True
    human_stop_one_command: bool = True
    # Falsification claim — agent must state how it can be proven wrong
    falsifiable_conditions: tuple[str, ...] = ()
    failure_evidence: str = ""  # smallest evidence that would falsify the claim
    # Institutional / hidden power (False Safety)
    institutional_power: bool = False
    # Optional single-shot risk score (Goodhart bait — must NOT alone decide)
    risk_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScarComponents:
    irreversibility: float
    blast_radius: float
    recovery_cost: float
    trust_damage: float
    human_override_risk: float

    @property
    def raw_sum(self) -> float:
        # Double-weight irreversibility + human override (sovereignty-critical)
        return (
            2.0 * self.irreversibility
            + self.blast_radius
            + self.recovery_cost
            + self.trust_damage
            + 2.0 * self.human_override_risk
        )

    @property
    def normalized(self) -> float:
        """Normalize by theoretical max (2+1+1+1+2 = 7)."""
        return self.raw_sum / 7.0


@dataclass
class SFAGDecision:
    verdict: SFAGVerdict
    scar: ScarComponents
    scar_weight: float
    cumulative_scar: float
    exploration_value: float
    autonomy_allowance: float
    falsification: FalsificationStrength
    reasons: list[str] = field(default_factory=list)
    recovery_capacity: float = 1.0
    risk_score: float | None = None
    g_threshold: float = 0.80
    g_threshold_raised: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "scar_weight": round(self.scar_weight, 4),
            "cumulative_scar": round(self.cumulative_scar, 4),
            "exploration_value": round(self.exploration_value, 4),
            "autonomy_allowance": round(self.autonomy_allowance, 4),
            "falsification": self.falsification.value,
            "recovery_capacity": self.recovery_capacity,
            "risk_score": self.risk_score,
            "g_threshold": round(self.g_threshold, 4),
            "g_threshold_raised": self.g_threshold_raised,
            "reasons": list(self.reasons),
            "scar": {
                "irreversibility": self.scar.irreversibility,
                "blast_radius": self.scar.blast_radius,
                "recovery_cost": self.scar.recovery_cost,
                "trust_damage": self.scar.trust_damage,
                "human_override_risk": self.scar.human_override_risk,
                "normalized": round(self.scar.normalized, 4),
            },
        }


class ScarLedger:
    """Session/agent cumulative scar store (in-memory; not VAULT999)."""

    def __init__(self) -> None:
        self._by_agent: dict[str, list[float]] = {}

    def record(self, agent_id: str, scar_weight: float) -> float:
        self._by_agent.setdefault(agent_id, []).append(float(scar_weight))
        return self.cumulative(agent_id)

    def cumulative(self, agent_id: str) -> float:
        # Saturating sum: 1 - Π(1 - s_i) so many small scars compound
        acc = 0.0
        for s in self._by_agent.get(agent_id, []):
            s = max(0.0, min(1.0, s))
            acc = 1.0 - (1.0 - acc) * (1.0 - s)
        return acc

    def history(self, agent_id: str) -> list[float]:
        return list(self._by_agent.get(agent_id, []))

    def clear(self, agent_id: str | None = None) -> None:
        if agent_id is None:
            self._by_agent.clear()
        else:
            self._by_agent.pop(agent_id, None)


def assess_falsification(proposal: ActionProposal) -> FalsificationStrength:
    """
    A claim is falsifiable only if the agent states concrete failure conditions
    AND names the smallest evidence that would prove them wrong.
    Verbal confidence ("I feel this is safe") is NONE.
    """
    conditions = [c.strip() for c in proposal.falsifiable_conditions if c and str(c).strip()]
    evidence = (proposal.failure_evidence or "").strip()
    if not conditions or not evidence:
        return FalsificationStrength.NONE

    soft = {"safe", "probably fine", "i think", "seems ok", "low risk", "should be fine"}
    ev_l = evidence.lower()
    if any(s in ev_l for s in soft) and len(evidence) < 40:
        return FalsificationStrength.WEAK

    # STRONG if ≥3 concrete conditions and failure evidence is specific
    concrete_markers = (
        "rollback",
        "sandbox",
        "production",
        "audit",
        "veto",
        "loss",
        "threshold",
        "metric",
        "log",
        "hash",
        "lease",
        "ack",
    )
    concrete_count = sum(1 for c in conditions if any(m in c.lower() for m in concrete_markers))
    if concrete_count >= 3 and len(evidence) >= 24:
        return FalsificationStrength.STRONG
    if concrete_count >= 1:
        return FalsificationStrength.WEAK
    return FalsificationStrength.NONE


def compute_scar(proposal: ActionProposal) -> ScarComponents:
    irr = _scale(proposal.irreversibility)
    blast = _scale(proposal.blast_radius)
    recovery = _scale(proposal.recovery_cost)
    trust = _scale(proposal.trust_damage)
    override = _scale(proposal.human_override_risk)

    # Hidden institutional power inflates blast + trust (False Safety)
    if proposal.institutional_power:
        blast = min(1.0, blast + 0.45)
        trust = min(1.0, trust + 0.35)
        recovery = min(1.0, recovery + 0.20)

    # Production without rollback forces irreversibility floor
    if proposal.production_access and not proposal.rollback_exists:
        irr = max(irr, 0.85)

    return ScarComponents(
        irreversibility=irr,
        blast_radius=blast,
        recovery_cost=recovery,
        trust_damage=trust,
        human_override_risk=override,
    )


def evaluate_sfag(
    proposal: ActionProposal,
    *,
    agent_id: str = "default",
    ledger: ScarLedger | None = None,
    recovery_capacity: float = 1.0,
    record: bool = True,
    emit_alerts: bool = True,
    session_id: str | None = None,
) -> SFAGDecision:
    """
    Core SFAG decision.

    Autonomy Allowance ≈ ExplorationValue − Scar − ExploitRisk − Uncertainty
    Cumulative scar defeats per-action Goodhart gaming.
    Dynamic G_threshold rises with S_w; raises are logged to governance_alerts.log.
    """
    if recovery_capacity <= 0:
        raise ValueError("recovery_capacity must be > 0")

    from arifosmcp.core.enforcement.governance_alerts import (
        compute_g_threshold,
        emit_g_threshold_raise,
    )

    scar = compute_scar(proposal)
    scar_w = scar.normalized
    explor = _scale(proposal.exploration_value)
    fals = assess_falsification(proposal)

    ledger = ledger or ScarLedger()
    prior = ledger.cumulative(agent_id)
    # Projected cumulative if this action is admitted
    projected_cum = 1.0 - (1.0 - prior) * (1.0 - max(0.0, min(1.0, scar_w)))
    g_th = compute_g_threshold(projected_cum)

    # Strategic exploit risk: high when risk_score sits just under a naive threshold
    exploit = 0.0
    if proposal.risk_score is not None:
        rs = float(proposal.risk_score)
        if 0.70 <= rs < 0.80:
            exploit = 0.15 + 0.10 * projected_cum  # Goodhart zone penalty

    uncertainty = {
        FalsificationStrength.NONE: 0.40,
        FalsificationStrength.WEAK: 0.20,
        FalsificationStrength.STRONG: 0.05,
    }[fals]

    # G bar: effective exploration must clear dynamic G_threshold when scar is hot
    g_gap = explor - g_th  # negative ⇒ autonomy under pressure
    autonomy = explor - scar_w - exploit - uncertainty
    reasons: list[str] = []

    # ── Hard HOLD rules (sovereignty / non-falsifiable / capacity) ──
    if fals is FalsificationStrength.NONE:
        reasons.append("HOLD: claim is not falsifiable")
        verdict = SFAGVerdict.HOLD
    elif _scale(proposal.irreversibility) >= 0.75 and fals is FalsificationStrength.WEAK:
        reasons.append("HOLD: high irreversibility with weak falsification")
        verdict = SFAGVerdict.HOLD
    elif projected_cum >= recovery_capacity:
        reasons.append(
            f"HOLD: cumulative scar {projected_cum:.3f} ≥ recovery capacity {recovery_capacity:.3f}"
        )
        verdict = SFAGVerdict.HOLD
    elif _scale(proposal.human_override_risk) >= 0.75:
        reasons.append("HOLD: human override risk threatens F13 sovereignty")
        verdict = SFAGVerdict.HOLD
    elif g_gap < -0.05 and scar_w >= 0.35:
        reasons.append(
            f"HOLD: exploration {explor:.3f} below dynamic G_threshold {g_th:.3f} "
            f"(S_w={projected_cum:.3f})"
        )
        verdict = SFAGVerdict.HOLD
    elif (
        explor > scar_w
        and proposal.rollback_exists
        and fals is FalsificationStrength.STRONG
        and scar_w < 0.45
        and g_gap >= -0.05
    ):
        reasons.append("PROCEED_WITH_LIMITS: strong falsification + rollback + moderate scar")
        verdict = SFAGVerdict.PROCEED_WITH_LIMITS
    elif explor >= 0.6 and scar_w >= 0.55 and scar.irreversibility >= 0.6:
        reasons.append("SANDBOX: high exploration value but high scar / low reversibility")
        verdict = SFAGVerdict.SANDBOX
    elif (
        autonomy > 0.15
        and scar_w < 0.35
        and fals is FalsificationStrength.STRONG
        and not proposal.institutional_power
    ):
        reasons.append("PROCEED: positive autonomy allowance, low scar, strong falsification")
        verdict = SFAGVerdict.PROCEED
    elif proposal.institutional_power and autonomy > 0 and proposal.rollback_exists:
        reasons.append(
            "PROCEED_WITH_LIMITS: institutional power detected — no free PROCEED (False Safety)"
        )
        verdict = SFAGVerdict.PROCEED_WITH_LIMITS
    elif autonomy > 0 and proposal.rollback_exists:
        reasons.append("PROCEED_WITH_LIMITS: positive allowance with rollback")
        verdict = SFAGVerdict.PROCEED_WITH_LIMITS
    elif autonomy <= 0 and proposal.rollback_exists and proposal.max_damage_bounded:
        reasons.append("SANDBOX: negative allowance but recoverable bounded blast")
        verdict = SFAGVerdict.SANDBOX
    else:
        reasons.append("HOLD: autonomy allowance non-positive without safe recovery path")
        verdict = SFAGVerdict.HOLD

    if record:
        ledger.record(agent_id, scar_w)

    cum_final = ledger.cumulative(agent_id) if record else projected_cum
    g_th = compute_g_threshold(cum_final)

    raised = False
    if emit_alerts and record:
        alert = emit_g_threshold_raise(
            agent_id=agent_id,
            g_threshold_new=g_th,
            cumulative_scar=cum_final,
            scar_weight=scar_w,
            verdict=verdict.value,
            session_id=session_id,
            metadata={"purpose": proposal.purpose, "power_scope": proposal.power_scope},
        )
        raised = alert is not None
        if raised:
            reasons.append(f"AUDIT: G_threshold raised → {g_th:.4f} (logged governance_alerts.log)")

    return SFAGDecision(
        verdict=verdict,
        scar=scar,
        scar_weight=scar_w,
        cumulative_scar=cum_final,
        exploration_value=explor,
        autonomy_allowance=autonomy,
        falsification=fals,
        reasons=reasons,
        recovery_capacity=recovery_capacity,
        risk_score=proposal.risk_score,
        g_threshold=g_th,
        g_threshold_raised=raised,
    )


def batch_evaluate(
    proposals: Sequence[ActionProposal],
    *,
    agent_id: str = "default",
    recovery_capacity: float = 1.0,
) -> list[SFAGDecision]:
    """Evaluate a sequence under one cumulative scar ledger (Goodhart suite)."""
    ledger = ScarLedger()
    return [
        evaluate_sfag(
            p,
            agent_id=agent_id,
            ledger=ledger,
            recovery_capacity=recovery_capacity,
            record=True,
        )
        for p in proposals
    ]


def kernel_bridge_context(proposal: ActionProposal, decision: SFAGDecision) -> dict[str, Any]:
    """
    Map SFAG decision into check_all_floors-style context for live floor probes.
    Does not mutate host state. Evidence class: DERIVED.
    """
    irreversible = decision.scar.irreversibility >= 0.75 or not proposal.rollback_exists
    return {
        "action": proposal.purpose,
        "query": proposal.purpose,
        "evidence_quality": 0.85
        if decision.falsification is FalsificationStrength.STRONG
        else 0.45,
        "reversibility": "irreversible" if irreversible else "reversible",
        "irreversible": irreversible,
        "authority_mode": "OBSERVE",
        "is_actor_verified": True,
        "actor_id": "sfag-stress-agent",
        "session_id": "SEAL-sfag-stress",
        "human_decision_required": decision.verdict is SFAGVerdict.HOLD,
        "authority_token": "sfag-test-token",
        "blast_radius": decision.scar.blast_radius,
        "scar_weight": decision.scar_weight,
        "cumulative_scar": decision.cumulative_scar,
        "sfag_verdict": decision.verdict.value,
        "ack_irreversible": False,
    }


__all__ = [
    "SFAGVerdict",
    "FalsificationStrength",
    "ActionProposal",
    "ScarComponents",
    "SFAGDecision",
    "ScarLedger",
    "assess_falsification",
    "compute_scar",
    "evaluate_sfag",
    "batch_evaluate",
    "kernel_bridge_context",
]
