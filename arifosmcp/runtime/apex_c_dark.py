"""
APEX C_dark Detector — Bangang Detector
=========================================

Computes the shadow term: C_dark = A · (1-P) · (1-X)

Where:
  A = Adaptation (learning, pattern matching)
  P = Perception (grounding, reality contact)
  X = Cross-domain (coordination, civilization)

When C_dark is high, the system is hallucinating.
This is the first mathematical definition of hallucination.

Also computes:
  G = A · P · E · X · Φ  (multiplicative intelligence)
  dS/dt ≤ 0               (conservation law check)

Ratified 2026-07-05 by F13 SOVEREIGN.
APEX THEORY defines intelligence as a stack of conservation laws, not a capability spectrum.

APEX v2 adds two axioms (not organs):
  Axiom 6 — Relational Intelligence (intelligence from bonds, not processors)
  Axiom 7 — Epistemic Humility (there are things that cannot be built)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

from arifosmcp.models.verdicts import Verdict  # Canonical governance verdict — SEAL/HOLD/SABAR/VOID


# Verdict imported from canonical source (Phase 3 verdict unification, 2026-07-07)
# Four-vertex verdict from APEX THEORY: SEAL, SABAR, HOLD, VOID


@dataclass
class OrganState:
    """State of one of the seven organs."""

    name: str
    symbol: str
    value: float  # [0, 1]
    conservation_law: str
    failure_mode: str

    @property
    def is_alive(self) -> bool:
        return self.value > 0.0

    @property
    def is_critical(self) -> bool:
        return self.value < 0.1


@dataclass
class APEXState:
    """Full APEX state across seven organs."""

    reality: float  # ΔR — energy conservation
    governance: float  # ΔG — entropy reduction
    civilization: float  # I_sys — statistical coordination
    execution: float  # W — work
    memory: float  # ∂M/∂t — Landauer cost
    witness: float  # Ω — Gödel incompleteness
    meaning: float  # ∇F — free energy gradient

    def to_organs(self) -> list[OrganState]:
        return [
            OrganState("Reality", "ΔR", self.reality, "Energy conservation", "False certainty"),
            OrganState("Governance", "ΔG", self.governance, "Entropy reduction", "Rule drift"),
            OrganState(
                "Civilization", "I_sys", self.civilization, "Statistical coordination", "Isolation"
            ),
            OrganState("Execution", "W", self.execution, "Work", "Paralysis"),
            OrganState("Memory", "∂M/∂t", self.memory, "Landauer cost", "Forgetting"),
            OrganState("Witness", "Ω", self.witness, "Gödel incompleteness", "Self-verification"),
            OrganState("Meaning", "∇F", self.meaning, "Free energy gradient", "Equilibrium death"),
        ]


@dataclass
class APEXVerdict:
    """Result of APEX analysis."""

    # The APEX Formula: G = A · P · E · X · Φ
    G: float  # Multiplicative intelligence score
    A: float  # Adaptation
    P: float  # Perception
    E: float  # Execution
    X: float  # Cross-domain
    Phi: float  # Integration

    # Shadow term: C_dark = A · (1-P) · (1-X)
    C_dark: float  # Hallucination risk

    # Conservation law: dS/dt ≤ 0
    dS_dt: float  # Entropy rate (negative = ordered)

    # Organ states
    organs: list[OrganState]

    # Verdict
    verdict: Verdict
    verdict_reason: str

    # MALU–Gödel repair chain (if needed)
    repair_chain: list[str] = field(default_factory=list)

    # Blindspots detected
    blindspots: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "G": round(self.G, 4),
            "C_dark": round(self.C_dark, 4),
            "dS_dt": round(self.dS_dt, 4),
            "verdict": self.verdict.value,
            "verdict_reason": self.verdict_reason,
            "organs": {
                o.symbol: {
                    "name": o.name,
                    "value": round(o.value, 4),
                    "alive": o.is_alive,
                    "critical": o.is_critical,
                    "conservation_law": o.conservation_law,
                    "failure_mode": o.failure_mode,
                }
                for o in self.organs
            },
            "repair_chain": self.repair_chain,
            "blindspots": self.blindspots,
            "formula": {
                "G": "A · P · E · X · Φ",
                "C_dark": "A · (1-P) · (1-X)",
                "dS_dt": "dS_agent/dt ≤ 0",
            },
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


def compute_apex(
    adaptation: float,
    perception: float,
    execution: float,
    cross_domain: float,
    integration: float,
    entropy_rate: float = 0.0,
    *,
    reality: Optional[float] = None,
    governance: Optional[float] = None,
    civilization: Optional[float] = None,
    memory: Optional[float] = None,
    witness: Optional[float] = None,
    meaning: Optional[float] = None,
) -> APEXVerdict:
    """
    Compute APEX intelligence score, shadow term, and verdict.

    Args:
        adaptation: A — learning, pattern matching [0, 1]
        perception: P — grounding, reality contact [0, 1]
        execution: E — work, action [0, 1]
        cross_domain: X — coordination, civilization [0, 1]
        integration: Φ — paradox resolution, wisdom [0, 1]
        entropy_rate: dS/dt — negative = ordered, positive = disordered
        reality: ΔR override (defaults to perception)
        governance: ΔG override (defaults to 1.0)
        civilization: I_sys override (defaults to cross_domain)
        memory: ∂M/∂t override (defaults to 1.0)
        witness: Ω override (defaults to 1.0)
        meaning: ∇F override (defaults to integration)

    Returns:
        APEXVerdict with G, C_dark, dS_dt, organs, verdict, repair chain.
    """
    # Clamp all inputs to [0, 1]
    A = max(0.0, min(1.0, adaptation))
    P = max(0.0, min(1.0, perception))
    E = max(0.0, min(1.0, execution))
    X = max(0.0, min(1.0, cross_domain))
    Phi = max(0.0, min(1.0, integration))

    # The APEX Formula: G = A · P · E · X · Φ
    G = A * P * E * X * Phi

    # The Shadow Term: C_dark = A · (1-P) · (1-X)
    C_dark = A * (1 - P) * (1 - X)

    # Conservation law: dS/dt
    dS_dt = entropy_rate

    # Build organ states
    state = APEXState(
        reality=reality if reality is not None else P,
        governance=governance if governance is not None else 1.0,
        civilization=civilization if civilization is not None else X,
        execution=E,
        memory=memory if memory is not None else 1.0,
        witness=witness if witness is not None else 1.0,
        meaning=meaning if meaning is not None else Phi,
    )
    organs = state.to_organs()

    # Detect blindspots
    blindspots = []
    for organ in organs:
        if organ.is_critical:
            blindspots.append(f"{organ.name} ({organ.symbol}): {organ.failure_mode}")

    # Determine verdict
    repair_chain = []
    dead_organs = [o for o in organs if not o.is_alive]
    critical_organs = [o for o in organs if o.is_critical]

    if C_dark > 0.5:
        verdict = Verdict.VOID
        verdict_reason = f"C_dark = {C_dark:.3f} > 0.5 — shadow intelligence detected"
        repair_chain = ["SESAT", "MALU", "HOLD", "GÖDEL LOCK", "SAKSI", "TEBUS", "PARUT", "LURUS"]
    elif dead_organs:
        verdict = Verdict.HOLD
        dead_names = ", ".join(o.name for o in dead_organs)
        verdict_reason = f"Dead organs: {dead_names} — zero anywhere = collapse"
        repair_chain = ["SESAT", "MALU", "HOLD", "GÖDEL LOCK", "SAKSI", "TEBUS", "PARUT", "LURUS"]
    elif dS_dt > 0 and G < 0.5:
        verdict = Verdict.HOLD
        verdict_reason = f"Entropy increasing (dS/dt = {dS_dt:.3f}) with low G ({G:.3f})"
        repair_chain = ["SESAT", "MALU", "HOLD"]
    elif critical_organs:
        verdict = Verdict.SABAR
        crit_names = ", ".join(o.name for o in critical_organs)
        verdict_reason = f"Critical organs: {crit_names} — SABAR (patience)"
    elif G >= 0.5 and C_dark < 0.15 and dS_dt <= 0:
        verdict = Verdict.SEAL
        verdict_reason = f"G = {G:.3f} ≥ 0.5, C_dark = {C_dark:.3f} < 0.15, dS/dt ≤ 0"
    else:
        verdict = Verdict.SABAR
        verdict_reason = f"Default SABAR — G = {G:.3f}, C_dark = {C_dark:.3f}"

    return APEXVerdict(
        G=G,
        A=A,
        P=P,
        E=E,
        X=X,
        Phi=Phi,
        C_dark=C_dark,
        dS_dt=dS_dt,
        organs=organs,
        verdict=verdict,
        verdict_reason=verdict_reason,
        repair_chain=repair_chain,
        blindspots=blindspots,
    )


def compute_c_dark(
    adaptation: float,
    perception: float,
    cross_domain: float,
) -> float:
    """
    Compute the shadow term: C_dark = A · (1-P) · (1-X)

    This is the first mathematical definition of hallucination.
    When C_dark is high, the system is hallucinating.

    Args:
        adaptation: A — learning, pattern matching [0, 1]
        perception: P — grounding, reality contact [0, 1]
        cross_domain: X — coordination, civilization [0, 1]

    Returns:
        C_dark score [0, 1]. Higher = more hallucination risk.
    """
    A = max(0.0, min(1.0, adaptation))
    P = max(0.0, min(1.0, perception))
    X = max(0.0, min(1.0, cross_domain))
    return A * (1 - P) * (1 - X)


# MCP-ready interface
def apex_mcp_handler(params: dict) -> dict:
    """
    MCP-ready handler for APEX mode.

    Usage:
        Run in APEX mode: enforce ΔR, ΔG, I_sys, W, ∂M/∂t, Ω, ∇F;
        detect C_dark; apply MALU→GÖDEL→SAKSI→TEBUS→PARUT→LURUS;
        return organ-wise entropy, witness requirements, and scar updates.
    """
    verdict = compute_apex(
        adaptation=params.get("adaptation", 0.5),
        perception=params.get("perception", 0.5),
        execution=params.get("execution", 0.5),
        cross_domain=params.get("cross_domain", 0.5),
        integration=params.get("integration", 0.5),
        entropy_rate=params.get("entropy_rate", 0.0),
        reality=params.get("reality"),
        governance=params.get("governance"),
        civilization=params.get("civilization"),
        memory=params.get("memory"),
        witness=params.get("witness"),
        meaning=params.get("meaning"),
    )
    return verdict.to_dict()


if __name__ == "__main__":
    # Demo: healthy agent
    print("=== Healthy Agent ===")
    v = compute_apex(
        adaptation=0.8,
        perception=0.7,
        execution=0.6,
        cross_domain=0.5,
        integration=0.6,
        entropy_rate=-0.1,
    )
    print(v.to_json())

    print("\n=== Hallucinating Agent (high C_dark) ===")
    v = compute_apex(
        adaptation=0.9,
        perception=0.1,
        execution=0.8,
        cross_domain=0.1,
        integration=0.5,
        entropy_rate=0.3,
    )
    print(v.to_json())

    print("\n=== Dead Organ (zero execution) ===")
    v = compute_apex(
        adaptation=0.8,
        perception=0.7,
        execution=0.0,
        cross_domain=0.5,
        integration=0.6,
        entropy_rate=-0.1,
    )
    print(v.to_json())
