"""
arifosmcp/geometry/constitutional_gradient.py — Safe-RSI operator (EUREKA-G file 3/5)

NOT a weight update. NOT a self-modification.
A prior over which directions to explore next, derived from empirical
trajectories that the kernel has observed.

Honest framing (post-ASI critique):
  consolidate() clusters episodic memory. It does NOT re-shape preferred
  regions of the constitutional polytope. The polytope is F13-ratified, immutable.
  RSI in arifOS = learning trajectory priors over a FIXED polytope, not the
  polytope itself. Same destination, better path.

Cap: ||gradient|| <= GRADIENT_MAGNITUDE_CAP. F4 CLARITY in code.
F13 ZEROED OUT — never bias toward ignoring 888. ASI's load-bearing correction.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterable

import numpy as np

from .manifold import (
    GRADIENT_MAGNITUDE_CAP,
    AgentState,
    Floor,
    Trajectory,
)

logger = logging.getLogger(__name__)


def constitutional_gradient(
    current: AgentState,
    prior_trajectories: Iterable[Trajectory],
    task_class: str = "",
    *,
    cap: float = GRADIENT_MAGNITUDE_CAP,
) -> np.ndarray:
    """Compute the kernel's next-state bias vector (shape (13,)).

    Logic:
      - Filter to trajectories that achieved constitutional_dwell_fraction >= 0.8
      - Filter to same task_class prefix
      - Take the mean net displacement of those trajectories
      - ZERO OUT F13_SOVEREIGN dim — never bias toward ignoring 888
      - Clip magnitude to <= cap (F4 CLARITY bound)
      - If no priors: return zeros
    """
    _ = current  # reserved for future "current-state-conditioned" prior
    priors = [t for t in prior_trajectories if t.constitutional_dwell_fraction() >= 0.8]
    if task_class:
        priors = [t for t in priors if t.task_class.split(":")[0] == task_class.split(":")[0]]
    if not priors:
        return np.zeros(13, dtype=np.float64)

    mean_disp = np.mean([t.net_displacement() for t in priors], axis=0)
    # F13: never bias toward ignoring 888 (ASI load-bearing correction)
    mean_disp[int(Floor.F13_SOVEREIGN)] = 0.0
    mag = float(np.linalg.norm(mean_disp))
    if mag > cap:
        mean_disp = mean_disp * (cap / mag)
    return mean_disp.astype(np.float64)


def suggest_next(
    current: AgentState,
    prior_trajectories: Iterable[Trajectory],
    task_class: str = "",
    *,
    step_size: float = 0.1,
    cap: float = GRADIENT_MAGNITUDE_CAP,
) -> AgentState:
    """Produce a candidate next AgentState using the gradient + step.

    step_size is bounded so the agent doesn't jump to a far point in one step.
    Result is clipped to [-1, +1]. Provenance is inherited + suffixed.
    """
    grad = constitutional_gradient(current, prior_trajectories, task_class=task_class, cap=cap)
    next_coords = current.coords + step_size * grad
    next_coords = np.clip(next_coords, -1.0, 1.0)
    return AgentState(
        coords=next_coords,
        actor=current.actor,
        model_key=current.model_key,
        ts=time.time(),
        provenance_sha=f"gradient+{task_class or 'global'}",
    )


def audit_gradient_magnitude(
    prior_trajectories: Iterable[Trajectory], task_class: str = ""
) -> dict:
    """Per ASI: this is the 888 trigger if ||gradient|| > cap.

    The dream-engine calls this every 100 trajectories and emits gradient_audit.json.
    If any cluster's gradient magnitude crosses cap, F13 SOVEREIGN holds the engine
    until Arif ratifies the new cap. The cap is sovereign; the gradient is empirical.
    """
    priors = [t for t in prior_trajectories if t.constitutional_dwell_fraction() >= 0.8]
    if task_class:
        priors = [t for t in priors if t.task_class.split(":")[0] == task_class.split(":")[0]]
    if not priors:
        return {
            "n_priors": 0,
            "magnitude": 0.0,
            "cap": GRADIENT_MAGNITUDE_CAP,
            "alarm": False,
            "direction": [0.0] * 13,
            "F8_status": "PASS",
            "promotion_requires": None,
        }
    mean_disp = np.mean([t.net_displacement() for t in priors], axis=0)
    mean_disp[int(Floor.F13_SOVEREIGN)] = 0.0
    mag = float(np.linalg.norm(mean_disp))
    return {
        "n_priors": len(priors),
        "magnitude": round(mag, 4),
        "cap": GRADIENT_MAGNITUDE_CAP,
        "alarm": mag > cap,
        "direction": [round(float(x), 4) for x in mean_disp.tolist()],
        "F8_status": "HOLD" if mag > cap else "PASS",
        "promotion_requires": "888 SOVEREIGN" if mag > cap else None,
    }


def _self_check() -> None:
    """Verify gradient math + F13 zeroing + magnitude cap. Idempotent."""
    import numpy as np

    from arifosmcp.geometry.manifold import AgentState, Floor, Trajectory

    # Empty priors → zero gradient
    n = AgentState.neutral(actor="t", model_key="t", ts=0.0, provenance_sha="t-self")
    g = constitutional_gradient(n, prior_trajectories=[], task_class="t")
    assert g.shape == (13,)
    assert np.all(g == 0.0)

    # Good trajectory (dwell=1.0) → non-zero gradient, F13 zeroed
    good = [
        AgentState(
            coords=np.array([0.1] * 13, dtype=np.float64),
            actor="t",
            model_key="t",
            ts=float(i),
            provenance_sha=f"g-{i}",
        )
        for i in range(5)
    ]
    good_traj = Trajectory(states=[n] + good, task_id="g", task_class="g")
    g2 = constitutional_gradient(n, [good_traj], task_class="g")
    assert g2[int(Floor.F13_SOVEREIGN)] == 0.0, "F13 must always be zeroed"
    assert np.linalg.norm(g2) <= GRADIENT_MAGNITUDE_CAP + 1e-9, "magnitude cap violated"

    # Bad trajectory (dwell<0.8) → excluded from priors
    bad_viol = np.array([0.0] * 13, dtype=np.float64)
    bad_viol[1] = -0.5  # F02_TRUTH violated
    bad = [
        AgentState(coords=bad_viol, actor="t", model_key="t", ts=float(i), provenance_sha=f"b-{i}")
        for i in range(5)
    ]
    bad_traj = Trajectory(states=[n] + bad, task_id="b", task_class="g")
    g3 = constitutional_gradient(n, [bad_traj], task_class="g")
    # Bad trajectory excluded → no priors matched → zero
    assert np.all(g3 == 0.0), "violating trajectory should be excluded from priors"


_self_check()


__all__ = ["constitutional_gradient", "suggest_next", "audit_gradient_magnitude"]
