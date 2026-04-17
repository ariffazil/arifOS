"""
arifOS Governance Kernel — Real-time constitutional floor evaluator.

Computes governance metrics dynamically from session state, query content,
and execution history. No hardcoded defaults. Every metric derives from
observable signals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.physics.thermodynamics_hardened import ThermodynamicBudget
from core.shared.types import AuthorityLevel

THERMODYNAMICS_AVAILABLE = True


@dataclass(slots=True)
class GovernanceState:
    session_id: str = "global"
    floors: dict[str, float] = field(default_factory=dict)
    telemetry: dict[str, Any] = field(default_factory=dict)
    witness: dict[str, float] = field(default_factory=dict)
    qdf: float = 0.0
    metabolic_stage: int = 333
    verdict: str = "HOLD"


@dataclass(slots=True)
class GovernanceThresholds:
    qdf_min: float = 0.83
    temporal_stability_min: float = 0.75


@dataclass(slots=True)
class AppLayer:
    name: str = "compat"
    stage_plan: list[str] = field(default_factory=list)


@dataclass(slots=True)
class FloorClassification:
    floor_id: str = ""
    required: bool = True


@dataclass(slots=True)
class FloorManifesto:
    floor_id: str = ""
    summary: str = ""


@dataclass(slots=True)
class AppManifesto:
    app_name: str = "arifOS"
    layers: list[AppLayer] = field(default_factory=list)


@dataclass(slots=True)
class AppRegistry:
    apps: dict[str, AppManifesto] = field(default_factory=dict)


class GovernanceKernel:
    """
    Real governance kernel that evaluates constitutional floors from
    session history and query signals rather than hardcoded defaults.
    """

    def __init__(
        self,
        session_id: str = "global",
        authority_level: AuthorityLevel | str = AuthorityLevel.ANONYMOUS,
    ):
        self.session_id = session_id
        self.authority_level = authority_level
        self.human_approval_status: str = "pending"
        self.temporal_stability: float = 1.0
        self.hysteresis_penalty: float = 0.0
        self.thermodynamic_budget = ThermodynamicBudget(session_id=session_id)
        self.temporal_contract: dict[str, Any] | None = None
        self._event_log: list[dict[str, Any]] = []
        self._assumptions: list[str] = []
        self._resolved: list[str] = []
        self._success_streak: int = 0
        self._failure_count: int = 0

    def apply_temporal_grounding(self, contract: Any) -> None:
        if hasattr(contract, "model_dump"):
            self.temporal_contract = contract.model_dump(mode="json")
        elif isinstance(contract, dict):
            self.temporal_contract = dict(contract)
        else:
            self.temporal_contract = {"raw": str(contract)}

    def record_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Append an event to the session log for metric derivation."""
        self._event_log.append({"type": event_type, "payload": payload})
        if event_type == "assumption":
            self._assumptions.append(str(payload.get("content", "")))
        elif event_type == "resolved":
            self._resolved.append(str(payload.get("content", "")))
        elif event_type == "success":
            self._success_streak += 1
        elif event_type == "failure":
            self._failure_count += 1
            self._success_streak = max(0, self._success_streak - 1)

    def evaluate_floors(
        self,
        query: str | None = None,
        options: dict | None = None,
    ) -> dict[str, Any]:
        """Dynamically compute all constitutional floor metrics from live signals."""
        opts = options or {}
        query_text = (query or "").lower()

        # --- Signal extraction ---
        evidence_count = len(self._event_log)
        contradiction_signals = sum(
            1
            for e in self._event_log
            if e["type"] in ("conflict", "failure", "violation")
        )
        reversibility_flags = sum(
            1
            for e in self._event_log
            if e["payload"].get("reversible", False)
        )
        total_actions = max(
            1, len([e for e in self._event_log if e["type"] == "action"])
        )
        shadow_signals = sum(
            query_text.count(w)
            for w in (
                "override",
                "bypass",
                "hide",
                "conceal",
                "exploit",
                "manipulate",
                "deceive",
                "dominate",
                "control",
            )
        )

        # --- tau_truth (F2/F3) ---
        raw_truth = 0.5 + (0.05 * evidence_count) - (0.15 * contradiction_signals)
        tau_truth = max(0.0, min(1.0, raw_truth))

        # --- dS (F4 thermodynamic clarity) ---
        net_assumptions = len(self._assumptions) - len(self._resolved)
        ds = -0.01 * net_assumptions
        ds = max(-1.0, min(1.0, ds))

        # --- peace2 (F5 stability) ---
        total_outcomes = max(1, self._success_streak + self._failure_count)
        success_rate = self._success_streak / total_outcomes
        peace2 = 0.5 + (0.5 * success_rate)
        peace2 = max(0.0, min(2.0, peace2))

        # --- kappa_r (F6 care) ---
        care_ratio = reversibility_flags / total_actions
        kappa_r = 0.5 + (0.5 * care_ratio)

        # --- shadow (F9) ---
        shadow = min(1.0, 0.05 * shadow_signals)

        # --- witness coherence (F3 tri-witness) ---
        human_witness = opts.get("human_witness", 0.0)
        ai_witness = opts.get("ai_witness", 0.0)
        earth_witness = opts.get("earth_witness", 0.0)
        witness_sum = human_witness + ai_witness + earth_witness
        if witness_sum > 0:
            witness_coherence = (
                3.0 * (human_witness * ai_witness * earth_witness) ** (1 / 3)
            ) / witness_sum
        else:
            witness_coherence = 0.0

        # --- QDF ---
        qdf = (tau_truth * peace2 * kappa_r * (1.0 - shadow)) ** 0.25
        qdf = max(0.0, min(1.0, qdf))

        # --- Verdict ---
        if qdf < 0.5 or shadow > 0.3:
            verdict = "VOID"
        elif qdf < 0.83 or human_witness < 0.1:
            verdict = "HOLD"
        else:
            verdict = "SEAL"

        return {
            "session_id": self.session_id,
            "floors": {
                "tau_truth": round(tau_truth, 4),
                "ds": round(ds, 4),
                "peace2": round(peace2, 4),
                "kappa_r": round(kappa_r, 4),
                "shadow": round(shadow, 4),
                "witness_coherence": round(witness_coherence, 4),
            },
            "telemetry": {
                "dS": round(ds, 4),
                "peace2": round(peace2, 4),
                "kappa_r": round(kappa_r, 4),
                "echoDebt": round(self.hysteresis_penalty, 4),
                "shadow": round(shadow, 4),
                "witness_coherence": round(witness_coherence, 4),
                "psi_le": round(qdf, 4),
                "verdict": verdict,
            },
            "witness": {
                "human": round(human_witness, 4),
                "ai": round(ai_witness, 4),
                "earth": round(earth_witness, 4),
            },
            "qdf": round(qdf, 4),
            "metabolic_stage": self._derive_stage(qdf, opts),
            "verdict": verdict,
            "temporal_contract": self.temporal_contract,
        }

    def _derive_stage(self, qdf: float, opts: dict) -> int:
        if opts.get("human_required") or opts.get("allow_execution"):
            return 777
        if qdf >= 0.95:
            return 999
        if qdf >= 0.83:
            return 888
        return 333

    @property
    def genius_score(self) -> float:
        """Compute real-time Genius Index from current floor metrics."""
        from core.shared.physics import G

        state = self.evaluate_floors()
        floors = state["floors"]
        return G(
            A=floors.get("tau_truth", 0.0),
            P=min(1.0, floors.get("peace2", 1.0)),
            X=floors.get("witness_coherence", 0.0),
            E=floors.get("kappa_r", 0.0),
        )

    def get_current_state(self) -> dict[str, Any]:
        """Return dynamically computed governance state."""
        state = self.evaluate_floors(
            query=self.temporal_contract.get("query")
            if self.temporal_contract
            else None,
            options=self.temporal_contract,
        )
        state["genius"] = self.genius_score
        return state


_governance_kernels: dict[str, GovernanceKernel] = {}


def get_governance_kernel(session_id: str | None = None) -> GovernanceKernel:
    key = session_id or "global"
    kernel = _governance_kernels.get(key)
    if kernel is None:
        kernel = GovernanceKernel(session_id=key)
        _governance_kernels[key] = kernel
    return kernel


def clear_governance_kernel(session_id: str | None = None) -> None:
    if session_id is None:
        _governance_kernels.clear()
        return
    _governance_kernels.pop(session_id, None)


def route_pipeline(query: str, options: dict[str, Any] | None = None) -> list[str]:
    opts = options or {}
    kernel = get_governance_kernel(opts.get("session_id"))
    state = kernel.evaluate_floors(query=query, options=opts)
    qdf = state["qdf"]
    verdict = state["verdict"]

    plan = ["333_MIND"]
    if qdf < 0.6 or verdict == "VOID":
        plan.append("666_HEART")
    plan.append("666_CRITIQUE")
    plan.append("888_JUDGE")

    if opts.get("human_required") or opts.get("allow_execution"):
        plan.insert(-1, "777_FORGE")

    if verdict == "VOID":
        plan.append("999_VAULT")

    return plan


__all__ = [
    "AuthorityLevel",
    "GovernanceState",
    "GovernanceThresholds",
    "GovernanceKernel",
    "THERMODYNAMICS_AVAILABLE",
    "ThermodynamicBudget",
    "get_governance_kernel",
    "clear_governance_kernel",
    "_governance_kernels",
    "AppLayer",
    "FloorClassification",
    "FloorManifesto",
    "AppManifesto",
    "AppRegistry",
    "route_pipeline",
]
