"""
arifOS WELL Bridge — Biological Substrate Connector v2
═══════════════════════════════════════════════════════════════════════════════

Connects the arifOS Governance Kernel to the WELL Human Substrate Layer.
Provides biological readiness signals (Sleep, Stress, Cognitive) to JUDGE.

WELL_v2: Consent reliability composite, HRV velocity, sleep architecture,
strain debt, decision reserve, convergence detector, acute stress circuit breaker.

Axiom: W0 — Sovereignty Invariant. WELL informs, JUDGE considers.

WELL_v2 APPLIED 2026-05-01: Full eureka upgrade — consent_reliability, HRV velocity,
sleep architecture, strain debt, decision reserve, convergence detector
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

import os as _os

WELL_STATE_PATH = Path(_os.environ.get("WELL_STATE_PATH", "/root/WELL/state.json"))

# ─── Thresholds (WELL_v2 calibration) ──────────────────────────────────────────
HRV_HIGH = 60
HRV_LOW = 45
HRV_VELOCITY_DANGER = -3.0
SLEEP_DEEP_MIN_ADEQUATE = 60
SLEEP_REM_MIN_ADEQUATE = 90
SLEEP_EFFICIENCY_MIN = 0.80
STRAIN_DEBT_DANGER = 2.5
DECISION_RESERVE_MIN_SAFE = 0.30
CONSENT_RELIABILITY_SAFE = 0.65


# ─── Helper Functions ──────────────────────────────────────────────────────────


def _compute_hrv_velocity(hrv_trend: list[float]) -> float:
    if len(hrv_trend) < 2:
        return 0.0
    return hrv_trend[-1] - hrv_trend[-2]


def _compute_consent_reliability(state: dict) -> float:
    """The fundamental governance question — can Arif give reliable intent?

    Weighted additive (40% HRV, 25% sleep, 25% decision, 10% floor).
    Multiplicative penalty applied on top for acute stress and strain debt.
    """
    metrics = state.get("metrics", {})

    hrv = metrics.get("hrv", 50)
    if hrv >= HRV_HIGH:
        hrv_factor = 1.0
    elif hrv <= HRV_LOW:
        hrv_factor = 0.2
    else:
        hrv_factor = (hrv - HRV_LOW) / (HRV_HIGH - HRV_LOW)

    sleep_deep = metrics.get("sleep_deep_min", 0)
    sleep_rem = metrics.get("sleep_rem_min", 0)
    sleep_efficiency = metrics.get("sleep_efficiency", 0.75)
    deep_factor = min(1.0, sleep_deep / SLEEP_DEEP_MIN_ADEQUATE)
    rem_factor = min(1.0, sleep_rem / SLEEP_REM_MIN_ADEQUATE)
    sleep_arch_factor = (deep_factor * 0.5) + (rem_factor * 0.3) + (sleep_efficiency * 0.2)

    decision_reserve_pct = metrics.get("decision_reserve_pct", 1.0)
    decision_factor = max(0.0, min(1.0, decision_reserve_pct))

    reliability = hrv_factor * 0.40 + sleep_arch_factor * 0.25 + decision_factor * 0.25 + 0.10

    acute_stress = state.get("acute_stress_active", False)
    strain_debt = metrics.get("strain_debt", 0.0)

    penalty = 1.0
    if acute_stress:
        penalty *= 0.60
    if strain_debt >= STRAIN_DEBT_DANGER:
        penalty *= 0.70
    elif strain_debt > 0:
        penalty *= 1.0 - (strain_debt / STRAIN_DEBT_DANGER) * 0.20

    return round(max(0.0, min(1.0, reliability * penalty)), 3)


def _detect_convergence_alert(state: dict) -> dict | None:
    """Multi-channel convergence risk detector."""
    metrics = state.get("metrics", {})
    channels_declining = []

    hrv_trend = metrics.get("hrv_trend", [])
    if len(hrv_trend) >= 3:
        hrv_velocity = _compute_hrv_velocity(hrv_trend)
        if hrv_velocity < HRV_VELOCITY_DANGER:
            channels_declining.append("hrv")

    sleep_deep = metrics.get("sleep_deep_min", 0)
    if sleep_deep < SLEEP_DEEP_MIN_ADEQUATE * 0.6:
        channels_declining.append("sleep_deep")

    sleep_rem = metrics.get("sleep_rem_min", 0)
    if sleep_rem < SLEEP_REM_MIN_ADEQUATE * 0.6:
        channels_declining.append("sleep_rem")

    decision_reserve_pct = metrics.get("decision_reserve_pct", 1.0)
    if decision_reserve_pct < DECISION_RESERVE_MIN_SAFE:
        channels_declining.append("decision_reserve")

    strain_debt = metrics.get("strain_debt", 0.0)
    if strain_debt > STRAIN_DEBT_DANGER:
        channels_declining.append("strain_debt")

    if state.get("acute_stress_active", False):
        channels_declining.append("acute_stress")

    if len(channels_declining) >= 2:
        severity = "critical" if len(channels_declining) >= 4 else "warning"
        return {
            "active": True,
            "channels_declining": channels_declining,
            "severity": severity,
            "message": f"Multi-channel convergence: {', '.join(channels_declining)} declining simultaneously",
        }

    return None


def _infer_task_readiness(score: float, violations: list, task_load: float = 0.5) -> str:
    if violations:
        return "DEGRADED"
    if task_load > 0.7:
        return "FUNCTIONAL"
    return "OPTIMAL"


def _compute_risk(
    baseline: str, task: str, consent_reliability: float = 1.0, strain_debt: float = 0.0
) -> str:
    if baseline == "DEGRADED":
        return "RED"
    if consent_reliability < 0.5:
        return "RED"
    if baseline == "OPTIMAL" and task in ("FUNCTIONAL", "DEGRADED"):
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
    if convergence_alert is not None:
        return "draft_only"
    if task_readiness == "DEGRADED":
        return "draft_only"
    if consent_reliability < CONSENT_RELIABILITY_SAFE:
        return "draft_only"
    if consent_reliability >= 0.85 and task_readiness == "OPTIMAL":
        return "full"
    return "normal"


def _compute_failure_flags(metrics: dict, hrv_velocity: float, consent_reliability: float) -> list:
    flags = []
    cog = metrics.get("cognitive", {})
    if cog.get("decision_fatigue", 0) > 7:
        flags.append("high_decision_fatigue")
    if cog.get("clarity", 10) < 4:
        flags.append("low_clarity_complex_coding")
    if hrv_velocity < HRV_VELOCITY_DANGER:
        flags.append(f"hrv_velocity_danger:{hrv_velocity:.1f}ms/day")
    if consent_reliability < 0.5:
        flags.append("consent_reliability_critical")
    elif consent_reliability < 0.65:
        flags.append("consent_reliability_reduced")
    sleep_deep = metrics.get("sleep_deep_min", 0)
    if sleep_deep < SLEEP_DEEP_MIN_ADEQUATE * 0.5:
        flags.append("severe_deep_sleep_deprivation")
    return flags


def get_biological_readiness(
    task_load: float = 0.5, override_state: dict | None = None
) -> dict[str, Any]:
    """
    Read the current biological readiness from WELL state.

    WELL_v2 schema:
    - consent_reliability: the governance answer (can Arif give reliable intent?)
    - hrv + hrv_trend + hrv_velocity: predictive signal (12-48h ahead)
    - sleep_deep_min + sleep_rem_min + sleep_efficiency: real recovery engine
    - strain_debt: accumulated recovery deficit
    - decision_reserve_pct: finite resource remaining
    - convergence_alert: multi-channel danger detector
    - acute_stress_active: circuit breaker

    W0 Invariant: WELL informs, Arif decides. WELL never vetoes.
    """
    if override_state is not None:
        state = override_state
    else:
        try:
            _exists = WELL_STATE_PATH.exists()
        except (PermissionError, OSError):
            _exists = False
        if not _exists:
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

        try:
            with open(WELL_STATE_PATH) as f:
                state = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read WELL state: {e}")
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
                "failure_flags": ["well_readiness_error"],
                "sabar_advisory": True,
                "consent_reliability": 0.0,
            }

    metrics = state.get("metrics", {})
    violations = state.get("floors_violated", [])

    hrv = metrics.get("hrv", 50)
    hrv_trend = metrics.get("hrv_trend", [])
    hrv_velocity = _compute_hrv_velocity(hrv_trend)

    sleep_hours = metrics.get("sleep_hours", 50 / 12)
    sleep_deep_min = metrics.get("sleep_deep_min", 0)
    sleep_rem_min = metrics.get("sleep_rem_min", 0)
    sleep_efficiency = metrics.get("sleep_efficiency", 0.75)

    decision_reserve_pct = metrics.get("decision_reserve_pct", 1.0)
    decisions_made_today = metrics.get("decisions_made_today", 0)

    strain_debt = metrics.get("strain_debt", 0.0)
    acute_stress_active = state.get("acute_stress_active", False)

    consent_reliability = _compute_consent_reliability(state)
    convergence_alert = _detect_convergence_alert(state)

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

    task_readiness = _infer_task_readiness(consent_reliability * 100, violations, task_load)
    coupled_risk = _compute_risk(baseline, task_readiness, consent_reliability, strain_debt)
    recommended_mode = _compute_mode(consent_reliability, task_readiness, convergence_alert)
    failure_flags = _compute_failure_flags(metrics, hrv_velocity, consent_reliability)
    well_score = round(consent_reliability * 100, 1)

    return {
        "ok": True,
        "verdict": baseline,
        "well_score": well_score,
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
        "human_baseline_readiness": baseline,
        "task_specific_readiness": task_readiness,
        "machine_readiness": "HEALTHY",
        "coupled_risk": coupled_risk,
        "bandwidth": bandwidth,
        "violations": violations,
        "sabar_advisory": sabar_advisory,
        "recommended_mode": recommended_mode,
        "failure_flags": failure_flags,
        "convergence_alert": convergence_alert,
        "acute_stress_active": acute_stress_active,
        "timestamp": state.get("timestamp"),
    }


def inject_biological_context(
    governance_state: dict[str, Any], task_load: float = 0.5
) -> dict[str, Any]:
    """
    Inject biological readiness into the governance state telemetry.
    Uses WELL_v2 split schema for precise human-machine coupling.
    """
    readiness = get_biological_readiness(task_load)

    telemetry = governance_state.get("telemetry", {})
    telemetry["well_score"] = readiness["well_score"]
    telemetry["well_verdict"] = readiness["human_baseline_readiness"]
    telemetry["well_bandwidth"] = readiness["bandwidth"]
    telemetry["well_task_readiness"] = readiness["task_specific_readiness"]
    telemetry["well_coupled_risk"] = readiness["coupled_risk"]
    telemetry["well_consent_reliability"] = readiness["consent_reliability"]
    telemetry["well_hrv"] = readiness["hrv"]
    telemetry["well_hrv_velocity"] = readiness["hrv_velocity"]
    telemetry["well_convergence_alert"] = readiness["convergence_alert"]

    if readiness.get("sabar_advisory"):
        governance_state["sabar_advisory"] = True
        if governance_state.get("verdict") == "SEAL":
            if readiness["task_specific_readiness"] == "DEGRADED":
                governance_state["verdict"] = "HOLD"
                governance_state["message"] = (
                    governance_state.get("message", "")
                    + " [WELL-HOLD] Task-specific readiness DEGRADED. Sovereign review required."
                )

    # WELL_v2: convergence alert forces HOLD even without sabar_advisory
    convergence = readiness.get("convergence_alert")
    if convergence and convergence.get("active"):
        if governance_state.get("verdict") == "SEAL":
            governance_state["verdict"] = "HOLD"
            governance_state["message"] = (
                governance_state.get("message", "")
                + f" [WELL-CONVERGENCE] {convergence.get('message', 'Multi-channel risk detected')}"
            )

    governance_state["telemetry"] = telemetry
    return governance_state


def signal_cognitive_pressure(load_delta: float, source: str = "forge") -> bool:
    """
    Signal cognitive pressure/load to WELL.
    Updates state.json with decision tracking and strain accumulation.
    """
    try:
        if not WELL_STATE_PATH.exists():
            return False
    except (PermissionError, OSError):
        return False

    try:
        with open(WELL_STATE_PATH) as f:
            state = json.load(f)

        metrics = state.get("metrics", {})
        cog = dict(metrics.get("cognitive", {"clarity": 10, "decision_fatigue": 0}))

        old_fatigue = cog.get("decision_fatigue", 0)
        new_fatigue = min(10.0, old_fatigue + load_delta)
        cog["decision_fatigue"] = new_fatigue
        metrics["cognitive"] = cog

        # Track decisions made
        decisions_made = metrics.get("decisions_made_today", 0)
        metrics["decisions_made_today"] = decisions_made + 1

        # Update decision reserve (deplete by load_delta/10)
        current_reserve = metrics.get("decision_reserve_pct", 1.0)
        metrics["decision_reserve_pct"] = max(0.0, current_reserve - (load_delta / 10))

        # W6 Logic
        violations = state.get("floors_violated", [])
        if load_delta > 2.0 and "W6_METABOLIC_PAUSE" not in violations:
            violations.append("W6_METABOLIC_PAUSE")

        state["metrics"] = metrics
        state["well_score"] = max(0, state.get("well_score", 50) - (load_delta * 2))
        state["floors_violated"] = violations

        with open(WELL_STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception:
        return False


async def anchor_well_to_vault(
    summary: str = "WELL Substrate Anchor", force: bool = False
) -> dict[str, Any]:
    """Anchor current WELL state to the arifOS VAULT999."""
    readiness = get_biological_readiness()
    if not readiness["ok"] and not force:
        return {"ok": False, "message": "Substrate offline. Anchor aborted."}

    try:
        from core.organs._4_vault import seal

        telemetry = {
            "well_score": readiness["well_score"],
            "well_verdict": readiness["human_baseline_readiness"],
            "well_bandwidth": readiness["bandwidth"],
            "well_violations": readiness.get("violations", []),
            "well_task_readiness": readiness["task_specific_readiness"],
            "well_coupled_risk": readiness["coupled_risk"],
            "well_consent_reliability": readiness["consent_reliability"],
            "well_hrv": readiness["hrv"],
            "well_hrv_velocity": readiness["hrv_velocity"],
            "well_convergence_alert": readiness.get("convergence_alert"),
            "source": "WELL-Substrate",
        }

        res = await seal(
            session_id="WELL-AUTO-SYNC",
            summary=summary,
            verdict=(
                "SEAL"
                if readiness["human_baseline_readiness"] in ("OPTIMAL", "FUNCTIONAL")
                else "HOLD"
            ),
            telemetry=telemetry,
            source_agent="well",
            pipeline_stage="999_VAULT",
            risk_tier="LOW",
        )

        return {
            "ok": True,
            "vault_id": res.seal_record.ledger_id,
            "hash": res.seal_record.hash,
            "verdict": res.verdict,
        }
    except Exception as e:
        logger.error(f"VAULT ANCHOR FAILED: {e}")
        return {"ok": False, "error": str(e)}
