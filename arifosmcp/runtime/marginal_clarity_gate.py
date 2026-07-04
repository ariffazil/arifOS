"""Marginal Clarity Gate — Zen Equation of Governed Intelligence.

Δ*_eff = ((C_{t+1} - C_t) / Cost) × Φ(A, P, H, S, U, E)

Tripwire: when marginal clarity gain no longer justifies compute cost,
the agent stops. Not by timeout. By maturity.

DITEMPA BUKAN DIBERI — ArifOS Federation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal
import json


# ── Verdicts ──────────────────────────────────────────────────────────
Verdict = Literal["CONTINUE", "CAUTION", "HOLD", "VOID"]


# ── APH-SUE Constraint Thresholds ────────────────────────────────────
@dataclass(frozen=True)
class Constraints:
    """Hard floors for the constraint multiplier Φ."""
    amanah_min: float = 0.99       # F1: information conservation
    humility_range: tuple = (0.03, 0.15)  # F7: entropy honesty
    signal_non_decrease: bool = True      # F2: evidence quality
    understanding_non_decrease: bool = True  # F3: causal coherence
    energy_budget: float = 1.0     # Landauer bound (normalised)


DEFAULT_CONSTRAINTS = Constraints()


# ── Tripwire Thresholds (ε per 1k tokens) ────────────────────────────
EPSILON_HIGH = 0.15      # CONTINUE — active entropy reduction
EPSILON_CAUTION = 0.05   # CAUTION — slowing, shift to synthesis
EPSILON_HOLD = 0.01      # HOLD — Zen Tripwire, seal and yield
EPSILON_VOID = 0.0       # VOID — entropy increasing


# ── State Snapshot ───────────────────────────────────────────────────
@dataclass
class ClarityState:
    """Single-iteration measurement."""
    step: int
    score_ct: float          # clarity score [0,1]
    entropy_st: float        # Shannon proxy [0,1]
    signal_st: float         # signal-to-noise [0,1]
    understanding_st: float  # causal coherence [0,1]
    tokens: int = 0
    compute_flops: float = 0.0
    time_ms: float = 0.0
    presence: str = "LIVE"   # LIVE | CACHED
    amanah: float = 1.0
    humility: float = 0.08
    energy: float = 0.0      # fraction of budget consumed


@dataclass
class GateVerdict:
    """The output of one tripwire evaluation."""
    step: int
    verdict: Verdict
    delta_c: float
    delta_star: float
    phi: float
    clarity: dict
    cost: dict
    constraints: dict
    narrative: str

    def to_json(self, indent: int = 2) -> str:
        return json.dumps({
            "step": self.step,
            "clarity": self.clarity,
            "cost": self.cost,
            "aph_sue": self.constraints,
            "verdict": self.verdict,
            "narrative": self.narrative,
        }, indent=indent)


# ── The Gate ─────────────────────────────────────────────────────────
class MarginalClarityGate:
    """Hook into any arifOS loop. Call .observe() each iteration.
    When verdict is HOLD or VOID, stop the loop.
    """

    def __init__(
        self,
        constraints: Constraints = DEFAULT_CONSTRAINTS,
        patience: int = 2,
    ):
        self.constraints = constraints
        self.patience = patience
        self.history: list[ClarityState] = []
        self.hold_streak = 0

    # ── APH-SUE Constraint Multiplier Φ ──
    def _compute_phi(self, s: ClarityState) -> float:
        checks = []

        # A — Amanah: information conservation
        checks.append(s.amanah >= self.constraints.amanah_min)

        # P — Presence: temporal anchoring
        checks.append(s.presence in ("LIVE", "CACHED"))

        # H — Humility: entropy honesty
        lo, hi = self.constraints.humility_range
        checks.append(lo <= s.humility <= hi)

        # S — Signal: non-decreasing evidence quality
        # BUG FIX: history[-1] is CURRENT (already appended). Use [-2] for previous.
        if len(self.history) >= 2:
            prev = self.history[-2]
            checks.append(
                s.signal_st >= prev.signal_st
                if self.constraints.signal_non_decrease
                else True
            )
        else:
            checks.append(True)  # no baseline yet

        # U — Understanding: non-decreasing causal coherence
        if len(self.history) >= 2:
            prev = self.history[-2]
            checks.append(
                s.understanding_st >= prev.understanding_st
                if self.constraints.understanding_non_decrease
                else True
            )
        else:
            checks.append(True)  # no baseline yet

        # E — Energy: within budget
        checks.append(s.energy <= self.constraints.energy_budget)

        # Φ = 0 if ANY hard constraint violated
        if not all(checks):
            return 0.0

        # Soft scaling: fraction of constraints passing (always 1.0 if all pass)
        return sum(checks) / len(checks)

    # ── Pseudo-clarity Detection ──
    def _is_pseudo_clarity(self, s: ClarityState, delta_c: float) -> bool:
        """ΔC > 0 but Signal or Understanding dropped.
        Structural complexity masking degraded evidence.
        """
        if len(self.history) < 1:
            return False
        prev = self.history[-1]
        signal_dropped = s.signal_st < prev.signal_st
        understanding_dropped = s.understanding_st < prev.understanding_st
        return delta_c > 0 and (signal_dropped or understanding_dropped)

    # ── Effective Marginal Clarity ──
    def _compute_delta_star(
        self, delta_c: float, cost: float, phi: float
    ) -> float:
        if cost <= 0:
            return 0.0
        # Use signed delta_c — negative delta means entropy increasing
        return (delta_c / cost) * phi

    # ── Verdict ──
    def _classify(self, delta_star: float) -> Verdict:
        if delta_star < EPSILON_VOID:
            return "VOID"
        elif delta_star <= EPSILON_HOLD:
            return "HOLD"
        elif delta_star <= EPSILON_CAUTION:
            return "CAUTION"
        else:
            return "CONTINUE"

    # ── Main Entry Point ──
    def observe(self, state: ClarityState) -> GateVerdict:
        """Evaluate one iteration. Returns verdict.
        Call this every loop iteration. Stop when HOLD or VOID.
        """
        self.history.append(state)

        # First iteration: no delta possible
        if len(self.history) < 2:
            return GateVerdict(
                step=state.step,
                verdict="CONTINUE",
                delta_c=0.0,
                delta_star=0.0,
                phi=1.0,
                clarity={"score_ct": state.score_ct, "entropy_st": state.entropy_st},
                cost={"tokens": state.tokens, "time_ms": state.time_ms},
                constraints={"phi": 1.0, "note": "first iteration"},
                narrative="Baseline established. No delta yet.",
            )

        prev = self.history[-2]

        # Raw clarity delta
        delta_c = state.score_ct - prev.score_ct

        # Pseudo-clarity check
        pseudo = self._is_pseudo_clarity(state, delta_c)

        # APH-SUE constraint multiplier
        phi = self._compute_phi(state)

        # Cost (normalised: tokens per 1k)
        cost = max(state.tokens / 1000.0, 0.001)

        # Effective marginal clarity
        # If pseudo-clarity: negate (complexity masking degraded evidence)
        effective_dc = -abs(delta_c) if pseudo else delta_c
        delta_star = self._compute_delta_star(effective_dc, cost, phi)

        # Classify
        verdict = self._classify(delta_star)

        # Hard override: constraint violation (Φ=0) is always VOID
        # regardless of delta_star sign. Constraint breach = stop.
        if phi == 0.0:
            verdict = "VOID"

        # Patience logic for HOLD
        if verdict == "HOLD":
            self.hold_streak += 1
            if self.hold_streak < self.patience:
                verdict = "CAUTION"  # not yet confirmed
        else:
            self.hold_streak = 0

        # Narrative
        narratives = {
            "CONTINUE": f"Active entropy reduction. Δ*_eff={delta_star:.4f}. Keep iterating.",
            "CAUTION": f"Marginal gains slowing. Δ*_eff={delta_star:.4f}. Shift to synthesis.",
            "HOLD": f"Zen Tripwire. Δ*_eff={delta_star:.4f} below ε={EPSILON_HOLD}. Sealing state.",
            "VOID": f"Pseudo-clarity or constraint violation. Φ={phi:.2f}. Rolling back.",
        }
        if pseudo:
            narratives["VOID"] = (
                f"Pseudo-clarity detected: ΔC={delta_c:.4f} > 0 but "
                f"signal/understanding degraded. Structural complexity ≠ clarity. VOID."
            )

        return GateVerdict(
            step=state.step,
            verdict=verdict,
            delta_c=round(delta_c, 6),
            delta_star=round(delta_star, 6),
            phi=round(phi, 4),
            clarity={
                "score_ct": state.score_ct,
                "entropy_st": state.entropy_st,
                "delta_c": round(delta_c, 6),
                "delta_star": round(delta_star, 6),
            },
            cost={
                "tokens": state.tokens,
                "compute_flops": state.compute_flops,
                "time_ms": state.time_ms,
            },
            constraints={
                "phi": round(phi, 4),
                "amanah": state.amanah,
                "presence": state.presence,
                "humility": state.humility,
                "signal": state.signal_st,
                "understanding": state.understanding_st,
                "energy": state.energy,
            },
            narrative=narratives[verdict],
        )
