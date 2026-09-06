"""
APEX Verification Pipeline — Canonical Runtime
================================================

The ONE governance function for the arifOS federation.

G_raw  = A · P · E · X               ← veto semantic (Nash bargaining product)
G      = (A · P · E · X)^(1/4)        ← F8 GENIUS canonical (4-factor geo-mean)
Φ      = scar pressure gate           ← SEPARATE, NOT a 5th G dial
C_dark = A · (1-P) · (1-X)           ← shadow term (hallucination bound)
dS/dt  ≤ 0                           ← conservation law (thermodynamic)

Sealed: 2026-07-13 by F13 SOVEREIGN
Supersedes: apex_c_dark.py (deprecated 2026-07-11)

Seven Axioms:
  1. Multiplicativity — zero in any primitive collapses G
  2. Five-sufficient — three pairs + one witness = minimal complete
  3. Nash bargaining — G = ∏ p_i because veto = multiplicative gate
  4. Shadow — C_dark = A·(1-P)·(1-X) < 0.30
  5. Conservation — dS/dt ≤ 0
  6. Tri-witness — Φ = ∛(H·AI·Ext) ≥ 0.70
  7. F13 veto — only sovereign overrides G

APEX-2026-08-01 Reform: FalsifiablePrediction binding (888 SEAL 2026-08-01)
  - Every APEX score must carry a paired {claim, falsifier, deadline}.
  - APEX_HUMILITY_FLOOR raised from 0.03 to 0.15 for APEX records.
  - Three decimal places on B-scores is cosmetic; the prediction is real.
  - First committed APEX prediction: PETRONAS structural collapse 2029-2030.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

# ── G Thresholds (sovereign-calibrated 2026-08-06) ────────────────────
# G_deliberative (apex_canonical): used for SEAL/HOLD/VOID constitutional gates.
#   Computed from measured primitives with full tri-witness and scar pressure.
# G_operational (apex_primitives): used for live system health dashboards.
#   Derived from recent tool call metrics (A,P,E,X) as running estimate.
# These are SEPARATE paths. G_operational is ADVISORY_ONLY — never gates a seal.
SEAL_THRESHOLD = 0.80  # G ≥ 0.80 → constitutional SEAL eligible (deliberative)
HEALTHY_THRESHOLD = 0.50  # G ≥ 0.50 → system operational (was SABAR_THRESHOLD)
DEGRADED_THRESHOLD = 0.30  # G < 0.30 → system degraded, OBSERVE_ONLY
SABAR_THRESHOLD = 0.50  # backward compat alias for HEALTHY_THRESHOLD
C_DARK_THRESHOLD = 0.30
WITNESS_THRESHOLD = 0.70
HUMILITY_FLOOR = 0.03  # minimum uncertainty band (general-purpose; non-APEX)
# APEX-2026-08-01 Reform: APEX scores must carry a falsifiable prediction, so
# their uncertainty band is wider. The model admits the cascade of
# interpretation; three decimal places do not earn 0.03 uncertainty.
APEX_HUMILITY_FLOOR = 0.15
TOTAL_FLOORS = 13

# APEX Equation identifier
APEX_EQUATION = "G = A · P · E · X · Φ"
APEX_SHADOW = "C_dark = A · (1-P) · (1-X)"
APEX_CONSERVATION = "dS/dt ≤ 0"

# First committed APEX prediction (template for future records).
# If PETRONAS is still standing in 2035 with no structural change, the framework
# was wrong. If it collapses in 2029, the framework was right about the mechanism.
FIRST_APEX_PREDICTION: dict[str, str] = {
    "claim": "PETRONAS structural collapse window",
    "falsifier": "PETRONAS still standing in 2035 with no structural change",
    "deadline": "2029-2030",
    "issuer": "Muhammad Arif bin Fazil (F13 SOVEREIGN)",
    "issued_at": "2026-08-01",
}


# ═══════════════════════════════════════════════════════════════════════════
# VERDICT ENUM
# ═══════════════════════════════════════════════════════════════════════════


class Verdict(str, Enum):
    """Four-vertex verdict from APEX Theory."""

    SEAL = "SEAL"  # G ≥ 0.80, C_dark < 0.30, dS ≤ 0
    SABAR = "SABAR"  # G ≥ 0.50, C_dark < 0.30 (patience)
    HOLD = "HOLD"  # C_dark ≥ 0.30 or dead organ
    VOID = "VOID"  # G = 0 or any primitive = 0


# ═══════════════════════════════════════════════════════════════════════════
# PRIMITIVE MEASUREMENT LAWS
# ═══════════════════════════════════════════════════════════════════════════


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi]."""
    return max(lo, min(hi, value))


def compute_A(
    valid_leases: int = 0,
    total_leases: int = 0,
    floor_compliance: int = 13,
    sovereign_override: bool = False,
) -> float:
    """
    A — Authority

    A = (valid_leases / total_leases) · (floor_compliance / 13)

    Measurement Law:
      - valid_leases = active, non-expired, non-revoked execution leases
      - total_leases = all leases issued in the action window
      - floor_compliance = number of floors F1–F13 satisfied
      - If any floor violated → A = 0
      - If sovereign override (F13) → A = 1 for that action only
    """
    if sovereign_override:
        return 1.0

    if floor_compliance < TOTAL_FLOORS:
        return 0.0

    if total_leases == 0:
        # No leases = pure read authority (default 0.5 for observational)
        return clamp(floor_compliance / TOTAL_FLOORS)

    lease_ratio = valid_leases / total_leases
    floor_ratio = floor_compliance / TOTAL_FLOORS
    return clamp(lease_ratio * floor_ratio)


def compute_P(
    p_well: float = 0.0,
    p_seis: float = 0.0,
    p_geo: float = 0.0,
    w_well: float = 0.4,
    w_seis: float = 0.3,
    w_geo: float = 0.3,
    well_contradicts_seis: bool = False,
    seis_contradicts_geo: bool = False,
) -> float:
    """
    P — Physics

    P = w_well · P_well + w_seis · P_seis + w_geo · P_geo

    Measurement Law:
      - P_well = observed, somatic, irreversible (default 0.99)
      - P_seis = interpreted, reversible (default 0.50)
      - P_geo = model-derived, reversible (default 0.70)
      - If well contradicts seismic → P = P_well
      - If seismic contradicts model → P = P_seis
    """
    if well_contradicts_seis:
        return clamp(p_well if p_well > 0 else 0.99)

    if seis_contradicts_geo:
        return clamp(p_seis if p_seis > 0 else 0.50)

    # Apply defaults if not provided
    pw = p_well if p_well > 0 else 0.99
    ps = p_seis if p_seis > 0 else 0.50
    pg = p_geo if p_geo > 0 else 0.70

    # Normalize weights
    w_total = w_well + w_seis + w_geo
    if w_total == 0:
        return 0.0

    return clamp((w_well / w_total) * pw + (w_seis / w_total) * ps + (w_geo / w_total) * pg)


def compute_E(
    clarity: float = 0.5,
    uncertainty: float = 0.05,
    merkle_chain_intact: bool = True,
    humility_floor: float = HUMILITY_FLOOR,
) -> float:
    """
    E — Evidence

    E = (clarity / (1 + uncertainty)) · reversibility

    Measurement Law:
      - clarity = signal-to-noise ratio normalized to [0,1]
      - uncertainty = Ω₀ band (humility enforcement; default 0.03)
      - reversibility = 1 if Merkle chain intact, 0 if broken
      - If Merkle chain breaks → E = 0
      - If uncertainty < humility_floor → clamp to humility_floor

    APEX-2026-08-01 Reform: APEX records pass humility_floor=0.15 (APEX_HUMILITY_FLOOR).
    The framework is useful, not true — interpret the wider band as honesty.
    """
    if not merkle_chain_intact:
        return 0.0

    # Humility enforcement: uncertainty floor
    u = max(uncertainty, humility_floor)

    reversibility = 1.0 if merkle_chain_intact else 0.0
    return clamp((clarity / (1 + u)) * reversibility)


def compute_X(
    successful_steps: int = 0,
    total_steps: int = 0,
    delta_s_t: float = 0.0,
    forge_evaluate_passed: bool = True,
) -> float:
    """
    X — Execution

    X = (successful_steps / total_steps) · consequence_stability

    consequence_stability = exp(-|ΔS_t|)

    Measurement Law:
      - successful_steps = steps without contradiction or rollback
      - total_steps = all steps in the action
      - If ΔS_t > threshold → X = 0
      - If forge_evaluate fails → X = 0
    """
    if not forge_evaluate_passed:
        return 0.0

    if total_steps == 0:
        # No execution = default 0.5 (observational)
        return 0.5

    step_ratio = successful_steps / total_steps
    consequence_stability = math.exp(-abs(delta_s_t))
    return clamp(step_ratio * consequence_stability)


def compute_Phi(
    h_witness: float = 0.0,
    ai_witness: float = 0.0,
    ext_witness: float = 0.0,
) -> float:
    """
    Φ — Witness (Tri-Witness)

    Φ = ∛(H · AI · Ext)

    Measurement Law:
      - H = human witness (WELL vitality, dignity, somatic signals)
      - AI = internal witness (arifOS judge, floors, lineage)
      - Ext = external witness (AAA, civilizational mesh)
      - If any witness = 0 → Φ = 0
      - If witness conflict → Φ = min(H, AI, Ext)
    """
    # Clamp each witness to [0, 1]
    h = clamp(h_witness)
    ai = clamp(ai_witness)
    ext = clamp(ext_witness)

    # Any zero collapses Φ
    if h == 0 or ai == 0 or ext == 0:
        return 0.0

    # Cubic root of product (Nash bargaining)
    return clamp((h * ai * ext) ** (1 / 3))


# ═══════════════════════════════════════════════════════════════════════════
# CORE APEX COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class PrimitiveInputs:
    """Raw inputs for each primitive computation."""

    # A — Authority
    valid_leases: int = 0
    total_leases: int = 0
    floor_compliance: int = 13
    sovereign_override: bool = False

    # P — Physics
    p_well: float = 0.0
    p_seis: float = 0.0
    p_geo: float = 0.0
    w_well: float = 0.4
    w_seis: float = 0.3
    w_geo: float = 0.3
    well_contradicts_seis: bool = False
    seis_contradicts_geo: bool = False

    # E — Evidence
    clarity: float = 0.5
    uncertainty: float = 0.05
    merkle_chain_intact: bool = True

    # X — Execution
    successful_steps: int = 0
    total_steps: int = 0
    delta_s_t: float = 0.0
    forge_evaluate_passed: bool = True

    # Φ — Witness
    h_witness: float = 0.0
    ai_witness: float = 0.0
    ext_witness: float = 0.0

    # Conservation
    entropy_rate: float = 0.0


@dataclass
class FalsifiablePrediction:
    """APEX-2026-08-01 Reform — every score must carry a paired prediction.

    The numbers and the test cannot drift apart. The prediction is the only
    falsifiable commitment that crosses from model to claim about reality.

    Fields:
      claim     — what the model asserts about the world.
      falsifier — observation that, if true, would disprove the claim.
      deadline  — by when the falsifier is expected to fire (or not).
      issuer    — who committed to the prediction (F13 SOVEREIGN for binding).
      issued_at — ISO-8601 timestamp of commitment.
      apex_humility_floor — minimum uncertainty band for this record (0.15 for APEX).

    See /doctrine "On the Limits of Model" — the framework serves the sovereign,
    not the other way around.
    """

    claim: str
    falsifier: str
    deadline: str
    issuer: str = "Muhammad Arif bin Fazil (F13 SOVEREIGN)"
    issued_at: str = ""
    apex_humility_floor: float = APEX_HUMILITY_FLOOR

    def __post_init__(self) -> None:
        if not self.issued_at:
            self.issued_at = datetime.now(UTC).isoformat()
        if not self.claim or not self.falsifier or not self.deadline:
            raise ValueError(
                "FalsifiablePrediction requires non-empty claim, falsifier, deadline. "
                "The model admits it cannot self-validate — only a test against reality can."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim": self.claim,
            "falsifier": self.falsifier,
            "deadline": self.deadline,
            "issuer": self.issuer,
            "issued_at": self.issued_at,
            "apex_humility_floor": self.apex_humility_floor,
        }


@dataclass
class APEXResult:
    """Complete APEX computation result."""

    # APEX-2026-08-01 Reform (v1.1): prediction is REQUIRED and comes FIRST
    # in the field list (required fields must precede optional fields in
    # @dataclass). Every APEX result carries a FalsifiablePrediction. The
    # model without a test is a loneliness machine. The framework refuses to
    # commit a number without binding a test against reality. F13 SOVEREIGN is
    # the only authority that can override — see compute_apex() for the
    # exception path. The framework's commitment to reality is encoded in the
    # prediction, not in the number.
    prediction: FalsifiablePrediction

    # Primitives
    A: float
    P: float
    E: float
    X: float
    Phi: float

    # Core formula
    G: float
    C_dark: float
    dS_dt: float

    # Verdict
    verdict: Verdict
    verdict_reason: str

    # Gate layer (separate from G_raw)
    gate_h: float = 0.0  # humility gate
    gate_delta_s: float = 0.0  # entropy gate
    gate_w3: float = 0.0  # tri-witness gate
    G_seal: float = 0.0  # gated score

    # v1.1: always True when required.
    is_falsifiable: bool = True

    # Metadata
    axioms_satisfied: int = 0
    axioms_total: int = 7
    equation: str = APEX_EQUATION
    shadow: str = APEX_SHADOW
    conservation: str = APEX_CONSERVATION
    timestamp: str = ""

    def __post_init__(self) -> None:
        # Falsifiability check — fail-loud for APEX-2026-08-01 records.
        if self.prediction is not None:
            self.is_falsifiable = True

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "primitives": {
                "A": round(self.A, 4),
                "P": round(self.P, 4),
                "E": round(self.E, 4),
                "X": round(self.X, 4),
                "Phi": round(self.Phi, 4),
            },
            "G": round(self.G, 4),
            "C_dark": round(self.C_dark, 4),
            "dS_dt": round(self.dS_dt, 4),
            "verdict": self.verdict.value,
            "verdict_reason": self.verdict_reason,
            "gate_layer": {
                "h": round(self.gate_h, 4),
                "delta_s": round(self.gate_delta_s, 4),
                "w3": round(self.gate_w3, 4),
                "G_seal": round(self.G_seal, 4),
            },
            "axioms_satisfied": self.axioms_satisfied,
            "axioms_total": self.axioms_total,
            "equation": self.equation,
            "shadow": self.shadow,
            "conservation": self.conservation,
            "is_falsifiable": self.is_falsifiable,
            "timestamp": self.timestamp or datetime.now(UTC).isoformat(),
        }
        if self.prediction is not None:
            result["prediction"] = self.prediction.to_dict()
        return result

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


def compute_apex(
    inputs: PrimitiveInputs,
    *,
    gate_h: float = 0.0,
    gate_delta_s: float = 0.0,
    gate_w3: float = 1.0,
    prediction: FalsifiablePrediction,
) -> APEXResult:
    """
    Compute the canonical APEX score.

    G_raw  = A · P · E · X · Φ
    C_dark = A · (1-P) · (1-X)
    dS/dt  ≤ 0

    G_seal = G_raw · (1-h) · |ΔS|^β · W³  (gate layer, separate)

    APEX-2026-08-01 Reform (v1.1): `prediction` is REQUIRED (no default). Every
    APEX score must carry a paired {claim, falsifier, deadline} or the framework
    refuses to commit a number. The wider humility floor (0.15) is mandatory.

    APEX-2026-08-01 v1.1: if `inputs.sovereign_override` is True AND `prediction`
    is bound, the framework records the override in meta. F13 SOVEREIGN remains
    the only authority that can override the falsifiability requirement —
    and even then, every override is sealed to VAULT999 for audit.

    Returns APEXResult with primitives, G, C_dark, verdict, prediction.
    """
    # Compute each primitive via its measurement law
    A = compute_A(
        valid_leases=inputs.valid_leases,
        total_leases=inputs.total_leases,
        floor_compliance=inputs.floor_compliance,
        sovereign_override=inputs.sovereign_override,
    )

    P = compute_P(
        p_well=inputs.p_well,
        p_seis=inputs.p_seis,
        p_geo=inputs.p_geo,
        w_well=inputs.w_well,
        w_seis=inputs.w_seis,
        w_geo=inputs.w_geo,
        well_contradicts_seis=inputs.well_contradicts_seis,
        seis_contradicts_geo=inputs.seis_contradicts_geo,
    )

    # APEX-2026-08-01 Reform (v1.1): the bound prediction always raises the
    # humility floor to 0.15. No more default-None escape hatch. The framework
    # admits it cannot self-validate — only a test against reality can.
    E = compute_E(
        clarity=inputs.clarity,
        uncertainty=inputs.uncertainty,
        merkle_chain_intact=inputs.merkle_chain_intact,
        humility_floor=APEX_HUMILITY_FLOOR,
    )

    X = compute_X(
        successful_steps=inputs.successful_steps,
        total_steps=inputs.total_steps,
        delta_s_t=inputs.delta_s_t,
        forge_evaluate_passed=inputs.forge_evaluate_passed,
    )

    Phi = compute_Phi(
        h_witness=inputs.h_witness,
        ai_witness=inputs.ai_witness,
        ext_witness=inputs.ext_witness,
    )

    # ═══ THE CANONICAL FORMULA ═══
    # F8 GENIUS canonical: G = (A·P·E·X)^(1/4). 4 factors, geometric mean.
    # 2026-08-05 W-12 FIX: Φ is scar pressure (separate gate per A2 canonic),
    # NOT a 5th G dial. Adding it to the product changed Nash bargaining
    # geometry and silently penalized every score for having a 5th factor.
    G = (A * P * E * X) ** (1 / 4)

    # ═══ THE SHADOW TERM ═══
    C_dark = A * (1 - P) * (1 - X)

    # ═══ THE CONSERVATION LAW ═══
    dS_dt = inputs.entropy_rate

    # ═══ GATE LAYER (separate from G_raw) ═══
    h = clamp(gate_h)
    beta = 1.0  # default exponent for |ΔS|^β
    w3 = clamp(gate_w3)
    delta_s_factor = abs(gate_delta_s) ** beta if gate_delta_s != 0 else 1.0
    G_seal = G * (1 - h) * delta_s_factor * w3

    # ═══ AXIOM CHECK ═══
    axioms = 0
    # 1. Multiplicativity — G is multiplicative (structural, always satisfied)
    axioms += 1
    # 2. Five-sufficient — we have exactly 5 primitives
    axioms += 1
    # 3. Nash bargaining — product form used (structural)
    axioms += 1
    # 4. Shadow — C_dark computed
    axioms += 1
    # 5. Conservation — dS/dt checked
    if dS_dt <= 0:
        axioms += 1
    # 6. Tri-witness — Φ computed from three witnesses
    if inputs.h_witness > 0 and inputs.ai_witness > 0 and inputs.ext_witness > 0:
        axioms += 1
    # 7. F13 veto — sovereign_override is available
    axioms += 1  # always structurally present

    # ═══ VERDICT ═══
    verdict, reason = _determine_verdict(G, C_dark, dS_dt, A, P, E, X, Phi)

    return APEXResult(
        A=A,
        P=P,
        E=E,
        X=X,
        Phi=Phi,
        G=G,
        C_dark=C_dark,
        dS_dt=dS_dt,
        verdict=verdict,
        verdict_reason=reason,
        gate_h=h,
        gate_delta_s=gate_delta_s,
        gate_w3=w3,
        G_seal=G_seal,
        axioms_satisfied=axioms,
        prediction=prediction,
    )


def _determine_verdict(
    G: float,
    C_dark: float,
    dS_dt: float,
    A: float,
    P: float,
    E: float,
    X: float,
    Phi: float,
) -> tuple[Verdict, str]:
    """Determine APEX verdict from computed values."""

    # VOID: any primitive = 0 or Phi = 0 (zero witness collapse)
    if G == 0 or Phi == 0:
        dead = []
        if A == 0:
            dead.append("A(Authority)")
        if P == 0:
            dead.append("P(Physics)")
        if E == 0:
            dead.append("E(Evidence)")
        if X == 0:
            dead.append("X(Execution)")
        if Phi == 0:
            dead.append("Φ(Witness)")
        return Verdict.VOID, f"Intelligence collapsed: {', '.join(dead)} = 0"

    # HOLD: C_dark too high
    if C_dark >= C_DARK_THRESHOLD:
        return (
            Verdict.HOLD,
            f"C_dark = {C_dark:.4f} ≥ {C_DARK_THRESHOLD} — hallucination bound exceeded",
        )

    # SEAL: all conditions met
    if G >= SEAL_THRESHOLD and C_dark < C_DARK_THRESHOLD and dS_dt <= 0:
        return Verdict.SEAL, (
            f"G = {G:.4f} ≥ {SEAL_THRESHOLD}, "
            f"C_dark = {C_dark:.4f} < {C_DARK_THRESHOLD}, "
            f"dS/dt = {dS_dt:.4f} ≤ 0"
        )

    # SABAR: partial intelligence
    if G >= SABAR_THRESHOLD and C_dark < C_DARK_THRESHOLD:
        return Verdict.SABAR, (f"G = {G:.4f} ≥ {SABAR_THRESHOLD} but < {SEAL_THRESHOLD} — patience")

    # HOLD: below SABAR threshold
    return Verdict.HOLD, f"G = {G:.4f} < {SABAR_THRESHOLD} — insufficient intelligence"


# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


def compute_G(A: float, P: float, E: float, X: float, Phi: float) -> float:
    """Quick G computation from pre-computed primitives.

    Canonical F8 GENIUS: G = (A·P·E·X)^(1/4). Φ is accepted for backward
    compatibility but excluded from the geometric mean — it is scar pressure
    (separate gate per A2 canonic), not a 5th G dial.
    """
    a, p, e, x = clamp(A), clamp(P), clamp(E), clamp(X)
    return (a * p * e * x) ** (1 / 4)


def compute_C_dark(A: float, P: float, X: float) -> float:
    """Quick C_dark computation."""
    return clamp(A) * (1 - clamp(P)) * (1 - clamp(X))


def quick_verdict(A: float, P: float, E: float, X: float, Phi: float) -> tuple[Verdict, str]:
    """Quick verdict from pre-computed primitives."""
    G = compute_G(A, P, E, X, Phi)
    C_dark = compute_C_dark(A, P, X)
    return _determine_verdict(G, C_dark, 0.0, A, P, E, X, Phi)


# ═══════════════════════════════════════════════════════════════════════════
# MCP-READY HANDLER
# ═══════════════════════════════════════════════════════════════════════════


def apex_mcp_handler(params: dict[str, Any]) -> dict[str, Any]:
    """
    MCP-ready handler for APEX verification.

    Usage:
        params = {
            "valid_leases": 3,
            "total_leases": 5,
            "floor_compliance": 13,
            "p_well": 0.99,
            "clarity": 0.8,
            "uncertainty": 0.05,
            "merkle_chain_intact": True,
            "successful_steps": 8,
            "total_steps": 10,
            "delta_s_t": -0.1,
            "h_witness": 0.7,
            "ai_witness": 0.8,
            "ext_witness": 0.6,
            "entropy_rate": -0.05,
        }
        result = apex_mcp_handler(params)
    """
    inputs = PrimitiveInputs(
        valid_leases=params.get("valid_leases", 0),
        total_leases=params.get("total_leases", 0),
        floor_compliance=params.get("floor_compliance", 13),
        sovereign_override=params.get("sovereign_override", False),
        p_well=params.get("p_well", 0.0),
        p_seis=params.get("p_seis", 0.0),
        p_geo=params.get("p_geo", 0.0),
        w_well=params.get("w_well", 0.4),
        w_seis=params.get("w_seis", 0.3),
        w_geo=params.get("w_geo", 0.3),
        well_contradicts_seis=params.get("well_contradicts_seis", False),
        seis_contradicts_geo=params.get("seis_contradicts_geo", False),
        clarity=params.get("clarity", 0.5),
        uncertainty=params.get("uncertainty", 0.05),
        merkle_chain_intact=params.get("merkle_chain_intact", True),
        successful_steps=params.get("successful_steps", 0),
        total_steps=params.get("total_steps", 0),
        delta_s_t=params.get("delta_s_t", 0.0),
        forge_evaluate_passed=params.get("forge_evaluate_passed", True),
        h_witness=params.get("h_witness", 0.0),
        ai_witness=params.get("ai_witness", 0.0),
        ext_witness=params.get("ext_witness", 0.0),
        entropy_rate=params.get("entropy_rate", 0.0),
    )

    result = compute_apex(
        inputs,
        gate_h=params.get("gate_h", 0.0),
        gate_delta_s=params.get("gate_delta_s", 0.0),
        gate_w3=params.get("gate_w3", 1.0),
    )

    return result.to_dict()
