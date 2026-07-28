"""arifOS APEX Calculus Engine (v2026.07.APEX.3).

Canonical G = (A · P · E · X)^(1/4) — 4-factor Nash Bargaining Product.

Nash Collapse invariant: ANY dial ≤ 0 → G = 0.0000.
No compensatory arithmetic. No averaging around zeros.
No Φ, H, S, U, E² factors — Arif explicitly banned these.

APEX letters (CANON_APEX_V3, F13-ratified 2026-07-28):
  A = AKAL/AUTHORITY     → F2, F7, F10  (verified identity, lawful reasoning)
  P = PRESENT/PHYSICS    → F1, F5, F11, F13  (substrate reality, reversibility)
  E = ENERGY/EVIDENCE    → F4, F12, energy  (epistemic clarity, thermodynamic budget)
  X = EXPLORATION/XEC    → F3, F6, F8, F9, risk  (action class, provable outcomes)

Floor ownership is exclusive (no double-counting). Hard floors veto BEFORE
scoring — the geometric mean never launders a constitutional violation.
"""

import math
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Verdict(StrEnum):
    SEAL = "SEAL"
    HOLD_888 = "HOLD_888"
    HOLD = "HOLD"
    SABAR = "SABAR"
    VOID = "VOID"


@dataclass
class APEXResult:
    floors: dict[str, float]
    A: float  # AKAL
    P: float  # PRESENT_AUTHORITY
    E: float  # ENTROPY_ENERGY
    X: float  # EXPLORATION_AMANAH
    G: float  # Overall Score
    verdict: Verdict
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "floors": self.floors,
            "apex": {
                "A": self.A,
                "P": self.P,
                "E": self.E,
                "X": self.X,
                "G": self.G,
            },
            "verdict": self.verdict.value,
            "reasons": self.reasons,
        }


def geometric_mean(scores: list[float]) -> float:
    """Computes Nash Geometric Mean over a list of normalized [0, 1] floats."""
    if not scores or any(s <= 0.0 for s in scores):
        return 0.0
    return math.exp(sum(math.log(s) for s in scores) / len(scores))


def compute_apex(
    floors: dict[str, float],
    energy_score: float = 0.90,
    risk_score: float = 0.90,
    is_reversible: bool = True,
    has_human_approval: bool = False,
) -> APEXResult:
    """Computes the APEX 4-Variable Calculus and enforces Hard Floor overrides."""
    reasons: list[str] = []

    # 1. HARD FLOOR OVERRIDES (Priority 1)
    if floors.get("F13", 0.0) < 1.0:
        return APEXResult(
            floors=floors,
            A=0.0,
            P=0.0,
            E=0.0,
            X=0.0,
            G=0.0,
            verdict=Verdict.VOID,
            reasons=["F13 Sovereign violation: Human veto absolute"],
        )

    if floors.get("F9", 0.0) < 1.0 or floors.get("F10", 0.0) < 1.0:
        return APEXResult(
            floors=floors,
            A=0.0,
            P=0.0,
            E=0.0,
            X=0.0,
            G=0.0,
            verdict=Verdict.VOID,
            reasons=["F9/F10 Hard Floor breach: Deception or ontology failure"],
        )

    if floors.get("F12", 0.0) < 1.0:
        return APEXResult(
            floors=floors,
            A=0.0,
            P=0.0,
            E=0.0,
            X=0.0,
            G=0.0,
            verdict=Verdict.VOID,
            reasons=["F12 Resilience breach: Security injection risk detected"],
        )

    # 2. REVERSIBILITY GATE (Priority 2)
    is_hold = False
    if not is_reversible and not has_human_approval:
        is_hold = True
        reasons.append("F1 Amanah: Irreversible mutation requires 888_HOLD operator ratification")

    # 3. COMPUTE 4 APEX LETTERS (Nash Geometric Mean, exclusive floor ownership)
    A = geometric_mean(  # noqa: N806  AKAL — reasoning lawfulness
        [floors.get("F2", 0), floors.get("F7", 0), floors.get("F10", 0)]
    )
    P = geometric_mean(  # noqa: N806  PRESENT×PHYSICS — state truth + reversibility
        [floors.get("F1", 0), floors.get("F5", 0), floors.get("F11", 0), floors.get("F13", 0)]
    )
    E = geometric_mean(  # noqa: N806  ENERGY×EVIDENCE — epistemic clarity + budget
        [floors.get("F4", 0), floors.get("F12", 0), energy_score]
    )
    X = geometric_mean(  # noqa: N806  EXPLORATION×XEC — action class + provable outcomes
        [floors.get("F3", 0), floors.get("F6", 0), floors.get("F8", 0), floors.get("F9", 0), risk_score]
    )

    # 4. GRAND EQUATION: G = (A · P · E · X)^(1/4) — 4-factor Nash Bargaining Product
    #    Constitutional target. No E², no Φ, no H, no S, no U.
    G = geometric_mean([A, P, E, X])  # noqa: N806

    # 5. DECIDE VERDICT
    if is_hold:
        final_verdict = Verdict.HOLD_888
    elif G >= 0.80:
        final_verdict = Verdict.SEAL
    elif G >= 0.70:
        final_verdict = Verdict.SABAR
        reasons.append(f"G score {G:.4f} below 0.80 SEAL threshold")
    else:
        final_verdict = Verdict.HOLD
        reasons.append(
            f"G score {G:.4f} below minimum execution confidence; evidence density insufficient"
        )

    return APEXResult(
        floors=floors,
        A=round(A, 4),
        P=round(P, 4),
        E=round(E, 4),
        X=round(X, 4),
        G=round(G, 4),
        verdict=final_verdict,
        reasons=reasons,
    )
