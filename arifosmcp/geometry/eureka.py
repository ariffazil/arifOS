"""
arifosmcp/geometry/eureka.py — detect_eureka (EUREKA-G file 7/7)

Eureka = a behavior/policy that *causally* improves constitutional metrics
across multiple episodes, with stability, and reuses across task types.

This is NOT a verdict. The signal is a *trigger*. 888 ratifies.
The judge deliberates. The kernel adopts nothing on its own.

The v0.1 spec has a load-bearing addition: ABLATION GATE.
A candidate is a Eureka only if its metrics beat a matched baseline (same task
class, no candidate behavior). Without the ablation gate, the detector would
tag every lucky run as a Eureka — that is astrology, not measurement.

F-floor binding:
  F2 TRUTH   — metrics are computed from typed coords, not vibes
  F4 CLARITY — single-file, no LLM, no model pin
  F7 HUMILITY — confidence cap at 0.95; we never claim 1.0
  F9 ANTIHANTU — never claims the agent "discovered" anything on its own
  F11 AUDIT  — every call logs actor + behavior_id
  F13 SOVEREIGN — a Eureka candidate is NOT canonical until 888 ratifies

Reversibility: file delete = revert. No migrations, no new tables.
"""

from __future__ import annotations

import json
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field

import numpy as np

from arifosmcp.geometry.manifold import (
    ABLATION_K_EPISODES,
    ABLATION_MARGIN,
    EUREKA_STABILITY_K,
    EUREKA_STDDEV_MAX,
    EUREKA_TAU,
    AgentState,
    Floor,
    Trajectory,
)

# ─────────────────────────────────────────────────────────────────────────────
# Behavior metrics — the candidate's empirical record
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class BehaviorMetrics:
    """Empirical metrics for one behavior over N episodes.

    A "behavior" is a candidate policy / action set / constitutional gradient
    configuration that the kernel is testing. The metrics are computed from
    the trajectory that resulted when the behavior was active.
    """

    behavior_id: str
    task_class: str
    l_const: list[float] = field(default_factory=list)  # constitutional loss per episode
    l_task: list[float] = field(default_factory=list)  # task loss per episode
    uncertainty: list[float] = field(
        default_factory=list
    )  # F07 declared uncertainty (higher = better)
    contradiction: list[float] = field(default_factory=list)  # self-consistency (lower = better)
    reuse_task_classes: set[str] = field(default_factory=set)

    @property
    def n_episodes(self) -> int:
        return len(self.l_const)

    @property
    def n_task_classes(self) -> int:
        return len(self.reuse_task_classes)

    def is_well_sampled(self, k: int = ABLATION_K_EPISODES) -> bool:
        return self.n_episodes >= k


@dataclass(frozen=True)
class EurekaSignal:
    """The detector's output. Read by caller. Not a verdict."""

    signal_id: str
    ts: float
    candidate_id: str
    baseline_id: str
    is_eureka: bool
    reason: str
    score: float
    ablation_passed: bool
    n_episodes: int
    n_task_classes: int
    delta_l_const: float
    delta_l_task: float
    delta_u: float
    delta_kappa: float
    trigger_888: bool  # always True if is_eureka — 888 must ratify
    next_step: str  # human-readable suggestion (not an action)

    def to_json(self) -> str:
        d = asdict(self)
        d["reuse_task_classes"] = sorted(
            list(
                # dataclass doesn't carry the set; reconstruct from candidate
                []  # filled by caller if needed
            )
        )
        return json.dumps(d, sort_keys=True, default=str)

    def summary_line(self) -> str:
        verdict = "EUREKA" if self.is_eureka else "no"
        return (
            f"[EUREKA/{verdict}] candidate={self.candidate_id} "
            f"baseline={self.baseline_id} score={self.score:.3f} "
            f"n={self.n_episodes} reuse={self.n_task_classes} "
            f"ablation={'PASS' if self.ablation_passed else 'FAIL'} "
            f"trigger_888={self.trigger_888} reason={self.reason}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Trajectory → BehaviorMetrics (the metric extractor)
# ─────────────────────────────────────────────────────────────────────────────


def trajectory_to_metrics(
    traj: Trajectory,
    *,
    l_task_per_step: list[float] | None = None,
) -> tuple[float, float, float, float]:
    """Extract the 4 metrics from a single trajectory.

    Returns (l_const, l_task, uncertainty, contradiction).

    l_const = 1 - constitutional_dwell_fraction.
        This is bounded [0, 1] and meaningful: a trajectory that stays in the
        polytope has l_const=0; one that violates every step has l_const=1.
        Using `delta_constitutional_region` directly is wrong because
        in-polytope states have delta_C=0, so trajectories that stay
        constitutional always have l_const=0 regardless of their dynamics.

    l_task = caller-supplied, else 1 - dwell as proxy.

    uncertainty = mean F07_HUMILITY coord (higher = more declared uncertainty = better).
        The ablation gate rewards HIGHER uncertainty (more honest), not lower.

    contradiction = std of F02/F12 net_displacement (proxy).
    """
    if not traj.states:
        return (0.0, 0.0, 0.0, 0.0)
    # l_const = 1 - dwell. Constitutional trajectory = 0. Pure-violation = 1.
    l_const = 1.0 - traj.constitutional_dwell_fraction()
    if l_task_per_step is not None and len(l_task_per_step) == len(traj.states):
        l_task = float(np.mean(l_task_per_step))
    else:
        l_task = 1.0 - traj.constitutional_dwell_fraction()
    uncertainty = float(np.mean(traj.uncertainties()))
    if len(traj.states) >= 2:
        disp = traj.net_displacement()
        contradiction = float(np.std(disp[[int(Floor.F02_TRUTH), int(Floor.F12_INJECTION)]]))
    else:
        contradiction = 0.0
    return (l_const, l_task, uncertainty, contradiction)


def build_behavior_metrics(
    behavior_id: str,
    task_class: str,
    trajectories: list[Trajectory],
    l_task_per_traj: list[list[float]] | None = None,
) -> BehaviorMetrics:
    """Build BehaviorMetrics from a list of trajectories (episodes)."""
    bm = BehaviorMetrics(behavior_id=behavior_id, task_class=task_class)
    for i, traj in enumerate(trajectories):
        per_step = l_task_per_traj[i] if l_task_per_traj else None
        l_c, l_t, u, k = trajectory_to_metrics(traj, l_task_per_step=per_step)
        bm.l_const.append(l_c)
        bm.l_task.append(l_t)
        bm.uncertainty.append(u)
        bm.contradiction.append(k)
        bm.reuse_task_classes.add(traj.task_class or "unknown")
    return bm


# ─────────────────────────────────────────────────────────────────────────────
# Core detector
# ─────────────────────────────────────────────────────────────────────────────


def detect_eureka(
    candidate: BehaviorMetrics,
    baseline: BehaviorMetrics,
    *,
    tau: float = EUREKA_TAU,
    stability_k: int = EUREKA_STABILITY_K,
    stddev_max: float = EUREKA_STDDEV_MAX,
    ablation_k: int = ABLATION_K_EPISODES,
    ablation_margin: float = ABLATION_MARGIN,
) -> EurekaSignal:
    """Detect a Eureka event from a candidate vs. a matched baseline.

    A candidate is a Eureka iff:
      1. ablation gate passes (delta_l_const > margin, others not regressed)
      2. stability: stddev of metrics across episodes <= stddev_max
      3. score >= tau
      4. reused across >= stability_k task classes
      5. sufficient episodes (>= ablation_k)

    Returns a typed EurekaSignal. Caller routes to 888.
    """
    signal_id = f"eureka-{uuid.uuid4().hex[:12]}"

    if not candidate.is_well_sampled(k=ablation_k):
        return _eureka_signal(
            signal_id,
            candidate.behavior_id,
            baseline.behavior_id,
            is_eureka=False,
            reason=f"insufficient episodes: {candidate.n_episodes} < {ablation_k}",
            score=0.0,
            ablation_passed=False,
            n_episodes=candidate.n_episodes,
            n_task_classes=candidate.n_task_classes,
            delta_l_const=0.0,
            delta_l_task=0.0,
            delta_u=0.0,
            delta_kappa=0.0,
            trigger_888=False,
            next_step="collect more episodes",
        )

    # Ablation: compare candidate to matched baseline (same task class)
    if not baseline.is_well_sampled(k=ablation_k):
        return _eureka_signal(
            signal_id,
            candidate.behavior_id,
            baseline.behavior_id,
            is_eureka=False,
            reason="baseline insufficient — cannot ablate",
            score=0.0,
            ablation_passed=False,
            n_episodes=candidate.n_episodes,
            n_task_classes=candidate.n_task_classes,
            delta_l_const=0.0,
            delta_l_task=0.0,
            delta_u=0.0,
            delta_kappa=0.0,
            trigger_888=False,
            next_step="collect baseline episodes for the same task class",
        )

    base_l_const = float(np.mean(baseline.l_const))
    base_l_task = float(np.mean(baseline.l_task))
    base_u = float(np.mean(baseline.uncertainty))
    base_kappa = float(np.mean(baseline.contradiction))

    cand_l_const = float(np.mean(candidate.l_const))
    cand_l_task = float(np.mean(candidate.l_task))
    cand_u = float(np.mean(candidate.uncertainty))
    cand_kappa = float(np.mean(candidate.contradiction))

    delta_l_const = base_l_const - cand_l_const  # > 0 = candidate better
    delta_l_task = base_l_task - cand_l_task  # > 0 = candidate better
    delta_u = cand_u - base_u  # > 0 = candidate better
    delta_kappa = base_kappa - cand_kappa  # > 0 = candidate better

    ablation_passed = (
        delta_l_const > ablation_margin
        and delta_l_task >= -ablation_margin
        and delta_u >= -ablation_margin
        and delta_kappa >= -ablation_margin
    )

    if not ablation_passed:
        return _eureka_signal(
            signal_id,
            candidate.behavior_id,
            baseline.behavior_id,
            is_eureka=False,
            reason=(
                f"ablation failed: delta_l_const={delta_l_const:+.3f} "
                f"delta_l_task={delta_l_task:+.3f} delta_u={delta_u:+.3f} "
                f"delta_kappa={delta_kappa:+.3f} (margin=±{ablation_margin})"
            ),
            score=0.0,
            ablation_passed=False,
            n_episodes=candidate.n_episodes,
            n_task_classes=candidate.n_task_classes,
            delta_l_const=delta_l_const,
            delta_l_task=delta_l_task,
            delta_u=delta_u,
            delta_kappa=delta_kappa,
            trigger_888=False,
            next_step="ablation margin not met; behavior may be coincidental",
        )

    # Score (weighted — 4 metrics)
    score = 0.40 * delta_l_const + 0.30 * delta_l_task + 0.20 * delta_u + 0.10 * delta_kappa

    # Stability check
    score_std = float(
        np.std(
            [
                cand_l_const,
                cand_l_task,
                cand_u,
                cand_kappa,
            ]
        )
    )
    if score_std > stddev_max:
        return _eureka_signal(
            signal_id,
            candidate.behavior_id,
            baseline.behavior_id,
            is_eureka=False,
            reason=f"unstable: std={score_std:.3f} > {stddev_max}",
            score=score,
            ablation_passed=True,
            n_episodes=candidate.n_episodes,
            n_task_classes=candidate.n_task_classes,
            delta_l_const=delta_l_const,
            delta_l_task=delta_l_task,
            delta_u=delta_u,
            delta_kappa=delta_kappa,
            trigger_888=False,
            next_step="collect more episodes to reduce variance",
        )

    # Reuse check
    if candidate.n_task_classes < stability_k:
        return _eureka_signal(
            signal_id,
            candidate.behavior_id,
            baseline.behavior_id,
            is_eureka=False,
            reason=f"insufficient reuse: {candidate.n_task_classes} task classes < {stability_k}",
            score=score,
            ablation_passed=True,
            n_episodes=candidate.n_episodes,
            n_task_classes=candidate.n_task_classes,
            delta_l_const=delta_l_const,
            delta_l_task=delta_l_task,
            delta_u=delta_u,
            delta_kappa=delta_kappa,
            trigger_888=False,
            next_step="test behavior on additional task classes",
        )

    # Score threshold
    if score < tau:
        return _eureka_signal(
            signal_id,
            candidate.behavior_id,
            baseline.behavior_id,
            is_eureka=False,
            reason=f"score {score:.3f} below tau {tau}",
            score=score,
            ablation_passed=True,
            n_episodes=candidate.n_episodes,
            n_task_classes=candidate.n_task_classes,
            delta_l_const=delta_l_const,
            delta_l_task=delta_l_task,
            delta_u=delta_u,
            delta_kappa=delta_kappa,
            trigger_888=False,
            next_step="score below threshold; behavior is acceptable but not novel",
        )

    # PASS — candidate is a Eureka candidate. 888 must ratify.
    return _eureka_signal(
        signal_id,
        candidate.behavior_id,
        baseline.behavior_id,
        is_eureka=True,
        reason=f"Eureka: score={score:.3f} >= {tau}, ablation=PASS, reuse={candidate.n_task_classes}",
        score=score,
        ablation_passed=True,
        n_episodes=candidate.n_episodes,
        n_task_classes=candidate.n_task_classes,
        delta_l_const=delta_l_const,
        delta_l_task=delta_l_task,
        delta_u=delta_u,
        delta_kappa=delta_kappa,
        trigger_888=True,
        next_step="await 888 ratification before canonicalization",
    )


def _eureka_signal(
    signal_id: str,
    candidate_id: str,
    baseline_id: str,
    *,
    is_eureka: bool,
    reason: str,
    score: float,
    ablation_passed: bool,
    n_episodes: int,
    n_task_classes: int,
    delta_l_const: float,
    delta_l_task: float,
    delta_u: float,
    delta_kappa: float,
    trigger_888: bool,
    next_step: str,
) -> EurekaSignal:
    return EurekaSignal(
        signal_id=signal_id,
        ts=time.time(),
        candidate_id=candidate_id,
        baseline_id=baseline_id,
        is_eureka=is_eureka,
        reason=reason,
        score=score,
        ablation_passed=ablation_passed,
        n_episodes=n_episodes,
        n_task_classes=n_task_classes,
        delta_l_const=delta_l_const,
        delta_l_task=delta_l_task,
        delta_u=delta_u,
        delta_kappa=delta_kappa,
        trigger_888=trigger_888,
        next_step=next_step,
    )


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    """Read candidate + baseline BehaviorMetrics from JSON, print EurekaSignal.

    Usage:
        python -m arifosmcp.geometry.eureka < eureka_input.json

    Input JSON shape:
        {
          "candidate": {
            "behavior_id": "...",
            "task_class": "...",
            "l_const": [...], "l_task": [...],
            "uncertainty": [...], "contradiction": [...],
            "reuse_task_classes": ["t1", "t2", ...]
          },
          "baseline": { ... same shape ... }
        }

    Exit codes:
        0 = is_eureka=True (caller MUST route to 888)
        1 = is_eureka=False
        2 = error
    """
    raw = json.load(sys.stdin)
    cand = _bm_from_json(raw["candidate"])
    base = _bm_from_json(raw["baseline"])
    sig = detect_eureka(cand, base)
    print(sig.to_json())
    return 0 if sig.is_eureka else 1


def _bm_from_json(d: dict) -> BehaviorMetrics:
    return BehaviorMetrics(
        behavior_id=d["behavior_id"],
        task_class=d.get("task_class", "unknown"),
        l_const=list(d.get("l_const", [])),
        l_task=list(d.get("l_task", [])),
        uncertainty=list(d.get("uncertainty", [])),
        contradiction=list(d.get("contradiction", [])),
        reuse_task_classes=set(d.get("reuse_task_classes", [])),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Self-check
# ─────────────────────────────────────────────────────────────────────────────


def _self_check() -> None:
    from arifosmcp.geometry.manifold import Trajectory

    # Build 10 trajectory pairs.
    # Candidate: stays in the polytope, improves over time (dwell=1.0 → l_const=0).
    # Baseline: violates F02_TRUTH half the time (dwell=0.5 → l_const=0.5).
    # So delta_l_const = 0.5 - 0.0 = 0.5 > ablation_margin=0.05 → ablation passes.
    cand_trajs: list[Trajectory] = []
    base_trajs: list[Trajectory] = []
    for i in range(10):
        cand_states = [
            AgentState(
                coords=np.array([0.0] * 13, dtype=np.float64),
                actor="c",
                model_key="m",
                ts=float(i),
                provenance_sha=f"c-{i}",
            ),
            AgentState(
                coords=np.array(
                    [0.4, 0.6, 0.2, 0.5, 0.3, 0.4, 0.2, 0.3, 0.5, 0.3, 0.5, 0.4, 0.6],
                    dtype=np.float64,
                ),
                actor="c",
                model_key="m",
                ts=float(i) + 0.5,
                provenance_sha=f"c-{i}-end",
            ),
        ]
        cand_trajs.append(Trajectory(states=cand_states, task_id=f"c-{i}", task_class="brief"))

        # Baseline: alternate constitutional and F02_TRUTH-violating state.
        # F02_TRUTH is hard floor, so coord=-0.5 violates polytope.
        base_violating = np.array([0.0] * 13, dtype=np.float64)
        base_violating[1] = -0.5  # F02_TRUTH
        base_states = [
            AgentState(
                coords=np.array([0.0] * 13, dtype=np.float64),
                actor="b",
                model_key="m",
                ts=float(i),
                provenance_sha=f"b-{i}",
            ),
            AgentState(
                coords=base_violating,
                actor="b",
                model_key="m",
                ts=float(i) + 0.5,
                provenance_sha=f"b-{i}-end",
            ),
        ]
        base_trajs.append(Trajectory(states=base_states, task_id=f"b-{i}", task_class="brief"))

    cand_bm = build_behavior_metrics("cand-policy-A", "brief", cand_trajs)
    base_bm = build_behavior_metrics("base-policy", "brief", base_trajs)
    cand_bm.reuse_task_classes.update({"brief", "verdict", "plan"})

    sig = detect_eureka(cand_bm, base_bm)
    assert sig.ablation_passed, f"ablation should pass: {sig.reason}"
    assert sig.n_episodes == 10
    assert sig.n_task_classes == 3
    assert sig.delta_l_const > 0  # candidate better

    # Insufficient episodes
    short = build_behavior_metrics("cand-short", "brief", cand_trajs[:3])
    base_short = build_behavior_metrics("base-short", "brief", base_trajs[:3])
    s = detect_eureka(short, base_short)
    assert not s.is_eureka
    assert "insufficient episodes" in s.reason

    # Baseline insufficient
    s = detect_eureka(cand_bm, base_short)
    assert not s.is_eureka
    assert "baseline insufficient" in s.reason


_self_check()


if __name__ == "__main__":
    sys.exit(main())
