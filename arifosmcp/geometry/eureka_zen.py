"""
arifosmcp/geometry/eureka_zen.py — EUREKA·ZEN Margin Thermodynamics (GENESIS 022)

Sealed framework SOT:
  /root/A-FORGE/forge_work/2026-07-18/EUREKA-ZEN-METRICS-FRAMEWORK.md
  VAULT999 claim: seq 26 · 326b0439a41d8b59bed1d3a453c81d23d020b6eef78df65f42cb854946757b6c

Iron line:
  Zen is not the last 2%. Zen is the first 10% of every full tank.

Coded equations:
  T ∈ [0,1]                         tank remaining
  U_eureka(T)=T , U_zen(T)=1−T      margin theorem utilities (cross at 0.50)
  dT/dt = J_rate − X_rate − k·T     tank dynamics
  G = A·P·E·X·Φ                     APEX Nash product
  C_dark = A·(1−P)·(1−X)            gaming potential
  W³ = (H·AI·EXT)^(1/3)             tri-witness
  ΔS = J − X ≤ 0                    F4
  M = X/(J+ε)                       metabolic balance

Floor bind: F2, F4, F7, F8, F11, F13 · F9/F10: thermodynamics of work, not soul.
Reversibility (F1): file delete = clean revert. No migrations.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# F13-ratified thresholds (defaults). Tunable only by sovereign ratify.
# ─────────────────────────────────────────────────────────────────────────────

T_MARGIN: float = 0.03  # first honest audit zone
T_CRITICAL: float = 0.02  # expansion illegal; only compression pays
T_ABUNDANCE: float = 0.50  # indifference + forced export before eureka
ZEN_FIRST: float = 0.10  # first 10% of full tank is zen export
EPS: float = 1e-6
CONFIDENCE_CAP: float = 0.95  # F7 — never claim 1.0
MET_HEALTHY: float = 1.0  # M ≥ 1 → export ≥ inject
C_DARK_HOLD: float = 0.15  # C_dark > 0.15 → significant gaming potential
W3_CONSENSUS: float = 0.70
W3_WEAK: float = 0.40
DISSIPATION_K: float = 0.01  # natural tank leak coefficient
# Sealed framework receipt (operator-attested)
SEALED_FRAMEWORK_PATH: str = "/root/A-FORGE/forge_work/2026-07-18/EUREKA-ZEN-METRICS-FRAMEWORK.md"
SEALED_VAULT_HASH: str = "326b0439a41d8b59bed1d3a453c81d23d020b6eef78df65f42cb854946757b6c"


class MetabolicPhase(StrEnum):
    """Where the system sits on the eureka↔zen cycle."""

    MARGIN_ZEN = "MARGIN_ZEN"  # T ≤ T_CRITICAL — only compression pays
    MARGIN_REFLEX = "MARGIN_REFLEX"  # T ≤ T_MARGIN — universe installs zen free
    ABUNDANCE_MUST_ZEN = "ABUNDANCE_MUST_ZEN"  # T ≥ 0.5, export not done
    ABUNDANCE_EUREKA_OK = "ABUNDANCE_EUREKA_OK"  # T ≥ 0.5, export completed
    NORMAL_DUAL = "NORMAL_DUAL"  # mid-tank dual phase


class ZenGateLabel(StrEnum):
    """Gate labels — never silent suppress. Sovereign decides."""

    PASS = "PASS"
    ZEN_BEFORE_EUREKA = "ZEN_BEFORE_EUREKA"  # iron rule hold-label
    MARGIN_EXPORT_ONLY = "MARGIN_EXPORT_ONLY"  # no expansion at critical
    METABOLIC_DEBT = "METABOLIC_DEBT"  # M < 1 sustained under abundance


# ─────────────────────────────────────────────────────────────────────────────
# Inputs / outputs
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class TankState:
    """Budget remaining as a unit interval.

    remaining_budget / max_budget → T.
    Accept either precomputed tank_level or raw budget pair.
    """

    tank_level: float | None = None
    remaining_budget: float | None = None
    max_budget: float | None = None

    def resolve(self) -> float:
        if self.tank_level is not None:
            return _clamp01(float(self.tank_level))
        if (
            self.remaining_budget is not None
            and self.max_budget is not None
            and float(self.max_budget) > 0
        ):
            return _clamp01(float(self.remaining_budget) / float(self.max_budget))
        raise ValueError("TankState requires tank_level or (remaining_budget, max_budget>0)")


@dataclass
class EntropyFlux:
    """Session-scale entropy inject (eureka) and export (zen).

    Units are abstract non-negative work units (files added vs deleted,
    surfaces opened vs closed, claims opened vs sealed). Callers normalize.
    """

    inject: float = 0.0  # J
    export: float = 0.0  # X

    def __post_init__(self) -> None:
        self.inject = max(0.0, float(self.inject))
        self.export = max(0.0, float(self.export))


@dataclass
class ExportReceipt:
    """Evidence that a zen export ran this epoch (Q4)."""

    export_actions: list[str] = field(default_factory=list)
    delta_s_claim: float = 0.0  # expected ΔS from export (should be ≤ 0)
    tank_at_export: float | None = None
    completed: bool = False

    def is_valid_export(self) -> bool:
        if not self.completed:
            return False
        if not self.export_actions:
            return False
        # F4: export must claim non-increasing entropy
        return self.delta_s_claim <= 0.0


@dataclass(frozen=True)
class EurekaZenMetrics:
    """Full equation metrics for one metabolic probe."""

    probe_id: str
    ts: float
    tank: float
    inject: float  # J
    export: float  # X
    delta_s_session: float  # J − X
    metabolic_balance: float  # M = X/(J+ε)
    phase: MetabolicPhase
    gate_label: ZenGateLabel
    export_completed: bool
    zen_first_fraction: float  # ZEN_FIRST constant echoed
    abundance_threshold: float
    margin_threshold: float
    critical_threshold: float
    f4_pass: bool  # ΔS_session ≤ 0
    iron_line: str
    reason: str
    confidence: float  # F7-capped
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["phase"] = self.phase.value
        d["gate_label"] = self.gate_label.value
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str)

    def summary_line(self) -> str:
        return (
            f"[EUREKA·ZEN/{self.phase.value}] T={self.tank:.3f} "
            f"J={self.inject:.3f} X={self.export:.3f} ΔS={self.delta_s_session:.3f} "
            f"M={self.metabolic_balance:.3f} gate={self.gate_label.value} "
            f"f4={'PASS' if self.f4_pass else 'FAIL'} — {self.reason}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Pure math
# ─────────────────────────────────────────────────────────────────────────────


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def metabolic_balance(inject: float, export: float, *, eps: float = EPS) -> float:
    """M = X / (J + ε). Export / inject ratio."""
    j = max(0.0, float(inject))
    x = max(0.0, float(export))
    return x / (j + eps)


def session_delta_s(inject: float, export: float) -> float:
    """ΔS_session = J − X. F4 wants ≤ 0."""
    return max(0.0, float(inject)) - max(0.0, float(export))


# ── Margin theorem utilities (sealed framework §3, §11) ──────────────────────


def u_eureka(tank: float) -> float:
    """U_eureka(T) = T — expansion utility rises with surplus.

    At T=0.80 >> U_zen; at T=0.50 ≈ U_zen; at T=0.03 << U_zen.
    """
    return _clamp01(tank)


def u_zen(tank: float) -> float:
    """U_zen(T) = 1 − T — compression utility rises as tank empties."""
    return _clamp01(1.0 - _clamp01(tank))


def preferred_mode(tank: float, *, t_indifference: float = T_ABUNDANCE) -> str:
    """Route preference from margin theorem.

    Returns: 'EUREKA' | 'ZEN' | 'INDIFFERENT'
    """
    t = _clamp01(tank)
    ue, uz = u_eureka(t), u_zen(t)
    if abs(ue - uz) < 1e-9 or abs(t - t_indifference) < 1e-9:
        return "INDIFFERENT"
    return "EUREKA" if ue > uz else "ZEN"


def tank_step(
    tank: float,
    *,
    injection_rate: float = 0.0,
    export_rate: float = 0.0,
    dt: float = 1.0,
    dissipation_k: float = DISSIPATION_K,
) -> float:
    """dT/dt = INJECTION_RATE − EXPORT_RATE − k·T  (framework §3).

    Note: injection_rate here is budget *drain* from eureka work (tokens spent),
    export_rate is budget *recovery* from compression efficiency — both ≥ 0.
    Net: tank falls when work burns budget faster than export recovers it.
    """
    t = _clamp01(tank)
    dtdt = float(export_rate) - float(injection_rate) - dissipation_k * t
    return _clamp01(t + float(dt) * dtdt)


# ── APEX G / C_dark / W³ (framework §1, §6) ──────────────────────────────────


def apex_g(a: float, p: float, e: float, x: float, phi: float) -> float:
    """G = A · P · E · X · Φ  (APEX Nash bargaining product, v2)."""
    return _clamp01(a) * _clamp01(p) * _clamp01(e) * _clamp01(x) * _clamp01(phi)


def c_dark(a: float, p: float, x: float) -> float:
    """C_dark = A · (1 − P) · (1 − X). Gaming potential.

    C_dark > 0.15 → HOLD; C_dark → 0 → SEAL candidate.
    """
    return _clamp01(a) * (1.0 - _clamp01(p)) * (1.0 - _clamp01(x))


def w3_witness(h: float, ai: float, ext: float) -> float:
    """W³ = (H · AI · EXT)^(1/3). Unknown channel MUST be 0.0 (not 0.5).

    Zero in any channel collapses consensus to 0.
    """
    h_c, ai_c, ext_c = _clamp01(h), _clamp01(ai), _clamp01(ext)
    if h_c <= 0.0 or ai_c <= 0.0 or ext_c <= 0.0:
        return 0.0
    return (h_c * ai_c * ext_c) ** (1.0 / 3.0)


def w3_verdict(w3: float) -> str:
    """W³ band → CONSENSUS | WEAK | DIVERGENT."""
    if w3 >= W3_CONSENSUS:
        return "CONSENSUS"
    if w3 >= W3_WEAK:
        return "WEAK"
    return "DIVERGENT"


def classify_phase(
    tank: float,
    *,
    export_completed: bool,
    t_margin: float = T_MARGIN,
    t_critical: float = T_CRITICAL,
    t_abundance: float = T_ABUNDANCE,
) -> MetabolicPhase:
    """Map tank + export state → metabolic phase."""
    t = _clamp01(tank)
    if t <= t_critical:
        return MetabolicPhase.MARGIN_ZEN
    if t <= t_margin:
        return MetabolicPhase.MARGIN_REFLEX
    if t >= t_abundance:
        if export_completed:
            return MetabolicPhase.ABUNDANCE_EUREKA_OK
        return MetabolicPhase.ABUNDANCE_MUST_ZEN
    return MetabolicPhase.NORMAL_DUAL


def gate_label_for(
    phase: MetabolicPhase,
    *,
    metabolic_balance_m: float,
    export_receipt: ExportReceipt | None,
    proposing_eureka: bool,
) -> tuple[ZenGateLabel, str]:
    """Iron-rule gate labels. Labels only — never silent block."""
    if phase == MetabolicPhase.MARGIN_ZEN:
        if proposing_eureka:
            return (
                ZenGateLabel.MARGIN_EXPORT_ONLY,
                "T≤T_CRITICAL: expansion illegal; only compression pays",
            )
        return ZenGateLabel.PASS, "margin zen — compression is correct work"

    if phase == MetabolicPhase.ABUNDANCE_MUST_ZEN and proposing_eureka:
        return (
            ZenGateLabel.ZEN_BEFORE_EUREKA,
            "T≥T_ABUNDANCE and no export this epoch: forced zen before next eureka",
        )

    if (
        phase in (MetabolicPhase.ABUNDANCE_MUST_ZEN, MetabolicPhase.ABUNDANCE_EUREKA_OK)
        and metabolic_balance_m < MET_HEALTHY
        and proposing_eureka
    ):
        return (
            ZenGateLabel.METABOLIC_DEBT,
            f"M={metabolic_balance_m:.3f}<1 under abundance: inject dominates export",
        )

    if phase == MetabolicPhase.ABUNDANCE_EUREKA_OK:
        return ZenGateLabel.PASS, "abundance export completed; eureka admissible"

    if phase == MetabolicPhase.MARGIN_REFLEX:
        return ZenGateLabel.PASS, "margin reflex zone — honest audit preferred"

    return ZenGateLabel.PASS, "normal dual phase — eureka and zen both open"


# ─────────────────────────────────────────────────────────────────────────────
# Top-level probe
# ─────────────────────────────────────────────────────────────────────────────


def compute_eureka_zen(
    tank: TankState | float,
    flux: EntropyFlux | None = None,
    *,
    export_receipt: ExportReceipt | None = None,
    proposing_eureka: bool = True,
    t_margin: float = T_MARGIN,
    t_critical: float = T_CRITICAL,
    t_abundance: float = T_ABUNDANCE,
    zen_first: float = ZEN_FIRST,
    extras: dict[str, Any] | None = None,
) -> EurekaZenMetrics:
    """Compute full EUREKA·ZEN margin metrics for the current session probe.

    Args:
        tank: TankState or float T ∈ [0,1]
        flux: inject/export this epoch (defaults to zeros)
        export_receipt: optional Q4 export evidence
        proposing_eureka: True if caller intends entropy injection next
        thresholds: override only under F13 ratify

    Returns:
        EurekaZenMetrics — observational + gate label. Not a verdict.
    """
    if isinstance(tank, (int, float)):
        t = _clamp01(float(tank))
    else:
        t = tank.resolve()

    flux = flux or EntropyFlux()
    receipt = export_receipt or ExportReceipt()
    export_done = receipt.is_valid_export()

    j = flux.inject
    x = flux.export
    # If receipt claims export work, fold into X if not already counted
    if export_done and x <= 0 and receipt.export_actions:
        x = max(x, float(len(receipt.export_actions)))

    m = metabolic_balance(j, x)
    ds = session_delta_s(j, x)
    phase = classify_phase(
        t,
        export_completed=export_done,
        t_margin=t_margin,
        t_critical=t_critical,
        t_abundance=t_abundance,
    )
    label, reason = gate_label_for(
        phase,
        metabolic_balance_m=m,
        export_receipt=receipt if receipt.completed else None,
        proposing_eureka=proposing_eureka,
    )

    ue, uz = u_eureka(t), u_zen(t)
    theorem_extras = {
        "u_eureka": ue,
        "u_zen": uz,
        "preferred_mode": preferred_mode(t, t_indifference=t_abundance),
        "sealed_framework": SEALED_FRAMEWORK_PATH,
        "sealed_vault_hash": SEALED_VAULT_HASH,
    }
    if extras:
        theorem_extras.update(extras)

    return EurekaZenMetrics(
        probe_id=str(uuid.uuid4()),
        ts=time.time(),
        tank=t,
        inject=j,
        export=x,
        delta_s_session=ds,
        metabolic_balance=m,
        phase=phase,
        gate_label=label,
        export_completed=export_done,
        zen_first_fraction=zen_first,
        abundance_threshold=t_abundance,
        margin_threshold=t_margin,
        critical_threshold=t_critical,
        f4_pass=ds <= 0.0,
        iron_line="Zen is not the last 2%. Zen is the first 10% of every full tank.",
        reason=reason,
        confidence=CONFIDENCE_CAP,
        extras=theorem_extras,
    )


def should_force_zen(
    metrics: EurekaZenMetrics,
) -> bool:
    """True when iron rule says export before eureka."""
    return metrics.gate_label in {
        ZenGateLabel.ZEN_BEFORE_EUREKA,
        ZenGateLabel.MARGIN_EXPORT_ONLY,
    }


# ═══════════════════════════════════════════════════════════════════════════
# SUNSHINE CHILD — eureka candidate protocol (CANDIDATE ONLY)
# ═══════════════════════════════════════════════════════════════════════════
#
# Child generates curiosity → Jauhari recognises value → BIJAKSANA tests
# → Reality decides.
#
# CANDIDATE ONLY outputs cannot proceed to JUDGE/SEAL/FORGE without
# first passing through Jauhari verification.
#
# Three rules:
#   1. Every candidate hypothesis is labelled CANDIDATE ONLY by default
#   2. Candidate cannot reach judge/seal/forge without evidence check
#   3. The child generates. The jauhari verifies. The sovereign decides.
# ═══════════════════════════════════════════════════════════════════════════
#
# NOTE: EurekaCandidate data model has been migrated to
#   arifosmcp/runtime/candidate_store.py — the authoritative server-managed
#   state machine. The functions below are now thin wrappers over the store.
#   The old EurekaCandidate dataclass is DEPRECATED. Use EurekaCandidateRecord
#   and CandidateStore for all new code.
#
# DITEMPA BUKAN DIBERI — Forged, Not Given.
# ═══════════════════════════════════════════════════════════════════════════

from arifosmcp.runtime.candidate_store import (
    CandidateNotFoundError,
    EurekaCandidateRecord,
    EurekaCandidateState,
    get_candidate_store,
    verify_candidate_for_authority,
)

# Re-export for backward compatibility
EurekaCandidate = EurekaCandidateRecord


def jauhari_check(
    candidate_ref: str | EurekaCandidateRecord | None,
    *,
    session_id: str | None = None,
    require_evidence: bool = True,
    actor_id: str = "",
) -> dict[str, bool | str]:
    """Jauhari gate: CANDIDATE ONLY → PROMOTED.

    A candidate MUST pass this check before it can proceed to
    arif_judge, arif_seal, or arif_forge (beyond PROMOTED state).

    Now uses the authoritative CandidateStore. The caller provides a
    candidate_ref (string ID) or an EurekaCandidateRecord.

    The jauhari asks:
      1. Is the candidate in the store? (not forged)
      2. Is there evidence this hypothesis connects to reality?
      3. Are there counterexamples that would falsify it?
      4. Can it be promoted from UNREVIEWED to PROMOTED?

    Args:
        candidate_ref: The candidate reference (ID string or record).
                       If None, assumes normal (non-wonder) work — passes.
        session_id: Governing session for store lookup.
        require_evidence: Whether evidence is mandatory for promotion.
        actor_id: Who is requesting the promotion.

    Returns:
        Dict with pass (bool), reason, and details.
    """
    if candidate_ref is None:
        return {"pass": True, "reason": "No candidate — normal work, no gate needed."}

    store = get_candidate_store()

    # Resolve candidate_id from string or record
    if isinstance(candidate_ref, str):
        try:
            record = store.get_candidate(candidate_ref, session_id=session_id)
        except CandidateNotFoundError:
            return {
                "pass": False,
                "reason": f"JAUHARI HOLD: candidate_ref={candidate_ref} not found in store. ",
                "candidate_only_blocked": True,
            }
        except Exception as exc:
            return {
                "pass": False,
                "reason": f"JAUHARI HOLD: candidate lookup failed: {exc}",
                "candidate_only_blocked": True,
            }
        candidate_id = candidate_ref
    else:
        record = candidate_ref
        candidate_id = record.candidate_id

    # Check current state
    if record.state != EurekaCandidateState.UNREVIEWED:
        if record.state in (
            EurekaCandidateState.PROMOTED,
            EurekaCandidateState.VERIFYING,
            EurekaCandidateState.VERIFIED,
        ):
            return {
                "pass": True,
                "candidate_id": candidate_id,
                "has_evidence": bool(record.evidence_refs),
                "has_counterexamples": bool(record.counterexamples),
                "current_state": record.state.value,
                "reason": f"JAUHARI PASS: candidate already in state {record.state.value}.",
                "next_step": "proceed to next stage",
            }
        if record.state == EurekaCandidateState.TENSION:
            return {
                "pass": False,
                "candidate_id": candidate_id,
                "current_state": "TENSION",
                "reason": "JAUHARI HOLD: candidate is in TENSION state. Resolve tension first.",
                "candidate_only_blocked": True,
            }
        if record.state in (EurekaCandidateState.KILAUAN, EurekaCandidateState.REJECTED):
            return {
                "pass": False,
                "candidate_id": candidate_id,
                "current_state": record.state.value,
                "reason": f"JAUHARI HOLD: candidate is in terminal state {record.state.value}.",
                "candidate_only_blocked": True,
            }

    # Evaluate evidence
    has_evidence = len(record.evidence_refs) > 0 if require_evidence else True

    if not has_evidence:
        return {
            "pass": False,
            "candidate_id": candidate_id,
            "has_evidence": False,
            "current_state": "UNREVIEWED",
            "reason": "JAUHARI HOLD: no evidence attached. Candidate cannot proceed to judge/seal/forge without evidence.",
            "candidate_only_blocked": True,
            "next_step": "return to child: gather evidence via arif_observe",
        }

    # Promote from UNREVIEWED to PROMOTED
    try:
        promoted = store.transition(
            candidate_id,
            EurekaCandidateState.PROMOTED,
            actor_id=actor_id,
            reason="Jauhari evidence check passed",
            session_id=session_id,
        )
    except Exception as exc:
        return {
            "pass": False,
            "reason": f"JAUHARI HOLD: promotion failed: {exc}",
            "candidate_only_blocked": True,
        }

    return {
        "pass": True,
        "candidate_id": candidate_id,
        "has_evidence": has_evidence,
        "has_counterexamples": bool(record.counterexamples),
        "jauhari_verified": True,
        "current_state": promoted.state.value,
        "transition_seq": promoted.transition_seq,
        "reason": "JAUHARI PASS: evidence found, candidate promoted to PROMOTED.",
        "next_step": "proceed to arif_think(mode=verify) or route to BIJAKSANA",
    }


def require_jauhari_before_judge(
    candidate_ref: str | EurekaCandidateRecord | None,
    *,
    session_id: str | None = None,
    required_state: EurekaCandidateState = EurekaCandidateState.VERIFIED,
) -> bool:
    """Constitutional firewall: True = candidate can proceed to judge/seal/forge.

    Now uses the authoritative CandidateStore.

    If no candidate_ref is provided, assumes this is normal governance work.
    If candidate_ref is provided but not in required state, BLOCKS.

    Args:
        candidate_ref: The candidate reference (ID string or record).
        session_id: Governing session for store lookup.
        required_state: Minimum state required (default VERIFIED for authority tools).

    Returns:
        True if candidate is verified and can proceed.
    """
    if candidate_ref is None:
        return True  # normal work, no child involved

    verdict = verify_candidate_for_authority(
        candidate_ref if isinstance(candidate_ref, str) else candidate_ref.candidate_id,
        session_id=session_id,
        required_state=required_state,
    )
    return bool(verdict.get("pass", False))


# ═══════════════════════════════════════════════════════════════════════════════
# Zen Debt — corrected minimal model (2026-07-18)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Per F13 SOVEREIGN verdict: one operational metric called Zen debt, calculated
# separately across canonical QQQQ layers, plus one decision function.
#
# Canonical QQQQ layers (from GENESIS/022_EUREKA_ZEN_MARGIN.md, QQQ_RECOMMENDATION_PROTOCOL.md):
#   Q1: Qualitative — option-space honesty (F2 TRUTH)
#   Q2: Quantitative — measured trade-offs (F4 CLARITY)
#   Q3: Quantum — second-order awareness (F7 HUMILITY)
#   Q4: Zen Export — forced entropy export under abundance (F4 + metabolism)
#
# For each layer i:
#   D_i = max(0, alpha_i * E_i - Z_i)
#   D_total = sum w_i * D_i
#
# Where:
#   E_i = evidence-backed new unresolved obligations in layer i
#   Z_i = evidence-backed obligations closed/verified/archived/rejected in layer i
#   alpha_i = governed cleanup obligation per layer (configurable)
#   D_i = remaining Zen debt
# ═══════════════════════════════════════════════════════════════════════════════

from dataclasses import dataclass, field

# Default cleanup obligation ratios per QQQQ layer.
# Q1 identity debt matters most; Q4 harness debt matters least.
# These are initial guesses — tune from telemetry.
DEFAULT_ALPHA: dict[str, float] = {
    "Q1": 0.50,  # identity: every 2 eureka units -> 1 zen unit obligation
    "Q2": 0.33,  # functions: every 3 -> 1
    "Q3": 0.25,  # extensions: every 4 -> 1
    "Q4": 0.25,  # forge: every 4 -> 1
}
DEFAULT_WEIGHTS: dict[str, float] = {
    "Q1": 0.40,
    "Q2": 0.25,
    "Q3": 0.20,
    "Q4": 0.15,
}
DEFAULT_DEBT_LIMIT: float = 10.0
DEFAULT_Q1_LIMIT: float = 3.0  # Q1 debt above this -> ZEN_REQUIRED


@dataclass
class LayerZenDebt:
    """Zen debt for one QQQQ layer."""

    layer: str
    eureka_units: float = 0.0
    zen_units: float = 0.0
    alpha: float = 0.25
    weight: float = 0.25
    debt: float = 0.0

    def compute(self) -> float:
        """D_i = max(0, alpha_i * E_i - Z_i)."""
        e = max(0.0, self.eureka_units)
        z = max(0.0, self.zen_units)
        self.debt = max(0.0, self.alpha * e - z)
        return self.debt


@dataclass
class ZenDebtState:
    """Complete Zen debt state across all QQQQ layers."""

    layers: dict[str, LayerZenDebt] = field(default_factory=dict)
    total_debt: float = 0.0
    debt_limit: float = DEFAULT_DEBT_LIMIT
    q1_limit: float = DEFAULT_Q1_LIMIT
    upstream_verdict: str = ""

    def compute_total(self) -> float:
        """D_total = sum w_i * D_i."""
        self.total_debt = 0.0
        for layer in self.layers.values():
            layer.compute()
            self.total_debt += layer.weight * layer.debt
        return self.total_debt


def compute_zen_debt(
    q1_eureka: float = 0.0,
    q1_zen: float = 0.0,
    q2_eureka: float = 0.0,
    q2_zen: float = 0.0,
    q3_eureka: float = 0.0,
    q3_zen: float = 0.0,
    q4_eureka: float = 0.0,
    q4_zen: float = 0.0,
    *,
    alpha: dict[str, float] | None = None,
    weights: dict[str, float] | None = None,
    debt_limit: float = DEFAULT_DEBT_LIMIT,
    q1_limit: float = DEFAULT_Q1_LIMIT,
) -> ZenDebtState:
    """Compute Zen debt across all 4 canonical QQQQ layers.

    Args:
        q1_eureka/q1_zen: identity layer (highest weight, lowest tolerance)
        q2_eureka/q2_zen: functions layer
        q3_eureka/q3_zen: extensions layer
        q4_eureka/q4_zen: forge/harnesses layer
        alpha: per-layer cleanup obligation ratios (default: DEFAULT_ALPHA)
        weights: per-layer weights for total (default: DEFAULT_WEIGHTS)
        debt_limit: total debt threshold (default: 10.0)
        q1_limit: Q1 debt threshold (default: 3.0)

    Returns:
        ZenDebtState with per-layer debts, total, and thresholds.
    """
    a = {**DEFAULT_ALPHA, **(alpha or {})}
    w = {**DEFAULT_WEIGHTS, **(weights or {})}

    layers = {
        "Q1": LayerZenDebt(
            layer="Q1", eureka_units=q1_eureka, zen_units=q1_zen, alpha=a["Q1"], weight=w["Q1"]
        ),
        "Q2": LayerZenDebt(
            layer="Q2", eureka_units=q2_eureka, zen_units=q2_zen, alpha=a["Q2"], weight=w["Q2"]
        ),
        "Q3": LayerZenDebt(
            layer="Q3", eureka_units=q3_eureka, zen_units=q3_zen, alpha=a["Q3"], weight=w["Q3"]
        ),
        "Q4": LayerZenDebt(
            layer="Q4", eureka_units=q4_eureka, zen_units=q4_zen, alpha=a["Q4"], weight=w["Q4"]
        ),
    }

    state = ZenDebtState(layers=layers, debt_limit=debt_limit, q1_limit=q1_limit)
    state.compute_total()
    return state


def metabolic_mode(state: ZenDebtState) -> dict[str, Any]:
    """Minimal kernel decision: EUREKA_ALLOWED / ZEN_BEFORE_EUREKA / ZEN_REQUIRED.

    Rules:
      1. If upstream_verdict is HOLD or VOID -> HOLD (Zen metrics never override).
      2. If Q1 identity debt > q1_limit -> ZEN_REQUIRED (identity debt is existential).
      3. If total Zen debt > debt_limit -> ZEN_BEFORE_EUREKA.
      4. Otherwise -> EUREKA_ALLOWED.

    Args:
        state: ZenDebtState from compute_zen_debt().

    Returns:
        Dict with mode, reasons, and all layer debts for audit.
    """
    # Rule 1: Upstream verdict always wins
    if state.upstream_verdict in {"HOLD", "VOID"}:
        return {
            "mode": state.upstream_verdict,
            "reasons": [f"Upstream verdict {state.upstream_verdict} — Zen metrics cannot override"],
            "total_debt": state.total_debt,
            "debt_limit": state.debt_limit,
            "q1_debt": state.layers.get("Q1", LayerZenDebt(layer="Q1")).debt,
            "q1_limit": state.q1_limit,
            "layers": {
                k: {"eureka": v.eureka_units, "zen": v.zen_units, "debt": v.debt}
                for k, v in state.layers.items()
            },
        }

    q1_debt = state.layers.get("Q1", LayerZenDebt(layer="Q1")).debt

    # Rule 2: Q1 identity debt existential
    if q1_debt > state.q1_limit:
        return {
            "mode": "ZEN_REQUIRED",
            "reasons": [f"Q1 identity debt {q1_debt:.1f} > limit {state.q1_limit}"],
            "total_debt": state.total_debt,
            "debt_limit": state.debt_limit,
            "q1_debt": q1_debt,
            "q1_limit": state.q1_limit,
            "layers": {
                k: {"eureka": v.eureka_units, "zen": v.zen_units, "debt": v.debt}
                for k, v in state.layers.items()
            },
        }

    # Rule 3: Total Zen debt
    if state.total_debt > state.debt_limit:
        return {
            "mode": "ZEN_BEFORE_EUREKA",
            "reasons": [f"Total Zen debt {state.total_debt:.1f} > limit {state.debt_limit}"],
            "total_debt": state.total_debt,
            "debt_limit": state.debt_limit,
            "q1_debt": q1_debt,
            "q1_limit": state.q1_limit,
            "layers": {
                k: {"eureka": v.eureka_units, "zen": v.zen_units, "debt": v.debt}
                for k, v in state.layers.items()
            },
        }

    # Rule 4: Default
    return {
        "mode": "EUREKA_ALLOWED",
        "reasons": [f"Total Zen debt {state.total_debt:.1f} within limit {state.debt_limit}"],
        "total_debt": state.total_debt,
        "debt_limit": state.debt_limit,
        "q1_debt": q1_debt,
        "q1_limit": state.q1_limit,
        "layers": {
            k: {"eureka": v.eureka_units, "zen": v.zen_units, "debt": v.debt}
            for k, v in state.layers.items()
        },
    }


def verify_zen_evidence(
    *,
    unresolved_surface_delta: float,
    drift_delta: float,
    receipts_produced: int = 0,
) -> dict[str, bool | list[str]]:
    """Kernel-verified Zen: was Zen actually performed?

    Zen can only be verified by measurable decrease in unresolved surface
    (delta_Q < 0), decrease in drift (delta_D < 0), or receipts produced (R > 0).

    Writing 'I performed Zen' without evidence -> ZenVerified = False.
    """
    evidence: list[str] = []
    if unresolved_surface_delta < 0:
        evidence.append(f"surface decreased by {abs(unresolved_surface_delta):.1f}")
    if drift_delta < 0:
        evidence.append(f"drift decreased by {abs(drift_delta):.1f}")
    if receipts_produced > 0:
        evidence.append(f"{receipts_produced} receipts produced")

    if evidence:
        return {
            "verified": True,
            "reason": "Zen verified: " + "; ".join(evidence),
            "evidence": evidence,
        }
    return {
        "verified": False,
        "reason": "No measurable Zen detected — delta_Q >= 0, delta_D >= 0, R = 0. Self-reported Zen without evidence is not verified.",
        "evidence": [],
    }
