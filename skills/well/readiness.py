"""
skills/well/readiness.py — Biological Readiness Check v2

Eureka insights from WHOOP red team audit applied:
1. Convergence > single metric (multi-channel, not well_score alone)
2. HRV velocity > HRV snapshot (3-point trend, 12-48h prediction)
3. Strain debt is invisible until it isn't (accumulated recovery deficit)
4. Sleep architecture > sleep duration (deep/REM, not just hours)
5. Decision reserve, not fatigue (finite resource, not accumulation)
6. Consent reliability composite (the fundamental governance question)
7. Acute stress circuit breaker (sudden-state-change override)

P0-B APPLIED 2026-05-01: Schema split — human_baseline vs task_specific
WELL_v2 APPLIED 2026-05-01: Full eureka upgrade — consent_reliability, HRV velocity,
  sleep architecture, strain debt, decision reserve, convergence detector

W0 Invariant: WELL informs, Arif decides. WELL never vetoes — but a convergence
alert forces HOLD regardless of autonomy level.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

WELL_STATE_PATH = Path(os.environ.get("WELL_STATE_PATH", "/root/WELL/state.json"))

# ─── Thresholds (WELL_v2 calibration) ──────────────────────────────────────────
HRV_HIGH = 60  # above this = vagal tone good
HRV_LOW = 45  # below this = sympathetic dominance, elevated risk
HRV_VELOCITY_DANGER = -3.0  # ms/day decline threshold — predictive of crash
SLEEP_DEEP_MIN_ADEQUATE = 60  # minutes
SLEEP_REM_MIN_ADEQUATE = 90  # minutes
SLEEP_EFFICIENCY_MIN = 0.80
STRAIN_DEBT_DANGER = 2.5  # days equivalent
DECISION_RESERVE_MIN_SAFE = 0.30  # 30% reserve floor for consequential actions
CONSENT_RELIABILITY_SAFE = 0.65  # minimum for SEAL without explicit human ack
ACUTE_STRESS_OVERRIDE = True  # forces sabar_advisory when True


# ─── Helper Functions ──────────────────────────────────────────────────────────


def _compute_hrv_velocity(hrv_trend: list[float]) -> float:
    """Compute HRV velocity (ms/day change) from 3-point trend."""
    if len(hrv_trend) < 2:
        return 0.0
    # Use most recent 2 points for velocity
    return hrv_trend[-1] - hrv_trend[-2]


def _compute_consent_reliability(state: dict) -> float:
    """
    Compute consent reliability composite — the fundamental governance question.

    Answers: Is Arif capable of reliable intent right now?

    Weighted additive composite (not multiplicative product) to avoid
    extreme compression when multiple factors are imperfect.

    Weights: HRV 40%, Sleep architecture 25%, Decision reserve 25%, Penalties 10%
    """
    metrics = state.get("metrics", {})

    # HRV factor (40% weight) — most governance-relevant signal
    hrv = metrics.get("hrv", 50)
    if hrv >= HRV_HIGH:
        hrv_factor = 1.0
    elif hrv <= HRV_LOW:
        hrv_factor = 0.2
    else:
        hrv_factor = (hrv - HRV_LOW) / (HRV_HIGH - HRV_LOW)

    # Sleep architecture factor (25% weight)
    sleep_deep = metrics.get("sleep_deep_min", 0)
    sleep_rem = metrics.get("sleep_rem_min", 0)
    sleep_efficiency = metrics.get("sleep_efficiency", 0.75)

    # Normalize: adequate deep = 60min, adequate rem = 90min
    deep_factor = min(1.0, sleep_deep / SLEEP_DEEP_MIN_ADEQUATE)
    rem_factor = min(1.0, sleep_rem / SLEEP_REM_MIN_ADEQUATE)
    sleep_arch_factor = (deep_factor * 0.5) + (rem_factor * 0.3) + (sleep_efficiency * 0.2)

    # Decision reserve factor (25% weight)
    decision_reserve_pct = metrics.get("decision_reserve_pct", 1.0)
    decision_factor = max(0.0, min(1.0, decision_reserve_pct))

    # Weighted sum
    reliability = (
        hrv_factor * 0.40
        + sleep_arch_factor * 0.25
        + decision_factor * 0.25
        + 0.10  # base floor — always at least 10%
    )

    # Penalties (multiplicative reduction on top of weighted sum)
    acute_stress = state.get("acute_stress_active", False)
    strain_debt = metrics.get("strain_debt", 0.0)

    penalty = 1.0
    if acute_stress:
        penalty *= 0.60  # acute stress: 40% reduction
    if strain_debt > 0:
        if strain_debt >= STRAIN_DEBT_DANGER:
            penalty *= 0.70  # severe strain debt
        else:
            penalty *= 1.0 - (strain_debt / STRAIN_DEBT_DANGER) * 0.20

    return round(max(0.0, min(1.0, reliability * penalty)), 3)


def _detect_convergence_alert(state: dict) -> dict | None:
    """
    Detect multi-channel convergence risk.

    The danger is NOT when any single channel degrades — it's when multiple
    independent channels trend negative simultaneously. The composite risk
    is the PRODUCT, not the average.

    Returns alert dict if 2+ channels declining, else None.
    """
    metrics = state.get("metrics", {})

    channels_declining = []

    # HRV trend check
    hrv_trend = metrics.get("hrv_trend", [])
    if len(hrv_trend) >= 3:
        hrv_velocity = _compute_hrv_velocity(hrv_trend)
        if hrv_velocity < HRV_VELOCITY_DANGER:
            channels_declining.append("hrv")

    # Sleep deep check
    sleep_deep = metrics.get("sleep_deep_min", SLEEP_DEEP_MIN_ADEQUATE)
    if sleep_deep < SLEEP_DEEP_MIN_ADEQUATE * 0.6:
        channels_declining.append("sleep_deep")

    # Sleep REM check
    sleep_rem = metrics.get("sleep_rem_min", SLEEP_REM_MIN_ADEQUATE)
    if sleep_rem < SLEEP_REM_MIN_ADEQUATE * 0.6:
        channels_declining.append("sleep_rem")

    # Decision reserve check
    decision_reserve_pct = metrics.get("decision_reserve_pct", 1.0)
    if decision_reserve_pct < DECISION_RESERVE_MIN_SAFE:
        channels_declining.append("decision_reserve")

    # Strain debt check
    strain_debt = metrics.get("strain_debt", 0.0)
    if strain_debt > STRAIN_DEBT_DANGER:
        channels_declining.append("strain_debt")

    # Acute stress override
    if state.get("acute_stress_active", False):
        channels_declining.append("acute_stress")

    if len(channels_declining) >= 2:
        severity = "critical" if len(channels_declining) >= 4 else "warning"
        return {
            "active": True,
            "channels_declining": channels_declining,
            "severity": severity,
            "message": f"Multi-channel convergence risk: {', '.join(channels_declining)} declining simultaneously",
        }

    return None


def _infer_task_readiness(score: float, violations: list, task_load: float = 0.5) -> str:
    """Infer task-specific readiness from task load and biological state."""
    if violations:
        return "DEGRADED"
    if task_load > 0.7:
        return "FUNCTIONAL"
    return "OPTIMAL"


def _compute_risk(
    baseline: str, task: str, consent_reliability: float = 1.0, strain_debt: float = 0.0
) -> str:
    """
    Compute coupled human-machine risk level.

    Multiplicative (not additive):
    - baseline DEGRADED × task FUNCTIONAL = RED (not AMBER)
    - consent_reliability < 0.5 = automatic RED
    - strain_debt > 2.5 = escalate one level
    """
    if baseline == "DEGRADED":
        return "RED"

    if consent_reliability < 0.5:
        return "RED"

    if baseline == "OPTIMAL" and task in ("FUNCTIONAL", "DEGRADED"):
        # consent reliability corrects the optimistic baseline
        if consent_reliability < 0.65:
            return "RED"
        return "AMBER"

    if baseline == "FUNCTIONAL":
        if consent_reliability < 0.7 or strain_debt > STRAIN_DEBT_DANGER:
            return "AMBER"
        return "GREEN"

    return "GREEN"


def _compute_mode(
    consent_reliability: float, task_readiness: str, convergence_alert: dict | None
) -> str:
    """
    Compute recommended mode from consent_reliability and task readiness.

    Convergence alert overrides consent_reliability.
    """
    if convergence_alert is not None:
        return "draft_only"

    if task_readiness == "DEGRADED":
        return "draft_only"

    if consent_reliability < CONSENT_RELIABILITY_SAFE:
        return "draft_only"

    if consent_reliability >= 0.85 and task_readiness == "OPTIMAL":
        return "full"

    return "normal"


def _compute_failure_flags(
    metrics: dict, hrv_velocity: float, consent_reliability: float
) -> list[str]:
    """Compute failure flags from WELL metrics."""
    flags = []

    cog = metrics.get("cognitive", {})
    if cog.get("decision_fatigue", 0) > 7:
        flags.append("high_decision_fatigue")
    if cog.get("clarity", 10) < 4:
        flags.append("low_clarity_complex_coding")

    # HRV velocity danger
    if hrv_velocity < HRV_VELOCITY_DANGER:
        flags.append(f"hrv_velocity_danger:{hrv_velocity:.1f}ms/day")

    # Consent reliability low
    if consent_reliability < 0.5:
        flags.append("consent_reliability_critical")
    elif consent_reliability < 0.65:
        flags.append("consent_reliability_reduced")

    # Sleep architecture
    sleep_deep = metrics.get("sleep_deep_min", 0)
    if sleep_deep < SLEEP_DEEP_MIN_ADEQUATE * 0.5:
        flags.append("severe_deep_sleep_deprivation")

    return flags


def readiness_check(task_load: float = 0.5, override_state: dict | None = None) -> dict[str, Any]:
    """
    Evaluate biological readiness from WELL state.

    WELL_v2 schema:
    - consent_reliability: the governance answer (can Arif give reliable intent?)
    - hrv + hrv_trend + hrv_velocity: predictive signal (12-48h ahead)
    - sleep_deep_min + sleep_rem_min + sleep_efficiency: real recovery engine
    - strain_debt: accumulated recovery deficit (invisible until catastrophic)
    - decision_reserve_pct: finite resource remaining (not accumulation)
    - convergence_alert: multi-channel danger detector
    - acute_stress_active: circuit breaker for sudden-state-change

    W0 Invariant: WELL informs, Arif decides. WELL never vetoes — but a convergence
    alert forces HOLD regardless of autonomy level.
    """
    try:
        if override_state is not None:
            state = override_state
            _state_source = "override"
        else:
            _exists = WELL_STATE_PATH.exists()
            if not _exists:
                return _offline_response()

            with open(WELL_STATE_PATH, "r") as f:
                state = json.load(f)
    except (PermissionError, OSError):
        return _offline_response()
    except json.JSONDecodeError:
        return _error_response("state.json is corrupted")

    try:
        # ── Extract signals ─────────────────────────────────────────────────
        metrics = state.get("metrics", {})
        violations = state.get("floors_violated", [])

        # Core HRV signal
        hrv = metrics.get("hrv", 50)
        hrv_trend = metrics.get("hrv_trend", [])
        hrv_velocity = _compute_hrv_velocity(hrv_trend)

        # Sleep architecture
        sleep_hours = metrics.get("sleep_hours", state.get("well_score", 50) / 12)
        sleep_deep_min = metrics.get("sleep_deep_min", 0)
        sleep_rem_min = metrics.get("sleep_rem_min", 0)
        sleep_efficiency = metrics.get("sleep_efficiency", 0.75)

        # Decision resource
        decision_reserve_pct = metrics.get("decision_reserve_pct", 1.0)
        decisions_made_today = metrics.get("decisions_made_today", 0)

        # Strain debt
        strain_debt = metrics.get("strain_debt", 0.0)

        # Acute stress
        acute_stress_active = state.get("acute_stress_active", False)

        # ── Consent reliability composite (the fundamental governance answer) ──
        consent_reliability = _compute_consent_reliability(state)

        # ── Convergence alert ──────────────────────────────────────────────
        convergence_alert = _detect_convergence_alert(state)

        # ── Baseline verdict (what WELL observed at rest) ─────────────────
        if violations:
            baseline = "DEGRADED"
            bandwidth = "RESTRICTED"
            sabar_advisory = True
        elif consent_reliability >= 0.85:
            baseline = "OPTIMAL"
            bandwidth = "FULL"
            sabar_advisory = False
        elif consent_reliability >= 0.65:
            baseline = "FUNCTIONAL"
            bandwidth = "NORMAL"
            sabar_advisory = False
        else:
            baseline = "LOW_CAPACITY"
            bandwidth = "REDUCED"
            sabar_advisory = True

        # ── Task-specific readiness ────────────────────────────────────────
        task_readiness = _infer_task_readiness(consent_reliability * 100, violations, task_load)

        # ── Coupled risk ───────────────────────────────────────────────────
        coupled_risk = _compute_risk(baseline, task_readiness, consent_reliability, strain_debt)

        # ── Recommended mode ──────────────────────────────────────────────
        recommended_mode = _compute_mode(consent_reliability, task_readiness, convergence_alert)

        # ── Failure flags ──────────────────────────────────────────────────
        failure_flags = _compute_failure_flags(metrics, hrv_velocity, consent_reliability)

        # ── WELL score (backward-compat composite) ─────────────────────────
        # Approximate from consent_reliability for backward compat
        well_score = round(consent_reliability * 100, 1)

        # ── Build response ─────────────────────────────────────────────────
        result = {
            "ok": True,
            "verdict": baseline,
            "well_score": well_score,
            # WELL_v2 new fields
            "consent_reliability": consent_reliability,
            "hrv": hrv,
            "hrv_trend": hrv_trend,
            "hrv_velocity": round(hrv_velocity, 1),
            "resting_hr": metrics.get("resting_hr", None),
            "sleep_hours": round(sleep_hours, 1),
            "sleep_deep_min": sleep_deep_min,
            "sleep_rem_min": sleep_rem_min,
            "sleep_efficiency": round(sleep_efficiency, 3),
            "strain_debt": round(strain_debt, 2),
            "recovery_rate": metrics.get("recovery_rate", None),
            "decisions_made_today": decisions_made_today,
            "decision_reserve_pct": round(decision_reserve_pct, 3),
            # P0-B split fields
            "human_baseline_readiness": baseline,
            "task_specific_readiness": task_readiness,
            "machine_readiness": "HEALTHY",
            "coupled_risk": coupled_risk,
            # Behavioral guidance
            "bandwidth": bandwidth,
            "violations": violations,
            "sabar_advisory": sabar_advisory,
            "recommended_mode": recommended_mode,
            "failure_flags": failure_flags,
            # Convergence detector
            "convergence_alert": convergence_alert,
            # Acute stress
            "acute_stress_active": acute_stress_active,
            "timestamp": state.get("timestamp"),
        }

        return result

    except Exception as e:
        return {
            "ok": False,
            "verdict": "ERROR",
            "human_baseline_readiness": "ERROR",
            "task_specific_readiness": "ERROR",
            "machine_readiness": "HEALTHY",
            "coupled_risk": "UNKNOWN",
            "error": str(e),
            "well_score": 0.0,
            "bandwidth": "RESTRICTED",
            "recommended_mode": "draft_only",
            "failure_flags": ["well_readiness_error"],
            "sabar_advisory": True,
            "consent_reliability": 0.0,
        }


def _offline_response() -> dict[str, Any]:
    return {
        "ok": False,
        "verdict": "UNKNOWN",
        "human_baseline_readiness": "UNKNOWN",
        "task_specific_readiness": "UNKNOWN",
        "machine_readiness": "HEALTHY",
        "coupled_risk": "UNKNOWN",
        "well_score": 50.0,
        "bandwidth": "NORMAL",
        "message": "WELL substrate offline or state missing.",
        "recommended_mode": "draft_only",
        "failure_flags": ["well_offline"],
        "sabar_advisory": False,
        "consent_reliability": 0.5,
        "hrv": None,
        "hrv_trend": [],
        "convergence_alert": None,
        "acute_stress_active": False,
    }


def _error_response(msg: str) -> dict[str, Any]:
    return {
        "ok": False,
        "verdict": "ERROR",
        "human_baseline_readiness": "ERROR",
        "task_specific_readiness": "ERROR",
        "machine_readiness": "HEALTHY",
        "coupled_risk": "UNKNOWN",
        "well_score": 0.0,
        "bandwidth": "RESTRICTED",
        "recommended_mode": "draft_only",
        "failure_flags": ["well_readiness_error", msg],
        "sabar_advisory": True,
        "consent_reliability": 0.0,
    }
