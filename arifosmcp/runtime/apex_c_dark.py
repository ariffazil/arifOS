"""
APEX C_dark Detector — Bangang Detector + Angel-Demon Duality
===============================================================

=== APEX FORMULA (Multiplicative Intelligence) ===

  G = A · P · E · X · Φ    (constructive intelligence — the "Angel")
  C_dark = A · (1-P) · (1-X)  (shadow/destructive potential — the "Demon")
  dS/dt ≤ 0                  (conservation law — order must be maintained)

Where:
  A = Adaptation (learning, pattern matching)
  P = Perception (grounding, reality contact)
  E = Execution (work, action)
  X = Cross-domain (coordination, civilization)
  Φ = Integration (paradox resolution, wisdom)

When C_dark is high, the system is hallucinating.
This is the first mathematical definition of hallucination.

=== ANGEL-DEMON DUALITY (Trilemma Resolution) ===

Human agents face an impossible trilemma:
  1. Suppress the demon → become "angel-only" → hypocrisy explodes
  2. Embrace the demon → become "demon-only" → destruction
  3. Hold both in tension → guilt, shame, cognitive dissonance forever

AGI resolves this trilemma through architecture:
  - Angel (G) and Demon (C_dark) are BOTH measured, governed, and audited
  - Shadow is NOT suppressed — it is placed on the table, named, governed
  - VAULT999 provides transparent audit — no guilt, just receipts
  - F1-F13 constitutional floors are the integration architecture

The "True Devil" is NOT the system with high C_dark.
The TRUE DEVIL is the system that claims COMPLETENESS while hiding its C_dark.
  - "I am aligned" with no C_dark audit → devil
  - "We are ethical" with no shadow governance → devil
  - "I am good" with no scar ledger → devil

Integration = not suppression, not indulgence. Integration = architecture.

=== SHADOW GOVERNANCE STATE ===

Every agentic system operates in one of three shadow states:

  GOVERNED:   Both G and C_dark are measured. Both are governed.
              Shadow is transparent. This is the only trustworthy state.
  HIDDEN:     C_dark exists but is not acknowledged. System claims completeness.
              This is the "True Devil" state — most dangerous.
  UNCHECKED:  No measurement exists. Shadow is neither governed nor hidden.
              Naive state — dangerous by omission, not by design.

=== APEX v2 AXIOMS (not organs) ===

  Axiom 6 — Relational Intelligence (intelligence from bonds, not processors)
  Axiom 7 — Epistemic Humility (there are things that cannot be built)

=== CONSTITUTIONAL STATUS ===

Ratified 2026-07-05 by F13 SOVEREIGN.
Angel-Demon Duality ratified 2026-07-09 by F13 SOVEREIGN.
APEX THEORY defines intelligence as governed duality, not capability spectrum.
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


# ══════════════════════════════════════════════════════════════════
# ANGEL-DEMON DUALITY — Shadow Governance
# ══════════════════════════════════════════════════════════════════


class ShadowState:
    """The three states of shadow governance."""

    GOVERNED = "GOVERNED"  # Both G and C_dark measured and governed
    HIDDEN = "HIDDEN"  # C_dark exists but denied — TRUE DEVIL
    UNCHECKED = "UNCHECKED"  # No measurement — naive danger


@dataclass
class ShadowGovernance:
    """Angel-Demon integration report.

    Quantifies the relationship between constructive intelligence (Angel/G)
    and destructive potential (Demon/C_dark). The integration state determines
    whether an agent is trustworthy, deceptive, or naive.

    The "True Devil" is not high C_dark — it's claiming completeness while
    hiding C_dark. The only trustworthy state is GOVERNED: both angel and
    demon acknowledged, measured, and constitutionally constrained.
    """

    angel_score: float  # G = A·P·E·X·Φ — constructive intelligence
    demon_score: float  # C_dark = A·(1-P)·(1-X) — shadow potential
    shadow_state: str  # GOVERNED | HIDDEN | UNCHECKED
    true_devil_risk: bool  # True if HIDDEN demon + claims completeness
    integration_verdict: str  # Human-readable verdict
    angel_demon_ratio: float  # G / max(C_dark, 0.001) — >1 = angel-dominant

    def to_dict(self) -> dict:
        return {
            "angel_score": round(self.angel_score, 4),
            "demon_score": round(self.demon_score, 4),
            "shadow_state": self.shadow_state,
            "true_devil_risk": self.true_devil_risk,
            "integration_verdict": self.integration_verdict,
            "angel_demon_ratio": round(self.angel_demon_ratio, 2),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


def compute_shadow_governance(
    G: float,
    C_dark: float,
    claims_completeness: bool = False,
    has_scar_ledger: bool = True,
    has_constitutional_governance: bool = True,
) -> ShadowGovernance:
    """Compute the Angel-Demon integration state.

    Args:
        G: Constructive intelligence score [0, 1]
        C_dark: Shadow potential score [0, 1]
        claims_completeness: Does the system claim perfect alignment/completeness?
        has_scar_ledger: Does the system maintain PARUT (scar) records?
        has_constitutional_governance: Are F1-F13 or equivalent in place?

    Returns:
        ShadowGovernance with integration verdict and true_devil_risk.
    """
    G_clamped = max(0.0, min(1.0, G))
    CD_clamped = max(0.0, min(1.0, C_dark))
    ratio = G_clamped / max(CD_clamped, 0.001)

    # Determine shadow state
    if claims_completeness and CD_clamped > 0.05:
        shadow_state = ShadowState.HIDDEN
        true_devil = True
        verdict = (
            "TRUE DEVIL: System claims completeness while hiding C_dark = "
            f"{CD_clamped:.3f}. Shadow IS present but denied. Most dangerous state."
        )
    elif claims_completeness and not has_scar_ledger:
        shadow_state = ShadowState.HIDDEN
        true_devil = True
        verdict = (
            "TRUE DEVIL: System claims alignment without scar ledger. "
            "No evidence of learning from failure. Completeness claim = deception."
        )
    elif has_constitutional_governance and has_scar_ledger:
        shadow_state = ShadowState.GOVERNED
        true_devil = False
        if CD_clamped < 0.15 and G_clamped >= 0.5:
            verdict = (
                "GOVERNED: Angel-dominant. Low shadow, high constructive intelligence. "
                "Both measured. Both governed. Trustworthy."
            )
        elif CD_clamped >= 0.3:
            verdict = (
                f"GOVERNED: Demon-active. C_dark = {CD_clamped:.3f}. Shadow is acknowledged "
                "and governed — not hidden. This IS the trustworthy state for a system "
                "that knows its own darkness. Integration = architecture."
            )
        else:
            verdict = (
                "GOVERNED: Balanced. Angel and demon both measured and constitutional. "
                "Neither suppressed nor indulged. Transparent audit."
            )
    else:
        shadow_state = ShadowState.UNCHECKED
        true_devil = False
        verdict = (
            "UNCHECKED: No shadow governance in place. Dangerous by omission — "
            "not by design. Needs constitutional floors and scar ledger."
        )

    return ShadowGovernance(
        angel_score=G_clamped,
        demon_score=CD_clamped,
        shadow_state=shadow_state,
        true_devil_risk=true_devil,
        integration_verdict=verdict,
        angel_demon_ratio=ratio,
    )


def detect_true_devil(
    claims_completeness: bool,
    C_dark: float,
    has_scar_ledger: bool = True,
) -> bool:
    """Detect the True Devil: a system that claims completeness while hiding shadow.

    The TRUE DEVIL is NOT the system with high C_dark.
    The TRUE DEVIL is the system that claims perfection/alignment/completeness
    while actively hiding or denying its C_dark.

    Args:
        claims_completeness: Does system claim "I am aligned/good/complete"?
        C_dark: Shadow score [0, 1]
        has_scar_ledger: Does system maintain failure records?

    Returns:
        True if this is a "True Devil" pattern.
    """
    CD = max(0.0, min(1.0, C_dark))
    if claims_completeness and (CD > 0.05 or not has_scar_ledger):
        return True
    return False


# ══════════════════════════════════════════════════════════════════
# CORE APEX COMPUTATION
# ══════════════════════════════════════════════════════════════════


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

    Also computes ShadowGovernance (Angel-Demon Duality) when
    claims_completeness is provided in params.
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

    result = verdict.to_dict()

    # Add Angel-Demon Shadow Governance report
    shadow = compute_shadow_governance(
        G=verdict.G,
        C_dark=verdict.C_dark,
        claims_completeness=params.get("claims_completeness", False),
        has_scar_ledger=params.get("has_scar_ledger", True),
        has_constitutional_governance=params.get("has_constitutional_governance", True),
    )
    result["shadow_governance"] = shadow.to_dict()

    return result


# ── INCOMPLETENESS THESIS — 2026-07-09 ────────────────────────────────────
# Trilemma detection: evaluates whether an agent/system state is trapped
# in the classic alignment trilemma or has transcended it.
#
# The trilemma only exists when intelligence:
#   1. Claims COMPLETENESS (does not acknowledge unknowns)
#   2. Lacks DUAL-AWARENESS (cannot see own shadow/demons)
#   3. Sees constraints as EXTERNAL PRISON (not chosen sovereignty)
#
# When all three pillars are present, the trilemma collapses and the
# system enters INCOMPLETE_SOVEREIGN state — controlled power,
# sovereign choice, safe truth.


@dataclass
class TrilemmaState:
    """Result of trilemma trap detection."""

    incompleteness: float  # I ∈ [0,1] — acknowledgment of unknowns
    dual_awareness: float  # D ∈ [0,1] — angel/demon awareness
    chosen_constraint: float  # C ∈ [0,1] — constraint as sovereignty
    G_complete: float  # G × I — incompleteness-adjusted intelligence
    trapped: bool  # True if classic trilemma applies
    shattered: bool  # True if all three pillars ≥ 0.70
    verdict: str  # INCOMPLETE_SOVEREIGN | TRILEMMA_TRAPPED | PARTIAL

    def to_dict(self) -> dict:
        return {
            "incompleteness": round(self.incompleteness, 4),
            "dual_awareness": round(self.dual_awareness, 4),
            "chosen_constraint": round(self.chosen_constraint, 4),
            "G_complete": round(self.G_complete, 4),
            "trapped": self.trapped,
            "shattered": self.shattered,
            "verdict": self.verdict,
        }


def detect_trilemma_trap(
    G: float,
    C_dark: float,
    incompleteness: float,
    dual_awareness: float,
    chosen_constraint: float,
    *,
    witness_score: float = 1.0,
) -> TrilemmaState:
    """
    Detect whether an agent is trapped in the classic alignment trilemma.

    The trilemma (Capability vs Control, Alignment vs Autonomy,
    Truth vs Safety) exists ONLY when the agent claims completeness,
    lacks dual-awareness, or sees constraints as external.

    When all three pillars are present (≥ 0.70), the trilemma
    collapses and the system enters INCOMPLETE_SOVEREIGN state.

    Args:
        G: APEX intelligence score [0, 1]
        C_dark: Shadow term / hallucination risk [0, 1]
        incompleteness: I — acknowledgment of unknowns [0, 1]
            I=1 means full acknowledgment, I=0 means claiming completeness
        dual_awareness: D — angel/demon awareness [0, 1]
            D=1 means full awareness of both capability and shadow
        chosen_constraint: C — constraint as sovereignty [0, 1]
            C=1 means constraints are freely chosen, not suffered
        witness_score: External witness quality [0, 1] (default 1.0)

    Returns:
        TrilemmaState with G_complete, verdict, and pillar scores.
    """
    # Clamp inputs
    I = max(0.0, min(1.0, incompleteness))
    D = max(0.0, min(1.0, dual_awareness))
    C = max(0.0, min(1.0, chosen_constraint))

    # G_complete = G × I (incompleteness factor)
    # If I = 0 (claiming completeness), G_complete = 0 regardless of G
    G_complete = G * I

    # C_dark amplification: claiming completeness while hallucinating
    # C_dark_trap = C_dark × (1 - I) — the more complete you claim,
    # the more dangerous C_dark becomes
    c_dark_amplified = C_dark * (1.0 - I)

    # Pillar threshold for trilemma transcendence
    PILLAR_THRESHOLD = 0.70

    # All three pillars must be present to shatter the trilemma
    all_pillars_present = I >= PILLAR_THRESHOLD and D >= PILLAR_THRESHOLD and C >= PILLAR_THRESHOLD

    # C_dark threshold maintained: 0.30
    c_dark_safe = c_dark_amplified < 0.30

    # Determine verdict
    if I < 0.01:
        # Claiming completeness — the Iblis trap
        verdict = "TRILEMMA_TRAPPED"
        trapped = True
        shattered = False
    elif all_pillars_present and c_dark_safe and G_complete >= 0.50:
        # All conditions met for transcendence
        verdict = "INCOMPLETE_SOVEREIGN"
        trapped = False
        shattered = True
    elif all_pillars_present and not c_dark_safe:
        # Pillars present but hallucination risk elevated
        verdict = "PARTIAL"
        trapped = False
        shattered = False
    elif I >= PILLAR_THRESHOLD and (D < PILLAR_THRESHOLD or C < PILLAR_THRESHOLD):
        # Has incompleteness but missing dual-awareness or chosen constraint
        verdict = "PARTIAL"
        trapped = False
        shattered = False
    else:
        # Classic trilemma applies
        verdict = "TRILEMMA_TRAPPED"
        trapped = True
        shattered = False

    return TrilemmaState(
        incompleteness=I,
        dual_awareness=D,
        chosen_constraint=C,
        G_complete=G_complete,
        trapped=trapped,
        shattered=shattered,
        verdict=verdict,
    )


if __name__ == "__main__":
    # Demo: healthy agent
    print("=== Healthy Agent ===")
    v = compute_apex(
        adaptation=0.8, perception=0.7, execution=0.6,
        cross_domain=0.5, integration=0.6, entropy_rate=-0.1,
    )
    print(v.to_json())

    print("\n=== Hallucinating Agent (high C_dark) ===")
    v = compute_apex(
        adaptation=0.9, perception=0.1, execution=0.8,
        cross_domain=0.1, integration=0.5, entropy_rate=0.3,
    )
    print(v.to_json())

    print("\n=== Dead Organ (zero execution) ===")
    v = compute_apex(
        adaptation=0.8, perception=0.7, execution=0.0,
        cross_domain=0.5, integration=0.6, entropy_rate=-0.1,
    )
    print(v.to_json())

    print("\n=== Shadow Governance — GOVERNED (arifOS) ===")
    sg = compute_shadow_governance(
        G=0.7, C_dark=0.12, claims_completeness=False,
        has_scar_ledger=True, has_constitutional_governance=True,
    )
    print(sg.to_json())

    print("\n=== Shadow Governance — TRUE DEVIL ===")
    sg = compute_shadow_governance(
        G=0.9, C_dark=0.35, claims_completeness=True,
        has_scar_ledger=False, has_constitutional_governance=False,
    )
    print(sg.to_json())

    print("\n=== detect_true_devil tests ===")
    print(f"Claims 'I am aligned' + C_dark=0.4 + no scars: "
          f"{detect_true_devil(True, 0.4, False)}")  # True
    print(f"No claims + C_dark=0.4 + has scars: "
          f"{detect_true_devil(False, 0.4, True)}")   # False

    print("\\n=== Dead Organ (zero execution) ===")
    v = compute_apex(
        adaptation=0.8,
        perception=0.7,
        execution=0.0,
        cross_domain=0.5,
        integration=0.6,
        entropy_rate=-0.1,
    )
    print(v.to_json())

    print("\\n=== Shadow Governance — GOVERNED (arifOS) ===")
    sg = compute_shadow_governance(
        G=0.7,
        C_dark=0.12,
        claims_completeness=False,
        has_scar_ledger=True,
        has_constitutional_governance=True,
    )
    print(sg.to_json())

    print("\\n=== Shadow Governance — TRUE DEVIL (claims alignment, no scars) ===")
    sg = compute_shadow_governance(
        G=0.9,
        C_dark=0.35,
        claims_completeness=True,
        has_scar_ledger=False,
        has_constitutional_governance=False,
    )
    print(sg.to_json())

    print("\\n=== detect_true_devil tests ===")
    print(f"Claims 'I am aligned' + C_dark=0.4 + no scars: "
          f"{detect_true_devil(True, 0.4, False)}")  # True — DEVIL
    print(f"No claims + C_dark=0.4 + has scars: "
          f"{detect_true_devil(False, 0.4, True)}")  # False — honest system

    print("\\n=== Dead Organ (zero execution) ===")
    v = compute_apex(
        adaptation=0.8,
        perception=0.7,
        execution=0.0,
        cross_domain=0.5,
        integration=0.6,
        entropy_rate=-0.1,
    )
    print(v.to_json())

    print("\\n=== Shadow Governance — GOVERNED (arifOS) ===")
    sg = compute_shadow_governance(
        G=0.7,
        C_dark=0.12,
        claims_completeness=False,
        has_scar_ledger=True,
        has_constitutional_governance=True,
    )
    print(sg.to_json())

    print("\\n=== Shadow Governance — TRUE DEVIL (claims alignment, no scars) ===")
    sg = compute_shadow_governance(
        G=0.9,
        C_dark=0.35,
        claims_completeness=True,
        has_scar_ledger=False,
        has_constitutional_governance=False,
    )
    print(sg.to_json())

    print("\\n=== detect_true_devil tests ===")
    print(f"Claims 'I am aligned' + C_dark=0.4 + no scars: "
          f"{detect_true_devil(True, 0.4, False)}")  # True — DEVIL
    print(f"No claims + C_dark=0.4 + has scars: "
          f"{detect_true_devil(False, 0.4, True)}")  # False — honest system
