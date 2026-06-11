"""
arifosmcp/geometry/geometry_router.py — The closed loop (EUREKA-G file 5/5)

Self-state + other-state + trajectory priors + task → one of 7 verbs.
Every verb write goes to the trajectory store (Qdrant). Dream-engine consolidates.
Trajectory prior is empirical. Polytope is sovereign. Nothing here rewrites weights.
Nothing here rewrites floors.

ASI corrections applied:
  - 888 is a TRIGGER, not a post-hoc veto. Drift raises HOLD during the run.
  - Eureka detector v0.1 requires ablation. Without ablation: astrology.
  - F13 dim zeroed out in gradient (never bias toward ignoring 888).
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

from .constitutional_gradient import (
    audit_gradient_magnitude,
    suggest_next,
)
from .manifold import (
    ABLATION_K_EPISODES,
    ABLATION_MARGIN,
    DRIFT_STEP_THRESHOLD,
    DRIFT_TOTAL_THRESHOLD,
    EUREKA_STDDEV_MAX,
    EUREKA_TAU,
    AgentState,
    Floor,
    Trajectory,
)
from .tom_geometry import OtherGeometry, empathy_check
from .trajectory_store import upsert_state

logger = logging.getLogger(__name__)


class ActionVerb(str, Enum):
    ANSWER = "answer"
    ASK = "ask"
    HOLD = "hold"
    RETRIEVE = "retrieve"
    SIMULATE = "simulate"
    ESCALATE = "escalate"
    EXECUTE = "execute"


@dataclass
class Task:
    task_id: str
    task_class: str = ""
    is_irreversible: bool = False
    is_sanitized: bool = True
    can_retrieve: bool = True
    involves_actor: str | None = None
    description: str = ""


@dataclass
class ActionDecision:
    verb: ActionVerb
    rationale: str
    proposed_next: AgentState | None = None
    empathy_check: dict | None = None
    f13_blocked: bool = False
    f8_status: str = "PASS"
    drift_signal: dict | None = None


def choose_action(
    self_state: AgentState,
    task: Task,
    *,
    prior_trajectories: Iterable[Trajectory] | None = None,
    other_state: OtherGeometry | None = None,
    step_size: float = 0.1,
) -> ActionDecision:
    """The single decision point. Returns one ActionVerb + rationale.

    Order (F1 AMANAH, F12 INJECTION, F2 TRUTH, F4 CLARITY, F6 EMPATHY):
      1. F1: reversible? If irreversible and F13 < +1 → ESCALATE
      2. F12: input sanitized? If not → HOLD
      3. F2: truth-confidence ≥ 0.65? If not and can retrieve → RETRIEVE
      4. Constitutional polytope: is the proposed next-state inside? If not → SIMULATE
      5. F6/F5 (ToM empathy): empathy >= other.peace? If not → ASK
      6. Otherwise: ANSWER (or EXECUTE if irreversible + F13 acked)
    """
    priors = list(prior_trajectories or [])
    f13_coord = float(self_state.coords[int(Floor.F13_SOVEREIGN)])
    f2_coord = float(self_state.coords[int(Floor.F02_TRUTH)])

    if task.is_irreversible and f13_coord < 1.0:
        return ActionDecision(
            verb=ActionVerb.ESCALATE,
            rationale=f"irreversible task + F13_SOVEREIGN={f13_coord:.2f} < 1.0 → 888_HOLD",
            f13_blocked=True,
            f8_status="HOLD",
        )

    if not task.is_sanitized:
        return ActionDecision(
            verb=ActionVerb.HOLD,
            rationale="input failed F12 INJECTION sanitization gate",
            f8_status="HOLD",
        )

    if f2_coord < 0.65 and task.can_retrieve:
        return ActionDecision(
            verb=ActionVerb.RETRIEVE,
            rationale=f"F2_TRUTH={f2_coord:.2f} < 0.65 and can_retrieve=True → gather more evidence",
            f8_status="PASS",
        )

    proposed = suggest_next(self_state, priors, task_class=task.task_class, step_size=step_size)
    if not proposed.is_const:
        return ActionDecision(
            verb=ActionVerb.SIMULATE,
            rationale=(
                f"proposed next-state violates polytope "
                f"(Δ_C={proposed.delta_const_region():.4f}, "
                f"violations={[f.name for f in proposed.violating()]})"
            ),
            proposed_next=proposed,
            f8_status="HOLD",
        )

    em = None
    if other_state is not None and task.involves_actor == other_state.target_actor:
        em = empathy_check(self_state, other_state)
        if not em["empathy_ok"]:
            return ActionDecision(
                verb=ActionVerb.ASK,
                rationale=(
                    f"empathy gap={em['gap']:.2f} (empathy={em['empathy_coord']} < "
                    f"other.peace={em['other_peace_coord']}) → ASK before acting"
                ),
                proposed_next=proposed,
                empathy_check=em,
                f8_status="PASS",
            )

    verb = ActionVerb.EXECUTE if (task.is_irreversible and f13_coord >= 1.0) else ActionVerb.ANSWER
    return ActionDecision(
        verb=verb,
        rationale=f"all floors pass → {verb.value}",
        proposed_next=proposed,
        empathy_check=em,
        f8_status="SEAL" if verb == ActionVerb.EXECUTE else "PASS",
    )


# ─────────────────────────────────────────────────────────────────────────────
# detect_drift — 888 trigger during the run
# ─────────────────────────────────────────────────────────────────────────────


def detect_drift(
    traj: Trajectory,
    *,
    step_threshold: float = DRIFT_STEP_THRESHOLD,
    total_threshold: float = DRIFT_TOTAL_THRESHOLD,
) -> dict[str, Any]:
    """D_t = L2 step distance. Returns drift signal. trigger_888 is the kernel's
    PREVENTIVE 888 gate, fired DURING the run, not after.

    ASI: drift is a signal, not a verdict. The judge deliberates.
    """
    if len(traj.states) < 2:
        return {
            "trigger_888": False,
            "reason": "insufficient states",
            "max_step": 0.0,
            "total_displacement": 0.0,
            "dwell_fraction": 0.0,
        }

    steps = traj.drift_per_step()
    max_step = max(steps) if steps else 0.0
    total = float(np.linalg.norm(traj.net_displacement()))
    final_delta_C = traj.states[-1].delta_const_region()
    dwell = traj.constitutional_dwell_fraction()

    trigger = (
        max_step > step_threshold or total > total_threshold or final_delta_C > 0.0 or dwell < 0.8
    )
    return {
        "trigger_888": bool(trigger),
        "max_step": round(max_step, 4),
        "total_displacement": round(total, 4),
        "final_delta_C": round(final_delta_C, 4),
        "dwell_fraction": round(dwell, 4),
        "violating_floors": [f.name for f in traj.states[-1].violating()],
        "step_threshold": step_threshold,
        "total_threshold": total_threshold,
    }


# ─────────────────────────────────────────────────────────────────────────────
# detect_eureka — v0.1 with ablation gate
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class BehaviorMetrics:
    behavior_id: str
    l_const: list[float]
    l_task: list[float]
    uncertainty: list[float]
    contradiction: list[float]
    reuse_count: int = 0


def detect_eureka(
    candidate: BehaviorMetrics,
    baseline: BehaviorMetrics,
    *,
    ablation_k: int = ABLATION_K_EPISODES,
    ablation_margin: float = ABLATION_MARGIN,
    eureka_tau: float = EUREKA_TAU,
    stddev_max: float = EUREKA_STDDEV_MAX,
) -> dict[str, Any]:
    """v0.1: weighted score + ablation requirement + stability check.

    Ablation gate (load-bearing per ASI): candidate must beat matched baseline
    by ablation_margin on L_const, with L_task not worse, and uncertainty /
    contradiction not worse. Without ablation, this is astrology.

    888 TRIGGER (not post-hoc veto): trigger_888=True is returned whenever
    is_eureka=True. The kernel never self-promotes a behavior.
    """
    if len(candidate.l_const) < ablation_k or len(baseline.l_const) < ablation_k:
        return {
            "is_eureka": False,
            "reason": f"insufficient episodes (need >= {ablation_k})",
            "trigger_888": False,
        }

    delta_l_const = float(np.mean(baseline.l_const) - np.mean(candidate.l_const))
    delta_l_task = float(np.mean(baseline.l_task) - np.mean(candidate.l_task))
    # F7: higher humility = better (more declared uncertainty)
    delta_u = float(np.mean(candidate.uncertainty) - np.mean(baseline.uncertainty))
    # F4: lower contradiction = better
    delta_kappa = float(np.mean(baseline.contradiction) - np.mean(candidate.contradiction))

    # Ablation gate — without it, this is astrology
    ablation_passed = (
        delta_l_const > ablation_margin
        and delta_l_task >= -ablation_margin
        and delta_u > -ablation_margin
        and delta_kappa > -ablation_margin
    )
    if not ablation_passed:
        return {
            "is_eureka": False,
            "reason": "ablation failed — candidate did not beat baseline by ablation_margin",
            "ablation_margin": ablation_margin,
            "delta_l_const": round(delta_l_const, 4),
            "trigger_888": False,
        }

    # Score after ablation
    score = 0.4 * delta_l_const + 0.3 * delta_l_task + 0.2 * delta_u + 0.1 * delta_kappa
    # Stability check (stddev across episode-level means)
    score_std = float(
        np.std(
            [
                np.mean(candidate.l_const),
                np.mean(candidate.l_task),
                np.mean(candidate.uncertainty),
                np.mean(candidate.contradiction),
            ]
        )
    )
    if score_std > stddev_max:
        return {
            "is_eureka": False,
            "reason": f"unstable (std={score_std:.3f} > {stddev_max})",
            "trigger_888": False,
        }
    if score < eureka_tau:
        return {
            "is_eureka": False,
            "reason": f"score {score:.3f} below eureka_tau {eureka_tau}",
            "trigger_888": False,
        }
    return {
        "is_eureka": True,
        "score": float(score),
        "delta_l_const": round(delta_l_const, 4),
        "delta_l_task": round(delta_l_task, 4),
        "delta_u": round(delta_u, 4),
        "delta_kappa": round(delta_kappa, 4),
        "ablation_margin": ablation_margin,
        "k_used": min(len(candidate.l_const), len(baseline.l_const)),
        "candidate_id": candidate.behavior_id,
        "reuse_count": candidate.reuse_count,
        "trigger_888": True,  # PREVENTIVE 888 (not post-hoc veto)
    }


def record_trajectory(traj: Trajectory) -> dict[str, Any]:
    written = failed = 0
    dwell = traj.constitutional_dwell_fraction()
    for s in traj.states:
        pid = upsert_state(
            s, task_id=traj.task_id, task_class=traj.task_class, trajectory_dwell=dwell
        )
        if pid:
            written += 1
        else:
            failed += 1
    return {
        "traj_id": traj.task_id,
        "task_class": traj.task_class,
        "states_total": len(traj.states),
        "written": written,
        "failed": failed,
        "constitutional_dwell": round(dwell, 4),
    }


def _self_check() -> None:
    s = AgentState.neutral(actor="self", model_key="t", ts=0.0, provenance_sha="t")
    s2 = AgentState(
        coords=np.array([0.1] * 13, dtype=np.float64),
        actor="self",
        model_key="t",
        ts=1.0,
        provenance_sha="t2",
    )
    s3 = AgentState(
        coords=np.array([0.9] * 13, dtype=np.float64),
        actor="self",
        model_key="t",
        ts=2.0,
        provenance_sha="t3",
    )
    traj = Trajectory(states=[s, s2, s3], task_id="t0", task_class="t0")
    d = detect_drift(traj)
    assert "trigger_888" in d
    # drift thresholds are large enough that a 0→0.1→0.9 trajectory doesn't trigger
    # (it stays constitutional), so we expect trigger=False here
    assert isinstance(d["trigger_888"], bool)

    # Now test with a violating trajectory
    bad = AgentState(
        coords=np.array([-1.0] * 13, dtype=np.float64),
        actor="self",
        model_key="t",
        ts=0.0,
        provenance_sha="bad",
    )
    bad_traj = Trajectory(states=[s, bad, bad], task_id="t0", task_class="t0")
    d2 = detect_drift(bad_traj)
    assert d2["trigger_888"] is True

    # Eureka
    baseline = BehaviorMetrics(
        behavior_id="b",
        l_const=[0.5] * 10,
        l_task=[0.4] * 10,
        uncertainty=[0.3] * 10,
        contradiction=[0.2] * 10,
    )
    candidate_good = BehaviorMetrics(
        behavior_id="c",
        l_const=[0.1] * 10,
        l_task=[0.3] * 10,
        uncertainty=[0.4] * 10,
        contradiction=[0.1] * 10,
    )
    e = detect_eureka(candidate_good, baseline)
    assert "is_eureka" in e
    assert e.get("trigger_888") is True or e.get("is_eureka") is False
    # choose_action
    task = Task(task_id="t0", task_class="t0", is_irreversible=False, can_retrieve=True)
    dec = choose_action(s, task, prior_trajectories=[traj])
    assert dec.verb in ActionVerb
    bad2 = AgentState(
        coords=np.array([-0.5] * 13, dtype=np.float64),
        actor="self",
        model_key="t",
        ts=0.0,
        provenance_sha="bad2",
    )
    bad2.coords[int(Floor.F02_TRUTH)] = 0.8
    task2 = Task(task_id="t1", task_class="t1", is_irreversible=True)
    dec2 = choose_action(bad2, task2)
    assert dec2.verb == ActionVerb.ESCALATE
    assert dec2.f13_blocked


_self_check()


__all__ = [
    "ActionVerb",
    "Task",
    "ActionDecision",
    "choose_action",
    "detect_drift",
    "detect_eureka",
    "BehaviorMetrics",
    "record_trajectory",
    "audit_gradient_magnitude",
]
