"""
arifosmcp/runtime/qqqq_metrics.py — QQQQ + Agentic Intelligence metrics

QQQ  = recommendation discipline (Q1 Qualitative, Q2 Quantitative, Q3 Quantum)
QQQQ = QQQ + Q4 Zen Export (metabolic jurisprudence under F4)

Does NOT add F14. Floors remain F1–F13.
Q4 expresses: forced entropy export while tank is abundant — zen as life, not cleanup.

Also computes the Agentic Intelligence product and kernel×agent×qqqq coupling.

Doctrine:
  /root/AAA/governance/QQQ_RECOMMENDATION_PROTOCOL.md
  /root/arifOS/GENESIS/022_EUREKA_ZEN_MARGIN.md

Floor bind: F2, F4, F7, F8, F11, F13
DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

from arifosmcp.geometry.eureka_zen import (
    CONFIDENCE_CAP,
    EPS,
    T_ABUNDANCE,
    EntropyFlux,
    EurekaZenMetrics,
    ExportReceipt,
    TankState,
    ZenGateLabel,
    compute_eureka_zen,
)
from arifosmcp.runtime.qqq_validator import QQQCheck, QQQVerdict, validate_qqq

logger = logging.getLogger("arifosmcp.qqqq_metrics")


# ─────────────────────────────────────────────────────────────────────────────
# Q4 / QQQQ verdicts
# ─────────────────────────────────────────────────────────────────────────────


class QQQQVerdict(StrEnum):
    COMPLETE = "QQQQ_COMPLETE"
    INADMISSIBLE_Q1 = "INADMISSIBLE-Q1"
    INADMISSIBLE_Q2 = "INADMISSIBLE-Q2"
    INADMISSIBLE_Q3 = "INADMISSIBLE-Q3"
    INADMISSIBLE_Q4 = "INADMISSIBLE-Q4"
    Q4_NOT_REQUIRED = "Q4_NOT_REQUIRED"
    NOT_REQUIRED = "NOT_REQUIRED"
    ENVELOPE_MISSING = "ENVELOPE_MISSING"


# Map QQQ → QQQQ base
_QQQ_TO_QQQQ = {
    QQQVerdict.COMPLETE: QQQQVerdict.COMPLETE,  # may still fail Q4
    QQQVerdict.INADMISSIBLE_Q1: QQQQVerdict.INADMISSIBLE_Q1,
    QQQVerdict.INADMISSIBLE_Q2: QQQQVerdict.INADMISSIBLE_Q2,
    QQQVerdict.INADMISSIBLE_Q3: QQQQVerdict.INADMISSIBLE_Q3,
    QQQVerdict.NOT_REQUIRED: QQQQVerdict.NOT_REQUIRED,
    QQQVerdict.ENVELOPE_MISSING: QQQQVerdict.ENVELOPE_MISSING,
}


@dataclass
class Q4Check:
    """Q4 Zen Export layer result."""

    required: bool
    passed: bool
    reasons: list[str] = field(default_factory=list)
    export_actions: list[str] = field(default_factory=list)
    delta_s_claim: float | None = None
    tank_at_export: float | None = None
    gate_label: str = ZenGateLabel.PASS.value


@dataclass
class QQQQCheck:
    """Full four-layer recommendation + metabolism check."""

    verdict: QQQQVerdict
    qqq: QQQCheck | None = None
    q4: Q4Check | None = None
    eureka_zen: EurekaZenMetrics | None = None
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "reasons": list(self.reasons),
            "qqq_verdict": self.qqq.verdict.value if self.qqq else None,
            "q4": asdict(self.q4) if self.q4 else None,
            "eureka_zen": self.eureka_zen.to_dict() if self.eureka_zen else None,
            "metadata": dict(self.metadata),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Agentic Intelligence product
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class AgenticFactors:
    """Six factors of governed agentic intelligence.

    AI = C × Gnd × Auth × Cont × Acc × Met
    Any zero factor collapses intelligence to zero in that dimension.
    """

    capability: float = 0.0  # C
    grounding: float = 0.0  # Gnd
    authority: float = 0.0  # Auth
    continuity: float = 0.0  # Cont
    accountability: float = 0.0  # Acc
    metabolism: float = 0.0  # Met — from M = X/(J+ε), capped [0,1]

    def __post_init__(self) -> None:
        for name in (
            "capability",
            "grounding",
            "authority",
            "continuity",
            "accountability",
            "metabolism",
        ):
            setattr(self, name, _clamp01(getattr(self, name)))


@dataclass(frozen=True)
class AgenticIntelligenceMetrics:
    """Full agent intelligence equation output."""

    probe_id: str
    ts: float
    factors: AgenticFactors
    agentic_intelligence: float  # product
    zero_factors: tuple[str, ...]
    genius: float | None  # F8 optional
    vitality_psi: float | None  # Ψ optional
    admissible: bool
    reasons: tuple[str, ...]
    confidence: float
    equations: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "probe_id": self.probe_id,
            "ts": self.ts,
            "factors": asdict(self.factors),
            "agentic_intelligence": self.agentic_intelligence,
            "zero_factors": list(self.zero_factors),
            "genius": self.genius,
            "vitality_psi": self.vitality_psi,
            "admissible": self.admissible,
            "reasons": list(self.reasons),
            "confidence": self.confidence,
            "equations": dict(self.equations),
        }


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def compute_agentic_intelligence(
    factors: AgenticFactors,
    *,
    genius_components: dict[str, float] | None = None,
    vitality_components: dict[str, float] | None = None,
    delta_s_session: float | None = None,
    qqqq_complete: bool = True,
    kernel_floors_pass: bool = True,
) -> AgenticIntelligenceMetrics:
    """AI = C · Gnd · Auth · Cont · Acc · Met

    Optional:
      G = (A × P × X × E²) × (1−h)     F8 Genius
      Ψ = (|ΔS|·Peace²·κᵣ·RASA·Amanah)/(Entropy+Shadow+ε)
    """
    f = factors
    product = (
        f.capability * f.grounding * f.authority * f.continuity * f.accountability * f.metabolism
    )

    zero: list[str] = []
    labels = {
        "capability": "passive assistant (C=0)",
        "grounding": "hallucinating agent (Gnd=0)",
        "authority": "rogue action (Auth=0)",
        "continuity": "amnesiac tool (Cont=0)",
        "accountability": "untraceable machine (Acc=0)",
        "metabolism": "repeating system / eureka debt (Met=0)",
    }
    for key, msg in labels.items():
        if getattr(f, key) <= 0.0:
            zero.append(msg)

    genius: float | None = None
    if genius_components:
        # G = (A × P × X × E²) × (1−h)
        a = float(genius_components.get("A", 0.0))
        p = float(genius_components.get("P", 0.0))
        x = float(genius_components.get("X", 0.0))
        e = float(genius_components.get("E", 0.0))
        h = _clamp01(float(genius_components.get("h", 0.04)))
        genius = (a * p * x * (e**2)) * (1.0 - h)
        genius = max(0.0, genius)

    psi: float | None = None
    if vitality_components:
        ds = abs(float(vitality_components.get("delta_s", 0.0)))
        peace2 = float(vitality_components.get("peace2", 0.0))
        kappa_r = float(vitality_components.get("kappa_r", 0.0))
        rasa = float(vitality_components.get("rasa", 0.0))
        amanah = float(vitality_components.get("amanah", 0.0))
        entropy = float(vitality_components.get("entropy", 0.0))
        shadow = float(vitality_components.get("shadow", 0.0))
        psi = (ds * peace2 * kappa_r * rasa * amanah) / (entropy + shadow + EPS)
        psi = max(0.0, min(10.0, psi))

    reasons: list[str] = []
    if zero:
        reasons.extend(zero)
    if delta_s_session is not None and delta_s_session > 0:
        reasons.append(f"F4 fail: ΔS_session={delta_s_session:.4f} > 0")
    if not qqqq_complete:
        reasons.append("QQQQ incomplete")
    if not kernel_floors_pass:
        reasons.append("kernel floors not pass")
    if genius is not None and genius < 0.80:
        reasons.append(f"F8 Genius G={genius:.3f} < 0.80")
    if psi is not None and psi < 1.0:
        reasons.append(f"Ψ vitality={psi:.3f} < 1.0 (not homeostatic)")

    admissible = (
        product > 0
        and kernel_floors_pass
        and qqqq_complete
        and (delta_s_session is None or delta_s_session <= 0)
        and (genius is None or genius >= 0.80)
    )

    equations = {
        "agentic_intelligence": "AI = C × Gnd × Auth × Cont × Acc × Met",
        "metabolism": "Met = clamp(X / (J + ε), 0, 1)",
        "session_entropy": "ΔS_session = J − X   (F4: ≤ 0)",
        "genius_f8": "G = (A × P × X × E²) × (1 − h) ≥ 0.80",
        "vitality_psi": "Ψ = (|ΔS|·Peace²·κᵣ·RASA·Amanah)/(Entropy+Shadow+ε)",
        "qqqq": "admissible ⊃ Q1 ∧ Q2 ∧ Q3 ∧ (Q4 when tank≥T_ABUNDANCE)",
        "iron_line": "Zen is not the last 2%. Zen is the first 10% of every full tank.",
    }

    return AgenticIntelligenceMetrics(
        probe_id=str(uuid.uuid4()),
        ts=time.time(),
        factors=f,
        agentic_intelligence=product,
        zero_factors=tuple(zero),
        genius=genius,
        vitality_psi=psi,
        admissible=admissible,
        reasons=tuple(reasons),
        confidence=CONFIDENCE_CAP,
        equations=equations,
    )


def metabolism_from_flux(inject: float, export: float) -> float:
    """Met factor for AgenticFactors from raw J,X — capped at 1."""
    j = max(0.0, float(inject))
    x = max(0.0, float(export))
    m = x / (j + EPS)
    # If no inject and no export, metabolism is neutral (1.0) not zero —
    # zero would falsely collapse AI when session is idle.
    if j <= 0 and x <= 0:
        return 1.0
    return _clamp01(m)


# ─────────────────────────────────────────────────────────────────────────────
# Q4 validation
# ─────────────────────────────────────────────────────────────────────────────


def q4_required(
    tank: float,
    *,
    intent_class: str,
    proposing_eureka: bool,
    t_abundance: float = T_ABUNDANCE,
) -> bool:
    """Q4 required when abundant and recommending/expanding, or always on VERDICT at abundance."""
    if tank < t_abundance:
        return False
    if intent_class in {"RECOMMENDATION", "DECISION", "VERDICT"} and proposing_eureka:
        return True
    return proposing_eureka and tank >= t_abundance


def validate_q4(
    export_block: dict[str, Any] | None,
    *,
    tank: float,
    intent_class: str = "RECOMMENDATION",
    proposing_eureka: bool = True,
    t_abundance: float = T_ABUNDANCE,
) -> Q4Check:
    """Validate Q4 Zen Export block."""
    required = q4_required(
        tank,
        intent_class=intent_class,
        proposing_eureka=proposing_eureka,
        t_abundance=t_abundance,
    )
    if not required:
        return Q4Check(required=False, passed=True, reasons=["Q4 not required at this tank/intent"])

    if not export_block:
        return Q4Check(
            required=True,
            passed=False,
            reasons=["Q4: export block missing under abundance (zen before eureka)"],
            gate_label=ZenGateLabel.ZEN_BEFORE_EUREKA.value,
        )

    actions = list(export_block.get("export_actions") or [])
    delta_s_claim = float(export_block.get("delta_s_claim", 1.0))
    tank_at = export_block.get("tank_at_export")
    completed = bool(export_block.get("completed", bool(actions)))

    reasons: list[str] = []
    if not actions:
        reasons.append("Q4: export_actions empty")
    if delta_s_claim > 0:
        reasons.append(f"Q4: delta_s_claim={delta_s_claim} > 0 (export must reduce entropy)")
    if not completed:
        reasons.append("Q4: export not marked completed")

    passed = len(reasons) == 0
    return Q4Check(
        required=True,
        passed=passed,
        reasons=reasons,
        export_actions=actions,
        delta_s_claim=delta_s_claim,
        tank_at_export=float(tank_at) if tank_at is not None else tank,
        gate_label=ZenGateLabel.PASS.value if passed else ZenGateLabel.ZEN_BEFORE_EUREKA.value,
    )


def validate_qqqq(
    envelope: dict[str, Any] | None,
    *,
    intent_class: str = "RECOMMENDATION",
    tank: float | TankState = 1.0,
    flux: EntropyFlux | None = None,
    proposing_eureka: bool = True,
) -> QQQQCheck:
    """Validate Q1–Q4 and attach EUREKA·ZEN metrics.

    Envelope shape (extends QQQ):
      paths, quantum, recommended_path_id  # Q1–Q3
      q4_export: { export_actions, delta_s_claim, tank_at_export, deferred_to_margin, completed }
    """
    if isinstance(tank, TankState):
        t = tank.resolve()
    else:
        t = _clamp01(float(tank))

    qqq = validate_qqq(envelope, intent_class=intent_class)

    export_block = None
    if envelope:
        export_block = envelope.get("q4_export") or envelope.get("zen_export")

    receipt = ExportReceipt()
    if export_block:
        receipt = ExportReceipt(
            export_actions=list(export_block.get("export_actions") or []),
            delta_s_claim=float(export_block.get("delta_s_claim", 0.0)),
            tank_at_export=(
                float(export_block["tank_at_export"])
                if export_block.get("tank_at_export") is not None
                else t
            ),
            completed=bool(export_block.get("completed", bool(export_block.get("export_actions")))),
        )

    ez = compute_eureka_zen(
        t,
        flux,
        export_receipt=receipt,
        proposing_eureka=proposing_eureka,
    )

    q4 = validate_q4(
        export_block,
        tank=t,
        intent_class=intent_class,
        proposing_eureka=proposing_eureka,
    )

    # Base from QQQ
    if qqq.verdict == QQQVerdict.NOT_REQUIRED and not q4.required:
        return QQQQCheck(
            verdict=QQQQVerdict.NOT_REQUIRED,
            qqq=qqq,
            q4=q4,
            eureka_zen=ez,
            reasons=["QQQQ not required for this intent/tank"],
            metadata={"intent_class": intent_class, "tank": t},
        )

    if qqq.verdict != QQQVerdict.COMPLETE and qqq.verdict != QQQVerdict.NOT_REQUIRED:
        base = _QQQ_TO_QQQQ.get(qqq.verdict, QQQQVerdict.INADMISSIBLE_Q1)
        return QQQQCheck(
            verdict=base,
            qqq=qqq,
            q4=q4,
            eureka_zen=ez,
            reasons=list(qqq.reasons) + list(q4.reasons),
            metadata={"intent_class": intent_class, "tank": t},
        )

    # QQQ complete or not required — check Q4
    if q4.required and not q4.passed:
        verdict = QQQQVerdict.INADMISSIBLE_Q4
        return QQQQCheck(
            verdict=verdict,
            qqq=qqq,
            q4=q4,
            eureka_zen=ez,
            reasons=list(q4.reasons),
            metadata={"intent_class": intent_class, "tank": t, "iron_rule": ez.iron_line},
        )

    # Full complete
    if qqq.verdict == QQQVerdict.NOT_REQUIRED and q4.required and q4.passed:
        # Q4 alone required (pure eureka expansion without recommendation envelope)
        return QQQQCheck(
            verdict=QQQQVerdict.COMPLETE,
            qqq=qqq,
            q4=q4,
            eureka_zen=ez,
            reasons=["Q4 export complete; Q1–Q3 not required for intent"],
            metadata={"intent_class": intent_class, "tank": t},
        )

    return QQQQCheck(
        verdict=QQQQVerdict.COMPLETE,
        qqq=qqq,
        q4=q4,
        eureka_zen=ez,
        reasons=[],
        metadata={"intent_class": intent_class, "tank": t, "iron_rule": ez.iron_line},
    )


def gate_qqqq(
    envelope: dict[str, Any] | None,
    *,
    intent_class: str = "RECOMMENDATION",
    tank: float = 1.0,
    flux: EntropyFlux | None = None,
    proposing_eureka: bool = True,
) -> QQQQCheck:
    """Gate 5c: QQQQ discipline (QQQ + Q4 zen). Labels, never silent suppress."""
    check = validate_qqqq(
        envelope,
        intent_class=intent_class,
        tank=tank,
        flux=flux,
        proposing_eureka=proposing_eureka,
    )
    check.metadata["qqqq_compliance"] = check.verdict.value
    if check.verdict == QQQQVerdict.COMPLETE:
        logger.info("QQQQ COMPLETE tank=%.3f", tank)
    else:
        logger.warning("QQQQ %s: %s", check.verdict.value, "; ".join(check.reasons))
    return check


# ─────────────────────────────────────────────────────────────────────────────
# Unified kernel × agent × qqqq metrics envelope
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class KernelAgentQQQQMetrics:
    """Single envelope: how kernel, QQQQ, and agent intelligence couple."""

    probe_id: str
    ts: float
    eureka_zen: EurekaZenMetrics
    qqqq: QQQQCheck
    agentic: AgenticIntelligenceMetrics
    coupling: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "probe_id": self.probe_id,
            "ts": self.ts,
            "eureka_zen": self.eureka_zen.to_dict(),
            "qqqq": self.qqqq.to_dict(),
            "agentic": self.agentic.to_dict(),
            "coupling": dict(self.coupling),
        }

    def summary_lines(self) -> list[str]:
        return [
            self.eureka_zen.summary_line(),
            f"[QQQQ/{self.qqqq.verdict.value}] reasons={self.qqqq.reasons or 'none'}",
            (
                f"[AGENT/AI={self.agentic.agentic_intelligence:.4f}] "
                f"admissible={self.agentic.admissible} "
                f"zeros={list(self.agentic.zero_factors) or 'none'}"
            ),
            f"[COUPLING] {self.coupling.get('formula', '')}",
        ]


def compute_kernel_agent_qqqq(
    *,
    tank: float = 1.0,
    inject: float = 0.0,
    export: float = 0.0,
    envelope: dict[str, Any] | None = None,
    intent_class: str = "RECOMMENDATION",
    proposing_eureka: bool = True,
    capability: float = 1.0,
    grounding: float = 1.0,
    authority: float = 1.0,
    continuity: float = 1.0,
    accountability: float = 1.0,
    kernel_floors_pass: bool = True,
    genius_components: dict[str, float] | None = None,
    vitality_components: dict[str, float] | None = None,
) -> KernelAgentQQQQMetrics:
    """Full equation metrics: kernel EUREKA·ZEN × QQQQ × Agentic Intelligence."""
    flux = EntropyFlux(inject=inject, export=export)
    qqqq = validate_qqqq(
        envelope,
        intent_class=intent_class,
        tank=tank,
        flux=flux,
        proposing_eureka=proposing_eureka,
    )
    assert qqqq.eureka_zen is not None
    ez = qqqq.eureka_zen

    # Prefer flux-derived Met; if export_receipt inflated X, use ez.export
    met = metabolism_from_flux(ez.inject, ez.export)
    factors = AgenticFactors(
        capability=capability,
        grounding=grounding,
        authority=authority,
        continuity=continuity,
        accountability=accountability,
        metabolism=met,
    )
    agentic = compute_agentic_intelligence(
        factors,
        genius_components=genius_components,
        vitality_components=vitality_components,
        delta_s_session=ez.delta_s_session,
        qqqq_complete=qqqq.verdict == QQQQVerdict.COMPLETE
        or qqqq.verdict == QQQQVerdict.NOT_REQUIRED,
        kernel_floors_pass=kernel_floors_pass,
    )

    coupling = {
        "formula": ("admissible = kernel_floors_pass ∧ qqqq_COMPLETE ∧ AI>0 ∧ ΔS_session≤0"),
        "kernel_floors_pass": kernel_floors_pass,
        "qqqq_verdict": qqqq.verdict.value,
        "ai": agentic.agentic_intelligence,
        "delta_s_session": ez.delta_s_session,
        "phase": ez.phase.value,
        "gate_label": ez.gate_label.value,
        "should_force_zen": ez.gate_label
        in (ZenGateLabel.ZEN_BEFORE_EUREKA, ZenGateLabel.MARGIN_EXPORT_ONLY),
        "iron_line": ez.iron_line,
    }

    return KernelAgentQQQQMetrics(
        probe_id=str(uuid.uuid4()),
        ts=time.time(),
        eureka_zen=ez,
        qqqq=qqqq,
        agentic=agentic,
        coupling=coupling,
    )
